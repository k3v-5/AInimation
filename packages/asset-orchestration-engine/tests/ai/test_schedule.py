"""
Tests for Daily Schedule & Routine System (UAF-81.57 Sections 131-135, 226).
"""

import pytest
from uaf.universal_ai import (
    ScheduleEntry,
    DailySchedule,
)


def test_schedule_entry_creation():
    entry = ScheduleEntry(
        start_time=7.0,
        end_time=8.5,
        activity="EAT_BREAKFAST",
        location="TAVERN",
        priority=2,
    )
    assert entry.start_time == 7.0
    assert entry.end_time == 8.5
    assert entry.activity == "EAT_BREAKFAST"
    assert entry.location == "TAVERN"
    assert entry.priority == 2


def test_daily_schedule_creation():
    e1 = ScheduleEntry(start_time=6.0, end_time=7.0, activity="WAKE", location="HOUSE")
    e2 = ScheduleEntry(start_time=7.0, end_time=17.0, activity="WORK", location="BLACKSMITH")
    e3 = ScheduleEntry(start_time=17.0, end_time=22.0, activity="REST", location="TAVERN")
    e4 = ScheduleEntry(start_time=22.0, end_time=6.0, activity="SLEEP", location="HOUSE")

    sched = DailySchedule(schedule_id="SCHED_BLACKSMITH", entries=[e1, e2, e3, e4])
    assert sched.schedule_id == "SCHED_BLACKSMITH"
    assert len(sched.entries) == 4


def test_schedule_activity_lookup_morning():
    e_morning = ScheduleEntry(start_time=7.0, end_time=9.0, activity="BREAKFAST", location="HOME")
    sched = DailySchedule(schedule_id="S1", entries=[e_morning])

    hour = 8.0
    active = next((e for e in sched.entries if e.start_time <= hour < e.end_time), None)
    assert active is not None
    assert active.activity == "BREAKFAST"


def test_schedule_activity_lookup_work():
    e_work = ScheduleEntry(start_time=9.0, end_time=17.0, activity="MINE_ORE", location="MINE")
    sched = DailySchedule(schedule_id="S2", entries=[e_work])

    hour = 13.5
    active = next((e for e in sched.entries if e.start_time <= hour < e.end_time), None)
    assert active is not None
    assert active.activity == "MINE_ORE"


def test_schedule_activity_lookup_night():
    e_sleep = ScheduleEntry(start_time=21.0, end_time=24.0, activity="SLEEP", location="BED")
    sched = DailySchedule(schedule_id="S3", entries=[e_sleep])

    hour = 22.5
    active = next((e for e in sched.entries if e.start_time <= hour < e.end_time), None)
    assert active is not None
    assert active.activity == "SLEEP"


def test_schedule_entry_priority_resolution():
    # Regular schedule: work at blacksmith (prio 1)
    e_regular = ScheduleEntry(start_time=8.0, end_time=18.0, activity="WORK", location="SHOP", priority=1)
    # Festival event: parade in town square (prio 10)
    e_festival = ScheduleEntry(start_time=12.0, end_time=14.0, activity="FESTIVAL", location="SQUARE", priority=10)

    sched = DailySchedule(schedule_id="S_PRIO", entries=[e_regular, e_festival])

    hour = 13.0
    matching = [e for e in sched.entries if e.start_time <= hour < e.end_time]
    best_entry = max(matching, key=lambda e: e.priority)
    assert best_entry.activity == "FESTIVAL"


def test_schedule_wrap_around_midnight():
    # 22.0 to 6.0 overnight sleep
    e_overnight = ScheduleEntry(start_time=22.0, end_time=6.0, activity="OVERNIGHT_SLEEP", location="BED")

    def is_in_entry(entry: ScheduleEntry, t: float) -> bool:
        if entry.start_time <= entry.end_time:
            return entry.start_time <= t < entry.end_time
        else:
            return t >= entry.start_time or t < entry.end_time

    assert is_in_entry(e_overnight, 23.5) is True
    assert is_in_entry(e_overnight, 2.0) is True
    assert is_in_entry(e_overnight, 12.0) is False
