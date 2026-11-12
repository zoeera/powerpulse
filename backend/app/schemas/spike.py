from typing import Optional
from datetime import datetime
from app.schemas.compat import BaseModel

class SpikeResponse(BaseModel):
    id: str
    user_id: str
    bill_id: Optional[str] = None
    spike_type: str  # "monthly" or "hourly"
    detected_at: datetime
    threshold_kwh: float
    actual_kwh: float
    deviation_pct: float
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SpikeResolveRequest(BaseModel):
    is_resolved: bool = True
