from pydantic import BaseModel, ConfigDict
from typing import Any
from datetime import datetime

class AreaSummary(BaseModel):
    area_name: str
    total_restaurants: int = 0
    new_restaurants: int = 0
    opening_soon: int = 0
    avg_opportunity_index: float = 0.0
    avg_marketing_readiness: float = 0.0
    top_lead_name: str | None = None

class SalesReportLead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    area: str | None = None
    opportunity_index: float | None = None
    marketing_readiness_score: float | None = None
    new_restaurant_score: float | None = None
    ai_contact_decision: str | None = None
    ai_decision_confidence: float | None = None
    ai_summary: str | None = None
    collaboration_reason: str | None = None
    outreach_message: str | None = None
    phone: str | None = None
    website: str | None = None
    google_maps_url: str | None = None
    photo_reference: str | None = None
    opening_status: str | None = None
    branding_score: float | None = None

class TodayLeadsResponseV2(BaseModel):
    success: bool = True
    date: str
    total: int
    leads: list[SalesReportLead]

class DailySalesReport(BaseModel):
    success: bool = True
    date: str
    total_scanned: int = 0
    newly_discovered: int = 0
    opening_soon: int = 0
    highest_opportunity_leads: list[SalesReportLead] = []
    highest_marketing_readiness: list[SalesReportLead] = []
    area_summary: list[AreaSummary] = []
    scan_statistics: dict[str, Any] = {}
    ai_summary: str = ""

class MarketingReadinessResult(BaseModel):
    score: float = 0.0
    confidence: float = 0.0
    reasons: list[str] = []
    evidence: dict[str, Any] = {}

class PhotoIntelligenceResult(BaseModel):
    interior_quality: str | None = None
    exterior_quality: str | None = None
    ambience: str | None = None
    premium_appearance: str | None = None
    branding_quality: str | None = None
    instagram_friendliness: str | None = None
    menu_presentation: str | None = None
    visual_strengths: list[str] = []
    visual_weaknesses: list[str] = []
    confidence: float = 0.0
    evidence: list[str] = []

class BusinessProfileResult(BaseModel):
    restaurant_category: str | None = None
    cuisine: str | None = None
    dining_style: str | None = None
    estimated_price_segment: str | None = None
    likely_customer_segments: list[str] = []
    restaurant_style: str | None = None
    marketing_maturity: str | None = None
    branding_quality: str | None = None
    digital_presence_quality: str | None = None
    operational_confidence: str | None = None
    confidence: float = 0.0
    evidence: list[str] = []

class BrandingScoreResult(BaseModel):
    score: float = 0.0
    logo_quality: str | None = None
    visual_consistency: str | None = None
    photography_quality: str | None = None
    website_presence: str | None = None
    menu_presentation: str | None = None
    storefront_quality: str | None = None
    reasoning: str = ""
    confidence: float = 0.0

class OpportunityIndexResult(BaseModel):
    index: float = 0.0
    factors: dict[str, float] = {}
    top_contributors: list[str] = []
    confidence: float = 0.0
    reasoning: str = ""
