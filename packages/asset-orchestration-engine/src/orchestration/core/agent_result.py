from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .agent_state import TaskStatus

@dataclass
class AssetMutation:
    asset_id: str
    semantic_id: str
    operation: str
    created_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    deleted_entities: List[str] = field(default_factory=list)
    materials_modified: List[str] = field(default_factory=list)
    timestamp: float = 0.0

@dataclass
class AgentResult:
    success: bool
    status: TaskStatus
    agent_id: str
    agent_version: str
    task_id: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    mutations: List[AssetMutation] = field(default_factory=list)
    checkpoint_id: Optional[str] = None
    execution_time: float = 0.0
