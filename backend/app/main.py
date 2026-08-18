from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.routes import auth, health_reports, sensors, locations, heatmap, trends, history, alerts, risk, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("EnviroHealth AI starting up", environment=settings.ENVIRONMENT)

    # Import here to trigger lazy engine creation only at startup
    from app.db.base import get_engine, Base
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")

    task = asyncio.create_task(_background_job_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await get_engine().dispose()
    logger.info("EnviroHealth AI shut down")


app = FastAPI(
    title="EnviroHealth AI",
    description="Environmental Health Risk Prediction & Early Warning Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again later."},
    )


PREFIX = settings.API_V1_STR
app.include_router(auth.router, prefix=PREFIX)
app.include_router(health_reports.router, prefix=PREFIX)
app.include_router(sensors.router, prefix=PREFIX)
app.include_router(locations.router, prefix=PREFIX)
app.include_router(heatmap.router, prefix=PREFIX)
app.include_router(trends.router, prefix=PREFIX)
app.include_router(history.router, prefix=PREFIX)
app.include_router(alerts.router, prefix=PREFIX)
app.include_router(risk.router, prefix=PREFIX)
app.include_router(admin.router, prefix=PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "EnviroHealth AI"}


async def _background_job_loop():
    from app.db.base import get_session_factory
    from app.services.sensor_service import check_and_update_sensor_status

    while True:
        try:
            async with get_session_factory()() as db:
                await check_and_update_sensor_status(db)
        except Exception as e:
            logger.warning("Background job error", error=str(e))
        await asyncio.sleep(settings.CHECK_SENSOR_STATUS_INTERVAL)
