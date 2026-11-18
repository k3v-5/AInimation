import time
from typing import List, Dict, Any, Optional
from ..core.critic_types import (
    ModificationLevel, CorrectionOperationType, RootCauseSeverity, CriticRiskLevel
)
from ..core.critic_schema import (
    RootCause, CorrectionPlan, CorrectionOp, PreservationContract
)

class CorrectionPlanner:
    @staticmethod
    def plan_correction(
        asset_id: str,
        root_causes: List[RootCause],
        locked_constraints: Optional[List[str]] = None
    ) -> CorrectionPlan:
        locked = locked_constraints or []
        plan_id = f"PLAN_CORR_{int(time.time()*1000)}"
        ops: List[CorrectionOp] = []
        total_cost = 0

        for rc in root_causes:
            # 1. Comprobar si la propiedad afectada está bloqueada por el usuario
            for prop in rc.affected_properties:
                for lock in locked:
                    if lock.lower() in prop.lower():
                        raise ValueError(f"CRITICAL_CONSTRAINT_VIOLATION: Cannot modify locked property '{prop}' (Constraint: {lock}).")

            # 2. Caso Techo (Forma vs Altura)
            if rc.cause_id == "RC_ROOF_GEOMETRY":
                if rc.severity == RootCauseSeverity.CRITICAL:
                    # Forma incorrecta -> REBUILD_COMPONENT
                    op = CorrectionOp(
                        operation_id=f"OP_{int(time.time()*1000)}_ROOF_REBUILD",
                        operation_type=CorrectionOperationType.REBUILD_COMPONENT,
                        target=f"{asset_id}.ROOF",
                        level=ModificationLevel.COMPONENT,
                        parameters={"roof_type": "GABLE"},
                        cost=5,
                        blast_radius="MEDIUM"
                    )
                else:
                    # Solo proporción/altura -> MODIFY_PROPERTY
                    op = CorrectionOp(
                        operation_id=f"OP_{int(time.time()*1000)}_ROOF_SCALE",
                        operation_type=CorrectionOperationType.SCALE_COMPONENT,
                        target=f"{asset_id}.ROOF",
                        level=ModificationLevel.PROPERTY,
                        parameters={"height_ratio": 0.30},
                        cost=2,
                        blast_radius="LOW"
                    )
                ops.append(op)
                total_cost += op.cost

            # 3. Caso Puerta (Propiedad aislada)
            elif rc.cause_id == "RC_DOOR_DIMENSION":
                op = CorrectionOp(
                    operation_id=f"OP_{int(time.time()*1000)}_DOOR_WIDTH",
                    operation_type=CorrectionOperationType.MODIFY_PROPERTY,
                    target=f"{asset_id}.DOOR.MAIN",
                    level=ModificationLevel.PROPERTY,
                    parameters={"width": 0.90},
                    cost=1,
                    blast_radius="LOW"
                )
                ops.append(op)
                total_cost += op.cost

        preservation = PreservationContract(
            preserve_properties=["dimensions.footprint", "wall_geometry", "window_positions"],
            target_modification="roof_and_openings_only"
        )

        risk = CriticRiskLevel.HIGH if total_cost > 10 else CriticRiskLevel.LOW

        return CorrectionPlan(
            plan_id=plan_id,
            target_asset=asset_id,
            operations=ops,
            preservation_contract=preservation,
            preconditions={"asset_exists": True},
            postconditions={"similarity_score_target": 0.90},
            estimated_cost=total_cost,
            risk=risk
        )
