"""FastAPI application initialization."""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from prometheus_client import make_asgi_app

from core.config import get_settings
from core.database import init_db, check_db_connection
from core.logging import logger
from services.etl_service import ETLService
from api.routes import router

settings = get_settings()


# Scheduler for periodic ETL runs
scheduler = BackgroundScheduler()
etl_service = ETLService()


def run_scheduled_etl():
    """Run ETL for all sources (called by scheduler)."""
    logger.info("Starting scheduled ETL run")
    try:
        results = etl_service.run_all_sources(parallel=True)
        logger.info(f"Scheduled ETL completed", extra={"results": results})
    except Exception as e:
        logger.error(f"Scheduled ETL failed: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting application...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
    
    # Run initial ETL if enabled
    if settings.enable_etl_on_startup:
        logger.info("Running initial ETL...")
        try:
            results = etl_service.run_all_sources(parallel=True)
            logger.info(f"Initial ETL completed", extra={"results": results})
        except Exception as e:
            logger.error(f"Initial ETL failed: {e}", exc_info=True)
    
    # Start scheduler for periodic ETL
    scheduler.add_job(
        run_scheduled_etl,
        'interval',
        minutes=settings.etl_schedule_minutes,
        id='etl_job',
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Scheduler started (interval: {settings.etl_schedule_minutes} minutes)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title="Cryptocurrency ETL & Backend System",
    description="Production-grade backend for cryptocurrency data ingestion and APIs",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(router)

# Mount Prometheus metrics if enabled
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.middleware("http")
async def add_request_metadata(request, call_next):
    """Add request metadata and timing."""
    request.state.request_id = str(uuid.uuid4())
    request.state.start_time = time.time()
    
    response = await call_next(request)
    
    # Add headers
    response.headers["X-Request-ID"] = request.state.request_id
    
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Cryptocurrency ETL & Backend System",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
