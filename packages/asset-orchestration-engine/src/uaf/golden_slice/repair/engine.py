"""Self-repair engine with safety checkpoints, rollback mechanics, and regression test generation."""

from __future__ import annotations
import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from uaf.golden_slice.repair.analyzer import FailureAnalyzer, FailureDiagnosis
from uaf.golden_slice.repair.knowledge_base import FailureKnowledgeBase


@dataclass
class RegressionTestRecord:
    test_id: str
    original_failure: str
    subsystem: str
    verification_action: str
    is_active: bool = True


@dataclass
class RepairExecutionResult:
    success: bool
    repair_action: str
    attempts_used: int
    checkpoint_restored: bool = False
    error: Optional[str] = None
    regression_test: Optional[RegressionTestRecord] = None


class SelfRepairEngine:
    """Executes safe autonomous repairs guarded by checkpoints and max attempt limits."""

    def __init__(
        self,
        max_repair_attempts: int = 3,
        knowledge_base: Optional[FailureKnowledgeBase] = None,
        analyzer: Optional[FailureAnalyzer] = None,
    ) -> None:
        self.max_repair_attempts = max_repair_attempts
        self.kb = knowledge_base or FailureKnowledgeBase()
        self.analyzer = analyzer or FailureAnalyzer()
        self.generated_regression_tests: List[RegressionTestRecord] = []
        self._checkpoints: Dict[str, Any] = {}

    def attempt_repair(
        self,
        target_state: Dict[str, Any],
        error_message: str,
        targeted_verifier: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ) -> RepairExecutionResult:
        diagnosis = self.analyzer.diagnose(error_message)

        # 1. Create safety checkpoint before applying any change
        checkpoint_id = f"chk_{diagnosis.failure_id}"
        self._checkpoints[checkpoint_id] = copy.deepcopy(target_state)

        for attempt in range(1, self.max_repair_attempts + 1):
            # Apply repair mutation
            action = diagnosis.suggested_repair
            self._apply_action(target_state, action)

            # Run targeted verification test
            passed = True
            if targeted_verifier is not None:
                try:
                    passed = targeted_verifier(target_state)
                except Exception:
                    passed = False

            if passed:
                # Commit change and record in knowledge base
                self.kb.record_repair(diagnosis.symptom, diagnosis.probable_cause, action, True)
                del self._checkpoints[checkpoint_id]

                # Section 90: Convert bug into permanent regression test
                reg_test = RegressionTestRecord(
                    test_id=f"reg_test_{diagnosis.symptom.lower()}",
                    original_failure=error_message,
                    subsystem=diagnosis.subsystem,
                    verification_action=action,
                )
                self.generated_regression_tests.append(reg_test)

                return RepairExecutionResult(
                    success=True,
                    repair_action=action,
                    attempts_used=attempt,
                    regression_test=reg_test,
                )

        # Exceeded max attempts -> Rollback to checkpoint
        target_state.clear()
        target_state.update(self._checkpoints.pop(checkpoint_id))
        self.kb.record_repair(diagnosis.symptom, diagnosis.probable_cause, diagnosis.suggested_repair, False)

        return RepairExecutionResult(
            success=False,
            repair_action=diagnosis.suggested_repair,
            attempts_used=self.max_repair_attempts,
            checkpoint_restored=True,
            error=f"Exceeded max repair attempts ({self.max_repair_attempts}); state rolled back to checkpoint.",
        )

    def _apply_action(self, target_state: Dict[str, Any], action: str) -> None:
        if action == "assign_fallback_texture":
            target_state["fallback_texture_assigned"] = True
        elif action == "unregister_orphan_actor":
            target_state.pop("orphan_actor_id", None)
        elif action == "clamp_emitter_spawn_rate":
            target_state["emitter_rate_clamped"] = True
        elif action == "nudge_spawn_position":
            target_state["spawn_nudged"] = True
        else:
            target_state["subsystem_restarted"] = True
