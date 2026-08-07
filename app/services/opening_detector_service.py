from typing import List, Optional
from app.database.models import Restaurant
from app.schemas.intelligence import OpeningStatusResult
from app.services.llm_service import BaseLLMService
from app.utils.prompts import OPENING_DETECTION_PROMPT
import json

class OpeningSoonDetectorService:
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service
        self.keywords = ['Opening Soon', 'Grand Opening', 'Launching', 'Soft Opening', 'Coming Soon', 'New Branch']

    def _check_text_signals(self, text: str) -> List[str]:
        """Checks for predefined opening-related keywords in text."""
        if not text:
            return []
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw.lower() in text_lower]

    async def detect_opening_status(self, restaurant: Restaurant) -> OpeningStatusResult:
        """Detects whether a restaurant is opening soon or newly opened."""
        signals = []
        
        if restaurant.business_status and 'OPENING' in restaurant.business_status.upper():
            signals.append("Business status indicates opening")
            
        if restaurant.name:
            signals.extend(self._check_text_signals(restaurant.name))
            
        if hasattr(restaurant, 'vision_text') and restaurant.vision_text:
            if isinstance(restaurant.vision_text, str):
                signals.extend(self._check_text_signals(restaurant.vision_text))
            elif isinstance(restaurant.vision_text, list):
                signals.extend(self._check_text_signals(" ".join(restaurant.vision_text)))
                
        if restaurant.website:
            signals.extend(self._check_text_signals(restaurant.website))
            
        if restaurant.user_rating_count is not None and restaurant.user_rating_count < 10:
            signals.append("Very low review count suggests recently opened")

        if signals:
            status = "OPENING_SOON" if "Business status indicates opening" in signals else "NEWLY_OPENED"
            return OpeningStatusResult(
                status=status,
                confidence=0.8,
                signals=list(set(signals))
            )

        # If ambiguous, use LLM
        prompt = OPENING_DETECTION_PROMPT.format(
            name=restaurant.name,
            business_status=restaurant.business_status,
            reviews=restaurant.user_rating_count
        )
        
        try:
            response_text = await self.llm_service.generate_text(prompt)
            # Remove markdown code fences if present
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            data = json.loads(response_text)
            return OpeningStatusResult(
                status=data.get("status", "UNKNOWN"),
                confidence=float(data.get("confidence", 0.0)),
                signals=data.get("signals", [])
            )
        except Exception:
            return OpeningStatusResult(status="UNKNOWN", confidence=0.0, signals=[])
