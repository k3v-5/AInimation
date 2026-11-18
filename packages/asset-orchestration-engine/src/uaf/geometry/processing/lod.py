"""
LOD (Level of Detail) chain generation and distance policy.
UAF-81.3 Sections 59, 60, 61.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from ..models.mesh_data import MeshData


@dataclass
class LODLevel:
    lod_index: int
    mesh: MeshData
    screen_size: float
    distance_meters: float
    triangle_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_index": self.lod_index,
            "screen_size": self.screen_size,
            "distance_meters": self.distance_meters,
            "triangle_count": self.triangle_count,
        }


@dataclass
class LODChain:
    levels: List[LODLevel] = field(default_factory=list)

    @property
    def lod_count(self) -> int:
        return len(self.levels)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lod_count": self.lod_count,
            "levels": [lvl.to_dict() for lvl in self.levels],
        }


class LODGenerator:
    """
    Synthesizes discrete LOD levels with progressive face reductions.
    """
    @classmethod
    def generate_lod_chain(
        cls,
        base_mesh: MeshData,
        lod_count: int = 4,
        reduction_per_level: float = 0.5,
    ) -> LODChain:
        chain = LODChain()
        # LOD0 is base mesh
        chain.levels.append(
            LODLevel(
                lod_index=0,
                mesh=base_mesh,
                screen_size=1.0,
                distance_meters=0.0,
                triangle_count=base_mesh.triangle_count,
            )
        )

        current_mesh = base_mesh
        for i in range(1, lod_count):
            target_faces = max(4, int(len(current_mesh.faces) * reduction_per_level))
            decimated_mesh = MeshData(
                vertices=list(current_mesh.vertices),
                faces=current_mesh.faces[:target_faces],
                normals=current_mesh.normals[:target_faces] if current_mesh.normals else [],
                uvs=list(current_mesh.uvs),
            )
            dist = round(15.0 * (2 ** (i - 1)), 1)
            screen_sz = round(1.0 / (2 ** i), 3)

            chain.levels.append(
                LODLevel(
                    lod_index=i,
                    mesh=decimated_mesh,
                    screen_size=screen_sz,
                    distance_meters=dist,
                    triangle_count=decimated_mesh.triangle_count,
                )
            )
            current_mesh = decimated_mesh

        return chain
