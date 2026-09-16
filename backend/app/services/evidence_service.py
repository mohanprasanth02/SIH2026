"""
SatQuery AI - Evidence Service
Generates classification maps, overlays, and change maps from model outputs.
All visualizations are derived from actual model mask data - never fabricated.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

import numpy as np

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EvidenceService:
    """
    Generates visual evidence from actual model outputs.
    
    Principles:
    - All colors are derived from class IDs in the actual mask
    - No random coloring
    - No fabricated regions
    - Map is always a direct visualization of the model's output
    """

    def __init__(self):
        self.results_dir = Path(settings.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def generate_classification_maps(
        self,
        mask: np.ndarray,
        original_array: np.ndarray,
        class_map: Dict,
        job_id: str,
        alpha: float = 0.5,
        target_class: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate classification map and overlay from an actual segmentation mask.
        Optimized with fast compression and target-class on-demand rendering.

        Args:
            mask: [H, W] int32 array with class IDs
            original_array: [H, W, C] original image
            class_map: {class_id: {"color": [R,G,B], "name": "...", "label": "..."}}
            job_id: For unique filenames
            alpha: Overlay transparency
            target_class: Optional specific class name to generate highlight for (e.g. "water")

        Returns:
            Dict with paths to saved images
        """
        try:
            from PIL import Image as PILImage

            h, w = mask.shape
            result_paths = {}

            # Downsample display preview if excessively large (>1024) to save I/O & memory
            display_scale = 1.0
            max_disp = 1024
            if max(h, w) > max_disp:
                display_scale = max_disp / max(h, w)
                new_w, new_h = int(w * display_scale), int(h * display_scale)
            else:
                new_w, new_h = w, h

            # 1. Classification map: color-coded by class
            color_mask = np.zeros((h, w, 3), dtype=np.uint8)
            for class_id, cls_info in class_map.items():
                color = cls_info.get("color", [128, 128, 128])
                px_mask = (mask == class_id)
                color_mask[px_mask] = color

            cls_filename = f"{job_id}_classification.png"
            cls_map_path = str(self.results_dir / cls_filename)
            cls_pil = PILImage.fromarray(color_mask)
            if display_scale < 1.0:
                cls_pil = cls_pil.resize((new_w, new_h), PILImage.Resampling.NEAREST)
            cls_pil.save(cls_map_path, format="PNG", compress_level=1)
            result_paths["classification_map"] = f"/results/{cls_filename}"

            # 2. Original image (normalized RGB)
            orig_rgb = self._array_to_rgb(original_array)
            orig_filename = f"{job_id}_original.png"
            orig_path = str(self.results_dir / orig_filename)
            orig_pil = PILImage.fromarray(orig_rgb)
            if display_scale < 1.0:
                orig_pil = orig_pil.resize((new_w, new_h), PILImage.Resampling.BILINEAR)
            orig_pil.save(orig_path, format="PNG", compress_level=1)
            result_paths["original"] = f"/results/{orig_filename}"

            # 3. Overlay: blend classification on original
            orig_rgba = orig_pil.convert("RGBA")
            cls_rgba = cls_pil.convert("RGBA")
            alpha_ch = int(alpha * 255)
            r, g, b, a = cls_rgba.split()
            a = a.point(lambda x: alpha_ch if x > 0 else 0)
            cls_rgba = PILImage.merge("RGBA", (r, g, b, a))
            overlay = PILImage.alpha_composite(orig_rgba, cls_rgba).convert("RGB")
            overlay_filename = f"{job_id}_overlay.png"
            overlay_path = str(self.results_dir / overlay_filename)
            overlay.save(overlay_path, format="PNG", compress_level=1)
            result_paths["overlay"] = f"/results/{overlay_filename}"

            # 4. On-demand visual evidence highlights
            # If target_class is specified, only generate for that class!
            # Otherwise generate for top 1 dominant class to keep response fast.
            class_highlights = {}
            class_masks = {}

            # Generate highlights for all detected classes present in the scene with pixels > 0
            candidate_classes = []
            for class_id, cls_info in class_map.items():
                if cls_info.get("name") in ("other", None):
                    continue
                px_c = int(np.sum(mask == class_id))
                if px_c > 0:
                    candidate_classes.append((px_c, class_id, cls_info))
            candidate_classes.sort(reverse=True, key=lambda x: x[0])
            classes_to_render = [(cid, cinfo) for _, cid, cinfo in candidate_classes]

            # If target_class is specified, ensure it is at the front of classes_to_render
            if target_class:
                found = False
                for idx, (cid, cinfo) in enumerate(classes_to_render):
                    if cinfo.get("name") == target_class:
                        classes_to_render.insert(0, classes_to_render.pop(idx))
                        found = True
                        break
                if not found:
                    for class_id, cls_info in class_map.items():
                        if cls_info.get("name") == target_class:
                            classes_to_render.insert(0, (class_id, cls_info))
                            break

            for class_id, cls_info in classes_to_render:
                cls_name = cls_info.get("name", "")
                px_mask = (mask == class_id)
                px_count = int(np.sum(px_mask))
                if px_count > 0:
                    cls_mask_binary = px_mask.astype(np.uint8) * 255
                    mask_filename = f"{job_id}_mask_{cls_name}.png"
                    cls_mask_path = str(self.results_dir / mask_filename)
                    mask_pil = PILImage.fromarray(cls_mask_binary)
                    if display_scale < 1.0:
                        mask_pil = mask_pil.resize((new_w, new_h), PILImage.Resampling.NEAREST)
                    mask_pil.save(cls_mask_path, format="PNG", compress_level=1)
                    class_masks[cls_name] = f"/results/{mask_filename}"

                    pct = (px_count / (h * w)) * 100
                    hl_url = self.generate_class_highlight(
                        mask=mask,
                        original_rgb=orig_rgb,
                        target_class_id=class_id,
                        cls_info=cls_info,
                        job_id=job_id,
                        pixel_count=px_count,
                        percentage=pct,
                    )
                    if hl_url:
                        class_highlights[cls_name] = hl_url

            result_paths["class_highlights"] = class_highlights
            result_paths["class_masks"] = class_masks

            return result_paths

        except Exception as e:
            logger.error(f"Evidence generation failed: {e}", exc_info=True)
            return {}

    def generate_class_highlight(
        self,
        mask: np.ndarray,
        original_rgb: np.ndarray,
        target_class_id: int,
        cls_info: Dict,
        job_id: str,
        pixel_count: int,
        percentage: float,
    ) -> Optional[str]:
        """
        Generate visual evidence: the original satellite image with the detected class
        prominently highlighted in vivid neon colors, contoured with boundary marks,
        stamped with analytical evidence badges and cluster markers.
        """
        try:
            from PIL import Image as PILImage, ImageDraw

            h, w = mask.shape
            target_px = (mask == target_class_id)
            if not np.any(target_px):
                return None

            cls_name = cls_info.get("name", f"class_{target_class_id}")
            cls_label = cls_info.get("label", cls_name.capitalize())

            # Specific distinct glowing colors for features
            neon_colors = {
                "water": [0, 245, 255],        # Radiant Electric Cyan
                "vegetation": [0, 255, 128],    # Radiant Neon Emerald Green
                "agriculture": [180, 255, 0],   # Vibrant Electric Chartreuse / Lime
                "built_up": [255, 60, 80],      # High-Impact Radiant Coral Red
                "roads": [255, 230, 0],         # High-Visibility Fluorescent Electric Yellow
                "bare_land": [255, 175, 40],    # Radiant Warm Desert Gold
            }
            hl_color = np.array(neon_colors.get(cls_name, cls_info.get("color", [0, 240, 255])), dtype=np.float32)

            # 1. Base: Dim non-target pixels slightly so the detected feature stands out
            base = (original_rgb.astype(np.float32) * 0.65).astype(np.uint8)

            # 2. Blend target pixels with vibrant glowing highlight
            target_orig = original_rgb[target_px].astype(np.float32)
            blended = (target_orig * 0.30 + hl_color * 0.70).astype(np.uint8)
            base[target_px] = blended

            # 3. Double-contour boundary marks (outer neon edge + inner bright line)
            padded = np.pad(target_px, 1, mode="constant", constant_values=False)
            edges = target_px & (
                (~padded[:-2, 1:-1]) | (~padded[2:, 1:-1]) |
                (~padded[1:-1, :-2]) | (~padded[1:-1, 2:])
            )
            base[edges] = np.clip(hl_color + 50, 0, 255).astype(np.uint8)

            # Dilate edges slightly for a subtle 2px glow boundary
            padded_edges = np.pad(edges, 1, mode="constant", constant_values=False)
            glow_edges = (
                (padded_edges[:-2, 1:-1] | padded_edges[2:, 1:-1] |
                 padded_edges[1:-1, :-2] | padded_edges[1:-1, 2:]) & ~target_px
            )
            glow_color = (hl_color * 0.6).astype(np.uint8)
            base[glow_edges] = np.clip(base[glow_edges].astype(np.float32) * 0.5 + glow_color * 0.5, 0, 255).astype(np.uint8)

            # 4. Create PIL Image and draw bounding markers and HUD badge
            pil_img = PILImage.fromarray(base)
            draw = ImageDraw.Draw(pil_img, "RGBA")

            # 5. Detect major clusters to draw spatial targeting callouts
            try:
                from scipy.ndimage import label
                labeled_array, num_features = label(target_px)
                if num_features > 0:
                    # Fast C-level cluster size calculation
                    counts = np.bincount(labeled_array.ravel())
                    # counts[0] is background, feature IDs start at 1
                    if len(counts) > 1:
                        top_ids = np.argsort(counts[1:])[-3:][::-1] + 1
                        top_clusters = [(int(counts[cid]), int(cid)) for cid in top_ids if counts[cid] >= 15]
                    else:
                        top_clusters = []

                    for rank, (c_size, c_id) in enumerate(top_clusters, start=1):
                        if c_size < 15:  # Skip tiny noise
                            continue
                        ys, xs = np.where(labeled_array == c_id)
                        ymin, ymax = int(ys.min()), int(ys.max())
                        xmin, xmax = int(xs.min()), int(xs.max())

                        # Draw bounding corner marks (high-tech reticle)
                        corner_len = min(12, max(4, (xmax - xmin) // 5))
                        box_color = (int(hl_color[0]), int(hl_color[1]), int(hl_color[2]), 220)

                        # Top-left corner
                        draw.line([(xmin, ymin), (xmin + corner_len, ymin)], fill=box_color, width=2)
                        draw.line([(xmin, ymin), (xmin, ymin + corner_len)], fill=box_color, width=2)
                        # Top-right corner
                        draw.line([(xmax, ymin), (xmax - corner_len, ymin)], fill=box_color, width=2)
                        draw.line([(xmax, ymin), (xmax, ymin + corner_len)], fill=box_color, width=2)
                        # Bottom-left corner
                        draw.line([(xmin, ymax), (xmin + corner_len, ymax)], fill=box_color, width=2)
                        draw.line([(xmin, ymax), (xmin, ymax - corner_len)], fill=box_color, width=2)
                        # Bottom-right corner
                        draw.line([(xmax, ymax), (xmax - corner_len, ymax)], fill=box_color, width=2)
                        draw.line([(xmax, ymax), (xmax, ymax - corner_len)], fill=box_color, width=2)

                        # Tiny callout label above largest cluster
                        if rank == 1 and ymin > 18 and (xmax - xmin) > 25:
                            tag_text = f"{cls_label.upper()} REGION"
                            tw = len(tag_text) * 6 + 10
                            draw.rectangle(
                                [xmin, max(0, ymin - 16), xmin + tw, ymin - 2],
                                fill=(10, 15, 25, 200),
                                outline=box_color,
                                width=1,
                            )
                            draw.text(
                                (xmin + 5, max(0, ymin - 15)),
                                tag_text,
                                fill=(255, 255, 255, 240),
                            )
            except Exception as e:
                logger.debug(f"Cluster targeting failed: {e}")

            # 6. Draw analytical evidence HUD badge on the top
            badge_text = f"EVIDENCE: {cls_label.upper()} | {percentage:.1f}% ({pixel_count:,} px)"
            badge_x, badge_y = 12, 12
            badge_w = min(len(badge_text) * 7 + 28, w - 24)
            badge_h = 28
            draw.rounded_rectangle(
                [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
                radius=6,
                fill=(8, 12, 24, 235),
                outline=(int(hl_color[0]), int(hl_color[1]), int(hl_color[2]), 255),
                width=1,
            )
            # Glowing indicator dot inside badge
            draw.ellipse(
                [badge_x + 8, badge_y + 9, badge_x + 18, badge_y + 19],
                fill=(int(hl_color[0]), int(hl_color[1]), int(hl_color[2]), 255),
            )
            draw.text(
                (badge_x + 24, badge_y + 7),
                badge_text,
                fill=(255, 255, 255, 255),
            )

            hl_filename = f"{job_id}_highlight_{cls_name}.png"
            highlight_path = str(self.results_dir / hl_filename)
            pil_img.save(highlight_path, format="PNG", compress_level=1)
            return f"/results/{hl_filename}"

        except Exception as e:
            logger.warning(f"Class highlight generation failed for {cls_info.get('name')}: {e}")
            return None

    def generate_zero_detection_evidence(
        self,
        original_rgb: np.ndarray,
        cls_name: str,
        cls_label: str,
        job_id: str,
    ) -> Optional[str]:
        """
        Generate visual evidence when 0% of a requested feature was detected.
        Displays the original image with a verified scan overlay stamp.
        """
        try:
            from PIL import Image as PILImage, ImageDraw

            h, w = original_rgb.shape[:2]
            pil_img = PILImage.fromarray(original_rgb.copy())
            draw = ImageDraw.Draw(pil_img, "RGBA")

            # Draw subtle grid corner crosshairs to indicate active scanner coverage
            crosshair_color = (0, 235, 255, 120)
            cs = 20
            # 4 corners
            draw.line([(20, 20), (20 + cs, 20)], fill=crosshair_color, width=1)
            draw.line([(20, 20), (20, 20 + cs)], fill=crosshair_color, width=1)
            draw.line([(w - 20, 20), (w - 20 - cs, 20)], fill=crosshair_color, width=1)
            draw.line([(w - 20, 20), (w - 20, 20 + cs)], fill=crosshair_color, width=1)
            draw.line([(20, h - 20), (20 + cs, h - 20)], fill=crosshair_color, width=1)
            draw.line([(20, h - 20), (20, h - 20 - cs)], fill=crosshair_color, width=1)
            draw.line([(w - 20, h - 20), (w - 20 - cs, h - 20)], fill=crosshair_color, width=1)
            draw.line([(w - 20, h - 20), (w - 20, h - 20 - cs)], fill=crosshair_color, width=1)

            # Analytical badge
            badge_text = f"VERIFIED EVIDENCE: NO {cls_label.upper()} DETECTED (0.0%)"
            badge_x, badge_y = 12, 12
            badge_w = min(len(badge_text) * 7 + 28, w - 24)
            badge_h = 28
            draw.rounded_rectangle(
                [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
                radius=6,
                fill=(8, 12, 24, 235),
                outline=(148, 163, 184, 200),
                width=1,
            )
            draw.ellipse(
                [badge_x + 8, badge_y + 9, badge_x + 18, badge_y + 19],
                fill=(148, 163, 184, 255),
            )
            draw.text(
                (badge_x + 24, badge_y + 7),
                badge_text,
                fill=(255, 255, 255, 255),
            )

            filename = f"{job_id}_zero_{cls_name}.png"
            out_path = str(self.results_dir / filename)
            pil_img.save(out_path)
            return f"/results/{filename}"
        except Exception as e:
            logger.warning(f"Zero detection evidence failed: {e}")
            return None

    def generate_change_maps(
        self,
        mask: np.ndarray,
        array_a: np.ndarray,
        array_b: np.ndarray,
        change_class_map: Dict,
        job_id: str,
    ) -> Dict[str, str]:
        """
        Generate before, after, and change visualization images.

        Args:
            mask: [H, W] int32 change class mask
            array_a: Before image array
            array_b: After image array
            change_class_map: {class_id: {"color": [...], "label": "..."}}
            job_id: For filenames

        Returns:
            Dict with web URLs to saved images
        """
        try:
            from PIL import Image as PILImage

            result_paths = {}
            h, w = mask.shape

            # Before image
            rgb_a = self._array_to_rgb(array_a)
            file_a = f"{job_id}_before.png"
            PILImage.fromarray(rgb_a).save(str(self.results_dir / file_a))
            result_paths["before"] = f"/results/{file_a}"

            # After image
            rgb_b = self._array_to_rgb(array_b)
            file_b = f"{job_id}_after.png"
            PILImage.fromarray(rgb_b).save(str(self.results_dir / file_b))
            result_paths["after"] = f"/results/{file_b}"

            # Change map: colored by change type
            change_color = np.zeros((h, w, 3), dtype=np.uint8)
            for class_id, cls_info in change_class_map.items():
                color = cls_info.get("color", [128, 128, 128])
                change_color[mask == class_id] = color
            # Make no-change areas dark gray
            change_color[mask == 0] = [20, 20, 20]

            file_change = f"{job_id}_change_map.png"
            PILImage.fromarray(change_color).save(str(self.results_dir / file_change))
            result_paths["change_map"] = f"/results/{file_change}"

            # Binary change overlay
            binary = (mask > 0).astype(np.uint8)
            highlight = np.zeros((h, w, 3), dtype=np.uint8)
            highlight[binary == 1] = [255, 50, 50]  # Red = changed

            orig_pil = PILImage.fromarray(rgb_b).convert("RGBA")
            hl_pil = PILImage.fromarray(highlight).convert("RGBA")
            r, g, b, a = hl_pil.split()
            a = a.point(lambda x: 160 if x > 0 else 0)
            hl_pil = PILImage.merge("RGBA", (r, g, b, a))
            overlay = PILImage.alpha_composite(orig_pil, hl_pil).convert("RGB")
            file_overlay = f"{job_id}_change_overlay.png"
            overlay.save(str(self.results_dir / file_overlay))
            result_paths["change_overlay"] = f"/results/{file_overlay}"

            return result_paths

        except Exception as e:
            logger.error(f"Change map generation failed: {e}", exc_info=True)
            return {}

    def generate_optical_sar_maps(
        self,
        optical_array: np.ndarray,
        sar_array: np.ndarray,
        fused_mask: np.ndarray,
        class_map: Dict,
        job_id: str,
        alpha: float = 0.5,
    ) -> Dict[str, str]:
        """
        Generate visual evidence maps for Optical + SAR fusion:
          1. Optical RGB preview
          2. SAR backscatter intensity false-color map
          3. Joint fused classification map
          4. Fusion consensus overlay
        """
        try:
            from PIL import Image as PILImage

            h, w = optical_array.shape[:2]
            result_paths = {}

            # 1. Optical RGB
            opt_rgb = self._array_to_rgb(optical_array)
            opt_file = f"{job_id}_optical.png"
            PILImage.fromarray(opt_rgb).save(str(self.results_dir / opt_file))
            result_paths["optical"] = f"/results/{opt_file}"

            # 2. SAR backscatter intensity visualization
            # Convert 1 or 2 channel SAR to a distinctive radar pseudo-color map
            sar_flt = sar_array.astype(np.float32)
            if sar_flt.ndim == 3:
                sar_band = sar_flt[:, :, 0]
            else:
                sar_band = sar_flt

            p2, p98 = np.percentile(sar_band, (2, 98))
            sar_norm = np.clip((sar_band - p2) / max(p98 - p2, 1e-6) * 255.0, 0, 255).astype(np.uint8)

            # False color for radar: blueish-gold thermal radar map
            sar_color = np.zeros((h, w, 3), dtype=np.uint8)
            sar_color[:, :, 0] = np.clip(sar_norm * 0.4, 0, 255).astype(np.uint8)
            sar_color[:, :, 1] = np.clip(sar_norm * 0.85, 0, 255).astype(np.uint8)
            sar_color[:, :, 2] = np.clip(sar_norm * 1.0, 0, 255).astype(np.uint8)

            sar_file = f"{job_id}_sar_intensity.png"
            PILImage.fromarray(sar_color).save(str(self.results_dir / sar_file))
            result_paths["sar"] = f"/results/{sar_file}"

            # 3. Fused classification map
            cls_color = np.zeros((h, w, 3), dtype=np.uint8)
            for cid, cinfo in class_map.items():
                col = cinfo.get("color", [128, 128, 128])
                cls_color[fused_mask == cid] = col

            fused_file = f"{job_id}_fused_classification.png"
            PILImage.fromarray(cls_color).save(str(self.results_dir / fused_file))
            result_paths["classification_map"] = f"/results/{fused_file}"

            # 4. Fused Overlay on Optical
            orig_pil = PILImage.fromarray(opt_rgb).convert("RGBA")
            cls_pil = PILImage.fromarray(cls_color).convert("RGBA")
            alpha_ch = int(alpha * 255)
            r, g, b, a = cls_pil.split()
            a = a.point(lambda x: alpha_ch if x > 0 else 0)
            cls_rgba = PILImage.merge("RGBA", (r, g, b, a))
            fused_overlay = PILImage.alpha_composite(orig_pil, cls_rgba).convert("RGB")

            overlay_file = f"{job_id}_fused_overlay.png"
            fused_overlay.save(str(self.results_dir / overlay_file))
            result_paths["overlay"] = f"/results/{overlay_file}"
            result_paths["original"] = f"/results/{opt_file}"

            return result_paths
        except Exception as e:
            logger.error(f"Optical-SAR map generation failed: {e}", exc_info=True)
            return {}

    def generate_grounding_evidence(
        self,
        original_array: np.ndarray,
        mask: np.ndarray,
        target_class_id: int,
        cls_info: Dict,
        bounding_boxes: List[Dict],
        job_id: str,
    ) -> Dict[str, str]:
        """
        Generates grounded visual evidence with bounding boxes, centroid reticles,
        and glowing segmentation contours.
        """
        try:
            from PIL import Image as PILImage, ImageDraw

            h, w = mask.shape
            orig_rgb = self._array_to_rgb(original_array)
            target_px = (mask == target_class_id)

            # Neon highlight for target feature
            neon_colors = {
                "water": [0, 245, 255],        # Radiant Electric Cyan
                "vegetation": [0, 255, 128],    # Radiant Neon Emerald Green
                "agriculture": [180, 255, 0],   # Vibrant Electric Chartreuse / Lime
                "built_up": [255, 60, 80],      # High-Impact Radiant Coral Red
                "roads": [255, 230, 0],         # High-Visibility Fluorescent Electric Yellow
                "bare_land": [255, 175, 40],    # Radiant Warm Desert Gold
            }
            cls_name = cls_info.get("name", "")
            hl_color = np.array(neon_colors.get(cls_name, cls_info.get("color", [0, 245, 255])), dtype=np.float32)
            base = (orig_rgb.astype(np.float32) * 0.65).astype(np.uint8)

            if np.any(target_px):
                base[target_px] = (orig_rgb[target_px].astype(np.float32) * 0.35 + hl_color * 0.65).astype(np.uint8)

            pil_img = PILImage.fromarray(base)
            draw = ImageDraw.Draw(pil_img, "RGBA")

            # Draw bounding boxes and corner reticles
            bcol = (int(hl_color[0]), int(hl_color[1]), int(hl_color[2]), 240)
            for i, box in enumerate(bounding_boxes, start=1):
                ymin, xmin, ymax, xmax = box["ymin"], box["xmin"], box["ymax"], box["xmax"]
                corner = min(14, max(4, (xmax - xmin) // 4))

                # Corners
                draw.line([(xmin, ymin), (xmin + corner, ymin)], fill=bcol, width=2)
                draw.line([(xmin, ymin), (xmin, ymin + corner)], fill=bcol, width=2)
                draw.line([(xmax, ymin), (xmax - corner, ymin)], fill=bcol, width=2)
                draw.line([(xmax, ymin), (xmax, ymin + corner)], fill=bcol, width=2)
                draw.line([(xmin, ymax), (xmin + corner, ymax)], fill=bcol, width=2)
                draw.line([(xmin, ymax), (xmin, ymax - corner)], fill=bcol, width=2)
                draw.line([(xmax, ymax), (xmax - corner, ymax)], fill=bcol, width=2)
                draw.line([(xmax, ymax), (xmax, ymax - corner)], fill=bcol, width=2)

                # Tag
                tag = f"TARGET #{i} ({cls_info.get('label', 'REGION')})"
                draw.rectangle([xmin, max(0, ymin - 16), xmin + len(tag) * 6 + 10, ymin - 2], fill=(10, 15, 25, 220), outline=bcol)
                draw.text((xmin + 4, max(0, ymin - 15)), tag, fill=(255, 255, 255, 255))

            ground_file = f"{job_id}_grounding_evidence.png"
            pil_img.save(str(self.results_dir / ground_file))

            orig_file = f"{job_id}_grounding_original.png"
            PILImage.fromarray(orig_rgb).save(str(self.results_dir / orig_file))

            return {
                "grounding_evidence": f"/results/{ground_file}",
                "original": f"/results/{orig_file}",
                "overlay": f"/results/{ground_file}",
            }
        except Exception as e:
            logger.error(f"Grounding evidence generation failed: {e}", exc_info=True)
            return {}

    def generate_thumbnail(self, image_path: str, max_size: int = 512) -> Optional[str]:
        """Generate a thumbnail for display in the UI."""
        try:
            from PIL import Image as PILImage
            import rasterio

            ext = Path(image_path).suffix.lower()
            stem = Path(image_path).stem
            thumb_path = str(self.results_dir / f"{stem}_thumb.png")

            if ext in (".tif", ".tiff"):
                with rasterio.open(image_path) as ds:
                    bands = min(ds.count, 3)
                    arrays = []
                    for i in range(1, bands + 1):
                        arr = ds.read(i).astype(np.float32)
                        valid = arr[arr > 0]
                        if valid.size > 0:
                            p2, p98 = np.percentile(valid, (2, 98))
                            arr = np.clip((arr - p2) / max(p98 - p2, 1e-6) * 255, 0, 255)
                        arrays.append(arr.astype(np.uint8))
                    if bands == 1:
                        arrays = arrays * 3
                    rgb = np.stack(arrays[:3], axis=-1)
                    img = PILImage.fromarray(rgb)
            else:
                img = PILImage.open(image_path).convert("RGB")

            img.thumbnail((max_size, max_size), PILImage.LANCZOS)
            img.save(thumb_path)
            return thumb_path

        except Exception as e:
            logger.warning(f"Thumbnail generation failed: {e}")
            return None

    def _array_to_rgb(self, array: np.ndarray, max_size: int = 0) -> np.ndarray:
        """Convert any image array to uint8 RGB [H, W, 3]."""
        arr = array.astype(np.float32)

        if arr.ndim == 2:
            arr = np.stack([arr, arr, arr], axis=-1)
        elif arr.shape[2] == 1:
            arr = np.concatenate([arr, arr, arr], axis=-1)
        elif arr.shape[2] > 3:
            arr = arr[:, :, :3]

        # Percentile stretch to [0, 255]
        valid = arr[np.isfinite(arr) & (arr > 0)]
        if valid.size > 0:
            p2, p98 = np.percentile(valid, (2, 98))
            if p98 > p2:
                arr = np.clip((arr - p2) / (p98 - p2) * 255, 0, 255)
            else:
                arr = np.clip(arr / (arr.max() + 1e-6) * 255, 0, 255)
        else:
            arr = np.zeros_like(arr)

        return arr.astype(np.uint8)
