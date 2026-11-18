import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    LearnedPatternsAPI, PatternState, ProblemSignature
)

class TestLearnedConstructionPatternsPhase27(unittest.TestCase):
    def setUp(self):
        self.api = LearnedPatternsAPI()

        # Registrar patrón inicial
        self.pat_roof = self.api.register_pattern(
            pattern_id="pat_medieval_roof_01",
            name="MedievalRoofCorrection_01",
            asset_family="medieval_house",
            problem_signature=ProblemSignature.ROOF_TOO_LOW.value,
            target_parameter="roof_height",
            correction_delta=0.18,
            confidence=0.92,
            builder_version="v1.0.0"
        )

    def test_01_pattern_retrieval_scenario_129(self):
        """Test 1: Scenario 129 - Busca y encuentra el patrón anterior para MEDIEVAL_HOUSE_B."""
        query = {
            "asset_family": "medieval_house",
            "problem_signature": ProblemSignature.ROOF_TOO_LOW.value,
            "builder_version": "v1.0.0"
        }
        results = self.api.search_patterns(query)
        self.assertGreaterEqual(len(results), 1)
        top_pat, sim, explanation = results[0]
        self.assertEqual(top_pat.pattern_id, "pat_medieval_roof_01")
        self.assertGreaterEqual(sim, 0.85)
        self.assertIn("matches", explanation)

    def test_02_statistics_update_and_promotion_scenario_130(self):
        """Test 2: Scenario 130 - 5 éxitos consecutivos promueven el patrón a KNOWN_GOOD."""
        for _ in range(5):
            self.api.record_outcome("pat_medieval_roof_01", success=True, improvement=0.14)

        pat = self.api.store.get_pattern("pat_medieval_roof_01")
        self.assertEqual(pat.state, PatternState.KNOWN_GOOD)
        self.assertEqual(pat.success_count, 6) # 1 inicial + 5
        self.assertGreaterEqual(pat.confidence, 0.95)

    def test_03_repeated_failure_decay_and_invalidation_scenario_131(self):
        """Test 3: Scenario 131 - 3 fallos consecutivos invalidan el patrón."""
        for _ in range(3):
            self.api.record_outcome("pat_medieval_roof_01", success=False)

        pat = self.api.store.get_pattern("pat_medieval_roof_01")
        self.assertEqual(pat.state, PatternState.INVALIDATED)

        # Futura búsqueda descarta el patrón invalidado
        results = self.api.search_patterns({"asset_family": "medieval_house", "problem_signature": "ROOF_TOO_LOW"})
        self.assertEqual(len(results), 0)

    def test_04_conflict_detection_scenario_132(self):
        """Test 4: Scenario 132 - Detecta conflicto entre patrones contradictorios."""
        self.api.register_pattern(
            pattern_id="pat_roof_opposing",
            name="MedievalRoofShrink_01",
            asset_family="medieval_house",
            problem_signature="ROOF_TOO_HIGH",
            target_parameter="roof_height",
            correction_delta=-0.15
        )
        has_conflict, reason = self.api.check_conflict("pat_medieval_roof_01", "pat_roof_opposing")
        self.assertTrue(has_conflict)
        self.assertIn("CONFLICT_DETECTED", reason)

    def test_05_builder_version_incompatibility_scenario_133(self):
        """Test 5: Scenario 133 - Incompatibilidad de versión de builder excluye el patrón."""
        query_v2 = {
            "asset_family": "medieval_house",
            "problem_signature": ProblemSignature.ROOF_TOO_LOW.value,
            "builder_version": "v2.0.0" # Incompatible con v1.0.0
        }
        results = self.api.search_patterns(query_v2)
        self.assertEqual(len(results), 0)

    def test_06_deterministic_ranking_scenario_134(self):
        """Test 6: Scenario 134 - Misma consulta produce idéntico ranking de patrones."""
        query = {"asset_family": "medieval_house", "problem_signature": "ROOF_TOO_LOW"}
        res1 = self.api.search_patterns(query)
        res2 = self.api.search_patterns(query)
        self.assertEqual(len(res1), len(res2))
        self.assertEqual(res1[0][0].pattern_id, res2[0][0].pattern_id)
        self.assertEqual(res1[0][1], res2[0][1])

    def test_07_pattern_deletion_scenario_135(self):
        """Test 7: Scenario 135 - Patrón eliminado no aparece en búsquedas pero persiste auditoría."""
        self.api.delete_pattern("pat_medieval_roof_01")
        results = self.api.search_patterns({"asset_family": "medieval_house"})
        self.assertEqual(len(results), 0)
        self.assertTrue(any(a["action"] == "DELETE_PATTERN" for a in self.api.store.audit_log))

    def test_08_low_confidence_auto_apply_prevention_scenario_136(self):
        """Test 8: Scenario 136 - Confianza baja (0.55) no se aplica automáticamente."""
        low_conf_pat = self.api.register_pattern(
            pattern_id="pat_low_conf",
            name="ExperimentalPattern",
            asset_family="medieval_house",
            problem_signature="WINDOWS_TOO_SMALL",
            target_parameter="window_scale",
            correction_delta=0.25,
            confidence=0.55
        )
        ok_apply, params, msg = self.api.apply_pattern(low_conf_pat, {"window_scale": 1.0}, auto_apply_threshold=0.90)
        self.assertFalse(ok_apply)
        self.assertIn("CONFIDENCE_TOO_LOW", msg)

    def test_09_high_confidence_auto_apply_scenario_137(self):
        """Test 9: Scenario 137 - Patrón de alta confianza (0.92) se aplica automáticamente."""
        ok_apply, params, msg = self.api.apply_pattern(self.pat_roof, {"roof_height": 1.75}, auto_apply_threshold=0.90)
        self.assertTrue(ok_apply)
        self.assertEqual(params["roof_height"], 2.065) # 1.75 * 1.18

    def test_10_variant_knowledge_reuse_scenario_138(self):
        """Test 10: Scenario 138 - Variante nueva de medieval_house reutiliza conocimiento compatible."""
        query_variant = {
            "asset_family": "medieval_house",
            "problem_signature": ProblemSignature.ROOF_TOO_LOW.value,
            "builder_version": "v1.0.0"
        }
        results = self.api.search_patterns(query_variant)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0][0].target_parameter, "roof_height")

if __name__ == "__main__":
    unittest.main()
