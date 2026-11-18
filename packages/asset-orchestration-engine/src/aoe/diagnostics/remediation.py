"""Autonomous remediation planning and mitigation generation."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List
from uaf.runtime_diagnostics.core import SubsystemType
from aoe.diagnostics.root_cause import RootCauseHypothesis


@dataclass
class RemediationAction:
    action_id: str
    title: str
    description: str
    target_subsystem: SubsystemType
    automated_applicable: bool
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "target_subsystem": self.target_subsystem.value,
            "automated_applicable": self.automated_applicable,
            "parameters": self.parameters,
        }


class RemediationPlanner:
    """Generates concrete remediation actions from root cause hypotheses."""

    def generate_remediation(self, hypothesis: RootCauseHypothesis) -> RemediationAction:
        subsys = hypothesis.offending_subsystem
        cat = hypothesis.recommended_action_category

        if "vfx" in cat or subsys == SubsystemType.VFX:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Scale Down VFX Particle Capacity",
                description="Reduce maximum active particles and throttle continuous emitters.",
                target_subsystem=SubsystemType.VFX,
                automated_applicable=True,
                parameters={"max_particles_scale": 0.5, "cull_distant_emitters": True},
            )

        elif "physics" in cat or subsys == SubsystemType.PHYSICS:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Increase Physics Sub-stepping / Clamp Max Collisions",
                description="Clamp maximum contact constraints per tick and enable sleeping for static bodies.",
                target_subsystem=SubsystemType.PHYSICS,
                automated_applicable=True,
                parameters={"max_solver_iterations": 8, "enable_aggressive_sleeping": True},
            )

        elif "ai" in cat or subsys == SubsystemType.AI:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Throttle AI Pathfinding Requests & Time-Slice Navigation",
                description="Enqueue pathfinding requests with maximum budget of 2ms per tick.",
                target_subsystem=SubsystemType.AI,
                automated_applicable=True,
                parameters={"max_pathfinding_ms_per_frame": 2.0, "rvo_sample_reduction": 0.5},
            )

        elif "render" in cat or subsys == SubsystemType.RENDERING:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Increase Render Dynamic LOD Aggressiveness",
                description="Force lower mesh LODs and disable shadow cascades on secondary lights.",
                target_subsystem=SubsystemType.RENDERING,
                automated_applicable=True,
                parameters={"lod_bias": 1.0, "disable_contact_shadows": True},
            )

        elif "deterministic" in cat or "fixed_point" in cat:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Canonical Fixed-Point Quantization Enforcement",
                description="Quantize transform and velocity state vectors to fixed-precision canonical formats.",
                target_subsystem=subsys,
                automated_applicable=True,
                parameters={"precision_decimals": 4, "sort_entity_iteration_keys": True},
            )

        elif "memory" in cat:
            return RemediationAction(
                action_id=f"rem_{uuid.uuid4().hex[:10]}",
                title="Trigger Force Resource Garbage Collection & Flush Pools",
                description="Purge unused memory pools, trim ring buffer capacities, and destroy unreferenced assets.",
                target_subsystem=subsys,
                automated_applicable=True,
                parameters={"force_pool_trim": True, "gc_generation": 2},
            )

        # Default fallback
        return RemediationAction(
            action_id=f"rem_{uuid.uuid4().hex[:10]}",
            title=f"Subsystem Degradation: {subsys.value}",
            description=f"Apply level 1 degradation profile to {subsys.value}.",
            target_subsystem=subsys,
            automated_applicable=True,
            parameters={"degradation_tier": 1},
        )

    def plan_remediations(self, hypotheses: List[RootCauseHypothesis]) -> List[RemediationAction]:
        return [self.generate_remediation(h) for h in hypotheses]
