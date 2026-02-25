from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import Report, ReportStatus
from pydantic import BaseModel
from backend.services.ai_service import generate_report
from backend.agents.research_pipeline import run_research_pipeline
from backend.services.ai_service import generate_report, get_token_usage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Report Platform",
    description="Multi-agent AI system for research and report generation",
    version="0.1.0"
)

# Add after app = FastAPI(...)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Pydantic model defines what the request body must look like
# FastAPI uses this for automatic validation
class CreateReportRequest(BaseModel):
    title: str
    topic: str
    user_id: int

class CreateUserRequest(BaseModel):
    name: str
    email: str

@app.post("/users", status_code=201)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    from backend.db.models import User
    new_user = User(
        name=request.name,
        email=request.email
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "created_at": new_user.created_at
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-report-platform",
        "version": "0.1.0"
    }

@app.post("/reports", status_code=201)
async def create_report(
    request: CreateReportRequest,
    db: AsyncSession = Depends(get_db)
):
    new_report = Report(
        title=request.title,
        topic=request.topic,
        user_id=request.user_id,
        status=ReportStatus.PENDING
    )
    db.add(new_report)
    await db.flush()
    await db.refresh(new_report)

    return {
        "id": new_report.id,
        "title": new_report.title,
        "topic": new_report.topic,
        "status": new_report.status,
        "created_at": new_report.created_at
    }

@app.get("/reports/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    report = result.scalar_one_or_none()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report.id,
        "title": report.title,
        "topic": report.topic,
        "status": report.status,
        "content": report.content,
        "created_at": report.created_at
    }

@app.post("/reports/generate", status_code=201)
async def generate_ai_report(
    request: CreateReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a report AND generates AI content for it.
    This connects the database layer with the AI layer.
    """
    # Step 1 — generate AI content
    content = await generate_report(request.topic)
    
    # Step 2 — save to database with generated content
    new_report = Report(
        title=request.title,
        topic=request.topic,
        content=content,
        status=ReportStatus.COMPLETED,
        user_id=request.user_id
    )
    db.add(new_report)
    await db.flush()
    await db.refresh(new_report)
    
    return {
        "id": new_report.id,
        "title": new_report.title,
        "topic": new_report.topic,
        "status": new_report.status,
        "content": new_report.content,
        "created_at": new_report.created_at
    }

@app.get("/ai/token-usage")
async def check_token_usage(topic: str):
    """
    Test endpoint to see token usage for a given topic.
    Useful for understanding costs.
    """
    result = await get_token_usage(topic)
    return result

@app.post("/reports/pipeline", status_code=201)
async def generate_pipeline_report(
    request: CreateReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Runs the full multi-agent pipeline:
    Research → Analysis → Writing → Validation → Save
    """
    print(f"🚀 Starting multi-agent pipeline for: {request.topic}")
    
    # Run the multi-agent pipeline
    result = await run_research_pipeline(request.topic)
    
    # Save the final report to PostgreSQL
    new_report = Report(
        title=request.title,
        topic=request.topic,
        content=result["final_report"],
        status=ReportStatus.COMPLETED,
        user_id=request.user_id
    )
    db.add(new_report)
    await db.flush()
    await db.refresh(new_report)
    
    return {
        "id": new_report.id,
        "title": new_report.title,
        "topic": new_report.topic,
        "status": new_report.status,
        "content": new_report.content,
        "iterations": result["iterations"],
        "approved": result["approved"],
        "created_at": new_report.created_at
    }