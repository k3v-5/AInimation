import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class FailureContext:
    job_id: Optional[str] = None
    worker_id: str = "worker_default"
    agent_id: str = "agent.visual.critic"
    contract_id: str = "contract.critic.v2"
    capability: str = "CAP_GEOMETRY"
    tool: str = "BlenderTool"
    pipeline_phase: str = "PHASE_77"
    pipeline_stage: str = "EXECUTION"
    semantic_id: str = "asset.default"
    asset_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    affected_objects: List[str] = field(default_factory=list)
    affected_materials: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    resource_locks: List[str] = field(default_factory=list)
    input_params: Dict[str, Any] = field(default_factory=dict)
    visual_reference: Optional[str] = None
    previous_benchmark: Optional[str] = None
    golden_asset_id: Optional[str] = None
    blender_state: Dict[str, Any] = field(default_factory=dict)
    blender_version: str = "4.2.0"
    aoe_version: str = "2.0.0"
    last_event: str = "START_OPERATION"
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "agent_id": self.agent_id,
            "contract_id": self.contract_id,
            "capability": self.capability,
            "tool": self.tool,
            "pipeline_phase": self.pipeline_phase,
            "pipeline_stage": self.pipeline_stage,
            "semantic_id": self.semantic_id,
            "asset_id": self.asset_id,
            "checkpoint_id": self.checkpoint_id,
            "affected_objects": self.affected_objects,
            "affected_materials": self.affected_materials,
            "affected_files": self.affected_files,
            "resource_locks": self.resource_locks,
            "input_params": self.input_params,
            "visual_reference": self.visual_reference,
            "previous_benchmark": self.previous_benchmark,
            "golden_asset_id": self.golden_asset_id,
            "blender_state": self.blender_state,
            "blender_version": self.blender_version,
            "aoe_version": self.aoe_version,
            "last_event": self.last_event,
            "timestamp": self.timestamp
        }
