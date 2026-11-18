import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.multi_agent_control_plane import (
    ControlPlaneAPI, AgentRole, DecisionAction, LockType,
    Task, AgentResult, TaskState
)

class TestMultiAgentControlPlanePhase49(unittest.TestCase):
    def setUp(self):
        self.api = ControlPlaneAPI(max_mcp_calls=30)

    def test_01_mandatory_case_1_pipeline_intent_routing(self):
        """Mandatory Case 1: Intent 'Crea una casa medieval' se descompone en el pipeline estándar de 7 etapas."""
        plan = self.api.plan_user_intent("Crea una casa medieval")
        expected_pipeline = [
            AgentRole.SPECIFICATION,
            AgentRole.DEPENDENCY,
            AgentRole.BLENDER,
            AgentRole.VALIDATION,
            AgentRole.CRITIC,
            AgentRole.UNREAL,
            AgentRole.VALIDATION
        ]
        self.assertEqual(plan.agent_pipeline, expected_pipeline)
        self.assertEqual(len(plan.subtasks), 7)

    def test_02_mandatory_case_2_critic_refine_on_mediocre_score(self):
        """Mandatory Case 2: Score mediocre (0.48) dispara REFINE (corrección mínima) en vez de regenerar todo."""
        action, msg = self.api.evaluate_critic_action("TASK_HOUSE", current_score=0.48, score_history=[0.48])
        self.assertEqual(action, DecisionAction.REFINE)

    def test_03_mandatory_case_3_diminishing_returns_detection(self):
        """Mandatory Case 3: Refinamiento de 0.63 a 0.64 (Delta < 0.02) detecta rendimientos decrecientes (ESCALATE)."""
        action, msg = self.api.evaluate_critic_action("TASK_HOUSE", current_score=0.64, score_history=[0.48, 0.63])
        self.assertEqual(action, DecisionAction.ESCALATE)
        self.assertIn("DIMINISHING_RETURNS", msg)

    def test_04_mandatory_case_4_mcp_timeout_state_reconciliation(self):
        """Mandatory Case 4: Timeout de MCP consulta estado real de Blender; si el asset existe, reconcilia sin duplicar."""
        res = self.api.reconcile_mcp_timeout(
            task_id="TASK_BLENDER_EXPORT",
            expected_object_name="SM_MedievalHouse_001",
            scene_objects=["Camera", "Light", "SM_MedievalHouse_001"]
        )
        self.assertEqual(res["action"], "RECONCILE")

    def test_05_mandatory_case_5_manual_unreal_modification_drift(self):
        """Mandatory Case 5: Modificación manual en Unreal bloquea sobreescritura ciega."""
        from src.production_pipeline_unreal import ProductionPipelineAPI
        unreal_api = ProductionPipelineAPI()
        m, _ = unreal_api.process_and_export_asset("HOUSE_MANUAL_49", "1.0.0", {"width": 8.0})
        unreal_api.stage_asset_in_unreal(m)
        unreal_api.publish_asset_to_unreal("HOUSE_MANUAL_49")
        unreal_api.mark_manual_modified_in_unreal("HOUSE_MANUAL_49")

        with self.assertRaises(PermissionError):
            unreal_api.publish_asset_to_unreal("HOUSE_MANUAL_49")

    def test_06_mandatory_case_6_resource_lock_serialization(self):
        """Mandatory Case 6: Dos tareas pidiendo el mismo lock de Blender serializan el acceso con RESOURCE_LOCKED."""
        self.api.acquire_resource_lock(LockType.BLENDER, "BLENDER_GPU_0", "TASK_A")
        with self.assertRaises(BlockingIOError) as ctx:
            self.api.acquire_resource_lock(LockType.BLENDER, "BLENDER_GPU_0", "TASK_B")
        self.assertIn("RESOURCE_LOCKED", str(ctx.exception))

    def test_07_mandatory_case_7_resource_lock_release(self):
        """Mandatory Case 7: Liberación de lock permite a la siguiente tarea adquirirlo."""
        self.api.acquire_resource_lock(LockType.BLENDER, "BLENDER_GPU_1", "TASK_A")
        released = self.api.release_resource_lock(LockType.BLENDER, "BLENDER_GPU_1", "TASK_A")
        self.assertTrue(released)
        lock2 = self.api.acquire_resource_lock(LockType.BLENDER, "BLENDER_GPU_1", "TASK_B")
        self.assertEqual(lock2.owner_task_id, "TASK_B")

    def test_08_mandatory_case_8_mcp_call_budget_exhaustion(self):
        """Mandatory Case 8: Superar max_mcp_calls bloquea la tarea con BUDGET_EXCEEDED."""
        tight_api = ControlPlaneAPI(max_mcp_calls=5)
        task = Task(task_id="TASK_OVERBUDGET", intent="Heavy mesh generation")
        res = tight_api.execute_task(task, requested_mcp_calls=10)
        self.assertFalse(res.is_valid)
        self.assertIn("BUDGET_EXCEEDED", str(res.error_message))

    def test_09_mandatory_case_9_tool_guard_malformed_result(self):
        """Mandatory Case 9: Resultado malformado o vacío es rechazado con AGENT_RESULT_INVALID."""
        bad_result = AgentResult(
            task_id="TASK_BAD",
            agent_id="AGENT_BLENDER",
            status=TaskState.FAILED,
            is_valid=False,
            error_message="Syntax error in geometry"
        )
        with self.assertRaises(ValueError) as ctx:
            self.api.validate_agent_output(bad_result)
        self.assertIn("AGENT_RESULT_INVALID", str(ctx.exception))

    def test_10_mandatory_case_10_salvage_partial_outputs(self):
        """Mandatory Case 10: Fallo parcial retiene artefactos válidos (mesh, collision) y evita reinicio total."""
        artifacts = {
            "SM_House_Mesh": True,
            "UCX_House_Collision": True,
            "MI_House_Material": False # Falló material
        }
        salvage = self.api.salvage_partial_failure("TASK_FAIL", artifacts)
        self.assertEqual(salvage["retained_outputs"], ["SM_House_Mesh", "UCX_House_Collision"])
        self.assertEqual(salvage["discarded_outputs"], ["MI_House_Material"])
        self.assertEqual(salvage["recovery_action"], "REGENERATE_DISCARDED_ONLY")

    def test_11_agent_registry_eight_agents(self):
        """Test 11: Registro de los 8 agentes especializados obligatorios."""
        agents = self.api.control_plane.registry.list_agents()
        self.assertEqual(len(agents), 8)

    def test_12_planner_agent_read_only(self):
        """Test 12: PlannerAgent tiene efecto READ_ONLY."""
        from src.multi_agent_control_plane.core.control_types import ToolEffect
        ag = self.api.control_plane.registry.get_agent(AgentRole.PLANNER)
        self.assertEqual(ag.allowed_effects, [ToolEffect.READ_ONLY])

    def test_13_blender_agent_mutating(self):
        """Test 13: BlenderAgent tiene permisos MUTATING."""
        from src.multi_agent_control_plane.core.control_types import ToolEffect
        ag = self.api.control_plane.registry.get_agent(AgentRole.BLENDER)
        self.assertIn(ToolEffect.MUTATING, ag.allowed_effects)

    def test_14_recovery_agent_destructive(self):
        """Test 14: RecoveryAgent tiene permisos DESTRUCTIVE para rollback."""
        from src.multi_agent_control_plane.core.control_types import ToolEffect
        ag = self.api.control_plane.registry.get_agent(AgentRole.RECOVERY)
        self.assertIn(ToolEffect.DESTRUCTIVE, ag.allowed_effects)

    def test_15_scheduler_priority_ordering(self):
        """Test 15: Scheduler despacha tareas por prioridad."""
        sched = self.api.control_plane.scheduler
        t_low = Task(task_id="T_LOW", intent="low", priority=1)
        t_high = Task(task_id="T_HIGH", intent="high", priority=10)
        sched.enqueue(t_low)
        sched.enqueue(t_high)
        self.assertEqual(sched.dequeue().task_id, "T_HIGH")

    def test_16_critic_accept_on_high_score(self):
        """Test 16: Critic score >= 0.85 dispara ACCEPT."""
        action, _ = self.api.evaluate_critic_action("TASK_HIGH", current_score=0.92, score_history=[0.80])
        self.assertEqual(action, DecisionAction.ACCEPT)

    def test_17_critic_regenerate_on_floor_score(self):
        """Test 17: Critic score < 0.40 dispara REGENERATE."""
        action, _ = self.api.evaluate_critic_action("TASK_FLOOR", current_score=0.25, score_history=[0.25])
        self.assertEqual(action, DecisionAction.REGENERATE)

    def test_18_mcp_retry_on_missing_scene_object(self):
        """Test 18: Timeout cuando el objeto no existe en escena indica RETRY seguro."""
        res = self.api.reconcile_mcp_timeout("TASK_TIMEOUT", "SM_Ghost", ["Camera", "Light"])
        self.assertEqual(res["action"], "RETRY")

    def test_19_task_budget_normal_execution(self):
        """Test 19: Ejecución dentro de presupuesto completa la tarea exitosamente."""
        t = Task(task_id="TASK_OK", intent="Mesh creation")
        res = self.api.execute_task(t, requested_mcp_calls=3)
        self.assertTrue(res.is_valid)
        self.assertEqual(res.status, TaskState.COMPLETED)

    def test_20_end_to_end_control_plane_handshake(self):
        """Test 20: Flujo E2E: Intent -> Plan -> Subtasks -> Critic -> Reconciliación -> Finalización."""
        plan = self.api.plan_user_intent("Crea una casa medieval de piedra")
        self.assertGreaterEqual(len(plan.subtasks), 7)
        self.assertEqual(plan.agent_pipeline[0], AgentRole.SPECIFICATION)
        self.assertEqual(plan.agent_pipeline[-1], AgentRole.VALIDATION)

if __name__ == "__main__":
    unittest.main()
