from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class HeatmapPoint(BaseModel):
    grid_id: str
    location_id: UUID
    location_name: str
    latitude: float
    longitude: float
    risk_score: float
    risk_level: str
    value: Optional[float] = None  # for specific layer (AQI, etc.)
    label: Optional[str] = None


class HeatmapResponse(BaseModel):
    layer: str
    points: List[HeatmapPoint]
    min_value: Optional[float] = None
    max_value: Optional[float] = None
