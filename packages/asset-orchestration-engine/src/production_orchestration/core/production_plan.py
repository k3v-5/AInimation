import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class ProductionPlan:
    plan_id: str
    job_id: str
    asset_semantic_id: str
    items_to_create: List[str] = field(default_factory=list)
    items_to_modify: List[str] = field(default_factory=list)
    participating_agents: List[str] = field(default_factory=lambda: [
        "agent.perception", "agent.strategy", "agent.geometry",
        "agent.material", "agent.critic", "agent.optimizer", "agent.packaging"
    ])
    required_capabilities: List[str] = field(default_factory=lambda: [
        "CAP_GEOMETRY", "CAP_MATERIAL", "CAP_BLENDER", "CAP_EVALUATION", "CAP_PACKAGING"
    ])
    target_files: List[str] = field(default_factory=list)
    required_resources: List[str] = field(default_factory=lambda: ["BlenderSession", "WorkspaceStorage"])
    validations_to_run: List[str] = field(default_factory=lambda: ["STRUCTURAL_QA", "VISUAL_QA", "UNREAL_READINESS"])
    benchmark_to_use: str = "BENCHMARK_HERO_WEAPON_V1"
    baseline_to_use: Optional[str] = None
    budget: Dict[str, Any] = field(default_factory=lambda: {
        "max_time_sec": 180.0,
        "max_corrections": 3,
        "polygon_budget": 20000
    })
    rejection_conditions: List[str] = field(default_factory=lambda: [
        "Quality score < 0.90", "Golden regression > 0.02", "Unapplied transforms"
    ])
    acceptance_conditions: List[str] = field(default_factory=lambda: [
        "F75 Benchmark APPROVED", "F76 Golden Non-Regressive", "Unreal readiness verified"
    ])
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "job_id": self.job_id,
            "asset_semantic_id": self.asset_semantic_id,
            "items_to_create": self.items_to_create,
            "items_to_modify": self.items_to_modify,
            "participating_agents": self.participating_agents,
            "required_capabilities": self.required_capabilities,
            "target_files": self.target_files,
            "required_resources": self.required_resources,
            "validations_to_run": self.validations_to_run,
            "benchmark_to_use": self.benchmark_to_use,
            "baseline_to_use": self.baseline_to_use,
            "budget": self.budget,
            "rejection_conditions": self.rejection_conditions,
            "acceptance_conditions": self.acceptance_conditions,
            "created_at": self.created_at
        }
