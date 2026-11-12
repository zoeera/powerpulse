from typing import Dict, Any, List
import math

class SolarCalculator:
    """
    Solar Generation and ROI Calculator powered by PM Surya Ghar Muft Bijli Yojana subsidies
    and solar irradiance characteristics across Indian cities.
    """

    CITY_SOLAR_HOURS = {
        "Hyderabad": 5.2,
        "Lucknow": 5.0,
        "Indore": 5.4,
        "Delhi": 4.9,
        "Default": 5.1
    }

    # PM Surya Ghar Central Government Subsidy Scheme
    @staticmethod
    def get_subsidy(panel_kw: float) -> float:
        if panel_kw <= 1.0:
            return 30000.0 * panel_kw
        elif panel_kw <= 2.0:
            return 30000.0 + (30000.0 * (panel_kw - 1.0))
        else:
            # Maximum central subsidy capped at ₹78,000 for residential systems >= 3 kW
            return 78000.0

    @classmethod
    def calculate_roi(
        cls,
        panel_kw: float = 3.0,
        battery_kwh: float = 0.0,
        city: str = "Hyderabad",
        occupants: int = 4,
        avg_tariff_per_kwh: float = 7.50
    ) -> Dict[str, Any]:
        """
        Calculate solar system generation, costs, government subsidy, net investment,
        monthly savings, payback period, and CO2 emissions reduction.
        """
        peak_sun_hours = cls.CITY_SOLAR_HOURS.get(city, cls.CITY_SOLAR_HOURS["Default"])
        
        # Gross installation cost: approx ₹55,000 per kW in India
        base_panel_cost = panel_kw * 55000.0
        # Battery cost if selected: approx ₹18,000 per kWh for Lithium LiFePO4
        battery_cost = battery_kwh * 18000.0
        gross_investment = round(base_panel_cost + battery_cost, 2)
        
        subsidy = cls.get_subsidy(panel_kw)
        net_investment = round(max(0.0, gross_investment - subsidy), 2)
        
        # Generation calculation:
        # Daily generation: panel_kw * peak_sun_hours * performance_ratio (0.80)
        daily_generation_kwh = panel_kw * peak_sun_hours * 0.80
        monthly_generation_kwh = daily_generation_kwh * 30.0
        annual_generation_kwh = daily_generation_kwh * 365.0
        
        # Financial savings
        monthly_savings_inr = round(monthly_generation_kwh * avg_tariff_per_kwh, 2)
        annual_savings_inr = round(annual_generation_kwh * avg_tariff_per_kwh, 2)
        
        payback_years = round(net_investment / max(1.0, annual_savings_inr), 1)
        
        # Environmental impact: India grid emission factor = 0.82 kg CO2 per kWh
        annual_co2_kg = round(annual_generation_kwh * 0.82, 1)

        # 24-hour typical generation curve
        hourly_curve = {}
        for h in range(24):
            if 6 <= h <= 18:
                # Bell curve from sunrise to sunset peaking at 12-13 hrs
                angle = (h - 6) / 12.0 * math.pi
                factor = math.sin(angle) ** 2
                hourly_kwh = round((daily_generation_kwh * factor / 6.0), 3)
            else:
                hourly_kwh = 0.0
            hourly_curve[f"{h:02d}:00"] = hourly_kwh

        return {
            "category": "solar",
            "title": f"{panel_kw:.1f} kW Rooftop Solar System",
            "description": f"Install a {panel_kw:.1f} kW rooftop solar system with PM Surya Ghar subsidy of ₹{subsidy:,.0f}.",
            "panel_kw": panel_kw,
            "battery_kwh": battery_kwh,
            "city": city,
            "investment_inr": gross_investment,
            "subsidy_amount_inr": subsidy,
            "net_investment_inr": net_investment,
            "monthly_generation_kwh": round(monthly_generation_kwh, 1),
            "annual_generation_kwh": round(annual_generation_kwh, 1),
            "monthly_savings_inr": monthly_savings_inr,
            "annual_savings_inr": annual_savings_inr,
            "payback_period_years": payback_years,
            "co2_reduction_kg_yr": annual_co2_kg,
            "hourly_generation_profile": hourly_curve
        }

