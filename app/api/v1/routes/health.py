from fastapi import APIRouter
from app.utils.helpers import now_utc

router = APIRouter(prefix="", tags=["Health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": now_utc().isoformat(),
        "version": "1.0.0"
    }
