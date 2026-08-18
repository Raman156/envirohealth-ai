from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


PARAMETER_RANGES = {
    "aqi": (0, 500),
    "pm25": (0, 500),
    "pm10": (0, 600),
    "co": (0, 50),
    "no2": (0, 2000),
    "so2": (0, 2000),
    "o3": (0, 500),
    "temperature": (-60, 60),
    "humidity": (0, 100),
    "rainfall": (0, 500),
    "wind_speed": (0, 200),
    "water_ph": (0, 14),
    "water_turbidity": (0, 1000),
    "water_tds": (0, 10000),
    "water_temperature": (0, 100),
    "uv_index": (0, 20),
    "pressure": (800, 1100),
}


class EnvironmentalReadingCreate(BaseModel):
    location_id: UUID
    sensor_id: Optional[UUID] = None
    parameter: str
    value: float
    unit: str
    source: str
    source_type: str = "SENSOR"
    timestamp: datetime
    quality_score: float = Field(default=1.0, ge=0, le=1)


class SensorReadingIngest(BaseModel):
    sensor_code: str
    timestamp: datetime
    readings: Dict[str, float]

    @field_validator("readings")
    @classmethod
    def validate_readings(cls, v):
        for param, value in v.items():
            param_lower = param.lower()
            if param_lower in PARAMETER_RANGES:
                min_val, max_val = PARAMETER_RANGES[param_lower]
                if not (min_val <= value <= max_val):
                    raise ValueError(
                        f"Value {value} for {param} is outside valid range [{min_val}, {max_val}]"
                    )
        return v


class EnvironmentalReadingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    location_id: UUID
    parameter: str
    value: float
    unit: str
    source: str
    timestamp: datetime
