import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_compiler_task_graph import (
    IntentCompilerAPI, PreflightStatus, TaskGraphDAG, TaskGraphNode,
    ExecutionPlanStep
)

class TestIntentCompilerTaskGraphPhase39(unittest.TestCase):
    def setUp(self):
        self.api = IntentCompilerAPI()

    def test_01_acceptance_1_structured_extraction(self):
        """Acceptance Test 1: Extracción estructurada de tipo, estilo y conteo de ventanas."""
        intent = self.api.compile_intent("Casa medieval con 4 ventanas y una puerta")
        req_keys = {r.key: r.value for r in intent.requirements}
        self.assertEqual(req_keys.get("asset_type"), "HOUSE")
        self.assertEqual(req_keys.get("style"), "MEDIEVAL")
        self.assertEqual(req_keys.get("window_count"), 4)
        self.assertEqual(req_keys.get("door_count"), 1)

    def test_02_acceptance_2_reference_masking_target_vs_context(self):
        """Acceptance Test 5: Separación de target (edificio), context (árboles) e ignore (cielo)."""
        intent = self.api.compile_intent("Recrea la casa de la imagen")
        self.assertIn("building", intent.target_mask.target)
        self.assertIn("trees", intent.target_mask.context)
        self.assertIn("sky", intent.target_mask.ignore)

    def test_03_acceptance_3_blocking_conflict_detection(self):
        """Acceptance Test 6: 'Casa grande pero de máximo 3 metros' genera BLOCKING_CONFLICT."""
        intent = self.api.compile_intent("Casa grande pero de max 3m")
        self.assertEqual(intent.preflight_status, PreflightStatus.BLOCKING_CONFLICT)

    def test_04_acceptance_4_semantic_conflict_needs_clarification(self):
        """Acceptance Test 7: 'Casa medieval con ventanas futuristas' genera advertencia y NEEDS_CLARIFICATION."""
        intent = self.api.compile_intent("Casa medieval con detalles y ventanas futuristas")
        self.assertEqual(intent.preflight_status, PreflightStatus.NEEDS_CLARIFICATION)
        self.assertIsNotNone(intent.clarification_request)

    def test_05_acceptance_5_unspecified_reference_clarification(self):
        """Acceptance Test 8: 'Hazla como la imagen' sin scope genera NEEDS_CLARIFICATION."""
        intent = self.api.compile_intent("Hazla como la imagen")
        self.assertEqual(intent.preflight_status, PreflightStatus.NEEDS_CLARIFICATION)
        self.assertTrue(intent.clarification_request.blocking)

    def test_06_acceptance_6_intent_drift_detection(self):
        """Acceptance Test 9: Plan que introduce elementos modernos en intento medieval genera INTENT_DRIFT_DETECTED."""
        intent = self.api.compile_intent("Casa medieval con muros de piedra")
        bad_steps = [
            ExecutionPlanStep("S1", "HOUSE.WINDOWS", "BUILD_OPENINGS", {"window_type": "modern_windows"})
        ]
        with self.assertRaises(ValueError) as ctx:
            self.api.detect_intent_drift(intent, bad_steps)
        self.assertIn("INTENT_DRIFT_DETECTED", str(ctx.exception))

    def test_07_acceptance_7_incremental_replan_roof_scope(self):
        """Acceptance Test 10: Modificar la altura del tejado solo afecta al subgrafo de tejado, materiales y validación."""
        delta = self.api.replan_delta(target="HOUSE.ROOF", property_name="height", old_val=1.8, new_val=1.2)
        self.assertEqual(delta.affected_subgraph, ["T_ROOF", "T_MATERIALS", "T_VALIDATE"])

    def test_08_acceptance_8_unimplemented_requirement_validation(self):
        """Acceptance Test 11: Requisito HARD sin tarea productora en el DAG genera UNIMPLEMENTED_REQUIREMENT."""
        intent = self.api.compile_intent("Casa medieval con 4 ventanas")
        # DAG sin nodo de aberturas
        bad_dag = TaskGraphDAG(graph_id="DAG_INCOMPLETE", nodes={
            "T_DIM": TaskGraphNode("T_DIM", "Dimensions", produces=["footprint"]),
            "T_WALLS": TaskGraphNode("T_WALLS", "Walls", produces=["walls", "roof"])
        })
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_graph(bad_dag, intent)
        self.assertIn("UNIMPLEMENTED_REQUIREMENT", str(ctx.exception))

    def test_09_acceptance_9_unsupported_capability_rejection(self):
        """Acceptance Test 12: Tarea que requiere capability no disponible genera UNSUPPORTED."""
        intent = self.api.compile_intent("Casa medieval con 4 ventanas")
        dag = self.api.build_task_graph(intent)
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_graph(dag, intent, available_capabilities=["only_read_capability"])
        self.assertIn("UNSUPPORTED", str(ctx.exception))

    def test_10_acceptance_10_constraint_parameter_propagation(self):
        """Acceptance Test 13: Propagación de parámetros (5m altura x 0.35 ratio = 1.75m techo)."""
        intent = self.api.compile_intent("Casa medieval de piedra con 4 ventanas")
        dag = self.api.build_task_graph(intent)
        steps = self.api.compile_plan(dag, intent)
        roof_step = next(s for s in steps if s.step_id == "STEP_3_ROOF")
        self.assertEqual(roof_step.parameters["calculated_height"], 1.75)

    def test_11_acceptance_11_exclusion_rules(self):
        """Acceptance Test 14: Intento medieval incluye exclusiones para elementos modernos."""
        intent = self.api.compile_intent("Casa medieval rústica")
        self.assertTrue(any("MODERN" in e.exclusion_id for e in intent.exclusions))

    def test_12_acceptance_12_material_strategy_update(self):
        """Acceptance Test 15: Cambio de material a piedra afecta únicamente al subgrafo de materiales."""
        delta = self.api.replan_delta(target="HOUSE.MATERIAL", property_name="texture", old_val="WOOD", new_val="STONE")
        self.assertEqual(delta.affected_subgraph, ["T_MATERIALS", "T_VALIDATE"])

    def test_13_acceptance_13_tower_structural_transformation(self):
        """Acceptance Test 16: Transformación a torre afecta muros, techo y aberturas."""
        delta = self.api.replan_delta(target="HOUSE.STRUCTURE.TOWER", property_name="archetype", old_val="HOUSE", new_val="TOWER")
        self.assertIn("T_WALLS", delta.affected_subgraph)
        self.assertIn("T_ROOF", delta.affected_subgraph)

    def test_14_acceptance_14_dag_cycle_detection(self):
        """Acceptance Test 17: Detección de ciclos en el grafo DAG lanza DAG_CYCLE_DETECTED."""
        intent = self.api.compile_intent("Casa medieval")
        cyclic_dag = TaskGraphDAG(graph_id="DAG_CYCLE", nodes={
            "A": TaskGraphNode("A", "Node A", requires=["B"]),
            "B": TaskGraphNode("B", "Node B", requires=["A"])
        })
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_graph(cyclic_dag, intent)
        self.assertIn("DAG_CYCLE_DETECTED", str(ctx.exception))

    def test_15_acceptance_15_preflight_ready(self):
        """Acceptance Test 18: Petición clara y completa pasa preflight como READY."""
        intent = self.api.compile_intent("Casa medieval de piedra y madera con 4 ventanas, tejado inclinado y una puerta")
        self.assertEqual(intent.preflight_status, PreflightStatus.READY)
        self.assertGreaterEqual(intent.confidence, 0.90)

    def test_16_acceptance_16_equivalent_compilation_reproducibility(self):
        """Acceptance Test 19: Misma petición produce la misma lista de requerimientos."""
        i1 = self.api.compile_intent("Casa medieval con 4 ventanas")
        i2 = self.api.compile_intent("Casa medieval con 4 ventanas")
        self.assertEqual(len(i1.requirements), len(i2.requirements))

    def test_17_acceptance_17_equivalent_dag_generation(self):
        """Acceptance Test 20: Mismo intento produce la misma estructura de DAG."""
        intent = self.api.compile_intent("Casa medieval con 4 ventanas")
        dag1 = self.api.build_task_graph(intent)
        dag2 = self.api.build_task_graph(intent)
        self.assertEqual(list(dag1.nodes.keys()), list(dag2.nodes.keys()))

    def test_18_acceptance_18_materials_extracted(self):
        """Acceptance Test 21: Extracción de materiales múltiples (piedra y madera)."""
        intent = self.api.compile_intent("Casa de piedra y madera")
        mat_req = next(r for r in intent.requirements if r.key == "materials")
        self.assertIn("STONE", mat_req.value)
        self.assertIn("TIMBER", mat_req.value)

    def test_19_acceptance_19_plan_steps_count(self):
        """Acceptance Test 22: Plan compilado genera 6 pasos canónicos con validación final."""
        intent = self.api.compile_intent("Casa medieval con 4 ventanas y puerta")
        dag = self.api.build_task_graph(intent)
        steps = self.api.compile_plan(dag, intent)
        self.assertEqual(len(steps), 6)
        self.assertEqual(steps[-1].operation, "VALIDATE_QUALITY")

    def test_20_acceptance_20_door_scope_replan(self):
        """Acceptance Test 23: Modificar solo la puerta no afecta al subgrafo de muros o tejado."""
        delta = self.api.replan_delta(target="HOUSE.DOOR", property_name="width", old_val=0.90, new_val=1.20)
        self.assertEqual(delta.affected_subgraph, ["T_OPENINGS", "T_MATERIALS", "T_VALIDATE"])

if __name__ == "__main__":
    unittest.main()
