"""Decode RGB instance-ID segmentation images into masks."""
import numpy as np


def decode_instance_ids(rgb_image: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb_image, dtype=np.uint32)
    return rgb[..., 0] | (rgb[..., 1] << 8) | (rgb[..., 2] << 16)


def mask_for_instance(id_map: np.ndarray, instance_id: int) -> np.ndarray:
    return np.asarray(id_map) == int(instance_id)
