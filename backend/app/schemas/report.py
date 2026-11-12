from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.compat import BaseModel

class ReportGenerateRequest(BaseModel):
    report_period: Optional[str] = "Last 12 Months"
    include_forecast: bool = True
    include_appliances: bool = True
    include_recommendations: bool = True

class ReportResponse(BaseModel):
    id: str
    title: str
    report_period: str
    download_url: str
    generated_at: datetime
    parameters: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
