import json
import re
from typing import Dict, Any, List

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.schemas.reports import BrandingScoreResult
from app.utils.prompts import BRANDING_SCORE_PROMPT

logger = get_logger(__name__)

def _extract_json(text: str) -> dict:
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return json.loads(text.strip())

class BrandingScoreService:
    """Service to calculate the branding score of a restaurant."""

    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def calculate_branding_score(self, restaurant: Restaurant) -> BrandingScoreResult:
        """Calculate branding score either via LLM (if vision data) or algorithmically."""
        has_vision = bool(restaurant.vision_labels or restaurant.vision_objects or restaurant.vision_text)

        if has_vision:
            prompt = BRANDING_SCORE_PROMPT.format(
                name=restaurant.name,
                vision_labels=json.dumps(restaurant.vision_labels or {}),
                vision_objects=json.dumps(restaurant.vision_objects or {}),
                vision_text=json.dumps(restaurant.vision_text or {})
            )
            try:
                response_text = await self.llm_service.generate_text(prompt)
                data = _extract_json(response_text)
                return BrandingScoreResult(
                    score=float(data.get("score", 50.0)),
                    confidence=float(data.get("confidence", 85.0)),
                    evidence=data.get("evidence", ["Vision data used for branding analysis."]),
                    reasons=data.get("reasons", [])
                )
            except Exception as e:
                logger.error(f"Failed to analyze branding with LLM for restaurant {restaurant.id}: {e}")
                # Fallback to algorithmic below
        
        # Algorithmic calculation
        score = 0.0
        evidence = []
        reasons = []
        available_signals = 0
        total_signals = 7

        if restaurant.website:
            score += 20
            available_signals += 1
            evidence.append("website_presence: +20")
            reasons.append("Has a dedicated website.")

        has_insta = restaurant.website and 'instagram.com' in restaurant.website
        if has_insta:
            score += 15
            available_signals += 1
            evidence.append("instagram_presence: +15")
            reasons.append("Instagram profile detected.")

        if restaurant.photo_reference:
            score += 15
            available_signals += 1
            evidence.append("photo_available: +15")
            reasons.append("Has high quality Google Maps photo.")

        if restaurant.rating is not None:
            available_signals += 1
            if restaurant.rating > 4.0:
                score += 15
                evidence.append("rating_quality: +15")
                reasons.append("High ratings indicate good brand perception.")

        if restaurant.price_level is not None:
            available_signals += 1
            if restaurant.price_level > 2:
                score += 10
                evidence.append("price_positioning: +10")
                reasons.append("Premium pricing positions brand highly.")

        if restaurant.name and len(restaurant.name) > 3:
            available_signals += 1
            generic_names = ['restaurant', 'cafe', 'diner', 'food']
            if not any(g == restaurant.name.lower() for g in generic_names):
                score += 10
                evidence.append("name_quality: +10")
                reasons.append("Unique and non-generic name.")

        if restaurant.user_rating_count is not None:
            available_signals += 1
            if restaurant.user_rating_count > 50:
                score += 15
                evidence.append("review_volume: +15")
                reasons.append("Substantial review volume establishes brand presence.")

        confidence = (available_signals / total_signals) * 100 if total_signals > 0 else 0
        score = min(score, 100.0)

        return BrandingScoreResult(
            score=score,
            confidence=confidence,
            evidence=evidence,
            reasons=reasons
        )
