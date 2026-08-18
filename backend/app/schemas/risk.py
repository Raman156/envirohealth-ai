from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class RiskScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: UUID
    overall_score: float
    risk_level: str
    health_score: Optional[float] = None
    air_score: Optional[float] = None
    water_score: Optional[float] = None
    weather_score: Optional[float] = None
    historical_score: Optional[float] = None
    trend: Optional[str] = None
    confidence: float
    calculated_at: datetime


class RiskPredictionResponse(BaseModel):
    location_id: UUID
    risk_type: str
    risk_score: float
    risk_level: str
    confidence: float
    trend: str
    explanation: List[str]
    model_version: str
    calculated_at: datetime
