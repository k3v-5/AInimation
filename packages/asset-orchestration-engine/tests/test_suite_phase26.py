import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AutonomousCorrectionLoopAPI, VisualReferenceAPI, ParametricAssetType,
    LoopStatus
)

class TestAutonomousCorrectionLoopPhase26(unittest.TestCase):
    def setUp(self):
        self.loop_api = AutonomousCorrectionLoopAPI()
        self.ref_api = VisualReferenceAPI()

        self.reference = self.ref_api.create_reference_profile(
            reference_id="ref_house_ideal",
            source_uri="ref://house_ideal.png",
            proportions={"roof_to_wall_ratio": 0.55, "window_scale": 1.25},
            detected_components=["foundation", "walls", "roof", "windows"]
        )

    def test_01_autonomous_correction_loop_convergence_to_accepted(self):
        """Test 1: Bucle de corrección converge a ACCEPTED en <= 2 iteraciones."""
        initial_params = {
            "width": 4.0,
            "depth": 3.5,
            "height": 5.0,
            "roof_height": 1.50, # Tejado bajo
            "window_scale": 1.0   # Ventanas pequeñas
        }
        res = self.loop_api.run_correction_loop(
            target_asset_id="house_auto_01",
            asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
            initial_parameters=initial_params,
            reference=self.reference
        )
        self.assertEqual(res.status, LoopStatus.ACCEPTED)
        self.assertLessEqual(res.iterations_run, 2)
        self.assertGreaterEqual(res.final_score, 0.90)

    def test_02_targeted_subtree_rebuild_scope(self):
        """Test 2: Modifica sólo los componentes afectados ('roof' y 'windows')."""
        initial_params = {
            "width": 4.0,
            "depth": 3.5,
            "height": 5.0,
            "roof_height": 1.50,
            "window_scale": 1.0
        }
        res = self.loop_api.run_correction_loop(
            target_asset_id="house_auto_02",
            asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
            initial_parameters=initial_params,
            reference=self.reference
        )
        self.assertGreaterEqual(len(res.history), 1)
        first_step = res.history[0]
        self.assertIn("roof", first_step.affected_components)
        self.assertIn("windows", first_step.affected_components)
        self.assertNotIn("foundation", first_step.affected_components)

    def test_03_max_iteration_limit_and_needs_review_status(self):
        """Test 3: Detiene a las 5 iteraciones con estado NEEDS_REVIEW ante error no resoluble."""
        initial_params = {"width": 4.0, "depth": 3.5, "height": 5.0}
        res = self.loop_api.run_correction_loop(
            target_asset_id="house_unresolvable",
            asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
            initial_parameters=initial_params,
            reference=self.reference,
            force_unresolvable=True
        )
        self.assertEqual(res.status, LoopStatus.NEEDS_REVIEW)
        self.assertEqual(res.iterations_run, 5)
        self.assertTrue(len(res.unresolved_problems) > 0)

    def test_04_initial_acceptable_asset_zero_iterations(self):
        """Test 4: Activo inicial que cumple el umbral se acepta en 0 iteraciones."""
        perfect_ref = self.ref_api.create_reference_profile(
            reference_id="ref_match",
            source_uri="ref://match.png",
            proportions={"roof_to_wall_ratio": 0.538, "window_scale": 1.0},
            detected_components=["foundation", "walls", "roof", "windows"]
        )
        initial_params = {"width": 4.0, "depth": 3.5, "height": 5.0, "roof_height": 1.75, "window_scale": 1.0}
        res = self.loop_api.run_correction_loop(
            target_asset_id="house_perfect_01",
            asset_type=ParametricAssetType.MEDIEVAL_HOUSE,
            initial_parameters=initial_params,
            reference=perfect_ref
        )
        self.assertEqual(res.status, LoopStatus.ACCEPTED)
        self.assertEqual(res.iterations_run, 0)

if __name__ == "__main__":
    unittest.main()
