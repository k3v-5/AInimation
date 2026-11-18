import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.production_orchestration import (
    ProductionJob, JobStatus,
    PipelineStage, StageResult, StageStatus,
    ProductionPlan, ProductionStateMachine,
    ProductionPipeline, StageExecutor, BudgetEnforcer,
    VersionManager, CrashRecoveryManager, CancellationManager, AuditReporter,
    ProductionStore, ProductionOrchestratorAPI
)
from src.evaluation import EvaluationBenchmarkAPI
from src.golden import GoldenAPI, GoldenAsset, GoldenAssetStatus
from src.failure_analysis import FailureAnalysisAPI
from src.strategy_learning import StrategyLearningAPI
from src.cost_performance import CostPerformanceAPI

class TestSuitePhase80ProductionOrchestration(unittest.TestCase):
    """
    Comprehensive test suite for Phase 80: Production Orchestration.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.prod_db = os.path.join(self.tmp_dir.name, "test_prod_store.json")
        self.eval_db = os.path.join(self.tmp_dir.name, "test_eval_store.json")
        self.golden_db = os.path.join(self.tmp_dir.name, "test_golden_store.json")
        self.failure_db = os.path.join(self.tmp_dir.name, "test_failure_store.json")
        self.strat_db = os.path.join(self.tmp_dir.name, "test_strat_store.json")
        self.cp_db = os.path.join(self.tmp_dir.name, "test_cp_store.json")

        self.eval_api = EvaluationBenchmarkAPI(persistence_path=self.eval_db)
        self.golden_api = GoldenAPI(persistence_path=self.golden_db)
        self.failure_api = FailureAnalysisAPI(persistence_path=self.failure_db, eval_api=self.eval_api, golden_api=self.golden_api)
        self.strat_api = StrategyLearningAPI(persistence_path=self.strat_db, eval_api=self.eval_api, golden_api=self.golden_api, failure_api=self.failure_api)
        self.cp_api = CostPerformanceAPI(persistence_path=self.cp_db, eval_api=self.eval_api, golden_api=self.golden_api, failure_api=self.failure_api, strat_api=self.strat_api)

        self.api = ProductionOrchestratorAPI(
            persistence_path=self.prod_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api,
            failure_api=self.failure_api,
            strat_api=self.strat_api,
            cp_api=self.cp_api
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    # 1. ProductionJob Models & Serialization
    def test_01_production_job_serialization(self):
        job = ProductionJob(
            job_id="JOB_001",
            asset_semantic_id="weapon.darx.production_rifle.001",
            asset_type="WEAPON"
        )
        d = job.to_dict()
        self.assertEqual(d["job_id"], "JOB_001")
        self.assertEqual(d["status"], JobStatus.CREATED.value)

        reconstructed = ProductionJob.from_dict(d)
        self.assertEqual(reconstructed.job_id, "JOB_001")
        self.assertEqual(reconstructed.status, JobStatus.CREATED)

    # 2. State Machine Transitions & Invariant Protection
    def test_02_state_machine_valid_transitions(self):
        job = ProductionJob(job_id="JOB_SM", status=JobStatus.CREATED)
        ok, _ = ProductionStateMachine.transition(job, JobStatus.PLANNED)
        self.assertTrue(ok)
        self.assertEqual(job.status, JobStatus.PLANNED)

        ok, _ = ProductionStateMachine.transition(job, JobStatus.RUNNING)
        self.assertTrue(ok)
        self.assertEqual(job.status, JobStatus.RUNNING)

        ok, _ = ProductionStateMachine.transition(job, JobStatus.COMPLETED)
        self.assertTrue(ok)
        self.assertEqual(job.status, JobStatus.COMPLETED)

    def test_03_state_machine_blocks_completed_to_running(self):
        job = ProductionJob(job_id="JOB_TERM", status=JobStatus.COMPLETED)
        ok, msg = ProductionStateMachine.transition(job, JobStatus.RUNNING)
        self.assertFalse(ok)
        self.assertIn("Illegal state transition", msg)

    # 3. Production Plan Building
    def test_04_production_plan_building(self):
        job = self.api.create_production_job("JOB_PLAN_TEST", "weapon.rifle.001")
        plan = self.api.plan_production(job.job_id, items_to_create=["SM_Rifle_001"])
        self.assertEqual(plan.plan_id, "PLAN_JOB_PLAN_TEST")
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.PLANNED)

    # 4. Pipeline Stages & Execution
    def test_05_stage_executor_success(self):
        res = StageExecutor.execute_stage(
            stage=PipelineStage.REQUEST_INGESTION,
            agent_id="agent.perception",
            capabilities=["CAP_PERCEPTION"],
            stage_func=lambda: {"artifacts_created": ["spec.json"], "metrics": {"words": 150}}
        )
        self.assertEqual(res.status, StageStatus.COMPLETED)
        self.assertIn("spec.json", res.artifacts_created)
        self.assertTrue(len(res.output_hash) > 0)

    def test_06_stage_executor_failure_handling(self):
        def failing_func():
            raise ValueError("Blender execution failed")

        res = StageExecutor.execute_stage(
            stage=PipelineStage.BLENDER_EXECUTION,
            agent_id="agent.blender",
            capabilities=["CAP_BLENDER"],
            stage_func=failing_func
        )
        self.assertEqual(res.status, StageStatus.FAILED)
        self.assertIn("Blender execution failed", res.errors[0])

    # 5. Budget Enforcement
    def test_07_budget_enforcer(self):
        job = ProductionJob(
            job_id="JOB_BUDGET",
            budget={"max_execution_time": 60.0, "max_correction_iterations": 2}
        )
        ok, _ = BudgetEnforcer.validate_job_budget(job, elapsed_time=30.0, current_corrections=1)
        self.assertTrue(ok)

        ok_time, msg_time = BudgetEnforcer.validate_job_budget(job, elapsed_time=90.0, current_corrections=1)
        self.assertFalse(ok_time)
        self.assertIn("BUDGET_EXCEEDED", msg_time)

        ok_corr, msg_corr = BudgetEnforcer.validate_job_budget(job, elapsed_time=30.0, current_corrections=3)
        self.assertFalse(ok_corr)
        self.assertIn("Correction iterations", msg_corr)

    # 6. Versioning & Immutability
    def test_08_version_manager(self):
        v1 = VersionManager.get_next_version(None)
        self.assertEqual(v1, "v001")
        v2 = VersionManager.get_next_version("weapon.darx.vandal.001.v001")
        self.assertEqual(v2, "v002")

    # 7. Pause & Resume Operations
    def test_09_pause_and_resume(self):
        job = self.api.create_production_job("JOB_PR", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.RUNNING)

        self.api.pause_production(job.job_id)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.PAUSED)

        self.api.resume_production(job.job_id)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.RUNNING)

    # 8. Cancellation Operation
    def test_10_safe_cancellation(self):
        job = self.api.create_production_job("JOB_CANCEL", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)

        ok, msg = self.api.cancel_production(job.job_id, "Resource limit reached")
        self.assertTrue(ok)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.CANCELLED)

    # 9. Crash Recovery (F70)
    def test_11_crash_recovery(self):
        job = ProductionJob(job_id="JOB_CRASH", status=JobStatus.FAILED, current_stage="ASSET_GENERATION")
        recovered = CrashRecoveryManager.recover_job(job, {"checkpoint_id": "CHK_01", "stage": "ASSET_GENERATION"})
        self.assertTrue(recovered)
        self.assertEqual(job.status, JobStatus.RUNNING)
        self.assertEqual(job.attempt, 2)

    # 10. Governance & Authorization (F72)
    def test_12_governance_authorization_check(self):
        ok, _ = self.api.multi_agent_bridge.verify_agent_authorization("agent.geometry", "CAP_GEOMETRY")
        self.assertTrue(ok)

        denied, msg = self.api.multi_agent_bridge.verify_agent_authorization("agent.unauthorized", "CAP_GEOMETRY")
        self.assertFalse(denied)
        self.assertIn("GOVERNANCE_REJECTED", msg)

    # 11. Regression Check & Golden Asset Integration (F76)
    def test_13_golden_regression_check(self):
        g = GoldenAsset("G_RIFLE", "weapon.rifle.001", "Rifle", baseline_score=0.95, status=GoldenAssetStatus.ACTIVE)
        self.golden_api.registry.register(g, allow_update=True)
        self.golden_api.versions.register_version(g)

        # Candidate with score 0.90 -> delta -0.05 -> regression
        is_reg, delta = self.api.golden_bridge.check_regression("weapon.rifle.001", 0.90)
        self.assertTrue(is_reg)
        self.assertLess(delta, 0.0)

    # 12. Full Acceptance & Packaging / Delivery Pipeline (F69)
    def test_14_approval_and_delivery(self):
        job = self.api.create_production_job("JOB_DELIV", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)

        pkg = self.api.packaging_bridge.create_package(job.job_id, job.asset_semantic_id, "v001")
        self.assertEqual(pkg["status"], "PACKAGED")

        deliv = self.api.packaging_bridge.deliver_package(pkg["package_id"])
        self.assertEqual(deliv["status"], "DELIVERED")

        self.api.approve_production(job.job_id)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.COMPLETED)

    # 13. Audit Reporter Manifests
    def test_15_audit_reporter(self):
        job = ProductionJob(job_id="JOB_AUDIT", status=JobStatus.COMPLETED)
        stage = StageResult(stage_id=PipelineStage.REQUEST_INGESTION, status=StageStatus.COMPLETED, completed_at=time.time())
        manifest = AuditReporter.generate_manifest(job, {}, [stage])
        self.assertEqual(manifest["final_status"], "COMPLETED")
        metrics = AuditReporter.generate_metrics(job, [stage])
        self.assertEqual(metrics["stages_executed"], 1)

    # 14. Persistence Reloading
    def test_16_store_persistence_reload(self):
        job = self.api.create_production_job("JOB_PERSIST", "weapon.darx.vandal.001")
        reloaded = ProductionStore(self.prod_db)
        loaded_job = reloaded.get_job("JOB_PERSIST")
        self.assertIsNotNone(loaded_job)
        self.assertEqual(loaded_job.asset_semantic_id, "weapon.darx.vandal.001")

    # 15. Pipeline Multi-Stage Execution & Errors
    def test_17_pipeline_executes_multiple_stages(self):
        job = self.api.create_production_job("JOB_PIPE", "weapon.rifle.001")
        pipeline = ProductionPipeline(job)

        res1 = pipeline.execute_stage(PipelineStage.REQUEST_INGESTION, "agent.perception", ["CAP_PERCEPTION"], lambda: {})
        self.assertEqual(res1.status, StageStatus.COMPLETED)
        self.assertEqual(len(pipeline.stage_results), 1)

        res2 = pipeline.execute_stage(PipelineStage.STRATEGY_SELECTION, "agent.strategy", ["CAP_STRATEGY"], lambda: {})
        self.assertEqual(res2.status, StageStatus.COMPLETED)
        self.assertEqual(len(pipeline.stage_results), 2)

    def test_18_reject_production_with_reason(self):
        job = self.api.create_production_job("JOB_REJ", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)

        ok, msg = self.api.reject_production(job.job_id, "Unreal collision check failed")
        self.assertTrue(ok)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.REJECTED)

    # 16. State Machine Edge Validations
    def test_19_cannot_cancel_completed_job(self):
        job = self.api.create_production_job("JOB_NC", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        self.api.approve_production(job.job_id)

        ok, _ = self.api.cancel_production(job.job_id)
        self.assertFalse(ok)

    def test_20_cannot_pause_planned_job(self):
        job = self.api.create_production_job("JOB_NP", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        ok, _ = self.api.pause_production(job.job_id)
        self.assertFalse(ok)

    def test_21_cannot_start_completed_job(self):
        job = self.api.create_production_job("JOB_NS", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        self.api.approve_production(job.job_id)
        ok, _ = self.api.start_production(job.job_id)
        self.assertFalse(ok)

    def test_22_cannot_retry_running_job(self):
        job = self.api.create_production_job("JOB_NR", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        ok, _ = self.api.retry_production(job.job_id)
        self.assertFalse(ok)

    def test_23_production_plan_defaults(self):
        plan = ProductionPlan("P_DEF", "J_DEF", "weapon.smg.001")
        self.assertGreater(len(plan.participating_agents), 3)
        self.assertIn("CAP_BLENDER", plan.required_capabilities)

    def test_24_audit_reporter_decision_log(self):
        job = ProductionJob("JOB_DLOG", status=JobStatus.COMPLETED, strategy={"name": "Optimal"})
        dlog = AuditReporter.generate_decision_log(job)
        self.assertEqual(len(dlog), 2)
        self.assertEqual(dlog[0]["decision"], "STRATEGY_SELECTED")

    def test_25_audit_reporter_events_list(self):
        stage = StageResult(PipelineStage.BLENDER_EXECUTION, StageStatus.COMPLETED, completed_at=time.time())
        events = AuditReporter.generate_events([stage])
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["stage"], "BLENDER_EXECUTION")

    def test_26_knowledge_graph_node_recorded(self):
        job = self.api.create_production_job("JOB_KG_TEST", "weapon.knife.001")
        node = self.api.kg_bridge.kg.get_node("prod_job:JOB_KG_TEST")
        self.assertIsNotNone(node)

    def test_27_get_production_artifacts_list(self):
        job = self.api.create_production_job("JOB_ART", "weapon.rifle.001")
        stage = StageResult(PipelineStage.ASSET_GENERATION, StageStatus.COMPLETED, artifacts_created=["SM_Rifle.fbx"])
        manifest = AuditReporter.generate_manifest(job, {}, [stage])
        self.api.store.store_manifest(job.job_id, manifest)
        artifacts = self.api.get_production_artifacts(job.job_id)
        self.assertIn("SM_Rifle.fbx", artifacts)

    def test_28_get_production_metrics_dict(self):
        job = self.api.create_production_job("JOB_MET", "weapon.rifle.001")
        metrics = self.api.get_production_metrics(job.job_id)
        self.assertEqual(metrics["job_id"], "JOB_MET")
        self.assertEqual(metrics["status"], JobStatus.CREATED.value)

    def test_29_state_machine_evaluating_to_correcting(self):
        job = ProductionJob("JOB_EV_CORR", status=JobStatus.EVALUATING)
        ok, _ = ProductionStateMachine.transition(job, JobStatus.CORRECTING)
        self.assertTrue(ok)
        self.assertEqual(job.status, JobStatus.CORRECTING)

    def test_30_state_machine_optimizing_to_regression_check(self):
        job = ProductionJob("JOB_OPT_REG", status=JobStatus.OPTIMIZING)
        ok, _ = ProductionStateMachine.transition(job, JobStatus.REGRESSION_CHECK)
        self.assertTrue(ok)
        self.assertEqual(job.status, JobStatus.REGRESSION_CHECK)

    def test_31_retry_rejected_production(self):
        job = self.api.create_production_job("JOB_RETRY_REJ", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        self.api.reject_production(job.job_id, "Visual defect detected")
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.REJECTED)

        ok, msg = self.api.retry_production(job.job_id)
        self.assertTrue(ok)
        self.assertEqual(self.api.get_production_status(job.job_id), JobStatus.RUNNING)
        loaded = self.api.store.get_job(job.job_id)
        self.assertEqual(loaded.attempt, 2)

    def test_32_cannot_approve_created_job(self):
        job = self.api.create_production_job("JOB_APPR_ERR", "weapon.rifle.001")
        ok, msg = self.api.approve_production(job.job_id)
        self.assertFalse(ok)
        self.assertIn("Illegal state transition", msg)

    def test_33_cannot_reject_completed_job(self):
        job = self.api.create_production_job("JOB_REJ_ERR", "weapon.rifle.001")
        self.api.plan_production(job.job_id)
        self.api.start_production(job.job_id)
        self.api.approve_production(job.job_id)
        ok, msg = self.api.reject_production(job.job_id, "Late reject")
        self.assertFalse(ok)
        self.assertIn("Illegal state transition", msg)

    def test_34_create_pipeline_factory(self):
        job = self.api.create_production_job("JOB_FACT", "weapon.rifle.001")
        pipeline = self.api.create_pipeline(job.job_id)
        self.assertEqual(pipeline.job.job_id, "JOB_FACT")

    def test_35_multi_agent_bridge_authorized(self):
        ok, msg = self.api.multi_agent_bridge.verify_agent_authorization("agent.geometry", "CAP_GEOMETRY")
        self.assertTrue(ok)
        self.assertEqual(msg, "Authorized")

    def test_36_multi_agent_bridge_unauthorized_capability(self):
        ok, msg = self.api.multi_agent_bridge.verify_agent_authorization("agent.geometry", "CAP_MATERIAL")
        self.assertFalse(ok)
        self.assertIn("GOVERNANCE_REJECTED", msg)

    def test_37_multi_agent_bridge_unauthorized_agent(self):
        ok, msg = self.api.multi_agent_bridge.verify_agent_authorization("agent.unauthorized", "CAP_GEOMETRY")
        self.assertFalse(ok)
        self.assertIn("GOVERNANCE_REJECTED", msg)

if __name__ == "__main__":
    unittest.main()

