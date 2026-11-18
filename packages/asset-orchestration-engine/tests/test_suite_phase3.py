import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, PrimitiveGenerator, ProfileGenerator, GeometryValidator, DimensionValidator
)

class TestGeometryEnginePhase3(unittest.TestCase):
    def setUp(self):
        self.geo_engine = GeometryEngine()

    def test_01_minimal_rebuild_only_affected_component(self):
        """Test 1: Modificación mínima - blade.length += 0.10 reconstruye solo blade."""
        # Crear espada con 4 componentes
        self.geo_engine.create_component("sword_01", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
        self.geo_engine.create_component("sword_01", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03}, parent_id="sword_01.handle")
        self.geo_engine.create_component("sword_01", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015, "tip_ratio": 0.15}, parent_id="sword_01.guard")
        self.geo_engine.create_component("sword_01", "pommel", "primitive", {"primitive": "sphere", "width": 0.05, "depth": 0.05, "height": 0.05}, parent_id="sword_01.handle")

        # Modificar solo blade.length
        res = self.geo_engine.modify_component("sword_01.blade", "length", "INCREMENT", 0.10)
        self.assertTrue(res["success"])
        self.assertEqual(res["rebuilt_components"], ["sword_01.blade"])
        self.assertIn("sword_01.handle", res["unaffected_components"])
        self.assertIn("sword_01.guard", res["unaffected_components"])
        self.assertIn("sword_01.pommel", res["unaffected_components"])

        # Verificar que handle y guard siguen en version 1, y blade pasó a version 2
        insp_handle = self.geo_engine.inspect_component("sword_01.handle")
        insp_blade = self.geo_engine.inspect_component("sword_01.blade")
        self.assertEqual(insp_handle["version"], 1)
        self.assertEqual(insp_blade["version"], 2)
        self.assertAlmostEqual(insp_blade["dimensions"][2], 0.95, places=3)

    def test_02_no_op_when_parameters_match(self):
        """Test 2: NO_OP - Enviar el mismo parámetro -> Cero reconstrucciones."""
        self.geo_engine.create_component("box_01", "body", "primitive", {"primitive": "box", "width": 1.0, "depth": 1.0, "height": 2.0})

        res = self.geo_engine.modify_component("box_01.body", "height", "SET", 2.0)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_OP")
        self.assertEqual(res["modified_components"], [])

    def test_03_parametric_dependency_propagation(self):
        """Test 3: Dependencia - guard.width = blade.width * 3 -> al mutar blade.width, ambos se reconstruyen."""
        self.geo_engine.create_component("sword_dep", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})
        self.geo_engine.create_component("sword_dep", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03})
        self.geo_engine.create_component("sword_dep", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})

        # Registrar regla derivada: guard.width = blade.width * 3
        self.geo_engine.set_derived_rule("sword_dep.guard", "width", "blade.width * 3")

        # Mutar blade.width a 0.08m
        res = self.geo_engine.modify_component("sword_dep.blade", "width", "SET", 0.08)
        self.assertTrue(res["success"])
        self.assertIn("sword_dep.blade", res["rebuilt_components"])
        self.assertIn("sword_dep.guard", res["rebuilt_components"])
        self.assertIn("sword_dep.handle", res["unaffected_components"])

        # Verificar que guard.width se recalculó a 0.24m (0.08 * 3)
        insp_guard = self.geo_engine.inspect_component("sword_dep.guard")
        self.assertAlmostEqual(insp_guard["parameters"]["width"], 0.24, places=3)

    def test_04_scope_enforcement(self):
        """Test 4: Scope - Modificar handle con allowed_components=[blade] -> SCOPE_VIOLATION."""
        self.geo_engine.create_component("sword_sc", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015})
        self.geo_engine.create_component("sword_sc", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})

        res = self.geo_engine.modify_component("sword_sc.handle", "height", "SET", 0.30, scope=["blade"])
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "SCOPE_VIOLATION")

    def test_05_rollback_on_build_failure(self):
        """Test 5: Rollback ante fallo en la construcción."""
        self.geo_engine.create_component("box_rb", "body", "primitive", {"primitive": "box", "width": 1.0, "depth": 1.0, "height": 1.0})

        # Intentar modificar con un generador no registrado para forzar fallo
        comp = self.geo_engine.registry.get("box_rb.body")
        comp.generator_type = "invalid_generator"
        res = self.geo_engine.modify_component("box_rb.body", "height", "SET", 5.0)
        self.assertFalse(res["success"])

        # Comprobar que los parámetros anteriores se preservaron
        self.assertEqual(comp.parameters["height"], 1.0)

    def test_06_determinism(self):
        """Test 6: Determinismo - Mismos parámetros producen misma geometría exacta."""
        p_gen = PrimitiveGenerator()
        geo1 = p_gen.build("comp1", {"primitive": "box", "width": 1.0, "depth": 2.0, "height": 3.0})
        geo2 = p_gen.build("comp2", {"primitive": "box", "width": 1.0, "depth": 2.0, "height": 3.0})

        self.assertEqual(geo1.vertices, geo2.vertices)
        self.assertEqual(geo1.faces, geo2.faces)
        self.assertEqual(geo1.dimensions, geo2.dimensions)

    def test_07_invalid_parameters_rejected(self):
        """Test 7: Parámetros inválidos (length = -1.0) -> INVALID_PARAMETER."""
        res = self.geo_engine.create_component("box_inv", "body", "primitive", {"primitive": "box", "width": -1.0, "depth": 1.0, "height": 1.0})
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "INVALID_PARAMETER")

    def test_08_dimension_validation(self):
        """Test 8: Dimension Validator comprueba cotas exactas con tolerancia."""
        p_gen = PrimitiveGenerator()
        geo = p_gen.build("box_val", {"primitive": "box", "width": 1.0, "depth": 1.0, "height": 2.0})

        # Tolerancia correcta
        val_pass, errs = DimensionValidator.validate_dimensions(geo, expected_w=1.0, expected_d=1.0, expected_h=2.0, tolerance=0.005)
        self.assertTrue(val_pass)

        # Mismatch intencional
        val_fail, errs_fail = DimensionValidator.validate_dimensions(geo, expected_w=1.0, expected_d=1.0, expected_h=3.0, tolerance=0.005)
        self.assertFalse(val_fail)
        self.assertIn("Height mismatch", errs_fail[0])

    def test_09_identity_preservation_after_rebuild(self):
        """Test 9: Rebuild e identidad - component_id y parent permanecen idénticos tras rebuild."""
        self.geo_engine.create_component("sword_id", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
        self.geo_engine.create_component("sword_id", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015}, parent_id="sword_id.handle")

        # Modificar blade
        self.geo_engine.modify_component("sword_id.blade", "width", "SET", 0.07)
        comp = self.geo_engine.registry.get("sword_id.blade")

        self.assertEqual(comp.component_id, "sword_id.blade")
        self.assertEqual(comp.asset_id, "sword_id")
        self.assertEqual(comp.parent_id, "sword_id.handle")

    def test_10_geometry_validation_vertex_face_integrity(self):
        """Test 10: Geometry Validation - Verifica integridad de vértices y caras."""
        p_gen = PrimitiveGenerator()
        geo = p_gen.build("test_geo", {"primitive": "cylinder", "width": 0.5, "depth": 0.5, "height": 1.0, "segments": 12})
        val_pass, errs = GeometryValidator.validate_geometry(geo)
        self.assertTrue(val_pass)
        self.assertGreater(len(geo.vertices), 0)
        self.assertGreater(len(geo.faces), 0)

    def test_11_primitive_generator_types(self):
        """Test 11: Primitive Generator soporta cube, cylinder y cone."""
        p_gen = PrimitiveGenerator()
        cube = p_gen.build("c", {"primitive": "cube", "width": 1.0, "depth": 1.0, "height": 1.0})
        cyl = p_gen.build("cy", {"primitive": "cylinder", "width": 0.5, "depth": 0.5, "height": 1.0})
        cone = p_gen.build("co", {"primitive": "cone", "width": 0.5, "depth": 0.5, "height": 1.0})

        self.assertEqual(cube.triangle_count, 12)
        self.assertGreater(cyl.triangle_count, 0)
        self.assertGreater(cone.triangle_count, 0)

    def test_12_profile_generator_blade_shape(self):
        """Test 12: Profile Generator construye hojas con tip_ratio y tapering."""
        prof_gen = ProfileGenerator()
        blade_geo = prof_gen.build("blade_test", {"length": 0.90, "width": 0.06, "thickness": 0.015, "tip_ratio": 0.20})

        self.assertEqual(len(blade_geo.vertices), 9) # 4 base + 4 mid + 1 tip
        self.assertEqual(len(blade_geo.faces), 9)
        self.assertEqual(blade_geo.dimensions, (0.06, 0.015, 0.90))

if __name__ == "__main__":
    unittest.main()
