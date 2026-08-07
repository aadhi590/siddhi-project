import httpx
from typing import Any
import json

from app.core.config import Settings
from app.core.exceptions import GooglePlacesAPIError

class GooglePlacesService:
    """Service for interacting with Google Places API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize the Google Places Service with configuration settings."""
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    async def search_nearby(self, latitude: float, longitude: float, radius: int = 5000, keyword: str = "restaurant", max_results: int = 20) -> list[dict[str, Any]]:
        """Search for places nearby a given coordinate."""
        endpoint = f"{self.base_url}/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "keyword": keyword,
            "key": self.api_key
        }
        
        results = []
        
        async with httpx.AsyncClient() as client:
            try:
                while len(results) < max_results:
                    response = await client.get(endpoint, params=params, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("status") not in ("OK", "ZERO_RESULTS"):
                        raise GooglePlacesAPIError(f"Nearby search failed: {data.get('status')} - {data.get('error_message', '')}")
                    
                    results.extend(data.get("results", []))
                    
                    next_page_token = data.get("next_page_token")
                    if not next_page_token or len(results) >= max_results:
                        break
                    
                    params = {"pagetoken": next_page_token, "key": self.api_key}
                    
            except httpx.RequestError as e:
                raise GooglePlacesAPIError(f"Network error during nearby search: {e}") from e
                
        return results[:max_results]

    async def get_place_details(self, place_id: str) -> dict[str, Any]:
        """Get detailed information for a specific place_id."""
        endpoint = f"{self.base_url}/details/json"
        fields = "name,formatted_address,geometry,formatted_phone_number,website,rating,user_ratings_total,business_status,types,opening_hours,url,price_level,photos"
        params = {
            "place_id": place_id,
            "fields": fields,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "OK":
                    raise GooglePlacesAPIError(f"Details request failed: {data.get('status')} - {data.get('error_message', '')}")
                
                return data.get("result", {})
            except httpx.RequestError as e:
                raise GooglePlacesAPIError(f"Network error getting place details: {e}") from e

    async def download_photo(self, photo_reference: str, max_width: int = 800) -> bytes:
        """Download a photo given a photo_reference string."""
        endpoint = f"{self.base_url}/photo"
        params = {
            "maxwidth": max_width,
            "photoreference": photo_reference,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params, follow_redirects=True, timeout=15.0)
                response.raise_for_status()
                return response.content
            except httpx.RequestError as e:
                raise GooglePlacesAPIError(f"Network error downloading photo: {e}") from e

    async def geocode_location(self, location: str) -> tuple[float, float]:
        """Convert a string location into a (latitude, longitude) tuple."""
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location,
            "key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") != "OK":
                    raise GooglePlacesAPIError(f"Geocoding failed: {data.get('status')} - {data.get('error_message', '')}")
                
                results = data.get("results", [])
                if not results:
                    raise GooglePlacesAPIError("No results found for location.")
                
                location_data = results[0]["geometry"]["location"]
                return location_data["lat"], location_data["lng"]
            except httpx.RequestError as e:
                raise GooglePlacesAPIError(f"Network error during geocoding: {e}") from e
