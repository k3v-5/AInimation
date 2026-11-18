"""
Universal Asset Factory (UAF) - Capability & Generation Strategy Fabric (UAF-81.2)
"""

from .capabilities import CapabilityType, CapabilityContract, ComprehensiveCapability
from .strategies import (
    StrategyCategory,
    DeterminismMode,
    GenerationStrategy,
    StrategyRegistry,
)
from .implementations import ExecutionBackend, ImplementationDescription, ImplementationRegistry
from .evaluation import (
    StrategyScore,
    CandidateEvaluation,
    StrategyDecisionTrace,
    StrategyEvaluator,
)
from .planning import (
    GenerationPlanNode,
    GenerationPlan,
    GenerationPlanner,
    PlanningResult,
    Replanner,
    ReplanRequest,
    ReplanningResult,
)

__all__ = [
    "CapabilityType",
    "CapabilityContract",
    "ComprehensiveCapability",
    "StrategyCategory",
    "DeterminismMode",
    "GenerationStrategy",
    "StrategyRegistry",
    "ExecutionBackend",
    "ImplementationDescription",
    "ImplementationRegistry",
    "StrategyScore",
    "CandidateEvaluation",
    "StrategyDecisionTrace",
    "StrategyEvaluator",
    "GenerationPlanNode",
    "GenerationPlan",
    "GenerationPlanner",
    "PlanningResult",
    "Replanner",
    "ReplanRequest",
    "ReplanningResult",
]
