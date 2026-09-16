import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

# The bund road runs vertically along the east bank of the lake (x roughly 105 to 120)
# Let's inspect a crop of this road: y from 50 to 180, x from 105 to 118
road_crop = rgb[50:180, 105:118]
r = road_crop[:, :, 0].astype(float)
g = road_crop[:, :, 1].astype(float)
b = road_crop[:, :, 2].astype(float)
bright = (r + g + b) / 3.0
max_c = np.maximum(np.maximum(r, g), b)
min_c = np.minimum(np.minimum(r, g), b)
chroma = max_c - min_c
sat = chroma / (max_c + 1e-5)

print("LAKESIDE ROAD (x: 105-118, y: 50-180):")
print(f"  R: mean={r.mean():.1f}, min={r.min()}, max={r.max()}")
print(f"  G: mean={g.mean():.1f}, min={g.min()}, max={g.max()}")
print(f"  B: mean={b.mean():.1f}, min={b.min()}, max={b.max()}")
print(f"  Brightness: mean={bright.mean():.1f}, min={bright.min():.1f}, max={bright.max():.1f}")
print(f"  Saturation: mean={sat.mean():.3f}, p90={np.percentile(sat, 90):.3f}")
print(f"  Chroma: mean={chroma.mean():.1f}, p90={np.percentile(chroma, 90):.1f}")
print(f"  |R - G|: mean={np.abs(r - g).mean():.1f}, p90={np.percentile(np.abs(r - g), 90):.1f}")
print(f"  |G - B|: mean={np.abs(g - b).mean():.1f}, p90={np.percentile(np.abs(g - b), 90):.1f}")

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter, LAND_COVER_CLASSES
adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']
road_crop_mask = mask[50:180, 105:118]
unique, counts = np.unique(road_crop_mask, return_counts=True)
print("\nCurrent classification of lakeside road crop:")
for u, c in zip(unique, counts):
    print(f"  {LAND_COVER_CLASSES[u]['name']} ({u}): {c} px ({c / road_crop_mask.size * 100:.1f}%)")
