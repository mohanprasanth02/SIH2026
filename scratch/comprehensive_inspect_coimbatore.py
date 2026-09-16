import numpy as np
from PIL import Image
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()  # (bands, H, W)
    profile = src.profile
    print("Rasterio profile:", profile)
    print("Array shape:", arr.shape, "dtype:", arr.dtype)

# Convert to (H, W, 3)
if arr.shape[0] >= 3:
    rgb = np.transpose(arr[:3], (1, 2, 0))
else:
    rgb = np.stack([arr[0]]*3, axis=-1)

print("RGB shape:", rgb.shape)
print("RGB ranges: R=[{}, {}], G=[{}, {}], B=[{}, {}]".format(
    rgb[:,:,0].min(), rgb[:,:,0].max(),
    rgb[:,:,1].min(), rgb[:,:,1].max(),
    rgb[:,:,2].min(), rgb[:,:,2].max()
))

# Test current adapter output
import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter, LAND_COVER_CLASSES

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']
counts = out.data['class_counts']
print("counts:", counts)
print("info:", info)
