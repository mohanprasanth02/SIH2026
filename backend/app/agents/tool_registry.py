"""
SatQuery AI - Tool Registry
Defines all 21 analysis tools with metadata.
Each tool has a name, description, input requirements, output schema.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ToolSpec:
    """Specification for a registered analysis tool."""
    name: str
    display_name: str
    description: str
    task: str
    supported_formats: List[str]
    supported_modalities: List[str]
    required_bands: Optional[List[str]]   # None = any
    requires_second_image: bool = False
    requires_geospatial: bool = False
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    output_keys: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    status: str = "available"             # available | unavailable | beta


class ToolRegistry:
    """
    Registry of all available analysis tools.
    Tools are invoked by the AgentController based on Gemini task routing.
    """

    _tools: Dict[str, ToolSpec] = {}

    def __init__(self):
        self._register_all()

    def _register_all(self) -> None:
        """Register specialist tools."""
        tools = [
            ToolSpec(
                name="input_validator",
                display_name="Input Validation & Geo-Compatibility",
                description="Checks format, modality, CRS, bounding box overlap (IoU), and structural scene compatibility.",
                task="validation",
                supported_formats=["geotiff", "tiff", "png", "jpeg", "jp2"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name="input_validator",
                output_keys=["is_valid", "error_message", "warnings"],
                status="available",
            ),
            ToolSpec(
                name="bigearthnet_adapter",
                display_name="BigEarthNet-19 RS Classifier",
                description="Domain-adapted on Sentinel-2 multispectral data using the BigEarthNet-19 class taxonomy.",
                task="land_cover_segmentation",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="bigearthnet_adapter",
                model_version="v2.1-rs-adapted",
                output_keys=["mask", "class_counts", "class_info", "confidence"],
                status="available",
            ),
            ToolSpec(
                name="cdvqa_adapter",
                display_name="CDVQA Bi-Temporal Change-VQA",
                description="Change-based Visual Question Answering evaluated on CDVQA and LEVIR-CD benchmarks.",
                task="change_vqa",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral", "sar"],
                required_bands=None,
                requires_second_image=True,
                model_name="cdvqa_adapter",
                model_version="v1.4-cdvqa-eval",
                output_keys=["answer", "primary_transition", "primary_location", "locations", "change_percentage"],
                status="available",
            ),
            ToolSpec(
                name="vrsbench_grounding",
                display_name="VRSBench Region Grounding",
                description="Remote-sensing visual region grounding evaluated on the VRSBench benchmark. Predicts spatial bounding boxes and reticles.",
                task="grounding",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="vrsbench_grounding",
                model_version="v2.0-vrsbench",
                output_keys=["bounding_boxes", "centroids", "grounding_evidence", "target_percentage"],
                status="available",
            ),
            ToolSpec(
                name="rsvqa_adapter",
                display_name="RSVQA Remote-Sensing VQA",
                description="Domain-adapted visual question answering conditioned on RSVQA (High & Low Resolution) remote sensing benchmarks.",
                task="vqa",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="rsvqa_adapter",
                model_version="v2.0-rsvqa-hr",
                output_keys=["question", "answer", "confidence"],
                status="available",
            ),
            ToolSpec(
                name="image_metadata",
                display_name="Image Metadata Extraction",
                description="Extract CRS, resolution, bands, transform, and acquisition info from image.",
                task="metadata",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name=None,
                output_keys=["crs", "resolution", "bands", "bounds", "acquisition_date"],
                status="available",
            ),
            ToolSpec(
                name="image_preprocessing",
                display_name="Image Preprocessing",
                description="Normalize, tile, and prepare images for model inference.",
                task="preprocessing",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name=None,
                output_keys=["normalized_array", "tiles"],
                status="available",
            ),
            ToolSpec(
                name="land_cover_segmentation",
                display_name="Land Cover Segmentation",
                description="Pixel-level land cover classification using SegFormer.",
                task="land_cover_segmentation",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                model_version="b4-ade-512-rs-adapted",
                output_keys=["mask", "class_counts", "class_info"],
                limitations=["Optimised for optical imagery.", "SAR not supported directly."],
                status="available",
            ),
            ToolSpec(
                name="water_analysis",
                display_name="Water Analysis",
                description="Detect and quantify water bodies using spectral indices (NDWI) or segmentation.",
                task="water",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                output_keys=["water_mask", "water_pixel_count", "water_percentage", "ndwi"],
                limitations=["NDWI requires NIR and Green bands.", "Turbid water may be missed."],
                status="available",
            ),
            ToolSpec(
                name="vegetation_analysis",
                display_name="Vegetation Analysis",
                description="Detect vegetation using NDVI (if NIR available) or segmentation.",
                task="vegetation",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                output_keys=["vegetation_mask", "ndvi", "vegetation_percentage"],
                limitations=["NDVI requires NIR band.", "Dense cloud cover reduces accuracy."],
                status="available",
            ),
            ToolSpec(
                name="agriculture_analysis",
                display_name="Agriculture Analysis",
                description="Identify and quantify agricultural land cover.",
                task="agriculture",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                output_keys=["agriculture_mask", "agriculture_percentage"],
                limitations=["Crop type classification not supported with current model."],
                status="available",
            ),
            ToolSpec(
                name="built_up_analysis",
                display_name="Built-up Area Analysis",
                description="Detect urban and built-up areas using NDBI or segmentation.",
                task="built_up",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                output_keys=["built_up_mask", "built_up_percentage", "ndbi"],
                limitations=["NDBI requires SWIR1 and NIR bands."],
                status="available",
            ),
            ToolSpec(
                name="road_detection",
                display_name="Road/Transport Detection",
                description="Detect roads and transportation infrastructure.",
                task="roads",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="segformer_land_cover",
                output_keys=["road_mask", "road_percentage"],
                limitations=["Fine road detection requires <5m resolution.", "High-res only."],
                status="available",
            ),
            ToolSpec(
                name="object_detection",
                display_name="Object Detection",
                description="Detect specific objects (buildings, vehicles, bridges).",
                task="object_detection",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical"],
                required_bands=None,
                model_name=None,
                output_keys=["objects", "bounding_boxes", "counts"],
                limitations=["Requires sub-meter resolution for vehicle detection."],
                status="beta",
            ),
            ToolSpec(
                name="vqa",
                display_name="Visual Question Answering",
                description="Answer natural-language questions about the image using Gemini Vision.",
                task="vqa",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name="gemini_vqa",
                model_version="gemini-1.5-pro",
                output_keys=["question", "answer"],
                status="available",
            ),
            ToolSpec(
                name="captioning",
                display_name="Image Captioning",
                description="Generate a descriptive caption for the satellite scene.",
                task="captioning",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="blip2_captioning",
                model_version="blip2-opt-2.7b",
                output_keys=["caption"],
                status="available",
            ),
            ToolSpec(
                name="grounding",
                display_name="Text-Guided Grounding",
                description="Locate specific features using text prompts (e.g. 'river', 'buildings').",
                task="grounding",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                model_name="grounding_dino",
                output_keys=["boxes", "masks", "labels", "scores"],
                status="beta",
            ),
            ToolSpec(
                name="image_registration",
                display_name="Image Registration",
                description="Co-register two images to the same spatial reference.",
                task="registration",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                requires_second_image=True,
                model_name=None,
                output_keys=["registered_a", "registered_b", "registration_error"],
                status="available",
            ),
            ToolSpec(
                name="change_detection",
                display_name="Change Detection",
                description="Detect and classify changes between two co-registered images.",
                task="change_detection",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                requires_second_image=True,
                model_name="change_detection",
                output_keys=["change_mask", "binary_change", "change_percentage"],
                status="available",
            ),
            ToolSpec(
                name="change_statistics",
                display_name="Change Statistics",
                description="Compute per-class change statistics for bi-temporal analysis.",
                task="change_statistics",
                supported_formats=["geotiff", "tiff"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                requires_second_image=True,
                requires_geospatial=True,
                model_name=None,
                output_keys=["class_changes", "total_change_area", "change_by_class"],
                status="available",
            ),
            ToolSpec(
                name="change_vqa",
                display_name="Change VQA",
                description="Answer questions about changes between two images.",
                task="change_vqa",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "multispectral"],
                required_bands=None,
                requires_second_image=True,
                model_name="gemini_vqa",
                output_keys=["question", "answer"],
                status="available",
            ),
            ToolSpec(
                name="optical_sar_analysis",
                display_name="Optical + SAR Joint Analysis",
                description="Fuse optical and SAR imagery for joint land cover analysis.",
                task="optical_sar",
                supported_formats=["geotiff", "tiff"],
                supported_modalities=["optical", "sar"],
                required_bands=None,
                requires_second_image=True,
                model_name="optical_sar_fusion",
                output_keys=["fused_mask", "optical_analysis", "sar_analysis"],
                limitations=["Requires co-registered optical+SAR pair."],
                status="available",
            ),
            ToolSpec(
                name="gis_area_calculation",
                display_name="GIS Area Calculation",
                description="Calculate pixel area in m², ha, km² using CRS and transform.",
                task="area_calculation",
                supported_formats=["geotiff", "tiff"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                requires_geospatial=True,
                model_name=None,
                output_keys=["area_m2", "area_ha", "area_km2", "pixel_area_m2"],
                limitations=["Unavailable for non-georeferenced images."],
                status="available",
            ),
            ToolSpec(
                name="spatial_statistics",
                display_name="Spatial Statistics",
                description="Compute per-class pixel counts, percentages, and area statistics.",
                task="spatial_statistics",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name=None,
                output_keys=["class_statistics", "total_area", "class_areas"],
                status="available",
            ),
            ToolSpec(
                name="map_generation",
                display_name="Classification Map Generation",
                description="Generate PNG classification maps, overlays, and change maps.",
                task="map_generation",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name=None,
                output_keys=["classification_map", "overlay", "change_map"],
                status="available",
            ),
            ToolSpec(
                name="report_generation",
                display_name="Report Generation",
                description="Generate comprehensive PDF analysis report.",
                task="report_generation",
                supported_formats=["geotiff", "tiff", "png", "jpeg"],
                supported_modalities=["optical", "sar", "multispectral"],
                required_bands=None,
                model_name=None,
                output_keys=["pdf_path"],
                status="available",
            ),
        ]

        for tool in tools:
            self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolSpec]:
        return self._tools.get(name)

    def get_or_raise(self, name: str) -> ToolSpec:
        tool = self.get(name)
        if tool is None:
            raise ValueError(
                f"Tool '{name}' not found. Available: {list(self._tools.keys())}"
            )
        return tool

    def list_all(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "display_name": t.display_name,
                "description": t.description,
                "task": t.task,
                "status": t.status,
                "model_name": t.model_name,
                "model_version": t.model_version,
                "requires_second_image": t.requires_second_image,
                "requires_geospatial": t.requires_geospatial,
                "limitations": t.limitations,
            }
            for t in self._tools.values()
        ]

    def tools_for_task(self, task: str) -> List[ToolSpec]:
        return [t for t in self._tools.values() if t.task == task]


# Global tool registry
tool_registry = ToolRegistry()
