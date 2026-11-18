"""
Acceptance Test Suite for UAF-81.81 — Universal Runtime Scene Streaming & World Partitioning.
Validates Contracts, SpatialGrid, CellStateMachine, StreamingScheduler, MemoryBudget,
HLOD, Visibility, Snapshots, Determinism, Validator, UE5 Packager, and Golden Scenarios.
"""

import math
from typing import Dict, List, Optional, Set, Tuple
import pytest
from uaf.runtime_streaming import (
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
    SpatialGrid,
    LEGAL_TRANSITIONS,
    CellStateMachine,
    StreamingScheduler,
    VisibilityCuller,
    UniversalRuntimeStreamingFabricator,
    StreamingValidationIssue,
    UniversalRuntimeStreamingValidator,
    UniversalRuntimeStreamingPackager,
)


# ==============================================================================
# HELPER BUILDERS
# ==============================================================================

def make_test_grid() -> SpatialGrid:
    return SpatialGrid(base_cell_size=64.0, scale_multiplier=2.0, max_levels=4)


def make_test_cell(
    level: int,
    x: int,
    y: int,
    z: int,
    grid: Optional[SpatialGrid] = None,
    ram_mb: int = 10,
    vram_mb: int = 20,
    is_critical: bool = False,
    data_layer: str = "Default",
) -> CellDefinition:
    g = grid or make_test_grid()
    key = CellKey(level=level, x=x, y=y, z=z)
    bounds = g.cell_key_to_bounds(key)
    res = [
        CellResourceDescriptor("mesh_main", "STATIC_MESH", ram_bytes=ram_mb * 1024 * 1024, vram_bytes=vram_mb * 1024 * 1024)
    ]
    return CellDefinition(
        key=key,
        bounds=bounds,
        resources=res,
        entity_count=50,
        is_critical=is_critical,
        data_layer=data_layer,
    )


# ==============================================================================
# 1. CONTRACTS & CANONICAL DATA MODEL (81.81.0)
# ==============================================================================

class TestCellKeyAndContracts:
    def test_cell_key_immutability_and_hash(self):
        k1 = CellKey(0, 1, 2, 3)
        k2 = CellKey(0, 1, 2, 3)
        assert k1 == k2
        assert hash(k1) == hash(k2)
        d = {k1: "cell_1"}
        assert d[k2] == "cell_1"

    def test_cell_key_ordering(self):
        k1 = CellKey(0, 0, 0, 0)
        k2 = CellKey(0, 1, 0, 0)
        k3 = CellKey(1, 0, 0, 0)
        sorted_keys = sorted([k3, k2, k1])
        assert sorted_keys == [k1, k2, k3]

    def test_cell_key_serialization(self):
        k = CellKey(1, -2, 5, 0)
        assert k.to_string() == "C_1_-2_5_0"
        assert k.to_list() == [1, -2, 5, 0]
        assert CellKey.from_string("C_1_-2_5_0") == k
        assert CellKey.from_list([1, -2, 5, 0]) == k

    def test_cell_bounds_calculations(self):
        b = CellBounds((0.0, 0.0, 0.0), (64.0, 64.0, 64.0))
        assert b.center() == (32.0, 32.0, 32.0)
        assert b.extents() == (32.0, 32.0, 32.0)
        assert b.size() == (64.0, 64.0, 64.0)
        assert b.contains_point((10.0, 20.0, 30.0)) is True
        assert b.contains_point((70.0, 20.0, 30.0)) is False
        assert b.closest_distance_to_point((64.0, 32.0, 32.0)) == 0.0
        assert b.closest_distance_to_point((74.0, 32.0, 32.0)) == pytest.approx(10.0, abs=1e-4)


# ==============================================================================
# 2. SPATIAL GRID & REGIONS (81.81.1)
# ==============================================================================

class TestSpatialGridEngine:
    def test_world_to_cell_key(self):
        grid = make_test_grid()
        # Level 0 is 64m
        assert grid.world_to_cell_key((10.0, 20.0, 30.0), level=0) == CellKey(0, 0, 0, 0)
        assert grid.world_to_cell_key((65.0, -10.0, 130.0), level=0) == CellKey(0, 1, -1, 2)
        # Level 1 is 128m
        assert grid.world_to_cell_key((65.0, 10.0, 130.0), level=1) == CellKey(1, 0, 0, 1)

    def test_cell_key_to_bounds(self):
        grid = make_test_grid()
        bounds = grid.cell_key_to_bounds(CellKey(0, 1, 2, 3))
        assert bounds.min_corner == (64.0, 128.0, 192.0)
        assert bounds.max_corner == (128.0, 192.0, 256.0)

    def test_neighborhood_queries(self):
        grid = make_test_grid()
        k = CellKey(0, 5, 5, 5)
        neighbors = grid.get_neighbors(k, radius=1)
        # 3^3 - 1 = 26 neighbors
        assert len(neighbors) == 26
        assert k not in neighbors
        assert CellKey(0, 4, 4, 4) in neighbors
        assert CellKey(0, 6, 6, 6) in neighbors

    def test_region_and_radius_queries(self):
        grid = make_test_grid()
        cells = grid.query_region((0.0, 0.0, 0.0), (100.0, 50.0, 20.0), level=0)
        # x covers [0, 64, 128] -> x in (0, 1) -> 2 * 1 * 1 = 2 cells
        assert CellKey(0, 0, 0, 0) in cells
        assert CellKey(0, 1, 0, 0) in cells
        assert len(cells) == 2

        radius_cells = grid.query_radius((0.0, 0.0, 0.0), 30.0, level=0)
        assert len(radius_cells) >= 1
        assert CellKey(0, 0, 0, 0) in radius_cells

    def test_hierarchy_parent_children(self):
        grid = make_test_grid()
        child = CellKey(0, 4, 6, 8)
        parent = grid.get_parent_key(child)
        assert parent == CellKey(1, 2, 3, 4)

        re_children = grid.get_child_keys(parent)
        assert len(re_children) == 8  # 2x2x2
        assert child in re_children


# ==============================================================================
# 3. CELL LIFECYCLE & STATE MACHINE (81.81.2)
# ==============================================================================

class TestCellStateMachine:
    def test_legal_transitions_path(self):
        sm = CellStateMachine()
        k = CellKey(0, 0, 0, 0)
        assert sm.get_state(k) == CellState.UNLOADED

        assert sm.transition(k, CellState.LOADING) == CellState.LOADING
        assert sm.transition(k, CellState.LOADED) == CellState.LOADED
        assert sm.transition(k, CellState.ACTIVE) == CellState.ACTIVE
        assert sm.transition(k, CellState.LOADED) == CellState.LOADED
        assert sm.transition(k, CellState.UNLOADING) == CellState.UNLOADING
        assert sm.transition(k, CellState.UNLOADED) == CellState.UNLOADED
        assert sm.get_revision(k) == 6

    def test_direct_active_to_unloading(self):
        sm = CellStateMachine()
        k = CellKey(0, 1, 1, 1)
        sm.transition(k, CellState.LOADING)
        sm.transition(k, CellState.LOADED)
        sm.transition(k, CellState.ACTIVE)
        # Direct unloading from active
        assert sm.transition(k, CellState.UNLOADING) == CellState.UNLOADING
        assert sm.transition(k, CellState.UNLOADED) == CellState.UNLOADED

    def test_loading_cancellation_rollback(self):
        sm = CellStateMachine()
        k = CellKey(0, 2, 2, 2)
        sm.transition(k, CellState.LOADING)
        # Rollback on load failure/cancellation
        assert sm.transition(k, CellState.UNLOADED) == CellState.UNLOADED

    def test_illegal_transitions_raise_contract_error(self):
        sm = CellStateMachine()
        k = CellKey(0, 0, 0, 0)
        with pytest.raises(InvalidCellStateTransitionError):
            sm.transition(k, CellState.ACTIVE)  # UNLOADED -> ACTIVE is illegal

        with pytest.raises(InvalidCellStateTransitionError):
            sm.transition(k, CellState.LOADED)  # UNLOADED -> LOADED is illegal

        sm.transition(k, CellState.LOADING)
        with pytest.raises(InvalidCellStateTransitionError):
            sm.transition(k, CellState.ACTIVE)  # LOADING -> ACTIVE is illegal

    def test_lifecycle_hooks(self):
        sm = CellStateMachine()
        k = CellKey(0, 0, 0, 0)
        hook_fired = []

        sm.register_hook(CellState.UNLOADED, CellState.LOADING, lambda key: hook_fired.append(key))
        sm.transition(k, CellState.LOADING)
        assert hook_fired == [k]


# ==============================================================================
# 4. DETERMINISTIC STREAMING SCHEDULER (81.81.3)
# ==============================================================================

class TestStreamingScheduler:
    def test_priority_scoring_components(self):
        grid = make_test_grid()
        sched = StreamingScheduler(grid)
        cell = make_test_cell(0, 0, 0, 0, grid)

        obs_stationary = ObserverState(position=(10.0, 10.0, 10.0), view_distance=200.0)
        prio_close = sched.calculate_priority(cell, obs_stationary, distance=10.0, is_visible=True, current_tick=100)

        prio_far = sched.calculate_priority(cell, obs_stationary, distance=180.0, is_visible=True, current_tick=100)
        assert prio_close > prio_far

    def test_predictive_velocity_prefetch(self):
        grid = make_test_grid()
        sched = StreamingScheduler(grid)
        # Cell at +X (100, 0, 0)
        cell_ahead = make_test_cell(0, 1, 0, 0, grid)
        # Cell at -X (-100, 0, 0)
        cell_behind = make_test_cell(0, -2, 0, 0, grid)

        # Observer moving fast along +X
        obs = ObserverState(position=(0.0, 0.0, 0.0), velocity=(50.0, 0.0, 0.0), forward=(1.0, 0.0, 0.0), view_distance=300.0)

        prio_ahead = sched.calculate_priority(cell_ahead, obs, distance=64.0, is_visible=True, current_tick=100)
        prio_behind = sched.calculate_priority(cell_behind, obs, distance=64.0, is_visible=False, current_tick=100)
        assert prio_ahead > prio_behind

    def test_total_order_determinism(self):
        grid = make_test_grid()
        sched = StreamingScheduler(grid)
        k1 = CellKey(0, 1, 2, 3)
        k2 = CellKey(0, 1, 2, 4)

        # Equal priority and distance
        tok1 = sched.compute_total_order_key(k1, 50.0, 100.0)
        tok2 = sched.compute_total_order_key(k2, 50.0, 100.0)
        # k1 should come before k2 strictly
        assert tok1 < tok2


# ==============================================================================
# 5. MEMORY BUDGET MANAGER (81.81.4)
# ==============================================================================

class TestMemoryBudgetManager:
    def test_budget_can_fit_enforcement(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        # Budget only allows 25 MB RAM
        fab.set_budget(StreamingBudget(ram_bytes=25 * 1024 * 1024, max_loaded_cells=10, max_loads_per_tick=5))
        fab.start()

        # Register two 20 MB cells
        c1 = make_test_cell(0, 0, 0, 0, grid, ram_mb=20)
        c2 = make_test_cell(0, 1, 0, 0, grid, ram_mb=20)
        fab.register_cell(c1)
        fab.register_cell(c2)

        fab.set_observer("main", ObserverState(position=(0.0, 0.0, 0.0), view_distance=300.0))

        # First tick should load c1 (20MB fits in 25MB), but c2 (20MB + 20MB = 40MB > 25MB) cannot fit!
        plan = fab.update(0.016)
        assert len(plan.loads) == 1
        assert plan.loads[0] == c1.key
        assert fab.metrics.current_ram_bytes == 20 * 1024 * 1024

    def test_ordered_eviction_when_moving_away(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        fab.set_budget(StreamingBudget(ram_bytes=500 * 1024 * 1024, max_loaded_cells=4, max_loads_per_tick=4))
        fab.start()

        c0 = make_test_cell(0, 0, 0, 0, grid)
        c1 = make_test_cell(0, 1, 0, 0, grid)
        c5 = make_test_cell(0, 5, 0, 0, grid)
        fab.register_cell(c0)
        fab.register_cell(c1)
        fab.register_cell(c5)

        # Observer near c0 and c1
        fab.set_observer("main", ObserverState(position=(0.0, 0.0, 0.0), view_distance=150.0))
        fab.update(0.016)
        assert fab.state_machine.get_state(c0.key) in (CellState.LOADED, CellState.ACTIVE)
        assert fab.state_machine.get_state(c1.key) in (CellState.LOADED, CellState.ACTIVE)

        # Observer teleports near c5 (320m away)
        fab.set_observer("main", ObserverState(position=(320.0, 0.0, 0.0), view_distance=150.0))
        plan2 = fab.update(0.016)

        # c0 and c1 should be evicted/unloaded
        assert c0.key in plan2.unloads or c1.key in plan2.unloads
        assert c5.key in plan2.loads


# ==============================================================================
# 6. HIERARCHICAL LEVEL OF DETAIL - HLOD (81.81.5)
# ==============================================================================

class TestHierarchicalLevelOfDetail:
    def test_hlod_distance_transitions(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        fab.start()

        c = make_test_cell(0, 0, 0, 0, grid)
        fab.register_cell(c)

        # Close -> LOD0 (inside cell or < 80m from bounds)
        fab.set_observer("main", ObserverState(position=(10.0, 10.0, 10.0), view_distance=500.0))
        plan = fab.update(0.016)
        assert plan.hlod_transitions.get(c.key) == 0

        # Mid -> LOD1 (dist: 160 - 64 = 96m; in [80m, 180m))
        fab.set_observer("main", ObserverState(position=(160.0, 0.0, 0.0), view_distance=500.0))
        plan = fab.update(0.016)
        assert plan.hlod_transitions.get(c.key) == 1

        # Far -> LOD2 (dist: 300 - 64 = 236m; in [180m, 350m))
        fab.set_observer("main", ObserverState(position=(300.0, 0.0, 0.0), view_distance=500.0))
        plan = fab.update(0.016)
        assert plan.hlod_transitions.get(c.key) == 2

        # Ultra-far -> LOD3 (dist: 500 - 64 = 436m; >= 350m)
        fab.set_observer("main", ObserverState(position=(500.0, 0.0, 0.0), view_distance=600.0))
        plan = fab.update(0.016)
        assert plan.hlod_transitions.get(c.key) == 3


# ==============================================================================
# 7. VISIBILITY & CULLING (81.81.6)
# ==============================================================================

class TestVisibilityAndCulling:
    def test_frustum_cone_culling(self):
        culler = VisibilityCuller()
        b_front = CellBounds((10.0, -10.0, 50.0), (30.0, 10.0, 70.0))
        b_behind = CellBounds((10.0, -10.0, -70.0), (30.0, 10.0, -50.0))

        obs = ObserverState(position=(0.0, 0.0, 0.0), forward=(0.0, 0.0, 1.0), fov_degrees=90.0, view_distance=200.0)

        assert culler.is_bounds_visible(b_front, obs) is True
        assert culler.is_bounds_visible(b_behind, obs) is False


# ==============================================================================
# 8. SNAPSHOTS, DETERMINISM & REPLAY (81.81.8)
# ==============================================================================

class TestSnapshotsAndDeterminism:
    def test_state_hash_determinism(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        c0 = make_test_cell(0, 0, 0, 0, grid)
        fab.register_cell(c0)
        fab.start()

        fab.update(0.016)

        snap1 = fab.take_snapshot()
        snap2 = fab.take_snapshot()

        assert snap1.state_hash == snap2.state_hash
        assert len(snap1.state_hash) == 64

    def test_snapshot_restore(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        c0 = make_test_cell(0, 0, 0, 0, grid)
        fab.register_cell(c0)
        fab.start()

        fab.update(0.016)
        snap = fab.take_snapshot()

        # Mutate world
        fab.state_machine.transition(c0.key, CellState.UNLOADING)
        fab.state_machine.transition(c0.key, CellState.UNLOADED)
        assert fab.state_machine.get_state(c0.key) == CellState.UNLOADED

        # Restore
        fab.restore_snapshot(snap)
        assert fab.state_machine.get_state(c0.key) == CellState.ACTIVE


# ==============================================================================
# 9. VALIDATOR & PACKAGER (81.81.9 & 81.81.10)
# ==============================================================================

class TestValidatorAndPackager:
    def test_validator_detects_invalid_bounds(self):
        cell_bad = CellDefinition(
            key=CellKey(0, 0, 0, 0),
            bounds=CellBounds((100.0, 0.0, 0.0), (50.0, 0.0, 0.0)),  # min > max!
        )
        issues = UniversalRuntimeStreamingValidator.validate_cell_definition(cell_bad)
        assert any(i.code == "STREAM_INVALID_BOUNDS" for i in issues)

    def test_validator_detects_invalid_budget(self):
        b = StreamingBudget(ram_bytes=-100)
        issues = UniversalRuntimeStreamingValidator.validate_budget(b)
        assert any(i.code == "STREAM_INVALID_RAM_BUDGET" for i in issues)

    def test_packager_ue5_world_partition_manifest(self):
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        c0 = make_test_cell(0, 0, 0, 0, grid, data_layer="Quest_Main")
        c1 = make_test_cell(0, 1, 0, 0, grid, data_layer="Default")
        fab.register_cell(c0)
        fab.register_cell(c1)

        pkg = UniversalRuntimeStreamingPackager.package_streaming_world(fab)
        assert "package_hash" in pkg
        assert "ue5_world_partition" in pkg
        ue5 = pkg["ue5_world_partition"]
        assert "Quest_Main" in ue5["DataLayers"]
        assert len(ue5["Cells"]) == 2
        assert ue5["DefaultGrid"]["CellSize"] == 64.0


# ==============================================================================
# 10. GOLDEN SCENARIO: CONTINUOUS TRAVERSAL
# ==============================================================================

class TestGoldenStreamingScenarios:
    def test_golden_continuous_world_traversal(self):
        """Simulate an observer driving across 5 contiguous cells without thrashing."""
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        # Register a row of 6 cells along +X
        cells = [make_test_cell(0, x, 0, 0, grid) for x in range(6)]
        for c in cells:
            fab.register_cell(c)

        fab.set_budget(StreamingBudget(max_loaded_cells=4, max_active_cells=2, max_loads_per_tick=2, max_unloads_per_tick=2))
        fab.start()

        # Step 1: Start at x=0
        fab.set_observer("main", ObserverState(position=(10.0, 10.0, 10.0), velocity=(20.0, 0.0, 0.0), view_distance=150.0))
        fab.update(0.1)
        assert fab.state_machine.get_state(cells[0].key) in (CellState.LOADED, CellState.ACTIVE)

        # Step 2: Drive to x=200 (near cell 3)
        fab.set_observer("main", ObserverState(position=(200.0, 10.0, 10.0), velocity=(20.0, 0.0, 0.0), view_distance=150.0))
        fab.update(0.1)
        fab.update(0.1)

        # Cell 3 should be loaded, while cell 0 should have been unloaded to respect max_loaded_cells=4
        assert fab.state_machine.get_state(cells[3].key) in (CellState.LOADED, CellState.ACTIVE)
        assert fab.metrics.resident_cells_count <= 4

        # Final snapshot check
        snap = fab.take_snapshot()
        assert len(snap.state_hash) == 64
        assert snap.world_revision > 0


# ==============================================================================
# 11. EDGE CASES, STRESS & CONTRACT ENFORCEMENT
# ==============================================================================

class TestStreamingEdgeCasesAndStress:
    def test_spatial_hysteresis_prevents_thrashing(self):
        """Spatial hysteresis keeps loaded cell in memory when observer slightly crosses view distance."""
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        c0 = make_test_cell(0, 0, 0, 0, grid)  # bounds: [0..64]
        fab.register_cell(c0)
        fab.start()

        # Step 1: Observer at (10, 0, 0). Inside cell -> c0 loads & activates
        fab.set_observer("main", ObserverState(position=(10.0, 0.0, 0.0), view_distance=100.0))
        fab.update(0.016)
        assert fab.state_machine.get_state(c0.key) in (CellState.LOADED, CellState.ACTIVE)

        # Step 2: Observer moves to (180, 0, 0).
        # Distance to c0 bounds is 180 - 64 = 116m.
        # view_distance = 100m, but with hysteresis_margin = 32m (total 132m), c0 is NOT evicted!
        fab.set_observer("main", ObserverState(position=(180.0, 0.0, 0.0), view_distance=100.0))
        plan2 = fab.update(0.016)
        assert c0.key not in plan2.unloads
        assert fab.state_machine.get_state(c0.key) in (CellState.LOADED, CellState.ACTIVE)

        # Step 3: Observer moves far to (220, 0, 0).
        # Distance is 220 - 64 = 156m > 132m. Hysteresis exceeded -> c0 is unloaded!
        fab.set_observer("main", ObserverState(position=(220.0, 0.0, 0.0), view_distance=100.0))
        plan3 = fab.update(0.016)
        assert c0.key in plan3.unloads
        assert fab.state_machine.get_state(c0.key) == CellState.UNLOADED

    def test_priority_tie_breaking_determinism(self):
        """Equidistant cells with identical priority score must be ordered strictly by (level, x, y, z)."""
        grid = make_test_grid()
        scheduler = StreamingScheduler(grid=grid)
        sm = CellStateMachine()

        # 4 cells equidistant from (64.0, 64.0, 0.0)
        cells = {
            CellKey(0, 1, 1, 0): make_test_cell(0, 1, 1, 0, grid),
            CellKey(0, 0, 0, 0): make_test_cell(0, 0, 0, 0, grid),
            CellKey(0, 1, 0, 0): make_test_cell(0, 1, 0, 0, grid),
            CellKey(0, 0, 1, 0): make_test_cell(0, 0, 1, 0, grid),
        }

        obs = ObserverState(position=(64.0, 64.0, 0.0), view_distance=200.0)
        budget = StreamingBudget(max_loaded_cells=4, max_loads_per_tick=4)

        plan = scheduler.plan_tick(cells, sm, obs, budget, current_tick=1)
        # All 4 are loaded; check order in plan.loads
        # Tie-breaker key is: (-priority, distance, level, x, y, z)
        # Since distance and priority are identical, level=0, x and y break ties:
        # (0, 0, 0) < (0, 0, 1) < (0, 1, 0) < (0, 1, 1)
        assert plan.loads == [
            CellKey(0, 0, 0, 0),
            CellKey(0, 0, 1, 0),
            CellKey(0, 1, 0, 0),
            CellKey(0, 1, 1, 0),
        ]

    def test_memory_budget_strict_refusal(self):
        """RAM budget exhaustion prevents new cell from loading."""
        grid = make_test_grid()
        fab = UniversalRuntimeStreamingFabricator(grid=grid)
        c0 = make_test_cell(0, 0, 0, 0, grid, ram_mb=80, vram_mb=10)
        c1 = make_test_cell(0, 1, 0, 0, grid, ram_mb=80, vram_mb=10)
        fab.register_cell(c0)
        fab.register_cell(c1)

        # Budget allows 100MB RAM only (c0 takes 80MB, c1 also needs 80MB -> 160MB > 100MB)
        fab.set_budget(StreamingBudget(
            ram_bytes=100 * 1024 * 1024,
            vram_bytes=500 * 1024 * 1024,
            max_loaded_cells=10,
            max_loads_per_tick=5,
        ))
        fab.start()

        fab.set_observer("main", ObserverState(position=(32.0, 32.0, 0.0), view_distance=200.0))
        fab.update(0.016)

        # c0 is closest (observer at 32, 32, 0 is inside c0), so c0 loads
        assert fab.state_machine.get_state(c0.key) in (CellState.LOADED, CellState.ACTIVE)
        # c1 exceeds RAM budget and CANNOT fit
        assert fab.state_machine.get_state(c1.key) == CellState.UNLOADED

    def test_unregistered_cell_query_returns_none(self):
        fab = UniversalRuntimeStreamingFabricator()
        assert fab.get_cell(CellKey(0, 99, 99, 99)) is None

    def test_lifecycle_illegal_direct_jump_raises(self):
        sm = CellStateMachine()
        key = CellKey(0, 0, 0, 0)
        # Direct jump UNLOADED -> ACTIVE is illegal (must go through LOADING -> LOADED -> ACTIVE)
        with pytest.raises(InvalidCellStateTransitionError):
            sm.transition(key, CellState.ACTIVE)

    @pytest.mark.parametrize("x,y,z", [
        (0.0, 0.0, 0.0),
        (-64.0, -64.0, -64.0),
        (127.99, -0.01, 1024.5),
        (-500.2, 350.1, -12.3),
    ])
    def test_spatial_grid_bounds_contain_point(self, x, y, z):
        grid = make_test_grid()
        key = grid.world_to_cell_key((x, y, z), level=0)
        bounds = grid.cell_key_to_bounds(key)
        assert bounds.contains_point((x, y, z)) is True
