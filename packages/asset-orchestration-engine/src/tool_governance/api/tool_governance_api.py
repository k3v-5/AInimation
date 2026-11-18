from typing import Optional, List, Dict, Any
from ..core.governance_status import ToolRisk, PermissionType, ActionLifecycle, ActionScope
from ..core.governance_schema import (
    ToolDefinition, ActionProposal, ExecutionBudget, NormalizedToolResult, ExecutionReport
)
from ..execution.tool_gateway import AIToolGateway
from ...correction_execution.providers.blender_provider import IBlenderProvider
from ...correction_execution.providers.mock_blender_provider import MockBlenderProvider
from ...intent_compiler.core.intent_schema import BuildSpecification

class ToolGovernanceAPI:
    """
    AI Execution Policy & Tool Governance API (AOE v22)
    
    Regla Fundamental:
    CORREA ARQUITECTÓNICA DE LA IA:
    OBSERVA, PROPONE Y PLANIFICA, PERO NUNCA TOCA BLENDER DIRECTAMENTE.
    TODA ACCIÓN ES EVALUADA CONTRA PERMISOS, LÍMITES, RESTRICCIONES, ANTI-DUPLICADOS Y POST-VERIFICADA.
    """
    def __init__(self, provider: Optional[IBlenderProvider] = None):
        self.gateway = AIToolGateway(provider)

    def submit_action_proposal(
        self,
        agent_id: str,
        proposal: ActionProposal,
        spec: Optional[BuildSpecification] = None,
        simulate_blender_state_failure: bool = False
    ) -> NormalizedToolResult:
        return self.gateway.submit_proposal(
            agent_id=agent_id,
            proposal=proposal,
            spec=spec,
            simulate_blender_state_failure=simulate_blender_state_failure
        )

    def set_budget(self, budget: ExecutionBudget):
        self.gateway.budget = budget

    def get_budget(self) -> ExecutionBudget:
        return self.gateway.budget

    def generate_report(self, task_id: str) -> ExecutionReport:
        b = self.gateway.budget
        return ExecutionReport(
            task_id=task_id,
            status="COMPLETED",
            total_proposals=len(self.gateway.logs),
            executed_actions=b.used_tool_calls,
            rejected_actions=len([l for l in self.gateway.logs if "REJECTED" in l or "DENIED" in l or "EXCEEDED" in l]),
            rolled_back_actions=len([l for l in self.gateway.logs if "Rolled back" in l]),
            budget_used={"tool_calls": b.used_tool_calls, "rebuilds": b.used_asset_rebuilds},
            logs=list(self.gateway.logs)
        )
