from typing import Dict, Any, List
from ..core.diagnostic_models import DiagnosticReport
from .corrective_action import CorrectiveAction

class CorrectionPlanner:
    """Plans deterministic corrective actions based on diagnostic reports without random guesses."""
    
    @staticmethod
    def plan_correction(report: DiagnosticReport, semantic_id: str) -> CorrectiveAction:
        act_type = report.recommended_action
        f_id = report.failure_id

        if act_type == "FIX_SCALE":
            return CorrectiveAction(
                action_id=f"ACT_SCALE_{f_id}",
                failure_id=f_id,
                action_type="FIX_SCALE",
                target=semantic_id,
                parameters={"apply_scale": True, "target_scale": [1.0, 1.0, 1.0]},
                risk_level="LOW",
                required_capabilities=["CAP_GEOMETRY", "CAP_BLENDER"],
                expected_effect="Reset and apply uniform scale (1.0, 1.0, 1.0) on all mesh objects.",
                validation_requirements=["F75_BENCHMARK", "F76_GOLDEN_COMPARE"]
            )
        elif act_type == "FIX_AXIS":
            return CorrectiveAction(
                action_id=f"ACT_AXIS_{f_id}",
                failure_id=f_id,
                action_type="FIX_AXIS",
                target=semantic_id,
                parameters={"target_axis": "X_FORWARD_Z_UP"},
                risk_level="LOW",
                required_capabilities=["CAP_GEOMETRY", "CAP_BLENDER"],
                expected_effect="Align primary forward vector to +X and up vector to +Z.",
                validation_requirements=["F75_BENCHMARK"]
            )
        elif act_type == "REBUILD_LOD":
            return CorrectiveAction(
                action_id=f"ACT_LOD_{f_id}",
                failure_id=f_id,
                action_type="REBUILD_LOD",
                target=semantic_id,
                parameters={"target_lods": 3, "decimate_ratios": [0.5, 0.25]},
                risk_level="LOW",
                required_capabilities=["CAP_GEOMETRY", "CAP_BLENDER"],
                expected_effect="Generate complete LOD0, LOD1, LOD2 mesh chain.",
                validation_requirements=["F75_BENCHMARK"]
            )
        elif act_type == "REBUILD_COLLISION":
            return CorrectiveAction(
                action_id=f"ACT_COL_{f_id}",
                failure_id=f_id,
                action_type="REBUILD_COLLISION",
                target=semantic_id,
                parameters={"hull_type": "UCX_CONVEX"},
                risk_level="LOW",
                required_capabilities=["CAP_GEOMETRY", "CAP_BLENDER"],
                expected_effect="Generate simplified UCX convex collision hulls.",
                validation_requirements=["F75_BENCHMARK"]
            )
        elif act_type == "REASSIGN_MATERIAL":
            return CorrectiveAction(
                action_id=f"ACT_MAT_{f_id}",
                failure_id=f_id,
                action_type="REASSIGN_MATERIAL",
                target=semantic_id,
                parameters={"materials": ["M_Dark_Titanium", "M_Matte_Carbon"]},
                risk_level="LOW",
                required_capabilities=["CAP_MATERIAL", "CAP_BLENDER"],
                expected_effect="Assign default tactical PBR materials.",
                validation_requirements=["F75_BENCHMARK"]
            )
        elif act_type == "RESTORE_CHECKPOINT":
            return CorrectiveAction(
                action_id=f"ACT_RESTORE_{f_id}",
                failure_id=f_id,
                action_type="RESTORE_CHECKPOINT",
                target=semantic_id,
                risk_level="MEDIUM",
                required_capabilities=["CAP_RECOVERY"],
                expected_effect="Restore last consistent checkpoint and restart clean process.",
                validation_requirements=["F70_RECOVERY_VERIFY"]
            )

        return CorrectiveAction(
            action_id=f"ACT_RETRY_{f_id}",
            failure_id=f_id,
            action_type="RETRY_OPERATION",
            target=semantic_id,
            risk_level="HIGH",
            required_capabilities=["CAP_BLENDER"],
            expected_effect="Retry operation after cleaning temporary cache.",
            validation_requirements=["F75_BENCHMARK"]
        )
