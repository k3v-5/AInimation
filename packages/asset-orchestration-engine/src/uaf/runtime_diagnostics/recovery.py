"""Multi-level crash recovery escalation and state restoration orchestrator."""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from uaf.runtime_diagnostics.core import CrashType, RecoveryLevel, SubsystemType
from uaf.runtime_diagnostics.crash import CrashReport


@dataclass
class RecoveryRecord:
    timestamp_ns: int
    crash_id: str
    subsystem: SubsystemType
    level: RecoveryLevel
    success: bool
    details: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp_ns": self.timestamp_ns,
            "crash_id": self.crash_id,
            "subsystem": self.subsystem.value,
            "level": self.level.name,
            "level_code": self.level.value,
            "success": self.success,
            "details": self.details,
            "metadata": self.metadata,
        }


RecoveryHandler = Callable[[CrashReport, RecoveryLevel], bool]


ORDERED_RECOVERY_LEVELS: List[RecoveryLevel] = [
    RecoveryLevel.LEVEL_0_COMPONENT_RESTART,
    RecoveryLevel.LEVEL_1_RESOURCE_RELOAD,
    RecoveryLevel.LEVEL_2_SUBSYSTEM_RESTART,
    RecoveryLevel.LEVEL_3_CHECKPOINT_RESTORE,
    RecoveryLevel.LEVEL_4_SAFE_MODE,
    RecoveryLevel.LEVEL_5_TERMINATE_CLEANLY,
]


class CrashRecoveryOrchestrator:
    """Escalates recovery attempts through 6 levels of remediation:
    Level 0: COMPONENT_RESTART
    Level 1: RESOURCE_RELOAD
    Level 2: SUBSYSTEM_RESTART
    Level 3: CHECKPOINT_RESTORE
    Level 4: SAFE_MODE
    Level 5: TERMINATE_CLEANLY
    """

    def __init__(self, escalation_threshold_s: float = 10.0, max_attempts_per_level: int = 2) -> None:
        self.escalation_threshold_s = escalation_threshold_s
        self.max_attempts_per_level = max_attempts_per_level
        # subsystem -> (current_level, attempt_count, last_attempt_time_s)
        self._subsystem_escalation: Dict[SubsystemType, tuple[RecoveryLevel, int, float]] = {}
        # custom handlers per level or subsystem
        self._handlers: Dict[RecoveryLevel, List[RecoveryHandler]] = {lvl: [] for lvl in ORDERED_RECOVERY_LEVELS}
        self.history: List[RecoveryRecord] = []
        self.is_in_safe_mode: bool = False
        self.is_shutdown_requested: bool = False

    def register_handler(self, level: RecoveryLevel, handler: RecoveryHandler) -> None:
        self._handlers[level].append(handler)

    def get_current_level(self, subsystem: SubsystemType) -> RecoveryLevel:
        if subsystem in self._subsystem_escalation:
            return self._subsystem_escalation[subsystem][0]
        return RecoveryLevel.LEVEL_0_COMPONENT_RESTART

    def reset_escalation(self, subsystem: SubsystemType) -> None:
        self._subsystem_escalation.pop(subsystem, None)

    def handle_crash(self, crash_report: CrashReport) -> RecoveryRecord:
        subsystem = crash_report.subsystem
        now = time.perf_counter()

        current_level, attempts, last_time = self._subsystem_escalation.get(
            subsystem,
            (RecoveryLevel.LEVEL_0_COMPONENT_RESTART, 0, 0.0)
        )

        # Check if we should escalate due to repeated crashes within window
        if (now - last_time) <= self.escalation_threshold_s:
            attempts += 1
            if attempts > self.max_attempts_per_level:
                # Escalate to next level
                idx = ORDERED_RECOVERY_LEVELS.index(current_level)
                if idx < len(ORDERED_RECOVERY_LEVELS) - 1:
                    current_level = ORDERED_RECOVERY_LEVELS[idx + 1]
                attempts = 1
        else:
            # Stabilized past window, start at Level 0
            current_level = RecoveryLevel.LEVEL_0_COMPONENT_RESTART
            attempts = 1

        self._subsystem_escalation[subsystem] = (current_level, attempts, now)

        # Update global flags
        if current_level == RecoveryLevel.LEVEL_4_SAFE_MODE:
            self.is_in_safe_mode = True
        elif current_level in (RecoveryLevel.LEVEL_5_TERMINATE_CLEANLY, RecoveryLevel.LEVEL_5_CONTROLLED_SHUTDOWN):
            self.is_shutdown_requested = True

        # Execute registered handlers
        success = False
        details = f"Executed recovery at {current_level.name} for {subsystem.value} (attempt {attempts})"
        handlers = self._handlers.get(current_level, [])
        if handlers:
            handler_results = []
            for h in handlers:
                try:
                    res = h(crash_report, current_level)
                    handler_results.append(res)
                except Exception:
                    handler_results.append(False)
            success = any(handler_results) if handler_results else False
        else:
            # Default recovery simulated success
            success = current_level != RecoveryLevel.LEVEL_5_TERMINATE_CLEANLY

        rec = RecoveryRecord(
            timestamp_ns=time.perf_counter_ns(),
            crash_id=crash_report.crash_id,
            subsystem=subsystem,
            level=current_level,
            success=success,
            details=details,
            metadata={
                "attempt_count": attempts,
                "crash_type": crash_report.crash_type.value,
                "safe_mode": self.is_in_safe_mode,
                "shutdown": self.is_shutdown_requested,
            },
        )
        self.history.append(rec)
        return rec

    def get_history(self) -> List[RecoveryRecord]:
        return list(self.history)
