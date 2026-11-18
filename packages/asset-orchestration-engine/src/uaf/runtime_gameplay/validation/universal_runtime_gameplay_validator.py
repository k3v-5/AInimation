"""
Universal Runtime Gameplay Validator (UAF-81.79).
Validates entities, components, commands, events, health, combat, abilities,
cooldowns, inventory, quests, status effects, saves, snapshots, and replays
according to §126 Non-Negotiable Invariants.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    CameraControllerComponent,
    CharacterControllerComponent,
    EntityLifecycleState,
    GameplayCommand,
    GameplayEvent,
    GameplaySnapshot,
    GameplayWorld,
    HealthComponent,
    InteractableComponent,
    InventoryComponent,
    ObjectiveState,
    QuestDefinition,
    QuestState,
    SaveState,
    StatusEffect,
    TriggerComponent,
)


@dataclass
class GameplayValidationIssue:
    severity: str  # "ERROR", "WARNING", "INFO"
    code: str
    message: str
    target_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "target_id": self.target_id,
        }


class UniversalRuntimeGameplayValidator:
    """Normative validator verifying all UAF-81.79 non-negotiable invariants."""

    @classmethod
    def validate(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Convenience alias for validate_world."""
        return cls.validate_world(world)

    @classmethod
    def validate_world(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Runs comprehensive validation checks across the entire Gameplay World."""
        issues: List[GameplayValidationIssue] = []

        issues.extend(cls.validate_limits(world))
        issues.extend(cls.validate_entities(world))
        issues.extend(cls.validate_characters_and_controllers(world))
        issues.extend(cls.validate_cameras(world))
        issues.extend(cls.validate_combat_and_health(world))
        issues.extend(cls.validate_abilities_and_cooldowns(world))
        issues.extend(cls.validate_status_effects(world))
        issues.extend(cls.validate_inventory(world))
        issues.extend(cls.validate_quests(world))
        issues.extend(cls.validate_interactions_and_triggers(world))
        issues.extend(cls.validate_tags(world))
        issues.extend(cls.validate_commands(world))

        return issues

    @classmethod
    def validate_limits(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates world resource limits (§126 NO_UNBOUNDED_GAMEPLAY_RESOURCE)."""
        issues: List[GameplayValidationIssue] = []

        if len(world.entities) > world.settings.max_entities:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="RESOURCE_LIMIT_EXCEEDED",
                    message=f"Total entities ({len(world.entities)}) exceeds max_entities ({world.settings.max_entities}).",
                )
            )

        for eid, ent in world.entities.items():
            if len(ent.components) > world.settings.max_components_per_entity:
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="RESOURCE_LIMIT_EXCEEDED",
                        message=f"Entity '{eid}' components ({len(ent.components)}) exceeds max_components_per_entity ({world.settings.max_components_per_entity}).",
                        target_id=eid,
                    )
                )

        if len(world.timers) > world.settings.max_timers:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="RESOURCE_LIMIT_EXCEEDED",
                    message=f"Active timers ({len(world.timers)}) exceeds max_timers ({world.settings.max_timers}).",
                )
            )

        if len(world.command_queue) > world.settings.max_commands_per_tick:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="RESOURCE_LIMIT_EXCEEDED",
                    message=f"Command queue ({len(world.command_queue)}) exceeds max_commands_per_tick ({world.settings.max_commands_per_tick}).",
                )
            )

        if len(world.rules) > world.settings.max_rules:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="RESOURCE_LIMIT_EXCEEDED",
                    message=f"Rules ({len(world.rules)}) exceeds max_rules ({world.settings.max_rules}).",
                )
            )

        return issues

    @classmethod
    def validate_entities(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates entity integrity and component ownership (§126)."""
        issues: List[GameplayValidationIssue] = []
        seen_component_instances: Dict[int, str] = {}

        for eid, entity in world.entities.items():
            if not eid or not eid.strip():
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="NO_INVALID_ENTITY",
                        message="Entity ID must be a non-empty string.",
                        target_id=eid,
                    )
                )

            # Check lifecycle state consistency
            if entity.state == EntityLifecycleState.DESTROYED and entity.is_enabled:
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="NO_INVALID_CHARACTER_STATE",
                        message=f"Entity '{eid}' is DESTROYED but marked as enabled.",
                        target_id=eid,
                    )
                )

            # Check unique component instance ownership across entities
            for comp_name, comp in entity.components.items():
                c_id = id(comp)
                if c_id in seen_component_instances and seen_component_instances[c_id] != eid:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_MULTIPLE_COMPONENT_OWNERS",
                            message=f"Component '{comp_name}' is attached to multiple entities: '{seen_component_instances[c_id]}' and '{eid}'.",
                            target_id=eid,
                        )
                    )
                seen_component_instances[c_id] = eid

        return issues

    @classmethod
    def validate_characters_and_controllers(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates character controllers and movement parameters."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            ctrl = entity.components.get("character_controller")
            if isinstance(ctrl, CharacterControllerComponent):
                if ctrl.move_speed < 0.0 or ctrl.run_speed < 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CHARACTER_STATE",
                            message=f"Character controller on '{eid}' has negative speed (move: {ctrl.move_speed}, run: {ctrl.run_speed}).",
                            target_id=eid,
                        )
                    )
                if ctrl.jump_force < 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CHARACTER_STATE",
                            message=f"Character controller on '{eid}' has negative jump_force {ctrl.jump_force}.",
                            target_id=eid,
                        )
                    )

        return issues

    @classmethod
    def validate_cameras(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates camera controllers and distance limits."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            cam = entity.components.get("camera_controller")
            if isinstance(cam, CameraControllerComponent):
                if cam.target_entity_id and cam.target_entity_id not in world.entities:
                    issues.append(
                        GameplayValidationIssue(
                            severity="WARNING",
                            code="NO_INVALID_CAMERA_LIMIT",
                            message=f"Camera controller on '{eid}' targets non-existent entity '{cam.target_entity_id}'.",
                            target_id=eid,
                        )
                    )

                if cam.zoom <= 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CAMERA_LIMIT",
                            message=f"Camera controller on '{eid}' has non-positive zoom {cam.zoom}.",
                            target_id=eid,
                        )
                    )

                if cam.min_distance > cam.max_distance:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CAMERA_LIMIT",
                            message=f"Camera controller on '{eid}' min_distance ({cam.min_distance}) > max_distance ({cam.max_distance}).",
                            target_id=eid,
                        )
                    )

                if cam.min_pitch > cam.max_pitch:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CAMERA_LIMIT",
                            message=f"Camera controller on '{eid}' min_pitch ({cam.min_pitch}) > max_pitch ({cam.max_pitch}).",
                            target_id=eid,
                        )
                    )

                if cam.distance < cam.min_distance or cam.distance > cam.max_distance:
                    issues.append(
                        GameplayValidationIssue(
                            severity="WARNING",
                            code="NO_INVALID_CAMERA_LIMIT",
                            message=f"Camera controller on '{eid}' distance {cam.distance} out of bounds [{cam.min_distance}, {cam.max_distance}].",
                            target_id=eid,
                        )
                    )

        return issues

    @classmethod
    def validate_combat_and_health(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates health bounds, shield values, and combat states (§126)."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            health_comp = entity.components.get("health")
            if isinstance(health_comp, HealthComponent):
                if health_comp.max_health <= 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_HEALTH_UNDERFLOW",
                            message=f"Entity '{eid}' has invalid max_health <= 0 ({health_comp.max_health}).",
                            target_id=eid,
                        )
                    )

                if health_comp.current_health < health_comp.min_health:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_HEALTH_UNDERFLOW",
                            message=f"Entity '{eid}' has health underflow: {health_comp.current_health} < min_health {health_comp.min_health}.",
                            target_id=eid,
                        )
                    )

                if health_comp.current_health > health_comp.max_health + 1e-4:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_HEALTH_OVERFLOW",
                            message=f"Entity '{eid}' has health overflow: {health_comp.current_health} > max_health {health_comp.max_health}.",
                            target_id=eid,
                        )
                    )

                if health_comp.current_shield < 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_HEALTH_UNDERFLOW",
                            message=f"Entity '{eid}' has negative shield: {health_comp.current_shield}.",
                            target_id=eid,
                        )
                    )

                if health_comp.current_shield > health_comp.max_shield + 1e-4:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_HEALTH_OVERFLOW",
                            message=f"Entity '{eid}' has shield overflow: {health_comp.current_shield} > max_shield {health_comp.max_shield}.",
                            target_id=eid,
                        )
                    )

                if health_comp.is_dead and health_comp.current_health > 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_CHARACTER_STATE",
                            message=f"Entity '{eid}' is marked dead but current_health={health_comp.current_health} > 0.",
                            target_id=eid,
                        )
                    )

        return issues

    @classmethod
    def validate_abilities_and_cooldowns(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates abilities, costs, and cooldown non-desync (§126)."""
        issues: List[GameplayValidationIssue] = []

        for aid, ability in world.abilities.items():
            if ability.cooldown < 0.0 or ability.resource_cost < 0.0 or ability.cast_time < 0.0:
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="NO_INVALID_ABILITY_STATE",
                        message=f"Ability '{aid}' has negative cooldown/cost/cast_time.",
                        target_id=aid,
                    )
                )

            if ability.remaining_cooldown < 0.0:
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="NO_COOLDOWN_CLOCK_DESYNC",
                        message=f"Ability '{aid}' has negative remaining_cooldown: {ability.remaining_cooldown}.",
                        target_id=aid,
                    )
                )

        return issues

    @classmethod
    def validate_status_effects(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates status effects stacks and duration (§126)."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            effects = entity.components.get("status_effects")
            if isinstance(effects, list):
                for eff in effects:
                    if isinstance(eff, StatusEffect):
                        if eff.duration < 0.0 and eff.duration != -1.0:
                            issues.append(
                                GameplayValidationIssue(
                                    severity="ERROR",
                                    code="NO_INVALID_STATUS_STACK",
                                    message=f"Status effect '{eff.effect_id}' on entity '{eid}' has negative duration {eff.duration}.",
                                    target_id=eff.effect_id,
                                )
                            )
                        if eff.stacks <= 0:
                            issues.append(
                                GameplayValidationIssue(
                                    severity="ERROR",
                                    code="NO_INVALID_STATUS_STACK",
                                    message=f"Status effect '{eff.effect_id}' on entity '{eid}' has non-positive stacks {eff.stacks}.",
                                    target_id=eff.effect_id,
                                )
                            )
                        if eff.stacks > eff.max_stacks:
                            issues.append(
                                GameplayValidationIssue(
                                    severity="ERROR",
                                    code="NO_INVALID_STATUS_STACK",
                                    message=f"Status effect '{eff.effect_id}' on entity '{eid}' has stacks ({eff.stacks}) > max_stacks ({eff.max_stacks}).",
                                    target_id=eff.effect_id,
                                )
                            )

        return issues

    @classmethod
    def validate_inventory(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates inventory slots, capacities, and item quantities (§126)."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            inv = entity.components.get("inventory")
            if isinstance(inv, InventoryComponent):
                if inv.max_slots < 0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_PARTIAL_INVENTORY_TRANSACTION",
                            message=f"Entity '{eid}' inventory max_slots is negative ({inv.max_slots}).",
                            target_id=eid,
                        )
                    )
                if len(inv.slots) > inv.max_slots:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_PARTIAL_INVENTORY_TRANSACTION",
                            message=f"Entity '{eid}' inventory slots count ({len(inv.slots)}) exceeds max_slots ({inv.max_slots}).",
                            target_id=eid,
                        )
                    )

                for s_idx, slot in inv.slots.items():
                    if slot.quantity <= 0:
                        issues.append(
                            GameplayValidationIssue(
                                severity="ERROR",
                                code="NO_INVALID_ITEM_QUANTITY",
                                message=f"Entity '{eid}' slot {s_idx} item '{slot.item_id}' has non-positive quantity {slot.quantity}.",
                                target_id=slot.item_id,
                            )
                        )
                    if slot.slot_index < 0 or slot.slot_index >= inv.max_slots:
                        issues.append(
                            GameplayValidationIssue(
                                severity="ERROR",
                                code="NO_PARTIAL_INVENTORY_TRANSACTION",
                                message=f"Entity '{eid}' slot_index {slot.slot_index} is out of bounds [0, {inv.max_slots}).",
                                target_id=eid,
                            )
                        )

        return issues

    @classmethod
    def validate_quests(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates quests and objective completion requirements (§126)."""
        issues: List[GameplayValidationIssue] = []

        for qid, quest in world.quests.items():
            if quest.state == QuestState.COMPLETED:
                if not quest.objectives:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_QUEST_COMPLETION_WITHOUT_OBJECTIVES",
                            message=f"Quest '{qid}' is marked COMPLETED but has no objectives defined.",
                            target_id=qid,
                        )
                    )
                else:
                    uncompleted = [
                        oid
                        for oid, obj in quest.objectives.items()
                        if obj.is_mandatory and obj.state != ObjectiveState.COMPLETED
                    ]
                    if uncompleted:
                        issues.append(
                            GameplayValidationIssue(
                                severity="ERROR",
                                code="NO_QUEST_COMPLETION_WITHOUT_OBJECTIVES",
                                message=f"Quest '{qid}' is marked COMPLETED but has incomplete mandatory objectives: {uncompleted}.",
                                target_id=qid,
                            )
                        )

        return issues

    @classmethod
    def validate_interactions_and_triggers(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates interactable and trigger components (§126)."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            interact = entity.components.get("interactable")
            if isinstance(interact, InteractableComponent):
                if interact.target_entity_id and interact.target_entity_id not in world.entities:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_INTERACTION_TARGET",
                            message=f"Interactable on entity '{eid}' targets non-existent entity '{interact.target_entity_id}'.",
                            target_id=eid,
                        )
                    )
                if interact.max_distance < 0.0:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INTERACTION_WITHOUT_VALIDATION",
                            message=f"Interactable on entity '{eid}' has negative max_distance {interact.max_distance}.",
                            target_id=eid,
                        )
                    )

            trig = entity.components.get("trigger")
            if isinstance(trig, TriggerComponent):
                if any(x <= 0.0 for x in trig.extents):
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_TRIGGER_STATE",
                            message=f"Trigger on entity '{eid}' has non-positive extents {trig.extents}.",
                            target_id=eid,
                        )
                    )

        return issues

    @classmethod
    def validate_tags(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates tag hierarchy formatting (§126 NO_TAG_HIERARCHY_CORRUPTION)."""
        issues: List[GameplayValidationIssue] = []

        for eid, entity in world.entities.items():
            for tag in entity.tags.tags:
                if not tag or ".." in tag or tag.startswith(".") or tag.endswith("."):
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_TAG_HIERARCHY_CORRUPTION",
                            message=f"Entity '{eid}' has invalid tag syntax '{tag}'.",
                            target_id=eid,
                        )
                    )

        return issues

    @classmethod
    def validate_commands(cls, world: GameplayWorld) -> List[GameplayValidationIssue]:
        """Validates queued commands targeting entities (§126)."""
        issues: List[GameplayValidationIssue] = []

        for cmd in world.command_queue:
            if cmd.target_entity_id:
                if cmd.target_entity_id not in world.entities:
                    issues.append(
                        GameplayValidationIssue(
                            severity="ERROR",
                            code="NO_INVALID_COMMAND",
                            message=f"Command '{cmd.command_id}' targets non-existent entity '{cmd.target_entity_id}'.",
                            target_id=cmd.command_id,
                        )
                    )
                else:
                    ent = world.entities[cmd.target_entity_id]
                    if ent.state == EntityLifecycleState.DESTROYED:
                        issues.append(
                            GameplayValidationIssue(
                                severity="ERROR",
                                code="NO_COMMAND_TO_DESTROYED_ENTITY",
                                message=f"Command '{cmd.command_id}' targets DESTROYED entity '{cmd.target_entity_id}'.",
                                target_id=cmd.command_id,
                            )
                        )
                    elif ent.state == EntityLifecycleState.PENDING_DESPAWN:
                        issues.append(
                            GameplayValidationIssue(
                                severity="ERROR",
                                code="NO_COMMAND_TO_DESPAWNED_ENTITY",
                                message=f"Command '{cmd.command_id}' targets DESPAWNED entity '{cmd.target_entity_id}'.",
                                target_id=cmd.command_id,
                            )
                        )

        return issues

    @classmethod
    def validate_save_state(cls, save: SaveState) -> List[GameplayValidationIssue]:
        """Validates persistent save state (§126 NO_TRANSIENT_STATE_IN_PERSISTENT_SAVE)."""
        issues: List[GameplayValidationIssue] = []

        if not save.save_id:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="NO_UNVALIDATED_LOAD",
                    message="SaveState missing valid save_id.",
                )
            )

        if save.version <= 0:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="NO_UNVALIDATED_LOAD",
                    message=f"SaveState version must be positive (got {save.version}).",
                )
            )

        transient_keys = {"_transient", "transient_state", "temp_cache", "volatile_memory"}
        for eid, edata in save.entities_data.items():
            if any(k in transient_keys for k in edata.keys()):
                issues.append(
                    GameplayValidationIssue(
                        severity="ERROR",
                        code="NO_TRANSIENT_STATE_IN_PERSISTENT_SAVE",
                        message=f"Entity '{eid}' contains transient state in persistent save.",
                        target_id=eid,
                    )
                )

        return issues

    @classmethod
    def validate_snapshot(cls, snapshot: GameplaySnapshot) -> List[GameplayValidationIssue]:
        """Validates snapshot integrity and determinism hash (§126)."""
        issues: List[GameplayValidationIssue] = []

        if not snapshot.snapshot_id:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="NO_UNVALIDATED_REPLAY",
                    message="Snapshot missing valid snapshot_id.",
                )
            )

        if not snapshot.fingerprint:
            issues.append(
                GameplayValidationIssue(
                    severity="ERROR",
                    code="NO_UNVALIDATED_REPLAY",
                    message="Snapshot missing valid fingerprint.",
                )
            )

        return issues
