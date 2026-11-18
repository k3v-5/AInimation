import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.golden import (
    GoldenAssetStatus, MutationType, RegressionLevel, GoldenAssetException,
    GoldenImmutabilityError, GoldenIntegrityError, GoldenDuplicateError, GoldenAuthorizationError,
    GoldenAsset, GoldenIdentityHelper, AssetFingerprinter, GeometryFingerprinter,
    MaterialFingerprinter, SceneFingerprinter, ReferenceFingerprinter, GoldenRegistry,
    VersionRegistry, GoldenStore, ManifestStore, IntegrityStore, GoldenComparator,
    GoldenComparisonResult, RegressionPolicy, CompatibilityChecker, ImmutabilityGuard,
    MutationDetector, AuthorizationGuard, EvaluationBridge, KnowledgeGraphBridge,
    RecoveryBridge, GoldenAPI
)
from src.evaluation import (
    EvaluationBenchmarkAPI, EvaluationBenchmark, AcceptanceDecision, DefectSeverity, EvaluationDefect
)

class TestSuitePhase76GoldenAssetsAndBaselineLibrary(unittest.TestCase):
    """
    Comprehensive test suite for Phase 76: Golden Assets & Baseline Reference Library.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_golden_store.json")
        self.eval_db_path = os.path.join(self.tmp_dir.name, "test_eval_store.json")
        self.api = GoldenAPI(persistence_path=self.db_path)
        self.eval_api = EvaluationBenchmarkAPI(persistence_path=self.eval_db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def _create_sample_asset_data(self) -> dict:
        return {
            "geometry": {
                "object_names": ["Body", "Barrel", "Magazine"],
                "mesh_names": ["SM_Body", "SM_Barrel", "SM_Mag"],
                "vertex_count": 4200,
                "polygon_count": 8500,
                "edge_count": 12700,
                "lod_count": 3,
                "collision_hulls": 1
            },
            "materials": {
                "material_names": ["M_Dark_Titanium", "M_Matte_Carbon"],
                "metallic": 0.85,
                "roughness": 0.35,
                "textures": ["T_Vandal_D", "T_Vandal_ORM", "T_Vandal_N"]
            },
            "scene": {
                "collection_names": ["Weapon_Vandal", "LODs", "Collisions"],
                "pivot": [0.0, 0.0, 0.0]
            },
            "unreal_readiness": {
                "axis": "X_FORWARD_Z_UP",
                "unit_scale": 1.0,
                "collision": True,
                "lods": 3
            }
        }

    def _create_approved_benchmark(self, b_id="BENCH_001") -> EvaluationBenchmark:
        bench = self.eval_api.evaluate_asset(
            asset_semantic_id="weapon.darx.vandal.001",
            candidate_id="cand_vandal_01",
            asset_data={
                "polygon_count": 8500,
                "materials": ["M_Dark_Titanium", "M_Matte_Carbon"],
                "lod_count": 3,
                "has_collision": True,
                "engine_readiness_score": 0.95,
                "silhouette_similarity": 0.94,
                "visual_match_score": 0.92
            },
            benchmark_id=b_id
        )
        return self.eval_api.finalize_benchmark(bench.benchmark_id)

    # 1. Identity & Naming Tests
    def test_01_golden_identity_generation_and_parsing(self):
        g_id = GoldenIdentityHelper.generate_golden_id("weapon.darx.vandal.001", version=1)
        self.assertEqual(g_id, "golden.weapon.darx.vandal.001.v1")

        sem_id, ver = GoldenIdentityHelper.parse_golden_id(g_id)
        self.assertEqual(sem_id, "weapon.darx.vandal.001")
        self.assertEqual(ver, 1)

        next_id = GoldenIdentityHelper.next_golden_id(g_id)
        self.assertEqual(next_id, "golden.weapon.darx.vandal.001.v2")

    def test_02_golden_asset_model_creation_and_integrity(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset(
            golden_id="golden.weapon.darx.vandal.001.v1",
            semantic_id="weapon.darx.vandal.001",
            asset_name="DarX Vandal Rifle",
            fingerprint=fps,
            baseline_score=0.9450
        )
        self.assertTrue(asset.verify_integrity())
        self.assertEqual(asset.status, GoldenAssetStatus.DRAFT)

    # 2. Fingerprinting Tests
    def test_03_deterministic_fingerprint_generation(self):
        data = self._create_sample_asset_data()
        fp1 = AssetFingerprinter.compute_all(data)
        fp2 = AssetFingerprinter.compute_all(data)
        self.assertEqual(fp1["asset"], fp2["asset"])
        self.assertEqual(fp1["geometry"], fp2["geometry"])
        self.assertEqual(fp1["materials"], fp2["materials"])

    def test_04_fingerprint_sensitivity_to_geometry_changes(self):
        data1 = self._create_sample_asset_data()
        data2 = self._create_sample_asset_data()
        data2["geometry"]["polygon_count"] = 9999

        fp1 = AssetFingerprinter.compute_all(data1)
        fp2 = AssetFingerprinter.compute_all(data2)
        self.assertNotEqual(fp1["geometry"], fp2["geometry"])
        self.assertNotEqual(fp1["asset"], fp2["asset"])
        self.assertEqual(fp1["materials"], fp2["materials"])

    def test_05_fingerprint_sensitivity_to_material_changes(self):
        data1 = self._create_sample_asset_data()
        data2 = self._create_sample_asset_data()
        data2["materials"]["metallic"] = 0.10

        fp1 = AssetFingerprinter.compute_all(data1)
        fp2 = AssetFingerprinter.compute_all(data2)
        self.assertNotEqual(fp1["materials"], fp2["materials"])
        self.assertEqual(fp1["geometry"], fp2["geometry"])

    # 3. Registry & Version Registry Tests
    def test_06_golden_registry_registration_and_duplicate_rejection(self):
        reg = GoldenRegistry()
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        a1 = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps)
        reg.register(a1)

        a_dup = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps)
        with self.assertRaises(GoldenDuplicateError):
            reg.register(a_dup)

    def test_07_version_registry_supersession(self):
        vreg = VersionRegistry()
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        v1 = GoldenAsset("golden.w.001.v1", "w.001", "W1", version=1, status=GoldenAssetStatus.ACTIVE, fingerprint=fps)
        vreg.register_version(v1)

        v2 = GoldenAsset("golden.w.001.v2", "w.001", "W1", version=2, status=GoldenAssetStatus.DRAFT, fingerprint=fps)
        vreg.supersede_version(v1, v2)

        self.assertEqual(v1.status, GoldenAssetStatus.SUPERSEDED)
        self.assertEqual(v2.status, GoldenAssetStatus.ACTIVE)
        self.assertEqual(v2.parent_golden_id, "golden.w.001.v1")

    # 4. Storage & Manifest Tests
    def test_08_manifest_generation_and_verification(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps, baseline_score=0.92)
        manifest = ManifestStore.generate_manifest(asset)
        self.assertTrue(ManifestStore.verify_manifest(manifest))

    def test_09_corrupted_manifest_verification_failure(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps, baseline_score=0.92)
        manifest = ManifestStore.generate_manifest(asset)
        manifest["evaluation"]["score"] = 0.10 # Tamper
        self.assertFalse(ManifestStore.verify_manifest(manifest))

    def test_10_golden_store_persistence_and_reload(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_STORE")
        asset = self.api.create_golden("weapon.vandal", "Vandal", data, bench)
        self.api.activate_golden(asset.golden_id, bench)

        api_reloaded = GoldenAPI(persistence_path=self.db_path)
        fetched = api_reloaded.get_golden(asset.golden_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.status, GoldenAssetStatus.ACTIVE)
        self.assertTrue(fetched.verify_integrity())

    # 5. Immutability & Mutation Detection Tests
    def test_11_immutability_guard_blocks_active_asset_modification(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_IMMUT")
        asset = self.api.create_golden("weapon.vandal", "Vandal", data, bench)
        self.api.activate_golden(asset.golden_id, bench)

        with self.assertRaises(GoldenImmutabilityError):
            self.api.store.store_golden(asset, allow_update=False)

    def test_12_mutation_detector_identifies_exact_changed_dimension(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps)

        # Mutate material only
        data_mod = self._create_sample_asset_data()
        data_mod["materials"]["metallic"] = 0.05
        fps_mod = AssetFingerprinter.compute_all(data_mod)

        m_type, diffs = MutationDetector.detect_mutations(asset, fps_mod)
        self.assertEqual(m_type, MutationType.MATERIAL_CHANGED)
        self.assertIn("materials", diffs)

    # 6. Comparison & Regression Policy Tests
    def test_13_golden_comparator_detects_improvement(self):
        data = self._create_sample_asset_data()
        bench_base = self._create_approved_benchmark("B_BASE")
        golden = self.api.create_golden("weapon.vandal", "Vandal", data, bench_base)
        self.api.activate_golden(golden.golden_id, bench_base)

        cand_bench = self.eval_api.evaluate_asset(
            "weapon.vandal", "cand_better",
            {"polygon_count": 8500, "materials": ["M1", "M2"], "visual_match_score": 0.98, "silhouette_similarity": 0.98},
            benchmark_id="B_BETTER"
        )
        res = self.api.compare_with_golden(cand_bench, golden.golden_id)
        self.assertIn(res.overall_status, [RegressionLevel.IMPROVEMENT, RegressionLevel.ACCEPTABLE_VARIATION])
        self.assertFalse(res.critical_regression)

    def test_14_golden_comparator_detects_critical_regression(self):
        data = self._create_sample_asset_data()
        bench_base = self._create_approved_benchmark("B_BASE_CRIT")
        golden = self.api.create_golden("weapon.vandal", "Vandal", data, bench_base)
        self.api.activate_golden(golden.golden_id, bench_base)

        cand_bench_bad = self.eval_api.evaluate_asset(
            "weapon.vandal", "cand_crit",
            {"polygon_count": 25000, "materials": [], "invalid_scale_or_axis": True},
            benchmark_id="B_BAD"
        )
        res = self.api.compare_with_golden(cand_bench_bad, golden.golden_id)
        self.assertEqual(res.overall_status, RegressionLevel.CRITICAL_REGRESSION)
        self.assertTrue(res.critical_regression)

    # 7. Integrations (F75, F74, F70, F72)
    def test_15_evaluation_bridge_blocks_unapproved_benchmark(self):
        data = self._create_sample_asset_data()
        bench_unapproved = self.eval_api.evaluate_asset(
            "weapon.vandal", "cand_unapp", {"polygon_count": 30000, "materials": []}, benchmark_id="B_UNAPP"
        )
        asset = self.api.create_golden("weapon.vandal", "Vandal", data, bench_unapproved)
        with self.assertRaises(GoldenAssetException):
            self.api.activate_golden(asset.golden_id, bench_unapproved)

    def test_16_knowledge_graph_sync_bridge(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_KG")
        asset = self.api.create_golden("weapon.darx.vandal.001", "Vandal", data, bench)
        self.api.activate_golden(asset.golden_id, bench)

        node = self.api.kg_bridge.kg.get_node(f"GOLDEN_{asset.golden_id}")
        self.assertIsNotNone(node)

    def test_17_recovery_bridge_rollback_on_failed_transaction(self):
        self.api.recovery.begin_checkpoint()
        self.api.store._golden_assets["golden.temp.001"] = GoldenAsset("golden.temp.001", "w.temp", "Temp")
        self.api.recovery.rollback_to_checkpoint()
        self.assertIsNone(self.api.get_golden("golden.temp.001"))

    def test_18_authorization_guard_rejects_unregistered_agent(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_AUTH")
        with self.assertRaises(GoldenAuthorizationError):
            self.api.create_golden("weapon.vandal", "Vandal", data, bench, agent_id="agent.unregistered.hacker")

    # 8. Supersession & Lifecycle
    def test_19_supersede_golden_version_lifecycle(self):
        data = self._create_sample_asset_data()
        bench1 = self._create_approved_benchmark("B_LIFE1")
        golden_v1 = self.api.create_golden("weapon.vandal", "Vandal", data, bench1, version=1)
        self.api.activate_golden(golden_v1.golden_id, bench1)

        bench2 = self._create_approved_benchmark("B_LIFE2")
        golden_v2 = self.api.create_golden("weapon.vandal", "Vandal", data, bench2, version=2)
        golden_v2_act = self.api.supersede_golden(golden_v1.golden_id, golden_v2, bench2)

        self.assertEqual(golden_v1.status, GoldenAssetStatus.SUPERSEDED)
        self.assertEqual(golden_v2_act.status, GoldenAssetStatus.ACTIVE)
        self.assertEqual(golden_v2_act.parent_golden_id, golden_v1.golden_id)

    def test_20_revoke_golden_asset(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_REV")
        golden = self.api.create_golden("weapon.vandal", "Vandal", data, bench)
        self.api.activate_golden(golden.golden_id, bench)
        rev = self.api.revoke_golden(golden.golden_id, "Security vulnerability identified")
        self.assertEqual(rev.status, GoldenAssetStatus.REVOKED)
        self.assertEqual(rev.metadata["revoke_reason"], "Security vulnerability identified")

    def test_21_list_all_versions_for_semantic_id(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_LIST")
        g1 = self.api.create_golden("weapon.vandal.list", "Vandal", data, bench, version=1)
        self.api.activate_golden(g1.golden_id, bench)
        g2 = self.api.create_golden("weapon.vandal.list", "Vandal", data, bench, version=2)
        self.api.supersede_golden(g1.golden_id, g2, bench)

        versions = self.api.list_versions("weapon.vandal.list")
        self.assertEqual(len(versions), 2)

    def test_22_tampered_disk_file_detection(self):
        data = self._create_sample_asset_data()
        bench = self._create_approved_benchmark("B_TAMPER")
        golden = self.api.create_golden("weapon.vandal", "Vandal", data, bench)
        self.api.activate_golden(golden.golden_id, bench)

        with open(self.db_path, "r", encoding="utf-8") as f:
            raw = f.read()
        corrupted = raw.replace('"baseline_score": ' + str(round(golden.baseline_score, 4)), '"baseline_score": 0.0001')
        with open(self.db_path, "w", encoding="utf-8") as f:
            f.write(corrupted)

        with self.assertRaises(GoldenIntegrityError):
            api_corrupt = GoldenAPI(persistence_path=self.db_path)

    def test_23_compatibility_checker_mismatched_semantic_id(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        golden = GoldenAsset("golden.w.001.v1", "weapon.vandal", "Vandal", fingerprint=fps)
        cand_bench = self._create_approved_benchmark("B_COMPAT")
        cand_bench.asset_semantic_id = "weapon.other_gun"
        errs = CompatibilityChecker.check_compatibility(cand_bench, golden)
        self.assertEqual(len(errs), 1)

    def test_24_scene_fingerprinter_determinism(self):
        sc1 = {"collection_names": ["ColA", "ColB"], "pivot": [0, 0, 0]}
        sc2 = {"collection_names": ["ColB", "ColA"], "pivot": [0, 0, 0]}
        self.assertEqual(SceneFingerprinter.compute(sc1), SceneFingerprinter.compute(sc2))

    def test_25_reference_fingerprinter_determinism(self):
        ue = {"axis": "X_FORWARD_Z_UP", "unit_scale": 1.0, "lods": 3}
        self.assertEqual(ReferenceFingerprinter.compute(ue), ReferenceFingerprinter.compute(ue))

    def test_26_golden_asset_serialization_roundtrip(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset("golden.test.v1", "test.sem", "Test", fingerprint=fps, version=1)
        d = asset.to_dict()
        restored = GoldenAsset.from_dict(d)
        self.assertEqual(asset.golden_id, restored.golden_id)
        self.assertEqual(asset.manifest_hash, restored.manifest_hash)

    def test_27_regression_policy_acceptable_variation(self):
        pol = RegressionPolicy(variation_threshold=0.03)
        res = pol.evaluate_regression(0.93, 0.94, {})
        self.assertEqual(res, RegressionLevel.ACCEPTABLE_VARIATION)

    def test_28_regression_policy_critical_dimension_drop(self):
        pol = RegressionPolicy()
        res = pol.evaluate_regression(0.95, 0.94, {"GEOMETRY": -0.10}) # Geometry dropped
        self.assertEqual(res, RegressionLevel.CRITICAL_REGRESSION)

    def test_29_mutation_detector_multiple_changes(self):
        data = self._create_sample_asset_data()
        fps = AssetFingerprinter.compute_all(data)
        asset = GoldenAsset("golden.w.001.v1", "w.001", "W1", fingerprint=fps)

        data_mod = self._create_sample_asset_data()
        data_mod["geometry"]["polygon_count"] = 12000
        data_mod["materials"]["metallic"] = 0.10
        fps_mod = AssetFingerprinter.compute_all(data_mod)

        m_type, diffs = MutationDetector.detect_mutations(asset, fps_mod)
        self.assertEqual(m_type, MutationType.MULTIPLE_CHANGES)
        self.assertEqual(len(diffs), 2)

    def test_30_integrity_store_validates_fingerprint_keys(self):
        fps_incomplete = {"asset": "a", "geometry": "g"}
        with self.assertRaises(GoldenIntegrityError):
            IntegrityStore.validate_fingerprints(fps_incomplete)

    def test_31_golden_comparison_result_to_dict(self):
        res = GoldenComparisonResult(overall_status=RegressionLevel.IMPROVEMENT, overall_delta=0.05)
        d = res.to_dict()
        self.assertEqual(d["overall_status"], "IMPROVEMENT")
        self.assertEqual(d["overall_delta"], 0.05)

    def test_32_get_active_golden_returns_none_when_empty(self):
        self.assertIsNone(self.api.get_active_golden("non.existent.semantic.id"))

if __name__ == "__main__":
    unittest.main()
