import json
import re

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.utils.prompts import OUTREACH_BUNDLE_PROMPT
from app.schemas.intelligence import OutreachBundle

logger = get_logger(__name__)

class OutreachGeneratorService:
    """Service to generate outreach content using AI."""
    
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def generate_all_outreach(self, restaurant: Restaurant) -> OutreachBundle:
        """
        Generates various outreach messages tailored to the given restaurant.
        
        Args:
            restaurant: The Restaurant instance.
            
        Returns:
            An OutreachBundle containing generated messages.
        """
        prompt = OUTREACH_BUNDLE_PROMPT.format(
            name=restaurant.name,
            restaurant_type=restaurant.restaurant_type or "Unknown",
            strengths=restaurant.strengths or "Unknown",
            weaknesses=restaurant.weaknesses or "Unknown",
            opening_status=restaurant.opening_status or "Unknown",
            target_audience=restaurant.target_audience or "Unknown",
            ai_summary=restaurant.ai_summary or "None",
            collaboration_opportunities=restaurant.collaboration_opportunities or "Unknown",
            opportunity_score=restaurant.opportunity_score or 0.0,
            website=restaurant.website or "None",
            phone=restaurant.phone or "None",
            rating=restaurant.rating or 0.0
        )
        
        try:
            response_text = await self.llm_service.generate_text(prompt)
            
            # Clean up markdown code fences if present
            cleaned_text = re.sub(r'```json\s*', '', response_text)
            cleaned_text = re.sub(r'```\s*', '', cleaned_text).strip()
            
            data = json.loads(cleaned_text)
            
            return OutreachBundle(
                cold_email=data.get("cold_email", ""),
                instagram_dm=data.get("instagram_dm", ""),
                whatsapp_message=data.get("whatsapp_message", ""),
                phone_script=data.get("phone_script", ""),
                linkedin_message=data.get("linkedin_message", ""),
                opening_congrats_message=data.get("opening_congrats_message", ""),
                marketing_proposal=data.get("marketing_proposal", "")
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for outreach generation: {e}")
            raise LLMServiceError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating outreach for restaurant {restaurant.id}: {e}")
            raise LLMServiceError(f"Outreach generation failed: {str(e)}")
