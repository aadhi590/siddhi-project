import json
import re
from typing import Dict, Any, List

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.schemas.reports import BusinessProfileResult
from app.utils.prompts import BUSINESS_PROFILE_PROMPT

logger = get_logger(__name__)

def _extract_json(text: str) -> dict:
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return json.loads(text.strip())

class BusinessProfileService:
    """Service to generate a comprehensive business profile for a restaurant."""

    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def generate_profile(self, restaurant: Restaurant) -> BusinessProfileResult:
        """Generate a complete business profile using available data."""
        restaurant_data = {
            "name": restaurant.name,
            "formatted_address": restaurant.formatted_address,
            "types": restaurant.types,
            "rating": restaurant.rating,
            "price_level": restaurant.price_level,
            "user_rating_count": restaurant.user_rating_count,
            "website": restaurant.website,
            "phone": restaurant.phone,
            "business_status": restaurant.business_status,
            "opening_hours": restaurant.opening_hours,
            "vision_labels": restaurant.vision_labels,
            "vision_objects": restaurant.vision_objects,
            "vision_text": restaurant.vision_text,
            "cuisine_type": getattr(restaurant, "cuisine_type", "Unknown"),
            "restaurant_style": getattr(restaurant, "restaurant_style", "Unknown"),
            "estimated_spending": getattr(restaurant, "estimated_spending", "Unknown"),
            "marketing_maturity": getattr(restaurant, "marketing_maturity", "Unknown"),
            "branding_quality": getattr(restaurant, "branding_quality", "Unknown"),
        }

        # Calculate evidence of data sources
        evidence = []
        for key, value in restaurant_data.items():
            if value:
                evidence.append(f"{key} data available")

        confidence_score = (len(evidence) / len(restaurant_data)) * 100

        prompt = BUSINESS_PROFILE_PROMPT.format(
            restaurant_data=json.dumps(restaurant_data, indent=2)
        )

        try:
            response_text = await self.llm_service.generate_text(prompt)
            data = _extract_json(response_text)
            
            return BusinessProfileResult(
                profile_summary=data.get("profile_summary", ""),
                target_audience=data.get("target_audience", []),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                confidence=confidence_score,
                evidence=evidence
            )
        except Exception as e:
            logger.error(f"Failed to generate profile for restaurant {restaurant.id}: {e}")
            return BusinessProfileResult(
                profile_summary="Profile generation failed.",
                target_audience=[],
                strengths=[],
                weaknesses=[],
                confidence=10.0,
                evidence=evidence + [f"Error: {str(e)}"]
            )
