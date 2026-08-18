import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from app.db.base import Base
from app.db.types import UUIDType


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUIDType, ForeignKey("locations.id"), nullable=False, index=True)
    grid_id = Column(String(20), nullable=True, index=True)
    overall_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    health_score = Column(Float, nullable=True)
    air_score = Column(Float, nullable=True)
    water_score = Column(Float, nullable=True)
    weather_score = Column(Float, nullable=True)
    historical_score = Column(Float, nullable=True)
    trend = Column(String(20), nullable=True)
    explanation = Column(Text, nullable=True)   # JSON stored as text
    model_version = Column(String(20), default="rule_based_v1")
    confidence = Column(Float, default=0.7)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
