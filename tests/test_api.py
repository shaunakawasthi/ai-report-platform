import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app

# ============================================================
# TEST CLIENT SETUP
# AsyncClient lets us make HTTP requests to our FastAPI app
# without actually starting a server
# ASGITransport connects the client directly to the app
# ============================================================

@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

# ============================================================
# TESTS
# Each test function starts with test_
# pytest finds and runs them automatically
# ============================================================

async def test_health_check(client):
    """Health endpoint should return 200 with healthy status"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ai-report-platform"

async def test_health_check_version(client):
    """Health endpoint should return version"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert "version" in response.json()

async def test_get_nonexistent_report(client):
    """Getting a report that doesn't exist should return 404"""
    pytest.skip("Requires database")
    response = await client.get("/reports/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Report not found"

async def test_create_report_missing_fields(client):
    """Creating a report without required fields should return 422"""
    response = await client.post("/reports", json={})
    assert response.status_code == 422  # Unprocessable Entity

async def test_docs_available(client):
    """API documentation should be accessible"""
    response = await client.get("/docs")
    assert response.status_code == 200