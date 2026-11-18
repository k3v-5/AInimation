import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import (
    VisualSpecificationAPI, VisualCompilationInput, RequirementClass,
    ValidationMethod, ContradictionSeverity, AmbiguitySeverity,
    InformationState, RequirementOrigin
)
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)

class TestVisualSpecificationCompilerPhase56(unittest.TestCase):
    def setUp(self):
        self.api = VisualSpecificationAPI()

    def test_01_case_a_simple_asset_compilation(self):
        """Case A: Espada medieval de acero de 1m genera VAS con identidad, dimensiones y materiales."""
        comp_input = VisualCompilationInput(
            prompt="Crear una espada medieval de acero, aproximadamente 1 metro de largo.",
            asset_class_hint="WEAPON.SWORD",
            semantic_context={"semantic_id": "sword_01.root", "asset_id": "sword_01"}
        )
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.semantic_identity["semantic_id"], "sword_01.root")
        self.assertEqual(vas.dimensions["height"], 1.0)
        self.assertEqual(vas.material_requirements["base_material"], "STEEL")
        self.assertGreater(len(vas.acceptance_criteria), 0)

    def test_02_case_b_visual_reference_fusion(self):
        """Case B: Prompt + Reporte F55 convierte observaciones visuales en requisitos trazables."""
        f55_rep = DecomposedReferenceReport(
            report_id="F55_BARREL_REP",
            reference_ids=["REF_1"],
            silhouette=SilhouetteExtraction(aspect_ratio=1.45, symmetry_axis="VERTICAL_Z"),
            proportions=ProportionEstimate(component_ratios={"body": 0.80, "rings": 0.20}),
            parts=[
                DecomposedPart("part_body", "BODY", (0,0,1,1.45), (0,0,0), True, 0.98),
                DecomposedPart("part_ring", "RING", (0,0,1,0.2), (0,0,1.1), False, 0.95)
            ],
            materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.70)
        )
        comp_input = VisualCompilationInput(
            prompt="Barril medieval estilizado",
            asset_class_hint="PROP.BARREL",
            reference_reports=[f55_rep],
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"}
        )
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.silhouette["aspect_ratio"], 1.45)
        self.assertEqual(len(vas.components), 2)
        self.assertTrue(any(t.source_type == RequirementOrigin.F55_REFERENCE for t in vas.traceability))

    def test_03_case_c_contradiction_detection(self):
        """Case C: 'highly detailed' + 500 triángulos genera contradicción crítica."""
        comp_input = VisualCompilationInput(
            prompt="Highly detailed realistic medieval prop",
            project_constraints={"triangle_budget": 500}
        )
        vas = self.api.compile_specification(comp_input)
        val = self.api.validate_specification(vas)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("CRITICAL_CONTRADICTION" in err for err in val.errors))

    def test_04_case_d_ambiguity_detection(self):
        """Case D: 'hazla más grande' genera reporte de ambigüedad con severidad HIGH."""
        comp_input = VisualCompilationInput(
            prompt="Espada bonita, pero hazla más grande"
        )
        vas = self.api.compile_specification(comp_input)
        self.assertTrue(any(a.severity == AmbiguitySeverity.HIGH for a in vas.ambiguity_report))

    def test_05_case_e_hard_requirement_preservation(self):
        """Case E: 'height = 2.0m ± 0.02m' se clasifica como HARD."""
        comp_input = VisualCompilationInput(
            prompt="Estructura de 2.0m de alto con tolerancia de ± 0.02m"
        )
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.requirement_classes.get("dimensions.height"), RequirementClass.HARD)

    def test_06_case_f_modifiable_variables_identification(self):
        """Case F: Variables modificables identificadas para F64 Autonomous Corrector."""
        comp_input = VisualCompilationInput(prompt="Barril estándar")
        vas = self.api.compile_specification(comp_input)
        var_ids = [v.variable_id for v in vas.variables]
        self.assertIn("VAR_BEVEL_WIDTH", var_ids)
        self.assertIn("VAR_ROUGHNESS", var_ids)
        self.assertTrue(all(v.allowed_to_change for v in vas.variables))

    def test_07_case_g_unreal_engine_technical_requirements(self):
        """Case G: Preservación de requisitos técnicos de Unreal (Nanite, LODs, Collisions)."""
        comp_input = VisualCompilationInput(
            prompt="Pilar de piedra",
            project_constraints={"nanite": True, "lod_count": 4, "collision_required": True}
        )
        vas = self.api.compile_specification(comp_input)
        self.assertTrue(vas.unreal_requirements.nanite_enabled)
        self.assertEqual(vas.unreal_requirements.lod_count, 4)
        self.assertTrue(vas.unreal_requirements.collision_required)

    def test_08_case_h_deterministic_hashing(self):
        """Case H: Misma entrada genera idéntico specification_hash."""
        inp1 = VisualCompilationInput(prompt="Cofre de madera con cerradura de hierro")
        inp2 = VisualCompilationInput(prompt="Cofre de madera con cerradura de hierro")
        vas1 = self.api.compile_specification(inp1)
        vas2 = self.api.compile_specification(inp2)
        self.assertEqual(vas1.specification_hash, vas2.specification_hash)

    def test_09_case_i_revision_tracking(self):
        """Case I: Recompilación con VAS previa incrementa la versión (1.1.0) manteniendo semantic_id."""
        inp1 = VisualCompilationInput(prompt="Barril básico", semantic_context={"semantic_id": "barrel_42.root", "asset_id": "barrel_42"})
        vas1 = self.api.compile_specification(inp1)
        self.assertEqual(vas1.specification_version, "1.0.0")

        inp2 = VisualCompilationInput(prompt="Barril básico con aros extra", previous_vas=vas1, semantic_context={"semantic_id": "barrel_42.root", "asset_id": "barrel_42"})
        vas2 = self.api.compile_specification(inp2)
        self.assertEqual(vas2.specification_version, "1.1.0")
        self.assertEqual(vas2.semantic_identity["semantic_id"], "barrel_42.root")

    def test_10_case_j_historical_state_preservation(self):
        """Case J: Nueva compilación preserva metadatos semánticos aceptados."""
        inp1 = VisualCompilationInput(prompt="Antorcha de pared", semantic_context={"semantic_id": "torch_01.root", "asset_id": "torch_01"})
        vas1 = self.api.compile_specification(inp1)
        
        inp2 = VisualCompilationInput(prompt="Antorcha de pared", previous_vas=vas1)
        vas2 = self.api.compile_specification(inp2)
        self.assertEqual(vas2.semantic_identity["semantic_id"], "torch_01.root")

    def test_11_requirement_classification_categories(self):
        """Test 11: Clasificación de requisitos en HARD, SOFT, PREFERENCE, INFORMATIONAL."""
        comp_input = VisualCompilationInput(prompt="Objeto decorativo")
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.requirement_classes.get("silhouette"), RequirementClass.HARD)
        self.assertEqual(vas.requirement_classes.get("secondary_details"), RequirementClass.PREFERENCE)

    def test_12_quantitative_acceptance_criteria(self):
        """Test 12: Generación de criterios cuantitativos con métodos de validación."""
        comp_input = VisualCompilationInput(prompt="Escudo metálico")
        vas = self.api.compile_specification(comp_input)
        methods = {c.validation_method for c in vas.acceptance_criteria}
        self.assertIn(ValidationMethod.VISUAL, methods)
        self.assertIn(ValidationMethod.NUMERIC, methods)
        self.assertIn(ValidationMethod.TOPOLOGICAL, methods)

    def test_13_invariant_specifications(self):
        """Test 13: Invariantes protegen silueta y componentes funcionales."""
        comp_input = VisualCompilationInput(prompt="Puerta blindada")
        vas = self.api.compile_specification(comp_input)
        inv_ids = [i.invariant_id for i in vas.invariants]
        self.assertIn("INV_SILHOUETTE", inv_ids)
        self.assertIn("INV_FUNCTIONAL_CONFIG", inv_ids)

    def test_14_traceability_origin_tracking(self):
        """Test 14: Registro de trazabilidad para cada requisito."""
        comp_input = VisualCompilationInput(prompt="Espada de 1.2m de acero")
        vas = self.api.compile_specification(comp_input)
        origins = {t.source_type for t in vas.traceability}
        self.assertIn(RequirementOrigin.USER_PROMPT, origins)

    def test_15_priorities_normalization(self):
        """Test 15: Prioridades normalizadas entre 0.0 y 1.0 con silueta a 1.0."""
        comp_input = VisualCompilationInput(prompt="Arco de madera")
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.priorities["silhouette"], 1.0)
        self.assertLess(vas.priorities["micro_detail"], vas.priorities["silhouette"])

    def test_16_validation_result_valid_specification(self):
        """Test 16: Especificación limpia valida con is_valid = True."""
        comp_input = VisualCompilationInput(prompt="Cubo de piedra")
        vas = self.api.compile_specification(comp_input)
        val = self.api.validate_specification(vas)
        self.assertTrue(val.is_valid)
        self.assertEqual(len(val.errors), 0)

    def test_17_information_state_explicit_vs_inferred(self):
        """Test 17: Detección de estado EXPLICIT si hay medidas explícitas en prompt."""
        inp_exp = VisualCompilationInput(prompt="Mesa de 2.0m de largo")
        vas_exp = self.api.compile_specification(inp_exp)
        self.assertEqual(vas_exp.intent["information_state"], InformationState.EXPLICIT)

    def test_18_empty_compilation_input_raises_error(self):
        """Test 18: Entrada vacía lanza ValueError."""
        with self.assertRaises(ValueError):
            self.api.compile_specification(VisualCompilationInput(prompt=""))

    def test_19_style_requirements_representation(self):
        """Test 19: Representación estructurada del estilo."""
        comp_input = VisualCompilationInput(prompt="Torre medieval estilizada")
        vas = self.api.compile_specification(comp_input)
        self.assertEqual(vas.visual_identity.get("archetype"), "STYLIZED")

    def test_20_end_to_end_compiler_pipeline(self):
        """Test 20: Flujo E2E: Input -> Compile -> Hash -> Validate -> VAS."""
        inp = VisualCompilationInput(
            prompt="Barril medieval de roble oscuro, 1.2m de alto",
            asset_class_hint="PROP.BARREL",
            semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"}
        )
        vas = self.api.compile_specification(inp)
        val = self.api.validate_specification(vas)
        self.assertTrue(val.is_valid)
        self.assertEqual(vas.semantic_identity["semantic_id"], "barrel_hero.root")
        self.assertEqual(vas.dimensions["height"], 1.2)

if __name__ == "__main__":
    unittest.main()
