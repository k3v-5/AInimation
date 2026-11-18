"""
UAF-81.82: Semantic Validation for NavMeshes, Behavior Trees, and Agents.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from ..behavior.tree import BehaviorTree
from ..engine.agent import AIAgent
from ..models.definition import BehaviorTreeInvalid, NavPolygon
from ..navigation.mesh import NavMesh
from ..navigation.polygon import compute_polygon_area_2d, is_polygon_convex


@dataclass(frozen=True)
class AIValidationIssue:
    severity: str  # "ERROR", "WARNING"
    code: str
    message: str
    context: str = ""


class UniversalRuntimeAIValidator:
    """Semantic validation engine verifying contracts, topology, and numeric safety."""

    @classmethod
    def validate_nav_mesh(cls, nav_mesh: NavMesh) -> List[AIValidationIssue]:
        issues: List[AIValidationIssue] = []

        if not nav_mesh.polygons:
            issues.append(AIValidationIssue("WARNING", "AI_EMPTY_NAVMESH", "NavMesh contains zero polygons."))
            return issues

        for pid, poly in nav_mesh.polygons.items():
            if len(poly.vertices) < 3:
                issues.append(AIValidationIssue(
                    "ERROR", "AI_INSUFFICIENT_VERTICES",
                    f"Polygon {pid} has less than 3 vertices ({len(poly.vertices)}).", str(pid)
                ))
                continue

            for idx, v in enumerate(poly.vertices):
                if any(math.isnan(c) or math.isinf(c) for c in v):
                    issues.append(AIValidationIssue(
                        "ERROR", "AI_NUMERIC_ERROR",
                        f"Polygon {pid} vertex {idx} contains non-finite coordinates: {v}", str(pid)
                    ))

            if not is_polygon_convex(poly.vertices):
                issues.append(AIValidationIssue(
                    "ERROR", "AI_NON_CONVEX_POLYGON",
                    f"Polygon {pid} is not strictly convex.", str(pid)
                ))

            area = compute_polygon_area_2d(poly.vertices)
            if area < 1e-6:
                issues.append(AIValidationIssue(
                    "ERROR", "AI_DEGENERATE_POLYGON",
                    f"Polygon {pid} has degenerate area ({area}).", str(pid)
                ))

            # Validate neighbor references exist
            for n_id in poly.neighbors:
                if n_id not in nav_mesh.polygons:
                    issues.append(AIValidationIssue(
                        "ERROR", "AI_ORPHAN_NEIGHBOR_REF",
                        f"Polygon {pid} references non-existent neighbor {n_id}.", str(pid)
                    ))

        return issues

    @classmethod
    def validate_behavior_tree(cls, tree: BehaviorTree) -> List[AIValidationIssue]:
        issues: List[AIValidationIssue] = []
        try:
            tree.validate_integrity()
        except BehaviorTreeInvalid as e:
            issues.append(AIValidationIssue("ERROR", "AI_INVALID_BEHAVIOR_TREE", str(e)))
        return issues

    @classmethod
    def validate_agent(cls, agent: AIAgent) -> List[AIValidationIssue]:
        issues: List[AIValidationIssue] = []

        if any(math.isnan(c) or math.isinf(c) for c in agent.position):
            issues.append(AIValidationIssue("ERROR", "AI_NUMERIC_ERROR", f"Agent {agent.agent_id} position is non-finite."))

        if any(math.isnan(c) or math.isinf(c) for c in agent.velocity):
            issues.append(AIValidationIssue("ERROR", "AI_NUMERIC_ERROR", f"Agent {agent.agent_id} velocity is non-finite."))

        if agent.radius <= 0.0:
            issues.append(AIValidationIssue("ERROR", "AI_INVALID_RADIUS", f"Agent {agent.agent_id} radius must be > 0."))

        if agent.height <= 0.0:
            issues.append(AIValidationIssue("ERROR", "AI_INVALID_HEIGHT", f"Agent {agent.agent_id} height must be > 0."))

        return issues
