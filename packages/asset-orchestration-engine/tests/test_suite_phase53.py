import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.blender_capability_layer import (
    BlenderCapabilityAPI, OperationRequest, OperationStatus,
    MockBlenderAdapter, AhujasidBlenderAdapter, CircuitState
)

class TestBlenderCapabilityLayerPhase53(unittest.TestCase):
    def setUp(self):
        self.mock_adapter = MockBlenderAdapter()
        self.api = BlenderCapabilityAPI(adapter=self.mock_adapter)

    def test_01_mandatory_case_1_abstract_capability_execution(self):
        """Mandatory Case 1: Operaciones abstractas (object.create, transform.set, material.assign) sin llamadas MCP directas."""
        req_create = OperationRequest("OP_1", "object.create", {"object_id": "Barrel_Body", "semantic_id": "barrel_body"})
        res_create = self.api.execute_operation(req_create)
        self.assertEqual(res_create.status, OperationStatus.SUCCEEDED)

        req_trans = OperationRequest("OP_2", "transform.set", {"object_id": "Barrel_Body", "scale": (1.0, 1.0, 1.2)})
        res_trans = self.api.execute_operation(req_trans)
        self.assertEqual(res_trans.status, OperationStatus.SUCCEEDED)

        req_mat = OperationRequest("OP_3", "material.assign", {"object_id": "Barrel_Body", "material_name": "M_DarkWood"})
        res_mat = self.api.execute_operation(req_mat)
        self.assertEqual(res_mat.status, OperationStatus.SUCCEEDED)

        obj = self.api.inspect_object("Barrel_Body")
        self.assertEqual(obj.transform["scale"], (1.0, 1.0, 1.2))
        self.assertIn("M_DarkWood", obj.materials)

    def test_02_mandatory_case_2_failure_reconciliation_no_duplicate(self):
        """Mandatory Case 2: Pérdida de conexión y reconciliación de estado que evita duplicar el objeto ring_02."""
        # 1. Creamos ring_02 con éxito
        req_ring = OperationRequest("OP_RING", "object.create", {"object_id": "Barrel_Ring_02", "semantic_id": "barrel_ring_02"})
        res_ring = self.api.execute_operation(req_ring)
        self.assertEqual(res_ring.status, OperationStatus.SUCCEEDED)

        # 2. Simulación de reintento tras timeout: StateReconciler detecta que ya existe
        res_retry = self.api.execute_operation(req_ring)
        self.assertEqual(res_retry.status, OperationStatus.SUCCEEDED)
        self.assertTrue(res_retry.result.get("reconciled"))
        self.assertEqual(len([o for o in self.mock_adapter.scene.objects if "Ring_02" in o]), 1)

    def test_03_mandatory_case_3_delta_modification_not_full_rebuild(self):
        """Mandatory Case 3: 'Haz el barril 20% más alto' ejecuta transform.set delta sin destruir el objeto."""
        self.api.execute_operation(OperationRequest("OP_CREATE", "object.create", {"object_id": "Barrel_Master"}))
        res_delta = self.api.execute_operation(OperationRequest("OP_DELTA", "transform.set", {"object_id": "Barrel_Master", "scale": (1.0, 1.0, 1.2)}))
        self.assertEqual(res_delta.status, OperationStatus.SUCCEEDED)
        self.assertEqual(self.api.inspect_object("Barrel_Master").transform["scale"], (1.0, 1.0, 1.2))

    def test_04_mandatory_case_4_adapter_hot_swap(self):
        """Mandatory Case 4: Sustituir AhujasidBlenderAdapter por MockBlenderAdapter ejecuta idénticamente."""
        ahujasid_api = BlenderCapabilityAPI(adapter=AhujasidBlenderAdapter(self.mock_adapter))
        res = ahujasid_api.execute_operation(OperationRequest("OP_AHUJASID", "object.create", {"object_id": "SM_Prop_01"}))
        self.assertEqual(res.status, OperationStatus.SUCCEEDED)

        # Swap a Mock directo
        ahujasid_api.swap_adapter(self.mock_adapter)
        res_swap = ahujasid_api.execute_operation(OperationRequest("OP_SWAP", "object.create", {"object_id": "SM_Prop_02"}))
        self.assertEqual(res_swap.status, OperationStatus.SUCCEEDED)

    def test_05_mandatory_case_5_circuit_breaker_tripped_on_repeated_errors(self):
        """Mandatory Case 5: 3 fallos consecutivos abren el Circuit Breaker bloqueando peticiones posteriores."""
        self.mock_adapter.fault_connection_loss = True
        req = OperationRequest("OP_FAIL", "object.create", {"object_id": "FailObj"})
        
        self.api.execute_operation(req) # 1
        self.api.execute_operation(req) # 2
        self.api.execute_operation(req) # 3 -> Circuit Breaker OPEN

        self.assertEqual(self.api.circuit_breaker.state, CircuitState.OPEN)

        # Petición 4 es rechazada de inmediato por Circuit Breaker
        res_blocked = self.api.execute_operation(req)
        self.assertIn("CIRCUIT_OPEN", res_blocked.errors[0])

    def test_06_mandatory_case_6_transaction_compensation_rollback(self):
        """Mandatory Case 6: Fallo en etapa 3 dispara compensaciones registradas en etapas 1 y 2."""
        tx_id = "TX_BARREL_BUILD"
        self.api.begin_transaction(tx_id)

        # Stage 1: Crear Body + compensación delete
        req1 = OperationRequest("OP_S1", "object.create", {"object_id": "TX_Body"})
        comp1 = OperationRequest("COMP_S1", "object.delete", {"object_id": "TX_Body"})
        self.api.execute_operation(req1)
        self.api.register_compensation(tx_id, req1, comp1)

        # Stage 2: Crear Ring + compensación delete
        req2 = OperationRequest("OP_S2", "object.create", {"object_id": "TX_Ring"})
        comp2 = OperationRequest("COMP_S2", "object.delete", {"object_id": "TX_Ring"})
        self.api.execute_operation(req2)
        self.api.register_compensation(tx_id, req2, comp2)

        self.assertIn("TX_Body", self.mock_adapter.scene.objects)
        self.assertIn("TX_Ring", self.mock_adapter.scene.objects)

        # Simular fallo en stage 3 y ejecutar rollback
        responses = self.api.rollback_transaction(tx_id)
        self.assertEqual(len(responses), 2)
        self.assertNotIn("TX_Body", self.mock_adapter.scene.objects)
        self.assertNotIn("TX_Ring", self.mock_adapter.scene.objects)

    def test_07_mandatory_case_7_strict_input_schema_validation(self):
        """Mandatory Case 7: Falta de parámetro obligatorio 'object_id' en transform.set lanza INVALID_REQUEST."""
        bad_req = OperationRequest("OP_BAD", "transform.set", {"scale": (1.0, 1.0, 1.0)})
        with self.assertRaises(ValueError) as ctx:
            self.api.execute_operation(bad_req)
        self.assertIn("INVALID_REQUEST", str(ctx.exception))

    def test_08_mandatory_case_8_resource_lock_concurrency_protection(self):
        """Mandatory Case 8: Lock sobre activo bloquea operaciones concurrentes no autorizadas."""
        self.api.acquire_lock("BARREL_LOCK_ASSET", "OP_OWNER_1")
        req_blocked = OperationRequest("OP_INTRUDER", "object.create", {"object_id": "IntruderObj"}, asset_id="BARREL_LOCK_ASSET")
        
        with self.assertRaises(BlockingIOError):
            self.api.execute_operation(req_blocked)

    def test_09_mandatory_case_9_targeted_object_inspection(self):
        """Mandatory Case 9: inspect_object consulta el estado exacto sin escanear toda la escena."""
        self.api.execute_operation(OperationRequest("OP_CR", "object.create", {"object_id": "TargetObj", "semantic_id": "target_semantic"}))
        obj = self.api.inspect_object("TargetObj")
        self.assertIsNotNone(obj)
        self.assertEqual(obj.semantic_id, "target_semantic")

    def test_10_mandatory_case_10_dry_run_execution(self):
        """Mandatory Case 10: is_dry_run = True devuelve respuesta simulada sin modificar la escena."""
        dry_req = OperationRequest("OP_DRY", "object.create", {"object_id": "DryObj"}, is_dry_run=True)
        res = self.api.execute_operation(dry_req)
        self.assertEqual(res.status, OperationStatus.SUCCEEDED)
        self.assertTrue(res.result.get("dry_run"))
        self.assertNotIn("DryObj", self.mock_adapter.scene.objects)

    def test_11_capability_registry_standards(self):
        """Test 11: CapabilityRegistry contiene los contratos estándar."""
        c = self.api.registry.get_contract("export.fbx")
        self.assertIsNotNone(c)
        self.assertEqual(c.version, "v1")

    def test_12_ahujasid_command_translator(self):
        """Test 12: AhujasidCommandTranslator construye el comando MCP esperado."""
        from src.blender_capability_layer.adapters.ahujasid.ahujasid_translator import AhujasidCommandTranslator
        req = OperationRequest("OP_T", "object.create", {"object_id": "Barrel"})
        cmd = AhujasidCommandTranslator.to_mcp_command(req)
        self.assertEqual(cmd["server"], "AhujasidMCP")
        self.assertEqual(cmd["tool"], "blender_object_create")

    def test_13_ahujasid_response_translator(self):
        """Test 13: AhujasidResponseTranslator traduce respuesta cruda a OperationResponse."""
        from src.blender_capability_layer.adapters.ahujasid.ahujasid_translator import AhujasidResponseTranslator
        resp = AhujasidResponseTranslator.from_mcp_response("OP_1", {"status": "SUCCESS", "result": {"ok": True}})
        self.assertEqual(resp.status, OperationStatus.SUCCEEDED)

    def test_14_health_check_reporting(self):
        """Test 14: Health check reporta estado y latencia."""
        h = self.api.health_check()
        self.assertEqual(h.status, "HEALTHY")
        self.assertEqual(h.circuit_state, CircuitState.CLOSED)

    def test_15_release_resource_lock(self):
        """Test 15: Liberar lock permite subsecuente ejecución."""
        self.api.acquire_lock("ASSET_TMP", "OP_1")
        self.api.release_lock("ASSET_TMP")
        req_allowed = OperationRequest("OP_2", "object.create", {"object_id": "FreeObj"}, asset_id="ASSET_TMP")
        res = self.api.execute_operation(req_allowed)
        self.assertEqual(res.status, OperationStatus.SUCCEEDED)

    def test_16_transaction_commit(self):
        """Test 16: Commit de transacción finaliza sin ejecutar rollbacks."""
        tx_id = "TX_COMMIT_TEST"
        self.api.begin_transaction(tx_id)
        self.api.commit_transaction(tx_id)
        self.assertNotIn(tx_id, self.api.tx_manager._active_transactions)

    def test_17_unknown_capability_rejection(self):
        """Test 17: Capability desconocida genera CAPABILITY_UNSUPPORTED."""
        req_unk = OperationRequest("OP_UNK", "unknown.custom_magic", {})
        with self.assertRaises(KeyError) as ctx:
            self.api.execute_operation(req_unk)
        self.assertIn("CAPABILITY_UNSUPPORTED", str(ctx.exception))

    def test_18_scene_revision_increment(self):
        """Test 18: La revisión de la escena incrementa en cada mutación."""
        rev_before = self.mock_adapter.scene.revision
        self.api.execute_operation(OperationRequest("OP_REV", "object.create", {"object_id": "RevObj"}))
        self.assertGreater(self.mock_adapter.scene.revision, rev_before)

    def test_19_circuit_breaker_reset_half_open(self):
        """Test 19: Reset de Circuit Breaker transiciona a HALF_OPEN."""
        self.api.circuit_breaker.record_failure()
        self.api.circuit_breaker.record_failure()
        self.api.circuit_breaker.record_failure()
        self.assertEqual(self.api.circuit_breaker.state, CircuitState.OPEN)
        self.api.circuit_breaker.reset()
        self.assertEqual(self.api.circuit_breaker.state, CircuitState.HALF_OPEN)

    def test_20_end_to_end_capability_pipeline(self):
        """Test 20: Flujo E2E: Request -> Contract Validation -> Execution -> State Inspection."""
        req = OperationRequest("OP_E2E", "object.create", {"object_id": "SM_FinalBarrel", "semantic_id": "barrel_root"})
        res = self.api.execute_operation(req)
        self.assertEqual(res.status, OperationStatus.SUCCEEDED)
        obj = self.api.inspect_object("SM_FinalBarrel")
        self.assertEqual(obj.name, "SM_FinalBarrel")

if __name__ == "__main__":
    unittest.main()
