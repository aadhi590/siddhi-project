from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.restaurant import RestaurantResponse, RestaurantListResponse, RestaurantUpdate, RestaurantAnalysisResponse
from app.services.restaurant_service import RestaurantService
from app.core.dependencies import get_restaurant_service
from app.background.tasks import analyze_single_restaurant, generate_outreach_for_restaurant
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])

@router.get("/", response_model=RestaurantListResponse)
async def list_restaurants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = None,
    restaurant_type: Optional[str] = None,
    min_rating: Optional[float] = None,
    min_premium_score: Optional[float] = None,
    service: RestaurantService = Depends(get_restaurant_service)
):
    filters = {}
    if name:
        filters["name"] = name
    if restaurant_type:
        filters["restaurant_type"] = restaurant_type
    if min_rating is not None:
        filters["min_rating"] = min_rating
    if min_premium_score is not None:
        filters["min_premium_score"] = min_premium_score
        
    return await service.get_all(page=page, page_size=page_size, filters=filters)

@router.get("/search", response_model=RestaurantListResponse)
async def search_restaurants(
    q: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: RestaurantService = Depends(get_restaurant_service)
):
    return await service.search(query=q, page=page, page_size=page_size)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return await service.get_by_id(restaurant_id)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.delete("/{restaurant_id}")
async def delete_restaurant(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    success = await service.delete(restaurant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"success": True, "message": "Restaurant deleted successfully"}

@router.patch("/{restaurant_id}", response_model=RestaurantResponse)
async def update_restaurant(restaurant_id: int, update_data: RestaurantUpdate, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return await service.update(restaurant_id, update_data)
    except NotFoundException:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@router.post("/analyze/{restaurant_id}", response_model=RestaurantAnalysisResponse)
async def analyze_restaurant(restaurant_id: int):
    result = await analyze_single_restaurant(restaurant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return RestaurantAnalysisResponse(**result)

@router.post("/outreach/{restaurant_id}")
async def generate_outreach(restaurant_id: int):
    message = await generate_outreach_for_restaurant(restaurant_id)
    if not message:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return {"message": message}
