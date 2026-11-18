import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    CorrectionExecutionAPI, MockBlenderProvider, ExecutionMode, OperationRegistry,
    VisualIntelligenceAPI
)

class TestCorrectionExecutionPhase11(unittest.TestCase):
    def setUp(self):
        self.provider = MockBlenderProvider()
        self.corr_api = CorrectionExecutionAPI(self.provider, execution_mode=ExecutionMode.BALANCED)

        # Configurar espada base
        self.provider.init_asset("sword_001", {
            "grip": {"dimensions": (0.03, 0.03, 0.25), "material": {"metallic": 0.0, "roughness": 0.8}},
            "guard": {"dimensions": (0.15, 0.03, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}},
            "blade": {"dimensions": (0.05, 0.02, 0.50), "material": {"metallic": 0.0, "roughness": 0.5}}, # Hoja corta no metálica
            "pommel": {"dimensions": (0.05, 0.05, 0.05), "material": {"metallic": 0.9, "roughness": 0.3}}
        })
        self.corr_api.register_component("grip_001", "sword_001", "obj_grip", "grip", is_locked=False)
        self.corr_api.register_component("blade_001", "sword_001", "obj_blade", "blade", is_locked=False)

    def test_01_simple_scale_dimensions(self):
        """Test 1: Simple Scale - SET_DIMENSIONS ajusta longitud de hoja a 0.70m."""
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.70}}
        ])
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "CORRECTED")
        dims = self.provider.get_component_dimensions("sword_001", "blade")
        self.assertEqual(dims[2], 0.70)

    def test_02_material_correction_metallic(self):
        """Test 2: Material correction - CHANGE_METALLIC ajusta metallic=1.0 sin tocar geometría."""
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "CHANGE_METALLIC", "target": "blade", "parameters": {"value": 1.0}}
        ])
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "CORRECTED")
        met = self.provider.get_material_property("sword_001", "blade", "metallic")
        self.assertEqual(met, 1.0)
        # Geometría intacta
        dims = self.provider.get_component_dimensions("sword_001", "blade")
        self.assertEqual(dims[2], 0.50)

    def test_03_component_isolation_handle_untouched(self):
        """Test 3: Isolation - Modificar blade deja grip 100% intacto."""
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.90}}
        ])
        self.assertTrue(res["success"])
        grip_dims = self.provider.get_component_dimensions("sword_001", "grip")
        self.assertEqual(grip_dims, (0.03, 0.03, 0.25))

    def test_04_rollback_on_failure(self):
        """Test 4: Rollback - Fallo en operación restaura snapshot previo."""
        # Estado antes
        prev_dims = self.provider.get_component_dimensions("sword_001", "blade")
        # Intentar modificar target inexistente
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.90}},
            {"type": "SET_DIMENSIONS", "target": "non_existent_part", "parameters": {"length": 0.90}}
        ])
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "ROLLED_BACK")
        # Estado restaurado al snapshot previo
        cur_dims = self.provider.get_component_dimensions("sword_001", "blade")
        self.assertEqual(cur_dims, prev_dims)

    def test_05_protected_locked_component_denied(self):
        """Test 5: Locked component - Modificar grip bloqueado devuelve DENIED."""
        self.corr_api.lock_component("grip_001", True)
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "grip_001", "parameters": {"length": 0.40}}
        ])
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "DENIED")
        self.assertEqual(res["error_code"], "PRECONDITION_FAILED")

    def test_06_preserve_list_protection(self):
        """Test 6: Preserve list - Componente en preserve_components es protegido."""
        res = self.corr_api.execute_correction(
            "sword_001",
            [{"type": "SET_DIMENSIONS", "target": "guard", "parameters": {"length": 0.40}}],
            protected_components=["guard", "pommel"]
        )
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "DENIED")

    def test_07_timeout_unknown_state_handling(self):
        """Test 7: Timeout - Timeout de MCP marca transacción como UNKNOWN."""
        self.provider.simulate_timeout = True
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.80}}
        ])
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "UNKNOWN")
        self.assertEqual(res["error_code"], "PROVIDER_TIMEOUT")

    def test_08_transient_retry_success(self):
        """Test 8: Retry - Error transitorio de conexión se reintenta y completa exitosamente."""
        self.provider.simulate_transient_error_count = 1 # 1 fallo y luego éxito
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.75}}
        ])
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "CORRECTED")

    def test_09_no_op_detection(self):
        """Test 9: NO_OP - Si ya tiene el valor pedido, devuelve NO_CHANGE_REQUIRED."""
        res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.50}}
        ])
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "NO_CHANGE_REQUIRED")

    def test_10_oscillation_detection_anti_loop(self):
        """Test 10: Anti-loop - 3 operaciones consecutivas de escala activan OSCILLATION_DETECTED."""
        self.corr_api.execute_correction("sword_001", [{"type": "SCALE_OBJECT", "target": "blade", "parameters": {"factor": 1.2}}])
        self.corr_api.execute_correction("sword_001", [{"type": "SCALE_OBJECT", "target": "blade", "parameters": {"factor": 0.8}}])
        self.corr_api.execute_correction("sword_001", [{"type": "SCALE_OBJECT", "target": "blade", "parameters": {"factor": 1.2}}])
        
        # 4ta mutación
        res = self.corr_api.execute_correction("sword_001", [{"type": "SCALE_OBJECT", "target": "blade", "parameters": {"factor": 0.8}}])
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "STOP")
        self.assertEqual(res["error_code"], "OSCILLATION_DETECTED")

    def test_11_prohibited_operations(self):
        """Test 11: Prohibited operations - CLEAR_SCENE es bloqueado."""
        self.assertTrue(OperationRegistry.is_prohibited("CLEAR_SCENE"))
        self.assertTrue(OperationRegistry.is_prohibited("DELETE_SCENE"))

    def test_12_permission_safe_mode(self):
        """Test 12: Permissions - Operación MEDIUM en modo SAFE es rechazada."""
        safe_api = CorrectionExecutionAPI(self.provider, execution_mode=ExecutionMode.SAFE)
        res = safe_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.80}}
        ])
        self.assertFalse(res["success"])
        self.assertEqual(res["status"], "DENIED")
        self.assertEqual(res["error_code"], "OPERATION_NOT_PERMITTED")

    def test_13_dry_run_mode(self):
        """Test 13: Dry run - dry_run=True retorna plan sin mutar el provider."""
        res = self.corr_api.execute_correction(
            "sword_001",
            [{"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.99}}],
            dry_run=True
        )
        self.assertTrue(res["success"])
        self.assertEqual(res["status"], "dry_run")
        # Provider no mutado
        dims = self.provider.get_component_dimensions("sword_001", "blade")
        self.assertEqual(dims[2], 0.50)

    def test_14_full_correction_pipeline_loop(self):
        """Test 14: Full Pipeline - Detección F10 -> Corrección F11 -> Revalidación F10 PASS."""
        vi = VisualIntelligenceAPI()
        goal = vi.build_goal_spec(category="ONE_HANDED_MEDIEVAL_SWORD")
        
        # 1. Evaluación inicial
        dims_init = {k: v["dimensions"] for k, v in self.provider.assets["sword_001"]["components"].items()}
        report1 = vi.verify_asset("sword_001", dims_init, list(dims_init.keys()), goal_spec=goal)
        self.assertIn(report1.status, ["NEEDS_CORRECTION", "PASS_WITH_WARNINGS"])

        # 2. Plan y ejecución de corrección
        plan = vi.plan_correction(report1)
        corr_res = self.corr_api.execute_correction("sword_001", [
            {"type": "SET_DIMENSIONS", "target": "blade", "parameters": {"length": 0.95}}
        ])
        self.assertTrue(corr_res["success"])

        # 3. Revalidación F10
        dims_post = {k: v["dimensions"] for k, v in self.provider.assets["sword_001"]["components"].items()}
        report2 = vi.verify_asset("sword_001", dims_post, list(dims_post.keys()), goal_spec=goal)
        self.assertEqual(report2.status, "PASS")

if __name__ == "__main__":
    unittest.main()
