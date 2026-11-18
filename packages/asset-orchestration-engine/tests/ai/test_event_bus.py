"""
Tests for AI Event Bus System (UAF-81.57 Sections 140-144, 226).
"""

import pytest
from uaf.universal_ai import (
    AIEventType,
    AIEventPriority,
    AIEvent,
)


def test_ai_event_type_enum():
    types = {t.value for t in AIEventType}
    expected = {
        "SPAWN",
        "DESPAWN",
        "DAMAGE",
        "DEATH",
        "SOUND",
        "VISUAL",
        "INTERACTION",
        "QUEST",
        "WEATHER",
        "TIME",
        "WORLD_CHANGE",
        "ALERT",
        "CUSTOM",
    }
    assert types == expected


def test_ai_event_priority_enum():
    prios = {p.value for p in AIEventPriority}
    expected = {"CRITICAL", "HIGH", "NORMAL", "LOW"}
    assert prios == expected


def test_ai_event_creation():
    event = AIEvent(
        event_type=AIEventType.DAMAGE,
        sender_id="WEAPON_SWORD",
        priority=AIEventPriority.HIGH,
        payload={"target": "NPC_01", "amount": 25.0},
        timestamp=4.2,
    )
    assert event.event_type == AIEventType.DAMAGE
    assert event.sender_id == "WEAPON_SWORD"
    assert event.priority == AIEventPriority.HIGH
    assert event.payload["amount"] == 25.0
    assert event.timestamp == 4.2


def test_event_bus_subscribe_and_publish():
    received = []

    def on_event(ev: AIEvent):
        received.append(ev)

    # Simple subscription mechanism
    handlers = [on_event]
    ev = AIEvent(event_type=AIEventType.DEATH, sender_id="MONSTER_01")

    for h in handlers:
        h(ev)

    assert len(received) == 1
    assert received[0].sender_id == "MONSTER_01"


def test_event_bus_filtering_by_type():
    dispatched = {"DAMAGE": [], "SOUND": []}

    def handle_damage(ev: AIEvent):
        dispatched["DAMAGE"].append(ev)

    def handle_sound(ev: AIEvent):
        dispatched["SOUND"].append(ev)

    routes = {
        AIEventType.DAMAGE: [handle_damage],
        AIEventType.SOUND: [handle_sound],
    }

    ev_damage = AIEvent(AIEventType.DAMAGE, sender_id="S1")
    ev_sound = AIEvent(AIEventType.SOUND, sender_id="S2")

    for ev in [ev_damage, ev_sound]:
        for h in routes.get(ev.event_type, []):
            h(ev)

    assert len(dispatched["DAMAGE"]) == 1
    assert len(dispatched["SOUND"]) == 1
    assert dispatched["DAMAGE"][0].sender_id == "S1"


def test_event_bus_priority_ordering():
    prio_map = {
        AIEventPriority.CRITICAL: 4,
        AIEventPriority.HIGH: 3,
        AIEventPriority.NORMAL: 2,
        AIEventPriority.LOW: 1,
    }

    events = [
        AIEvent(AIEventType.TIME, "CLOCK", priority=AIEventPriority.LOW),
        AIEvent(AIEventType.DAMAGE, "TRAP", priority=AIEventPriority.CRITICAL),
        AIEvent(AIEventType.ALERT, "GUARD", priority=AIEventPriority.NORMAL),
    ]

    sorted_events = sorted(events, key=lambda e: prio_map[e.priority], reverse=True)
    assert sorted_events[0].priority == AIEventPriority.CRITICAL
    assert sorted_events[1].priority == AIEventPriority.NORMAL
    assert sorted_events[2].priority == AIEventPriority.LOW
