import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.diagnostics import (
    FailureStatus, FailureType, ResolutionStatus, FailureSeverity, FailureRecord,
    RootCause, DiagnosticReport, FailureCapture, ExceptionNormalizer, EventCollector,
    FailureClassifier, FailureSignature, CategoryRules, EvidenceItem, StateSnapshot,
    BlenderEvidenceCollector, EvidenceCollector, RootCauseAnalyzer, DependencyAnalyzer,
    ImpactAnalyzer, ConfidenceEngine, CorrectiveAction, CorrectionPlanner,
    CorrectionExecutor, CorrectionValidator, IncidentStore, FailureHistory,
    PatternDetector, GovernanceBridge, JobRecoveryBridge, DiagnosticsKnowledgeGraphBridge,
    DiagnosticsAPI
)
from src.evaluation import EvaluationBenchmarkAPI, EvaluationBenchmark, AcceptanceDecision, DefectSeverity
from src.golden import GoldenAPI

class TestSuitePhase77FailureAnalysisAndSelfDebugging(unittest.TestCase):
    """
    Comprehensive test suite for Phase 77: Failure Analysis & Self-Debugging System.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.incident_db = os.path.join(self.tmp_dir.name, "test_incident_store.json")
        self.eval_db = os.path.join(self.tmp_dir.name, "test_eval_store.json")
        self.golden_db = os.path.join(self.tmp_dir.name, "test_golden_store.json")

        self.eval_api = EvaluationBenchmarkAPI(persistence_path=self.eval_db)
        self.golden_api = GoldenAPI(persistence_path=self.golden_db)
        self.api = DiagnosticsAPI(
            persistence_path=self.incident_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    # 1. Failure Record & Model Tests
    def test_01_failure_record_creation_and_serialization(self):
        rec = FailureRecord(
            failure_id="FAIL_001",
            semantic_id="weapon.darx.vandal.001",
            message="Object has non-uniform scale X=1.2 Y=1.0 Z=1.0",
            failure_type=FailureType.SCALE_ERROR,
            severity=FailureSeverity.ERROR
        )
        d = rec.to_dict()
        restored = FailureRecord.from_dict(d)
        self.assertEqual(restored.failure_id, "FAIL_001")
        self.assertEqual(restored.failure_type, FailureType.SCALE_ERROR)
        self.assertEqual(restored.status, FailureStatus.DETECTED)

    def test_02_failure_status_transitions(self):
        rec = FailureRecord("FAIL_002", "weapon.vandal", "Mesh error")
        rec.status = FailureStatus.ANALYZING
        self.assertEqual(rec.status, FailureStatus.ANALYZING)
        rec.status = FailureStatus.RESOLVED
        self.assertEqual(rec.status, FailureStatus.RESOLVED)

    # 2. Taxonomy, Normalization & Classification Tests
    def test_03_exception_normalizer_scale_error(self):
        msg = "Error: Object Body has non-uniform scale (1.5, 1.0, 1.0)"
        f_type, code, norm_msg, sev = ExceptionNormalizer.normalize(msg)
        self.assertEqual(f_type, FailureType.SCALE_ERROR)
        self.assertEqual(code, "ERR_SCALE_NON_UNIFORM")

    def test_04_exception_normalizer_material_error(self):
        msg = "Missing material reference M_Dark_Titanium"
        f_type, code, norm_msg, sev = ExceptionNormalizer.normalize(msg)
        self.assertEqual(f_type, FailureType.MATERIAL_ERROR)
        self.assertEqual(code, "ERR_MATERIAL_MISSING")

    def test_05_failure_classifier_with_evidence(self):
        ev = {"scale": [1.2, 1.0, 1.0]}
        f_type = FailureClassifier.classify("Generic warning", ev)
        self.assertEqual(f_type, FailureType.SCALE_ERROR)

    def test_06_failure_signature_matching(self):
        sig = FailureSignature("SIG_LOD", FailureType.LOD_ERROR, "ERR_LOD", "insufficient lod", FailureSeverity.ERROR)
        self.assertTrue(sig.matches("Validation failed: insufficient lod count generated"))
        self.assertFalse(sig.matches("All textures loaded"))

    def test_07_severity_contextual_derivation(self):
        self.assertEqual(FailureSeverity.from_context("Blender crashed unexpectedly"), FailureSeverity.CRITICAL)
        self.assertEqual(FailureSeverity.from_context("Fatal memory corruption"), FailureSeverity.FATAL)
        self.assertEqual(FailureSeverity.from_context("Minor warning in uv map"), FailureSeverity.WARNING)

    # 3. Evidence Collection & State Snapshot Tests
    def test_08_evidence_item_integrity(self):
        ev = EvidenceItem("EV_001", "BLENDER", "blender.exe", {"objects": ["Body", "Barrel"]})
        self.assertTrue(ev.verify_integrity())
        ev.content["objects"].append("HackedObject")
        self.assertFalse(ev.verify_integrity())

    def test_09_state_snapshot_diffing(self):
        b = {"polygon_count": 8000, "scale": [1.5, 1.0, 1.0]}
        a = {"polygon_count": 8000, "scale": [1.0, 1.0, 1.0]}
        diffs = StateSnapshot.diff_states(b, a)
        self.assertIn("scale", diffs)
        self.assertNotIn("polygon_count", diffs)

    def test_10_evidence_collector_tamper_detection(self):
        col = EvidenceCollector()
        item = col.add_evidence("EV_10", "PROPS", "scene", {"poly_count": 5000})
        item.content["poly_count"] = 999999
        with self.assertRaises(RuntimeError):
            col.get_evidence("EV_10")

    # 4. Analysis, Root Cause & Confidence Tests
    def test_11_root_cause_analysis_and_causal_chain(self):
        rec = FailureRecord("FAIL_11", "weapon.vandal", "Scale mismatch", failure_type=FailureType.SCALE_ERROR)
        diag = RootCauseAnalyzer.analyze(rec)
        self.assertEqual(diag.root_cause.category, "TRANSFORM")
        self.assertGreaterEqual(len(diag.root_cause.causal_chain), 2)
        self.assertEqual(diag.recommended_action, "FIX_SCALE")

    def test_12_confidence_engine_scoring(self):
        conf = ConfidenceEngine.calculate_confidence(has_direct_evidence=True, evidence_count=3, has_corroboration=True)
        self.assertEqual(conf, 1.0)
        self.assertEqual(ConfidenceEngine.categorize_confidence(conf), "HIGH")

    def test_13_dependency_analyzer_cascades(self):
        deps = DependencyAnalyzer.get_dependent_components("GEOMETRY")
        self.assertIn("UV", deps)
        self.assertIn("MATERIAL", deps)
        self.assertIn("EVALUATION", deps)

    def test_14_impact_analyzer_minimal_regeneration_boundary(self):
        impact = ImpactAnalyzer.analyze_impact("weapon.vandal", "GEOMETRY")
        self.assertIn("EVAL_weapon.vandal_uv", impact["invalidated_evaluations"])
        self.assertIn("GEOMETRY", impact["required_revalidation"])

    # 5. Correction Planning & Execution Tests
    def test_15_correction_planner_scale_action(self):
        rec = FailureRecord("FAIL_15", "weapon.vandal", "Scale error", failure_type=FailureType.SCALE_ERROR)
        diag = RootCauseAnalyzer.analyze(rec)
        act = CorrectionPlanner.plan_correction(diag, "weapon.vandal")
        self.assertEqual(act.action_type, "FIX_SCALE")
        self.assertEqual(act.risk_level, "LOW")
        self.assertIn("CAP_GEOMETRY", act.required_capabilities)

    def test_16_correction_validator_resolved(self):
        b1 = self.eval_api.evaluate_asset("w.1", "c1", {"polygon_count": 25000, "materials": []})
        b2 = self.eval_api.evaluate_asset("w.1", "c2", {"polygon_count": 8500, "materials": ["M1", "M2"], "visual_match_score": 0.95})
        b2_fin = self.eval_api.finalize_benchmark(b2.benchmark_id)

        res = CorrectionValidator.validate_resolution(b1, b2_fin)
        self.assertEqual(res, ResolutionStatus.RESOLVED)

    def test_17_correction_validator_unresolved_when_still_rejected(self):
        b1 = self.eval_api.evaluate_asset("w.1", "c1", {"polygon_count": 30000})
        b2 = self.eval_api.evaluate_asset("w.1", "c2", {"polygon_count": 35000})
        res = CorrectionValidator.validate_resolution(b1, b2)
        self.assertEqual(res, ResolutionStatus.UNRESOLVED)

    # 6. History, Store & Pattern Detection Tests
    def test_18_incident_store_disk_persistence_and_reload(self):
        rec = FailureRecord("FAIL_18", "weapon.vandal", "Axis error", failure_type=FailureType.AXIS_ERROR)
        self.api.store.store_incident(rec)

        api_reloaded = DiagnosticsAPI(
            persistence_path=self.incident_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api
        )
        fetched = api_reloaded.get_incident("FAIL_18")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.failure_type, FailureType.AXIS_ERROR)

    def test_19_pattern_detector_identifies_recurring_failures(self):
        incs = [
            FailureRecord("F1", "weapon.vandal", "Scale 1", failure_type=FailureType.SCALE_ERROR),
            FailureRecord("F2", "weapon.vandal", "Scale 2", failure_type=FailureType.SCALE_ERROR),
            FailureRecord("F3", "weapon.phantom", "Scale 3", failure_type=FailureType.SCALE_ERROR),
            FailureRecord("F4", "weapon.vandal", "Material 1", failure_type=FailureType.MATERIAL_ERROR)
        ]
        res = PatternDetector.detect_patterns(incs)
        self.assertEqual(len(res["recurring_patterns"]), 1)
        self.assertEqual(res["recurring_patterns"][0]["failure_type"], "SCALE_ERROR")
        self.assertEqual(res["recurring_patterns"][0]["count"], 3)

    # 7. Governance, Recovery & Knowledge Graph Bridges
    def test_20_governance_bridge_denial_for_unauthorized_agent(self):
        act = CorrectiveAction("ACT_01", "FAIL_01", "FIX_SCALE", "w.vandal", required_capabilities=["CAP_SUPER_ADMIN_UNKNOWN"])
        res = self.api.execute_correction(act, "fake.blend", agent_id="agent.unauthorized")
        self.assertFalse(res["success"])
        self.assertIn("Governance denied", res["error"])

    def test_21_diagnostics_knowledge_graph_sync(self):
        rec = FailureRecord("FAIL_21", "weapon.darx.vandal.001", "LOD error", failure_type=FailureType.LOD_ERROR)
        diag = self.api.diagnose_failure(self.api.store.store_incident(rec) or "FAIL_21")
        node = self.api.kg_bridge.kg.get_node(f"FAILURE_{rec.failure_id}")
        self.assertIsNotNone(node)

    # 8. Self-Debugging Closed Loop Tests
    def test_22_self_debug_loop_resolves_error(self):
        res = self.api.run_self_debug(
            semantic_id="weapon.darx.vandal.001",
            initial_error_msg="Error: Object has non-uniform scale X=1.5",
            blend_file="dummy.blend",
            initial_asset_data={
                "polygon_count": 8500,
                "materials": ["M_Dark_Titanium", "M_Matte_Carbon"],
                "scale": [1.5, 1.0, 1.0],
                "invalid_scale_or_axis": True,
                "engine_readiness_score": 0.40,
                "silhouette_similarity": 0.50
            },
            max_iterations=3
        )
        self.assertEqual(res["status"], "RESOLVED")
        self.assertEqual(res["iterations"], 1)

    def test_23_self_debug_loop_escalates_when_limit_exceeded(self):
        # We simulate an unrecoverable failure that fails execution
        act = CorrectiveAction("ACT_FAIL", "FAIL_ESC", "RETRY_OPERATION", "w.unrec", required_capabilities=["CAP_FORBIDDEN"])
        rec = self.api.capture_failure(RuntimeError("Unrecoverable error"), "w.unrec")
        res = self.api.execute_correction(act, "dummy.blend", agent_id="agent.unauthorized")
        self.assertFalse(res["success"])
        inc = self.api.get_incident(rec.failure_id)
        # Verify status is not falsely RESOLVED
        self.assertNotEqual(inc.status, FailureStatus.RESOLVED)

    def test_24_event_collector_trace_logging(self):
        ec = EventCollector()
        ec.record_event("DIAG_START", {"agent": "agent.critic"}, correlation_id="CORR_1")
        ec.record_event("DIAG_END", {"status": "SUCCESS"}, correlation_id="CORR_1")
        events = ec.get_events("CORR_1")
        self.assertEqual(len(events), 2)

    def test_25_root_cause_model_serialization(self):
        rc = RootCause("C1", "TRANSFORM", "Scale issue", confidence=0.95)
        d = rc.to_dict()
        self.assertEqual(d["category"], "TRANSFORM")
        self.assertEqual(d["confidence"], 0.95)

    def test_26_diagnostic_report_serialization(self):
        rc = RootCause("C1", "TRANSFORM", "Scale issue")
        rep = DiagnosticReport("D1", "F1", rc, recommended_action="FIX_SCALE")
        d = rep.to_dict()
        self.assertEqual(d["recommended_action"], "FIX_SCALE")

    def test_27_corrective_action_serialization(self):
        act = CorrectiveAction("A1", "F1", "FIX_SCALE", "w.vandal", risk_level="LOW")
        d = act.to_dict()
        self.assertEqual(d["risk_level"], "LOW")

    def test_28_job_recovery_bridge_restore(self):
        j_bridge = JobRecoveryBridge(None)
        self.assertTrue(j_bridge.restore_checkpoint("CHK_01"))

    def test_29_category_rules_collision_error(self):
        ev = {"has_collision": False, "collision_hulls": 0}
        self.assertEqual(CategoryRules.classify_from_evidence(ev), FailureType.COLLISION_ERROR)

    def test_30_category_rules_lod_error(self):
        ev = {"lod_count": 0}
        self.assertEqual(CategoryRules.classify_from_evidence(ev), FailureType.LOD_ERROR)

    def test_31_get_history_empty_returns_empty_list(self):
        self.assertEqual(self.api.get_history("non.existent.semantic.id"), [])

    def test_32_analyze_root_cause_api_method(self):
        rec = self.api.capture_failure(RuntimeError("Missing material M_Dark_Titanium"), "weapon.vandal")
        rc = self.api.analyze_root_cause(rec.failure_id)
        self.assertEqual(rc.category, "MATERIAL")

    def test_33_failure_analysis_api_record_and_diagnose(self):
        from src.failure_analysis import FailureAnalysisAPI
        fa_store = os.path.join(self.tmp_dir.name, "fa_store.json")
        fa_api = FailureAnalysisAPI(persistence_path=fa_store, eval_api=self.eval_api, golden_api=self.golden_api)
        
        rec = fa_api.record_failure("weapon.rifle.01", "Scale X=1.5 Y=1.0 Z=1.0 error")
        self.assertEqual(rec.failure_type, FailureType.SCALE_ERROR)
        
        diag = fa_api.diagnose_failure(rec.failure_id)
        self.assertEqual(diag.root_cause.category, "TRANSFORM")
        self.assertEqual(diag.recommended_action, "FIX_SCALE")

    def test_34_recovery_planner_minimal_boundary(self):
        from src.failure_analysis import RecoveryPlanner, RecoveryActionType, RegenerationStrategy
        plan = RecoveryPlanner.plan("FAIL_001", "weapon.vandal", RecoveryActionType.REBUILD_MATERIAL)
        self.assertTrue(plan.regeneration_required)
        self.assertEqual(plan.action, RecoveryActionType.REBUILD_MATERIAL)
        
        boundary = RegenerationStrategy.compute_boundary("MATERIALS", ["Receiver", "Barrel", "Materials", "UV"])
        self.assertEqual(boundary, ["Materials", "Shaders"])

    def test_35_solution_reuse_and_failure_statistics(self):
        from src.failure_analysis import FailureMemory, SolutionReuseEngine, FailureStatistics
        mem = FailureMemory()
        f1 = FailureRecord("F1", "weapon.vandal", "scale err", failure_type=FailureType.SCALE_ERROR)
        f1.resolution = "RESOLVED"
        f1.recommended_action = "FIX_SCALE"
        mem.record(f1)
        
        sol = SolutionReuseEngine.recommend_solution(FailureType.SCALE_ERROR.value, mem.list_all())
        self.assertEqual(sol, "FIX_SCALE")
        
        stats = FailureStatistics.compute_statistics(mem.list_all())
        self.assertEqual(stats["total_failures"], 1)
        self.assertEqual(stats["resolved_count"], 1)
        self.assertEqual(stats["auto_resolution_rate"], 1.0)

    def test_36_validation_failure_detector_from_benchmark(self):
        from src.failure_analysis import ValidationFailureDetector
        from src.evaluation.models.evaluation_models import EvaluationBenchmark, AcceptanceDecision, EvaluationDefect, DefectSeverity, EvaluationDimension
        
        bench = EvaluationBenchmark(
            benchmark_id="BENCH_TEST",
            asset_semantic_id="weapon.vandal",
            acceptance=AcceptanceDecision.REJECTED,
            defects=[EvaluationDefect("D1", EvaluationDimension.ENGINE_READINESS, DefectSeverity.CRITICAL, "Missing collision UCX", "Has UCX", "None")]
        )
        recs = ValidationFailureDetector.from_benchmark(bench)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].failure_type, FailureType.COLLISION_ERROR)

    def test_37_regression_failure_detector(self):
        from src.failure_analysis import RegressionFailureDetector, FailureType as FAType
        from src.golden import GoldenAsset
        
        g = GoldenAsset("G1", "weapon.vandal", "DarX Vandal", baseline_score=0.95)
        recs = RegressionFailureDetector.detect_regression("weapon.vandal", g, current_score=0.80)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].failure_type, FAType.REGRESSION_ERROR)

    def test_38_rollback_strategy_and_intervention_policy(self):
        from src.failure_analysis import RollbackStrategy, InterventionPolicy
        rb = RollbackStrategy.plan_rollback("CHK_99", "weapon.vandal")
        self.assertEqual(rb["checkpoint_id"], "CHK_99")
        
        self.assertTrue(InterventionPolicy.requires_human_intervention(attempt_count=3, severity="ERROR", is_governance_denied=False))
        self.assertTrue(InterventionPolicy.requires_human_intervention(attempt_count=1, severity="FATAL", is_governance_denied=False))
        self.assertTrue(InterventionPolicy.requires_human_intervention(attempt_count=1, severity="ERROR", is_governance_denied=True))
        self.assertFalse(InterventionPolicy.requires_human_intervention(attempt_count=1, severity="ERROR", is_governance_denied=False))

if __name__ == "__main__":
    unittest.main()

