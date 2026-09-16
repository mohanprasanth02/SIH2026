import sys
sys.path.insert(0, 'backend')
import numpy as np
import rasterio
from app.models.adapters.segmentation import SegmentationAdapter
from app.services.evidence_service import EvidenceService

src = rasterio.open('backend/data/uploads/2cb0885f-e1cc-49be-8904-d894c741857a.tif')
rgb = np.transpose(src.read()[:3], (1, 2, 0))

adapter = SegmentationAdapter()
adapter.load()
out = adapter.infer(image_array=rgb)

ev_svc = EvidenceService()
# Test generating water highlight
water_res = ev_svc.generate_classification_maps(
    mask=out.data['mask'],
    original_array=rgb,
    class_map=out.data['class_map'],
    job_id='coimbatore_final_water',
    target_class='water'
)
print("Water Evidence Paths:", water_res)

# Test generating roads highlight
road_res = ev_svc.generate_classification_maps(
    mask=out.data['mask'],
    original_array=rgb,
    class_map=out.data['class_map'],
    job_id='coimbatore_final_road',
    target_class='roads'
)
print("Road Evidence Paths:", road_res)
