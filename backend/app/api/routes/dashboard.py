"""SatQuery AI - Dashboard Route"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.workers.job_manager import job_manager
from app.models.adapters.base import model_registry, detect_device
from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """
    Return REAL dashboard statistics from job manager.
    Never fabricates values - shows 0 if no analyses have been run.
    """
    jobs = list(job_manager._jobs.values())
    total = len(jobs)
    completed = sum(1 for j in jobs if j.status == "completed")
    failed = sum(1 for j in jobs if j.status == "failed")
    running = sum(1 for j in jobs if j.status == "running")

    # Calculate average processing time from completed jobs
    completed_jobs = [j for j in jobs if j.status == "completed" and j.started_at and j.completed_at]
    if completed_jobs:
        avg_ms = sum(
            (j.completed_at - j.started_at).total_seconds() * 1000
            for j in completed_jobs
        ) / len(completed_jobs)
    else:
        avg_ms = None

    # Device info
    device = detect_device(settings.device)
    device_info = model_registry.device_info()

    # Count by task type
    task_counts = {}
    for j in jobs:
        result = j.result or {}
        task = result.get("task", "unknown")
        task_counts[task] = task_counts.get(task, 0) + 1

    return JSONResponse(content={
        "total_analyses": total,
        "completed_analyses": completed,
        "failed_analyses": failed,
        "running_analyses": running,
        "average_processing_time_ms": round(avg_ms) if avg_ms else None,
        "task_breakdown": task_counts,
        "device": device,
        "device_info": device_info,
        "models_loaded": sum(1 for a in model_registry._adapters.values() if a.is_loaded),
        "models_registered": len(model_registry._adapters),
    })


@router.get("/dashboard/recent")
async def get_recent_analyses():
    """Return recent analysis jobs (most recent first)."""
    jobs = sorted(
        job_manager._jobs.values(),
        key=lambda j: j.created_at,
        reverse=True
    )[:10]  # Last 10

    recent = []
    for j in jobs:
        result = j.result or {}
        recent.append({
            "job_id": j.job_id,
            "status": j.status,
            "stage": j.stage,
            "task": result.get("task"),
            "query": result.get("query"),
            "created_at": j.created_at.isoformat(),
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        })

    return JSONResponse(content={"recent_analyses": recent})
