import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetReuseEngineAPI, LibraryAssetRecord, AssetMetadata, AssetState,
    ReuseDecisionType, AssetSearchQuery, FingerprintMatcher
)

class TestAssetReuseEnginePhase23(unittest.TestCase):
    def setUp(self):
        self.api = AssetReuseEngineAPI()

        # Registrar casa medieval estándar (4m, estilizada, calidad 0.95)
        self.house_001 = LibraryAssetRecord(
            asset_id="house_001",
            name="Medieval House Standard",
            metadata=AssetMetadata(
                category="BUILDING",
                type_name="house",
                style="medieval_stylized",
                dimensions={"width": 4.0, "length": 4.0, "height": 5.0}
            ),
            quality_score=0.95,
            geometry_fingerprint=FingerprintMatcher.compute_geometry_fingerprint({"width": 4.0, "length": 4.0, "height": 5.0}, 1200)
        )
        self.api.register_asset(self.house_001)

    def test_01_exact_reuse_scenario_133(self):
        """Test 1: Scenario 133 - Casa medieval estilizada de 4m produce EXACT_REUSE."""
        q = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 4.0})
        decision = self.api.search_and_decide_reuse(q)
        self.assertEqual(decision.decision, ReuseDecisionType.EXACT_REUSE)
        self.assertEqual(decision.selected_asset_id, "house_001")

    def test_02_parametric_variant_scenario_134(self):
        """Test 2: Scenario 134 - Misma casa pero de 6m produce PARAMETRIC_VARIANT."""
        q = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 6.0})
        decision = self.api.search_and_decide_reuse(q, overrides={"width": 6.0})
        self.assertEqual(decision.decision, ReuseDecisionType.PARAMETRIC_VARIANT)
        self.assertEqual(decision.selected_asset_id, "house_001")
        self.assertIsNotNone(decision.variant_id)

    def test_03_style_mismatch_filtering_scenario_135(self):
        """Test 3: Scenario 135 - Búsqueda de estilo futurista descarta la casa medieval y produce GENERATE_NEW."""
        q = AssetSearchQuery("house", style="futuristic", target_dimensions={"width": 4.0})
        decision = self.api.search_and_decide_reuse(q)
        self.assertEqual(decision.decision, ReuseDecisionType.GENERATE_NEW)

    def test_04_duplicate_asset_detection_scenario_136(self):
        """Test 4: Scenario 136 - Detección de duplicados con fingerprint idéntico."""
        house_002 = LibraryAssetRecord(
            asset_id="house_002",
            name="Medieval House Clone",
            metadata=AssetMetadata(category="BUILDING", type_name="house", style="medieval_stylized", dimensions={"width": 4.0, "length": 4.0, "height": 5.0}),
            geometry_fingerprint=self.house_001.geometry_fingerprint
        )
        self.api.register_asset(house_002)
        dups = self.api.find_duplicate_geometries()
        self.assertEqual(len(dups), 1)
        self.assertEqual(dups[0], ("house_001", "house_002"))

    def test_05_instancing_system_scenario_137(self):
        """Test 5: Scenario 137 - 50 casas iguales genera 1 canónico + 49 instancias."""
        res = self.api.instantiate_batch("house_001", count=50)
        self.assertEqual(res["canonical_count"], 1)
        self.assertEqual(res["instances_count"], 49)
        self.assertEqual(len(res["instances"]), 49)

    def test_06_visual_reference_matching_scenario_138(self):
        """Test 6: Scenario 138 - visual_score = 0.96 produce EXACT_REUSE."""
        q = AssetSearchQuery("house", style="medieval_stylized", reference_visual_score=0.96)
        decision = self.api.search_and_decide_reuse(q)
        self.assertEqual(decision.decision, ReuseDecisionType.EXACT_REUSE)

    def test_07_generation_fallback_scenario_139(self):
        """Test 7: Scenario 139 - visual_score < threshold produce GENERATE_NEW."""
        q = AssetSearchQuery("spaceship", style="sci_fi")
        decision = self.api.search_and_decide_reuse(q)
        self.assertEqual(decision.decision, ReuseDecisionType.GENERATE_NEW)
        self.assertIn("NO_ACCEPTABLE_ASSET", decision.reasons[0])

    def test_08_quarantine_protection_scenario_140(self):
        """Test 8: Scenario 140 - Activo con >= 5 fallos entra en QUARANTINED y es excluido."""
        for _ in range(5):
            self.api.registry.record_failure("house_001")
        self.assertEqual(self.house_001.state, AssetState.QUARANTINED)

        q = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 4.0})
        decision = self.api.search_and_decide_reuse(q)
        self.assertEqual(decision.decision, ReuseDecisionType.GENERATE_NEW)

    def test_09_production_lock_protection_scenario_141(self):
        """Test 9: Scenario 141 - Activo PRODUCTION_LOCKED fuerza PARAMETRIC_VARIANT."""
        self.api.registry.lock_asset("house_001")
        self.assertEqual(self.house_001.state, AssetState.PRODUCTION_LOCKED)

        q = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 4.0})
        decision = self.api.search_and_decide_reuse(q, overrides={"roof_height": 1.2})
        self.assertEqual(decision.decision, ReuseDecisionType.PARAMETRIC_VARIANT)
        self.assertTrue(any("PRODUCTION_LOCKED" in r for r in decision.reasons))

    def test_10_anti_waste_creation_policy_scenario_142(self):
        """Test 10: Scenario 142 - Intentar crear sin retrieval produce POLICY_DENIED."""
        ok_policy, msg = self.api.validate_creation_policy(performed_retrieval=False)
        self.assertFalse(ok_policy)
        self.assertIn("POLICY_DENIED", msg)

        ok_valid, msg_v = self.api.validate_creation_policy(performed_retrieval=True)
        self.assertTrue(ok_valid)

    def test_11_duplicate_variant_prevention(self):
        """Test 11: Crear variante idéntica dos veces devuelve la misma instancia."""
        v1 = self.api.variant_mgr.create_or_get_variant("house_001", {"width": 6.0})
        v2 = self.api.variant_mgr.create_or_get_variant("house_001", {"width": 6.0})
        self.assertEqual(v1.variant_id, v2.variant_id)

    def test_12_search_scoring_breakdown(self):
        """Test 12: Búsqueda devuelve breakdown completo de puntuaciones."""
        q = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 4.0})
        candidates = self.api.search_candidates(q)
        self.assertGreaterEqual(len(candidates), 1)
        top = candidates[0]
        self.assertEqual(top.semantic_score, 1.0)
        self.assertEqual(top.style_score, 1.0)
        self.assertGreaterEqual(top.reuse_score, 0.90)

if __name__ == "__main__":
    unittest.main()
