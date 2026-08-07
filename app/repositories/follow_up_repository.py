from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc, or_, and_
from sqlalchemy.exc import SQLAlchemyError

from app.core.logging import get_logger
from app.core.exceptions import DatabaseError
from app.database.models import FollowUp
from app.utils.helpers import now_utc

logger = get_logger(__name__)

class FollowUpRepository:
    """Repository for managing FollowUp entities in the database."""
    
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict) -> FollowUp:
        """Create a new FollowUp record."""
        try:
            follow_up = FollowUp(**data)
            self.session.add(follow_up)
            await self.session.commit()
            await self.session.refresh(follow_up)
            return follow_up
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to create FollowUp: {e}")
            raise DatabaseError(f"Database error during creation: {str(e)}")

    async def update(self, follow_up_id: int, data: dict) -> Optional[FollowUp]:
        """Update an existing FollowUp record."""
        try:
            result = await self.session.execute(
                select(FollowUp).where(FollowUp.id == follow_up_id)
            )
            follow_up = result.scalars().first()
            if not follow_up:
                return None
                
            for key, value in data.items():
                if hasattr(follow_up, key):
                    setattr(follow_up, key, value)
                    
            await self.session.commit()
            await self.session.refresh(follow_up)
            return follow_up
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to update FollowUp {follow_up_id}: {e}")
            raise DatabaseError(f"Database error during update: {str(e)}")

    async def delete(self, follow_up_id: int) -> bool:
        """Delete a FollowUp record."""
        try:
            result = await self.session.execute(
                select(FollowUp).where(FollowUp.id == follow_up_id)
            )
            follow_up = result.scalars().first()
            if not follow_up:
                return False
                
            await self.session.delete(follow_up)
            await self.session.commit()
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Failed to delete FollowUp {follow_up_id}: {e}")
            raise DatabaseError(f"Database error during deletion: {str(e)}")

    async def get_by_id(self, follow_up_id: int) -> Optional[FollowUp]:
        """Retrieve a FollowUp by its ID."""
        try:
            result = await self.session.execute(
                select(FollowUp).where(FollowUp.id == follow_up_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve FollowUp {follow_up_id}: {e}")
            raise DatabaseError(f"Database error retrieving FollowUp: {str(e)}")

    async def get_by_restaurant_id(self, restaurant_id: int) -> List[FollowUp]:
        """Retrieve all FollowUps for a specific restaurant."""
        try:
            result = await self.session.execute(
                select(FollowUp)
                .where(FollowUp.restaurant_id == restaurant_id)
                .order_by(desc(FollowUp.created_at))
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve FollowUps for restaurant {restaurant_id}: {e}")
            raise DatabaseError(f"Database error retrieving FollowUps: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 50, filters: Optional[dict] = None) -> Tuple[List[FollowUp], int]:
        """Retrieve a paginated list of FollowUps, optionally filtered."""
        try:
            query = select(FollowUp)
            
            if filters:
                conditions = []
                if 'status' in filters:
                    conditions.append(FollowUp.status == filters['status'])
                if 'restaurant_id' in filters:
                    conditions.append(FollowUp.restaurant_id == filters['restaurant_id'])
                if 'contacted_via' in filters:
                    conditions.append(FollowUp.contacted_via == filters['contacted_via'])
                    
                if conditions:
                    query = query.where(and_(*conditions))
                    
            # Count query
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await self.session.execute(count_query)
            total = total_result.scalar() or 0
            
            # Retrieve items
            query = query.order_by(desc(FollowUp.created_at)).offset(skip).limit(limit)
            result = await self.session.execute(query)
            items = list(result.scalars().all())
            
            return items, total
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve list of FollowUps: {e}")
            raise DatabaseError(f"Database error retrieving FollowUps: {str(e)}")

    async def get_pending_follow_ups(self) -> List[FollowUp]:
        """Retrieve all pending follow-ups (due date passed, not converted or rejected)."""
        try:
            current_time = now_utc()
            result = await self.session.execute(
                select(FollowUp)
                .where(
                    and_(
                        FollowUp.follow_up_date <= current_time,
                        FollowUp.status.notin_(['converted', 'rejected'])
                    )
                )
                .order_by(FollowUp.follow_up_date)
            )
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Failed to retrieve pending FollowUps: {e}")
            raise DatabaseError(f"Database error retrieving pending FollowUps: {str(e)}")
