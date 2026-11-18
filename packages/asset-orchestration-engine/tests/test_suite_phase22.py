import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ToolGovernanceAPI, ActionProposal, ActionScope, ActionLifecycle,
    ExecutionBudget, BuildSpecification, Requirement, RequirementPriority,
    ActionType, SpecStatus
)

class TestToolGovernancePhase22(unittest.TestCase):
    def setUp(self):
        self.gov = ToolGovernanceAPI()

    def test_01_valid_action_lifecycle(self):
        """Test 1: modify roof_height = 0.80m -> ALLOW -> EXECUTE -> VERIFY -> COMMITTED."""
        prop = ActionProposal("prop_01", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
        res = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.COMMITTED)
        self.assertTrue(res.verification_passed)

    def test_02_out_of_range_parameter_rejection(self):
        """Test 2: roof_height = 100m -> REJECTED before Blender."""
        prop = ActionProposal("prop_02", "task_01", "modify_asset", "house_003", parameters={"roof_height": 100.0})
        res = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("PARAMETER_OUT_OF_RANGE", res.message)

    def test_03_unauthorized_scope_escalation(self):
        """Test 3: Intentar escalar modify_component a SCENE -> REJECTED."""
        prop = ActionProposal(
            "prop_03", "task_01", "modify_component", "house_003",
            scope=ActionScope.SCENE, parameters={"roof_height": 0.80}
        )
        res = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("UNAUTHORIZED_SCOPE_ESCALATION", res.message)

    def test_04_duplicate_action_detection(self):
        """Test 4: modify roof_height repetido -> DUPLICATE_ACTION."""
        prop = ActionProposal("prop_04", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
        res1 = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res1.status, ActionLifecycle.COMMITTED)

        # Repetir idéntico
        res2 = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res2.status, ActionLifecycle.REJECTED)
        self.assertIn("DUPLICATE_ACTION", res2.message)

    def test_05_infinite_loop_protection(self):
        """Test 5: Patrón cíclico A -> B -> A -> B -> LOOP_DETECTED."""
        propA = ActionProposal("propA", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.70})
        propB = ActionProposal("propB", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.90})

        # Gateway con loop guard
        self.gov.submit_action_proposal("designer_agent", propA)
        self.gov.gateway.dup_detector.clear()
        self.gov.submit_action_proposal("designer_agent", propB)
        self.gov.gateway.dup_detector.clear()
        self.gov.submit_action_proposal("designer_agent", propA)
        self.gov.gateway.dup_detector.clear()
        res = self.gov.submit_action_proposal("designer_agent", propB)

        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("LOOP_DETECTED", res.message)

    def test_06_budget_exhaustion_protection(self):
        """Test 6: max_asset_rebuilds = 3 -> 4ta reconstrucción produce BUDGET_EXCEEDED."""
        self.gov.set_budget(ExecutionBudget(max_asset_rebuilds=3, used_asset_rebuilds=3))
        prop = ActionProposal("prop_06", "task_01", "rebuild_asset", "house_003")
        res = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("BUDGET_EXCEEDED", res.message)

    def test_07_post_action_verification_failure_and_rollback(self):
        """Test 7: MCP responde success pero Blender no actualiza -> VERIFICATION_FAILED y ROLLED_BACK."""
        prop = ActionProposal("prop_07", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
        res = self.gov.submit_action_proposal("designer_agent", prop, simulate_blender_state_failure=True)
        self.assertEqual(res.status, ActionLifecycle.ROLLED_BACK)
        self.assertIn("VERIFICATION_FAILED", res.message)

    def test_08_requirement_constraint_protection(self):
        """Test 8: IA intenta cambiar requisito explícito width=4m a 5m -> REQUIREMENT_MUTATION_DENIED."""
        spec = BuildSpecification(
            spec_id="spec_test",
            action=ActionType.CREATE,
            target_type="HOUSE",
            target_id="house_003",
            requirements={
                "length": Requirement("r1", "DIMENSION", "length", 4.0, priority=RequirementPriority.CRITICAL, source="USER_EXPLICIT")
            },
            status=SpecStatus.READY
        )
        prop = ActionProposal("prop_08", "task_01", "modify_asset", "house_003", parameters={"width": 5.0})
        res = self.gov.submit_action_proposal("designer_agent", prop, spec=spec)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("REQUIREMENT_MUTATION_DENIED", res.message)

    def test_09_destructive_action_high_risk_policy(self):
        """Test 9: DELETE_ASSET requiere aprobación humana explícita."""
        prop = ActionProposal("prop_09", "task_01", "delete_asset", "house_003")
        res = self.gov.submit_action_proposal("designer_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("PENDING_APPROVAL", res.message)

    def test_10_least_privilege_permission_denial(self):
        """Test 10: Agente de sólo lectura no puede ejecutar modify_asset -> PERMISSION_DENIED."""
        prop = ActionProposal("prop_10", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
        res = self.gov.submit_action_proposal("inspector_agent", prop)
        self.assertEqual(res.status, ActionLifecycle.REJECTED)
        self.assertIn("PERMISSION_DENIED", res.message)

    def test_11_execution_report_generation(self):
        """Test 11: Genera ExecutionReport con métricas completas."""
        prop = ActionProposal("prop_11", "task_rep", "modify_asset", "house_003", parameters={"roof_height": 0.80})
        self.gov.submit_action_proposal("designer_agent", prop)
        rep = self.gov.generate_report("task_rep")
        self.assertEqual(rep.status, "COMPLETED")
        self.assertGreaterEqual(rep.executed_actions, 1)

if __name__ == "__main__":
    unittest.main()
