from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError
from app.database.models import WatchArea
from app.core.exceptions import DatabaseError
from app.utils.helpers import now_utc

class WatchAreaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> WatchArea:
        try:
            area = WatchArea(**data)
            self.session.add(area)
            await self.session.commit()
            await self.session.refresh(area)
            return area
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to create watch area: {str(e)}")

    async def update(self, area_id: int, data: dict) -> WatchArea | None:
        try:
            stmt = (
                update(WatchArea)
                .where(WatchArea.id == area_id)
                .values(**data)
                .returning(WatchArea)
            )
            result = await self.session.execute(stmt)
            area = result.scalar_one_or_none()
            if area:
                await self.session.commit()
            return area
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to update watch area: {str(e)}")

    async def delete(self, area_id: int) -> bool:
        try:
            stmt = delete(WatchArea).where(WatchArea.id == area_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount > 0
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Failed to delete watch area: {str(e)}")

    async def get_by_id(self, area_id: int) -> WatchArea | None:
        try:
            stmt = select(WatchArea).where(WatchArea.id == area_id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get watch area by ID: {str(e)}")

    async def get_by_name(self, name: str) -> WatchArea | None:
        try:
            stmt = select(WatchArea).where(WatchArea.name == name)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get watch area by name: {str(e)}")

    async def get_all(self, skip: int = 0, limit: int = 50) -> tuple[list[WatchArea], int]:
        try:
            count_stmt = select(func.count()).select_from(WatchArea)
            total = await self.session.execute(count_stmt)
            
            stmt = select(WatchArea).offset(skip).limit(limit)
            result = await self.session.execute(stmt)
            
            return list(result.scalars().all()), total.scalar_one()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get watch areas: {str(e)}")

    async def get_enabled(self) -> list[WatchArea]:
        try:
            stmt = select(WatchArea).where(WatchArea.is_active == True)
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to get enabled watch areas: {str(e)}")

    async def update_scan_stats(self, area_id: int, restaurants_found: int) -> WatchArea | None:
        try:
            data = {
                "last_scanned_at": now_utc(),
                "total_restaurants_found": WatchArea.total_restaurants_found + restaurants_found
            }
            return await self.update(area_id, data)
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to update watch area stats: {str(e)}")
