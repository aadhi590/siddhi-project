from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.follow_up_repository import FollowUpRepository
from app.services.restaurant_service import RestaurantService
from app.services.google_places_service import GooglePlacesService
from app.services.google_vision_service import GoogleVisionService
from app.services.llm_service import get_llm_service, BaseLLMService
from app.services.photo_service import PhotoService
from app.services.lead_scoring_service import LeadScoringService
from app.services.follow_up_service import FollowUpService
from app.services.intelligence_service import RestaurantIntelligenceService
from app.services.collaboration_intelligence_service import CollaborationIntelligenceService
from app.services.opening_detector_service import OpeningSoonDetectorService
from app.services.outreach_generator_service import OutreachGeneratorService
from app.services.ai_decision_service import AIDecisionService
from app.services.owner_discovery_service import OwnerDiscoveryService
from app.services.competitor_analysis_service import CompetitorAnalysisService
from app.services.opportunity_score_service import OpportunityScoreService
from app.services.new_restaurant_service import NewRestaurantDetectionService
from app.services.daily_insights_service import DailyInsightsService
from app.core.config import get_settings

async def get_db_dep() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session

def get_restaurant_repository(session: AsyncSession = Depends(get_db_dep)) -> RestaurantRepository:
    return RestaurantRepository(session)

def get_restaurant_service(repo: RestaurantRepository = Depends(get_restaurant_repository)) -> RestaurantService:
    return RestaurantService(repo)

def get_places_service() -> GooglePlacesService:
    settings = get_settings()
    return GooglePlacesService(api_key=settings.GOOGLE_PLACES_API_KEY)

def get_vision_service() -> GoogleVisionService:
    settings = get_settings()
    return GoogleVisionService(api_key=settings.GOOGLE_VISION_API_KEY)

def get_llm_service_dep() -> BaseLLMService:
    return get_llm_service()

def get_photo_service(places: GooglePlacesService = Depends(get_places_service)) -> PhotoService:
    return PhotoService(places)

def get_lead_scoring_service() -> LeadScoringService:
    return LeadScoringService()

def get_follow_up_repository(session: AsyncSession = Depends(get_db_dep)) -> FollowUpRepository:
    return FollowUpRepository(session)

def get_follow_up_service(repo: FollowUpRepository = Depends(get_follow_up_repository)) -> FollowUpService:
    return FollowUpService(repo)

def get_intelligence_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> RestaurantIntelligenceService:
    return RestaurantIntelligenceService(llm)

def get_collaboration_intelligence_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> CollaborationIntelligenceService:
    return CollaborationIntelligenceService(llm)

def get_opening_detector_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> OpeningSoonDetectorService:
    return OpeningSoonDetectorService(llm)

def get_outreach_generator_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> OutreachGeneratorService:
    return OutreachGeneratorService(llm)

def get_ai_decision_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> AIDecisionService:
    return AIDecisionService(llm)

def get_owner_discovery_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> OwnerDiscoveryService:
    return OwnerDiscoveryService(llm)

def get_competitor_analysis_service(places: GooglePlacesService = Depends(get_places_service)) -> CompetitorAnalysisService:
    return CompetitorAnalysisService(places)

def get_opportunity_score_service() -> OpportunityScoreService:
    return OpportunityScoreService()

def get_new_restaurant_service() -> NewRestaurantDetectionService:
    return NewRestaurantDetectionService()

def get_daily_insights_service(llm: BaseLLMService = Depends(get_llm_service_dep)) -> DailyInsightsService:
    return DailyInsightsService(llm)
