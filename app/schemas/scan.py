from typing import Optional, List
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Schema for requesting a scan by a string location."""
    query: str = "restaurant"
    location: str = Field(..., description="E.g., 'New York, NY'")
    radius: int = Field(5000, ge=100, le=50000, description="Radius in meters")
    max_results: int = Field(20, ge=1, le=60, description="Max results per scan")


class ScanLocationRequest(BaseModel):
    """Schema for requesting a scan by latitude and longitude."""
    latitude: float
    longitude: float
    radius: int = Field(5000, ge=100, le=50000, description="Radius in meters")
    max_results: int = Field(20, ge=1, le=60, description="Max results per scan")
    query: str = "restaurant"


class ScanResponse(BaseModel):
    """Response returned when a scan is initiated."""
    success: bool = True
    message: str
    scan_id: str
    status: str = "pending"
    total_found: int = 0


class ScanStatusResponse(BaseModel):
    """Response for checking the status of an ongoing or completed scan."""
    success: bool = True
    scan_id: str
    status: str
    processed: int
    total: int
    errors: Optional[List[str]] = None
