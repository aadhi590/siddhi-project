from typing import List
from app.database.models import Restaurant
from app.schemas.intelligence import CompetitorAnalysisResult, CompetitorInfo
from app.services.google_places_service import GooglePlacesService
from app.utils.helpers import calculate_distance

class CompetitorAnalysisService:
    def __init__(self, places_service: GooglePlacesService) -> None:
        self.places_service = places_service

    async def analyze_competitors(self, restaurant: Restaurant, radius: int = 500) -> CompetitorAnalysisResult:
        """Analyzes competitors near a given restaurant."""
        if not restaurant.latitude or not restaurant.longitude:
            return CompetitorAnalysisResult(
                competitors=[],
                competition_score="Unknown",
                opportunity="Unknown"
            )
            
        results = await self.places_service.search_nearby(
            lat=restaurant.latitude,
            lng=restaurant.longitude,
            radius=radius,
            keyword="restaurant"
        )
        
        competitors = []
        for res in results:
            if res.get("place_id") == restaurant.place_id:
                continue
                
            dist = calculate_distance(
                restaurant.latitude,
                restaurant.longitude,
                res.get("geometry", {}).get("location", {}).get("lat", 0),
                res.get("geometry", {}).get("location", {}).get("lng", 0)
            )
            
            competitors.append(CompetitorInfo(
                name=res.get("name", ""),
                rating=res.get("rating"),
                user_rating_count=res.get("user_ratings_total"),
                price_level=res.get("price_level"),
                distance_meters=dist
            ))
            
        comp_count = len(competitors)
        if comp_count > 10:
            competition_score = "High"
            opportunity = "Low"
        elif comp_count >= 5:
            competition_score = "Medium"
            opportunity = "Medium"
        else:
            competition_score = "Low"
            opportunity = "High"
            
        return CompetitorAnalysisResult(
            competitors=competitors,
            competition_score=competition_score,
            opportunity=opportunity
        )
