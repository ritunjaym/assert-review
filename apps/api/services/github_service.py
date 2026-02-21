"""
GitHub API client using httpx.
"""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        """Fetch files changed in a PR."""
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            )
            if resp.status_code != 200:
                logger.warning(f"GitHub API error {resp.status_code} for PR files")
                return []
            return resp.json()
