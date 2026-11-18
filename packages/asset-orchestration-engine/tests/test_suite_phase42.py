import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp_execution_gateway import (
    MCPGatewayAPI, CommandType, RiskLevel, ExecutionStatus,
    GatewayPolicy, MockMCPAdapter, CapabilityManager, ExecutionResult
)

class TestMCPExecutionGatewayPhase42(unittest.TestCase):
    def setUp(self):
        self.mock_adapter = MockMCPAdapter()
        self.api = MCPGatewayAPI(
            policy=GatewayPolicy(max_mcp_calls_per_operation=10, max_same_command_retries=3),
            adapter=self.mock_adapter
        )

    def test_01_acceptance_1_high_level_command_planning(self):
        """Acceptance Test 1: Planificación estructurada de comando CREATE_ASSET."""
        cmd = self.api.create_command("CMD_01", "OP_01", CommandType.CREATE_ASSET, "HOUSE_001", {"width": 8.0})
        plan = self.api.plan_operations([cmd])
        self.assertEqual(plan.estimated_mcp_calls, 1)
        self.assertEqual(plan.overall_risk, RiskLevel.LOW)

    def test_02_acceptance_2_denylist_blocks_delete_all(self):
        """Acceptance Test 2: Intento de DELETE_ALL_OBJECTS es bloqueado por política de sandboxing."""
        cmd = self.api.create_command("CMD_DANGEROUS", "OP_99", CommandType.DELETE_ALL_OBJECTS, "ALL")
        with self.assertRaises(PermissionError) as ctx:
            self.api.execute_command(cmd)
        self.assertIn("COMMAND_DENIED", str(ctx.exception))

    def test_03_acceptance_3_call_budget_enforcement(self):
        """Acceptance Test 3: Operación que excede el presupuesto de llamadas MCP lanza BUDGET_EXCEEDED."""
        cmds = [
            self.api.create_command(f"CMD_{i}", "OP_BULK", CommandType.CREATE_OBJECT, f"OBJ_{i}")
            for i in range(12) # Budget is 10
        ]
        with self.assertRaises(ValueError) as ctx:
            self.api.plan_operations(cmds)
        self.assertIn("BUDGET_EXCEEDED", str(ctx.exception))

    def test_04_acceptance_4_optimistic_concurrency_conflict(self):
        """Acceptance Test 4: Discrepancia en expected_scene_version lanza STATE_CONFLICT."""
        # Incrementar versión de escena ejecutando un comando
        cmd1 = self.api.create_command("CMD_01", "OP_01", CommandType.CREATE_OBJECT, "OBJ_WALLS")
        self.api.execute_command(cmd1)

        # Comando con versión desactualizada (esperaba 1, pero es 2)
        cmd2 = self.api.create_command("CMD_02", "OP_02", CommandType.UPDATE_OBJECT, "OBJ_WALLS", expected_scene_version=1)
        with self.assertRaises(RuntimeError) as ctx:
            self.api.execute_command(cmd2)
        self.assertIn("STATE_CONFLICT", str(ctx.exception))

    def test_05_acceptance_5_drift_detection_external_edit(self):
        """Acceptance Test 5: Detección de drift cuando Blender tiene objetos no registrados."""
        cmd = self.api.create_command("CMD_01", "OP_01", CommandType.CREATE_OBJECT, "HOUSE_001_WALLS")
        self.api.execute_command(cmd)

        drift = self.api.detect_scene_drift({"HOUSE_001_WALLS", "EXTERNAL_MANUAL_CUBE"})
        self.assertIsNotNone(drift)
        self.assertIn("DRIFT_DETECTED", drift)

    def test_06_acceptance_6_idempotency_protection(self):
        """Acceptance Test 6: Mismo comando ejecutado con idempotency_key devuelve resultado en cache sin llamadas extra."""
        cmd = self.api.create_command("CMD_01", "OP_01", CommandType.CREATE_OBJECT, "HOUSE_ROOF", idempotency_key="IDEM_ROOF_01")
        res1 = self.api.execute_command(cmd)
        calls_before = self.mock_adapter.call_count

        res2 = self.api.execute_command(cmd)
        self.assertEqual(self.mock_adapter.call_count, calls_before)
        self.assertEqual(res1.execution_id, res2.execution_id)

    def test_07_acceptance_7_transaction_rollback_surgical(self):
        """Acceptance Test 7: Fallo en ejecución hace rollback eliminando solo los objetos de esa transacción."""
        # Objeto previo existente
        self.api.execute_command(self.api.create_command("CMD_PREV", "OP_PREV", CommandType.CREATE_OBJECT, "FOUNDATION_OK"))
        
        # Simular fallo en nueva transacción
        self.mock_adapter.simulate_failure = True
        cmd_fail = self.api.create_command("CMD_FAIL", "OP_FAIL", CommandType.CREATE_OBJECT, "FAILED_WALLS")
        res = self.api.execute_command(cmd_fail)
        
        self.assertEqual(res.status, ExecutionStatus.FAILED_EXECUTION)
        # El objeto previo se preserva y el fallido no existe
        self.assertIn("FOUNDATION_OK", self.mock_adapter.scene_objects)
        self.assertNotIn("FAILED_WALLS", self.mock_adapter.scene_objects)

    def test_08_acceptance_8_result_verification_failure(self):
        """Acceptance Test 8: Si el objeto no aparece en Blender tras la llamada MCP, marca FAILED_VERIFICATION."""
        # Crear adapter donde el objeto no se añade a la escena
        class MissingObjAdapter(MockMCPAdapter):
            def execute_command(self, cmd):
                # Simula que devuelve SUCCESS pero no añade el objeto
                return ExecutionResult(execution_id="EXEC_FAKE", command_id=cmd.command_id, status=ExecutionStatus.SUCCESS)

        gw = MCPGatewayAPI(adapter=MissingObjAdapter())
        cmd = gw.create_command("CMD_MISS", "OP_MISS", CommandType.CREATE_OBJECT, "GHOST_OBJECT")
        res = gw.execute_command(cmd)
        self.assertEqual(res.status, ExecutionStatus.FAILED_VERIFICATION)

    def test_09_acceptance_9_unknown_outcome_recovery_on_timeout(self):
        """Acceptance Test 9: Timeout recupera el estado comprobando si el objeto fue creado."""
        self.mock_adapter.simulate_timeout = True
        cmd = self.api.create_command("CMD_TIME", "OP_TIME", CommandType.CREATE_OBJECT, "ROOF_TIMEOUT_RECOVERED")
        res = self.api.execute_command(cmd)
        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertTrue(res.output.get("recovered_from_timeout", False))

    def test_10_acceptance_10_dry_run_simulation(self):
        """Acceptance Test 10: Dry-run calcula estimaciones y riesgos sin ejecutar."""
        cmds = [
            self.api.create_command("C1", "OP1", CommandType.CREATE_OBJECT, "WALLS", risk_level=RiskLevel.MEDIUM),
            self.api.create_command("C2", "OP1", CommandType.CREATE_OBJECT, "ROOF", risk_level=RiskLevel.LOW)
        ]
        plan = self.api.plan_operations(cmds)
        self.assertEqual(plan.estimated_mcp_calls, 2)
        self.assertEqual(plan.overall_risk, RiskLevel.MEDIUM)

    def test_11_acceptance_11_component_locking(self):
        """Acceptance Test 11: Bloqueo de componente evita condiciones de carrera."""
        self.api.acquire_lock("HOUSE_001_ROOF")
        with self.assertRaises(RuntimeError) as ctx:
            self.api.acquire_lock("HOUSE_001_ROOF")
        self.assertIn("LOCK_CONFLICT", str(ctx.exception))
        self.api.release_lock("HOUSE_001_ROOF")

    def test_12_acceptance_12_loop_guard_prevention(self):
        """Acceptance Test 12: Loop guard bloquea comandos repetidos fallidos."""
        self.mock_adapter.simulate_failure = True
        cmd = self.api.create_command("CMD_LOOP", "OP_LOOP", CommandType.CREATE_OBJECT, "LOOP_OBJ")
        for _ in range(3):
            self.api.execute_command(cmd)
        
        # 4ta repetición supera max_retries=3
        with self.assertRaises(RuntimeError) as ctx:
            self.api.execute_command(cmd)
        self.assertIn("LOOP_DETECTED", str(ctx.exception))

    def test_13_acceptance_13_emergency_stop(self):
        """Acceptance Test 13: Emergency stop bloquea cualquier ejecución subsiguiente."""
        self.api.emergency_stop()
        cmd = self.api.create_command("CMD_AFTER_STOP", "OP_01", CommandType.CREATE_OBJECT, "OBJ_BLOCKED")
        res = self.api.execute_command(cmd)
        self.assertEqual(res.status, ExecutionStatus.BLOCKED)

    def test_14_acceptance_14_unsupported_capability_rejection(self):
        """Acceptance Test 14: Capacidad no soportada lanza CAPABILITY_UNSUPPORTED."""
        caps = CapabilityManager({"supports_rendering": False})
        with self.assertRaises(ValueError) as ctx:
            caps.check_capability("supports_rendering")
        self.assertIn("CAPABILITY_UNSUPPORTED", str(ctx.exception))

    def test_15_acceptance_15_empty_target_rejection(self):
        """Acceptance Test 15: Target vacío lanza COMMAND_INVALID."""
        cmd = self.api.create_command("CMD_EMPTY", "OP_01", CommandType.CREATE_OBJECT, "   ")
        with self.assertRaises(ValueError) as ctx:
            self.api.execute_command(cmd)
        self.assertIn("COMMAND_INVALID", str(ctx.exception))

    def test_16_acceptance_16_end_to_end_gateway_execution(self):
        """Acceptance Test 16: Flujo E2E de creación y verificación en Blender state tracker."""
        initial_ver = self.api.current_scene_version
        cmd = self.api.create_command("CMD_E2E", "OP_E2E", CommandType.CREATE_OBJECT, "HOUSE_COMPLETED")
        res = self.api.execute_command(cmd)
        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertGreater(self.api.current_scene_version, initial_ver)

if __name__ == "__main__":
    unittest.main()
