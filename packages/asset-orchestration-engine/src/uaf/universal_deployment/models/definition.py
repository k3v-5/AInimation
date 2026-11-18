"""
Universal Build, Packaging, Dependency, Content Addressing, Asset Registry,
Installation, Patching, Update, DLC, Modular Content & Runtime Deployment Models (UAF-81.63).
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class AssetType(str, Enum):
    """Authoritative asset categories (§8 & UAF-81.0 Core)."""
    TEXTURE = "TEXTURE"
    MESH = "MESH"
    MATERIAL = "MATERIAL"
    SHADER = "SHADER"
    ANIMATION = "ANIMATION"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    FONT = "FONT"
    SCRIPT = "SCRIPT"
    SCENE = "SCENE"
    PREFAB = "PREFAB"
    DATA = "DATA"
    LOCALIZATION = "LOCALIZATION"
    UI = "UI"
    CONFIGURATION = "CONFIGURATION"
    PLUGIN = "PLUGIN"
    CHARACTER = "CHARACTER"
    CREATURE = "CREATURE"
    WEAPON = "WEAPON"
    PROP = "PROP"
    MODULAR_KIT = "MODULAR_KIT"
    ARCHITECTURE = "ARCHITECTURE"
    ENVIRONMENT = "ENVIRONMENT"
    VFX = "VFX"
    RIG = "RIG"
    LEVEL = "LEVEL"
    WORLD = "WORLD"
    BLUEPRINT = "BLUEPRINT"
    OTHER = "OTHER"

    @classmethod
    def from_str(cls, value: str) -> "AssetType":
        normalized = value.strip().upper()
        try:
            return cls(normalized)
        except ValueError:
            return cls.DATA


class ContentType(str, Enum):
    """Deployment packaging content units (§9)."""
    BASE_GAME = "BASE_GAME"
    LEVEL = "LEVEL"
    EXPANSION = "EXPANSION"
    DLC = "DLC"
    LANGUAGE_PACK = "LANGUAGE_PACK"
    OPTIONAL_PACK = "OPTIONAL_PACK"
    MOD = "MOD"
    PATCH = "PATCH"


class DependencyType(str, Enum):
    """Dependency relationship categories (§15)."""
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    CONFLICT = "CONFLICT"
    LOAD_ORDER = "LOAD_ORDER"
    BUILD_ORDER = "BUILD_ORDER"
    RUNTIME_ORDER = "RUNTIME_ORDER"


class ConflictPolicy(str, Enum):
    """Policy for resolving content and version collisions (§22)."""
    REJECT = "REJECT"
    SELECT_COMPATIBLE = "SELECT_COMPATIBLE"
    REQUIRE_USER_DECISION = "REQUIRE_USER_DECISION"


class BuildState(str, Enum):
    """Build task lifecycle states (§41)."""
    QUEUED = "QUEUED"
    RESOLVING = "RESOLVING"
    PREPARING = "PREPARING"
    BUILDING = "BUILDING"
    PACKAGING = "PACKAGING"
    HASHING = "HASHING"
    SIGNING = "SIGNING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ArtifactLifecycle(str, Enum):
    """Lifecycle states of a generated build artifact (§47)."""
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    SIGNED = "SIGNED"
    PUBLISHED = "PUBLISHED"
    AVAILABLE = "AVAILABLE"
    DEPRECATED = "DEPRECATED"
    REVOKED = "REVOKED"
    DELETED = "DELETED"


class PackageType(str, Enum):
    """Types of deployable packages (§62)."""
    FULL = "FULL"
    PATCH = "PATCH"
    DELTA = "DELTA"
    DLC = "DLC"
    OPTIONAL = "OPTIONAL"
    LANGUAGE = "LANGUAGE"
    MOD = "MOD"


class DownloadState(str, Enum):
    """Download manager operation states (§71)."""
    QUEUED = "QUEUED"
    CONNECTING = "CONNECTING"
    DOWNLOADING = "DOWNLOADING"
    PAUSED = "PAUSED"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class InstallState(str, Enum):
    """Installation transaction states (§77)."""
    DISCOVERING = "DISCOVERING"
    VALIDATING = "VALIDATING"
    PREPARING = "PREPARING"
    BACKING_UP = "BACKING_UP"
    INSTALLING = "INSTALLING"
    VERIFYING = "VERIFYING"
    COMMITTING = "COMMITTING"
    ACTIVATING = "ACTIVATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"


class UninstallState(str, Enum):
    """Uninstallation operation states (§86)."""
    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    REMOVING = "REMOVING"
    VERIFYING = "VERIFYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class TrustPolicy(str, Enum):
    """Cryptographic signature and origin trust levels (§58)."""
    TRUSTED = "TRUSTED"
    UNTRUSTED = "UNTRUSTED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class RepairAction(str, Enum):
    """Action taken during file verification and repair (§216)."""
    VERIFIED = "VERIFIED"
    REDOWNLOAD = "REDOWNLOAD"
    REINSTALL = "REINSTALL"
    BACKUP_RESTORE = "BACKUP_RESTORE"
    QUARANTINE = "QUARANTINE"


# ==============================================================================
# DATA STRUCTURES & VALUE OBJECTS
# ==============================================================================

@dataclass
class AssetRecord:
    """Logical asset record independent of machine paths (§6, §7)."""
    asset_id: str
    asset_type: AssetType
    source_id: str
    version: str = "1.0.0"
    content_hash: str = ""
    metadata_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def calculate_content_hash(self, content_bytes: bytes) -> str:
        self.content_hash = hashlib.sha256(content_bytes).hexdigest()
        return self.content_hash


@dataclass
class ContentPackage:
    """Deployable content grouping (§9, §10, §11)."""
    content_id: str
    content_type: ContentType
    content_version: str = "1.0.0"
    manifest_id: str = ""
    content_hash: str = ""
    assets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DependencyEdge:
    """Directional dependency relation between entities (§14, §15)."""
    source_id: str
    target_id: str
    dep_type: DependencyType = DependencyType.REQUIRED
    min_version: Optional[str] = None
    max_version: Optional[str] = None


@dataclass
class DependencyGraph:
    """Graph structure with cycle detection and topological resolution (§13, §16, §17, §18)."""
    nodes: Set[str] = field(default_factory=set)
    edges: List[DependencyEdge] = field(default_factory=list)

    def add_node(self, node_id: str) -> None:
        self.nodes.add(node_id)

    def add_edge(self, edge: DependencyEdge) -> None:
        self.nodes.add(edge.source_id)
        self.nodes.add(edge.target_id)
        self.edges.append(edge)

    def has_cycle(self) -> bool:
        """Detects circular dependencies using DFS graph coloring."""
        adj: Dict[str, List[str]] = {n: [] for n in self.nodes}
        for e in self.edges:
            if e.dep_type in [DependencyType.REQUIRED, DependencyType.BUILD_ORDER, DependencyType.LOAD_ORDER]:
                adj[e.source_id].append(e.target_id)

        visited: Dict[str, int] = {n: 0 for n in self.nodes}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(u: str) -> bool:
            visited[u] = 1
            for v in adj[u]:
                if visited[v] == 1:
                    return True
                if visited[v] == 0 and dfs(v):
                    return True
            visited[u] = 2
            return False

        for node in self.nodes:
            if visited[node] == 0:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        """Returns deterministic build/load order using Kahn's algorithm."""
        if self.has_cycle():
            raise ValueError("Dependency cycle detected; cannot compute topological order.")

        adj: Dict[str, List[str]] = {n: [] for n in self.nodes}
        in_degree: Dict[str, int] = {n: 0 for n in self.nodes}

        for e in self.edges:
            if e.dep_type in [DependencyType.REQUIRED, DependencyType.BUILD_ORDER, DependencyType.LOAD_ORDER]:
                adj[e.target_id].append(e.source_id)  # target must be built before source
                in_degree[e.source_id] += 1

        queue = sorted([n for n, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in sorted(adj[u]):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
            queue.sort()

        if len(order) != len(self.nodes):
            raise ValueError("Incomplete topological sort.")
        return order


@dataclass
class BuildNode:
    """Compilation or transformation step in the build graph (§31)."""
    node_id: str
    inputs: List[str] = field(default_factory=list)
    output_artifact: str = ""
    tool_version: str = "1.0.0"
    command: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BuildGraph:
    """Graph of dependent transformation and compilation tasks (§30, §32)."""
    nodes: Dict[str, BuildNode] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, node: BuildNode, depends_on: Optional[List[str]] = None) -> None:
        self.nodes[node.node_id] = node
        self.dependencies[node.node_id] = list(depends_on or [])


@dataclass
class BuildCacheEntry:
    """Deterministic build artifact cache entry (§34, §35)."""
    cache_key: str
    artifact_id: str
    source_hash: str
    tool_version: str
    platform: str
    created_at: float


@dataclass
class BuildArtifact:
    """Produced binary or packaged asset deliverable (§44, §46)."""
    artifact_id: str
    artifact_type: AssetType
    version: str = "1.0.0"
    platform: str = "Windows"
    architecture: str = "x64"
    size_bytes: int = 0
    content_hash: str = ""
    build_id: str = ""
    lifecycle: ArtifactLifecycle = ArtifactLifecycle.CREATED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileManifestEntry:
    """Individual file metadata within an installable manifest (§51)."""
    relative_path: str
    size_bytes: int
    hash_sha256: str
    chunk_id: Optional[str] = None
    flags: List[str] = field(default_factory=list)


@dataclass
class PackageManifest:
    """Authoritative delivery and installation manifest (§50, §51, §52)."""
    product_id: str
    content_id: str
    content_version: str
    platform: str = "Windows"
    architecture: str = "x64"
    manifest_version: str = "1.0.0"
    files: List[FileManifestEntry] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    hashes: Dict[str, str] = field(default_factory=dict)
    signatures: Dict[str, str] = field(default_factory=dict)
    install_rules: Dict[str, Any] = field(default_factory=dict)
    uninstall_rules: Dict[str, Any] = field(default_factory=dict)

    def calculate_manifest_hash(self) -> str:
        sorted_files = sorted(
            [{"path": f.relative_path, "hash": f.hash_sha256, "size": f.size_bytes} for f in self.files],
            key=lambda x: x["path"],
        )
        serialized = json.dumps({
            "product_id": self.product_id,
            "content_id": self.content_id,
            "content_version": self.content_version,
            "platform": self.platform,
            "architecture": self.architecture,
            "files": sorted_files,
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class ChunkDescriptor:
    """Sub-package chunk descriptor for multi-part distribution (§67, §68)."""
    chunk_id: str
    offset: int
    size_bytes: int
    hash_sha256: str


@dataclass
class DeploymentPackage:
    """Complete deliverable container (§61, §63)."""
    package_id: str
    package_type: PackageType
    manifest: PackageManifest
    chunks: List[ChunkDescriptor] = field(default_factory=list)
    payload_files: Dict[str, bytes] = field(default_factory=dict)
    signature: str = ""
    is_certified: bool = False


@dataclass
class DownloadRequest:
    """Stateful download task (§70, §71)."""
    download_id: str
    package_id: str
    target_url: str
    state: DownloadState = DownloadState.QUEUED
    bytes_downloaded: int = 0
    total_bytes: int = 0
    attempts: int = 0
    error_message: Optional[str] = None


@dataclass
class InstallationRecord:
    """Active or committed installation status (§76, §77, §80)."""
    install_id: str
    package_id: str
    version: str
    install_dir: str
    installed_files: Dict[str, str] = field(default_factory=dict)  # relative_path -> sha256
    state: InstallState = InstallState.COMPLETED
    backup_dir: Optional[str] = None
    installed_at: float = 0.0


@dataclass
class PatchDescriptor:
    """Differential or delta update metadata (§38, §39, §89)."""
    patch_id: str
    source_version: str
    target_version: str
    package_id: str
    delta_files: List[str] = field(default_factory=list)
    removed_files: List[str] = field(default_factory=list)


@dataclass
class SigningCertificate:
    """Cryptographic signing key certificate (§55, §58)."""
    cert_id: str
    issuer: str
    public_key: str
    trust_policy: TrustPolicy = TrustPolicy.TRUSTED
    expires_at: float = 0.0


@dataclass
class DeploymentDiagnosticReport:
    """Health check report for the deployment subsystem."""
    is_healthy: bool = True
    registered_assets: int = 0
    installed_packages: int = 0
    corrupted_files: int = 0
    pending_updates: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
