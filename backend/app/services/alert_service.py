from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.alert import Alert, AlertType, AlertSeverity
from app.core.config import settings


async def get_active_alerts(db: AsyncSession, location_id=None, limit: int = 20) -> List[Alert]:
    now = datetime.utcnow()
    conditions = [Alert.is_active == True, Alert.expires_at > now]
    if location_id:
        conditions.append(Alert.location_id == str(location_id))
    result = await db.execute(
        select(Alert).where(and_(*conditions)).order_by(Alert.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_alert(
    db: AsyncSession,
    type: str,
    severity: str,
    title: str,
    message: str,
    location_id=None,
    risk_score: Optional[float] = None,
    ttl_hours: int = 24,
) -> Alert:
    # Deduplication: skip if a similar alert was created within cooldown window
    if location_id:
        cutoff = datetime.utcnow() - timedelta(minutes=settings.ALERT_COOLDOWN_MINUTES)
        result = await db.execute(
            select(Alert).where(
                and_(
                    Alert.location_id == str(location_id),
                    Alert.type == type,
                    Alert.created_at >= cutoff,
                    Alert.is_active == True,
                )
            ).limit(1)
        )
        if result.scalar_one_or_none():
            return result.scalar_one_or_none()  # type: ignore

    alert = Alert(
        type=type, severity=severity,
        location_id=str(location_id) if location_id else None,
        title=title, message=message, risk_score=risk_score,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def evaluate_and_generate_alerts(db: AsyncSession, location_id, risk_data: dict):
    overall = risk_data.get("risk_score", 0)
    env = risk_data.get("env_readings", {})
    trends = risk_data.get("symptom_trends", {})
    alerts_created = []

    if overall >= settings.ALERT_RISK_THRESHOLD:
        a = await create_alert(
            db, type=AlertType.HEALTH_RISK,
            severity="HIGH" if overall >= 80 else "MODERATE",
            title="Elevated environmental health risk detected",
            message=f"Overall risk score has reached {overall:.0f}/100. Increased environmental and community health activity detected.",
            location_id=location_id, risk_score=overall,
        )
        alerts_created.append(a)

    aqi = env.get("aqi", 0)
    if aqi >= settings.ALERT_AQI_THRESHOLD:
        a = await create_alert(
            db, type=AlertType.AIR_QUALITY,
            severity="HIGH" if aqi >= 200 else "MODERATE",
            title="Poor air quality conditions detected",
            message=f"Air Quality Index is {aqi:.0f}, which poses respiratory health risks.",
            location_id=location_id, risk_score=overall,
        )
        alerts_created.append(a)

    for symptom, change in (trends or {}).items():
        if change >= settings.ALERT_SYMPTOM_GROWTH_THRESHOLD:
            a = await create_alert(
                db, type=AlertType.TREND,
                severity="MODERATE",
                title=f"Significant increase in {symptom} reports",
                message=f"Community reports of {symptom} have increased by {change:.0f}% compared to the previous period.",
                location_id=location_id,
            )
            alerts_created.append(a)

    return alerts_created
