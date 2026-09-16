"""
SatQuery AI - Analysis Routes
All analysis endpoints trigger the AgentController pipeline.
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.workers.job_manager import job_manager
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class AnalyzeRequest(BaseModel):
    image_id: str = Field(..., description="Primary image ID (from /upload)")
    query: str = Field(..., description="Natural language query")
    image_b_id: Optional[str] = Field(None, description="Second image ID (change detection / SAR)")
    task: Optional[str] = Field(None, description="Force task type (overrides Gemini routing)")
    parameters: Optional[dict] = Field(default_factory=dict)


def _resolve_image_path(image_id: str) -> str:
    """Resolve image_id to stored filepath."""
    upload_dir = Path(settings.upload_dir)

    # 1. Exact file match
    exact = upload_dir / image_id
    if exact.is_file():
        return str(exact)

    # 2. Match image_id.*
    matches = list(upload_dir.glob(f"{image_id}.*"))
    if matches:
        return str(matches[0])

    # 3. Match containing image_id
    matches = list(upload_dir.glob(f"*{image_id}*"))
    if matches:
        return str(matches[0])

    # 4. Match short UUID (first 8 chars)
    if len(image_id) >= 8:
        short_id = image_id[:8]
        matches = list(upload_dir.glob(f"*{short_id}*"))
        if matches:
            return str(matches[0])

    raise HTTPException(status_code=404, detail=f"Image {image_id} not found.")


async def _run_analysis_job(job_id: str, req: AnalyzeRequest):
    """Background task: run full analysis pipeline and update job."""
    from app.agents.agent_controller import AgentController

    await job_manager.update_job(
        job_id, status="running", stage="Starting analysis", progress=5
    )

    # Progress callback
    async def on_step(step: dict):
        step_map = {
            "Extracting image metadata": 10,
            "Image metadata extracted": 15,
            "Classifying query with Gemini": 20,
            "Query classified": 25,
            "Loading and preprocessing images": 30,
            "Images loaded": 35,
            "Running land cover segmentation": 45,
            "Segmentation completed": 60,
            "Calculating spatial statistics": 65,
            "Statistics calculated": 70,
            "Generating classification map": 75,
            "Running VQA": 50,
            "VQA completed": 65,
            "Running image captioning": 50,
            "Captioning completed": 65,
            "Running change detection": 50,
            "Change detection completed": 65,
            "Running Optical-SAR fusion": 50,
            "Optical-SAR fusion completed": 65,
            "Generating AI explanation": 85,
            "AI explanation generated": 95,
        }
        progress = step_map.get(step.get("step_name", ""), None)
        await job_manager.update_job(
            job_id,
            stage=step.get("step_name", ""),
            progress=progress,
            step=step,
        )

    def sync_on_step(step: dict):
        """Sync wrapper for async callback."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(on_step(step))
        except Exception:
            pass

    try:
        image_path = _resolve_image_path(req.image_id)
        image_b_path = _resolve_image_path(req.image_b_id) if req.image_b_id else None

        controller = AgentController(on_progress=sync_on_step)
        result = await controller.run(
            image_path=image_path,
            query=req.query,
            image_b_path=image_b_path,
            task_override=req.task,
            parameters=req.parameters or {},
        )

        # Remove numpy arrays from result before storing
        safe_result = _make_json_safe(result)

        await job_manager.update_job(
            job_id,
            status="completed",
            stage="Analysis complete",
            progress=100,
            result=safe_result,
        )

    except HTTPException as e:
        await job_manager.update_job(
            job_id, status="failed", stage="Failed", error=str(e.detail)
        )
    except Exception as e:
        logger.error(f"Analysis job {job_id} failed: {e}", exc_info=True)
        await job_manager.update_job(
            job_id, status="failed", stage="Failed", error=str(e)
        )


def _make_json_safe(obj):
    """Recursively make object JSON-serializable."""
    try:
        import numpy as np
        if isinstance(obj, np.ndarray):
            return None  # Strip raw arrays
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
    except ImportError:
        pass
    if isinstance(obj, dict):
        return {k: _make_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_safe(i) for i in obj]
    return obj


# ── Generic Analysis Endpoint ─────────────────────────────────────

@router.post("/analyze")
async def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Generic analysis endpoint. Gemini agent selects the appropriate pipeline.
    Returns a job_id immediately; poll /jobs/{id} for status.
    """
    # Validate image exists
    _resolve_image_path(req.image_id)
    if req.image_b_id:
        _resolve_image_path(req.image_b_id)

    job_id = job_manager.create_job()
    background_tasks.add_task(_run_analysis_job, job_id, req)

    return JSONResponse(content={
        "job_id": job_id,
        "status": "pending",
        "message": "Analysis job started. Poll /api/v1/jobs/{job_id} for status.",
    })


# ── Specific Task Endpoints ───────────────────────────────────────

@router.post("/analyze/area")
async def analyze_area(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Full land cover analysis."""
    req.task = "land_cover"
    return await analyze(req, background_tasks)


@router.post("/analyze/land-cover")
async def analyze_land_cover(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "land_cover"
    return await analyze(req, background_tasks)


@router.post("/analyze/water")
async def analyze_water(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "water"
    return await analyze(req, background_tasks)


@router.post("/analyze/vegetation")
async def analyze_vegetation(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "vegetation"
    return await analyze(req, background_tasks)


@router.post("/analyze/agriculture")
async def analyze_agriculture(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "agriculture"
    return await analyze(req, background_tasks)


@router.post("/analyze/built-up")
async def analyze_built_up(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "built_up"
    return await analyze(req, background_tasks)


@router.post("/analyze/roads")
async def analyze_roads(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "roads"
    return await analyze(req, background_tasks)


@router.post("/analyze/vqa")
async def analyze_vqa(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "vqa"
    return await analyze(req, background_tasks)


@router.post("/analyze/caption")
async def analyze_caption(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "captioning"
    return await analyze(req, background_tasks)


@router.post("/analyze/grounding")
async def analyze_grounding(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    req.task = "grounding"
    return await analyze(req, background_tasks)


@router.post("/analyze/change")
async def analyze_change(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Change detection between two images."""
    if not req.image_b_id:
        raise HTTPException(
            status_code=400,
            detail="Change detection requires image_b_id (second image)."
        )
    req.task = "change_detection"
    return await analyze(req, background_tasks)


@router.post("/analyze/change-vqa")
async def analyze_change_vqa(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    if not req.image_b_id:
        raise HTTPException(status_code=400, detail="Change VQA requires image_b_id.")
    req.task = "change_vqa"
    return await analyze(req, background_tasks)


@router.post("/analyze/optical-sar")
async def analyze_optical_sar(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """Optical + SAR fusion analysis."""
    if not req.image_b_id:
        raise HTTPException(
            status_code=400,
            detail="Optical-SAR analysis requires image_b_id (SAR image)."
        )
    req.task = "optical_sar"
    return await analyze(req, background_tasks)
