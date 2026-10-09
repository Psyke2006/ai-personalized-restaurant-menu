from fastapi import APIRouter
from backend.schemas.health import HealthResponse
from backend.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    """Returns system status and backend operational health."""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        recommender_engine="active"
    )
