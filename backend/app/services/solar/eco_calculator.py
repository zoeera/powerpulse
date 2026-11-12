from typing import List, Dict, Any

class EcoCalculator:
    """
    ROI and energy savings calculator for Indian households:
    - LED bulbs retrofitting
    - 5-Star Inverter AC upgrade
    - Solar Water Heater (SWH)
    - Home Battery Storage
    """

    @staticmethod
    def get_all_eco_recommendations(avg_monthly_kwh: float = 250.0, tariff_rate: float = 7.50) -> List[Dict[str, Any]]:
        recs = []

        # 1. LED Bulbs Upgrade
        # Replace 8 standard bulbs (40-60W) with 9W LEDs
        led_count = 8
        led_watt_saving_per_bulb = 50.0  # watts saved
        daily_hours = 5.0
        annual_kwh_saved_led = (led_count * led_watt_saving_per_bulb * daily_hours * 365) / 1000.0  # ~365 kWh/year
        investment_led = led_count * 120.0  # ₹960
        annual_savings_led = annual_kwh_saved_led * tariff_rate
        monthly_savings_led = annual_savings_led / 12.0
        payback_led = round(investment_led / max(1.0, annual_savings_led), 1)
        recs.append({
            "category": "led",
            "title": "Upgrade 8 Bulbs to Energy-Efficient LEDs",
            "description": "Replace regular 60W incandescent or old CFL bulbs with 9W Bureau of Energy Efficiency (BEE) 5-star LEDs.",
            "investment_inr": round(investment_led, 2),
            "monthly_savings_inr": round(monthly_savings_led, 2),
            "annual_savings_inr": round(annual_savings_led, 2),
            "payback_period_years": payback_led,
            "co2_reduction_kg_yr": round(annual_kwh_saved_led * 0.82, 1),
            "parameters": {"bulbs_count": led_count, "kwh_saved_year": round(annual_kwh_saved_led, 1)}
        })

        # 2. 5-Star Inverter AC
        # Replacing 3-star non-inverter AC with 5-star Inverter AC saves ~450 kWh annually
        ac_kwh_saved = 480.0
        ac_extra_investment = 9500.0  # Premium cost for 5-star inverter over base model
        annual_savings_ac = ac_kwh_saved * tariff_rate
        monthly_savings_ac = annual_savings_ac / 12.0
        payback_ac = round(ac_extra_investment / max(1.0, annual_savings_ac), 1)
        recs.append({
            "category": "inverter_ac",
            "title": "Upgrade to 5-Star BEE Inverter Air Conditioner",
            "description": "Switching to an inverter compressor with variable-speed cooling cuts AC electricity draw by up to 35%.",
            "investment_inr": round(ac_extra_investment, 2),
            "monthly_savings_inr": round(monthly_savings_ac, 2),
            "annual_savings_inr": round(annual_savings_ac, 2),
            "payback_period_years": payback_ac,
            "co2_reduction_kg_yr": round(ac_kwh_saved * 0.82, 1),
            "parameters": {"kwh_saved_year": ac_kwh_saved, "efficiency_gain_pct": 35}
        })

        # 3. Solar Water Heater (SWH)
        # 100 Liter per Day (LPD) system replacing 2 kW electric geyser
        swh_kwh_saved = 1100.0
        swh_investment = 24000.0
        annual_savings_swh = swh_kwh_saved * tariff_rate
        monthly_savings_swh = annual_savings_swh / 12.0
        payback_swh = round(swh_investment / max(1.0, annual_savings_swh), 1)
        recs.append({
            "category": "swh",
            "title": "Install 100 LPD Solar Water Heater (SWH)",
            "description": "Eliminate morning water heating loads by replacing electric resistance geysers with rooftop evacuated tube collectors.",
            "investment_inr": round(swh_investment, 2),
            "monthly_savings_inr": round(monthly_savings_swh, 2),
            "annual_savings_inr": round(annual_savings_swh, 2),
            "payback_period_years": payback_swh,
            "co2_reduction_kg_yr": round(swh_kwh_saved * 0.82, 1),
            "parameters": {"capacity_lpd": 100, "kwh_saved_year": swh_kwh_saved}
        })

        # 4. Battery Storage (Power Resilience)
        # 5 kWh LiFePO4 battery storage
        bat_kwh_shifted = 750.0
        bat_investment = 75000.0
        # Peak-offpeak arbitrage and backup power protection
        annual_savings_bat = 750.0 * (tariff_rate * 0.40)  # Arbitrage savings + zero diesel generator running
        monthly_savings_bat = annual_savings_bat / 12.0
        payback_bat = round(bat_investment / max(1.0, annual_savings_bat), 1)
        recs.append({
            "category": "battery",
            "title": "5 kWh Lithium (LiFePO4) Home Battery System",
            "description": "Provides 8+ hours of power blackout backup and enables solar energy time-shifting to avoid peak evening grid tariffs.",
            "investment_inr": round(bat_investment, 2),
            "monthly_savings_inr": round(monthly_savings_bat, 2),
            "annual_savings_inr": round(annual_savings_bat, 2),
            "payback_period_years": payback_bat,
            "co2_reduction_kg_yr": round(bat_kwh_shifted * 0.40 * 0.82, 1),
            "parameters": {"storage_kwh": 5.0, "chemistry": "LiFePO4"}
        })

        return recs

