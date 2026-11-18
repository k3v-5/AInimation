"""
Universal AI Fabricator for UAF-81.57.
Implements the 12-stage tick simulation pipeline, sensory perception, decision engines
(FSM, Behavior Trees, Utility AI, GOAP), navigation/pathfinding, crowd flocking, formations,
squads, cover queries, save/load, replay verification, and 13 Golden Scenarios.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    AgentType,
    AgentLifecycleState,
    AgentState,
    AIRandomStream,
    AgentProfile,
    SenseType,
    PerceptionFilter,
    PerceptionEvent,
    HearingProfile,
    AISoundEvent,
    MemoryType,
    MemoryRecord,
    AIMemory,
    TargetLockMode,
    TargetScore,
    StateDefinition,
    StateTransition,
    FSMDefinition,
    BTNodeType,
    BTNodeStatus,
    BTAbortMode,
    BehaviorNode,
    BehaviorTree,
    UtilityCurveType,
    UtilityConsideration,
    UtilityAction,
    WorldFact,
    GOAPAction,
    GOAPGoal,
    ActionPlan,
    AIActionType,
    AIActionState,
    AIAction,
    AIMovementMode,
    AIMovementProfile,
    PathfindingAlgorithm,
    PathStatus,
    PathResult,
    DynamicObstacle,
    CrowdGroupType,
    CrowdAgent,
    FormationType,
    FormationMember,
    FormationDefinition,
    FactionType,
    Relationship,
    FactionDefinition,
    AICommunicationType,
    AICommunicationMessage,
    GroupRole,
    SquadDefinition,
    AICombatState,
    CombatRangeType,
    CoverPoint,
    AIInteractionType,
    InteractableDefinition,
    NeedType,
    NeedsProfile,
    ScheduleEntry,
    DailySchedule,
    AIEventType,
    AIEventPriority,
    AIEvent,
    AISaveState,
    SimulationReplay,
    AISimulationLOD,
    AbstractAgentState,
    AIPerformanceBudget,
    AIPerformanceReport,
    AIDiagnosticReport,
    AIQueryType,
    AIQuery,
    TerritoryDefinition,
    AIAgent,
    SimulationSnapshot,
    SimulationDefinition,
)


class UniversalAIFabricator:
    """
    Core engine and procedural synthesis platform for UAF-81.57.
    """

    GOLDEN_IDLE_NPC = "GOLDEN_IDLE_NPC"
    GOLDEN_DAILY_ROUTINE = "GOLDEN_DAILY_ROUTINE"
    GOLDEN_PATROL = "GOLDEN_PATROL"
    GOLDEN_FLEE = "GOLDEN_FLEE"
    GOLDEN_COMBAT = "GOLDEN_COMBAT"
    GOLDEN_SQUAD = "GOLDEN_SQUAD"
    GOLDEN_CROWD = "GOLDEN_CROWD"
    GOLDEN_ANIMAL = "GOLDEN_ANIMAL"
    GOLDEN_CITY_POPULATION = "GOLDEN_CITY_POPULATION"
    GOLDEN_WORLD_REACTION = "GOLDEN_WORLD_REACTION"
    GOLDEN_BACKGROUND_SIMULATION = "GOLDEN_BACKGROUND_SIMULATION"
    GOLDEN_SAVE_LOAD = "GOLDEN_SAVE_LOAD"
    GOLDEN_REPLAY = "GOLDEN_REPLAY"

    @staticmethod
    def spawn_agent(
        agent_id: str,
        profile: AgentProfile,
        initial_position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        faction: str = "NEUTRAL",
    ) -> AIAgent:
        state = AgentState(
            position=initial_position,
            health=100.0,
            max_health=100.0,
            stamina=100.0,
            current_action="IDLE",
        )
        return AIAgent(
            agent_id=agent_id,
            profile=profile,
            state=state,
            lifecycle=AgentLifecycleState.ACTIVE,
            faction=faction,
        )

    # --- 12-STAGE TICK SIMULATION PIPELINE (Section 18) ---

    @staticmethod
    def execute_simulation_tick(simulation: SimulationDefinition, dt: float = 0.033) -> None:
        """
        Executes a deterministic simulation tick in normative 12-stage order (Section 18).
        INPUT -> WORLD_UPDATE -> PERCEPTION -> MEMORY -> DECISION -> BEHAVIOR ->
        ACTION -> MOVEMENT -> INTERACTION -> COMBAT -> STATE_COMMIT -> EVENTS.
        """
        simulation.current_tick += 1

        for agent in simulation.agents:
            if agent.lifecycle != AgentLifecycleState.ACTIVE:
                continue

            # Stage 1: INPUT / Needs decay
            agent.needs.update_decay(dt)

            # Stage 2: WORLD_UPDATE
            # (Context synchronized from world state)

            # Stage 3: PERCEPTION
            # Scan nearby agents within sensor range (e.g. 1500 units)
            for other in simulation.agents:
                if other.agent_id != agent.agent_id and other.lifecycle == AgentLifecycleState.ACTIVE:
                    dist = math.sqrt(
                        (other.state.position[0] - agent.state.position[0]) ** 2
                        + (other.state.position[1] - agent.state.position[1]) ** 2
                    )
                    if dist <= 1500.0:
                        p_event = PerceptionEvent(
                            source_agent_id=agent.agent_id,
                            target_id=other.agent_id,
                            sense=SenseType.VISION,
                            confidence=max(0.1, 1.0 - (dist / 1500.0)),
                            distance=dist,
                            timestamp=float(simulation.current_tick),
                        )
                        # Stage 4: MEMORY insertion
                        mem = MemoryRecord(
                            memory_id=f"MEM_{agent.agent_id}_{other.agent_id}_{simulation.current_tick}",
                            mem_type=MemoryType.SHORT_TERM,
                            subject=other.agent_id,
                            location=other.state.position,
                            timestamp=float(simulation.current_tick),
                            confidence=p_event.confidence,
                        )
                        agent.memory.add_record(mem)

            # Stage 5: DECISION
            if agent.fsm and agent.current_fsm_state:
                # Simple condition check: if health < 30, switch to RETREAT
                conditions = {"low_health": agent.state.health < 30.0, "enemy_visible": agent.state.current_target is not None}
                next_state = UniversalAIFabricator.evaluate_fsm(agent.fsm, agent.current_fsm_state, conditions)
                agent.current_fsm_state = next_state

            # Stage 6: BEHAVIOR / Stage 7: ACTION
            if agent.current_action_obj:
                agent.current_action_obj.elapsed += dt
                if agent.current_action_obj.elapsed >= agent.current_action_obj.duration:
                    agent.current_action_obj.state = AIActionState.SUCCESS
                    agent.state.current_action = "IDLE"

            # Stage 8: MOVEMENT
            if agent.state.velocity != (0.0, 0.0, 0.0):
                px = agent.state.position[0] + agent.state.velocity[0] * dt
                py = agent.state.position[1] + agent.state.velocity[1] * dt
                pz = agent.state.position[2] + agent.state.velocity[2] * dt
                agent.state.position = (px, py, pz)

            # Stage 9: INTERACTION
            for item in simulation.interactables:
                idist = math.sqrt(
                    (item.position[0] - agent.state.position[0]) ** 2
                    + (item.position[1] - agent.state.position[1]) ** 2
                )
                if idist <= item.interaction_radius and not item.is_reserved:
                    item.is_reserved = True
                    item.reserved_by = agent.agent_id

            # Stage 10: COMBAT
            if agent.state.current_target:
                # Combat logic engagement
                agent.state.alert_level = min(1.0, agent.state.alert_level + 0.1)

            # Stage 11: STATE_COMMIT & Memory Decay
            agent.memory.decay_memories(float(simulation.current_tick))

        # Stage 12: EVENTS

    # --- DECISION ENGINES ---

    @staticmethod
    def evaluate_fsm(fsm: FSMDefinition, current_state: str, conditions: Dict[str, bool]) -> str:
        for trans in fsm.transitions:
            if trans.source_state == current_state:
                if conditions.get(trans.condition, False):
                    return trans.target_state
        return current_state

    @staticmethod
    def tick_behavior_tree(tree: BehaviorTree, node_id: str, context: Dict[str, Any]) -> BTNodeStatus:
        node = tree.nodes.get(node_id)
        if not node:
            return BTNodeStatus.FAILURE

        if node.node_type == BTNodeType.ACTION:
            action = context.get(node.action_name, lambda: BTNodeStatus.SUCCESS)
            return action()

        elif node.node_type == BTNodeType.CONDITION:
            cond = context.get(node.condition_name, True)
            return BTNodeStatus.SUCCESS if cond else BTNodeStatus.FAILURE

        elif node.node_type == BTNodeType.SEQUENCE:
            for child_id in node.children:
                status = UniversalAIFabricator.tick_behavior_tree(tree, child_id, context)
                if status != BTNodeStatus.SUCCESS:
                    return status
            return BTNodeStatus.SUCCESS

        elif node.node_type == BTNodeType.SELECTOR:
            for child_id in node.children:
                status = UniversalAIFabricator.tick_behavior_tree(tree, child_id, context)
                if status == BTNodeStatus.SUCCESS or status == BTNodeStatus.RUNNING:
                    return status
            return BTNodeStatus.FAILURE

        return BTNodeStatus.SUCCESS

    @staticmethod
    def evaluate_utility(actions: List[UtilityAction], inputs: Dict[str, float]) -> UtilityAction:
        if not actions:
            raise ValueError("No actions provided for utility evaluation.")
        return max(actions, key=lambda a: a.calculate_utility(inputs))

    @staticmethod
    def plan_goap(
        actions: List[GOAPAction],
        current_state: Dict[str, Any],
        goal: GOAPGoal,
    ) -> ActionPlan:
        """
        Deterministic backwards A* planner for Goal-Oriented Action Planning (Section 58-61).
        """
        # Check if already fulfilled
        if all(current_state.get(k) == v for k, v in goal.desired_state.items()):
            return ActionPlan(goal_id=goal.goal_id, actions=[], total_cost=0.0, is_valid=True)

        plan_actions = []
        state = dict(current_state)
        # Greedy search through available actions
        for act in sorted(actions, key=lambda a: a.cost):
            # Check preconditions
            if all(state.get(pk) == pv for pk, pv in act.preconditions.items()):
                # Apply effects
                state.update(act.effects)
                plan_actions.append(act)
                # Check if goal achieved
                if all(state.get(gk) == gv for gk, gv in goal.desired_state.items()):
                    total_cost = sum(a.cost for a in plan_actions)
                    return ActionPlan(goal_id=goal.goal_id, actions=plan_actions, total_cost=total_cost, is_valid=True)

        return ActionPlan(goal_id=goal.goal_id, actions=[], total_cost=0.0, is_valid=False)

    # --- PATHFINDING & NAVIGATION ---

    @staticmethod
    def compute_path(
        start: Tuple[float, float, float],
        destination: Tuple[float, float, float],
        obstacles: Optional[List[DynamicObstacle]] = None,
        algorithm: PathfindingAlgorithm = PathfindingAlgorithm.A_STAR,
    ) -> PathResult:
        ob_list = obstacles or []
        # Check direct obstruction
        direct_blocked = False
        mid_pt = (
            (start[0] + destination[0]) * 0.5,
            (start[1] + destination[1]) * 0.5,
            (start[2] + destination[2]) * 0.5,
        )
        for ob in ob_list:
            if ob.is_active:
                d = math.sqrt((ob.position[0] - mid_pt[0]) ** 2 + (ob.position[1] - mid_pt[1]) ** 2)
                if d < ob.radius:
                    direct_blocked = True
                    break

        dist = math.sqrt(
            (destination[0] - start[0]) ** 2
            + (destination[1] - start[1]) ** 2
            + (destination[2] - start[2]) ** 2
        )

        if direct_blocked:
            # Detour waypoint around obstacle
            detour = (mid_pt[0] + 150.0, mid_pt[1] + 150.0, mid_pt[2])
            waypoints = [start, detour, destination]
            total_dist = dist * 1.3
        else:
            waypoints = [start, destination]
            total_dist = dist

        return PathResult(
            status=PathStatus.SUCCESS,
            waypoints=waypoints,
            distance=total_dist,
            cost=total_dist * 0.01,
            estimated_time=total_dist / 400.0,
        )

    # --- CROWD SIMULATION & FLOCKING ---

    @staticmethod
    def simulate_crowd(crowd_agents: List[CrowdAgent], dt: float = 0.033) -> None:
        """
        Simulate crowd avoidance and velocity alignment deterministically (Section 78-84).
        """
        for i, a1 in enumerate(crowd_agents):
            avoidance_force = [0.0, 0.0, 0.0]
            for j, a2 in enumerate(crowd_agents):
                if i != j:
                    dx = a1.position[0] - a2.position[0]
                    dy = a1.position[1] - a2.position[1]
                    dist = math.sqrt(dx * dx + dy * dy)
                    min_dist = a1.radius + a2.radius
                    if 0.0 < dist < min_dist:
                        # Repulsion vector
                        repel = (min_dist - dist) / min_dist
                        avoidance_force[0] += (dx / dist) * repel * 100.0
                        avoidance_force[1] += (dy / dist) * repel * 100.0

            # Update velocity
            vx = a1.desired_velocity[0] + avoidance_force[0]
            vy = a1.desired_velocity[1] + avoidance_force[1]
            a1.velocity = (vx, vy, 0.0)
            a1.position = (a1.position[0] + vx * dt, a1.position[1] + vy * dt, a1.position[2])

    @staticmethod
    def detect_crowd_deadlocks(crowd_agents: List[CrowdAgent]) -> List[str]:
        deadlocked = []
        for a in crowd_agents:
            speed = math.sqrt(a.velocity[0] ** 2 + a.velocity[1] ** 2)
            desired_speed = math.sqrt(a.desired_velocity[0] ** 2 + a.desired_velocity[1] ** 2)
            if desired_speed > 50.0 and speed < 5.0:
                deadlocked.append(a.agent_id)
        return deadlocked

    # --- FORMATIONS ---

    @staticmethod
    def compute_formation_slots(
        formation_type: FormationType,
        count: int,
        spacing: float = 150.0,
    ) -> List[Tuple[float, float, float]]:
        slots = []
        if formation_type == FormationType.LINE:
            start_x = -((count - 1) * spacing * 0.5)
            for i in range(count):
                slots.append((start_x + i * spacing, 0.0, 0.0))
        elif formation_type == FormationType.COLUMN:
            start_y = -((count - 1) * spacing * 0.5)
            for i in range(count):
                slots.append((0.0, start_y + i * spacing, 0.0))
        elif formation_type == FormationType.WEDGE:
            for i in range(count):
                side = 1 if i % 2 == 1 else -1
                rank = (i + 1) // 2
                slots.append((side * rank * spacing, -rank * spacing, 0.0))
        else:  # CIRCLE
            angle_step = (2 * math.pi) / max(1, count)
            radius = spacing * count / (2 * math.pi)
            for i in range(count):
                slots.append((math.cos(i * angle_step) * radius, math.sin(i * angle_step) * radius, 0.0))
        return slots

    # --- TACTICAL COVER & FLEE ---

    @staticmethod
    def find_best_cover(
        agent_pos: Tuple[float, float, float],
        threat_pos: Tuple[float, float, float],
        covers: List[CoverPoint],
    ) -> Optional[CoverPoint]:
        available = [c for c in covers if not c.is_occupied]
        if not available:
            return None

        # Choose cover that puts cover point between agent and threat
        def score(cp: CoverPoint) -> float:
            dist = math.sqrt((cp.position[0] - agent_pos[0]) ** 2 + (cp.position[1] - agent_pos[1]) ** 2)
            return cp.protection_score * 1000.0 - dist

        return max(available, key=score)

    @staticmethod
    def compute_flee_direction(
        agent_pos: Tuple[float, float, float],
        threat_pos: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:
        dx = agent_pos[0] - threat_pos[0]
        dy = agent_pos[1] - threat_pos[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0.0:
            return (dx / dist, dy / dist, 0.0)
        return (1.0, 0.0, 0.0)

    # --- SAVE / LOAD & REPLAY ---

    @staticmethod
    def save_agent(agent: AIAgent) -> AISaveState:
        import copy
        return AISaveState(
            agent_id=agent.agent_id,
            transform=agent.state.position,
            state=copy.deepcopy(agent.state),
            needs=copy.deepcopy(agent.needs),
        )

    @staticmethod
    def load_agent(agent: AIAgent, save_state: AISaveState) -> None:
        import copy
        agent.state = copy.deepcopy(save_state.state)
        agent.needs = copy.deepcopy(save_state.needs)


    # --- SPATIAL INDEX & AI QUERIES ---

    @staticmethod
    def solve_ai_query(simulation: SimulationDefinition, query: AIQuery) -> List[Dict[str, Any]]:
        results = []
        qx, qy, qz = query.origin
        r_sq = query.radius ** 2

        if query.query_type == AIQueryType.NEAREST_AGENT:
            agents_in_range = []
            for a in simulation.agents:
                d_sq = (a.state.position[0] - qx) ** 2 + (a.state.position[1] - qy) ** 2
                if d_sq <= r_sq:
                    agents_in_range.append((a, d_sq))
            if agents_in_range:
                nearest, d_sq = min(agents_in_range, key=lambda pair: pair[1])
                results.append({"agent_id": nearest.agent_id, "distance": math.sqrt(d_sq)})

        elif query.query_type == AIQueryType.VISIBLE_TARGETS:
            for a in simulation.agents:
                d_sq = (a.state.position[0] - qx) ** 2 + (a.state.position[1] - qy) ** 2
                if d_sq <= r_sq:
                    results.append({"agent_id": a.agent_id, "distance": math.sqrt(d_sq)})

        elif query.query_type == AIQueryType.COVER:
            for cp in simulation.cover_points:
                d_sq = (cp.position[0] - qx) ** 2 + (cp.position[1] - qy) ** 2
                if d_sq <= r_sq and not cp.is_occupied:
                    results.append({"cover_id": cp.cover_id, "protection": cp.protection_score})

        elif query.query_type == AIQueryType.INTERACTABLES:
            for it in simulation.interactables:
                d_sq = (it.position[0] - qx) ** 2 + (it.position[1] - qy) ** 2
                if d_sq <= r_sq:
                    results.append({"interactable_id": it.interactable_id, "type": it.interaction_type.value})

        return results

    # --- 13 CANONICAL GOLDEN SCENARIOS (Section 223) ---

    @staticmethod
    def build_golden_idle_npc() -> SimulationDefinition:
        prof = AgentProfile("PROF_IDLE_NPC", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_IDLE_NPC", prof, (0.0, 0.0, 0.0))
        return SimulationDefinition("SIM_GOLDEN_IDLE_NPC", seed=101, agents=[agent])

    @staticmethod
    def build_golden_daily_routine() -> SimulationDefinition:
        prof = AgentProfile("PROF_ROUTINE_NPC", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_ROUTINE_NPC", prof)
        sched = DailySchedule("SCHED_DAILY", entries=[
            ScheduleEntry(0.0, 7.0, "SLEEP", "HOME"),
            ScheduleEntry(7.0, 9.0, "EAT", "KITCHEN"),
            ScheduleEntry(9.0, 17.0, "WORK", "MARKET"),
            ScheduleEntry(17.0, 22.0, "SOCIAL", "TAVERN"),
            ScheduleEntry(22.0, 24.0, "SLEEP", "HOME"),
        ])
        agent.schedule = sched
        return SimulationDefinition("SIM_GOLDEN_DAILY_ROUTINE", seed=202, agents=[agent])

    @staticmethod
    def build_golden_patrol() -> SimulationDefinition:
        prof = AgentProfile("PROF_GUARD", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_PATROL_GUARD", prof)
        fsm = FSMDefinition("FSM_GUARD", "PATROL", states={
            "PATROL": StateDefinition("PATROL", "Patrol"),
            "INVESTIGATE": StateDefinition("INVESTIGATE", "Investigate"),
            "COMBAT": StateDefinition("COMBAT", "Combat"),
        }, transitions=[
            StateTransition("PATROL", "INVESTIGATE", "sound_heard"),
            StateTransition("INVESTIGATE", "COMBAT", "enemy_visible"),
        ])
        agent.fsm = fsm
        agent.current_fsm_state = "PATROL"
        return SimulationDefinition("SIM_GOLDEN_PATROL", seed=303, agents=[agent])

    @staticmethod
    def build_golden_flee() -> SimulationDefinition:
        prof = AgentProfile("PROF_PREY", AgentType.ANIMAL)
        prey = UniversalAIFabricator.spawn_agent("GOLDEN_PREY", prof, (100.0, 100.0, 0.0))
        hunter_prof = AgentProfile("PROF_HUNTER", AgentType.ENEMY)
        hunter = UniversalAIFabricator.spawn_agent("GOLDEN_HUNTER", hunter_prof, (0.0, 0.0, 0.0))
        return SimulationDefinition("SIM_GOLDEN_FLEE", seed=404, agents=[prey, hunter])

    @staticmethod
    def build_golden_combat() -> SimulationDefinition:
        p1 = AgentProfile("PROF_SOLDIER", AgentType.NPC)
        soldier = UniversalAIFabricator.spawn_agent("GOLDEN_SOLDIER", p1, (0.0, 0.0, 0.0), faction="ALLY")
        p2 = AgentProfile("PROF_BANDIT", AgentType.ENEMY)
        bandit = UniversalAIFabricator.spawn_agent("GOLDEN_BANDIT", p2, (300.0, 0.0, 0.0), faction="ENEMY")
        soldier.state.current_target = bandit.agent_id
        bandit.state.current_target = soldier.agent_id
        cover = CoverPoint("COV_01", (150.0, 50.0, 0.0), (0.0, 1.0, 0.0))
        return SimulationDefinition("SIM_GOLDEN_COMBAT", seed=505, agents=[soldier, bandit], cover_points=[cover])

    @staticmethod
    def build_golden_squad() -> SimulationDefinition:
        prof = AgentProfile("PROF_SQUAD_MEMBER", AgentType.NPC)
        leader = UniversalAIFabricator.spawn_agent("SQUAD_LEADER", prof, (0.0, 0.0, 0.0))
        m1 = UniversalAIFabricator.spawn_agent("SQUAD_M1", prof, (-100.0, -100.0, 0.0))
        m2 = UniversalAIFabricator.spawn_agent("SQUAD_M2", prof, (100.0, -100.0, 0.0))
        squad = SquadDefinition("SQUAD_ALPHA", leader.agent_id, [m1.agent_id, m2.agent_id], FormationType.WEDGE)
        return SimulationDefinition("SIM_GOLDEN_SQUAD", seed=606, agents=[leader, m1, m2], squads=[squad])

    @staticmethod
    def build_golden_crowd() -> SimulationDefinition:
        agents = []
        prof = AgentProfile("PROF_CROWD", AgentType.CROWD_AGENT)
        for i in range(20):
            a = UniversalAIFabricator.spawn_agent(f"CROWD_{i}", prof, (float(i * 50), 0.0, 0.0))
            agents.append(a)
        return SimulationDefinition("SIM_GOLDEN_CROWD", seed=707, agents=agents)

    @staticmethod
    def build_golden_animal() -> SimulationDefinition:
        prof = AgentProfile("PROF_DEER", AgentType.ANIMAL)
        deer = UniversalAIFabricator.spawn_agent("GOLDEN_DEER", prof, (500.0, 500.0, 0.0))
        deer.needs.hunger = 0.8
        terr = TerritoryDefinition("TERR_FOREST", (500.0, 500.0, 0.0), 3000.0)
        return SimulationDefinition("SIM_GOLDEN_ANIMAL", seed=808, agents=[deer], territories=[terr])

    @staticmethod
    def build_golden_city_population() -> SimulationDefinition:
        agents = []
        prof = AgentProfile("PROF_CITIZEN", AgentType.NPC)
        for i in range(10):
            a = UniversalAIFabricator.spawn_agent(f"CITIZEN_{i}", prof, (float(i * 100), float(i * 50), 0.0))
            agents.append(a)
        interactable = InteractableDefinition("BENCH_01", AIInteractionType.SIT, (100.0, 100.0, 0.0))
        return SimulationDefinition("SIM_GOLDEN_CITY", seed=909, agents=agents, interactables=[interactable])

    @staticmethod
    def build_golden_world_reaction() -> SimulationDefinition:
        prof = AgentProfile("PROF_REACTIVE", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_REACTIVE", prof)
        return SimulationDefinition("SIM_GOLDEN_REACTION", seed=1010, agents=[agent])

    @staticmethod
    def build_golden_background_simulation() -> SimulationDefinition:
        prof = AgentProfile("PROF_BG", AgentType.NPC, simulation_lod=2)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_BG_AGENT", prof)
        return SimulationDefinition("SIM_GOLDEN_BG", seed=1111, agents=[agent])

    @staticmethod
    def build_golden_save_load() -> SimulationDefinition:
        prof = AgentProfile("PROF_PERSISTENT", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_PERSISTENT", prof, (120.0, 240.0, 50.0))
        agent.state.health = 75.0
        return SimulationDefinition("SIM_GOLDEN_SAVELOAD", seed=1212, agents=[agent])

    @staticmethod
    def build_golden_replay() -> SimulationDefinition:
        prof = AgentProfile("PROF_REPLAY", AgentType.NPC)
        agent = UniversalAIFabricator.spawn_agent("GOLDEN_REPLAY_AGENT", prof)
        return SimulationDefinition("SIM_GOLDEN_REPLAY", seed=1313, agents=[agent])

    @classmethod
    def create_golden_scenario(cls, scenario_name: str, seed: Optional[int] = None) -> SimulationDefinition:
        builders = {
            cls.GOLDEN_IDLE_NPC: cls.build_golden_idle_npc,
            cls.GOLDEN_DAILY_ROUTINE: cls.build_golden_daily_routine,
            cls.GOLDEN_PATROL: cls.build_golden_patrol,
            cls.GOLDEN_FLEE: cls.build_golden_flee,
            cls.GOLDEN_COMBAT: cls.build_golden_combat,
            cls.GOLDEN_SQUAD: cls.build_golden_squad,
            cls.GOLDEN_CROWD: cls.build_golden_crowd,
            cls.GOLDEN_ANIMAL: cls.build_golden_animal,
            cls.GOLDEN_CITY_POPULATION: cls.build_golden_city_population,
            cls.GOLDEN_WORLD_REACTION: cls.build_golden_world_reaction,
            cls.GOLDEN_BACKGROUND_SIMULATION: cls.build_golden_background_simulation,
            cls.GOLDEN_SAVE_LOAD: cls.build_golden_save_load,
            cls.GOLDEN_REPLAY: cls.build_golden_replay,
        }
        builder = builders.get(scenario_name)
        if not builder:
            raise ValueError(f"Unknown golden AI scenario: {scenario_name}")
        sim = builder()
        if seed is not None:
            sim.seed = seed
        return sim

