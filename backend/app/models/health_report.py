import enum
import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from app.db.base import Base
from app.db.types import UUIDType


class SymptomType(str, enum.Enum):
    FEVER = "fever"
    COUGH = "cough"
    COLD = "cold"
    HEADACHE = "headache"
    VOMITING = "vomiting"
    DIARRHEA = "diarrhea"
    BREATHING_DIFFICULTY = "breathing_difficulty"
    SKIN_IRRITATION = "skin_irritation"
    FATIGUE = "fatigue"
    BODY_PAIN = "body_pain"


class SeverityLevel(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class AgeGroup(str, enum.Enum):
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    SENIOR = "senior"


class HealthReport(Base):
    __tablename__ = "health_reports"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    anonymous_user_id = Column(String(64), nullable=False, index=True)
    location_id = Column(UUIDType, ForeignKey("locations.id"), nullable=False, index=True)
    # Store symptoms as JSON string (SQLite-compatible, no ARRAY type)
    _symptoms = Column("symptoms", Text, nullable=False, default="[]")
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MILD)
    age_group = Column(Enum(AgeGroup), nullable=True)
    source = Column(String(50), default="COMMUNITY")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def symptoms(self):
        try:
            return json.loads(self._symptoms) if self._symptoms else []
        except Exception:
            return []

    @symptoms.setter
    def symptoms(self, value):
        self._symptoms = json.dumps(value if value else [])
