import time
from typing import Dict, Any, List, Optional

from ..core.failure_types import FailureType, FailureSeverity, FailureStatus, RecoveryActionType
from ..core.failure_models import FailureRecord
from ..core.failure_context import FailureContext
from ..core.failure_classifier import FailureClassifier
from ..detection.exception_detector import ExceptionDetector
from ..diagnosis.root_cause_analyzer import RootCauseAnalyzer, DiagnosticReport
from ..diagnosis.dependency_analyzer import DependencyAnalyzer
from ..diagnosis.evidence_analyzer import EvidenceItem
from ..recovery.recovery_planner import RecoveryPlanner, RecoveryPlan
from ..correction.corrective_action import CorrectiveAction
from ..correction.correction_planner import CorrectionPlanner
from ..correction.correction_executor import CorrectionExecutor
from ..correction.correction_validator import CorrectionValidator
from ..correction.correction_history import CorrectionHistory
from ..learning.failure_memory import FailureMemory
from ..learning.pattern_detector import PatternDetector
from ..learning.solution_reuse import SolutionReuseEngine
from ..learning.failure_statistics import FailureStatistics
from ..integration.governance_bridge import GovernanceBridge
from ..integration.benchmark_bridge import BenchmarkBridge
from ..integration.golden_asset_bridge import GoldenAssetBridge
from ..integration.knowledge_graph_bridge import KnowledgeGraphBridge
from ..persistence.failure_store import FailureStore
from ...evaluation import EvaluationBenchmarkAPI, EvaluationBenchmark
from ...golden import GoldenAPI

class FailureAnalysisAPI:
    """Unified public API for Phase 77 Failure Analysis & Self-Debugging System."""

    def __init__(
        self,
        persistence_path: Optional[str] = None,
        eval_api: Optional[EvaluationBenchmarkAPI] = None,
        golden_api: Optional[GoldenAPI] = None
    ):
        self.store = FailureStore(persistence_path)
        self.memory = FailureMemory()
        self.correction_history = CorrectionHistory()
        self.gov = GovernanceBridge()
        self.eval_bridge = BenchmarkBridge(eval_api)
        self.golden_bridge = GoldenAssetBridge(golden_api)
        self.kg_bridge = KnowledgeGraphBridge()

        # Ingest stored failures into memory
        for f in self.store.list_failures():
            self.memory.record(f)

    def record_failure(
        self,
        semantic_id: str,
        message: str,
        failure_type: FailureType = FailureType.UNKNOWN_ERROR,
        failure_id: Optional[str] = None,
        context: Optional[FailureContext] = None,
        state_before: Optional[Dict[str, Any]] = None
    ) -> FailureRecord:
        f_id = failure_id or f"FAIL_{int(time.time()*1000)}_{semantic_id.replace('.', '_')}"
        if failure_type == FailureType.UNKNOWN_ERROR:
            failure_type, cat, sev = FailureClassifier.classify(message, state_before)
        else:
            cat = "GENERAL"
            sev = FailureSeverity.ERROR

        rec = FailureRecord(
            failure_id=f_id,
            semantic_id=semantic_id,
            message=message,
            failure_type=failure_type,
            failure_category=cat,
            severity=sev,
            status=FailureStatus.DETECTED,
            actual_state=state_before or {},
            job_id=context.job_id if context else None
        )
        self.store.store_failure(rec)
        self.memory.record(rec)
        self.kg_bridge.record_failure_node(rec.failure_id, rec.semantic_id, rec.failure_type.value, rec.severity.value)
        return rec

    def get_failure(self, failure_id: str) -> Optional[FailureRecord]:
        return self.store.get_failure(failure_id)

    def list_failures(self) -> List[FailureRecord]:
        return self.store.list_failures()

    def classify_failure(self, message: str, evidence: Optional[Dict[str, Any]] = None):
        return FailureClassifier.classify(message, evidence)

    def diagnose_failure(self, failure_id: str, evidence_items: Optional[List[Dict[str, Any]]] = None) -> DiagnosticReport:
        rec = self.get_failure(failure_id)
        if not rec:
            raise KeyError(f"FailureRecord {failure_id} not found.")

        rec.status = FailureStatus.ANALYZING
        report = RootCauseAnalyzer.analyze(rec, evidence_items)
        rec.probable_root_cause = f"{report.root_cause.category}: {report.root_cause.description}"
        rec.recommended_action = report.recommended_action
        rec.confidence = report.confidence
        rec.status = FailureStatus.DIAGNOSED

        self.store.store_failure(rec)
        self.kg_bridge.record_root_cause_node(
            report.root_cause.cause_id,
            rec.failure_id,
            report.root_cause.category,
            report.root_cause.description
        )
        return report

    def create_recovery_plan(self, failure_id: str, action: RecoveryActionType) -> RecoveryPlan:
        rec = self.get_failure(failure_id)
        semantic_id = rec.semantic_id if rec else "asset.default"
        plan = RecoveryPlanner.plan(failure_id, semantic_id, action)
        if rec:
            rec.recovery_plan = plan.to_dict()
            self.store.store_failure(rec)
        return plan

    def create_correction_plan(self, diagnostic: DiagnosticReport, target_asset: str) -> CorrectiveAction:
        rec = self.get_failure(diagnostic.failure_id)
        action = CorrectionPlanner.plan_correction(diagnostic, target_asset)
        if rec:
            rec.correction_plan = action.to_dict()
            rec.status = FailureStatus.CORRECTION_PLANNED
            self.store.store_failure(rec)
        return action

    def execute_correction(
        self,
        action: CorrectiveAction,
        blend_file: str,
        blender_exe: str = r"E:\Blender\blender.exe",
        agent_id: str = "agent.geometry"
    ) -> Dict[str, Any]:
        rec = self.get_failure(action.failure_id)
        if rec:
            rec.status = FailureStatus.CORRECTING
            self.store.store_failure(rec)

        executor = CorrectionExecutor(self.gov)
        result = executor.execute(action, blend_file, blender_exe, agent_id)

        if not result.get("success"):
            if rec:
                rec.status = FailureStatus.ESCALATED if result.get("status") == "GOVERNANCE_DENIED" else FailureStatus.UNRESOLVED
                self.store.store_failure(rec)
        return result

    def validate_correction(
        self,
        failure_id: str,
        before_bench: EvaluationBenchmark,
        after_bench: EvaluationBenchmark,
        semantic_id: str
    ) -> FailureStatus:
        rec = self.get_failure(failure_id)
        golden = self.golden_bridge.get_golden(semantic_id)
        status = CorrectionValidator.validate_resolution(before_bench, after_bench, golden)

        if rec:
            rec.status = status
            if status == FailureStatus.RESOLVED:
                rec.resolution = "RESOLVED"
                rec.resolved_at = time.time()
            elif status == FailureStatus.UNRESOLVED:
                rec.resolution = "UNRESOLVED"
            self.store.store_failure(rec)
        return status

    def resolve_failure(self, failure_id: str, resolution_notes: str = "Manual resolution confirmed."):
        rec = self.get_failure(failure_id)
        if rec:
            rec.status = FailureStatus.RESOLVED
            rec.resolution = "RESOLVED"
            rec.resolved_at = time.time()
            rec.resolution_evidence = {"notes": resolution_notes}
            self.store.store_failure(rec)

    def escalate_failure(self, failure_id: str, reason: str = "Max attempts exceeded or governance denial."):
        rec = self.get_failure(failure_id)
        if rec:
            rec.status = FailureStatus.ESCALATED
            rec.requires_human = True
            rec.resolution = "ESCALATED"
            rec.resolution_evidence = {"escalation_reason": reason}
            self.store.store_failure(rec)

    def get_failure_history(self, semantic_id: Optional[str] = None) -> List[FailureRecord]:
        if semantic_id:
            return self.memory.find_by_semantic_id(semantic_id)
        return self.memory.list_all()

    def get_failure_statistics(self) -> Dict[str, Any]:
        return FailureStatistics.compute_statistics(self.memory.list_all())

    def find_similar_failures(self, failure_type_val: str) -> List[FailureRecord]:
        return self.memory.find_by_type(failure_type_val)
