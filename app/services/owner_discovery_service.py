import json
import re

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.utils.prompts import OWNER_DISCOVERY_PROMPT
from app.schemas.intelligence import OwnerInfo
from app.utils.helpers import safe_float

logger = get_logger(__name__)

class OwnerDiscoveryService:
    """Service to discover owner and contact information for a restaurant."""
    
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def discover_owner_info(self, restaurant: Restaurant) -> OwnerInfo:
        """
        Attempts to extract or infer owner contact information using AI.
        
        Args:
            restaurant: The Restaurant instance.
            
        Returns:
            An OwnerInfo instance.
        """
        vision_text = ""
        if restaurant.vision_text:
            vision_text = json.dumps(restaurant.vision_text)
            
        prompt = OWNER_DISCOVERY_PROMPT.format(
            name=restaurant.name,
            website=restaurant.website or "None",
            phone=restaurant.phone or "None",
            formatted_address=restaurant.formatted_address or "None",
            vision_text=vision_text
        )
        
        try:
            response_text = await self.llm_service.generate_text(prompt)
            
            cleaned_text = re.sub(r'```json\s*', '', response_text)
            cleaned_text = re.sub(r'```\s*', '', cleaned_text).strip()
            
            data = json.loads(cleaned_text)
            
            # Calculate confidence based on found fields
            fields_found = sum(1 for key, val in data.items() if key != "confidence" and val and str(val).strip().lower() not in ["", "null", "none", "unknown"])
            total_fields = 8 # owner_name, manager_name, business_email, instagram, facebook, linkedin, website, phone
            calculated_confidence = float(fields_found) / float(total_fields) if total_fields > 0 else 0.0
            
            return OwnerInfo(
                owner_name=data.get("owner_name"),
                manager_name=data.get("manager_name"),
                business_email=data.get("business_email"),
                instagram=data.get("instagram"),
                facebook=data.get("facebook"),
                linkedin=data.get("linkedin"),
                website=data.get("website", restaurant.website),
                phone=data.get("phone", restaurant.phone),
                confidence=calculated_confidence
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response for owner discovery: {e}")
            raise LLMServiceError(f"Invalid JSON response from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"Error discovering owner info for restaurant {restaurant.id}: {e}")
            raise LLMServiceError(f"Owner discovery failed: {str(e)}")
