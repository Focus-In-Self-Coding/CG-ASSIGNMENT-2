"""Small GLFW window wrapper."""
from __future__ import annotations
import glfw


class Window:
    def __init__(self, width: int, height: int, title: str):
        if not glfw.init():
            raise RuntimeError("Could not initialize GLFW. Check your graphics driver/display.")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        self.handle = glfw.create_window(width, height, title, None, None)
        if not self.handle:
            glfw.terminate()
            raise RuntimeError("Could not create an OpenGL 3.3 window.")
        glfw.make_context_current(self.handle)
        glfw.swap_interval(1)
        self.width, self.height = width, height
        self.mouse_captured = False
        self._last_time = glfw.get_time()
        glfw.set_input_mode(self.handle, glfw.STICKY_KEYS, glfw.TRUE)

    def set_key_callback(self, callback):
        glfw.set_key_callback(self.handle, callback)

    def set_cursor_callback(self, callback):
        glfw.set_cursor_pos_callback(self.handle, callback)

    def set_mouse_capture(self, captured: bool):
        self.mouse_captured = captured
        mode = glfw.CURSOR_DISABLED if captured else glfw.CURSOR_NORMAL
        glfw.set_input_mode(self.handle, glfw.CURSOR, mode)

    def tick(self) -> float:
        glfw.poll_events()
        now = glfw.get_time()
        dt = min(now - self._last_time, 0.1)
        self._last_time = now
        return dt

    def should_close(self) -> bool:
        return glfw.window_should_close(self.handle)

    def swap_buffers(self):
        glfw.swap_buffers(self.handle)

    def close(self):
        if self.handle:
            glfw.destroy_window(self.handle)
            self.handle = None
        glfw.terminate()
