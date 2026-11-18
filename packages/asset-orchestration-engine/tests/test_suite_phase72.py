import sys
import os
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.governance import (
    AgentContractsToolGovernanceAPI, AgentContractV2, ContractValidator, ContractRegistry,
    Permission, ResourceClassification, RiskLevel, AuthorizationStatus, PermissionManager,
    CapabilityDefinition, CapabilityRegistry, ToolDefinition, ToolRegistry,
    ResourceScope, ResourceManager, PolicySnapshot, EmergencyStopController,
    AuditRecord, AuditLogger, AuthorizationRequest, AuthorizationDecision, AuthorizationEngine,
    MutationRecord, MutationGuard, InvalidContractError, AuthorizationDeniedError
)

class TestSuitePhase72AgentContractsToolGovernance(unittest.TestCase):

    def setUp(self):
        self.api = AgentContractsToolGovernanceAPI()

    def test_01_contract_v2_creation_and_hash_integrity(self):
        c = AgentContractV2(
            agent_id="agent.test.integrity", agent_type="TEST",
            capabilities=["geometry.generate_mesh"],
            permissions=[Permission.GEOMETRY_CREATE]
        )
        self.assertTrue(c.verify_integrity())
        
        # Tampering with permissions
        c.permissions.append(Permission.ASSET_DELETE)
        self.assertFalse(c.verify_integrity())

    def test_02_contract_validator_contradiction_rejection(self):
        # Contradictory tools
        with self.assertRaises(InvalidContractError):
            ContractValidator.validate(AgentContractV2(
                agent_id="agent.invalid.tools", agent_type="TEST",
                allowed_tools=["mesh_generator"],
                forbidden_tools=["mesh_generator"]
            ))

    def test_03_contract_registry_crud_and_lookup(self):
        reg = ContractRegistry()
        c = AgentContractV2(
            agent_id="agent.crud", agent_type="TEST",
            capabilities=["test.cap"],
            permissions=[Permission.ASSET_READ]
        )
        reg.register_contract(c)
        self.assertEqual(reg.get_contract("agent.crud").agent_id, "agent.crud")
        self.assertEqual(len(reg.find_by_capability("test.cap")), 1)
        self.assertEqual(len(reg.find_by_permission(Permission.ASSET_READ)), 1)
        
        reg.remove_contract("agent.crud")
        self.assertIsNone(reg.get_contract("agent.crud"))

    def test_04_deny_by_default_missing_permission(self):
        # Agent has no permissions declared
        c = AgentContractV2(agent_id="agent.unprivileged", agent_type="TEST")
        self.api.contracts.register_contract(c)
        
        dec = self.api.authorize_operation(
            agent_id="agent.unprivileged", tool_id="mesh_generator", capability_id="geometry.generate_mesh"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("PERMISSION_DENIED", dec.reason)

    def test_05_authorization_engine_authorized_operation(self):
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", tool_id="mesh_generator", capability_id="geometry.generate_mesh",
            resource_id="AOE_Generated/WP_Receiver", operation="CREATE_MESH"
        )
        self.assertEqual(dec.status, AuthorizationStatus.AUTHORIZED)

    def test_06_authorization_engine_denied_forbidden_tool(self):
        dec = self.api.authorize_operation(
            agent_id="agent.perception", tool_id="filesystem_deleter", operation="DELETE"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("TOOL_FORBIDDEN", dec.reason)

    def test_07_authorization_engine_unregistered_tool(self):
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", tool_id="malicious_unregistered_tool"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("UNREGISTERED_TOOL", dec.reason)

    def test_08_authorization_engine_unknown_capability(self):
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", capability_id="arbitrary.unknown.capability"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("UNKNOWN_CAPABILITY", dec.reason)

    def test_09_delete_protection_without_explicit_delete_permission(self):
        # Agent has ASSET_WRITE but NOT ASSET_DELETE
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", resource_id="AOE_Generated/Mesh", operation="DELETE_ASSET"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("DELETE_PROTECTION_VIOLATION", dec.reason)

    def test_10_protected_project_resource_violation(self):
        # Modifying protected Art/ source files requires PROJECT_WRITE
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", resource_id="Art/Blender/DarX_Assets.blend", operation="WRITE_ASSET"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("PROTECTED_RESOURCE_VIOLATION", dec.reason)

    def test_11_resource_ownership_conflict(self):
        # Agent A acquires ownership
        self.api.resources.acquire_ownership("WP_Target_Asset", "agent.geometry", "T_01")
        
        # Agent B attempts to mutate same resource
        dec = self.api.authorize_operation(
            agent_id="agent.material", resource_id="WP_Target_Asset", operation="WRITE_MATERIAL"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("RESOURCE_OWNERSHIP_CONFLICT", dec.reason)
        
        # Release ownership
        self.api.resources.release_ownership("WP_Target_Asset", "agent.geometry")
        dec_after = self.api.authorize_operation(
            agent_id="agent.material", resource_id="WP_Target_Asset", operation="WRITE_MATERIAL"
        )
        self.assertEqual(dec_after.status, AuthorizationStatus.AUTHORIZED)

    def test_12_contract_tampering_detected(self):
        c = self.api.contracts.get_contract("agent.geometry")
        original_hash = c.contract_hash
        # Modify internally without recomputing hash
        c.permissions.append(Permission.PROJECT_WRITE)
        
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", tool_id="mesh_generator"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("CONTRACT_INTEGRITY_ERROR", dec.reason)
        
        # Restore contract
        c.permissions.remove(Permission.PROJECT_WRITE)
        c.contract_hash = original_hash

    def test_13_emergency_stop_blocks_all_mutations(self):
        self.api.emergency_stop("TEST_EMERGENCY_HALT")
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", tool_id="mesh_generator", capability_id="geometry.generate_mesh"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("EMERGENCY_STOP_ACTIVE", dec.reason)

    def test_14_emergency_stop_resume(self):
        self.api.emergency_stop("TEST_HALT")
        self.api.resume_from_emergency_stop()
        dec = self.api.authorize_operation(
            agent_id="agent.geometry", tool_id="mesh_generator", capability_id="geometry.generate_mesh"
        )
        self.assertEqual(dec.status, AuthorizationStatus.AUTHORIZED)

    def test_15_mutation_guard_guarded_execution(self):
        req = AuthorizationRequest(
            agent_id="agent.geometry", tool_id="mesh_generator",
            capability_id="geometry.generate_mesh", resource_id="AOE_Generated/WP_Vandal",
            operation="CREATE_MESH", task_id="T_GEOM", orchestration_id="ORCH_01"
        )
        
        executed = []
        def do_mutate():
            executed.append(True)
            return "SUCCESS_GEOM"
            
        result = self.api.mutation_guard.execute_guarded_mutation(
            auth_req=req, mutation_fn=do_mutate, asset_id="WP_Vandal",
            semantic_id="weapon.vandal.001", created=["Receiver_Mesh"]
        )
        self.assertEqual(result, "SUCCESS_GEOM")
        self.assertTrue(executed[0])
        
        records = self.api.mutation_guard.list_mutations("WP_Vandal")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].created_entities, ["Receiver_Mesh"])
        self.assertIsNotNone(records[0].before_state_hash)
        self.assertIsNotNone(records[0].after_state_hash)

    def test_16_mutation_guard_rejection_on_denial(self):
        req = AuthorizationRequest(
            agent_id="agent.perception", tool_id="filesystem_deleter",
            operation="DELETE", task_id="T_BAD", orchestration_id="ORCH_01"
        )
        executed = []
        def do_bad():
            executed.append(True)
            
        with self.assertRaises(AuthorizationDeniedError):
            self.api.mutation_guard.execute_guarded_mutation(
                auth_req=req, mutation_fn=do_bad, asset_id="WP_Vandal", semantic_id="weapon.vandal.001"
            )
        self.assertEqual(len(executed), 0)

    def test_17_audit_logger_records_authorized_and_denied(self):
        self.api.authorize_operation(agent_id="agent.geometry", tool_id="mesh_generator") # Auth
        self.api.authorize_operation(agent_id="agent.visual.critic", tool_id="mesh_generator") # Denied
        
        records = self.api.audit.list_records()
        self.assertGreaterEqual(len(records), 2)
        statuses = [r.status for r in records]
        self.assertIn(AuthorizationStatus.AUTHORIZED, statuses)
        self.assertIn(AuthorizationStatus.DENIED, statuses)

    def test_18_audit_logger_sanitizes_secrets(self):
        req = AuthorizationRequest(
            agent_id="agent.geometry", tool_id="mesh_generator",
            payload={"normal_key": "val", "db_password": "super_secret_password", "auth_token": "bearer 1234"}
        )
        self.api.auth_engine.authorize(req)
        last_rec = self.api.audit.list_records()[-1]
        self.assertEqual(last_rec.sanitized_input["db_password"], "[REDACTED_SECRET]")
        self.assertEqual(last_rec.sanitized_input["auth_token"], "[REDACTED_SECRET]")
        self.assertEqual(last_rec.sanitized_input["normal_key"], "val")

    def test_19_policy_snapshot_capture(self):
        snap = self.api.create_policy_snapshot("SNAP_001")
        self.assertEqual(snap.snapshot_id, "SNAP_001")
        self.assertIn("agent.geometry", snap.contract_versions)
        self.assertEqual(snap.emergency_stop_active, False)

    def test_20_perception_agent_governance_boundaries(self):
        # Allowed
        dec_read = self.api.authorize_operation(agent_id="agent.perception", tool_id="reference_analyzer")
        self.assertEqual(dec_read.status, AuthorizationStatus.AUTHORIZED)
        # Denied
        dec_del = self.api.authorize_operation(agent_id="agent.perception", operation="DELETE_ASSET")
        self.assertEqual(dec_del.status, AuthorizationStatus.DENIED)

    def test_21_visual_critic_governance_boundaries(self):
        # Allowed
        dec_crit = self.api.authorize_operation(agent_id="agent.visual.critic", tool_id="visual_evaluator")
        self.assertEqual(dec_crit.status, AuthorizationStatus.AUTHORIZED)
        # Denied
        dec_mesh = self.api.authorize_operation(agent_id="agent.visual.critic", tool_id="mesh_generator")
        self.assertEqual(dec_mesh.status, AuthorizationStatus.DENIED)

    def test_22_geometry_agent_governance_boundaries(self):
        # Allowed
        dec_geom = self.api.authorize_operation(agent_id="agent.geometry", tool_id="mesh_generator")
        self.assertEqual(dec_geom.status, AuthorizationStatus.AUTHORIZED)
        # Denied
        dec_proc = self.api.authorize_operation(agent_id="agent.geometry", tool_id="process_runner")
        self.assertEqual(dec_proc.status, AuthorizationStatus.DENIED)

    def test_23_conflict_resolution_deny_wins(self):
        # When a tool is in forbidden_tools, even if capability has matching permissions, it must DENY
        c = AgentContractV2(
            agent_id="agent.conflict.test", agent_type="TEST",
            capabilities=["geometry.generate_mesh"],
            permissions=[Permission.GEOMETRY_CREATE, Permission.ASSET_WRITE],
            allowed_tools=["mesh_generator"],
            forbidden_tools=["mesh_generator_special"]
        )
        self.api.contracts.register_contract(c)
        dec = self.api.authorize_operation(agent_id="agent.conflict.test", tool_id="mesh_generator_special")
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("TOOL_FORBIDDEN", dec.reason)

    def test_24_filesystem_governance_read_vs_write_delete(self):
        c = AgentContractV2(
            agent_id="agent.fs.reader", agent_type="TEST",
            permissions=[Permission.FILESYSTEM_READ],
            allowed_tools=["reference_analyzer"]
        )
        self.api.contracts.register_contract(c)
        dec = self.api.authorize_operation(
            agent_id="agent.fs.reader", tool_id="filesystem_deleter", operation="DELETE"
        )
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)

    def test_25_unregistered_agent_denied(self):
        dec = self.api.authorize_operation(agent_id="agent.nonexistent", tool_id="reference_analyzer")
        self.assertEqual(dec.status, AuthorizationStatus.DENIED)
        self.assertIn("NO_REGISTERED_CONTRACT", dec.reason)

    def test_26_tool_invocation_gate_authorized_execution(self):
        def my_mesh_op(inputs):
            return {"created_entities": ["WP_Receiver"], "artifacts": ["WP_Receiver.fbx"]}
            
        res = self.api.gate.invoke_tool(
            agent_id="agent.geometry",
            instance_id="agent.geometry.inst.001",
            tool_id="mesh_generator",
            capability_id="geometry.generate_mesh",
            inputs={"mesh_type": "receiver"},
            tool_callable=my_mesh_op,
            resource_id="AOE_Generated/WP_Receiver",
            operation="CREATE_MESH",
            expected_entities=["WP_Receiver"]
        )
        self.assertTrue(res.success)
        self.assertEqual(res.status, "COMPLETED")
        self.assertIn("WP_Receiver", res.created_entities)

    def test_27_tool_invocation_gate_false_success_prevention(self):
        # Tool returns success=True but fails to produce expected entity
        def fake_tool(inputs):
            return {"success": True, "created_entities": []}
            
        res = self.api.gate.invoke_tool(
            agent_id="agent.geometry",
            instance_id="agent.geometry.inst.001",
            tool_id="mesh_generator",
            capability_id="geometry.generate_mesh",
            inputs={"mesh_type": "receiver"},
            tool_callable=fake_tool,
            resource_id="AOE_Generated/WP_Receiver",
            operation="CREATE_MESH",
            expected_entities=["WP_Receiver_Missing"]
        )
        self.assertFalse(res.success)
        self.assertEqual(res.status, "VALIDATION_FAILED")
        self.assertIn("False Success Prevention", res.errors[0])

    def test_28_tool_invocation_gate_input_validation_failure(self):
        res = self.api.gate.invoke_tool(
            agent_id="agent.geometry",
            instance_id="agent.geometry.inst.001",
            tool_id="mesh_generator",
            capability_id="geometry.generate_mesh",
            inputs={"forbidden_param": "malicious_payload"},
            tool_callable=lambda x: {"created_entities": []}
        )
        self.assertFalse(res.success)
        self.assertEqual(res.status, "INVALID_INPUT")

    def test_29_agent_substitution_compatibility(self):
        # Register v1 and v2 with same capability
        c_v1 = AgentContractV2(
            agent_id="blender.agent.v1", agent_type="BLENDER",
            capabilities=["blender.assemble_asset"],
            permissions=[Permission.BLENDER_EXECUTE, Permission.ASSET_WRITE]
        )
        c_v2 = AgentContractV2(
            agent_id="blender.agent.v2", agent_type="BLENDER",
            capabilities=["blender.assemble_asset"],
            permissions=[Permission.BLENDER_EXECUTE, Permission.ASSET_WRITE]
        )
        self.api.contracts.register_contract(c_v1)
        self.api.contracts.register_contract(c_v2)
        
        candidates = self.api.contracts.find_by_capability("blender.assemble_asset")
        candidate_ids = [c.agent_id for c in candidates]
        self.assertIn("blender.agent.v1", candidate_ids)
        self.assertIn("blender.agent.v2", candidate_ids)

    def test_30_cancellation_releases_locks_and_resources(self):
        self.api.resources.acquire_ownership("WP_Target", "agent.geometry", "T_CANCEL")
        scope = self.api.resources.get_scope("WP_Target")
        self.assertEqual(scope.owner_agent_id, "agent.geometry")
        
        # Simulate cancellation cleanup
        self.api.resources.release_ownership("WP_Target", "agent.geometry")
        scope_after = self.api.resources.get_scope("WP_Target")
        self.assertIsNone(scope_after.owner_agent_id)

if __name__ == "__main__":
    unittest.main()
