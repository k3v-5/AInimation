"""
Universal Runtime Streaming Fabricator Engine (UAF-81.81).
Authoritative scene streaming orchestrator coordinating SpatialGrid, CellStateMachine,
StreamingScheduler, VisibilityCuller, BudgetManager, snapshots, determinism, and replay.
"""

from __future__ import annotations

import copy
import hashlib
import json
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..models.definition import (
    CellBounds,
    CellDefinition,
    CellKey,
    CellResourceDescriptor,
    CellSnapshot,
    CellState,
    ObserverState,
    StreamingBudget,
    StreamingMetrics,
    StreamingPlan,
    StreamingSnapshot,
    StreamingWorldState,
    copy_dict_deterministic,
)
from .cell_state_machine import CellStateMachine
from .spatial_grid import SpatialGrid
from .streaming_scheduler import StreamingScheduler
from .visibility_culler import VisibilityCuller


class UniversalRuntimeStreamingFabricator:
    """
    Authoritative scene streaming fabricator.
    Pure, headless execution coordinating multi-cell residency, memory budgets, and determinism.
    """

    def __init__(
        self,
        streaming_world_id: str = "streaming_world_default",
        grid: Optional[SpatialGrid] = None,
        budget: Optional[StreamingBudget] = None,
    ):
        self.streaming_world_id = streaming_world_id
        self.state = StreamingWorldState.CREATED
        self.grid = grid or SpatialGrid()
        self.budget = budget or StreamingBudget()
        self.culler = VisibilityCuller()
        self.state_machine = CellStateMachine()
        self.scheduler = StreamingScheduler(self.grid, self.culler)

        self.registered_cells: Dict[CellKey, CellDefinition] = {}
        self.observers: Dict[str, ObserverState] = {
            "main": ObserverState()
        }
        self.metrics = StreamingMetrics()
        self.current_tick: int = 0
        self.simulation_time: float = 0.0
        self.world_revision: int = 0
        self.scheduler_revision: int = 0
        self.snapshots: List[StreamingSnapshot] = []

    # --------------------------------------------------------------------------
    # 1. LIFECYCLE MANAGEMENT
    # --------------------------------------------------------------------------

    def initialize(self) -> bool:
        if self.state in (StreamingWorldState.CREATED, StreamingWorldState.STOPPED):
            self.state = StreamingWorldState.INITIALIZING
            self.state = StreamingWorldState.READY
            return True
        return False

    def start(self) -> bool:
        if self.state in (StreamingWorldState.READY, StreamingWorldState.PAUSED):
            self.state = StreamingWorldState.RUNNING
            return True
        elif self.state == StreamingWorldState.CREATED:
            if self.initialize():
                self.state = StreamingWorldState.RUNNING
                return True
        return False

    def pause(self) -> bool:
        if self.state == StreamingWorldState.RUNNING:
            self.state = StreamingWorldState.PAUSED
            return True
        return False

    def resume(self) -> bool:
        if self.state == StreamingWorldState.PAUSED:
            self.state = StreamingWorldState.RUNNING
            return True
        return False

    def stop(self) -> bool:
        if self.state in (StreamingWorldState.RUNNING, StreamingWorldState.PAUSED):
            self.state = StreamingWorldState.STOPPED
            return True
        return False

    def destroy(self) -> bool:
        self.state = StreamingWorldState.DESTROYED
        self.registered_cells.clear()
        self.observers.clear()
        return True

    # --------------------------------------------------------------------------
    # 2. CELL REGISTRATION & CONFIGURATION
    # --------------------------------------------------------------------------

    def register_cell(self, cell_def: CellDefinition) -> None:
        self.registered_cells[cell_def.key] = cell_def
        self.world_revision += 1

    def get_cell(self, key: CellKey) -> Optional[CellDefinition]:
        return self.registered_cells.get(key)

    def set_observer(self, observer_id: str, state: ObserverState) -> None:
        self.observers[observer_id] = state

    def get_observer(self, observer_id: str = "main") -> Optional[ObserverState]:
        return self.observers.get(observer_id)

    def set_budget(self, budget: StreamingBudget) -> None:
        self.budget = budget

    def get_budget(self) -> StreamingBudget:
        return self.budget

    def request_region(
        self,
        min_corner: Tuple[float, float, float],
        max_corner: Tuple[float, float, float],
        level: int = 0,
    ) -> List[CellKey]:
        """Query all CellKeys inside an AABB region."""
        return self.grid.query_region(min_corner, max_corner, level)

    # --------------------------------------------------------------------------
    # 3. STREAMING TICK UPDATE
    # --------------------------------------------------------------------------

    def update(self, delta_time: float = 1.0 / 60.0) -> StreamingPlan:
        """
        Evaluate observer position, update cell residency plans, execute state transitions,
        and maintain strict memory and cell count budgets deterministically.
        """
        if self.state != StreamingWorldState.RUNNING:
            return StreamingPlan()

        self.current_tick += 1
        self.simulation_time += delta_time

        observer = self.observers.get("main", ObserverState())

        # 1. Plan streaming operations using pure deterministic scheduler
        plan = self.scheduler.plan_tick(
            self.registered_cells,
            self.state_machine,
            observer,
            self.budget,
            self.current_tick,
        )

        # 2. Execute Unloads
        for key in plan.unloads:
            st = self.state_machine.get_state(key)
            if st == CellState.ACTIVE:
                self.state_machine.transition(key, CellState.LOADED, "Deactivate for unload")
                st = CellState.LOADED
            if st == CellState.LOADED:
                self.state_machine.transition(key, CellState.UNLOADING, "Begin eviction")
                self.state_machine.transition(key, CellState.UNLOADED, "Eviction finished")
                self.scheduler.record_cell_state_change(key, self.current_tick)
                self.metrics.total_evictions_count += 1

        # 3. Execute Deactivations (ACTIVE -> LOADED)
        for key in plan.deactivations:
            if self.state_machine.get_state(key) == CellState.ACTIVE:
                self.state_machine.transition(key, CellState.LOADED, "Deactivate outside immediate radius")
                self.scheduler.record_cell_state_change(key, self.current_tick)

        # 4. Execute Loads (UNLOADED -> LOADING -> LOADED)
        for key in plan.loads:
            st = self.state_machine.get_state(key)
            if st == CellState.UNLOADED:
                self.state_machine.transition(key, CellState.LOADING, "Schedule load")
                # Deterministic simulation transition to LOADED
                self.state_machine.transition(key, CellState.LOADED, "Resources staged")
                self.scheduler.record_cell_state_change(key, self.current_tick)

        # 5. Execute Activations (LOADED -> ACTIVE)
        for key in plan.activations:
            st = self.state_machine.get_state(key)
            if st == CellState.LOADED:
                self.state_machine.transition(key, CellState.ACTIVE, "Add to active tick")
                self.scheduler.record_cell_state_change(key, self.current_tick)

        # 6. Update Metrics
        resident_count = 0
        active_count = 0
        ram_used = 0
        vram_used = 0

        for key, cell_def in self.registered_cells.items():
            st = self.state_machine.get_state(key)
            if st in (CellState.LOADED, CellState.ACTIVE):
                resident_count += 1
                ram_used += cell_def.total_ram_bytes()
                vram_used += cell_def.total_vram_bytes()
            if st == CellState.ACTIVE:
                active_count += 1

        self.metrics.resident_cells_count = resident_count
        self.metrics.active_cells_count = active_count
        self.metrics.current_ram_bytes = ram_used
        self.metrics.current_vram_bytes = vram_used

        if ram_used > self.budget.ram_bytes or vram_used > self.budget.vram_bytes:
            self.metrics.budget_violations_count += 1

        if not plan.is_empty():
            self.scheduler_revision += 1

        return plan

    # --------------------------------------------------------------------------
    # 4. SNAPSHOTS, DETERMINISM & REPLAY
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> StreamingSnapshot:
        """
        Capture an immutable, fully deterministic snapshot of the streaming world.
        Excludes volatile memory addresses, wall-clock time, and OS thread metrics.
        """
        snap_id = f"snap_stream_{self.current_tick}"

        cell_snaps: Dict[str, Dict[str, Any]] = {}
        active_keys_list: List[List[int]] = []

        observer = self.observers.get("main", ObserverState())

        for key, cell_def in sorted(self.registered_cells.items(), key=lambda x: x[0]):
            state = self.state_machine.get_state(key)
            resident = state in (CellState.LOADED, CellState.ACTIVE)
            visible = self.culler.is_bounds_visible(cell_def.bounds, observer)
            revision = self.state_machine.get_revision(key)

            snap = CellSnapshot(
                key=key,
                state=state,
                lod=0,
                resident=resident,
                visible=visible,
                entity_count=cell_def.entity_count,
                ram_bytes=cell_def.total_ram_bytes(),
                vram_bytes=cell_def.total_vram_bytes(),
                revision=revision,
            )
            cell_snaps[key.to_string()] = snap.to_dict()
            if state == CellState.ACTIVE:
                active_keys_list.append(key.to_list())

        snapshot = StreamingSnapshot(
            snapshot_id=snap_id,
            timestamp=self.simulation_time,
            world_revision=self.world_revision,
            scheduler_revision=self.scheduler_revision,
            cell_snapshots=cell_snaps,
            budget_metrics=self.metrics.to_dict(),
            active_keys=active_keys_list,
        )
        self.snapshots.append(snapshot)
        return snapshot

    def restore_snapshot(self, snapshot: StreamingSnapshot) -> bool:
        """Restore cell states and revisions precisely from a snapshot."""
        for key_str, data in snapshot.cell_snapshots.items():
            key = CellKey.from_string(key_str)
            target_state = CellState(data["state"])
            curr_state = self.state_machine.get_state(key)

            # Direct state override for snapshot restore
            self.state_machine._cell_states[key] = target_state
            self.state_machine._cell_revisions[key] = data["revision"]

        self.world_revision = snapshot.world_revision
        self.scheduler_revision = snapshot.scheduler_revision
        self.simulation_time = snapshot.timestamp
        return True

    def get_metrics(self) -> StreamingMetrics:
        return copy.deepcopy(self.metrics)
