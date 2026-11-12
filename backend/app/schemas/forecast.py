from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.schemas.compat import BaseModel, Field

class DailyForecastPoint(BaseModel):
    date: date
    day_name: str
    predicted_kwh: float
    estimated_cost_inr: float
    is_holiday: bool = False

class ForecastResponse(BaseModel):
    forecast_type: str = Field(..., description="monthly, daily, weekly, bill")
    target_date: date
    predicted_kwh: float
    estimated_cost_inr: float
    confidence_tier: str = Field(..., description="HIGH, LOW, ESTIMATE")
    confidence_label: str = Field(..., description="High Confidence, Low Confidence, Reference Estimate")
    model_used: str
    is_estimate: bool = True
    disclaimer: str
    source_info: str
    as_of_date: date
    daily_breakdown: Optional[List[DailyForecastPoint]] = None
    bill_count_used: int = 0
    tariff_slab_applied: Optional[str] = None
    subsidy_applied_inr: float = 0.0

class BillForecastResponse(BaseModel):
    forecast_month: str
    predicted_kwh: float
    estimated_energy_charges: float
    estimated_fixed_charges: float
    estimated_customer_charges: float
    estimated_duty: float
    estimated_subsidy: float
    subsidy_scheme: Optional[str] = None
    net_payable_inr: float
    confidence_tier: str
    disclaimer: str
    as_of_date: date
