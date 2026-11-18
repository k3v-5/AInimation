"""
Replanner and fallback recovery models.
UAF-81.2 Sections 31, 32, 33, 34, 83, 84, 85.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .generation_plan import GenerationPlan
from .plan_node import GenerationPlanNode
from ...core.diagnostics.errors import GenerationError


@dataclass
class ReplanRequest:
    failed_node_id: str
    failure_reason: str
    current_plan: GenerationPlan
    partial_artifacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ReplanningResult:
    is_success: bool
    updated_plan: Optional[GenerationPlan] = None
    degradation_report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class Replanner:
    """
    Recovers from runtime node failure by re-evaluating fallbacks with explicit degradation logging.
    """
    @classmethod
    def replan(cls, request: ReplanRequest) -> ReplanningResult:
        failed_id = request.failed_node_id
        plan = request.current_plan

        if failed_id not in plan.nodes:
            return ReplanningResult(
                is_success=False,
                error_message=f"Node '{failed_id}' not found in current plan.",
            )

        failed_node = plan.nodes[failed_id]
        if not failed_node.fallbacks:
            return ReplanningResult(
                is_success=False,
                error_message=f"Node '{failed_id}' has no configured fallbacks.",
            )

        # Select next fallback implementation
        next_implementation = failed_node.fallbacks[0]
        remaining_fallbacks = failed_node.fallbacks[1:]

        # NO SILENT QUALITY LOSS (Section 34)
        degradation_report = {
            "node_id": failed_id,
            "failed_implementation": failed_node.implementation,
            "fallback_implementation": next_implementation,
            "reason": request.failure_reason,
            "severity": "WARNING",
            "affected_requirements": [failed_node.capability],
        }

        # Create updated node
        updated_node = GenerationPlanNode(
            node_id=failed_node.node_id,
            operation=failed_node.operation,
            capability=failed_node.capability,
            implementation=next_implementation,
            inputs=failed_node.inputs,
            outputs=failed_node.outputs,
            dependencies=failed_node.dependencies,
            resource_budget=failed_node.resource_budget,
            quality_requirement=failed_node.quality_requirement,
            fallbacks=remaining_fallbacks,
            failure_policy=failed_node.failure_policy,
        )

        updated_nodes = dict(plan.nodes)
        updated_nodes[failed_id] = updated_node

        updated_plan = GenerationPlan(
            plan_id=f"{plan.plan_id}_v2",
            asset_id=plan.asset_id,
            strategy_id=plan.strategy_id,
            specification_hash=plan.specification_hash,
            nodes=updated_nodes,
            execution_order=plan.execution_order,
            estimated_cost=plan.estimated_cost,
            expected_quality=max(0.1, plan.expected_quality - 0.1),  # Degraded quality recorded
            risks=plan.risks + [f"Fallback applied on {failed_id}"],
            fallbacks={nid: n.fallbacks for nid, n in updated_nodes.items() if n.fallbacks},
            version="2.0.0",
            metadata=dict(plan.metadata, degradation=degradation_report),
        )

        return ReplanningResult(
            is_success=True,
            updated_plan=updated_plan,
            degradation_report=degradation_report,
        )
