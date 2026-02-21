from fastapi import APIRouter
from models.ranking import RetrieveRequest, RetrieveResponse
from services.ml_service import get_ml_service

router = APIRouter(prefix="/retrieve", tags=["retrieval"])


@router.post("", response_model=RetrieveResponse)
async def retrieve_similar(request: RetrieveRequest):
    """Retrieve similar historical code hunks."""
    ml = get_ml_service()
    result = ml.retrieve(request.query_diff, request.k)
    return RetrieveResponse(results=result.get("results", []))
