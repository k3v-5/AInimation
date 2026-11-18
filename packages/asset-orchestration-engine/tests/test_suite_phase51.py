import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompt_compiler_intent_spec import (
    PromptCompilerAPI, CompilationStatus, IntentType,
    ProvenanceType, ConversationContext
)

class TestPromptCompilerPhase51(unittest.TestCase):
    def setUp(self):
        self.api = PromptCompilerAPI()

    def test_01_mandatory_case_1_barrel_intent_compilation(self):
        """Mandatory Case 1: Prompt completo de barril medieval grabbable."""
        prompt = "Quiero un barril medieval grande, de madera oscura, estilizado, con dos aros metálicos y que el jugador pueda recogerlo."
        res = self.api.compile_intent(prompt)
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        spec = res.specification
        self.assertEqual(spec.asset_class, "PROP.BARREL")
        self.assertEqual(spec.intent, IntentType.CREATE)
        self.assertIn("MEDIEVAL", spec.style)
        self.assertIn("STYLIZED", spec.style)
        self.assertEqual(spec.materials.get("body"), "DARK_WOOD")
        self.assertEqual(spec.components.get("METAL_RING"), 2)
        self.assertTrue(spec.gameplay_flags.get("grabbable"))
        self.assertIn("COLLISION_REQUIRED", spec.derived_requirements)
        self.assertEqual(spec.provenance_map.get("comp_METAL_RING"), ProvenanceType.USER_EXPLICIT)

    def test_02_mandatory_case_2_sword_default_compilation(self):
        """Mandatory Case 2: 'Hazme una espada' compila a WEAPON.SWORD sin inventar detalles arbitrarios."""
        res = self.api.compile_intent("Hazme una espada")
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        self.assertEqual(res.specification.asset_class, "WEAPON.SWORD")

    def test_03_mandatory_case_3_size_contradiction_conflict(self):
        """Mandatory Case 3: 'Haz una casa pequeña pero enorme' detecta conflicto directo."""
        res = self.api.compile_intent("Haz una casa pequeña pero enorme")
        self.assertEqual(res.status, CompilationStatus.CONFLICT)
        self.assertGreater(len(res.conflicts), 0)
        self.assertEqual(res.conflicts[0].conflict_id, "CONF_SIZE_CONTRADICTION")

    def test_04_mandatory_case_4_relative_height_modification(self):
        """Mandatory Case 4: 'Hazlo igual que el anterior pero 20% más alto' sobre activo previo."""
        ctx = ConversationContext(
            active_asset_id="BARREL_001",
            active_asset_class="PROP.BARREL",
            previous_parameters={"height": 1.50}
        )
        res = self.api.compile_intent("Hazlo igual que el anterior pero 20% más alto", ctx)
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        # 1.50 * 1.20 = 1.80
        self.assertEqual(res.specification.dimensions.get("height"), 1.80)

    def test_05_mandatory_case_5_vague_bonito_safe_defaults(self):
        """Mandatory Case 5: 'Haz un barril bonito' usa defaults seguros sin inventar 17 detalles."""
        res = self.api.compile_intent("Haz un barril bonito")
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        self.assertEqual(res.specification.provenance_map.get("aesthetic"), ProvenanceType.DEFAULT)

    def test_06_mandatory_case_6_negative_constraint_forbidden_rings(self):
        """Mandatory Case 6: 'Haz un barril sin aros' añade METAL_RING a forbidden_features."""
        res = self.api.compile_intent("Haz un barril sin aros")
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        self.assertIn("METAL_RING", res.specification.forbidden_features)
        self.assertNotIn("METAL_RING", res.specification.components)

    def test_07_mandatory_case_7_contradictory_rings_conflict(self):
        """Mandatory Case 7: 'Quiero un barril con dos aros, pero que no tenga ningún aro metálico' detecta conflicto."""
        res = self.api.compile_intent("Quiero un barril con dos aros, pero que no tenga ningún aro metálico")
        self.assertEqual(res.status, CompilationStatus.CONFLICT)
        self.assertTrue(any(c.conflict_id == "CONF_RING_CONTRADICTION" for c in res.conflicts))

    def test_08_mandatory_case_8_gameplay_derived_expansion(self):
        """Mandatory Case 8: 'Haz un barril para gameplay' expande collision y valid pivot."""
        res = self.api.compile_intent("Haz un barril para gameplay")
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        self.assertIn("COLLISION_REQUIRED", res.specification.derived_requirements)
        self.assertIn("VALID_PIVOT_REQUIRED", res.specification.derived_requirements)

    def test_09_mandatory_case_9_modification_without_context_clarification(self):
        """Mandatory Case 9: 'Hazlo más grande' sin activo previo solicita clarificación."""
        res = self.api.compile_intent("Hazlo más grande") # context = None
        self.assertEqual(res.status, CompilationStatus.CLARIFICATION_REQUIRED)
        self.assertGreater(len(res.clarifications), 0)
        self.assertIn("activo", res.clarifications[0].question.lower())

    def test_10_mandatory_case_10_change_material_without_target_clarification(self):
        """Mandatory Case 10: 'Hazlo igual pero cambia el material' sin target pide clarificación de material."""
        ctx = ConversationContext(active_asset_id="BARREL_001", active_asset_class="PROP.BARREL")
        res = self.api.compile_intent("Hazlo igual pero cambia el material", ctx)
        self.assertEqual(res.status, CompilationStatus.CLARIFICATION_REQUIRED)
        self.assertEqual(res.clarifications[0].impact_category, "MATERIAL")

    def test_11_synonym_normalization_tonel(self):
        """Test 11: 'tonel' normaliza a PROP.BARREL."""
        res = self.api.compile_intent("Crea un tonel de madera")
        self.assertEqual(res.specification.asset_class, "PROP.BARREL")

    def test_12_component_synonym_bandas(self):
        """Test 12: 'dos bandas' normaliza a METAL_RING: 2."""
        res = self.api.compile_intent("Barril con dos bandas metálicas")
        self.assertEqual(res.specification.components.get("METAL_RING"), 2)

    def test_13_percentage_modifier_parsing(self):
        """Test 13: UnitNormalizer procesa '30% más alto' -> 1.30."""
        from src.prompt_compiler_intent_spec.normalizer.unit_normalizer import UnitNormalizer
        mod = UnitNormalizer.parse_percentage_modifier("30% más alto")
        self.assertEqual(mod, 1.30)

    def test_14_delete_intent_parsing(self):
        """Test 14: 'elimina la puerta' parsea intent DELETE."""
        res = self.api.compile_intent("elimina la puerta")
        self.assertEqual(res.specification.intent, IntentType.DELETE)

    def test_15_material_extraction_stone_and_wood(self):
        """Test 15: Extracción de madera y piedra."""
        res = self.api.compile_intent("Casa de piedra con tejado de madera")
        self.assertEqual(res.specification.materials.get("walls"), "STONE")
        self.assertEqual(res.specification.materials.get("body"), "WOOD")

    def test_16_style_extraction_low_poly(self):
        """Test 16: Extracción de estilo LOW_POLY."""
        res = self.api.compile_intent("Un barril low-poly")
        self.assertIn("LOW_POLY", res.specification.style)

    def test_17_provenance_derived_tracking(self):
        """Test 17: Mapeo de provenance para requisitos derivados."""
        res = self.api.compile_intent("Un barril para agarrar")
        self.assertEqual(res.specification.provenance_map.get("COLLISION_REQUIRED"), ProvenanceType.DERIVED)

    def test_18_immutable_specification_object(self):
        """Test 18: La especificación compilada contiene id y versión formal."""
        res = self.api.compile_intent("Un barril medieval")
        self.assertTrue(res.specification.specification_id.startswith("SPEC_"))
        self.assertEqual(res.specification.version, "1.0.0")

    def test_19_modify_intent_parsing(self):
        """Test 19: 'modifica el tejado' parsea intent MODIFY."""
        ctx = ConversationContext(active_asset_id="HOUSE_001", active_asset_class="BUILDING.HOUSE")
        res = self.api.compile_intent("modifica el tejado", ctx)
        self.assertEqual(res.specification.intent, IntentType.MODIFY)

    def test_20_end_to_end_intent_to_specification_pipeline(self):
        """Test 20: Flujo E2E: Lenguaje natural -> Normalización -> Extracción -> Reglas de Gameplay -> CompiledSpecification."""
        prompt = "Hazme un barril medieval estilizado con dos aros de metal para gameplay"
        res = self.api.compile_intent(prompt)
        self.assertEqual(res.status, CompilationStatus.SUCCESS)
        self.assertEqual(res.specification.asset_class, "PROP.BARREL")
        self.assertEqual(res.specification.components.get("METAL_RING"), 2)
        self.assertIn("COLLISION_REQUIRED", res.specification.derived_requirements)

if __name__ == "__main__":
    unittest.main()
