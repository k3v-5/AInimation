from typing import List, Dict, Any, Tuple
from ..core.surface_types import BakeChannelType, ColorSpaceType
from ..core.surface_schema import BakePlan, TextureRequirement

class BakingPlanner:
    @classmethod
    def generate_bake_and_texture_requirements(
        cls,
        semantic_id: str,
        resolution: int = 2048
    ) -> Tuple[BakePlan, List[TextureRequirement]]:
        bake = BakePlan(
            bake_id=f"BAKE_{semantic_id.upper()}",
            maps_to_bake=[BakeChannelType.NORMAL, BakeChannelType.AO, BakeChannelType.ORM, BakeChannelType.CURVATURE],
            resolution=resolution,
            format="TGA",
            bit_depth=16,
            orm_channels={"R": "AO", "G": "Roughness", "B": "Metallic"}
        )

        tex_reqs = [
            TextureRequirement(f"T_{semantic_id}_BaseColor", "BaseColor", resolution, "PNG", ColorSpaceType.SRGB, True),
            TextureRequirement(f"T_{semantic_id}_Normal", "Normal", resolution, "PNG", ColorSpaceType.NON_COLOR, True),
            TextureRequirement(f"T_{semantic_id}_ORM", "ORM", resolution, "PNG", ColorSpaceType.NON_COLOR, True),
            TextureRequirement(f"T_{semantic_id}_Emissive", "Emissive", resolution, "PNG", ColorSpaceType.SRGB, False)
        ]

        return bake, tex_reqs
