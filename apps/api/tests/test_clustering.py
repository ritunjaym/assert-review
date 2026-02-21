import pytest
from unittest.mock import patch
from httpx import ASGITransport, AsyncClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


MOCK_CLUSTER_RESULT = {
    "pr_id": "42",
    "groups": [
        {"cluster_id": 0, "label": "auth login", "files": ["src/auth/login.py"], "coherence": 0.95},
        {"cluster_id": 1, "label": "tests", "files": ["tests/test_auth.py"], "coherence": 1.0},
    ],
}


@pytest.mark.asyncio
async def test_cluster_endpoint():
    with patch("services.ml_service.MLService.cluster_pr", return_value=MOCK_CLUSTER_RESULT):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/cluster", json={
                "pr_id": "42",
                "files": [
                    {"filename": "src/auth/login.py", "additions": 10, "deletions": 0},
                    {"filename": "tests/test_auth.py", "additions": 5, "deletions": 0},
                ]
            })
    assert response.status_code == 200
    data = response.json()
    assert data["pr_id"] == "42"
    assert len(data["groups"]) == 2
