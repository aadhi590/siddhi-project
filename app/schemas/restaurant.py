from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RestaurantBase(BaseModel):
    """Base fields for a restaurant schema."""
    name: str
    place_id: str
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    business_status: Optional[str] = None
    types: Optional[List[str]] = None
    price_level: Optional[int] = None
    google_maps_url: Optional[str] = None


class RestaurantCreate(RestaurantBase):
    """Schema for creating a new restaurant."""
    pass


class RestaurantUpdate(BaseModel):
    """Schema for updating an existing restaurant."""
    name: Optional[str] = None
    place_id: Optional[str] = None
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    business_status: Optional[str] = None
    types: Optional[List[str]] = None
    price_level: Optional[int] = None
    google_maps_url: Optional[str] = None
    photo_reference: Optional[str] = None
    restaurant_type: Optional[str] = None
    ambience: Optional[str] = None
    target_audience: Optional[str] = None
    premium_score: Optional[float] = None
    collaboration_score: Optional[float] = None
    collaboration_reason: Optional[str] = None
    ai_summary: Optional[str] = None
    outreach_message: Optional[str] = None
    vision_labels: Optional[Dict[str, Any]] = None
    vision_objects: Optional[Dict[str, Any]] = None
    vision_text: Optional[Dict[str, Any]] = None
    vision_landmarks: Optional[Dict[str, Any]] = None
    opening_hours: Optional[Dict[str, Any]] = None


class RestaurantInDB(RestaurantBase):
    """Schema representing a restaurant as retrieved from the database."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    photo_reference: Optional[str] = None
    restaurant_type: Optional[str] = None
    ambience: Optional[str] = None
    target_audience: Optional[str] = None
    premium_score: Optional[float] = None
    collaboration_score: Optional[float] = None
    collaboration_reason: Optional[str] = None
    ai_summary: Optional[str] = None
    outreach_message: Optional[str] = None
    vision_labels: Optional[Dict[str, Any]] = None
    vision_objects: Optional[Dict[str, Any]] = None
    vision_text: Optional[Dict[str, Any]] = None
    vision_landmarks: Optional[Dict[str, Any]] = None
    opening_hours: Optional[Dict[str, Any]] = None
    first_seen: datetime
    last_seen: datetime
    created_at: datetime
    updated_at: datetime


class RestaurantResponse(BaseModel):
    """Standard API response schema for a single restaurant."""
    success: bool = True
    data: RestaurantInDB


class RestaurantListResponse(BaseModel):
    """Standard API response schema for a list of restaurants."""
    success: bool = True
    data: List[RestaurantInDB]
    total: int
    page: int
    page_size: int


class RestaurantAnalysisResponse(BaseModel):
    """Response schema containing a restaurant and its AI analysis."""
    success: bool = True
    data: RestaurantInDB
    analysis: Optional[Dict[str, Any]] = None


class VisionAnalysisResult(BaseModel):
    """Schema for results of the Google Vision API analysis."""
    labels: Optional[List[Dict[str, Any]]] = None
    objects: Optional[List[Dict[str, Any]]] = None
    text: Optional[List[str]] = None
    logos: Optional[List[Dict[str, Any]]] = None
    dominant_colors: Optional[List[Dict[str, Any]]] = None
    safe_search: Optional[Dict[str, Any]] = None


class LLMAnalysisResult(BaseModel):
    """Schema for results of the LLM analysis."""
    restaurant_type: Optional[str] = None
    ambience: Optional[str] = None
    target_audience: Optional[str] = None
    estimated_spending: Optional[str] = None
    style: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    marketing_suggestions: Optional[List[str]] = None
    collaboration_opportunities: Optional[List[str]] = None
    ai_summary: Optional[str] = None
    premium_score: Optional[float] = None
