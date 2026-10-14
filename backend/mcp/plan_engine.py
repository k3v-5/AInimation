"""
Human-in-the-Loop Production Plan Engine for IANIMATION.

Generates structured production plans, manages confirmation gates,
and orchestrates safe approval workflows for heavy generation and render tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.core.models import (
    LogLevel,
    PlanProposalEvent,
    PlanRiskLevel,
    PlanStatus,
    PlanStep,
    ProductionPlan,
    ProgressEvent,
    LogEvent,
)
from backend.core.telemetry import TelemetryBus, get_telemetry_bus


class PlanEngine:
    """
    Manages production plan generation, step confirmation gates, and telemetry updates.
    """

    def __init__(self, telemetry_bus: Optional[TelemetryBus] = None) -> None:
        self.telemetry_bus: TelemetryBus = telemetry_bus or get_telemetry_bus()
        self._plans: Dict[str, ProductionPlan] = {}

    def create_plan(
        self,
        goal: str,
        audio_path: str = "",
        image_path: str = "",
        video_path: str = "",
        style: str = "cyberpunk",
    ) -> ProductionPlan:
        """
        Generate an ordered production plan broken down into atomic tool steps.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        steps: List[PlanStep] = [
            PlanStep(
                step_id=f"{plan_id}_step_1_audio",
                index=0,
                tool_name="analyze_audio",
                title="Audio Rhythm Analysis",
                description="Extract BPM tempo, beats, and energy onsets for camera/light synchronization",
                parameters={"audio_path": audio_path},
                risk_level=PlanRiskLevel.LOW,
                requires_confirmation=False,
                status=PlanStatus.PROPOSED,
            ),
            PlanStep(
                step_id=f"{plan_id}_step_2_mesh",
                index=1,
                tool_name="image_to_3d",
                title="3D Character Generation",
                description="Generate 3D textured mesh with PBR maps from concept image",
                parameters={"image_path": image_path, "provider": "auto"},
                risk_level=PlanRiskLevel.MEDIUM,
                requires_confirmation=True,
                status=PlanStatus.PROPOSED,
            ),
            PlanStep(
                step_id=f"{plan_id}_step_3_rig",
                index=2,
                tool_name="auto_rig",
                title="Skeletal Rigging",
                description="Bind 3D character mesh with standard UE5 mannequin armature",
                parameters={"skeleton_type": "ue5_mannequin"},
                risk_level=PlanRiskLevel.LOW,
                requires_confirmation=False,
                status=PlanStatus.PROPOSED,
            ),
            PlanStep(
                step_id=f"{plan_id}_step_4_scene",
                index=3,
                tool_name="build_ue5_scene",
                title="UE5 Scene Assembly",
                description="Set up Lumen lighting rig, CineCamera trajectory, and spawn character",
                parameters={"style": style},
                risk_level=PlanRiskLevel.LOW,
                requires_confirmation=False,
                status=PlanStatus.PROPOSED,
            ),
            PlanStep(
                step_id=f"{plan_id}_step_5_render",
                index=4,
                tool_name="render_video",
                title="Cinematic Movie Render",
                description="Render final 60 FPS video using Unreal Movie Render Queue and ComfyUI",
                parameters={"resolution": "1920x1080", "fps": "60"},
                risk_level=PlanRiskLevel.HIGH,
                requires_confirmation=True,
                status=PlanStatus.PROPOSED,
            ),
        ]

        plan = ProductionPlan(
            plan_id=plan_id,
            title=f"Production Plan: {goal}",
            description=f"Automated end-to-end plan targeting goal '{goal}' with {len(steps)} steps.",
            steps=steps,
            status=PlanStatus.PROPOSED,
            total_estimated_duration_seconds=30.0,
        )
        self._plans[plan_id] = plan

        self.telemetry_bus.emit_threadsafe(
            PlanProposalEvent(
                plan_id=plan_id,
                steps=steps,
                status=PlanStatus.PROPOSED,
            )
        )
        return plan

    def get_plan(self, plan_id: str) -> Optional[ProductionPlan]:
        """Retrieve existing plan by ID."""
        return self._plans.get(plan_id)

    def confirm_step(self, plan_id: str, step_id: str, approved: bool = True) -> ProductionPlan:
        """
        Human approval gate for an individual plan step.
        """
        plan = self._plans.get(plan_id)
        if not plan:
            raise KeyError(f"Production plan '{plan_id}' not found")

        step = plan.get_step(step_id)
        if not step:
            raise KeyError(f"Step '{step_id}' not found in plan '{plan_id}'")

        if approved:
            step.status = PlanStatus.APPROVED
            self.telemetry_bus.emit_threadsafe(
                ProgressEvent(
                    stage=step.tool_name,
                    percentage=100.0,
                    message=f"Step '{step_id}' approved by user",
                    plan_id=plan_id,
                    step_id=step_id,
                    tool_name=step.tool_name,
                )
            )
            # Promote plan to APPROVED when all steps are approved
            if plan.status != PlanStatus.REJECTED and all(s.status == PlanStatus.APPROVED for s in plan.steps):
                plan.status = PlanStatus.APPROVED
                self.telemetry_bus.emit_threadsafe(
                    PlanProposalEvent(
                        plan_id=plan_id,
                        steps=plan.steps,
                        status=PlanStatus.APPROVED,
                    )
                )
        else:
            step.status = PlanStatus.REJECTED
            plan.status = PlanStatus.REJECTED
            self.telemetry_bus.emit_threadsafe(
                LogEvent(
                    level=LogLevel.ERROR,
                    message=f"Step '{step_id}' rejected by user. Plan halted.",
                    source="PlanEngine",
                )
            )

        plan.updated_at = datetime.now(timezone.utc).isoformat()
        return plan

    def reject_step(self, plan_id: str, step_id: str) -> ProductionPlan:
        """Explicit rejection shorthand."""
        return self.confirm_step(plan_id=plan_id, step_id=step_id, approved=False)
