"""
ConstraintResolver evaluates constraints against parameters, creates resolution traces,
and enforces the NO-SILENT-CORRECTION invariant.
UAF-81.1 Sections 12, 48, 49, 50.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from .constraint import AssetConstraint, ConstraintType


@dataclass
class ResolutionTraceEntry:
    parameter: str
    requested_value: Any
    resolved_value: Any
    applied_constraints: List[str]
    status: str  # "accepted", "relaxed", "rejected", "adjusted_with_warning"
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter": self.parameter,
            "requested_value": self.requested_value,
            "resolved_value": self.resolved_value,
            "applied_constraints": self.applied_constraints,
            "status": self.status,
            "rationale": self.rationale,
        }


@dataclass
class ConflictReport:
    has_conflicts: bool
    conflicting_parameters: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    traces: List[ResolutionTraceEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_conflicts": self.has_conflicts,
            "conflicting_parameters": self.conflicting_parameters,
            "reasons": self.reasons,
            "traces": [t.to_dict() for t in self.traces],
        }


class ConstraintResolver:
    """
    Evaluates constraints across parameters.
    Guarantees no silent alteration of explicit parameters.
    """
    @classmethod
    def resolve(
        cls,
        parameters: Dict[str, Any],
        constraints: List[AssetConstraint],
    ) -> Tuple[Dict[str, Any], ConflictReport]:
        traces: List[ResolutionTraceEntry] = []
        conflicts: List[str] = []
        reasons: List[str] = []
        resolved_params = dict(parameters)

        # Sort constraints by priority (descending)
        sorted_constraints = sorted(constraints, key=lambda c: c.priority, reverse=True)

        for constraint in sorted_constraints:
            param_name = constraint.target_parameter
            if param_name not in parameters:
                continue

            current_val = resolved_params[param_name]
            satisfied = constraint.evaluate(current_val)

            if not satisfied:
                if constraint.constraint_type == ConstraintType.HARD:
                    conflicts.append(param_name)
                    msg = (
                        f"Hard constraint '{constraint.constraint_id}' violated for '{param_name}': "
                        f"actual={current_val}, expected {constraint.condition} {constraint.expected_value}."
                    )
                    reasons.append(msg)
                    traces.append(
                        ResolutionTraceEntry(
                            parameter=param_name,
                            requested_value=current_val,
                            resolved_value=current_val,
                            applied_constraints=[constraint.constraint_id],
                            status="rejected",
                            rationale=msg,
                        )
                    )
                elif constraint.constraint_type == ConstraintType.SOFT:
                    # Explicit adjustment with recorded rationale (NO SILENT CORRECTION)
                    adjusted_val = constraint.expected_value
                    resolved_params[param_name] = adjusted_val
                    traces.append(
                        ResolutionTraceEntry(
                            parameter=param_name,
                            requested_value=current_val,
                            resolved_value=adjusted_val,
                            applied_constraints=[constraint.constraint_id],
                            status="adjusted_with_warning",
                            rationale=f"Soft constraint adjusted '{param_name}' from {current_val} to {adjusted_val}.",
                        )
                    )
            else:
                traces.append(
                    ResolutionTraceEntry(
                        parameter=param_name,
                        requested_value=current_val,
                        resolved_value=current_val,
                        applied_constraints=[constraint.constraint_id],
                        status="accepted",
                        rationale="Satisfies constraint.",
                    )
                )

        has_conflicts = len(conflicts) > 0
        report = ConflictReport(
            has_conflicts=has_conflicts,
            conflicting_parameters=conflicts,
            reasons=reasons,
            traces=traces,
        )
        return resolved_params, report
