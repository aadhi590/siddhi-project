from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.dependencies import (
    get_db_dep, get_intelligence_service, get_collaboration_intelligence_service,
    get_opening_detector_service, get_ai_decision_service, get_owner_discovery_service,
    get_competitor_analysis_service, get_opportunity_score_service, get_new_restaurant_service,
    get_daily_insights_service, get_marketing_readiness_service, get_photo_intelligence_service,
    get_business_profile_service, get_branding_score_service, get_opportunity_index_service,
    get_restaurant_repository
)
from app.schemas.reports import TodayLeadsResponseV2, DailySalesReport, SalesReportLead
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.marketing_readiness_service import MarketingReadinessService
from app.services.photo_intelligence_service import PhotoIntelligenceService
from app.services.business_profile_service import BusinessProfileService
from app.services.branding_score_service import BrandingScoreService
from app.services.opportunity_index_service import OpportunityIndexService
from app.services.daily_insights_service import DailyInsightsService

router = APIRouter(prefix="/reports", tags=["Reports & Sales"])

@router.get("/today-leads", response_model=TodayLeadsResponseV2)
async def get_today_leads(
    limit: int = Query(20, ge=1, le=100),
    daily_insights_service: DailyInsightsService = Depends(get_daily_insights_service)
):
    """Get today's top leads."""
    return await daily_insights_service.get_today_leads(limit=limit)

@router.get("/daily-sales-report", response_model=DailySalesReport)
async def get_daily_sales_report(
    daily_insights_service: DailyInsightsService = Depends(get_daily_insights_service)
):
    """Generate daily sales report with area breakdown."""
    return await daily_insights_service.generate_daily_sales_report()

@router.post("/analyze-full/{restaurant_id}")
async def run_full_analysis(
    restaurant_id: int,
    repo: RestaurantRepository = Depends(get_restaurant_repository),
    marketing_readiness_service: MarketingReadinessService = Depends(get_marketing_readiness_service),
    photo_intelligence_service: PhotoIntelligenceService = Depends(get_photo_intelligence_service),
    business_profile_service: BusinessProfileService = Depends(get_business_profile_service),
    branding_score_service: BrandingScoreService = Depends(get_branding_score_service),
    opportunity_index_service: OpportunityIndexService = Depends(get_opportunity_index_service)
) -> dict[str, Any]:
    """Run full Phase 3 analysis pipeline on a single restaurant."""
    restaurant = await repo.get_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    marketing_readiness = await marketing_readiness_service.calculate_readiness(restaurant)
    photo_intel = await photo_intelligence_service.analyze_photos(restaurant)
    business_profile = await business_profile_service.generate_profile(restaurant)
    branding_score = await branding_score_service.calculate_branding_score(restaurant)

    restaurant.marketing_readiness_score = marketing_readiness
    restaurant.photo_intelligence = photo_intel
    restaurant.business_profile = business_profile
    restaurant.branding_score = branding_score

    await repo.update(restaurant)

    opportunity_index = await opportunity_index_service.calculate_index(restaurant)
    restaurant.opportunity_index = opportunity_index
    await repo.update(restaurant)

    return {
        "marketing_readiness_score": marketing_readiness,
        "photo_intelligence": photo_intel,
        "business_profile": business_profile,
        "branding_score": branding_score,
        "opportunity_index": opportunity_index
    }
