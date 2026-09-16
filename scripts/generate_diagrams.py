"""
SatQuery AI - Architecture & Flow Diagram Generator
Renders high-resolution, publication-quality technical diagrams for:
1. System 4-Tier Architecture
2. End-to-End Query Processing Pipeline
3. Water Detection Engine (NDWI / MNDWI / Optical RGB / SAR / Shadow Rejection)
4. Building & Urban Built-Up Area Detection Engine
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Font configuration
WINDIR = os.environ.get("WINDIR", "C:\\Windows")
FONT_DIR = os.path.join(WINDIR, "Fonts")

def get_font(name: str, size: int):
    candidates = [
        os.path.join(FONT_DIR, f"{name}.ttf"),
        os.path.join(FONT_DIR, "segoeui.ttf"),
        os.path.join(FONT_DIR, "arial.ttf"),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

def get_bold_font(size: int):
    candidates = [
        os.path.join(FONT_DIR, "segoeuib.ttf"),
        os.path.join(FONT_DIR, "arialbd.ttf"),
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return get_font("arial", size)

def draw_rounded_card(draw, xy, fill, outline, width=1, radius=8):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start_xy, end_xy, color, width=2, arrow_size=6):
    x1, y1 = start_xy
    x2, y2 = end_xy
    draw.line([start_xy, end_xy], fill=color, width=width)
    import math
    angle = math.atan2(y2 - y1, x2 - x1)
    # arrow head
    p1 = (x2 - arrow_size * math.cos(angle - math.pi / 6),
          y2 - arrow_size * math.sin(angle - math.pi / 6))
    p2 = (x2 - arrow_size * math.cos(angle + math.pi / 6),
          y2 - arrow_size * math.sin(angle + math.pi / 6))
    draw.polygon([end_xy, p1, p2], fill=color)


def generate_system_architecture_diagram(output_path: str):
    """Generates the 4-tier high-level system architecture diagram."""
    w, h = 1600, 960
    img = Image.new("RGB", (w, h), color="#0F172A")  # Dark Slate Background
    draw = ImageDraw.Draw(img)

    f_title = get_bold_font(26)
    f_sub = get_font("segoeui", 14)
    f_tier = get_bold_font(18)
    f_box_title = get_bold_font(14)
    f_box_sub = get_font("segoeui", 11)
    f_badge = get_bold_font(10)

    # Header Banner
    draw.rectangle([0, 0, w, 75], fill="#0B192C")
    draw.text((35, 14), "SATQUERY AI — 4-TIER SYSTEM ARCHITECTURE", font=f_title, fill="#FFFFFF")
    draw.text((35, 46), "Multimodal Remote Sensing Vision-Language Assistant  •  ISRO Problem Statement ID: 26167", font=f_sub, fill="#94A3B8")
    draw.line([0, 75, w, 75], fill="#FF6500", width=3)  # Accent ISRO orange

    tiers = [
        {
            "name": "TIER 1: PRESENTATION & CLIENT LAYER (React 18 + Vite)",
            "y": 95, "h": 150, "color": "#1E293B", "border": "#38BDF8", "badge": "FRONTEND",
            "cards": [
                ("Mission Control Dashboard", "Glassmorphic telemetry, live AOI selection, dynamic task switching"),
                ("Geospatial Map Viewer", "MapLibre GL & Leaflet, GeoJSON polygon overlays, split-screen swipe"),
                ("Earth Intelligence Copilot", "Conversational chat, multi-turn dialogue, Web Speech voice input"),
                ("Evidence & Report Center", "Interactive metrics, class area breakdown, downloadable PDF/HTML reports"),
            ]
        },
        {
            "name": "TIER 2: API GATEWAY & ASYNC ORCHESTRATION (FastAPI)",
            "y": 275, "h": 150, "color": "#1E293B", "border": "#818CF8", "badge": "GATEWAY & ORCHESTRATOR",
            "cards": [
                ("FastAPI REST & WebSockets", "Async ASGI routes, live job streaming, sub-second telemetry"),
                ("Async Job Manager", "Background task queue, state store (SQLite/PostgreSQL), execution logs"),
                ("Input & Geographic Validator", "Co-registration, CRS compatibility, dimension matching, band check"),
                ("Metadata Ingestion Engine", "Rasterio & GDAL GeoTIFF affine parsing, GSD extraction, EPSG transforms"),
            ]
        },
        {
            "name": "TIER 3: AGENTIC AI REASONING LAYER (Gemini 1.5 Pro)",
            "y": 455, "h": 150, "color": "#1E293B", "border": "#F59E0B", "badge": "AGENTIC REASONING",
            "cards": [
                ("Gemini 1.5 Pro Cognitive Agent", "NL intent classification, ReAct loop, zero-hallucination guardrails"),
                ("Dynamic Tool Registry", "Autonomous routing to specialist models, dynamic tool selection"),
                ("StepTracker Audit Engine", "Auditable execution steps, telemetry latency tracking, provenance"),
                ("Executive Multi-Modal Explainer", "Domain-scientific synthesis combining visual context & GIS stats"),
            ]
        },
        {
            "name": "TIER 4: SPECIALIST COMPUTER VISION & GIS ENGINES (PyTorch + GDAL)",
            "y": 635, "h": 260, "color": "#1E293B", "border": "#10B981", "badge": "SPECIALIST & GIS ENGINES",
            "cards": [
                ("SegFormer-B4 Land Cover", "Transformer segmentation, 7-class semantic map, 512x512 tiling"),
                ("BigEarthNet-19 RS Classifier", "Multi-spectral Sentinel-2 taxonomy, 19 CORINE-aligned classes"),
                ("CDVQA Bi-Temporal Engine", "Siamese change detection, transition dynamics, spatial quadrants"),
                ("VRSBench Visual Grounding", "Spatial bounding boxes [ymin, xmin, ymax, xmax], visual reticles"),
                ("Spectral Indices Engine", "NDVI, NDWI, MNDWI, NDBI band-aware physical calculation"),
                ("Optical-SAR Fusion", "Sentinel-1 SAR backscatter fusion (< -18dB water, > -8dB built-up)"),
                ("Deterministic Area Calculator", "UTM projection, pixel-to-metric math in m2, hectares & km2"),
                ("Evidence & Report Generator", "ReportLab PDF & HTML compilation, vector raster overlay maps"),
            ]
        }
    ]

    for t in tiers:
        # Tier Container Box
        draw_rounded_card(draw, [25, t["y"], w - 25, t["y"] + t["h"]], fill=t["color"], outline=t["border"], width=1, radius=6)
        # Tier Header Tag
        draw.text((40, t["y"] + 10), t["name"], font=f_tier, fill=t["border"])
        
        # Cards inside tier
        cards = t["cards"]
        n_cards = len(cards)
        card_w = (w - 70 - (n_cards - 1) * 12) / n_cards
        
        if t["h"] > 180: # Tier 4 has 2 rows
            half = len(cards) // 2
            card_w = (w - 70 - (half - 1) * 12) / half
            for i, (ctitle, csub) in enumerate(cards):
                row = 0 if i < half else 1
                col = i if i < half else i - half
                cx1 = 35 + col * (card_w + 12)
                cy1 = t["y"] + 42 + row * 102
                cx2 = cx1 + card_w
                cy2 = cy1 + 92
                draw_rounded_card(draw, [cx1, cy1, cx2, cy2], fill="#0F172A", outline="#334155", width=1, radius=5)
                draw.text((cx1 + 10, cy1 + 10), ctitle, font=f_box_title, fill="#FFFFFF")
                # wrap subtext
                words = csub.split()
                line1, line2 = "", ""
                for word in words:
                    if len(line1) + len(word) < 32:
                        line1 += word + " "
                    else:
                        line2 += word + " "
                draw.text((cx1 + 10, cy1 + 34), line1.strip(), font=f_box_sub, fill="#94A3B8")
                if line2:
                    draw.text((cx1 + 10, cy1 + 52), line2.strip(), font=f_box_sub, fill="#94A3B8")
        else:
            for i, (ctitle, csub) in enumerate(cards):
                cx1 = 35 + i * (card_w + 12)
                cy1 = t["y"] + 42
                cx2 = cx1 + card_w
                cy2 = cy1 + 92
                draw_rounded_card(draw, [cx1, cy1, cx2, cy2], fill="#0F172A", outline="#334155", width=1, radius=5)
                draw.text((cx1 + 10, cy1 + 10), ctitle, font=f_box_title, fill="#FFFFFF")
                words = csub.split()
                line1, line2 = "", ""
                for word in words:
                    if len(line1) + len(word) < 30:
                        line1 += word + " "
                    else:
                        line2 += word + " "
                draw.text((cx1 + 10, cy1 + 34), line1.strip(), font=f_box_sub, fill="#94A3B8")
                if line2:
                    draw.text((cx1 + 10, cy1 + 52), line2.strip(), font=f_box_sub, fill="#94A3B8")

    # Connective Vertical Flow Arrows between Tiers
    arrow_xs = [200, 600, 1000, 1400]
    for ax in arrow_xs:
        draw_arrow(draw, (ax, 245), (ax, 275), color="#0EA5E9", width=2, arrow_size=6)
        draw_arrow(draw, (ax, 425), (ax, 455), color="#0EA5E9", width=2, arrow_size=6)
        draw_arrow(draw, (ax, 605), (ax, 635), color="#0EA5E9", width=2, arrow_size=6)

    # Footer
    draw.rectangle([0, h - 35, w, h], fill="#0B192C")
    draw.text((35, h - 25), "SatQuery AI  •  Enterprise Architecture v2.4  •  Smart India Hackathon 2026", font=f_sub, fill="#64748B")
    draw.text((w - 360, h - 25), "Zero-Hallucination Deterministic GIS + Agentic AI", font=f_sub, fill="#38BDF8")

    img.save(output_path, "PNG", quality=95)
    print(f"[OK] System architecture diagram generated: {output_path}")


def generate_water_detection_flowchart(output_path: str):
    """Generates the specialized Water Detection Engine architecture flowchart."""
    w, h = 1400, 840
    img = Image.new("RGB", (w, h), color="#0B192C")
    draw = ImageDraw.Draw(img)

    f_title = get_bold_font(24)
    f_sub = get_font("segoeui", 13)
    f_card_t = get_bold_font(14)
    f_body = get_font("segoeui", 10.5)
    f_formula = get_bold_font(11.5)

    # Header
    draw.rectangle([0, 0, w, 70], fill="#08101E")
    draw.text((30, 12), "SATQUERY AI — WATER DETECTION ENGINE ARCHITECTURE", font=f_title, fill="#38BDF8")
    draw.text((30, 42), "Quad-Path Multi-Modal Extraction & Physics-Guided Shadow Elimination Pipeline", font=f_sub, fill="#94A3B8")
    draw.line([0, 70, w, 70], fill="#0284C7", width=2)

    # Ingestion Stage (Top)
    draw_rounded_card(draw, [400, 90, 1000, 150], fill="#1E293B", outline="#0EA5E9", radius=6)
    draw.text((420, 100), "Input Satellite Raster (GeoTIFF / Sentinel-2 / Landsat / SAR / Aerial RGB)", font=f_card_t, fill="#FFFFFF")
    draw.text((420, 124), "Metadata Inspection: Band identification (Red, Green, Blue, NIR, SWIR1, SAR VV/VH)", font=f_body, fill="#94A3B8")

    # Connector down to 4 branches
    draw_arrow(draw, (700, 150), (700, 185), color="#0EA5E9", width=2)
    draw.line([175, 185, 1225, 185], fill="#0EA5E9", width=2)
    draw_arrow(draw, (175, 185), (175, 210), color="#0EA5E9", width=2)
    draw_arrow(draw, (525, 185), (525, 210), color="#0EA5E9", width=2)
    draw_arrow(draw, (875, 185), (875, 210), color="#0EA5E9", width=2)
    draw_arrow(draw, (1225, 185), (1225, 210), color="#0EA5E9", width=2)

    # 4 Detection Paths
    paths = [
        {
            "x": 35, "w": 280, "title": "PATH 1: MULTISPECTRAL NDWI",
            "badge": "McFeeters (1996)", "badge_col": "#0284C7",
            "formula": "NDWI = (Green - NIR) / (Green + NIR)",
            "details": [
                "• Requires: Band 3 (Green) & Band 8 (NIR)",
                "• Physics: Water absorbs NIR, reflects Green",
                "• Threshold: NDWI > 0.0 => Water pixel",
                "• Best for: Open lakes, rivers, ocean",
            ]
        },
        {
            "x": 385, "w": 280, "title": "PATH 2: MODIFIED NDWI (MNDWI)",
            "badge": "Xu (2006)", "badge_col": "#06B6D4",
            "formula": "MNDWI = (Green - SWIR1) / (Green + SWIR1)",
            "details": [
                "• Requires: Band 3 (Green) & Band 11 (SWIR1)",
                "• Physics: Replaces NIR to eliminate urban noise",
                "• Threshold: MNDWI > 0.0 => Water pixel",
                "• Best for: Urban floods & reservoir perimeters",
            ]
        },
        {
            "x": 735, "w": 280, "title": "PATH 3: OPTICAL RGB ABSORPTION",
            "badge": "Spectral Physics Engine", "badge_col": "#38BDF8",
            "formula": "B > 1.10·R, B >= 0.85·G, R < 85, Bright < 95",
            "details": [
                "• For: Aerial photos, Cartosat RGB, Google Earth",
                "• Turbid Water: G > 1.08·R, B >= 0.95·R",
                "• Algal Lake: ExG < 25, GLI < 0.10, local_std < 14",
                "• Cluster filter: >= 60 px (blue), >= 200 px (turbid)",
            ]
        },
        {
            "x": 1085, "w": 280, "title": "PATH 4: SAR RADAR SPECULAR",
            "badge": "Sentinel-1 VV/VH", "badge_col": "#818CF8",
            "formula": "SAR Backscatter < -18.0 dB",
            "details": [
                "• Physics: Smooth water specularly reflects radar",
                "• Low radar return to sensor antenna",
                "• Cloud Penetration: All-weather & 24/7 day/night",
                "• Critical for: Monsoon & cyclone emergency mapping",
            ]
        }
    ]

    for p in paths:
        draw_rounded_card(draw, [p["x"], 210, p["x"] + p["w"], 430], fill="#1E293B", outline=p["badge_col"], radius=6)
        draw.text((p["x"] + 12, 222), p["title"], font=f_card_t, fill="#FFFFFF")
        draw.text((p["x"] + 12, 244), p["badge"], font=f_body, fill=p["badge_col"])
        draw.rectangle([p["x"] + 10, 266, p["x"] + p["w"] - 10, 295], fill="#0F172A")
        draw.text((p["x"] + 14, 273), p["formula"], font=f_formula, fill="#38BDF8")
        y_text = 308
        for line in p["details"]:
            draw.text((p["x"] + 14, y_text), line, font=f_body, fill="#CBD5E1")
            y_text += 22

    # Converge to Post-Refinement
    for p in paths:
        draw.line([p["x"] + p["w"] / 2, 430, p["x"] + p["w"] / 2, 460], fill="#0EA5E9", width=2)
    draw.line([175, 460, 1225, 460], fill="#0EA5E9", width=2)
    draw_arrow(draw, (700, 460), (700, 490), color="#0EA5E9", width=2)

    # Post-Refinement Box
    draw_rounded_card(draw, [180, 490, 1220, 650], fill="#1E293B", outline="#F59E0B", radius=6)
    draw.text((200, 502), "PHYSICS-GUIDED REMOTE SENSING POST-REFINEMENT & ANTI-HALLUCINATION", font=f_card_t, fill="#F59E0B")

    refinements = [
        ("1. Tree Shadow Rejection", "Roughness σ >= 6.0 and green dominance G > 1.15·R reclassifies dark forest shadows to Vegetation."),
        ("2. Blue Metal Roof Rejection", "High brightness (> 125) and red reflectance (R >= 55) reclassifies blue tin factory roofs to Built-Up."),
        ("3. Wave Ripple Hole Filling", "Morphological binary hole filling (scipy.ndimage) restores unbroken lake surface topology."),
        ("4. Isolated Speckle Pruning", "Connected clusters smaller than 30 pixels are pruned, preventing noisy road artifacts."),
    ]
    for i, (rtitle, rdesc) in enumerate(refinements):
        rx = 200 + (i % 2) * 510
        ry = 535 + (i // 2) * 52
        draw.text((rx, ry), rtitle, font=f_formula, fill="#FFFFFF")
        draw.text((rx, ry + 18), rdesc, font=f_body, fill="#94A3B8")

    # Final Output Arrow
    draw_arrow(draw, (700, 650), (700, 685), color="#10B981", width=2)

    # Final Output Card
    draw_rounded_card(draw, [250, 685, 1150, 785], fill="#064E3B", outline="#10B981", radius=6)
    draw.text((270, 698), "VERIFIED WATER BODY GIS ARTIFACTS & QUANTIFICATION", font=f_card_t, fill="#A7F3D0")
    draw.text((270, 725), "• Deterministic Area Calculation: UTM zone reprojected exact metric surface area in m², hectares & km²", font=f_body, fill="#FFFFFF")
    draw.text((270, 746), "• Outputs: Cyan GeoJSON vector contours, binary raster mask, color-coded visual overlay, calibrated confidence score", font=f_body, fill="#FFFFFF")

    img.save(output_path, "PNG", quality=95)
    print(f"[OK] Water detection flowchart generated: {output_path}")


def generate_building_detection_flowchart(output_path: str):
    """Generates the specialized Building & Built-Up Detection Engine architecture flowchart."""
    w, h = 1400, 840
    img = Image.new("RGB", (w, h), color="#0B192C")
    draw = ImageDraw.Draw(img)

    f_title = get_bold_font(24)
    f_sub = get_font("segoeui", 13)
    f_card_t = get_bold_font(14)
    f_body = get_font("segoeui", 10.5)
    f_formula = get_bold_font(11.5)

    # Header
    draw.rectangle([0, 0, w, 70], fill="#08101E")
    draw.text((30, 12), "SATQUERY AI — BUILDING & BUILT-UP DETECTION ENGINE", font=f_title, fill="#F87171")
    draw.text((30, 42), "Transformer Attention, 5-Rooftop Material Taxonomy, Disambiguation & Radar Double-Bounce", font=f_sub, fill="#94A3B8")
    draw.line([0, 70, w, 70], fill="#EF4444", width=2)

    # Ingestion Stage
    draw_rounded_card(draw, [350, 90, 1050, 150], fill="#1E293B", outline="#EF4444", radius=6)
    draw.text((370, 100), "Satellite Scene Ingestion & Tiled 512x512 Preprocessing", font=f_card_t, fill="#FFFFFF")
    draw.text((370, 124), "SegFormer-B4 Hierarchical Encoder + NDBI Index + SAR Backscatter Fusion", font=f_body, fill="#94A3B8")

    # Arrow down
    draw_arrow(draw, (700, 150), (700, 185), color="#EF4444", width=2)
    draw.line([145, 185, 1255, 185], fill="#EF4444", width=2)
    for cx in [145, 425, 700, 975, 1255]:
        draw_arrow(draw, (cx, 185), (cx, 210), color="#EF4444", width=2)

    # 5 Rooftop Material Archetypes
    roofs = [
        {
            "x": 30, "w": 230, "title": "1. TERRACOTTA / CLAY",
            "badge": "Red-Orange Roofs",
            "cond": "R > 1.08·G, R > 1.18·B\nR >= 68, GLI < 0.04",
            "desc": "Traditional homes, tile roofs, historic towns",
        },
        {
            "x": 310, "w": 230, "title": "2. CONCRETE / CEMENT",
            "badge": "Masonry Slabs",
            "cond": "|R - G| <= 25, |G - B| <= 30\nBrightness 65 to 235",
            "desc": "Apartments, commercial blocks, modern houses",
        },
        {
            "x": 585, "w": 230, "title": "3. HIGH-ALBEDO WHITE",
            "badge": "Reflective Membrane",
            "cond": "Brightness >= 165\nSaturation < 0.24, GLI < 0.05",
            "desc": "White roofs, warehouses, solar/sheet zinc",
        },
        {
            "x": 860, "w": 230, "title": "4. DARK COMPOSITE",
            "badge": "Tar & Metal Roofs",
            "cond": "Brightness 42–65, Sat < 0.22\nor Blue tin: B > 1.08·R",
            "desc": "Industrial facilities, blue shed warehouses",
        },
        {
            "x": 1135, "w": 230, "title": "5. SAR RADAR BOUNCE",
            "badge": "Double-Bounce Geometry",
            "cond": "SAR Backscatter > -8.0 dB\nWall-ground corner bounce",
            "desc": "Verifies 3D vertical structures through clouds",
        }
    ]

    for r in roofs:
        draw_rounded_card(draw, [r["x"], 210, r["x"] + r["w"], 385], fill="#1E293B", outline="#F87171", radius=6)
        draw.text((r["x"] + 10, 222), r["title"], font=f_card_t, fill="#FFFFFF")
        draw.text((r["x"] + 10, 244), r["badge"], font=f_body, fill="#FCA5A5")
        draw.rectangle([r["x"] + 8, 266, r["x"] + r["w"] - 8, 320], fill="#0F172A")
        lines = r["cond"].split("\n")
        draw.text((r["x"] + 12, 274), lines[0], font=f_formula, fill="#F87171")
        if len(lines) > 1:
            draw.text((r["x"] + 12, 296), lines[1], font=f_formula, fill="#F87171")
        draw.text((r["x"] + 10, 335), r["desc"], font=f_body, fill="#CBD5E1")

    # Converge down to Disambiguation
    for r in roofs:
        draw.line([r["x"] + r["w"] / 2, 385, r["x"] + r["w"] / 2, 415], fill="#EF4444", width=2)
    draw.line([145, 415, 1255, 415], fill="#EF4444", width=2)
    draw_arrow(draw, (700, 415), (700, 445), color="#EF4444", width=2)

    # Disambiguation Card
    draw_rounded_card(draw, [100, 445, 1300, 625], fill="#1E293B", outline="#F59E0B", radius=6)
    draw.text((120, 458), "SPATIAL DISAMBIGUATION & FALSE-URBANIZATION PREVENTION ENGINE", font=f_card_t, fill="#F59E0B")

    filters = [
        ("A. Road / Transport Disambiguation", "Asphalt transit corridors (brightness 24–112, sat < 0.25, chroma < 28) evaluated FIRST to reserve Class 5 for streets."),
        ("B. Bare Soil Disambiguation", "Monotonic spectral profile (R >= 1.04·G >= 1.00·B) separated from rooftops and assigned to Class 6."),
        ("C. Rural Expanses Filter", "Massive flat patches (> 2500 px) with roughness σ < 3.5 reclassified to Agriculture or Bare Land."),
        ("D. Strong Chlorophyll Reversion", "Any roof candidate showing living green chlorophyll (GLI >= 0.12, G > 1.15·R) is reverted to Vegetation."),
    ]
    for i, (ftitle, fdesc) in enumerate(filters):
        fx = 120 + (i % 2) * 590
        fy = 490 + (i // 2) * 62
        draw.text((fx, fy), ftitle, font=f_formula, fill="#FFFFFF")
        draw.text((fx, fy + 20), fdesc, font=f_body, fill="#94A3B8")

    # Output arrow
    draw_arrow(draw, (700, 625), (700, 660), color="#10B981", width=2)

    # Final Output Card
    draw_rounded_card(draw, [250, 660, 1150, 785], fill="#064E3B", outline="#10B981", radius=6)
    draw.text((270, 675), "VERIFIED BUILT-UP INFRASTRUCTURE DELIVERABLES", font=f_card_t, fill="#A7F3D0")
    draw.text((270, 704), "• Urban Built-Up Area Quantification: Exact metric surface area in m², hectares & km² via UTM projection", font=f_body, fill="#FFFFFF")
    draw.text((270, 726), "• Structure Grounding: VRSBench bounding boxes [ymin, xmin, ymax, xmax], centroids, red overlay mask", font=f_body, fill="#FFFFFF")
    draw.text((270, 748), "• Bi-Temporal Expansion: CDVQA transition detection ('Vegetation -> Built-up Construction') with quadrant localization", font=f_body, fill="#FFFFFF")

    img.save(output_path, "PNG", quality=95)
    print(f"[OK] Building detection flowchart generated: {output_path}")


if __name__ == "__main__":
    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(exist_ok=True)

    f1 = str(docs_dir / "system_architecture_diagram.png")
    f2 = str(docs_dir / "water_detection_flowchart.png")
    f3 = str(docs_dir / "building_detection_flowchart.png")

    generate_system_architecture_diagram(f1)
    generate_water_detection_flowchart(f2)
    generate_building_detection_flowchart(f3)
    print("[SUCCESS] All 3 architectural diagram images generated in docs/")
