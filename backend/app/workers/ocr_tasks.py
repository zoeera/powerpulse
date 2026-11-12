import os
import time
from datetime import datetime, timezone
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models import Job, Bill, Spike
from app.services.parsers.ocr_engine import run_ocr
from app.services.parsers.bill_parser import parse_bill_text
from app.services.spike.spike_detector import SpikeDetector
from app.core.storage import get_absolute_path

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def process_bill_ocr_task(self, job_id: str, bill_id: str, relative_file_path: str, user_id: str):
    """
    Async background task for OCR extraction and parsing with up to 3 automatic retries.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "PROCESSING"
            job.celery_task_id = self.request.id
            db.commit()

        abs_path = get_absolute_path(relative_file_path)
        with open(abs_path, "rb") as f:
            file_bytes = f.read()

        # Run OCR
        ocr_text = run_ocr(file_bytes)
        
        # Parse fields
        parsed = parse_bill_text(ocr_text)

        # Update Bill in DB
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if bill:
            bill.provider = parsed.provider
            bill.state = parsed.state
            bill.tariff_category = parsed.tariff_category
            bill.from_date = parsed.from_date
            bill.to_date = parsed.to_date
            bill.billing_days = parsed.billing_days
            bill.units_consumed_kwh = parsed.units_consumed_kwh
            bill.energy_charges = parsed.energy_charges
            bill.fixed_charges = parsed.fixed_charges
            bill.customer_charges = parsed.customer_charges
            bill.electricity_duty = parsed.electricity_duty
            bill.subsidy_amount = parsed.subsidy_amount
            bill.subsidy_scheme = parsed.subsidy_scheme
            bill.net_payable = parsed.net_payable
            bill.meter_number = parsed.meter_number
            bill.consumer_number = parsed.consumer_number
            bill.manual_review_required = parsed.manual_review_required
            bill.confidence_score = parsed.confidence_score
            bill.raw_ocr_text = ocr_text
            bill.parsed_json = json.loads(parsed.model_dump_json())
            db.commit()

            # Check for monthly spike
            past_bills = db.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.id != bill.id
            ).order_by(Bill.to_date.asc()).all()
            history = [b.units_consumed_kwh for b in past_bills]
            
            spike_res = SpikeDetector.detect_monthly_spike(bill.units_consumed_kwh, history)
            if spike_res:
                spike = Spike(
                    user_id=user_id,
                    bill_id=bill.id,
                    spike_type="monthly",
                    threshold_kwh=spike_res["threshold_kwh"],
                    actual_kwh=spike_res["actual_kwh"],
                    deviation_pct=spike_res["deviation_pct"],
                    message=spike_res["message"]
                )
                db.add(spike)
                db.commit()

        if job:
            job.status = "COMPLETED"
            job.updated_at = datetime.now(timezone.utc)
            db.commit()

        return {"status": "SUCCESS", "bill_id": bill_id}

    except Exception as exc:
        db.rollback()
        retries = self.request.retries
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.retries = retries
            job.error_message = str(exc)
            if retries >= self.max_retries:
                job.status = "FAILED"
            db.commit()

        # Retry with exponential backoff
        if retries < self.max_retries:
            raise self.retry(exc=exc, countdown=5 * (2 ** retries))
        raise exc
    finally:
        db.close()

