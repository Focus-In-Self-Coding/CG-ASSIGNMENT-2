"""FPS-style camera used for both preview and annotation rendering."""
from __future__ import annotations
import math
import glfw
import glm


class Camera:
    def __init__(self, position=(0.0, 1.6, 6.0), aspect=16 / 9,
                 fov_degrees=50.0, near=0.1, far=100.0):
        self.position = glm.vec3(*position)
        self.world_up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = -10.0
        self.speed = 3.0
        self.sensitivity = 0.10
        self.fov = fov_degrees
        self.aspect = aspect
        self.near = near
        self.far = far
        self.front = glm.vec3(0.0, 0.0, -1.0)
        self.right = glm.vec3(1.0, 0.0, 0.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self._first_mouse = True
        self._last_x = 0.0
        self._last_y = 0.0
        self._update_vectors()

    def _update_vectors(self):
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        front = glm.vec3(math.cos(yaw) * math.cos(pitch), math.sin(pitch),
                         math.sin(yaw) * math.cos(pitch))
        self.front = glm.normalize(front)
        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))

    def on_mouse_move(self, _window, x, y):
        if self._first_mouse:
            self._last_x, self._last_y = x, y
            self._first_mouse = False
            return
        dx, dy = x - self._last_x, self._last_y - y
        self._last_x, self._last_y = x, y
        self.yaw += dx * self.sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch + dy * self.sensitivity))
        self._update_vectors()

    def process_keyboard(self, handle, dt):
        velocity = self.speed * dt
        if glfw.get_key(handle, glfw.KEY_W) == glfw.PRESS:
            self.position += self.front * velocity
        if glfw.get_key(handle, glfw.KEY_S) == glfw.PRESS:
            self.position -= self.front * velocity
        if glfw.get_key(handle, glfw.KEY_A) == glfw.PRESS:
            self.position -= self.right * velocity
        if glfw.get_key(handle, glfw.KEY_D) == glfw.PRESS:
            self.position += self.right * velocity
        if glfw.get_key(handle, glfw.KEY_E) == glfw.PRESS:
            self.position += self.world_up * velocity
        if glfw.get_key(handle, glfw.KEY_Q) == glfw.PRESS:
            self.position -= self.world_up * velocity

    def view_matrix(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def projection_matrix(self, aspect=None):
        return glm.perspective(glm.radians(self.fov), aspect or self.aspect,
                               self.near, self.far)

    def metadata(self):
        return {
            "position": [float(v) for v in self.position],
            "yaw_degrees": float(self.yaw),
            "pitch_degrees": float(self.pitch),
            "fov_degrees": float(self.fov),
            "near": float(self.near),
            "far": float(self.far),
            "aspect": float(self.aspect),
        }
