# Phase 40 Legacy Imports
from .core.memory_schema import FailureRecord, CorrectionRecord, StrategyRecord
from .core.failure_registry import FailureCategory, FailureTypeRegistry
from .storage.sqlite_memory_store import SQLiteMemoryStore
from .analytics.similarity_engine import SimilarityEngine
from .analytics.confidence_engine import ConfidenceEngine
from .analytics.pattern_detector import PatternDetector
from .retrieval.memory_ranker import MemoryRanker
from .recommendation.generation_advisor import GenerationAdvisor
from .api.asset_memory_api import AssetMemoryAPI

# Phase 73 Context & Memory Management Imports
from .core.memory_types import (
    MemoryType, MemoryScope, MemoryStatus, MemorySource, MemoryRecord
)
from .core.exceptions import (
    MemoryError, MemoryNotFoundError, MemoryPermissionDeniedError,
    MemoryConflictError, ContextBudgetExceededError
)
from .core.memory_provenance import MemoryProvenanceService, ProvenanceNode
from .core.memory_versioning import MemoryVersionManager
from .query.memory_query_engine import MemoryQueryEngine
from .store.memory_store import MemoryStore
from .context.context_relevance import ContextRelevanceEngine
from .context.conflict_detector import ContextConflictDetector
from .context.context_builder import ContextBuilder, ExecutionContext
from .context.context_snapshot import ContextSnapshot, ContextSnapshotManager
from .core.memory_consolidator import MemoryConsolidator
from .governance.memory_governance import MemoryGovernanceGuard
from .api.memory_api import ContextMemoryAPI

__all__ = [
    # Phase 40
    "FailureRecord",
    "CorrectionRecord",
    "StrategyRecord",
    "FailureCategory",
    "FailureTypeRegistry",
    "SQLiteMemoryStore",
    "SimilarityEngine",
    "ConfidenceEngine",
    "PatternDetector",
    "MemoryRanker",
    "GenerationAdvisor",
    "AssetMemoryAPI",
    # Phase 73
    "MemoryType",
    "MemoryScope",
    "MemoryStatus",
    "MemorySource",
    "MemoryRecord",
    "MemoryError",
    "MemoryNotFoundError",
    "MemoryPermissionDeniedError",
    "MemoryConflictError",
    "ContextBudgetExceededError",
    "MemoryProvenanceService",
    "ProvenanceNode",
    "MemoryVersionManager",
    "MemoryQueryEngine",
    "MemoryStore",
    "ContextRelevanceEngine",
    "ContextConflictDetector",
    "ContextBuilder",
    "ExecutionContext",
    "ContextSnapshot",
    "ContextSnapshotManager",
    "MemoryConsolidator",
    "MemoryGovernanceGuard",
    "ContextMemoryAPI"
]
