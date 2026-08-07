import json
from typing import Optional
from app.database.models import Restaurant
from app.schemas.intelligence import RestaurantIntelligenceResult
from app.services.llm_service import BaseLLMService
from app.utils.prompts import RESTAURANT_INTELLIGENCE_PROMPT

class RestaurantIntelligenceService:
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def analyze_restaurant(self, restaurant: Restaurant, vision_data: Optional[dict] = None) -> RestaurantIntelligenceResult:
        """Analyzes restaurant data utilizing LLM to generate intelligent insights."""
        vision_labels = vision_data.get("labels", []) if vision_data else getattr(restaurant, "vision_labels", [])
        vision_objects = vision_data.get("objects", []) if vision_data else getattr(restaurant, "vision_objects", [])
        vision_text = vision_data.get("text", []) if vision_data else getattr(restaurant, "vision_text", [])
        
        prompt = RESTAURANT_INTELLIGENCE_PROMPT.format(
            name=restaurant.name,
            address=restaurant.formatted_address,
            types=restaurant.types,
            rating=restaurant.rating,
            price_level=restaurant.price_level,
            user_rating_count=restaurant.user_rating_count,
            vision_labels=vision_labels,
            vision_objects=vision_objects,
            vision_text=vision_text,
            website=restaurant.website,
            phone=restaurant.phone,
            business_status=restaurant.business_status
        )

        response_text = await self.llm_service.generate_text(prompt)
        
        try:
            # Robust JSON parsing
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()
                
            data = json.loads(clean_text)
            return RestaurantIntelligenceResult(**data)
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")
