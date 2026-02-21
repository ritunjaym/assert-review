"""
GitHub webhook receiver.
Validates X-Hub-Signature-256 HMAC, enqueues PR events for async processing.
"""
import hashlib
import hmac
import json
import logging
import os

from fastapi import APIRouter, HTTPException, Request, Response

from services.queue_service import get_queue_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def _verify_signature(payload: bytes, signature_header: str | None, secret: str) -> bool:
    """Verify X-Hub-Signature-256 HMAC."""
    if not signature_header:
        return False
    if not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)


@router.post("/github")
async def github_webhook(request: Request):
    """Receive GitHub webhook events."""
    payload_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    event_type = request.headers.get("X-GitHub-Event", "")

    webhook_secret = os.environ.get("GITHUB_WEBHOOK_SECRET", "")

    if webhook_secret:
        if not _verify_signature(payload_bytes, signature, webhook_secret):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

    try:
        payload = json.loads(payload_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if event_type == "ping":
        return {"ok": True}

    if event_type == "pull_request":
        action = payload.get("action", "")
        if action in ("opened", "synchronize"):
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {})

            queue = get_queue_service()
            await queue.enqueue({
                "action": "rank_pr",
                "pr_id": pr.get("number"),
                "repo": f"{repo.get('owner', {}).get('login', '')}/{repo.get('name', '')}",
                "files": [],  # Will be fetched by background worker
            })
            logger.info(f"Enqueued PR #{pr.get('number')} for processing")

    return Response(status_code=200)
