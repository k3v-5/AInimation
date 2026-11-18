"""
Tests for Memory System (UAF-81.57 Sections 34-40, 226).
"""

import pytest
from uaf.universal_ai import (
    MemoryType,
    MemoryRecord,
    AIMemory,
)


def test_memory_types_enum():
    types = {m.value for m in MemoryType}
    expected = {"SHORT_TERM", "LONG_TERM", "SPATIAL", "SOCIAL", "THREAT", "TASK", "EPISODIC", "CUSTOM"}
    assert types == expected


def test_memory_record_creation_and_expiration():
    record = MemoryRecord(
        memory_id="MEM_01",
        mem_type=MemoryType.THREAT,
        subject="ENEMY_01",
        location=(100.0, 200.0, 0.0),
        timestamp=10.0,
        expiration=5.0,
    )
    assert record.memory_id == "MEM_01"
    assert record.subject == "ENEMY_01"
    assert record.is_expired(12.0) is False
    assert record.is_expired(15.1) is True


def test_ai_memory_add_and_lookup():
    mem = AIMemory(capacity=10)
    r1 = MemoryRecord(memory_id="M1", mem_type=MemoryType.SHORT_TERM, subject="APPLE")
    r2 = MemoryRecord(memory_id="M2", mem_type=MemoryType.THREAT, subject="WOLF")

    mem.add_record(r1)
    mem.add_record(r2)

    assert len(mem.records) == 2
    threats = mem.get_records_by_type(MemoryType.THREAT)
    assert len(threats) == 1
    assert threats[0].subject == "WOLF"


def test_ai_memory_capacity_eviction():
    mem = AIMemory(capacity=3)
    r1 = MemoryRecord(memory_id="M1", importance=0.2, subject="TRIVIAL")
    r2 = MemoryRecord(memory_id="M2", importance=0.8, subject="IMPORTANT")
    r3 = MemoryRecord(memory_id="M3", importance=0.5, subject="MEDIUM")
    r4 = MemoryRecord(memory_id="M4", importance=0.9, subject="CRITICAL")

    mem.add_record(r1)
    mem.add_record(r2)
    mem.add_record(r3)
    assert len(mem.records) == 3

    # Adding M4 should evict M1 (lowest importance 0.2)
    mem.add_record(r4)
    assert len(mem.records) == 3
    assert "M1" not in mem.records
    assert "M2" in mem.records
    assert "M3" in mem.records
    assert "M4" in mem.records


def test_ai_memory_decay():
    mem = AIMemory()
    r1 = MemoryRecord(memory_id="M_OLD", timestamp=0.0, expiration=10.0)
    r2 = MemoryRecord(memory_id="M_NEW", timestamp=10.0, expiration=10.0)

    mem.add_record(r1)
    mem.add_record(r2)
    assert len(mem.records) == 2

    # Advance time to 15.0: r1 should decay, r2 should remain
    mem.decay_memories(current_time=15.0)
    assert len(mem.records) == 1
    assert "M_NEW" in mem.records
    assert "M_OLD" not in mem.records


def test_ai_memory_serialization():
    mem = AIMemory(capacity=50)
    rec = MemoryRecord(memory_id="M_REC", mem_type=MemoryType.SPATIAL, location=(10.0, 20.0, 0.0))
    mem.add_record(rec)

    data = mem.to_dict()
    assert data["capacity"] == 50
    assert data["record_count"] == 1
    assert data["records"][0]["memory_id"] == "M_REC"
    assert data["records"][0]["mem_type"] == "SPATIAL"


def test_ai_memory_type_filtering_empty():
    mem = AIMemory()
    r1 = MemoryRecord(memory_id="M1", mem_type=MemoryType.SHORT_TERM)
    mem.add_record(r1)

    social = mem.get_records_by_type(MemoryType.SOCIAL)
    assert len(social) == 0
