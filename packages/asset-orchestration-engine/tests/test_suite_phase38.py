import sys
import os
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.orchestration_runtime import (
    OrchestrationAPI, RuntimeTaskStatus, RuntimeTaskType, RuntimePriority,
    RuntimeLockType, AgentState, ExecutionState
)

class TestOrchestrationRuntimePhase38(unittest.TestCase):
    def setUp(self):
        self.api = OrchestrationAPI()
        self.api.register_agent("BlenderAgent", capabilities=["build_geometry", "modify_geometry"], permissions=["READ", "EXECUTE"])
        self.api.register_agent("CriticAgent", capabilities=["analyze", "critique"], permissions=["READ", "PLAN"])

    def test_01_acceptance_1_basic_workflow_state_transitions(self):
        """Acceptance Test 1: Ciclo completo de estados de una tarea hasta COMPLETED."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        self.assertEqual(task.status, RuntimeTaskStatus.CREATED)

        self.api.transition_task(task.task_id, RuntimeTaskStatus.QUEUED)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.PLANNING)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.READY)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.RUNNING)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.VALIDATING)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.COMPLETED)
        self.assertEqual(task.status, RuntimeTaskStatus.COMPLETED)

    def test_02_acceptance_2_invalid_state_transition(self):
        """Acceptance Test 2: Transición inválida COMPLETED -> RUNNING lanza error."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.QUEUED)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.READY)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.RUNNING)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.VALIDATING)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.COMPLETED)

        with self.assertRaises(ValueError) as ctx:
            self.api.transition_task(task.task_id, RuntimeTaskStatus.RUNNING)
        self.assertIn("INVALID_STATE_TRANSITION", str(ctx.exception))

    def test_03_acceptance_3_mcp_timeout_handling(self):
        """Acceptance Test 3: Timeout en MCP lanza TimeoutError y captura evento sin corromper el runtime."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        with self.assertRaises(TimeoutError) as ctx:
            self.api.execute_operation(
                task_id=task.task_id,
                operation="CREATE_OBJECT",
                agent_id="BlenderAgent",
                asset_id="HOUSE_001",
                parameters={"object_name": "roof"},
                idempotency_key="KEY_TIMEOUT_1",
                simulated_timeout=True
            )
        self.assertIn("MCP_TIMEOUT", str(ctx.exception))

    def test_04_acceptance_4_concurrent_modification_lock_conflict(self):
        """Acceptance Test 4: Bloqueo exclusivo impide que dos tareas modifiquen el mismo asset simultáneamente."""
        self.api.acquire_lock("ASSET_HOUSE_001", "TASK_001", RuntimeLockType.EXCLUSIVE)
        with self.assertRaises(RuntimeError) as ctx:
            self.api.acquire_lock("ASSET_HOUSE_001", "TASK_002", RuntimeLockType.EXCLUSIVE)
        self.assertIn("LOCK_CONFLICT", str(ctx.exception))

    def test_05_acceptance_5_parallel_execution_different_assets(self):
        """Acceptance Test 5: Activos diferentes permiten bloqueos y ejecución paralela."""
        lease1 = self.api.acquire_lock("ASSET_HOUSE_001", "TASK_001", RuntimeLockType.EXCLUSIVE)
        lease2 = self.api.acquire_lock("ASSET_HOUSE_002", "TASK_002", RuntimeLockType.EXCLUSIVE)
        self.assertIsNotNone(lease1)
        self.assertIsNotNone(lease2)

    def test_06_acceptance_6_agent_offline_detection(self):
        """Acceptance Test 6: Agente sin latido por más de 10s pasa a estado OFFLINE."""
        ag = self.api.agent_manager.agents["BlenderAgent"]
        ag.last_heartbeat = time.time() - 20.0
        state = self.api.agent_manager.check_agent_health("BlenderAgent", timeout_seconds=10.0)
        self.assertEqual(state, AgentState.OFFLINE)

    def test_07_acceptance_7_missing_capability_plan_invalid(self):
        """Acceptance Test 7: Agente sin capability requerida genera PLAN_INVALID."""
        with self.assertRaises(ValueError) as ctx:
            self.api.agent_manager.verify_capabilities("BlenderAgent", ["unreal_nanite_bake"])
        self.assertIn("PLAN_INVALID", str(ctx.exception))

    def test_08_acceptance_8_agent_hallucination_state_verification(self):
        """Acceptance Test 8: Verificación empírica detecta si el agente declara un objeto inexistente."""
        with self.assertRaises(RuntimeError) as ctx:
            self.api.verify_claimed_state("HOUSE_001", "roof_geometry")
        self.assertIn("AGENT_RESULT_MISMATCH", str(ctx.exception))

    def test_09_acceptance_9_task_cancellation_and_lock_release(self):
        """Acceptance Test 9: Cancelación de tarea y liberación de locks."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        self.api.acquire_lock("ASSET_HOUSE_001", task.task_id)
        self.api.release_lock("ASSET_HOUSE_001", task.task_id)
        self.api.transition_task(task.task_id, RuntimeTaskStatus.CANCELLED)
        self.assertEqual(task.status, RuntimeTaskStatus.CANCELLED)

    def test_10_acceptance_10_dependency_failure_blocks_task(self):
        """Acceptance Test 10: Falla en dependencia marca la tarea dependiente como BLOCKED."""
        t_a = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        t_b = self.api.create_task("HOUSE_001", RuntimeTaskType.MODIFY_ASSET, dependencies=[t_a.task_id])
        self.api.task_queue.push(t_b)
        ready = self.api.task_queue.pop_ready(completed_task_ids=[], failed_task_ids=[t_a.task_id])
        self.assertIsNone(ready)
        self.assertEqual(t_b.status, RuntimeTaskStatus.BLOCKED)

    def test_11_acceptance_11_event_replay(self):
        """Acceptance Test 11: Reconstrucción de historial de eventos mediante replay."""
        self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        events = self.api.replay_events()
        self.assertGreaterEqual(len(events), 1)

    def test_12_acceptance_12_workflow_resume(self):
        """Acceptance Test 12: Reanudar workflow sin repetir pasos completados."""
        wf = self.api.workflow_engine.create_asset_workflow("HOUSE_001")
        self.api.workflow_engine.advance_workflow(wf.workflow_id) # Step 1 (Analyze)
        self.api.workflow_engine.advance_workflow(wf.workflow_id) # Step 2 (Build)
        resumed_step = self.api.workflow_engine.resume_workflow(wf.workflow_id)
        self.assertEqual(resumed_step.step_id, "STEP_3_VALIDATE")

    def test_13_acceptance_13_idempotent_execution(self):
        """Acceptance Test 13: Ejecución idempotente con la misma clave no duplica objetos en escena."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        u1 = self.api.execute_operation(task.task_id, "CREATE_OBJECT", "BlenderAgent", "HOUSE_001", {"object_name": "wall_mesh"}, "IDEMP_KEY_99")
        u2 = self.api.execute_operation(task.task_id, "CREATE_OBJECT", "BlenderAgent", "HOUSE_001", {"object_name": "wall_mesh"}, "IDEMP_KEY_99")
        self.assertEqual(u1.result, u2.result)
        objects = self.api.mcp_adapter.query_scene("HOUSE_001")
        self.assertEqual(len(objects), 1)

    def test_14_acceptance_14_approval_queue(self):
        """Acceptance Test 14: Operación de borrado requiere aprobación humana."""
        status = self.api.request_approval("DELETE_ASSET", "HOUSE_001", "User requested deletion")
        self.assertEqual(status, "PENDING_APPROVAL")

    def test_15_acceptance_15_permission_firewall(self):
        """Acceptance Test 15: CriticAgent intentando ejecutar acción EXECUTE es bloqueado."""
        task = self.api.create_task("HOUSE_001", RuntimeTaskType.CREATE_ASSET)
        with self.assertRaises(PermissionError) as ctx:
            self.api.execute_operation(task.task_id, "CREATE_OBJECT", "CriticAgent", "HOUSE_001", {"object_name": "roof"}, "IDEMP_KEY_CRITIC")
        self.assertIn("PERMISSION_DENIED", str(ctx.exception))

    def test_16_acceptance_16_deadlock_detection(self):
        """Acceptance Test 16: Dependencia circular de locks es detectada inmediatamente."""
        self.api.acquire_lock("RES_A", "TASK_A")
        self.api.acquire_lock("RES_B", "TASK_B")
        
        # Simular intento cruzado
        self.api.lock_manager.wait_graph["TASK_A"] = "TASK_B"
        with self.assertRaises(RuntimeError) as ctx:
            self.api.acquire_lock("RES_A", "TASK_B")
        self.assertIn("DEADLOCK_DETECTED", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
