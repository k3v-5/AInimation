import time
import hashlib
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

class MemoryType(str, Enum):
    PROJECT_MEMORY = "PROJECT_MEMORY"
    ASSET_MEMORY = "ASSET_MEMORY"
    REFERENCE_MEMORY = "REFERENCE_MEMORY"
    REQUIREMENT_MEMORY = "REQUIREMENT_MEMORY"
    DECISION_MEMORY = "DECISION_MEMORY"
    OPERATION_MEMORY = "OPERATION_MEMORY"
    AGENT_MEMORY = "AGENT_MEMORY"
    JOB_MEMORY = "JOB_MEMORY"
    EVALUATION_MEMORY = "EVALUATION_MEMORY"
    FAILURE_MEMORY = "FAILURE_MEMORY"
    RECOVERY_MEMORY = "RECOVERY_MEMORY"
    DELIVERY_MEMORY = "DELIVERY_MEMORY"
    TASK_MEMORY = "OPERATION_MEMORY"
    # Aliases
    STYLE_MEMORY = "PROJECT_MEMORY"
    CONSTRAINT_MEMORY = "REQUIREMENT_MEMORY"
    ERROR_MEMORY = "FAILURE_MEMORY"
    RESULT_MEMORY = "OPERATION_MEMORY"
    SESSION_MEMORY = "JOB_MEMORY"

class MemoryScope(str, Enum):
    GLOBAL = "GLOBAL"
    PROJECT = "PROJECT"
    ASSET = "ASSET"
    TASK = "TASK"
    SESSION = "SESSION"
    AGENT = "AGENT"

class MemoryStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"
    INVALIDATED = "INVALIDATED"
    ARCHIVED = "ARCHIVED"

class MemorySource(str, Enum):
    USER = "USER"
    PROMPT_COMPILER = "PROMPT_COMPILER"
    REFERENCE_ANALYSIS = "REFERENCE_ANALYSIS"
    STRATEGY_ENGINE = "AOE"
    BLENDER = "BLENDER"
    UNREAL = "UNREAL"
    AOE = "AOE"
    AGENT = "AGENT"
    VALIDATION = "VALIDATION"
    TEST = "TEST"
    RECOVERY = "RECOVERY"
    IMPORT = "IMPORT"
    EXPORT = "EXPORT"
    CRITIC = "VALIDATION"
    SYSTEM = "AOE"

@dataclass
class MemoryRecord:
    memory_id: str
    memory_type: MemoryType
    scope: MemoryScope
    content: Dict[str, Any]
    source: MemorySource = MemorySource.AOE
    source_id: str = "SYS_AUTO"
    project_id: str = "DarX"
    semantic_id: Optional[str] = None
    job_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: int = 1
    confidence: float = 1.0     # [0.0, 1.0]
    importance: float = 0.5     # [0.0, 1.0]
    valid_from: float = field(default_factory=time.time)
    valid_until: Optional[float] = None
    status: MemoryStatus = MemoryStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_memory_id: Optional[str] = None
    supersedes_memory_id: Optional[str] = None
    superseded_by: Optional[str] = None
    integrity_hash: str = ""

    def __post_init__(self):
        if not self.integrity_hash:
            self.integrity_hash = self.compute_hash()

    @property
    def memory_hash(self) -> str:
        return self.integrity_hash

    @memory_hash.setter
    def memory_hash(self, value: str):
        self.integrity_hash = value

    def compute_hash(self) -> str:
        data = {
            "memory_id": self.memory_id,
            "type": self.memory_type.value,
            "scope": self.scope.value,
            "semantic_id": self.semantic_id,
            "job_id": self.job_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "content": self.content,
            "version": self.version,
            "source": self.source.value,
            "parent_memory_id": self.parent_memory_id,
            "supersedes_memory_id": self.supersedes_memory_id
        }
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_integrity(self) -> bool:
        return self.compute_hash() == self.integrity_hash

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "scope": self.scope.value,
            "content": self.content,
            "source": self.source.value,
            "source_id": self.source_id,
            "project_id": self.project_id,
            "semantic_id": self.semantic_id,
            "job_id": self.job_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "confidence": self.confidence,
            "importance": self.importance,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
            "status": self.status.value,
            "tags": self.tags,
            "metadata": self.metadata,
            "parent_memory_id": self.parent_memory_id,
            "supersedes_memory_id": self.supersedes_memory_id,
            "superseded_by": self.superseded_by,
            "integrity_hash": self.integrity_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryRecord":
        return cls(
            memory_id=data["memory_id"],
            memory_type=MemoryType(data["memory_type"]),
            scope=MemoryScope(data["scope"]),
            content=data.get("content", {}),
            source=MemorySource(data.get("source", "AOE")),
            source_id=data.get("source_id", "SYS_AUTO"),
            project_id=data.get("project_id", "DarX"),
            semantic_id=data.get("semantic_id"),
            job_id=data.get("job_id"),
            task_id=data.get("task_id"),
            agent_id=data.get("agent_id"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            version=data.get("version", 1),
            confidence=data.get("confidence", 1.0),
            importance=data.get("importance", 0.5),
            valid_from=data.get("valid_from", time.time()),
            valid_until=data.get("valid_until"),
            status=MemoryStatus(data.get("status", "ACTIVE")),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            parent_memory_id=data.get("parent_memory_id"),
            supersedes_memory_id=data.get("supersedes_memory_id"),
            superseded_by=data.get("superseded_by"),
            integrity_hash=data.get("integrity_hash") or data.get("memory_hash", "")
        )
