"""
SatQuery AI - Satellite AOI Route
Endpoints for capturing live satellite map regions (AOIs) as real GeoTIFFs.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.satellite_aoi_service import satellite_aoi_service

logger = logging.getLogger(__name__)
router = APIRouter()


class AoiCaptureRequest(BaseModel):
    bbox: List[float] = Field(
        ...,
        description="Bounding box coordinates in WGS84: [west, south, east, north]",
        min_items=4,
        max_items=4,
    )
    zoom: Optional[int] = Field(
        None, description="Zoom level (10-17). Auto-calculated if omitted.", ge=10, le=17
    )
    source: Optional[str] = Field("satellite", description="Tile source: 'satellite' or 'osm'")
    name: Optional[str] = Field(None, description="Descriptive label for this AOI")


@router.post("/satellite/aoi")
async def capture_aoi(req: AoiCaptureRequest):
    """
    Capture live satellite imagery for an Area of Interest (AOI).
    Downloads actual satellite tiles, composites them, embeds EPSG:3857 GeoTIFF tags,
    and returns an UploadResult ready for all SatQuery AI analysis tools.
    """
    try:
        west, south, east, north = req.bbox
        result = await satellite_aoi_service.capture_aoi(
            west=west,
            south=south,
            east=east,
            north=north,
            zoom=req.zoom,
            source=req.source or "satellite",
            name=req.name,
        )
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to capture satellite AOI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to capture satellite AOI: {str(e)}")


@router.get("/satellite/presets")
async def get_satellite_presets():
    """Return curated global remote-sensing presets with interesting land cover features."""
    presets = satellite_aoi_service.list_presets()
    return JSONResponse(content={"presets": presets})


@router.get("/satellite/geocode")
async def geocode_place(q: str):
    """
    Geocode any place, city, region, landmark, or coordinates globally.
    Queries Komoot Photon + OSM Nominatim + coordinate parsing.
    """
    if not q or len(q.strip()) < 2:
        return JSONResponse(content={"results": []})
    try:
        results = await satellite_aoi_service.geocode(q.strip())
        return JSONResponse(content={"results": results})
    except Exception as e:
        logger.error(f"Geocoding error: {e}", exc_info=True)
        return JSONResponse(content={"results": []})

