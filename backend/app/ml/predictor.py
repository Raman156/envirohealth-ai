"""
Risk prediction engine — uses ML model if available, falls back to rules.
"""
import os
from typing import Dict, Optional
from uuid import UUID
from app.ml.fallback import RuleBasedPredictor

# Attempt to load trained model
_ml_model = None
_model_available = False

try:
    import pickle
    model_path = os.path.join(os.path.dirname(__file__), "../../ml/models/risk_model.pkl")
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            _ml_model = pickle.load(f)
        _model_available = True
except Exception:
    pass

_fallback = RuleBasedPredictor()


def predict_risk(
    location_id: UUID,
    env_readings: Dict[str, float],
    symptom_counts: Dict[str, int],
    symptom_trends: Optional[Dict[str, float]] = None,
    historical_avg_score: float = 30.0,
) -> Dict:
    """Main prediction entry point — ML or rule-based fallback."""
    if _model_available and _ml_model is not None:
        try:
            return _ml_model.predict(location_id, env_readings, symptom_counts, symptom_trends, historical_avg_score)
        except Exception:
            pass  # Fall through to rule-based

    return _fallback.predict(location_id, env_readings, symptom_counts, symptom_trends, historical_avg_score)


def is_ml_model_available() -> bool:
    return _model_available
