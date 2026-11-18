import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    SpecificationCompilerAPI, AssetSpec, AttributeProvenance, UnitResolver
)

class TestSpecCompilerPhase14(unittest.TestCase):
    def setUp(self):
        self.spec_api = SpecificationCompilerAPI()

    def test_01_exact_dimension_compilation(self):
        """Test 1: Exact Dimension - 'espada de 120 cm' compila a 1.20m como hard constraint."""
        ok, spec, msg = self.spec_api.compile_request("Quiero una espada de 120 cm")
        self.assertTrue(ok)
        self.assertIsNotNone(spec)
        dim = spec.dimensions.get("total_length")
        self.assertIsNotNone(dim)
        self.assertEqual(dim.target, 1.20)
        self.assertEqual(dim.tolerance, 0.0)
        self.assertTrue(dim.is_hard_constraint)
        self.assertEqual(dim.provenance, AttributeProvenance.EXPLICIT)

    def test_02_approximate_dimension_compilation(self):
        """Test 2: Approximate Dimension - 'espada de unos 120 cm' compila con tolerancia 5% y soft constraint."""
        ok, spec, msg = self.spec_api.compile_request("Quiero una espada de unos 120 cm")
        self.assertTrue(ok)
        dim = spec.dimensions.get("total_length")
        self.assertEqual(dim.target, 1.20)
        self.assertEqual(dim.tolerance, 0.05)
        self.assertFalse(dim.is_hard_constraint)

    def test_03_negative_constraint_extraction(self):
        """Test 3: Negative constraint - 'sin grabados' se extrae como negative_constraints = ['engraving']."""
        ok, spec, msg = self.spec_api.compile_request("Quiero una espada medieval sin grabados")
        self.assertTrue(ok)
        self.assertIn("engraving", spec.negative_constraints)

    def test_04_relative_relation_extraction(self):
        """Test 4: Relative relation - 'hoja tres veces más larga que la empuñadura' compila ratio=3.0."""
        ok, spec, msg = self.spec_api.compile_request("Espada con hoja tres veces más larga que la empuñadura")
        self.assertTrue(ok)
        self.assertEqual(spec.proportions.get("blade_to_handle_ratio"), 3.0)

    def test_05_conflict_detection(self):
        """Test 5: Conflict - Dimensiones contradictorias '100 cm y 150 cm' devuelven SPECIFICATION_CONFLICT."""
        ok, spec, msg = self.spec_api.compile_request("Quiero una espada de 100 cm y 150 cm a la vez")
        self.assertFalse(ok)
        self.assertIn("SPECIFICATION_CONFLICT", msg)

    def test_06_ambiguity_detection(self):
        """Test 6: Ambiguity - 'hazla grande' sin cotas técnicas devuelve AMBIGUITY_DETECTED."""
        ok, spec, msg = self.spec_api.compile_request("Quiero una espada grande y bonita")
        self.assertFalse(ok)
        self.assertIn("AMBIGUITY_DETECTED", msg)

    def test_07_explicit_vs_inferred_provenance(self):
        """Test 7: Provenance - 'empuñadura de cuero' tiene material EXPLICIT y roughness INFERRED."""
        ok, spec, msg = self.spec_api.compile_request("Espada con empuñadura de cuero oscuro")
        self.assertTrue(ok)
        grip = spec.components.get("grip")
        self.assertIsNotNone(grip)
        self.assertEqual(grip.materials.get("material_type"), "LEATHER")
        self.assertEqual(grip.provenance, AttributeProvenance.EXPLICIT)
        self.assertEqual(grip.materials.get("roughness"), 0.80)

    def test_08_specification_patching(self):
        """Test 8: Patching - Modificar blade.length incrementa versión a v2 y aísla el cambio."""
        ok, spec_v1, _ = self.spec_api.compile_request("Espada de 120 cm")
        spec_v2, diff = self.spec_api.apply_patch(spec_v1, "blade.length", 1.40)
        self.assertEqual(spec_v2.version, 2)
        self.assertEqual(spec_v2.components["blade"].dimensions["length"].target, 1.40)
        self.assertEqual(diff["before"], 1.20)
        self.assertEqual(diff["after"], 1.40)

    def test_09_specification_drift_detection(self):
        """Test 9: Drift detection - Longitud real 1.50m vs especificación 1.20m produce drift HIGH."""
        ok, spec, _ = self.spec_api.compile_request("Espada de 120 cm")
        sev, pct, msg = self.spec_api.check_drift({"blade_length": 1.50}, spec)
        self.assertEqual(sev, "HIGH")
        self.assertGreater(pct, 0.20)
        self.assertIn("SPEC_DRIFT", msg)

    def test_10_json_serialization_roundtrip(self):
        """Test 10: Serialization - to_json -> from_json conserva equivalencia exacta."""
        ok, spec1, _ = self.spec_api.compile_request("Espada medieval estilizada de 120 cm con empuñadura de cuero")
        json_str = spec1.to_json()
        spec2 = AssetSpec.from_json(json_str)
        self.assertEqual(spec1.spec_id, spec2.spec_id)
        self.assertEqual(spec1.asset_type, spec2.asset_type)
        self.assertEqual(spec1.style.realism, spec2.style.realism)

    def test_11_ontology_extension(self):
        """Test 11: Ontology extension - Reconoce SHIELD sin modificar el código base."""
        self.spec_api.register_asset_type("SHIELD")
        ok, spec, msg = self.spec_api.compile_request("Quiero un escudo medieval")
        self.assertTrue(ok)
        self.assertEqual(spec.asset_type, "SHIELD")

    def test_12_compiler_caching(self):
        """Test 12: Caching - Misma petición se resuelve desde caché."""
        ok1, spec1, _ = self.spec_api.compile_request("Espada de 100 cm")
        ok2, spec2, msg2 = self.spec_api.compile_request("Espada de 100 cm")
        self.assertTrue(ok2)
        self.assertEqual(spec1.spec_id, spec2.spec_id)
        self.assertIn("cache", msg2)

    def test_13_unit_conversions(self):
        """Test 13: Unit conversions - mm y pulgadas se normalizan a metros."""
        dim_mm = UnitResolver.parse_dimension_from_text("35 mm")
        self.assertEqual(dim_mm.target, 0.035)
        dim_in = UnitResolver.parse_dimension_from_text("48 inches")
        self.assertEqual(dim_in.target, 1.2192)

    def test_14_full_pipeline_compilation(self):
        """Test 14: Full Pipeline - Petición completa compila todas las entidades y restricciones."""
        text = "Quiero una espada medieval estilizada de 120 cm, con una hoja ancha, guardia metálica y empuñadura de cuero oscuro. No quiero grabados."
        ok, spec, msg = self.spec_api.compile_request(text)
        self.assertTrue(ok)
        self.assertEqual(spec.asset_type, "SWORD")
        self.assertEqual(spec.style.category, "MEDIEVAL")
        self.assertEqual(spec.style.realism, "STYLIZED")
        self.assertEqual(spec.dimensions["total_length"].target, 1.20)
        self.assertIn("engraving", spec.negative_constraints)
        self.assertIn("blade", spec.components)
        self.assertIn("guard", spec.components)
        self.assertIn("grip", spec.components)

if __name__ == "__main__":
    unittest.main()
