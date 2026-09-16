"""SatQuery AI - Results, Reports, Models, Auth, Dashboard routes"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.workers.job_manager import job_manager
from app.agents.tool_registry import tool_registry
from app.models.adapters.base import model_registry, detect_device
from app.config.settings import get_settings

settings = get_settings()

# ── Results ───────────────────────────────────────────────────────
router_results = APIRouter()

@router_results.get("/results/{job_id}")
async def get_result(job_id: str):
    from fastapi import HTTPException
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        return JSONResponse(content={"status": job.status, "result": None})
    return JSONResponse(content={"status": "completed", "result": job.result})

# Create the module-level router for import in main.py
router = router_results
