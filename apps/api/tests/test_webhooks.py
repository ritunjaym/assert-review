import hashlib
import hmac
import json
import pytest
from httpx import ASGITransport, AsyncClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_signature(payload: bytes, secret: str) -> str:
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"


@pytest.mark.asyncio
async def test_webhook_ping_event():
    from main import app
    payload = json.dumps({"zen": "Keep it simple"}).encode()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=payload,
            headers={"X-GitHub-Event": "ping", "Content-Type": "application/json"},
        )
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_webhook_valid_signature():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "test_secret"
    from main import app

    payload = json.dumps({"action": "opened", "pull_request": {"number": 1}, "repository": {"name": "repo", "owner": {"login": "user"}}}).encode()
    sig = make_signature(payload, "test_secret")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": sig,
                "Content-Type": "application/json",
            },
        )
    assert response.status_code == 200
    del os.environ["GITHUB_WEBHOOK_SECRET"]


@pytest.mark.asyncio
async def test_webhook_invalid_signature():
    os.environ["GITHUB_WEBHOOK_SECRET"] = "test_secret"
    from main import app

    payload = json.dumps({"action": "opened"}).encode()
    tampered_sig = "sha256=deadbeef"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/webhooks/github",
            content=payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": tampered_sig,
                "Content-Type": "application/json",
            },
        )
    assert response.status_code == 403
    del os.environ["GITHUB_WEBHOOK_SECRET"]
