import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generation_strategy_engine import (
    GenerationStrategyAPI, GenerationStrategyType,
    AssetComplexityLevel, StrategyFailureCategory,
    GenerationStageType
)

class TestGenerationStrategyPhase52(unittest.TestCase):
    def setUp(self):
        self.api = GenerationStrategyAPI()

    def test_01_mandatory_case_1_single_barrel_scripted_modeling(self):
        """Mandatory Case 1: Barril individual estilizado selecciona SCRIPTED_MODELING por su alta editabilidad."""
        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2,
            batch_size=1,
            expected_frequent_revisions=True
        )
        self.assertEqual(strat, GenerationStrategyType.SCRIPTED_MODELING)
        self.assertEqual(record.chosen_strategy, GenerationStrategyType.SCRIPTED_MODELING)

    def test_02_mandatory_case_2_batch_100_barrels_procedural(self):
        """Mandatory Case 2: Lote de 100 barriles cambia estrategia a PROCEDURAL_GENERATION."""
        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2,
            batch_size=100
        )
        self.assertEqual(strat, GenerationStrategyType.PROCEDURAL_GENERATION)

    def test_03_mandatory_case_3_modular_village_component_assembly(self):
        """Mandatory Case 3: Aldea modular / casas selecciona COMPONENT_ASSEMBLY."""
        strat, record = self.api.select_strategy(
            asset_class="BUILDING.HOUSE",
            components_count=6,
            batch_size=1
        )
        self.assertEqual(strat, GenerationStrategyType.COMPONENT_ASSEMBLY)

    def test_04_mandatory_case_4_existing_asset_modification_reuse(self):
        """Mandatory Case 4: Activo existente con alta similitud selecciona EXISTING_ASSET_MODIFICATION."""
        library = {
            "approved_house_01": {
                "asset_class": "BUILDING.HOUSE",
                "status": "APPROVED",
                "similarity": 0.94
            }
        }
        strat, record = self.api.select_strategy(
            asset_class="BUILDING.HOUSE",
            components_count=6,
            existing_library=library,
            intent_type="MODIFY"
        )
        self.assertEqual(strat, GenerationStrategyType.EXISTING_ASSET_MODIFICATION)

    def test_05_mandatory_case_5_structural_identity_failure_strategy_shift(self):
        """Mandatory Case 5: Fallo de identidad estructural permite cambio de estrategia a Geometry Nodes."""
        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2,
            force_strategy=GenerationStrategyType.GEOMETRY_NODES
        )
        self.assertEqual(strat, GenerationStrategyType.GEOMETRY_NODES)

    def test_06_mandatory_case_6_blacklist_and_fallback_on_topology_errors(self):
        """Mandatory Case 6: Fallos repetidos de topología meten en blacklist y activan fallback a GEOMETRY_NODES."""
        self.api.record_failure("PROP.BARREL", GenerationStrategyType.SCRIPTED_MODELING, StrategyFailureCategory.TOPOLOGY_ERROR)
        self.api.record_failure("PROP.BARREL", GenerationStrategyType.SCRIPTED_MODELING, StrategyFailureCategory.TOPOLOGY_ERROR)

        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2
        )
        self.assertEqual(strat, GenerationStrategyType.GEOMETRY_NODES)
        self.assertIn("blacklisted", record.reason)

    def test_07_mandatory_case_7_primitive_composition_rework_penalty(self):
        """Mandatory Case 7: Pobre editabilidad de primitivas sufre penalización de rework frente a Scripted Modeling."""
        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2,
            expected_frequent_revisions=True
        )
        scores = record.candidate_scores
        self.assertGreater(scores["SCRIPTED_MODELING"], scores["PRIMITIVE_COMPOSITION"])

    def test_08_mandatory_case_8_human_override_honored(self):
        """Mandatory Case 8: Override humano forzado es respetado."""
        strat, record = self.api.select_strategy(
            asset_class="PROP.BARREL",
            components_count=2,
            force_strategy=GenerationStrategyType.GEOMETRY_NODES
        )
        self.assertEqual(strat, GenerationStrategyType.GEOMETRY_NODES)
        self.assertTrue(record.override_applied)

    def test_09_mandatory_case_9_progressive_generation_plan_stages(self):
        """Mandatory Case 9: Plan progresivo contiene las 6 etapas ordenadas."""
        plan = self.api.build_plan(
            specification_id="SPEC_BARREL_01",
            selected_strategy=GenerationStrategyType.SCRIPTED_MODELING,
            parameters={"height": 1.5, "rings": 2}
        )
        self.assertEqual(len(plan.stages), 6)
        self.assertEqual(plan.stages[0].stage_type, GenerationStageType.BLOCKOUT)
        self.assertEqual(plan.stages[-1].stage_type, GenerationStageType.VALIDATION)

    def test_10_mandatory_case_10_deterministic_seed_generation(self):
        """Mandatory Case 10: Semilla determinista fijada en el plan."""
        plan = self.api.build_plan(
            specification_id="SPEC_BARREL_01",
            selected_strategy=GenerationStrategyType.SCRIPTED_MODELING,
            parameters={},
            seed=42
        )
        self.assertEqual(plan.seed, 42)
        self.assertTrue(plan.is_deterministic)

    def test_11_registry_contains_standards(self):
        """Test 11: El registro contiene las estrategias estándar."""
        strategies = self.api.selector.registry.list_strategies()
        self.assertGreaterEqual(len(strategies), 6)

    def test_12_complexity_analyzer_modular_building(self):
        """Test 12: Complejidad para edificios modularizados."""
        from src.generation_strategy_engine.analyzers.complexity_analyzer import AssetComplexityAnalyzer
        rep = AssetComplexityAnalyzer.analyze("BUILDING.HOUSE", 6)
        self.assertEqual(rep.complexity_level, AssetComplexityLevel.HIGHLY_MODULAR)

    def test_13_complexity_analyzer_organic_character(self):
        """Test 13: Complejidad para personajes orgánicos."""
        from src.generation_strategy_engine.analyzers.complexity_analyzer import AssetComplexityAnalyzer
        rep = AssetComplexityAnalyzer.analyze("CHARACTER.HERO", 4)
        self.assertEqual(rep.complexity_level, AssetComplexityLevel.ORGANIC)

    def test_14_reuse_analyzer_no_match(self):
        """Test 14: ReuseAnalyzer devuelve FULL_GENERATION si no hay coincidencias."""
        from src.generation_strategy_engine.analyzers.reuse_analyzer import ReuseAnalyzer
        rep = ReuseAnalyzer.analyze_reuse("PROP.BARREL", {})
        self.assertFalse(rep.has_match)
        self.assertEqual(rep.recommended_action, "FULL_GENERATION")

    def test_15_decision_record_candidate_scores(self):
        """Test 15: DecisionRecord almacena puntuaciones de candidatos."""
        strat, record = self.api.select_strategy("PROP.BARREL", 2)
        self.assertIn("SCRIPTED_MODELING", record.candidate_scores)

    def test_16_generation_plan_fallback_configured(self):
        """Test 16: Plan de generación incluye fallback strategy configurada."""
        plan = self.api.build_plan("SPEC_01", GenerationStrategyType.SCRIPTED_MODELING, {})
        self.assertEqual(plan.fallback_strategy, GenerationStrategyType.GEOMETRY_NODES)

    def test_17_stage_quality_gates(self):
        """Test 17: Quality gates fijados en la etapa de blockout."""
        plan = self.api.build_plan("SPEC_01", GenerationStrategyType.SCRIPTED_MODELING, {})
        self.assertEqual(plan.stages[0].quality_gates.get("silhouette"), 0.80)

    def test_18_scripted_modeling_high_editability(self):
        """Test 18: Scripted Modeling cuenta con editability_score >= 0.90."""
        st = self.api.selector.registry.get_strategy(GenerationStrategyType.SCRIPTED_MODELING)
        self.assertGreaterEqual(st.editability_score, 0.90)

    def test_19_existing_asset_modification_cost(self):
        """Test 19: Existing asset modification cuenta con el menor coste base."""
        st = self.api.selector.registry.get_strategy(GenerationStrategyType.EXISTING_ASSET_MODIFICATION)
        self.assertEqual(st.base_cost, 0.5)

    def test_20_end_to_end_strategy_engine_handshake(self):
        """Test 20: Flujo E2E: CompiledSpec -> StrategySelector -> DecisionRecord -> GenerationPlan."""
        strat, record = self.api.select_strategy("PROP.BARREL", 2)
        plan = self.api.build_plan("SPEC_END2END", strat, {"height": 1.5, "radius": 0.6})
        self.assertEqual(plan.selected_strategy, GenerationStrategyType.SCRIPTED_MODELING)
        self.assertEqual(len(plan.stages), 6)
        self.assertEqual(plan.parameters["height"], 1.5)

if __name__ == "__main__":
    unittest.main()
