import logging
from app.services.google_places_service import GooglePlacesService
from app.database.models import Restaurant
from app.utils.constants import MAX_PHOTO_WIDTH
from app.core.exceptions import GooglePlacesAPIError

logger = logging.getLogger(__name__)

class PhotoService:
    """Service to handle photo downloads and management."""

    def __init__(self, places_service: GooglePlacesService) -> None:
        """Initialize with a GooglePlacesService dependency."""
        self.places_service = places_service

    async def download_restaurant_photo(self, photo_reference: str) -> bytes | None:
        """Download a photo given a reference string, returning bytes or None on failure."""
        try:
            return await self.places_service.download_photo(photo_reference, max_width=MAX_PHOTO_WIDTH)
        except GooglePlacesAPIError as e:
            logger.warning(f"Failed to download photo with reference {photo_reference[:15]}...: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading photo: {e}")
            return None

    async def get_photo_for_analysis(self, restaurant: Restaurant) -> bytes | None:
        """Get the primary photo for a restaurant if a reference exists."""
        if not restaurant.photo_reference:
            return None
        return await self.download_restaurant_photo(restaurant.photo_reference)
