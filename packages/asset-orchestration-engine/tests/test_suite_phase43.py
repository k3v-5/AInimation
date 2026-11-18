import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ai_orchestration_api import (
    AIOrchestratorAPI, PermissionLevel, AgentOperationStatus,
    AgentDecision, ToolRegistry, ToolDefinition, ToolCategory
)
from src.visual_reference_matching import ReferenceImageSpec

class TestAIOrchestrationAPIPhase43(unittest.TestCase):
    def setUp(self):
        self.api = AIOrchestratorAPI(permission=PermissionLevel.MODIFY)
        self.ref = ReferenceImageSpec(
            image_id="REF_HOUSE",
            expected_aspect_ratio=1.52,
            expected_roof_ratio=0.31,
            expected_components={"chimney": True}
        )

    def test_01_acceptance_1_discovery_capabilities(self):
        """Acceptance Test 1: get_capabilities devuelve capacidades y generadores registrados."""
        resp = self.api.get_capabilities()
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertIn("supported_generators", resp.output_data)
        self.assertIn("walls", resp.output_data["supported_generators"])

    def test_02_acceptance_2_create_plan_estimation(self):
        """Acceptance Test 2: create_plan compila un plan con estimación de llamadas y riesgo."""
        resp = self.api.create_plan("HOUSE_001", {"roof_height": 1.45})
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertIn("plan", resp.output_data)
        self.assertEqual(resp.output_data["plan"].estimated_mcp_calls, 1)

    def test_03_acceptance_3_explain_plan(self):
        """Acceptance Test 3: explain_plan devuelve explicación comprensible de las operaciones."""
        p_resp = self.api.create_plan("HOUSE_001", {"roof_height": 1.45})
        exp_resp = self.api.explain_plan(p_resp.operation_id)
        self.assertEqual(exp_resp.status, AgentOperationStatus.SUCCESS)
        self.assertIn("estimated", exp_resp.summary)

    def test_04_acceptance_4_asset_creation_typed_params(self):
        """Acceptance Test 4: create_asset genera el activo con componentes canónicos."""
        resp = self.api.create_asset("HOUSE_001", {"width": 8.0, "roof_height": 1.8})
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertEqual(len(resp.affected_components), 5)

    def test_05_acceptance_5_surgical_asset_update(self):
        """Acceptance Test 5: update_asset actualiza parámetros y declara componentes afectados."""
        self.api.create_asset("HOUSE_001", {"width": 8.0, "roof_height": 1.8})
        resp = self.api.update_asset("HOUSE_001", {"roof_height": 1.45})
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertIn("roof", resp.affected_components)

    def test_06_acceptance_6_destructive_action_approval_gate(self):
        """Acceptance Test 6: delete_asset requiere aprobación humana (REQUIRES_APPROVAL)."""
        del_api = AIOrchestratorAPI(permission=PermissionLevel.DELETE)
        resp = del_api.delete_asset("HOUSE_001")
        self.assertEqual(resp.status, AgentOperationStatus.REQUIRES_APPROVAL)
        self.assertEqual(resp.next_action, AgentDecision.ASK)

    def test_07_acceptance_7_sandboxing_blocks_forbidden_tools(self):
        """Acceptance Test 7: Registro o acceso a execute_python lanza violación de seguridad."""
        reg = ToolRegistry()
        with self.assertRaises(PermissionError) as ctx:
            reg.register(ToolDefinition("execute_python", ToolCategory.EXECUTION, PermissionLevel.ADMIN))
        self.assertIn("SECURITY_VIOLATION", str(ctx.exception))

    def test_08_acceptance_8_permission_hierarchy_gate(self):
        """Acceptance Test 8: Agente con permiso READ intentando mutar lanza PERMISSION_DENIED."""
        read_only_api = AIOrchestratorAPI(permission=PermissionLevel.READ)
        with self.assertRaises(PermissionError) as ctx:
            read_only_api.create_asset("HOUSE_READ", {"width": 8.0})
        self.assertIn("PERMISSION_DENIED", str(ctx.exception))

    def test_09_acceptance_9_context_compression_tokens(self):
        """Acceptance Test 9: inspect_asset devuelve contexto compacto del activo sin saturar tokens."""
        self.api.create_asset("HOUSE_001", {"width": 8.0, "roof_height": 1.8})
        resp = self.api.inspect_asset("HOUSE_001")
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        ctx = resp.output_data["context"]
        self.assertEqual(ctx.asset_id, "HOUSE_001")
        self.assertIn("foundation", ctx.components)

    def test_10_acceptance_10_run_visual_critic(self):
        """Acceptance Test 10: run_visual_critic devuelve puntuación estructurada y decisión CORRECT."""
        self.api.create_asset("HOUSE_001", {"width": 9.0, "roof_height": 2.0})
        resp = self.api.run_visual_critic("HOUSE_001", self.ref, aspect_ratio=1.80, roof_ratio=0.43)
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertIn("overall_score", resp.validation)
        self.assertEqual(resp.next_action, AgentDecision.CORRECT)

    def test_11_acceptance_11_apply_correction(self):
        """Acceptance Test 11: apply_correction aplica el cambio paramétrico de forma segura."""
        self.api.create_asset("HOUSE_001", {"width": 9.0, "roof_height": 2.0})
        resp = self.api.apply_correction("HOUSE_001", "roof_height", 1.45)
        self.assertEqual(resp.status, AgentOperationStatus.SUCCESS)
        self.assertEqual(resp.output_data["parameters"]["roof_height"], 1.45)

    def test_12_acceptance_12_loop_guard_prevention(self):
        """Acceptance Test 12: Repetición de la misma corrección detecta LOOP_DETECTED."""
        self.api.create_asset("HOUSE_001", {"width": 9.0, "roof_height": 2.0})
        self.api.apply_correction("HOUSE_001", "roof_height", 1.45)
        self.api.apply_correction("HOUSE_001", "roof_height", 1.45)
        # 3ra repetición
        resp = self.api.apply_correction("HOUSE_001", "roof_height", 1.45)
        self.assertEqual(resp.status, AgentOperationStatus.BLOCKED)
        self.assertEqual(resp.next_action, AgentDecision.STOP)
        self.assertIn("LOOP_DETECTED", resp.errors[0])

    def test_13_acceptance_13_stagnation_detection(self):
        """Acceptance Test 13: Cero mejora en puntuación genera advertencia NO_PROGRESS."""
        self.api.create_asset("HOUSE_001", {"width": 9.0, "roof_height": 2.0})
        # Registrar 3 iteraciones con el mismo score en memoria
        self.api.facade.memory.record_iteration("HOUSE_001", 1, 0.750, {})
        self.api.facade.memory.record_iteration("HOUSE_001", 2, 0.751, {})
        stag = self.api.facade.memory.record_iteration("HOUSE_001", 3, 0.752, {})
        self.assertIsNotNone(stag)
        self.assertIn("NO_PROGRESS", stag)

    def test_14_acceptance_14_budget_exhaustion(self):
        """Acceptance Test 14: Agotar presupuesto de llamadas MCP bloquea nuevas actualizaciones."""
        self.api.facade.budget.remaining_calls = 0
        resp = self.api.update_asset("HOUSE_001", {"width": 10.0})
        self.assertEqual(resp.status, AgentOperationStatus.BLOCKED)
        self.assertIn("BUDGET_EXCEEDED", resp.errors[0])
        self.assertEqual(resp.next_action, AgentDecision.STOP)

    def test_15_acceptance_15_async_status_and_cancel(self):
        """Acceptance Test 15: get_operation_status y cancel_operation gestionan el ciclo de vida."""
        c_resp = self.api.create_asset("HOUSE_001", {"width": 8.0})
        status_resp = self.api.get_operation_status(c_resp.operation_id)
        self.assertEqual(status_resp.status, AgentOperationStatus.SUCCESS)
        
        cancel_resp = self.api.cancel_operation("OP_ASYNC_99")
        self.assertEqual(cancel_resp.next_action, AgentDecision.STOP)

    def test_16_acceptance_16_full_agent_workflow_loop(self):
        """Acceptance Test 16: Flujo completo: Discovery -> Plan -> Create -> Critique -> Correct -> Accept."""
        # 1. Discovery
        disc = self.api.get_capabilities()
        self.assertEqual(disc.status, AgentOperationStatus.SUCCESS)

        # 2. Plan & Create
        self.api.create_plan("HOUSE_001", {"width": 8.0, "roof_height": 1.8})
        self.api.create_asset("HOUSE_001", {"width": 8.0, "roof_height": 1.8})

        # 3. Critique
        crit = self.api.run_visual_critic("HOUSE_001", self.ref, aspect_ratio=1.80, roof_ratio=0.43)
        self.assertEqual(crit.next_action, AgentDecision.CORRECT)

        # 4. Correct
        corr = self.api.apply_correction("HOUSE_001", "roof_height", 1.45)
        self.assertEqual(corr.status, AgentOperationStatus.SUCCESS)

if __name__ == "__main__":
    unittest.main()
