import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.asset_knowledge_base import (
    AssetKnowledgeAPI, ComponentNecessity, StyleEra, DefectPatternType,
    ConflictPriority, KnowledgeStatus
)
from src.parametric_asset_engine import ParametricAssetAPI

class TestAssetKnowledgeBasePhase44(unittest.TestCase):
    def setUp(self):
        self.api = AssetKnowledgeAPI()
        self.param_api = ParametricAssetAPI()

    def test_01_archetype_discovery_slots(self):
        """Test 1: Consulta de MEDIEVAL_HOUSE devuelve slots obligatorios y opcionales."""
        arch = self.api.get_archetype("MEDIEVAL_HOUSE")
        self.assertEqual(arch.component_slots["roof"].necessity, ComponentNecessity.MANDATORY)
        self.assertEqual(arch.component_slots["windows"].necessity, ComponentNecessity.OPTIONAL)

    def test_02_component_hierarchy_parent_children(self):
        """Test 2: Comprobación del grafo jerárquico de componentes (foundation -> walls -> roof)."""
        arch = self.api.get_archetype("MEDIEVAL_HOUSE")
        self.assertEqual(arch.component_slots["walls"].parent_component, "foundation")
        self.assertIn("roof", arch.component_slots["walls"].children)
        self.assertEqual(arch.component_slots["roof"].parent_component, "walls")

    def test_03_missing_mandatory_component(self):
        """Test 3: Falta de componente obligatorio (roof) detecta MISSING_MANDATORY_COMPONENT."""
        res = self.api.validate_design("MEDIEVAL_HOUSE", {}, active_components={"foundation", "walls", "door"})
        self.assertFalse(res.is_valid)
        self.assertTrue(any("MISSING_MANDATORY_COMPONENT" in e and "roof" in e for e in res.errors))

    def test_04_template_instantiation_and_inheritance(self):
        """Test 4: MEDIEVAL_RURAL_HOUSE hereda de RESIDENTIAL_HOUSE y BASE_BUILDING."""
        tmpl = self.api.get_template("MEDIEVAL_RURAL_HOUSE")
        self.assertEqual(tmpl.parameter_overrides["width"], 8.0)
        self.assertEqual(tmpl.parameter_overrides["window_count"], 4)
        self.assertEqual(tmpl.parameter_overrides["roof_pitch"], 38.0)
        self.assertEqual(tmpl.materials["walls"], "STONE_ROUGH")

    def test_05_incompatible_geometric_combination(self):
        """Test 5: Base redonda con tejado a dos aguas (GABLE) detecta INCOMPATIBLE_COMBINATION."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"base_shape": "ROUND", "roof_type": "GABLE"},
            active_components={"foundation", "walls", "roof", "door"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("INCOMPATIBLE_COMBINATION" in e for e in res.errors))

    def test_06_minimum_roof_pitch_rule(self):
        """Test 6: Pendiente de techo < 25 grados detecta DESIGN_RULE_VIOLATION."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"roof_pitch": 18.0},
            active_components={"foundation", "walls", "roof", "door"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("DESIGN_RULE_VIOLATION" in e for e in res.errors))

    def test_07_unsatisfied_attachment_chimney(self):
        """Test 7: Chimenea activa sin techo detecta UNSATISFIED_ATTACHMENT."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {},
            active_components={"foundation", "walls", "door", "chimney"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("UNSATISFIED_ATTACHMENT" in e for e in res.errors))

    def test_08_spatial_limit_window_overflow(self):
        """Test 8: Ventana que excede la altura de la pared detecta SPATIAL_RULE_VIOLATION."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"wall_height": 2.5, "window_sill_height": 1.5, "window_height": 1.5},
            active_components={"foundation", "walls", "roof", "door", "windows"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("SPATIAL_RULE_VIOLATION" in e for e in res.errors))

    def test_09_style_incompatibility(self):
        """Test 9: Materiales futuristas en estilo medieval detectan STYLE_INCOMPATIBILITY."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"wall_material": "NEON_FUTURISTIC"},
            active_components={"foundation", "walls", "roof", "door"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("STYLE_INCOMPATIBILITY" in e for e in res.errors))

    def test_10_defect_pattern_roof_too_high(self):
        """Test 10: Defecto ROOF_TOO_HIGH devuelve parámetro roof_height y factor 0.80."""
        pat = self.api.lookup_correction_pattern(DefectPatternType.ROOF_TOO_HIGH)
        self.assertEqual(pat.candidate_parameter, "roof_height")
        self.assertEqual(pat.recommended_factor, 0.80)

    def test_11_defect_pattern_facade_too_wide(self):
        """Test 11: Defecto FACADE_TOO_WIDE devuelve parámetro width y factor 0.85."""
        pat = self.api.lookup_correction_pattern(DefectPatternType.FACADE_TOO_WIDE)
        self.assertEqual(pat.candidate_parameter, "width")
        self.assertEqual(pat.recommended_factor, 0.85)

    def test_12_query_by_style_nordic(self):
        """Test 12: query_archetypes_by_style(StyleEra.NORDIC) devuelve NORDIC_CABIN."""
        results = self.api.query_archetypes_by_style(StyleEra.NORDIC)
        self.assertTrue(any(a.archetype_id == "NORDIC_CABIN" for a in results))

    def test_13_slot_max_capacity_exceeded(self):
        """Test 13: 12 ventanas en ranura de max 8 detecta SLOT_CAPACITY_EXCEEDED."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"window_count": 12},
            active_components={"foundation", "walls", "roof", "door", "windows"}
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(any("SLOT_CAPACITY_EXCEEDED" in e for e in res.errors))

    def test_14_valid_design_passes(self):
        """Test 14: Diseño conforme pasa validación con is_valid = True."""
        res = self.api.validate_design(
            "MEDIEVAL_HOUSE",
            {"roof_pitch": 35.0, "window_count": 4, "wall_material": "STONE"},
            active_components={"foundation", "walls", "roof", "door", "windows", "chimney"}
        )
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.errors), 0)

    def test_15_knowledge_base_immutability(self):
        """Test 15: Modificar copia obtenida no altera el registro central."""
        arch = self.api.get_archetype("MEDIEVAL_HOUSE")
        arch.name = "CORRUPTED_NAME"
        arch_fresh = self.api.get_archetype("MEDIEVAL_HOUSE")
        self.assertNotEqual(arch_fresh.name, "CORRUPTED_NAME")

    def test_16_generator_selection_primary(self):
        """Test 16: Selección de generador primario para componentes."""
        gen = self.api.select_generator("MEDIEVAL_HOUSE", "roof")
        self.assertEqual(gen.generator_id, "GEN_ROOF_PARAMETRIC")

    def test_17_generator_fallback_upon_failure(self):
        """Test 17: Fallo en generador primario activa el generador fallback."""
        gen_fb = self.api.select_generator("MEDIEVAL_HOUSE", "roof", simulate_failure=True)
        self.assertEqual(gen_fb.generator_id, "GEN_ROOF_PRIMITIVE")

    def test_18_generator_ranking(self):
        """Test 18: Ranking de generadores calcula score basado en costo y confiabilidad."""
        ranked = self.api.rank_generators("MEDIEVAL_HOUSE")
        self.assertGreater(len(ranked), 0)
        self.assertIn("score", ranked[0])

    def test_19_conflict_resolution_priority_order(self):
        """Test 19: Resolución de conflictos: SAFETY gana sobre STYLE y PREFERENCE."""
        res = self.api.resolve_conflict("roof_pitch", {
            ConflictPriority.STYLE: 15.0,
            ConflictPriority.SAFETY: 35.0,
            ConflictPriority.PREFERENCE: 20.0
        })
        self.assertEqual(res["winning_value"], 35.0)
        self.assertEqual(res["resolved_by_priority"], "SAFETY")

    def test_20_learning_pipeline_observation_and_promotion(self):
        """Test 20: Registro de observación y promoción a APPROVED con evidencia formal."""
        sig = "REPAIR_ROOF_HEIGHT_MINUS_20_PERCENT"
        self.api.record_repair_observation(sig, succeeded=True, evidence="Benchmark test passed")
        self.api.record_repair_observation(sig, succeeded=True, evidence="Visual Critic IoU > 0.90")
        
        msg = self.api.promote_candidate_rule(sig, has_formal_tests=True)
        self.assertIn("successfully promoted to APPROVED", msg)

if __name__ == "__main__":
    unittest.main()
