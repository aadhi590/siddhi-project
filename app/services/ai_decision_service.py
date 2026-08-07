import json
import re

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.utils.prompts import AI_DECISION_PROMPT
from app.schemas.intelligence import AIDecisionResult
from app.utils.helpers import safe_float

logger = get_logger(__name__)

class AIDecisionService:
    """Service to determine if a restaurant should be contacted today."""
    
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def should_contact_today(self, restaurant: Restaurant) -> AIDecisionResult:
        """
        Evaluates whether the given restaurant is a good candidate to contact today.
        
        Args:
            restaurant: The Restaurant instance.
            
        Returns:
            An AIDecisionResult instance.
        """
        prompt = AI_DECISION_PROMPT.format(
            name=restaurant.name,
            rating=restaurant.rating or 0.0,
            reviews=restaurant.user_rating_count or 0,
            opening_status=restaurant.opening_status or "Unknown",
            new_restaurant_score=restaurant.new_restaurant_score or 0.0,
            opportunity_score=restaurant.opportunity_score or 0.0,
            premium_score=restaurant.premium_score or 0.0,
            collaboration_score=restaurant.collaboration_score or 0.0,
            competition_score=restaurant.competition_score or "Unknown",
            website=restaurant.website or "None",
            instagram_presence=restaurant.instagram_presence or "Unknown",
            ai_summary=restaurant.ai_summary or "None",
            strengths=restaurant.strengths or "None",
            weaknesses=restaurant.weaknesses or "None"
        )
        
        try:
            response_text = await self.llm_service.generate_text(prompt)
            
            cleaned_text = re.sub(r'```json\s*', '', response_text)
            cleaned_text = re.sub(r'```\s*', '', cleaned_text).strip()
            
            data = json.loads(cleaned_text)
            
            return AIDecisionResult(
                decision=data.get("decision", "MAYBE"),
                confidence=safe_float(data.get("confidence", 0.0)),
                reasoning=data.get("reasoning", "No reasoning provided."),
                expected_roi=data.get("expected_roi", "Unknown")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for AI decision: {e}")
            raise LLMServiceError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating AI decision for restaurant {restaurant.id}: {e}")
            raise LLMServiceError(f"AI decision generation failed: {str(e)}")
