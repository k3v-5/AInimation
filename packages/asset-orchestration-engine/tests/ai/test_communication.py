"""
Tests for Communication & Messaging System (UAF-81.57 Sections 96-100, 226).
"""

import pytest
from uaf.universal_ai import (
    AICommunicationType,
    AICommunicationMessage,
)


def test_communication_type_enum():
    types = {t.value for t in AICommunicationType}
    expected = {"SPEECH", "SIGNAL", "RADIO", "GESTURE", "ALERT", "CUSTOM"}
    assert types == expected


def test_communication_message_creation():
    msg = AICommunicationMessage(
        message_id="MSG_001",
        source="GUARD_1",
        target="GUARD_2",
        channel=AICommunicationType.SPEECH,
        payload={"text": "Halt! Who goes there?"},
        priority=2,
        timestamp=5.0,
    )
    assert msg.message_id == "MSG_001"
    assert msg.source == "GUARD_1"
    assert msg.target == "GUARD_2"
    assert msg.channel == AICommunicationType.SPEECH
    assert msg.payload["text"] == "Halt! Who goes there?"
    assert msg.priority == 2
    assert msg.timestamp == 5.0


def test_communication_broadcast_message():
    broadcast = AICommunicationMessage(
        message_id="BCAST_01",
        source="COMMANDER",
        target="*",
        channel=AICommunicationType.RADIO,
        payload={"order": "FALL_BACK"},
    )
    assert broadcast.target == "*"
    assert broadcast.channel == AICommunicationType.RADIO


def test_communication_radio_long_range():
    msg = AICommunicationMessage(
        message_id="RADIO_ALERT",
        source="OUTPOST_ALPHA",
        target="BASE_HQ",
        channel=AICommunicationType.RADIO,
        payload={"threat_loc": [12000.0, 4500.0, 0.0], "threat_count": 5},
    )
    assert msg.payload["threat_count"] == 5
    assert msg.channel == AICommunicationType.RADIO


def test_communication_speech_proximity_filter():
    max_speech_range = 1000.0
    sender_pos = (0.0, 0.0, 0.0)
    listeners = [
        ("NEAR_AGENT", (500.0, 0.0, 0.0)),
        ("FAR_AGENT", (1500.0, 0.0, 0.0)),
    ]

    def can_hear(pos):
        d = ((pos[0] - sender_pos[0])**2 + (pos[1] - sender_pos[1])**2)**0.5
        return d <= max_speech_range

    recipients = [lid for lid, pos in listeners if can_hear(pos)]
    assert recipients == ["NEAR_AGENT"]


def test_communication_priority_dispatch():
    msgs = [
        AICommunicationMessage("M1", "A", "B", priority=1),
        AICommunicationMessage("M2", "A", "B", priority=10),
        AICommunicationMessage("M3", "A", "B", priority=5),
    ]
    sorted_msgs = sorted(msgs, key=lambda m: m.priority, reverse=True)
    assert [m.message_id for m in sorted_msgs] == ["M2", "M3", "M1"]


def test_communication_alert_signal():
    alert = AICommunicationMessage(
        message_id="ALARM_HORN",
        source="WATCHTOWER",
        target="FACTION_ALLIES",
        channel=AICommunicationType.ALERT,
        payload={"alarm_level": "RED"},
    )
    assert alert.channel == AICommunicationType.ALERT
    assert alert.payload["alarm_level"] == "RED"
