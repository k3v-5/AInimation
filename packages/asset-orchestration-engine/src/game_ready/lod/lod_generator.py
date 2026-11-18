from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any
from .lod_profile import GameReadyLODProfile
from ..optimization.mesh_decimator import MeshDecimator
from ...geometry.generators.base_generator import GeneratedGeometry

@dataclass
class GeneratedLODLevel:
    level: int
    screen_size: float
    components_geometry: Dict[str, GeneratedGeometry]
    total_triangles: int
    visual_deviation: float

class LODGenerator:
    @staticmethod
    def generate_lods(
        source_components: Dict[str, GeneratedGeometry],
        profile: GameReadyLODProfile
    ) -> List[GeneratedLODLevel]:
        lods: List[GeneratedLODLevel] = []

        for lvl, cfg in sorted(profile.levels.items()):
            lvl_geos: Dict[str, GeneratedGeometry] = {}
            total_tris = 0
            max_dev = 0.0

            for cid, geo in source_components.items():
                if cfg.level == 0:
                    dec_geo = geo
                    dev = 0.0
                else:
                    dec_geo, dev = MeshDecimator.decimate_geometry(
                        geo, cfg.reduction_ratio, cfg.max_visual_deviation
                    )
                lvl_geos[cid] = dec_geo
                total_tris += dec_geo.triangle_count
                max_dev = max(max_dev, dev)

            lods.append(GeneratedLODLevel(
                level=cfg.level,
                screen_size=cfg.screen_size,
                components_geometry=lvl_geos,
                total_triangles=total_tris,
                visual_deviation=max_dev
            ))

        return lods
