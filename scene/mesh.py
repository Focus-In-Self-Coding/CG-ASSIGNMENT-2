"""CPU mesh data and lazy OpenGL upload."""
from __future__ import annotations
import ctypes
import numpy as np
from OpenGL.GL import *


class Mesh:
    def __init__(self, vertices: np.ndarray, name="mesh"):
        vertices = np.asarray(vertices, dtype=np.float32)
        if vertices.ndim != 2 or vertices.shape[1] != 6:
            raise ValueError("Mesh vertices must be an Nx6 array: position xyz + normal xyz")
        if len(vertices) == 0:
            raise ValueError("Mesh has no triangle vertices")
        self.vertices = np.ascontiguousarray(vertices)
        self.name = name
        self.vao = 0
        self.vbo = 0

    def upload(self):
        if self.vao:
            return
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        stride = 6 * self.vertices.itemsize
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride,
                              ctypes.c_void_p(3 * self.vertices.itemsize))
        glBindVertexArray(0)

    def draw(self):
        self.upload()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        glBindVertexArray(0)

    def close(self):
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = 0
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = 0
