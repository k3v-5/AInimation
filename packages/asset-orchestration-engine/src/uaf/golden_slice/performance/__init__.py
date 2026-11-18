"""Performance budgeting, profiling, and frame time distribution analytics."""

from uaf.golden_slice.performance.budget import PerformanceBudget, BudgetComplianceReport
from uaf.golden_slice.performance.profiler import (
    GoldenSliceProfiler,
    ProfilingSummary,
    SubsystemFrameCost,
)

__all__ = [
    "PerformanceBudget",
    "BudgetComplianceReport",
    "GoldenSliceProfiler",
    "ProfilingSummary",
    "SubsystemFrameCost",
]
