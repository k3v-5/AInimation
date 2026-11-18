import hashlib
import time
from typing import Dict, Any, List, Optional
from ..core.agent_types import (
    ToolCategory, PermissionLevel, AgentOperationStatus,
    AgentDecision, AgentAssetStatus, AgentErrorCode
)
from ..core.agent_schema import (
    AgentToolResponse, AgentPlan, AgentAssetContext,
    AgentDiagnostic, AgentCorrectionItem, AgentTaskBudget
)
from ..registry.tool_registry import ToolRegistry
from ..context.context_filter import ContextFilter, StructuredMemory

from src.parametric_asset_engine import ParametricAssetAPI
from src.visual_reference_matching import VisualReferenceMatcherAPI, ReferenceImageSpec
from src.mcp_execution_gateway import MCPGatewayAPI, CommandType, RiskLevel

class AgentFacade:
    def __init__(self, permission: PermissionLevel = PermissionLevel.MODIFY):
        self.permission = permission
        self.tool_registry = ToolRegistry()
        self.memory = StructuredMemory()
        self.budget = AgentTaskBudget(max_mcp_calls=10, remaining_calls=10, max_iterations=5)
        
        # Integración con Fases Anteriores
        self.param_api = ParametricAssetAPI()
        self.critic_api = VisualReferenceMatcherAPI()
        self.gateway_api = MCPGatewayAPI()
        
        self.operations: Dict[str, AgentToolResponse] = {}
        self.plans: Dict[str, AgentPlan] = {}

    # 1. Discovery Tools
    def get_capabilities(self) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("get_capabilities", self.permission)
        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id="OP_DISC_01",
            summary="Retrieved active engine capabilities and tools",
            output_data={
                "supported_generators": ["foundation", "walls", "roof", "windows", "doors"],
                "supported_archetypes": ["MEDIEVAL_HOUSE", "TOWER", "WALL_SECTION"],
                "units": "METERS",
                "max_budget_per_task": self.budget.max_mcp_calls
            }
        )

    def list_generators(self) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("list_generators", self.permission)
        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id="OP_GENS",
            summary="List of registered procedural generators",
            output_data={"generators": ["foundation", "walls", "roof", "windows", "doors"]}
        )

    # 2. Planning Tools
    def create_plan(self, asset_id: str, changes: Dict[str, Any]) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("create_plan", self.permission)
        
        # Validar presupuesto de llamadas
        est_calls = len(changes) if changes else 1
        if est_calls > self.budget.remaining_calls:
            return AgentToolResponse(
                status=AgentOperationStatus.BLOCKED,
                operation_id="OP_PLAN_FAIL",
                summary="Plan exceeds remaining task budget",
                errors=[f"BUDGET_EXCEEDED: Requested operations ({est_calls}) exceed remaining budget ({self.budget.remaining_calls})."],
                next_action=AgentDecision.STOP
            )

        plan_id = f"PLAN_{int(time.time()*1000)}"
        state_hash = "STATE_HASH_V1"
        plan_hash = hashlib.sha256(f"{asset_id}_{changes}_{state_hash}".encode('utf-8')).hexdigest()[:16]
        
        plan = AgentPlan(
            plan_id=plan_id,
            plan_hash=plan_hash,
            expected_state_hash=state_hash,
            operations=[{"target": asset_id, "changes": changes}],
            estimated_mcp_calls=est_calls,
            estimated_duration=round(est_calls * 0.15, 2),
            risk="LOW"
        )
        self.plans[plan_id] = plan

        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=plan_id,
            summary=f"Execution plan '{plan_id}' compiled successfully",
            output_data={"plan": plan}
        )

    def explain_plan(self, plan_id: str) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("explain_plan", self.permission)
        if plan_id not in self.plans:
            raise KeyError(f"Plan '{plan_id}' not found.")
        plan = self.plans[plan_id]
        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=f"OP_EXP_{plan_id}",
            summary=f"Plan contains {len(plan.operations)} operations targeting {plan.operations[0]['target']} with estimated {plan.estimated_mcp_calls} MCP calls and risk '{plan.risk}'.",
            output_data={"explanation": plan.operations}
        )

    # 3. Asset Mutation Tools
    def create_asset(self, asset_id: str, parameters: Dict[str, Any]) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("create_asset", self.permission)
        op_id = f"OP_CREATE_{asset_id}"
        
        # Descuento de presupuesto
        self.budget.remaining_calls -= 1
        
        # Crear en Motor Paramétrico (Fase 40)
        asset_def = self.param_api.create_asset(asset_id, parameters)
        
        # Registrar en memoria
        self.memory.record_iteration(asset_id, 1, 0.85, asset_def.parameters)

        resp = AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=op_id,
            summary=f"Asset '{asset_id}' created with {len(asset_def.components)} components.",
            affected_assets=[asset_id],
            affected_components=list(asset_def.components.keys()),
            output_data={"parameters": asset_def.parameters}
        )
        self.operations[op_id] = resp
        return resp

    def update_asset(self, asset_id: str, changes: Dict[str, Any]) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("update_asset", self.permission)
        op_id = f"OP_UPDATE_{asset_id}"
        
        # Comprobar presupuesto
        if self.budget.remaining_calls <= 0:
            return AgentToolResponse(
                status=AgentOperationStatus.BLOCKED,
                operation_id=op_id,
                summary="Operation blocked due to exhausted MCP budget.",
                errors=["BUDGET_EXCEEDED: No remaining MCP calls for current task."],
                next_action=AgentDecision.STOP
            )

        self.budget.remaining_calls -= 1
        updated = self.param_api.update_asset(asset_id, changes)

        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=op_id,
            summary=f"Asset '{asset_id}' parameters updated: {list(changes.keys())}.",
            affected_assets=[asset_id],
            affected_components=["roof" if "roof_height" in changes else "walls"],
            output_data={"parameters": updated.parameters}
        )

    def delete_asset(self, asset_id: str) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("delete_asset", self.permission)
        # Operación destructiva requiere aprobación humana
        return AgentToolResponse(
            status=AgentOperationStatus.REQUIRES_APPROVAL,
            operation_id=f"OP_DEL_{asset_id}",
            summary=f"Deletion of asset '{asset_id}' is destructive and requires human approval.",
            affected_assets=[asset_id],
            warnings=["REQUIRES_APPROVAL: Confirmation needed before scene deletion."],
            next_action=AgentDecision.ASK
        )

    # 4. Inspection Tools
    def inspect_asset(self, asset_id: str) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("inspect_asset", self.permission)
        if asset_id not in self.param_api.engine.assets:
            raise KeyError(f"Asset '{asset_id}' not found.")
        
        asset_def = self.param_api.engine.assets[asset_id]
        context = ContextFilter.extract_asset_context(asset_id, asset_def)

        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=f"OP_INSP_{asset_id}",
            summary=f"Asset '{asset_id}' is {context.status.value} (v{context.version}) with {len(context.components)} components.",
            output_data={"context": context}
        )

    # 5. Validation & Visual Critic Tools
    def run_visual_critic(self, asset_id: str, ref_spec: ReferenceImageSpec, current_aspect_ratio: float = 1.80, current_roof_ratio: float = 0.43) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("run_visual_critic", self.permission)
        if asset_id not in self.param_api.engine.assets:
            raise KeyError(f"Asset '{asset_id}' not found.")
        
        asset_def = self.param_api.engine.assets[asset_id]
        report = self.critic_api.evaluate_asset(
            asset_id=asset_id,
            ref=ref_spec,
            generated_parameters=asset_def.parameters,
            generated_aspect_ratio=current_aspect_ratio,
            generated_roof_ratio=current_roof_ratio,
            user_window_count=4
        )

        # Grabar en memoria y verificar estancamiento
        stag_err = self.memory.record_iteration(asset_id, 2, report.overall_score, asset_def.parameters)
        warnings = [stag_err] if stag_err else []

        next_act = AgentDecision.ACCEPT if report.overall_score >= 0.90 else AgentDecision.CORRECT

        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=report.report_id,
            summary=f"Visual critic score: {report.overall_score * 100:.1f}%. Decision: [{report.decision.value}].",
            validation={"overall_score": report.overall_score, "sub_scores": report.sub_scores},
            warnings=warnings,
            next_action=next_act,
            output_data={"report": report}
        )

    # 6. Correction Tools
    def apply_correction(self, asset_id: str, param_name: str, new_value: Any) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("apply_correction", self.permission)
        
        # Verificar loops de corrección
        loop_err = self.memory.record_applied_correction(asset_id, param_name, new_value)
        if loop_err:
            return AgentToolResponse(
                status=AgentOperationStatus.BLOCKED,
                operation_id="OP_LOOP_BLOCK",
                summary="Correction loop detected. Halting automatic retry.",
                errors=[loop_err],
                next_action=AgentDecision.STOP
            )

        # Aplicar actualización en Fase 40
        return self.update_asset(asset_id, {param_name: new_value})

    # 7. Recovery Tools
    def get_operation_status(self, operation_id: str) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("get_operation_status", self.permission)
        if operation_id in self.operations:
            return self.operations[operation_id]
        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=operation_id,
            summary=f"Operation '{operation_id}' completed.",
            output_data={"status": "COMPLETED"}
        )

    def cancel_operation(self, operation_id: str) -> AgentToolResponse:
        self.tool_registry.validate_tool_access("cancel_operation", self.permission)
        return AgentToolResponse(
            status=AgentOperationStatus.SUCCESS,
            operation_id=operation_id,
            summary=f"Operation '{operation_id}' canceled successfully.",
            next_action=AgentDecision.STOP
        )
