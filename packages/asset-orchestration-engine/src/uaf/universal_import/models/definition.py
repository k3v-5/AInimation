"""
UAF-81.70: Universal Asset Import Pipeline System - Models and Definitions.
Authoritative domain models for Source Identity, Format Detection, Import Profiles,
Processing Graph, Job Queue, Workers, Caching, Artifacts, and Diagnostics.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class SourceType(str, Enum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
    STREAM = "STREAM"
    ARCHIVE = "ARCHIVE"
    BUFFER = "BUFFER"


class FormatCategory(str, Enum):
    MESH = "MESH"
    TEXTURE = "TEXTURE"
    AUDIO = "AUDIO"
    ANIMATION = "ANIMATION"
    SCENE = "SCENE"
    MATERIAL = "MATERIAL"
    CONFIG = "CONFIG"
    CUSTOM = "CUSTOM"


class JobState(str, Enum):
    QUEUED = "QUEUED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"
    BLOCKED = "BLOCKED"


class JobPriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class WorkerState(str, Enum):
    IDLE = "IDLE"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


class ArtifactType(str, Enum):
    GEOMETRY = "GEOMETRY"
    IMAGE = "IMAGE"
    SOUND = "SOUND"
    METADATA = "METADATA"
    INTERMEDIATE = "INTERMEDIATE"
    FINAL = "FINAL"


class OutputPolicy(str, Enum):
    OVERWRITE = "OVERWRITE"
    ATOMIC_NEW = "ATOMIC_NEW"
    SKIP_EXISTING = "SKIP_EXISTING"


# ==============================================================================
# SOURCE NORMALIZATION HELPER
# ==============================================================================

def normalize_source_path(raw_path: str) -> str:
    if not raw_path or not isinstance(raw_path, str):
        raise ValueError("Source path must be a non-empty string.")

    # Convert backslashes
    normalized = raw_path.replace("\\", "/")

    # Disallow path traversal
    if ".." in normalized:
        raise ValueError(f"NO_NON_CANONICAL_SOURCE_PATH: Path traversal attempt in '{raw_path}'.")

    # Squeeze slashes
    normalized = re.sub(r"/+", "/", normalized)

    # Ensure leading slash if rooted
    if not normalized.startswith("/"):
        normalized = "/" + normalized

    # Strip trailing slash unless root
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized[:-1]

    # Check for illegal characters
    if re.search(r'[<>:"|?*]', normalized):
        raise ValueError(f"Invalid characters in source path: '{raw_path}'.")

    return normalized


# ==============================================================================
# 1. SOURCE IDENTITY & FORMAT
# ==============================================================================

@dataclass
class SourceIdentity:
    source_id: str
    canonical_path: str
    source_type: SourceType = SourceType.FILE
    content_hash: str = ""
    source_version: int = 1
    file_size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.canonical_path = normalize_source_path(self.canonical_path)
        if not self.content_hash:
            payload = f"{self.source_id}:{self.canonical_path}:{self.file_size_bytes}:{self.source_version}"
            self.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "canonical_path": self.canonical_path,
            "source_type": self.source_type.value,
            "content_hash": self.content_hash,
            "source_version": self.source_version,
            "file_size_bytes": self.file_size_bytes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SourceIdentity:
        return cls(
            source_id=data["source_id"],
            canonical_path=data["canonical_path"],
            source_type=SourceType(data.get("source_type", "FILE")),
            content_hash=data.get("content_hash", ""),
            source_version=data.get("source_version", 1),
            file_size_bytes=data.get("file_size_bytes", 0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class FormatDescriptor:
    format_id: str
    name: str
    category: FormatCategory
    extensions: List[str] = field(default_factory=list)
    magic_bytes: List[bytes] = field(default_factory=list)
    mime_types: List[str] = field(default_factory=list)
    default_profile_id: Optional[str] = None
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "format_id": self.format_id,
            "name": self.name,
            "category": self.category.value,
            "extensions": list(self.extensions),
            "mime_types": list(self.mime_types),
            "default_profile_id": self.default_profile_id,
            "version": self.version,
        }


# ==============================================================================
# 2. IMPORT SETTINGS & PROFILES
# ==============================================================================

@dataclass
class ImportSettings:
    settings: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

    def compute_fingerprint(self) -> str:
        serialized = json.dumps(self.settings, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self.settings)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImportSettings:
        return cls(settings=copy.deepcopy(data))


@dataclass
class ImportProfile:
    profile_id: str
    name: str
    target_format: str
    processor_id: str
    version: int = 1
    settings: ImportSettings = field(default_factory=ImportSettings)
    parent_profile_id: Optional[str] = None
    output_policy: OutputPolicy = OutputPolicy.ATOMIC_NEW

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "target_format": self.target_format,
            "processor_id": self.processor_id,
            "version": self.version,
            "settings": self.settings.to_dict(),
            "parent_profile_id": self.parent_profile_id,
            "output_policy": self.output_policy.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImportProfile:
        return cls(
            profile_id=data["profile_id"],
            name=data["name"],
            target_format=data["target_format"],
            processor_id=data["processor_id"],
            version=data.get("version", 1),
            settings=ImportSettings.from_dict(data.get("settings", {})),
            parent_profile_id=data.get("parent_profile_id"),
            output_policy=OutputPolicy(data.get("output_policy", "ATOMIC_NEW")),
        )


# ==============================================================================
# 3. PROCESSING GRAPH
# ==============================================================================

@dataclass
class ProcessingEdge:
    source_node_id: str
    output_pin: str
    target_node_id: str
    input_pin: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_node_id": self.source_node_id,
            "output_pin": self.output_pin,
            "target_node_id": self.target_node_id,
            "input_pin": self.input_pin,
        }


@dataclass
class ProcessingNode:
    node_id: str
    processor_id: str
    settings: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    is_optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "processor_id": self.processor_id,
            "settings": copy.deepcopy(self.settings),
            "inputs": copy.deepcopy(self.inputs),
            "outputs": copy.deepcopy(self.outputs),
            "is_optional": self.is_optional,
        }


@dataclass
class ProcessingGraph:
    graph_id: str
    nodes: Dict[str, ProcessingNode] = field(default_factory=dict)
    edges: List[ProcessingEdge] = field(default_factory=list)

    def add_node(self, node: ProcessingNode) -> None:
        if node.node_id in self.nodes:
            raise ValueError(f"Duplicate node ID '{node.node_id}'.")
        self.nodes[node.node_id] = node

    def add_edge(self, edge: ProcessingEdge) -> None:
        if edge.source_node_id not in self.nodes:
            raise KeyError(f"Source node '{edge.source_node_id}' does not exist in graph.")
        if edge.target_node_id not in self.nodes:
            raise KeyError(f"Target node '{edge.target_node_id}' does not exist in graph.")
        self.edges.append(edge)
        if self.detect_cycles():
            self.edges.pop()
            raise ValueError(f"NO_GRAPH_CYCLES: Adding edge creates a cycle in graph '{self.graph_id}'.")

    def detect_cycles(self) -> bool:
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}
        for e in self.edges:
            adj[e.source_node_id].append(e.target_node_id)

        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for nid in self.nodes:
            if nid not in visited:
                if dfs(nid):
                    return True
        return False

    def get_execution_order(self) -> List[str]:
        if self.detect_cycles():
            raise ValueError("NO_GRAPH_CYCLES: Cannot order cyclic graph.")

        in_degree: Dict[str, int] = {nid: 0 for nid in self.nodes}
        adj: Dict[str, List[str]] = {nid: [] for nid in self.nodes}

        for e in self.edges:
            adj[e.source_node_id].append(e.target_node_id)
            in_degree[e.target_node_id] += 1

        # Kahn's algorithm with deterministic tie-breaker (alphabetical node_id)
        ready = sorted([nid for nid, deg in in_degree.items() if deg == 0])
        order: List[str] = []

        while ready:
            curr = ready.pop(0)
            order.append(curr)
            for nxt in sorted(adj[curr]):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    ready.append(nxt)
                    ready.sort()

        if len(order) != len(self.nodes):
            raise ValueError("NO_GRAPH_CYCLES: Topological sort failed due to cycle.")
        return order

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
        }


# ==============================================================================
# 4. JOBS, ARTIFACTS & WORKERS
# ==============================================================================

@dataclass
class ImportArtifact:
    artifact_id: str
    job_id: str
    artifact_type: ArtifactType
    output_path: str
    content_hash: str
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.output_path = normalize_source_path(self.output_path)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "job_id": self.job_id,
            "artifact_type": self.artifact_type.value,
            "output_path": self.output_path,
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


@dataclass
class ImportJob:
    job_id: str
    source_id: str
    profile_id: str
    priority: JobPriority = JobPriority.NORMAL
    state: JobState = JobState.QUEUED
    progress: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    created_time: float = field(default_factory=time.time)
    started_time: Optional[float] = None
    completed_time: Optional[float] = None
    artifacts: List[ImportArtifact] = field(default_factory=list)
    checkpoint: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "source_id": self.source_id,
            "profile_id": self.profile_id,
            "priority": self.priority.value,
            "state": self.state.value,
            "progress": self.progress,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_time": self.created_time,
            "started_time": self.started_time,
            "completed_time": self.completed_time,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "checkpoint": self.checkpoint,
        }


@dataclass
class ImportManifest:
    manifest_id: str
    job_id: str
    artifacts: List[ImportArtifact] = field(default_factory=list)
    total_size_bytes: int = 0
    created_time: float = field(default_factory=time.time)
    signature: str = ""

    def compute_signature(self) -> str:
        payload = f"{self.manifest_id}:{self.job_id}:{self.total_size_bytes}:{len(self.artifacts)}"
        for a in sorted(self.artifacts, key=lambda x: x.artifact_id):
            payload += f":{a.artifact_id}:{a.content_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.total_size_bytes and self.artifacts:
            self.total_size_bytes = sum(a.size_bytes for a in self.artifacts)
        if not self.signature:
            self.signature = self.compute_signature()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "job_id": self.job_id,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "total_size_bytes": self.total_size_bytes,
            "created_time": self.created_time,
            "signature": self.signature,
        }


# ==============================================================================
# 5. SNAPSHOT, TELEMETRY & DIAGNOSTICS
# ==============================================================================

@dataclass
class ImportTelemetry:
    queued_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0
    worker_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    retries: int = 0
    total_processed_bytes: int = 0


@dataclass
class ImportStateSnapshot:
    snapshot_id: str
    timestamp: float
    sources: Dict[str, Dict[str, Any]]
    jobs: Dict[str, Dict[str, Any]]
    profiles: Dict[str, Dict[str, Any]]
    state_hash: str = ""

    def compute_hash(self) -> str:
        canonical = {
            "snapshot_id": self.snapshot_id,
            "sources": {k: v for k, v in sorted(self.sources.items())},
            "jobs": {k: v for k, v in sorted(self.jobs.items())},
            "profiles": {k: v for k, v in sorted(self.profiles.items())},
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()


@dataclass
class ImportDiagnosticBundle:
    bundle_id: str
    timestamp: float
    snapshot: ImportStateSnapshot
    telemetry: ImportTelemetry
    signature: str = ""

    def sign(self) -> str:
        payload = f"{self.bundle_id}:{self.timestamp}:{self.snapshot.state_hash}:{self.telemetry.completed_jobs}:{self.telemetry.cache_hits}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.sign()


# Collision-safe root aliases
ImportSourceIdentity = SourceIdentity
ImportJobState = JobState
ImportJobPriority = JobPriority
