import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cost_performance import (
    CostReport, CostMetric, MeasurementMethod,
    PerformanceReport, QualityFloor, OptimizationProfile, ProfileType,
    BudgetLimits, BudgetStatus,
    CostEvaluator, PerformanceEvaluator, ParetoAnalyzer, TradeoffAnalyzer, BudgetChecker,
    CandidateStrategy, CandidateStatus,
    GeometryOptimizer, MaterialOptimizer, TextureOptimizer, LODOptimizer, CollisionOptimizer,
    OptimizationPlan, PlanBuilder, LifecycleController, LifecycleStage,
    AuditRecord, CostPerformanceStore, CostPerformanceAPI
)
from src.evaluation import EvaluationBenchmarkAPI
from src.golden import GoldenAPI
from src.failure_analysis import FailureAnalysisAPI
from src.strategy_learning import StrategyLearningAPI

class TestSuitePhase79CostPerformanceOptimizer(unittest.TestCase):
    """
    Comprehensive test suite for Phase 79: Cost/Performance Optimizer System.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.cp_db = os.path.join(self.tmp_dir.name, "test_cp_store.json")
        self.eval_db = os.path.join(self.tmp_dir.name, "test_eval_store.json")
        self.golden_db = os.path.join(self.tmp_dir.name, "test_golden_store.json")
        self.failure_db = os.path.join(self.tmp_dir.name, "test_failure_store.json")
        self.strat_db = os.path.join(self.tmp_dir.name, "test_strat_store.json")

        self.eval_api = EvaluationBenchmarkAPI(persistence_path=self.eval_db)
        self.golden_api = GoldenAPI(persistence_path=self.golden_db)
        self.failure_api = FailureAnalysisAPI(persistence_path=self.failure_db, eval_api=self.eval_api, golden_api=self.golden_api)
        self.strat_api = StrategyLearningAPI(persistence_path=self.strat_db, eval_api=self.eval_api, golden_api=self.golden_api, failure_api=self.failure_api)

        self.api = CostPerformanceAPI(
            persistence_path=self.cp_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api,
            failure_api=self.failure_api,
            strat_api=self.strat_api
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    # 1. Cost & Performance Models
    def test_01_cost_metric_and_report_serialization(self):
        m = CostMetric("generation_time", "seconds", 25.5, measurement_method=MeasurementMethod.MEASURED)
        d = m.to_dict()
        self.assertEqual(d["name"], "generation_time")
        self.assertEqual(d["value"], 25.5)

        report = CostReport(generation_time=25.0, memory_usage_mb=180.0)
        rep_d = report.to_dict()
        self.assertGreater(rep_d["total_cost"], 0.0)

    def test_02_performance_report_serialization_and_nanite(self):
        perf = PerformanceReport(triangle_count=22000, texture_memory_mb=32.0)
        d = perf.to_dict()
        self.assertEqual(d["triangle_count"], 22000)
        self.assertTrue(d["nanite_compatibility"])

    # 2. Quality Floor & Hard Limits
    def test_03_quality_floor_enforcement(self):
        floor = QualityFloor(overall_quality_floor=0.92, minimum_visual_score=0.88)
        
        # Passing candidate
        pass_scores = {"overall_quality": 0.95, "visual": 0.92, "geometry": 0.94, "engine_readiness": 0.95}
        passed, _ = floor.evaluate(pass_scores)
        self.assertTrue(passed)

        # Failing candidate
        fail_scores = {"overall_quality": 0.89, "visual": 0.92, "geometry": 0.94, "engine_readiness": 0.95}
        failed, reason = floor.evaluate(fail_scores)
        self.assertFalse(failed)
        self.assertIn("below floor", reason)

    # 3. Optimization Profiles & Scoring
    def test_04_optimization_profile_weights_and_scoring(self):
        q_prof = OptimizationProfile.quality_first()
        p_prof = OptimizationProfile.performance_first()

        score_q = q_prof.calculate_score(quality_val=0.98, cost_norm=0.2, perf_norm=0.2, memory_norm=0.2, time_norm=0.2, risk_val=0.0)
        score_p = p_prof.calculate_score(quality_val=0.98, cost_norm=0.2, perf_norm=0.2, memory_norm=0.2, time_norm=0.2, risk_val=0.0)
        self.assertGreater(score_q, score_p)

    # 4. Budget System
    def test_05_budget_limits_and_status(self):
        limits = BudgetLimits(polygon_budget=15000, material_budget=2)
        
        # Within budget
        status, breakdown = limits.check({"polygon_count": 10000, "material_count": 1})
        self.assertEqual(status, BudgetStatus.WITHIN_BUDGET)

        # Over budget
        status_over, _ = limits.check({"polygon_count": 25000, "material_count": 1})
        self.assertEqual(status_over, BudgetStatus.OVER_BUDGET)

    # 5. Pareto Front Multi-objective Analysis
    def test_06_pareto_front_classification(self):
        c1 = {"candidate_id": "C1_HIGH_Q", "quality_score": 0.98, "total_cost": 150.0, "memory_mb": 50.0, "generation_time": 60.0}
        c2 = {"candidate_id": "C2_BALANCED", "quality_score": 0.95, "total_cost": 70.0, "memory_mb": 20.0, "generation_time": 25.0}
        c3 = {"candidate_id": "C3_DOMINATED", "quality_score": 0.90, "total_cost": 90.0, "memory_mb": 30.0, "generation_time": 40.0}

        non_dom, dom = ParetoAnalyzer.classify_candidates([c1, c2, c3])
        non_dom_ids = [c["candidate_id"] for c in non_dom]
        dom_ids = [c["candidate_id"] for c in dom]

        self.assertIn("C1_HIGH_Q", non_dom_ids)
        self.assertIn("C2_BALANCED", non_dom_ids)
        self.assertIn("C3_DOMINATED", dom_ids)

    # 6. Tradeoff Explanations
    def test_07_tradeoff_analyzer_percentage_deltas(self):
        base = {"quality_score": 0.90, "memory_mb": 25.0, "generation_time": 30.0, "total_cost": 100.0}
        cand = {"candidate_id": "C_OPT", "quality_score": 0.95, "memory_mb": 15.0, "generation_time": 20.0, "total_cost": 60.0}

        tradeoff = TradeoffAnalyzer.compare_tradeoff(base, cand)
        self.assertGreater(tradeoff["delta_quality_percent"], 0.0)
        self.assertLess(tradeoff["delta_memory_percent"], 0.0)
        self.assertIn("quality", tradeoff["explanation"])

    # 7. Sub-domain Optimizers (Geometry, Material, Texture, LOD, Collision)
    def test_08_geometry_optimizer_analysis(self):
        res = GeometryOptimizer.analyze_geometry(poly_count=22000, target_budget=15000)
        self.assertEqual(res["status"], "OVER_BUDGET")

    def test_09_material_optimizer_deduplication(self):
        res = MaterialOptimizer.analyze_materials(["M_Titanium", "M_Carbon", "M_Titanium"])
        self.assertIn("MATERIAL_DEDUPLICATION", res["opportunities"])

    def test_10_texture_optimizer_resolution_options(self):
        res = TextureOptimizer.evaluate_resolution_tradeoff(current_resolution="4K", quality_floor=0.92)
        self.assertEqual(res["optimal_recommendation"], "2K")

    def test_11_lod_and_collision_optimizers(self):
        lod_res = LODOptimizer.evaluate_lods([15000, 7500, 3000])
        self.assertEqual(lod_res["status"], "OPTIMAL_LOD_CHAIN")

        col_res = CollisionOptimizer.evaluate_collision(hull_count=8, max_budget=12)
        self.assertEqual(col_res["status"], "OPTIMAL")

    # 8. Optimization Plan Building & Selection
    def test_12_plan_builder_selection_and_rejections(self):
        c_a = CandidateStrategy(
            candidate_id="C_HIGH_Q", strategy_name="High_Quality",
            quality_score=0.97, visual_score=0.96, geometry_score=0.96,
            cost_report=CostReport(generation_time=50.0),
            performance_report=PerformanceReport(asset_memory_estimate_mb=40.0)
        )
        c_b = CandidateStrategy(
            candidate_id="C_BALANCED", strategy_name="Balanced",
            quality_score=0.95, visual_score=0.95, geometry_score=0.95,
            cost_report=CostReport(generation_time=22.0),
            performance_report=PerformanceReport(asset_memory_estimate_mb=18.0)
        )
        c_c = CandidateStrategy(
            candidate_id="C_SUB_PAR", strategy_name="Sub_Par",
            quality_score=0.82, visual_score=0.80, geometry_score=0.80, # Violates floor
            cost_report=CostReport(generation_time=10.0),
            performance_report=PerformanceReport(asset_memory_estimate_mb=5.0)
        )

        plan = PlanBuilder.build_plan(
            plan_id="PLAN_TEST_01",
            semantic_id="weapon.darx.vandal.001",
            baseline={"quality_score": 0.90, "memory_mb": 25.0, "generation_time": 30.0, "total_cost": 100.0},
            candidates=[c_a, c_b, c_c],
            profile=OptimizationProfile.balanced(),
            floor=QualityFloor(overall_quality_floor=0.90)
        )

        self.assertIn("C_SUB_PAR", plan.rejected_strategy_ids)
        self.assertEqual(plan.selected_strategy_id, "C_BALANCED")

    # 9. Lifecycle Progression (Commit vs Rollback)
    def test_13_lifecycle_controller_commit(self):
        plan = OptimizationPlan(plan_id="P1", asset_semantic_id="w.vandal", baseline={})
        ctl = LifecycleController(plan)
        ctl.advance_to_apply()
        self.assertEqual(ctl.current_stage, LifecycleStage.APPLY)
        ctl.commit()
        self.assertEqual(ctl.current_stage, LifecycleStage.COMMIT)
        self.assertTrue(ctl.is_committed)

    def test_14_lifecycle_controller_rollback(self):
        plan = OptimizationPlan(plan_id="P2", asset_semantic_id="w.vandal", baseline={})
        ctl = LifecycleController(plan)
        ctl.rollback("Regression detected")
        self.assertEqual(ctl.current_stage, LifecycleStage.ROLLBACK)
        self.assertTrue(ctl.is_rolled_back)

    # 10. Governance & Unauthorized Protection
    def test_15_governance_blocks_unauthorized_agent(self):
        plan = OptimizationPlan(plan_id="P_GOV", asset_semantic_id="w.vandal", baseline={}, selected_strategy_id="C1")
        applied, msg = self.api.apply_optimization(plan, agent_id="agent.unauthorized")
        self.assertFalse(applied)
        self.assertIn("GOVERNANCE_DENIED", msg)

    # 11. Persistence & Audit Trail
    def test_16_store_persistence_and_audit_record(self):
        audit = AuditRecord(
            optimization_id="OPT_01",
            asset_id="weapon.vandal",
            baseline_id="BASE_01",
            profile="BALANCED",
            selected_candidate_id="C_BALANCED",
            rejected_candidate_ids=["C_REJ"],
            rejection_reasons={"C_REJ": "Floor violation"}
        )
        self.api.store.record_audit(audit)

        reloaded = CostPerformanceStore(self.cp_db)
        audits = reloaded.list_audits()
        self.assertEqual(len(audits), 1)
        self.assertEqual(audits[0].selected_candidate_id, "C_BALANCED")

    # 12. Full API End-to-End Execution
    def test_17_api_optimize_asset_end_to_end(self):
        c_a = CandidateStrategy(
            candidate_id="C_HQ", strategy_name="High_Quality",
            quality_score=0.96, visual_score=0.95, geometry_score=0.95,
            cost_report=CostReport(generation_time=45.0),
            performance_report=PerformanceReport(asset_memory_estimate_mb=30.0)
        )
        c_b = CandidateStrategy(
            candidate_id="C_BAL", strategy_name="Balanced",
            quality_score=0.94, visual_score=0.94, geometry_score=0.94,
            cost_report=CostReport(generation_time=20.0),
            performance_report=PerformanceReport(asset_memory_estimate_mb=15.0)
        )

        plan = self.api.optimize_asset(
            semantic_id="weapon.darx.vandal.001",
            baseline={"quality_score": 0.90, "memory_mb": 25.0, "generation_time": 30.0, "total_cost": 100.0},
            candidates=[c_a, c_b],
            profile=OptimizationProfile.balanced()
        )

        self.assertIsNotNone(plan.selected_strategy_id)
        self.assertEqual(len(self.api.store.list_audits()), 1)

    def test_18_fast_iteration_and_memory_first_profiles(self):
        fast_prof = OptimizationProfile.fast_iteration()
        mem_prof = OptimizationProfile.memory_first()
        self.assertGreater(fast_prof.weight_time, fast_prof.weight_memory)
        self.assertGreater(mem_prof.weight_memory, mem_prof.weight_time)

    def test_19_budget_status_near_limit(self):
        limits = BudgetLimits(polygon_budget=10000)
        status, _ = limits.check({"polygon_count": 9000})
        self.assertEqual(status, BudgetStatus.NEAR_LIMIT)

    def test_20_geometry_optimizer_under_budget(self):
        res = GeometryOptimizer.analyze_geometry(poly_count=4000, target_budget=15000)
        self.assertEqual(res["status"], "UNDER_BUDGET")

    def test_21_texture_optimizer_all_resolutions(self):
        res = TextureOptimizer.evaluate_resolution_tradeoff(current_resolution="2K", quality_floor=0.85)
        self.assertEqual(len(res["options"]), 4)

    def test_22_collision_optimizer_missing_collision(self):
        res = CollisionOptimizer.evaluate_collision(hull_count=0)
        self.assertEqual(res["status"], "MISSING_COLLISION")

    def test_23_plan_builder_dominated_candidate_marked(self):
        c1 = CandidateStrategy("C1", "High", quality_score=0.96, cost_report=CostReport(generation_time=20.0))
        c2 = CandidateStrategy("C2", "Dom", quality_score=0.90, cost_report=CostReport(generation_time=40.0))
        plan = PlanBuilder.build_plan("P", "w.vandal", {}, [c1, c2])
        self.assertIn("C1", plan.pareto_front_ids)
        self.assertNotIn("C2", plan.pareto_front_ids)

    def test_24_quality_floor_regression_delta_rejected(self):
        floor = QualityFloor(maximum_allowed_regression=0.00)
        passed, reason = floor.evaluate({"overall_quality": 0.95, "regression_delta": -0.05})
        self.assertFalse(passed)
        self.assertIn("Regression delta", reason)

    def test_25_api_check_budgets(self):
        limits = BudgetLimits(polygon_budget=20000)
        status, _ = self.api.check_budgets(limits, {"polygon_count": 15000})
        self.assertEqual(status, BudgetStatus.WITHIN_BUDGET)

    def test_26_api_build_pareto_front(self):
        c1 = {"candidate_id": "A", "quality_score": 0.95, "total_cost": 50.0, "memory_mb": 10.0, "generation_time": 10.0}
        c2 = {"candidate_id": "B", "quality_score": 0.85, "total_cost": 80.0, "memory_mb": 20.0, "generation_time": 20.0}
        non_dom, dom = self.api.build_pareto_front([c1, c2])
        self.assertEqual(len(non_dom), 1)
        self.assertEqual(non_dom[0]["candidate_id"], "A")

    def test_27_api_evaluate_cost_and_performance(self):
        cost_rep = self.api.evaluate_cost({"generation_time": 15.0, "memory_mb": 100.0})
        self.assertEqual(cost_rep.generation_time, 15.0)
        perf_rep = self.api.evaluate_performance({"triangle_count": 12000})
        self.assertEqual(perf_rep.triangle_count, 12000)

    def test_28_api_validation_failure_triggers_rollback(self):
        c_bad = CandidateStrategy("C_BAD", "Bad", quality_score=0.95)
        from src.golden import GoldenAsset, GoldenAssetStatus
        g = GoldenAsset("G_VANDAL", "weapon.darx.vandal.001", "Vandal", baseline_score=0.99, status=GoldenAssetStatus.ACTIVE)
        self.golden_api.registry.register(g, allow_update=True)
        self.golden_api.versions.register_version(g)

        plan = self.api.optimize_asset(
            semantic_id="weapon.darx.vandal.001",
            baseline={"quality_score": 0.90},
            candidates=[c_bad]
        )
        # Candidate score 0.95 vs Golden 0.99 -> delta -0.04 -> triggers rollback
        audits = self.api.store.list_audits()
        self.assertTrue(audits[-1].is_rolled_back)

    def test_29_knowledge_graph_node_recorded(self):
        c = CandidateStrategy("C_KG", "Kg", quality_score=0.95)
        plan = self.api.create_optimization_plan("PLAN_KG", "w.vandal", {}, [c])
        node = self.api.kg_bridge.kg.get_node("opt_plan:PLAN_KG")
        self.assertIsNotNone(node)

    def test_30_deterministic_plan_building(self):
        c = CandidateStrategy("C_DET", "Det", quality_score=0.95)
        plan1 = PlanBuilder.build_plan("P_DET1", "w.vandal", {}, [c])
        plan2 = PlanBuilder.build_plan("P_DET2", "w.vandal", {}, [c])
        self.assertEqual(plan1.selected_strategy_id, plan2.selected_strategy_id)

if __name__ == "__main__":
    unittest.main()

