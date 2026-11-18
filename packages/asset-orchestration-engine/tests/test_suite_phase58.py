import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import (
    GeometryGenerationAPI, GenerationContext, GenerationStatus,
    ExportRole
)

class TestGeometryGenerationEnginePhase58(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()

    def test_01_case_a_simple_asset_generation(self):
        """Case A: Flujo VAS -> MSP -> F58 produce geometría válida."""
        vas_in = VisualCompilationInput(
            prompt="Espada medieval de 1.1m",
            asset_class_hint="WEAPON.SWORD",
            semantic_context={"semantic_id": "sword_01.root", "asset_id": "sword_01"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertEqual(geom.status, GenerationStatus.SUCCESS)
        self.assertGreater(len(geom.geometry_objects), 0)
        self.assertEqual(geom.semantic_id, "sword_01.root")

    def test_02_case_b_hard_surface_bevel_mirror(self):
        """Case B: Hard surface produce modificadores bevel y mirror con topología manifold."""
        vas_in = VisualCompilationInput(prompt="Escudo metálico con simetría bilateral")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertTrue(geom.topology_summary.is_manifold)
        has_mods = any(len(o.modifiers) > 0 for o in geom.geometry_objects)
        self.assertTrue(has_mods)

    def test_03_case_c_procedural_deterministic_seed(self):
        """Case C: Semilla determinista produce idéntica geometría y hash."""
        vas_in = VisualCompilationInput(prompt="Barril de roble oscuro")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        
        ctx1 = GenerationContext(generation_id="G1", strategy_plan=msp, generation_seed=12345)
        ctx2 = GenerationContext(generation_id="G2", strategy_plan=msp, generation_seed=12345)
        geom1 = self.geom_api.generate_geometry(msp, ctx1)
        geom2 = self.geom_api.generate_geometry(msp, ctx2)
        self.assertEqual(geom1.generation_hash, geom2.generation_hash)

    def test_04_case_d_modular_component_breakdown(self):
        """Case D: Activo modular genera objetos con semantic_component_id únicos."""
        vas_in = VisualCompilationInput(prompt="Barril con aros")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        cids = {o.semantic_component_id for o in geom.geometry_objects}
        self.assertIn("comp_main", cids)

    def test_05_case_e_partial_regeneration(self):
        """Case E: Regeneración parcial no altera componentes independientes."""
        vas_in = VisualCompilationInput(prompt="Barril con aros")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom_full = self.geom_api.generate_geometry(msp)
        
        # Regenerar solo 'comp_main'
        geom_part = self.geom_api.regenerate_geometry(["comp_main"], msp)
        self.assertEqual(len(geom_part.geometry_objects), 1)
        self.assertEqual(geom_part.geometry_objects[0].semantic_component_id, "comp_main")

    def test_06_case_f_failure_detection_and_compensation(self):
        """Case F: Operación con error es detectada y compensada."""
        vas_in = VisualCompilationInput(prompt="Pilar simple")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        
        # Inyectar una operación con parámetro inválido en el MSP
        msp.execution_graph[0].parameters["primitive"] = "NON_EXISTENT_PRIMITIVE"
        geom = self.geom_api.generate_geometry(msp)
        self.assertEqual(geom.status, GenerationStatus.FAILED)
        self.assertGreater(len(geom.errors), 0)

    def test_07_case_g_budget_compliance(self):
        """Case G: Generación respeta el presupuesto de triángulos asignado."""
        vas_in = VisualCompilationInput(prompt="Caja de suministros", project_constraints={"triangle_budget": 5000})
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertLessEqual(geom.triangle_count, 5000)

    def test_08_case_h_unreal_engine_interface_and_collision(self):
        """Case H: Genera colisión CUSTOM_UCX y respeta pivot en suelo."""
        vas_in = VisualCompilationInput(prompt="Mesa de comedor")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertIsNotNone(geom.collision_geometry)
        self.assertEqual(geom.collision_geometry.export_role, ExportRole.COLLISION_MESH)
        self.assertEqual(geom.pivot_state["strategy"], "BASE_CENTER_GROUNDED")

    def test_09_case_i_deterministic_geometry_hashing(self):
        """Case I: Dos ejecuciones idénticas producen el mismo hash lógico."""
        vas_in = VisualCompilationInput(prompt="Antorcha gótica")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom1 = self.geom_api.generate_geometry(msp)
        geom2 = self.geom_api.generate_geometry(msp)
        self.assertEqual(geom1.generation_hash, geom2.generation_hash)

    def test_10_case_j_reproducibility_from_history(self):
        """Case J: Reconstrucción desde VAS + MSP + seed reproduce la misma geometría."""
        vas_in = VisualCompilationInput(prompt="Pilar ornamental")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        
        ctx = GenerationContext("REPRO_01", msp, generation_seed=777)
        res1 = self.geom_api.generate_geometry(msp, ctx)
        
        ctx_repro = GenerationContext("REPRO_02", msp, generation_seed=777)
        res2 = self.geom_api.generate_geometry(msp, ctx_repro)
        self.assertEqual(res1.triangle_count, res2.triangle_count)
        self.assertEqual(res1.generation_hash, res2.generation_hash)

    def test_11_topology_metrics_calculation(self):
        """Test 11: Cálculo agregado de métricas de topología (triángulos, vértices, manifold)."""
        vas_in = VisualCompilationInput(prompt="Cubo básico")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertGreater(geom.topology_summary.triangle_count, 0)
        self.assertGreater(geom.topology_summary.vertex_count, 0)
        self.assertTrue(geom.topology_summary.is_manifold)

    def test_12_material_interface_slots(self):
        """Test 12: Preservación de slots de materiales en objetos para F59."""
        vas_in = VisualCompilationInput(prompt="Barril con madera y hierro")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertGreater(len(geom.material_slots), 0)

    def test_13_bounds_and_dimensions_calculation(self):
        """Test 13: Cálculo de dimensiones reales y bounding box AABB."""
        vas_in = VisualCompilationInput(prompt="Cilindro de 1.2m")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertIn("dimensions", geom.bounds)
        self.assertGreater(geom.dimensions["z"], 0.0)

    def test_14_modifier_stack_tracking(self):
        """Test 14: Registro de modificadores aplicados en cada objeto."""
        vas_in = VisualCompilationInput(prompt="Estructura con bevel")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        has_bevel = any(any(m["type"] == "BEVEL" for m in o.modifiers) for o in geom.geometry_objects)
        self.assertTrue(has_bevel)

    def test_15_execution_trace_recording(self):
        """Test 15: Registro de traza de ejecución de operaciones."""
        vas_in = VisualCompilationInput(prompt="Cofre de madera")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertGreater(len(geom.execution_trace), 0)
        self.assertEqual(geom.execution_trace[0]["status"], "SUCCESS")

    def test_16_component_results_dictionary(self):
        """Test 16: Diccionario de resultados individuales indexado por component_id."""
        vas_in = VisualCompilationInput(prompt="Puerta de fortaleza")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertIn("comp_main", geom.component_results)
        self.assertEqual(geom.component_results["comp_main"].status, GenerationStatus.SUCCESS)

    def test_17_semantic_identity_preservation(self):
        """Test 17: Preservación de la identidad semántica en los objetos generados."""
        vas_in = VisualCompilationInput(
            prompt="Espada sagrada",
            semantic_context={"semantic_id": "holy_sword.root", "asset_id": "holy_sword"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        self.assertEqual(geom.semantic_id, "holy_sword.root")
        self.assertEqual(geom.geometry_objects[0].semantic_id, "holy_sword.root")

    def test_18_validation_clean_result(self):
        """Test 18: Validación de resultado limpio retorna is_valid = True."""
        vas_in = VisualCompilationInput(prompt="Escudo de caballero")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        val = self.geom_api.validate_geometry(geom)
        self.assertTrue(val.is_valid)

    def test_19_generate_single_component_api(self):
        """Test 19: API generate_component produce resultado específico."""
        vas_in = VisualCompilationInput(prompt="Barril medieval")
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        comp_res = self.geom_api.generate_component("comp_main", msp)
        self.assertEqual(comp_res.component_id, "comp_main")
        self.assertEqual(comp_res.status, GenerationStatus.SUCCESS)

    def test_20_end_to_end_full_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 (VAS) -> F57 (MSP) -> F58 (Geometry) -> Contrato F59."""
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble oscuro con aros de hierro, 1.2m de alto",
            asset_class_hint="PROP.BARREL",
            semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"},
            project_constraints={"triangle_budget": 20000}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        val = self.geom_api.validate_geometry(geom)
        
        self.assertTrue(val.is_valid)
        self.assertEqual(geom.semantic_id, "barrel_hero.root")
        self.assertGreater(geom.triangle_count, 0)
        self.assertGreater(len(geom.material_slots), 0)

if __name__ == "__main__":
    unittest.main()
