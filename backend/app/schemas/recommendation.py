from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.compat import BaseModel, Field

class SolarRoiRequest(BaseModel):
    panel_kw: float = Field(default=3.0, ge=0.5, le=25.0)
    battery_kwh: float = Field(default=0.0, ge=0.0, le=50.0)
    city: Optional[str] = "Hyderabad"
    occupants: int = Field(default=4, ge=1, le=10)
    roof_area_sqft: Optional[float] = 300.0

class RecommendationResponse(BaseModel):
    id: Optional[str] = None
    category: str  # "solar", "led", "inverter_ac", "battery", "swh"
    title: str
    description: str
    investment_inr: float
    monthly_savings_inr: float
    annual_savings_inr: float
    payback_period_years: float
    co2_reduction_kg_yr: float
    parameters: Optional[Dict[str, Any]] = None

class SolarRoiDetailResponse(RecommendationResponse):
    hourly_generation_profile: Optional[Dict[str, float]] = None
    annual_generation_kwh: float
    subsidy_amount_inr: float  # PM Surya Ghar scheme
    net_investment_inr: float
