from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Restaurant
from app.core.exceptions import DatabaseError
from app.utils.helpers import now_utc

class RestaurantRepository:
    """Repository for managing Restaurant entities in the database."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an active AsyncSession."""
        self.session = session

    async def create(self, data: dict[str, Any]) -> Restaurant:
        """Insert a new restaurant into the database and return it."""
        try:
            restaurant = Restaurant(**data)
            self.session.add(restaurant)
            await self.session.commit()
            await self.session.refresh(restaurant)
            return restaurant
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to create restaurant: {e}") from e

    async def update(self, restaurant_id: int, data: dict[str, Any]) -> Restaurant | None:
        """Partially update an existing restaurant by ID."""
        try:
            stmt = (
                update(Restaurant)
                .where(Restaurant.id == restaurant_id)
                .values(**data, updated_at=now_utc())
                .returning(Restaurant)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to update restaurant {restaurant_id}: {e}") from e

    async def delete(self, restaurant_id: int) -> bool:
        """Delete a restaurant by ID."""
        try:
            stmt = delete(Restaurant).where(Restaurant.id == restaurant_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to delete restaurant {restaurant_id}: {e}") from e

    async def get_by_id(self, restaurant_id: int) -> Restaurant | None:
        """Fetch a restaurant by its primary key ID."""
        try:
            stmt = select(Restaurant).where(Restaurant.id == restaurant_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get restaurant by ID {restaurant_id}: {e}") from e

    async def get_by_place_id(self, place_id: str) -> Restaurant | None:
        """Fetch a restaurant by its unique Google place_id."""
        try:
            stmt = select(Restaurant).where(Restaurant.place_id == place_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get restaurant by place_id {place_id}: {e}") from e

    async def get_all(
        self, skip: int = 0, limit: int = 50, filters: dict[str, Any] | None = None
    ) -> tuple[list[Restaurant], int]:
        """Fetch a paginated list of restaurants with optional filtering."""
        try:
            stmt = select(Restaurant)
            if filters:
                if "name" in filters:
                    stmt = stmt.where(Restaurant.name.ilike(f"%{filters['name']}%"))
                if "restaurant_type" in filters:
                    stmt = stmt.where(Restaurant.restaurant_type == filters["restaurant_type"])
                if "min_rating" in filters:
                    stmt = stmt.where(Restaurant.rating >= filters["min_rating"])
                if "min_premium_score" in filters:
                    stmt = stmt.where(Restaurant.premium_score >= filters["min_premium_score"])
                if "business_status" in filters:
                    stmt = stmt.where(Restaurant.business_status == filters["business_status"])

            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_count = await self.session.scalar(count_stmt) or 0

            stmt = stmt.offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            restaurants = list(result.scalars().all())
            return restaurants, total_count
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get restaurants: {e}") from e

    async def save_many(self, restaurants_data: list[dict[str, Any]]) -> list[Restaurant]:
        """Bulk upsert restaurants. Updates if place_id exists, inserts otherwise."""
        try:
            saved_restaurants = []
            for data in restaurants_data:
                place_id = data.get("place_id")
                if not place_id:
                    continue

                existing = await self.get_by_place_id(place_id)
                if existing:
                    updated = await self.update(existing.id, data)
                    if updated:
                        saved_restaurants.append(updated)
                else:
                    new_rest = await self.create(data)
                    saved_restaurants.append(new_rest)
            return saved_restaurants
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to bulk save restaurants: {e}") from e

    async def mark_seen(self, place_id: str) -> Restaurant | None:
        """Update the last_seen timestamp for a given place_id."""
        try:
            stmt = (
                update(Restaurant)
                .where(Restaurant.place_id == place_id)
                .values(last_seen=now_utc())
                .returning(Restaurant)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to mark restaurant {place_id} as seen: {e}") from e

    async def search(self, query: str, skip: int = 0, limit: int = 50) -> tuple[list[Restaurant], int]:
        """Perform full text search across several fields."""
        try:
            search_filter = or_(
                Restaurant.name.ilike(f"%{query}%"),
                Restaurant.formatted_address.ilike(f"%{query}%"),
                Restaurant.restaurant_type.ilike(f"%{query}%"),
                Restaurant.ai_summary.ilike(f"%{query}%"),
            )
            stmt = select(Restaurant).where(search_filter)
            
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_count = await self.session.scalar(count_stmt) or 0
            
            stmt = stmt.offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            return list(result.scalars().all()), total_count
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to search restaurants with query '{query}': {e}") from e

    async def count(self) -> int:
        """Get the total number of restaurants in the database."""
        try:
            result = await self.session.execute(select(func.count()).select_from(Restaurant))
            return result.scalar_one() or 0
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to count restaurants: {e}") from e
