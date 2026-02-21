from pydantic import BaseModel
from typing import Any, Optional


class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    pull_request: Optional[dict] = None
    repository: Optional[dict] = None
    sender: Optional[dict] = None
