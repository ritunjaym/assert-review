"""
GitHub PR scraper — fetches merged PRs using GITHUB_TOKEN.
Rate-limit aware: sleeps when X-RateLimit-Remaining < 10.
"""
import asyncio
import json
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

DEFAULT_REPOS = [
    "microsoft/vscode",
    "vercel/next.js",
    "huggingface/transformers",
]

RAW_DIR = Path(__file__).parent / "raw"


class GitHubScraper:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.base_url = "https://api.github.com"

    async def _check_rate_limit(self, response: httpx.Response) -> None:
        remaining = int(response.headers.get("X-RateLimit-Remaining", 100))
        if remaining < 10:
            reset_at = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_sec = max(0, reset_at - time.time()) + 5
            print(f"Rate limit low ({remaining} remaining). Sleeping {sleep_sec:.0f}s...")
            await asyncio.sleep(sleep_sec)

    async def fetch_merged_prs(
        self,
        repo: str,
        max_prs: int = 100,
        client: httpx.AsyncClient | None = None,
    ) -> list[dict]:
        """Fetch merged PRs from a repo, up to max_prs."""
        prs = []
        page = 1
        per_page = min(max_prs, 100)
        
        should_close = client is None
        if client is None:
            client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        
        try:
            while len(prs) < max_prs:
                url = f"{self.base_url}/repos/{repo}/pulls"
                params = {"state": "closed", "sort": "updated", "direction": "desc",
                         "per_page": per_page, "page": page}
                resp = await client.get(url, params=params)
                await self._check_rate_limit(resp)
                resp.raise_for_status()
                
                batch = [pr for pr in resp.json() if pr.get("merged_at")]
                if not batch:
                    break
                prs.extend(batch)
                page += 1
                
                if len(resp.json()) < per_page:
                    break
        finally:
            if should_close:
                await client.aclose()
        
        return prs[:max_prs]

    async def fetch_pr_files(self, repo: str, pr_number: int, client: httpx.AsyncClient) -> list[dict]:
        """Fetch files changed in a PR."""
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        resp = await client.get(url, params={"per_page": 100})
        await self._check_rate_limit(resp)
        if resp.status_code != 200:
            return []
        return resp.json()

    async def scrape(
        self,
        repos: list[str] | None = None,
        max_prs_per_repo: int = 50,
        output_dir: Path | None = None,
    ) -> list[dict]:
        """Main scrape function — fetches PRs + files, saves raw JSON."""
        repos = repos or DEFAULT_REPOS
        output_dir = output_dir or RAW_DIR
        output_dir.mkdir(parents=True, exist_ok=True)
        
        all_prs = []
        
        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            for repo in repos:
                print(f"Scraping {repo}...")
                prs = await self.fetch_merged_prs(repo, max_prs_per_repo, client)
                print(f"  Found {len(prs)} merged PRs")
                
                for pr in prs:
                    pr_number = pr["number"]
                    files = await self.fetch_pr_files(repo, pr_number, client)
                    pr["files"] = files
                    pr["repo"] = repo
                    all_prs.append(pr)
                    await asyncio.sleep(0.1)  # Be polite
        
        # Save raw
        out_file = output_dir / "prs_raw.jsonl"
        with open(out_file, "w") as f:
            for pr in all_prs:
                f.write(json.dumps(pr) + "\n")
        print(f"Saved {len(all_prs)} PRs to {out_file}")
        return all_prs


async def main():
    scraper = GitHubScraper()
    await scraper.scrape(max_prs_per_repo=50)


if __name__ == "__main__":
    asyncio.run(main())
