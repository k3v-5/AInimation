import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    UnrealEngine, GameplayEngine, AIPlanningAPI, PlanOptimizer,
    PlannedTask, DestructiveOperationGuard, RiskLevel
)

class TestAIPlanningPhase9(unittest.TestCase):
    def setUp(self):
        self.ue = UnrealEngine("Planning_Level")
        self.gp = GameplayEngine()
        self.planner = AIPlanningAPI(self.ue, self.gp, max_mcp_calls_budget=10)

        # Actores estándar
        self.sword = self.ue.spawn_actor("sword_001", "Sword_Actor", tags=["Weapon"], actor_id="actor_sword_01")
        self.gp.set_gameplay_data("actor_sword_01", "damage", 25.0)

    def test_01_no_rebuild_minimal_plan(self):
        """Test 1: No Rebuild - Cambiar daño a 40 ejecuta 1 modificación de dato sin reconstruir nada."""
        res = self.planner.process_request("Haz que la espada haga 40 de daño", context_target="actor_sword_01")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "COMPLETED")
        self.assertEqual(self.gp.actor_data["actor_sword_01"].get_effective("damage"), 40.0)

    def test_02_noop_detection(self):
        """Test 2: NO_OP - Cambiar daño a 25 cuando ya es 25 produce NO_OP sin llamadas MCP."""
        res = self.planner.process_request("Haz que la espada haga 25 de daño", context_target="actor_sword_01")
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_OP")
        self.assertEqual(res["mcp_calls"], 0)

    def test_03_ambiguous_target_detection(self):
        """Test 3: Ambiguous Target - 2 espadas en escena sin target explícito produce AMBIGUOUS_TARGET."""
        self.ue.spawn_actor("sword_001", "Sword_Actor_2", tags=["Weapon"], actor_id="actor_sword_02")
        res = self.planner.process_request("Haz la espada roja")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "AMBIGUOUS_TARGET")

    def test_04_scope_enforcement(self):
        """Test 4: Scope - Modificar actor objetivo no altera otros actores."""
        self.ue.spawn_actor("sword_001", "Sword_Actor_2", tags=["Weapon"], actor_id="actor_sword_02")
        self.gp.set_gameplay_data("actor_sword_02", "damage", 25.0)
        res = self.planner.process_request("Haz que la espada haga 40 de daño", context_target="actor_sword_01")
        self.assertTrue(res["success"])
        self.assertEqual(self.gp.actor_data["actor_sword_01"].get_effective("damage"), 40.0)
        self.assertEqual(self.gp.actor_data["actor_sword_02"].get_effective("damage"), 25.0)

    def test_05_failure_loop_repair_limit(self):
        """Test 5: Repair limit - Operación fallida se detiene tras 2 intentos con REPAIR_LIMIT_REACHED."""
        from src.ai_planning.tasks.task_graph import TaskGraph, PlannedTask
        graph = TaskGraph()
        graph.add_task(PlannedTask("f_task", "FAIL_SIMULATION", "target"))
        res = self.planner.executor.execute_plan(graph)
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "REPAIR_LIMIT_REACHED")
        self.assertEqual(res["attempts"], 3) # Intento inicial + 2 reparaciones = 3

    def test_06_existing_capability_reuse(self):
        """Test 6: Existing capability reuse - Re-agregar PICKUP no duplica componentes."""
        self.gp.add_capability("actor_sword_01", "PICKUP")
        res = self.planner.process_request("Haz que la espada se pueda recoger", context_target="actor_sword_01")
        self.assertTrue(res["success"])

    def test_07_stop_on_goal_reached(self):
        """Test 7: Stop rule - Al completar el plan se activa stop_rule_triggered = True."""
        res = self.planner.process_request("Haz que la espada haga 40 de daño", context_target="actor_sword_01")
        self.assertTrue(res["stop_rule_triggered"])

    def test_08_mcp_call_budget_exceeded(self):
        """Test 8: MCP Budget - Plan que excede presupuesto es bloqueado con PLAN_EXCEEDS_BUDGET."""
        strict_planner = AIPlanningAPI(self.ue, self.gp, max_mcp_calls_budget=0)
        res = strict_planner.process_request("Haz que la espada se pueda recoger y equipar", context_target="actor_sword_01")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "PLAN_EXCEEDS_BUDGET")

    def test_09_destructive_operation_guard(self):
        """Test 9: Destructive Guard - Borrar todas las espadas requiere confirmación crítica."""
        res = self.planner.process_request("Elimina todas las espadas", context_target="actor_sword_01")
        self.assertFalse(res["success"])
        self.assertEqual(res["error_code"], "CRITICAL_RISK_CONFIRMATION_REQUIRED")

    def test_10_composite_intent_decomposition(self):
        """Test 10: Composite Intent - 'recoger y equipar' se descompone en 2 tareas."""
        res = self.planner.process_request("Haz que la espada se pueda recoger y equipar", context_target="actor_sword_01")
        self.assertTrue(res["success"])
        self.assertGreaterEqual(res["tasks_count"], 2)

    def test_11_operation_folding(self):
        """Test 11: Operation Folding - 3 traslaciones consecutivas se pliegan en 1 única operación."""
        t1 = PlannedTask("t1", "MOVE_ACTOR", "sword", {"delta": (10.0, 0.0, 0.0)})
        t2 = PlannedTask("t2", "MOVE_ACTOR", "sword", {"delta": (20.0, 0.0, 0.0)})
        t3 = PlannedTask("t3", "MOVE_ACTOR", "sword", {"delta": (30.0, 0.0, 0.0)})
        folded = PlanOptimizer.optimize_tasks([t1, t2, t3])
        self.assertEqual(len(folded), 1)
        self.assertEqual(folded[0].parameters["delta"], (60.0, 0.0, 0.0))

    def test_12_idempotency_request_id(self):
        """Test 12: Idempotency - Mismo request_id devuelve DUPLICATE_REQUEST con resultado en caché."""
        res1 = self.planner.process_request("Haz que la espada haga 50 de daño", context_target="actor_sword_01", request_id="fixed_req_100")
        res2 = self.planner.process_request("Haz que la espada haga 50 de daño", context_target="actor_sword_01", request_id="fixed_req_100")
        self.assertTrue(res2["success"])
        self.assertEqual(res2["status"], "DUPLICATE_REQUEST")

    def test_13_dry_run_mode(self):
        """Test 13: Dry run - dry_run=True retorna el plan sin mutar el dato real."""
        res = self.planner.process_request("Haz que la espada haga 99 de daño", context_target="actor_sword_01", dry_run=True)
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        self.assertEqual(self.gp.actor_data["actor_sword_01"].get_effective("damage"), 25.0)

    def test_14_risk_classification(self):
        """Test 14: Risk classification - Clasificación correcta de niveles de riesgo."""
        self.assertEqual(DestructiveOperationGuard.classify_risk("MOVE_ACTOR"), RiskLevel.LOW)
        self.assertEqual(DestructiveOperationGuard.classify_risk("MAKE_PICKABLE"), RiskLevel.MEDIUM)
        self.assertEqual(DestructiveOperationGuard.classify_risk("DELETE_ACTOR"), RiskLevel.HIGH)
        self.assertEqual(DestructiveOperationGuard.classify_risk("CLEAR_LEVEL"), RiskLevel.CRITICAL)

if __name__ == "__main__":
    unittest.main()
