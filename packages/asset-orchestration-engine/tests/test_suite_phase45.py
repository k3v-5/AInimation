import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.reference_understanding_visual_spec import (
    VisualSpecificationAPI, ReferenceRole, ReferenceType,
    DetailTreatmentType, UncertaintyType, TargetProfileType,
    VisualTargetProfile
)
from src.parametric_asset_engine import ParametricAssetAPI

class TestReferenceUnderstandingPhase45(unittest.TestCase):
    def setUp(self):
        self.api = VisualSpecificationAPI()
        self.param_api = ParametricAssetAPI()
        self.ref_primary = self.api.create_reference_item(
            "REF_HOUSE_FRONT",
            "assets/references/medieval_house_front.png",
            role=ReferenceRole.PRIMARY,
            metadata={"aspect_ratio": 1.52}
        )

    def test_01_multi_reference_creation_roles(self):
        """Test 1: Creación de ítems de referencia con roles diferenciados."""
        ref_mat = self.api.create_reference_item("REF_STONE_MAT", "assets/stone.png", role=ReferenceRole.MATERIAL)
        self.assertEqual(ref_mat.role, ReferenceRole.MATERIAL)
        self.assertEqual(self.ref_primary.role, ReferenceRole.PRIMARY)

    def test_02_reference_conflict_detection(self):
        """Test 2: Detección de conflicto entre referencias primarias contradictorias."""
        ref_contradict = self.api.create_reference_item(
            "REF_HOUSE_CONTRADICT",
            "assets/ref2.png",
            role=ReferenceRole.PRIMARY,
            metadata={"aspect_ratio": 0.80} # 1.52 vs 0.80 -> Delta > 0.30
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.analyze_references_to_visual_spec([self.ref_primary, ref_contradict])
        self.assertIn("REFERENCE_CONFLICT", str(ctx.exception))

    def test_03_aspect_ratio_extraction(self):
        """Test 3: Extracción de relación de aspecto de la silueta."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertEqual(vspec.aspect_ratio, 1.52)

    def test_04_roof_proportion_constraint(self):
        """Test 4: Extracción de proporción de tejado (0.31)."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertEqual(vspec.roof_ratio, 0.31)

    def test_05_landmark_detection(self):
        """Test 5: Detección de puntos de referencia geométricos (Landmarks)."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        apex = next((lm for lm in vspec.landmarks if lm.landmark_id == "LM_ROOF_APEX"), None)
        self.assertIsNotNone(apex)
        self.assertEqual(apex.normalized_pos, (0.50, 1.00))

    def test_06_component_detection_boxes_and_counts(self):
        """Test 6: Detección de componentes con conteo y bounding box normalizado."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertIn("walls", vspec.detected_components)
        self.assertIn("roof", vspec.detected_components)
        self.assertEqual(vspec.detected_components["windows"].count, 4)

    def test_07_bilateral_symmetry(self):
        """Test 7: Detección de simetría bilateral en fachada."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        door = vspec.detected_components["door"]
        self.assertEqual(door.normalized_pos[0], 0.5) # Centrado

    def test_08_spatial_relationship_graph(self):
        """Test 8: Construcción del grafo de relaciones espaciales."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        roof_rels = vspec.detected_components["roof"].spatial_relations
        self.assertTrue(any(r["relation"] == "ABOVE" and r["target"] == "walls" for r in roof_rels))

    def test_09_material_assignment_extraction(self):
        """Test 9: Extracción de materiales PBR dominantes."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertEqual(vspec.materials["walls"], "STONE_ROUGH")
        self.assertEqual(vspec.materials["roof"], "TIMBER_SHINGLES")

    def test_10_detail_treatment_classification(self):
        """Test 10: Clasificación de detalles entre Geometría y Normal/Textura."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertEqual(vspec.detail_treatments["silhouette_contour"], DetailTreatmentType.GEOMETRY)
        self.assertEqual(vspec.detail_treatments["wood_grain_scratches"], DetailTreatmentType.NORMAL)

    def test_11_scale_unknown_uncertainty(self):
        """Test 11: Detección de incertidumbre SCALE_UNKNOWN si el prompt no define escala."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary], user_prompt="haz una casa")
        self.assertTrue(any(u.uncertainty_type == UncertaintyType.SCALE_UNKNOWN for u in vspec.uncertainties))

    def test_12_backside_unknown_uncertainty(self):
        """Test 12: Detección de incertidumbre BACKSIDE_UNKNOWN en referencia de vista única."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        self.assertTrue(any(u.uncertainty_type == UncertaintyType.BACKSIDE_UNKNOWN for u in vspec.uncertainties))

    def test_13_clarification_question_formulation(self):
        """Test 13: Formulación de pregunta de clarificación para incertidumbres críticas."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        scale_unc = next(u for u in vspec.uncertainties if u.uncertainty_type == UncertaintyType.SCALE_UNKNOWN)
        self.assertIsNotNone(scale_unc.suggested_question)
        self.assertIn("escala", scale_unc.suggested_question.lower())

    def test_14_structural_specification_compilation(self):
        """Test 14: Compilación de VisualSpecification en StructuralSpecification."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        sspec = self.api.compile_structural_specification(vspec)
        self.assertEqual(sspec.archetype_id, "MEDIEVAL_HOUSE")
        self.assertEqual(sspec.target_parameters["roof_pitch"], 35.0)
        self.assertEqual(sspec.target_parameters["window_count"], 4)

    def test_15_user_explicit_override_priority(self):
        """Test 15: Prioridad USER_EXPLICIT sobrescribe valores observados de referencia."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        # Usuario especifica explícitamente 6 ventanas en lugar de las 4 observadas
        sspec = self.api.compile_structural_specification(vspec, user_overrides={"window_count": 6, "width": 10.0})
        self.assertEqual(sspec.target_parameters["window_count"], 6)
        self.assertEqual(sspec.target_parameters["width"], 10.0)

    def test_16_gameplay_constraints_inclusion(self):
        """Test 16: Inclusión de restricciones de gameplay (ancho mínimo de puerta y colisiones)."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        sspec = self.api.compile_structural_specification(vspec)
        self.assertEqual(sspec.gameplay_constraints["min_door_width"], 1.0)
        self.assertTrue(sspec.gameplay_constraints["collision_required"])

    def test_17_feature_parameter_attribution(self):
        """Test 17: Atribución de características visuales a parámetros del motor."""
        attr = self.api.get_parameter_attribution("roof_silhouette")
        self.assertIn("roof_height", attr.candidate_parameters)
        self.assertIn("roof_pitch", attr.candidate_parameters)

    def test_18_parameter_sensitivity_rating(self):
        """Test 18: Calificación de sensibilidad del parámetro (HIGH para roof_silhouette)."""
        attr = self.api.get_parameter_attribution("roof_silhouette")
        self.assertEqual(attr.sensitivity_rating, "HIGH")

    def test_19_visual_target_profile_gameplay(self):
        """Test 19: Inicialización de perfil de objetivo visual GAMEPLAY."""
        profile = VisualTargetProfile(profile_type=TargetProfileType.GAMEPLAY)
        self.assertEqual(profile.similarity_weights["silhouette"], 0.30)
        self.assertEqual(profile.polygon_budget, 25000)

    def test_20_e2e_reference_to_parametric_engine(self):
        """Test 20: Flujo E2E: Referencia -> VisualSpec -> StructuralSpec -> Parametric Asset Engine."""
        vspec = self.api.analyze_references_to_visual_spec([self.ref_primary])
        sspec = self.api.compile_structural_specification(vspec)
        
        # Crear en Motor Paramétrico de Fase 40
        asset = self.param_api.create_asset("HOUSE_FROM_SPEC", sspec.target_parameters)
        self.assertEqual(asset.asset_id, "HOUSE_FROM_SPEC")
        self.assertEqual(len(asset.components), 5)
        self.assertEqual(asset.components["walls"].materials["wall_mat"], "STONE_ROUGH")

if __name__ == "__main__":
    unittest.main()
