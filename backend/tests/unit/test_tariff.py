import sys
import unittest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.tariff.tariff_calculator import TariffCalculator

class TestTariffCalculator(unittest.TestCase):

    def test_tgspdcl_gruha_jyothi_free_under_200(self):
        """TGSPDCL: <=200 units must result in net_payable = 0.0 with GJS subsidy."""
        calc = TariffCalculator.calculate_bill("TGSPDCL", units_consumed=148.0, billing_days=30, apply_subsidy=True)
        self.assertEqual(calc["provider"], "TGSPDCL")
        self.assertEqual(calc["subsidy_scheme"], "GJS")
        self.assertGreater(calc["subsidy_amount"], 0.0)
        self.assertEqual(calc["net_payable"], 0.0)

    def test_tgspdcl_above_200_no_free_subsidy(self):
        """TGSPDCL: >200 units falls into LT-I(B)(ii) with full billing."""
        calc = TariffCalculator.calculate_bill("TGSPDCL", units_consumed=250.0, billing_days=30, apply_subsidy=True)
        self.assertEqual(calc["tariff_category"], "LT-I(B)(ii)")
        self.assertIsNone(calc["subsidy_scheme"])
        self.assertGreater(calc["net_payable"], 1000.0)

    def test_uppcl_lmv1_sample(self):
        """UPPCL: 250 units -> approx ₹1,400."""
        calc = TariffCalculator.calculate_bill("UPPCL", units_consumed=250.0, billing_days=30)
        self.assertEqual(calc["provider"], "UPPCL")
        self.assertEqual(calc["tariff_category"], "LMV-1")
        # Should be near ₹1400 (within 10%)
        self.assertAlmostEqual(calc["net_payable"], 1400.0, delta=120.0)

    def test_mpwz_domestic_sample(self):
        """MPWZ: 235 units -> approx ₹1,330 current charges."""
        calc = TariffCalculator.calculate_bill("MPWZ", units_consumed=235.0, billing_days=30)
        self.assertEqual(calc["provider"], "MPWZ")
        self.assertAlmostEqual(calc["net_payable"], 1330.0, delta=100.0)

    def test_bses_delhi_domestic_b1(self):
        """BSES Delhi: 200 units free, 420 units sample near ₹2,360."""
        calc_free = TariffCalculator.calculate_bill("BSES Delhi", units_consumed=180.0, apply_subsidy=True)
        self.assertEqual(calc_free["net_payable"], 0.0)

        calc_420 = TariffCalculator.calculate_bill("BSES Delhi", units_consumed=420.0, apply_subsidy=True)
        self.assertAlmostEqual(calc_420["net_payable"], 2360.0, delta=200.0)

if __name__ == "__main__":
    unittest.main()

