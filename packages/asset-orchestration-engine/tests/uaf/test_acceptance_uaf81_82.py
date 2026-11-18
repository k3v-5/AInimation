"""
Acceptance Test Suite for UAF-81.82:
Universal Runtime AI, Navigation Mesh, Dynamic Avoidance & Behavior Tree System.
Validates NavMesh, A*, Funnel, RVO/ORCA, Perception, Memory Decay, Blackboard,
Behavior Trees, Target Selection, AI LOD, Determinism, Snapshots, and Golden Scenario.
"""

import math
from typing import List, Tuple
import pytest

from uaf.runtime_ai import (
    AIAgent,
    AIAgentSnapshot,
    AIBudget,
    AIEntity,
    AIError,
    AILOD,
    AIMetrics,
    AINumericStateError,
    AIPriority,
    AIRuntimeWorldState,
    AISnapshot,
    AIValidationIssue,
    AStarPathfinder,
    AttackTargetTask,
    BehaviorTree,
    BehaviorTreeInvalid,
    Blackboard,
    BlackboardTypeError,
    BTContext,
    BTNode,
    BTService,
    ConditionGateDecorator,
    CooldownDecorator,
    DamageSensor,
    DamageStimulus,
    DeterministicRNG,
    DynamicObstacle,
    DynamicObstacleManager,
    FunnelAlgorithm,
    HearingSensor,
    HierarchicalPathfinder,
    InvalidNavMesh,
    InvalidNavigationProfile,
    InverterDecorator,
    MoveToTargetTask,
    NavAreaType,
    NavigationProfile,
    NavigationTileUnavailable,
    NavigationWorld,
    NavMesh,
    NavPolygon,
    NavTile,
    NodeStatus,
    ORCAHalfPlane,
    ORCASolver,
    ParallelNode,
    ParallelPolicy,
    PathNotFound,
    PathRequest,
    PathRequestQueue,
    PathResult,
    PathStatus,
    PathValidator,
    PerceptionSensor,
    Portal,
    RepeaterDecorator,
    RVOPrimitive,
    SafeIdleTask,
    SelectorNode,
    SensoryMemory,
    SensoryMemoryEntry,
    SequenceNode,
    SoundStimulus,
    SteeringController,
    TargetSelector,
    TeamRelation,
    TeamRelationProvider,
    TimeoutDecorator,
    UniversalRuntimeAIFabricator,
    UniversalRuntimeAIPackager,
    UniversalRuntimeAIValidator,
    Vec3,
    VisionSensor,
    WaitTicksTask,
    closest_point_on_polygon,
    compute_polygon_area_2d,
    ensure_finite_float,
    ensure_finite_vec3,
    find_shared_edge,
    is_point_inside_polygon_2d,
    is_polygon_convex,
    vec3_add,
    vec3_distance,
    vec3_length,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)


# ==============================================================================
# HELPER BUILDERS
# ==============================================================================

def make_square_polygon(poly_id: int, min_x: float, min_z: float, size: float = 10.0, area_type: str = "GROUND", cost: float = 1.0) -> NavPolygon:
    """Create convex 4-vertex CCW polygon in XZ plane."""
    v0 = (min_x, 0.0, min_z)
    v1 = (min_x + size, 0.0, min_z)
    v2 = (min_x + size, 0.0, min_z + size)
    v3 = (min_x, 0.0, min_z + size)
    return NavPolygon(
        polygon_id=poly_id,
        vertices=(v0, v1, v2, v3),
        area_type=area_type,
        traversal_cost=cost,
    )


def make_linear_test_mesh(num_polys: int = 5, poly_size: float = 10.0) -> NavMesh:
    """Create a linear strip of connected convex polygons along +X."""
    mesh = NavMesh()
    for i in range(num_polys):
        p = make_square_polygon(i + 1, min_x=float(i * poly_size), min_z=0.0, size=poly_size)
        mesh.add_polygon(p)
    mesh.build_adjacency()
    return mesh


# ==============================================================================
# 1. NAVMESH, POLYGONS & GEOMETRY
# ==============================================================================

class TestNavMeshAndGeometry:
    def test_convex_polygon_creation_and_area(self):
        poly = make_square_polygon(1, 0.0, 0.0, 10.0)
        assert is_polygon_convex(poly.vertices) is True
        area = compute_polygon_area_2d(poly.vertices)
        assert pytest.approx(area, 0.01) == 100.0

    def test_concave_polygon_rejected(self):
        # Bowtie / self-intersecting or non-convex
        concave_verts = (
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (5.0, 0.0, 2.0),
            (10.0, 0.0, 10.0),
            (0.0, 0.0, 10.0),
        )
        assert is_polygon_convex(concave_verts) is False
        mesh = NavMesh()
        with pytest.raises(InvalidNavMesh):
            mesh.add_polygon(NavPolygon(1, concave_verts))

    def test_degenerate_polygon_rejected(self):
        degen_verts = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        mesh = NavMesh()
        with pytest.raises(InvalidNavMesh):
            mesh.add_polygon(NavPolygon(1, degen_verts))

    def test_point_inside_and_closest_point(self):
        poly = make_square_polygon(1, 0.0, 0.0, 10.0)
        inside_pt = (5.0, 0.0, 5.0)
        outside_pt = (15.0, 0.0, 5.0)

        assert is_point_inside_polygon_2d(inside_pt, poly.vertices) is True
        assert is_point_inside_polygon_2d(outside_pt, poly.vertices) is False

        closest = closest_point_on_polygon(outside_pt, poly.vertices)
        assert pytest.approx(closest[0]) == 10.0
        assert pytest.approx(closest[2]) == 5.0

    def test_mesh_adjacency_and_shared_edge(self):
        p1 = make_square_polygon(1, 0.0, 0.0, 10.0)
        p2 = make_square_polygon(2, 10.0, 0.0, 10.0)
        edge = find_shared_edge(p1, p2)
        assert edge is not None

        mesh = NavMesh()
        mesh.add_polygon(p1)
        mesh.add_polygon(p2)
        mesh.build_adjacency()

        assert 2 in mesh.get_polygon(1).neighbors
        assert 1 in mesh.get_polygon(2).neighbors

        portal = mesh.get_portal(1, 2)
        assert portal is not None
        assert portal.from_poly == 1
        assert portal.to_poly == 2


# ==============================================================================
# 2. DETERMINISTIC A* PATHFINDING
# ==============================================================================

class TestAStarPathfinder:
    def test_direct_path_traversal(self):
        mesh = make_linear_test_mesh(num_polys=5, poly_size=10.0)
        start = (2.0, 0.0, 5.0)
        goal = (45.0, 0.0, 5.0)

        res = AStarPathfinder.find_path(mesh, start, goal)
        assert res.status == PathStatus.SUCCESS
        assert res.polygons == (1, 2, 3, 4, 5)
        assert len(res.portals) == 4
        assert res.total_cost > 0.0

    def test_same_polygon_path(self):
        mesh = make_linear_test_mesh(num_polys=3)
        start = (2.0, 0.0, 2.0)
        goal = (8.0, 0.0, 8.0)
        res = AStarPathfinder.find_path(mesh, start, goal)
        assert res.status == PathStatus.SUCCESS
        assert res.polygons == (1,)
        assert len(res.portals) == 0

    def test_unreachable_goal_returns_no_path(self):
        mesh = NavMesh()
        # Two disconnected islands
        p1 = make_square_polygon(1, 0.0, 0.0, 10.0)
        p2 = make_square_polygon(2, 100.0, 0.0, 10.0)
        mesh.add_polygon(p1)
        mesh.add_polygon(p2)
        mesh.build_adjacency()

        res = AStarPathfinder.find_path(mesh, (5.0, 0.0, 5.0), (105.0, 0.0, 5.0))
        assert res.status == PathStatus.NO_PATH

    def test_navigation_profile_area_filter(self):
        mesh = make_linear_test_mesh(num_polys=3)
        # Mark middle polygon as WATER
        p2 = make_square_polygon(2, 10.0, 0.0, 10.0, area_type="WATER")
        mesh.add_polygon(p2)
        mesh.build_adjacency()

        # Profile does not allow WATER
        prof = NavigationProfile(profile_id="GroundOnly", allowed_areas=("GROUND",))
        res = AStarPathfinder.find_path(mesh, (5.0, 0.0, 5.0), (25.0, 0.0, 5.0), profile=prof)
        assert res.status == PathStatus.NO_PATH

        # Profile allows WATER
        prof_water = NavigationProfile(profile_id="Amphibious", allowed_areas=("GROUND", "WATER"))
        res2 = AStarPathfinder.find_path(mesh, (5.0, 0.0, 5.0), (25.0, 0.0, 5.0), profile=prof_water)
        assert res2.status == PathStatus.SUCCESS


# ==============================================================================
# 3. FUNNEL ALGORITHM (STRING PULLING)
# ==============================================================================

class TestFunnelAlgorithm:
    def test_straight_corridor_smoothing(self):
        mesh = make_linear_test_mesh(num_polys=4, poly_size=10.0)
        start = (2.0, 0.0, 5.0)
        goal = (38.0, 0.0, 5.0)

        res = AStarPathfinder.find_path(mesh, start, goal)
        assert res.status == PathStatus.SUCCESS

        smoothed = FunnelAlgorithm.smooth_path(start, res.portals, goal)
        # Straight line between start and goal
        assert len(smoothed) == 2
        assert smoothed[0] == start
        assert smoothed[1] == goal

    def test_corner_turn_funnel(self):
        # L-shaped corridor: poly 1 (0..10, 0..10), poly 2 (10..20, 0..10), poly 3 (10..20, 10..20)
        mesh = NavMesh()
        mesh.add_polygon(make_square_polygon(1, 0.0, 0.0, 10.0))
        mesh.add_polygon(make_square_polygon(2, 10.0, 0.0, 10.0))
        mesh.add_polygon(make_square_polygon(3, 10.0, 10.0, 10.0))
        mesh.build_adjacency()

        start = (2.0, 0.0, 2.0)
        goal = (18.0, 0.0, 18.0)
        res = AStarPathfinder.find_path(mesh, start, goal)
        assert res.status == PathStatus.SUCCESS

        smoothed = FunnelAlgorithm.smooth_path(start, res.portals, goal)
        assert len(smoothed) >= 2
        assert smoothed[0] == start
        assert smoothed[-1] == goal


# ==============================================================================
# 4. DYNAMIC OBSTACLES & MESH CARVING
# ==============================================================================

class TestDynamicObstacles:
    def test_dynamic_obstacle_blocks_and_restores_path(self):
        mesh = make_linear_test_mesh(num_polys=3, poly_size=10.0)
        start = (5.0, 0.0, 5.0)
        goal = (25.0, 0.0, 5.0)

        # Before obstacle: path exists
        res1 = AStarPathfinder.find_path(mesh, start, goal)
        assert res1.status == PathStatus.SUCCESS

        # Place cylinder obstacle in poly 2 (center at 15.0, 0.0, 5.0)
        mgr = DynamicObstacleManager()
        obs = DynamicObstacle(obstacle_id="barrier_1", position=(15.0, 0.0, 5.0), radius=2.0)
        affected = mgr.register_obstacle(obs, mesh)
        assert 2 in affected

        # Path now blocked
        res2 = AStarPathfinder.find_path(mesh, start, goal)
        assert res2.status == PathStatus.NO_PATH

        # Remove obstacle -> path restored
        mgr.remove_obstacle("barrier_1", mesh)
        res3 = AStarPathfinder.find_path(mesh, start, goal)
        assert res3.status == PathStatus.SUCCESS


# ==============================================================================
# 5. DYNAMIC AVOIDANCE (STEERING, RVO, ORCA)
# ==============================================================================

class TestAvoidanceAndSteering:
    def test_steering_seek_and_arrive(self):
        pos = (0.0, 0.0, 0.0)
        target = (10.0, 0.0, 0.0)

        v_seek = SteeringController.seek(pos, target, max_speed=5.0)
        assert pytest.approx(v_seek[0]) == 5.0
        assert pytest.approx(v_seek[1]) == 0.0
        assert pytest.approx(v_seek[2]) == 0.0

        v_arrive_close = SteeringController.arrive(pos, (0.05, 0.0, 0.0), max_speed=5.0, stopping_distance=0.1)
        assert v_arrive_close == (0.0, 0.0, 0.0)

    def test_rvo_collision_cone_detection(self):
        pos_a = (0.0, 0.0, 0.0)
        vel_a = (5.0, 0.0, 0.0)
        pos_b = (10.0, 0.0, 0.0)
        vel_b = (-5.0, 0.0, 0.0)  # Head-on collision

        in_cone = RVOPrimitive.is_in_collision_cone(pos_a, vel_a, 0.5, pos_b, vel_b, 0.5, time_horizon=2.0)
        assert in_cone is True

        # Moving away
        vel_a_away = (-5.0, 0.0, 0.0)
        assert RVOPrimitive.is_in_collision_cone(pos_a, vel_a_away, 0.5, pos_b, vel_b, 0.5, time_horizon=2.0) is False

    def test_orca_two_agent_crossing(self):
        # Two agents moving towards each other
        agent_a = AIAgent(agent_id="A", entity_id="E_A", position=(0.0, 0.0, 0.0))
        agent_a.preferred_velocity = (3.0, 0.0, 0.0)

        agent_b = AIAgent(agent_id="B", entity_id="E_B", position=(4.0, 0.0, 0.0))
        agent_b.preferred_velocity = (-3.0, 0.0, 0.0)

        neighbors = [(agent_b.agent_id, agent_b.to_kinematics())]
        safe_vel = ORCASolver.solve_avoidance(agent_a.to_kinematics(), neighbors)

        # Must avoid directly crashing along +X axis
        assert not (math.isnan(safe_vel[0]) or math.isnan(safe_vel[2]))
        # The agent should divert in Z to pass each other
        assert abs(safe_vel[2]) > 0.01 or abs(safe_vel[0]) < 3.0

    def test_orca_zero_division_safety(self):
        # Two agents placed at exact same coordinate
        agent_a = AIAgent(agent_id="A", entity_id="E_A", position=(0.0, 0.0, 0.0))
        agent_b = AIAgent(agent_id="B", entity_id="E_B", position=(0.0, 0.0, 0.0))

        neighbors = [(agent_b.agent_id, agent_b.to_kinematics())]
        safe_vel = ORCASolver.solve_avoidance(agent_a.to_kinematics(), neighbors)
        assert not (math.isnan(safe_vel[0]) or math.isnan(safe_vel[2]))


# ==============================================================================
# 6. PERCEPTION & SENSORY MEMORY DECAY
# ==============================================================================

class TestPerceptionAndMemory:
    def test_vision_fov_and_range(self):
        sensor = VisionSensor(vision_range=20.0, vision_angle_degrees=90.0)
        obs_pos = (0.0, 0.0, 0.0)
        obs_fwd = (1.0, 0.0, 0.0)

        # Directly ahead at 10m -> True
        assert sensor.can_see(obs_pos, obs_fwd, (10.0, 0.0, 0.0)) is True
        # Directly behind at 10m -> False
        assert sensor.can_see(obs_pos, obs_fwd, (-10.0, 0.0, 0.0)) is False
        # Beyond max range (30m) -> False
        assert sensor.can_see(obs_pos, obs_fwd, (30.0, 0.0, 0.0)) is False

    def test_vision_line_of_sight_raycast(self):
        sensor = VisionSensor(vision_range=30.0, vision_angle_degrees=120.0, line_of_sight_required=True)
        obs_pos = (0.0, 0.0, 0.0)
        obs_fwd = (1.0, 0.0, 0.0)
        target_pos = (20.0, 0.0, 0.0)

        # Unblocked
        assert sensor.can_see(obs_pos, obs_fwd, target_pos, raycast_fn=lambda o, d, m: False) is True
        # Blocked
        assert sensor.can_see(obs_pos, obs_fwd, target_pos, raycast_fn=lambda o, d, m: True) is False

    def test_hearing_sound_intensity_decay(self):
        sensor = HearingSensor(sensitivity=1.0, max_hearing_range=50.0)
        obs_pos = (0.0, 0.0, 0.0)
        sound_close = SoundStimulus(source_id="gunshot", position=(5.0, 0.0, 0.0), intensity=100.0)
        sound_far = SoundStimulus(source_id="whisper", position=(40.0, 0.0, 0.0), intensity=1.0)

        assert sensor.perceive_sound(obs_pos, sound_close) is not None
        assert sensor.perceive_sound(obs_pos, sound_far) is None

    def test_sensory_memory_decay_by_logical_ticks(self):
        mem = SensoryMemory(default_ttl_ticks=10)
        mem.record_stimulus("s1", "target_A", "VISION", (10.0, 0.0, 0.0), 10.0, current_tick=1)

        # Tick 1: full confidence
        assert mem.get_entry("target_A").confidence == 1.0

        # Tick 6: 5 ticks elapsed -> confidence ~0.5
        mem.update_decay(current_tick=6)
        entry = mem.get_entry("target_A")
        assert entry is not None
        assert pytest.approx(entry.confidence, 0.01) == 0.5

        # Tick 12: 11 ticks elapsed (> TTL 10) -> purged
        expired = mem.update_decay(current_tick=12)
        assert "target_A" in expired
        assert mem.get_entry("target_A") is None


# ==============================================================================
# 7. BLACKBOARD
# ==============================================================================

class TestBlackboard:
    def test_blackboard_set_get_and_types(self):
        bb = Blackboard()
        bb.set("is_alert", True)
        bb.set("target_pos", (10.0, 0.0, 5.0))
        bb.set("threat_level", 2)
        bb.set("enemy_name", "Goblin")

        assert bb.get("is_alert") is True
        assert bb.get("target_pos") == (10.0, 0.0, 5.0)
        assert bb.get("threat_level") == 2
        assert bb.get("missing_key", 99) == 99

    def test_blackboard_unsupported_type_raises(self):
        bb = Blackboard()
        class VolatileObject:
            pass
        with pytest.raises(BlackboardTypeError):
            bb.set("bad", VolatileObject())


# ==============================================================================
# 8. BEHAVIOR TREES (SEQUENCE, SELECTOR, PARALLEL, DECORATORS, TASKS)
# ==============================================================================

class DummyTask(BTNode):
    def __init__(self, node_id: str, return_status: NodeStatus):
        super().__init__(node_id)
        self.return_status = return_status
        self.tick_count = 0

    def tick(self, context: BTContext) -> NodeStatus:
        self.tick_count += 1
        return self.return_status


class TestBehaviorTrees:
    def test_sequence_node_logic(self):
        ctx = BTContext("A1", Blackboard(), 1, 0.016)
        t1 = DummyTask("t1", NodeStatus.SUCCESS)
        t2 = DummyTask("t2", NodeStatus.SUCCESS)
        seq = SequenceNode("seq", [t1, t2])

        assert seq.tick(ctx) == NodeStatus.SUCCESS
        assert t1.tick_count == 1
        assert t2.tick_count == 1

        # Failure short-circuits
        t_fail = DummyTask("tf", NodeStatus.FAILURE)
        t_unreached = DummyTask("tu", NodeStatus.SUCCESS)
        seq_fail = SequenceNode("seq_fail", [t_fail, t_unreached])
        assert seq_fail.tick(ctx) == NodeStatus.FAILURE
        assert t_fail.tick_count == 1
        assert t_unreached.tick_count == 0

    def test_selector_node_logic(self):
        ctx = BTContext("A1", Blackboard(), 1, 0.016)
        t1 = DummyTask("t1", NodeStatus.FAILURE)
        t2 = DummyTask("t2", NodeStatus.SUCCESS)
        t3 = DummyTask("t3", NodeStatus.SUCCESS)
        sel = SelectorNode("sel", [t1, t2, t3])

        assert sel.tick(ctx) == NodeStatus.SUCCESS
        assert t1.tick_count == 1
        assert t2.tick_count == 1
        assert t3.tick_count == 0  # Short-circuited on t2 success

    def test_parallel_node_policies(self):
        ctx = BTContext("A1", Blackboard(), 1, 0.016)
        t_s = DummyTask("ts", NodeStatus.SUCCESS)
        t_f = DummyTask("tf", NodeStatus.FAILURE)

        par_all = ParallelNode("p_all", [t_s, t_f], policy=ParallelPolicy.SUCCESS_ON_ALL)
        assert par_all.tick(ctx) == NodeStatus.FAILURE

        par_one = ParallelNode("p_one", [t_s, t_f], policy=ParallelPolicy.SUCCESS_ON_ONE)
        assert par_one.tick(ctx) == NodeStatus.SUCCESS

    def test_decorators(self):
        ctx = BTContext("A1", Blackboard(), 1, 0.016)
        t_s = DummyTask("ts", NodeStatus.SUCCESS)
        inv = InverterDecorator("inv", t_s)
        assert inv.tick(ctx) == NodeStatus.FAILURE

        # Condition Gate
        ctx.blackboard.set("can_move", False)
        gate = ConditionGateDecorator("gate", t_s, predicate=lambda bb: bb.get("can_move") is True)
        assert gate.tick(ctx) == NodeStatus.FAILURE

        ctx.blackboard.set("can_move", True)
        assert gate.tick(ctx) == NodeStatus.SUCCESS

    def test_behavior_tree_cycle_detection(self):
        t1 = DummyTask("loop_node", NodeStatus.SUCCESS)
        seq = SequenceNode("seq", [t1])
        # Force a cycle
        t1_as_composite = SequenceNode("loop_node", [seq])
        with pytest.raises(BehaviorTreeInvalid):
            BehaviorTree(t1_as_composite)


# ==============================================================================
# 9. TARGET SELECTION & TEAMS
# ==============================================================================

class TestTargetingAndTeams:
    def test_team_relations(self):
        tp = TeamRelationProvider()
        assert tp.get_relation("Player", "Player") == TeamRelation.FRIENDLY
        assert tp.get_relation("Player", "Enemy") == TeamRelation.HOSTILE
        assert tp.get_relation("Player", "Neutral") == TeamRelation.NEUTRAL

    def test_target_scoring_utility(self):
        obs_pos = (0.0, 0.0, 0.0)
        # Target 1: close (5m), visible
        s1 = TargetSelector.calculate_score(obs_pos, (5.0, 0.0, 0.0), threat_level=2.0, is_visible=True)
        # Target 2: far (40m), not visible
        s2 = TargetSelector.calculate_score(obs_pos, (40.0, 0.0, 0.0), threat_level=1.0, is_visible=False)

        best = TargetSelector.select_best_target([("T2", s2), ("T1", s1)])
        assert best == "T1"


# ==============================================================================
# 10. DETERMINISTIC RNG, SNAPSHOTS & REPLAY
# ==============================================================================

class TestDeterminismAndSnapshots:
    def test_deterministic_rng_reproducibility(self):
        rng1 = DeterministicRNG(1337, "agent_1", tick=42)
        rng2 = DeterministicRNG(1337, "agent_1", tick=42)

        vals1 = [rng1.next_float() for _ in range(5)]
        vals2 = [rng2.next_float() for _ in range(5)]
        assert vals1 == vals2

    def test_snapshot_and_state_hash(self):
        fab = UniversalRuntimeAIFabricator(world_seed=999)
        agent = AIAgent(agent_id="A1", entity_id="E1", position=(10.0, 0.0, 10.0))
        fab.register_agent(agent)
        fab.start()
        fab.update(0.016)

        snap1 = fab.take_snapshot()
        snap2 = fab.take_snapshot()
        assert snap1.state_hash == snap2.state_hash
        assert len(snap1.state_hash) == 64

    def test_checkpoint_restore(self):
        fab = UniversalRuntimeAIFabricator(world_seed=123)
        agent = AIAgent(agent_id="A1", entity_id="E1", position=(10.0, 0.0, 10.0))
        fab.register_agent(agent)
        fab.start()
        fab.update(0.016)

        snap = fab.take_snapshot()

        # Mutate world
        agent.position = (500.0, 0.0, 500.0)
        assert fab.get_agent("A1").position == (500.0, 0.0, 500.0)

        # Restore
        fab.restore_snapshot(snap)
        assert fab.get_agent("A1").position == (10.0, 0.0, 10.0)


# ==============================================================================
# 11. NUMERIC INVARIANCE & SAFE RECOVERY
# ==============================================================================

class TestNumericInvarianceAndRecovery:
    def test_nan_coord_raises_ai_numeric_error(self):
        with pytest.raises(AINumericStateError):
            ensure_finite_vec3((float("nan"), 0.0, 0.0), "test")

    def test_infinity_coord_raises_ai_numeric_error(self):
        with pytest.raises(AINumericStateError):
            ensure_finite_vec3((0.0, float("inf"), 0.0), "test")

    def test_agent_safe_idle_recovery(self):
        fab = UniversalRuntimeAIFabricator()
        agent = AIAgent(agent_id="A1", entity_id="E1", position=(0.0, 0.0, 0.0), velocity=(5.0, 0.0, 0.0))
        fab.register_agent(agent)
        fab.recover_agent("A1")

        assert agent.velocity == (0.0, 0.0, 0.0)
        assert agent.preferred_velocity == (0.0, 0.0, 0.0)


# ==============================================================================
# 12. SPATIAL STREAMING INTEGRATION (UAF-81.81)
# ==============================================================================

class TestStreamingIntegration:
    def test_unloaded_tile_returns_navigation_unavailable(self):
        world = NavigationWorld()
        tile = NavTile(tile_x=0, tile_y=0, bounds=((0.0, 0.0, 0.0), (50.0, 0.0, 50.0)), is_resident=False)
        world.register_tile(tile)

        res = world.find_path((5.0, 0.0, 5.0), (25.0, 0.0, 25.0))
        assert res.status == PathStatus.NAVIGATION_UNAVAILABLE

    def test_resident_tile_allows_navigation(self):
        world = NavigationWorld()
        # Add polygon and tile
        p1 = make_square_polygon(1, 0.0, 0.0, 20.0)
        world.nav_mesh.add_polygon(p1)
        world.nav_mesh.build_adjacency()

        tile = NavTile(tile_x=0, tile_y=0, bounds=((0.0, 0.0, 0.0), (20.0, 0.0, 20.0)), is_resident=True)
        tile.add_polygon(1)
        world.register_tile(tile)

        res = world.find_path((2.0, 0.0, 2.0), (18.0, 0.0, 18.0))
        assert res.status == PathStatus.SUCCESS


# ==============================================================================
# 13. BUDGET & SCHEDULING FAIRNESS
# ==============================================================================

class TestBudgetAndScheduling:
    def test_path_budget_deferral(self):
        fab = UniversalRuntimeAIFabricator(budget=AIBudget(max_path_requests_per_tick=2))
        mesh = make_linear_test_mesh(num_polys=4)
        fab.navigation_world.nav_mesh = mesh
        fab.start()

        # Enqueue 4 path requests
        for i in range(4):
            a = AIAgent(agent_id=f"A{i}", entity_id=f"E{i}", position=(5.0, 0.0, 5.0))
            fab.register_agent(a)
            fab.request_path(f"A{i}", (35.0, 0.0, 5.0))

        metrics = fab.update(0.016)
        assert metrics.successful_paths == 2
        assert metrics.deferred_path_requests >= 1


# ==============================================================================
# 14. VALIDATOR & UE5 PACKAGER
# ==============================================================================

class TestValidatorAndPackager:
    def test_validator_detects_bad_mesh(self):
        mesh = NavMesh()
        # Orphan neighbor reference
        p = NavPolygon(1, ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 0.0, 10.0)), neighbors=(999,))
        mesh.add_polygon(p, validate=False)

        issues = UniversalRuntimeAIValidator.validate_nav_mesh(mesh)
        assert any(i.code == "AI_ORPHAN_NEIGHBOR_REF" for i in issues)

    def test_packager_manifest_creation(self):
        fab = UniversalRuntimeAIFabricator()
        mesh = make_linear_test_mesh(num_polys=2)
        fab.navigation_world.nav_mesh = mesh
        a = AIAgent(agent_id="Hero", entity_id="E_Hero", position=(1.0, 0.0, 1.0))
        fab.register_agent(a)

        pkg = UniversalRuntimeAIPackager.package_ai_world(fab)
        assert "package_hash" in pkg
        assert "ue5_ai_manifest" in pkg
        ue5 = pkg["ue5_ai_manifest"]
        assert ue5["UE5_NavMesh"]["PolygonCount"] == 2
        assert len(ue5["UE5_Agents"]) == 1


# ==============================================================================
# 15. GOLDEN SCENARIO: HEADLESS WORLD SIMULATION
# ==============================================================================

class TestGoldenScenarioEndToEnd:
    def test_golden_simulation_run(self):
        """
        Headless end-to-end scenario:
        1 Player + 10 Enemies + 100 Civil agents navigating, perceiving, avoiding with ORCA,
        engaging in combat, receiving damage, and updating reproducible state hashes.
        """
        fab = UniversalRuntimeAIFabricator(world_seed=2026)
        mesh = make_linear_test_mesh(num_polys=10, poly_size=20.0)
        fab.navigation_world.nav_mesh = mesh
        fab.start()

        # 1. Player
        player = AIAgent(agent_id="player", entity_id="P1", position=(10.0, 0.0, 10.0), team_id="Player")
        fab.register_agent(player)

        # 2. 10 Enemies with attack BehaviorTree
        for i in range(10):
            enemy = AIAgent(
                agent_id=f"enemy_{i}",
                entity_id=f"E_{i}",
                position=(15.0 + i * 2.0, 0.0, 10.0),
                team_id="Enemy",
                lod=AILOD.LOD0_FULL,
            )
            enemy.blackboard.set("current_target_id", "player")
            # BT: Sequence(AttackTargetTask)
            attack_task = AttackTargetTask(f"atk_{i}", attack_range=10.0, cooldown_ticks=1, damage_amount=5.0)
            enemy.behavior_tree = BehaviorTree(SequenceNode(f"seq_atk_{i}", [attack_task]))
            fab.register_agent(enemy)

        # 3. 100 Civil agents with LOD2/LOD3
        for i in range(100):
            civil = AIAgent(
                agent_id=f"civil_{i}",
                entity_id=f"C_{i}",
                position=(20.0 + (i % 20) * 5.0, 0.0, 5.0 + (i // 20) * 2.0),
                team_id="Neutral",
                lod=AILOD.LOD2_SIMPLIFIED_DECISION if i < 50 else AILOD.LOD3_STATISTICAL,
            )
            civil.preferred_velocity = (1.0, 0.0, 0.0)
            fab.register_agent(civil)

        # Simulate 10 ticks
        for _ in range(10):
            fab.update(0.05)

        # Check that combat occurred and damage was recorded
        assert player.blackboard.get("damage_received", 0.0) > 0.0
        assert fab.metrics.avoidance_pairs_evaluated > 0

        # Verify state hash determinism
        snap_a = fab.take_snapshot()
        snap_b = fab.take_snapshot()
        assert snap_a.state_hash == snap_b.state_hash
        assert len(snap_a.state_hash) == 64
