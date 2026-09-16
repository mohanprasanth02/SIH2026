"""SatQuery AI - API Route Packages"""
from app.api.routes import upload, analyze, jobs, results, reports, models_router, auth, dashboard, satellite_aoi

__all__ = ["upload", "analyze", "jobs", "results", "reports", "models_router", "auth", "dashboard", "satellite_aoi"]
