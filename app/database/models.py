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
    # Feature 2: New Restaurant Detection
    discovered_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    last_scan_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    new_restaurant_score: Mapped[Optional[float]] = mapped_column(sa.Float, default=0.0)
    is_new: Mapped[Optional[bool]] = mapped_column(sa.Boolean, default=False)
    new_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)
    new_reason: Mapped[Optional[str]] = mapped_column(sa.Text)

    # Feature 3: Opening Soon Detector
    opening_status: Mapped[Optional[str]] = mapped_column(sa.String(50))  # OPENING_SOON, NEWLY_OPENED, ESTABLISHED, UNKNOWN

    # Feature 4: Restaurant Intelligence
    cuisine_type: Mapped[Optional[str]] = mapped_column(sa.String(200))
    estimated_spending: Mapped[Optional[str]] = mapped_column(sa.String(50))  # Budget, Mid Range, Premium, Luxury
    customer_segment: Mapped[Optional[str]] = mapped_column(sa.String(500))  # JSON-like list of segments
    restaurant_style: Mapped[Optional[str]] = mapped_column(sa.String(200))
    strengths: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    weaknesses: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)
    marketing_maturity: Mapped[Optional[str]] = mapped_column(sa.String(100))
    branding_quality: Mapped[Optional[str]] = mapped_column(sa.String(100))

    # Feature 5: Collaboration Intelligence
    collaboration_opportunities: Mapped[Optional[Dict[str, Any]]] = mapped_column(sa.JSON)  # list of {type, probability, reason}

    # Feature 6: Opportunity Score
    opportunity_score: Mapped[Optional[float]] = mapped_column(sa.Float, default=0.0)
    opportunity_reason: Mapped[Optional[str]] = mapped_column(sa.Text)

    # Feature 7: Competitor Analysis
    competition_score: Mapped[Optional[str]] = mapped_column(sa.String(20))  # High, Medium, Low
    competitor_count: Mapped[Optional[int]] = mapped_column(sa.Integer, default=0)
    competition_opportunity: Mapped[Optional[str]] = mapped_column(sa.String(20))

    # Feature 8: Outreach - additional columns
    cold_email: Mapped[Optional[str]] = mapped_column(sa.Text)
    instagram_dm: Mapped[Optional[str]] = mapped_column(sa.Text)
    whatsapp_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    phone_script: Mapped[Optional[str]] = mapped_column(sa.Text)
    linkedin_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    opening_congrats_message: Mapped[Optional[str]] = mapped_column(sa.Text)
    marketing_proposal: Mapped[Optional[str]] = mapped_column(sa.Text)

    # Feature 11: AI Decision
    ai_contact_decision: Mapped[Optional[str]] = mapped_column(sa.String(10))  # YES, NO, MAYBE
    ai_decision_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)
    ai_decision_reasoning: Mapped[Optional[str]] = mapped_column(sa.Text)
    ai_expected_roi: Mapped[Optional[str]] = mapped_column(sa.String(100))

    # Feature 12: Owner Discovery
    owner_name: Mapped[Optional[str]] = mapped_column(sa.String(200))
    manager_name: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_email: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_instagram: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_facebook: Mapped[Optional[str]] = mapped_column(sa.String(200))
    contact_linkedin: Mapped[Optional[str]] = mapped_column(sa.String(200))
    owner_confidence: Mapped[Optional[float]] = mapped_column(sa.Float)

    # Feature 15: Additional
    instagram_presence: Mapped[Optional[str]] = mapped_column(sa.String(100))
    website_quality: Mapped[Optional[str]] = mapped_column(sa.String(100))
    online_presence_score: Mapped[Optional[float]] = mapped_column(sa.Float)
    last_ai_analysis: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    scan_zone: Mapped[Optional[str]] = mapped_column(sa.String(100))  # which Chennai zone

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
    status: Mapped[str] = mapped_column(sa.String(50), nullable=False, default="contacted")  # contacted, interested, meeting_scheduled, proposal_sent, converted, rejected
    notes: Mapped[Optional[str]] = mapped_column(sa.Text)
    follow_up_date: Mapped[Optional[datetime]] = mapped_column(sa.DateTime(timezone=True))
    next_action: Mapped[Optional[str]] = mapped_column(sa.String(500))
    contacted_via: Mapped[Optional[str]] = mapped_column(sa.String(50))  # email, instagram, whatsapp, phone, linkedin
    created_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="follow_ups")

    def __repr__(self) -> str:
        return f"<FollowUp(id={self.id}, restaurant_id={self.restaurant_id}, status='{self.status}')>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
