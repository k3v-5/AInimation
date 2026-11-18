import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from ..core.failure_models import FailureRecord
from ..core.failure_types import FailureType
from .confidence_engine import ConfidenceEngine

@dataclass
class RootCause:
    cause_id: str
    category: str
    description: str
    evidence_ids: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    confidence: float = 0.90
    alternatives: List[str] = field(default_factory=list)
    causal_chain: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cause_id": self.cause_id,
            "category": self.category,
            "description": self.description,
            "evidence_ids": self.evidence_ids,
            "affected_components": self.affected_components,
            "confidence": round(self.confidence, 4),
            "alternatives": self.alternatives,
            "causal_chain": self.causal_chain
        }

@dataclass
class DiagnosticReport:
    report_id: str
    failure_id: str
    semantic_id: str
    root_cause: RootCause
    confidence: float = 0.90
    dependencies: List[str] = field(default_factory=list)
    recommended_action: str = "RETRY"
    risk_level: str = "LOW"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "failure_id": self.failure_id,
            "semantic_id": self.semantic_id,
            "root_cause": self.root_cause.to_dict(),
            "confidence": round(self.confidence, 4),
            "dependencies": self.dependencies,
            "recommended_action": self.recommended_action,
            "risk_level": self.risk_level,
            "timestamp": self.timestamp
        }

class RootCauseAnalyzer:
    """Analyzes failures to differentiate symptoms from primary root causes."""

    @classmethod
    def analyze(cls, failure: FailureRecord, evidence_items: Optional[List[Dict[str, Any]]] = None) -> DiagnosticReport:
        f_type = failure.failure_type
        ev_ids = [e.get("evidence_id", "EV_GENERIC") for e in (evidence_items or [])]
        has_blender = any("BLENDER" in str(e) for e in (evidence_items or []))
        
        conf = ConfidenceEngine.calculate_confidence(
            has_blender_evidence=has_blender,
            has_benchmark_score=bool(failure.actual_state),
            has_stack_trace=bool(failure.stack_trace)
        )

        if f_type in (FailureType.SCALE_ERROR, FailureType.TRANSFORM_ERROR):
            rc = RootCause(
                cause_id=f"RC_SCALE_{failure.failure_id}",
                category="TRANSFORM",
                description="Object has non-uniform or unapplied scale transforms.",
                evidence_ids=ev_ids,
                affected_components=["Body", "Collision_UCX", "LODs"],
                confidence=conf,
                alternatives=["Modifier distortion", "Pivot misalignment"],
                causal_chain=[
                    "Non-uniform scale present in Blender object",
                    "Bounding box and collision hull calculation skewed",
                    "Unreal Engine readiness validation failure",
                    "Asset rejected by QA Benchmark"
                ]
            )
            rec_action = "FIX_SCALE"
            risk = "LOW"
        elif f_type in (FailureType.MATERIAL_ERROR, FailureType.SHADER_ERROR):
            rc = RootCause(
                cause_id=f"RC_MAT_{failure.failure_id}",
                category="MATERIAL",
                description="Missing PBR material assignments or invalid shader parameters.",
                evidence_ids=ev_ids,
                affected_components=["Materials", "Shaders"],
                confidence=conf,
                alternatives=["Missing texture map", "Unassigned material slot"],
                causal_chain=[
                    "Missing material slot in mesh geometry",
                    "Engine readiness detects empty shader assignment",
                    "Visual Critic Benchmark rejection"
                ]
            )
            rec_action = "REASSIGN_MATERIAL"
            risk = "LOW"
        elif f_type == FailureType.LOD_ERROR:
            rc = RootCause(
                cause_id=f"RC_LOD_{failure.failure_id}",
                category="LOD",
                description="LOD hierarchy missing or decimation ratio insufficient.",
                evidence_ids=ev_ids,
                affected_components=["LOD1", "LOD2", "LOD3"],
                confidence=conf,
                alternatives=["Decimate modifier unapplied"],
                causal_chain=[
                    "Missing secondary LOD meshes",
                    "LOD evaluation dimension fails QA floor",
                    "Asset rejected"
                ]
            )
            rec_action = "REBUILD_LOD"
            risk = "LOW"
        elif f_type == FailureType.COLLISION_ERROR:
            rc = RootCause(
                cause_id=f"RC_COL_{failure.failure_id}",
                category="COLLISION",
                description="Convex collision hull UCX missing or non-manifold.",
                evidence_ids=ev_ids,
                affected_components=["UCX_Collision"],
                confidence=conf,
                alternatives=["Collision geometry intersects weapon boundary"],
                causal_chain=[
                    "Collision hull generation failed",
                    "Game Engine readiness reject missing UCX",
                    "Asset packaging blocked"
                ]
            )
            rec_action = "REBUILD_COLLISION"
            risk = "LOW"
        elif f_type == FailureType.GOVERNANCE_ERROR:
            rc = RootCause(
                cause_id=f"RC_GOV_{failure.failure_id}",
                category="GOVERNANCE",
                description="Agent lacking required capabilities in Contract V2.",
                evidence_ids=ev_ids,
                affected_components=["ToolInvocationGate"],
                confidence=conf,
                alternatives=["Unregistered agent", "Missing token"],
                causal_chain=[
                    "Agent requested restricted tool call",
                    "ToolInvocationGate denied execution (deny-by-default)",
                    "Pipeline execution halted"
                ]
            )
            rec_action = "ESCALATE"
            risk = "HIGH"
        else:
            rc = RootCause(
                cause_id=f"RC_GEN_{failure.failure_id}",
                category=failure.failure_category,
                description=f"Observed error: {failure.message}",
                evidence_ids=ev_ids,
                affected_components=["Asset"],
                confidence=conf,
                alternatives=["Execution timeout", "Subprocess failure"],
                causal_chain=[failure.message, "Operation failed"]
            )
            rec_action = "RETRY"
            risk = "MEDIUM"

        return DiagnosticReport(
            report_id=f"DIAG_{failure.failure_id}",
            failure_id=failure.failure_id,
            semantic_id=failure.semantic_id,
            root_cause=rc,
            confidence=conf,
            dependencies=["Geometry", "Materials", "LOD", "Collision", "Evaluation"],
            recommended_action=rec_action,
            risk_level=risk
        )
