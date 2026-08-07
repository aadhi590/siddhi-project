from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional

class FollowUpCreate(BaseModel):
    restaurant_id: int
    status: str = "contacted"
    notes: str | None = None
    follow_up_date: datetime | None = None
    next_action: str | None = None
    contacted_via: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["contacted", "interested", "meeting_scheduled", "proposal_sent", "converted", "rejected"]
        if v.lower() not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(allowed)}")
        return v.lower()

class FollowUpUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    follow_up_date: datetime | None = None
    next_action: str | None = None
    contacted_via: str | None = None

class FollowUpInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    restaurant_id: int
    status: str
    notes: str | None = None
    follow_up_date: datetime | None = None
    next_action: str | None = None
    contacted_via: str | None = None
    created_at: datetime
    updated_at: datetime

class FollowUpResponse(BaseModel):
    success: bool = True
    data: FollowUpInDB

class FollowUpListResponse(BaseModel):
    success: bool = True
    data: list[FollowUpInDB]
    total: int
