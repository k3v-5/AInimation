import time
from typing import Dict, Any, Optional
from .corrective_action import CorrectiveAction
from ..diagnosis.root_cause_analyzer import DiagnosticReport

class CorrectionPlanner:
    """Plans deterministic corrective actions based on root cause diagnostics."""

    @staticmethod
    def plan_correction(diagnostic: DiagnosticReport, target_asset: str) -> CorrectiveAction:
        rec_action = diagnostic.recommended_action
        risk = diagnostic.risk_level
        action_id = f"ACT_{rec_action}_{int(time.time()*1000)}"

        params: Dict[str, Any] = {}
        req_caps = ["CAP_GEOMETRY", "CAP_BLENDER"]

        if rec_action == "FIX_SCALE":
            params = {"apply_transforms": True, "target_scale": [1.0, 1.0, 1.0]}
            expected = "Uniform unit scale applied across all asset meshes"
        elif rec_action == "REASSIGN_MATERIAL":
            params = {"shader_type": "PrincipledBSDF", "assign_default": True}
            req_caps = ["CAP_MATERIAL", "CAP_BLENDER"]
            expected = "PBR PrincipledBSDF shader assigned to all active material slots"
        elif rec_action == "REBUILD_LOD":
            params = {"ratios": [0.6, 0.3, 0.1]}
            expected = "LOD1, LOD2, and LOD3 regenerated with proper decimation"
        elif rec_action == "REBUILD_COLLISION":
            params = {"hull_type": "UCX_CONVEX"}
            expected = "Simplified convex collision hulls generated for Unreal Engine"
        else:
            params = {"action": "RETRY"}
            expected = "Re-attempt operation with refreshed pipeline state"

        return CorrectiveAction(
            action_id=action_id,
            failure_id=diagnostic.failure_id,
            action_type=rec_action,
            target=target_asset,
            parameters=params,
            risk_level=risk,
            required_capabilities=req_caps,
            expected_effect=expected,
            validation_requirements=["F75_BENCHMARK", "F76_GOLDEN_CHECK"]
        )
