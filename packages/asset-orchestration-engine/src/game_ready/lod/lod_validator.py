from typing import Tuple, Optional, List
from .lod_generator import GeneratedLODLevel
from .lod_profile import GameReadyLODProfile

class LODValidator:
    @staticmethod
    def validate_lods(
        lods: List[GeneratedLODLevel],
        profile: GameReadyLODProfile
    ) -> Tuple[bool, Optional[str]]:
        for lod in lods:
            cfg = profile.levels.get(lod.level)
            if cfg:
                if lod.total_triangles > cfg.max_triangles:
                    return False, f"POLYGON_BUDGET_EXCEEDED: LOD{lod.level} has {lod.total_triangles} triangles, exceeding budget limit of {cfg.max_triangles}."
                if lod.visual_deviation > cfg.max_visual_deviation + 0.001:
                    return False, f"VISUAL_DEVIATION_EXCEEDED: LOD{lod.level} visual deviation ({lod.visual_deviation}) exceeds limit ({cfg.max_visual_deviation})."

        return True, None
