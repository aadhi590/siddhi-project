from typing import Any
from pydantic import BaseModel
import json

from app.database.models import Restaurant
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, VisionAnalysisResult, LLMAnalysisResult
from app.core.exceptions import NotFoundException
from app.utils.helpers import build_google_maps_url

class RestaurantService:
    """Orchestrates business logic for restaurant entities."""

    def __init__(self, repository: RestaurantRepository) -> None:
        """Initialize with a RestaurantRepository."""
        self.repository = repository

    async def get_restaurant(self, restaurant_id: int) -> Restaurant:
        """Get a restaurant by ID or raise NotFoundException."""
        restaurant = await self.repository.get_by_id(restaurant_id)
        if not restaurant:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return restaurant

    async def get_restaurant_by_place_id(self, place_id: str) -> Restaurant | None:
        """Get a restaurant by Google place_id."""
        return await self.repository.get_by_place_id(place_id)

    async def list_restaurants(self, page: int = 1, page_size: int = 50, filters: dict[str, Any] | None = None) -> tuple[list[Restaurant], int]:
        """List restaurants with pagination and optional filters."""
        skip = (page - 1) * page_size
        return await self.repository.get_all(skip=skip, limit=page_size, filters=filters)

    async def create_restaurant(self, data: RestaurantCreate) -> Restaurant:
        """Create a new restaurant."""
        return await self.repository.create(data.model_dump())

    async def update_restaurant(self, restaurant_id: int, data: RestaurantUpdate) -> Restaurant:
        """Update an existing restaurant."""
        update_data = data.model_dump(exclude_unset=True)
        updated_restaurant = await self.repository.update(restaurant_id, update_data)
        if not updated_restaurant:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found to update.")
        return updated_restaurant

    async def delete_restaurant(self, restaurant_id: int) -> bool:
        """Delete a restaurant by ID."""
        success = await self.repository.delete(restaurant_id)
        if not success:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found to delete.")
        return True

    async def save_from_places(self, places_data: list[dict[str, Any]]) -> list[Restaurant]:
        """Transform raw Google Places API data and upsert into the DB."""
        formatted_data = []
        for place in places_data:
            geom = place.get("geometry", {}).get("location", {})
            photos = place.get("photos", [])
            photo_ref = photos[0].get("photo_reference") if photos else None
            
            rest_dict = {
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "formatted_address": place.get("formatted_address") or place.get("vicinity"),
                "latitude": geom.get("lat"),
                "longitude": geom.get("lng"),
                "phone": place.get("formatted_phone_number"),
                "website": place.get("website"),
                "rating": place.get("rating"),
                "user_rating_count": place.get("user_ratings_total"),
                "business_status": place.get("business_status"),
                "types": place.get("types"),
                "opening_hours": place.get("opening_hours"),
                "google_maps_url": place.get("url") or build_google_maps_url(place.get("place_id")),
                "price_level": place.get("price_level"),
                "photo_reference": photo_ref,
            }
            formatted_data.append(rest_dict)

        return await self.repository.save_many(formatted_data)

    async def update_vision_data(self, restaurant_id: int, vision_data: VisionAnalysisResult) -> Restaurant:
        """Update a restaurant with parsed Vision API results."""
        update_dict = {
            "vision_labels": [label for label in vision_data.labels],
            "vision_objects": [obj for obj in vision_data.objects],
            "vision_text": vision_data.text,
            "vision_landmarks": []  # Extend VisionAnalysisResult if landmarks are parsed
        }
        updated = await self.repository.update(restaurant_id, update_dict)
        if not updated:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return updated

    async def update_ai_analysis(self, restaurant_id: int, analysis: LLMAnalysisResult) -> Restaurant:
        """Update a restaurant with AI Analysis."""
        update_dict = {
            "restaurant_type": analysis.restaurant_type,
            "ambience": analysis.ambience,
            "target_audience": analysis.target_audience,
            "ai_summary": analysis.ai_summary
        }
        updated = await self.repository.update(restaurant_id, update_dict)
        if not updated:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return updated

    async def update_outreach(self, restaurant_id: int, message: str) -> Restaurant:
        """Update the generated outreach message."""
        updated = await self.repository.update(restaurant_id, {"outreach_message": message})
        if not updated:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return updated

    async def update_scores(self, restaurant_id: int, premium_score: float, collaboration_score: float, collaboration_reason: str) -> Restaurant:
        """Update lead scoring data."""
        update_dict = {
            "premium_score": premium_score,
            "collaboration_score": collaboration_score,
            "collaboration_reason": collaboration_reason
        }
        updated = await self.repository.update(restaurant_id, update_dict)
        if not updated:
            raise NotFoundException(f"Restaurant with ID {restaurant_id} not found.")
        return updated

    async def search_restaurants(self, query: str, page: int = 1, page_size: int = 50) -> tuple[list[Restaurant], int]:
        """Perform text search with pagination."""
        skip = (page - 1) * page_size
        return await self.repository.search(query, skip=skip, limit=page_size)
