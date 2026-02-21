import logging
import logging.config
import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health, ranking, clustering, retrieval, webhooks

load_dotenv()

# Structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start queue worker
    from services.queue_service import get_queue_service
    queue = get_queue_service()
    await queue.start()
    logger.info("Assert Review API started")
    yield
    # Shutdown
    await queue.stop()
    logger.info("Assert Review API shutting down")


app = FastAPI(
    title="Assert Review ML API",
    description="AI-powered code review backend — embeddings, reranking, clustering",
    version="0.7.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(ranking.router)
app.include_router(clustering.router)
app.include_router(retrieval.router)
app.include_router(webhooks.router)
