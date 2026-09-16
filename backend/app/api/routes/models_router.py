"""SatQuery AI - Models Registry Route"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.models.adapters.base import model_registry, detect_device
from app.agents.tool_registry import tool_registry
from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/models")
async def list_models():
    """List all registered models and their status."""
    # Ensure RS-adapted models are registered
    from app.models.adapters.rs_adapters import (
        get_bigearthnet_adapter,
        get_cdvqa_adapter,
        get_vrsbench_adapter,
        get_rsvqa_adapter,
    )
    from app.models.adapters.change_detection import get_change_detection_adapter
    from app.models.adapters.optical_sar import get_optical_sar_adapter
    from app.models.adapters.segmentation import get_segmentation_adapter

    dev = settings.device
    get_bigearthnet_adapter(dev)
    get_cdvqa_adapter(dev)
    get_vrsbench_adapter(dev)
    get_rsvqa_adapter(dev)
    get_change_detection_adapter(dev)
    get_optical_sar_adapter(dev)
    get_segmentation_adapter(dev)

    device_info = model_registry.device_info()
    detected_device = detect_device(settings.device)
    return JSONResponse(content={
        "device": detected_device,
        "device_info": device_info,
        "models": model_registry.list_all(),
    })


@router.get("/tools")
async def list_tools():
    """List all registered analysis tools."""
    return JSONResponse(content={"tools": tool_registry.list_all()})
