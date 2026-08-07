from typing import Dict, Any
from app.database.session import get_db_session
from app.repositories.restaurant_repository import RestaurantRepository
from app.background.scanner import scanner
from app.services.llm_service import get_llm_service
from app.services.google_places_service import GooglePlacesService
from app.core.config import get_settings

async def analyze_single_restaurant(restaurant_id: int) -> Dict[str, Any]:
    await scanner.process_restaurant_pipeline(restaurant_id)
    async with get_db_session() as session:
        repo = RestaurantRepository(session)
        restaurant = await repo.get_by_id(restaurant_id)
        if not restaurant:
            return {"error": "Not found"}
        return {
            "ai_summary": restaurant.ai_summary,
            "premium_score": restaurant.premium_score,
            "collaboration_score": restaurant.collaboration_score
        }

async def generate_outreach_for_restaurant(restaurant_id: int) -> str:
    async with get_db_session() as session:
        repo = RestaurantRepository(session)
        restaurant = await repo.get_by_id(restaurant_id)
        if not restaurant:
            return ""
            
        llm = get_llm_service()
        outreach = await llm.generate_outreach(restaurant)
        
        await repo.update(restaurant.id, {"outreach_message": outreach})
        return outreach

async def rescan_restaurant(restaurant_id: int) -> Dict[str, Any]:
    settings = get_settings()
    async with get_db_session() as session:
        repo = RestaurantRepository(session)
        restaurant = await repo.get_by_id(restaurant_id)
        if not restaurant or not restaurant.place_id:
            return {"error": "Not found or missing place_id"}
            
        places_service = GooglePlacesService(api_key=settings.GOOGLE_PLACES_API_KEY)
        place_details = await places_service.get_place_details(restaurant.place_id)
        if place_details:
            update_data = {
                "name": place_details.get("name", restaurant.name),
                "rating": place_details.get("rating", restaurant.rating),
                "user_rating_count": place_details.get("user_ratings_total", restaurant.user_rating_count),
                "business_status": place_details.get("business_status", restaurant.business_status),
            }
            photos = place_details.get("photos", [])
            if photos:
                update_data["photo_reference"] = photos[0].get("photo_reference")
                
            await repo.update(restaurant.id, update_data)
            
    await scanner.process_restaurant_pipeline(restaurant_id)
    return {"status": "success"}
