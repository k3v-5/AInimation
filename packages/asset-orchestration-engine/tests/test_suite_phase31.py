import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_specification_compiler import (
    IntentSpecificationAPI, AssetSpec, SpecStatus, ApprovalState,
    SemanticDictionary, SpecDiffEngine
)

class TestIntentSpecificationCompilerPhase31(unittest.TestCase):
    def setUp(self):
        self.api = IntentSpecificationAPI()
        self.raw_prompt = (
            "Quiero una casa medieval pequeña, vieja y ligeramente inclinada, "
            "con una puerta grande de madera, dos ventanas estrechas, "
            "una escalera interior al segundo piso y que el jugador pueda entrar. "
            "No quiero que parezca una casa de fantasía, sino una construcción medieval rural."
        )

    def test_01_complex_natural_language_compilation_scenario_140(self):
        """Test 1: Scenario 140 - Compila prompt complejo a AssetSpec completo sin ejecutar MCP."""
        spec, warnings, errors = self.api.compile_intent(self.raw_prompt, spec_id="spec_rural_house_01")
        self.assertEqual(len(errors), 0)
        self.assertEqual(spec.style.architecture, "MEDIEVAL_RURAL")
        self.assertEqual(spec.style.condition, "AGED")
        self.assertIn("FANTASY", spec.style.forbidden_styles)
        self.assertEqual(spec.visual.lean_angle_deg, 2.5)
        self.assertEqual(spec.door.material, "WOOD")
        self.assertEqual(spec.door.width_m, 0.90)
        self.assertTrue(spec.door.player_passable)
        self.assertEqual(spec.windows.count, 2)
        self.assertEqual(spec.windows.style, "NARROW")
        self.assertTrue(spec.stairs.required)
        self.assertEqual(spec.stairs.destination, "SECOND_FLOOR")
        self.assertGreaterEqual(len(spec.requirements), 8)
        self.assertGreaterEqual(len(spec.assumptions), 2)

    def test_02_spec_v1_to_v2_diff_and_impact_analysis_scenario_141(self):
        """Test 2: Scenario 141 - Modificación a 3 ventanas genera Spec v2 y calcula subárbol afectado."""
        spec_v1, _, _ = self.api.compile_intent(self.raw_prompt, spec_id="house_v1")
        prompt_v2 = self.raw_prompt.replace("dos ventanas", "tres ventanas")
        spec_v2, _, _ = self.api.compile_intent(prompt_v2, spec_id="house_v2")
        spec_v2.spec_version = "2.0.0"

        diff, impact = self.api.diff_and_analyze_impact(spec_v1, spec_v2)
        self.assertIn("windows.count", diff.modified_fields)
        self.assertEqual(diff.modified_fields["windows.count"], (2, 3))
        self.assertIn("windows", impact.affected_components)
        self.assertIn("wall_geometry", impact.affected_components)
        self.assertIn("door", impact.unaffected_components)
        self.assertIn("stairs", impact.unaffected_components)
        self.assertEqual(impact.rebuild_scope, "SUBTREE")

    def test_03_anti_hallucination_unknown_material(self):
        """Test 3: Material inventado 'dragonium' produce error UNKNOWN_MATERIAL."""
        fake_prompt = "Quiero una casa con material dragonium"
        _, _, errors = self.api.compile_intent(fake_prompt)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(any("UNKNOWN_MATERIAL" in e for e in errors))

    def test_04_contradiction_conflict_detection(self):
        """Test 4: Puerta de 0.50m con player_passable=True genera SPEC_CONFLICT."""
        spec, _, _ = self.api.compile_intent(self.raw_prompt)
        spec.door.width_m = 0.50 # Inválido para jugador
        is_valid, conflicts = self.api.validate_spec(spec)
        self.assertFalse(is_valid)
        self.assertTrue(any("SPEC_CONFLICT" in c for c in conflicts))

    def test_05_deterministic_canonical_hash(self):
        """Test 5: Mismo prompt produce idéntico spec_hash determinista."""
        spec1, _, _ = self.api.compile_intent(self.raw_prompt)
        spec2, _, _ = self.api.compile_intent(self.raw_prompt)
        h1 = spec1.compute_spec_hash()
        h2 = spec2.compute_spec_hash()
        self.assertEqual(h1, h2)

    def test_06_spec_to_task_compiler_traceability(self):
        """Test 6: SpecTaskCompiler mapea cada tarea a los REQ-xxx correspondientes."""
        spec, _, _ = self.api.compile_intent(self.raw_prompt)
        tasks = self.api.generate_tasks_from_spec(spec)
        self.assertGreaterEqual(len(tasks), 5)
        door_task = next(t for t in tasks if t["task_id"] == "T_DOOR")
        self.assertIn("REQ-005", door_task["implements"])
        self.assertIn("REQ-008", door_task["implements"])

    def test_07_semantic_dictionary_normalization(self):
        """Test 7: Normalización semántica de sinónimos."""
        self.assertEqual(SemanticDictionary.normalize_term("de tamaño reducido"), "SMALL")
        self.assertEqual(SemanticDictionary.normalize_term("envejecida"), "AGED")
        self.assertEqual(SemanticDictionary.normalize_term("inclinada"), "SLIGHTLY_LEANING")

    def test_08_spec_validation_and_approval_transition(self):
        """Test 8: Validación exitosa transiciona estado a VALIDATED y APPROVED."""
        spec, _, _ = self.api.compile_intent(self.raw_prompt)
        is_valid, conflicts = self.api.validate_spec(spec)
        self.assertTrue(is_valid)
        self.assertEqual(spec.status, SpecStatus.VALIDATED)
        self.assertEqual(spec.approval, ApprovalState.APPROVED)

    def test_09_forbidden_style_exclusion(self):
        """Test 9: Estilo prohibido 'FANTASY' se registra explícitamente en forbidden_styles."""
        spec, _, _ = self.api.compile_intent(self.raw_prompt)
        self.assertIn("FANTASY", spec.style.forbidden_styles)

    def test_10_offline_pure_compilation(self):
        """Test 10: Compilación puramente analítica y determinista sin efectos secundarios."""
        spec, warnings, errors = self.api.compile_intent(self.raw_prompt)
        self.assertIsNotNone(spec)
        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
