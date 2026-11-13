"""A renderable object plus annotation identity and transform."""
from __future__ import annotations
import glm


class SceneObject:
    def __init__(self, name, mesh, position=(0, 0, 0), rotation=(0, 0, 0),
                 scale=(1, 1, 1), class_id=0, color=(0.7, 0.7, 0.7), instance_id=1):
        self.name = str(name)
        self.mesh = mesh
        self.position = tuple(map(float, position))
        self.rotation = tuple(map(float, rotation))  # degrees: X, Y, Z
        self.scale = tuple(map(float, scale))
        self.class_id = int(class_id)
        self.color = tuple(map(float, color))
        self.instance_id = int(instance_id)
        if self.instance_id <= 0 or self.instance_id > 0xFFFFFF:
            raise ValueError("instance_id must be between 1 and 16,777,215")

    def model_matrix(self):
        matrix = glm.mat4(1.0)
        matrix = glm.translate(matrix, glm.vec3(*self.position))
        matrix = glm.rotate(matrix, glm.radians(self.rotation[0]), glm.vec3(1, 0, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation[1]), glm.vec3(0, 1, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation[2]), glm.vec3(0, 0, 1))
        matrix = glm.scale(matrix, glm.vec3(*self.scale))
        return matrix

    def instance_color(self):
        i = self.instance_id
        return ((i & 255) / 255.0, ((i >> 8) & 255) / 255.0,
                ((i >> 16) & 255) / 255.0)

    def metadata(self):
        return {"name": self.name, "instance_id": self.instance_id,
                "class_id": self.class_id, "position": list(self.position),
                "rotation_degrees": list(self.rotation), "scale": list(self.scale),
                "color": list(self.color), "mesh": self.mesh.name}
