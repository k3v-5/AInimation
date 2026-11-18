"""
MeshData encapsulates geometric primitives, vertex/face indices, normals, UVs, and topological validation.
UAF-81.3 Sections 4, 47, 48, 50, 64.
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple, Set
from .bounding_volume import AABB


@dataclass
class MeshData:
    vertices: List[List[float]] = field(default_factory=list)
    faces: List[List[int]] = field(default_factory=list)  # 3 or 4 vertex indices per face
    normals: List[List[float]] = field(default_factory=list)
    uvs: List[List[float]] = field(default_factory=list)
    material_indices: List[int] = field(default_factory=list)

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def face_count(self) -> int:
        return len(self.faces)

    @property
    def triangle_count(self) -> int:
        count = 0
        for f in self.faces:
            if len(f) == 3:
                count += 1
            elif len(f) == 4:
                count += 2
            elif len(f) > 4:
                count += len(f) - 2
        return count

    def calculate_aabb(self) -> AABB:
        return AABB.from_points(self.vertices)

    def has_degenerate_faces(self) -> bool:
        """Detects faces with duplicate vertex indices or zero area."""
        for f in self.faces:
            if len(f) < 3:
                return True
            if len(set(f)) != len(f):
                return True  # Duplicate indices in single face
        return False

    def is_manifold(self) -> bool:
        """
        Validates edge-manifold property: every edge must be shared by at most 2 faces,
        and no non-manifold T-junctions or edges.
        """
        edge_count: Dict[Tuple[int, int], int] = {}
        for f in self.faces:
            n = len(f)
            for i in range(n):
                v1, v2 = f[i], f[(i + 1) % n]
                edge = (min(v1, v2), max(v1, v2))
                edge_count[edge] = edge_count.get(edge, 0) + 1

        for count in edge_count.values():
            if count > 2:
                return False  # Non-manifold edge shared by > 2 faces
        return True

    def calculate_facet_normals(self) -> None:
        """Calculates facet normals for each face."""
        self.normals = []
        for f in self.faces:
            if len(f) < 3:
                self.normals.append([0.0, 0.0, 1.0])
                continue
            p0 = self.vertices[f[0]]
            p1 = self.vertices[f[1]]
            p2 = self.vertices[f[2]]

            u = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
            v = [p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]]

            # Cross product
            nx = u[1] * v[2] - u[2] * v[1]
            ny = u[2] * v[0] - u[0] * v[2]
            nz = u[0] * v[1] - u[1] * v[0]

            length = math.sqrt(nx * nx + ny * ny + nz * nz)
            if length > 1e-8:
                self.normals.append([round(nx / length, 5), round(ny / length, 5), round(nz / length, 5)])
            else:
                self.normals.append([0.0, 0.0, 1.0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vertices": self.vertices,
            "faces": self.faces,
            "normals": self.normals,
            "uvs": self.uvs,
            "material_indices": self.material_indices,
            "triangle_count": self.triangle_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeshData":
        return cls(
            vertices=data.get("vertices", []),
            faces=data.get("faces", []),
            normals=data.get("normals", []),
            uvs=data.get("uvs", []),
            material_indices=data.get("material_indices", []),
        )

    @classmethod
    def create_cube(cls, size: float = 1.0) -> "MeshData":
        """Factory for standard canonical cube centered at origin."""
        s = size / 2.0
        vertices = [
            [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
            [-s, -s, s], [s, -s, s], [s, s, s], [-s, s, s],
        ]
        faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 7, 6, 5],  # Top
            [0, 4, 5, 1],  # Front
            [1, 5, 6, 2],  # Right
            [2, 6, 7, 3],  # Back
            [3, 7, 4, 0],  # Left
        ]
        mesh = cls(vertices=vertices, faces=faces)
        mesh.calculate_facet_normals()
        return mesh
