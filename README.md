# 🤖 AI Report Platform

A production-grade, full-stack AI research and report generation platform built with a multi-agent architecture. This system uses four specialized AI agents — Research, Analysis, Writing, and Validation — to autonomously generate comprehensive, high-quality research reports on any topic.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
- [Multi-Agent Pipeline](#multi-agent-pipeline)
- [Database Schema](#database-schema)
- [CI/CD Pipeline](#cicd-pipeline)
- [Docker & Containerization](#docker--containerization)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)

---

## Overview

The AI Report Platform demonstrates how multiple specialized AI agents can collaborate to produce outputs significantly better than a single LLM call. Instead of asking one model to do everything, each agent has a focused role, its own system prompt, and a specific job in the pipeline.

A user submits a topic. Four agents work sequentially — researching, analyzing, writing, and validating. The final approved report is saved to a PostgreSQL database and returned through a clean React frontend.

**What makes this different from a simple ChatGPT wrapper:**

- Four specialized agents each optimized for their specific task
- LangGraph orchestration with conditional edges — the validator can send the report back for revision
- Full persistent storage — every report saved to PostgreSQL with complete metadata
- Production-ready infrastructure — Docker containers, CI/CD pipeline, GitHub Actions automation
- Real async architecture — handles concurrent users without blocking

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│              (Next.js + TypeScript + Tailwind)           │
│         Agent Progress Tracker + Report Viewer           │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (CORS enabled)
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                        │
│              (Python + Uvicorn + Async)                  │
│           REST API with auto-generated docs              │
└──────┬───────────────────────────────┬───────────────────┘
       │                               │
┌──────▼──────┐               ┌────────▼────────┐
│  PostgreSQL  │               │  LangGraph       │
│  Database    │               │  Agent Pipeline  │
│  (SQLAlchemy │               │                  │
│  + Alembic)  │               │  ┌─────────────┐ │
└─────────────┘               │  │  Research   │ │
                               │  │  Agent      │ │
                               │  └──────┬──────┘ │
                               │         │        │
                               │  ┌──────▼──────┐ │
                               │  │  Analysis   │ │
                               │  │  Agent      │ │
                               │  └──────┬──────┘ │
                               │         │        │
                               │  ┌──────▼──────┐ │
                               │  │  Writing    │ │
                               │  │  Agent      │ │
                               │  └──────┬──────┘ │
                               │         │        │
                               │  ┌──────▼──────┐ │
                               │  │  Validator  │ │
                               │  │  Agent      │ │
                               │  └─────────────┘ │
                               └──────────────────┘
                                        │
                               ┌────────▼────────┐
                               │  Azure OpenAI    │
                               │  GPT-4o          │
                               └─────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Next.js 14, React, TypeScript | User interface |
| Styling | Tailwind CSS | Component styling |
| HTTP Client | Axios | Frontend-backend communication |
| Markdown | react-markdown | Rendering formatted reports |
| Backend | FastAPI, Python 3.11 | REST API framework |
| Server | Uvicorn | ASGI server |
| Database | PostgreSQL 15 | Persistent data storage |
| ORM | SQLAlchemy (async) | Python-database bridge |
| Migrations | Alembic | Database version control |
| AI Agents | LangGraph 1.0.9 | Multi-agent orchestration |
| LLM Framework | LangChain | LLM building blocks |
| AI Model | Azure OpenAI GPT-4o | Large language model |
| Containerization | Docker, Docker Compose | Environment consistency |
| CI/CD | GitHub Actions | Automated testing and deployment |
| Testing | pytest, pytest-asyncio, httpx | Backend test suite |
| Version Control | Git, GitHub | Source control with Gitflow |

---

## Features

### Multi-Agent Report Generation
Submit any research topic and four specialized AI agents collaborate autonomously to produce a comprehensive, structured report. Each agent has a focused system prompt optimized for its specific role.

### Real-time Agent Progress Tracking
The frontend displays live progress as each agent completes its work — Research, Analysis, Writing, and Validation — with visual status indicators.

### Intelligent Quality Validation
The Validator Agent reviews every report before finalizing. If quality standards aren't met, it sends the report back to the Writing Agent for revision. The pipeline supports up to three revision iterations before finalizing.

### Persistent Report Storage
Every generated report is saved to PostgreSQL with full metadata — title, topic, content, status, iteration count, approval status, and timestamps. Reports persist across sessions.

### Automatic API Documentation
FastAPI auto-generates interactive Swagger documentation at `/docs`. Every endpoint is documented and testable directly in the browser.

### Containerized Development
Docker Compose starts the entire stack — PostgreSQL, backend, and frontend — with a single command. Identical environment across development and production.

### Automated CI/CD
GitHub Actions runs automated tests on every push to `develop` and every pull request targeting `main`. The CD pipeline triggers on every merge to `main`.

---

## Project Structure

```
ai-report-platform/
│
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI pipeline - tests on every push
│       └── cd.yml              # CD pipeline - deploy on merge to main
│
├── backend/
│   ├── api/
│   │   └── main.py             # FastAPI app, all routes, CORS config
│   ├── agents/
│   │   ├── __init__.py
│   │   └── research_pipeline.py # LangGraph multi-agent pipeline
│   ├── db/
│   │   ├── database.py         # Async SQLAlchemy engine, session factory
│   │   └── models.py           # ORM models - User, Report, ReportStatus
│   ├── services/
│   │   └── ai_service.py       # Direct Azure OpenAI integration
│   └── Dockerfile              # Backend container recipe
│
├── frontend/
│   ├── app/
│   │   └── page.tsx            # Main UI - input form, agent tracker, report viewer
│   ├── lib/
│   │   └── api.ts              # API service layer, TypeScript interfaces
│   ├── next.config.ts          # Next.js config with standalone output
│   └── Dockerfile              # Frontend multi-stage container recipe
│
├── alembic/                    # Database migration files
│   ├── versions/               # Migration history
│   └── env.py                  # Alembic configuration
│
├── tests/
│   ├── __init__.py
│   └── test_api.py             # API endpoint tests
│
├── infra/                      # Infrastructure configuration
├── docs/                       # Project documentation
│
├── conftest.py                 # pytest configuration, Python path setup
├── pytest.ini                  # Test runner settings
├── docker-compose.yml          # Full stack orchestration
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (never committed)
├── .gitignore                  # Git exclusions
├── .dockerignore               # Docker build exclusions
└── README.md                   # This file
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Docker Desktop
- Azure OpenAI access (endpoint, API key, deployment name)

### Local Development Setup

**1. Clone the repository**
```bash
git clone https://github.com/shaunakawasthi/ai-report-platform.git
cd ai-report-platform
```

**2. Set up Python environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

**3. Configure environment variables**

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/ai_report
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
APP_ENV=development
APP_VERSION=0.1.0
```

**4. Set up the database**
```bash
# Create database in PostgreSQL (via pgAdmin or psql)
# Then run migrations
alembic upgrade head
```

**5. Start the backend**
```bash
uvicorn backend.api.main:app --reload
```
Backend available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

**6. Start the frontend**
```bash
cd frontend
npm install
npm run dev
```
Frontend available at: `http://localhost:3000`

### Docker Setup (Recommended)

Start the entire stack with one command:
```bash
docker-compose up
```

This starts:
- PostgreSQL on port 5433
- FastAPI backend on port 8000
- Next.js frontend on port 3000

All three containers are networked together automatically.

---

## API Reference

### Health Check
```
GET /health
```
Returns service status and version. Used by load balancers and monitoring tools.

**Response:**
```json
{
  "status": "healthy",
  "service": "ai-report-platform",
  "version": "0.1.0"
}
```

---

### Create User
```
POST /users
```
**Request body:**
```json
{
  "name": "Shaunak Awasthi",
  "email": "shaunak@example.com"
}
```

---

### Create Report (manual)
```
POST /reports
```
Creates a report record without AI generation. Status defaults to `pending`.

---

### Get Report
```
GET /reports/{report_id}
```
Retrieves a specific report by ID including full AI-generated content.

---

### Generate Report (single LLM call)
```
POST /reports/generate
```
Generates a report using a single Azure OpenAI call. Faster but lower quality than the pipeline endpoint.

---

### Generate Pipeline Report (multi-agent)
```
POST /reports/pipeline
```
Runs the full four-agent pipeline. Takes 30-60 seconds. Returns higher quality output than the single-call endpoint.

**Request body:**
```json
{
  "title": "AI in Healthcare",
  "topic": "Impact of artificial intelligence on medical diagnostics",
  "user_id": 1
}
```

**Response:**
```json
{
  "id": 7,
  "title": "AI in Healthcare",
  "topic": "Impact of artificial intelligence on medical diagnostics",
  "status": "completed",
  "content": "## Executive Summary\n\n...",
  "iterations": 1,
  "approved": true,
  "created_at": "2026-02-25T12:37:35"
}
```

---

### Check Token Usage
```
GET /ai/token-usage?topic=machine+learning
```
Returns token consumption for a test generation. Useful for cost monitoring.

---

## Multi-Agent Pipeline

The core of the platform is a LangGraph state machine with four specialized agents and conditional routing.

### State Definition

All agents share a common state object — a typed dictionary that flows through the entire pipeline:

```python
class ReportState(TypedDict):
    topic: str                 # original user input
    research: str              # output from Research Agent
    analysis: str              # output from Analysis Agent
    report_draft: str          # output from Writing Agent
    validation_feedback: str   # output from Validator Agent
    final_report: str          # approved final report
    iteration_count: int       # revision counter
    is_approved: bool          # validator decision
```

### Agent Roles

**Research Agent**
- System prompt: Expert research specialist
- Input: topic
- Output: Structured research with background, current state, statistics, challenges, key players
- Optimized for: Thoroughness and factual accuracy

**Analysis Agent**
- System prompt: Expert analyst
- Input: topic + research
- Output: Key themes, critical insights, cause-effect relationships, strategic implications
- Optimized for: Interpretation over repetition

**Writing Agent**
- System prompt: Expert report writer
- Input: topic + research + analysis
- Output: Structured professional report with Executive Summary, Introduction, Key Findings, Analysis, Implications, Conclusion
- Optimized for: Clarity and professional business language

**Validator Agent**
- System prompt: Strict quality reviewer
- Input: topic + report draft
- Output: APPROVED/REJECTED decision with detailed feedback
- Optimized for: Critical evaluation of completeness, structure, clarity, accuracy

### Graph Flow

```
[Research] → [Analysis] → [Writing] → [Validation]
                                            │
                              ┌─────────────┴──────────────┐
                              │                            │
                         APPROVED                      REJECTED
                              │                      (if iterations < 3)
                              ▼                            │
                          [Finalize]                  [Writing] ←──┘
                              │
                            [END]
```

The conditional edge after validation checks two conditions: whether the report is approved and whether the maximum iteration count (3) has been reached. This prevents infinite loops while allowing genuine quality improvement.

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### Reports Table
```sql
CREATE TABLE reports (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    topic       VARCHAR(500) NOT NULL,
    content     TEXT,
    status      report_status_enum DEFAULT 'pending',
    user_id     INTEGER REFERENCES users(id) NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);
```

### Status Enum
```
pending     → created, not yet processed
processing  → agent pipeline running
completed   → report generated and approved
failed      → pipeline encountered an error
```

Migrations are managed by Alembic. To create a new migration after model changes:
```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

---

## CI/CD Pipeline

### CI Pipeline (`ci.yml`)

Triggers on every push to `develop` and every pull request targeting `main`.

**Backend job:**
1. Checkout code
2. Set up Python 3.11
3. Cache pip packages
4. Install dependencies
5. Run pytest test suite

**Frontend job:**
1. Checkout code
2. Set up Node.js 20
3. Install npm dependencies
4. Build Next.js production bundle

If either job fails, the PR cannot be merged. Broken code never reaches `main`.

### CD Pipeline (`cd.yml`)

Triggers on every merge to `main`.

Currently configured to confirm deployment trigger. Expand this workflow with Azure Container Registry push and Azure Container Apps update steps for full automated deployment.

### Branch Strategy

```
main        → production-ready code only, protected branch
develop     → integration branch, all features merge here first
feature/*   → individual feature development
```

All merges to `main` require a pull request from `develop` with passing CI checks.

---

## Docker & Containerization

### Backend Dockerfile

Uses Python 3.11-slim base image. Requirements are installed before copying application code to leverage Docker layer caching — if only code changes, pip install is skipped on rebuild.

```bash
# Build
docker build -f backend/Dockerfile -t ai-report-backend .

# Run with environment variables
docker run -p 8000:8000 --env-file .env ai-report-backend
```

### Frontend Dockerfile

Uses a multi-stage build. Stage 1 (builder) compiles the Next.js application using a full Node image. Stage 2 (runner) copies only the compiled output into a minimal Alpine image. This reduces the final image size from ~400MB to ~70MB.

```bash
# Build
docker build -f frontend/Dockerfile -t ai-report-frontend ./frontend

# Run
docker run -p 3000:3000 ai-report-frontend
```

### Docker Compose

Starts all three services with correct networking and dependency ordering:

```bash
# Start everything
docker-compose up

# Start in background
docker-compose up -d

# Stop everything
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

Services:
- `db` — PostgreSQL 15 on port 5433
- `backend` — FastAPI on port 8000, depends on `db`
- `frontend` — Next.js on port 3000, depends on `backend`

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource URL | `https://resource.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-01` |
| `APP_ENV` | Environment name | `development` / `production` |
| `APP_VERSION` | Application version | `0.1.0` |

Never commit `.env` to version control. It is listed in `.gitignore`.

---

## Development Workflow

### Starting a New Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Committing Changes

Follow conventional commit format:
```bash
git commit -m "feat: add PDF export endpoint"
git commit -m "fix: resolve foreign key violation on report creation"
git commit -m "docs: update API reference for pipeline endpoint"
git commit -m "chore: upgrade langgraph to 1.0.9"
```

### Merging to Develop

```bash
git push origin feature/your-feature-name
# Open PR on GitHub: feature/* → develop
```

### Releasing to Main

```bash
# Open PR on GitHub: develop → main
# CI must pass before merge is allowed
# CD pipeline triggers automatically after merge
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_api.py::test_health_check -v
```

---

## About

Built as a learning project to understand and implement production-grade AI application development from the ground up — covering backend APIs, database design, multi-agent orchestration, frontend development, containerization, and CI/CD automation.

**Author:** Shaunak Awasthi  
**Role:** AI Product Manager  
**LinkedIn:** [shaunakawasthi](https://linkedin.com/in/shaunakawasthi)  
**GitHub:** [shaunakawasthi](https://github.com/shaunakawasthi)
