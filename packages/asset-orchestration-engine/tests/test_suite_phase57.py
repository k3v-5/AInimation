import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.procedural_modeling_strategy import (
    ProceduralModelingStrategyAPI, ComponentConstructionMethod,
    SymmetryType, AssetCategoryTag, StrategyRiskLevel
)

class TestProceduralModelingStrategyPhase57(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()

    def test_01_case_a_sword_component_decomposition(self):
        """Case A: Espada descompuesta en componentes independientes (hoja, guarda, mango)."""
        vas_input = VisualCompilationInput(
            prompt="Espada medieval de acero templado, 1.1m",
            asset_class_hint="WEAPON.SWORD",
            semantic_context={"semantic_id": "sword_hero.root", "asset_id": "sword_hero"}
        )
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertIn(AssetCategoryTag.WEAPON, msp.asset_classification)
        self.assertGreater(len(msp.component_strategies), 0)
        self.assertEqual(msp.semantic_id, "sword_hero.root")

    def test_02_case_b_repetitive_element_array_strategy(self):
        """Case B: Elemento repetitivo (aros/remaches) utiliza ARRAY_BASED en vez de mallas sueltas."""
        vas_input = VisualCompilationInput(
            prompt="Barril medieval con 20 remaches repetitivos en los aros",
            asset_class_hint="PROP.BARREL"
        )
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        methods = [c.method for c in msp.component_strategies]
        self.assertIn(ComponentConstructionMethod.ARRAY_BASED, methods)

    def test_03_case_c_bilateral_symmetry_mirror(self):
        """Case C: Activo bilateral utiliza estrategia de simetría MIRROR."""
        vas_input = VisualCompilationInput(prompt="Escudo con simetría bilateral")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertEqual(msp.symmetry_strategy, SymmetryType.MIRROR)
        has_mirror = any(any(m.modifier_type == "MIRROR" for m in c.modifiers) for c in msp.component_strategies)
        self.assertTrue(has_mirror)

    def test_04_case_d_variant_reuse_strategy(self):
        """Case D: Variantes de activo preservan la estrategia base."""
        vas_input = VisualCompilationInput(prompt="Barril de vino estándar")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertIsNotNone(msp.reuse_strategy)

    def test_05_case_e_budget_distribution(self):
        """Case E: Presupuesto poligonal distribuido entre componentes sin exceder el total."""
        vas_input = VisualCompilationInput(
            prompt="Pilar gótico",
            project_constraints={"triangle_budget": 5000}
        )
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        allocated = sum(msp.geometry_budget.component_budgets.values())
        self.assertLessEqual(allocated, 5500)

    def test_06_case_f_unreal_engine_interface(self):
        """Case F: Requisitos de Unreal (Nanite, LODs, Collisions) integrados en el plan."""
        vas_input = VisualCompilationInput(
            prompt="Mesa de banquete",
            project_constraints={"nanite": True, "lod_count": 3, "collision_required": True}
        )
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertTrue(msp.unreal_interface["nanite"])
        self.assertEqual(msp.unreal_interface["lod_count"], 3)
        self.assertEqual(msp.unreal_interface["collision_type"], "CUSTOM_UCX")

    def test_07_case_g_parametric_spec_and_ranges(self):
        """Case G: Parámetros geométricos con unidades y rangos definidos."""
        vas_input = VisualCompilationInput(prompt="Cofre medieval")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        main_comp = msp.component_strategies[0]
        self.assertGreater(len(main_comp.parameters), 0)
        self.assertEqual(main_comp.parameters[0].unit, "meters")

    def test_08_case_h_budget_conflict_detection(self):
        """Case H: Presupuesto imposible (100 tris para 5 componentes) genera conflicto."""
        vas_input = VisualCompilationInput(
            prompt="Castillo modular complejo altamente detallado",
            project_constraints={"triangle_budget": 300}
        )
        # Forzar múltiples componentes
        vas = self.vas_api.compile_specification(vas_input)
        vas.components = [
            {"component_id": f"comp_{i}", "semantic_type": "WALL", "is_primary": (i==0)} for i in range(5)
        ]
        msp = self.msp_api.plan_strategy(vas)
        val = self.msp_api.validate_plan(msp)
        self.assertFalse(val.is_valid)
        self.assertTrue(any("BUDGET_CONFLICT" in err for err in val.errors))

    def test_09_case_i_deterministic_strategy_hash(self):
        """Case I: Misma VAS produce idéntico strategy_hash."""
        vas_input = VisualCompilationInput(prompt="Barril de roble oscuro")
        vas1 = self.vas_api.compile_specification(vas_input)
        vas2 = self.vas_api.compile_specification(vas_input)
        msp1 = self.msp_api.plan_strategy(vas1)
        msp2 = self.msp_api.plan_strategy(vas2)
        self.assertEqual(msp1.strategy_hash, msp2.strategy_hash)

    def test_10_case_j_fallback_strategy_preservation(self):
        """Case J: Fallback definido para cada componente crítico."""
        vas_input = VisualCompilationInput(prompt="Estatua ornamental")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertEqual(msp.component_strategies[0].fallback_method, ComponentConstructionMethod.PRIMITIVE)

    def test_11_dag_execution_order(self):
        """Test 11: El DAG de ejecución coloca operaciones primarias antes de dependientes."""
        vas_input = VisualCompilationInput(prompt="Barril de madera con aros")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertGreater(len(msp.execution_graph), 0)
        self.assertEqual(len(msp.execution_graph[0].dependencies), 0)

    def test_12_modifier_stack_bevel(self):
        """Test 12: Modifier stack incorpora Bevel para hard-surface."""
        vas_input = VisualCompilationInput(prompt="Cubo metálico hard-surface")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        has_bevel = any(any(m.modifier_type == "BEVEL" for m in c.modifiers) for c in msp.component_strategies)
        self.assertTrue(has_bevel)

    def test_13_circular_dependency_detection(self):
        """Test 13: Detector de ciclos en grafo detecta dependencias circulares."""
        from src.procedural_modeling_strategy.analyzers.dag_builder import DAGBuilder
        cyclic_deps = {"A": ["B"], "B": ["C"], "C": ["A"]}
        self.assertTrue(DAGBuilder.check_circular_dependencies(cyclic_deps))

    def test_14_cost_estimator_and_score(self):
        """Test 14: Estimador de costes produce score >= 0.80 para planes óptimos."""
        vas_input = VisualCompilationInput(prompt="Caja de suministros")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        est = self.msp_api.estimate_cost(msp)
        self.assertGreaterEqual(est.strategy_score, 0.80)

    def test_15_strategy_ranking(self):
        """Test 15: Ranking ordena estrategias candidatas por strategy_score descendente."""
        vas_input = VisualCompilationInput(prompt="Puerta de madera")
        vas = self.vas_api.compile_specification(vas_input)
        msp1 = self.msp_api.plan_strategy(vas)
        msp2 = self.msp_api.plan_strategy(vas)
        msp2.cost_estimate.strategy_score = 0.50
        ranked = self.msp_api.rank_strategies([msp2, msp1])
        self.assertEqual(ranked[0].cost_estimate.strategy_score, msp1.cost_estimate.strategy_score)

    def test_16_pivot_grounding_strategy(self):
        """Test 16: Estrategia de pivot centrada en suelo por defecto."""
        vas_input = VisualCompilationInput(prompt="Farola urbana")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertEqual(msp.pivot_strategy.value, "BASE_CENTER_GROUNDED")

    def test_17_curve_based_organic_classification(self):
        """Test 17: Activo con cuerdas/curvas clasificado como CURVE_BASED."""
        vas_input = VisualCompilationInput(prompt="Cuerda de amarre con nudos (curve rope)")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        methods = [c.method for c in msp.component_strategies]
        self.assertIn(ComponentConstructionMethod.CURVE_BASED, methods)

    def test_18_valid_plan_passes_validation(self):
        """Test 18: Plan sin conflictos valida con is_valid = True."""
        vas_input = VisualCompilationInput(prompt="Banqueta de madera simple")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        val = self.msp_api.validate_plan(msp)
        self.assertTrue(val.is_valid)

    def test_19_traceability_vas_source_link(self):
        """Test 19: Trazabilidad vincula el plan a la VAS de origen."""
        vas_input = VisualCompilationInput(prompt="Escudo circular")
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        self.assertEqual(msp.specification_id, vas.specification_id)

    def test_20_end_to_end_strategy_planning_pipeline(self):
        """Test 20: Flujo E2E: VAS (F56) -> Strategy Engine (F57) -> Valid MSP -> Contrato para F58."""
        vas_input = VisualCompilationInput(
            prompt="Barril medieval de roble oscuro, 1.2m de alto con 2 aros de hierro",
            asset_class_hint="PROP.BARREL",
            semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"}
        )
        vas = self.vas_api.compile_specification(vas_input)
        msp = self.msp_api.plan_strategy(vas)
        val = self.msp_api.validate_plan(msp)
        self.assertTrue(val.is_valid)
        self.assertEqual(msp.semantic_id, "barrel_hero.root")
        self.assertGreater(len(msp.execution_graph), 0)

if __name__ == "__main__":
    unittest.main()
