from pydantic import BaseModel
from typing import List


class TrendItem(BaseModel):
    condition: str
    current: int
    previous: int
    change_percent: float
    direction: str  # INCREASING, DECREASING, STABLE


class TrendsResponse(BaseModel):
    location_id: str
    period_days: int
    trends: List[TrendItem]


class TrendResponse(BaseModel):
    condition: str
    current: int
    previous: int
    change_percent: float
    direction: str
