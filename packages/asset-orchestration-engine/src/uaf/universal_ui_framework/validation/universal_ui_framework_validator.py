"""
UAF-81.66: Universal UI Framework Validator.
Enforces structural tree invariants, box constraints integrity, theme contrast compliance,
accessibility requirements, binding validity, and snapshot cryptographic signatures.
"""

from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple

from uaf.universal_ui_framework.models.definition import (
    UIBoxConstraints,
    UITheme,
    UIAccessibleNode,
    UIAccessibleRole,
    UIStructuralSnapshot,
    UIDiagnosticBundle,
)
from uaf.universal_ui_framework.engine.universal_ui_framework_fabricator import (
    UniversalUIFrameworkFabricator,
    UIElement,
)


class UniversalUIFrameworkValidator:
    """
    Authoritative validator for Universal UI Framework.
    """

    @staticmethod
    def validate_tree_invariants(fabricator: UniversalUIFrameworkFabricator, root_id: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if root_id not in fabricator.roots:
            errors.append(f"Root '{root_id}' does not exist in fabricator roots.")
            return False, errors

        visited: Set[str] = set()
        stack: Set[str] = set()

        def dfs(element_id: str, parent_id: str | None) -> None:
            if element_id == parent_id:
                errors.append(f"NO_SELF_PARENT: Element '{element_id}' is its own parent.")
            if element_id in stack:
                errors.append(f"NO_CYCLES: Cycle detected involving element '{element_id}'.")
                return
            if element_id not in fabricator.elements:
                errors.append(f"Element '{element_id}' referenced in tree is not registered.")
                return

            elem = fabricator.elements[element_id]
            if parent_id is not None and elem.parent_id != parent_id:
                errors.append(f"ONE_PARENT: Element '{element_id}' expected parent '{parent_id}', got '{elem.parent_id}'.")

            stack.add(element_id)
            visited.add(element_id)

            # Check unique children
            if len(elem.children_ids) != len(set(elem.children_ids)):
                errors.append(f"VALID_CHILD_ORDER: Duplicate child detected under '{element_id}'.")

            for child_id in elem.children_ids:
                dfs(child_id, element_id)

            stack.remove(element_id)

        dfs(root_id, None)
        return len(errors) == 0, errors

    @staticmethod
    def validate_box_constraints(constraints: UIBoxConstraints) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if constraints.min_width < 0:
            errors.append(f"min_width ({constraints.min_width}) must be >= 0.")
        if constraints.min_height < 0:
            errors.append(f"min_height ({constraints.min_height}) must be >= 0.")
        if constraints.min_width > constraints.max_width:
            errors.append(f"min_width ({constraints.min_width}) cannot exceed max_width ({constraints.max_width}).")
        if constraints.min_height > constraints.max_height:
            errors.append(f"min_height ({constraints.min_height}) cannot exceed max_height ({constraints.max_height}).")
        return len(errors) == 0, errors

    @staticmethod
    def validate_theme_contrast(theme: UITheme, min_ratio: float = 4.5) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        colors = theme.tokens.colors

        pairs = [
            ("on_background", "background"),
            ("on_surface", "surface"),
            ("on_primary", "primary")
        ]

        for fg_key, bg_key in pairs:
            if fg_key in colors and bg_key in colors:
                fg = colors[fg_key]
                bg = colors[bg_key]
                ratio = fg.contrast_ratio(bg)
                if ratio < min_ratio:
                    errors.append(f"CONTRAST_FAILURE: '{fg_key}' on '{bg_key}' has contrast {ratio:.2f}:1 (requires >= {min_ratio}:1).")

        return len(errors) == 0, errors

    @staticmethod
    def validate_accessibility_node(node: UIAccessibleNode) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        interactive_roles = {
            UIAccessibleRole.BUTTON,
            UIAccessibleRole.TEXT_FIELD,
            UIAccessibleRole.CHECKBOX,
            UIAccessibleRole.SLIDER
        }
        if node.role in interactive_roles and not node.name.strip():
            errors.append(f"MISSING_ACCESSIBLE_NAME: Interactive element '{node.element_id}' has no accessible name.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_structural_snapshot(snapshot: UIStructuralSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected_hash = snapshot.compute_hash()
        if snapshot.state_hash != expected_hash:
            errors.append(f"SNAPSHOT_CORRUPTION: Hash mismatch! expected {expected_hash}, got {snapshot.state_hash}.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: UIDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected_sig = bundle.sign()
        if bundle.signature != expected_sig:
            errors.append(f"BUNDLE_CORRUPTION: Signature mismatch! expected {expected_sig}, got {bundle.signature}.")
        return len(errors) == 0, errors
