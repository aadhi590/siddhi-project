from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.watchlist import WatchAreaCreate, WatchAreaUpdate, WatchAreaResponse, WatchAreaListResponse
from app.services.watchlist_service import WatchlistService
from app.core.dependencies import get_watchlist_service

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.post("/", response_model=WatchAreaResponse)
async def create_watch_area(
    request: WatchAreaCreate,
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """Create a new watch area."""
    return await watchlist_service.create_area(request)

@router.get("/", response_model=WatchAreaListResponse)
async def list_watch_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """List watch areas with pagination."""
    areas, total = await watchlist_service.get_areas(skip=skip, limit=limit)
    return WatchAreaListResponse(items=areas, total=total, skip=skip, limit=limit)

@router.get("/{area_id}", response_model=WatchAreaResponse)
async def get_watch_area(
    area_id: int,
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """Get a single watch area."""
    area = await watchlist_service.get_area(area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Watch area not found")
    return area

@router.patch("/{area_id}", response_model=WatchAreaResponse)
async def update_watch_area(
    area_id: int,
    request: WatchAreaUpdate,
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """Update a watch area."""
    area = await watchlist_service.update_area(area_id, request)
    if not area:
        raise HTTPException(status_code=404, detail="Watch area not found")
    return area

@router.delete("/{area_id}")
async def delete_watch_area(
    area_id: int,
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """Delete a watch area."""
    success = await watchlist_service.delete_area(area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Watch area not found")
    return {"message": "Watch area deleted successfully"}

@router.post("/seed")
async def seed_watch_areas(
    watchlist_service: WatchlistService = Depends(get_watchlist_service)
):
    """Seed default Chennai watch areas."""
    await watchlist_service.seed_chennai_areas()
    return {"message": "Chennai watch areas seeded successfully"}
