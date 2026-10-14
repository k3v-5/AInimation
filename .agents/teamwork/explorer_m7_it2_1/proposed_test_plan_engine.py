"""
Unit tests for Production Plan Engine (HITL gates, risk grading, and state machine lifecycle).
Conforms 100% to Zero-Any strict typing and SOLID architecture.
"""
from __future__ import annotations

import pytest
from typing import Dict, List

from backend.mcp.plan_engine import PlanEngine
from backend.core.models import (
    PlanRiskLevel,
    PlanStatus,
    ProductionPlan,
    PlanProposalEvent,
    ProgressEvent,
    LogEvent,
)
from backend.core.telemetry import TelemetryBus


class TestPlanEngine:
    def test_create_plan_structure(self) -> None:
        engine = PlanEngine()
        plan = engine.create_plan(
            goal="Create Cyberpunk Music Video",
            audio_path="music.wav",
            image_path="hero.png",
            video_path="dance.mp4",
        )
        assert isinstance(plan, ProductionPlan)
        assert len(plan.steps) == 5
        assert plan.status == PlanStatus.PROPOSED
        assert plan.steps[0].tool_name == "analyze_audio"
        assert plan.steps[0].risk_level == PlanRiskLevel.LOW
        assert plan.steps[1].tool_name == "image_to_3d"
        assert plan.steps[1].risk_level == PlanRiskLevel.MEDIUM
        assert plan.steps[4].tool_name == "render_video"
        assert plan.steps[4].risk_level == PlanRiskLevel.HIGH

    def test_confirm_individual_step(self) -> None:
        engine = PlanEngine()
        plan = engine.create_plan(goal="Single Step Approval")
        step_id = plan.steps[1].step_id

        updated = engine.confirm_step(plan.plan_id, step_id, approved=True)
        assert updated.get_step(step_id).status == PlanStatus.APPROVED

    def test_reject_step_halts_plan(self) -> None:
        engine = PlanEngine()
        plan = engine.create_plan(goal="Rejection Test")
        step_id = plan.steps[0].step_id

        updated = engine.confirm_step(plan.plan_id, step_id, approved=False)
        assert updated.get_step(step_id).status == PlanStatus.REJECTED
        assert updated.status == PlanStatus.REJECTED

    def test_full_approval_promotes_plan(self) -> None:
        engine = PlanEngine()
        plan = engine.create_plan(goal="Promote Plan")
        for step in plan.steps:
            engine.confirm_step(plan.plan_id, step.step_id, approved=True)

        assert plan.status == PlanStatus.APPROVED
        assert all(s.status == PlanStatus.APPROVED for s in plan.steps)
