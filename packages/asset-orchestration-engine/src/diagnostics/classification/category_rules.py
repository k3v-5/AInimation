from typing import Dict, Any, List
from ..core.failure_types import FailureType

class CategoryRules:
    """Rules mapping defect attributes and evidence fields to failure categories."""
    
    @staticmethod
    def classify_from_evidence(evidence: Dict[str, Any]) -> FailureType:
        # Check scale/transform
        scale = evidence.get("scale")
        if scale and (scale[0] != scale[1] or scale[1] != scale[2] or any(s != 1.0 for s in scale)):
            return FailureType.SCALE_ERROR

        # Check axis
        if evidence.get("invalid_scale_or_axis") or evidence.get("axis") not in (None, "X_FORWARD_Z_UP"):
            return FailureType.AXIS_ERROR

        # Check LODs
        if evidence.get("lod_count", 3) < 1:
            return FailureType.LOD_ERROR

        # Check collision
        if evidence.get("has_collision") is False or evidence.get("collision_hulls", 1) < 1:
            return FailureType.COLLISION_ERROR

        # Check materials
        mats = evidence.get("materials", [])
        if isinstance(mats, list) and len(mats) == 0:
            return FailureType.MATERIAL_ERROR

        # Check non-manifold
        if evidence.get("non_manifold_count", 0) > 0:
            return FailureType.TOPOLOGY_ERROR

        return FailureType.UNKNOWN
