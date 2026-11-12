from typing import List, Dict, Any, Optional
import math

class SpikeDetector:
    """
    Spike detection for electricity consumption:
    - Monthly rule: new_bill_kwh > mean(last 3 same-season bills) * 1.30 (30% above threshold)
    - Hourly rule: median + 3 * 1.4826 * MAD
    """

    @staticmethod
    def detect_monthly_spike(
        current_kwh: float,
        history_kwh: List[float],
        season_history_kwh: Optional[List[float]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if the current monthly bill represents an abnormal spike (>30% above expected).
        """
        # Prefer same-season bills if available
        comparison_set = season_history_kwh if season_history_kwh and len(season_history_kwh) >= 1 else history_kwh
        
        if not comparison_set:
            # No prior history, benchmark against typical average (200 kWh)
            baseline = 200.0
        else:
            # Use last up to 3 bills in the comparison set
            recent = comparison_set[-3:]
            baseline = sum(recent) / len(recent)

        threshold = baseline * 1.30
        
        if current_kwh > threshold and baseline > 0:
            deviation_pct = round(((current_kwh - baseline) / baseline) * 100.0, 1)
            return {
                "is_spike": True,
                "spike_type": "monthly",
                "threshold_kwh": round(threshold, 2),
                "actual_kwh": round(current_kwh, 2),
                "baseline_kwh": round(baseline, 2),
                "deviation_pct": deviation_pct,
                "message": f"Abnormal spike detected! Monthly usage of {current_kwh:.1f} kWh is {deviation_pct}% above your expected baseline ({baseline:.1f} kWh)."
            }
        
        return None

    @staticmethod
    def detect_hourly_spikes(readings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hourly spike detection using Median Absolute Deviation (MAD).
        readings: list of dicts with keys 'timestamp' and 'kwh'
        """
        if not readings or len(readings) < 5:
            return []

        values = [float(r["kwh"]) for r in readings]
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        median = sorted_vals[n // 2] if n % 2 != 0 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        abs_diffs = sorted([abs(v - median) for v in values])
        mad = abs_diffs[n // 2] if n % 2 != 0 else (abs_diffs[n // 2 - 1] + abs_diffs[n // 2]) / 2.0

        # When MAD is 0 (e.g. constant background readings), use std dev or 20% of median
        if mad == 0.0:
            mad = max(0.1, median * 0.15)

        threshold = median + (3 * 1.4826 * mad)

        spikes = []
        for r in readings:
            val = float(r["kwh"])
            if val > threshold:
                dev_pct = round(((val - median) / max(0.01, median)) * 100.0, 1)
                spikes.append({
                    "timestamp": r["timestamp"],
                    "actual_kwh": round(val, 3),
                    "threshold_kwh": round(threshold, 3),
                    "median_kwh": round(median, 3),
                    "deviation_pct": dev_pct,
                    "message": f"Hourly spike detected at {r['timestamp']}: {val:.2f} kWh exceeds normal range threshold of {threshold:.2f} kWh."
                })

        return spikes

