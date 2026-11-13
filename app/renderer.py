"""OpenGL renderer with RGB, instance-ID, and depth capture passes."""
from __future__ import annotations
from pathlib import Path
import ctypes
import numpy as np
from OpenGL.GL import *
import glm

from scene.mesh import Mesh
from annotations.depth_map import depth_buffer_to_meters


class Renderer:
    def __init__(self, width: int, height: int, shader_dir: Path):
        self.width, self.height = width, height
        self.shader_dir = Path(shader_dir)
        self.rgb_program = self._create_program("vertex.glsl", "fragment.glsl")
        self.seg_program = self._create_program("vertex.glsl", "segmentation.glsl")
        self._create_framebuffer()
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glDisable(GL_CULL_FACE)

    def _read_shader(self, name):
        return (self.shader_dir / name).read_text(encoding="utf-8")

    def _compile_shader(self, source, kind):
        shader = glCreateShader(kind)
        glShaderSource(shader, source)
        glCompileShader(shader)
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            message = glGetShaderInfoLog(shader).decode("utf-8", errors="replace")
            raise RuntimeError(f"Shader compilation failed ({kind}):\n{message}")
        return shader

    def _create_program(self, vertex_name, fragment_name):
        vs = self._compile_shader(self._read_shader(vertex_name), GL_VERTEX_SHADER)
        fs = self._compile_shader(self._read_shader(fragment_name), GL_FRAGMENT_SHADER)
        program = glCreateProgram()
        glAttachShader(program, vs)
        glAttachShader(program, fs)
        glLinkProgram(program)
        glDeleteShader(vs)
        glDeleteShader(fs)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            message = glGetProgramInfoLog(program).decode("utf-8", errors="replace")
            raise RuntimeError(f"Shader link failed:\n{message}")
        return program

    def _create_framebuffer(self):
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        self.color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.color_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, self.width, self.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                                GL_TEXTURE_2D, self.color_texture, 0)

        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32F, self.width,
                     self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                GL_TEXTURE_2D, self.depth_texture, 0)

        glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer is incomplete: 0x{status:x}")

    @staticmethod
    def _uniform(program, name):
        return glGetUniformLocation(program, name)

    def _mat4(self, program, name, matrix):
        glUniformMatrix4fv(self._uniform(program, name), 1, GL_FALSE,
                           glm.value_ptr(matrix))

    def _render_scene(self, scene, camera, program, segmentation=False):
        glUseProgram(program)
        view = camera.view_matrix()
        projection = camera.projection_matrix(self.width / self.height)
        self._mat4(program, "u_view", view)
        self._mat4(program, "u_projection", projection)
        if not segmentation:
            glUniform3f(self._uniform(program, "u_light_pos"), 3.5, 6.0, 4.0)
            glUniform3f(self._uniform(program, "u_view_pos"),
                        camera.position.x, camera.position.y, camera.position.z)
            glUniform3f(self._uniform(program, "u_light_color"), 1.0, 1.0, 1.0)

        for obj in scene.objects:
            model = obj.model_matrix()
            self._mat4(program, "u_model", model)
            if segmentation:
                r, g, b = obj.instance_color()
                glUniform3f(self._uniform(program, "u_object_color"), r, g, b)
            else:
                glUniform3f(self._uniform(program, "u_color"), *obj.color)
            obj.mesh.draw()
        glUseProgram(0)

    def _begin_offscreen(self, clear_color=(0.055, 0.065, 0.085, 1.0)):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)
        glClearColor(*clear_color)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def _blit_to_screen(self, window_width=None, window_height=None):
        ww = window_width or self.width
        wh = window_height or self.height
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.fbo)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
        glBlitFramebuffer(0, 0, self.width, self.height, 0, 0, ww, wh,
                          GL_COLOR_BUFFER_BIT, GL_NEAREST)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def render_to_window(self, scene, camera, window_width=None, window_height=None):
        self._begin_offscreen()
        self._render_scene(scene, camera, self.rgb_program, segmentation=False)
        self._blit_to_screen(window_width, window_height)

    def _read_color(self):
        raw = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        image = np.frombuffer(raw, dtype=np.uint8).reshape(self.height, self.width, 4)
        return np.flipud(image[:, :, :3]).copy()

    def _read_depth(self):
        raw = glReadPixels(0, 0, self.width, self.height, GL_DEPTH_COMPONENT, GL_FLOAT)
        depth = np.frombuffer(raw, dtype=np.float32).reshape(self.height, self.width)
        return np.flipud(depth).copy()

    def capture(self, scene, camera):
        """Render and return arrays with top-left image origin."""
        self._begin_offscreen()
        self._render_scene(scene, camera, self.rgb_program, segmentation=False)
        glFinish()
        rgb = self._read_color()
        depth_buffer = self._read_depth()
        depth_meters = depth_buffer_to_meters(depth_buffer, camera.near, camera.far)

        # Render a second pass where every object has a unique integer ID encoded as RGB.
        glDisable(GL_DITHER)
        glDisable(GL_BLEND)
        self._begin_offscreen(clear_color=(0.0, 0.0, 0.0, 1.0))
        self._render_scene(scene, camera, self.seg_program, segmentation=True)
        glFinish()
        segmentation = self._read_color()
        glEnable(GL_DITHER)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return {"rgb": rgb, "depth_meters": depth_meters,
                "depth_buffer": depth_buffer, "segmentation": segmentation}

    def close(self):
        for program in (getattr(self, "rgb_program", 0), getattr(self, "seg_program", 0)):
            if program:
                glDeleteProgram(program)
        for name in ("color_texture", "depth_texture"):
            value = getattr(self, name, 0)
            if value:
                glDeleteTextures([value])
        if getattr(self, "fbo", 0):
            glDeleteFramebuffers(1, [self.fbo])
