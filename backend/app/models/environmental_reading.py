import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from app.db.base import Base
from app.db.types import UUIDType


class EnvironmentalReading(Base):
    __tablename__ = "environmental_readings"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    location_id = Column(UUIDType, ForeignKey("locations.id"), nullable=False, index=True)
    sensor_id = Column(UUIDType, ForeignKey("sensors.id"), nullable=True, index=True)
    parameter = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    source = Column(String(50), nullable=False)
    source_type = Column(String(50), nullable=False, default="SENSOR")
    timestamp = Column(DateTime, nullable=False, index=True)
    quality_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
