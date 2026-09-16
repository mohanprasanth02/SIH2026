"""
SatQuery AI - FastAPI Main Application
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.database.session import init_db

settings = get_settings()

# ── Configure logging ─────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("satquery")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    logger.info("SatQuery AI starting up...")

    # Create data directories
    for dir_path in [
        settings.upload_dir,
        settings.processed_dir,
        settings.results_dir,
        settings.model_cache_dir,
    ]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Initialize database (creates tables)
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't crash; run without DB if needed

    # Set HuggingFace cache directory
    if settings.hf_home:
        os.environ["HF_HOME"] = settings.hf_home
        os.environ["TRANSFORMERS_CACHE"] = settings.hf_home

    logger.info(f"Device: {settings.device}")
    logger.info("SatQuery AI ready.")

    yield

    logger.info("SatQuery AI shutting down.")


# ── FastAPI App ───────────────────────────────────────────────────
app = FastAPI(
    title="SatQuery AI",
    description="Agentic Remote-Sensing Vision-Language Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────
from app.api.routes import upload, analyze, jobs, results, reports, models_router, auth, dashboard, satellite_aoi

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(satellite_aoi.router, prefix="/api/v1", tags=["Satellite AOI"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(results.router, prefix="/api/v1", tags=["Results"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(models_router.router, prefix="/api/v1", tags=["Models"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

# ── Static files (serve result images) ───────────────────────────
results_path = Path(settings.results_dir)
results_path.mkdir(parents=True, exist_ok=True)
app.mount("/results", StaticFiles(directory=str(results_path)), name="results")

uploads_path = Path(settings.upload_dir)
uploads_path.mkdir(parents=True, exist_ok=True)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    from app.models.adapters.base import model_registry, detect_device

    device = detect_device(settings.device)
    return {
        "status": "ok",
        "version": "1.0.0",
        "device": device,
        "models_loaded": sum(1 for a in model_registry._adapters.values() if a.is_loaded),
        "models_registered": len(model_registry._adapters),
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )
