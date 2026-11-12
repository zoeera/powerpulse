from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, Bill, MeterReading, ApplianceProfile, Spike, Forecast, Recommendation, Report, Consent
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recent_bill = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(Bill.to_date.desc()).first()

    result = UserResponse.model_validate(current_user)
    if recent_bill:
        result.current_tariff_category = recent_bill.tariff_category
        result.current_utility = recent_bill.provider
    return result

@router.delete("/me")
def delete_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    FR-15: Explicit Data Consent + 'Delete My Data' flow.
    Soft-deletes the user profile with deleted_at timestamp and purges all associated
    personal bills, telemetry, and appliance profiles.
    """
    user_id = current_user.id

    # Purge user data tables
    db.query(Spike).filter(Spike.user_id == user_id).delete()
    db.query(MeterReading).filter(MeterReading.user_id == user_id).delete()
    db.query(Bill).filter(Bill.user_id == user_id).delete()
    db.query(ApplianceProfile).filter(ApplianceProfile.user_id == user_id).delete()
    db.query(Forecast).filter(Forecast.user_id == user_id).delete()
    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()
    db.query(Report).filter(Report.user_id == user_id).delete()
    db.query(Consent).filter(Consent.user_id == user_id).delete()

    # Soft-delete the user record
    current_user.deleted_at = datetime.now(timezone.utc)
    current_user.is_active = False
    db.commit()

    return {
        "status": "SUCCESS",
        "message": "All your personal electricity bills, meter readings, and account data have been completely deleted in compliance with privacy guidelines."
    }

