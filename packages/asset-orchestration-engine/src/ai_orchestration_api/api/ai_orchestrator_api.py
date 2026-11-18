from typing import Dict, Any, List, Optional
from ..core.agent_types import (
    ToolCategory, PermissionLevel, AgentOperationStatus,
    AgentDecision, AgentAssetStatus, AgentComponentStatus, AgentErrorCode
)
from ..core.agent_schema import (
    ToolDefinition, AgentToolResponse, AgentPlan, AgentAssetContext,
    AgentDiagnostic, AgentCorrectionItem, AgentTaskBudget
)
from ..facade.agent_facade import AgentFacade

class AIOrchestratorAPI:
    """
    AI Orchestration API & Agent Contract (AOE v43)
    
    Regla Fundamental:
    LA IA ES EL DIRECTOR DEL SISTEMA, NO EL OPERADOR DE BLENDER.
    ANTIGRAVITY INTERACTÚA EXCLUSIVAMENTE MEDIANTE HERRAMIENTAS ESTRUCTURADAS
    CON ESQUEMAS TIPADOS, PERMISOS CLAROS, CONTROL DE PRESUPUESTO Y MEMORIA DE CONVERGENCIA.
    """
    def __init__(self, permission: PermissionLevel = PermissionLevel.MODIFY):
        self.facade = AgentFacade(permission=permission)

    # 1. Discovery
    def get_capabilities(self) -> AgentToolResponse:
        return self.facade.get_capabilities()

    def list_generators(self) -> AgentToolResponse:
        return self.facade.list_generators()

    # 2. Planning
    def create_plan(self, asset_id: str, changes: Dict[str, Any]) -> AgentToolResponse:
        return self.facade.create_plan(asset_id, changes)

    def explain_plan(self, plan_id: str) -> AgentToolResponse:
        return self.facade.explain_plan(plan_id)

    # 3. Asset
    def create_asset(self, asset_id: str, parameters: Dict[str, Any]) -> AgentToolResponse:
        return self.facade.create_asset(asset_id, parameters)

    def update_asset(self, asset_id: str, changes: Dict[str, Any]) -> AgentToolResponse:
        return self.facade.update_asset(asset_id, changes)

    def delete_asset(self, asset_id: str) -> AgentToolResponse:
        return self.facade.delete_asset(asset_id)

    # 4. Inspection
    def inspect_asset(self, asset_id: str) -> AgentToolResponse:
        return self.facade.inspect_asset(asset_id)

    # 5. Validation & Critic
    def run_visual_critic(self, asset_id: str, ref_spec: Any, aspect_ratio: float = 1.80, roof_ratio: float = 0.43) -> AgentToolResponse:
        return self.facade.run_visual_critic(asset_id, ref_spec, aspect_ratio, roof_ratio)

    # 6. Correction
    def apply_correction(self, asset_id: str, param_name: str, new_value: Any) -> AgentToolResponse:
        return self.facade.apply_correction(asset_id, param_name, new_value)

    # 7. Recovery
    def get_operation_status(self, op_id: str) -> AgentToolResponse:
        return self.facade.get_operation_status(op_id)

    def cancel_operation(self, op_id: str) -> AgentToolResponse:
        return self.facade.cancel_operation(op_id)
