from typing import List, Optional
from datetime import datetime
from app.schemas.compat import BaseModel, Field

class MeterReadingItem(BaseModel):
    timestamp: datetime
    kwh: float = Field(..., ge=0.0)

class MeterReadingResponse(BaseModel):
    id: str
    timestamp: datetime
    kwh: float

    class Config:
        from_attributes = True

class MeterUploadResponse(BaseModel):
    status: str
    readings_imported: int
    message: str
    detected_spikes_count: int = 0
