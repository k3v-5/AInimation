import re
from typing import Dict, Any, Tuple, Optional
from .failure_types import FailureType, FailureSeverity

class FailureClassifier:
    """Deterministic classifier mapping error messages, stack traces, and evidence to FailureTypes."""

    RULES = [
        (r"non-uniform scale|scale x=.*y=.*z=|unapplied scale", FailureType.SCALE_ERROR, "TRANSFORM", FailureSeverity.ERROR),
        (r"axis mismatch|invalid orientation|forward axis", FailureType.AXIS_ERROR, "TRANSFORM", FailureSeverity.ERROR),
        (r"non-manifold|loose vertices|inverted normals", FailureType.TOPOLOGY_ERROR, "GEOMETRY", FailureSeverity.ERROR),
        (r"geometry error|mesh invalid|degenerate face", FailureType.GEOMETRY_ERROR, "GEOMETRY", FailureSeverity.ERROR),
        (r"missing material|shader compilation failed|missing texture", FailureType.MATERIAL_ERROR, "MATERIAL", FailureSeverity.ERROR),
        (r"missing uv|uv overlap|stretched uv", FailureType.UV_ERROR, "MATERIAL", FailureSeverity.ERROR),
        (r"missing lod|insufficient lod count", FailureType.LOD_ERROR, "LOD", FailureSeverity.ERROR),
        (r"missing collision|collision hull invalid|ucx_", FailureType.COLLISION_ERROR, "COLLISION", FailureSeverity.ERROR),
        (r"governance denied|permission denied|unauthorized capability", FailureType.GOVERNANCE_ERROR, "GOVERNANCE", FailureSeverity.CRITICAL),
        (r"blender crash|access violation|segmentation fault", FailureType.BLENDER_CRASH, "BLENDER", FailureSeverity.FATAL),
        (r"blender timeout|execution timed out", FailureType.BLENDER_TIMEOUT, "BLENDER", FailureSeverity.CRITICAL),
        (r"golden integrity|manifest hash mismatch|golden modified", FailureType.REGRESSION_ERROR, "GOLDEN", FailureSeverity.CRITICAL),
        (r"benchmark rejected|score below threshold", FailureType.BENCHMARK_ERROR, "EVALUATION", FailureSeverity.ERROR),
        (r"duplicate asset|idempotency failed", FailureType.DUPLICATION_ERROR, "IDENTITY", FailureSeverity.ERROR),
        (r"checkpoint error|recovery failed", FailureType.RECOVERY_ERROR, "RECOVERY", FailureSeverity.CRITICAL)
    ]

    @classmethod
    def classify(cls, message: str, evidence: Optional[Dict[str, Any]] = None) -> Tuple[FailureType, str, FailureSeverity]:
        if evidence:
            scale = evidence.get("scale")
            if scale and (scale[0] != scale[1] or scale[1] != scale[2] or any(s != 1.0 for s in scale)):
                return FailureType.SCALE_ERROR, "TRANSFORM", FailureSeverity.ERROR

            if evidence.get("invalid_scale_or_axis") or evidence.get("axis") not in (None, "X_FORWARD_Z_UP"):
                return FailureType.AXIS_ERROR, "TRANSFORM", FailureSeverity.ERROR

            if evidence.get("lod_count", 3) < 1:
                return FailureType.LOD_ERROR, "LOD", FailureSeverity.ERROR

            if evidence.get("has_collision") is False or evidence.get("collision_hulls", 1) < 1:
                return FailureType.COLLISION_ERROR, "COLLISION", FailureSeverity.ERROR

            mats = evidence.get("materials", [])
            if isinstance(mats, list) and len(mats) == 0:
                return FailureType.MATERIAL_ERROR, "MATERIAL", FailureSeverity.ERROR

        raw_lower = str(message).lower()
        for pattern, f_type, cat, sev in cls.RULES:
            if re.search(pattern, raw_lower):
                return f_type, cat, sev

        return FailureType.UNKNOWN_ERROR, "GENERAL", FailureSeverity.ERROR
