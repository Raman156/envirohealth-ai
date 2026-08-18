"""Pure unit tests for trend detection — no DB dependency."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest.mock as mock
sys.modules['asyncpg'] = mock.MagicMock()
sys.modules['geoalchemy2'] = mock.MagicMock()
sys.modules['geoalchemy2.types'] = mock.MagicMock()

import pytest
from app.analytics.trend_detector import calculate_trend, build_symptom_trends


def test_trend_increasing():
    change, direction = calculate_trend(100, 60)
    assert direction == "INCREASING"
    assert change > 10


def test_trend_decreasing():
    change, direction = calculate_trend(30, 100)
    assert direction == "DECREASING"
    assert change < -10


def test_trend_stable():
    change, direction = calculate_trend(50, 52)
    assert direction == "STABLE"


def test_trend_from_zero():
    change, direction = calculate_trend(10, 0)
    assert direction == "INCREASING"
    assert change == 100.0


def test_build_symptom_trends():
    current = {"fever": 40, "cough": 30}
    previous = {"fever": 20, "cough": 35}
    trends = build_symptom_trends(current, previous)
    fever_trend = next(t for t in trends if t.condition == "fever")
    assert fever_trend.direction == "INCREASING"
    assert abs(fever_trend.change_percent - 100.0) < 0.1
