from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.models import Report, ReportStatus
from pydantic import BaseModel

app = FastAPI(
    title="AI Report Platform",
    description="Multi-agent AI system for research and report generation",
    version="0.1.0"
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