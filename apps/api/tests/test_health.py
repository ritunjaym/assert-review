import pytest
from httpx import ASGITransport, AsyncClient

import sys
import os

# Add api directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.mark.asyncio
async def test_health_returns_ok():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
