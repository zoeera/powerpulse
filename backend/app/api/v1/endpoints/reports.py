import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, Bill, ApplianceProfile, Report
from app.schemas.report import ReportGenerateRequest, ReportResponse
from app.services.report.pdf_generator import generate_pdf_report
from app.services.solar.solar_calculator import SolarCalculator
from app.services.solar.eco_calculator import EcoCalculator
from app.ml.model_loader import model_loader
from app.services.tariff.tariff_calculator import TariffCalculator
from app.core.storage import generate_signed_url

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    req: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch bills
    bills = db.query(Bill).filter(Bill.user_id == current_user.id).order_by(Bill.to_date.desc()).all()
    bill_history = []
    bill_kwh_list = []
    for b in bills:
        bill_history.append({
            "billing_period": f"{b.from_date.strftime('%d/%m/%Y')} - {b.to_date.strftime('%d/%m/%Y')}",
            "units_consumed_kwh": b.units_consumed_kwh,
            "energy_charges": b.energy_charges,
            "subsidy_amount": b.subsidy_amount,
            "net_payable": b.net_payable
        })
        bill_kwh_list.append(b.units_consumed_kwh)

    # Forecast
    pred_res = model_loader.predict_bill_history(datetime.now().month % 12 + 1, datetime.now().year, bill_kwh_list)
    tariff = TariffCalculator.calculate_bill(
        provider=current_user.utility,
        units_consumed=pred_res["predicted_kwh"],
        apply_subsidy=True
    )
    forecast_dict = {
        "predicted_kwh": pred_res["predicted_kwh"],
        "estimated_cost_inr": tariff["net_payable"],
        "confidence_tier": pred_res["confidence_tier"],
        "disclaimer": pred_res["disclaimer"]
    }

    # Appliances
    appliances = db.query(ApplianceProfile).filter(ApplianceProfile.user_id == current_user.id).all()
    appliance_data = [{
        "appliance_type": a.appliance_type,
        "count": a.count,
        "wattage_watts": a.wattage_watts,
        "daily_hours": a.daily_hours,
        "estimated_monthly_kwh": a.estimated_monthly_kwh
    } for a in appliances]

    # Recommendations
    solar = SolarCalculator.calculate_roi(panel_kw=3.0, city=current_user.city)
    recs = [solar] + EcoCalculator.get_all_eco_recommendations()

    # Generate PDF
    report_filename = f"powerpulse_report_{current_user.id[:8]}_{int(datetime.now().timestamp())}.pdf"
    rel_path, abs_path = generate_pdf_report(
        user_name=current_user.full_name,
        utility=current_user.utility,
        state=current_user.state,
        bill_history=bill_history,
        forecast=forecast_dict,
        appliances=appliance_data,
        recommendations=recs,
        output_filename=report_filename
    )

    report = Report(
        user_id=current_user.id,
        title=f"PowerPulse Energy Report - {req.report_period}",
        report_period=req.report_period or "Last 12 Months",
        pdf_file_path=rel_path,
        parameters={"bill_count": len(bills), "forecast_kwh": pred_res["predicted_kwh"]}
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    download_url = generate_signed_url(rel_path)

    return ReportResponse(
        id=report.id,
        title=report.title,
        report_period=report.report_period,
        download_url=download_url,
        generated_at=report.generated_at,
        parameters=report.parameters
    )

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    download_url = generate_signed_url(report.pdf_file_path)
    return ReportResponse(
        id=report.id,
        title=report.title,
        report_period=report.report_period,
        download_url=download_url,
        generated_at=report.generated_at,
        parameters=report.parameters
    )

