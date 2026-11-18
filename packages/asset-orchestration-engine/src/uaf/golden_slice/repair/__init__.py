"""Autonomous failure analysis, checkpointed self-repair, and knowledge base."""

from uaf.golden_slice.repair.analyzer import FailureDiagnosis, FailureAnalyzer
from uaf.golden_slice.repair.knowledge_base import KnowledgeEntry, FailureKnowledgeBase
from uaf.golden_slice.repair.engine import (
    RegressionTestRecord,
    RepairExecutionResult,
    SelfRepairEngine,
)

__all__ = [
    "FailureDiagnosis",
    "FailureAnalyzer",
    "KnowledgeEntry",
    "FailureKnowledgeBase",
    "RegressionTestRecord",
    "RepairExecutionResult",
    "SelfRepairEngine",
]
