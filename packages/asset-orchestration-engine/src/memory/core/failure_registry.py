from enum import Enum
from typing import List, Dict

class FailureCategory(str, Enum):
    PROPORTION = "PROPORTION"
    SILHOUETTE = "SILHOUETTE"
    GEOMETRY = "GEOMETRY"
    TOPOLOGY = "TOPOLOGY"
    MATERIAL = "MATERIAL"
    COLOR = "COLOR"
    UV = "UV"
    HIERARCHY = "HIERARCHY"
    COLLISION = "COLLISION"
    EXPORT = "EXPORT"

class FailureTypeRegistry:
    FAILURE_TAXONOMY: Dict[str, FailureCategory] = {
        "BLADE_TOO_SHORT": FailureCategory.PROPORTION,
        "BLADE_TOO_LONG": FailureCategory.PROPORTION,
        "GUARD_TOO_NARROW": FailureCategory.PROPORTION,
        "GRIP_TOO_THICK": FailureCategory.PROPORTION,
        "SILHOUETTE_MISMATCH": FailureCategory.SILHOUETTE,
        "MATERIAL_METALLIC_MISMATCH": FailureCategory.MATERIAL,
        "MATERIAL_ROUGHNESS_MISMATCH": FailureCategory.MATERIAL,
        "MISSING_REQUIRED_COMPONENTS": FailureCategory.HIERARCHY,
        "FORBIDDEN_COMPONENTS_DETECTED": FailureCategory.HIERARCHY,
        "NON_MANIFOLD_TOPOLOGY": FailureCategory.TOPOLOGY
    }

    @classmethod
    def get_category(cls, failure_type: str) -> FailureCategory:
        return cls.FAILURE_TAXONOMY.get(failure_type, FailureCategory.GEOMETRY)
