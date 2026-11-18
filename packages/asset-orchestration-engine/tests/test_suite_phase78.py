import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.strategy_learning import (
    StrategyRecord, StrategyStatus, StrategyOutcome, LearningEvent,
    StrategyOptimizationProfile, FinalStatus,
    ProblemFeatures, FeatureExtractor, ProblemSignature, StrategySignature,
    StrategyHistory, OutcomeHistory, ExecutionHistory,
    StrategyAnalyzer, SuccessAnalyzer, FailureAnalyzer, CostAnalyzer, RegressionAnalyzer,
    CandidateScorer, ConfidenceEngine, ExplorationPolicy, StrategyRanker,
    TradeoffOptimizer, ParameterOptimizer, ConstraintOptimizer, StrategyOptimizer,
    OutcomeLearner, PatternLearner, TransferLearning,
    LearningGuard, StrategyGuard, RegressionGuard,
    StrategyLearningStore, StrategyLearningAPI
)
from src.evaluation import EvaluationBenchmarkAPI
from src.golden import GoldenAPI
from src.failure_analysis import FailureAnalysisAPI

class TestSuitePhase78StrategyLearningAndOptimization(unittest.TestCase):
    """
    Comprehensive test suite for Phase 78: Strategy Learning & Optimization System.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.strat_db = os.path.join(self.tmp_dir.name, "test_strategy_learning_store.json")
        self.eval_db = os.path.join(self.tmp_dir.name, "test_eval_store.json")
        self.golden_db = os.path.join(self.tmp_dir.name, "test_golden_store.json")
        self.failure_db = os.path.join(self.tmp_dir.name, "test_failure_store.json")

        self.eval_api = EvaluationBenchmarkAPI(persistence_path=self.eval_db)
        self.golden_api = GoldenAPI(persistence_path=self.golden_db)
        self.failure_api = FailureAnalysisAPI(persistence_path=self.failure_db, eval_api=self.eval_api, golden_api=self.golden_api)

        self.api = StrategyLearningAPI(
            persistence_path=self.strat_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api,
            failure_api=self.failure_api
        )

    def tearDown(self):
        self.tmp_dir.cleanup()

    # 1. Strategy Model Tests
    def test_01_strategy_record_creation_and_serialization(self):
        strat = StrategyRecord(
            strategy_id="STRAT_WEAPON_HIGH_POLY",
            asset_type="WEAPON",
            asset_class="RIFLE",
            average_quality_score=0.95
        )
        d = strat.to_dict()
        restored = StrategyRecord.from_dict(d)
        self.assertEqual(restored.strategy_id, "STRAT_WEAPON_HIGH_POLY")
        self.assertEqual(restored.average_quality_score, 0.95)
        self.assertEqual(restored.status, StrategyStatus.ACTIVE)

    def test_02_strategy_outcome_creation_and_serialization(self):
        outcome = StrategyOutcome(
            execution_id="EXEC_001",
            strategy_id="STRAT_WEAPON_HIGH_POLY",
            semantic_id="weapon.darx.vandal.001",
            quality_score=0.96,
            success=True
        )
        d = outcome.to_dict()
        restored = StrategyOutcome.from_dict(d)
        self.assertEqual(restored.execution_id, "EXEC_001")
        self.assertEqual(restored.quality_score, 0.96)
        self.assertTrue(restored.success)

    # 2. Feature Extraction & Problem Signatures
    def test_03_feature_extractor(self):
        req = {
            "category": "WEAPON",
            "complexity": "HIGH",
            "part_count": 8,
            "polygon_budget": 20000
        }
        features = FeatureExtractor.extract(req)
        self.assertEqual(features.asset_category, "WEAPON")
        self.assertEqual(features.part_count, 8)
        self.assertEqual(features.polygon_budget, 20000)

    def test_04_deterministic_problem_signatures(self):
        f1 = ProblemFeatures(asset_category="WEAPON", asset_complexity="HIGH")
        f2 = ProblemFeatures(asset_category="WEAPON", asset_complexity="HIGH")
        sig1 = ProblemSignature.compute(f1)
        sig2 = ProblemSignature.compute(f2)
        self.assertEqual(sig1, sig2)

    def test_05_strategy_signatures(self):
        s_dict = {"asset_type": "WEAPON", "generation_method": "MODULAR_PARAMETRIC"}
        sig = StrategySignature.compute(s_dict)
        self.assertIsInstance(sig, str)
        self.assertEqual(len(sig), 64)

    # 3. Strategy Store & History Persistence
    def test_06_store_persistence_and_reload(self):
        s = StrategyRecord(strategy_id="STRAT_PERSIST_01", average_quality_score=0.92)
        self.api.register_strategy(s)

        reloaded_api = StrategyLearningAPI(
            persistence_path=self.strat_db,
            eval_api=self.eval_api,
            golden_api=self.golden_api,
            failure_api=self.failure_api
        )
        fetched = reloaded_api.get_strategy("STRAT_PERSIST_01")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.average_quality_score, 0.92)

    # 4. Analysis Engines (Success, Failure, Cost, Regression)
    def test_07_success_analyzer_variance(self):
        outcomes = [
            StrategyOutcome("E1", "S1", "w1", quality_score=0.90),
            StrategyOutcome("E2", "S1", "w1", quality_score=0.94),
            StrategyOutcome("E3", "S1", "w1", quality_score=0.92)
        ]
        res = SuccessAnalyzer.analyze_success(outcomes)
        self.assertEqual(res["sample_count"], 3)
        self.assertEqual(res["quality_mean"], 0.92)

    def test_08_failure_analyzer_penalties(self):
        outcomes = [
            StrategyOutcome("E1", "S1", "w1", success=False, failure_count=1),
            StrategyOutcome("E2", "S1", "w1", success=True, failure_count=0)
        ]
        res = FailureAnalyzer.analyze_failures(outcomes)
        self.assertEqual(res["failure_rate"], 0.5)
        self.assertEqual(res["total_failures"], 1)

    def test_09_cost_analyzer_averages(self):
        outcomes = [
            StrategyOutcome("E1", "S1", "w1", resource_cost=100.0, generation_time=30.0, token_cost=1000),
            StrategyOutcome("E2", "S1", "w1", resource_cost=200.0, generation_time=50.0, token_cost=2000)
        ]
        res = CostAnalyzer.analyze_cost(outcomes)
        self.assertEqual(res["average_cost"], 150.0)
        self.assertEqual(res["average_time"], 40.0)
        self.assertEqual(res["average_tokens"], 1500)

    def test_10_regression_analyzer(self):
        outcomes = [
            StrategyOutcome("E1", "S1", "w1", regression_detected=True),
            StrategyOutcome("E2", "S1", "w1", regression_detected=False)
        ]
        res = RegressionAnalyzer.analyze_regression(outcomes)
        self.assertEqual(res["regression_count"], 1)
        self.assertTrue(res["is_high_risk"])

    # 5. Candidate Scoring & Profiles
    def test_11_candidate_scorer_quality_first_vs_performance_first(self):
        strat_high_q = StrategyRecord("S_HQ", average_quality_score=0.98, estimated_cost=250.0, estimated_time=90.0)
        strat_fast = StrategyRecord("S_FAST", average_quality_score=0.90, estimated_cost=50.0, estimated_time=15.0)

        q_prof = StrategyOptimizationProfile.quality_first()
        p_prof = StrategyOptimizationProfile.performance_first()

        score_hq_under_q = CandidateScorer.calculate_score(strat_high_q, q_prof)
        score_fast_under_q = CandidateScorer.calculate_score(strat_fast, q_prof)
        self.assertGreater(score_hq_under_q, score_fast_under_q)

        score_hq_under_p = CandidateScorer.calculate_score(strat_high_q, p_prof)
        score_fast_under_p = CandidateScorer.calculate_score(strat_fast, p_prof)
        self.assertGreater(score_fast_under_p, score_hq_under_p)

    # 6. Strategy Ranking & Determinism
    def test_12_strategy_ranker_deterministic(self):
        s1 = StrategyRecord("S1", average_quality_score=0.95, estimated_cost=100.0)
        s2 = StrategyRecord("S2", average_quality_score=0.88, estimated_cost=50.0)

        ranked = StrategyRanker.rank([s1, s2])
        self.assertEqual(ranked[0][0].strategy_id, "S1")

    def test_13_recommend_strategy_with_constraints(self):
        s1 = StrategyRecord("S_OVER_BUDGET", input_features={"polygon_budget": 50000})
        s2 = StrategyRecord("S_WITHIN_BUDGET", input_features={"polygon_budget": 12000})
        self.api.register_strategy(s1)
        self.api.register_strategy(s2)

        feat = ProblemFeatures(polygon_budget=15000)
        rec = self.api.recommend_strategy(features=feat)
        self.assertEqual(rec.strategy_id, "S_WITHIN_BUDGET")

    # 7. Pareto Optimization
    def test_14_pareto_front_computation(self):
        # S1: High Q (0.96), High Cost (100) -> Pareto
        s1 = StrategyRecord("S1", average_quality_score=0.96, estimated_cost=100.0, estimated_time=50.0)
        # S2: Good Q (0.94), Low Cost (40) -> Pareto
        s2 = StrategyRecord("S2", average_quality_score=0.94, estimated_cost=40.0, estimated_time=20.0)
        # S3: Dominated by S2 (Lower Q 0.90, Higher Cost 60) -> Dominated
        s3 = StrategyRecord("S3", average_quality_score=0.90, estimated_cost=60.0, estimated_time=30.0)

        pareto = TradeoffOptimizer.compute_pareto_front([s1, s2, s3])
        pareto_ids = [s.strategy_id for s in pareto]
        self.assertIn("S1", pareto_ids)
        self.assertIn("S2", pareto_ids)
        self.assertNotIn("S3", pareto_ids)

    # 8. Learning & Moving Averages
    def test_15_outcome_learner_incremental_update(self):
        strat = StrategyRecord("S_LEARN", average_quality_score=0.90, sample_count=1)
        outcome = StrategyOutcome("E1", "S_LEARN", "w.vandal", quality_score=0.96, success=True)

        evt = OutcomeLearner.learn_from_outcome(strat, outcome)
        self.assertEqual(strat.sample_count, 2)
        self.assertEqual(strat.average_quality_score, 0.93)
        self.assertGreater(evt.delta_quality, 0.0)

    # 9. Parameter & Strategy Optimization
    def test_16_parameter_optimizer_recommendation(self):
        configs = [
            {"params": {"poly_budget": 10000}, "score": 0.88},
            {"params": {"poly_budget": 15000}, "score": 0.95},
            {"params": {"poly_budget": 20000}, "score": 0.91}
        ]
        best_poly = ParameterOptimizer.recommend_best_parameter(configs, "poly_budget")
        self.assertEqual(best_poly, 15000)

    def test_17_strategy_optimizer_derive_version(self):
        base = StrategyRecord("STRAT_V1", strategy_version="1.0.0", average_quality_score=0.90)
        v2 = StrategyOptimizer.derive_optimized_version(base, {"bevel": 0.05})
        self.assertEqual(v2.strategy_version, "2.0.0")
        self.assertEqual(v2.parent_strategy_id, "STRAT_V1")

    # 10. Transfer Learning
    def test_18_transfer_learning_similarity_and_discount(self):
        sim = TransferLearning.calculate_similarity("RIFLE", "SMG")
        self.assertEqual(sim, 0.85)

        s_rifle = StrategyRecord("S_RIFLE", asset_class="RIFLE", confidence=0.90)
        s_smg = TransferLearning.transfer_strategy(s_rifle, "SMG", "S_SMG_TRANSFERRED")
        self.assertEqual(s_smg.asset_class, "SMG")
        self.assertLess(s_smg.confidence, s_rifle.confidence)

    # 11. Safety & Learning Guards
    def test_19_learning_guard_rejects_corrupted_result(self):
        corrupted = StrategyOutcome("E_CORRUPT", "S1", "w1", success=False, quality_score=0.0)
        valid, msg = LearningGuard.is_outcome_valid_for_learning(corrupted)
        self.assertFalse(valid)

    def test_20_strategy_guard_protects_system_defaults(self):
        self.assertFalse(StrategyGuard.can_modify_strategy("SYSTEM_DEFAULT_STRATEGY"))
        self.assertTrue(StrategyGuard.can_modify_strategy("CUSTOM_USER_STRATEGY"))

    # 12. A/B Strategy Comparison
    def test_21_compare_strategies_api(self):
        s_a = StrategyRecord("STRAT_A", average_quality_score=0.96, estimated_cost=100.0)
        s_b = StrategyRecord("STRAT_B", average_quality_score=0.91, estimated_cost=60.0)
        self.api.register_strategy(s_a)
        self.api.register_strategy(s_b)

        comp = self.api.compare_strategies("STRAT_A", "STRAT_B")
        self.assertEqual(comp["winner"], "STRAT_A")
        self.assertEqual(comp["delta_quality"], 0.05)

    # 13. Full API End-to-End Workflow
    def test_22_api_record_outcome_updates_strategy_and_events(self):
        strat = StrategyRecord("STRAT_FLOW", average_quality_score=0.88, sample_count=1)
        self.api.register_strategy(strat)

        outcome = StrategyOutcome("EXEC_FLOW_1", "STRAT_FLOW", "weapon.vandal", quality_score=0.98, success=True)
        self.api.record_outcome(outcome)

        updated = self.api.get_strategy("STRAT_FLOW")
        self.assertEqual(updated.sample_count, 2)
        self.assertEqual(updated.average_quality_score, 0.93)

        events = self.api.store.list_events()
        self.assertGreaterEqual(len(events), 1)

    def test_23_api_find_similar_cases(self):
        s1 = StrategyRecord("S_RIFLE_1", asset_class="RIFLE")
        s2 = StrategyRecord("S_RIFLE_2", asset_class="RIFLE")
        s3 = StrategyRecord("S_PISTOL", asset_class="PISTOL")
        self.api.register_strategy(s1)
        self.api.register_strategy(s2)
        self.api.register_strategy(s3)

        rifles = self.api.find_similar_cases("RIFLE")
        self.assertEqual(len(rifles), 2)

    def test_24_api_learning_statistics(self):
        strat = StrategyRecord("S_STAT", average_quality_score=0.90)
        self.api.register_strategy(strat)
        outcome = StrategyOutcome("E_STAT", "S_STAT", "w.vandal", success=True)
        self.api.record_outcome(outcome)

        stats = self.api.get_learning_statistics()
        self.assertGreaterEqual(stats["total_strategies"], 1)
        self.assertGreaterEqual(stats["total_outcomes"], 1)
        self.assertEqual(stats["success_rate"], 1.0)

    def test_25_pattern_learner_discover_best_methods(self):
        s1 = StrategyRecord("S1", average_quality_score=0.88, generation_method="CSG_BOOLEAN")
        s2 = StrategyRecord("S2", average_quality_score=0.96, generation_method="MODULAR_PARAMETRIC")
        best = PatternLearner.discover_best_methods([s1, s2])
        self.assertEqual(best["preferred_generation_method"], "MODULAR_PARAMETRIC")

    def test_26_strategy_versioning_and_parent_links(self):
        base = StrategyRecord("STRAT_ORIGIN", strategy_version="1.0.0")
        self.api.register_strategy(base)
        opt = self.api.optimize_strategy("STRAT_ORIGIN", {"lod_ratios": [0.5, 0.25, 0.1]})
        self.assertEqual(opt.parent_strategy_id, "STRAT_ORIGIN")
        self.assertEqual(opt.strategy_version, "2.0.0")

    def test_27_execution_history_recording(self):
        self.api.execution_history.record_trace("JOB_101", "agent.strategy", "STRAT_A", "weapon.vandal")
        traces = self.api.execution_history.list_traces()
        self.assertEqual(len(traces), 1)
        self.assertEqual(traces[0]["job_id"], "JOB_101")

    def test_28_learning_guard_regression_rejection(self):
        bad_outcome = StrategyOutcome(
            "E_REG", "S1", "w.vandal", success=False, regression_detected=True, golden_asset_delta=-0.15
        )
        valid, msg = LearningGuard.is_outcome_valid_for_learning(bad_outcome)
        self.assertFalse(valid)
        self.assertIn("Severe regression", msg)

    def test_29_confidence_engine_asymptotic_growth(self):
        c1 = ConfidenceEngine.compute_confidence(sample_count=1, failure_rate=0.0, regression_rate=0.0)
        c20 = ConfidenceEngine.compute_confidence(sample_count=20, failure_rate=0.0, regression_rate=0.0)
        self.assertGreater(c20, c1)

    def test_30_pareto_front_all_non_dominated(self):
        # 3 strategies with distinct trade-offs: High Q / High Cost, Med Q / Med Cost, Low Q / Low Cost
        s1 = StrategyRecord("S1", average_quality_score=0.98, estimated_cost=150.0, estimated_time=80.0)
        s2 = StrategyRecord("S2", average_quality_score=0.92, estimated_cost=80.0, estimated_time=40.0)
        s3 = StrategyRecord("S3", average_quality_score=0.85, estimated_cost=30.0, estimated_time=15.0)

        pareto = TradeoffOptimizer.compute_pareto_front([s1, s2, s3])
        self.assertEqual(len(pareto), 3)

    def test_31_constraint_optimizer_rejects_exceeded_poly_budget(self):
        s = StrategyRecord("S_EXPENSIVE", input_features={"polygon_budget": 50000})
        feat = ProblemFeatures(polygon_budget=20000)
        self.assertFalse(ConstraintOptimizer.validate_constraints(s, feat))

    def test_32_strategy_learning_api_get_strategy_history(self):
        s = StrategyRecord("S_HIST", average_quality_score=0.91)
        self.api.register_strategy(s)
        o1 = StrategyOutcome("E1", "S_HIST", "w.vandal", quality_score=0.92)
        o2 = StrategyOutcome("E2", "S_HIST", "w.vandal", quality_score=0.94)
        self.api.record_outcome(o1)
        self.api.record_outcome(o2)

        history = self.api.get_strategy_history("S_HIST")
        self.assertEqual(len(history), 2)

if __name__ == "__main__":
    unittest.main()

