from typing import Optional, Dict, Any
from datetime import date, datetime
from app.schemas.compat import BaseModel, Field

class ParsedBillSchema(BaseModel):
    """
    Exact required output format for every parsed bill before saving to DB.
    """
    provider: str = Field(..., description="Electricity provider name, e.g. TGSPDCL")
    state: str = Field(..., description="Indian state name, e.g. Telangana")
    tariff_category: str = Field(..., description="Tariff category, e.g. LT-I(A)")
    from_date: date = Field(..., description="Billing cycle start date")
    to_date: date = Field(..., description="Billing cycle end date")
    billing_days: int = Field(..., description="Number of days in billing cycle")
    units_consumed_kwh: float = Field(..., description="Total kWh units consumed")
    energy_charges: float = Field(default=0.0, description="Energy charges in INR")
    fixed_charges: float = Field(default=0.0, description="Fixed charges in INR")
    customer_charges: float = Field(default=0.0, description="Customer charges in INR")
    electricity_duty: float = Field(default=0.0, description="Electricity duty in INR")
    subsidy_amount: float = Field(default=0.0, description="Subsidy amount credited in INR")
    subsidy_scheme: Optional[str] = Field(default=None, description="Subsidy scheme, e.g. GJS")
    net_payable: float = Field(default=0.0, description="Final net amount payable in INR")
    meter_number: Optional[str] = Field(default=None, description="Meter serial number")
    consumer_number: Optional[str] = Field(default=None, description="Consumer/Account ID number")
    manual_review_required: bool = Field(default=False, description="Flag for review fallback")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="OCR confidence")

class BillCreateManual(ParsedBillSchema):
    pass

class BillUpdate(BaseModel):
    provider: Optional[str] = None
    state: Optional[str] = None
    tariff_category: Optional[str] = None
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    billing_days: Optional[int] = None
    units_consumed_kwh: Optional[float] = None
    energy_charges: Optional[float] = None
    fixed_charges: Optional[float] = None
    customer_charges: Optional[float] = None
    electricity_duty: Optional[float] = None
    subsidy_amount: Optional[float] = None
    subsidy_scheme: Optional[str] = None
    net_payable: Optional[float] = None
    meter_number: Optional[str] = None
    consumer_number: Optional[str] = None
    manual_review_required: Optional[bool] = None

class BillResponse(ParsedBillSchema):
    id: str
    user_id: str
    source_file_hash: Optional[str] = None
    source_file_path: Optional[str] = None
    signed_url: Optional[str] = None
    is_manual: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BillUploadResponse(BaseModel):
    job_id: Optional[str] = None
    status: str
    message: str
    bill: Optional[BillResponse] = None
