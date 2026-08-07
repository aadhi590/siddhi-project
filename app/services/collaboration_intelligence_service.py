import json
from typing import Optional
from app.database.models import Restaurant
from app.schemas.intelligence import CollaborationIntelligenceResult, CollaborationOpportunity
from app.services.llm_service import BaseLLMService
from app.utils.prompts import COLLABORATION_INTELLIGENCE_PROMPT

class CollaborationIntelligenceService:
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def analyze_collaboration(self, restaurant: Restaurant, intelligence: Optional[dict] = None) -> CollaborationIntelligenceResult:
        """Analyzes collaboration opportunities using LLM."""
        prompt = COLLABORATION_INTELLIGENCE_PROMPT.format(
            name=restaurant.name,
            types=restaurant.types,
            rating=restaurant.rating,
            intelligence=json.dumps(intelligence) if intelligence else "{}"
        )

        response_text = await self.llm_service.generate_text(prompt)
        
        try:
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3].strip()
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3].strip()
                
            data = json.loads(clean_text)
            
            opportunities = []
            total_score = 0
            for opp in data.get("opportunities", []):
                opportunities.append(CollaborationOpportunity(**opp))
                total_score += opp.get("probability", 0)
                
            overall_score = total_score / len(opportunities) if opportunities else 0.0
            
            top_rec = max(opportunities, key=lambda x: x.probability).type if opportunities else "Unknown"
            
            return CollaborationIntelligenceResult(
                opportunities=opportunities,
                overall_score=overall_score,
                top_recommendation=top_rec
            )
        except Exception as e:
            raise Exception(f"Failed to parse LLM response for collaboration: {str(e)}")
