"""Minimal OBJ and ASCII PLY triangle-mesh loaders (no external renderer)."""
from __future__ import annotations
from pathlib import Path
import numpy as np
from scene.mesh import Mesh


def _triangle_normal(a, b, c):
    n = np.cross(b - a, c - a)
    length = np.linalg.norm(n)
    return n / length if length > 1e-12 else np.array([0.0, 1.0, 0.0])


def _make_mesh(triangles, name):
    packed = []
    for tri in triangles:
        a, b, c = [np.asarray(v, dtype=np.float32) for v in tri]
        face_normal = _triangle_normal(a[:3], b[:3], c[:3])
        for vertex in (a, b, c):
            normal = vertex[3:6] if len(vertex) >= 6 and np.linalg.norm(vertex[3:6]) > 1e-8 else face_normal
            packed.append(np.concatenate((vertex[:3], normal)))
    return Mesh(np.asarray(packed, dtype=np.float32), name=name)


def load_obj(path: str | Path) -> Mesh:
    path = Path(path)
    positions, normals, triangles = [], [], []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "v" and len(parts) >= 4:
            positions.append(np.array(list(map(float, parts[1:4])), dtype=np.float32))
        elif parts[0] == "vn" and len(parts) >= 4:
            normals.append(np.array(list(map(float, parts[1:4])), dtype=np.float32))
        elif parts[0] == "f" and len(parts) >= 4:
            face = []
            for token in parts[1:]:
                values = token.split("/")
                vi = int(values[0])
                vi = vi - 1 if vi > 0 else len(positions) + vi
                ni = None
                if len(values) >= 3 and values[2]:
                    ni = int(values[2])
                    ni = ni - 1 if ni > 0 else len(normals) + ni
                if vi < 0 or vi >= len(positions):
                    raise ValueError(f"Invalid vertex index at {path}:{line_no}")
                point = positions[vi]
                normal = normals[ni] if ni is not None and 0 <= ni < len(normals) else np.zeros(3, dtype=np.float32)
                face.append(np.concatenate((point, normal)))
            # Fan triangulation supports convex polygons; concave polygons need a better triangulator.
            for i in range(1, len(face) - 1):
                triangles.append((face[0], face[i], face[i + 1]))
    if not triangles:
        raise ValueError(f"No faces found in OBJ file: {path}")
    return _make_mesh(triangles, path.stem)


def load_ascii_ply(path: str | Path) -> Mesh:
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        if f.readline().strip() != "ply":
            raise ValueError(f"Not a PLY file: {path}")
        vertex_count = face_count = 0
        vertex_properties = []
        current_element = None
        fmt = None
        while True:
            line = f.readline()
            if not line:
                raise ValueError(f"Unexpected EOF in PLY header: {path}")
            parts = line.strip().split()
            if not parts:
                continue
            if parts[0] == "format":
                fmt = parts[1]
            elif parts[0] == "element":
                current_element = parts[1]
                if current_element == "vertex": vertex_count = int(parts[2])
                if current_element == "face": face_count = int(parts[2])
            elif parts[0] == "property" and current_element == "vertex":
                vertex_properties.append(parts[-1])
            elif parts[0] == "end_header":
                break
        if fmt != "ascii":
            raise ValueError("This starter supports ASCII PLY only; binary PLY is not implemented yet.")
        required = ["x", "y", "z"]
        if not all(k in vertex_properties for k in required):
            raise ValueError("PLY vertex properties must include x, y, z")
        index = {name: i for i, name in enumerate(vertex_properties)}
        vertices = []
        for _ in range(vertex_count):
            values = list(map(float, f.readline().split()))
            xyz = [values[index[k]] for k in ("x", "y", "z")]
            nrm = [values[index[k]] for k in ("nx", "ny", "nz")] if all(k in index for k in ("nx", "ny", "nz")) else [0, 0, 0]
            vertices.append(np.array(xyz + nrm, dtype=np.float32))
        triangles = []
        for _ in range(face_count):
            values = list(map(int, f.readline().split()))
            count, face = values[0], values[1:1 + values[0]]
            if count < 3:
                continue
            if min(face) < 0 or max(face) >= len(vertices):
                raise ValueError("PLY face references an invalid vertex")
            for i in range(1, count - 1):
                triangles.append((vertices[face[0]], vertices[face[i]], vertices[face[i + 1]]))
    if not triangles:
        raise ValueError(f"No faces found in PLY file: {path}")
    return _make_mesh(triangles, path.stem)


def load_mesh(path: str | Path) -> Mesh:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        return load_obj(path)
    if suffix == ".ply":
        return load_ascii_ply(path)
    raise ValueError(f"Unsupported model format '{suffix}'. Expected .obj or .ply")
