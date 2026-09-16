"""
Generate full set of Lucide-style minimalist, high-contrast circular icons for SATQuery AI presentation.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math

icon_dir = Path("scratch/ppt_assets/icons")
icon_dir.mkdir(parents=True, exist_ok=True)

# Color System
C_BLUE = (18, 59, 93)        # #123B5D Data / Architecture
C_TEAL = (20, 138, 131)      # #148A83 AI / Intelligence
C_GREEN = (61, 155, 101)     # #3D9B65 Evidence / Benefit
C_ORANGE = (233, 138, 58)    # #E98A3A Warning / Highlight
C_PURPLE = (110, 69, 184)    # #6E45B8 Modality / Reports
C_RED = (217, 83, 79)        # #D9534F Disaster / Alert
C_CYAN = (15, 139, 141)      # #0F8B8D Water / Ocean
C_WHITE = (255, 255, 255)

def create_circular_icon(name, bg_color, symbol_type, size=160):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    pad = 4
    draw.ellipse([pad, pad, size - pad, size - pad], fill=bg_color)
    draw.ellipse([pad + 6, pad + 6, size - pad - 6, size - pad - 6], outline=(255, 255, 255, 30), width=2)
    
    cx, cy = size // 2, size // 2

    if symbol_type == "satellite":
        # Satellite with solar panels
        draw.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], outline=C_WHITE, width=4)
        # Panels
        draw.line([cx - 28, cy, cx - 10, cy], fill=C_WHITE, width=4)
        draw.line([cx + 10, cy, cx + 28, cy], fill=C_WHITE, width=4)
        draw.rectangle([cx - 36, cy - 8, cx - 28, cy + 8], fill=C_WHITE)
        draw.rectangle([cx + 28, cy - 8, cx + 36, cy + 8], fill=C_WHITE)
        # Dish antenna
        draw.arc([cx - 12, cy - 26, cx + 12, cy - 6], start=30, end=150, fill=C_WHITE, width=4)
        draw.line([cx, cy - 10, cx, cy - 16], fill=C_WHITE, width=3)

    elif symbol_type == "message":
        # Chat message bubble
        draw.rounded_rectangle([cx - 24, cy - 20, cx + 24, cy + 14], radius=6, outline=C_WHITE, width=4)
        # Bubble tail
        draw.polygon([(cx - 12, cy + 14), (cx - 18, cy + 24), (cx - 4, cy + 14)], fill=C_WHITE)
        # Lines inside
        draw.line([cx - 14, cy - 8, cx + 14, cy - 8], fill=C_WHITE, width=3)
        draw.line([cx - 14, cy + 2, cx + 6, cy + 2], fill=C_WHITE, width=3)

    elif symbol_type == "shield":
        # Security shield with checkmark
        draw.polygon([(cx, cy - 24), (cx + 24, cy - 14), (cx + 20, cy + 12), (cx, cy + 26), (cx - 20, cy + 12), (cx - 24, cy - 14)], outline=C_WHITE, width=4)
        draw.line([cx - 10, cy + 2, cx - 2, cy + 10], fill=C_WHITE, width=4)
        draw.line([cx - 2, cy + 10, cx + 12, cy - 6], fill=C_WHITE, width=4)

    elif symbol_type == "network":
        # Agentic network nodes
        draw.ellipse([cx - 22, cy - 14, cx - 8, cy], fill=C_WHITE)
        draw.ellipse([cx + 8, cy - 14, cx + 22, cy], fill=C_WHITE)
        draw.ellipse([cx - 7, cy + 10, cx + 7, cy + 24], fill=C_WHITE)
        draw.line([cx - 15, cy - 7, cx + 15, cy - 7], fill=C_WHITE, width=4)
        draw.line([cx - 15, cy - 7, cx, cy + 17], fill=C_WHITE, width=4)
        draw.line([cx + 15, cy - 7, cx, cy + 17], fill=C_WHITE, width=4)

    elif symbol_type == "brain":
        # Neural brain network
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=C_WHITE, width=4)
        draw.line([cx, cy - 20, cx, cy + 20], fill=C_WHITE, width=3)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=C_WHITE)
        draw.line([cx - 14, cy - 6, cx + 14, cy + 6], fill=C_WHITE, width=3)
        draw.line([cx - 14, cy + 6, cx + 14, cy - 6], fill=C_WHITE, width=3)

    elif symbol_type == "eye":
        # Eye / Visual evidence
        draw.arc([cx - 26, cy - 16, cx + 26, cy + 16], start=0, end=180, fill=C_WHITE, width=4)
        draw.arc([cx - 26, cy - 16, cx + 26, cy + 16], start=180, end=360, fill=C_WHITE, width=4)
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=C_WHITE, width=4)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=C_WHITE)

    elif symbol_type == "file_report":
        # Document report with lines
        draw.rounded_rectangle([cx - 16, cy - 22, cx + 16, cy + 22], radius=3, outline=C_WHITE, width=4)
        draw.line([cx - 10, cy - 12, cx + 10, cy - 12], fill=C_WHITE, width=3)
        draw.line([cx - 10, cy - 4, cx + 10, cy - 4], fill=C_WHITE, width=3)
        draw.line([cx - 10, cy + 4, cx + 4, cy + 4], fill=C_WHITE, width=3)
        draw.line([cx - 10, cy + 12, cx + 8, cy + 12], fill=C_WHITE, width=3)

    elif symbol_type == "layers":
        # 3 stacked polygon layers
        for dy in [-12, 0, 12]:
            draw.polygon([(cx, cy + dy - 8), (cx + 22, cy + dy), (cx, cy + dy + 8), (cx - 22, cy + dy)], outline=C_WHITE, width=3)

    elif symbol_type == "settings_user":
        # User head with gear
        draw.ellipse([cx - 10, cy - 24, cx + 10, cy - 4], fill=C_WHITE)
        draw.arc([cx - 20, cy + 2, cx + 20, cy + 30], start=180, end=0, fill=C_WHITE, width=5)
        # Gear teeth
        draw.line([cx + 16, cy - 16, cx + 24, cy - 16], fill=C_WHITE, width=4)
        draw.line([cx + 20, cy - 20, cx + 20, cy - 12], fill=C_WHITE, width=4)

    elif symbol_type == "radar":
        # Radar circles
        draw.arc([cx - 24, cy - 24, cx + 24, cy + 24], start=210, end=330, fill=C_WHITE, width=4)
        draw.arc([cx - 16, cy - 16, cx + 16, cy + 16], start=210, end=330, fill=C_WHITE, width=4)
        draw.arc([cx - 8, cy - 8, cx + 8, cy + 8], start=210, end=330, fill=C_WHITE, width=4)
        draw.ellipse([cx - 3, cy + 16, cx + 3, cy + 22], fill=C_WHITE)

    elif symbol_type == "code":
        draw.line([cx - 24, cy, cx - 12, cy - 18], fill=C_WHITE, width=5)
        draw.line([cx - 24, cy, cx - 12, cy + 18], fill=C_WHITE, width=5)
        draw.line([cx + 24, cy, cx + 12, cy - 18], fill=C_WHITE, width=5)
        draw.line([cx + 24, cy, cx + 12, cy + 18], fill=C_WHITE, width=5)
        draw.line([cx - 4, cy + 18, cx + 4, cy - 18], fill=C_WHITE, width=4)

    elif symbol_type == "database":
        for dy in [-16, 0, 16]:
            draw.rounded_rectangle([cx - 22, cy + dy - 6, cx + 22, cy + dy + 6], radius=5, fill=None, outline=C_WHITE, width=4)
        draw.line([cx - 22, cy - 16, cx - 22, cy + 16], fill=C_WHITE, width=4)
        draw.line([cx + 22, cy - 16, cx + 22, cy + 16], fill=C_WHITE, width=4)

    elif symbol_type == "globe":
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=C_WHITE, width=4)
        draw.line([cx - 22, cy, cx + 22, cy], fill=C_WHITE, width=3)
        draw.ellipse([cx - 12, cy - 22, cx + 12, cy + 22], outline=C_WHITE, width=3)

    elif symbol_type == "cloud_rain":
        draw.ellipse([cx - 20, cy - 14, cx + 6, cy + 8], fill=C_WHITE)
        draw.ellipse([cx - 6, cy - 22, cx + 20, cy + 6], fill=C_WHITE)
        draw.ellipse([cx + 6, cy - 12, cx + 24, cy + 8], fill=C_WHITE)
        draw.rectangle([cx - 16, cy, cx + 20, cy + 8], fill=C_WHITE)
        # Raindrops
        draw.line([cx - 10, cy + 14, cx - 14, cy + 24], fill=(255, 230, 80), width=4)
        draw.line([cx, cy + 14, cx - 4, cy + 24], fill=(255, 230, 80), width=4)
        draw.line([cx + 10, cy + 14, cx + 6, cy + 24], fill=(255, 230, 80), width=4)

    elif symbol_type == "cpu":
        # CPU Microchip
        draw.rectangle([cx - 16, cy - 16, cx + 16, cy + 16], outline=C_WHITE, width=4)
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], fill=C_WHITE)
        # Pins
        for p in [-10, 0, 10]:
            draw.line([cx + p, cy - 24, cx + p, cy - 16], fill=C_WHITE, width=3)
            draw.line([cx + p, cy + 16, cx + p, cy + 24], fill=C_WHITE, width=3)
            draw.line([cx - 24, cy + p, cx - 16, cy + p], fill=C_WHITE, width=3)
            draw.line([cx + 16, cy + p, cx + 24, cy + p], fill=C_WHITE, width=3)

    elif symbol_type == "lock_shield":
        draw.polygon([(cx, cy - 22), (cx + 22, cy - 12), (cx + 20, cy + 12), (cx, cy + 24), (cx - 20, cy + 12), (cx - 22, cy - 12)], outline=C_WHITE, width=4)
        draw.arc([cx - 8, cy - 12, cx + 8, cy], start=180, end=0, fill=C_WHITE, width=4)
        draw.rounded_rectangle([cx - 10, cy - 2, cx + 10, cy + 14], radius=3, fill=C_WHITE)

    elif symbol_type == "target":
        draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=C_WHITE, width=4)
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=C_WHITE, width=3)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=C_WHITE)
        draw.line([cx - 28, cy, cx + 28, cy], fill=C_WHITE, width=3)
        draw.line([cx, cy - 28, cx, cy + 28], fill=C_WHITE, width=3)

    elif symbol_type == "check_circle":
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=C_WHITE, width=4)
        draw.line([cx - 10, cy + 1, cx - 3, cy + 8], fill=C_WHITE, width=5)
        draw.line([cx - 3, cy + 8, cx + 11, cy - 7], fill=C_WHITE, width=5)

    elif symbol_type == "plant":
        draw.arc([cx - 16, cy - 20, cx + 16, cy + 12], start=90, end=270, fill=C_WHITE, width=4)
        draw.arc([cx - 16, cy - 20, cx + 16, cy + 12], start=270, end=90, fill=C_WHITE, width=4)
        draw.line([cx, cy - 18, cx, cy + 22], fill=C_WHITE, width=4)

    elif symbol_type == "water_drop":
        draw.ellipse([cx - 14, cy - 6, cx + 14, cy + 20], fill=C_WHITE)
        draw.polygon([(cx, cy - 22), (cx - 12, cy - 2), (cx + 12, cy - 2)], fill=C_WHITE)

    elif symbol_type == "building":
        draw.rectangle([cx - 18, cy - 16, cx - 4, cy + 22], outline=C_WHITE, width=3)
        draw.rectangle([cx - 2, cy - 24, cx + 14, cy + 22], outline=C_WHITE, width=3)
        for dy in [-16, -8, 0, 8]:
            draw.rectangle([cx + 2, cy + dy, cx + 10, cy + dy + 4], fill=C_WHITE)
            if dy >= -8:
                draw.rectangle([cx - 14, cy + dy, cx - 8, cy + dy + 4], fill=C_WHITE)

    elif symbol_type == "tree":
        draw.polygon([(cx, cy - 22), (cx + 16, cy - 2), (cx - 16, cy - 2)], fill=C_WHITE)
        draw.polygon([(cx, cy - 10), (cx + 20, cy + 10), (cx - 20, cy + 10)], fill=C_WHITE)
        draw.rectangle([cx - 4, cy + 10, cx + 4, cy + 22], fill=C_WHITE)

    elif symbol_type == "alert":
        pts = [(cx, cy - 24), (cx + 24, cy + 18), (cx - 24, cy + 18)]
        draw.polygon(pts, outline=C_WHITE, width=4)
        draw.line([cx, cy - 10, cx, cy + 6], fill=C_WHITE, width=4)
        draw.ellipse([cx - 3, cy + 10, cx + 3, cy + 16], fill=C_WHITE)

    elif symbol_type == "book":
        draw.line([cx, cy - 16, cx, cy + 18], fill=C_WHITE, width=4)
        draw.arc([cx - 24, cy - 20, cx, cy + 14], start=180, end=0, fill=C_WHITE, width=4)
        draw.arc([cx, cy - 20, cx + 24, cy + 14], start=180, end=0, fill=C_WHITE, width=4)
        draw.line([cx - 24, cy - 3, cx - 24, cy + 15], fill=C_WHITE, width=4)
        draw.line([cx + 24, cy - 3, cx + 24, cy + 15], fill=C_WHITE, width=4)
        draw.arc([cx - 24, cy - 2, cx, cy + 20], start=180, end=0, fill=C_WHITE, width=4)
        draw.arc([cx, cy - 2, cx + 24, cy + 20], start=180, end=0, fill=C_WHITE, width=4)

    elif symbol_type == "speedometer":
        draw.arc([cx - 22, cy - 22, cx + 22, cy + 22], start=150, end=390, fill=C_WHITE, width=5)
        draw.line([cx, cy, cx + 14, cy - 12], fill=(255, 230, 80), width=4)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=C_WHITE)

    elif symbol_type == "chart_up":
        draw.line([cx - 22, cy + 20, cx + 22, cy + 20], fill=C_WHITE, width=4)
        draw.line([cx - 22, cy - 20, cx - 22, cy + 20], fill=C_WHITE, width=4)
        draw.line([cx - 20, cy + 14, cx - 6, cy + 4], fill=C_WHITE, width=4)
        draw.line([cx - 6, cy + 4, cx + 6, cy + 10], fill=C_WHITE, width=4)
        draw.line([cx + 6, cy + 10, cx + 20, cy - 14], fill=(255, 230, 80), width=5)

    img.save(icon_dir / f"{name}.png", "PNG")
    print(f"Generated: {name}.png")

all_icons = [
    ("ico_sat", C_BLUE, "satellite"),
    ("ico_msg", C_TEAL, "message"),
    ("ico_shield", C_BLUE, "shield"),
    ("ico_net", C_TEAL, "network"),
    ("ico_brain", C_TEAL, "brain"),
    ("ico_eye", C_GREEN, "eye"),
    ("ico_doc", C_BLUE, "file_report"),
    ("ico_layers", C_BLUE, "layers"),
    ("ico_settings", C_BLUE, "settings_user"),
    ("ico_radar", C_TEAL, "radar"),
    ("ico_code", C_BLUE, "code"),
    ("ico_db", C_BLUE, "database"),
    ("ico_globe", C_BLUE, "globe"),
    ("ico_cloud_rain", C_ORANGE, "cloud_rain"),
    ("ico_cpu", C_ORANGE, "cpu"),
    ("ico_lock_shield", C_ORANGE, "lock_shield"),
    ("ico_target", C_ORANGE, "target"),
    ("ico_check", C_GREEN, "check_circle"),
    ("ico_plant", C_GREEN, "plant"),
    ("ico_water", C_CYAN, "water_drop"),
    ("ico_building", C_BLUE, "building"),
    ("ico_tree", C_GREEN, "tree"),
    ("ico_alert", C_RED, "alert"),
    ("ico_book", C_BLUE, "book"),
    ("ico_speed", C_BLUE, "speedometer"),
    ("ico_chart", C_GREEN, "chart_up"),
]

for n, c, s in all_icons:
    create_circular_icon(n, c, s)

print("All icons successfully generated!")
