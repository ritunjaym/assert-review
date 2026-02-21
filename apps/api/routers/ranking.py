import time
from fastapi import APIRouter, HTTPException
from models.ranking import RankRequest, RankResponse, RankedFile
from services.ml_service import get_ml_service

router = APIRouter(prefix="/rank", tags=["ranking"])


@router.post("", response_model=RankResponse)
async def rank_pr(request: RankRequest):
    """Rank PR files by ML-estimated importance."""
    ml = get_ml_service()
    result = ml.rank_pr(
        request.pr_id,
        request.repo,
        [f.model_dump() for f in request.files],
    )

    ranked_files = [
        RankedFile(
            filename=rf["filename"],
            rank=rf["rank"],
            reranker_score=rf["reranker_score"],
            retrieval_score=rf["retrieval_score"],
            final_score=rf["final_score"],
            explanation=rf["explanation"],
        )
        for rf in result["ranked_files"]
    ]

    return RankResponse(
        pr_id=request.pr_id,
        ranked_files=ranked_files,
        processing_ms=result["processing_ms"],
    )
