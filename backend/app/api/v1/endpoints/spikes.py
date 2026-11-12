from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, Spike
from app.schemas.spike import SpikeResponse, SpikeResolveRequest

router = APIRouter()

@router.get("", response_model=List[SpikeResponse])
def get_user_spikes(
    unresolved_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Spike).filter(Spike.user_id == current_user.id)
    if unresolved_only:
        query = query.filter(Spike.is_resolved == False)
    spikes = query.order_by(Spike.detected_at.desc()).all()
    return [SpikeResponse.model_validate(s) for s in spikes]

@router.patch("/{spike_id}/resolve", response_model=SpikeResponse)
def resolve_spike(
    spike_id: str,
    resolve_req: SpikeResolveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    spike = db.query(Spike).filter(Spike.id == spike_id, Spike.user_id == current_user.id).first()
    if not spike:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spike alert not found")

    spike.is_resolved = resolve_req.is_resolved
    db.commit()
    db.refresh(spike)
    return SpikeResponse.model_validate(spike)

