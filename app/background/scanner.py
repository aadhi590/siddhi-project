import asyncio
from typing import Dict, Any, Optional
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import get_db_session
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.google_places_service import GooglePlacesService
from app.services.google_vision_service import GoogleVisionService
from app.services.llm_service import get_llm_service
from app.services.restaurant_service import RestaurantService
from app.services.photo_service import PhotoService
from app.services.lead_scoring_service import LeadScoringService
from app.utils.helpers import generate_uuid, now_utc
from app.schemas.restaurant import RestaurantUpdate

logger = get_logger(__name__)

class RestaurantScanner:
    def __init__(self):
        self.logger = logger
        self.settings = get_settings()
        self.scan_results: Dict[str, Dict[str, Any]] = {}

    async def start_scan(self, latitude: float, longitude: float, radius: int = 5000, keyword: str = "restaurant", max_results: int = 20) -> str:
        scan_id = generate_uuid()
        self.scan_results[scan_id] = {
            "status": "pending",
            "total_found": 0,
            "processed": 0,
            "error": None,
            "started_at": now_utc().isoformat()
        }
        asyncio.create_task(self._run_scan(scan_id, latitude, longitude, radius, keyword, max_results))
        return scan_id

    def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        return self.scan_results.get(scan_id)

    async def _run_scan(self, scan_id: str, latitude: float, longitude: float, radius: int, keyword: str, max_results: int) -> None:
        try:
            self.scan_results[scan_id]["status"] = "in_progress"
            places_service = GooglePlacesService(api_key=self.settings.GOOGLE_PLACES_API_KEY)
            
            places = await places_service.search_nearby(latitude, longitude, radius, keyword)
            places_to_process = places[:max_results]
            
            self.scan_results[scan_id]["total_found"] = len(places_to_process)
            
            for place in places_to_process:
                try:
                    place_details = await places_service.get_place_details(place.get("place_id", ""))
                    if not place_details:
                        continue
                    
                    async with get_db_session() as session:
                        repo = RestaurantRepository(session)
                        service = RestaurantService(repo)
                        
                        existing = await repo.get_by_place_id(place_details.get("place_id", ""))
                        if existing:
                            await repo.mark_seen(existing.id)
                            self.scan_results[scan_id]["processed"] += 1
                            continue
                            
                        restaurant_data = {
                            "place_id": place_details.get("place_id"),
                            "name": place_details.get("name"),
                            "formatted_address": place_details.get("formatted_address"),
                            "latitude": place_details.get("geometry", {}).get("location", {}).get("lat"),
                            "longitude": place_details.get("geometry", {}).get("location", {}).get("lng"),
                            "phone": place_details.get("formatted_phone_number"),
                            "website": place_details.get("website"),
                            "rating": place_details.get("rating"),
                            "user_rating_count": place_details.get("user_ratings_total"),
                            "business_status": place_details.get("business_status"),
                            "types": place_details.get("types", []),
                            "opening_hours": place_details.get("opening_hours", {}),
                            "google_maps_url": place_details.get("url"),
                            "price_level": place_details.get("price_level"),
                        }
                        
                        photos = place_details.get("photos", [])
                        if photos:
                            restaurant_data["photo_reference"] = photos[0].get("photo_reference")
                            
                        restaurant = await service.create_restaurant(RestaurantUpdate(**restaurant_data))
                        await self.process_restaurant_pipeline(restaurant.id)
                        
                except Exception as e:
                    self.logger.error(f"Error processing place: {str(e)}")
                finally:
                    self.scan_results[scan_id]["processed"] += 1
                    
            self.scan_results[scan_id]["status"] = "completed"
            
        except Exception as e:
            self.logger.error(f"Scan {scan_id} failed: {str(e)}")
            self.scan_results[scan_id]["status"] = "failed"
            self.scan_results[scan_id]["error"] = str(e)

    async def process_restaurant_pipeline(self, restaurant_id: int) -> None:
        async with get_db_session() as session:
            try:
                repo = RestaurantRepository(session)
                restaurant = await repo.get_by_id(restaurant_id)
                if not restaurant:
                    return
                    
                places_service = GooglePlacesService(api_key=self.settings.GOOGLE_PLACES_API_KEY)
                photo_service = PhotoService(places_service)
                vision_service = GoogleVisionService(api_key=self.settings.GOOGLE_VISION_API_KEY)
                llm_service = get_llm_service()
                scoring_service = LeadScoringService()
                
                vision_data = None
                if restaurant.photo_reference:
                    try:
                        photo_bytes = await photo_service.download_photo(restaurant.photo_reference)
                        if photo_bytes:
                            vision_data = await vision_service.analyze_image(photo_bytes)
                            await repo.update(restaurant.id, {
                                "vision_labels": vision_data.get("labels"),
                                "vision_objects": vision_data.get("objects"),
                                "vision_text": vision_data.get("text"),
                                "vision_landmarks": vision_data.get("landmarks")
                            })
                    except Exception as e:
                        self.logger.error(f"Photo/Vision failed for {restaurant_id}: {str(e)}")
                
                try:
                    analysis = await llm_service.analyze_restaurant(restaurant, vision_data)
                    await repo.update(restaurant.id, {
                        "restaurant_type": analysis.get("restaurant_type"),
                        "ambience": analysis.get("ambience"),
                        "target_audience": analysis.get("target_audience"),
                        "ai_summary": analysis.get("ai_summary")
                    })
                except Exception as e:
                    self.logger.error(f"LLM analysis failed for {restaurant_id}: {str(e)}")
                    
                try:
                    restaurant = await repo.get_by_id(restaurant_id)
                    if restaurant:
                        scores = scoring_service.calculate_scores(restaurant)
                        await repo.update(restaurant.id, {
                            "premium_score": scores.get("premium_score"),
                            "collaboration_score": scores.get("collaboration_score"),
                            "collaboration_reason": scores.get("collaboration_reason")
                        })
                except Exception as e:
                    self.logger.error(f"Scoring failed for {restaurant_id}: {str(e)}")
                    
                try:
                    restaurant = await repo.get_by_id(restaurant_id)
                    if restaurant:
                        outreach = await llm_service.generate_outreach(restaurant)
                        await repo.update(restaurant.id, {"outreach_message": outreach})
                except Exception as e:
                    self.logger.error(f"Outreach failed for {restaurant_id}: {str(e)}")
                    
            except Exception as e:
                self.logger.error(f"Pipeline failed for {restaurant_id}: {str(e)}")

scanner = RestaurantScanner()
