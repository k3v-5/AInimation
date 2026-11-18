import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    BuildOrchestratorAPI, OrchestratorConfig, TaskManager, TaskState,
    AssetLockManager, LockType, CheckpointManager, ReworkDetector,
    CorrectionAgent, AgentRegistry
)

class TestBuildOrchestratorPhase30(unittest.TestCase):
    def setUp(self):
        self.config = OrchestratorConfig(max_attempts_per_task=3)
        self.api = BuildOrchestratorAPI(self.config)

    def test_01_full_orchestrated_build_scenario_201(self):
        """Test 1: Scenario 201 - Construcción orquestada completa de casa medieval."""
        params = {"width": 4.0, "height": 5.0, "door_width": 0.90}
        report = self.api.run_orchestrated_build("medieval_house_01", params)
        self.assertTrue(report.is_approved)
        self.assertEqual(report.status, "APPROVED")
        self.assertEqual(report.tasks_executed, 4)
        self.assertIn("COMMIT: Asset passed all QA validations", report.execution_logs[-1])

    def test_02_surgical_subtree_correction_scenario_202(self):
        """Test 2: Scenario 202 - DOOR_TOO_NARROW modifica únicamente door_width sin tocar paredes/techo."""
        params = {"width": 4.0, "height": 5.0, "door_width": 0.62}
        report = self.api.run_orchestrated_build("medieval_house_narrow", params, simulated_qa_error="DOOR_TOO_NARROW")
        self.assertTrue(report.is_approved)
        self.assertEqual(report.status, "APPROVED")
        self.assertEqual(report.final_parameters["door_width"], 0.85)
        self.assertEqual(report.final_parameters["width"], 4.0) # Paredes intactas

    def test_03_anti_rework_limit_and_rollback_scenario_202(self):
        """Test 3: Scenario 202 - Fallo persistente tras 3 intentos activa ROLLBACK y detiene bucle."""
        detector = ReworkDetector(max_attempts=3)
        stop1, _ = detector.record_attempt("T_DOOR", "door_width", 0.62)
        self.assertFalse(stop1)
        stop2, _ = detector.record_attempt("T_DOOR", "door_width", 0.64)
        self.assertFalse(stop2)
        stop3, reason = detector.record_attempt("T_DOOR", "door_width", 0.66)
        self.assertTrue(stop3)
        self.assertIn("MAX_ATTEMPTS_EXCEEDED", reason)

    def test_04_oscillation_detection(self):
        """Test 4: Detección de oscilación A -> B -> A en parámetros."""
        detector = ReworkDetector(max_attempts=5)
        detector.record_attempt("T_ROOF", "roof_angle", 30.0)
        detector.record_attempt("T_ROOF", "roof_angle", 40.0)
        stop_osc, reason = detector.record_attempt("T_ROOF", "roof_angle", 30.0)
        self.assertTrue(stop_osc)
        self.assertIn("OSCILLATION_DETECTED", reason)

    def test_05_least_privilege_tool_permissions(self):
        """Test 5: Principio de menor privilegio - gameplay_qa no puede crear mallas de blender."""
        has_qa_perm = self.api.validate_tool_permission("gameplay_qa_agent", "qa.validate_door")
        self.assertTrue(has_qa_perm)
        has_blender_perm = self.api.validate_tool_permission("gameplay_qa_agent", "blender.create_mesh")
        self.assertFalse(has_blender_perm)

    def test_06_asset_lock_isolation(self):
        """Test 6: AssetLockManager previene escrituras concurrentes conflictivas."""
        lock_mgr = AssetLockManager()
        ok1 = lock_mgr.acquire_lock("house_01", "agent_A", LockType.WRITE)
        self.assertTrue(ok1)
        ok2 = lock_mgr.acquire_lock("house_01", "agent_B", LockType.EXCLUSIVE)
        self.assertFalse(ok2)
        lock_mgr.release_lock("house_01", "agent_A")
        ok3 = lock_mgr.acquire_lock("house_01", "agent_B", LockType.EXCLUSIVE)
        self.assertTrue(ok3)

    def test_07_task_dependency_enforcement(self):
        """Test 7: Tareas hijas no se ejecutan hasta que los padres estén completados."""
        tm = TaskManager()
        tm.create_task("T_WALLS", "CREATE_WALLS", "house_01")
        tm.create_task("T_ROOF", "CREATE_ROOF", "house_01")
        tm.add_dependency("T_ROOF", "T_WALLS")

        self.assertFalse(tm.can_execute_task("T_ROOF"))
        tm.transition_state("T_WALLS", TaskState.PASSED)
        self.assertTrue(tm.can_execute_task("T_ROOF"))

    def test_08_checkpoint_creation_and_restoration(self):
        """Test 8: CheckpointManager captura y restaura estado de parámetros con precisión."""
        cm = CheckpointManager()
        params = {"width": 4.0, "door_width": 0.62}
        cp = cm.create_checkpoint("cp_test_01", "house_01", params, {"T_01": TaskState.RUNNING})
        self.assertEqual(cp.parameters["door_width"], 0.62)

        restored = cm.restore_checkpoint("cp_test_01")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.parameters["door_width"], 0.62)

    def test_09_agent_capability_matching(self):
        """Test 9: AgentRegistry resuelve agente adecuado según capacidad requerida."""
        reg = AgentRegistry()
        agent = reg.find_agent_for_capability("mesh_creation")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, "blender_operator")

    def test_10_execution_report_audit_trail(self):
        """Test 10: ExecutionReport genera trazabilidad y logs de auditoría completos."""
        report = self.api.run_orchestrated_build("audit_house", {"width": 5.0})
        self.assertGreaterEqual(len(report.execution_logs), 3)
        self.assertTrue(any("CHECKPOINT" in l for l in report.execution_logs))
        self.assertTrue(any("EXECUTE" in l for l in report.execution_logs))
        self.assertTrue(any("COMMIT" in l for l in report.execution_logs))

if __name__ == "__main__":
    unittest.main()
