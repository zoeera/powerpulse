import sys
import unittest
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.parsers.bill_parser import parse_bill_text, detect_provider_and_state

class TestBillParsers(unittest.TestCase):
    
    def test_bug_4_provider_auto_detection(self):
        """Bug 4: Verify auto-detection of all target Indian distribution utilities."""
        self.assertEqual(detect_provider_and_state("Visit tssouthernpower.com for quick pay"), ("TGSPDCL", "Telangana"))
        self.assertEqual(detect_provider_and_state("Welcome to TGSPDCL Hyderabad electricity portal"), ("TGSPDCL", "Telangana"))
        self.assertEqual(detect_provider_and_state("UTTAR PRADESH POWER CORPORATION LIMITED (UPPCL)"), ("UPPCL", "Uttar Pradesh"))
        self.assertEqual(detect_provider_and_state("मध्य प्रदेश पश्चिम क्षेत्र विद्युत वितरण कंपनी mpwz.co.in"), ("MPWZ", "Madhya Pradesh"))
        self.assertEqual(detect_provider_and_state("BSES Rajdhani Power Limited bsesdelhi.com"), ("BSES Delhi", "Delhi"))
        self.assertEqual(detect_provider_and_state("TGNPDCL Warangal circle"), ("TGNPDCL", "Telangana"))

    def test_bug_1_tgspdcl_thermal_slip_and_gjs_subsidy(self):
        """Bug 1: Fix TGSPDCL thermal slip extraction, regex Bill Amount, and GJS subsidy."""
        ocr_text = """
        TGSPDCL tssouthernpower.com
        Meter No: 29443604
        DATE STS READING
        75:01/03/24 61 12722
        5: 07/02/24 81 12574
        Units: 148 Days? 23
        Energy Chardes: 599.80
        Fixed Charges: 16.60
        Cust Charges ६ 90.00
        Electrici Duty: 8.88
        Bill Amount 715.00
        GJS Subsidy : -715.00
        Net 0.00
        """
        parsed = parse_bill_text(ocr_text)
        self.assertEqual(parsed.provider, "TGSPDCL")
        self.assertEqual(parsed.state, "Telangana")
        self.assertEqual(parsed.units_consumed_kwh, 148.0)
        self.assertEqual(parsed.energy_charges, 599.80)
        self.assertEqual(parsed.fixed_charges, 16.60)
        self.assertEqual(parsed.customer_charges, 90.00)
        self.assertEqual(parsed.electricity_duty, 8.88)
        self.assertEqual(parsed.subsidy_amount, 715.00)
        self.assertEqual(parsed.subsidy_scheme, "GJS")
        self.assertEqual(parsed.net_payable, 0.00)
        self.assertEqual(parsed.meter_number, "29443604")
        self.assertFalse(parsed.manual_review_required)

    def test_bug_2_mpwz_hindi_bill_units_column(self):
        """Bug 2: Extract consumption column instead of meter reading, with validation diff."""
        ocr_text = """
        मध्य प्रदेश पश्चिम क्षेत्र विद्युत वितरण कंपनी लिमिटेड
        उपभोक्ता क्रमांक : 8765432101
        मीटर संख्या | वर्तमान रीडिंग | पूर्व रीडिंग | कुल खपत (यूनिट)
        1122334455 | 8965 | 8730 | 235
        ऊर्जा प्रभार | 1,175.00
        निश्वित शुल्क 50.00
        विद्युत शुल्क | 58.75
        कुल देय राशि 1,455.00
        """
        parsed = parse_bill_text(ocr_text)
        self.assertEqual(parsed.provider, "MPWZ")
        self.assertEqual(parsed.units_consumed_kwh, 235.0)  # Correct consumption, NOT 8965
        self.assertEqual(parsed.net_payable, 1455.0)

    def test_bug_3_telugu_bill_decimal_shift(self):
        """Bug 3: Telugu bill decimal shift ₹104600.0 divided by 100 to ₹1046.00 with manual review flag."""
        ocr_text = """
        TGNPDCL
        Units: 212
        Energy Charges: 702.80
        Fixed Charges: 20.00
        Cust Charges: 50.00
        Total Amount Due: 104600.0
        """
        parsed = parse_bill_text(ocr_text)
        self.assertEqual(parsed.net_payable, 1046.00)
        self.assertTrue(parsed.manual_review_required)
        self.assertLessEqual(parsed.confidence_score, 0.85)

if __name__ == "__main__":
    unittest.main()

