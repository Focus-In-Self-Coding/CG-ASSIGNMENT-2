"""Write synchronized RGB, depth, masks, YOLO labels and metadata."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
from PIL import Image

from annotations.bounding_box import bbox_from_mask, bbox_to_yolo
from annotations.segmentation import decode_instance_ids, mask_for_instance
from annotations.depth_map import depth_preview_u16


class DatasetExporter:
    def __init__(self, output_dir: str | Path):
        self.root = Path(output_dir)
        self.images_dir = self.root / "images"
        self.depth_dir = self.root / "depth"
        self.mask_color_dir = self.root / "masks" / "instance_color"
        self.instance_masks_dir = self.root / "masks" / "instances"
        self.labels_dir = self.root / "labels"
        self.metadata_dir = self.root / "metadata"
        for directory in (self.images_dir, self.depth_dir, self.mask_color_dir,
                          self.instance_masks_dir, self.labels_dir, self.metadata_dir):
            directory.mkdir(parents=True, exist_ok=True)

    def _next_sample_id(self):
        existing = [int(p.stem) for p in self.images_dir.glob("*.png") if p.stem.isdigit()]
        return f"{max(existing, default=0) + 1:06d}"

    def save_sample(self, sample: dict, scene, camera):
        sample_id = self._next_sample_id()
        rgb = np.asarray(sample["rgb"], dtype=np.uint8)
        depth = np.asarray(sample["depth_meters"], dtype=np.float32)
        seg = np.asarray(sample["segmentation"], dtype=np.uint8)
        height, width = rgb.shape[:2]
        if depth.shape != (height, width) or seg.shape[:2] != (height, width):
            raise ValueError("RGB, depth and segmentation dimensions must match")

        Image.fromarray(rgb).save(self.images_dir / f"{sample_id}.png")
        np.save(self.depth_dir / f"{sample_id}.npy", depth)
        Image.fromarray(depth_preview_u16(depth)).save(
            self.depth_dir / f"{sample_id}.png")
        Image.fromarray(seg).save(self.mask_color_dir / f"{sample_id}.png")

        id_map = decode_instance_ids(seg)
        yolo_lines = []
        annotation_records = []
        for obj in scene.objects:
            mask = mask_for_instance(id_map, obj.instance_id)
            bbox = bbox_from_mask(mask)
            visible = bbox is not None
            if visible:
                mask_name = f"{sample_id}_{obj.instance_id:06d}.png"
                Image.fromarray(mask.astype(np.uint8) * 255).save(
                    self.instance_masks_dir / mask_name)
                yolo = bbox_to_yolo(bbox, width, height)
                yolo_lines.append(f"{obj.class_id} " + " ".join(f"{v:.6f}" for v in yolo))
            else:
                mask_name = None
            annotation_records.append({
                "name": obj.name, "instance_id": obj.instance_id,
                "class_id": obj.class_id, "visible": visible,
                "bbox_pixels": bbox, "instance_mask": mask_name,
            })

        (self.labels_dir / f"{sample_id}.txt").write_text(
            "\n".join(yolo_lines) + ("\n" if yolo_lines else ""), encoding="utf-8")
        metadata = {
            "sample_id": sample_id,
            "image": f"images/{sample_id}.png",
            "depth_npy": f"depth/{sample_id}.npy",
            "depth_preview": f"depth/{sample_id}.png",
            "instance_color_mask": f"masks/instance_color/{sample_id}.png",
            "yolo_labels": f"labels/{sample_id}.txt",
            "image_width": width, "image_height": height,
            "camera": camera.metadata(),
            "objects": scene.metadata(),
            "annotations": annotation_records,
            "depth_convention": "positive camera-space distance in scene units; background=0",
        }
        (self.metadata_dir / f"{sample_id}.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8")
        return sample_id
