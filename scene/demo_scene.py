"""Build a deterministic scene from the sample external OBJ assets."""
from pathlib import Path
from scene.model_loader import load_mesh
from scene.scene_object import SceneObject
from scene.scene_manager import SceneManager


ROOT = Path(__file__).resolve().parents[1]


def create_demo_scene():
    models = ROOT / "assets" / "models"
    cube = load_mesh(models / "cube.obj")
    pyramid = load_mesh(models / "pyramid.obj")
    ply_example = load_mesh(models / "example_ascii.ply")
    objects = [
        SceneObject("blue_cube", cube, position=(-1.1, 0.0, 0.0),
                    scale=(1.0, 1.0, 1.0), class_id=0,
                    color=(0.18, 0.48, 0.86), instance_id=1),
        SceneObject("orange_pyramid", pyramid, position=(1.15, 0.0, -0.3),
                    rotation=(0.0, 22.0, 0.0), scale=(1.0, 1.2, 1.0),
                    class_id=1, color=(0.92, 0.42, 0.12), instance_id=2),
        SceneObject("green_ply_model", ply_example, position=(0.0, 0.0, -1.6),
                    rotation=(0.0, 15.0, 0.0), scale=(0.85, 0.85, 0.85),
                    class_id=2, color=(0.20, 0.72, 0.42), instance_id=3),
    ]
    return SceneManager(objects)
