from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "EnviroHealth AI"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://envirohealth:envirohealth@localhost:5432/envirohealth_db"
    SYNC_DATABASE_URL: str = "postgresql://envirohealth:envirohealth@localhost:5432/envirohealth_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # External APIs
    WEATHER_API_KEY: Optional[str] = None
    AIR_QUALITY_API_KEY: Optional[str] = None
    WATER_QUALITY_API_KEY: Optional[str] = None

    # Rate limiting
    RATE_LIMIT_HEALTH_REPORTS: str = "10/minute"

    # Background job intervals (seconds)
    FETCH_ENV_DATA_INTERVAL: int = 600
    UPDATE_RISK_SCORES_INTERVAL: int = 900
    CALCULATE_TRENDS_INTERVAL: int = 3600
    CHECK_SENSOR_STATUS_INTERVAL: int = 300

    # Risk scoring weights (must sum to 1.0)
    RISK_WEIGHT_HEALTH: float = 0.35
    RISK_WEIGHT_AIR: float = 0.25
    RISK_WEIGHT_WATER: float = 0.20
    RISK_WEIGHT_WEATHER: float = 0.10
    RISK_WEIGHT_HISTORICAL: float = 0.10

    # Alert thresholds
    ALERT_RISK_THRESHOLD: float = 60.0
    ALERT_SYMPTOM_GROWTH_THRESHOLD: float = 50.0
    ALERT_AQI_THRESHOLD: float = 150.0
    ALERT_COOLDOWN_MINUTES: int = 60

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
