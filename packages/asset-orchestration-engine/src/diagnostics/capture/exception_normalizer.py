import re
from typing import Tuple
from ..core.failure_types import FailureType
from ..core.severity import FailureSeverity

class ExceptionNormalizer:
    """Normalizes disparate exception texts into canonical failure types, error codes, and patterns."""
    
    PATTERNS = [
        (r"non-uniform scale|scale x=.*y=.*z=|unapplied scale", FailureType.SCALE_ERROR, "ERR_SCALE_NON_UNIFORM", "Non-uniform object scale detected"),
        (r"axis mismatch|invalid orientation|forward axis", FailureType.AXIS_ERROR, "ERR_AXIS_ORIENTATION", "Forward/Up axis orientation invalid"),
        (r"pivot not at origin|invalid pivot|origin offset", FailureType.PIVOT_ERROR, "ERR_PIVOT_OFFSET", "Pivot is not centered at origin"),
        (r"non-manifold|loose vertices|inverted normals", FailureType.TOPOLOGY_ERROR, "ERR_TOPOLOGY_NON_MANIFOLD", "Non-manifold geometry or normal defect"),
        (r"missing material|shader compilation failed|missing texture", FailureType.MATERIAL_ERROR, "ERR_MATERIAL_MISSING", "Material shader or texture reference missing"),
        (r"missing uv|uv overlap|stretched uv", FailureType.UV_ERROR, "ERR_UV_UNWRAP", "UV mapping or overlap defect"),
        (r"missing lod|insufficient lod count", FailureType.LOD_ERROR, "ERR_LOD_COUNT", "Insufficient LOD levels generated"),
        (r"missing collision|collision hull invalid|ucx_", FailureType.COLLISION_ERROR, "ERR_COLLISION_INVALID", "Collision hull generation failed or invalid"),
        (r"governance denied|permission denied|unauthorized capability", FailureType.GOVERNANCE_DENIED, "ERR_GOVERNANCE_DENIED", "Operation denied by governance contract"),
        (r"blender crash|access violation|segmentation fault", FailureType.BLENDER_CRASH, "ERR_BLENDER_CRASH", "Blender process crash or access violation"),
        (r"golden integrity|manifest hash mismatch|golden modified", FailureType.GOLDEN_INTEGRITY_FAILURE, "ERR_GOLDEN_TAMPERED", "Golden asset cryptographic integrity violation"),
        (r"benchmark rejected|score below threshold|regression detected", FailureType.EVALUATION_FAILURE, "ERR_EVALUATION_FAILED", "Benchmark score below acceptance threshold"),
        (r"resource lock|lock busy|resource busy", FailureType.RESOURCE_LOCK_ERROR, "ERR_RESOURCE_LOCKED", "Resource locked by another agent")
    ]

    @classmethod
    def normalize(cls, raw_message: str) -> Tuple[FailureType, str, str, FailureSeverity]:
        raw_clean = str(raw_message).strip()
        raw_lower = raw_clean.lower()

        for pattern, f_type, err_code, norm_msg in cls.PATTERNS:
            if re.search(pattern, raw_lower):
                sev = FailureSeverity.CRITICAL if f_type in (
                    FailureType.BLENDER_CRASH, FailureType.GOLDEN_INTEGRITY_FAILURE, FailureType.GOVERNANCE_DENIED
                ) else FailureSeverity.ERROR
                return f_type, err_code, norm_msg, sev

        return FailureType.UNKNOWN, "ERR_GENERIC_FAILURE", raw_clean, FailureSeverity.ERROR
