import sys
sys.path.insert(0, 'backend')
import numpy as np
import rasterio
from app.models.adapters.segmentation import SegmentationAdapter

src = rasterio.open('backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif')
rgb = np.transpose(src.read()[:3], (1, 2, 0))

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)

print(f"Success: {out.success}")
print(f"Calibrated Confidence: {out.confidence * 100:.1f}%")
counts = out.data['class_counts']
total = out.data['total_pixels']
cmap = out.data['class_map']
print("\nClass breakdown:")
for c, info in cmap.items():
    cnt = counts.get(c, 0)
    pct = cnt / total * 100
    print(f"  {info['name']}: {pct:.2f}% ({cnt} px)")

mask = out.data['mask']
lake_crop = mask[:, :100]
print(f"\nLake (cols 0..100) Water Coverage: {np.mean(lake_crop == 1)*100:.2f}%")
print(f"Urban area (x > 120) false water count: {np.sum(mask[:, 120:] == 1)} px")
print(f"Bund road center (x=111, y:50-180) Road coverage: {np.mean(mask[50:180, 111] == 5)*100:.1f}%")
