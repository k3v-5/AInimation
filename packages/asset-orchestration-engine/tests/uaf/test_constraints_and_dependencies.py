"""
Tests for Constraints, ConstraintResolver (NO-SILENT-CORRECTION), and DependencyGraph (Cycle Detection).
UAF-81.1 Sections 10, 11, 12, 25, 26, 50.
"""

import pytest
from uaf.intelligence.constraints.constraint import AssetConstraint, ConstraintType, ConstraintCategory
from uaf.intelligence.constraints.constraint_resolver import ConstraintResolver
from uaf.intelligence.dependencies.dependency_graph import DependencyGraph, CyclicDependencyError


def test_constraint_resolver_hard_conflict():
    constraints = [
        AssetConstraint(
            constraint_id="max_height_capsule",
            category=ConstraintCategory.DIMENSIONAL,
            constraint_type=ConstraintType.HARD,
            target_parameter="height",
            condition="max_value",
            expected_value=1.92,
        )
    ]
    # Height of 2.10 violates 1.92 max
    resolved, report = ConstraintResolver.resolve(
        parameters={"height": 2.10},
        constraints=constraints,
    )

    assert report.has_conflicts is True
    assert "height" in report.conflicting_parameters
    assert any("violated" in r for r in report.reasons)


def test_constraint_resolver_soft_adjustment_with_trace_no_silent_correction():
    """
    CRITICAL INVARIANT (Section 50):
    Soft constraints can adjust parameters ONLY if explicit trace and rationale are recorded.
    Silent modifications are forbidden.
    """
    constraints = [
        AssetConstraint(
            constraint_id="standard_mobile_texture_cap",
            category=ConstraintCategory.PERFORMANCE,
            constraint_type=ConstraintType.SOFT,
            target_parameter="texture_resolution",
            condition="max_value",
            expected_value=2048,
        )
    ]
    resolved, report = ConstraintResolver.resolve(
        parameters={"texture_resolution": 4096},
        constraints=constraints,
    )

    assert report.has_conflicts is False
    assert resolved["texture_resolution"] == 2048
    # Must have recorded trace entry explaining adjustment
    assert len(report.traces) == 1
    trace = report.traces[0]
    assert trace.status == "adjusted_with_warning"
    assert trace.requested_value == 4096
    assert trace.resolved_value == 2048
    assert "adjusted" in trace.rationale


def test_dependency_graph_acyclic_topological_sort():
    graph = DependencyGraph()
    # A depends on B, B depends on C
    # Execution order must be C, then B, then A
    graph.add_dependency("Character", "Armor")
    graph.add_dependency("Armor", "Material")

    order = graph.topological_sort()
    assert order.index("Material") < order.index("Armor")
    assert order.index("Armor") < order.index("Character")


def test_dependency_graph_cycle_detection_raises_error():
    graph = DependencyGraph()
    # Cycle: NodeA -> NodeB -> NodeC -> NodeA
    graph.add_dependency("NodeA", "NodeB")
    graph.add_dependency("NodeB", "NodeC")
    graph.add_dependency("NodeC", "NodeA")

    with pytest.raises(CyclicDependencyError, match="Circular dependency cycle detected"):
        graph.topological_sort()
