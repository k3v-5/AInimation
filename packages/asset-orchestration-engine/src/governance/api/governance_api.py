from typing import Dict, Any, List, Optional
from ..core.permission_manager import Permission, RiskLevel, AuthorizationStatus, ResourceClassification
from ..core.agent_contract_v2 import AgentContractV2
from ..core.contract_registry import ContractRegistry
from ..policies.capability_policy import CapabilityRegistry, CapabilityDefinition
from ..policies.tool_policy import ToolRegistry, ToolDefinition
from ..policies.resource_policy import ResourceManager, ResourceScope
from ..policies.execution_policy import EmergencyStopController, PolicySnapshot
from ..audit.audit_logger import AuditLogger, AuditRecord
from ..engine.authorization_engine import AuthorizationEngine, AuthorizationRequest, AuthorizationDecision
from ..engine.mutation_guard import MutationGuard, MutationRecord
from ..engine.tool_invocation_gate import ToolInvocationGate, ToolInvocationResult

class AgentContractsToolGovernanceAPI:
    """
    Agent Contracts & Tool Governance API (F72).
    Unified public facade for managing agent contracts, tool policies, authorization checks,
    resource protections, mutation guards, tool invocation gates, and immutable audit logs.
    """
    def __init__(
        self,
        contract_registry: Optional[ContractRegistry] = None,
        capability_registry: Optional[CapabilityRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None,
        resource_manager: Optional[ResourceManager] = None,
        emergency_controller: Optional[EmergencyStopController] = None,
        audit_logger: Optional[AuditLogger] = None
    ):
        self.contracts = contract_registry or ContractRegistry()
        self.capabilities = capability_registry or CapabilityRegistry()
        self.tools = tool_registry or ToolRegistry()
        self.resources = resource_manager or ResourceManager()
        self.emergency = emergency_controller or EmergencyStopController()
        self.audit = audit_logger or AuditLogger()
        self.auth_engine = AuthorizationEngine(
            self.contracts, self.capabilities, self.tools, self.resources, self.emergency, self.audit
        )
        self.mutation_guard = MutationGuard(self.auth_engine)
        self.gate = ToolInvocationGate(self.auth_engine, self.mutation_guard, self.audit)
        self._register_default_agent_contracts()

    def _register_default_agent_contracts(self):
        defaults = [
            AgentContractV2(
                agent_id="agent.perception", agent_type="PERCEPTION",
                capabilities=["perception.analyze_reference", "perception.decompose_parts"],
                permissions=[Permission.REFERENCE_READ, Permission.REFERENCE_ANALYZE, Permission.ASSET_READ],
                allowed_tools=["reference_analyzer", "vision_decomposer"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                forbidden_operations=["DELETE", "MUTATE"]
            ),
            AgentContractV2(
                agent_id="agent.design_analysis", agent_type="DESIGN_ANALYSIS",
                capabilities=["design.compile_specification"],
                permissions=[Permission.PROJECT_READ, Permission.ASSET_READ],
                allowed_tools=["vas_compiler"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                forbidden_operations=["DELETE", "MUTATE"]
            ),
            AgentContractV2(
                agent_id="agent.strategy", agent_type="STRATEGY",
                capabilities=["strategy.plan_modeling"],
                permissions=[Permission.PROJECT_READ, Permission.ASSET_READ],
                allowed_tools=["strategy_planner"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                forbidden_operations=["DELETE", "MUTATE"]
            ),
            AgentContractV2(
                agent_id="agent.geometry", agent_type="GEOMETRY",
                capabilities=["geometry.generate_mesh"],
                permissions=[Permission.GEOMETRY_CREATE, Permission.GEOMETRY_MODIFY, Permission.ASSET_WRITE, Permission.ASSET_READ],
                allowed_tools=["mesh_generator", "bmesh_ops"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                write_scope=["AOE_Generated", "WP_*"]
            ),
            AgentContractV2(
                agent_id="agent.material", agent_type="MATERIAL",
                capabilities=["material.create_pbr"],
                permissions=[Permission.MATERIAL_CREATE, Permission.MATERIAL_MODIFY, Permission.ASSET_WRITE, Permission.ASSET_READ],
                allowed_tools=["shader_builder"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                write_scope=["AOE_Generated", "WP_*"]
            ),
            AgentContractV2(
                agent_id="agent.blender.execution", agent_type="BLENDER_EXECUTION",
                capabilities=["blender.assemble_asset", "blender.render_viewport"],
                permissions=[Permission.BLENDER_EXECUTE, Permission.BLENDER_SCENE_MODIFY, Permission.BLENDER_READ, Permission.ASSET_WRITE],
                allowed_tools=["blender_capability_api", "viewport_renderer"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                write_scope=["AOE_Generated", "WP_*"]
            ),
            AgentContractV2(
                agent_id="agent.visual.critic", agent_type="VISUAL_CRITIC",
                capabilities=["critic.evaluate_visuals", "critic.detect_defects"],
                permissions=[Permission.VISUAL_EVALUATE, Permission.REFERENCE_READ, Permission.ASSET_READ],
                allowed_tools=["visual_evaluator", "defect_clusterer"],
                forbidden_tools=["mesh_generator", "bmesh_ops", "filesystem_deleter", "process_runner"],
                forbidden_operations=["MUTATE", "DELETE", "WRITE"]
            ),
            AgentContractV2(
                agent_id="agent.qa.validator", agent_type="QA_VALIDATOR",
                capabilities=["qa.validate_geometry"],
                permissions=[Permission.ASSET_READ],
                allowed_tools=["topology_qa_scanner"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                forbidden_operations=["MUTATE", "DELETE", "WRITE"]
            ),
            AgentContractV2(
                agent_id="agent.correction", agent_type="CORRECTION",
                capabilities=["correction.apply_surgical_fix"],
                permissions=[Permission.GEOMETRY_MODIFY, Permission.ASSET_WRITE, Permission.ASSET_READ],
                allowed_tools=["impact_analyzer"],
                forbidden_tools=["filesystem_deleter", "process_runner"],
                write_scope=["AOE_Generated", "WP_*"]
            ),
            AgentContractV2(
                agent_id="agent.packaging", agent_type="PACKAGING",
                capabilities=["packaging.deliver_package"],
                permissions=[Permission.PACKAGE_ASSET, Permission.EXPORT_ASSET, Permission.ASSET_READ],
                allowed_tools=["package_sealer"],
                forbidden_tools=["filesystem_deleter", "process_runner"]
            )
        ]
        for c in defaults:
            if not self.contracts.get_contract(c.agent_id):
                self.contracts.register_contract(c)

    def authorize_operation(
        self,
        agent_id: str,
        tool_id: Optional[str] = None,
        capability_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        operation: Optional[str] = None,
        task_id: str = "T_UNKNOWN",
        orchestration_id: str = "ORCH_UNKNOWN",
        payload: Optional[Dict[str, Any]] = None
    ) -> AuthorizationDecision:
        req = AuthorizationRequest(
            agent_id=agent_id,
            tool_id=tool_id,
            capability_id=capability_id,
            resource_id=resource_id,
            operation=operation,
            task_id=task_id,
            orchestration_id=orchestration_id,
            payload=payload or {}
        )
        return self.auth_engine.authorize(req)

    def emergency_stop(self, reason: str = "ADMIN_EMERGENCY_HALT"):
        self.emergency.activate(reason)

    def resume_from_emergency_stop(self):
        self.emergency.deactivate()

    def create_policy_snapshot(self, snapshot_id: str) -> PolicySnapshot:
        contracts_map = {c.agent_id: c.contract_version for c in self.contracts.list_contracts()}
        return PolicySnapshot(
            snapshot_id=snapshot_id,
            contract_versions=contracts_map,
            emergency_stop_active=self.emergency.is_active
        )
