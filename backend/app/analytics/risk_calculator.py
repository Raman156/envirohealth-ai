from typing import Dict, Optional, List
from app.core.config import settings


RISK_LEVELS = [
    (20, "LOW"),
    (40, "MODERATE"),
    (60, "ELEVATED"),
    (80, "HIGH"),
    (100, "VERY HIGH"),
]


def get_risk_level(score: float) -> str:
    for threshold, level in RISK_LEVELS:
        if score <= threshold:
            return level
    return "VERY HIGH"


def calculate_air_risk_score(readings: Dict[str, float]) -> float:
    """Convert AQI/PM readings to 0-100 risk score."""
    score = 0.0
    weight_total = 0.0

    aqi = readings.get("aqi")
    if aqi is not None:
        # AQI 0-500 mapped to 0-100
        score += min(aqi / 5.0, 100) * 0.5
        weight_total += 0.5

    pm25 = readings.get("pm25")
    if pm25 is not None:
        # WHO guideline: 15 µg/m³ annual, 35 for 24hr
        score += min(pm25 / 2.5, 100) * 0.35
        weight_total += 0.35

    pm10 = readings.get("pm10")
    if pm10 is not None:
        score += min(pm10 / 1.5, 100) * 0.15
        weight_total += 0.15

    if weight_total == 0:
        return 0.0
    return min(score / weight_total, 100) if weight_total < 1 else min(score, 100)


def calculate_water_risk_score(readings: Dict[str, float]) -> float:
    score = 0.0
    weight_total = 0.0

    ph = readings.get("water_ph")
    if ph is not None:
        # Ideal pH 6.5-8.5; deviations increase risk
        deviation = abs(ph - 7.0)
        score += min(deviation * 20, 100) * 0.3
        weight_total += 0.3

    turbidity = readings.get("water_turbidity")
    if turbidity is not None:
        # WHO guideline: < 1 NTU; up to 5 NTU acceptable
        score += min(turbidity * 20, 100) * 0.35
        weight_total += 0.35

    tds = readings.get("water_tds")
    if tds is not None:
        # WHO: < 300 mg/L excellent, > 1200 unacceptable
        score += min(tds / 12.0, 100) * 0.35
        weight_total += 0.35

    if weight_total == 0:
        return 0.0
    return min(score / weight_total, 100) if weight_total < 1 else min(score, 100)


def calculate_weather_risk_score(readings: Dict[str, float]) -> float:
    score = 0.0

    temp = readings.get("temperature")
    if temp is not None:
        if temp > 40:
            score += min((temp - 40) * 10, 50)
        elif temp < 5:
            score += min((5 - temp) * 10, 50)

    humidity = readings.get("humidity")
    if humidity is not None:
        if humidity > 85:
            score += min((humidity - 85) * 3, 30)

    rainfall = readings.get("rainfall")
    if rainfall is not None:
        if rainfall > 50:
            score += min(rainfall / 5, 30)

    if score == 0:
        return 20.0  # neutral baseline
    return min(score, 100)


def calculate_health_activity_score(symptom_counts: Dict[str, int], total_population: int = 10000) -> float:
    """Score based on symptom report frequency relative to population."""
    if not symptom_counts:
        return 0.0

    total_reports = sum(symptom_counts.values())
    # Rate per 10,000
    rate = (total_reports / total_population) * 10000
    # Rate of 100+ per 10k = very high risk
    return min(rate, 100)


def calculate_overall_risk(
    health_score: float,
    air_score: float,
    water_score: float,
    weather_score: float,
    historical_score: float,
) -> float:
    return (
        health_score * settings.RISK_WEIGHT_HEALTH
        + air_score * settings.RISK_WEIGHT_AIR
        + water_score * settings.RISK_WEIGHT_WATER
        + weather_score * settings.RISK_WEIGHT_WEATHER
        + historical_score * settings.RISK_WEIGHT_HISTORICAL
    )


def build_explanation(
    health_score: float,
    air_score: float,
    water_score: float,
    weather_score: float,
    symptom_trends: Optional[Dict[str, float]] = None,
    env_readings: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Generate human-readable explanation for the risk score."""
    reasons = []

    if air_score > 60:
        aqi = (env_readings or {}).get("aqi", 0)
        reasons.append(f"Air quality is poor (AQI: {aqi:.0f})" if aqi else "Air quality is significantly elevated")
        pm25 = (env_readings or {}).get("pm25", 0)
        if pm25 > 35:
            reasons.append(f"PM2.5 levels ({pm25:.0f} µg/m³) exceed safe thresholds")

    if health_score > 40:
        if symptom_trends:
            top = sorted(symptom_trends.items(), key=lambda x: x[1], reverse=True)[:2]
            for symptom, change in top:
                if change > 20:
                    reasons.append(f"Reports of {symptom} have increased by {change:.0f}%")
        else:
            reasons.append("Community health reports have increased in this area")

    if water_score > 50:
        reasons.append("Water quality indicators are outside normal ranges")

    if weather_score > 60:
        temp = (env_readings or {}).get("temperature")
        if temp and temp > 38:
            reasons.append(f"Extreme heat conditions ({temp:.1f}°C) increase health risks")
        else:
            reasons.append("Weather conditions are contributing to elevated risk")

    if not reasons:
        reasons.append("Multiple environmental factors are slightly elevated")

    return reasons
