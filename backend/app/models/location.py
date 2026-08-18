import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from app.db.base import Base
from app.db.types import UUIDType


class Location(Base):
    __tablename__ = "locations"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    grid_id = Column(String(20), nullable=True, index=True)
    population_estimate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
