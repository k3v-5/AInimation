"""
Deterministic Streaming Scheduler Engine (UAF-81.81 Section 5 & 7).
Pure priority scoring, total-order lexicographical sorting, predictive prefetch,
preventive budget admission (can_fit), and thrashing-resistant eviction planning.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Set, Tuple

from ..models.definition import (
    CellBounds,
    CellDefinition,
    CellKey,
    CellState,
    ObserverState,
    StreamingBudget,
    StreamingPlan,
)
from .cell_state_machine import CellStateMachine
from .spatial_grid import SpatialGrid
from .visibility_culler import VisibilityCuller


class StreamingScheduler:
    """
    Authoritative deterministic streaming scheduler.
    Pure functional decision pipeline guaranteeing total order reproducibility.
    """

    def __init__(
        self,
        grid: SpatialGrid,
        culler: Optional[VisibilityCuller] = None,
        thrashing_cooldown_ticks: int = 15,
        velocity_lookahead_sec: float = 2.0,
        hysteresis_margin: float = 32.0,
    ):
        self.grid = grid
        self.culler = culler or VisibilityCuller()
        self.thrashing_cooldown_ticks = thrashing_cooldown_ticks
        self.velocity_lookahead_sec = velocity_lookahead_sec
        self.hysteresis_margin = hysteresis_margin
        self._last_state_change_tick: Dict[CellKey, int] = {}

    def record_cell_state_change(self, key: CellKey, current_tick: int) -> None:
        self._last_state_change_tick[key] = current_tick

    def calculate_priority(
        self,
        cell_def: CellDefinition,
        observer: ObserverState,
        distance: float,
        is_visible: bool,
        current_tick: int,
    ) -> float:
        """
        Pure function scoring the streaming priority of a cell.
        Higher score means more urgent to load/keep active.
        """
        view_dist = max(1.0, observer.view_distance)

        # 1. Distance score (0 to 100)
        dist_factor = max(0.0, min(1.0, (view_dist - distance) / view_dist))
        score = dist_factor * 100.0

        # 2. Predictive velocity prefetch (0 to 60)
        speed = observer.speed()
        if speed > 0.01:
            predicted_pos = (
                observer.position[0] + observer.velocity[0] * self.velocity_lookahead_sec,
                observer.position[1] + observer.velocity[1] * self.velocity_lookahead_sec,
                observer.position[2] + observer.velocity[2] * self.velocity_lookahead_sec,
            )
            dist_pred = cell_def.bounds.closest_distance_to_point(predicted_pos)
            pred_factor = max(0.0, min(1.0, (view_dist - dist_pred) / view_dist))
            score += pred_factor * 60.0

        # 3. Visibility score (0 or 40)
        if is_visible:
            score += 40.0

        # 4. Gameplay criticality (+200 boost)
        if cell_def.is_critical:
            score += 200.0

        # 5. Anti-thrashing penalty (-80 penalty if recently toggled)
        last_tick = self._last_state_change_tick.get(cell_def.key, -99999)
        if current_tick - last_tick < self.thrashing_cooldown_ticks:
            score -= 80.0

        return score

    def compute_total_order_key(
        self,
        key: CellKey,
        priority: float,
        distance: float,
    ) -> Tuple[float, float, int, int, int, int]:
        """
        Construct a strict lexicographical total-ordering tuple.
        (-priority, distance, level, x, y, z)
        """
        return (-priority, distance, key.level, key.x, key.y, key.z)

    def plan_tick(
        self,
        registered_cells: Dict[CellKey, CellDefinition],
        state_machine: CellStateMachine,
        observer: ObserverState,
        budget: StreamingBudget,
        current_tick: int,
    ) -> StreamingPlan:
        """
        Generate a deterministic StreamingPlan for this tick.
        Follows strict CAN_FIT admission control and ordered evictions.
        """
        plan = StreamingPlan()

        # Gather resident counts and memory consumption
        current_loaded_keys: Set[CellKey] = set()
        current_active_keys: Set[CellKey] = set()
        used_ram = 0
        used_vram = 0

        for key, cell_def in registered_cells.items():
            state = state_machine.get_state(key)
            if state in (CellState.LOADED, CellState.ACTIVE):
                current_loaded_keys.add(key)
                used_ram += cell_def.total_ram_bytes()
                used_vram += cell_def.total_vram_bytes()
            if state == CellState.ACTIVE:
                current_active_keys.add(key)

        # Evaluate candidate cells in neighborhood / radius
        query_dist = observer.view_distance + (observer.speed() * self.velocity_lookahead_sec) + 64.0
        candidate_keys = self.grid.query_radius(observer.position, query_dist, level=0)

        scored_candidates: List[Tuple[Tuple[float, float, int, int, int, int], CellKey, float, float, bool]] = []
        for key in candidate_keys:
            cell_def = registered_cells.get(key)
            if not cell_def:
                continue
            dist = cell_def.bounds.closest_distance_to_point(observer.position)
            is_vis = self.culler.is_bounds_visible(cell_def.bounds, observer)
            prio = self.calculate_priority(cell_def, observer, dist, is_vis, current_tick)
            order_key = self.compute_total_order_key(key, prio, dist)
            scored_candidates.append((order_key, key, prio, dist, is_vis))

        # Sort all candidates by total order
        scored_candidates.sort(key=lambda item: item[0])

        # Target classification
        desired_active: Set[CellKey] = set()
        desired_loaded: Set[CellKey] = set()

        active_distance_threshold = self.grid.get_cell_size_for_level(0) * 1.5

        for _, key, prio, dist, is_vis in scored_candidates:
            cell_def = registered_cells[key]
            # Spatial Hysteresis: loaded cells have an extra margin before becoming unneeded
            load_margin = self.hysteresis_margin if key in current_loaded_keys else 0.0
            if dist <= (observer.view_distance + load_margin) or cell_def.is_critical:
                desired_loaded.add(key)
                if (dist <= active_distance_threshold or cell_def.is_critical) and len(desired_active) < budget.max_active_cells:
                    desired_active.add(key)

        # ----------------------------------------------------------------------
        # 1. PLAN UNLOADS / EVICTIONS
        # ----------------------------------------------------------------------
        eviction_candidates: List[Tuple[float, float, CellKey]] = []
        for key in current_loaded_keys:
            if key not in desired_loaded:
                cell_def = registered_cells[key]
                dist = cell_def.bounds.closest_distance_to_point(observer.position)
                prio = self.calculate_priority(cell_def, observer, dist, False, current_tick)
                # Sort: lowest priority, farthest distance first
                eviction_candidates.append((prio, -dist, key))

        eviction_candidates.sort(key=lambda item: (item[0], item[1], item[2].level, item[2].x, item[2].y, item[2].z))

        unloads_count = 0
        for _, _, evict_key in eviction_candidates:
            if unloads_count >= budget.max_unloads_per_tick:
                break
            cell_def = registered_cells[evict_key]
            plan.unloads.append(evict_key)
            used_ram -= cell_def.total_ram_bytes()
            used_vram -= cell_def.total_vram_bytes()
            current_loaded_keys.discard(evict_key)
            current_active_keys.discard(evict_key)
            unloads_count += 1

        # ----------------------------------------------------------------------
        # 2. PLAN DEACTIVATIONS (ACTIVE -> LOADED)
        # ----------------------------------------------------------------------
        for key in list(current_active_keys):
            if key not in desired_active and key in current_loaded_keys:
                plan.deactivations.append(key)
                current_active_keys.discard(key)

        # ----------------------------------------------------------------------
        # 3. PLAN LOADS (CAN_FIT ENFORCEMENT)
        # ----------------------------------------------------------------------
        loads_count = 0
        for _, key, _, _, _ in scored_candidates:
            if key in desired_loaded and key not in current_loaded_keys:
                if loads_count >= budget.max_loads_per_tick:
                    break
                if len(current_loaded_keys) >= budget.max_loaded_cells:
                    break

                cell_def = registered_cells[key]
                needed_ram = cell_def.total_ram_bytes()
                needed_vram = cell_def.total_vram_bytes()

                # Check if fits in budget
                if (used_ram + needed_ram <= budget.ram_bytes) and (used_vram + needed_vram <= budget.vram_bytes):
                    plan.loads.append(key)
                    used_ram += needed_ram
                    used_vram += needed_vram
                    current_loaded_keys.add(key)
                    loads_count += 1
                else:
                    # CAN_FIT prevented load
                    break

        # ----------------------------------------------------------------------
        # 4. PLAN ACTIVATIONS (LOADED -> ACTIVE)
        # ----------------------------------------------------------------------
        for key in sorted(desired_active):
            # If already loaded or scheduled to load this tick, and not active
            if key in current_loaded_keys and key not in current_active_keys:
                if state_machine.get_state(key) == CellState.LOADED or key in plan.loads:
                    plan.activations.append(key)
                    current_active_keys.add(key)

        # ----------------------------------------------------------------------
        # 5. HLOD TRANSITIONS
        # ----------------------------------------------------------------------
        for _, key, _, dist, _ in scored_candidates:
            # Deterministic distance bands
            if dist < 80.0:
                lod = 0
            elif dist < 180.0:
                lod = 1
            elif dist < 350.0:
                lod = 2
            else:
                lod = 3
            plan.hlod_transitions[key] = lod

        return plan
