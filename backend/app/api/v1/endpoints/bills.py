import hashlib
import json
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, Bill, Job, Spike
from app.schemas.bill import (
    ParsedBillSchema, BillCreateManual, BillUpdate, BillResponse, BillUploadResponse
)
from app.core.storage import save_uploaded_file, generate_signed_url, compute_file_hash
from app.services.parsers.ocr_engine import run_ocr
from app.services.parsers.bill_parser import parse_bill_text
from app.services.spike.spike_detector import SpikeDetector

router = APIRouter()

@router.post("/upload", response_model=BillResponse)
async def upload_bill(
    file: UploadFile = File(...),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header 'Idempotency-Key' is required for file upload operations"
        )
    
    # Read file content
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum allowed 10 MB limit (FR-02)"
        )

    raw_hash = compute_file_hash(contents)
    file_hash = hashlib.sha256(f"{current_user.id}:{raw_hash}".encode("utf-8")).hexdigest()
    
    # Check per-user deduplication: bills.source_file_hash UNIQUE
    existing_bill = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.source_file_hash == file_hash
    ).first()
    if existing_bill and existing_bill.energy_charges > 0:
        # If bill was already parsed with valid positive charges, return existing record
        signed_url = generate_signed_url(existing_bill.source_file_path) if existing_bill.source_file_path else None
        res = BillResponse.model_validate(existing_bill)
        res.signed_url = signed_url
        return res
    elif existing_bill:
        # Purge stale unparsed / zero-charge record so it re-scans with updated OCR
        db.delete(existing_bill)
        db.commit()

    # Save to local storage
    rel_path, _ = save_uploaded_file(contents, file.filename or "bill.jpg", subdir="bills")
    signed_url = generate_signed_url(rel_path)

    # Perform OCR & Parse off the event loop so concurrent API calls stay responsive
    ocr_text = await run_in_threadpool(run_ocr, contents)
    parsed = parse_bill_text(ocr_text, default_provider=current_user.utility)

    # Save Bill into DB
    bill = Bill(
        user_id=current_user.id,
        provider=parsed.provider,
        state=parsed.state,
        tariff_category=parsed.tariff_category,
        from_date=parsed.from_date,
        to_date=parsed.to_date,
        billing_days=parsed.billing_days,
        units_consumed_kwh=parsed.units_consumed_kwh,
        energy_charges=parsed.energy_charges,
        fixed_charges=parsed.fixed_charges,
        customer_charges=parsed.customer_charges,
        electricity_duty=parsed.electricity_duty,
        subsidy_amount=parsed.subsidy_amount,
        subsidy_scheme=parsed.subsidy_scheme,
        net_payable=parsed.net_payable,
        meter_number=parsed.meter_number,
        consumer_number=parsed.consumer_number,
        manual_review_required=parsed.manual_review_required,
        confidence_score=parsed.confidence_score,
        source_file_hash=file_hash,
        source_file_path=rel_path,
        raw_ocr_text=ocr_text,
        parsed_json=json.loads(parsed.model_dump_json()),
        is_manual=False
    )
    db.add(bill)
    db.flush()

    # Check for monthly spike
    past_bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.id != bill.id
    ).order_by(Bill.to_date.asc()).all()
    history = [b.units_consumed_kwh for b in past_bills]
    
    spike_res = SpikeDetector.detect_monthly_spike(bill.units_consumed_kwh, history)
    if spike_res:
        spike = Spike(
            user_id=current_user.id,
            bill_id=bill.id,
            spike_type="monthly",
            threshold_kwh=spike_res["threshold_kwh"],
            actual_kwh=spike_res["actual_kwh"],
            deviation_pct=spike_res["deviation_pct"],
            message=spike_res["message"]
        )
        db.add(spike)

    db.commit()
    db.refresh(bill)

    response = BillResponse.model_validate(bill)
    response.signed_url = signed_url
    return response

@router.post("/manual", response_model=BillResponse)
def create_bill_manual(
    bill_in: BillCreateManual,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = Bill(
        user_id=current_user.id,
        provider=bill_in.provider,
        state=bill_in.state,
        tariff_category=bill_in.tariff_category,
        from_date=bill_in.from_date,
        to_date=bill_in.to_date,
        billing_days=bill_in.billing_days,
        units_consumed_kwh=bill_in.units_consumed_kwh,
        energy_charges=bill_in.energy_charges,
        fixed_charges=bill_in.fixed_charges,
        customer_charges=bill_in.customer_charges,
        electricity_duty=bill_in.electricity_duty,
        subsidy_amount=bill_in.subsidy_amount,
        subsidy_scheme=bill_in.subsidy_scheme,
        net_payable=bill_in.net_payable,
        meter_number=bill_in.meter_number,
        consumer_number=bill_in.consumer_number,
        manual_review_required=False,
        confidence_score=1.0,
        is_manual=True,
        parsed_json=json.loads(bill_in.model_dump_json())
    )
    db.add(bill)
    db.flush()

    # Spike check
    past_bills = db.query(Bill).filter(
        Bill.user_id == current_user.id,
        Bill.id != bill.id
    ).order_by(Bill.to_date.asc()).all()
    history = [b.units_consumed_kwh for b in past_bills]
    
    spike_res = SpikeDetector.detect_monthly_spike(bill.units_consumed_kwh, history)
    if spike_res:
        spike = Spike(
            user_id=current_user.id,
            bill_id=bill.id,
            spike_type="monthly",
            threshold_kwh=spike_res["threshold_kwh"],
            actual_kwh=spike_res["actual_kwh"],
            deviation_pct=spike_res["deviation_pct"],
            message=spike_res["message"]
        )
        db.add(spike)

    db.commit()
    db.refresh(bill)
    return BillResponse.model_validate(bill)

@router.get("", response_model=List[BillResponse])
def get_user_bills(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bills = db.query(Bill).filter(
        Bill.user_id == current_user.id
    ).order_by(Bill.to_date.desc()).offset(skip).limit(limit).all()

    result = []
    for b in bills:
        resp = BillResponse.model_validate(b)
        if b.source_file_path:
            resp.signed_url = generate_signed_url(b.source_file_path)
        result.append(resp)
    return result

@router.patch("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: str,
    bill_update: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")

    update_dict = bill_update.model_dump() if hasattr(bill_update, "model_dump") else bill_update.__dict__
    units_updated = False
    for field, val in update_dict.items():
        if val is not None:
            if field == "units_consumed_kwh":
                units_updated = True
            setattr(bill, field, val)

    # Recalculate TGSPDCL/TGNPDCL tariff category when units change
    if units_updated and bill.provider in ("TGSPDCL", "TGNPDCL"):
        kwh = bill.units_consumed_kwh
        if kwh <= 100:
            bill.tariff_category = "LT-I(A)"
        elif kwh <= 200:
            bill.tariff_category = "LT-I(B)(i)"
        else:
            bill.tariff_category = "LT-I(B)(ii)"
        # GJS subsidy: net payable is 0 for <= 200 units
        if bill.subsidy_scheme == "GJS" and kwh <= 200:
            bill.net_payable = 0.0

    db.commit()
    db.refresh(bill)
    resp = BillResponse.model_validate(bill)
    if bill.source_file_path:
        resp.signed_url = generate_signed_url(bill.source_file_path)
    return resp


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(Bill).filter(Bill.id == bill_id, Bill.user_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
    db.delete(bill)
    db.commit()
    return {"status": "SUCCESS", "deleted_bill_id": bill_id}

