"""World Partition cell streaming, Data Layer, and HLOD integration bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CellStreamingState(str, Enum):
    LOADED = "Loaded"
    UNLOADED = "Unloaded"
    STREAMING = "Streaming"
    FAILED = "Failed"


@dataclass
class WorldPartitionCellPayload:
    cell_id: str
    grid_coords: Tuple[int, int]
    state: CellStreamingState = CellStreamingState.UNLOADED
    priority: float = 1.0
    hlod_tier: int = 0
    assigned_data_layers: List[str] = field(default_factory=list)
    actor_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "grid_coords": list(self.grid_coords),
            "state": self.state.value,
            "priority": self.priority,
            "hlod_tier": self.hlod_tier,
            "assigned_data_layers": self.assigned_data_layers,
            "actor_count": self.actor_count,
        }


class WorldPartitionBridge:
    """Manages UE5 World Partition cell states synchronized with UAF-81.81."""

    def __init__(self, grid_size: float = 128.0) -> None:
        self.grid_size = grid_size
        self.cells: Dict[str, WorldPartitionCellPayload] = {}

    def get_or_create_cell(self, x: int, y: int) -> WorldPartitionCellPayload:
        cell_id = f"cell_{x}_{y}"
        if cell_id not in self.cells:
            self.cells[cell_id] = WorldPartitionCellPayload(
                cell_id=cell_id,
                grid_coords=(x, y),
                state=CellStreamingState.UNLOADED,
            )
        return self.cells[cell_id]

    def set_cell_state(self, x: int, y: int, state: CellStreamingState) -> WorldPartitionCellPayload:
        cell = self.get_or_create_cell(x, y)
        cell.state = state
        return cell

    def update_cell_state(
        self,
        cell_id: str,
        grid_coords: Tuple[int, int],
        state: CellStreamingState,
        priority: float = 1.0,
        hlod_tier: int = 0,
        data_layers: Optional[List[str]] = None,
    ) -> WorldPartitionCellPayload:
        cell = WorldPartitionCellPayload(
            cell_id=cell_id,
            grid_coords=grid_coords,
            state=state,
            priority=priority,
            hlod_tier=hlod_tier,
            assigned_data_layers=data_layers or [],
        )
        self.cells[cell_id] = cell
        return cell

    def get_cell(self, cell_id: str) -> Optional[WorldPartitionCellPayload]:
        return self.cells.get(cell_id)

    def get_loaded_cells(self) -> List[WorldPartitionCellPayload]:
        return [c for c in self.cells.values() if c.state == CellStreamingState.LOADED]
