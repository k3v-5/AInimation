"""
Universal Event Validator (UAF-81.65).
Authoritative validator for events, commands, replay recordings, and diagnostic bundles.
"""

from __future__ import annotations
import json
import re
import time
from typing import Any, Dict, List

from ..models.definition import (
    Event,
    Command,
    ReplayRecording,
    DiagnosticEventBundle,
    EventDiagnosticReport,
)


class UniversalEventValidator:
    """
    Enforces UAF-81.65 event, command, replay, and security constraints.
    """

    SECRET_PATTERNS = [
        re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE),
        re.compile(r"api[_-]?key", re.IGNORECASE),
        re.compile(r"password", re.IGNORECASE),
    ]

    def validate_event(self, event: Event) -> EventDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        if not event.event_id or not event.event_id.strip():
            errors.append("Event has empty or missing event_id.")
        if event.timestamp <= 0.0:
            errors.append(f"Event has non-positive timestamp: {event.timestamp}")

        return EventDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_command(self, command: Command) -> EventDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        if not command.command_id or not command.command_id.strip():
            errors.append("Command has empty command_id.")
        if not command.action or not command.action.strip():
            errors.append("Command has empty action name.")

        return EventDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_replay_recording(self, recording: ReplayRecording) -> EventDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        if recording.total_frames != len(recording.frames):
            errors.append(
                f"Recording frame count mismatch: declared {recording.total_frames}, actual {len(recording.frames)}."
            )

        prev_frame = -1
        for f in recording.frames:
            if f.frame_number != prev_frame + 1:
                errors.append(f"Non-monotonic frame sequence at frame {f.frame_number} (expected {prev_frame + 1}).")
            if len(f.state_hash) != 64:
                errors.append(f"Frame {f.frame_number} has invalid state hash length: {len(f.state_hash)}")
            prev_frame = f.frame_number

        return EventDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )

    def validate_diagnostic_bundle(self, bundle: DiagnosticEventBundle) -> EventDiagnosticReport:
        errors: List[str] = []
        warnings: List[str] = []
        info: List[str] = []

        expected = bundle.sha256_digest
        computed = bundle.compute_digest()
        if expected != computed:
            errors.append(f"Digest mismatch: expected '{expected}', computed '{computed}'.")

        serialized = json.dumps(bundle.event_logs)
        for pat in self.SECRET_PATTERNS:
            if pat.search(serialized):
                errors.append("Unredacted credential or secret detected in diagnostic bundle event logs.")

        return EventDiagnosticReport(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
        )
