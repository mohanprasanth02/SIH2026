import numpy as np
from PIL import Image
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter, LAND_COVER_CLASSES

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']

# Create a colored classification map
cmap = np.zeros((h, w, 3), dtype=np.uint8)
for c_id, c_meta in LAND_COVER_CLASSES.items():
    cmap[mask == c_id] = c_meta['color']

Image.fromarray(cmap).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/current_class_map.png')

# Create an overlay: original dimmed + vivid class colors with alpha=0.5
overlay = (rgb.astype(float) * 0.4 + cmap.astype(float) * 0.6).astype(np.uint8)
Image.fromarray(overlay).save('C:/Users/mohan/.gemini/antigravity-ide/brain/0bc72704-fe0e-4cb6-8d9b-f7bc76149502/current_overlay.png')

print("Saved current_class_map.png and current_overlay.png")
