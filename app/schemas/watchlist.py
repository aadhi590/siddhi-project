from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

class WatchAreaCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius: int = 2000
    enabled: bool = True

    @field_validator("radius")
    @classmethod
    def validate_radius(cls, v: int) -> int:
        if v < 100 or v > 50000:
            raise ValueError("Radius must be between 100 and 50000 meters")
        return v

class WatchAreaUpdate(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    radius: int | None = None
    enabled: bool | None = None

class WatchAreaInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    latitude: float
    longitude: float
    radius: int
    enabled: bool
    last_scanned: datetime | None = None
    restaurants_found: int | None = 0
    created_at: datetime
    updated_at: datetime

class WatchAreaResponse(BaseModel):
    success: bool = True
    data: WatchAreaInDB

class WatchAreaListResponse(BaseModel):
    success: bool = True
    data: list[WatchAreaInDB]
    total: int

class WatchlistScanRequest(BaseModel):
    keyword: str = "restaurant"
    max_results_per_area: int = 20

class WatchlistScanResponse(BaseModel):
    success: bool = True
    message: str
    scan_id: str
    areas_queued: int
