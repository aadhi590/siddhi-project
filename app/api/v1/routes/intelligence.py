from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import (
    get_db_dep,
    get_intelligence_service,
    get_collaboration_intelligence_service,
    get_opening_detector_service,
    get_outreach_generator_service,
    get_ai_decision_service,
    get_owner_discovery_service,
    get_competitor_analysis_service,
    get_opportunity_score_service,
    get_new_restaurant_service
)
from app.schemas.intelligence import OutreachBundle, CompetitorAnalysisResult, OwnerInfo
from app.services.intelligence_service import RestaurantIntelligenceService
from app.services.collaboration_intelligence_service import CollaborationIntelligenceService
from app.services.opening_detector_service import OpeningSoonDetectorService
from app.services.outreach_generator_service import OutreachGeneratorService
from app.services.ai_decision_service import AIDecisionService
from app.services.owner_discovery_service import OwnerDiscoveryService
from app.services.competitor_analysis_service import CompetitorAnalysisService
from app.services.opportunity_score_service import OpportunityScoreService
from app.services.new_restaurant_service import NewRestaurantDetectionService

router = APIRouter(prefix="/intelligence", tags=["Intelligence"])

@router.post("/analyze/{restaurant_id}")
async def analyze_restaurant(
    restaurant_id: int,
    session: AsyncSession = Depends(get_db_dep),
    intelligence: RestaurantIntelligenceService = Depends(get_intelligence_service),
    opening: OpeningSoonDetectorService = Depends(get_opening_detector_service),
    collaboration: CollaborationIntelligenceService = Depends(get_collaboration_intelligence_service),
    opportunity: OpportunityScoreService = Depends(get_opportunity_score_service),
    competitor: CompetitorAnalysisService = Depends(get_competitor_analysis_service),
    new_restaurant: NewRestaurantDetectionService = Depends(get_new_restaurant_service),
    ai_decision: AIDecisionService = Depends(get_ai_decision_service),
    owner: OwnerDiscoveryService = Depends(get_owner_discovery_service)
) -> dict[str, Any]:
    """
    Run full intelligence analysis on a restaurant.
    """
    try:
        results = {
            "intelligence": await intelligence.analyze(session, restaurant_id),
            "opening_soon": await opening.detect(session, restaurant_id),
            "collaboration": await collaboration.analyze(session, restaurant_id),
            "opportunity_score": await opportunity.calculate(session, restaurant_id),
            "competitor_analysis": await competitor.analyze(session, restaurant_id),
            "new_restaurant": await new_restaurant.detect(session, restaurant_id),
            "ai_decision": await ai_decision.get_decision_for_restaurant(session, restaurant_id),
            "owner": await owner.discover(session, restaurant_id)
        }
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/outreach/{restaurant_id}", response_model=OutreachBundle)
async def generate_outreach(
    restaurant_id: int,
    session: AsyncSession = Depends(get_db_dep),
    outreach: OutreachGeneratorService = Depends(get_outreach_generator_service)
) -> OutreachBundle:
    """
    Generate full outreach bundle for a restaurant.
    """
    try:
        return await outreach.generate_bundle(session, restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/competitors/{restaurant_id}", response_model=CompetitorAnalysisResult)
async def analyze_competitors(
    restaurant_id: int,
    session: AsyncSession = Depends(get_db_dep),
    competitor: CompetitorAnalysisService = Depends(get_competitor_analysis_service)
) -> CompetitorAnalysisResult:
    """
    Competitor analysis for a restaurant.
    """
    try:
        return await competitor.analyze(session, restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/owner/{restaurant_id}", response_model=OwnerInfo)
async def discover_owner(
    restaurant_id: int,
    session: AsyncSession = Depends(get_db_dep),
    owner: OwnerDiscoveryService = Depends(get_owner_discovery_service)
) -> OwnerInfo:
    """
    Discover owner information for a restaurant.
    """
    try:
        return await owner.discover(session, restaurant_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
