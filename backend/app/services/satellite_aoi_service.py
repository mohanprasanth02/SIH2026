"""
SatQuery AI - Satellite AOI Service
Fetches real satellite imagery tiles for any user-selected bounding box (AOI),
stitches them into a georeferenced GeoTIFF with real CRS (EPSG:3857) and affine transform.
"""
import math
import os
import uuid
import asyncio
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

import httpx
import numpy as np
from PIL import Image as PILImage
import rasterio
from rasterio.transform import from_bounds

from app.config.settings import get_settings
from app.services.metadata_service import MetadataService, ImageMetadata
from app.services.evidence_service import EvidenceService

logger = logging.getLogger(__name__)
settings = get_settings()

metadata_service = MetadataService()
evidence_service = EvidenceService()

# High-resolution satellite basemap tile servers
# Esri World Imagery provides high-resolution worldwide satellite imagery
SATELLITE_TILE_URLS = {
    "satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "osm": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
}

# Curated global satellite presets for analysts
SATELLITE_PRESETS = [
    {
        "id": "delhi_urban",
        "name": "Delhi Urban Conurbation, India",
        "category": "Urban & Built-Up",
        "description": "High-density built-up structures and Yamuna river corridor.",
        "bbox": [77.18, 28.58, 77.26, 28.64],
        "zoom": 14,
        "tags": ["urban", "built_up", "river", "transport"],
    },
    {
        "id": "kansas_agriculture",
        "name": "Finney County Center-Pivot Agriculture, USA",
        "category": "Agriculture",
        "description": "Geometric circular crop fields and irrigation patterns.",
        "bbox": [-100.95, 37.95, -100.85, 38.02],
        "zoom": 13,
        "tags": ["agriculture", "crops", "irrigation"],
    },
    {
        "id": "sundarbans_mangrove",
        "name": "Sundarbans Mangrove Delta, India/Bangladesh",
        "category": "Water & Wetlands",
        "description": "Dense tidal mangrove networks and complex water channels.",
        "bbox": [88.85, 21.80, 88.98, 21.90],
        "zoom": 13,
        "tags": ["water", "vegetation", "wetlands", "mangroves"],
    },
    {
        "id": "dubai_coast",
        "name": "Palm Jumeirah & Coastline, Dubai",
        "category": "Coastal & Infrastructure",
        "description": "Artificial coastal archipelago, marine environment, and urban grid.",
        "bbox": [55.10, 25.10, 55.18, 25.16],
        "zoom": 14,
        "tags": ["coastal", "water", "built_up"],
    },
    {
        "id": "amazon_deforestation",
        "name": "Rondônia Forest Frontier, Brazil",
        "category": "Forest & Change",
        "description": "Fishbone deforestation patterns cutting through primary rainforest.",
        "bbox": [-63.15, -10.25, -63.02, -10.15],
        "zoom": 13,
        "tags": ["forest", "vegetation", "deforestation"],
    },
    {
        "id": "nile_delta",
        "name": "Nile River & Valley, Cairo, Egypt",
        "category": "Agriculture & Water",
        "description": "Sharp boundary between lush irrigated agricultural land and desert.",
        "bbox": [31.18, 30.00, 31.30, 30.10],
        "zoom": 13,
        "tags": ["agriculture", "river", "water", "arid"],
    },
]


class SatelliteAoiService:
    """Service to capture and georeference live satellite imagery over an AOI."""

    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
        """Convert latitude/longitude in degrees to Web Mercator XYZ tile coordinates."""
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    @staticmethod
    def num2deg(xtile: int, ytile: int, zoom: int) -> Tuple[float, float]:
        """Convert tile coordinate to NW corner latitude and longitude in degrees."""
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    @staticmethod
    def lonlat_to_mercator(lon: float, lat: float) -> Tuple[float, float]:
        """Convert WGS84 Lon/Lat to EPSG:3857 Spherical Mercator meters."""
        r = 6378137.0
        x = r * math.radians(lon)
        scale = math.sin(math.radians(lat))
        y = (r / 2.0) * math.log((1.0 + scale) / (1.0 - scale))
        return x, y

    async def fetch_tile(
        self, client: httpx.AsyncClient, url_template: str, z: int, x: int, y: int
    ) -> Optional[bytes]:
        """Fetch a single satellite tile with retry."""
        url = url_template.format(z=z, x=x, y=y)
        for attempt in range(3):
            try:
                resp = await client.get(
                    url,
                    headers={"User-Agent": "SatQueryAI/1.0 (Earth Observation Intelligence)"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    return resp.content
            except Exception as e:
                logger.debug(f"Tile {z}/{x}/{y} attempt {attempt} failed: {e}")
                await asyncio.sleep(0.3 * (attempt + 1))
        return None

    async def capture_aoi(
        self,
        west: float,
        south: float,
        east: float,
        north: float,
        zoom: Optional[int] = None,
        source: str = "satellite",
        name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Capture an Area of Interest (AOI), stitch tiles, and create a georeferenced GeoTIFF.

        Args:
            west: Minimum longitude (degrees)
            south: Minimum latitude (degrees)
            east: Maximum longitude (degrees)
            north: Maximum latitude (degrees)
            zoom: Web Mercator zoom level (auto-calculated if None, typically 12-16)
            source: 'satellite' (Esri World Imagery) or 'osm'
            name: Optional descriptive label

        Returns:
            Dict matching UploadResult schema
        """
        # Validate coordinates
        west = max(-180.0, min(180.0, west))
        east = max(-180.0, min(180.0, east))
        south = max(-85.0511, min(85.0511, south))
        north = max(-85.0511, min(85.0511, north))
        if west >= east or south >= north:
            raise ValueError(f"Invalid bounding box: [{west}, {south}, {east}, {north}]")

        # High-resolution auto-zoom calibrated for rich 2048px+ output
        lon_span = abs(east - west)
        lat_span = abs(north - south)
        max_span = max(lon_span, lat_span)

        if zoom is None:
            # Calibrate zoom level to ensure output image is crisp (targeting 2048px across)
            if max_span > 2.0:
                zoom = 12
            elif max_span > 0.8:
                zoom = 13
            elif max_span > 0.3:
                zoom = 14
            elif max_span > 0.1:
                zoom = 15
            elif max_span > 0.04:
                zoom = 16
            elif max_span > 0.015:
                zoom = 17
            else:
                zoom = 18
        else:
            # Respect user zoom when zoomed in, supporting sub-meter clarity (zoom 18-19)
            zoom = max(11, min(19, zoom))

        # Get tile coordinates
        x_min, y_min = self.deg2num(north, west, zoom)
        x_max, y_max = self.deg2num(south, east, zoom)

        # Ensure order
        if x_min > x_max:
            x_min, x_max = x_max, x_min
        if y_min > y_max:
            y_min, y_max = y_max, y_min

        tile_cols = x_max - x_min + 1
        tile_rows = y_max - y_min + 1

        # Allow up to 160 tiles (e.g. 16x10 or 12x12 = ~3072x3072 native pixels)
        # to prevent artificial down-zooming when inspecting zoomed-in farmland or towns
        while tile_cols * tile_rows > 160 and zoom > 10:
            zoom -= 1
            x_min, y_min = self.deg2num(north, west, zoom)
            x_max, y_max = self.deg2num(south, east, zoom)
            if x_min > x_max:
                x_min, x_max = x_max, x_min
            if y_min > y_max:
                y_min, y_max = y_max, y_min
            tile_cols = x_max - x_min + 1
            tile_rows = y_max - y_min + 1

        logger.info(
            f"Capturing Ultra High-Res AOI [{west:.4f}, {south:.4f}, {east:.4f}, {north:.4f}] "
            f"at zoom {zoom}: {tile_cols}x{tile_rows} tiles ({tile_cols*tile_rows} total, ~{tile_cols*256}x{tile_rows*256}px)"
        )

        tile_url = SATELLITE_TILE_URLS.get(source, SATELLITE_TILE_URLS["satellite"])

        # Fetch tiles concurrently with generous connection pool
        tile_tasks = []
        tile_coords = []
        limits = httpx.Limits(max_keepalive_connections=30, max_connections=60)
        async with httpx.AsyncClient(limits=limits) as client:
            for y in range(y_min, y_max + 1):
                for x in range(x_min, x_max + 1):
                    tile_coords.append((x, y))
                    tile_tasks.append(self.fetch_tile(client, tile_url, zoom, x, y))

            tile_bytes_list = await asyncio.gather(*tile_tasks)

        # Assemble full mosaic image
        tile_w, tile_h = 256, 256
        mosaic_w = tile_cols * tile_w
        mosaic_h = tile_rows * tile_h

        mosaic = PILImage.new("RGB", (mosaic_w, mosaic_h), color=(30, 30, 30))

        import io
        for (x, y), tile_bytes in zip(tile_coords, tile_bytes_list):
            if tile_bytes:
                try:
                    img = PILImage.open(io.BytesIO(tile_bytes)).convert("RGB")
                    px = (x - x_min) * tile_w
                    py = (y - y_min) * tile_h
                    mosaic.paste(img, (px, py))
                except Exception as e:
                    logger.warning(f"Failed to paste tile {x},{y}: {e}")

        # Compute accurate geographical bounds of the tiled area
        nw_lat, nw_lon = self.num2deg(x_min, y_min, zoom)
        se_lat, se_lon = self.num2deg(x_max + 1, y_max + 1, zoom)

        # Convert bounding boxes to Spherical Mercator EPSG:3857 meters
        tile_x_min_m, tile_y_max_m = self.lonlat_to_mercator(nw_lon, nw_lat)
        tile_x_max_m, tile_y_min_m = self.lonlat_to_mercator(se_lon, se_lat)

        aoi_x_min_m, aoi_y_min_m = self.lonlat_to_mercator(west, south)
        aoi_x_max_m, aoi_y_max_m = self.lonlat_to_mercator(east, north)

        # Crop mosaic to the exact requested AOI
        span_x_m = tile_x_max_m - tile_x_min_m
        span_y_m = tile_y_max_m - tile_y_min_m

        if span_x_m > 0 and span_y_m > 0:
            left_px = max(0, int((aoi_x_min_m - tile_x_min_m) / span_x_m * mosaic_w))
            right_px = min(mosaic_w, int((aoi_x_max_m - tile_x_min_m) / span_x_m * mosaic_w))
            top_px = max(0, int((tile_y_max_m - aoi_y_max_m) / span_y_m * mosaic_h))
            bottom_px = min(mosaic_h, int((tile_y_max_m - aoi_y_min_m) / span_y_m * mosaic_h))

            # Ensure valid crop rectangle
            if right_px > left_px + 32 and bottom_px > top_px + 32:
                cropped = mosaic.crop((left_px, top_px, right_px, bottom_px))
            else:
                cropped = mosaic
                aoi_x_min_m, aoi_y_min_m = tile_x_min_m, tile_y_min_m
                aoi_x_max_m, aoi_y_max_m = tile_x_max_m, tile_y_max_m
        else:
            cropped = mosaic

        # Scientific image detail preservation: subtle unsharp mask sharpening & contrast balancing
        try:
            from PIL import ImageFilter, ImageEnhance
            # Sharpen subtle features like roads, water boundaries, building outlines
            cropped = cropped.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=2))
            enhancer = ImageEnhance.Contrast(cropped)
            cropped = enhancer.enhance(1.04)
        except Exception as filter_err:
            logger.debug(f"Detail filter skipped: {filter_err}")

        # Output dimensions
        width, height = cropped.size

        # Convert to numpy array [3, H, W] for rasterio
        arr = np.array(cropped)  # [H, W, 3]
        arr_chfirst = np.transpose(arr, (2, 0, 1))  # [3, H, W]

        # Calculate exact affine transform in EPSG:3857
        transform = from_bounds(
            aoi_x_min_m, aoi_y_min_m, aoi_x_max_m, aoi_y_max_m, width, height
        )

        # Save as GeoTIFF
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.tif"
        output_path = self.upload_dir / filename

        with rasterio.open(
            str(output_path),
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=3,
            dtype=rasterio.uint8,
            crs="EPSG:3857",
            transform=transform,
        ) as dst:
            dst.write(arr_chfirst)
            dst.set_band_description(1, "Red")
            dst.set_band_description(2, "Green")
            dst.set_band_description(3, "Blue")

        logger.info(f"GeoTIFF generated: {output_path} ({width}x{height}, EPSG:3857)")

        # Extract metadata
        meta = metadata_service.extract(str(output_path))
        meta.modality = "optical"
        meta.sensor = "Satellite Basemap (High Resolution)"

        # Generate preview thumbnail
        thumb_path = evidence_service.generate_thumbnail(str(output_path))

        display_name = name or f"Satellite AOI [{west:.2f}, {south:.2f}]"

        return {
            "image_id": image_id,
            "stored_filename": filename,
            "stored_path": str(output_path),
            "original_filename": f"{display_name}.tif",
            "detected_mime": "image/tiff",
            "thumbnail_url": f"/results/{Path(thumb_path).name}" if thumb_path else None,
            "metadata": meta.to_dict(),
        }

    def list_presets(self) -> List[Dict[str, Any]]:
        """Return curated remote sensing presets."""
        return SATELLITE_PRESETS

    async def geocode(self, query: str) -> List[Dict[str, Any]]:
        """
        Global geocoding: coordinates parsing, Photon/OSM search, and fallback to presets.
        Searches any place in the world without arbitrary limitations.
        """
        import re
        q = query.strip()
        if not q:
            return []

        # 1. Try parsing direct Lat/Lng coordinates
        cleaned = q.replace("°", "").replace("N", "").replace("S", "").replace("E", "").replace("W", "").strip()
        if "," in cleaned or " " in cleaned:
            parts = [p.strip() for p in re.split(r"[,\s]+", cleaned) if p.strip()]
            if len(parts) == 2:
                try:
                    lat, lng = float(parts[0]), float(parts[1])
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        return [{
                            "name": f"Coordinates: {lat:.4f}°N, {lng:.4f}°E",
                            "lat": lat,
                            "lng": lng,
                            "bbox": [lng - 0.04, lat - 0.04, lng + 0.04, lat + 0.04],
                            "type": "coordinate"
                        }]
                except ValueError:
                    pass

        results = []

        # 2. Query Photon by Komoot (ultra-fast OSM-based global search, no rate limits)
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(
                    "https://photon.komoot.io/api/",
                    params={"q": q, "limit": 7}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for feat in data.get("features", []):
                        props = feat.get("properties", {})
                        coords = feat.get("geometry", {}).get("coordinates", [])
                        if len(coords) >= 2:
                            lng, lat = coords[0], coords[1]
                            name_parts = []
                            if props.get("name"): name_parts.append(props["name"])
                            if props.get("city") and props["city"] != props.get("name"): name_parts.append(props["city"])
                            if props.get("state") and props["state"] != props.get("name"): name_parts.append(props["state"])
                            if props.get("country"): name_parts.append(props["country"])
                            
                            display = ", ".join(name_parts) if name_parts else props.get("name", q)
                            extent = props.get("extent")
                            bbox = [extent[0], extent[3], extent[2], extent[1]] if (extent and len(extent) == 4) else [lng - 0.04, lat - 0.04, lng + 0.04, lat + 0.04]
                            
                            results.append({
                                "name": display,
                                "lat": lat,
                                "lng": lng,
                                "bbox": bbox,
                                "type": props.get("osm_value", "place")
                            })
        except Exception as e:
            logger.warning(f"Photon geocoding failed: {e}")

        # 3. If photon returned results, return them
        if results:
            return results

        # 4. Fallback: OSM Nominatim
        try:
            headers = {"User-Agent": "SatQuery-Earth-Intelligence/2.0 (sih2026@satquery.ai)"}
            async with httpx.AsyncClient(timeout=4.0, headers=headers) as client:
                resp = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"format": "json", "q": q, "limit": 7}
                )
                if resp.status_code == 200:
                    for item in resp.json():
                        lat = float(item["lat"])
                        lng = float(item["lon"])
                        bb = item.get("boundingbox", [])
                        bbox = [float(bb[2]), float(bb[0]), float(bb[3]), float(bb[1])] if len(bb) == 4 else [lng - 0.04, lat - 0.04, lng + 0.04, lat + 0.04]
                        name_parts = [p.strip() for p in item.get("display_name", "").split(",")[:3]]
                        results.append({
                            "name": ", ".join(name_parts),
                            "lat": lat,
                            "lng": lng,
                            "bbox": bbox,
                            "type": item.get("type", "place")
                        })
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed: {e}")

        # 5. Local fallback against presets
        if not results:
            for p in SATELLITE_PRESETS:
                if q.lower() in p["name"].lower() or q.lower() in p["id"].lower():
                    west, south, east, north = p["bbox"]
                    results.append({
                        "name": p["name"],
                        "lat": (south + north) / 2,
                        "lng": (west + east) / 2,
                        "bbox": p["bbox"],
                        "type": "preset"
                    })

        return results


satellite_aoi_service = SatelliteAoiService()
