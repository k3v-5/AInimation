"""
UAF-81.82: Universal Runtime AI Fabricator and Central Orchestrator.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

from ..avoidance.orca import ORCASolver
from ..behavior.node import BTContext
from ..behavior.tree import BehaviorTree
from ..models.definition import (
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
    DamageStimulus,
    DeterministicRNG,
    NavigationProfile,
    PathRequest,
    PathResult,
    PathStatus,
    SensoryMemoryEntry,
    SoundStimulus,
    Vec3,
    ensure_finite_vec3,
    vec3_add,
    vec3_distance,
    vec3_scale,
)
from .agent import AIAgent
from .budget import AIBudgetManager
from .navigation_world import NavigationWorld
from .targeting import TargetSelector, TeamRelationProvider
from ..navigation.path import PathRequestQueue


class UniversalRuntimeAIFabricator:
    """
    Authoritative simulation orchestrator for runtime AI, navigation, dynamic avoidance,
    and behavior trees. Purely headless, deterministic, and project-agnostic.
    """

    def __init__(
        self,
        world_seed: int = 1337,
        navigation_world: Optional[NavigationWorld] = None,
        budget: Optional[AIBudget] = None,
    ):
        self.world_seed = world_seed
        self.state = AIRuntimeWorldState.CREATED
        self.current_tick: int = 0
        self.simulation_time: float = 0.0
        self.world_revision: int = 0

        self.navigation_world = navigation_world or NavigationWorld()
        self.budget_manager = AIBudgetManager(budget or AIBudget())
        self.team_relations = TeamRelationProvider()
        self.path_queue = PathRequestQueue()
        self.metrics = AIMetrics()

        self.agents: Dict[str, AIAgent] = {}
        self._next_request_id: int = 1

    # --------------------------------------------------------------------------
    # 1. LIFECYCLE MANAGEMENT
    # --------------------------------------------------------------------------

    def start(self) -> bool:
        if self.state in (AIRuntimeWorldState.CREATED, AIRuntimeWorldState.STOPPED):
            self.state = AIRuntimeWorldState.RUNNING
            return True
        return False

    def pause(self) -> bool:
        if self.state == AIRuntimeWorldState.RUNNING:
            self.state = AIRuntimeWorldState.PAUSED
            return True
        return False

    def resume(self) -> bool:
        if self.state == AIRuntimeWorldState.PAUSED:
            self.state = AIRuntimeWorldState.RUNNING
            return True
        return False

    def stop(self) -> bool:
        if self.state in (AIRuntimeWorldState.RUNNING, AIRuntimeWorldState.PAUSED):
            self.state = AIRuntimeWorldState.STOPPED
            return True
        return False

    def destroy(self) -> bool:
        self.state = AIRuntimeWorldState.DESTROYED
        self.agents.clear()
        return True

    # --------------------------------------------------------------------------
    # 2. AGENT REGISTRATION
    # --------------------------------------------------------------------------

    def register_agent(self, agent: AIAgent) -> None:
        self.agents[agent.agent_id] = agent
        self.world_revision += 1

    def unregister_agent(self, agent_id: str) -> Optional[AIAgent]:
        agent = self.agents.pop(agent_id, None)
        if agent:
            self.world_revision += 1
        return agent

    def get_agent(self, agent_id: str) -> Optional[AIAgent]:
        return self.agents.get(agent_id)

    def recover_agent(self, agent_id: str) -> None:
        """Safe recovery handler: resets agent into SafeIdleState."""
        agent = self.get_agent(agent_id)
        if agent is not None:
            agent.velocity = (0.0, 0.0, 0.0)
            agent.preferred_velocity = (0.0, 0.0, 0.0)
            agent.clear_path()
            agent.current_target_id = None
            if agent.behavior_tree is not None:
                agent.behavior_tree.reset()

    # --------------------------------------------------------------------------
    # 3. SENSORY STIMULI DISPATCH
    # --------------------------------------------------------------------------

    def emit_sound(self, sound: SoundStimulus) -> int:
        """Deliver sound stimulus to all agents capable of perceiving it."""
        heard_count = 0
        for aid in sorted(self.agents.keys()):
            agent = self.agents[aid]
            if not agent.enabled or agent.lod == AILOD.LOD4_DORMANT:
                continue

            perceived_intensity = agent.hearing_sensor.perceive_sound(agent.position, sound)
            if perceived_intensity is not None:
                agent.sensory_memory.record_stimulus(
                    stimulus_id=f"snd_{sound.source_id}_{self.current_tick}",
                    source_id=sound.source_id,
                    stimulus_type="SOUND",
                    position=sound.position,
                    strength=perceived_intensity,
                    current_tick=self.current_tick,
                    initial_confidence=1.0,
                )
                heard_count += 1
        return heard_count

    def apply_agent_damage(self, source_id: str, target_id: str, amount: float, tick: int) -> bool:
        """Apply combat damage stimulus to target agent."""
        target = self.get_agent(target_id)
        if target is None or not target.enabled:
            return False

        source = self.get_agent(source_id)
        source_pos = source.position if source else (0.0, 0.0, 0.0)

        damage_stim = DamageStimulus(
            source_id=source_id,
            target_id=target_id,
            amount=amount,
            position=source_pos,
            tick=tick,
        )

        if target.damage_sensor.process_damage(target_id, damage_stim):
            target.sensory_memory.record_stimulus(
                stimulus_id=f"dmg_{source_id}_{tick}",
                source_id=source_id,
                stimulus_type="DAMAGE",
                position=source_pos,
                strength=amount,
                current_tick=tick,
                initial_confidence=1.0,
            )
            # Record damage received in blackboard
            curr_dmg = target.blackboard.get("damage_received", 0.0)
            target.blackboard.set("damage_received", curr_dmg + amount)
            target.blackboard.set("last_attacker_id", source_id)
            return True

        return False

    # --------------------------------------------------------------------------
    # 4. PATH REQUESTS
    # --------------------------------------------------------------------------

    def request_path(
        self,
        agent_id: str,
        goal: Vec3,
        priority: AIPriority = AIPriority.NORMAL,
        profile_id: Optional[str] = None,
    ) -> int:
        """Queue a path request."""
        agent = self.get_agent(agent_id)
        if agent is None:
            return -1

        req_id = self._next_request_id
        self._next_request_id += 1

        prof = profile_id or agent.navigation_profile
        req = PathRequest(
            request_id=req_id,
            agent_id=agent_id,
            start=agent.position,
            goal=goal,
            profile_id=prof,
            priority=priority,
            requested_tick=self.current_tick,
        )
        self.path_queue.push(req)
        self.metrics.total_path_requests += 1
        return req_id

    # --------------------------------------------------------------------------
    # 5. SIMULATION TICK
    # --------------------------------------------------------------------------

    def update(self, delta_time: float = 1.0 / 60.0) -> AIMetrics:
        """
        Execute deterministic AI simulation tick across perception, pathfinding,
        decision trees, local avoidance, and kinematics.
        """
        if self.state != AIRuntimeWorldState.RUNNING:
            return self.metrics

        self.current_tick += 1
        self.simulation_time += delta_time
        self.budget_manager.reset_tick()

        # Step 1: Invariant numeric sanity check across all agents
        for aid in sorted(self.agents.keys()):
            agent = self.agents[aid]
            try:
                ensure_finite_vec3(agent.position, f"agent({aid}).position")
                ensure_finite_vec3(agent.velocity, f"agent({aid}).velocity")
            except AINumericStateError:
                self.recover_agent(aid)
                raise

        # Step 2: Decay sensory memory across all enabled agents
        for aid in sorted(self.agents.keys()):
            agent = self.agents[aid]
            if agent.enabled and agent.lod != AILOD.LOD4_DORMANT:
                agent.sensory_memory.update_decay(self.current_tick)

        # Step 3: Process queued path requests up to budget
        while not self.path_queue.is_empty():
            req = self.path_queue.pop()
            if req is None:
                break

            if not self.budget_manager.can_process_path(req.agent_id):
                # Budget exceeded: re-enqueue with fairness tracking
                self.path_queue.push(req)
                self.metrics.deferred_path_requests += 1
                break

            self.budget_manager.consume_path(req.agent_id)
            agent = self.get_agent(req.agent_id)
            if agent is not None and agent.enabled:
                prof = NavigationProfile(profile_id=req.profile_id)
                res = self.navigation_world.find_path(req.start, req.goal, prof, req.request_id)
                if res.status == PathStatus.SUCCESS:
                    agent.set_path(res.points)
                    self.metrics.successful_paths += 1
                else:
                    self.metrics.failed_paths += 1

        # Step 4: Evaluate Behavior Trees according to AI LOD
        lod_counts: Dict[int, int] = {}
        for aid in sorted(self.agents.keys()):
            agent = self.agents[aid]
            if not agent.enabled:
                continue

            lod_counts[agent.lod.value] = lod_counts.get(agent.lod.value, 0) + 1

            if agent.lod == AILOD.LOD4_DORMANT:
                continue

            # LOD evaluation frequency:
            # LOD0: every tick (mod 1 == 0)
            # LOD1: every 2 ticks (tick % 2 == 0)
            # LOD2: every 4 ticks (tick % 4 == 0)
            # LOD3: every 8 ticks (tick % 8 == 0)
            lod_interval = 2 ** agent.lod.value
            if self.current_tick % lod_interval == 0:
                if agent.behavior_tree is not None:
                    ctx = BTContext(
                        agent_id=aid,
                        blackboard=agent.blackboard,
                        tick=self.current_tick,
                        delta_time=delta_time,
                        fabricator=self,
                    )
                    agent.behavior_tree.tick(ctx)
                    self.metrics.total_bt_nodes_executed += 1

            # Follow active path waypoints if present
            agent.follow_active_path()

        self.metrics.agents_by_lod = lod_counts

        # Step 5: Local Avoidance (ORCA)
        # Collect kinematics for all enabled, active agents
        active_agents = [
            agent for agent in (self.agents[aid] for aid in sorted(self.agents.keys()))
            if agent.enabled and agent.lod != AILOD.LOD4_DORMANT
        ]

        for agent in active_agents:
            if not self.budget_manager.can_process_avoidance():
                break

            # Find neighbors within 6 meters
            neighbors = []
            for other in active_agents:
                if other.agent_id == agent.agent_id:
                    continue
                dist = vec3_distance(agent.position, other.position)
                if dist <= 6.0:
                    neighbors.append((other.agent_id, other.to_kinematics()))

            if neighbors:
                self.budget_manager.consume_avoidance()
                self.metrics.avoidance_pairs_evaluated += len(neighbors)
                safe_vel = ORCASolver.solve_avoidance(agent.to_kinematics(), neighbors, time_step=delta_time)
                agent.velocity = safe_vel
            else:
                agent.velocity = agent.preferred_velocity

        # Step 6: Kinematic Integration
        for agent in active_agents:
            # Integrate position
            new_pos = vec3_add(agent.position, vec3_scale(agent.velocity, delta_time))
            agent.position = ensure_finite_vec3(new_pos, f"integrate({agent.agent_id})")

        return self.metrics

    # --------------------------------------------------------------------------
    # 6. SNAPSHOTS, CHECKPOINTS & REPLAY
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> AISnapshot:
        """Capture immutable, bit-exact snapshot with canonical SHA-256 state_hash."""
        agent_snaps: Dict[str, AIAgentSnapshot] = {}

        for aid in sorted(self.agents.keys()):
            a = self.agents[aid]
            # Capture deterministic RNG state
            rng = DeterministicRNG(self.world_seed, aid, self.current_tick)
            rng_state = rng.next_u32()

            agent_snaps[aid] = AIAgentSnapshot(
                agent_id=a.agent_id,
                entity_id=a.entity_id,
                lod=a.lod.value,
                position=a.position,
                velocity=a.velocity,
                current_target_id=a.current_target_id,
                blackboard_data=a.blackboard.snapshot(),
                memory_entries={
                    k: {
                        "stimulus_id": e.stimulus_id,
                        "source_id": e.source_id,
                        "type": e.stimulus_type,
                        "position": e.position,
                        "strength": e.strength,
                        "confidence": e.confidence,
                    }
                    for k, e in sorted(a.sensory_memory.entries.items())
                },
                path_points=a.current_path_points,
                bt_status=a.behavior_tree.root.status.value if a.behavior_tree else "NONE",
                rng_state=rng_state,
            )

        return AISnapshot.create(
            tick=self.current_tick,
            world_revision=self.world_revision,
            agents=agent_snaps,
        )

    def restore_snapshot(self, snapshot: AISnapshot) -> None:
        """Restore world state precisely to snapshot."""
        self.current_tick = snapshot.tick
        self.world_revision = snapshot.world_revision

        for aid, s in snapshot.agents.items():
            agent = self.get_agent(aid)
            if agent is None:
                agent = AIAgent(
                    agent_id=s.agent_id,
                    entity_id=s.entity_id,
                    position=s.position,
                    velocity=s.velocity,
                    lod=AILOD(s.lod),
                )
                self.register_agent(agent)

            agent.position = s.position
            agent.velocity = s.velocity
            agent.lod = AILOD(s.lod)
            agent.current_target_id = s.current_target_id
            agent.blackboard.restore(s.blackboard_data)
            agent.current_path_points = s.path_points
            agent.current_waypoint_index = 0
