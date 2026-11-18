import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    IntentCompilerAPI, NaturalLanguageRequest, RequestContext,
    SpecStatus, RequirementPriority, RequirementStatus
)

class TestIntentCompilerPhase21(unittest.TestCase):
    def setUp(self):
        self.compiler = IntentCompilerAPI()

    def test_01_basic_compilation_scenario_120(self):
        """Test 1: Scenario 120 - 'Crea espada medieval estilizada de 90 cm' produce spec READY."""
        req = NaturalLanguageRequest("req_01", "Crea una espada medieval estilizada de 90 cm.")
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.READY)
        self.assertEqual(spec.target_type, "SWORD")
        self.assertIn("length", spec.requirements)
        self.assertEqual(spec.requirements["length"].value, 0.90)
        self.assertEqual(spec.requirements["length"].priority, RequirementPriority.CRITICAL)
        self.assertEqual(spec.requirements["style"].value, "MEDIEVAL_STYLIZED")

    def test_02_unit_ambiguity_blocking_scenario_121(self):
        """Test 2: Scenario 121 - 'Crea espada de 90' bloquea por UNIT_AMBIGUITY."""
        req = NaturalLanguageRequest("req_02", "Crea una espada de 90.")
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.BLOCKED)
        self.assertTrue(any("UNIT_AMBIGUITY" in r for r in spec.blocking_reasons))

    def test_03_sequential_recency_override_scenario_122(self):
        """Test 3: Scenario 122 - 90 cm seguido de 'mejor de 110 cm' marca OVERRIDDEN y RESOLVED."""
        req1 = NaturalLanguageRequest("req_03a", "Crea una espada de 90 cm.")
        spec1 = self.compiler.compile(req1)
        req2 = NaturalLanguageRequest("req_03b", "Mejor de 110 cm.")
        spec2 = self.compiler.compile(req2)

        merged = self.compiler.apply_sequential_override(spec1, spec2)
        self.assertEqual(merged.requirements["length"].value, 1.10)
        self.assertEqual(merged.requirements["length_prev"].status, RequirementStatus.OVERRIDDEN)

    def test_04_spatial_directional_constraint_scenario_123(self):
        """Test 4: Scenario 123 - 'Mueve la torre al norte de la plaza' genera constraint NORTH_OF."""
        ctx = RequestContext(available_entities={"tower_001": "tower", "plaza_001": "plaza"})
        req = NaturalLanguageRequest("req_04", "Mueve la torre al norte de la plaza.", context=ctx)
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.READY)
        self.assertEqual(len(spec.constraints), 1)
        self.assertEqual(spec.constraints[0].relation, "NORTH_OF")
        self.assertEqual(spec.constraints[0].object_target, "plaza_001")

    def test_05_target_ambiguity_blocking_scenario_124(self):
        """Test 5: Scenario 124 - 'Mueve la torre' con 2 torres presentes bloquea por TARGET_AMBIGUITY."""
        ctx = RequestContext(available_entities={"tower_001": "tower", "tower_002": "tower"})
        req = NaturalLanguageRequest("req_05", "Mueve la torre.", context=ctx)
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.BLOCKED)
        self.assertTrue(any("TARGET_AMBIGUITY" in r for r in spec.blocking_reasons))

    def test_06_explicit_dimension_priority_scenario_125(self):
        """Test 6: Scenario 125 - Referencia + '4 metros de ancho' asigna 4.0m exactos como USER_EXPLICIT."""
        req = NaturalLanguageRequest(
            "req_06",
            "Haz una casa medieval estilizada igual a esta referencia pero de 4 metros de ancho.",
            reference_image_uri="ref://house_01.png"
        )
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.READY)
        self.assertEqual(spec.requirements["length"].value, 4.0)
        self.assertEqual(spec.requirements["length"].source, "USER_EXPLICIT")

    def test_07_relative_modification_scenario_126(self):
        """Test 7: Scenario 126 - '10% más grande' sobre casa de 4.0m produce 4.4m."""
        req = NaturalLanguageRequest("req_07", "Haz la casa 10% más grande.")
        spec = self.compiler.compile(req)
        self.assertEqual(spec.requirements["width"].value, 4.40)

    def test_08_footprint_incompatibility_scenario_127(self):
        """Test 8: Scenario 127 - '20 casas en 5m x 5m' bloquea por FOOTPRINT_EXCEEDED en simulación."""
        req = NaturalLanguageRequest("req_08", "Crea 20 casas.")
        spec = self.compiler.compile(req)
        ok_sim, errors = self.compiler.simulate(spec, bounds=(5.0, 5.0))
        self.assertFalse(ok_sim)
        self.assertTrue(any("FOOTPRINT_EXCEEDED" in e for e in errors))

    def test_09_contradiction_conflict_blocking_scenario_128(self):
        """Test 9: Scenario 128 - 'Torre de 100m pero que tenga exactamente 10m' produce CONFLICT_DETECTED."""
        req = NaturalLanguageRequest("req_09", "Crea una torre de 100m pero que tenga exactamente 10m de altura.")
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.BLOCKED)
        self.assertTrue(any("CONFLICT_DETECTED" in r for r in spec.blocking_reasons))

    def test_10_contextual_reference_scenario_129(self):
        """Test 10: Scenario 129 - 'Hazla como la anterior' hereda especificación previa."""
        prev_req = NaturalLanguageRequest("req_prev", "Crea una espada medieval estilizada de 90 cm.")
        prev_spec = self.compiler.compile(prev_req)

        ctx = RequestContext(previous_specification=prev_spec)
        req = NaturalLanguageRequest("req_10", "Hazla como la anterior.", context=ctx)
        spec = self.compiler.compile(req)
        self.assertEqual(spec.status, SpecStatus.READY)
        self.assertEqual(spec.target_type, "SWORD")
        self.assertEqual(spec.requirements["length"].value, 0.90)

    def test_11_intent_trace_explainability(self):
        """Test 11: Trace - Genera traza completa desde texto a especificación."""
        req = NaturalLanguageRequest("req_11", "Crea una espada medieval estilizada de 90 cm.")
        spec = self.compiler.compile(req)
        trace = self.compiler.generate_trace(req.text, spec)
        self.assertEqual(trace.raw_text, req.text)
        self.assertEqual(trace.status, "READY")
        self.assertEqual(len(trace.requirements_trace), 2)

    def test_12_build_authorization_gate(self):
        """Test 12: Auth - Autoriza sólo especificaciones READY."""
        req_ok = NaturalLanguageRequest("req_ok", "Crea una espada de 90 cm.")
        spec_ok = self.compiler.compile(req_ok)
        auth_ok = self.compiler.authorize(spec_ok)
        self.assertTrue(auth_ok.authorized)

        req_bad = NaturalLanguageRequest("req_bad", "Crea una espada de 90.")
        spec_bad = self.compiler.compile(req_bad)
        auth_bad = self.compiler.authorize(spec_bad)
        self.assertFalse(auth_bad.authorized)

if __name__ == "__main__":
    unittest.main()
