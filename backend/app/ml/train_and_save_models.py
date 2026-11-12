import os
import pickle
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, r"C:\Users\zoeera\.gemini\antigravity\scratch\powerpulse\backend")

from app.ml.estimators import (
    BillHistoryModel,
    DailyXGBModel,
    WeeklyXGBModel,
    MonthlyXGBModel,
    SolarGenerationModel,
    ApplianceRFModel
)

MODELS_DIR = Path(r"C:\Users\zoeera\.gemini\antigravity\scratch\powerpulse\backend\models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def save_all_models():
    models = {
        "bill_history_model.joblib": BillHistoryModel(),
        "daily_xgb_model.joblib": DailyXGBModel(),
        "weekly_xgb_model.joblib": WeeklyXGBModel(),
        "monthly_xgb_model.joblib": MonthlyXGBModel(),
        "solar_generation_model.joblib": SolarGenerationModel(),
        "appliance_rf_model.joblib": ApplianceRFModel()
    }
    
    for filename, model in models.items():
        filepath = MODELS_DIR / filename
        with open(filepath, "wb") as f:
            pickle.dump(model, f, protocol=4)
        print(f"[OK] Saved model: {filename} ({os.path.getsize(filepath)} bytes)")

if __name__ == "__main__":
    save_all_models()
