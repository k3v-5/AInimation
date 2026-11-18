"""
Universal Runtime Scene Streaming & World Partitioning Module (UAF-81.81).
Public API exports for deterministic spatial partitioning, cell state machines,
streaming schedulers, memory budgeting, visibility culling, snapshots,
and Unreal Engine 5 World Partitioning adapters.
"""

from .models.definition import (
    BudgetExceededError,
    CellBounds,
    CellDefinition,
    CellKey,
    CellNotFoundError,
    CellResourceDescriptor,
    CellSnapshot,
    CellState,
    EvictionReason,
    HLODLevel,
    InvalidCellStateTransitionError,
    ObserverState,
    StreamingBudget,
    StreamingError,
    StreamingMetrics,
    StreamingPlan,
    StreamingSnapshot,
    StreamingWorldState,
    copy_dict_deterministic,
)

from .engine.spatial_grid import SpatialGrid
from .engine.cell_state_machine import (
    LEGAL_TRANSITIONS,
    CellStateMachine,
)
from .engine.streaming_scheduler import StreamingScheduler
from .engine.visibility_culler import VisibilityCuller
from .engine.universal_runtime_streaming_fabricator import (
    UniversalRuntimeStreamingFabricator,
)

from .validation.universal_runtime_streaming_validator import (
    StreamingValidationIssue,
    UniversalRuntimeStreamingValidator,
)

from .package.universal_runtime_streaming_packager import (
    UniversalRuntimeStreamingPackager,
)

__all__ = [
    "BudgetExceededError",
    "CellBounds",
    "CellDefinition",
    "CellKey",
    "CellNotFoundError",
    "CellResourceDescriptor",
    "CellSnapshot",
    "CellState",
    "EvictionReason",
    "HLODLevel",
    "InvalidCellStateTransitionError",
    "ObserverState",
    "StreamingBudget",
    "StreamingError",
    "StreamingMetrics",
    "StreamingPlan",
    "StreamingSnapshot",
    "StreamingWorldState",
    "copy_dict_deterministic",
    "SpatialGrid",
    "LEGAL_TRANSITIONS",
    "CellStateMachine",
    "StreamingScheduler",
    "VisibilityCuller",
    "UniversalRuntimeStreamingFabricator",
    "StreamingValidationIssue",
    "UniversalRuntimeStreamingValidator",
    "UniversalRuntimeStreamingPackager",
]
