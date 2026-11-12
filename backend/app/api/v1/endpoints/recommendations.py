from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.db.models import User, Bill
from app.schemas.recommendation import SolarRoiRequest, SolarRoiDetailResponse, RecommendationResponse
from app.services.solar.solar_calculator import SolarCalculator
from app.services.solar.eco_calculator import EcoCalculator
from app.services.tariff.tariff_calculator import TariffCalculator

router = APIRouter()


def _resolve_effective_tariff_rate(bills: List[Bill], fallback_provider: str) -> float:
    """Compute a positive per-unit rate from bills, falling back to utility tariff or ₹7.50/unit."""
    if not bills:
        return 7.50

    total_units = sum((b.units_consumed_kwh or 0.0) for b in bills)
    total_energy_charges = sum((b.energy_charges or 0.0) for b in bills)

    if total_units > 0 and total_energy_charges > 0:
        rate = total_energy_charges / total_units
        if rate >= 2.0:
            return round(rate, 2)

    if total_units > 0:
        avg_kwh = total_units / len(bills)
        provider = bills[-1].provider or fallback_provider
        calc = TariffCalculator.calculate_bill(
            provider=provider,
            units_consumed=avg_kwh,
            billing_days=30,
            apply_subsidy=False,
        )
        if calc["energy_charges"] > 0 and avg_kwh > 0:
            rate = calc["energy_charges"] / avg_kwh
            if rate >= 2.0:
                return round(rate, 2)

    return 7.50


@router.post("/solar", response_model=SolarRoiDetailResponse)
def calculate_solar_roi(
    req: SolarRoiRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bills = db.query(Bill).filter(Bill.user_id == current_user.id).all()
    tariff_rate = _resolve_effective_tariff_rate(bills, current_user.utility)

    roi_dict = SolarCalculator.calculate_roi(
        panel_kw=req.panel_kw,
        battery_kwh=req.battery_kwh,
        city=req.city or current_user.city or "Hyderabad",
        avg_tariff_per_kwh=tariff_rate
    )

    return SolarRoiDetailResponse(**roi_dict)


@router.get("", response_model=List[RecommendationResponse])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bills = db.query(Bill).filter(Bill.user_id == current_user.id).all()
    if bills:
        avg_kwh = sum((b.units_consumed_kwh or 0.0) for b in bills) / len(bills)
    else:
        avg_kwh = 220.0

    tariff_rate = _resolve_effective_tariff_rate(bills, current_user.utility)

    solar_res = SolarCalculator.calculate_roi(
        panel_kw=3.0,
        battery_kwh=0.0,
        city=current_user.city or "Hyderabad",
        avg_tariff_per_kwh=tariff_rate
    )

    eco_recs = EcoCalculator.get_all_eco_recommendations(
        avg_monthly_kwh=avg_kwh,
        tariff_rate=tariff_rate,
    )

    all_recs = [
        RecommendationResponse(
            category=solar_res["category"],
            title=solar_res["title"],
            description=solar_res["description"],
            investment_inr=solar_res["investment_inr"],
            monthly_savings_inr=solar_res["monthly_savings_inr"],
            annual_savings_inr=solar_res["annual_savings_inr"],
            payback_period_years=solar_res["payback_period_years"],
            co2_reduction_kg_yr=solar_res["co2_reduction_kg_yr"],
            parameters={"panel_kw": 3.0, "subsidy_inr": solar_res["subsidy_amount_inr"]}
        )
    ]

    for er in eco_recs:
        all_recs.append(RecommendationResponse(
            category=er["category"],
            title=er["title"],
            description=er["description"],
            investment_inr=er["investment_inr"],
            monthly_savings_inr=er["monthly_savings_inr"],
            annual_savings_inr=er["annual_savings_inr"],
            payback_period_years=er["payback_period_years"],
            co2_reduction_kg_yr=er["co2_reduction_kg_yr"],
            parameters=er.get("parameters")
        ))

    return all_recs
