import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.database.base import Base

class Restaurant(Base):
    """SQLAlchemy model representing a restaurant lead."""
    __tablename__ = "restaurants"

    # === EXISTING COLUMNS (keep all) ===
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
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    # === PHASE 2: NEW COLUMNS ===
    discovered_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    last_scan_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    new_restaurant_score: Mapped[Optional[float]] = mapped_column(sa.Float, default=0.0)
    is_new: Mapped[Optional[bool]] = mapped_column(sa.Boolean, default=False)
    new_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)
    new_reason: Mapped[Optional[str]] = mapped_column(sa.Text)

    opening_status: Mapped[Optional[str]] = mapped_column(sa.String(50))
    cuisine_type: Mapped[Optional[str]] = mapped_column(sa.String(200))
    estimated_spending: Mapped[Optional[str]] = mapped_column(sa.String(50))
    customer_segment: Mapped[Optional[str]] = mapped_column(sa.String(500))
    restaurant_style: Mapped[Optional[str]] = mapped_column(sa.String(200))
    strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    weaknesses: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    marketing_maturity: Mapped[Optional[str]] = mapped_column(sa.String(100))
    branding_quality: Mapped[Optional[str]] = mapped_column(sa.String(100))

    collaboration_opportunities: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    opportunity_score: Mapped[Optional[float]] = mapped_column(sa.Float, default=0.0)
    opportunity_reason: Mapped[Optional[str]] = mapped_column(sa.Text)

    competition_score: Mapped[Optional[str]] = mapped_column(sa.String(20))
    competitor_count: Mapped[Optional[int]] = mapped_column(sa.Integer, default=0)
    competition_opportunity: Mapped[Optional[str]] = mapped_column(sa.String(20))

    cold_email: Mapped[Optional[str]] = mapped_column(sa.Text)
    instagram_dm: Mapped[Optional[str]] = mapped_column(sa.Text)
    whatsapp_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    phone_script: Mapped[Optional[str]] = mapped_column(sa.Text)
    linkedin_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    opening_congrats_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    marketing_proposal: Mapped[Optional[str]] = mapped_column(sa.Text)

    ai_contact_decision: Mapped[Optional[str]] = mapped_column(sa.String(10))
    ai_decision_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)
    ai_decision_reasoning: Mapped[Optional[str]] = mapped_column(sa.Text)
    ai_expected_roi: Mapped[Optional[str]] = mapped_column(sa.String(100))

    owner_name: Mapped[Optional[str]] = mapped_column(sa.String(200))
    manager_name: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_email: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_instagram: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_facebook: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_linkedin: Mapped[Optional[str]] = mapped_column(sa.String(200))
    owner_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)

    instagram_presence: Mapped[Optional[str]] = mapped_column(sa.String(100))
    website_quality: Mapped[Optional[str]] = mapped_column(sa.String(100))
    online_presence_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    last_ai_analysis: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    scan_zone: Mapped[Optional[str]] = mapped_column(sa.String(100))

    # Phase 3 Feature 16: Marketing Readiness
    marketing_readiness_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    marketing_readiness_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)
    marketing_readiness_reasons: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    marketing_readiness_evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)

    # Phase 3 Feature 20: Photo Intelligence
    interior_quality: Mapped[Optional[str]] = mapped_column(sa.String(50))
    exterior_quality: Mapped[Optional[str]] = mapped_column(sa.String(50))
    photo_ambience: Mapped[Optional[str]] = mapped_column(sa.String(100))
    premium_appearance: Mapped[Optional[str]] = mapped_column(sa.String(50))
    photo_branding_quality: Mapped[Optional[str]] = mapped_column(sa.String(50))
    instagram_friendliness: Mapped[Optional[str]] = mapped_column(sa.String(50))
    menu_presentation: Mapped[Optional[str]] = mapped_column(sa.String(50))
    visual_strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    visual_weaknesses: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)

    # Phase 3 Feature 21: Business Profile
    dining_style: Mapped[Optional[str]] = mapped_column(sa.String(100))
    digital_presence_quality: Mapped[Optional[str]] = mapped_column(sa.String(50))
    operational_confidence: Mapped[Optional[str]] = mapped_column(sa.String(50))

    # Phase 3 Feature 24: Branding Score
    branding_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    branding_score_reasons: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)

    # Phase 3 Feature 19: Enhanced New Restaurant Detection
    new_restaurant_status: Mapped[Optional[str]] = mapped_column(sa.String(30))  # NEWLY_DISCOVERED, LIKELY_NEW, OPENING_SOON, ESTABLISHED, UNKNOWN

    # Phase 3 Feature 25: Follow-up message
    follow_up_message: Mapped[Optional[str]] = mapped_column(sa.Text)

    # Phase 3 Feature 28: Opportunity Index
    opportunity_index: Mapped[Optional[float]] = mapped_column(sa.Float)
    opportunity_index_factors: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)

    # Relationships
    follow_ups: Mapped[list["FollowUp"]] = relationship("FollowUp", back_populates="restaurant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Restaurant(id={self.id}, name='{self.name}', place_id='{self.place_id}')>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FollowUp(Base):
    """Model for tracking follow-up interactions with restaurants."""
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="contacted")
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    next_action: Mapped[Optional[str]] = mapped_column(sa.String(500))
    contacted_via: Mapped[Optional[str]] = mapped_column(sa.String(50))
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="follow_ups")

    def __repr__(self) -> str:
        return f"<FollowUp(id={self.id}, restaurant_id={self.restaurant_id}, status='{self.status}')>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class WatchArea(Base):
    """Model for storing predefined watch areas for automated scanning."""
    __tablename__ = "watch_areas"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(200), nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(sa.Float, nullable=False)
    longitude: Mapped[float] = mapped_column(sa.Float, nullable=False)
    radius: Mapped[int] = mapped_column(sa.Integer, default=2000)
    enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    last_scanned: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    restaurants_found: Mapped[Optional[int]] = mapped_column(sa.Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    def __repr__(self) -> str:
        return f"<WatchArea(id={self.id}, name='{self.name}', enabled={self.enabled})>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
