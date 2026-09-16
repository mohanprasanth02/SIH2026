"""SatQuery AI - Job Status Routes"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from app.workers.job_manager import job_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get full job state including result."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    return JSONResponse(content={
        "job_id": job.job_id,
        "status": job.status,
        "stage": job.stage,
        "progress": job.progress,
        "error": job.error,
        "result": job.result,
        "execution_steps": job.steps,
        "created_at": job.created_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    })


@router.get("/jobs/{job_id}/status")
async def stream_job_status(job_id: str):
    """
    SSE stream for real-time job status updates.
    Connect with EventSource in the frontend.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    return StreamingResponse(
        job_manager.subscribe(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending or running job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
    cancelled = job_manager.cancel_job(job_id)
    return JSONResponse(content={
        "job_id": job_id,
        "cancelled": cancelled,
        "status": "cancelled" if cancelled else job.status,
    })


@router.get("/jobs")
async def list_jobs():
    """List all analysis jobs ordered by creation time descending."""
    jobs = sorted(
        job_manager._jobs.values(),
        key=lambda j: j.created_at,
        reverse=True
    )
    job_list = []
    for j in jobs:
        result = j.result or {}
        job_list.append({
            "job_id": j.job_id,
            "status": j.status,
            "stage": j.stage,
            "progress": j.progress,
            "error": j.error,
            "task": result.get("task"),
            "query": result.get("query"),
            "confidence": result.get("confidence"),
            "created_at": j.created_at.isoformat(),
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        })
    return JSONResponse(content={"jobs": job_list})

