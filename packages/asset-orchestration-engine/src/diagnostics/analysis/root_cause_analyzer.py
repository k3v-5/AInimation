import time
from typing import Dict, Any, List, Optional
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType
from ..core.diagnostic_models import RootCause, DiagnosticReport
from ..evidence.provenance import EvidenceItem
from .confidence_engine import ConfidenceEngine
from .impact_analyzer import ImpactAnalyzer

class RootCauseAnalyzer:
    """Analyzes failure records and evidence to determine true root causes and causal chains."""
    
    @classmethod
    def analyze(
        cls,
        failure: FailureRecord,
        evidence_items: Optional[List[EvidenceItem]] = None
    ) -> DiagnosticReport:
        f_type = failure.failure_type
        ev_ids = [e.evidence_id for e in evidence_items] if evidence_items else failure.evidence_ids

        # Analyze root cause mapping
        if f_type in (FailureType.SCALE_ERROR, FailureType.TRANSFORM_ERROR):
            category = "TRANSFORM"
            desc = "Object has non-uniform or unapplied scale transforms."
            rec_action = "FIX_SCALE"
            chain = [
                "Non-uniform scale present in Blender object",
                "Bounding box and collision hull calculation skewed",
                "Unreal Engine readiness validation failure",
                "Asset rejected by QA Benchmark"
            ]
        elif f_type in (FailureType.AXIS_ERROR, FailureType.PIVOT_ERROR):
            category = "AXIS_PIVOT"
            desc = "Asset orientation or pivot point is not aligned with Unreal standard."
            rec_action = "FIX_AXIS"
            chain = [
                "Object forward axis is not aligned to +X or pivot is offset",
                "Engine import alignment failure",
                "Asset rejected"
            ]
        elif f_type == FailureType.LOD_ERROR:
            category = "LOD"
            desc = "Insufficient LOD chain generated for performance profiling."
            rec_action = "REBUILD_LOD"
            chain = [
                "LOD generation skipped or aborted",
                "LOD count less than minimum threshold",
                "Optimization validation failure"
            ]
        elif f_type == FailureType.COLLISION_ERROR:
            category = "COLLISION"
            desc = "Missing or invalid collision primitives (UCX hulls)."
            rec_action = "REBUILD_COLLISION"
            chain = [
                "Collision generator not invoked or failed",
                "Missing UCX collision hull",
                "Engine readiness check failed"
            ]
        elif f_type == FailureType.MATERIAL_ERROR:
            category = "MATERIAL"
            desc = "Missing PBR material assignments or invalid shader parameters."
            rec_action = "REASSIGN_MATERIAL"
            chain = [
                "Material slots empty or textures unassigned",
                "Visual shading evaluator score dropped",
                "Benchmark rejected"
            ]
        elif f_type == FailureType.GOVERNANCE_DENIED:
            category = "GOVERNANCE"
            desc = "Agent contract does not authorize requested mutating tool or capability."
            rec_action = "REQUEST_AUTHORIZATION"
            chain = [
                "Agent attempted unauthorized mutation",
                "ToolGuard / GovernanceGuard blocked execution",
                "Operation aborted with GOVERNANCE_DENIED"
            ]
        elif f_type in (FailureType.BLENDER_CRASH, FailureType.CHECKPOINT_ERROR):
            category = "RECOVERY"
            desc = "Blender process crash or memory corruption during execution."
            rec_action = "RESTORE_CHECKPOINT"
            chain = [
                "Process crash or unexpected termination",
                "State left incomplete",
                "Recovery checkpoint required"
            ]
        else:
            category = "GENERAL"
            desc = failure.normalized_message or failure.message
            rec_action = "RETRY_OPERATION"
            chain = ["Unknown operational failure occurred", "Pipeline stopped"]

        conf_score = ConfidenceEngine.calculate_confidence(
            has_direct_evidence=bool(evidence_items),
            evidence_count=len(evidence_items) if evidence_items else 0,
            has_corroboration=True
        )

        root = RootCause(
            cause_id=f"CAUSE_{failure.failure_id}",
            category=category,
            description=desc,
            evidence_ids=ev_ids,
            affected_components=[category],
            confidence=conf_score,
            alternatives=[],
            causal_chain=chain
        )

        impact = ImpactAnalyzer.analyze_impact(failure.semantic_id, category)

        return DiagnosticReport(
            diagnosis_id=f"DIAG_{failure.failure_id}",
            failure_id=failure.failure_id,
            root_cause=root,
            alternative_causes=[],
            impacted_assets=[failure.semantic_id],
            invalidated_evaluations=impact["invalidated_evaluations"],
            recommended_action=rec_action,
            confidence=conf_score
        )
