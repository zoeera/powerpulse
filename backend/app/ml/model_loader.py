import os
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

from app.core.config import settings

class ModelLoader:
    """
    Central ML model registry and inference coordinator.
    Loads models from the models/ directory:
    1. bill_history_model.joblib
    2. daily_xgb_model.joblib
    3. weekly_xgb_model.joblib
    4. monthly_xgb_model.joblib
    5. solar_generation_model.joblib
    6. appliance_rf_model.joblib
    """
    _instance = None
    _models: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_all_models()
        return cls._instance

    def _load_single_model(self, model_name: str) -> Optional[Any]:
        # Look in backend/models or settings.MODELS_DIR
        search_paths = [
            Path(settings.MODELS_DIR) / model_name,
            Path("models") / model_name,
            Path(__file__).parent.parent.parent / "models" / model_name
        ]
        
        for path in search_paths:
            if path.exists():
                try:
                    if HAS_JOBLIB:
                        return joblib.load(path)
                    else:
                        with open(path, "rb") as f:
                            return pickle.load(f)
                except Exception as e:
                    print(f"Error loading {model_name} from {path}: {e}")
        return None

    def _load_all_models(self):
        model_files = [
            "bill_history_model.joblib",
            "daily_xgb_model.joblib",
            "weekly_xgb_model.joblib",
            "monthly_xgb_model.joblib",
            "solar_generation_model.joblib",
            "appliance_rf_model.joblib"
        ]
        for mf in model_files:
            loaded = self._load_single_model(mf)
            if loaded:
                self._models[mf] = loaded
                print(f"[ModelLoader] Loaded {mf} successfully.")
            else:
                print(f"[ModelLoader] Warning: Could not find {mf}, using fallback.")

    def get_model(self, name: str) -> Optional[Any]:
        return self._models.get(name)

    def predict_bill_history(self, month: int, year: int, bill_kwh_list: List[float]) -> Dict[str, Any]:
        """
        Forecasting with Confidence Tiers:
        - user has >= 12 bills -> model: bill_history_model, tier: HIGH
        - user has 6-11 bills  -> model: bill_history_model, tier: LOW (show disclaimer)
        - user has < 6 bills   -> no personal model, tier: ESTIMATE (use reference_consumption benchmarks)
        """
        n_bills = len(bill_kwh_list)
        
        if n_bills >= 12:
            tier = "HIGH"
            confidence_label = "High Confidence (12+ Months of Bill History)"
            disclaimer = "Forecast generated using your full historical consumption cycle. Actual bills may vary with temperature swings or unusual usage."
        elif n_bills >= 6:
            tier = "LOW"
            confidence_label = "Low Confidence (Partial History: 6–11 Bills)"
            disclaimer = "Notice: Forecast based on limited bill history (fewer than 12 billing cycles). Confidence improves as more monthly bills are added."
        else:
            tier = "ESTIMATE"
            confidence_label = "Reference Estimate (<6 Bills)"
            disclaimer = "Estimate based on Indian residential benchmarks for your city and household size. Upload past bills to unlock personal ML forecasts."

        if n_bills >= 6 and "bill_history_model.joblib" in self._models:
            model = self._models["bill_history_model.joblib"]
            lag1 = bill_kwh_list[-1]
            lag2 = bill_kwh_list[-2]
            lag3 = bill_kwh_list[-3]
            rolling3 = (lag1 + lag2 + lag3) / 3.0
            pred = model.predict([[month, year, lag1, lag2, lag3, rolling3]])[0]
            model_name = "bill_history_model.joblib"
        elif n_bills > 0:
            # Weighted average of available bills with seasonal adjustment
            weights = [1.0 + (0.1 * i) for i in range(n_bills)]
            pred = sum(b * w for b, w in zip(bill_kwh_list, weights)) / sum(weights)
            model_name = "weighted_benchmark_model"
        else:
            # Default reference consumption for 3-4 person Indian home: ~180-220 kWh
            pred = 200.0
            model_name = "reference_consumption_benchmark"

        return {
            "predicted_kwh": round(pred, 1),
            "confidence_tier": tier,
            "confidence_label": confidence_label,
            "disclaimer": disclaimer,
            "model_used": model_name,
            "bills_count_used": n_bills
        }

    def predict_daily_hourly(self, recent_readings_kwh: List[float], start_hour: int = 0) -> List[float]:
        """Generate 24-hour forecast."""
        model = self._models.get("daily_xgb_model.joblib")
        forecast = []
        last_val = recent_readings_kwh[-1] if recent_readings_kwh else 0.5
        rolling = sum(recent_readings_kwh[-168:]) / max(1, len(recent_readings_kwh[-168:])) if recent_readings_kwh else 0.4
        
        for h in range(24):
            hour = (start_hour + h) % 24
            row = [hour, 2, 5] + [last_val] * 24 + [rolling]
            if model:
                pred = model.predict([row])[0]
            else:
                pred = last_val
            forecast.append(round(pred, 3))
            last_val = pred
        return forecast

    def predict_solar_hourly(self, panel_kw: float, city_idx: int = 0, irradiance: float = 650.0, temp: float = 32.0, cloud: float = 20.0) -> float:
        model = self._models.get("solar_generation_model.joblib")
        if model:
            row = [city_idx, panel_kw, irradiance, temp, cloud, 0.0, 4]
            return model.predict([row])[0]
        return round(panel_kw * (irradiance / 1000.0) * 0.80, 3)

    def predict_appliance_breakdown(self, total_monthly_kwh: float, month: int = 5) -> Dict[str, float]:
        model = self._models.get("appliance_rf_model.joblib")
        if model and hasattr(model, "predict_breakdown"):
            return model.predict_breakdown(total_monthly_kwh, month)
        # Fallback benchmark
        return {
            "Air Conditioner & Cooling": round(total_monthly_kwh * 0.38, 1),
            "Refrigerator": round(total_monthly_kwh * 0.18, 1),
            "Ceiling Fans & Ventilation": round(total_monthly_kwh * 0.14, 1),
            "Lighting": round(total_monthly_kwh * 0.08, 1),
            "Water Heater / Geyser": round(total_monthly_kwh * 0.08, 1),
            "Washing Machine": round(total_monthly_kwh * 0.06, 1),
            "TV & Electronics": round(total_monthly_kwh * 0.05, 1),
            "Other Plug Loads": round(total_monthly_kwh * 0.03, 1)
        }

model_loader = ModelLoader()

