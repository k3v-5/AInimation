"""
UAF-81.92: Advanced Multi-Agent NPC Ecosystem, Cognitive GOAP, Squad Tactics & Faction Reputation
Acceptance Test Suite.
Verifies WorldState belief modeling, A* state-space GOAP planning, dynamic replanning,
squad bounding overwatch, >= 60 deg flanking geometry, perception cones, memory decay,
faction alliance ripple cascades, and Unreal Engine 5 StateTree export.
"""

import json
import math
import pytest
from pathlib import Path

from uaf.ai import (
    FactionId,
    DispositionType,
    TacticalRole,
    StimulusType,
    PerceptionStimulus,
    WorldState,
    GOAPAction,
    GOAPGoal,
    GOAPPlan,
    GOAPPlanner,
    SquadMember,
    SquadBlackboard,
    Squad,
    TrackedThreat,
    PerceptionSensor,
    FactionReputationMatrix,
    StateTreeTaskSchema,
    StateTreeNodeSchema,
    UE5StateTreeManifest,
    UE5AIExporter,
)


class TestWorldStateAndContracts:
    """Test suite for belief state representation and atomic condition evaluation."""

    def test_world_state_satisfaction_and_effects(self):
        ws = WorldState(values={"armed": True, "in_cover": False, "ammo_count": 30})
        assert ws.satisfies({"armed": True, "in_cover": False}) is True
        assert ws.satisfies({"armed": True, "in_cover": True}) is False

        # Apply effect
        new_ws = ws.apply_effects({"in_cover": True, "ammo_count": 25})
        assert new_ws.get("in_cover") is True
        assert new_ws.get("ammo_count") == 25
        assert ws.get("in_cover") is False  # Original state unchanged (immutability)

    def test_world_state_heuristic_distance(self):
        ws = WorldState(values={"a": 1, "b": 2, "c": 3})
        # Needs b=5, c=3, d=4 -> 2 mismatches (b and d)
        h = ws.heuristic_distance({"b": 5, "c": 3, "d": 4})
        assert h == 2


class TestGOAPStateSpacePlanner:
    """Test suite for GOAP A* state-space search and dynamic replanning."""

    def test_goap_optimal_plan_generation(self):
        actions = [
            GOAPAction(action_id="a_move_cover", name="Move to Cover", preconditions={"in_danger": True}, effects={"in_cover": True}, cost=1.5),
            GOAPAction(action_id="a_reload", name="Reload Weapon", preconditions={"in_cover": True}, effects={"has_ammo": True}, cost=1.0),
            GOAPAction(action_id="a_aim", name="Aim at Target", preconditions={"has_ammo": True}, effects={"target_locked": True}, cost=0.5),
            GOAPAction(action_id="a_shoot", name="Neutralize Target", preconditions={"target_locked": True}, effects={"target_neutralized": True}, cost=2.0),
        ]

        planner = GOAPPlanner(actions)
        start_state = WorldState(values={"in_danger": True, "in_cover": False, "has_ammo": False, "target_locked": False, "target_neutralized": False})
        goal = GOAPGoal(goal_id="g_defeat", name="Defeat Enemy", target_state={"target_neutralized": True})

        plan = planner.plan(start_state, goal)
        assert plan is not None
        assert plan.is_complete is False
        assert [a.action_id for a in plan.actions] == ["a_move_cover", "a_reload", "a_aim", "a_shoot"]
        assert math.isclose(plan.total_cost, 5.0, abs_tol=1e-3)

    def test_goap_impossible_goal_returns_none(self):
        # Goal requires keycard, but no action provides it
        actions = [
            GOAPAction(action_id="a_kick", name="Kick Door", preconditions={}, effects={"door_dented": True}, cost=1.0)
        ]
        planner = GOAPPlanner(actions)
        start = WorldState(values={"door_open": False})
        goal = GOAPGoal(goal_id="g_open", name="Open Security Gate", target_state={"door_open": True})

        plan = planner.plan(start, goal)
        assert plan is None

    def test_goap_plan_step_and_precondition_invalidation(self):
        a1 = GOAPAction(action_id="a1", name="Step 1", preconditions={"step0": True}, effects={"step1": True})
        a2 = GOAPAction(action_id="a2", name="Step 2", preconditions={"step1": True, "safe": True}, effects={"done": True})

        plan = GOAPPlan(goal_id="g", actions=[a1, a2], total_cost=2.0)
        curr_state = WorldState(values={"step0": True, "safe": True})

        # Step 1 is valid
        assert plan.validate_step(curr_state) is True
        curr_state = curr_state.apply_effects(a1.effects)
        plan.advance()

        # Step 2 is valid when safe=True
        assert plan.validate_step(curr_state) is True

        # Sudden combat event: safe becomes False
        curr_state.set("safe", False)
        assert plan.validate_step(curr_state) is False  # Precondition broken!


class TestMultiAgentSquadTactics:
    """Test suite for squad coordination, bounding overwatch, and flanking geometry."""

    def test_bounding_overwatch_leapfrog(self):
        squad = Squad(squad_id="Squad_Alpha", leader_id="m1")
        m1 = SquadMember(agent_id="m1", role=TacticalRole.POINTMAN, world_pos=(0.0, 0.0, 0.0))
        m2 = SquadMember(agent_id="m2", role=TacticalRole.SUPPRESSOR, world_pos=(-200.0, 0.0, 0.0))
        squad.add_member(m1)
        squad.add_member(m2)

        orders = squad.execute_bounding_overwatch(advance_target_pos=(1200.0, 0.0, 0.0))
        assert m2.is_suppressing is True
        assert m2.is_moving is False
        assert m1.is_moving is True
        assert squad.blackboard.is_threat_suppressed is True
        assert "PROVIDE_COVERING_FIRE" in orders.values()

    def test_flanking_angular_separation_geometry(self):
        squad = Squad(squad_id="Squad_Flank", leader_id="f1")
        flanker = SquadMember(agent_id="f1", role=TacticalRole.FLANKER, world_pos=(0.0, 0.0, 0.0))
        squad.add_member(flanker)

        # Threat is at (1000, 0, 0) facing directly towards squad (-X, 180 deg)
        squad.blackboard.threat_world_pos = (1000.0, 0.0, 0.0)
        squad.blackboard.threat_forward_vector = (-1.0, 0.0, 0.0)

        candidates = [
            (500.0, 0.0, 0.0),    # Direct head-on approach: angle = 0 deg relative to facing -> INVALID
            (1000.0, 600.0, 0.0), # Perpendicular flank: angle = 90 deg relative to facing -> VALID
            (1500.0, 200.0, 0.0), # Behind threat: angle = 160 deg relative to facing -> VALID
        ]

        chosen_flank = squad.select_flanking_position(candidates, min_angle_deg=60.0)
        assert chosen_flank == (1000.0, 600.0, 0.0)
        assert squad.blackboard.assigned_flank_pos == (1000.0, 600.0, 0.0)

    def test_coordinated_room_breach(self):
        squad = Squad(squad_id="Squad_Breach", leader_id="p1")
        squad.add_member(SquadMember(agent_id="p1", role=TacticalRole.POINTMAN, world_pos=(0.0, 0.0, 0.0)))
        squad.add_member(SquadMember(agent_id="f1", role=TacticalRole.FLANKER, world_pos=(0.0, -100.0, 0.0)))
        squad.add_member(SquadMember(agent_id="s1", role=TacticalRole.SUPPRESSOR, world_pos=(-100.0, 0.0, 0.0)))

        orders = squad.coordinate_breach(door_location=(500.0, 0.0, 0.0))
        assert orders["p1"] == "BREACH_DOOR"
        assert orders["f1"] == "CLEAR_CORNER_LEFT"
        assert orders["s1"] == "COVER_HALLWAY_CENTER"
        assert squad.blackboard.active_maneuver == "ROOM_BREACH"


class TestSensoryPerceptionAndMemory:
    """Test suite for vision cones, acoustic hearing, and exponential memory decay."""

    def test_vision_cone_and_occlusion(self):
        sensor = PerceptionSensor(sight_range_cm=2000.0, fov_angle_deg=90.0)
        agent_pos = (0.0, 0.0, 0.0)
        agent_fwd = (1.0, 0.0, 0.0)  # Facing +X

        # Target directly in front (dist=1000, angle=0) -> Visible
        assert sensor.can_see(agent_pos, agent_fwd, (1000.0, 0.0, 0.0), is_occluded=False) is True

        # Target occluded by wall -> Not visible
        assert sensor.can_see(agent_pos, agent_fwd, (1000.0, 0.0, 0.0), is_occluded=True) is False

        # Target outside FOV (angle = 60 deg > 45 deg half-angle) -> Not visible
        assert sensor.can_see(agent_pos, agent_fwd, (500.0, 1000.0, 0.0)) is False

        # Target beyond sight range (dist=2500 > 2000) -> Not visible
        assert sensor.can_see(agent_pos, agent_fwd, (2500.0, 0.0, 0.0)) is False

    def test_acoustic_hearing_range(self):
        sensor = PerceptionSensor(hearing_range_cm=3000.0)
        agent_pos = (0.0, 0.0, 0.0)

        # Normal gunshot within range
        assert sensor.can_hear(agent_pos, (1500.0, 1500.0, 0.0), sound_intensity=1.0) is True
        # Distant sound beyond range
        assert sensor.can_hear(agent_pos, (4000.0, 0.0, 0.0), sound_intensity=1.0) is False

    def test_threat_memory_exponential_decay(self):
        sensor = PerceptionSensor(memory_decay_rate=0.25, lost_threshold=0.20)
        stim = PerceptionStimulus(
            stimulus_id="stim_01",
            stimulus_type=StimulusType.SOUND,
            source_pos=(800.0, 0.0, 0.0),
        )

        sensor.process_stimulus("threat_01", stim, current_time=0.0)
        # Mark as not visible to start decay
        sensor.memory["threat_01"].is_currently_visible = False

        # Decay after 2 seconds: C = 1.0 * exp(-0.25 * 2) = exp(-0.5) ~= 0.606
        sensor.update_memory(delta_time_sec=2.0)
        conf = sensor.memory["threat_01"].confidence
        assert math.isclose(conf, math.exp(-0.5), abs_tol=1e-3)

        # Decay after additional 6 seconds: total 8s -> C = exp(-2.0) ~= 0.135 < lost_threshold (0.20)
        active = sensor.update_memory(delta_time_sec=6.0)
        assert len(active) == 0
        assert "threat_01" not in sensor.memory


class TestFactionReputationMatrix:
    """Test suite for diplomatic dispositions and alliance ripple cascades."""

    def test_faction_matrix_defaults_and_classifications(self):
        matrix = FactionReputationMatrix.create_default_matrix()

        # Self-disposition is 100
        assert matrix.get_disposition(FactionId.PLAYER, FactionId.PLAYER) == 100.0
        # Feral Xenos are hostile
        assert matrix.get_relationship_type(FactionId.PLAYER, FactionId.FERAL_XENOS) == DispositionType.HOSTILE
        # Military Syndicate and Colonial Security are allied
        assert matrix.get_relationship_type(FactionId.MILITARY_SYNDICATE, FactionId.COLONIAL_SECURITY) == DispositionType.ALLIED

    def test_alliance_ripple_cascade(self):
        matrix = FactionReputationMatrix.create_default_matrix()
        # Initial Syndicate vs Player is 0.0 (Neutral)
        assert matrix.get_disposition(FactionId.MILITARY_SYNDICATE, FactionId.PLAYER) == 0.0

        # Player attacks Colonial Security (delta = -60.0)
        # Syndicate is allied with Colonial Security (strength = 65.0)
        # Ripple delta = -60.0 * 0.65 = -39.0
        matrix.modify_disposition(actor_faction=FactionId.PLAYER, target_faction=FactionId.COLONIAL_SECURITY, delta=-60.0)

        syndicate_score = matrix.get_disposition(FactionId.MILITARY_SYNDICATE, FactionId.PLAYER)
        assert syndicate_score == -39.0
        assert matrix.get_relationship_type(FactionId.MILITARY_SYNDICATE, FactionId.PLAYER) == DispositionType.HOSTILE


class TestUE5AIExporter:
    """Test suite for Unreal Engine 5 StateTree and AI manifest serialization."""

    def test_ue5_statetree_export_pipeline(self, tmp_path: Path):
        actions = [
            GOAPAction(action_id="a_cover", name="Take Cover", cost=1.0),
            GOAPAction(action_id="a_shoot", name="Fire Weapon", cost=2.0),
        ]
        squad = Squad(squad_id="S_Bravo", leader_id="b1")
        squad.add_member(SquadMember(agent_id="b1", role=TacticalRole.POINTMAN, world_pos=(100.0, 200.0, 0.0)))

        exporter = UE5AIExporter(asset_name="ST_TacticalAgent")
        manifest = exporter.build_statetree_manifest(actions=actions, squads=[squad])

        assert manifest.asset_name == "ST_TacticalAgent"
        assert len(manifest.states) == 5
        assert "ThreatActor" in manifest.blackboard_keys
        assert len(manifest.actions) == 2
        assert len(manifest.squads) == 1

        # Export JSON
        out_json = tmp_path / "ST_TacticalAgent_manifest.json"
        exporter.export_to_json(manifest, out_json)
        assert out_json.exists()

        # Ingestion script
        script_content = exporter.generate_unreal_python_script(str(out_json))
        assert "Autonomous Unreal Engine 5 StateTree & Cognitive AI Ingestion Script" in script_content
        assert "ST_TacticalAgent" in script_content

    def test_end_to_end_cognitive_ecosystem_pipeline(self, tmp_path: Path):
        """
        Complete end-to-end integration test:
        1. Setup multi-agent squad
        2. Perceive threat via visual cone
        3. Formulate GOAP combat plan
        4. Execute bounding overwatch maneuver
        5. Verify threat memory decay
        6. Apply faction reputation update
        7. Export StateTree & AI bundle to disk.
        """
        # 1. Squad
        squad = Squad(squad_id="E2E_Squad", leader_id="alpha_1")
        p1 = SquadMember(agent_id="alpha_1", role=TacticalRole.POINTMAN, world_pos=(0.0, 0.0, 0.0))
        s1 = SquadMember(agent_id="alpha_2", role=TacticalRole.SUPPRESSOR, world_pos=(-300.0, 0.0, 0.0))
        f1 = SquadMember(agent_id="alpha_3", role=TacticalRole.FLANKER, world_pos=(-150.0, -150.0, 0.0))
        squad.add_member(p1)
        squad.add_member(s1)
        squad.add_member(f1)

        # 2. Perception
        sensor = PerceptionSensor(sight_range_cm=3000.0, fov_angle_deg=110.0)
        threat_pos = (1500.0, 0.0, 0.0)
        assert sensor.can_see(p1.world_pos, (1.0, 0.0, 0.0), threat_pos) is True

        stim = PerceptionStimulus(stimulus_id="vis_1", stimulus_type=StimulusType.VISION, source_pos=threat_pos)
        sensor.process_stimulus("threat_raider", stim, current_time=0.0)

        # 3. GOAP Plan
        actions = [
            GOAPAction(action_id="act_suppress", name="Suppress Threat", preconditions={"threat_spotted": True}, effects={"threat_pinned": True}, cost=1.0),
            GOAPAction(action_id="act_flank", name="Flank Position", preconditions={"threat_pinned": True}, effects={"threat_flanked": True}, cost=2.0),
            GOAPAction(action_id="act_eliminate", name="Eliminate Threat", preconditions={"threat_flanked": True}, effects={"threat_eliminated": True}, cost=1.5),
        ]
        planner = GOAPPlanner(actions)
        state = WorldState(values={"threat_spotted": True, "threat_pinned": False, "threat_flanked": False, "threat_eliminated": False})
        goal = GOAPGoal(goal_id="g_neutralize", name="Neutralize Raider", target_state={"threat_eliminated": True})

        plan = planner.plan(state, goal)
        assert plan is not None
        assert len(plan.actions) == 3

        # 4. Squad Maneuver
        squad.blackboard.threat_world_pos = threat_pos
        squad.blackboard.threat_forward_vector = (-1.0, 0.0, 0.0)
        overwatch_orders = squad.execute_bounding_overwatch(advance_target_pos=(800.0, 0.0, 0.0))
        assert "alpha_1" in overwatch_orders

        flank_pos = squad.select_flanking_position([(1500.0, 800.0, 0.0), (1000.0, 0.0, 0.0)])
        assert flank_pos == (1500.0, 800.0, 0.0)

        # 5. Faction diplomacy update
        reputation = FactionReputationMatrix.create_default_matrix()
        reputation.modify_disposition(actor_faction=FactionId.PLAYER, target_faction=FactionId.RENEGADE_RAIDERS, delta=-20.0)

        # 6. UE5 Export
        exporter = UE5AIExporter(asset_name="ST_E2E_SquadAI")
        manifest = exporter.build_statetree_manifest(actions=actions, squads=[squad])
        manifest_file = tmp_path / "ST_E2E_SquadAI_manifest.json"
        exporter.export_to_json(manifest, manifest_file)

        assert manifest_file.exists()
        with open(manifest_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["asset_name"] == "ST_E2E_SquadAI"
            assert len(data["squads"]) == 1
