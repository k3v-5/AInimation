import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluation import (
    EvaluationDimension, DefectSeverity, DefectStatus, BenchmarkStatus, AcceptanceDecision,
    EvaluationDefect, DimensionScore, EvaluationProfile, EvaluationBenchmark,
    create_weapon_profile, create_unreal_ready_profile, create_visual_asset_profile, ProfileRegistry,
    DimensionEvaluator, ABComparisonEngine, ABComparisonResult, RegressionDetector, RegressionReport,
    EvaluationStore, BenchmarkCorruptedError, BenchmarkFinalizedImmutableError,
    EvaluationGovernanceGuard, EvaluationPermissionDeniedError, KnowledgeGraphEvaluationBridge,
    EvaluationBenchmarkAPI
)

class TestSuitePhase75EvaluationBenchmarkSystem(unittest.TestCase):
    """
    Complete unit and integration test suite for Phase 75: Evaluation Benchmark System.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_benchmarks.json")
        self.api = EvaluationBenchmarkAPI(persistence_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_01_profile_registry_and_default_weapon_profile(self):
        profile = self.api.profiles.get_profile("PROFILE_WEAPON_DARX")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.minimum_global_score, 0.85)
        self.assertIn(EvaluationDimension.GEOMETRY, profile.critical_dimensions)
        self.assertIn(EvaluationDimension.ENGINE_READINESS, profile.critical_dimensions)

    def test_02_dimension_evaluation_geometry_clean(self):
        data = {"polygon_count": 8500, "non_manifold_count": 0}
        score = self.api.evaluate_dimension(EvaluationDimension.GEOMETRY, data)
        self.assertEqual(score.score, 1.0)
        self.assertEqual(len(score.defects), 0)

    def test_03_dimension_evaluation_geometry_non_manifold_defect(self):
        data = {"polygon_count": 8500, "non_manifold_count": 4}
        score = self.api.evaluate_dimension(EvaluationDimension.GEOMETRY, data)
        self.assertLess(score.score, 1.0)
        self.assertEqual(len(score.defects), 1)
        self.assertEqual(score.defects[0].severity, DefectSeverity.MAJOR)

    def test_04_full_asset_evaluation_and_acceptance_pass(self):
        asset_data = {
            "polygon_count": 9200,
            "non_manifold_count": 0,
            "materials": ["M_Titanium", "M_Carbon"],
            "has_collision": True,
            "lod_count": 3,
            "engine_readiness_score": 0.96,
            "silhouette_similarity": 0.92,
            "visual_match_score": 0.90
        }
        bench = self.api.evaluate_asset(
            asset_semantic_id="weapon.darx.vandal.001",
            candidate_id="cand_v1",
            asset_data=asset_data,
            profile_id="PROFILE_WEAPON_DARX"
        )
        self.assertGreaterEqual(bench.weighted_score, 0.85)
        self.assertEqual(bench.acceptance, AcceptanceDecision.APPROVED)
        self.assertTrue(bench.verify_integrity())

    def test_05_critical_dimension_failure_causes_rejection(self):
        # Good global scores but fails critical engine readiness
        asset_data = {
            "polygon_count": 9200,
            "materials": ["M_Titanium"],
            "has_collision": True,
            "lod_count": 3,
            "invalid_scale_or_axis": True, # Triggers critical engine readiness defect
            "engine_readiness_score": 0.50
        }
        bench = self.api.evaluate_asset(
            asset_semantic_id="weapon.darx.vandal.001",
            candidate_id="cand_bad_axis",
            asset_data=asset_data,
            profile_id="PROFILE_WEAPON_DARX"
        )
        self.assertEqual(bench.acceptance, AcceptanceDecision.REJECTED)
        critical_defs = [d for d in bench.defects if d.severity == DefectSeverity.CRITICAL]
        self.assertGreaterEqual(len(critical_defs), 1)

    def test_06_ab_comparison_detects_superior_candidate(self):
        base_data = {"polygon_count": 5000, "materials": ["M_Base"], "lod_count": 1, "silhouette_similarity": 0.70}
        cand_data = {"polygon_count": 8000, "materials": ["M_Titanium", "M_Carbon"], "lod_count": 3, "silhouette_similarity": 0.95}

        bench_a = self.api.evaluate_asset("weapon.vandal", "candidate_a", base_data, benchmark_id="B_A")
        bench_b = self.api.evaluate_asset("weapon.vandal", "candidate_b", cand_data, benchmark_id="B_B")

        comp = self.api.compare_assets(bench_a, bench_b)
        self.assertEqual(comp.winner, "candidate_b")
        self.assertGreater(comp.global_delta, 0.0)
        self.assertGreater(len(comp.improvements), 0)

    def test_07_regression_detection_against_baseline(self):
        base_data = {"polygon_count": 9000, "materials": ["M_Titanium"], "has_collision": True, "lod_count": 3}
        cand_data = {"polygon_count": 9000, "materials": [], "has_collision": False, "lod_count": 0} # Regressed

        baseline = self.api.evaluate_asset("weapon.vandal", "baseline_v1", base_data, benchmark_id="BASE_01")
        candidate = self.api.evaluate_asset("weapon.vandal", "candidate_v2", cand_data, benchmark_id="CAND_01", baseline_id="BASE_01")

        reg_rep = self.api.detect_regressions(candidate, baseline)
        self.assertTrue(reg_rep.has_regression)
        self.assertIn("MATERIAL (-0.5)", reg_rep.regressed_dimensions)
        self.assertIn("COLLISION (-0.6)", reg_rep.regressed_dimensions)

    def test_08_benchmark_determinism(self):
        asset_data = {"polygon_count": 7500, "materials": ["M_Titanium"], "lod_count": 3}
        run1 = self.api.evaluate_asset("weapon.vandal", "run1", asset_data, benchmark_id="R1")
        run2 = self.api.evaluate_asset("weapon.vandal", "run2", asset_data, benchmark_id="R2")
        self.assertEqual(round(run1.weighted_score, 4), round(run2.weighted_score, 4))
        self.assertEqual(run1.acceptance, run2.acceptance)

    def test_09_persistence_and_reload(self):
        asset_data = {"polygon_count": 8000, "materials": ["M_Titanium"]}
        bench = self.api.evaluate_asset("weapon.vandal", "cand_pers", asset_data, benchmark_id="BENCH_PERSIST")

        # New API instance reading same persistence file
        api2 = EvaluationBenchmarkAPI(persistence_path=self.db_path)
        fetched = api2.get_benchmark("BENCH_PERSIST")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.candidate_id, "cand_pers")
        self.assertTrue(fetched.verify_integrity())

    def test_10_tampered_benchmark_corruption_detection(self):
        asset_data = {"polygon_count": 8000, "materials": ["M_Titanium"]}
        bench = self.api.evaluate_asset("weapon.vandal", "cand_tamp", asset_data, benchmark_id="BENCH_TAMP")
        
        # Tamper with score without recalculating hash
        bench.weighted_score = 0.999
        self.assertFalse(bench.verify_integrity())

    def test_11_governance_finalized_benchmark_immutability(self):
        asset_data = {"polygon_count": 8000, "materials": ["M_Titanium"]}
        bench = self.api.evaluate_asset("weapon.vandal", "cand_final", asset_data, benchmark_id="BENCH_FINAL")
        self.api.finalize_benchmark("BENCH_FINAL", agent_id="agent.visual.critic")

        # Attempting to mutate finalized benchmark raises error
        with self.assertRaises(BenchmarkFinalizedImmutableError):
            self.api.store.store_benchmark(bench)

    def test_12_knowledge_graph_sync_bridge(self):
        asset_data = {"polygon_count": 8000, "materials": ["M_Titanium"], "non_manifold_count": 2}
        bench = self.api.evaluate_asset("weapon.darx.vandal.001", "cand_kg", asset_data, benchmark_id="BENCH_KG_TEST")
        self.api.finalize_benchmark("BENCH_KG_TEST", agent_id="agent.visual.critic")

        # Verification via KG
        eval_node = self.api.kg_bridge.kg.get_node("EVAL_BENCH_KG_TEST")
        self.assertIsNotNone(eval_node)

    def test_13_benchmark_text_report_generation(self):
        asset_data = {"polygon_count": 8000, "materials": ["M_Titanium"]}
        bench = self.api.evaluate_asset("weapon.vandal", "cand_rep", asset_data, benchmark_id="BENCH_REPORT")
        report = self.api.generate_benchmark_report("BENCH_REPORT")
        self.assertIn("F75 BENCHMARK REPORT", report)
        self.assertIn("Global Score:", report)
        self.assertIn("DIMENSION BREAKDOWN:", report)

    def test_14_aggregated_statistics(self):
        self.api.evaluate_asset("weapon.1", "c1", {"polygon_count": 8000, "materials": ["M1"]})
        self.api.evaluate_asset("weapon.2", "c2", {"polygon_count": 3000, "materials": []})
        stats = self.api.get_statistics()
        self.assertEqual(stats["total_benchmarks"], 2)
        self.assertGreater(stats["average_score"], 0.0)

    def test_15_material_evaluation_empty_materials_defect(self):
        score = self.api.evaluate_dimension(EvaluationDimension.MATERIAL, {"materials": []})
        self.assertLess(score.score, 1.0)
        self.assertEqual(len(score.defects), 1)
        self.assertEqual(score.defects[0].defect_id, "DEF_MAT_MISSING")

    def test_16_lod_metrics_evaluation(self):
        score_3lod = self.api.evaluate_dimension(EvaluationDimension.LOD, {"lod_count": 3})
        score_1lod = self.api.evaluate_dimension(EvaluationDimension.LOD, {"lod_count": 1})
        self.assertEqual(score_3lod.score, 1.0)
        self.assertLess(score_1lod.score, 1.0)

    def test_17_collision_metrics_evaluation(self):
        score_col = self.api.evaluate_dimension(EvaluationDimension.COLLISION, {"has_collision": True})
        score_no_col = self.api.evaluate_dimension(EvaluationDimension.COLLISION, {"has_collision": False})
        self.assertEqual(score_col.score, 1.0)
        self.assertLess(score_no_col.score, 1.0)

    def test_18_unreal_ready_profile_evaluation(self):
        asset_data = {
            "polygon_count": 5000,
            "materials": ["M_Titanium"],
            "has_collision": True,
            "lod_count": 3,
            "engine_readiness_score": 0.98
        }
        bench = self.api.evaluate_asset(
            "weapon.darx.vandal.001", "cand_ue", asset_data, profile_id="PROFILE_UNREAL_READY"
        )
        self.assertGreaterEqual(bench.weighted_score, 0.90)
        self.assertEqual(bench.acceptance, AcceptanceDecision.APPROVED)

    def test_19_reproduce_benchmark_evaluation(self):
        asset_data = {"polygon_count": 6000, "materials": ["M_Titanium"]}
        b1 = self.api.evaluate_asset("weapon.vandal", "cand_orig", asset_data, benchmark_id="B_ORIG")
        b_repro = self.api.reproduce_benchmark("B_ORIG", asset_data)
        self.assertEqual(round(b1.weighted_score, 4), round(b_repro.weighted_score, 4))

    def test_20_topology_loose_geometry_defect(self):
        score = self.api.evaluate_dimension(EvaluationDimension.TOPOLOGY, {"has_loose_geometry": True})
        self.assertLess(score.score, 0.90)
        self.assertEqual(len(score.defects), 1)
        self.assertEqual(score.defects[0].defect_id, "DEF_TOP_LOOSE_GEO")

    def test_21_visual_art_profile_evaluation(self):
        asset_data = {
            "silhouette_similarity": 0.88,
            "visual_match_score": 0.91,
            "style_score": 0.95
        }
        bench = self.api.evaluate_asset("weapon.vandal", "cand_art", asset_data, profile_id="PROFILE_VISUAL_ART")
        self.assertGreaterEqual(bench.weighted_score, 0.80)

    def test_22_uv_overlap_defect_detection(self):
        score = self.api.evaluate_dimension(EvaluationDimension.UV, {"uv_overlaps": 3})
        self.assertLess(score.score, 0.95)
        self.assertEqual(len(score.defects), 1)
        self.assertEqual(score.defects[0].defect_id, "DEF_UV_OVERLAP")

    def test_23_empty_benchmark_statistics(self):
        api_empty = EvaluationBenchmarkAPI(persistence_path=os.path.join(self.tmp_dir.name, "empty.json"))
        stats = api_empty.get_statistics()
        self.assertEqual(stats["total_benchmarks"], 0)

    def test_24_f70_job_and_checkpoint_association(self):
        bench = self.api.evaluate_asset(
            asset_semantic_id="weapon.darx.vandal.001",
            candidate_id="cand_job",
            asset_data={"polygon_count": 8000, "materials": ["M_Titanium"]},
            job_id="JOB_F70_RECOVERY",
            agent_id="agent.visual.critic"
        )
        self.assertEqual(bench.job_id, "JOB_F70_RECOVERY")
        self.assertEqual(bench.agent_id, "agent.visual.critic")

    def test_25_f72_unregistered_agent_evaluation_denial(self):
        bench = self.api.evaluate_asset("weapon.vandal", "c1", {"polygon_count": 5000})
        with self.assertRaises(EvaluationPermissionDeniedError):
            self.api.finalize_benchmark(bench.benchmark_id, agent_id="agent.unregistered.hacker")

    def test_26_ab_comparison_tie_result(self):
        data = {"polygon_count": 5000, "materials": ["M_Titanium"]}
        b1 = self.api.evaluate_asset("weapon.vandal", "c1", data, benchmark_id="B_TIE1")
        b2 = self.api.evaluate_asset("weapon.vandal", "c2", data, benchmark_id="B_TIE2")
        res = self.api.compare_assets(b1, b2)
        self.assertEqual(res.winner, "TIE")
        self.assertEqual(res.global_delta, 0.0)

    def test_27_regression_detector_new_critical_defect(self):
        base_bench = self.api.evaluate_asset("weapon.vandal", "b1", {"polygon_count": 5000, "materials": ["M_Titanium"]})
        cand_bench = self.api.evaluate_asset("weapon.vandal", "c1", {
            "polygon_count": 5000, "materials": ["M_Titanium"], "invalid_scale_or_axis": True
        })
        rep = self.api.detect_regressions(cand_bench, base_bench)
        self.assertTrue(rep.has_regression)
        self.assertTrue(rep.critical_regression_detected)

    def test_28_corrupted_disk_file_detection(self):
        self.api.evaluate_asset("weapon.vandal", "cand_corrupt", {"polygon_count": 5000}, benchmark_id="BENCH_CORR")
        
        # Modify file on disk with wrong hash
        with open(self.db_path, "r", encoding="utf-8") as f:
            raw = f.read()
        corrupted = raw.replace('"weighted_score": 0.0', '"weighted_score": 0.9999')
        if corrupted == raw:
            # Replace candidate_id or any other hashed field
            corrupted = raw.replace('"cand_corrupt"', '"cand_tampered"')
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write(corrupted)

        with self.assertRaises(BenchmarkCorruptedError):
            api_corrupt = EvaluationBenchmarkAPI(persistence_path=self.db_path)

    def test_29_dimension_score_serialization_roundtrip(self):
        ds = DimensionScore(dimension=EvaluationDimension.MATERIAL, score=0.88, weight=1.5, weighted_score=1.32)
        d_dict = ds.to_dict()
        ds_restored = DimensionScore.from_dict(d_dict)
        self.assertEqual(ds.dimension, ds_restored.dimension)
        self.assertEqual(ds.score, ds_restored.score)

    def test_30_defect_serialization_roundtrip(self):
        defect = EvaluationDefect(
            defect_id="DEF_001", category="GEO", severity=DefectSeverity.MAJOR,
            dimension=EvaluationDimension.GEOMETRY, description="Test defect", blocking=True
        )
        d_dict = defect.to_dict()
        restored = EvaluationDefect.from_dict(d_dict)
        self.assertEqual(defect.defect_id, restored.defect_id)
        self.assertEqual(defect.severity, restored.severity)
        self.assertTrue(restored.blocking)

    def test_31_profile_serialization_roundtrip(self):
        prof = create_weapon_profile()
        p_dict = prof.to_dict()
        restored = EvaluationProfile.from_dict(p_dict)
        self.assertEqual(prof.profile_id, restored.profile_id)
        self.assertEqual(prof.minimum_global_score, restored.minimum_global_score)

    def test_32_global_score_calculation_edge_cases(self):
        bench = EvaluationBenchmark(
            benchmark_id="B_EDGE", project_id="DarX", asset_semantic_id="w.edge",
            candidate_id="c.edge", evaluation_profile=create_weapon_profile()
        )
        bench.calculate_global_score()
        self.assertEqual(bench.weighted_score, 0.0)
        self.assertEqual(bench.acceptance, AcceptanceDecision.REJECTED)

if __name__ == "__main__":
    unittest.main()
