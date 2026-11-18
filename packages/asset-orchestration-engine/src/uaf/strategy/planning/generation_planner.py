"""
GenerationPlanner transforms resolved specifications into validated GenerationPlans.
UAF-81.2 Sections 19, 20, 21, 25, 35, 60, 61, 91.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from ...core.diagnostics.errors import GenerationError, CapabilityError
from ...core.operations.operation_types import OperationType
from ...core.context.resource_budget import ResourceBudget
from ...intelligence.compiler.resolved_specification import ResolvedAssetSpecification
from ...intelligence.compiler.capability_gap import CapabilityGapReport
from ...intelligence.dependencies.dependency_graph import DependencyGraph
from ..strategies.strategy_registry import StrategyRegistry
from ..strategies.generation_strategy import GenerationStrategy
from ..implementations.implementation_registry import ImplementationRegistry
from ..evaluation.strategy_evaluator import StrategyEvaluator
from ..evaluation.strategy_score import StrategyDecisionTrace
from .plan_node import GenerationPlanNode
from .generation_plan import GenerationPlan


@dataclass
class PlanningResult:
    is_success: bool
    plan: Optional[GenerationPlan] = None
    gap_report: Optional[CapabilityGapReport] = None
    decision_trace: Optional[StrategyDecisionTrace] = None
    error_message: Optional[str] = None


class GenerationPlanner:
    """
    Central planning engine synthesizing executable GenerationPlans from semantic specifications.
    """
    def __init__(
        self,
        strategy_registry: Optional[StrategyRegistry] = None,
        implementation_registry: Optional[ImplementationRegistry] = None,
    ):
        self.strategies = strategy_registry or StrategyRegistry()
        self.implementations = implementation_registry or ImplementationRegistry()

    def plan(
        self,
        spec: ResolvedAssetSpecification,
        available_capabilities: Optional[Set[str]] = None,
        resource_budget: Optional[ResourceBudget] = None,
    ) -> PlanningResult:
        asset_id = spec.original_specification.identity.asset_id
        asset_type = spec.original_specification.identity.asset_type

        # Build available capabilities set from implementation registry if not provided
        if available_capabilities is None:
            available_caps = {imp.capability_id for imp in self.implementations.list() if imp.is_available}
        else:
            available_caps = set(available_capabilities)

        # Step 1: Find candidate strategies
        candidates = self.strategies.find_for_asset(asset_type)
        if not candidates:
            # Check all strategies if none specifically registered for asset_type
            candidates = self.strategies.list()

        # Step 2: Evaluate and rank candidates
        selected_strategy, trace = StrategyEvaluator.evaluate_candidates(
            spec=spec,
            candidates=candidates,
            available_capabilities=available_caps,
        )

        # Step 3: FAIL-EARLY if no valid strategy can satisfy hard constraints (Section 35, 91)
        if selected_strategy is None:
            missing = [c for c in spec.required_capabilities if c not in available_caps]
            gap_report = CapabilityGapReport(
                is_supported=False,
                requested_capabilities=spec.required_capabilities,
                available_capabilities=sorted(list(available_caps)),
                missing_capabilities=missing,
                asset_id=asset_id,
                rationale=trace.selection_rationale,
            )
            return PlanningResult(
                is_success=False,
                gap_report=gap_report,
                decision_trace=trace,
                error_message=f"NO_VALID_STRATEGY: {trace.selection_rationale}",
            )

        # Step 4: Construct GenerationPlan DAG from selected strategy templates
        nodes: Dict[str, GenerationPlanNode] = {}
        dep_graph = DependencyGraph()

        for tpl in selected_strategy.pipeline_node_templates:
            node_id = tpl["node_id"]
            capability_id = tpl["capability"]
            dependencies = tpl.get("dependencies", [])

            # Find matching implementation
            matching_imps = self.implementations.find_for_capability(capability_id)
            if not matching_imps:
                # No implementation available for node capability
                gap_report = CapabilityGapReport(
                    is_supported=False,
                    requested_capabilities=[capability_id],
                    available_capabilities=sorted(list(available_caps)),
                    missing_capabilities=[capability_id],
                    asset_id=asset_id,
                    rationale=f"Missing implementation for capability '{capability_id}'.",
                )
                return PlanningResult(
                    is_success=False,
                    gap_report=gap_report,
                    decision_trace=trace,
                    error_message=f"No implementation registered for capability '{capability_id}'.",
                )

            primary_imp = matching_imps[0]
            fallback_imps = [imp.implementation_id for imp in matching_imps[1:]]

            plan_node = GenerationPlanNode(
                node_id=node_id,
                operation=OperationType.GENERATE,
                capability=capability_id,
                implementation=primary_imp.implementation_id,
                dependencies=dependencies,
                fallbacks=fallback_imps,
            )
            nodes[node_id] = plan_node
            dep_graph.add_node(node_id)
            for dep in dependencies:
                dep_graph.add_dependency(node_id, dep)

        # Validate acyclic and obtain execution order
        dep_graph.validate_acyclic()
        execution_order = dep_graph.topological_sort()

        plan = GenerationPlan(
            plan_id=f"plan_{asset_id}_{uuid.uuid4().hex[:8]}",
            asset_id=asset_id,
            strategy_id=selected_strategy.strategy_id,
            specification_hash=spec.resolved_specification_hash,
            nodes=nodes,
            execution_order=execution_order,
            estimated_cost=selected_strategy.cost_rating,
            expected_quality=selected_strategy.quality_rating,
            risks=[f"Risk rating: {selected_strategy.risk_rating}"],
            fallbacks={nid: n.fallbacks for nid, n in nodes.items() if n.fallbacks},
            metadata={
                "strategy_name": selected_strategy.name,
                "category": selected_strategy.category.value,
                "determinism": selected_strategy.determinism.value,
            },
        )

        return PlanningResult(
            is_success=True,
            plan=plan,
            decision_trace=trace,
        )
