import time
import hashlib
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class ContextPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
    ARCHIVAL = "ARCHIVAL"

class ConflictStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    IGNORED = "IGNORED"

@dataclass
class GlobalContext:
    project_id: str = "DarX"
    project_name: str = "DarX Game Project"
    engine: str = "Unreal Engine 5.4"
    blender_version: str = "5.2.0"
    ue_version: str = "5.4.4"
    project_rules: List[str] = field(default_factory=list)
    asset_standards: Dict[str, Any] = field(default_factory=dict)
    directory_rules: Dict[str, str] = field(default_factory=dict)
    naming_rules: Dict[str, str] = field(default_factory=dict)

@dataclass
class AssetContext:
    semantic_id: str
    asset_type: str = "WEAPON"
    current_version: str = "1.0.0"
    status: str = "IN_PROGRESS"
    dependencies: List[str] = field(default_factory=list)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    geometry: Dict[str, Any] = field(default_factory=dict)
    collision: Dict[str, Any] = field(default_factory=dict)
    lods: List[Dict[str, Any]] = field(default_factory=list)
    export_settings: Dict[str, Any] = field(default_factory=dict)
    engine_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskContext:
    task_id: str
    objective: str
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    current_state: str = "PENDING"
    completed_steps: List[str] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)

@dataclass
class AgentContext:
    agent_id: str
    role: str
    permissions: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    known_facts: List[Dict[str, Any]] = field(default_factory=list)
    pending_actions: List[str] = field(default_factory=list)
    previous_actions: List[str] = field(default_factory=list)

@dataclass
class JobContext:
    job_id: str
    job_state: str = "RUNNING"
    current_checkpoint: Optional[str] = None
    completed_operations: List[str] = field(default_factory=list)
    failed_operations: List[str] = field(default_factory=list)
    retry_count: int = 0
    recovery_state: Optional[Dict[str, Any]] = None

@dataclass
class ContextPackage:
    package_id: str
    task_id: str
    agent_id: str
    required_context: Dict[str, Any] = field(default_factory=dict)
    optional_context: Dict[str, Any] = field(default_factory=dict)
    historical_context: List[Dict[str, Any]] = field(default_factory=list)
    priority: ContextPriority = ContextPriority.NORMAL
    assembled_at: float = field(default_factory=time.time)

@dataclass
class ContextConflict:
    conflict_id: str
    memory_a_id: str
    memory_b_id: str
    conflict_type: str
    severity: str = "HIGH"
    resolution_status: ConflictStatus = ConflictStatus.OPEN
    resolution_details: Optional[Dict[str, Any]] = None
    detected_at: float = field(default_factory=time.time)

@dataclass
class ContextSnapshot:
    snapshot_id: str
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    parent_snapshot_id: Optional[str] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: str = ""

    def __post_init__(self):
        if not self.integrity_hash:
            self.integrity_hash = self.compute_hash()

    def compute_hash(self) -> str:
        raw = json.dumps({
            "snapshot_id": self.snapshot_id,
            "version": self.version,
            "parent_snapshot_id": self.parent_snapshot_id,
            "context_data": self.context_data
        }, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.integrity_hash
