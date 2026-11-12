from typing import Optional
from datetime import datetime
from app.schemas.compat import BaseModel, Field

class ApplianceCreate(BaseModel):
    appliance_type: str = Field(..., description="e.g. Air Conditioner, Refrigerator, Ceiling Fan")
    count: int = Field(default=1, ge=1)
    wattage_watts: float = Field(..., gt=0.0)
    star_rating: Optional[int] = Field(default=3, ge=1, le=5)
    daily_hours: float = Field(default=4.0, ge=0.0, le=24.0)

class ApplianceResponse(BaseModel):
    id: str
    user_id: str
    appliance_type: str
    count: int
    wattage_watts: float
    star_rating: Optional[int]
    daily_hours: float
    estimated_monthly_kwh: float
    created_at: datetime

    class Config:
        from_attributes = True
