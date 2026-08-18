from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    severity: str
    location_id: Optional[UUID] = None
    title: str
    message: str
    risk_score: Optional[float] = None
    is_active: bool
    created_at: datetime
