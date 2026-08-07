from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Any

class CollaborationOpportunity(BaseModel):
    type: str
    probability: float
    reason: str

class CompetitorInfo(BaseModel):
    name: str | None = None
    rating: float | None = None
    review_count: int | None = None
    price_level: int | None = None
    distance_meters: float | None = None

class CompetitorAnalysisResult(BaseModel):
    competitor_count: int = 0
    competitors: list[CompetitorInfo] = []
    competition_score: str = "Medium"
    opportunity: str = "Medium"
    analysis: str | None = None

class NewRestaurantResult(BaseModel):
    new_restaurant_score: float = 0.0
    is_new: bool = False
    confidence: float = 0.0
    reason: str = ""

class OpeningStatusResult(BaseModel):
    opening_status: str = "UNKNOWN"  # OPENING_SOON, NEWLY_OPENED, ESTABLISHED, UNKNOWN
    confidence: float = 0.0
    signals: list[str] = []

class RestaurantIntelligenceResult(BaseModel):
    restaurant_type: str | None = None
    cuisine_type: str | None = None
    estimated_spending: str | None = None
    customer_segment: list[str] = []
    restaurant_style: str | None = None
    strengths: list[str] = []
    weaknesses: list[str] = []
    marketing_maturity: str | None = None
    branding_quality: str | None = None
    online_presence_score: float = 0.0
    ai_summary: str | None = None
    premium_score: float = 0.0

class CollaborationIntelligenceResult(BaseModel):
    opportunities: list[CollaborationOpportunity] = []
    overall_score: float = 0.0
    top_recommendation: str | None = None

class OpportunityScoreResult(BaseModel):
    opportunity_score: float = 0.0
    factors: dict[str, float] = {}
    reason: str = ""

class OutreachBundle(BaseModel):
    cold_email: str = ""
    instagram_dm: str = ""
    whatsapp_message: str = ""
    phone_script: str = ""
    linkedin_message: str = ""
    opening_congrats_message: str = ""
    marketing_proposal: str = ""

class AIDecisionResult(BaseModel):
    decision: str = "MAYBE"  # YES, NO, MAYBE
    confidence: float = 0.0
    reasoning: str = ""
    expected_roi: str = ""

class OwnerInfo(BaseModel):
    owner_name: str | None = None
    manager_name: str | None = None
    business_email: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    website: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    confidence: float = 0.0

class TodayLeadItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    formatted_address: str | None = None
    opportunity_score: float | None = None
    new_restaurant_score: float | None = None
    opening_status: str | None = None
    premium_score: float | None = None
    ai_summary: str | None = None
    ai_contact_decision: str | None = None
    ai_decision_reasoning: str | None = None
    outreach_message: str | None = None
    phone: str | None = None
    website: str | None = None
    google_maps_url: str | None = None
    photo_reference: str | None = None
    scan_zone: str | None = None
    collaboration_reason: str | None = None

class TodayLeadsResponse(BaseModel):
    success: bool = True
    date: str
    total: int
    leads: list[TodayLeadItem]

class DailyInsights(BaseModel):
    date: str
    best_leads: list[TodayLeadItem] = []
    top_premium: list[TodayLeadItem] = []
    most_likely_to_collaborate: list[TodayLeadItem] = []
    opening_soon: list[TodayLeadItem] = []
    high_roi: list[TodayLeadItem] = []
    low_competition: list[TodayLeadItem] = []
    total_restaurants: int = 0
    new_today: int = 0
    summary: str = ""

class ChennaiScanRequest(BaseModel):
    zones: list[str] | None = None  # if None, scan all zones
    keyword: str = "restaurant"
    max_results_per_zone: int = 20

class ChennaiScanResponse(BaseModel):
    success: bool = True
    message: str
    scan_id: str
    zones_queued: int
    total_zones: int
