from app.repositories.watchlist_repository import WatchAreaRepository
from app.database.models import WatchArea
from app.schemas.watchlist import WatchAreaCreate, WatchAreaUpdate
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)

class WatchlistService:
    def __init__(self, repository: WatchAreaRepository):
        self.repository = repository

    async def create_watch_area(self, data: WatchAreaCreate) -> WatchArea:
        return await self.repository.create(data.model_dump())

    async def update_watch_area(self, area_id: int, data: WatchAreaUpdate) -> WatchArea:
        area = await self.repository.update(area_id, data.model_dump(exclude_unset=True))
        if not area:
            raise NotFoundException(f"Watch area with id {area_id} not found")
        return area

    async def delete_watch_area(self, area_id: int) -> bool:
        success = await self.repository.delete(area_id)
        if not success:
            raise NotFoundException(f"Watch area with id {area_id} not found")
        return success

    async def get_watch_area(self, area_id: int) -> WatchArea:
        area = await self.repository.get_by_id(area_id)
        if not area:
            raise NotFoundException(f"Watch area with id {area_id} not found")
        return area

    async def list_watch_areas(self, page: int = 1, page_size: int = 50) -> tuple[list[WatchArea], int]:
        skip = (page - 1) * page_size
        return await self.repository.get_all(skip=skip, limit=page_size)

    async def get_enabled_areas(self) -> list[WatchArea]:
        return await self.repository.get_enabled()

    async def seed_default_areas(self) -> list[WatchArea]:
        areas, total = await self.repository.get_all(limit=1)
        if total > 0:
            logger.info("Watch areas table not empty, skipping seed")
            # Fetch all to return them
            all_areas, _ = await self.repository.get_all(limit=100)
            return all_areas
            
        defaults = [
            {"name": "Anna Nagar", "latitude": 13.0860, "longitude": 80.2101, "radius": 2000, "is_active": True},
            {"name": "T Nagar", "latitude": 13.0418, "longitude": 80.2341, "radius": 1500, "is_active": True},
            {"name": "Nungambakkam", "latitude": 13.0569, "longitude": 80.2425, "radius": 1500, "is_active": True},
            {"name": "Adyar", "latitude": 13.0012, "longitude": 80.2565, "radius": 2000, "is_active": True},
            {"name": "Velachery", "latitude": 12.9815, "longitude": 80.2180, "radius": 2000, "is_active": True},
            {"name": "OMR", "latitude": 12.9165, "longitude": 80.2274, "radius": 3000, "is_active": True},
            {"name": "ECR", "latitude": 12.9249, "longitude": 80.2540, "radius": 3000, "is_active": True},
            {"name": "Guindy", "latitude": 13.0067, "longitude": 80.2206, "radius": 1500, "is_active": True},
            {"name": "Porur", "latitude": 13.0380, "longitude": 80.1560, "radius": 2000, "is_active": True},
            {"name": "Chromepet", "latitude": 12.9516, "longitude": 80.1462, "radius": 2000, "is_active": True},
            {"name": "Tambaram", "latitude": 12.9249, "longitude": 80.1000, "radius": 2000, "is_active": True},
            {"name": "Perungudi", "latitude": 12.9640, "longitude": 80.2432, "radius": 1500, "is_active": True},
            {"name": "Sholinganallur", "latitude": 12.9010, "longitude": 80.2279, "radius": 2000, "is_active": True},
            {"name": "Kodambakkam", "latitude": 13.0520, "longitude": 80.2250, "radius": 1500, "is_active": True},
            {"name": "Medavakkam", "latitude": 12.9200, "longitude": 80.1920, "radius": 2000, "is_active": True}
        ]
        
        created = []
        for d in defaults:
            area = await self.repository.create(d)
            created.append(area)
            
        logger.info(f"Seeded {len(created)} default watch areas")
        return created
