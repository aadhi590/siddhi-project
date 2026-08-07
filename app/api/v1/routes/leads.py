from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_dep, get_daily_insights_service, get_ai_decision_service
from app.services.daily_insights_service import DailyInsightsService
from app.services.ai_decision_service import AIDecisionService
from app.schemas.intelligence import TodayLeadsResponse, DailyInsights, AIDecisionResult

router = APIRouter(prefix="/leads", tags=["Leads & Insights"])

@router.get("/today", response_model=TodayLeadsResponse)
async def get_today_leads(
    limit: int = Query(20, description="Maximum number of leads to return"),
    session: AsyncSession = Depends(get_db_dep),
    service: DailyInsightsService = Depends(get_daily_insights_service)
) -> TodayLeadsResponse:
    """
    Get top leads for today.
    """
    try:
        return await service.get_today_leads(session, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", response_model=DailyInsights)
async def get_daily_insights(
    session: AsyncSession = Depends(get_db_dep),
    service: DailyInsightsService = Depends(get_daily_insights_service)
) -> DailyInsights:
    """
    Generate or retrieve daily insights.
    """
    try:
        return await service.generate_daily_insights(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/decision/{restaurant_id}", response_model=AIDecisionResult)
async def get_ai_decision(
    restaurant_id: int,
    session: AsyncSession = Depends(get_db_dep),
    service: AIDecisionService = Depends(get_ai_decision_service)
) -> AIDecisionResult:
    """
    Should we contact this restaurant?
    """
    try:
        return await service.get_decision_for_restaurant(session, restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
