"""Entry point for the Assignment 2 synthetic image generator starter."""
from __future__ import annotations

import argparse
from pathlib import Path

import glfw

from app.window import Window
from app.renderer import Renderer
from app.camera import Camera
from dataset.exporter import DatasetExporter
from scene.demo_scene import create_demo_scene


def parse_args():
    parser = argparse.ArgumentParser(description="Synthetic image generator starter")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--output", type=Path, default=Path("output"))
    return parser.parse_args()


def main():
    args = parse_args()
    window = Window(args.width, args.height, "CG Assignment 2 - Synthetic Image Generator")
    camera = Camera(aspect=args.width / args.height)
    scene = create_demo_scene()
    renderer = Renderer(args.width, args.height, Path(__file__).parent / "shaders")
    exporter = DatasetExporter(args.output)
    capture_requested = {"value": False}

    def on_key(handle, key, _scancode, action, _mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            # First ESC releases the mouse; a second ESC closes the app.
            if window.mouse_captured:
                window.set_mouse_capture(False)
            else:
                glfw.set_window_should_close(handle, True)
        elif key == glfw.KEY_X and action == glfw.PRESS:
            capture_requested["value"] = True
        elif key == glfw.KEY_ENTER and action == glfw.PRESS:
            window.set_mouse_capture(True)

    window.set_key_callback(on_key)
    def on_cursor_move(handle, x, y):
        if window.mouse_captured:
            camera.on_mouse_move(handle, x, y)
        else:
            camera._first_mouse = True

    window.set_cursor_callback(on_cursor_move)

    print("\nControls: WASD move | Q/E down/up | mouse look | ENTER capture mouse")
    print("Press X to export RGB + depth + segmentation + YOLO labels; ESC releases mouse/closes.\n")

    try:
        while not window.should_close():
            dt = window.tick()
            camera.process_keyboard(window.handle, dt)
            renderer.render_to_window(scene, camera, window.width, window.height)

            if capture_requested["value"]:
                capture_requested["value"] = False
                sample = renderer.capture(scene, camera)
                sample_id = exporter.save_sample(sample, scene, camera)
                print(f"Saved dataset sample: {sample_id} -> {args.output.resolve()}")

            window.swap_buffers()
    finally:
        renderer.close()
        window.close()


if __name__ == "__main__":
    main()
