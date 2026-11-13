# Computer Graphics – Assignment 2 Starter

A small, extendable **Python + PyOpenGL** starter for the HCMUT Computer Graphics Assignment 2: Synthetic Image Generator for Detection, Segmentation, and Depth Estimation.

This starter deliberately implements the graphics and label-generation pipeline itself. It does **not** use a game engine or a complete synthetic-dataset generator.

## What is included

- GLFW window and a programmable OpenGL 3.3 shader pipeline.
- Orbit-free first-person camera controls (WASD + mouse look).
- OBJ mesh loading and **ASCII PLY** mesh loading.
- A demo scene containing external OBJ models (`cube.obj`, `pyramid.obj`) and an ASCII PLY model (`example_ascii.ply`).
- Configurable object positions, rotations, scales, colors, and class IDs.
- Off-screen rendering for RGB images, instance-ID segmentation, and depth-buffer capture.
- Per-instance binary masks, YOLO-format bounding boxes, metric depth `.npy`, preview depth `.png`, and JSON scene metadata.
- Small unit tests for annotation and depth conversion helpers.

## 1. Windows setup (PowerShell)

Open PowerShell in this project folder:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

If PowerShell blocks activation, run this in the same PowerShell window and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.venv\Scripts\Activate.ps1
```

You need a graphics driver that supports OpenGL 3.3 or newer.

## 2. Run the demo

```powershell
python main.py
```

Controls:

- `W`, `A`, `S`, `D`: move the camera.
- `Q`, `E`: move down/up.
- Mouse: look around after pressing `ENTER` to capture the mouse; press `ESC` to release it.
- `X`: render and export one dataset sample.
- `ESC`: close the application.

The first successful capture is written under `output/` with matching sample names.

## 3. Run without the interactive window

This starter currently exports through the interactive OpenGL context. Start the app and press `X` after the demo scene appears.

## 4. Output layout

```text
output/
├── images/                 # RGB images
├── depth/
│   ├── *.npy               # metric depth in the camera/view direction
│   └── *.png               # normalized 16-bit depth preview
├── masks/
│   ├── instance_color/     # each instance has a unique RGB color
│   └── instances/          # one binary mask per visible instance
├── labels/                 # YOLO: class cx cy width height (normalized)
└── metadata/               # camera/object metadata for each sample
```

YOLO coordinates are normalized to `[0, 1]`. The mask image uses an instance ID encoded in RGB; the metadata maps instance IDs to class IDs and object names.

## 5. Add your own models and objects

1. Put `.obj` or ASCII `.ply` files in `assets/models/`.
2. Edit `scene/demo_scene.py` and add `SceneObject` instances.
3. Set `class_id` consistently for each semantic category.
4. Run the app and press `X` to export a sample.

Example:

```python
SceneObject(
    name="my_chair",
    mesh=load_mesh("assets/models/chair.obj"),
    position=(1.0, 0.0, -2.0),
    rotation=(0.0, 30.0, 0.0),
    scale=(1.0, 1.0, 1.0),
    class_id=2,
    color=(0.65, 0.35, 0.18),
)
```

## 6. Important limitations / next improvements

This is a **working starting point**, not a finished submission. In particular:

- The PLY loader currently supports ASCII PLY only. Binary PLY needs an additional parser or implementation.
- OBJ support covers vertex positions, optional vertex normals, and polygon triangulation; it does not yet handle material libraries (`.mtl`) or textures.
- The depth output is linearized camera-space depth from the OpenGL depth buffer; validate the numeric range and convention against your report requirements.
- The current demo uses simple directional-style lighting and solid object colors. Add texture loading, richer lighting, random scene generation, and camera variation as extensions.
- The renderer is intentionally compact. Add resize handling and stronger OpenGL resource cleanup before treating it as a final application.
- `cglibs` is not required by this starter; install/use it only if your course environment or instructor requires it.

The assignment PDF (v1.2) requires RGB images, bounding boxes, instance segmentation, and depth maps. It names COCO or YOLO as acceptable annotation formats. This starter exports YOLO detection labels and per-instance PNG masks.
