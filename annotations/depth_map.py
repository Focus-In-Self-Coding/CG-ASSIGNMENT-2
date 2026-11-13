"""Depth-buffer conversion utilities."""
import numpy as np


def depth_buffer_to_meters(depth_buffer: np.ndarray, near: float, far: float) -> np.ndarray:
    """Convert OpenGL depth [0,1] to positive camera-space distance.

    Pixels at the far/background depth are represented as 0.0 so they can be
    distinguished from valid geometry. The output is float32.
    """
    z = np.asarray(depth_buffer, dtype=np.float32)
    z_ndc = 2.0 * z - 1.0
    denom = far + near - z_ndc * (far - near)
    distance = (2.0 * near * far) / np.maximum(denom, 1e-8)
    distance = np.where(z >= 0.999999, 0.0, distance)
    return distance.astype(np.float32)


def depth_preview_u16(depth_meters: np.ndarray, max_depth: float | None = None) -> np.ndarray:
    """Make a 16-bit preview: near=bright, far=dark; zero remains background."""
    depth = np.asarray(depth_meters, dtype=np.float32)
    valid = depth > 0
    if not np.any(valid):
        return np.zeros(depth.shape, dtype=np.uint16)
    limit = float(max_depth or np.percentile(depth[valid], 99))
    limit = max(limit, 1e-6)
    normalized = np.zeros_like(depth, dtype=np.float32)
    normalized[valid] = 1.0 - np.clip(depth[valid] / limit, 0.0, 1.0)
    return np.round(normalized * 65535.0).astype(np.uint16)
