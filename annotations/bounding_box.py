"""Bounding-box helpers. Coordinates use top-left image origin."""
import numpy as np


def bbox_from_mask(mask: np.ndarray):
    ys, xs = np.where(np.asarray(mask, dtype=bool))
    if len(xs) == 0:
        return None
    x_min, x_max = int(xs.min()), int(xs.max())
    y_min, y_max = int(ys.min()), int(ys.max())
    return {"x_min": x_min, "y_min": y_min,
            "x_max": x_max, "y_max": y_max,
            "width": x_max - x_min + 1,
            "height": y_max - y_min + 1}


def bbox_to_yolo(bbox, image_width: int, image_height: int):
    if bbox is None:
        return None
    cx = (bbox["x_min"] + bbox["x_max"] + 1) / 2.0 / image_width
    cy = (bbox["y_min"] + bbox["y_max"] + 1) / 2.0 / image_height
    width = bbox["width"] / image_width
    height = bbox["height"] / image_height
    return (cx, cy, width, height)
