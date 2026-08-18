from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class LocationCreate(BaseModel):
    name: str
    city: str
    state: str
    country: str = "India"
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    grid_id: Optional[str] = None


class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: object  # UUID
    name: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    grid_id: Optional[str] = None
