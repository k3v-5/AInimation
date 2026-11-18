"""
Tests for Status Effects and Over-Time Mechanics (UAF-81.58 Sections 141-150, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    EffectType,
    StatusEffectInstance,
    EntityType,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_effect_type_enum():
    types = {e.value for e in EffectType}
    expected = {
        "BUFF",
        "DEBUFF",
        "DAMAGE_OVER_TIME",
        "HEAL_OVER_TIME",
        "CROWD_CONTROL",
        "STAT_BOOST",
        "IMMUNITY",
        "CUSTOM",
    }
    assert types == expected


def test_status_effect_instance_creation():
    eff = StatusEffectInstance(
        effect_id="eff_burn",
        name="Burning",
        effect_type=EffectType.DAMAGE_OVER_TIME,
        duration=6.0,
        remaining_duration=6.0,
        tick_interval=1.0,
        magnitude=10.0,
    )
    assert eff.effect_id == "eff_burn"
    assert eff.name == "Burning"
    assert eff.effect_type == EffectType.DAMAGE_OVER_TIME
    assert eff.duration == 6.0
    assert eff.magnitude == 10.0
    assert not eff.is_expired()


def test_status_effect_expiration_predicate():
    eff = StatusEffectInstance(
        effect_id="eff_slow",
        name="Slow",
        effect_type=EffectType.DEBUFF,
        duration=3.0,
        remaining_duration=0.0,
    )
    assert eff.is_expired()

    eff.remaining_duration = -1.5
    assert eff.is_expired()

    eff.remaining_duration = 0.5
    assert not eff.is_expired()


def test_status_effect_damage_over_time_tick():
    state = GameplayState("SIM_EFFECTS")
    target = UniversalGameplayFabricator.spawn_entity("TARGET", EntityType.NPC)
    target.health = 100.0
    target.max_health = 100.0
    state.entities[target.entity_id] = target

    poison = StatusEffectInstance(
        effect_id="poison_1",
        name="Poison",
        effect_type=EffectType.DAMAGE_OVER_TIME,
        duration=5.0,
        remaining_duration=5.0,
        tick_interval=1.0,
        magnitude=15.0,
    )
    target.active_effects.append(poison)

    # Advance 1.0s (1 tick of 1.0s)
    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert target.health == 85.0
    assert poison.remaining_duration == 4.0


def test_status_effect_heal_over_time_tick():
    state = GameplayState("SIM_EFFECTS")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.health = 50.0
    player.max_health = 100.0
    state.entities[player.entity_id] = player

    regen = StatusEffectInstance(
        effect_id="regen_1",
        name="Regeneration",
        effect_type=EffectType.HEAL_OVER_TIME,
        duration=10.0,
        remaining_duration=10.0,
        tick_interval=1.0,
        magnitude=20.0,
    )
    player.active_effects.append(regen)

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert player.health == 70.0


def test_status_effect_health_clamping_to_zero():
    state = GameplayState("SIM_EFFECTS")
    target = UniversalGameplayFabricator.spawn_entity("TARGET", EntityType.NPC)
    target.health = 5.0
    state.entities[target.entity_id] = target

    dot = StatusEffectInstance(
        effect_id="bleed_lethal",
        name="Lethal Bleed",
        effect_type=EffectType.DAMAGE_OVER_TIME,
        duration=2.0,
        remaining_duration=2.0,
        tick_interval=1.0,
        magnitude=25.0,
    )
    target.active_effects.append(dot)

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert target.health == 0.0


def test_status_effect_health_clamping_to_max():
    state = GameplayState("SIM_EFFECTS")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.health = 95.0
    player.max_health = 100.0
    state.entities[player.entity_id] = player

    hot = StatusEffectInstance(
        effect_id="hot_overflow",
        name="Overflow Heal",
        effect_type=EffectType.HEAL_OVER_TIME,
        duration=2.0,
        remaining_duration=2.0,
        tick_interval=1.0,
        magnitude=50.0,
    )
    player.active_effects.append(hot)

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert player.health == 100.0


def test_status_effect_automatic_removal_on_expiry():
    state = GameplayState("SIM_EFFECTS")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    short_buff = StatusEffectInstance(
        effect_id="buff_short",
        name="Sprint",
        effect_type=EffectType.BUFF,
        duration=0.5,
        remaining_duration=0.5,
    )
    player.active_effects.append(short_buff)

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    assert len(player.active_effects) == 0


def test_status_effect_multiple_simultaneous():
    state = GameplayState("SIM_EFFECTS")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.health = 50.0
    player.max_health = 100.0
    state.entities[player.entity_id] = player

    hot = StatusEffectInstance("hot", "Regen", EffectType.HEAL_OVER_TIME, 5.0, 5.0, tick_interval=1.0, magnitude=15.0)
    dot = StatusEffectInstance("dot", "Burn", EffectType.DAMAGE_OVER_TIME, 5.0, 5.0, tick_interval=1.0, magnitude=5.0)
    player.active_effects.extend([hot, dot])

    UniversalGameplayFabricator.advance_simulation_tick(state, dt=1.0)
    # Net: 50 + 15 - 5 = 60
    assert player.health == 60.0
    assert len(player.active_effects) == 2
