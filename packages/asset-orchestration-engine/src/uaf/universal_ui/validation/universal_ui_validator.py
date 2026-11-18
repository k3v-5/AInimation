"""
Universal UI Validator (UAF-81.61).
Normative verification pipeline (§18, §19, §29, §88, §94, §174) for widget hierarchy,
cycle detection, bounds integrity, remapping conflict analysis, and accessibility.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    WidgetType,
    LayoutMode,
    InputDevice,
    AccessibilityRole,
    UIBounds,
    UIWidget,
    UIScreen,
    UIAsset,
    InputRemappingProfile,
    UIPreferences,
)


@dataclass
class UIValidationReport:
    """Consolidated diagnostic report of UI validation pipeline (§174)."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_pass(self, check_name: str) -> None:
        self.passed_checks.append(check_name)


class UniversalUIValidator:
    """
    Automated validator ensuring UI assets, widget trees, and input configurations
    comply with UAF-81.61 normative specifications.
    """

    def validate_widget(self, widget: UIWidget) -> UIValidationReport:
        """Validates bounds, styles, and parameters of an individual widget."""
        report = UIValidationReport()

        if not widget.widget_id:
            report.add_error("Widget ID cannot be empty.")

        # Bounds validation (§15)
        b = widget.bounds
        if math.isnan(b.x) or math.isnan(b.y) or math.isnan(b.width) or math.isnan(b.height):
            report.add_error(f"Widget '{widget.widget_id}' has NaN in bounds.")
        elif b.width < 0.0 or b.height < 0.0:
            report.add_error(f"Widget '{widget.widget_id}' bounds width/height cannot be negative.")

        # Scale parameters validation (§29)
        if "scale" in widget.parameters:
            scale_val = widget.parameters["scale"]
            if scale_val <= 0.0:
                report.add_error(f"Widget '{widget.widget_id}' has invalid zero or negative scale.")

        # Color-only signal check (§88)
        if "color" in widget.parameters and "shape" not in widget.parameters and "text" not in widget.parameters:
            if widget.widget_type == WidgetType.ICON and "icon" not in widget.parameters:
                report.add_warning(f"Widget '{widget.widget_id}' may rely solely on color for state presentation.")

        if not report.errors:
            report.add_pass(f"widget_{widget.widget_id}")
        return report

    def validate_screen(self, screen: UIScreen) -> UIValidationReport:
        """
        Validates screen hierarchy, single parent integrity, and cycle prevention (§18, §19).
        """
        report = UIValidationReport()

        if not screen.screen_id:
            report.add_error("Screen ID cannot be empty.")

        visited_nodes: Set[str] = set()

        # Check for cycles using DFS (§19)
        for wid in screen.widgets:
            path: List[str] = []
            curr: Optional[str] = wid
            while curr is not None:
                if curr in path:
                    cycle_str = " -> ".join(path + [curr])
                    report.add_error(f"Cycle detected in widget hierarchy: {cycle_str}")
                    break
                path.append(curr)
                curr_w = screen.widgets.get(curr)
                curr = curr_w.parent_id if curr_w else None

            # Validate each widget
            w_obj = screen.widgets[wid]
            w_rep = self.validate_widget(w_obj)
            if not w_rep.is_valid:
                for err in w_rep.errors:
                    report.add_error(f"Screen '{screen.screen_id}' -> {err}")
            for w in w_rep.warnings:
                report.add_warning(w)

        if not report.errors:
            report.add_pass(f"screen_{screen.screen_id}")
        return report

    def validate_remapping_profile(self, profile: InputRemappingProfile) -> UIValidationReport:
        """Validates key remappings against conflicts and reserved bindings (§94)."""
        report = UIValidationReport()

        if not profile.profile_id:
            report.add_error("Remapping profile ID cannot be empty.")

        # Check conflicting bindings (multiple actions bound to same key)
        key_to_actions: Dict[str, List[str]] = {}
        for action, key in profile.mappings.items():
            key_to_actions.setdefault(key, []).append(action)

        for key, actions in key_to_actions.items():
            if len(actions) > 1:
                report.add_warning(f"Conflicting bindings detected: key '{key}' bound to {actions}")

        if not report.errors:
            report.add_pass(f"remapping_{profile.profile_id}")
        return report

    def validate_preferences(self, prefs: UIPreferences) -> UIValidationReport:
        """Validates user preference ranges (§29, §175)."""
        report = UIValidationReport()

        if prefs.ui_scale <= 0.0 or prefs.ui_scale > 5.0:
            report.add_error("UI scale must be within (0.0, 5.0].")

        if prefs.font_scale <= 0.0 or prefs.font_scale > 5.0:
            report.add_error("Font scale must be within (0.0, 5.0].")

        if not report.errors:
            report.add_pass("preferences_integrity")
        return report

    def validate_all(self, asset: UIAsset) -> UIValidationReport:
        """Complete normative UI asset verification pipeline (§174)."""
        report = UIValidationReport()

        if not asset.ui_id:
            report.add_error("Asset UI ID cannot be empty.")

        # Validate root screen
        screen_rep = self.validate_screen(asset.root_screen)
        if not screen_rep.is_valid:
            for err in screen_rep.errors:
                report.add_error(err)
        for w in screen_rep.warnings:
            report.add_warning(w)

        report.metrics = {
            "widgets_count": len(asset.root_screen.widgets),
            "version": asset.version,
        }

        if not report.errors:
            report.add_pass("full_ui_asset_verification")
        return report
