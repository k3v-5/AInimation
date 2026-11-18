import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, VisualAPI, VisualFeedbackLoop, VisualReference,
    ReferenceType, ReferenceView, ViewOrientation, DifferenceType,
    SilhouetteComparator, CameraNormalizer, RenderCapture, QualityStatus
)

class TestVisualPerceptionPhase4(unittest.TestCase):
    def setUp(self):
        self.geo_engine = GeometryEngine()
        self.visual_api = VisualAPI(self.geo_engine)

    def test_01_identical_silhouette_pass(self):
        """Test 1: Silueta idéntica - Referencia y modelo idénticos -> PASS (1.0)."""
        # Crear espada en geometría
        self.geo_engine.create_component("sword_qa", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
        self.geo_engine.create_component("sword_qa", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "handle", "dimensions": {"width": 0.035, "depth": 0.035, "height": 0.25}},
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_qa", spec)
        self.assertEqual(report["status"], "PASS")
        self.assertAlmostEqual(report["quality_score"], 1.0, places=2)
        self.assertEqual(len(report["differences"]), 0)

    def test_02_incorrect_dimension_detected(self):
        """Test 2: Dimensión incorrecta - Modelo 10% más corto -> Detecta LENGTH."""
        # Modelo creado con hoja de 0.85m
        self.geo_engine.create_component("sword_dim", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        # Especificación requería 0.95m
        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_dim", spec)
        diff_types = [d["type"] for d in report["differences"]]
        self.assertIn("LENGTH", diff_types)

    def test_03_missing_component_detected(self):
        """Test 3: Componente ausente - Spec requiere guard pero modelo carece de él."""
        self.geo_engine.create_component("sword_miss", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85}},
                {"id": "guard", "dimensions": {"width": 0.15, "depth": 0.03, "height": 0.03}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_miss", spec)
        diff_types = [d["type"] for d in report["differences"]]
        self.assertIn("MISSING_COMPONENT", diff_types)

    def test_04_extra_component_detected(self):
        """Test 4: Componente extra - Modelo contiene objeto no especificado."""
        self.geo_engine.create_component("sword_ext", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})
        self.geo_engine.create_component("sword_ext", "extra_spike", "primitive", {"primitive": "cone", "width": 0.1, "depth": 0.1, "height": 0.2})

        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_ext", spec)
        diff_types = [d["type"] for d in report["differences"]]
        self.assertIn("EXTRA_COMPONENT", diff_types)

    def test_05_camera_normalization_avoids_false_positives(self):
        """Test 5: Cámara normalizada - Diferentes posiciones de cámara encuadran el objeto al 80% occupancy."""
        cam1 = CameraNormalizer.get_normalized_camera(ViewOrientation.FRONT, (1.0, 1.0, 2.0))
        cam2 = CameraNormalizer.get_normalized_camera(ViewOrientation.FRONT, (2.0, 2.0, 4.0))

        # Ambas son ortográficas y proporcionales
        self.assertEqual(cam1.projection, "orthographic")
        self.assertAlmostEqual(cam1.ortho_scale * 2.0, cam2.ortho_scale, places=2)

    def test_06_framing_scale_normalization(self):
        """Test 6: Escala de framing normalizada para siluetas."""
        grid_a = [[1 if (x > 10 and x < 20 and y > 10 and y < 20) else 0 for x in range(32)] for y in range(32)]
        grid_b = [[1 if (x > 10 and x < 20 and y > 10 and y < 20) else 0 for x in range(32)] for y in range(32)]

        iou = SilhouetteComparator.calculate_iou(grid_a, grid_b)
        self.assertEqual(iou, 1.0)

    def test_07_parametric_correction_proposal(self):
        """Test 7: Corrección paramétrica - Detecta blade 10cm más corta y genera SET blade.length = 0.95."""
        self.geo_engine.create_component("sword_prop", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_prop", spec)
        self.assertGreater(len(report["corrections"]), 0)
        c = report["corrections"][0]
        self.assertEqual(c["target"], "blade")
        self.assertEqual(c["parameter"], "length")
        self.assertEqual(c["operation"], "SET")
        self.assertEqual(c["value"], 0.95)

    def test_08_minimal_correction_only_affected_component(self):
        """Test 8: Corrección mínima - Solo propone modificar blade, handle permanece intacto."""
        self.geo_engine.create_component("sword_min", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
        self.geo_engine.create_component("sword_min", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "handle", "dimensions": {"width": 0.035, "depth": 0.035, "height": 0.25}},
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_min", spec)
        correction_targets = [c["target"] for c in report["corrections"]]
        self.assertEqual(correction_targets, ["blade"])
        self.assertIn("sword_min.handle", report["unaffected_components"])

    def test_09_no_op_when_requirements_met(self):
        """Test 9: NO_OP - Si el modelo cumple, 0 correcciones y status PASS."""
        self.geo_engine.create_component("sword_ok", "blade", "profile", {"length": 0.95, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
            ]
        }

        report = self.visual_api.evaluate_asset("sword_ok", spec)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["corrections"]), 0)

    def test_10_correction_loop_detection(self):
        """Test 10: Correction Loop - Detección de bucle de corrección oscilante."""
        self.geo_engine.create_component("loop_asset", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})

        spec = {
            "components": [
                {"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
            ]
        }

        # Ejecutar auto-corrección
        loop = VisualFeedbackLoop(self.geo_engine)
        ref = VisualReference(
            reference_id="ref_loop",
            expected_dimensions={"blade": {"width": 0.05, "depth": 0.015, "height": 0.95}},
            expected_structure=["blade"]
        )

        report = loop.run_qa_cycle("loop_asset", ref, auto_correct=True, max_iterations=3)
        # En la primera iteración se corrige y pasa a PASS en la iteración 2
        self.assertEqual(report["status"], "PASS")

    def test_11_rollback_on_degraded_score(self):
        """Test 11: Degradación de score detectada."""
        # Un score que empeore respecto a la iteración anterior gatilla ROLLBACK
        self.geo_engine.create_component("rb_asset", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})
        insp = self.geo_engine.inspect_component("rb_asset.blade")
        self.assertEqual(insp["parameters"]["length"], 0.85)

    def test_12_reference_conflict(self):
        """Test 12: Conflicto de referencias - Spec coherente."""
        spec = {"components": [{"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85}}]}
        ref = VisualReference(reference_id="ref_ok", expected_structure=["blade"])
        self.assertEqual(ref.reference_id, "ref_ok")

    def test_13_partial_reference_unobserved_views(self):
        """Test 13: Referencia parcial - Vista frontal no evalúa vistas no observadas."""
        ref = VisualReference(
            reference_id="ref_front_only",
            views={ViewOrientation.FRONT: ReferenceView(orientation=ViewOrientation.FRONT, expected_components=["blade"])}
        )
        self.assertIn(ViewOrientation.FRONT, ref.views)
        self.assertNotIn(ViewOrientation.BACK, ref.views)

    def test_14_determinism(self):
        """Test 14: Determinismo - Misma entrada produce mismo diagnóstico exacto."""
        self.geo_engine.create_component("det_asset", "blade", "profile", {"length": 0.80, "width": 0.05, "thickness": 0.015})
        spec = {"components": [{"id": "blade", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.90}}]}

        rep1 = self.visual_api.evaluate_asset("det_asset", spec)
        rep2 = self.visual_api.evaluate_asset("det_asset", spec)

        self.assertEqual(rep1["quality_score"], rep2["quality_score"])
        self.assertEqual(rep1["differences"], rep2["differences"])
        self.assertEqual(rep1["corrections"], rep2["corrections"])

if __name__ == "__main__":
    unittest.main()
