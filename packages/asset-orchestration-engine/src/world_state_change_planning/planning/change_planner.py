import hashlib
import json
import time
from typing import Dict, Any, List
from ..core.world_schema import ChangeRequest, ChangePlan, DryRunResult, WorldState
from ..state.world_state_manager import WorldDependencyGraph
from .target_resolver import TargetResolver, ConstraintRegistry

class ChangePlanner:
    """
    Change Planner (AOE v33):
    Interpreta el cambio solicitado, verifica restricciones, calcula dependencias mínimas
    y genera un plan atómico con soporte de Dry-Run.
    """
    @staticmethod
    def plan_change(request: ChangeRequest, world_state: WorldState) -> ChangePlan:
        # 1. Resolver Objetivo
        target_id = request.target_asset_id
        if not target_id or target_id not in world_state.assets:
            target_id = TargetResolver.resolve_target(request.target_asset_id or "house", world_state)

        asset = world_state.assets[target_id]

        # 2. Validar Restricciones
        ConstraintRegistry.validate_change_against_constraints(asset, request.property_path, request.new_value)

        # 3. Análisis de Impacto (Minimal Change Principle)
        impact = WorldDependencyGraph.get_impact(request.property_path)
        affected = impact["affected"]
        unaffected = impact["unaffected"]

        plan_id = f"PLAN_{int(time.time()*1000)}"
        change_desc = f"{request.operation.value} {target_id}.{request.property_path} -> {request.new_value}"

        raw_payload = f"{target_id}:{request.property_path}:{request.new_value}:{affected}"
        plan_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()[:16]

        return ChangePlan(
            plan_id=plan_id,
            target_asset_id=target_id,
            requested_changes=[change_desc],
            affected_components=affected,
            unaffected_components=unaffected,
            complexity_score=20,
            is_approved=True,
            plan_hash=plan_hash
        )

    @classmethod
    def dry_run(cls, request: ChangeRequest, world_state: WorldState) -> DryRunResult:
        plan = cls.plan_change(request, world_state)
        return DryRunResult(
            change_plan=plan,
            what_will_change=[f"[+] {c}" for c in plan.affected_components],
            what_will_not_change=[f"[-] {c}" for c in plan.unaffected_components],
            warnings=[],
            estimated_cost_ms=45.0,
            status="PASS"
        )
