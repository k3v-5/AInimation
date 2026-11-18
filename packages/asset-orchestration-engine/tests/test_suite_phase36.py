import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_reference_similarity import (
    VisualSimilarityAPI, ReferencePriority, EvaluationStatus, DifferenceType,
    CandidateAsset
)

class TestVisualReferenceSimilarityPhase36(unittest.TestCase):
    def setUp(self):
        self.api = VisualSimilarityAPI()
        self.ref_house = self.api.create_reference_profile(
            ref_id="REF_2026_000182",
            expected_features={
                "roof_type": "GABLE",
                "windows": 4,
                "chimney": True,
                "balcony": False,
                "materials": {"walls": "STONE", "roof": "WOOD"}
            },
            proportions={"roof_to_body": 0.30}
        )

    def test_01_acceptance_1_silhouette_matching(self):
        """Acceptance Test 1: Casa con tejado a dos aguas coincide con la silueta de referencia."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={
                "roof_type": "GABLE",
                "windows": 4,
                "chimney": True,
                "balcony": False,
                "materials": {"walls": "STONE", "roof": "WOOD"}
            },
            detected_proportions={"roof_to_body": 0.30}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertGreaterEqual(report.category_scores["silhouette"], 0.95)
        self.assertEqual(report.evaluation_status, EvaluationStatus.PASS)

    def test_02_acceptance_2_wrong_roof_critical_failure(self):
        """Acceptance Test 2: Techo plano en vez de GABLE genera fallo crítico y estado FAIL."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "FLAT", "windows": 4, "chimney": True, "materials": {"walls": "STONE"}},
            detected_proportions={"roof_to_body": 0.30}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertEqual(report.evaluation_status, EvaluationStatus.FAIL)
        self.assertTrue(any("roof_shape" in f for f in report.critical_failures))

    def test_03_acceptance_3_wrong_window_count(self):
        """Acceptance Test 3: 7 ventanas en lugar de 4 genera diferencia WRONG_COUNT."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "GABLE", "windows": 7, "chimney": True, "materials": {"walls": "STONE"}}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        w_diffs = [d for d in report.differences if d.diff_type == DifferenceType.WRONG_COUNT]
        self.assertEqual(len(w_diffs), 1)
        self.assertEqual(w_diffs[0].expected, 4)
        self.assertEqual(w_diffs[0].actual, 7)

    def test_04_acceptance_4_missing_chimney_component(self):
        """Acceptance Test 4: Ausencia de chimenea genera MISSING."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "GABLE", "windows": 4, "chimney": False, "materials": {"walls": "STONE"}}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertTrue(any(d.diff_type == DifferenceType.MISSING for d in report.differences))

    def test_05_acceptance_5_extra_balcony_component(self):
        """Acceptance Test 5: Presencia de balcón no solicitado genera EXTRA."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "GABLE", "windows": 4, "chimney": True, "balcony": True, "materials": {"walls": "STONE"}}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertTrue(any(d.diff_type == DifferenceType.EXTRA for d in report.differences))

    def test_06_acceptance_6_proportion_discrepancy(self):
        """Acceptance Test 6: Discrepancia grande de proporción genera penalización en proportions."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "GABLE", "windows": 4, "chimney": True, "materials": {"walls": "STONE"}},
            detected_proportions={"roof_to_body": 0.50}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertLess(report.category_scores["proportions"], 0.70)

    def test_07_acceptance_7_material_mismatch(self):
        """Acceptance Test 7: Muros de METAL cuando se esperaba STONE genera WRONG_MATERIAL."""
        obs = self.api.observe_asset(
            asset_id="HOUSE_001",
            detected_features={"roof_type": "GABLE", "windows": 4, "chimney": True, "materials": {"walls": "METAL", "roof": "WOOD"}}
        )
        report = self.api.evaluate_asset(self.ref_house, obs, use_cache=False)
        self.assertTrue(any(d.diff_type == DifferenceType.WRONG_MATERIAL for d in report.differences))

    def test_08_acceptance_8_correction_score_improvement(self):
        """Acceptance Test 8: Corregir proporción de tejado incrementa la puntuación global."""
        obs_bad = self.api.observe_asset("HOUSE_001", {"roof_type": "GABLE", "windows": 4, "chimney": True}, {"roof_to_body": 0.50})
        obs_good = self.api.observe_asset("HOUSE_001", {"roof_type": "GABLE", "windows": 4, "chimney": True}, {"roof_to_body": 0.30})
        rep_bad = self.api.evaluate_asset(self.ref_house, obs_bad, use_cache=False)
        rep_good = self.api.evaluate_asset(self.ref_house, obs_good, use_cache=False)
        self.assertGreater(rep_good.overall_score, rep_bad.overall_score)

    def test_09_acceptance_9_regression_detection(self):
        """Acceptance Test 9: Si una corrección degrada la silueta, detect_regression devuelve True."""
        obs_1 = self.api.observe_asset("HOUSE_001", {"roof_type": "GABLE", "windows": 4, "chimney": True}, aspect_ratio=1.3)
        obs_2 = self.api.observe_asset("HOUSE_001", {"roof_type": "GABLE", "windows": 4, "chimney": True}, aspect_ratio=1.8)
        rep_1 = self.api.evaluate_asset(self.ref_house, obs_1, use_cache=False)
        rep_2 = self.api.evaluate_asset(self.ref_house, obs_2, use_cache=False)
        self.assertTrue(self.api.detect_regression(rep_1, rep_2))

    def test_10_acceptance_10_oscillation_and_stagnation(self):
        """Acceptance Test 10: Detección de oscilación y estancamiento en ciclo de autocorrección."""
        history_oscillating = [0.70, 0.40, 0.70, 0.40]
        self.assertTrue(self.api.detect_oscillation(history_oscillating))

        history_stalled = [0.75, 0.75, 0.74]
        self.assertTrue(self.api.detect_stagnation(history_stalled, patience=3))

    def test_11_acceptance_11_reference_conflict_detection(self):
        """Acceptance Test 11: Dos referencias de alta prioridad en conflicto producen REFERENCE_CONFLICT."""
        ref_b = self.api.create_reference_profile(
            ref_id="REF_2026_000183",
            expected_features={"roof_type": "FLAT", "windows": 4},
            priority=ReferencePriority.HIGH
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.detect_conflicts(self.ref_house, ref_b)
        self.assertIn("REFERENCE_CONFLICT", str(ctx.exception))

    def test_12_acceptance_12_candidate_ranking_critical_failure_gate(self):
        """Acceptance Test 12: Candidato con score 0.89 y 0 fallos críticos gana a candidato con score 0.92 y 1 fallo crítico."""
        c1 = CandidateAsset(candidate_id="CAND_01", score=0.92, critical_failures_count=1)
        c2 = CandidateAsset(candidate_id="CAND_02", score=0.89, critical_failures_count=0)
        ranked = self.api.rank_candidates([c1, c2])
        self.assertEqual(ranked[0].candidate_id, "CAND_02")

if __name__ == "__main__":
    unittest.main()
