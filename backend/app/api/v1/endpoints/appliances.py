from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, ApplianceProfile
from app.schemas.appliance import ApplianceCreate, ApplianceResponse

router = APIRouter()

@router.post("", response_model=ApplianceResponse)
def add_appliance(
    appliance_in: ApplianceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Monthly kWh = count * wattage * daily_hours * 30 / 1000
    monthly_kwh = (appliance_in.count * appliance_in.wattage_watts * appliance_in.daily_hours * 30.0) / 1000.0
    
    appliance = ApplianceProfile(
        user_id=current_user.id,
        appliance_type=appliance_in.appliance_type,
        count=appliance_in.count,
        wattage_watts=appliance_in.wattage_watts,
        star_rating=appliance_in.star_rating,
        daily_hours=appliance_in.daily_hours,
        estimated_monthly_kwh=round(monthly_kwh, 2)
    )
    db.add(appliance)
    db.commit()
    db.refresh(appliance)
    return ApplianceResponse.model_validate(appliance)

@router.get("", response_model=List[ApplianceResponse])
def get_user_appliances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    apps = db.query(ApplianceProfile).filter(
        ApplianceProfile.user_id == current_user.id
    ).all()
    return [ApplianceResponse.model_validate(a) for a in apps]

@router.delete("/{appliance_id}", status_code=204)
def delete_appliance(
    appliance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    appl = db.query(ApplianceProfile).filter(
        ApplianceProfile.id == appliance_id,
        ApplianceProfile.user_id == current_user.id
    ).first()
    if not appl:
        raise HTTPException(status_code=404, detail="Appliance not found")
    db.delete(appl)
    db.commit()
    return Response(status_code=204)

