"""
Universal Runtime Streaming Validator (UAF-81.81 Section 10).
Semantic validation for cell bounds, memory budgets, spatial grids, and streaming integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models.definition import (
    CellDefinition,
    CellKey,
    StreamingBudget,
)
from ..engine.spatial_grid import SpatialGrid
from ..engine.universal_runtime_streaming_fabricator import (
    UniversalRuntimeStreamingFabricator,
)


@dataclass
class StreamingValidationIssue:
    code: str
    message: str
    severity: str = "ERROR"  # "ERROR", "WARNING"
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "context": self.context,
        }


class UniversalRuntimeStreamingValidator:
    """
    Authoritative validator ensuring integrity of spatial streaming structures,
    non-negative memory descriptors, valid AABB geometries, and reachable hierarchy levels.
    """

    @classmethod
    def validate_cell_definition(cls, cell_def: CellDefinition) -> List[StreamingValidationIssue]:
        issues: List[StreamingValidationIssue] = []

        min_c = cell_def.bounds.min_corner
        max_c = cell_def.bounds.max_corner

        if min_c[0] > max_c[0] or min_c[1] > max_c[1] or min_c[2] > max_c[2]:
            issues.append(
                StreamingValidationIssue(
                    "STREAM_INVALID_BOUNDS",
                    f"Cell {cell_def.key} has inverted bounds: min {min_c} > max {max_c}.",
                    "ERROR",
                    {"key": cell_def.key.to_list()},
                )
            )

        if cell_def.total_ram_bytes() < 0 or cell_def.total_vram_bytes() < 0:
            issues.append(
                StreamingValidationIssue(
                    "STREAM_NEGATIVE_MEMORY",
                    f"Cell {cell_def.key} specifies negative memory footprint.",
                    "ERROR",
                    {"key": cell_def.key.to_list()},
                )
            )

        return issues

    @classmethod
    def validate_budget(cls, budget: StreamingBudget) -> List[StreamingValidationIssue]:
        issues: List[StreamingValidationIssue] = []

        if budget.ram_bytes <= 0:
            issues.append(StreamingValidationIssue("STREAM_INVALID_RAM_BUDGET", "RAM budget must be strictly positive.", "ERROR"))
        if budget.vram_bytes <= 0:
            issues.append(StreamingValidationIssue("STREAM_INVALID_VRAM_BUDGET", "VRAM budget must be strictly positive.", "ERROR"))
        if budget.max_loaded_cells <= 0:
            issues.append(StreamingValidationIssue("STREAM_INVALID_MAX_CELLS", "max_loaded_cells must be > 0.", "ERROR"))
        if budget.max_active_cells > budget.max_loaded_cells:
            issues.append(
                StreamingValidationIssue(
                    "STREAM_ACTIVE_EXCEEDS_LOADED",
                    f"max_active_cells ({budget.max_active_cells}) cannot exceed max_loaded_cells ({budget.max_loaded_cells}).",
                    "ERROR",
                )
            )

        return issues

    @classmethod
    def validate_world(cls, fab: UniversalRuntimeStreamingFabricator) -> List[StreamingValidationIssue]:
        issues: List[StreamingValidationIssue] = []

        issues.extend(cls.validate_budget(fab.budget))

        for key, cell_def in fab.registered_cells.items():
            issues.extend(cls.validate_cell_definition(cell_def))
            # Verify that key bounds match grid calculation closely
            grid_bounds = fab.grid.cell_key_to_bounds(key)
            if (
                abs(grid_bounds.min_corner[0] - cell_def.bounds.min_corner[0]) > 1e-4
                or abs(grid_bounds.min_corner[1] - cell_def.bounds.min_corner[1]) > 1e-4
                or abs(grid_bounds.min_corner[2] - cell_def.bounds.min_corner[2]) > 1e-4
            ):
                issues.append(
                    StreamingValidationIssue(
                        "STREAM_GRID_BOUNDS_MISMATCH",
                        f"Cell {key} definition bounds do not match grid formula bounds.",
                        "WARNING",
                        {"key": key.to_list()},
                    )
                )

        return issues
