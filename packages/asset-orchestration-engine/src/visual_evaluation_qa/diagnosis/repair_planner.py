import uuid
from typing import List, Optional
from ..core.evaluation_schema import (
    EvaluationReport, RepairPlan, RepairCandidate, RepairScope
)

class RepairPlanner:
    @staticmethod
    def create_repair_plan(report: EvaluationReport) -> Optional[RepairPlan]:
        if report.is_pass or not report.failures:
            return None

        candidates: List[RepairCandidate] = []
        for fail in report.failures:
            candidates.append(RepairCandidate(
                repair_id=f"rep_{uuid.uuid4().hex[:6]}",
                target_entity=fail.entity_id,
                scope=fail.suggested_scope,
                component_id=fail.component_id,
                parameter_name=fail.parameter_name,
                current_value=fail.actual,
                target_value=fail.expected,
                expected_improvement=0.25,
                cost=1.0 if fail.suggested_scope == RepairScope.PARAMETER else 2.5
            ))

        # Ordenar por ratio beneficio / coste (PARAMETER primero)
        candidates.sort(key=lambda c: c.expected_improvement / c.cost, reverse=True)

        return RepairPlan(
            plan_id=f"rplan_{uuid.uuid4().hex[:6]}",
            target_entity=report.target_id,
            candidates=candidates,
            estimated_rebuild_ratio=0.10 if candidates[0].scope == RepairScope.PARAMETER else 0.25
        )
