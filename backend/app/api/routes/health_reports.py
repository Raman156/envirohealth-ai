import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.health_report import HealthReportCreate, HealthReportResponse
from app.services.health_report_service import submit_health_report

router = APIRouter(prefix="/health-reports", tags=["Health Reports"])


@router.post("", response_model=HealthReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_report(
    data: HealthReportCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Submit an anonymous community health report."""
    # Generate anonymous ID from client IP (hashed) — not stored as PII
    client_ip = request.client.host if request.client else "unknown"
    anon_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, client_ip + str(data.latitude)[:6]))

    try:
        report = await submit_health_report(db, data, anon_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return HealthReportResponse(
        id=report.id,
        symptoms=report.symptoms,
        severity=report.severity,
        timestamp=report.timestamp,
        location_id=report.location_id,
    )
