import numpy as np
from annotations.bounding_box import bbox_from_mask, bbox_to_yolo
from annotations.segmentation import decode_instance_ids, mask_for_instance
from annotations.depth_map import depth_buffer_to_meters


def test_bbox_and_yolo_coordinates():
    mask = np.zeros((10, 20), dtype=bool)
    mask[2:6, 4:10] = True
    bbox = bbox_from_mask(mask)
    assert bbox == {"x_min": 4, "y_min": 2, "x_max": 9, "y_max": 5,
                    "width": 6, "height": 4}
    cx, cy, w, h = bbox_to_yolo(bbox, 20, 10)
    assert np.allclose((cx, cy, w, h), (0.35, 0.4, 0.3, 0.4))


def test_instance_id_round_trip():
    rgb = np.array([[[1, 0, 0], [2, 0, 0], [1, 0, 0]]], dtype=np.uint8)
    ids = decode_instance_ids(rgb)
    assert ids.tolist() == [[1, 2, 1]]
    assert mask_for_instance(ids, 2).tolist() == [[False, True, False]]


def test_depth_conversion_background_is_zero():
    depth = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
    meters = depth_buffer_to_meters(depth, near=0.1, far=100.0)
    assert np.isclose(meters[0, 0], 0.1)
    assert meters[0, 1] > meters[0, 0]
    assert meters[0, 2] == 0.0
