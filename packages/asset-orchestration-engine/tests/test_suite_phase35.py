import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.amsl import (
    AMSLAPI, AssetSpecification, DimensionValue, DimensionsSpec,
    ConstraintSpec, ConstraintType, ConstraintPriority, AMSLAssetType
)

class TestAMSLPhase35Acceptance(unittest.TestCase):
    def setUp(self):
        self.api = AMSLAPI()
        self.base_spec = self.api.create_medieval_house_spec()

    def test_01_acceptance_1_medieval_house_full_spec_creation(self):
        """Acceptance Test 1: Crear 'medieval_house' produce una especificación completa sin comandos Blender."""
        spec = self.base_spec
        self.assertEqual(spec.category, "MEDIEVAL_HOUSE")
        self.assertEqual(spec.dimensions.width.target, 6.0)
        self.assertEqual(spec.structure.floors, 2)
        self.assertEqual(len(spec.components), 2)
        self.assertGreater(len(spec.materials), 0)
        self.assertEqual(spec.generation.generator, "MedievalHouseBuilder")

    def test_02_acceptance_2_single_property_diff(self):
        """Acceptance Test 2: Modificar solo 'dimensions.width' genera una diff que contiene únicamente dicha propiedad."""
        spec_b = self.api.create_medieval_house_spec(width=7.5)
        diff = self.api.diff_specs(self.base_spec, spec_b)
        self.assertIn("dimensions.width", diff.modified)
        self.assertEqual(diff.modified["dimensions.width"]["from"], 6.0)
        self.assertEqual(diff.modified["dimensions.width"]["to"], 7.5)
        self.assertNotIn("dimensions.height", diff.modified)

    def test_03_acceptance_3_structural_dependency_detection(self):
        """Acceptance Test 3: Modificar 'structure.roof.pitch' detecta dependencias estructurales y exige rebuild."""
        _, reqs = self.api.compile_spec(self.base_spec, overrides={"structure.roof.pitch": 45.0})
        self.assertTrue(reqs.requires_rebuild)
        self.assertEqual(reqs.modification_cost, "HIGH")
        self.assertIn("ROOF_SUPPORT", reqs.dependencies)

    def test_04_acceptance_4_locked_constraint_conflict(self):
        """Acceptance Test 4: Intentar modificar propiedad bloqueada produce SPECIFICATION_CONFLICT."""
        spec_locked = self.api.create_medieval_house_spec()
        spec_locked.constraints.append(
            ConstraintSpec(type=ConstraintType.HARD, priority=ConstraintPriority.USER_HARD, rule={"preserve": "structure.roof"})
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.compile_spec(spec_locked, overrides={"structure.roof.pitch": 50.0})
        self.assertIn("SPECIFICATION_CONFLICT", str(ctx.exception))

    def test_05_acceptance_5_deterministic_specification_hash(self):
        """Acceptance Test 5: Dos especificaciones con misma seed y versión producen el mismo hash determinista."""
        s1 = self.api.create_medieval_house_spec(seed=12345)
        s2 = self.api.create_medieval_house_spec(seed=12345)
        self.assertEqual(s1.compute_specification_hash(), s2.compute_specification_hash())

    def test_06_acceptance_6_material_only_change_optimization(self):
        """Acceptance Test 6: Modificar únicamente material no provoca reconstrucción geométrica."""
        _, reqs = self.api.compile_spec(self.base_spec, overrides={"material.mat_walls": "#A0A0A0"})
        self.assertFalse(reqs.requires_rebuild)
        self.assertEqual(reqs.modification_cost, "LOW")
        self.assertEqual(reqs.required_builders, ["MaterialBuilder"])

    def test_07_acceptance_7_invalid_unit_protection(self):
        """Acceptance Test 7: Introducir una unidad desconocida produce INVALID_UNIT."""
        bad_spec = self.api.create_medieval_house_spec()
        bad_spec.dimensions.width = DimensionValue(target=10.0, unit="cubits")
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_spec(bad_spec)
        self.assertIn("INVALID_UNIT", str(ctx.exception))

    def test_08_acceptance_8_missing_required_field_protection(self):
        """Acceptance Test 8: Eliminar un campo obligatorio produce INVALID_SPECIFICATION."""
        bad_spec = self.api.create_medieval_house_spec()
        bad_spec.specification_id = ""
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_spec(bad_spec)
        self.assertIn("INVALID_SPECIFICATION", str(ctx.exception))

    def test_09_acceptance_9_unknown_schema_field_protection(self):
        """Acceptance Test 9: Agregar un campo no declarado produce SCHEMA_ERROR."""
        raw_payload = {
            "specification_id": "SPEC_001",
            "schema_version": "1.0.0",
            "asset_id": "HOUSE_001",
            "asset_type": "BUILDING",
            "hallucinated_field": "some_ai_garbage"
        }
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_spec(self.base_spec, raw_dict=raw_payload)
        self.assertIn("SCHEMA_ERROR", str(ctx.exception))

    def test_10_acceptance_10_canonical_hash_invariant_to_order(self):
        """Acceptance Test 10: Dos especificaciones semánticamente iguales con distinto orden producen el mismo hash canónico."""
        s1 = self.api.create_medieval_house_spec()
        s2 = self.api.create_medieval_house_spec()
        s2.components.reverse()
        s2.materials.reverse()
        self.assertEqual(s1.compute_specification_hash(), s2.compute_specification_hash())

if __name__ == "__main__":
    unittest.main()
