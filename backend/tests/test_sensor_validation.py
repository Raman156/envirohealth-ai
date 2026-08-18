"""Unit tests for sensor reading validation — no DB dependency."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest.mock as mock
sys.modules['asyncpg'] = mock.MagicMock()
sys.modules['geoalchemy2'] = mock.MagicMock()
sys.modules['geoalchemy2.types'] = mock.MagicMock()
sys.modules['sqlalchemy.dialects.postgresql'] = mock.MagicMock()

import pytest
from pydantic import ValidationError
from datetime import datetime, timezone


def test_valid_sensor_reading():
    from app.schemas.environmental import SensorReadingIngest
    data = SensorReadingIngest(
        sensor_code="AIR-TEST-001",
        timestamp=datetime.now(timezone.utc),
        readings={"pm25": 85, "pm10": 120, "aqi": 164, "temperature": 34, "humidity": 61},
    )
    assert data.sensor_code == "AIR-TEST-001"
    assert data.readings["pm25"] == 85


def test_invalid_pm25_out_of_range():
    from app.schemas.environmental import SensorReadingIngest
    with pytest.raises(ValidationError):
        SensorReadingIngest(
            sensor_code="AIR-TEST-001",
            timestamp=datetime.now(timezone.utc),
            readings={"pm25": 9999},
        )


def test_invalid_ph_out_of_range():
    from app.schemas.environmental import SensorReadingIngest
    with pytest.raises(ValidationError):
        SensorReadingIngest(
            sensor_code="WTR-TEST-001",
            timestamp=datetime.now(timezone.utc),
            readings={"water_ph": 20.0},
        )


def test_temperature_in_range():
    from app.schemas.environmental import SensorReadingIngest
    data = SensorReadingIngest(
        sensor_code="WTH-TEST-001",
        timestamp=datetime.now(timezone.utc),
        readings={"temperature": -30, "humidity": 80},
    )
    assert data.readings["temperature"] == -30
