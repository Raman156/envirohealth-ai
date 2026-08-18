import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from app.db.base import Base
from app.db.types import UUIDType


class AlertType(str, enum.Enum):
    HEALTH_RISK = "HEALTH_RISK"
    AIR_QUALITY = "AIR_QUALITY"
    WATER_QUALITY = "WATER_QUALITY"
    WEATHER = "WEATHER"
    TREND = "TREND"
    SENSOR = "SENSOR"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    location_id = Column(UUIDType, ForeignKey("locations.id"), nullable=True)
    title = Column(String(255), nullable=False)
    message = Column(String(1000), nullable=False)
    risk_score = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
