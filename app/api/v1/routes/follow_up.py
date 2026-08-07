from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate, FollowUpResponse, FollowUpListResponse
from app.services.follow_up_service import FollowUpService
from app.core.dependencies import get_follow_up_service

router = APIRouter(prefix="/follow-ups", tags=["Follow Up"])

@router.post("/", response_model=FollowUpResponse)
async def create_follow_up(
    follow_up: FollowUpCreate,
    service: FollowUpService = Depends(get_follow_up_service)
) -> FollowUpResponse:
    """
    Create a new follow up.
    """
    try:
        return await service.create_follow_up(follow_up)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=FollowUpListResponse)
async def list_follow_ups(
    status: str | None = Query(None, description="Filter by status"),
    restaurant_id: int | None = Query(None, description="Filter by restaurant ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: FollowUpService = Depends(get_follow_up_service)
) -> FollowUpListResponse:
    """
    List follow ups with pagination and filters.
    """
    try:
        return await service.list_follow_ups(status=status, restaurant_id=restaurant_id, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending", response_model=list[FollowUpResponse])
async def get_pending_follow_ups(
    service: FollowUpService = Depends(get_follow_up_service)
) -> list[FollowUpResponse]:
    """
    Get all pending follow ups.
    """
    try:
        return await service.get_pending_follow_ups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{follow_up_id}", response_model=FollowUpResponse)
async def get_follow_up(
    follow_up_id: int,
    service: FollowUpService = Depends(get_follow_up_service)
) -> FollowUpResponse:
    """
    Get a specific follow up.
    """
    try:
        return await service.get_follow_up(follow_up_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{follow_up_id}", response_model=FollowUpResponse)
async def update_follow_up(
    follow_up_id: int,
    update_data: FollowUpUpdate,
    service: FollowUpService = Depends(get_follow_up_service)
) -> FollowUpResponse:
    """
    Update a follow up.
    """
    try:
        return await service.update_follow_up(follow_up_id, update_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{follow_up_id}")
async def delete_follow_up(
    follow_up_id: int,
    service: FollowUpService = Depends(get_follow_up_service)
) -> dict[str, Any]:
    """
    Delete a follow up.
    """
    try:
        await service.delete_follow_up(follow_up_id)
        return {"status": "success", "message": f"Follow-up {follow_up_id} deleted."}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
