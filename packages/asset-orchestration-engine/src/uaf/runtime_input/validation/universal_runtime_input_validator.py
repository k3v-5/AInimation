"""
Universal Runtime Input Validator (UAF-81.77).
Normative validation for input devices, bindings, contexts, dead zones, and profiles.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    InputDevice,
    RawInputEvent,
    InputAction,
    InputAxis,
    InputContext,
    InputRebindingProfile,
    InputWorld,
)


class InputValidationIssue(str):
    """A string-compatible validation issue with structured error attributes."""

    error_code: str
    message: str
    severity: str

    def __new__(cls, error_code: str, message: str = "", severity: str = "ERROR"):
        full = f"{severity}: [{error_code}] {message}" if message else error_code
        instance = super().__new__(cls, full)
        instance.error_code = error_code
        instance.message = message or error_code
        instance.severity = severity
        return instance


class UniversalRuntimeInputValidator:
    """Normative validation of runtime input world entities, bindings and constraints."""

    def validate_device(self, device: InputDevice) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not device.device_id or not device.device_id.strip():
            errors.append(InputValidationIssue("INVALID_DEVICE_ID", "device_id cannot be empty."))
        return errors

    def validate_raw_event(self, event: RawInputEvent) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not event.event_id or not event.event_id.strip():
            errors.append(InputValidationIssue("INVALID_EVENT_ID", "event_id cannot be empty."))
        if event.timestamp < 0.0:
            errors.append(InputValidationIssue("INVALID_EVENT_TIMESTAMP", "timestamp cannot be negative."))
        return errors

    def validate_action(self, action: InputAction) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not action.action_id or not action.action_id.strip():
            errors.append(InputValidationIssue("INVALID_ACTION_ID", "action_id cannot be empty."))
        for b in action.bindings:
            if not b.code or not b.code.strip():
                errors.append(InputValidationIssue("INVALID_BINDING_CODE", f"Binding '{b.binding_id}' has empty code."))
        return errors

    def validate_axis(self, axis: InputAxis) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not axis.axis_id or not axis.axis_id.strip():
            errors.append(InputValidationIssue("INVALID_AXIS_ID", "axis_id cannot be empty."))
        for b in axis.bindings:
            if b.dead_zone < 0.0 or b.dead_zone >= 1.0:
                errors.append(InputValidationIssue("INVALID_DEAD_ZONE", f"dead_zone must be in [0, 1) ({b.dead_zone})."))
            if b.sensitivity < 0.0:
                errors.append(InputValidationIssue("INVALID_SENSITIVITY", f"sensitivity cannot be negative ({b.sensitivity})."))
        return errors

    def validate_context(self, context: InputContext, world: Optional[InputWorld] = None) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not context.context_id or not context.context_id.strip():
            errors.append(InputValidationIssue("INVALID_CONTEXT_ID", "context_id cannot be empty."))
        if world:
            for aid in context.action_ids:
                if aid not in world.actions:
                    errors.append(InputValidationIssue("MISSING_ACTION_IN_CONTEXT", f"Action '{aid}' in context '{context.context_id}' not found in world."))
            for xid in context.axis_ids:
                if xid not in world.axes:
                    errors.append(InputValidationIssue("MISSING_AXIS_IN_CONTEXT", f"Axis '{xid}' in context '{context.context_id}' not found in world."))
        return errors

    def validate_profile(self, profile: InputRebindingProfile) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        if not profile.profile_id or not profile.profile_id.strip():
            errors.append(InputValidationIssue("INVALID_PROFILE_ID", "profile_id cannot be empty."))
        if profile.version < 1:
            errors.append(InputValidationIssue("INVALID_PROFILE_VERSION", f"Profile version must be >= 1 ({profile.version})."))
        for ax, dz in profile.dead_zone_overrides.items():
            if dz < 0.0 or dz >= 1.0:
                errors.append(InputValidationIssue("INVALID_DEAD_ZONE_OVERRIDE", f"Dead zone override for '{ax}' must be in [0, 1) ({dz})."))
        return errors

    def validate_world(self, world: InputWorld) -> List[InputValidationIssue]:
        errors: List[InputValidationIssue] = []
        for dev in world.devices.values():
            errors.extend(self.validate_device(dev))
        for act in world.actions.values():
            errors.extend(self.validate_action(act))
        for ax in world.axes.values():
            errors.extend(self.validate_axis(ax))
        for ctx in world.contexts.values():
            errors.extend(self.validate_context(ctx, world))
        for prof in world.profiles.values():
            errors.extend(self.validate_profile(prof))
        return errors

    validate = validate_world
