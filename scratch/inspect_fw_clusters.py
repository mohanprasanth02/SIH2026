import numpy as np
import rasterio

tif_path = 'backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif'
with rasterio.open(tif_path) as src:
    arr = src.read()
rgb = np.transpose(arr[:3], (1, 2, 0))
h, w = rgb.shape[:2]

import sys
sys.path.insert(0, 'backend')
from app.models.adapters.segmentation import SegmentationAdapter

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)
mask = out.data['mask']

false_water = (mask == 1) & (np.arange(w)[None, :] > 150)
import scipy.ndimage as ndi
labeled, num = ndi.label(false_water)
print(f"Number of false water clusters: {num}")
sizes = np.bincount(labeled.ravel())[1:]
print("Cluster sizes:", sorted(sizes, reverse=True)[:15])

# Find the largest false water cluster
largest_cluster_id = np.argmax(sizes) + 1
y_idx, x_idx = np.where(labeled == largest_cluster_id)
print(f"Largest false water cluster: size={len(y_idx)}, y range=[{y_idx.min()}, {y_idx.max()}], x range=[{x_idx.min()}, {x_idx.max()}]")

# Check RGB of largest cluster
cluster_rgb = rgb[y_idx, x_idx]
print(f"RGB values: R mean={cluster_rgb[:,0].mean():.1f}, G mean={cluster_rgb[:,1].mean():.1f}, B mean={cluster_rgb[:,2].mean():.1f}")
