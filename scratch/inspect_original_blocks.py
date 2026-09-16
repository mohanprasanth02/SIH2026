import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

# Save full resolution original RGB
im = Image.fromarray(rgb)
im.save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/original_coimbatore.png')

# Let's also print average color for grid regions 4x4
print(f"Image dimension: {w} x {h}")
for gy in range(4):
    for gx in range(4):
        y0, y1 = int(gy * h / 4), int((gy + 1) * h / 4)
        x0, x1 = int(gx * w / 4), int((gx + 1) * w / 4)
        block = rgb[y0:y1, x0:x1]
        r_m, g_m, b_m = block[:,:,0].mean(), block[:,:,1].mean(), block[:,:,2].mean()
        print(f"Block [{gy},{gx}] (x:{x0}..{x1}, y:{y0}..{y1}): R={r_m:.1f}, G={g_m:.1f}, B={b_m:.1f}")
