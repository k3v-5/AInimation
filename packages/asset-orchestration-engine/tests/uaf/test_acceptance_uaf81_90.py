"""
UAF-81.90: Universal Procedural Level Design, Modular Assembly (WFC) & Dynamic Mission Director
Acceptance Test Suite.
Verifies WFC 2D/3D solvers, Shannon entropy, AC-3 propagation, backtracking,
topological graph reachability, zero-softlock invariants, quest DAG orchestration,
AI pacing curves, and UE5 level export manifests.
"""

import json
import pytest
from pathlib import Path

from uaf.level_design import (
    Direction2D,
    Direction3D,
    SocketType,
    RoomType,
    ObjectiveType,
    ObjectiveState,
    DependencyType,
    PacingPhase,
    ModularTileDefinition,
    PlacedTile,
    PlayerStressMetric,
    PacingDecision,
    WaveFunctionCollapse2D,
    WaveFunctionCollapse3D,
    WFCContradictionError,
    create_scifi_interior_catalog_2d,
    create_scifi_multilevel_catalog_3d,
    TopologyNode,
    LevelTopologyGraph,
    KeyItem,
    LockedDoor,
    LockKeyProgressionResult,
    LockAndKeyGenerator,
    VolumeTrigger,
    MissionNode,
    MissionGraph,
    MissionCycleError,
    SpatialSpawnPoint,
    DynamicPacingDirector,
    UE5ActorInstance,
    UE5LevelManifest,
    UE5LevelExporter,
)


class TestWFC2D:
    """Test suite for 2D Wave Function Collapse."""

    def test_wfc_2d_solve_and_determinism(self):
        catalog = create_scifi_interior_catalog_2d()
        solver1 = WaveFunctionCollapse2D(width=5, height=5, tile_catalog=catalog, seed=99)
        solver1.constrain_boundaries()
        grid1 = solver1.solve()

        solver2 = WaveFunctionCollapse2D(width=5, height=5, tile_catalog=catalog, seed=99)
        solver2.constrain_boundaries()
        grid2 = solver2.solve()

        assert len(grid1) == 25
        assert len(grid2) == 25
        # Determinism check
        for coord in grid1:
            assert grid1[coord].tile_id == grid2[coord].tile_id
            assert grid1[coord].world_pos == grid2[coord].world_pos

    def test_wfc_2d_ac3_boundary_constraints(self):
        catalog = create_scifi_interior_catalog_2d()
        solver = WaveFunctionCollapse2D(width=4, height=4, tile_catalog=catalog, seed=42)
        assert solver.constrain_boundaries(SocketType.WALL) is True
        grid = solver.solve()

        # Check outer walls
        catalog_dict = {t.tile_id: t for t in catalog}
        for (x, y), tile in grid.items():
            tile_def = catalog_dict[tile.tile_id]
            if y == 3:  # North boundary
                assert tile_def.get_socket_2d(Direction2D.NORTH) == SocketType.WALL
            if y == 0:  # South boundary
                assert tile_def.get_socket_2d(Direction2D.SOUTH) == SocketType.WALL
            if x == 0:  # West boundary
                assert tile_def.get_socket_2d(Direction2D.WEST) == SocketType.WALL
            if x == 3:  # East boundary
                assert tile_def.get_socket_2d(Direction2D.EAST) == SocketType.WALL

    def test_wfc_2d_impossible_constraint_raises_contradiction(self):
        # Catalog with no matching sockets
        t1 = ModularTileDefinition(
            tile_id="t1",
            name="Tile 1",
            sockets_2d={
                Direction2D.NORTH: SocketType.DOOR,
                Direction2D.SOUTH: SocketType.WALL,
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
        )
        t2 = ModularTileDefinition(
            tile_id="t2",
            name="Tile 2",
            sockets_2d={
                Direction2D.NORTH: SocketType.WALL,
                Direction2D.SOUTH: SocketType.VENT,  # Never connects to DOOR
                Direction2D.EAST: SocketType.WALL,
                Direction2D.WEST: SocketType.WALL,
            },
        )
        solver = WaveFunctionCollapse2D(width=1, height=2, tile_catalog=[t1, t2], seed=42)
        # In a 1x2 grid, t1 requires DOOR to the North, but no tile in catalog has DOOR to the South.
        # AC-3 propagation should immediately detect contradiction and return False.
        consistent = solver.constrain_cell(0, 0, {"t1"})
        assert consistent is False

        # Attempting solve should raise WFCContradictionError
        with pytest.raises(WFCContradictionError):
            solver.solve()


class TestWFC3D:
    """Test suite for 3D Multilevel Wave Function Collapse."""

    def test_wfc_3d_multilevel_solve(self):
        catalog = create_scifi_multilevel_catalog_3d()
        solver = WaveFunctionCollapse3D(width=3, depth=3, height=2, tile_catalog=catalog, seed=101)
        grid = solver.solve()

        assert len(grid) == 18
        catalog_dict = {t.tile_id: t for t in catalog}

        # Verify vertical socket compatibility between z=0 and z=1
        for x in range(3):
            for y in range(3):
                tile_bottom = grid[(x, y, 0)]
                tile_top = grid[(x, y, 1)]

                sock_up = catalog_dict[tile_bottom.tile_id].get_socket_3d(Direction3D.UP)
                sock_down = catalog_dict[tile_top.tile_id].get_socket_3d(Direction3D.DOWN)
                assert sock_up == sock_down


class TestTopologyAndLockKey:
    """Test suite for graph pathfinding and zero-softlock progression."""

    def test_topology_graph_pathfinding_and_cycles(self):
        catalog = {t.tile_id: t for t in create_scifi_interior_catalog_2d()}
        solver = WaveFunctionCollapse2D(width=6, height=6, tile_catalog=list(catalog.values()), seed=77)
        solver.constrain_boundaries()
        grid = solver.solve()

        graph = LevelTopologyGraph.from_placed_tiles_2d(grid, catalog)
        components = graph.get_connected_components()
        assert len(components) > 0

        largest = max(components, key=len)
        coords = list(largest)
        if len(coords) >= 2:
            start, goal = coords[0], coords[-1]
            path_bfs = graph.shortest_path_bfs(start, goal)
            path_astar = graph.shortest_path_astar(start, goal)
            assert path_bfs is not None
            assert path_astar is not None
            assert len(path_bfs) == len(path_astar)

        cycles = graph.detect_cycles()
        assert isinstance(cycles, list)

    def test_zero_softlock_generator_and_verifier(self):
        catalog = {t.tile_id: t for t in create_scifi_interior_catalog_2d()}
        solver = WaveFunctionCollapse2D(width=8, height=8, tile_catalog=list(catalog.values()), seed=456)
        solver.constrain_boundaries()
        grid = solver.solve()

        graph = LevelTopologyGraph.from_placed_tiles_2d(grid, catalog)
        components = graph.get_connected_components()
        largest = max(components, key=len)
        coords = list(largest)

        # Select two distant nodes in the connected component
        start = coords[0]
        goal = coords[-1]
        path = graph.shortest_path_astar(start, goal)

        generator = LockAndKeyGenerator(graph, seed=42)
        if path and len(path) >= 4:
            result = generator.generate_lock_and_key_loop(start, goal)
            if result:
                key, door = result
                # Invariant: Key distance < Door distance from start
                dist_key = len(graph.shortest_path_astar(start, key.coord))
                dist_door = len(graph.shortest_path_astar(start, door.coord))
                assert dist_key <= dist_door

                # Progression verification must pass
                verification = generator.verify_progression(start, goal, [door], [key])
                assert verification.is_solvable is True
                assert key.key_id in verification.collected_keys

    def test_softlock_verifier_catches_trapped_player(self):
        # Manually create a trapped graph: Start -> Door -> Key -> Goal
        # Where the key is behind the door!
        graph = LevelTopologyGraph()
        c0, c1, c2, c3 = (0, 0), (1, 0), (2, 0), (3, 0)
        tile = PlacedTile(tile_id="corridor", x=0, y=0, room_type=RoomType.CORRIDOR, world_pos=(0, 0, 0))

        graph.nodes[c0] = TopologyNode(coord=c0, tile=tile)
        graph.nodes[c1] = TopologyNode(coord=c1, tile=tile)
        graph.nodes[c2] = TopologyNode(coord=c2, tile=tile)
        graph.nodes[c3] = TopologyNode(coord=c3, tile=tile)

        graph.nodes[c0].neighbors.add(c1)
        graph.nodes[c1].neighbors.update({c0, c2})
        graph.nodes[c2].neighbors.update({c1, c3})
        graph.nodes[c3].neighbors.add(c2)

        # Door at c1, Key at c2 (behind door!), Goal at c3
        door = LockedDoor(door_id="D1", name="Door 1", coord=c1, required_key_id="K1")
        key = KeyItem(key_id="K1", name="Key 1", coord=c2)

        generator = LockAndKeyGenerator(graph)
        res = generator.verify_progression(c0, c3, [door], [key])

        assert res.is_solvable is False
        assert "softlock_details" in res.model_dump()
        assert res.softlock_details is not None


class TestMissionGraphDAG:
    """Test suite for Mission Graph DAG and Kahn's algorithm."""

    def test_mission_dag_topological_sort_and_progression(self):
        mission = MissionGraph(mission_id="M_STATION", mission_title="Deep Space Station Recovery")

        obj1 = MissionNode(node_id="obj_airlock", name="Breach Airlock", objective_type=ObjectiveType.REACH_EXTRACTION)
        obj2 = MissionNode(node_id="obj_power", name="Restore Auxiliary Power", objective_type=ObjectiveType.HACK_TERMINAL, prerequisites=["obj_airlock"])
        obj3 = MissionNode(node_id="obj_purge", name="Purge Biocontainment", objective_type=ObjectiveType.DEFEND_AREA, prerequisites=["obj_power"])
        obj4 = MissionNode(node_id="obj_escape", name="Escape via Pod", objective_type=ObjectiveType.REACH_EXTRACTION, prerequisites=["obj_purge"])

        mission.add_node(obj1)
        mission.add_node(obj2)
        mission.add_node(obj3)
        mission.add_node(obj4)

        order = mission.validate_dag()
        assert order == ["obj_airlock", "obj_power", "obj_purge", "obj_escape"]

        # Initial state
        ready = mission.get_ready_objectives()
        assert len(ready) == 1
        assert ready[0].node_id == "obj_airlock"
        assert mission.is_mission_complete() is False

        # Progress through objectives
        mission.start_objective("obj_airlock")
        mission.complete_objective("obj_airlock")

        ready = mission.get_ready_objectives()
        assert len(ready) == 1
        assert ready[0].node_id == "obj_power"

        mission.complete_objective("obj_power")
        mission.complete_objective("obj_purge")
        mission.complete_objective("obj_escape")

        assert mission.is_mission_complete() is True

    def test_mission_dag_cycle_detection(self):
        mission = MissionGraph(mission_id="M_CYCLE", mission_title="Broken Mission")
        n1 = MissionNode(node_id="A", name="Node A", objective_type=ObjectiveType.HACK_TERMINAL)
        n2 = MissionNode(node_id="B", name="Node B", objective_type=ObjectiveType.COLLECT_ITEM, prerequisites=["A"])
        mission.add_node(n1)
        mission.add_node(n2)

        # Introduce cycle: A depends on B
        with pytest.raises(MissionCycleError):
            mission.add_dependency(child_id="A", parent_id="B")

    def test_mission_dag_or_dependency_logic(self):
        mission = MissionGraph(mission_id="M_BRANCH", mission_title="Alternative Paths")
        n_start = MissionNode(node_id="start", name="Start", objective_type=ObjectiveType.REACH_EXTRACTION)
        n_path_a = MissionNode(node_id="path_a", name="Stealth Route", objective_type=ObjectiveType.HACK_TERMINAL, prerequisites=["start"])
        n_path_b = MissionNode(node_id="path_b", name="Assault Route", objective_type=ObjectiveType.ELIMINATE_TARGET, prerequisites=["start"])

        # Boss unlocked if EITHER path_a OR path_b is completed
        n_boss = MissionNode(
            node_id="boss",
            name="Final Encounter",
            objective_type=ObjectiveType.ELIMINATE_TARGET,
            prerequisites=["path_a", "path_b"],
            dependency_logic=DependencyType.ANY_REQUIRED,
        )

        mission.add_node(n_start)
        mission.add_node(n_path_a)
        mission.add_node(n_path_b)
        mission.add_node(n_boss)

        mission.complete_objective("start")
        # Only complete path_a
        mission.complete_objective("path_a")

        ready = mission.get_ready_objectives()
        ready_ids = [r.node_id for r in ready]
        assert "boss" in ready_ids


class TestDynamicPacingDirector:
    """Test suite for AI Pacing Director and stress curve regulation."""

    def test_stress_math_and_phase_progression(self):
        director = DynamicPacingDirector(
            calm_duration_sec=2.0,
            buildup_duration_sec=4.0,
            peak_duration_sec=3.0,
            sustained_duration_sec=2.0,
            cooldown_duration_sec=3.0,
        )

        # Baseline calm
        low_stress = PlayerStressMetric(health_ratio=1.0, ammo_ratio=1.0, active_enemies=0)
        assert low_stress.compute_stress_score() == 0.0

        decision = director.update(1.0, low_stress)
        assert decision.current_phase == PacingPhase.CALM
        assert decision.spawn_multiplier == 0.25

        # Wait out calm -> BUILDUP
        decision = director.update(1.5, low_stress)
        assert decision.current_phase == PacingPhase.BUILDUP
        assert decision.spawn_multiplier >= 1.0

        # High stress spike -> PEAK
        high_stress = PlayerStressMetric(health_ratio=0.2, ammo_ratio=0.1, active_enemies=6, damage_received_rate=20.0)
        assert high_stress.compute_stress_score() > 0.7
        decision = director.update(1.0, high_stress)
        assert decision.current_phase == PacingPhase.PEAK
        assert decision.spawn_multiplier == 2.2
        assert decision.music_intensity >= 0.9

        # Overwhelming stress (> 0.90) -> Emergency COOLDOWN
        extreme_stress = PlayerStressMetric(health_ratio=0.05, ammo_ratio=0.0, active_enemies=8, damage_received_rate=30.0)
        decision = director.update(0.5, extreme_stress)
        assert decision.current_phase == PacingPhase.COOLDOWN
        assert decision.spawn_multiplier == 0.0

    def test_out_of_sight_spawn_filtering(self):
        director = DynamicPacingDirector()
        player_pos = (0.0, 0.0, 0.0)
        player_fwd = (1.0, 0.0, 0.0)  # Facing East (+X)

        candidates = [
            SpatialSpawnPoint(spawn_id="sp_front", world_pos=(1200.0, 0.0, 0.0)),     # Directly in front (In FOV)
            SpatialSpawnPoint(spawn_id="sp_front_diag", world_pos=(1200.0, 200.0, 0.0)),  # Inside 90 deg FOV
            SpatialSpawnPoint(spawn_id="sp_behind", world_pos=(-1200.0, 0.0, 0.0)),   # Behind (Valid)
            SpatialSpawnPoint(spawn_id="sp_too_close", world_pos=(-300.0, 0.0, 0.0)), # Behind but under 800 cm
            SpatialSpawnPoint(spawn_id="sp_too_far", world_pos=(-5000.0, 0.0, 0.0)),  # Behind but over 3500 cm
            SpatialSpawnPoint(spawn_id="sp_inactive", world_pos=(-1500.0, 0.0, 0.0), is_active=False),
        ]

        valid = director.select_out_of_sight_spawn_points(
            player_pos=player_pos,
            player_forward_vector=player_fwd,
            candidate_spawns=candidates,
            min_distance=800.0,
            max_distance=3500.0,
            fov_angle_deg=90.0,
        )

        valid_ids = [s.spawn_id for s in valid]
        assert valid_ids == ["sp_behind"]


class TestUE5LevelExporter:
    """Test suite for Unreal Engine 5 level manifest and Python ingestion generation."""

    def test_ue5_export_pipeline(self, tmp_path: Path):
        catalog_list = create_scifi_interior_catalog_2d()
        catalog_dict = {t.tile_id: t for t in catalog_list}

        solver = WaveFunctionCollapse2D(width=4, height=4, tile_catalog=catalog_list, seed=12)
        solver.constrain_boundaries()
        grid = solver.solve()

        doors = [
            LockedDoor(door_id="D_Red", name="Red Gate", coord=(1, 1), required_key_id="K_Red", color="RED")
        ]
        keys = [
            KeyItem(key_id="K_Red", name="Red Pass", coord=(0, 0), color="RED")
        ]
        spawners = [
            SpatialSpawnPoint(spawn_id="Spawn_01", world_pos=(400.0, 800.0, 0.0), room_id="corridor")
        ]

        mission = MissionGraph(mission_id="M_OUTPOST", mission_title="Outpost Alpha")
        mission.add_node(MissionNode(node_id="obj_1", name="Access Terminal", objective_type=ObjectiveType.HACK_TERMINAL))

        exporter = UE5LevelExporter(level_name="L_TestFacility", tile_size_meters=4.0)
        manifest = exporter.build_manifest(
            placed_tiles=grid,
            tile_catalog=catalog_dict,
            doors=doors,
            keys=keys,
            spawn_points=spawners,
            mission_graph=mission,
        )

        assert manifest.level_name == "L_TestFacility"
        assert len(manifest.tiles) == 16
        assert len(manifest.doors) == 1
        assert len(manifest.keys) == 1
        assert len(manifest.spawn_points) == 1
        assert manifest.mission is not None

        # Verify Unreal cm coordinate conversions (4m = 400cm)
        door_instance = manifest.doors[0]
        assert door_instance.location_cm == (400.0, 400.0, 0.0)

        # Export JSON
        out_json = tmp_path / "L_TestFacility_manifest.json"
        exporter.export_to_json(manifest, out_json)
        assert out_json.exists()

        with open(out_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["level_name"] == "L_TestFacility"
            assert len(data["tiles"]) == 16

        # Ingestion script generation
        script = exporter.generate_unreal_python_script(str(out_json))
        assert "Autonomous Unreal Engine 5 Procedural Level Ingestion Script" in script
        assert "import_procedural_level" in script
        assert "L_TestFacility_manifest.json" in script

    def test_end_to_end_level_design_pipeline(self, tmp_path: Path):
        """
        Full vertical integration:
        WFC 2D layout -> Graph Topology -> Lock & Key Loop -> Mission DAG ->
        AI Pacing Director -> UE5 Export Manifest -> Portable Script.
        """
        # 1. WFC Procedural Assembly
        catalog = create_scifi_interior_catalog_2d()
        catalog_dict = {t.tile_id: t for t in catalog}
        solver = WaveFunctionCollapse2D(width=7, height=7, tile_catalog=catalog, seed=888)
        solver.constrain_boundaries()
        placed_tiles = solver.solve()
        assert len(placed_tiles) == 49

        # 2. Topology Analysis & Pathfinding
        graph = LevelTopologyGraph.from_placed_tiles_2d(placed_tiles, catalog_dict)
        components = graph.get_connected_components()
        assert len(components) > 0

        largest_comp = max(components, key=len)
        comp_coords = list(largest_comp)
        start_coord, goal_coord = comp_coords[0], comp_coords[-1]
        path = graph.shortest_path_astar(start_coord, goal_coord)
        assert path is not None

        # 3. Lock and Key Generation
        gen = LockAndKeyGenerator(graph, seed=888)
        lock_res = gen.generate_lock_and_key_loop(start_coord, goal_coord)
        doors = [lock_res[1]] if lock_res else []
        keys = [lock_res[0]] if lock_res else []

        if lock_res:
            verif = gen.verify_progression(start_coord, goal_coord, doors, keys)
            assert verif.is_solvable is True

        # 4. Dynamic Mission DAG
        mission = MissionGraph(mission_id="M_E2E", mission_title="Facility Containment")
        n1 = MissionNode(
            node_id="obj_reach_entrance",
            name="Infiltrate Level",
            objective_type=ObjectiveType.REACH_EXTRACTION,
            target_coord=start_coord,
            trigger=VolumeTrigger(
                trigger_id="trig_start",
                center_pos=(float(start_coord[0] * 400), float(start_coord[1] * 400), 0.0),
            ),
        )
        n2 = MissionNode(
            node_id="obj_extract",
            name="Extract from Facility",
            objective_type=ObjectiveType.REACH_EXTRACTION,
            prerequisites=["obj_reach_entrance"],
            target_coord=goal_coord,
        )
        mission.add_node(n1)
        mission.add_node(n2)
        assert mission.validate_dag() == ["obj_reach_entrance", "obj_extract"]

        # 5. AI Pacing Director Simulation
        director = DynamicPacingDirector()
        pacing_decision = director.update(5.0, PlayerStressMetric(health_ratio=0.8, ammo_ratio=0.7, active_enemies=1))
        assert pacing_decision.current_phase in [PacingPhase.CALM, PacingPhase.BUILDUP]

        # 6. UE5 Level Export
        exporter = UE5LevelExporter(level_name="L_E2E_Facility", tile_size_meters=4.0)
        manifest = exporter.build_manifest(
            placed_tiles=placed_tiles,
            tile_catalog=catalog_dict,
            doors=doors,
            keys=keys,
            mission_graph=mission,
        )
        manifest_path = tmp_path / "L_E2E_Facility_manifest.json"
        exporter.export_to_json(manifest, manifest_path)
        assert manifest_path.exists()

        script_content = exporter.generate_unreal_python_script(str(manifest_path))
        assert "L_E2E_Facility" in script_content
