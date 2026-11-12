import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, 
    Text, JSON, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    state = Column(String(100), default="Telangana")
    city = Column(String(100), default="Hyderabad")
    utility = Column(String(50), default="TGSPDCL")
    tariff_category = Column(String(50), default="LT-I(A)")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    consents = relationship("Consent", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")
    meter_readings = relationship("MeterReading", back_populates="user", cascade="all, delete-orphan")
    appliances = relationship("ApplianceProfile", back_populates="user", cascade="all, delete-orphan")
    spikes = relationship("Spike", back_populates="user", cascade="all, delete-orphan")
    forecasts = relationship("Forecast", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")

class Consent(Base):
    __tablename__ = "consents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type = Column(String(100), nullable=False)  # e.g., "TERMS_AND_PRIVACY", "OCR_DATA_PROCESSING"
    granted = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="consents")

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Required JSON schema fields
    provider = Column(String(100), nullable=False, default="TGSPDCL")
    state = Column(String(100), nullable=False, default="Telangana")
    tariff_category = Column(String(50), nullable=False, default="LT-I(A)")
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
    billing_days = Column(Integer, nullable=False, default=30)
    units_consumed_kwh = Column(Float, nullable=False)
    energy_charges = Column(Float, default=0.0)
    fixed_charges = Column(Float, default=0.0)
    customer_charges = Column(Float, default=0.0)
    electricity_duty = Column(Float, default=0.0)
    subsidy_amount = Column(Float, default=0.0)
    subsidy_scheme = Column(String(50), nullable=True)  # e.g. "GJS"
    net_payable = Column(Float, default=0.0)
    meter_number = Column(String(100), nullable=True)
    consumer_number = Column(String(100), nullable=True)
    manual_review_required = Column(Boolean, default=False)
    confidence_score = Column(Float, default=1.0)
    
    # Metadata & Deduplication
    source_file_hash = Column(String(64), unique=True, nullable=True, index=True)
    source_file_path = Column(String(500), nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    is_manual = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="bills")
    spikes = relationship("Spike", back_populates="bill", cascade="all, delete-orphan")

class MeterReading(Base):
    __tablename__ = "meter_readings"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    kwh = Column(Float, nullable=False)
    source_file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="meter_readings")
    
    __table_args__ = (
        Index("idx_user_meter_time", "user_id", "timestamp"),
    )

class ApplianceProfile(Base):
    __tablename__ = "appliance_profiles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    appliance_type = Column(String(100), nullable=False)  # e.g. "Air Conditioner", "Refrigerator", "Ceiling Fan"
    count = Column(Integer, default=1, nullable=False)
    wattage_watts = Column(Float, nullable=False)
    star_rating = Column(Integer, nullable=True)
    daily_hours = Column(Float, default=4.0, nullable=False)
    estimated_monthly_kwh = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="appliances")

class Spike(Base):
    __tablename__ = "spikes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bill_id = Column(String(36), ForeignKey("bills.id", ondelete="SET NULL"), nullable=True)
    spike_type = Column(String(20), nullable=False)  # "monthly" or "hourly"
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    threshold_kwh = Column(Float, nullable=False)
    actual_kwh = Column(Float, nullable=False)
    deviation_pct = Column(Float, nullable=False)  # e.g., 35.5%
    message = Column(String(500), nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="spikes")
    bill = relationship("Bill", back_populates="spikes")

class Forecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    forecast_type = Column(String(20), nullable=False)  # "monthly", "daily", "weekly", "bill"
    target_date = Column(Date, nullable=False)
    predicted_kwh = Column(Float, nullable=False)
    estimated_cost_inr = Column(Float, nullable=False)
    confidence_tier = Column(String(20), nullable=False)  # "HIGH", "LOW", "ESTIMATE"
    model_used = Column(String(100), nullable=False)
    feature_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="forecasts")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # "solar", "led", "inverter_ac", "battery", "swh"
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    investment_inr = Column(Float, nullable=False)
    monthly_savings_inr = Column(Float, nullable=False)
    payback_period_years = Column(Float, nullable=False)
    co2_reduction_kg_yr = Column(Float, nullable=False)
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="recommendations")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    report_period = Column(String(50), nullable=False)
    pdf_file_path = Column(String(500), nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    parameters = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="reports")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    task_name = Column(String(100), nullable=False)
    celery_task_id = Column(String(100), unique=True, nullable=True)
    status = Column(String(20), default="PENDING", nullable=False)  # "PENDING", "PROCESSING", "COMPLETED", "FAILED"
    error_message = Column(Text, nullable=True)
    retries = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="jobs")

class Utility(Base):
    __tablename__ = "utilities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    website = Column(String(255), nullable=True)
    customer_care_number = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)

class Tariff(Base):
    __tablename__ = "tariffs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utility_code = Column(String(50), nullable=False, index=True)
    tariff_category = Column(String(50), nullable=False)
    min_units = Column(Float, nullable=False)
    max_units = Column(Float, nullable=False)  # INF represented as large float e.g. 999999
    rate_per_kwh = Column(Float, nullable=False)
    fixed_charge = Column(Float, default=0.0)
    customer_charge = Column(Float, default=0.0)
    effective_from = Column(Date, nullable=False)

class Subsidy(Base):
    __tablename__ = "subsidies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    utility_code = Column(String(50), nullable=False, index=True)
    scheme_name = Column(String(100), nullable=False)  # e.g., "Gruha Jyothi Scheme (GJS)"
    max_units_free = Column(Float, nullable=False)     # e.g., 200.0
    criteria = Column(Text, nullable=True)
    active = Column(Boolean, default=True)

class ReferenceConsumption(Base):
    __tablename__ = "reference_consumption"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    household_size = Column(Integer, nullable=False)  # 1 to 6+
    monthly_average_kwh = Column(Float, nullable=False)
    seasonal_factor = Column(Float, default=1.0)

