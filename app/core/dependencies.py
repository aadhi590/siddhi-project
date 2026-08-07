from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.restaurant_service import RestaurantService
from app.services.google_places_service import GooglePlacesService
from app.services.google_vision_service import GoogleVisionService
from app.services.llm_service import get_llm_service, BaseLLMService
from app.services.photo_service import PhotoService
from app.services.lead_scoring_service import LeadScoringService
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
