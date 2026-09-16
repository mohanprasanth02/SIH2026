"""
Script to create clean high-res helper badge assets for SATQuery AI SIH 2026 presentation.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_dir = Path("scratch/ppt_assets")
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Create SIH 2026 Badge
def create_sih_badge():
    w, h = 420, 140
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Background pill
    draw.rounded_rectangle([2, 2, w - 2, h - 2], radius=16, fill=(255, 255, 255, 240), outline=(220, 225, 230), width=2)
    
    # Left brain/bulb icon simplified aesthetic
    cx, cy = 60, 70
    draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35], fill=(247, 249, 248), outline=(22, 135, 127), width=2)
    draw.arc([cx - 25, cy - 25, cx + 25, cy + 25], start=0, end=360, fill=(233, 138, 58), width=3)
    
    # Inner light/brain symbol
    draw.line([cx, cy - 20, cx, cy + 20], fill=(18, 59, 93), width=3)
    draw.line([cx - 15, cy - 8, cx + 15, cy - 8], fill=(61, 155, 101), width=3)
    draw.line([cx - 12, cy + 6, cx + 12, cy + 6], fill=(233, 138, 58), width=3)
    
    # Text
    # Use default bitmap or simple text
    draw.text((120, 25), "SMART INDIA HACKATHON", fill=(18, 59, 93), spacing=2)
    draw.text((120, 50), "2026", fill=(233, 138, 58))
    draw.text((120, 80), "HARDWARE & SOFTWARE EDITION", fill=(95, 109, 126))
    draw.text((120, 100), "PS ID: 26167 · ISRO", fill=(22, 135, 127))
    
    img.save(out_dir / "sih_badge.png", "PNG")
    print("Saved sih_badge.png")

# 2. Create ISRO Badge
def create_isro_badge():
    w, h = 280, 80
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    draw.rounded_rectangle([2, 2, w - 2, h - 2], radius=12, fill=(18, 59, 93), outline=(22, 135, 127), width=2)
    draw.text((20, 18), "ISRO / DOS", fill=(233, 138, 58))
    draw.text((20, 42), "SPACE TECHNOLOGY · PS 26167", fill=(247, 249, 248))
    
    img.save(out_dir / "isro_badge.png", "PNG")
    print("Saved isro_badge.png")

create_sih_badge()
create_isro_badge()
