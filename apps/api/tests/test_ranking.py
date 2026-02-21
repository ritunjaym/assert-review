import pytest
from unittest.mock import MagicMock, patch
from httpx import ASGITransport, AsyncClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


MOCK_RANK_RESULT = {
    "pr_id": "42",
    "ranked_files": [
        {
            "filename": "src/auth/login.py",
            "rank": 1,
            "reranker_score": 0.9,
            "retrieval_score": 0.8,
            "final_score": 0.86,
            "explanation": "security-sensitive path → high priority",
        }
    ],
    "processing_ms": 10,
}


@pytest.mark.asyncio
async def test_rank_endpoint():
    with patch("services.ml_service.MLService.rank_pr", return_value=MOCK_RANK_RESULT):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/rank", json={
                "pr_id": "42",
                "repo": "test/repo",
                "files": [
                    {"filename": "src/auth/login.py", "additions": 50, "deletions": 10}
                ]
            })
    assert response.status_code == 200
    data = response.json()
    assert data["pr_id"] == "42"
    assert len(data["ranked_files"]) == 1
    assert data["ranked_files"][0]["rank"] == 1


@pytest.mark.asyncio
async def test_rank_empty_files():
    with patch("services.ml_service.MLService.rank_pr", return_value={"pr_id": "1", "ranked_files": [], "processing_ms": 0}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/rank", json={
                "pr_id": "1",
                "repo": "test/repo",
                "files": []
            })
    assert response.status_code == 200
    assert response.json()["ranked_files"] == []
