from typing import List, Tuple, Optional, Dict, Any

from app.core.logging import get_logger
from app.core.exceptions import NotFoundException
from app.repositories.follow_up_repository import FollowUpRepository
from app.schemas.follow_up import FollowUpCreate, FollowUpUpdate
from app.database.models import FollowUp

logger = get_logger(__name__)

class FollowUpService:
    """Service layer for handling FollowUp business logic."""
    
    def __init__(self, repository: FollowUpRepository) -> None:
        self.repository = repository

    async def create_follow_up(self, data: FollowUpCreate) -> FollowUp:
        """Creates a new follow-up."""
        logger.info(f"Creating follow-up for restaurant {data.restaurant_id}")
        return await self.repository.create(data.model_dump(exclude_unset=True))

    async def update_follow_up(self, follow_up_id: int, data: FollowUpUpdate) -> FollowUp:
        """Updates an existing follow-up."""
        logger.info(f"Updating follow-up {follow_up_id}")
        updated = await self.repository.update(follow_up_id, data.model_dump(exclude_unset=True))
        if not updated:
            raise NotFoundException(f"FollowUp with ID {follow_up_id} not found")
        return updated

    async def delete_follow_up(self, follow_up_id: int) -> bool:
        """Deletes a follow-up."""
        logger.info(f"Deleting follow-up {follow_up_id}")
        deleted = await self.repository.delete(follow_up_id)
        if not deleted:
            raise NotFoundException(f"FollowUp with ID {follow_up_id} not found")
        return True

    async def get_follow_up(self, follow_up_id: int) -> FollowUp:
        """Retrieves a specific follow-up by ID."""
        follow_up = await self.repository.get_by_id(follow_up_id)
        if not follow_up:
            raise NotFoundException(f"FollowUp with ID {follow_up_id} not found")
        return follow_up

    async def get_restaurant_follow_ups(self, restaurant_id: int) -> List[FollowUp]:
        """Retrieves all follow-ups for a given restaurant."""
        return await self.repository.get_by_restaurant_id(restaurant_id)

    async def list_follow_ups(self, page: int = 1, page_size: int = 50, filters: Optional[Dict[str, Any]] = None) -> Tuple[List[FollowUp], int]:
        """Retrieves a paginated list of follow-ups."""
        skip = (page - 1) * page_size
        return await self.repository.get_all(skip=skip, limit=page_size, filters=filters)

    async def get_pending(self) -> List[FollowUp]:
        """Retrieves all pending follow-ups."""
        return await self.repository.get_pending_follow_ups()
