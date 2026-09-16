"""
SATQuery AI - Professional SIH 2026 Presentation Generator (Finalist/Winning Level)
Problem Statement ID: 26167
Theme: Space Technology | Organization: ISRO
Produces SATQuery_AI_SIH_2026.pptx with high-density visual storytelling, icons, diagrams, and clean layout.
"""
import os
import sys
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Color Palette ──────────────────────────────────────────────────────────
C_BG = RGBColor(247, 249, 248)             # #F7F9F8 Light Scientific Off-White
C_PRIMARY = RGBColor(18, 59, 93)           # #123B5D Deep Space Blue
C_SECONDARY = RGBColor(20, 138, 131)       # #148A83 Earth Observation Teal
C_GREEN = RGBColor(61, 155, 101)          # #3D9B65 Earth Green
C_ORANGE = RGBColor(233, 138, 58)         # #E98A3A Satellite Orange
C_PURPLE = RGBColor(110, 69, 184)         # #6E45B8 Royal Violet
C_RED = RGBColor(217, 83, 79)             # #D9534F Alert Red
C_TEXT = RGBColor(23, 32, 39)              # #172027 Dark Body Text
C_MUTED = RGBColor(100, 114, 124)          # #64727C Slate Gray Muted
C_WHITE = RGBColor(255, 255, 255)          # Pure White
C_BORDER = RGBColor(221, 227, 234)         # Crisp Border
C_LIGHT_BLUE = RGBColor(240, 244, 248)     # Soft Blue Tint
C_LIGHT_TEAL = RGBColor(237, 247, 246)     # Soft Teal Tint
C_LIGHT_ORANGE = RGBColor(254, 246, 238)   # Soft Orange Tint
C_LIGHT_GREEN = RGBColor(238, 248, 242)    # Soft Green Tint

FONT_NAME = "Segoe UI"
FONT_BODY = "Segoe UI"
C_TEAL = C_SECONDARY
C_BLUE = C_PRIMARY

# Asset Paths
BASE_ARTIFACTS = Path(r"C:\Users\mohan\.gemini\antigravity-ide\brain\0062e810-5cf3-4e21-9c25-09b5639698af")
IMG_REYKJAVIK = BASE_ARTIFACTS / "reykjavik_search_result_1789054613590.png"
IMG_VISION = BASE_ARTIFACTS / "captured_aoi_vision_layout_1789052845241.png"
IMG_OBSERVATION = BASE_ARTIFACTS / "analysis_observation_card_1789052888357.png"
IMG_DASHBOARD = BASE_ARTIFACTS / "dashboard_overview_1789053607094.png"
IMG_BUILTUP = BASE_ARTIFACTS / "builtup_class_highlight_overlay_1789052980186.png"
IMG_SLIDE3 = Path("scratch/ppt_assets/slide3_analysis_clean.png")

SIH_BADGE = Path("scratch/ppt_assets/sih_badge.png")
ICON_DIR = Path("scratch/ppt_assets/icons")


def init_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_icon(slide, icon_name, left, top, size=Inches(0.42)):
    """Embed circular Lucide-style icon."""
    p = ICON_DIR / f"{icon_name}.png"
    if p.exists():
        return slide.shapes.add_picture(str(p), left, top, size, size)
    return None


def add_slide_header(slide, title_text, slide_number=2):
    """
    Winning-grade header:
    - Top Left: Team SATQuery badge
    - Center/Left: Large bold modern title
    - Top Right: Official SIH 2026 badge
    - Bottom: Subtle consistent footer
    """
    # Top-Left Team Pill
    team_pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.2), Inches(1.8), Inches(0.45)
    )
    team_pill.fill.solid()
    team_pill.fill.fore_color.rgb = C_WHITE
    team_pill.line.color.rgb = C_PRIMARY
    team_pill.line.width = Pt(1.5)
    tf_team = team_pill.text_frame
    p_team = tf_team.paragraphs[0]
    p_team.alignment = PP_ALIGN.CENTER
    p_team.text = "Team SATQuery"
    p_team.font.name = FONT_NAME
    p_team.font.size = Pt(9.5)
    p_team.font.bold = True
    p_team.font.color.rgb = C_PRIMARY

    # Main Title
    tb_title = slide.shapes.add_textbox(Inches(2.6), Inches(0.18), Inches(8.0), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = C_PRIMARY

    # Top-Right SIH Badge
    if SIH_BADGE.exists():
        slide.shapes.add_picture(str(SIH_BADGE), Inches(10.8), Inches(0.12), Inches(2.1), Inches(0.74))

    # Subtle consistent footer
    tb_foot = slide.shapes.add_textbox(Inches(0.6), Inches(7.15), Inches(10.5), Inches(0.28))
    p_f = tb_foot.text_frame.paragraphs[0]
    p_f.text = "SATQUERY AI  •  SIH 2026  •  PS 26167  •  ISRO  •  SPACE TECHNOLOGY"
    p_f.font.name = FONT_NAME
    p_f.font.size = Pt(8.5)
    p_f.font.color.rgb = C_MUTED

    tb_num = slide.shapes.add_textbox(Inches(12.2), Inches(7.15), Inches(0.6), Inches(0.28))
    p_num = tb_num.text_frame.paragraphs[0]
    p_num.alignment = PP_ALIGN.RIGHT
    p_num.text = str(slide_number)
    p_num.font.name = FONT_NAME
    p_num.font.bold = True
    p_num.font.size = Pt(9.5)
    p_num.font.color.rgb = C_PRIMARY


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1: TITLE PAGE
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_1(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()

    # Header Strip
    hdr_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.95))
    hdr_box.fill.solid()
    hdr_box.fill.fore_color.rgb = C_WHITE
    hdr_box.line.color.rgb = C_BORDER
    hdr_box.line.width = Pt(1)

    # Accent Top Line
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.08))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_SECONDARY
    top_bar.line.fill.background()

    # Header Title
    tb_h = slide.shapes.add_textbox(Inches(0.8), Inches(0.18), Inches(9.5), Inches(0.65))
    tf_h = tb_h.text_frame
    p_h = tf_h.paragraphs[0]
    p_h.text = "SMART INDIA HACKATHON 2026"
    p_h.font.name = FONT_NAME
    p_h.font.size = Pt(18)
    p_h.font.bold = True
    p_h.font.color.rgb = C_PRIMARY

    p_sub = tf_h.add_paragraph()
    p_sub.text = "ISRO · DEPARTMENT OF SPACE · THEME: SPACE TECHNOLOGY · SOFTWARE EDITION"
    p_sub.font.name = FONT_NAME
    p_sub.font.size = Pt(9)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_SECONDARY

    if SIH_BADGE.exists():
        slide.shapes.add_picture(str(SIH_BADGE), Inches(10.6), Inches(0.12), Inches(2.2), Inches(0.74))

    # LEFT COLUMN: Main Title, Subtitle, Badges & Official Metadata
    # Big Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(6.8), Inches(1.5))
    tf_t = tb_title.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = "SATQUERY AI"
    p_t.font.name = FONT_NAME
    p_t.font.size = Pt(36)
    p_t.font.bold = True
    p_t.font.color.rgb = C_PRIMARY

    p_st = tf_t.add_paragraph()
    p_st.text = "An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries"
    p_st.font.name = FONT_NAME
    p_st.font.size = Pt(12)
    p_st.font.bold = True
    p_st.font.color.rgb = C_SECONDARY
    p_st.space_before = Pt(4)

    # 3 Small Feature Badges
    badges = [
        ("NATURAL-LANGUAGE QUERY", C_PRIMARY, C_LIGHT_BLUE),
        ("MULTIMODAL ANALYSIS", C_SECONDARY, C_LIGHT_TEAL),
        ("AGENTIC AI ORCHESTRATION", C_GREEN, C_LIGHT_GREEN),
    ]
    b_x = Inches(0.8)
    for b_text, b_col, b_bg in badges:
        b_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, b_x, Inches(2.82), Inches(2.0), Inches(0.36))
        b_box.fill.solid()
        b_box.fill.fore_color.rgb = b_bg
        b_box.line.color.rgb = b_col
        b_box.line.width = Pt(1)
        tf_b = b_box.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.alignment = PP_ALIGN.CENTER
        p_b.text = b_text
        p_b.font.name = FONT_NAME
        p_b.font.bold = True
        p_b.font.size = Pt(7.5)
        p_b.font.color.rgb = b_col
        b_x += Inches(2.1)

    # Official Credentials Card
    card_meta = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.32), Inches(6.1), Inches(3.2))
    card_meta.fill.solid()
    card_meta.fill.fore_color.rgb = C_WHITE
    card_meta.line.color.rgb = C_BORDER
    card_meta.line.width = Pt(1)

    tb_meta = slide.shapes.add_textbox(Inches(0.95), Inches(3.45), Inches(5.8), Inches(3.0))
    tf_m = tb_meta.text_frame
    tf_m.word_wrap = True

    creds = [
        ("Problem Statement ID:", "26167"),
        ("Problem Statement Title:", "SatQuery AI - An Interactive Vision-Language Assistant for Multimodal Remote Sensing Image Analysis through Text Queries"),
        ("Organization:", "Indian Space Research Organisation (ISRO)"),
        ("Department:", "Department of Space / Indian Space Research Organisation"),
        ("Theme & Category:", "Space Technology · Software"),
        ("Team Name & ID:", "Team SATQuery · SIH2026-26167"),
    ]
    for idx, (label, val) in enumerate(creds):
        p = tf_m.paragraphs[0] if idx == 0 else tf_m.add_paragraph()
        p.space_before = Pt(4) if idx > 0 else Pt(0)
        r1 = p.add_run()
        r1.text = f"{label} "
        r1.font.name = FONT_NAME
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = C_PRIMARY

        r2 = p.add_run()
        r2.text = val
        r2.font.name = FONT_NAME
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_TEXT

    # RIGHT COLUMN: Subtle Earth Observation Composition
    # SATELLITE ➔ EARTH RASTERS ➔ MULTIMODAL VLM ➔ VISUAL EVIDENCE
    card_e = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.15), Inches(5.4), Inches(5.37))
    card_e.fill.solid()
    card_e.fill.fore_color.rgb = C_WHITE
    card_e.line.color.rgb = C_BORDER
    card_e.line.width = Pt(1)

    # Actual Application Screenshot
    if IMG_REYKJAVIK.exists():
        slide.shapes.add_picture(str(IMG_REYKJAVIK), Inches(7.35), Inches(1.3), Inches(5.1), Inches(2.75))

    # Flow Banner inside right card
    add_icon(slide, "ico_sat", Inches(7.5), Inches(4.2), size=Inches(0.44))
    add_icon(slide, "ico_layers", Inches(8.75), Inches(4.2), size=Inches(0.44))
    add_icon(slide, "ico_brain", Inches(10.0), Inches(4.2), size=Inches(0.44))
    add_icon(slide, "ico_eye", Inches(11.25), Inches(4.2), size=Inches(0.44))

    # Flow arrows
    for arr_x in [Inches(8.35), Inches(9.6), Inches(10.85)]:
        tb_arr = slide.shapes.add_textbox(arr_x, Inches(4.22), Inches(0.3), Inches(0.4))
        p_a = tb_arr.text_frame.paragraphs[0]
        p_a.text = "➔"
        p_a.font.bold = True
        p_a.font.size = Pt(13)
        p_a.font.color.rgb = C_SECONDARY

    flow_lbls = [
        ("SATELLITE", Inches(7.25)),
        ("EARTH RASTER", Inches(8.5)),
        ("MULTIMODAL AI", Inches(9.75)),
        ("EVIDENCE", Inches(11.0))
    ]
    for lbl, lx in flow_lbls:
        tb_l = slide.shapes.add_textbox(lx, Inches(4.7), Inches(0.95), Inches(0.3))
        p_l = tb_l.text_frame.paragraphs[0]
        p_l.alignment = PP_ALIGN.CENTER
        p_l.text = lbl
        p_l.font.name = FONT_NAME
        p_l.font.bold = True
        p_l.font.size = Pt(7.5)
        p_l.font.color.rgb = C_MUTED

    # Bottom Callout in card
    call_strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.35), Inches(5.15), Inches(5.1), Inches(1.15))
    call_strip.fill.solid()
    call_strip.fill.fore_color.rgb = C_LIGHT_TEAL
    call_strip.line.color.rgb = C_SECONDARY
    call_strip.line.width = Pt(1)
    tf_cs = call_strip.text_frame
    tf_cs.word_wrap = True
    p_cs = tf_cs.paragraphs[0]
    p_cs.alignment = PP_ALIGN.CENTER
    r_cs1 = p_cs.add_run()
    r_cs1.text = "“From Satellite Data → Intelligent Evidence”\n"
    r_cs1.font.name = FONT_NAME
    r_cs1.font.bold = True
    r_cs1.font.size = Pt(10.5)
    r_cs1.font.color.rgb = C_SECONDARY

    r_cs2 = p_cs.add_run()
    r_cs2.text = "Verified Production System · SegFormer · BLIP-2 · CDVQA · Optical + SAR Fusion"
    r_cs2.font.name = FONT_NAME
    r_cs2.font.size = Pt(8.5)
    r_cs2.font.color.rgb = C_TEXT

    # Bottom subtle footer
    tb_foot = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.7), Inches(0.28))
    p_f = tb_foot.text_frame.paragraphs[0]
    p_f.text = "SATQUERY AI  •  SIH 2026  •  PS 26167  •  ISRO  •  SPACE TECHNOLOGY"
    p_f.font.name = FONT_NAME
    p_f.font.size = Pt(8.5)
    p_f.font.color.rgb = C_MUTED


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2: THE PROBLEM → OUR SOLUTION → WHAT MAKES IT DIFFERENT
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_2(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, "SATQUERY AI — FROM COMPLEX GIS TO NATURAL-LANGUAGE AI", slide_number=2)

    # ── 1. TOP: THE PROBLEM (3 Problem Cards) ──
    y_prob = Inches(1.1)
    h_prob = Inches(1.5)
    w_prob = Inches(3.85)
    gap_p = Inches(0.24)

    prob_data = [
        ("ico_layers", "FRAGMENTED TOOLS", "Isolated specialist workflows", "Land cover, change detection, VQA & SAR are siloed in disparate software."),
        ("ico_settings", "EXPERT DEPENDENCY", "High technical barrier", "Requires manual parameter tuning: bands, radiometric calibration & CRS transforms."),
        ("ico_sat", "MULTIMODAL COMPLEXITY", "Data integration disconnect", "Single optical images fail in clouds; optical, SAR & temporal passes remain uncoupled.")
    ]

    for idx, (icon_name, title, sub, desc) in enumerate(prob_data):
        cur_x = Inches(0.6) + idx * (w_prob + gap_p)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_prob, w_prob, h_prob)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_BORDER
        card.line.width = Pt(1)

        add_icon(slide, icon_name, cur_x + Inches(0.14), y_prob + Inches(0.16), size=Inches(0.42))

        tb = slide.shapes.add_textbox(cur_x + Inches(0.64), y_prob + Inches(0.1), w_prob - Inches(0.74), h_prob - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME
        p_t.font.bold = True
        p_t.font.size = Pt(10)
        p_t.font.color.rgb = C_PRIMARY

        p_s = tf.add_paragraph()
        p_s.text = sub
        p_s.font.name = FONT_NAME
        p_s.font.bold = True
        p_s.font.size = Pt(8)
        p_s.font.color.rgb = C_ORANGE

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(7.5)
        p_d.font.color.rgb = C_TEXT

    # ── 2. MIDDLE: CENTRAL WORKFLOW & SCREENSHOT ──
    card_mid = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(2.75), Inches(12.133), Inches(2.65))
    card_mid.fill.solid()
    card_mid.fill.fore_color.rgb = C_WHITE
    card_mid.line.color.rgb = C_SECONDARY
    card_mid.line.width = Pt(1.5)

    # Left: Process Workflow Diagram
    flow_steps = [
        ("USER QUESTION", '“What changed between\nthese two passes?”', C_PRIMARY),
        ("AGENTIC CONTROLLER", "Autonomous intent &\ntask classification", C_SECONDARY),
        ("SPECIALIST AI", "SegFormer · CDVQA\nOptical + SAR Fusion", C_TEAL),
        ("EVIDENCE OUTPUT", "Pixel Masks · Hectares\nConfidence & Audit Trace", C_GREEN),
    ]

    x_flow = Inches(0.85)
    f_box_w = Inches(1.55)
    f_gap = Inches(0.22)
    y_f = Inches(3.05)

    for idx, (f_title, f_sub, f_col) in enumerate(flow_steps):
        cur_x = x_flow + idx * (f_box_w + f_gap)
        fb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_f, f_box_w, Inches(1.95))
        fb.fill.solid()
        fb.fill.fore_color.rgb = C_LIGHT_BLUE if idx == 0 else (C_LIGHT_TEAL if idx in [1, 2] else C_LIGHT_GREEN)
        fb.line.color.rgb = f_col
        fb.line.width = Pt(1)

        tb_fb = slide.shapes.add_textbox(cur_x + Inches(0.08), y_f + Inches(0.12), f_box_w - Inches(0.16), Inches(1.7))
        tf_fb = tb_fb.text_frame
        tf_fb.word_wrap = True
        p_ft = tf_fb.paragraphs[0]
        p_ft.alignment = PP_ALIGN.CENTER
        p_ft.text = f_title
        p_ft.font.name = FONT_NAME
        p_ft.font.bold = True
        p_ft.font.size = Pt(8.5)
        p_ft.font.color.rgb = f_col

        p_fs = tf_fb.add_paragraph()
        p_fs.alignment = PP_ALIGN.CENTER
        p_fs.text = f_sub
        p_fs.font.name = FONT_BODY
        p_fs.font.size = Pt(7.5)
        p_fs.font.color.rgb = C_TEXT
        p_fs.space_before = Pt(8)

        if idx < len(flow_steps) - 1:
            arr = slide.shapes.add_textbox(cur_x + f_box_w, y_f + Inches(0.7), f_gap, Inches(0.4))
            p_a = arr.text_frame.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            p_a.text = "➔"
            p_a.font.bold = True
            p_a.font.size = Pt(13)
            p_a.font.color.rgb = C_SECONDARY

    # Right: Real Application Screenshot
    if IMG_OBSERVATION.exists():
        slide.shapes.add_picture(str(IMG_OBSERVATION), Inches(7.8), Inches(2.9), Inches(4.75), Inches(2.35))

    # ── 3. BOTTOM: 4 SOLUTION PILLARS ──
    sol_cards = [
        ("01", "NATURAL LANGUAGE", "Plain text query replacing GIS commands", C_PRIMARY),
        ("02", "AGENTIC ROUTING", "Autonomous model and tool selection", C_SECONDARY),
        ("03", "OPTICAL + SAR FUSION", "Multi-sensor day/night & cloud penetration", C_TEAL),
        ("04", "BI-TEMPORAL REASONING", "Quantitative transition matrices & CDVQA", C_GREEN),
    ]

    w_sol = Inches(2.85)
    gap_s = Inches(0.24)
    y_sol = Inches(5.55)

    for idx, (num, title, desc, col) in enumerate(sol_cards):
        cur_x = Inches(0.6) + idx * (w_sol + gap_s)
        sc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_sol, w_sol, Inches(0.85))
        sc.fill.solid()
        sc.fill.fore_color.rgb = C_WHITE
        sc.line.color.rgb = col
        sc.line.width = Pt(1.5)

        # Number pill
        npill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x + Inches(0.1), y_sol + Inches(0.12), Inches(0.45), Inches(0.35))
        npill.fill.solid()
        npill.fill.fore_color.rgb = col
        npill.line.fill.background()
        p_np = npill.text_frame.paragraphs[0]
        p_np.alignment = PP_ALIGN.CENTER
        p_np.text = num
        p_np.font.name = FONT_NAME
        p_np.font.bold = True
        p_np.font.size = Pt(9)
        p_np.font.color.rgb = C_WHITE

        tb_sc = slide.shapes.add_textbox(cur_x + Inches(0.6), y_sol + Inches(0.06), w_sol - Inches(0.65), Inches(0.75))
        tf_sc = tb_sc.text_frame
        tf_sc.word_wrap = True
        p_sct = tf_sc.paragraphs[0]
        p_sct.text = title
        p_sct.font.name = FONT_NAME
        p_sct.font.bold = True
        p_sct.font.size = Pt(8.5)
        p_sct.font.color.rgb = col

        p_scd = tf_sc.add_paragraph()
        p_scd.text = desc
        p_scd.font.name = FONT_BODY
        p_scd.font.size = Pt(7.5)
        p_scd.font.color.rgb = C_TEXT

    # Bottom Why SATQuery Statement
    card_why = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.5), Inches(12.133), Inches(0.55))
    card_why.fill.solid()
    card_why.fill.fore_color.rgb = C_PRIMARY
    card_why.line.color.rgb = C_SECONDARY
    card_why.line.width = Pt(1.5)

    tb_w = slide.shapes.add_textbox(Inches(0.8), Inches(6.52), Inches(11.7), Inches(0.45))
    p_w = tb_w.text_frame.paragraphs[0]
    p_w.alignment = PP_ALIGN.CENTER
    r_w1 = p_w.add_run()
    r_w1.text = "WHY SATQUERY?  "
    r_w1.font.name = FONT_NAME
    r_w1.font.bold = True
    r_w1.font.size = Pt(10)
    r_w1.font.color.rgb = C_ORANGE

    r_w2 = p_w.add_run()
    r_w2.text = '“One interface. Multiple specialist models. Evidence-grounded answers.”'
    r_w2.font.name = FONT_NAME
    r_w2.font.bold = True
    r_w2.font.size = Pt(10)
    r_w2.font.color.rgb = C_WHITE


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3: HOW SATQUERY AI WORKS (Most Visual Architecture Slide)
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_3(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, "HOW SATQUERY AI WORKS", slide_number=3)

    # ── 1. TOP HORIZONTAL ARCHITECTURE PIPELINE (7 Stages with Large Icons) ──
    pipeline = [
        ("01", "ico_sat", "SATELLITE INPUT", "GeoTIFF · Sentinel-1/2\nMulti-Band Imagery"),
        ("02", "ico_msg", "QUERY PARSING", "Intent classification\nTask identification"),
        ("03", "ico_shield", "INPUT VALIDATION", "CRS · Resolution\nIoU Bounding Box"),
        ("04", "ico_net", "AGENTIC ROUTER", "Specialist selection\nWorkflow planning"),
        ("05", "ico_brain", "SPECIALIST AI", "SegFormer · BLIP-2\nCDVQA · Optical-SAR"),
        ("06", "ico_eye", "EVIDENCE GEN", "Pixel masks · NDVI\nConfidence metric"),
        ("07", "ico_doc", "ACTIONABLE OUTPUT", "PDF / HTML Report\nStepTracker audit"),
    ]

    x_pipe = Inches(0.6)
    p_card_w = Inches(1.52)
    p_gap = Inches(0.24)
    y_pipe = Inches(1.1)

    for idx, (num, icon_name, title, desc) in enumerate(pipeline):
        cur_x = x_pipe + idx * (p_card_w + p_gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_pipe, p_card_w, Inches(1.75))
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = C_PRIMARY if idx % 2 == 0 else C_SECONDARY
        card.line.width = Pt(1.2)

        # Stage Number
        num_lbl = slide.shapes.add_textbox(cur_x, y_pipe + Inches(0.04), p_card_w, Inches(0.25))
        p_n = num_lbl.text_frame.paragraphs[0]
        p_n.alignment = PP_ALIGN.CENTER
        p_n.text = num
        p_n.font.name = FONT_NAME
        p_n.font.bold = True
        p_n.font.size = Pt(8.5)
        p_n.font.color.rgb = C_MUTED

        # Icon
        add_icon(slide, icon_name, cur_x + Inches(0.53), y_pipe + Inches(0.28), size=Inches(0.44))

        # Title & Desc
        tb_c = slide.shapes.add_textbox(cur_x + Inches(0.05), y_pipe + Inches(0.76), p_card_w - Inches(0.1), Inches(0.95))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        p_ct = tf_c.paragraphs[0]
        p_ct.alignment = PP_ALIGN.CENTER
        p_ct.text = title
        p_ct.font.name = FONT_NAME
        p_ct.font.bold = True
        p_ct.font.size = Pt(7.5)
        p_ct.font.color.rgb = C_PRIMARY

        p_cd = tf_c.add_paragraph()
        p_cd.alignment = PP_ALIGN.CENTER
        p_cd.text = desc
        p_cd.font.name = FONT_BODY
        p_cd.font.size = Pt(6.5)
        p_cd.font.color.rgb = C_TEXT

        # Pipeline Arrow
        if idx < len(pipeline) - 1:
            arr = slide.shapes.add_textbox(cur_x + p_card_w, y_pipe + Inches(0.6), p_gap, Inches(0.4))
            p_a = arr.text_frame.paragraphs[0]
            p_a.alignment = PP_ALIGN.CENTER
            p_a.text = "➔"
            p_a.font.bold = True
            p_a.font.size = Pt(11)
            p_a.font.color.rgb = C_SECONDARY

    # ── 2. SPECIALIST AI BRANCHING DIAGRAM (Left Middle) ──
    card_branch = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(2.95), Inches(5.8), Inches(4.0))
    card_branch.fill.solid()
    card_branch.fill.fore_color.rgb = C_WHITE
    card_branch.line.color.rgb = C_PRIMARY
    card_branch.line.width = Pt(1.5)

    # Controller Root
    ctrl_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.7), Inches(3.1), Inches(3.6), Inches(0.55))
    ctrl_box.fill.solid()
    ctrl_box.fill.fore_color.rgb = C_PRIMARY
    ctrl_box.line.fill.background()
    p_ctrl = ctrl_box.text_frame.paragraphs[0]
    p_ctrl.alignment = PP_ALIGN.CENTER
    p_ctrl.text = "AGENTIC CONTROLLER & TASK ROUTING"
    p_ctrl.font.name = FONT_NAME
    p_ctrl.font.bold = True
    p_ctrl.font.size = Pt(9.5)
    p_ctrl.font.color.rgb = C_WHITE

    # 3 Branches
    branches = [
        ("SINGLE IMAGE", "ico_eye", "VQA · CAPTION · GROUNDING", "• RSVQA high-res adapter\n• BLIP-2 scene captioner\n• SegFormer-B0 land-cover", C_BLUE, C_LIGHT_BLUE),
        ("BI-TEMPORAL", "ico_layers", "CHANGE AI & TRANSITIONS", "• CDVQA change VQA engine\n• LEVIR-CD transition matrix\n• Hectare / km² delta metrics", C_TEAL, C_LIGHT_TEAL),
        ("OPTICAL + SAR", "ico_radar", "CROSS-MODAL FUSION", "• Sentinel-1 SAR (VV/VH)\n• Sentinel-2 MSI optical bands\n• Cloud penetration consensus", C_GREEN, C_LIGHT_GREEN),
    ]

    y_br = Inches(3.85)
    b_w = Inches(1.7)
    b_gap = Inches(0.18)

    for idx, (b_name, b_ico, b_spec, b_pts, b_col, b_bg) in enumerate(branches):
        cur_x = Inches(0.75) + idx * (b_w + b_gap)
        bbox = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_br, b_w, Inches(2.95))
        bbox.fill.solid()
        bbox.fill.fore_color.rgb = b_bg
        bbox.line.color.rgb = b_col
        bbox.line.width = Pt(1)

        # Header Pill
        hp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x + Inches(0.08), y_br + Inches(0.1), b_w - Inches(0.16), Inches(0.35))
        hp.fill.solid()
        hp.fill.fore_color.rgb = b_col
        hp.line.fill.background()
        p_hp = hp.text_frame.paragraphs[0]
        p_hp.alignment = PP_ALIGN.CENTER
        p_hp.text = b_name
        p_hp.font.name = FONT_NAME
        p_hp.font.bold = True
        p_hp.font.size = Pt(8)
        p_hp.font.color.rgb = C_WHITE

        # Icon
        add_icon(slide, b_ico, cur_x + Inches(0.63), y_br + Inches(0.55), size=Inches(0.42))

        # Title
        tb_bt = slide.shapes.add_textbox(cur_x + Inches(0.05), y_br + Inches(1.02), b_w - Inches(0.1), Inches(0.5))
        tf_bt = tb_bt.text_frame
        tf_bt.word_wrap = True
        p_bt = tf_bt.paragraphs[0]
        p_bt.alignment = PP_ALIGN.CENTER
        p_bt.text = b_spec
        p_bt.font.name = FONT_NAME
        p_bt.font.bold = True
        p_bt.font.size = Pt(7.5)
        p_bt.font.color.rgb = b_col

        # Bullets
        tb_bp = slide.shapes.add_textbox(cur_x + Inches(0.06), y_br + Inches(1.55), b_w - Inches(0.12), Inches(1.3))
        tf_bp = tb_bp.text_frame
        tf_bp.word_wrap = True
        p_bp = tf_bp.paragraphs[0]
        p_bp.text = b_pts
        p_bp.font.name = FONT_BODY
        p_bp.font.size = Pt(7)
        p_bp.font.color.rgb = C_TEXT

    # ── 3. REAL APPLICATION SCREENSHOT WITH CALLOUT LABELS (Right Side) ──
    card_ui = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.6), Inches(2.95), Inches(6.133), Inches(4.0))
    card_ui.fill.solid()
    card_ui.fill.fore_color.rgb = C_WHITE
    card_ui.line.color.rgb = C_BORDER
    card_ui.line.width = Pt(1)

    src_img = IMG_SLIDE3 if IMG_SLIDE3.exists() else IMG_VISION
    if src_img.exists():
        slide.shapes.add_picture(str(src_img), Inches(6.75), Inches(3.08), Inches(5.83), Inches(2.85))

    # Callout Labels below screenshot
    callouts = [
        ("① Natural Language Query", C_PRIMARY),
        ("② Model Selection", C_SECONDARY),
        ("③ Visual Evidence Overlay", C_GREEN),
        ("④ Confidence Metric", C_ORANGE),
        ("⑤ Execution Trace", C_PURPLE),
    ]

    c_x = Inches(6.75)
    c_w = Inches(1.1)
    for c_lbl, c_col in callouts:
        c_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_x, Inches(6.05), c_w, Inches(0.72))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = C_LIGHT_BLUE
        c_box.line.color.rgb = c_col
        c_box.line.width = Pt(1)
        tf_cb = c_box.text_frame
        tf_cb.word_wrap = True
        p_cb = tf_cb.paragraphs[0]
        p_cb.alignment = PP_ALIGN.CENTER
        p_cb.text = c_lbl
        p_cb.font.name = FONT_NAME
        p_cb.font.bold = True
        p_cb.font.size = Pt(7.5)
        p_cb.font.color.rgb = c_col
        c_x += Inches(1.18)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4: FEASIBILITY & VIABILITY
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_4(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, "FEASIBILITY & VIABILITY", slide_number=4)

    col_w = Inches(3.85)
    gap = Inches(0.24)
    y_top = Inches(1.15)
    h_col = Inches(5.15)

    # ── Column 1: Technically Feasible ──
    pill_1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), y_top, col_w, Inches(0.42))
    pill_1.fill.solid()
    pill_1.fill.fore_color.rgb = C_PRIMARY
    pill_1.line.fill.background()
    p_p1 = pill_1.text_frame.paragraphs[0]
    p_p1.alignment = PP_ALIGN.CENTER
    p_p1.text = "TECHNICALLY FEASIBLE"
    p_p1.font.name = FONT_NAME
    p_p1.font.bold = True
    p_p1.font.size = Pt(10.5)
    p_p1.font.color.rgb = C_WHITE

    card_1 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), y_top + Inches(0.48), col_w, h_col - Inches(0.48))
    card_1.fill.solid()
    card_1.fill.fore_color.rgb = C_WHITE
    card_1.line.color.rgb = C_BORDER
    card_1.line.width = Pt(1)

    f_cards = [
        ("ico_code", "Open Geospatial Stack", "Rasterio, GDAL, EPSG:3857/4326 affine coordinate transforms."),
        ("ico_db", "Open Satellite Datasets", "Sentinel-1/2 (Copernicus), Landsat-8/9, LandCover.ai benchmarks."),
        ("ico_brain", "Specialist AI Models", "SegFormer-B0, CDVQA, BLIP-2 with remote-sensing domain adapters."),
        ("ico_globe", "Web-Based Deployment", "FastAPI async pipeline + React Leaflet hardware-accelerated viewer.")
    ]
    y_item = y_top + Inches(0.6)
    for icon_name, title, desc in f_cards:
        add_icon(slide, icon_name, Inches(0.78), y_item, size=Inches(0.42))
        tb = slide.shapes.add_textbox(Inches(1.28), y_item - Inches(0.04), col_w - Inches(0.75), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME
        p_t.font.bold = True
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = C_PRIMARY

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(8)
        p_d.font.color.rgb = C_TEXT
        y_item += Inches(1.1)

    # ── Column 2: Challenges ──
    x_col2 = Inches(0.6) + col_w + gap
    pill_2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_col2, y_top, col_w, Inches(0.42))
    pill_2.fill.solid()
    pill_2.fill.fore_color.rgb = C_ORANGE
    pill_2.line.fill.background()
    p_p2 = pill_2.text_frame.paragraphs[0]
    p_p2.alignment = PP_ALIGN.CENTER
    p_p2.text = "POTENTIAL CHALLENGES"
    p_p2.font.name = FONT_NAME
    p_p2.font.bold = True
    p_p2.font.size = Pt(10.5)
    p_p2.font.color.rgb = C_WHITE

    card_2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_col2, y_top + Inches(0.48), col_w, h_col - Inches(0.48))
    card_2.fill.solid()
    card_2.fill.fore_color.rgb = C_WHITE
    card_2.line.color.rgb = C_BORDER
    card_2.line.width = Pt(1)

    c_cards = [
        ("ico_cloud_rain", "Optical Image Quality", "Cloud occlusion, atmospheric haze, and night-time optical blindness."),
        ("ico_layers", "Optical-SAR Alignment", "Disparate sensor grids, spatial resolutions, and vantage angles."),
        ("ico_cpu", "Large-Image Computation", "Multi-gigabyte GeoTIFF rasters strain memory and inference latency."),
        ("ico_lock_shield", "AI Reliability & Trust", "Generic VLMs can hallucinate without spatial grounding verification.")
    ]
    y_item = y_top + Inches(0.6)
    for icon_name, title, desc in c_cards:
        add_icon(slide, icon_name, x_col2 + Inches(0.18), y_item, size=Inches(0.42))
        tb = slide.shapes.add_textbox(x_col2 + Inches(0.68), y_item - Inches(0.04), col_w - Inches(0.75), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME
        p_t.font.bold = True
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = C_ORANGE

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(8)
        p_d.font.color.rgb = C_TEXT
        y_item += Inches(1.1)

    # ── Column 3: Mitigation ──
    x_col3 = Inches(0.6) + (col_w + gap) * 2
    pill_3 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_col3, y_top, col_w, Inches(0.42))
    pill_3.fill.solid()
    pill_3.fill.fore_color.rgb = C_GREEN
    pill_3.line.fill.background()
    p_p3 = pill_3.text_frame.paragraphs[0]
    p_p3.alignment = PP_ALIGN.CENTER
    p_p3.text = "MITIGATION STRATEGIES"
    p_p3.font.name = FONT_NAME
    p_p3.font.bold = True
    p_p3.font.size = Pt(10.5)
    p_p3.font.color.rgb = C_WHITE

    card_3 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_col3, y_top + Inches(0.48), col_w, h_col - Inches(0.48))
    card_3.fill.solid()
    card_3.fill.fore_color.rgb = C_WHITE
    card_3.line.color.rgb = C_BORDER
    card_3.line.width = Pt(1)

    m_cards = [
        ("ico_radar", "Complementary SAR Fusion", "SAR microwaves penetrate clouds and operate day/night unconditionally."),
        ("ico_check", "Validate Spatial Compatibility", "InputValidator verifies CRS & IoU bounding box overlap before inference."),
        ("ico_layers", "Tiling & Patch Processing", "Sub-region patch extraction (512x512) and pyramid tiling prevent OOM."),
        ("ico_eye", "Evidence-Grounded Output", "Every response is tethered to pixel masks, spectral indices, & confidence.")
    ]
    y_item = y_top + Inches(0.6)
    for icon_name, title, desc in m_cards:
        add_icon(slide, icon_name, x_col3 + Inches(0.18), y_item, size=Inches(0.42))
        tb = slide.shapes.add_textbox(x_col3 + Inches(0.68), y_item - Inches(0.04), col_w - Inches(0.75), Inches(0.95))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_NAME
        p_t.font.bold = True
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = C_GREEN

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(8)
        p_d.font.color.rgb = C_TEXT
        y_item += Inches(1.1)

    # ── Bottom Visual Statement: BUILDABLE + SCALABLE + AUDITABLE ──
    goal_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.45), Inches(12.133), Inches(0.62))
    goal_card.fill.solid()
    goal_card.fill.fore_color.rgb = C_PRIMARY
    goal_card.line.color.rgb = C_SECONDARY
    goal_card.line.width = Pt(1.5)

    add_icon(slide, "ico_target", Inches(0.8), Inches(6.52), size=Inches(0.46))

    tb_goal = slide.shapes.add_textbox(Inches(1.35), Inches(6.5), Inches(11.2), Inches(0.5))
    tf_g = tb_goal.text_frame
    p_g = tf_g.paragraphs[0]
    r_g1 = p_g.add_run()
    r_g1.text = "BUILDABLE + SCALABLE + AUDITABLE:  "
    r_g1.font.name = FONT_NAME
    r_g1.font.bold = True
    r_g1.font.size = Pt(10.5)
    r_g1.font.color.rgb = C_ORANGE

    r_g2 = p_g.add_run()
    r_g2.text = '“Make complex multimodal satellite analysis accessible through one intelligent interface.”'
    r_g2.font.name = FONT_NAME
    r_g2.font.bold = True
    r_g2.font.size = Pt(10)
    r_g2.font.color.rgb = C_WHITE


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5: IMPACT & BENEFITS
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_5(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, "IMPACT & BENEFITS", slide_number=5)

    # ── 1. TOP: 4 LARGE METRIC-STYLE CARDS (Verified Real Metrics) ──
    metrics = [
        ("SUPPORTED MODALITIES", "SINGLE · BI-TEMPORAL\nOPTICAL + SAR", "Optical MSI, SAR Radar (VV/VH), Multi-Temporal", C_PRIMARY, C_LIGHT_BLUE),
        ("SPECIALIST WORKFLOWS", "21 REGISTERED TOOLS", "VQA, SegFormer, CDVQA, Grounding, Spectral Indices", C_SECONDARY, C_LIGHT_TEAL),
        ("EVIDENCE OUTPUT", "PIXEL MASKS & STATS", "Exact Hectares, km², NDVI, NDWI, NDBI & Confidence", C_GREEN, C_LIGHT_GREEN),
        ("REPORT GENERATION", "AUDIT-READY DOSSIERS", "Dynamic ReportLab PDF & HTML + StepTracker Trace", C_PURPLE, C_LIGHT_BLUE),
    ]

    m_w = Inches(2.88)
    m_gap = Inches(0.2)
    y_m = Inches(1.15)
    h_m = Inches(1.5)

    for idx, (m_label, m_val, m_sub, m_col, m_bg) in enumerate(metrics):
        cur_x = Inches(0.6) + idx * (m_w + m_gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, y_m, m_w, h_m)
        card.fill.solid()
        card.fill.fore_color.rgb = C_WHITE
        card.line.color.rgb = m_col
        card.line.width = Pt(1.5)

        # Label Header
        tb_l = slide.shapes.add_textbox(cur_x + Inches(0.12), y_m + Inches(0.1), m_w - Inches(0.24), Inches(0.3))
        p_l = tb_l.text_frame.paragraphs[0]
        p_l.text = m_label
        p_l.font.name = FONT_NAME
        p_l.font.bold = True
        p_l.font.size = Pt(8.5)
        p_l.font.color.rgb = m_col

        # Big Value
        tb_v = slide.shapes.add_textbox(cur_x + Inches(0.12), y_m + Inches(0.38), m_w - Inches(0.24), Inches(0.65))
        tf_v = tb_v.text_frame
        tf_v.word_wrap = True
        p_v = tf_v.paragraphs[0]
        p_v.text = m_val
        p_v.font.name = FONT_NAME
        p_v.font.bold = True
        p_v.font.size = Pt(12)
        p_v.font.color.rgb = C_PRIMARY

        # Sub
        tb_s = slide.shapes.add_textbox(cur_x + Inches(0.12), y_m + Inches(1.02), m_w - Inches(0.24), Inches(0.42))
        tf_s = tb_s.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = m_sub
        p_s.font.name = FONT_BODY
        p_s.font.size = Pt(7)
        p_s.font.color.rgb = C_MUTED

    # ── 2. APPLICATION DOMAIN CARDS (6 Cards with Clean Icons) ──
    domains = [
        ("ico_plant", "AGRICULTURE", "Crop & Vegetation Monitoring", "Quantify crop vigor, drought stress & irrigation dynamics.", "• 10m Sentinel-2 MSI • NDVI/EVI vigor tracking • Field stress alerts"),
        ("ico_water", "WATER RESOURCES", "Hydrology & Catchment Basins", "Delineate surface water bodies, reservoirs & river morphology.", "• Automated NDWI thresholding • Temporal surface retention delta"),
        ("ico_building", "URBAN PLANNING", "Built-Up Footprint & Zoning", "Track urban sprawl, impervious surfaces & infrastructure growth.", "• SegFormer semantic extraction • NDBI built-up indices • Zoning audit"),
        ("ico_tree", "FOREST & ECOLOGY", "Biomass & Conservation", "Surveil dense forest cover, illegal clearing & coastal buffers.", "• Multi-temporal change delta • Coastal CRZ protection monitoring"),
        ("ico_alert", "DISASTER RESPONSE", "All-Weather Flood & Hazards", "Rapid damage assessment during cyclones, floods & landslides.", "• Sentinel-1 C-band SAR • Pierces cloud cover & night • Hour-zero triage"),
        ("ico_sat", "EARTH OBSERVATION", "Sovereign Intelligence & Access", "Democratize complex EO rasters for non-GIS domain specialists.", "• 21 registered specialist tools • WGS84 & GeoTIFF spatial integrity")
    ]

    y_dom = Inches(2.85)
    d_w = Inches(3.85)
    d_h = Inches(1.65)
    d_gap_x = Inches(0.24)
    d_gap_y = Inches(0.18)

    for idx, (icon_name, d_title, d_sub, d_desc, d_metric) in enumerate(domains):
        col_idx = idx % 3
        row_idx = idx // 3
        cur_x = Inches(0.6) + col_idx * (d_w + d_gap_x)
        cur_y = y_dom + row_idx * (d_h + d_gap_y)

        dc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cur_x, cur_y, d_w, d_h)
        dc.fill.solid()
        dc.fill.fore_color.rgb = C_WHITE
        dc.line.color.rgb = C_BORDER
        dc.line.width = Pt(1)

        add_icon(slide, icon_name, cur_x + Inches(0.15), cur_y + Inches(0.18), size=Inches(0.44))

        tb = slide.shapes.add_textbox(cur_x + Inches(0.68), cur_y + Inches(0.1), d_w - Inches(0.78), d_h - Inches(0.15))
        tf = tb.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = d_title
        p_t.font.name = FONT_NAME
        p_t.font.bold = True
        p_t.font.size = Pt(9.5)
        p_t.font.color.rgb = C_PRIMARY

        p_s = tf.add_paragraph()
        p_s.text = d_sub
        p_s.font.name = FONT_NAME
        p_s.font.bold = True
        p_s.font.size = Pt(8)
        p_s.font.color.rgb = C_SECONDARY

        p_d = tf.add_paragraph()
        p_d.text = d_desc
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(7.5)
        p_d.font.color.rgb = C_TEXT

        p_m = tf.add_paragraph()
        p_m.text = d_metric
        p_m.font.name = FONT_BODY
        p_m.font.size = Pt(7)
        p_m.font.color.rgb = C_MUTED

    # ── 3. BOTTOM VISUAL FLOW ──
    flow_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.5), Inches(12.133), Inches(0.55))
    flow_bar.fill.solid()
    flow_bar.fill.fore_color.rgb = C_LIGHT_TEAL
    flow_bar.line.color.rgb = C_SECONDARY
    flow_bar.line.width = Pt(1.5)

    tb_fl = slide.shapes.add_textbox(Inches(0.8), Inches(6.52), Inches(11.7), Inches(0.45))
    p_fl = tb_fl.text_frame.paragraphs[0]
    p_fl.alignment = PP_ALIGN.CENTER
    p_fl.text = "SATELLITE DATA (Optical / SAR / Pairs)   ➔   AGENTIC AI   ➔   VISUAL EVIDENCE   ➔   ACTIONABLE INSIGHT   ➔   DECISION SUPPORT"
    p_fl.font.name = FONT_NAME
    p_fl.font.bold = True
    p_fl.font.size = Pt(9.5)
    p_fl.font.color.rgb = C_PRIMARY


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6: RESEARCH, BENCHMARKS & TECHNICAL FOUNDATION
# ─────────────────────────────────────────────────────────────────────────────
def build_slide_6(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, "RESEARCH, BENCHMARKS & TECHNICAL FOUNDATION", slide_number=6)

    # ── LEFT: RESEARCH FOUNDATION (6 Compact Cards with Book Icons) ──
    card_left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.15), Inches(6.4), Inches(5.2))
    card_left.fill.solid()
    card_left.fill.fore_color.rgb = C_WHITE
    card_left.line.color.rgb = C_PRIMARY
    card_left.line.width = Pt(1.5)

    add_icon(slide, "ico_book", Inches(0.8), Inches(1.28), size=Inches(0.42))

    tb_lh = slide.shapes.add_textbox(Inches(1.3), Inches(1.26), Inches(5.5), Inches(0.4))
    p_lh = tb_lh.text_frame.paragraphs[0]
    p_lh.text = "RESEARCH FOUNDATIONS & BENCHMARKS"
    p_lh.font.name = FONT_NAME
    p_lh.font.bold = True
    p_lh.font.size = Pt(12)
    p_lh.font.color.rgb = C_PRIMARY

    papers = [
        ("ico_db", "BigEarthNet", "Remote-Sensing Representation Learning", "Sumbul et al., IEEE IGARSS 2019 · Sentinel-2 multispectral band adaptation & land-cover taxonomy."),
        ("ico_msg", "RSVQA", "Remote-Sensing Visual Question Answering", "Lobry et al., IEEE TGRS 2020 · Foundational formulation for spatial counting, presence & relation VQA."),
        ("ico_target", "VRSBench", "Vision-Language Grounding & Captioning", "Li et al., NeurIPS / IEEE 2024 · Evaluation benchmark for text-guided visual region reticles."),
        ("ico_chart", "CDVQA", "Bi-Temporal Change Detection VQA", "Yuan et al., IEEE GRSL 2022 · Informs change reasoning and quantitative transition matrix extraction."),
        ("ico_brain", "SegFormer", "Semantic Transformer Segmentation", "Xie et al., NeurIPS 2021 · Core neural backbone powering 6-class land cover segmentation on LandCover.ai."),
        ("ico_radar", "SEN1-2", "Optical-SAR Multimodal Learning", "Schmitt et al., ISPRS Annals 2018 · Spatial co-registration & cross-spectral feature fusion standards.")
    ]

    y_p = Inches(1.8)
    for ico_p, title, role, cite in papers:
        pb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.78), y_p, Inches(6.04), Inches(0.68))
        pb.fill.solid()
        pb.fill.fore_color.rgb = C_LIGHT_BLUE
        pb.line.color.rgb = C_BORDER
        pb.line.width = Pt(1)

        add_icon(slide, ico_p, Inches(0.9), y_p + Inches(0.12), size=Inches(0.44))

        tb_p = slide.shapes.add_textbox(Inches(1.42), y_p + Inches(0.04), Inches(5.3), Inches(0.6))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        p_pt = tf_p.paragraphs[0]
        r1 = p_pt.add_run()
        r1.text = f"{title} — "
        r1.font.name = FONT_NAME
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_PRIMARY

        r2 = p_pt.add_run()
        r2.text = role
        r2.font.name = FONT_NAME
        r2.font.bold = True
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_SECONDARY

        p_pd = tf_p.add_paragraph()
        p_pd.text = cite
        p_pd.font.name = FONT_BODY
        p_pd.font.size = Pt(7)
        p_pd.font.color.rgb = C_TEXT

        y_p += Inches(0.74)

    # ── RIGHT: HOW RESEARCH SUPPORTS SATQUERY (Vertical Visual Mapping) ──
    card_right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.2), Inches(1.15), Inches(5.533), Inches(5.2))
    card_right.fill.solid()
    card_right.fill.fore_color.rgb = C_WHITE
    card_right.line.color.rgb = C_SECONDARY
    card_right.line.width = Pt(1.5)

    add_icon(slide, "ico_net", Inches(7.4), Inches(1.28), size=Inches(0.42))

    tb_rh = slide.shapes.add_textbox(Inches(7.9), Inches(1.26), Inches(4.7), Inches(0.4))
    p_rh = tb_rh.text_frame.paragraphs[0]
    p_rh.text = "HOW RESEARCH SUPPORTS SATQUERY"
    p_rh.font.name = FONT_NAME
    p_rh.font.bold = True
    p_rh.font.size = Pt(12)
    p_rh.font.color.rgb = C_SECONDARY

    mappings = [
        ("ico_globe", "BigEarthNet", "Remote Sensing Adaptation Layer", C_BLUE),
        ("ico_msg", "RSVQA", "Visual Question Answering (VQA) Module", C_TEAL),
        ("ico_target", "VRSBench", "Region Grounding & Scene Captioning", C_PRIMARY),
        ("ico_layers", "CDVQA", "Bi-Temporal Change Detection Engine", C_PURPLE),
        ("ico_radar", "SEN1-2", "Optical + SAR Cross-Modal Fusion", C_GREEN),
        ("ico_shield", "Indian Space Policy 2023", "Democratization of EO Data for Non-GIS Users", C_ORANGE),
    ]

    y_m = Inches(1.8)
    for ico_m, src, target, col in mappings:
        mb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.38), y_m, Inches(5.15), Inches(0.55))
        mb.fill.solid()
        mb.fill.fore_color.rgb = C_LIGHT_TEAL
        mb.line.color.rgb = col
        mb.line.width = Pt(1)

        add_icon(slide, ico_m, Inches(7.48), y_m + Inches(0.08), size=Inches(0.38))

        tb_mb = slide.shapes.add_textbox(Inches(7.95), y_m + Inches(0.08), Inches(4.5), Inches(0.4))
        p_mb = tb_mb.text_frame.paragraphs[0]
        r1 = p_mb.add_run()
        r1.text = f"{src}   ➔   "
        r1.font.name = FONT_NAME
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = col

        r2 = p_mb.add_run()
        r2.text = target
        r2.font.name = FONT_NAME
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT

        y_m += Inches(0.61)

    # Policy note in right card
    pol_note = slide.shapes.add_textbox(Inches(7.38), Inches(5.55), Inches(5.15), Inches(0.7))
    tf_pn = pol_note.text_frame
    tf_pn.word_wrap = True
    p_pn = tf_pn.paragraphs[0]
    p_pn.text = "🏛 ISRO Bhuvan & NRSC Compatibility: Adheres to OGC standards, WGS84 (EPSG:4326), Web Mercator (EPSG:3857) and GeoTIFF specifications for interoperable national infrastructure."
    p_pn.font.name = FONT_BODY
    p_pn.font.size = Pt(7.5)
    p_pn.font.color.rgb = C_MUTED

    # ── BOTTOM STATEMENT ──
    stat_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.5), Inches(12.133), Inches(0.55))
    stat_bar.fill.solid()
    stat_bar.fill.fore_color.rgb = C_PRIMARY
    stat_bar.line.color.rgb = C_SECONDARY
    stat_bar.line.width = Pt(1.5)

    tb_sb = slide.shapes.add_textbox(Inches(0.8), Inches(6.52), Inches(11.7), Inches(0.45))
    p_sb = tb_sb.text_frame.paragraphs[0]
    p_sb.alignment = PP_ALIGN.CENTER
    p_sb.text = "RESEARCH  ➔  MODELS  ➔  AGENTIC ORCHESTRATION  ➔  EVIDENCE  ➔  APPLICATION"
    p_sb.font.name = FONT_NAME
    p_sb.font.bold = True
    p_sb.font.size = Pt(10)
    p_sb.font.color.rgb = C_WHITE


# ── Generator Entrypoint ────────────────────────────────────────────────────
def main():
    prs = init_presentation()
    print("Generating Slide 1: Title Page...")
    build_slide_1(prs)
    print("Generating Slide 2: The Problem → Solution → Innovation...")
    build_slide_2(prs)
    print("Generating Slide 3: How SATQuery AI Works...")
    build_slide_3(prs)
    print("Generating Slide 4: Feasibility & Viability...")
    build_slide_4(prs)
    print("Generating Slide 5: Impact & Benefits...")
    build_slide_5(prs)
    print("Generating Slide 6: Research, Benchmarks & Technical Foundation...")
    build_slide_6(prs)

    output_pptx = Path("SATQuery_AI_SIH_2026.pptx")
    prs.save(str(output_pptx))
    print(f"\nSUCCESS: Presentation generated successfully at: {output_pptx.resolve()}")

if __name__ == "__main__":
    main()
