"""
Rule-based fallback prediction when no ML model is trained.
Transparent, explainable, and uses the same interface as the ML model.
"""
from typing import Dict, List, Optional
from datetime import datetime
from uuid import UUID
from app.analytics.risk_calculator import (
    calculate_air_risk_score,
    calculate_water_risk_score,
    calculate_weather_risk_score,
    calculate_health_activity_score,
    calculate_overall_risk,
    get_risk_level,
    build_explanation,
)


class RuleBasedPredictor:
    """Transparent rule-based risk predictor used as ML fallback."""

    def predict(
        self,
        location_id: UUID,
        env_readings: Dict[str, float],
        symptom_counts: Dict[str, int],
        symptom_trends: Optional[Dict[str, float]] = None,
        historical_avg_score: float = 30.0,
    ) -> Dict:
        health_score = calculate_health_activity_score(symptom_counts)
        air_score = calculate_air_risk_score(env_readings)
        water_score = calculate_water_risk_score(env_readings)
        weather_score = calculate_weather_risk_score(env_readings)

        overall = calculate_overall_risk(
            health_score, air_score, water_score, weather_score, historical_avg_score
        )
        overall = round(min(max(overall, 0), 100), 1)

        # Determine dominant risk type
        scores = {
            "respiratory": air_score * 0.7 + health_score * 0.3,
            "waterborne": water_score * 0.7 + health_score * 0.3,
            "heat_stress": weather_score * 0.8 + health_score * 0.2,
            "general": overall,
        }
        risk_type = max(scores, key=scores.get)

        explanation = build_explanation(
            health_score, air_score, water_score, weather_score,
            symptom_trends, env_readings
        )

        # Determine trend from historical comparison
        if overall > historical_avg_score + 10:
            trend = "INCREASING"
        elif overall < historical_avg_score - 10:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "location_id": location_id,
            "risk_type": risk_type,
            "risk_score": overall,
            "risk_level": get_risk_level(overall),
            "health_score": round(health_score, 1),
            "air_score": round(air_score, 1),
            "water_score": round(water_score, 1),
            "weather_score": round(weather_score, 1),
            "historical_score": round(historical_avg_score, 1),
            "confidence": 0.70,
            "trend": trend,
            "explanation": explanation,
            "model_version": "rule_based_v1",
            "calculated_at": datetime.utcnow(),
        }
