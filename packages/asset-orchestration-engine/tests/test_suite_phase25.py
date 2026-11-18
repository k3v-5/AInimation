import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import VisualReferenceAPI

class TestVisualReferenceMatchingPhase25(unittest.TestCase):
    def setUp(self):
        self.api = VisualReferenceAPI()
        self.ref = self.api.create_reference_profile(
            reference_id="ref_medieval_house_01",
            source_uri="ref://medieval_house_01.png",
            proportions={"roof_to_wall_ratio": 0.55, "window_scale": 1.25},
            detected_components=["foundation", "walls", "roof", "windows"]
        )

    def test_01_feature_extraction_and_discrepancy_detection(self):
        """Test 1: Detecta techo bajo y ventanas pequeñas respecto a la referencia."""
        model_data = {
            "dimensions": {"width": 4.0, "depth": 3.5, "height": 5.0},
            "components": ["foundation", "walls", "roof", "windows"],
            "parameters": {"roof_height": 1.40, "window_scale": 1.0}
        }
        error_map = self.api.compare_model("house_001", model_data, self.ref)
        self.assertFalse(error_map.is_match)
        self.assertEqual(len(error_map.discrepancies), 2)
        disc_comps = [d.component for d in error_map.discrepancies]
        self.assertIn("roof", disc_comps)
        self.assertIn("windows", disc_comps)

    def test_02_recommended_patches_generation(self):
        """Test 2: Genera parches recomendados para roof_height y window_scale."""
        model_data = {
            "dimensions": {"width": 4.0, "depth": 3.5, "height": 5.0},
            "components": ["foundation", "walls", "roof", "windows"],
            "parameters": {"roof_height": 1.40, "window_scale": 1.0}
        }
        error_map = self.api.compare_model("house_001", model_data, self.ref)
        self.assertIn("roof_height", error_map.recommended_patches)
        self.assertIn("window_scale", error_map.recommended_patches)
        self.assertEqual(error_map.recommended_patches["window_scale"], 1.25)

    def test_03_perfect_match(self):
        """Test 3: Modelo que cumple proporciones da is_match = True."""
        perfect_ref = self.api.create_reference_profile(
            reference_id="ref_perfect",
            source_uri="ref://perfect.png",
            proportions={"roof_to_wall_ratio": 0.538, "window_scale": 1.0},
            detected_components=["foundation", "walls", "roof", "windows"]
        )
        model_data = {
            "dimensions": {"width": 4.0, "depth": 3.5, "height": 5.0},
            "components": ["foundation", "walls", "roof", "windows"],
            "parameters": {"roof_height": 1.75, "window_scale": 1.0}
        }
        error_map = self.api.compare_model("house_perfect", model_data, perfect_ref)
        self.assertTrue(error_map.is_match)
        self.assertGreaterEqual(error_map.overall_geometric_score, 0.90)

    def test_04_missing_component_detection(self):
        """Test 4: Detecta componente faltante (windows)."""
        model_data = {
            "dimensions": {"width": 4.0, "depth": 3.5, "height": 5.0},
            "components": ["foundation", "walls", "roof"], # falta windows
            "parameters": {"roof_height": 1.75}
        }
        error_map = self.api.compare_model("house_no_win", model_data, self.ref)
        self.assertIn("windows", error_map.missing_components)
        self.assertFalse(error_map.is_match)

if __name__ == "__main__":
    unittest.main()
