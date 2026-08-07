import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional, Dict, Any

from app.database.base import Base


class Restaurant(Base):
    """SQLAlchemy model representing a restaurant in the database."""
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    place_id: Mapped[str] = mapped_column(sa.String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    formatted_address: Mapped[Optional[str]] = mapped_column(sa.String(1000))
    latitude: Mapped[Optional[float]] = mapped_column(sa.Float)
    longitude: Mapped[Optional[float]] = mapped_column(sa.Float)
    phone: Mapped[Optional[str]] = mapped_column(sa.String(50))
    website: Mapped[Optional[str]] = mapped_column(sa.String(1000))
    rating: Mapped[Optional[float]] = mapped_column(sa.Float)
    user_rating_count: Mapped[Optional[int]] = mapped_column(sa.Integer)
    business_status: Mapped[Optional[str]] = mapped_column(sa.String(50))
    types: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    opening_hours: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    google_maps_url: Mapped[Optional[str]] = mapped_column(sa.String(1000))
    price_level: Mapped[Optional[int]] = mapped_column(sa.Integer)
    photo_reference: Mapped[Optional[str]] = mapped_column(sa.String(1000))
    
    restaurant_type: Mapped[Optional[str]] = mapped_column(sa.String(100))
    ambience: Mapped[Optional[str]] = mapped_column(sa.String(200))
    target_audience: Mapped[Optional[str]] = mapped_column(sa.String(500))
    premium_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    collaboration_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    collaboration_reason: Mapped[Optional[str]] = mapped_column(sa.Text)
    ai_summary: Mapped[Optional[str]] = mapped_column(sa.Text)
    outreach_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    
    vision_labels: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    vision_objects: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    vision_text: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    vision_landmarks: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    
    first_seen: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    last_seen: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        """String representation of the Restaurant model."""
        return f"<Restaurant(id={self.id}, name='{self.name}', place_id='{self.place_id}')>"

    def to_dict(self) -> dict:
        """Serialize the model instance to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
