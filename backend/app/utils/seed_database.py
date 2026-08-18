"""
Seed database with realistic synthetic demo data.
Run: python -m app.utils.seed_database
"""
import asyncio
import random
import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_engine, get_session_factory, Base
from app.models.location import Location
from app.models.sensor import Sensor, SensorType, SensorStatus
from app.models.health_report import HealthReport, SeverityLevel, AgeGroup
from app.models.environmental_reading import EnvironmentalReading
from app.models.risk_score import RiskScore
from app.models.alert import Alert
from app.models.user import User, UserRole
from app.core.security import hash_password

LOCATIONS = [
    {"name": "Greater Noida Sector 1", "city": "Greater Noida", "state": "UP",    "lat": 28.4744, "lng": 77.5040, "grid": "G101"},
    {"name": "Connaught Place",         "city": "New Delhi",     "state": "Delhi", "lat": 28.6315, "lng": 77.2167, "grid": "G102"},
    {"name": "Andheri East",            "city": "Mumbai",        "state": "MH",    "lat": 19.1136, "lng": 72.8697, "grid": "G103"},
    {"name": "Koramangala",             "city": "Bengaluru",     "state": "KA",    "lat": 12.9352, "lng": 77.6245, "grid": "G104"},
    {"name": "Salt Lake City",          "city": "Kolkata",       "state": "WB",    "lat": 22.5726, "lng": 88.3639, "grid": "G105"},
    {"name": "Anna Nagar",              "city": "Chennai",       "state": "TN",    "lat": 13.0843, "lng": 80.2097, "grid": "G106"},
    {"name": "Banjara Hills",           "city": "Hyderabad",     "state": "TS",    "lat": 17.4126, "lng": 78.4484, "grid": "G107"},
    {"name": "Civil Lines",             "city": "Jaipur",        "state": "RJ",    "lat": 26.9124, "lng": 75.7873, "grid": "G108"},
    {"name": "Shivaji Nagar",           "city": "Pune",          "state": "MH",    "lat": 18.5308, "lng": 73.8474, "grid": "G109"},
    {"name": "Sector 17",               "city": "Chandigarh",    "state": "PB",    "lat": 30.7393, "lng": 76.7856, "grid": "G110"},
]

# (base_aqi, risk_multiplier, dominant_symptoms)
PROFILES = {
    "G101": (164, 1.4, ["cough", "fever", "breathing_difficulty"]),
    "G102": (187, 1.6, ["cough", "headache", "fever"]),
    "G103": (95,  1.0, ["cold", "cough", "fever"]),
    "G104": (72,  0.8, ["fever", "headache", "fatigue"]),
    "G105": (142, 1.3, ["diarrhea", "vomiting", "fever"]),
    "G106": (88,  0.9, ["fever", "skin_irritation", "cough"]),
    "G107": (118, 1.1, ["fever", "fatigue", "headache"]),
    "G108": (201, 1.7, ["breathing_difficulty", "cough", "headache"]),
    "G109": (79,  0.85,["cold", "fever", "cough"]),
    "G110": (110, 1.0, ["cough", "fever", "cold"]),
}
ALL_SYMPTOMS = ["fever","cough","cold","headache","vomiting","diarrhea",
                "breathing_difficulty","skin_irritation","fatigue","body_pain"]
UNIT_MAP = {
    "aqi":"AQI","pm25":"µg/m³","pm10":"µg/m³",
    "temperature":"°C","humidity":"%","rainfall":"mm",
    "water_ph":"pH","water_tds":"mg/L","water_turbidity":"NTU",
}


async def seed(db: AsyncSession):
    print("🌱 Seeding EnviroHealth AI demo data...")

    # Admin user
    admin = User(
        anonymous_id=str(uuid.uuid4()),
        email="admin@envirohealth.ai",
        password_hash=hash_password("Admin@1234"),
        role=UserRole.ADMIN,
    )
    db.add(admin)
    await db.flush()

    # Locations
    locations = []
    for meta in LOCATIONS:
        loc = Location(
            name=meta["name"], city=meta["city"], state=meta["state"], country="India",
            latitude=meta["lat"], longitude=meta["lng"], grid_id=meta["grid"],
        )
        db.add(loc)
        locations.append(loc)
    await db.flush()

    # Sensors — 2 per location (AIR + WATER)
    sensors = []
    for i, loc in enumerate(locations):
        grid = LOCATIONS[i]["grid"]
        for stype, prefix in [(SensorType.AIR, "AIR"), (SensorType.WATER, "WTR")]:
            s = Sensor(
                sensor_code=f"{prefix}-{grid}-001",
                name=f"{stype.value} Sensor — {loc.city}",
                type=stype,
                location_id=str(loc.id),
                latitude=loc.latitude + random.uniform(-0.005, 0.005),
                longitude=loc.longitude + random.uniform(-0.005, 0.005),
                status=SensorStatus.ONLINE if random.random() > 0.15 else SensorStatus.OFFLINE,
                last_seen=datetime.utcnow() - timedelta(minutes=random.randint(1, 20)),
            )
            db.add(s)
            sensors.append((s, loc, grid))
    await db.flush()

    # Environmental readings — 90 days
    print("  Creating environmental readings...")
    now = datetime.utcnow()
    for sensor, loc, grid in sensors:
        base_aqi, multiplier, _ = PROFILES[grid]
        for day in range(90):
            ts = now - timedelta(days=day, hours=random.randint(0, 23))
            sf = 1.0 + 0.2 * (day % 30) / 30
            aqi = base_aqi * sf * random.uniform(0.8, 1.2)
            vals = {
                "aqi":           round(aqi, 1),
                "pm25":          round(aqi * 0.5 * random.uniform(0.9, 1.1), 1),
                "pm10":          round(aqi * 0.75 * random.uniform(0.9, 1.1), 1),
                "temperature":   round(28 + multiplier * 3 + random.uniform(-4, 4), 1),
                "humidity":      round(min(99, 55 + multiplier * 8 + random.uniform(-10, 10)), 1),
                "rainfall":      round(max(0, random.gauss(3, 5)), 1),
                "water_ph":      round(random.uniform(6.2, 8.5), 2),
                "water_tds":     round(250 + multiplier * 100 + random.uniform(-50, 100), 1),
                "water_turbidity": round(max(0.1, multiplier * 2 + random.gauss(0, 1)), 2),
            }
            for param, value in vals.items():
                db.add(EnvironmentalReading(
                    location_id=str(loc.id), sensor_id=str(sensor.id),
                    parameter=param, value=value, unit=UNIT_MAP.get(param, ""),
                    source=sensor.sensor_code, source_type="SENSOR",
                    timestamp=ts, quality_score=round(random.uniform(0.85, 1.0), 2),
                ))

    await db.flush()

    # Health reports — 50–85 per location over 60 days
    print("  Creating health reports...")
    for i, loc in enumerate(locations):
        grid = LOCATIONS[i]["grid"]
        _, multiplier, dominant = PROFILES[grid]
        count = int(50 * multiplier) + random.randint(10, 30)
        for _ in range(count):
            ts = now - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
            pool = dominant * 3 + ALL_SYMPTOMS
            syms = list(set(random.choices(pool, k=random.randint(1, 3))))
            severity = random.choices(list(SeverityLevel), weights=[0.5, 0.35, 0.15])[0]
            r = HealthReport(
                anonymous_user_id=str(uuid.uuid4()),
                location_id=str(loc.id),
                severity=severity,
                age_group=random.choice(list(AgeGroup)),
                source="COMMUNITY",
                timestamp=ts,
            )
            r.symptoms = syms
            db.add(r)

    await db.flush()

    # Risk scores — 30 days history
    print("  Creating risk scores...")
    from app.analytics.risk_calculator import (
        calculate_air_risk_score, calculate_water_risk_score,
        calculate_weather_risk_score, calculate_overall_risk, get_risk_level
    )
    for i, loc in enumerate(locations):
        grid = LOCATIONS[i]["grid"]
        base_aqi, multiplier, _ = PROFILES[grid]
        for day in range(30):
            ts = now - timedelta(days=day)
            env = {
                "aqi": base_aqi * (1 + random.uniform(-0.15, 0.15)),
                "pm25": base_aqi * 0.5,
                "water_ph": random.uniform(6.5, 8.0),
                "water_tds": 300 * multiplier,
                "temperature": 30 + multiplier * 2,
                "humidity": 60 + multiplier * 5,
            }
            air = calculate_air_risk_score(env)
            water = calculate_water_risk_score(env)
            weather = calculate_weather_risk_score(env)
            health = min(multiplier * 30 + random.uniform(-10, 10), 100)
            overall = round(min(max(calculate_overall_risk(health, air, water, weather, air * 0.8), 0), 100), 1)
            expl = ["Air quality is elevated", "Community health reports increasing"] if multiplier > 1.2 else ["Conditions within normal range"]
            db.add(RiskScore(
                location_id=str(loc.id), grid_id=grid,
                overall_score=overall, risk_level=get_risk_level(overall),
                health_score=round(health, 1), air_score=round(air, 1),
                water_score=round(water, 1), weather_score=round(weather, 1),
                historical_score=round(air * 0.8, 1),
                trend="INCREASING" if multiplier > 1.2 else "STABLE",
                explanation=json.dumps(expl),
                model_version="rule_based_v1", confidence=0.7,
                calculated_at=ts,
            ))

    await db.flush()

    # Alerts for high-risk locations
    print("  Creating alerts...")
    for i, loc in enumerate(locations):
        grid = LOCATIONS[i]["grid"]
        _, multiplier, _ = PROFILES[grid]
        if multiplier >= 1.3:
            db.add(Alert(
                type="HEALTH_RISK",
                severity="HIGH" if multiplier >= 1.5 else "MODERATE",
                location_id=str(loc.id),
                title=f"Elevated respiratory health risk in {LOCATIONS[i]['city']}",
                message=f"Respiratory symptoms and poor air quality have increased in {LOCATIONS[i]['name']}.",
                risk_score=round(multiplier * 55, 1),
                is_active=True,
                expires_at=now + timedelta(hours=24),
            ))
        if grid in ("G102", "G108"):
            db.add(Alert(
                type="AIR_QUALITY",
                severity="HIGH",
                location_id=str(loc.id),
                title=f"Very poor air quality in {LOCATIONS[i]['city']}",
                message=f"AQI has reached {PROFILES[grid][0]} in {LOCATIONS[i]['name']}. Sensitive groups should avoid outdoor activities.",
                risk_score=round(PROFILES[grid][0] / 5, 1),
                is_active=True,
                expires_at=now + timedelta(hours=12),
            ))

    await db.commit()
    print("✅ Seed complete!")
    print(f"   • {len(locations)} locations")
    print(f"   • {len(sensors)} sensors")
    print("   • Admin login: admin@envirohealth.ai / Admin@1234")


async def main():
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with get_session_factory()() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
