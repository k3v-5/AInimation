"""
Tests for AI Performance & Diagnostics System (UAF-81.57 Sections 162-167, 226).
"""

import pytest
from uaf.universal_ai import (
    AIPerformanceBudget,
    AIPerformanceReport,
    AIDiagnosticReport,
)


def test_performance_budget_defaults():
    budget = AIPerformanceBudget()
    assert budget.max_active_agents == 1000
    assert budget.max_full_agents == 100
    assert budget.max_tick_time_ms == 16.67


def test_performance_report_defaults():
    report = AIPerformanceReport()
    assert report.perception_time_ms == 0.0
    assert report.decision_time_ms == 0.0
    assert report.behavior_time_ms == 0.0
    assert report.pathfinding_time_ms == 0.0
    assert report.movement_time_ms == 0.0
    assert report.combat_time_ms == 0.0
    assert report.crowd_time_ms == 0.0
    assert report.total_tick_time_ms == 0.0


def test_performance_report_stage_aggregation():
    report = AIPerformanceReport(
        perception_time_ms=1.5,
        decision_time_ms=2.0,
        behavior_time_ms=1.2,
        pathfinding_time_ms=3.0,
        movement_time_ms=0.8,
        combat_time_ms=1.0,
        crowd_time_ms=1.5,
    )
    total = (
        report.perception_time_ms
        + report.decision_time_ms
        + report.behavior_time_ms
        + report.pathfinding_time_ms
        + report.movement_time_ms
        + report.combat_time_ms
        + report.crowd_time_ms
    )
    report.total_tick_time_ms = total
    assert round(report.total_tick_time_ms, 2) == 11.0


def test_diagnostic_report_defaults():
    diag = AIDiagnosticReport()
    assert diag.agent_count == 0
    assert diag.active_count == 0
    assert diag.path_failures == 0
    assert diag.deadlocks_detected == 0
    assert len(diag.errors) == 0
    assert len(diag.warnings) == 0


def test_diagnostic_report_errors_and_warnings():
    diag = AIDiagnosticReport(agent_count=50, active_count=48)
    diag.errors.append("Agent NPC_99 fallen out of world bounds")
    diag.warnings.append("High crowd density near Gate 3")

    assert len(diag.errors) == 1
    assert len(diag.warnings) == 1
    assert "NPC_99" in diag.errors[0]


def test_performance_budget_validation_within_limits():
    budget = AIPerformanceBudget(max_active_agents=500, max_tick_time_ms=16.67)
    diag = AIDiagnosticReport(active_count=400)
    perf = AIPerformanceReport(total_tick_time_ms=12.5)

    is_valid = (diag.active_count <= budget.max_active_agents) and (perf.total_tick_time_ms <= budget.max_tick_time_ms)
    assert is_valid is True


def test_performance_budget_validation_exceeded_agents():
    budget = AIPerformanceBudget(max_active_agents=100)
    diag = AIDiagnosticReport(active_count=150)
    assert diag.active_count > budget.max_active_agents


def test_performance_budget_validation_exceeded_tick_time():
    budget = AIPerformanceBudget(max_tick_time_ms=16.67)
    perf = AIPerformanceReport(total_tick_time_ms=25.0)
    assert perf.total_tick_time_ms > budget.max_tick_time_ms
