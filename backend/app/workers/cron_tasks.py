from datetime import datetime, timedelta, timezone
from app.workers.celery_app import celery_app
from app.db.session import SessionLocal
from app.db.models import Bill, MeterReading
from app.core.config import settings

@celery_app.task
def purge_expired_data_task():
    """
    Cron job enforcing 24-month data retention policy on bills and meter readings.
    Auto-deletes records older than DATA_RETENTION_MONTHS (24 months).
    """
    db = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=settings.DATA_RETENTION_MONTHS * 30)
        
        # Purge older meter readings
        deleted_meter_count = db.query(MeterReading).filter(MeterReading.timestamp < cutoff_date).delete()
        
        # Purge older bills
        deleted_bills_count = db.query(Bill).filter(Bill.created_at < cutoff_date).delete()
        
        db.commit()
        return {
            "status": "COMPLETED",
            "purged_meter_readings": deleted_meter_count,
            "purged_bills": deleted_bills_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        db.rollback()
        return {"status": "ERROR", "error": str(e)}
    finally:
        db.close()

