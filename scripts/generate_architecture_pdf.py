"""
SatQuery AI - System Architecture & Technical Specification PDF Generator
Generates a comprehensive, publication-quality technical architecture document
covering all system layers, AI models, image processing pipelines, water detection,
building detection, change detection, GIS quantification, and execution flows.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that accurately computes the total page count
    and renders professional running headers and footers on every page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        page_w, page_h = letter
        margin = 36  # 0.5 inch

        # First page has specialized title banner; suppress running header on page 1
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#0B192C"))
            self.drawString(margin, page_h - 26, "SATQUERY AI")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(margin + 62, page_h - 26, "— System Architecture & Technical Specification  |  ISRO PS 26167")
            
            # Header rule
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(margin, page_h - 30, page_w - margin, page_h - 30)

        # Running Footer (all pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(margin, 32, page_w - margin, 32)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(margin, 20, "Smart India Hackathon 2026  •  Team SATQuery  •  ISRO / Department of Space")

        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(page_w - margin, 20, page_str)
        self.restoreState()


def build_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_primary = colors.HexColor("#0B192C")      # Deep Space Navy
    c_secondary = colors.HexColor("#1E3E62")    # Slate Navy
    c_accent = colors.HexColor("#FF6500")       # ISRO Saffron Orange
    c_teal = colors.HexColor("#0284C7")         # Geospatial Cyan/Teal
    c_dark = colors.HexColor("#0F172A")         # Charcoal Dark
    c_body = colors.HexColor("#334155")         # Text Slate
    c_muted = colors.HexColor("#64748B")        # Light Slate
    c_bg_light = colors.HexColor("#F8FAFC")     # Card background
    c_border = colors.HexColor("#E2E8F0")       # Border grey
    c_success = colors.HexColor("#15803D")      # Green

    # Typography Styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.white,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#E2E8F0"),
        spaceAfter=2,
    )
    meta_tag_style = ParagraphStyle(
        "DocMetaTag",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#FFD580"),
    )
    h1_style = ParagraphStyle(
        "Heading1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=c_primary,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=c_secondary,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "Heading3Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=c_teal,
        spaceBefore=5,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=11,
        textColor=c_body,
        spaceAfter=3.5,
    )
    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-6,
        spaceAfter=2,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.2,
        leading=9.8,
        textColor=c_dark,
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=c_primary,
    )
    table_cell_header = ParagraphStyle(
        "TableCellHeader",
        parent=table_cell,
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.8,
        textColor=colors.white,
    )
    callout_text = ParagraphStyle(
        "CalloutText",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.6,
        leading=10.5,
        textColor=c_dark,
    )

    elements = []

    # =========================================================================
    # COVER / HEADER HERO BANNER
    # =========================================================================
    hero_table_data = [
        [
            Paragraph("SMART INDIA HACKATHON 2026  •  ISRO / DEPARTMENT OF SPACE  •  PS 26167", meta_tag_style),
        ],
        [
            Paragraph("SATQUERY AI — SYSTEM ARCHITECTURE &amp; TECHNICAL SPECIFICATION", title_style),
        ],
        [
            Paragraph(
                "An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Natural Language Text Queries",
                subtitle_style
            ),
        ],
        [
            Paragraph(
                "<b>Document Release:</b> Enterprise Architecture v2.4  |  <b>Security:</b> Public / Academic Review  |  "
                "<b>Date:</b> September 2026  |  <b>Lead Team:</b> Team SATQuery",
                ParagraphStyle("DocHeroSub", parent=meta_tag_style, textColor=colors.HexColor("#CBD5E1"), fontSize=7.2)
            )
        ]
    ]

    hero_table = Table(hero_table_data, colWidths=[540])
    hero_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_primary),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    elements.append(hero_table)
    elements.append(Spacer(1, 8))

    # Executive Metadata Summary Table
    meta_box_data = [
        [
            Paragraph("<b>Problem Statement ID:</b> 26167", table_cell),
            Paragraph("<b>Target Domain:</b> Space Technology (Software)", table_cell),
            Paragraph("<b>Client Architecture:</b> React 18 + Vite + MapLibre", table_cell),
        ],
        [
            Paragraph("<b>Sponsoring Organization:</b> ISRO", table_cell),
            Paragraph("<b>Supported Modalities:</b> Optical, Multispectral, SAR", table_cell),
            Paragraph("<b>Backend Engine:</b> FastAPI + PyTorch + GDAL/Rasterio", table_cell),
        ],
        [
            Paragraph("<b>Core VLM Backbone:</b> Google Gemini 1.5 Pro", table_cell),
            Paragraph("<b>Vision Specialist:</b> SegFormer-B4 + Spectral Physics", table_cell),
            Paragraph("<b>GIS Engine:</b> Deterministic Area Calculator (UTM)", table_cell),
        ]
    ]
    meta_box = Table(meta_box_data, colWidths=[180, 180, 180])
    meta_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), c_bg_light),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(meta_box)
    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & SYSTEM OBJECTIVES
    # =========================================================================
    elements.append(Paragraph("1. Executive Summary &amp; System Objectives", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "<b>SatQuery AI</b> addresses a critical operational bottleneck in Earth Observation (EO): the steep technical "
        "barrier of legacy GIS software (e.g., QGIS, ArcGIS, ENVI). While modern space constellations (Sentinel-2, "
        "Sentinel-1 SAR, Landsat, Cartosat, and commercial satellites) generate petabytes of high-resolution imagery daily, "
        "deriving actionable geospatial intelligence requires trained GIS professionals skilled in coordinate reference systems, "
        "band mathematics, radiometric calibration, and supervised classification. SatQuery AI eliminates this complexity by providing an "
        "<b>autonomous, interactive vision-language intelligence platform</b> that accepts unconstrained natural language queries "
        "(e.g., <i>'Calculate the water reservoir surface area and identify new building construction between 2024 and 2026'</i>) "
        "and executes end-to-end, scientifically verified remote sensing workflows.",
        body_style
    ))

    # Architectural Tenet Callout
    tenet_data = [[
        Paragraph(
            "<b>The Core Architectural Tenet: The 'Hybrid AI' Paradigm</b><br/>"
            "Pure Large Vision-Language Models (VLMs) frequently hallucinate quantitative metrics (e.g., fabricating precise km&sup2; "
            "or confusing building shadows with water bodies). SatQuery AI enforces a rigorous <b>Hybrid Architecture</b>: "
            "Gemini 1.5 Pro acts as an agentic cognitive orchestrator and contextual explainer, while all quantitative surface areas, "
            "spectral indices (NDVI, NDWI, NDBI), pixel classifications, and spatial bounding boxes are computed by <b>specialist "
            "computer vision models (SegFormer-B4, BigEarthNet, CDVQA, VRSBench)</b> and <b>deterministic GDAL/Rasterio GIS math</b>. "
            "The AI is structurally barred from guessing quantitative numbers.",
            callout_text
        )
    ]]
    tenet_box = Table(tenet_data, colWidths=[540])
    tenet_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#93C5FD")),
        ("PADDING", (0, 0), (-1, -1), 5.5),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    elements.append(tenet_box)
    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 2: END-TO-END 4-TIER SYSTEM ARCHITECTURE
    # =========================================================================
    elements.append(Paragraph("2. End-to-End 4-Tier System Architecture", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "The system is organized into four modular, decoupled architectural layers designed for high scalability, "
        "fault isolation, and sub-second agentic decision-making:",
        body_style
    ))

    arch_table_data = [
        [
            Paragraph("Layer", table_cell_header),
            Paragraph("Key Technologies &amp; Components", table_cell_header),
            Paragraph("Functional Responsibility &amp; Capabilities", table_cell_header),
        ],
        [
            Paragraph("<b>Tier 1:<br/>Presentation &amp; UI</b>", table_cell_bold),
            Paragraph("• React 18, TypeScript, Vite<br/>• MapLibre GL &amp; Leaflet Viewers<br/>• Tailwind Glassmorphic Theme<br/>• Mission Control Dashboard<br/>• Web Speech API (Voice Queries)", table_cell),
            Paragraph("Provides an aerospace-grade command interface. Features split-screen bi-temporal swipe comparisons, interactive GeoJSON polygon overlays, band false-color switching, live audio speech-to-text queries, and downloadable audit reports.", table_cell),
        ],
        [
            Paragraph("<b>Tier 2:<br/>API Gateway &amp; Orchestration</b>", table_cell_bold),
            Paragraph("• FastAPI (ASGI, Asyncio)<br/>• WebSockets for live execution telemetry<br/>• Background Job Manager<br/>• JWT Security &amp; Rate Limiting<br/>• SQLite / PostgreSQL Storage", table_cell),
            Paragraph("Manages long-running asynchronous geospatial workloads. Streams real-time step-by-step progress to the client via WebSockets. Enforces strict input validation, image dimension matching, CRS co-registration, and file integrity.", table_cell),
        ],
        [
            Paragraph("<b>Tier 3:<br/>Agentic AI &amp; Reasoning</b>", table_cell_bold),
            Paragraph("• Google Gemini 1.5 Pro / Pro Vision<br/>• ReAct Cognitive Loop<br/>• Dynamic Remote Sensing Tool Registry<br/>• StepTracker Execution Logger<br/>• Hallucination Guardrails", table_cell),
            Paragraph("Translates natural language prompts into targeted geospatial tasks. Autonomously routes queries to specialist model adapters, evaluates intermediate data quality, synthesizes natural language summaries, and assigns calibrated confidence scores.", table_cell),
        ],
        [
            Paragraph("<b>Tier 4:<br/>Specialist Vision &amp; GIS Engines</b>", table_cell_bold),
            Paragraph("• SegFormer-B4 + Spectral Physics Engine<br/>• BigEarthNet-19 Sentinel-2 Adapter<br/>• CDVQA &amp; ChangeFormer CD Engine<br/>• VRSBench Visual Grounding Adapter<br/>• Rasterio &amp; GDAL UTM Area Calculator", table_cell),
            Paragraph("Executes pixel-level deep learning and remote sensing physics. Handles 12/16-bit radiometric stretch, 512&times;512 overlapping tiling, spectral index math (NDVI, NDWI, MNDWI, NDBI), SAR backscatter thresholding, and metric area conversion.", table_cell),
        ]
    ]

    arch_table = Table(arch_table_data, colWidths=[80, 200, 260])
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(arch_table)
    elements.append(Spacer(1, 9))

    # Clean Structured Topology Card
    flow_table_data = [
        [
            Paragraph("<b>Step 1: Input Ingestion</b><br/>User query + Optical / Multi-spectral / SAR GeoTIFF", table_cell),
            Paragraph("<b>&rarr; Step 2: Metadata &amp; Validation</b><br/>Rasterio affine, CRS check, dimension alignment", table_cell),
            Paragraph("<b>&rarr; Step 3: Agentic Router</b><br/>Gemini 1.5 Pro classifies intent &amp; selects tools", table_cell),
        ],
        [
            Paragraph("<b>&rarr; Step 4: Tiled Preprocessing</b><br/>512&times;512 overlap tiling with 2-98% radiometric stretch", table_cell),
            Paragraph("<b>&rarr; Step 5: Specialist Execution</b><br/>SegFormer, NDWI/MNDWI, NDBI, CDVQA, SAR fusion", table_cell),
            Paragraph("<b>&rarr; Step 6: Physical Refinement</b><br/>Shadow rejection, wave fill, metal roof filter", table_cell),
        ],
        [
            Paragraph("<b>&rarr; Step 7: GIS Area Math</b><br/>Exact UTM metric area calculation in ha &amp; km&sup2;", table_cell),
            Paragraph("<b>&rarr; Step 8: Multi-Modal Explanation</b><br/>Gemini synthesis + visual overlay generation", table_cell),
            Paragraph("<b>&rarr; Output Artifacts</b><br/>Downloadable PDF report, GeoJSON, PNG masks", table_cell),
        ]
    ]
    flow_table = Table(flow_table_data, colWidths=[180, 180, 180])
    flow_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(flow_table)
    elements.append(Spacer(1, 8))

    # Embed System Architecture Visual Diagram
    diag_path = str(Path(__file__).resolve().parent.parent / "docs" / "system_architecture_diagram.png")
    if os.path.exists(diag_path):
        elements.append(Paragraph("<b>Figure 1: Full 4-Tier System Architecture &amp; Subsystem Interaction Topology</b>", h3_style))
        elements.append(RLImage(diag_path, width=540, height=270))
        elements.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: END-TO-END QUERY & IMAGE PROCESSING FLOW
    # =========================================================================
    elements.append(Paragraph("3. End-to-End Query &amp; Image Processing Flow", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "Every incoming query traverses an 8-stage deterministic execution pipeline managed by the "
        "<b>AgentController</b> (<code>app/agents/agent_controller.py</code>):",
        body_style
    ))

    steps_data = [
        ("Stage 1: Ingestion &amp; Metadata Extraction",
         "The user uploads optical, multispectral, or SAR rasters (GeoTIFF, TIFF, PNG, JPEG) and enters a text/audio query. "
         "<code>MetadataService</code> invokes Rasterio to extract dimensions, bit-depth, spectral bands, affine transform, "
         "Coordinate Reference System (CRS/EPSG), and spatial bounding coordinates."),
        ("Stage 2: Input Validation &amp; Compatibility",
         "<code>InputValidator</code> performs sanity checks: verifies image dimension parity for bi-temporal pairs, checks "
         "geographic co-registration, validates whether required spectral bands (e.g., NIR for NDVI, SWIR for NDBI) are present, "
         "and rejects corrupt or unreadable rasters with actionable error messages."),
        ("Stage 3: Autonomous Query Routing",
         "<code>GeminiAgent</code> inspects the query and metadata context. It categorizes the intent into: "
         "<i>land_cover, water, built_up, vegetation, agriculture, change_detection, change_vqa, grounding, or vqa</i>. "
         "It selects the optimal combination of specialist tools and GIS calculators."),
        ("Stage 4: Radiometric Normalization &amp; Preprocessing",
         "Handles 12-bit / 16-bit satellite data (e.g. Sentinel-2 L2A BOA reflectance). Applies dynamic <b>2nd-to-98th percentile "
         "contrast stretching</b> across non-zero pixels to prevent atmospheric haze or solar glint from washing out features. "
         "For gigapixel rasters, creates 512&times;512 tiles with 64px overlap and distance-weighted blending to eliminate border seams."),
        ("Stage 5: Specialist Model Inference",
         "Dispatches arrays to the target specialist adapter: SegFormer-B4 semantic segmentation, BigEarthNet-19 classifier, "
         "VRSBench region grounding, CDVQA change detector, or Optical-SAR fusion. If deep learning weights are uninitialized, "
         "it falls back seamlessly to the high-precision spectral remote-sensing engine."),
        ("Stage 6: Physics-Guided Remote Sensing Post-Refinement",
         "Sanity-checks predictions against physical electromagnetic laws: eliminates false agriculture on concrete roofs, "
         "removes tree shadows falsely classified as water, fills wave ripples, and reclassifies blue industrial tin roofs."),
        ("Stage 7: Deterministic GIS Metric Calculation",
         "<code>AreaCalculator</code> combines classified pixel counts with the raster's ground sampling distance (GSD). "
         "If georeferenced, it projects bounding coordinates to the local UTM zone to compute exact surface area in "
         "<b>square meters (m&sup2;), hectares (ha), and square kilometers (km&sup2;)</b>, without rounding approximations."),
        ("Stage 8: Multi-Modal Explanation &amp; Report Assembly",
         "Gemini 1.5 Pro receives the verified GIS statistics, model metadata, and detected class distributions to draft an "
         "executive natural language synthesis. <code>ReportService</code> concurrently generates publication-quality "
         "PDF and interactive HTML reports with embedded color-coded evidence overlays and audit logs.")
    ]

    for stage_title, stage_desc in steps_data:
        elements.append(Paragraph(f"<b>{stage_title}</b>", h3_style))
        elements.append(Paragraph(stage_desc, bullet_style))

    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 4: HOW WATER IS DETECTED (DEEP DIVE)
    # =========================================================================
    elements.append(Paragraph("4. Deep Dive: Water Detection Architecture &amp; Algorithms", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "Water body extraction in satellite imagery is notoriously challenging due to spectral confusion: "
        "dark asphalt highways, deep cloud shadows, and dense coniferous tree canopies often mimic water's low optical reflectance. "
        "SatQuery AI solves this with a <b>multi-modal, physics-guided detection pipeline</b>:",
        body_style
    ))

    water_table_data = [
        [
            Paragraph("Detection Path", table_cell_header),
            Paragraph("Physical Principle &amp; Mathematical Formula", table_cell_header),
            Paragraph("Operational Thresholds &amp; Implementation", table_cell_header),
        ],
        [
            Paragraph("<b>Path A:<br/>Multispectral NDWI<br/>(McFeeters, 1996)</b>", table_cell_bold),
            Paragraph("Liquid water has high reflectance in the green band and near-total absorption in near-infrared (NIR):<br/>"
                      "<b>NDWI = (Green &minus; NIR) / (Green + NIR)</b>", table_cell),
            Paragraph("Water threshold: <b>NDWI &gt; 0.0</b>.<br/>Implemented in <code>app/gis/indices.py</code>. Automatically "
                      "detects Sentinel-2 Band 3 (Green) and Band 8 (NIR). Returns unpolluted open water bodies.", table_cell),
        ],
        [
            Paragraph("<b>Path B:<br/>Modified NDWI<br/>(MNDWI, Xu, 2006)</b>", table_cell_bold),
            Paragraph("Replaces NIR with Shortwave Infrared (SWIR1, B11) to eliminate false positives from built-up urban concrete:<br/>"
                      "<b>MNDWI = (Green &minus; SWIR1) / (Green + SWIR1)</b>", table_cell),
            Paragraph("Water threshold: <b>MNDWI &gt; 0.0</b>.<br/>Drastically suppresses urban high-albedo structures, making it "
                      "the gold standard for urban flood tracking and reservoir perimeter mapping.", table_cell),
        ],
        [
            Paragraph("<b>Path C:<br/>Optical RGB Reflectance Engine</b>", table_cell_bold),
            Paragraph("Physics-based multi-criteria spectral rules in <code>_spectral_rs_classify()</code>:<br/>"
                      "• <b>Deep Clean Water:</b> Blue dominant (B &gt; 1.10&middot;R, B &ge; 0.85&middot;G), low red (R &lt; 85), low brightness (&lt; 95), smooth texture (&sigma; &lt; 12.0).<br/>"
                      "• <b>Turbid / Sediment Water:</b> G &gt; 1.08&middot;R, B &ge; 0.95&middot;R, NDWI_GR &gt; 0.05.<br/>"
                      "• <b>Green Algal Lakes:</b> G &gt; 1.04&middot;R, ExG &lt; 25, GLI &lt; 0.10, &sigma; &lt; 14.0.", table_cell),
            Paragraph("Operates when NIR is absent (e.g. standard aerial photography, Google Earth, Cartosat-2 RGB). Uses "
                      "connected component analysis (<code>scipy.ndimage.label</code>) with cluster size filtering (&ge;60px for blue, &ge;200px for turbid).", table_cell),
        ],
        [
            Paragraph("<b>Path D:<br/>SAR Radar Backscatter</b>", table_cell_bold),
            Paragraph("Specular scattering: Smooth water surfaces act as specular reflectors, bouncing radar pulses away from the "
                      "satellite sensor, producing near-zero backscatter return.", table_cell),
            Paragraph("Sentinel-1 VV/VH threshold: <b>&lt; &minus;18.0 dB</b>.<br/>Implemented in <code>OpticalSARAdapter</code>. Enables "
                      "all-weather, 24/7 flood detection through dense clouds, monsoons, and smoke.", table_cell),
        ]
    ]

    water_table = Table(water_table_data, colWidths=[100, 220, 220])
    water_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(water_table)
    elements.append(Spacer(1, 5))

    # Water Anti-Hallucination Callout
    elements.append(Paragraph("<b>Water False-Positive Elimination (Post-Refinement Stage):</b>", h3_style))
    elements.append(Paragraph(
        "• <b>Tree Shadow Rejection:</b> Shadowed vegetation exhibits low brightness but high surface roughness (standard deviation "
        "&sigma; &ge; 6.0) and distinct chlorophyll green-over-red ratios (G &gt; 1.15&middot;R). These are reclassified to <i>Vegetation</i>.<br/>"
        "• <b>Blue Tin / Coated Metal Roof Rejection:</b> Industrial warehouses with blue metal roofs mimic water's blue band dominance. "
        "The engine checks brightness (&gt; 125) and red component (R &ge; 55). High-reflectance blue surfaces are reclassified to <i>Built-up</i>.<br/>"
        "• <b>Morphological Ripple Hole Filling:</b> Wind-induced sun glint or wave ripples on lake surfaces create internal voids. "
        "<code>scipy.ndimage.binary_fill_holes()</code> restores continuous water body topology.<br/>"
        "• <b>Isolated Speckle Pruning:</b> Isolated pixel clusters smaller than 30 pixels are pruned to eliminate road noise.",
        body_style
    ))
    elements.append(Spacer(1, 6))

    # Embed Water Detection Flowchart
    water_diag = str(Path(__file__).resolve().parent.parent / "docs" / "water_detection_flowchart.png")
    if os.path.exists(water_diag):
        elements.append(Paragraph("<b>Figure 2: Multi-Modal Water Detection &amp; Shadow Elimination Pipeline Flowchart</b>", h3_style))
        elements.append(RLImage(water_diag, width=540, height=270))
        elements.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: HOW BUILDINGS & BUILT-UP ARE DETECTED (DEEP DIVE)
    # =========================================================================
    elements.append(Paragraph("5. Deep Dive: Building &amp; Built-Up Area Detection", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "Detecting urban structures in remote sensing is complex because rooftops vary drastically in construction material: "
        "concrete, red clay terracotta tiles, galvanized iron/tin, asphalt shingles, and bright reflective waterproofing membranes. "
        "SatQuery AI deploys a <b>comprehensive multi-spectral, transformer, and morphological classification taxonomy</b>:",
        body_style
    ))

    building_table_data = [
        [
            Paragraph("Rooftop / Structure Type", table_cell_header),
            Paragraph("Spectral Profile &amp; Feature Signature", table_cell_header),
            Paragraph("Classification Logic &amp; Disambiguation", table_cell_header),
        ],
        [
            Paragraph("<b>Terracotta / Red Clay Tiles</b>", table_cell_bold),
            Paragraph("High red reflectance, absorption in green and blue:<br/><b>R &gt; 1.08&middot;G, R &gt; 1.18&middot;B, R &ge; 68, GLI &lt; 0.04</b>", table_cell),
            Paragraph("Prevents misclassifying rural terracotta homes and historic urban residential blocks as bare soil or dry fallow land.", table_cell),
        ],
        [
            Paragraph("<b>Concrete / Cement / Plaster</b>", table_cell_bold),
            Paragraph("Spectrally neutral reflectance across RGB:<br/><b>|R &minus; G| &le; 25, |G &minus; B| &le; 30, Brightness 65 to 235</b>", table_cell),
            Paragraph("Captures typical residential concrete roofs, masonry, commercial complexes, and urban apartment slabs.", table_cell),
        ],
        [
            Paragraph("<b>High-Albedo Reflective Roofs</b>", table_cell_bold),
            Paragraph("White membranes, polished sheet metal, galvanized zinc:<br/><b>Brightness &ge; 165, Saturation &lt; 0.24, GLI &lt; 0.05</b>", table_cell),
            Paragraph("Distinguished from clouds through lack of shadow casting and crisp rectilinear geometry.", table_cell),
        ],
        [
            Paragraph("<b>Dark Composite / Industrial Metal</b>", table_cell_bold),
            Paragraph("Low-to-medium albedo tar or blue coated tin:<br/><b>Brightness 42&ndash;65, Saturation &lt; 0.22, or B &gt; 1.08&middot;R</b>", table_cell),
            Paragraph("Distinguished from asphalt roads via aspect ratio and adjacency to parcel boundaries.", table_cell),
        ],
        [
            Paragraph("<b>Multispectral NDBI Engine</b>", table_cell_bold),
            Paragraph("Impervious built-up reflects strongly in SWIR1 and absorbs NIR:<br/><b>NDBI = (SWIR1 &minus; NIR) / (SWIR1 + NIR)</b>", table_cell),
            Paragraph("Threshold: <b>NDBI &gt; 0.0</b>. Provides baseline impervious surface masking when multispectral bands are available.", table_cell),
        ],
        [
            Paragraph("<b>SAR Double-Bounce Radar</b>", table_cell_bold),
            Paragraph("Corner reflector effect between vertical building walls and flat ground generates intense radar return:<br/><b>SAR Backscatter &gt; &minus;8.0 dB</b>", table_cell),
            Paragraph("Provides geometric structural confirmation in cloud-covered optical images, verifying vertical man-made construction.", table_cell),
        ]
    ]

    building_table = Table(building_table_data, colWidths=[120, 200, 220])
    building_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_secondary),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(building_table)
    elements.append(Spacer(1, 5))

    # Built-up disambiguation rules
    elements.append(Paragraph("<b>Disambiguation: Separating Buildings from Roads, Agriculture &amp; Bare Soil:</b>", h3_style))
    elements.append(Paragraph(
        "• <b>Road Disambiguation:</b> Asphalt roads have dark, neutral reflectance (Brightness 24&ndash;112, Saturation &lt; 0.25, "
        "Chroma &lt; 28). Road networks are evaluated <i>prior</i> to built-up, reserving Class 5 for transport corridors.<br/>"
        "• <b>Bare Land Disambiguation:</b> Natural exposed soil displays a strictly monotonic rise from Blue to Green to Red "
        "(R &ge; 1.04&middot;G &ge; 1.00&middot;B). Soil lacks the high spectral variation of urban clusters and is mapped to Class 6.<br/>"
        "• <b>Rural Expanses Filter:</b> Massive contiguous patches (&gt; 2500 connected pixels) with near-zero texture roughness "
        "(&sigma; &lt; 3.5) are automatically reclassified from Built-up to Agriculture (if GLI &ge; 0.08) or Bare Land, "
        "completely preventing false urbanization across vast rural plains.<br/>"
        "• <b>Deep Learning Backbone:</b> SegFormer-B4 (Hierarchical Transformer Encoder) extracts multi-scale attention across "
        "512&times;512 receptive fields, ensuring contextual understanding of building boundaries.",
        body_style
    ))
    elements.append(Spacer(1, 6))

    # Embed Building Detection Flowchart
    bldg_diag = str(Path(__file__).resolve().parent.parent / "docs" / "building_detection_flowchart.png")
    if os.path.exists(bldg_diag):
        elements.append(Paragraph("<b>Figure 3: Building &amp; Built-Up Detection Engine &amp; Disambiguation Flowchart</b>", h3_style))
        elements.append(RLImage(bldg_diag, width=540, height=270))
        elements.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: SPECIALIST MODELS & BENCHMARKS
    # =========================================================================
    elements.append(Paragraph("6. AI Models, Specialist Adapters &amp; Remote Sensing Benchmarks", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "SatQuery AI integrates seven domain-adapted specialist model adapters registered in the unified "
        "<code>model_registry</code> (<code>app/models/adapters/</code>):",
        body_style
    ))

    model_specs_data = [
        [
            Paragraph("Specialist Model Adapter", table_cell_header),
            Paragraph("Base Architecture / Backbone", table_cell_header),
            Paragraph("Domain Adaptation &amp; Benchmark Evaluation", table_cell_header),
            Paragraph("Output &amp; Role", table_cell_header),
        ],
        [
            Paragraph("<b>SegFormer Land Cover</b><br/><code>segmentation.py</code>", table_cell_bold),
            Paragraph("SegFormer-B4 Transformer<br/>(MiT-B4 Hierarchical Encoder)", table_cell),
            Paragraph("Adapted from ADE20K with custom Remote Sensing class remapping and physical post-refinement.", table_cell),
            Paragraph("Full 7-class semantic raster mask, pixel counts, and GIS polygon boundaries.", table_cell),
        ],
        [
            Paragraph("<b>BigEarthNet-19 Classifier</b><br/><code>rs_adapters.py</code>", table_cell_bold),
            Paragraph("ResNet-50 / ViT-B Multi-Label Classifier", table_cell),
            Paragraph("Evaluated on <b>BigEarthNet-19</b> benchmark (590,326 Sentinel-2 image patches across 10 European nations).", table_cell),
            Paragraph("19 CORINE-aligned multi-spectral land use labels with calibrated confidence ratings.", table_cell),
        ],
        [
            Paragraph("<b>CDVQA Bi-Temporal Engine</b><br/><code>rs_adapters.py</code>", table_cell_bold),
            Paragraph("Bi-Temporal Siamese Network + Spatial Quadrant Classifier", table_cell),
            Paragraph("Evaluated on <b>CDVQA</b> &amp; <b>LEVIR-CD</b> benchmarks for bi-temporal building and vegetation transition.", table_cell),
            Paragraph("Change masks, primary transition dynamics (e.g. Veg&rarr;Built-up), and cardinal locations.", table_cell),
        ],
        [
            Paragraph("<b>VRSBench Grounding</b><br/><code>rs_adapters.py</code>", table_cell_bold),
            Paragraph("Connected Component Segmenter + Bounding Box Regressor", table_cell),
            Paragraph("Evaluated on <b>VRSBench</b> remote-sensing visual grounding benchmark for natural language queries.", table_cell),
            Paragraph("Spatial bounding boxes [ymin, xmin, ymax, xmax], visual reticles, centroids.", table_cell),
        ],
        [
            Paragraph("<b>RSVQA Remote Sensing VQA</b><br/><code>rs_adapters.py</code>", table_cell_bold),
            Paragraph("Gemini 1.5 Pro Vision conditioned with RSVQA system prompts", table_cell),
            Paragraph("Evaluated on <b>RSVQA (HR/LR)</b> benchmark. Eliminates common shadow/water false positives.", table_cell),
            Paragraph("Domain-scientific textual answers grounded in geospatial evidence.", table_cell),
        ],
        [
            Paragraph("<b>Optical-SAR Fusion</b><br/><code>optical_sar.py</code>", table_cell_bold),
            Paragraph("Channel Concatenation + Backscatter Consensus", table_cell),
            Paragraph("Evaluated on SEN12MS multimodal dataset (Sentinel-1 SAR + Sentinel-2 Optical).", table_cell),
            Paragraph("Joint all-weather land cover analysis, penetrating cloud decks and smoke.", table_cell),
        ],
        [
            Paragraph("<b>Gemini Cognitive Reasoner</b><br/><code>gemini_agent.py</code>", table_cell_bold),
            Paragraph("Google Gemini 1.5 Pro Multimodal Foundation Model", table_cell),
            Paragraph("Configured with strict remote-sensing system prompts and zero-hallucination math guardrails.", table_cell),
            Paragraph("Query classification, dynamic tool invocation, and executive natural language summaries.", table_cell),
        ]
    ]

    model_table = Table(model_specs_data, colWidths=[90, 110, 180, 160])
    model_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("PADDING", (0, 0), (-1, -1), 3.8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(model_table)
    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 7: BI-TEMPORAL CHANGE DETECTION & SPATIAL QUADRANTS
    # =========================================================================
    elements.append(Paragraph("7. Bi-Temporal Change Detection &amp; Spatial Dynamics", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "When two co-registered temporal scenes (T<sub>1</sub> and T<sub>2</sub>) are uploaded, SatQuery AI activates the "
        "<b>CDVQA Change Detection Engine</b> (<code>app/models/adapters/change_detection.py</code>):",
        body_style
    ))

    elements.append(Paragraph(
        "• <b>Radiometric Alignment:</b> Both scenes are normalized to common dynamic ranges via 2nd&ndash;98th percentile contrast matching.<br/>"
        "• <b>Difference &amp; Gradient Computation:</b> Absolute spectral distance |T<sub>2</sub> &minus; T<sub>1</sub>| is computed across channels. "
        "Statistical Otsu thresholding separates significant land-use transitions from seasonal illumination shifts.<br/>"
        "• <b>Transition Categorization:</b> The engine classifies changes into 7 discrete transition classes: "
        "<i>Vegetation Gain (Reforestation), Vegetation Loss (Deforestation), Water Body Inundation/Depletion, "
        "Built-Up Gain (Urban Expansion), Built-Up Loss (Demolition), and Surface Modification</i>.<br/>"
        "• <b>Spatial Quadrant &amp; Centroid Localization:</b> Connected change clusters are evaluated for center-of-mass coordinates. "
        "The engine computes mean latitude/longitude and assigns cardinal sector descriptions (e.g. <i>'Predominantly Northern-Eastern sector'</i>), "
        "answering both 'What changed?' and 'Where did it change?'.",
        body_style
    ))
    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 8: VERIFICATION, GIS MATH & ANTI-HALLUCINATION GUARANTEES
    # =========================================================================
    elements.append(Paragraph("8. GIS Metric Quantification &amp; Zero-Hallucination Guardrails", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    elements.append(Paragraph(
        "In critical remote sensing domains (e.g., assessing flood damage for NDRF disaster relief, monitoring illegal deforestation, "
        "or auditing urban property expansion), hallucinated metrics are hazardous. SatQuery AI enforces three structural guarantees:",
        body_style
    ))

    guarantee_data = [
        [
            Paragraph("1. Deterministic Projection-Aware Area Math", table_cell_bold),
            Paragraph("<code>AreaCalculator</code> (<code>app/gis/area_calculator.py</code>) never allows LLMs to calculate areas. "
                      "It reads the raster's affine transformation matrix (|a &times; e &minus; b &times; d|) to obtain pixel ground sampling distance. "
                      "If the image is in geographic coordinates (EPSG:4326), it automatically reprojects bounding boxes to the "
                      "corresponding local <b>Universal Transverse Mercator (UTM) zone</b>. Pixel counts are converted to exact "
                      "metric units: Area<sub>m&sup2;</sub> = N<sub>pixels</sub> &times; (GSD<sub>x</sub> &times; GSD<sub>y</sub>). "
                      "Results are reported in hectares (10<sup>4</sup> m&sup2;) and square kilometers (10<sup>6</sup> m&sup2;).", table_cell),
        ],
        [
            Paragraph("2. Physics-Grounded Confidence Calibration", table_cell_bold),
            Paragraph("Instead of displaying static arbitrary confidence, SatQuery AI calculates <b>calibrated confidence</b> dynamically: "
                      "derived from spectral contrast standard deviation (&sigma; / 255.0), cluster connectivity, and sensor signal-to-noise ratio. "
                      "Confidence scores range from 0.70 (partially obscured) to 0.96 (high-contrast multispectral consensus).", table_cell),
        ],
        [
            Paragraph("3. Auditable Execution Trace &amp; Provenance", table_cell_bold),
            Paragraph("Every completed job outputs an immutable <code>execution_summary</code> containing: exact input image hashes, "
                      "detected EPSG CRS, selected tools, model version IDs, per-class pixel counts, duration in milliseconds, and warnings. "
                      "This trace is embedded into downloadable PDF and HTML inspection reports.", table_cell),
        ]
    ]

    guarantee_table = Table(guarantee_data, colWidths=[160, 380])
    guarantee_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), c_bg_light),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("PADDING", (0, 0), (-1, -1), 4.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(guarantee_table)
    elements.append(Spacer(1, 9))

    # =========================================================================
    # SECTION 9: COMPLETE TECHNOLOGY STACK & DEPLOYMENT TOPOLOGY
    # =========================================================================
    elements.append(PageBreak())
    elements.append(Paragraph("9. Complete Technology Stack &amp; Production Topology", h1_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=1, spaceAfter=5))

    tech_stack_data = [
        [
            Paragraph("Subsystem", table_cell_header),
            Paragraph("Technologies &amp; Frameworks", table_cell_header),
            Paragraph("Version &amp; Production Configuration", table_cell_header),
        ],
        [
            Paragraph("<b>Frontend Client</b>", table_cell_bold),
            Paragraph("React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, MapLibre GL, Leaflet", table_cell),
            Paragraph("Port 5173 / Production NGINX CDN. Responsive glassmorphic dark UI, WebSpeech voice queries.", table_cell),
        ],
        [
            Paragraph("<b>Backend API &amp; Server</b>", table_cell_bold),
            Paragraph("Python 3.13, FastAPI, Uvicorn (ASGI), Asyncio, Pydantic v2, SQLite / PostgreSQL", table_cell),
            Paragraph("Port 8000. RESTful API with automated OpenAPI 3.1 docs, async background tasks, WebSocket channels.", table_cell),
        ],
        [
            Paragraph("<b>Geospatial &amp; Image Engine</b>", table_cell_bold),
            Paragraph("GDAL, Rasterio 1.5, Shapely 2.1, Scipy 1.18, OpenCV 5.0, Pillow 12.3, Affine 3.0", table_cell),
            Paragraph("High-performance C++ wrapped geospatial bindings for GeoTIFF CRS transforms and morphology.", table_cell),
        ],
        [
            Paragraph("<b>AI / ML &amp; VLM Stack</b>", table_cell_bold),
            Paragraph("PyTorch 2.14, HuggingFace Transformers, Google Generative AI SDK, SegFormer-B4", table_cell),
            Paragraph("Gemini 1.5 Pro multimodal reasoning + local SegFormer transformer / deterministic spectral engines.", table_cell),
        ],
        [
            Paragraph("<b>Reporting &amp; Evidence</b>", table_cell_bold),
            Paragraph("ReportLab 5.0, Jinja2 3.1, Aiofiles, JSONL Provenance Logger", table_cell),
            Paragraph("Automated vector PDF report generation with color-coded raster overlays and audit trail.", table_cell),
        ]
    ]

    tech_table = Table(tech_stack_data, colWidths=[110, 230, 200])
    tech_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("BOX", (0, 0), (-1, -1), 0.7, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, c_border),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_bg_light]),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(tech_table)
    elements.append(Spacer(1, 10))

    # Concluding Sign-off Box
    signoff_data = [[
        Paragraph(
            "<b>SATQUERY AI — ARCHITECTURAL SPECIFICATION COMPLIANCE SIGN-OFF</b><br/>"
            "This technical specification satisfies all functional, architectural, and algorithmic requirements specified in "
            "<b>ISRO Problem Statement ID 26167</b> (Smart India Hackathon 2026). The platform provides complete multimodal remote sensing "
            "intelligence across optical, multispectral, and SAR imagery, executing verified water, building, road, vegetation, and change "
            "detection workflows through natural-language conversation.",
            callout_text
        )
    ]]
    signoff_box = Table(signoff_data, colWidths=[540])
    signoff_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, c_accent),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    elements.append(signoff_box)

    # Build Document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Architecture PDF successfully generated at: {output_path}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent
    pdf_filename = "SatQuery_AI_System_Architecture_and_Technical_Specification.pdf"
    target_path = str(out_dir / pdf_filename)
    build_pdf(target_path)

    # Also save a copy in docs/
    docs_dir = out_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    docs_target = str(docs_dir / pdf_filename)
    shutil.copy2(target_path, docs_target)
    print(f"[SUCCESS] Copy also saved to docs: {docs_target}")
