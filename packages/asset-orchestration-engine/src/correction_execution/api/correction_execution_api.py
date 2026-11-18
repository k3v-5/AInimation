import uuid
from typing import Dict, Any, List, Optional
from ..core.correction_plan import CorrectionPlan, CorrectionOperation, OperationType
from ..core.object_registry import ComponentRegistry, RegisteredComponent
from ..risk.permission_manager import ExecutionMode
from ..providers.blender_provider import IBlenderProvider
from ..execution.mutation_executor import MutationExecutor

class CorrectionExecutionAPI:
    """
    Correction Execution & Safe Mutation API (AOE v11)
    
    Regla Fundamental:
    NO CORREGIR POR INTUICIÓN. CORREGIR A PARTIR DE UN DIAGNÓSTICO VALIDADO.
    NO DESTRUCTIVE ACTION WITHOUT SNAPSHOT + PERMISSION + VALIDATION + ROLLBACK.
    """
    def __init__(self, provider: IBlenderProvider, execution_mode: ExecutionMode = ExecutionMode.BALANCED):
        self.provider = provider
        self.registry = ComponentRegistry()
        self.mode = execution_mode
        self.executor = MutationExecutor(provider, self.registry, execution_mode=execution_mode)

    def register_component(
        self,
        component_id: str,
        asset_id: str,
        object_id: str,
        semantic_role: str,
        is_locked: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        comp = RegisteredComponent(
            component_id=component_id,
            asset_id=asset_id,
            object_id=object_id,
            semantic_role=semantic_role,
            is_locked=is_locked,
            metadata=metadata or {}
        )
        self.registry.register(comp)

    def lock_component(self, component_id: str, locked: bool = True):
        self.registry.lock_component(component_id, locked)

    def execute_correction(
        self,
        asset_id: str,
        operations: List[Dict[str, Any]],
        protected_components: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        op_objs: List[CorrectionOperation] = []
        for idx, op in enumerate(operations):
            op_type_enum = OperationType(op["type"])
            op_objs.append(CorrectionOperation(
                operation_id=op.get("id", f"op_{idx}_{op['type']}"),
                operation_type=op_type_enum,
                target=op["target"],
                parameters=op.get("parameters", {}),
                reason=op.get("reason", ""),
                risk=op.get("risk", "LOW"),
                reversible=op.get("reversible", True)
            ))

        plan = CorrectionPlan(
            plan_id=f"plan_{uuid.uuid4().hex[:6]}",
            asset_id=asset_id,
            goal_id="visual_goal_01",
            source_verification_id="verif_01",
            operations=op_objs
        )

        return self.executor.execute_plan(plan, protected_components=protected_components, dry_run=dry_run)
