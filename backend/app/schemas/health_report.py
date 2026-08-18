from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.health_report import SymptomType, SeverityLevel, AgeGroup


class HealthReportCreate(BaseModel):
    symptoms: List[SymptomType] = Field(..., min_length=1, max_length=10)
    severity: SeverityLevel = SeverityLevel.MILD
    age_group: Optional[AgeGroup] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    @field_validator("symptoms")
    @classmethod
    def deduplicate_symptoms(cls, v):
        return list(set(v))


class HealthReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    symptoms: List[str]
    severity: str
    timestamp: datetime
    location_id: UUID
