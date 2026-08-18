"""Pure unit tests for risk calculation — no DB dependency."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Stub out the db module before anything else imports it
import unittest.mock as mock
sys.modules['asyncpg'] = mock.MagicMock()
sys.modules['geoalchemy2'] = mock.MagicMock()
sys.modules['geoalchemy2.types'] = mock.MagicMock()

import pytest
from app.analytics.risk_calculator import (
    calculate_air_risk_score,
    calculate_water_risk_score,
    calculate_weather_risk_score,
    calculate_health_activity_score,
    calculate_overall_risk,
    get_risk_level,
    build_explanation,
)


def test_get_risk_level():
    assert get_risk_level(10) == "LOW"
    assert get_risk_level(30) == "MODERATE"
    assert get_risk_level(50) == "ELEVATED"
    assert get_risk_level(70) == "HIGH"
    assert get_risk_level(90) == "VERY HIGH"


def test_air_risk_with_high_aqi():
    score = calculate_air_risk_score({"aqi": 300, "pm25": 120, "pm10": 200})
    assert score > 60


def test_air_risk_with_clean_air():
    score = calculate_air_risk_score({"aqi": 30, "pm25": 5, "pm10": 15})
    assert score < 30


def test_water_risk_with_bad_ph():
    score = calculate_water_risk_score({"water_ph": 4.0, "water_turbidity": 20, "water_tds": 800})
    assert score > 40


def test_weather_extreme_heat():
    score = calculate_weather_risk_score({"temperature": 46, "humidity": 90})
    assert score > 40


def test_overall_risk_weights():
    overall = calculate_overall_risk(80, 80, 80, 80, 80)
    assert abs(overall - 80.0) < 0.01


def test_explanation_high_aqi():
    reasons = build_explanation(20, 80, 20, 20, {}, {"aqi": 200, "pm25": 80})
    assert len(reasons) > 0
    assert any("AQI" in r or "air" in r.lower() for r in reasons)


def test_health_activity_score():
    score = calculate_health_activity_score({"fever": 100, "cough": 50}, total_population=10000)
    assert score > 0
    assert score <= 100
