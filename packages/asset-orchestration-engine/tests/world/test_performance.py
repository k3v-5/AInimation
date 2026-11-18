"""
Tests for World Performance, Budgets & Diagnostics (UAF-81.56 Section 206).
"""

import pytest
from uaf.universal_world import (
    MemoryBudget,
    InstanceBudget,
    TriangleBudget,
    StreamingBudget,
    WorldPerformanceReport,
    WorldDiagnosticReport,
)


def test_generation_budget():
    rep = WorldPerformanceReport(generation_time_ms=120.5)
    assert rep.generation_time_ms < 5000.0  # Must be well within budget


def test_instance_budget():
    budget = InstanceBudget(vegetation=50000, rocks=10000)
    assert budget.vegetation == 50000
    assert budget.rocks == 10000


def test_triangle_budget():
    budget = TriangleBudget(terrain=2000000, structures=1000000)
    assert budget.terrain == 2000000


def test_memory_budget():
    mem = MemoryBudget(max_memory_mb=2048.0)
    assert mem.max_memory_mb == 2048.0


def test_streaming_budget():
    sb = StreamingBudget(load_cost_ms=3.0, unload_cost_ms=1.5)
    assert sb.load_cost_ms <= 5.0


def test_navigation_budget():
    mem = MemoryBudget(max_navigation_memory_mb=128.0)
    assert mem.max_navigation_memory_mb == 128.0


def test_hlod_budget():
    budget = TriangleBudget(hlod=800000)
    assert budget.hlod == 800000
