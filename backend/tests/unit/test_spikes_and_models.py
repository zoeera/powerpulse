import sys
import unittest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.spike.spike_detector import SpikeDetector
from app.ml.model_loader import model_loader
from app.services.solar.solar_calculator import SolarCalculator
from app.services.solar.eco_calculator import EcoCalculator

class TestSpikesAndModels(unittest.TestCase):

    def test_monthly_spike_detection(self):
        """Monthly spike: new_bill_kwh > mean(last 3 same-season bills) * 1.30."""
        # Baseline = (100 + 100 + 100) / 3 = 100. Threshold = 130.
        normal = SpikeDetector.detect_monthly_spike(120.0, [100.0, 100.0, 100.0])
        self.assertIsNone(normal)

        spike = SpikeDetector.detect_monthly_spike(145.0, [100.0, 100.0, 100.0])
        self.assertIsNotNone(spike)
        self.assertTrue(spike["is_spike"])
        self.assertEqual(spike["threshold_kwh"], 130.0)
        self.assertEqual(spike["deviation_pct"], 45.0)

    def test_hourly_spike_detection_mad(self):
        """Hourly MAD rule: median + 3 * 1.4826 * MAD."""
        readings = [
            {"timestamp": f"2026-11-10T{h:02d}:00:00", "kwh": 0.35}
            for h in range(20)
        ]
        # Add an abnormal spike
        readings.append({"timestamp": "2026-11-10T20:00:00", "kwh": 3.80})
        spikes = SpikeDetector.detect_hourly_spikes(readings)
        self.assertGreaterEqual(len(spikes), 1)
        self.assertEqual(spikes[0]["actual_kwh"], 3.80)

    def test_forecast_confidence_tiers(self):
        """
        Confidence Tiers:
        - >=12 bills -> HIGH
        - 6-11 bills -> LOW
        - <6 bills -> ESTIMATE
        """
        # >=12 bills
        res_high = model_loader.predict_bill_history(5, 2026, [150.0] * 12)
        self.assertEqual(res_high["confidence_tier"], "HIGH")

        # 6-11 bills
        res_low = model_loader.predict_bill_history(5, 2026, [150.0] * 8)
        self.assertEqual(res_low["confidence_tier"], "LOW")
        self.assertIn("Notice", res_low["disclaimer"])

        # <6 bills
        res_est = model_loader.predict_bill_history(5, 2026, [150.0] * 3)
        self.assertEqual(res_est["confidence_tier"], "ESTIMATE")

    def test_solar_roi_pm_surya_ghar_subsidy(self):
        """PM Surya Ghar subsidy: ₹30k for 1kW, ₹60k for 2kW, ₹78k for >=3kW."""
        self.assertEqual(SolarCalculator.get_subsidy(1.0), 30000.0)
        self.assertEqual(SolarCalculator.get_subsidy(2.0), 60000.0)
        self.assertEqual(SolarCalculator.get_subsidy(3.0), 78000.0)
        self.assertEqual(SolarCalculator.get_subsidy(5.0), 78000.0)

        roi_3kw = SolarCalculator.calculate_roi(panel_kw=3.0, city="Hyderabad")
        self.assertEqual(roi_3kw["subsidy_amount_inr"], 78000.0)
        self.assertGreater(roi_3kw["annual_generation_kwh"], 3500.0)
        self.assertGreater(roi_3kw["co2_reduction_kg_yr"], 2000.0)
        self.assertLess(roi_3kw["payback_period_years"], 6.0)

    def test_eco_alternatives_generation(self):
        """Verify generation of LED, Inverter AC, SWH, and Battery recommendations."""
        recs = EcoCalculator.get_all_eco_recommendations(avg_monthly_kwh=250.0)
        categories = {r["category"] for r in recs}
        self.assertIn("led", categories)
        self.assertIn("inverter_ac", categories)
        self.assertIn("swh", categories)
        self.assertIn("battery", categories)

if __name__ == "__main__":
    unittest.main()

