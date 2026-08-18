from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class HistoryDataPoint(BaseModel):
    timestamp: str
    value: float


class HistoryResponse(BaseModel):
    location: str
    location_id: str
    period: str
    health: Dict[str, int]
    environment: Dict[str, Optional[float]]
    health_series: Optional[Dict[str, List[HistoryDataPoint]]] = None
    environment_series: Optional[Dict[str, List[HistoryDataPoint]]] = None
    risk_series: Optional[List[HistoryDataPoint]] = None
