from fastapi import APIRouter
from models.ranking import ClusterRequest, ClusterResponse, ClusterOutput
from services.ml_service import get_ml_service

router = APIRouter(prefix="/cluster", tags=["clustering"])


@router.post("", response_model=ClusterResponse)
async def cluster_pr(request: ClusterRequest):
    """Cluster PR files into semantic groups."""
    ml = get_ml_service()
    result = ml.cluster_pr(
        request.pr_id,
        [f.model_dump() for f in request.files],
    )

    groups = [
        ClusterOutput(
            cluster_id=g["cluster_id"],
            label=g["label"],
            files=g["files"],
            coherence=g["coherence"],
        )
        for g in result["groups"]
    ]

    return ClusterResponse(pr_id=request.pr_id, groups=groups)
