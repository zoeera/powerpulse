import csv
import io
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, MeterReading, Spike
from app.schemas.meter import MeterReadingResponse, MeterUploadResponse
from app.services.spike.spike_detector import SpikeDetector

router = APIRouter()

@router.post("/upload", response_model=MeterUploadResponse)
async def upload_meter_readings_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV files are supported")
    
    contents = await file.read()
    decoded = contents.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))
    
    # Validate columns (FR-05: timestamp, kwh)
    headers = [h.strip().lower() for h in (reader.fieldnames or [])]
    if "timestamp" not in headers or "kwh" not in headers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must contain 'timestamp' and 'kwh' columns (FR-05)"
        )

    readings_to_insert = []
    detection_items = []
    
    for row in reader:
        ts_val = row.get("timestamp") or row.get("Timestamp")
        kwh_val = row.get("kwh") or row.get("kWh") or row.get("Kwh")
        if not ts_val or not kwh_val:
            continue
        
        try:
            # Parse timestamp with common formats
            ts = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M"):
                try:
                    ts = datetime.strptime(ts_val.strip(), fmt)
                    break
                except ValueError:
                    continue
            if not ts:
                ts = datetime.fromisoformat(ts_val.strip())
            
            kwh = float(kwh_val.strip())
            readings_to_insert.append(MeterReading(
                user_id=current_user.id,
                timestamp=ts,
                kwh=kwh,
                source_file_path=file.filename
            ))
            detection_items.append({"timestamp": ts.isoformat(), "kwh": kwh})
        except Exception:
            continue

    if not readings_to_insert:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No valid reading rows could be parsed")

    db.bulk_save_objects(readings_to_insert)
    db.commit()

    # Run MAD spike detection (FR-10 hourly rule)
    spikes = SpikeDetector.detect_hourly_spikes(detection_items)
    for sp in spikes:
        spike_obj = Spike(
            user_id=current_user.id,
            spike_type="hourly",
            threshold_kwh=sp["threshold_kwh"],
            actual_kwh=sp["actual_kwh"],
            deviation_pct=sp["deviation_pct"],
            message=sp["message"]
        )
        db.add(spike_obj)
    db.commit()

    return MeterUploadResponse(
        status="SUCCESS",
        readings_imported=len(readings_to_insert),
        message=f"Successfully imported {len(readings_to_insert)} smart meter readings",
        detected_spikes_count=len(spikes)
    )

@router.get("/readings", response_model=List[MeterReadingResponse])
def get_meter_readings(
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    readings = db.query(MeterReading).filter(
        MeterReading.user_id == current_user.id
    ).order_by(MeterReading.timestamp.desc()).limit(limit).all()
    
    return [MeterReadingResponse.model_validate(r) for r in readings]

