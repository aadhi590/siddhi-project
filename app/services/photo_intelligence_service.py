import json
import re
from typing import Dict, Any, List

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.schemas.reports import PhotoIntelligenceResult
from app.utils.prompts import PHOTO_INTELLIGENCE_PROMPT

logger = get_logger(__name__)

def _extract_json(text: str) -> dict:
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return json.loads(text.strip())

class PhotoIntelligenceService:
    """Service to analyze restaurant photos via AI."""

    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def analyze_photos(self, restaurant: Restaurant) -> PhotoIntelligenceResult:
        """Analyze restaurant vision data to extract intelligence."""
        has_labels = bool(restaurant.vision_labels)
        has_objects = bool(restaurant.vision_objects)
        has_text = bool(restaurant.vision_text)

        if not (has_labels or has_objects or has_text):
            return PhotoIntelligenceResult(
                score=0.0,
                confidence=0.0,
                evidence=["No photo/vision data available"],
                reasons=[],
                insights={}
            )

        evidence = []
        if has_labels:
            evidence.append("Vision labels available.")
        if has_objects:
            evidence.append("Vision objects available.")
        if has_text:
            evidence.append("Vision text available.")

        prompt = PHOTO_INTELLIGENCE_PROMPT.format(
            restaurant_name=restaurant.name,
            vision_labels=json.dumps(restaurant.vision_labels or {}),
            vision_objects=json.dumps(restaurant.vision_objects or {}),
            vision_text=json.dumps(restaurant.vision_text or {})
        )

        try:
            response_text = await self.llm_service.generate_text(prompt)
            data = _extract_json(response_text)
            
            return PhotoIntelligenceResult(
                score=float(data.get("score", 50.0)),
                confidence=float(data.get("confidence", 80.0)),
                evidence=evidence + data.get("evidence", []),
                reasons=data.get("reasons", []),
                insights=data.get("insights", {})
            )
        except Exception as e:
            logger.error(f"Failed to analyze photos for restaurant {restaurant.id}: {e}")
            return PhotoIntelligenceResult(
                score=50.0,
                confidence=10.0,
                evidence=evidence + [f"Analysis failed: {str(e)}"],
                reasons=["Error during AI analysis"],
                insights={}
            )
