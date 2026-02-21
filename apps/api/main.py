from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import health

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: lazy-load ML models when first requested
    yield
    # Shutdown: cleanup


app = FastAPI(
    title="Assert Review ML API",
    description="AI-powered code review backend — embeddings, reranking, clustering",
    version="0.1.0",
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
