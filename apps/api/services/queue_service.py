"""
In-memory asyncio.Queue for background PR processing.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class QueueService:
    def __init__(self, maxsize: int = 100):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._worker_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the background worker."""
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("Queue worker started")

    async def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()

    async def enqueue(self, item: dict) -> None:
        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull:
            logger.warning("Queue full, dropping item")

    async def _worker(self) -> None:
        while True:
            try:
                item = await self._queue.get()
                await self._process(item)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Queue worker error: {e}")

    async def _process(self, item: dict) -> None:
        from services.ml_service import get_ml_service
        action = item.get("action")
        logger.info(f"Processing queue item: action={action}")

        if action == "rank_pr":
            ml = get_ml_service()
            files = item.get("files", [])
            pr_id = str(item.get("pr_id", ""))
            repo = item.get("repo", "")
            result = ml.rank_pr(pr_id, repo, files)
            logger.info(f"Ranked PR {pr_id}: {len(result.get('ranked_files', []))} files")


_queue_service: QueueService | None = None


def get_queue_service() -> QueueService:
    global _queue_service
    if _queue_service is None:
        _queue_service = QueueService()
    return _queue_service
