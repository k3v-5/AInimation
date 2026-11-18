"""
Universal Runtime Gameplay Fabricator Engine (UAF-81.79).
Authoritative gameplay world lifecycle, deterministic simulation tick,
Entity Component System (ECS), character and camera controllers, interaction and trigger systems,
hierarchical gameplay tags, rule engine, commands & events, health & combat pipeline,
status effects, abilities & cooldowns, timers, transactional inventory, quest progression,
spawn/despawn, versioned save/load, snapshots and deterministic replay.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
    copy_dict_deterministic,
    AbilityDefinition,
    AbilityState,
    CameraControllerComponent,
    CameraMode,
    CharacterControllerComponent,
    CombatState,
    DamageRequest,
    DamageResult,
    DamageType,
    DespawnRequest,
    Entity,
    EntityLifecycleState,
    GameplayCommand,
    GameplayCommandType,
    GameplayEvent,
    GameplayEventType,
    GameplayRule,
    GameplaySnapshot,
    GameplayTagContainer,
    GameplayTimer,
    GameplayWorld,
    GameplayWorldSettings,
    GameplayWorldState,
    HealthComponent,
    InteractableComponent,
    InteractionState,
    InventoryComponent,
    InventorySlot,
    MovementState,
    ObjectiveState,
    QuestDefinition,
    QuestObjective,
    QuestState,
    SaveState,
    SpawnRequest,
    StatusEffect,
    StatusStackingPolicy,
    TimerType,
    TriggerComponent,
    TriggerEventType,
    TriggerState,
)


class UniversalRuntimeGameplayFabricator:
    """Production fabricator and deterministic runtime engine for the UAF Gameplay World."""

    VALID_TRANSITIONS: Dict[GameplayWorldState, Set[GameplayWorldState]] = {
        GameplayWorldState.CREATED: {GameplayWorldState.INITIALIZING, GameplayWorldState.DESTROYED},
        GameplayWorldState.INITIALIZING: {GameplayWorldState.READY, GameplayWorldState.FAILED, GameplayWorldState.DESTROYED},
        GameplayWorldState.READY: {GameplayWorldState.RUNNING, GameplayWorldState.STOPPING, GameplayWorldState.DESTROYED},
        GameplayWorldState.RUNNING: {GameplayWorldState.PAUSED, GameplayWorldState.STOPPING, GameplayWorldState.FAILED, GameplayWorldState.DESTROYED},
        GameplayWorldState.PAUSED: {GameplayWorldState.RUNNING, GameplayWorldState.STOPPING, GameplayWorldState.DESTROYED},
        GameplayWorldState.STOPPING: {GameplayWorldState.STOPPED, GameplayWorldState.DESTROYED},
        GameplayWorldState.STOPPED: {GameplayWorldState.READY, GameplayWorldState.RUNNING, GameplayWorldState.DESTROYED},
        GameplayWorldState.FAILED: {GameplayWorldState.INITIALIZING, GameplayWorldState.DESTROYED},
        GameplayWorldState.DESTROYED: set(),
    }

    # =========================================================================
    # 1. LIFECYCLE MANAGEMENT
    # =========================================================================

    @classmethod
    def create_gameplay_world(
        cls,
        gameplay_world_id: str = "gameplay_world_default",
        runtime_world_id: str = "runtime_world_default",
        settings: Optional[GameplayWorldSettings] = None,
    ) -> GameplayWorld:
        """Instantiates a new Gameplay World in CREATED state."""
        return GameplayWorld(
            gameplay_world_id=gameplay_world_id,
            runtime_world_id=runtime_world_id,
            state=GameplayWorldState.CREATED,
            settings=settings or GameplayWorldSettings(),
        )

    @classmethod
    def transition_state(cls, world: GameplayWorld, new_state: GameplayWorldState) -> None:
        """Transitions GameplayWorld state enforcing the transition state machine."""
        allowed = cls.VALID_TRANSITIONS.get(world.state, set())
        if new_state not in allowed:
            raise ValueError(
                f"NO INVALID GAMEPLAY WORLD TRANSITION: Transition from {world.state.value} to {new_state.value} is forbidden."
            )
        world.state = new_state

    @classmethod
    def initialize(cls, world: GameplayWorld) -> None:
        """Initializes the Gameplay World."""
        cls.transition_state(world, GameplayWorldState.INITIALIZING)
        cls.transition_state(world, GameplayWorldState.READY)

    @classmethod
    def start(cls, world: GameplayWorld) -> None:
        """Starts Gameplay World execution."""
        cls.transition_state(world, GameplayWorldState.RUNNING)

    @classmethod
    def pause(cls, world: GameplayWorld) -> None:
        """Pauses Gameplay World execution."""
        cls.transition_state(world, GameplayWorldState.PAUSED)

    @classmethod
    def resume(cls, world: GameplayWorld) -> None:
        """Resumes Gameplay World execution."""
        cls.transition_state(world, GameplayWorldState.RUNNING)

    @classmethod
    def stop(cls, world: GameplayWorld) -> None:
        """Stops Gameplay World execution."""
        cls.transition_state(world, GameplayWorldState.STOPPING)
        cls.transition_state(world, GameplayWorldState.STOPPED)

    @classmethod
    def destroy(cls, world: GameplayWorld) -> None:
        """Destroys Gameplay World releasing all resources."""
        if world.state != GameplayWorldState.DESTROYED:
            world.state = GameplayWorldState.DESTROYED
        cls.cleanup(world)

    # =========================================================================
    # 2. TICK & SIMULATION CLOCK
    # =========================================================================

    @classmethod
    def tick(cls, world: GameplayWorld, dt: float = 0.016) -> None:
        """Executes a single deterministic simulation tick."""
        if world.state not in (GameplayWorldState.RUNNING, GameplayWorldState.READY, GameplayWorldState.CREATED):
            return

        world.tick.tick_index += 1
        world.tick.delta_time = dt
        world.tick.simulation_time += dt

        # 1. Process Timers
        cls._tick_timers(world, dt)

        # 2. Process Cooldowns
        cls._tick_cooldowns(world, dt)

        # 3. Process Status Effects
        cls._tick_status_effects(world, dt)

        # 4. Process Commands
        cls._process_commands(world)

        # 5. Evaluate Rules
        cls.evaluate_rules(world)

    @classmethod
    def _tick_timers(cls, world: GameplayWorld, dt: float) -> None:
        # Sort timers deterministically by timer_id
        for tid in sorted(world.timers.keys()):
            tm = world.timers[tid]
            if not tm.is_active or tm.is_completed:
                continue
            tm.elapsed += dt
            if tm.elapsed >= tm.duration:
                if tm.callback_event:
                    cls.dispatch_event(
                        world,
                        GameplayEventType.ABILITY_COMPLETED if "ability" in tm.callback_event else GameplayEventType.STATUS_REMOVED,
                        target_entity_id="",
                        payload={"timer_id": tm.timer_id, "callback": tm.callback_event},
                    )
                if tm.timer_type == TimerType.REPEATING:
                    tm.elapsed = 0.0
                else:
                    tm.is_completed = True
                    tm.is_active = False

    @classmethod
    def _tick_cooldowns(cls, world: GameplayWorld, dt: float) -> None:
        for ability in world.abilities.values():
            if ability.remaining_cooldown > 0.0:
                ability.remaining_cooldown = max(0.0, ability.remaining_cooldown - dt)
                if ability.remaining_cooldown == 0.0:
                    ability.state = AbilityState.AVAILABLE

    @classmethod
    def _tick_status_effects(cls, world: GameplayWorld, dt: float) -> None:
        for ent in world.entities.values():
            effects = ent.components.get("status_effects", {})
            for eff_id in list(effects.keys()):
                eff = effects[eff_id]
                if eff.is_expired:
                    continue
                eff.elapsed += dt
                eff.time_since_tick += dt

                # Periodic tick
                if eff.tick_interval > 0.0 and eff.time_since_tick >= eff.tick_interval:
                    eff.time_since_tick = 0.0
                    # Apply periodic magnitude (e.g. poison / burn damage)
                    cls.apply_damage(
                        world,
                        DamageRequest(
                            request_id=f"dot_{uuid.uuid4().hex[:6]}",
                            source_entity_id=eff.source_entity_id,
                            target_entity_id=eff.target_entity_id,
                            raw_damage=eff.magnitude * eff.stacks,
                            damage_type=DamageType.POISON,
                        ),
                    )

                if eff.elapsed >= eff.duration:
                    eff.is_expired = True
                    cls.dispatch_event(
                        world,
                        GameplayEventType.STATUS_REMOVED,
                        target_entity_id=ent.entity_id,
                        payload={"effect_id": eff_id},
                    )

    @classmethod
    def _process_commands(cls, world: GameplayWorld) -> None:
        cmds = list(world.command_queue)
        world.command_queue.clear()
        for cmd in cmds:
            cls.execute_command(world, cmd)

    # =========================================================================
    # 3. ENTITY COMPONENT SYSTEM (ECS)
    # =========================================================================

    @classmethod
    def spawn_entity(
        cls,
        world: GameplayWorld,
        entity_id: Optional[str] = None,
        name: str = "",
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Spawns an entity in the Gameplay World with a unique deterministic identity."""
        if len(world.entities) >= world.settings.max_entities:
            raise ValueError(f"Resource exhaustion: max_entities limit ({world.settings.max_entities}) reached.")

        eid = entity_id or f"entity_{world.spawn_counter}"
        if eid in world.entities:
            raise ValueError(f"NO DUPLICATE ENTITY ID: Entity '{eid}' already exists in Gameplay World.")

        world.spawn_counter += 1
        tag_container = GameplayTagContainer(set(tags or []))
        ent = Entity(
            entity_id=eid,
            name=name or eid,
            state=EntityLifecycleState.ACTIVE,
            tags=tag_container,
            position=position,
            rotation=rotation,
            metadata=metadata or {},
        )
        world.entities[eid] = ent
        cls.dispatch_event(
            world,
            GameplayEventType.ENTITY_SPAWNED,
            target_entity_id=eid,
            payload={"position": position},
        )
        return ent

    @classmethod
    def despawn_entity(cls, world: GameplayWorld, entity_id: str, reason: str = "DEFAULT") -> None:
        """Marks an entity as despawned safely."""
        if entity_id not in world.entities:
            return
        ent = world.entities[entity_id]
        ent.state = EntityLifecycleState.DISABLED
        cls.dispatch_event(
            world,
            GameplayEventType.ENTITY_DESPAWNED,
            target_entity_id=entity_id,
            payload={"reason": reason},
        )

    @classmethod
    def destroy_entity(cls, world: GameplayWorld, entity_id: str) -> None:
        """Removes an entity completely from the world."""
        if entity_id in world.entities:
            world.entities[entity_id].state = EntityLifecycleState.DESTROYED
            del world.entities[entity_id]
            cls.dispatch_event(
                world,
                GameplayEventType.ENTITY_DESPAWNED,
                target_entity_id=entity_id,
                payload={"reason": "DESTROYED"},
            )

    @classmethod
    def add_component(cls, world: GameplayWorld, entity_id: str, component_key: str, component: Any) -> None:
        """Attaches a component to an entity enforcing single-ownership."""
        if entity_id not in world.entities:
            raise ValueError(f"Cannot add component: Entity '{entity_id}' does not exist.")

        ent = world.entities[entity_id]
        if len(ent.components) >= world.settings.max_components_per_entity:
            raise ValueError(f"Resource exhaustion: max_components_per_entity reached on '{entity_id}'.")

        # Check if component is already owned by another entity
        for other_id, other_ent in world.entities.items():
            if other_id != entity_id and component_key in other_ent.components:
                if other_ent.components[component_key] is component:
                    raise ValueError(f"NO MULTIPLE COMPONENT OWNERS: Component is already owned by '{other_id}'.")

        ent.components[component_key] = component

    @classmethod
    def get_component(cls, world: GameplayWorld, entity_id: str, component_key: str) -> Optional[Any]:
        """Retrieves a component from an entity."""
        ent = world.entities.get(entity_id)
        if not ent:
            return None
        return ent.components.get(component_key)

    @classmethod
    def remove_component(cls, world: GameplayWorld, entity_id: str, component_key: str) -> Optional[Any]:
        """Removes a component from an entity."""
        ent = world.entities.get(entity_id)
        if not ent:
            return None
        return ent.components.pop(component_key, None)

    # =========================================================================
    # 4. CHARACTER CONTROLLERS
    # =========================================================================

    @classmethod
    def create_character_controller(
        cls,
        controller_id: str,
        move_speed: float = 6.0,
        run_speed: float = 10.0,
        jump_force: float = 8.0,
    ) -> CharacterControllerComponent:
        """Factory for CharacterControllerComponent."""
        return CharacterControllerComponent(
            controller_id=controller_id,
            move_speed=move_speed,
            run_speed=run_speed,
            jump_force=jump_force,
        )

    @classmethod
    def move_character(
        cls,
        world: GameplayWorld,
        entity_id: str,
        direction_x: float,
        direction_y: float,
        is_running: bool = False,
    ) -> None:
        """Applies movement to character controller."""
        ctrl: Optional[CharacterControllerComponent] = cls.get_component(world, entity_id, "character_controller")
        if not ctrl or not ctrl.is_enabled:
            return

        ent = world.entities[entity_id]
        if ent.state != EntityLifecycleState.ACTIVE:
            return

        mag = math.sqrt(direction_x * direction_x + direction_y * direction_y)
        if mag > 0.0:
            nx = direction_x / mag
            ny = direction_y / mag
            speed = ctrl.run_speed if is_running else ctrl.move_speed
            vx = nx * speed
            vy = ny * speed
            ctrl.velocity = (vx, vy, ctrl.velocity[2])
            ctrl.movement_state = MovementState.RUNNING if is_running else MovementState.WALKING
            ent.position = (
                ent.position[0] + vx * world.tick.delta_time,
                ent.position[1] + vy * world.tick.delta_time,
                ent.position[2],
            )
        else:
            ctrl.velocity = (0.0, 0.0, ctrl.velocity[2])
            ctrl.movement_state = MovementState.IDLE

    @classmethod
    def jump(cls, world: GameplayWorld, entity_id: str) -> bool:
        """Initiates jump if character is grounded."""
        ctrl: Optional[CharacterControllerComponent] = cls.get_component(world, entity_id, "character_controller")
        if not ctrl or not ctrl.is_enabled or not ctrl.is_grounded:
            return False

        ctrl.is_grounded = False
        ctrl.movement_state = MovementState.JUMPING
        ctrl.velocity = (ctrl.velocity[0], ctrl.velocity[1], ctrl.jump_force)
        return True

    @classmethod
    def set_grounded(cls, world: GameplayWorld, entity_id: str, is_grounded: bool) -> None:
        """Updates grounded status (e.g. from Physics World)."""
        ctrl: Optional[CharacterControllerComponent] = cls.get_component(world, entity_id, "character_controller")
        if ctrl:
            ctrl.is_grounded = is_grounded
            if is_grounded and ctrl.movement_state in (MovementState.JUMPING, MovementState.FALLING):
                ctrl.movement_state = MovementState.GROUNDED
                ctrl.velocity = (ctrl.velocity[0], ctrl.velocity[1], 0.0)

    # =========================================================================
    # 5. CAMERA CONTROLLERS
    # =========================================================================

    @classmethod
    def create_camera_controller(
        cls,
        camera_id: str,
        camera_mode: CameraMode = CameraMode.THIRD_PERSON,
        **kwargs: Any,
    ) -> CameraControllerComponent:
        """Factory for CameraControllerComponent."""
        return CameraControllerComponent(camera_id=camera_id, camera_mode=camera_mode, **kwargs)

    @classmethod
    def update_camera(
        cls,
        world: GameplayWorld,
        entity_id: str,
        delta_yaw: float = 0.0,
        delta_pitch: float = 0.0,
        zoom_delta: float = 0.0,
    ) -> None:
        """Updates camera orientation and distance respecting angle limits."""
        cam: Optional[CameraControllerComponent] = cls.get_component(world, entity_id, "camera_controller")
        if not cam:
            return

        cam.yaw = (cam.yaw + delta_yaw) % 360.0
        new_pitch = cam.pitch + delta_pitch
        cam.pitch = max(cam.min_pitch, min(cam.max_pitch, new_pitch))

        new_dist = cam.distance + zoom_delta
        cam.distance = max(cam.min_distance, min(cam.max_distance, new_dist))

    # =========================================================================
    # 6. INTERACTION SYSTEM
    # =========================================================================

    @classmethod
    def register_interactable(cls, world: GameplayWorld, entity_id: str, interaction: InteractableComponent) -> None:
        """Registers interactable component on an entity."""
        cls.add_component(world, entity_id, "interactable", interaction)

    @classmethod
    def query_interactions(
        cls,
        world: GameplayWorld,
        source_pos: Tuple[float, float, float],
        max_range: float = 5.0,
    ) -> List[InteractableComponent]:
        """Queries in-range interactables deterministically ordered by priority and distance."""
        candidates: List[Tuple[float, int, str, InteractableComponent]] = []
        for eid, ent in world.entities.items():
            inter: Optional[InteractableComponent] = ent.components.get("interactable")
            if inter and inter.state in (InteractionState.AVAILABLE, InteractionState.IN_RANGE):
                dx = ent.position[0] - source_pos[0]
                dy = ent.position[1] - source_pos[1]
                dz = ent.position[2] - source_pos[2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                if dist <= min(max_range, inter.max_distance):
                    candidates.append((dist, -inter.priority, inter.interaction_id, inter))

        candidates.sort(key=lambda x: (x[1], x[0], x[2]))
        return [c[3] for c in candidates]

    @classmethod
    def execute_interaction(cls, world: GameplayWorld, interaction_id: str, actor_entity_id: str) -> bool:
        """Validates and executes an interaction."""
        target_inter: Optional[InteractableComponent] = None
        target_eid: Optional[str] = None
        for eid, ent in world.entities.items():
            inter = ent.components.get("interactable")
            if inter and inter.interaction_id == interaction_id:
                target_inter = inter
                target_eid = eid
                break

        if not target_inter or not target_eid:
            raise ValueError(f"NO INVALID INTERACTION TARGET: Interaction '{interaction_id}' not found.")

        # Re-validate distance and state
        actor_ent = world.entities.get(actor_entity_id)
        target_ent = world.entities.get(target_eid)
        if not actor_ent or not target_ent:
            return False

        dx = actor_ent.position[0] - target_ent.position[0]
        dy = actor_ent.position[1] - target_ent.position[1]
        dz = actor_ent.position[2] - target_ent.position[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist > target_inter.max_distance:
            return False

        target_inter.state = InteractionState.COMPLETED
        cls.dispatch_event(
            world,
            GameplayEventType.INTERACTION_COMPLETED,
            target_entity_id=target_eid,
            source_entity_id=actor_entity_id,
            payload={"interaction_id": interaction_id},
        )
        return True

    # =========================================================================
    # 7. TRIGGER SYSTEM
    # =========================================================================

    @classmethod
    def create_trigger(
        cls,
        trigger_id: str,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        extents: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        filter_tags: Optional[Set[str]] = None,
    ) -> TriggerComponent:
        """Factory for TriggerComponent."""
        return TriggerComponent(
            trigger_id=trigger_id,
            position=position,
            extents=extents,
            filter_tags=filter_tags or set(),
        )

    @classmethod
    def process_trigger_overlap(
        cls,
        world: GameplayWorld,
        trigger: TriggerComponent,
        entity_id: str,
        is_overlapping: bool,
    ) -> Optional[TriggerEventType]:
        """Evaluates trigger overlaps and dispatches ENTER / EXIT events."""
        if trigger.state not in (TriggerState.ACTIVE, TriggerState.TRIGGERED):
            return None

        ent = world.entities.get(entity_id)
        if not ent:
            return None

        # Check tag filter
        if trigger.filter_tags and not ent.tags.has_any(trigger.filter_tags):
            return None

        if is_overlapping:
            if entity_id not in trigger.inside_entities:
                trigger.inside_entities.add(entity_id)
                trigger.state = TriggerState.TRIGGERED
                return TriggerEventType.ENTER
            return TriggerEventType.STAY
        else:
            if entity_id in trigger.inside_entities:
                trigger.inside_entities.remove(entity_id)
                if not trigger.inside_entities:
                    trigger.state = TriggerState.ACTIVE
                return TriggerEventType.EXIT
            return None

    # =========================================================================
    # 8. RULE EVALUATION ENGINE
    # =========================================================================

    @classmethod
    def add_rule(cls, world: GameplayWorld, rule: GameplayRule) -> None:
        """Registers a gameplay rule."""
        if len(world.rules) >= world.settings.max_rules:
            raise ValueError(f"Resource exhaustion: max_rules limit ({world.settings.max_rules}) reached.")
        world.rules[rule.rule_id] = rule

    @classmethod
    def evaluate_rules(cls, world: GameplayWorld, recursion_depth: int = 0) -> int:
        """Evaluates rules deterministically ordered by priority with recursion guard."""
        if recursion_depth > 10:
            raise ValueError("NO RULE RECURSION WITHOUT LIMIT: Maximum rule evaluation depth exceeded.")

        applied_count = 0
        sorted_rules = sorted(world.rules.values(), key=lambda r: (-r.priority, r.rule_id))

        for rule in sorted_rules:
            # Check conditions
            all_match = True
            for cond in rule.conditions:
                c_type = cond.get("type")
                if c_type == "entity_alive":
                    eid = cond.get("entity_id")
                    ent = world.entities.get(eid)
                    if not ent or ent.state != EntityLifecycleState.ACTIVE:
                        all_match = False
                        break
                elif c_type == "has_tag":
                    eid = cond.get("entity_id")
                    tag = cond.get("tag")
                    ent = world.entities.get(eid)
                    if not ent or not ent.tags.has(tag):
                        all_match = False
                        break

            if all_match:
                # Apply effects
                for eff in rule.effects:
                    e_type = eff.get("type")
                    if e_type == "add_tag":
                        eid = eff.get("entity_id")
                        tag = eff.get("tag")
                        if eid in world.entities:
                            world.entities[eid].tags.add(tag)
                    elif e_type == "damage":
                        cls.apply_damage(
                            world,
                            DamageRequest(
                                request_id=f"rule_dmg_{uuid.uuid4().hex[:6]}",
                                source_entity_id="",
                                target_entity_id=eff.get("entity_id", ""),
                                raw_damage=eff.get("amount", 0.0),
                            ),
                        )
                applied_count += 1

        return applied_count

    # =========================================================================
    # 9. COMMANDS & EVENTS
    # =========================================================================

    @classmethod
    def enqueue_command(cls, world: GameplayWorld, command: GameplayCommand) -> None:
        """Enqueues a command for deterministic execution."""
        if len(world.command_queue) >= world.settings.max_commands_per_tick:
            raise ValueError("Resource exhaustion: max_commands_per_tick exceeded.")
        world.command_queue.append(command)

    @classmethod
    def execute_command(cls, world: GameplayWorld, command: GameplayCommand) -> None:
        """Executes a gameplay command."""
        target_ent = world.entities.get(command.target_entity_id)
        if not target_ent or target_ent.state in (EntityLifecycleState.DESTROYED, EntityLifecycleState.PENDING_DESPAWN):
            # Dropped safely
            return

        if command.command_type == GameplayCommandType.MOVE:
            cls.move_character(
                world,
                command.target_entity_id,
                command.payload.get("dx", 0.0),
                command.payload.get("dy", 0.0),
                command.payload.get("is_running", False),
            )
        elif command.command_type == GameplayCommandType.USE_ABILITY:
            cls.activate_ability(world, command.target_entity_id, command.payload.get("ability_id", ""))
        elif command.command_type == GameplayCommandType.TAKE_DAMAGE:
            cls.apply_damage(
                world,
                DamageRequest(
                    request_id=f"cmd_dmg_{uuid.uuid4().hex[:6]}",
                    source_entity_id=command.source_entity_id,
                    target_entity_id=command.target_entity_id,
                    raw_damage=command.payload.get("damage", 0.0),
                ),
            )
        elif command.command_type == GameplayCommandType.HEAL:
            cls.heal(world, command.target_entity_id, command.payload.get("heal", 0.0))

    @classmethod
    def dispatch_event(
        cls,
        world: GameplayWorld,
        event_type: GameplayEventType,
        target_entity_id: str,
        source_entity_id: str = "",
        payload: Optional[Dict[str, Any]] = None,
    ) -> GameplayEvent:
        """Emits a gameplay event with deterministic sequence counter."""
        world.event_sequence_counter += 1
        ev = GameplayEvent(
            event_id=f"ev_{world.event_sequence_counter}",
            event_type=event_type,
            target_entity_id=target_entity_id,
            source_entity_id=source_entity_id,
            sequence_number=world.event_sequence_counter,
            timestamp=world.tick.simulation_time,
            payload=payload or {},
        )
        world.event_queue.append(ev)
        world.event_history.append(ev)
        return ev

    # =========================================================================
    # 10. HEALTH & COMBAT PIPELINE
    # =========================================================================

    @classmethod
    def apply_damage(cls, world: GameplayWorld, request: DamageRequest) -> DamageResult:
        """Applies damage through mitigation, shield absorption, and death detection."""
        target = world.entities.get(request.target_entity_id)
        if not target or target.state != EntityLifecycleState.ACTIVE:
            return DamageResult(
                request_id=request.request_id,
                source_entity_id=request.source_entity_id,
                target_entity_id=request.target_entity_id,
                raw_damage=request.raw_damage,
                mitigated_damage=0.0,
                shield_absorbed=0.0,
                health_damage=0.0,
                final_health=0.0,
                is_killed=False,
            )

        hp: Optional[HealthComponent] = cls.get_component(world, request.target_entity_id, "health")
        if not hp or hp.is_invulnerable or hp.is_dead:
            return DamageResult(
                request_id=request.request_id,
                source_entity_id=request.source_entity_id,
                target_entity_id=request.target_entity_id,
                raw_damage=request.raw_damage,
                mitigated_damage=0.0,
                shield_absorbed=0.0,
                health_damage=0.0,
                final_health=hp.current_health if hp else 0.0,
                is_killed=False,
            )

        # Modifiers & mitigation
        raw = max(0.0, request.raw_damage)
        mitigated = raw
        if "armor" in request.modifiers:
            armor = request.modifiers["armor"]
            mitigated = raw * (100.0 / (100.0 + max(0.0, armor)))

        # Shield absorption
        absorbed = 0.0
        remaining_damage = mitigated
        if hp.current_shield > 0.0:
            absorbed = min(hp.current_shield, remaining_damage)
            hp.current_shield -= absorbed
            remaining_damage -= absorbed
            cls.dispatch_event(
                world,
                GameplayEventType.SHIELD_ABSORBED,
                target_entity_id=request.target_entity_id,
                payload={"absorbed": absorbed},
            )

        # Health damage
        health_dmg = min(hp.current_health, remaining_damage)
        hp.current_health = max(hp.min_health, hp.current_health - health_dmg)
        is_killed = hp.current_health <= hp.min_health

        cls.dispatch_event(
            world,
            GameplayEventType.DAMAGE_APPLIED,
            target_entity_id=request.target_entity_id,
            source_entity_id=request.source_entity_id,
            payload={"damage": health_dmg, "shield_damage": absorbed},
        )
        cls.dispatch_event(
            world,
            GameplayEventType.HEALTH_CHANGED,
            target_entity_id=request.target_entity_id,
            payload={"current_health": hp.current_health},
        )

        if is_killed:
            hp.is_dead = True
            target.components["combat_state"] = CombatState.DEAD
            cls.dispatch_event(
                world,
                GameplayEventType.DIED,
                target_entity_id=request.target_entity_id,
                source_entity_id=request.source_entity_id,
            )

        return DamageResult(
            request_id=request.request_id,
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            raw_damage=raw,
            mitigated_damage=mitigated,
            shield_absorbed=absorbed,
            health_damage=health_dmg,
            final_health=hp.current_health,
            is_killed=is_killed,
        )

    @classmethod
    def heal(cls, world: GameplayWorld, entity_id: str, amount: float) -> float:
        """Heals an entity respecting max_health boundaries."""
        hp: Optional[HealthComponent] = cls.get_component(world, entity_id, "health")
        if not hp or hp.is_dead:
            return 0.0

        amt = max(0.0, amount)
        actual_heal = min(hp.max_health - hp.current_health, amt)
        hp.current_health += actual_heal

        cls.dispatch_event(
            world,
            GameplayEventType.HEALED,
            target_entity_id=entity_id,
            payload={"amount": actual_heal},
        )
        cls.dispatch_event(
            world,
            GameplayEventType.HEALTH_CHANGED,
            target_entity_id=entity_id,
            payload={"current_health": hp.current_health},
        )
        return actual_heal

    # =========================================================================
    # 11. STATUS EFFECTS
    # =========================================================================

    @classmethod
    def apply_status_effect(cls, world: GameplayWorld, effect: StatusEffect) -> None:
        """Applies a status effect respecting its stacking policy."""
        ent = world.entities.get(effect.target_entity_id)
        if not ent:
            return

        effects = ent.components.setdefault("status_effects", {})
        existing = effects.get(effect.effect_id)

        if existing and not existing.is_expired:
            if effect.policy == StatusStackingPolicy.REFRESH:
                existing.elapsed = 0.0
                existing.duration = effect.duration
            elif effect.policy == StatusStackingPolicy.STACK:
                existing.stacks = min(existing.max_stacks, existing.stacks + 1)
                existing.elapsed = 0.0
            elif effect.policy == StatusStackingPolicy.MAX:
                existing.magnitude = max(existing.magnitude, effect.magnitude)
                existing.elapsed = 0.0
            elif effect.policy == StatusStackingPolicy.REPLACE:
                effects[effect.effect_id] = effect
            elif effect.policy == StatusStackingPolicy.IGNORE:
                return
        else:
            effects[effect.effect_id] = effect

        cls.dispatch_event(
            world,
            GameplayEventType.STATUS_APPLIED,
            target_entity_id=effect.target_entity_id,
            payload={"effect_id": effect.effect_id, "stacks": effect.stacks},
        )

    # =========================================================================
    # 12. ABILITIES & COOLDOWNS
    # =========================================================================

    @classmethod
    def register_ability(cls, world: GameplayWorld, ability: AbilityDefinition) -> None:
        """Registers an ability in the world."""
        world.abilities[ability.ability_id] = ability

    @classmethod
    def activate_ability(cls, world: GameplayWorld, entity_id: str, ability_id: str) -> bool:
        """Validates conditions and activates an ability."""
        ent = world.entities.get(entity_id)
        ab = world.abilities.get(ability_id)
        if not ent or not ab:
            return False

        if ab.remaining_cooldown > 0.0 or ab.state == AbilityState.ON_COOLDOWN:
            return False

        # Tag condition checks
        if ab.required_tags and not ent.tags.has_all(ab.required_tags):
            return False
        if ab.blocked_tags and ent.tags.has_any(ab.blocked_tags):
            return False

        ab.remaining_cooldown = ab.cooldown
        ab.state = AbilityState.ON_COOLDOWN

        cls.dispatch_event(
            world,
            GameplayEventType.ABILITY_STARTED,
            target_entity_id=entity_id,
            payload={"ability_id": ability_id},
        )
        cls.dispatch_event(
            world,
            GameplayEventType.ABILITY_COMPLETED,
            target_entity_id=entity_id,
            payload={"ability_id": ability_id},
        )
        return True

    # =========================================================================
    # 13. TIMERS
    # =========================================================================

    @classmethod
    def add_timer(
        cls,
        world: GameplayWorld,
        timer_id: str,
        duration: float,
        timer_type: TimerType = TimerType.ONE_SHOT,
        callback_event: Optional[str] = None,
    ) -> GameplayTimer:
        """Registers a gameplay timer."""
        if len(world.timers) >= world.settings.max_timers:
            raise ValueError("Resource exhaustion: max_timers exceeded.")

        tm = GameplayTimer(
            timer_id=timer_id,
            duration=max(1e-4, duration),
            timer_type=timer_type,
            callback_event=callback_event,
        )
        world.timers[timer_id] = tm
        return tm

    @classmethod
    def cancel_timer(cls, world: GameplayWorld, timer_id: str) -> None:
        """Cancels and removes a timer."""
        if timer_id in world.timers:
            world.timers[timer_id].is_active = False
            del world.timers[timer_id]

    # =========================================================================
    # 14. INVENTORY SYSTEM (TRANSACTIONAL & ATOMIC)
    # =========================================================================

    @classmethod
    def create_inventory(cls, inventory_id: str, max_slots: int = 20) -> InventoryComponent:
        """Creates a new inventory component."""
        return InventoryComponent(inventory_id=inventory_id, max_slots=max_slots)

    @classmethod
    def add_item(cls, inv: InventoryComponent, item_id: str, quantity: int, max_stack: int = 99) -> int:
        """Adds items filling stacks first; returns remaining unadded count."""
        if quantity <= 0:
            return 0
        rem = quantity

        # 1. Fill existing matching stacks
        for slot in inv.slots.values():
            if slot.item_id == item_id and slot.quantity < slot.max_stack:
                space = slot.max_stack - slot.quantity
                to_add = min(space, rem)
                slot.quantity += to_add
                rem -= to_add
                if rem == 0:
                    return 0

        # 2. Add to empty slots
        for s_idx in range(inv.max_slots):
            if s_idx not in inv.slots:
                to_add = min(max_stack, rem)
                inv.slots[s_idx] = InventorySlot(
                    slot_id=s_idx,
                    item_id=item_id,
                    quantity=to_add,
                    max_stack=max_stack,
                )
                rem -= to_add
                if rem == 0:
                    return 0

        return rem

    @classmethod
    def remove_item(cls, inv: InventoryComponent, item_id: str, quantity: int) -> bool:
        """Removes items atomically: if total available < quantity, nothing is modified."""
        if quantity <= 0:
            return True

        total_avail = sum(s.quantity for s in inv.slots.values() if s.item_id == item_id)
        if total_avail < quantity:
            return False

        rem = quantity
        for s_idx in sorted(inv.slots.keys()):
            s = inv.slots[s_idx]
            if s.item_id == item_id:
                if s.quantity <= rem:
                    rem -= s.quantity
                    del inv.slots[s_idx]
                else:
                    s.quantity -= rem
                    rem = 0
                if rem == 0:
                    break
        return True

    @classmethod
    def transfer_item(
        cls,
        from_inv: InventoryComponent,
        to_inv: InventoryComponent,
        item_id: str,
        quantity: int,
    ) -> bool:
        """Transfers items between inventories atomically without partial mutation."""
        if quantity <= 0:
            return True

        # Check source has enough
        total_avail = sum(s.quantity for s in from_inv.slots.values() if s.item_id == item_id)
        if total_avail < quantity:
            return False

        # Backup destination
        to_backup = copy.deepcopy(to_inv.slots)
        rem = cls.add_item(to_inv, item_id, quantity)
        if rem > 0:
            # Destination cannot accept all items -> rollback
            to_inv.slots = to_backup
            return False

        # Source removal
        cls.remove_item(from_inv, item_id, quantity)
        return True

    # =========================================================================
    # 15. QUEST SYSTEM
    # =========================================================================

    @classmethod
    def register_quest(cls, world: GameplayWorld, quest: QuestDefinition) -> None:
        """Registers a quest in the world."""
        world.quests[quest.quest_id] = quest

    @classmethod
    def start_quest(cls, world: GameplayWorld, quest_id: str) -> bool:
        """Starts a quest."""
        q = world.quests.get(quest_id)
        if not q or q.state != QuestState.INACTIVE:
            return False

        q.state = QuestState.ACTIVE
        for obj in q.objectives.values():
            obj.state = ObjectiveState.ACTIVE

        cls.dispatch_event(
            world,
            GameplayEventType.QUEST_STARTED,
            target_entity_id="",
            payload={"quest_id": quest_id},
        )
        return True

    @classmethod
    def progress_objective(cls, world: GameplayWorld, quest_id: str, objective_id: str, delta: int = 1) -> bool:
        """Progresses a quest objective and completes the quest if all mandatory objectives are met."""
        q = world.quests.get(quest_id)
        if not q or q.state != QuestState.ACTIVE:
            return False

        obj = q.objectives.get(objective_id)
        if not obj or obj.state == ObjectiveState.COMPLETED:
            return False

        obj.current_count = min(obj.target_count, obj.current_count + delta)
        if obj.current_count >= obj.target_count:
            obj.state = ObjectiveState.COMPLETED
            cls.dispatch_event(
                world,
                GameplayEventType.OBJECTIVE_COMPLETED,
                target_entity_id="",
                payload={"quest_id": quest_id, "objective_id": objective_id},
            )

        # Check quest completion
        if all(o.state == ObjectiveState.COMPLETED for o in q.objectives.values() if o.is_mandatory):
            q.state = QuestState.COMPLETED

        return True

    # =========================================================================
    # 16. SAVE / LOAD STATE
    # =========================================================================

    @classmethod
    def save_state(cls, world: GameplayWorld, save_id: str = "save_001") -> SaveState:
        """Serializes persistent gameplay state excluding transient memory."""
        entities_data = {}
        for eid, ent in world.entities.items():
            if ent.state == EntityLifecycleState.ACTIVE:
                entities_data[eid] = {
                    "name": ent.name,
                    "position": ent.position,
                    "rotation": ent.rotation,
                    "tags": ent.tags.to_dict(),
                    "health": ent.components["health"].to_dict() if "health" in ent.components else None,
                }

        return SaveState(
            save_id=save_id,
            version=1,
            timestamp=world.tick.simulation_time,
            gameplay_world_id=world.gameplay_world_id,
            entities_data=entities_data,
            quest_data={k: q.to_dict() for k, q in world.quests.items()},
            cooldowns_data={k: a.remaining_cooldown for k, a in world.abilities.items()},
        )

    @classmethod
    def load_state(cls, world: GameplayWorld, save: SaveState) -> bool:
        """Restores persistent state from SaveState with version validation."""
        if save.version != 1:
            return False

        if save.gameplay_world_id:
            world.gameplay_world_id = save.gameplay_world_id

        world.entities.clear()
        for eid, edata in save.entities_data.items():
            ent = cls.spawn_entity(
                world,
                entity_id=eid,
                name=edata.get("name", eid),
                position=edata.get("position", (0.0, 0.0, 0.0)),
                rotation=edata.get("rotation", (0.0, 0.0, 0.0)),
                tags=edata.get("tags", []),
            )
            if edata.get("health"):
                h_info = edata["health"]
                cls.add_component(
                    world,
                    eid,
                    "health",
                    HealthComponent(
                        current_health=h_info["current_health"],
                        max_health=h_info["max_health"],
                        current_shield=h_info["current_shield"],
                        max_shield=h_info["max_shield"],
                    ),
                )

        world.tick.simulation_time = save.timestamp
        return True

    # =========================================================================
    # 17. SNAPSHOTS & REPLAY
    # =========================================================================

    @classmethod
    def create_snapshot(cls, world: GameplayWorld, snapshot_id: Optional[str] = None) -> GameplaySnapshot:
        """Captures complete deterministic state snapshot."""
        sid = snapshot_id or f"snap_{uuid.uuid4().hex[:8]}"
        return GameplaySnapshot(
            snapshot_id=sid,
            gameplay_world_id=world.gameplay_world_id,
            state=world.state.value,
            tick_index=world.tick.tick_index,
            simulation_time=world.tick.simulation_time,
            entities={k: e.to_dict() for k, e in world.entities.items()},
            quests={k: q.to_dict() for k, q in world.quests.items()},
            abilities={k: a.to_dict() for k, a in world.abilities.items()},
            timers={k: t.to_dict() for k, t in world.timers.items()},
            fingerprint=world.compute_fingerprint(),
        )

    @classmethod
    def restore_snapshot(cls, world: GameplayWorld, snapshot: GameplaySnapshot) -> None:
        """Restores world to exact snapshot state."""
        world.gameplay_world_id = snapshot.gameplay_world_id
        world.state = GameplayWorldState(snapshot.state)
        world.tick.tick_index = snapshot.tick_index
        world.tick.simulation_time = snapshot.simulation_time

        world.entities.clear()
        for eid, edict in snapshot.entities.items():
            ent = Entity(
                entity_id=eid,
                name=edict.get("name", eid),
                state=EntityLifecycleState(edict.get("state", "ACTIVE")),
                tags=GameplayTagContainer(set(edict.get("tags", []))),
                position=tuple(edict.get("position", (0.0, 0.0, 0.0))),
                rotation=tuple(edict.get("rotation", (0.0, 0.0, 0.0))),
            )
            # Restore components if present
            for ck, cv in edict.get("components", {}).items():
                if ck == "health":
                    ent.components["health"] = HealthComponent(**cv)
                elif ck == "character_controller":
                    ent.components["character_controller"] = CharacterControllerComponent(**cv)
            world.entities[eid] = ent

    @classmethod
    def replay_commands(cls, world: GameplayWorld, commands: List[GameplayCommand]) -> None:
        """Replays commands in deterministic sequence."""
        for cmd in commands:
            cls.execute_command(world, cmd)

    # =========================================================================
    # 18. CLEANUP & TEARDOWN
    # =========================================================================

    @classmethod
    def cleanup(cls, world: GameplayWorld) -> None:
        """Cleans up all entities, components, rules, and resets counters."""
        world.entities.clear()
        world.rules.clear()
        world.abilities.clear()
        world.quests.clear()
        world.timers.clear()
        world.command_queue.clear()
        world.event_queue.clear()
        world.event_history.clear()
        world.event_sequence_counter = 0
        world.spawn_counter = 0
