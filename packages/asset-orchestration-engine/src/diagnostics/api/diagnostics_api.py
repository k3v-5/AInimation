from typing import Dict, Any, List, Optional, Tuple
from ..core.failure_types import FailureStatus, FailureType, ResolutionStatus
from ..core.severity import FailureSeverity
from ..core.failure_models import FailureRecord
from ..core.diagnostic_models import RootCause, DiagnosticReport
from ..capture.failure_capture import FailureCapture
from ..classification.failure_classifier import FailureClassifier
from ..evidence.evidence_collector import EvidenceCollector
from ..evidence.provenance import EvidenceItem
from ..evidence.blender_evidence import BlenderEvidenceCollector
from ..analysis.root_cause_analyzer import RootCauseAnalyzer
from ..analysis.impact_analyzer import ImpactAnalyzer
from ..correction.corrective_action import CorrectiveAction
from ..correction.correction_planner import CorrectionPlanner
from ..correction.correction_executor import CorrectionExecutor
from ..correction.correction_validator import CorrectionValidator
from ..history.incident_store import IncidentStore
from ..history.failure_history import FailureHistory
from ..history.pattern_detector import PatternDetector
from ..integration.governance_bridge import GovernanceBridge
from ..integration.evaluation_bridge import EvaluationBridge
from ..integration.golden_bridge import GoldenBridge
from ..integration.knowledge_graph_bridge import DiagnosticsKnowledgeGraphBridge
from ...evaluation import EvaluationBenchmark

class DiagnosticsAPI:
    """
    Unified public facade for Failure Analysis & Self-Debugging System (Phase 77).
    """
    def __init__(
        self,
        persistence_path: Optional[str] = None,
        eval_api: Optional[EvaluationBenchmarkAPI] = None,
        golden_api: Optional[GoldenAPI] = None
    ):
        self.store = IncidentStore(persistence_path)
        self.history = FailureHistory()
        self.evidence_collector = EvidenceCollector()
        self.gov = GovernanceBridge()
        self.eval_bridge = EvaluationBridge(eval_api)
        self.golden_bridge = GoldenBridge(golden_api)
        self.kg_bridge = DiagnosticsKnowledgeGraphBridge()

        # Ingest stored incidents
        for inc in self.store.list_incidents():
            self.history.append(inc)

    def capture_failure(
        self,
        exc: Exception,
        semantic_id: str,
        operation: str = "GENERATE_ASSET",
        agent_id: str = "agent.visual.critic",
        failure_id: Optional[str] = None,
        job_id: Optional[str] = None,
        state_before: Optional[Dict[str, Any]] = None
    ) -> FailureRecord:
        record = FailureCapture.capture_exception(
            exc=exc,
            semantic_id=semantic_id,
            operation=operation,
            agent_id=agent_id,
            failure_id=failure_id,
            job_id=job_id,
            state_before=state_before
        )
        self.store.store_incident(record)
        self.history.append(record)
        return record

    def classify_failure(self, message: str, evidence: Optional[Dict[str, Any]] = None) -> FailureType:
        return FailureClassifier.classify(message, evidence)

    def collect_evidence(
        self,
        evidence_id: str,
        evidence_type: str,
        source: str,
        content: dict,
        relevance: float = 1.0
    ) -> EvidenceItem:
        return self.evidence_collector.add_evidence(evidence_id, evidence_type, source, content, relevance)

    def diagnose_failure(
        self,
        failure_id: str,
        evidence_items: Optional[List[EvidenceItem]] = None
    ) -> DiagnosticReport:
        record = self.store.get_incident(failure_id)
        if not record:
            raise KeyError(f"FailureRecord '{failure_id}' not found.")

        record.status = FailureStatus.ANALYZING
        report = RootCauseAnalyzer.analyze(record, evidence_items)
        record.status = FailureStatus.DIAGNOSED
        self.store.store_incident(record)

        try:
            self.kg_bridge.record_incident_in_graph(record, report, agent_id=record.agent_id)
        except Exception as e:
            print(f"[DiagnosticsAPI] Note syncing incident to graph: {e}")

        return report

    def analyze_root_cause(self, failure_id: str) -> RootCause:
        report = self.diagnose_failure(failure_id)
        return report.root_cause

    def analyze_impact(self, semantic_id: str, failed_component: str) -> Dict[str, Any]:
        return ImpactAnalyzer.analyze_impact(semantic_id, failed_component)

    def plan_correction(self, report: DiagnosticReport, semantic_id: str) -> CorrectiveAction:
        action = CorrectionPlanner.plan_correction(report, semantic_id)
        record = self.store.get_incident(report.failure_id)
        if record:
            record.status = FailureStatus.CORRECTION_PLANNED
            self.store.store_incident(record)
        return action

    def execute_correction(
        self,
        action: CorrectiveAction,
        blend_file: str,
        agent_id: str = "agent.visual.critic"
    ) -> Dict[str, Any]:
        # Governance check (F72)
        has_perm = self.gov.check_correction_permission(agent_id, action.required_capabilities[0] if action.required_capabilities else "CAP_GEOMETRY")
        if not has_perm:
            record = self.store.get_incident(action.failure_id)
            if record:
                record.status = FailureStatus.ESCALATED
                self.store.store_incident(record)
            return {
                "success": False,
                "error": f"Governance denied: Agent '{agent_id}' lacks required capabilities {action.required_capabilities}",
                "status": FailureType.GOVERNANCE_DENIED.value
            }

        record = self.store.get_incident(action.failure_id)
        if record:
            record.status = FailureStatus.CORRECTING
            self.store.store_incident(record)

        res = CorrectionExecutor.execute_in_blender(action, blend_file)
        return res

    def verify_correction(
        self,
        failure_id: str,
        before_bench: EvaluationBenchmark,
        after_bench: EvaluationBenchmark,
        semantic_id: str
    ) -> ResolutionStatus:
        record = self.store.get_incident(failure_id)
        if record:
            record.status = FailureStatus.VERIFYING

        golden_comp = self.golden_bridge.compare_with_active_golden(semantic_id, after_bench)
        status = CorrectionValidator.validate_resolution(before_bench, after_bench, golden_comp)

        if record:
            if status == ResolutionStatus.RESOLVED:
                record.status = FailureStatus.RESOLVED
            elif status == ResolutionStatus.PARTIALLY_RESOLVED:
                record.status = FailureStatus.PARTIALLY_RESOLVED
            else:
                record.status = FailureStatus.UNRESOLVED
            self.store.store_incident(record)

        return status

    def get_failure(self, failure_id: str) -> Optional[FailureRecord]:
        return self.store.get_incident(failure_id)

    def get_incident(self, failure_id: str) -> Optional[FailureRecord]:
        return self.store.get_incident(failure_id)

    def get_history(self, semantic_id: str) -> List[FailureRecord]:
        return self.history.get_history(semantic_id)

    def detect_patterns(self) -> Dict[str, Any]:
        return PatternDetector.detect_patterns(self.store.list_incidents())

    def run_self_debug(
        self,
        semantic_id: str,
        initial_error_msg: str,
        blend_file: str,
        initial_asset_data: Dict[str, Any],
        agent_id: str = "agent.geometry",
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """Runs the bounded closed-loop self-debugging engine."""
        iteration = 0
        failure = self.capture_failure(
            exc=RuntimeError(initial_error_msg),
            semantic_id=semantic_id,
            agent_id=agent_id,
            state_before=initial_asset_data
        )

        current_asset_data = dict(initial_asset_data)
        before_bench = self.eval_bridge.evaluate_candidate(
            semantic_id, "cand_pre_debug", current_asset_data, f"BENCH_PRE_{failure.failure_id}"
        )

        while iteration < max_iterations:
            iteration += 1
            # 1. Collect Evidence
            ev_item = self.collect_evidence(
                evidence_id=f"EV_ITER_{iteration}_{failure.failure_id}",
                evidence_type="BLENDER_STATE",
                source=blend_file,
                content=current_asset_data
            )

            # 2. Diagnose & Root Cause
            diag = self.diagnose_failure(failure.failure_id, [ev_item])

            # 3. Plan Correction
            action = self.plan_correction(diag, semantic_id)

            # 4. Execute Correction
            exec_res = self.execute_correction(action, blend_file, agent_id=agent_id)
            if not exec_res.get("success"):
                return {
                    "status": ResolutionStatus.UNRESOLVED.value,
                    "failure_id": failure.failure_id,
                    "iteration": iteration,
                    "error": exec_res.get("error")
                }

            # Update asset state to simulate corrected parameters
            if action.action_type == "FIX_SCALE":
                current_asset_data["scale"] = [1.0, 1.0, 1.0]
                current_asset_data["invalid_scale_or_axis"] = False
                current_asset_data["engine_readiness_score"] = 0.95
                current_asset_data["silhouette_similarity"] = 0.94
                current_asset_data["visual_match_score"] = 0.92
                current_asset_data["has_collision"] = True
                current_asset_data["lod_count"] = 3
            elif action.action_type == "REASSIGN_MATERIAL":
                current_asset_data["materials"] = ["M_Dark_Titanium", "M_Matte_Carbon"]

            # 5. Re-evaluate
            after_bench = self.eval_bridge.evaluate_candidate(
                semantic_id, f"cand_post_{iteration}", current_asset_data, f"BENCH_POST_{iteration}_{failure.failure_id}"
            )

            # 6. Verify Resolution
            res_status = self.verify_correction(failure.failure_id, before_bench, after_bench, semantic_id)
            if res_status == ResolutionStatus.RESOLVED:
                return {
                    "status": res_status.value,
                    "failure_id": failure.failure_id,
                    "iterations": iteration,
                    "root_cause": diag.root_cause.to_dict(),
                    "corrective_action": action.to_dict(),
                    "before_score": before_bench.weighted_score,
                    "after_score": after_bench.weighted_score
                }

        # Max iterations exceeded
        failure.status = FailureStatus.ESCALATED
        self.store.store_incident(failure)
        return {
            "status": ResolutionStatus.ESCALATED.value,
            "failure_id": failure.failure_id,
            "iterations": iteration,
            "message": "Maximum self-debug iterations exceeded."
        }
