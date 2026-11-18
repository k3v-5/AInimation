"""
Shadow Atlas Allocator & Tile Manager for UAF-81.85.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .core import LightPriority, LightId


@dataclass
class AtlasTile:
    """Represents an allocated region in the shadow atlas."""
    tile_id: str
    light_id: LightId
    x: int
    y: int
    width: int
    height: int
    priority: LightPriority
    last_used_frame: int


class ShadowAtlas:
    """
    Manages a 2D texture atlas for packing spotlight and pointlight shadow maps.
    Uses grid-based power-of-two binning with priority-based eviction.
    """

    def __init__(self, size: int = 4096, bytes_per_pixel: int = 4) -> None:
        self.size = size
        self.bytes_per_pixel = bytes_per_pixel
        self.allocated_tiles: Dict[str, AtlasTile] = {}  # light_id_str -> AtlasTile
        self.current_frame: int = 0

        # Simple grid tracking: default minimum tile size is 128
        self.min_tile_size = 128
        self.grid_cols = self.size // self.min_tile_size
        self.grid_rows = self.size // self.min_tile_size
        # 2D occupancy grid of cells (True = occupied)
        self.occupancy: List[List[bool]] = [
            [False for _ in range(self.grid_cols)] for _ in range(self.grid_rows)
        ]

    @property
    def total_memory_bytes(self) -> int:
        return self.size * self.size * self.bytes_per_pixel

    @property
    def allocated_memory_bytes(self) -> int:
        total = 0
        for tile in self.allocated_tiles.values():
            total += tile.width * tile.height * self.bytes_per_pixel
        return total

    @property
    def occupancy_ratio(self) -> float:
        if self.total_memory_bytes == 0:
            return 0.0
        return self.allocated_memory_bytes / float(self.total_memory_bytes)

    def allocate(
        self,
        light_id: LightId,
        requested_resolution: int,
        priority: LightPriority,
        frame: int = 0
    ) -> Optional[AtlasTile]:
        """
        Allocates a square tile within the atlas.
        If full, attempts eviction of lower priority tiles.
        """
        self.current_frame = frame
        key = light_id.value

        # If already allocated with same size, touch frame and return
        if key in self.allocated_tiles:
            tile = self.allocated_tiles[key]
            if tile.width == requested_resolution:
                tile.last_used_frame = frame
                return tile
            # Size changed, release old first
            self.release(light_id)

        res = max(self.min_tile_size, min(self.size, requested_resolution))
        cells_needed = res // self.min_tile_size

        # Find free block
        pos = self._find_free_cells(cells_needed)
        if pos is None:
            # Try evicting lower priority tiles
            evicted = self._evict_lower_priority(priority, cells_needed)
            if evicted:
                pos = self._find_free_cells(cells_needed)

        if pos is None:
            return None

        col, row = pos
        self._mark_cells(col, row, cells_needed, True)

        tile = AtlasTile(
            tile_id=f"tile_{key}_{frame}",
            light_id=light_id,
            x=col * self.min_tile_size,
            y=row * self.min_tile_size,
            width=res,
            height=res,
            priority=priority,
            last_used_frame=frame,
        )
        self.allocated_tiles[key] = tile
        return tile

    def release(self, light_id: LightId) -> bool:
        """Frees the tile allocated for a light."""
        key = light_id.value
        if key not in self.allocated_tiles:
            return False
        tile = self.allocated_tiles.pop(key)
        col = tile.x // self.min_tile_size
        row = tile.y // self.min_tile_size
        cells = tile.width // self.min_tile_size
        self._mark_cells(col, row, cells, False)
        return True

    def _find_free_cells(self, cells_needed: int) -> Optional[Tuple[int, int]]:
        for r in range(self.grid_rows - cells_needed + 1):
            for c in range(self.grid_cols - cells_needed + 1):
                if self._can_fit(c, r, cells_needed):
                    return (c, r)
        return None

    def _can_fit(self, col: int, row: int, cells: int) -> bool:
        for r in range(row, row + cells):
            for c in range(col, col + cells):
                if self.occupancy[r][c]:
                    return False
        return True

    def _mark_cells(self, col: int, row: int, cells: int, occupied: bool) -> None:
        for r in range(row, row + cells):
            for c in range(col, col + cells):
                self.occupancy[r][c] = occupied

    def _evict_lower_priority(self, min_priority: LightPriority, cells_needed: int) -> bool:
        priority_order = [
            LightPriority.COSMETIC,
            LightPriority.VFX,
            LightPriority.ENVIRONMENT,
            LightPriority.CHARACTER,
            LightPriority.GAMEPLAY,
            LightPriority.CRITICAL,
        ]
        target_idx = priority_order.index(min_priority)

        # Candidates are tiles strictly lower priority than min_priority
        candidates = [
            (tile.light_id, tile.priority, tile.last_used_frame)
            for tile in self.allocated_tiles.values()
            if priority_order.index(tile.priority) < target_idx
        ]

        if not candidates:
            return False

        # Sort by priority ascending, then oldest frame
        candidates.sort(key=lambda c: (priority_order.index(c[1]), c[2]))

        for light_id, _, _ in candidates:
            self.release(light_id)
            if self._find_free_cells(cells_needed) is not None:
                return True

        return False
