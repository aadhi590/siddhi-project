import json
import re
from datetime import datetime, date
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, and_

from app.core.logging import get_logger
from app.core.exceptions import LLMServiceError
from app.database.models import Restaurant
from app.services.llm_service import BaseLLMService
from app.utils.prompts import DAILY_SUMMARY_PROMPT
from app.utils.helpers import now_utc
from app.schemas.intelligence import TodayLeadItem, TodayLeadsResponse, DailyInsights

logger = get_logger(__name__)

class DailyInsightsService:
    """Service to generate daily intelligence insights and leads."""
    
    def __init__(self, llm_service: BaseLLMService) -> None:
        self.llm_service = llm_service

    async def generate_today_leads(self, session: AsyncSession, limit: int = 20) -> TodayLeadsResponse:
        """
        Generates a prioritized list of leads for today.
        
        Args:
            session: The database session.
            limit: Maximum number of leads to return.
            
        Returns:
            A TodayLeadsResponse containing the leads.
        """
        query = select(Restaurant).order_by(
            desc(Restaurant.opportunity_score),
            desc(Restaurant.new_restaurant_score),
            desc(Restaurant.premium_score)
        ).limit(limit * 2)
        
        result = await session.execute(query)
        restaurants = list(result.scalars().all())
        
        def get_status_priority(status: str | None) -> int:
            if status == "OPENING_SOON": return 0
            if status == "NEWLY_OPENED": return 1
            return 2
            
        restaurants.sort(key=lambda r: (
            get_status_priority(r.opening_status),
            -(r.opportunity_score or 0.0),
            -(r.new_restaurant_score or 0.0),
            -(r.premium_score or 0.0)
        ))
        
        top_restaurants = restaurants[:limit]
        
        items = []
        for r in top_restaurants:
            items.append(
                TodayLeadItem(
                    id=r.id,
                    name=r.name,
                    opportunity_score=r.opportunity_score or 0.0,
                    opening_status=r.opening_status,
                    ai_decision=r.ai_contact_decision,
                    ai_confidence=r.ai_decision_confidence or 0.0
                )
            )
            
        return TodayLeadsResponse(leads=items, count=len(items))

    async def generate_daily_insights(self, session: AsyncSession) -> DailyInsights:
        """
        Generates comprehensive daily insights grouped into categories and summarized by AI.
        
        Args:
            session: The database session.
            
        Returns:
            A DailyInsights instance.
        """
        today = now_utc().date()
        
        # best_leads
        res = await session.execute(select(Restaurant).order_by(desc(Restaurant.opportunity_score)).limit(10))
        best_leads = list(res.scalars().all())
        
        # top_premium
        res = await session.execute(select(Restaurant).order_by(desc(Restaurant.premium_score)).limit(10))
        top_premium = list(res.scalars().all())
        
        # most_likely_to_collaborate
        res = await session.execute(select(Restaurant).order_by(desc(Restaurant.collaboration_score)).limit(10))
        most_likely_to_collaborate = list(res.scalars().all())
        
        # opening_soon
        res = await session.execute(select(Restaurant).where(Restaurant.opening_status == "OPENING_SOON"))
        opening_soon = list(res.scalars().all())
        
        # high_roi
        res = await session.execute(
            select(Restaurant)
            .where(Restaurant.ai_contact_decision == "YES")
            .order_by(desc(Restaurant.ai_decision_confidence))
            .limit(10)
        )
        high_roi = list(res.scalars().all())
        
        # low_competition
        res = await session.execute(
            select(Restaurant)
            .where(Restaurant.competition_score == "Low")
            .limit(10)
        )
        low_competition = list(res.scalars().all())
        
        # Total count
        res = await session.execute(select(func.count(Restaurant.id)))
        total_restaurants = res.scalar() or 0
        
        # New today count
        res = await session.execute(
            select(func.count(Restaurant.id))
            .where(func.date(Restaurant.first_seen) == today)
        )
        new_today = res.scalar() or 0
        
        # AI Summary
        prompt = DAILY_SUMMARY_PROMPT.format(
            total_restaurants=total_restaurants,
            new_today=new_today,
            best_leads_count=len(best_leads),
            opening_soon_count=len(opening_soon),
            high_roi_count=len(high_roi)
        )
        
        summary = "Summary generation failed."
        try:
            summary = await self.llm_service.generate_text(prompt)
        except Exception as e:
            logger.error(f"Error generating daily summary: {e}")
            
        return DailyInsights(
            total_restaurants=total_restaurants,
            new_today=new_today,
            best_leads=[{"id": r.id, "name": r.name, "score": r.opportunity_score} for r in best_leads],
            top_premium=[{"id": r.id, "name": r.name, "score": r.premium_score} for r in top_premium],
            most_likely_to_collaborate=[{"id": r.id, "name": r.name, "score": r.collaboration_score} for r in most_likely_to_collaborate],
            opening_soon=[{"id": r.id, "name": r.name} for r in opening_soon],
            high_roi=[{"id": r.id, "name": r.name, "confidence": r.ai_decision_confidence} for r in high_roi],
            low_competition=[{"id": r.id, "name": r.name} for r in low_competition],
            ai_summary=summary
        )
