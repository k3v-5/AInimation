import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.reference_analysis_visual_decomposition import (
    ReferenceAnalysisAPI, ImageReferenceInput, ReferenceModality,
    CameraPerspective, ExtractedMaterialType, StyleArchetype,
    VisualFeatureImportance
)

class TestReferenceAnalysisPhase55(unittest.TestCase):
    def setUp(self):
        self.api = ReferenceAnalysisAPI()

    def test_01_single_reference_barrel_decomposition(self):
        """Test 01: Ingesta y descomposición estructurada de una imagen de referencia de barril."""
        ref = ImageReferenceInput(
            reference_id="REF_BARREL_01",
            file_path_or_uri="textures/references/barrel_concept.png",
            modality=ReferenceModality.CONCEPT_ART,
            metadata={
                "aspect_ratio": 1.42,
                "curvature": 0.25,
                "base_material": "WOOD",
                "roughness": 0.70,
                "metallic": 0.30
            }
        )
        report = self.api.analyze_references([ref])
        self.assertEqual(report.asset_class_hint, "PROP.BARREL")
        self.assertEqual(report.silhouette.aspect_ratio, 1.42)
        self.assertEqual(report.materials.base_material, ExtractedMaterialType.WOOD)
        self.assertEqual(len(report.parts), 3)

    def test_02_multi_reference_fusion(self):
        """Test 02: Fusión de múltiples referencias con roles PRIMARY y SECONDARY."""
        ref1 = ImageReferenceInput("REF_1", "ref1.png", role="PRIMARY", metadata={"aspect_ratio": 1.40, "base_material": "WOOD"})
        ref2 = ImageReferenceInput("REF_2", "ref2.png", role="MATERIAL", metadata={"roughness": 0.65})
        report = self.api.analyze_references([ref1, ref2])
        self.assertEqual(len(report.reference_ids), 2)
        self.assertEqual(report.silhouette.aspect_ratio, 1.40)

    def test_03_silhouette_aspect_ratio_extraction(self):
        """Test 03: Extracción de silueta y aspect ratio."""
        ref = ImageReferenceInput("REF_SIL", "sil.png", metadata={"aspect_ratio": 1.55, "contour_complexity": 0.20})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.silhouette.aspect_ratio, 1.55)
        self.assertEqual(report.silhouette.contour_complexity, 0.20)

    def test_04_proportion_estimation_components(self):
        """Test 04: Estimación de proporciones relativas de componentes."""
        ref = ImageReferenceInput("REF_PROP", "prop.png", metadata={"component_ratios": {"body": 0.85, "rings": 0.15}})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.proportions.component_ratios["body"], 0.85)

    def test_05_part_decomposition_semantic_parts(self):
        """Test 05: Descomposición de partes semánticas (BODY, RING_01, RING_02)."""
        ref = ImageReferenceInput("REF_PARTS", "parts.png")
        report = self.api.analyze_references([ref])
        types = [p.semantic_type for p in report.parts]
        self.assertIn("BODY", types)
        self.assertIn("RING_01", types)
        self.assertIn("RING_02", types)

    def test_06_material_classification_pbr(self):
        """Test 06: Clasificación de materiales PBR (WOOD, IRON, rugosidad, metallic)."""
        ref = ImageReferenceInput("REF_MAT", "mat.png", metadata={"base_material": "WOOD", "roughness": 0.75, "metallic": 0.25})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.materials.base_material, ExtractedMaterialType.WOOD)
        self.assertEqual(report.materials.surface_roughness, 0.75)
        self.assertEqual(report.materials.metallic_ratio, 0.25)

    def test_07_color_palette_extraction(self):
        """Test 07: Extracción de paleta de colores dominantes y de acento."""
        ref = ImageReferenceInput("REF_COL", "col.png", metadata={"dominant_colors": ["#4A2E18"], "accent_colors": ["#222222"]})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.colors.dominant_colors[0], "#4A2E18")
        self.assertEqual(report.colors.accent_colors[0], "#222222")

    def test_08_camera_perspective_estimation(self):
        """Test 08: Estimación de ángulo y perspectiva de la cámara de referencia."""
        ref = ImageReferenceInput("REF_CAM", "cam.png", metadata={"camera_view": "FRONT", "elevation_deg": 0.0, "azimuth_deg": 0.0})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.camera.estimated_view, CameraPerspective.FRONT)
        self.assertEqual(report.camera.elevation_deg, 0.0)

    def test_09_style_conflict_warning(self):
        """Test 09: Detección de conflicto de estilos en referencias contradictorias."""
        ref1 = ImageReferenceInput("REF_1", "1.png", role="PRIMARY", metadata={"style": "STYLIZED"})
        ref2 = ImageReferenceInput("REF_2", "2.png", role="DETAIL", metadata={"style": "PHOTOREALISTIC"})
        report = self.api.analyze_references([ref1, ref2])
        self.assertTrue(any("STYLE_CONFLICT" in w for w in report.warnings))

    def test_10_empty_reference_list_raises_error(self):
        """Test 10: Lista vacía de referencias lanza ValueError."""
        with self.assertRaises(ValueError):
            self.api.analyze_references([])

    def test_11_visual_requirement_importance_weights(self):
        """Test 11: Ponderación de importancia en requisitos visuales extraídos."""
        ref = ImageReferenceInput("REF_REQ", "req.png")
        report = self.api.analyze_references([ref])
        req_sil = next(r for r in report.visual_requirements if r.category == "SILHOUETTE")
        self.assertEqual(req_sil.importance, VisualFeatureImportance.CRITICAL)

    def test_12_curvature_extraction(self):
        """Test 12: Extracción del abombamiento / curvatura del barril."""
        ref = ImageReferenceInput("REF_CURV", "curv.png", metadata={"curvature": 0.30})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.proportions.estimated_curvature, 0.30)

    def test_13_symmetry_axis_vertical_z(self):
        """Test 13: Identificación de simetría vertical en Z."""
        ref = ImageReferenceInput("REF_SYM", "sym.png", metadata={"symmetry": "VERTICAL_Z"})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.silhouette.symmetry_axis, "VERTICAL_Z")

    def test_14_non_barrel_custom_parts_decomposition(self):
        """Test 14: Descomposición de partes personalizadas para espada."""
        custom_parts = [
            {"part_id": "blade", "semantic_type": "BLADE", "is_primary": True, "confidence": 0.99},
            {"part_id": "guard", "semantic_type": "GUARD", "is_primary": False, "confidence": 0.95}
        ]
        ref = ImageReferenceInput("REF_SWORD", "sword.png", metadata={"detected_parts": custom_parts})
        report = self.api.analyze_references([ref], asset_class_hint="WEAPON.SWORD")
        self.assertEqual(len(report.parts), 2)
        self.assertEqual(report.parts[0].semantic_type, "BLADE")

    def test_15_brightness_saturation_profiles(self):
        """Test 15: Perfiles de brillo y saturación."""
        ref = ImageReferenceInput("REF_PAL", "pal.png", metadata={"brightness": "DARK", "saturation": "VIBRANT"})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.colors.brightness_profile, "DARK")
        self.assertEqual(report.colors.saturation_profile, "VIBRANT")

    def test_16_bounding_box_coordinates(self):
        """Test 16: Bounding box de la silueta normalizado."""
        ref = ImageReferenceInput("REF_BB", "bb.png", metadata={"aspect_ratio": 1.42})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.silhouette.bounding_box, (0.0, 0.0, 1.0, 1.42))

    def test_17_overall_confidence_calculation(self):
        """Test 17: Cálculo de confianza global >= 0.90."""
        ref = ImageReferenceInput("REF_CONF", "conf.png")
        report = self.api.analyze_references([ref])
        self.assertGreaterEqual(report.overall_confidence, 0.90)

    def test_18_stone_material_extraction(self):
        """Test 18: Extracción de material STONE."""
        ref = ImageReferenceInput("REF_STONE", "stone.png", metadata={"base_material": "STONE"})
        report = self.api.analyze_references([ref])
        self.assertEqual(report.materials.base_material, ExtractedMaterialType.STONE)

    def test_19_visual_requirements_count(self):
        """Test 19: Cantidad adecuada de requisitos visuales compilados."""
        ref = ImageReferenceInput("REF_CNT", "cnt.png")
        report = self.api.analyze_references([ref])
        self.assertGreaterEqual(len(report.visual_requirements), 5)

    def test_20_end_to_end_reference_decomposition_handshake(self):
        """Test 20: Flujo E2E: Ingesta -> Extracción -> Fusión -> DecomposedReferenceReport."""
        ref = ImageReferenceInput(
            "REF_E2E", "hero_barrel.png",
            metadata={"aspect_ratio": 1.42, "base_material": "WOOD", "camera_view": "ISOMETRIC_THREE_QUARTERS"}
        )
        report = self.api.analyze_references([ref], target_style=StyleArchetype.STYLIZED)
        self.assertTrue(report.report_id.startswith("REP_REF_"))
        self.assertEqual(report.style_archetype, StyleArchetype.STYLIZED)
        self.assertEqual(report.camera.estimated_view, CameraPerspective.ISOMETRIC_THREE_QUARTERS)

if __name__ == "__main__":
    unittest.main()
