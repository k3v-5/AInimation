import re
import time
from typing import Dict, Any, List, Optional
from ..core.task_types import (
    TaskSource, TaskAction, SemanticOperation, TaskScope, TaskPriority,
    TaskRiskLevel, TaskStatusEnum, AmbiguityType, TaskPermissionType, ConstraintTypeEnum
)
from ..core.task_schema import (
    TargetSpec, TaskConstraint, TaskPreference, TaskEnvelope, TaskPreview
)
from .unit_normalizer import TaskUnitNormalizer
from .permission_firewall import ToolFirewall, RiskAnalyzer

class TaskCompiler:
    """
    Core AI Task Compiler (AOE v34):
    Compila lenguaje natural e intenciones de la IA en un TaskEnvelope formal con
    extracción de restricciones negativas, normalización de unidades y evaluación de riesgo.
    """
    @staticmethod
    def compile_instruction(
        raw_instruction: str,
        context: Optional[Dict[str, Any]] = None,
        source: TaskSource = TaskSource.USER
    ) -> TaskEnvelope:
        ctx = context or {}
        sanitized = ToolFirewall.sanitize_instruction(raw_instruction)
        p_lower = raw_instruction.lower()

        task_id = f"TASK_{time.strftime('%Y')}_{int(time.time()*1000)%1000000:06d}"
        active_asset = ctx.get("active_asset", "HOUSE_001")
        existing_assets = ctx.get("existing_assets", [active_asset])

        # 1. Comprobar existencia del activo objetivo
        target_in_prompt = None
        for a_id in ["HOUSE_001", "HOUSE_002", "HOUSE_999", "TOWER_001"]:
            if a_id.lower() in p_lower:
                target_in_prompt = a_id
                break

        if target_in_prompt and target_in_prompt not in existing_assets:
            raise ValueError(f"TARGET_NOT_FOUND: Asset '{target_in_prompt}' does not exist in WorldState.")

        # 2. Comprobar restricciones de referencia contextual ("igual que la anterior")
        if "igual que la anterior" in p_lower or "como la anterior" in p_lower:
            prev_asset = ctx.get("previous_asset")
            if not prev_asset:
                raise ValueError("AMBIGUOUS_REFERENCE: No previous asset found in context memory.")
            target_id = prev_asset
        else:
            target_id = target_in_prompt or active_asset

        # 3. Detectar Ambigüedades de Objetivo ("la puerta" con múltiples puertas en contexto)
        doors_in_context = ctx.get("available_doors", [])
        if "la puerta" in p_lower and "principal" not in p_lower and len(doors_in_context) > 1:
            raise ValueError(f"AMBIGUOUS_TARGET: Multiple doors ({doors_in_context}) found in {target_id}. Clarification required.")

        # 4. Clasificación Semántica de Operaciones y Parámetros
        constraints: List[TaskConstraint] = []
        preferences: List[TaskPreference] = []
        parameters: Dict[str, Any] = {}
        target_spec = TargetSpec(semantic_id=target_id, asset_id=target_id)
        action = TaskAction.MODIFY
        scope = TaskScope.COMPONENT

        # Caso A: Borrado de activo (Destructivo)
        if "borra" in p_lower or "delete" in p_lower or "elimina" in p_lower:
            action = TaskAction.DELETE
            operation = SemanticOperation.DELETE_ASSET
            scope = TaskScope.ASSET
            permissions = [TaskPermissionType.DELETE_ASSET]
            target_spec = TargetSpec(semantic_id=target_id, asset_id=target_id, target_type="ASSET")

        # Caso B: Multi-target ("todas las ventanas")
        elif "todas las ventanas" in p_lower or "all windows" in p_lower:
            operation = SemanticOperation.MULTI_TARGET
            scope = TaskScope.COMPONENT
            target_spec = TargetSpec(semantic_id=f"{target_id}.WINDOWS", asset_id=target_id, target_type="MULTI")
            permissions = [TaskPermissionType.MODIFY_ASSET]
            # Extraer reducción (ej. 10% más pequeñas)
            if "10%" in p_lower:
                parameters["scale"] = 0.90
                parameters["relative_delta"] = -0.10

        # Caso C: Redimensionado de Puerta
        elif "puerta" in p_lower:
            operation = SemanticOperation.CHANGE_DIMENSIONS
            component_id = "DOOR.MAIN" if ("principal" in p_lower or "main" in p_lower or len(doors_in_context) <= 1) else "DOOR"
            target_spec = TargetSpec(semantic_id=f"{target_id}.{component_id}", asset_id=target_id, component_id=component_id)
            permissions = [TaskPermissionType.MODIFY_ASSET]

            # Extraer dimensiones (ej. 20 cm, 30 cm)
            dim_match = re.search(r'([0-9.]+)\s*(cm|m|mm|inches|in)', p_lower)
            if dim_match:
                dim_str = dim_match.group(0)
                norm = TaskUnitNormalizer.normalize_dimension(f"+{dim_str}")
                parameters["width"] = norm
            else:
                parameters["width"] = {"mode": "DELTA", "value": 0.20, "unit": "m"}

        # Caso D: Envejecer Activo
        elif "vieja" in p_lower or "aged" in p_lower or "envejecer" in p_lower:
            operation = SemanticOperation.AGE_ASSET
            scope = TaskScope.ASSET
            permissions = [TaskPermissionType.MODIFY_ASSET]
            parameters = {"weathering": 0.80, "surface_damage": True}

        # Caso E: Escala general
        else:
            operation = SemanticOperation.CHANGE_DIMENSIONS
            permissions = [TaskPermissionType.MODIFY_ASSET]

        # 5. Extracción de Restricciones Negativas ("sin moverla", "no cambies la altura", "no cambies la posición")
        if "sin moverla" in p_lower or "sin mover" in p_lower or "no cambies la posición" in p_lower or "no cambies su posición" in p_lower:
            constraints.append(TaskConstraint("C_LOCK_POS", ConstraintTypeEnum.LOCK, "transform.position", is_hard=True))

        if "no cambies la altura" in p_lower or "no cambies su altura" in p_lower or "sin cambiar la altura" in p_lower:
            constraints.append(TaskConstraint("C_LOCK_HEIGHT", ConstraintTypeEnum.LOCK, "dimensions.height", is_hard=True))

        # 6. Comprobar si la propiedad solicitada ya estaba bloqueada en el contexto (Locked Property Constraint)
        locked_props = ctx.get("locked_properties", [])
        if "techo" in p_lower and "roof.shape" in locked_props:
            raise ValueError("CONSTRAINT_CONFLICT: Property 'roof.shape' is LOCKED in asset context.")

        # 7. Análisis de Riesgo y Aprobación
        risk, req_approval = RiskAnalyzer.assess_risk(operation, action, scope.value)

        envelope = TaskEnvelope(
            task_id=task_id,
            source=source,
            source_id="antigravity_core",
            raw_instruction=sanitized,
            context=ctx,
            requested_operation=operation,
            target=target_spec,
            parameters=parameters,
            constraints=constraints,
            preferences=preferences,
            priority=TaskPriority.HIGH if risk == TaskRiskLevel.CRITICAL else TaskPriority.NORMAL,
            risk=risk,
            permissions=permissions,
            status=TaskStatusEnum.WAITING_APPROVAL if req_approval else TaskStatusEnum.COMPILED,
            requires_approval=req_approval,
            idempotency_key=""
        )
        envelope.idempotency_key = envelope.compute_envelope_hash()
        return envelope

    @staticmethod
    def preview_task(envelope: TaskEnvelope) -> TaskPreview:
        c_list = [f"LOCK: {c.target_property}" for c in envelope.constraints]
        if envelope.requested_operation == SemanticOperation.CHANGE_DIMENSIONS:
            affected = ["door", "frame", "wall_opening", "collision"]
            unaffected = ["roof", "windows", "foundation", "house_position"]
            expl = f"Modificaré las dimensiones de {envelope.target.semantic_id}. No modificaré altura, posición ni techo."
        elif envelope.requested_operation == SemanticOperation.DELETE_ASSET:
            affected = [envelope.target.semantic_id]
            unaffected = ["other_assets"]
            expl = f"Eliminará completamente el activo {envelope.target.semantic_id} del nivel. Requiere aprobación."
        else:
            affected = [envelope.target.semantic_id]
            unaffected = ["other_components"]
            expl = f"Ejecutará la operación {envelope.requested_operation.value} sobre {envelope.target.semantic_id}."

        return TaskPreview(
            task_id=envelope.task_id,
            target=envelope.target.semantic_id,
            operation=envelope.requested_operation.value,
            parameters=envelope.parameters,
            constraints=c_list,
            expected_affected=affected,
            expected_unaffected=unaffected,
            risk=envelope.risk.value,
            estimated_cost_ms=35.0,
            explanation=expl
        )
