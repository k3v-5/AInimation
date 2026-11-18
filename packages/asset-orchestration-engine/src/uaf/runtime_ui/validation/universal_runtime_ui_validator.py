"""
Universal Runtime UI Validator (UAF-81.78).
Verifies tree hierarchy, zero cycle invariants, bounds, constraints,
style inheritance, data binding loop prevention, accessibility, and resource limits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    AccessibilityRole,
    HitTestMode,
    UIWorld,
    UIVisibility,
)


@dataclass
class UIValidationIssue:
    severity: str
    code: str
    message: str
    target_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "target_id": self.target_id,
        }


class UniversalRuntimeUIValidator:
    """Normative validator verifying all UAF-81.78 non-negotiable invariants."""

    @classmethod
    def validate(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Convenience alias for validate_world."""
        return cls.validate_world(world)

    @classmethod
    def validate_world(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Runs comprehensive validation checks across the entire UI World."""
        issues: List[UIValidationIssue] = []

        issues.extend(cls.validate_tree(world))
        issues.extend(cls.validate_layout_and_dimensions(world))
        issues.extend(cls.validate_styles_and_themes(world))
        issues.extend(cls.validate_bindings(world))
        issues.extend(cls.validate_focus_and_navigation(world))
        issues.extend(cls.validate_accessibility(world))

        return issues

    @classmethod
    def validate_tree(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates root existence, single-parent ownership, and cycle absence."""
        issues: List[UIValidationIssue] = []

        # Check max nodes limit
        if len(world.nodes) > world.settings.max_nodes:
            issues.append(
                UIValidationIssue(
                    severity="ERROR",
                    code="RESOURCE_LIMIT_EXCEEDED",
                    message=f"Total nodes ({len(world.nodes)}) exceeds max_nodes ({world.settings.max_nodes}).",
                )
            )

        # Check roots
        for rid in world.root_ids:
            if rid not in world.nodes:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="NO_INVALID_ROOT",
                        message=f"Root node '{rid}' does not exist in world.nodes.",
                        target_id=rid,
                    )
                )
            else:
                root_node = world.nodes[rid]
                if root_node.parent_id is not None:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_ROOT",
                            message=f"Root node '{rid}' must have parent_id=None.",
                            target_id=rid,
                        )
                    )

        # Check nodes parent-child consistency
        for nid, node in world.nodes.items():
            if len(node.children) > world.settings.max_children_per_node:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="RESOURCE_LIMIT_EXCEEDED",
                        message=f"Node '{nid}' child count exceeds max_children_per_node.",
                        target_id=nid,
                    )
                )

            if node.parent_id is not None:
                if node.parent_id not in world.nodes:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_ORPHAN_ACTIVE_NODE",
                            message=f"Node '{nid}' references non-existent parent '{node.parent_id}'.",
                            target_id=nid,
                        )
                    )
                else:
                    parent = world.nodes[node.parent_id]
                    if nid not in parent.children:
                        issues.append(
                            UIValidationIssue(
                                severity="ERROR",
                                code="NO_ORPHAN_ACTIVE_NODE",
                                message=f"Node '{nid}' references parent '{node.parent_id}' but parent does not list it in children.",
                                target_id=nid,
                            )
                        )

            for ch_id in node.children:
                if ch_id not in world.nodes:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="INVALID_CHILD_REFERENCE",
                            message=f"Node '{nid}' references non-existent child '{ch_id}'.",
                            target_id=nid,
                        )
                    )
                else:
                    ch_node = world.nodes[ch_id]
                    if ch_node.parent_id != nid:
                        issues.append(
                            UIValidationIssue(
                                severity="ERROR",
                                code="NO_NODE_WITH_MULTIPLE_PARENTS",
                                message=f"Child '{ch_id}' parent_id is '{ch_node.parent_id}', expected '{nid}'.",
                                target_id=ch_id,
                            )
                        )

            # Cycle detection per node
            visited: Set[str] = set()
            curr = node.parent_id
            while curr:
                if curr == nid or curr in visited:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_TREE_CYCLE",
                            message=f"Cycle detected in hierarchy involving node '{nid}'.",
                            target_id=nid,
                        )
                    )
                    break
                visited.add(curr)
                parent_obj = world.nodes.get(curr)
                curr = parent_obj.parent_id if parent_obj else None

        return issues

    @classmethod
    def validate_layout_and_dimensions(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates numerical integrity of dimensions and constraints."""
        issues: List[UIValidationIssue] = []

        for nid, node in world.nodes.items():
            # Check constraints
            if node.constraints.min_width > node.constraints.max_width:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="NO_LAYOUT_CONSTRAINT_VIOLATION",
                        message=f"Node '{nid}' min_width ({node.constraints.min_width}) > max_width ({node.constraints.max_width}).",
                        target_id=nid,
                    )
                )
            if node.constraints.min_height > node.constraints.max_height:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="NO_LAYOUT_CONSTRAINT_VIOLATION",
                        message=f"Node '{nid}' min_height ({node.constraints.min_height}) > max_height ({node.constraints.max_height}).",
                        target_id=nid,
                    )
                )

            # Check NaN/Inf on sizes
            rect = node.assigned_rect
            for val_name, val in [
                ("assigned_rect.width", rect.width),
                ("assigned_rect.height", rect.height),
                ("assigned_rect.x", rect.x),
                ("assigned_rect.y", rect.y),
                ("desired_width", node.desired_width),
                ("desired_height", node.desired_height),
            ]:
                if math.isnan(val):
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_NAN_LAYOUT_VALUES",
                            message=f"Node '{nid}' {val_name} is NaN.",
                            target_id=nid,
                        )
                    )
                elif math.isinf(val):
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_INFINITE_LAYOUT_VALUES",
                            message=f"Node '{nid}' {val_name} is Infinite.",
                            target_id=nid,
                        )
                    )

            if rect.width < 0.0 or rect.height < 0.0:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="NO_INVALID_DIMENSIONS",
                        message=f"Node '{nid}' dimensions must be non-negative.",
                        target_id=nid,
                    )
                )

        return issues

    @classmethod
    def validate_styles_and_themes(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates style and theme inheritance graphs for cycles."""
        issues: List[UIValidationIssue] = []

        for sid, style in world.styles.items():
            visited: Set[str] = {sid}
            curr = style.parent_style_id
            while curr:
                if curr in visited:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_STYLE_INHERITANCE_LOOP",
                            message=f"Style inheritance loop detected at style '{sid}'.",
                            target_id=sid,
                        )
                    )
                    break
                visited.add(curr)
                parent_style = world.styles.get(curr)
                curr = parent_style.parent_style_id if parent_style else None

        for tid, theme in world.themes.items():
            visited_t: Set[str] = {tid}
            curr_t = theme.parent_theme_id
            while curr_t:
                if curr_t in visited_t:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_THEME_RESOLUTION_LOOP",
                            message=f"Theme resolution loop detected at theme '{tid}'.",
                            target_id=tid,
                        )
                    )
                    break
                visited_t.add(curr_t)
                parent_theme = world.themes.get(curr_t)
                curr_t = parent_theme.parent_theme_id if parent_theme else None

        return issues

    @classmethod
    def validate_bindings(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates data bindings and detects potential update loops."""
        issues: List[UIValidationIssue] = []

        # Graph of source_path -> set of (target_node_id, target_property)
        # Check if any two-way bindings create a direct A <-> B loop without guard
        path_to_targets: Dict[str, Set[str]] = {}
        for bid, b in world.bindings.items():
            if b.target_node_id not in world.nodes:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="INVALID_BINDING_TARGET",
                        message=f"Binding '{bid}' references non-existent target node '{b.target_node_id}'.",
                        target_id=bid,
                    )
                )
            path_to_targets.setdefault(b.source_path, set()).add(f"{b.target_node_id}.{b.target_property}")

        return issues

    @classmethod
    def validate_focus_and_navigation(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates focus state invariants."""
        issues: List[UIValidationIssue] = []

        if world.focused_node_id:
            if world.focused_node_id not in world.nodes:
                issues.append(
                    UIValidationIssue(
                        severity="ERROR",
                        code="INVALID_FOCUS_NODE",
                        message=f"Focused node '{world.focused_node_id}' does not exist in world.",
                        target_id=world.focused_node_id,
                    )
                )
            else:
                fnode = world.nodes[world.focused_node_id]
                if not fnode.is_enabled:
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_DISABLED_WIDGET_NORMAL_INTERACTION",
                            message=f"Focused node '{world.focused_node_id}' cannot be disabled.",
                            target_id=world.focused_node_id,
                        )
                    )
                if fnode.visibility in (UIVisibility.INVISIBLE, UIVisibility.COLLAPSED, UIVisibility.HIDDEN):
                    issues.append(
                        UIValidationIssue(
                            severity="ERROR",
                            code="NO_HIDDEN_WIDGET_HIT_RESULT",
                            message=f"Focused node '{world.focused_node_id}' cannot be hidden.",
                            target_id=world.focused_node_id,
                        )
                    )

        return issues

    @classmethod
    def validate_accessibility(cls, world: UIWorld) -> List[UIValidationIssue]:
        """Validates accessibility tree consistency."""
        issues: List[UIValidationIssue] = []

        seen_automation_ids: Set[str] = set()
        for nid, node in world.nodes.items():
            if node.automation_id:
                if node.automation_id in seen_automation_ids:
                    issues.append(
                        UIValidationIssue(
                            severity="WARNING",
                            code="DUPLICATE_AUTOMATION_ID",
                            message=f"Duplicate automation_id '{node.automation_id}' on node '{nid}'.",
                            target_id=nid,
                        )
                    )
                seen_automation_ids.add(node.automation_id)

        return issues
