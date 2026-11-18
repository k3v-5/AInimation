"""
Universal Scene Assembly, Prefabs, Entity Hierarchy & Serialization Models.
Complies with UAF-81.72 specification.
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple


class ComponentType(str, Enum):
    TRANSFORM = "TRANSFORM"
    MESH_RENDERER = "MESH_RENDERER"
    LIGHT = "LIGHT"
    CAMERA = "CAMERA"
    AUDIO_SOURCE = "AUDIO_SOURCE"
    COLLIDER = "COLLIDER"
    SCRIPT = "SCRIPT"
    CUSTOM = "CUSTOM"


class OverrideType(str, Enum):
    PROPERTY = "PROPERTY"
    COMPONENT_ADD = "COMPONENT_ADD"
    COMPONENT_REMOVE = "COMPONENT_REMOVE"
    CHILD_ADD = "CHILD_ADD"
    CHILD_REMOVE = "CHILD_REMOVE"


class MergeConflictResolution(str, Enum):
    TAKE_MINE = "TAKE_MINE"
    TAKE_THEIRS = "TAKE_THEIRS"
    TAKE_BASE = "TAKE_BASE"
    MANUAL = "MANUAL"


class SceneBuildMode(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    SHIPPING = "SHIPPING"
    PREVIEW = "PREVIEW"


class SceneState(str, Enum):
    DIRTY = "DIRTY"
    SAVED = "SAVED"
    BUILDING = "BUILDING"
    BUILT = "BUILT"
    ERROR = "ERROR"


def normalize_scene_path(path: str) -> str:
    if not path or not isinstance(path, str):
        raise ValueError("INVALID_PATH: Path must be a non-empty string.")
    
    p = path.replace("\\", "/").strip()
    parts = p.split("/")
    if ".." in parts:
        raise ValueError("PATH_TRAVERSAL_DETECTED: Path contains '..' segments.")
    
    clean_p = p
    if len(p) >= 2 and p[1] == ":" and p[0].isalpha():
        clean_p = p[2:]
    
    illegal = set('<>:"|?*')
    for ch in clean_p:
        if ch in illegal or ord(ch) < 32:
            raise ValueError(f"ILLEGAL_PATH_CHARACTER: Forbidden character '{ch}' in path.")
    
    p = re.sub(r"/+", "/", p)
    if not p.startswith("/"):
        p = "/" + p
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


@dataclass
class Transform:
    position: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    scale: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])

    def combine(self, parent: "Transform") -> "Transform":
        # Hierarchical position addition & scale multiplication
        combined_pos = [
            parent.position[0] + self.position[0] * parent.scale[0],
            parent.position[1] + self.position[1] * parent.scale[1],
            parent.position[2] + self.position[2] * parent.scale[2],
        ]
        combined_rot = [
            parent.rotation[0] + self.rotation[0],
            parent.rotation[1] + self.rotation[1],
            parent.rotation[2] + self.rotation[2],
        ]
        combined_scale = [
            parent.scale[0] * self.scale[0],
            parent.scale[1] * self.scale[1],
            parent.scale[2] * self.scale[2],
        ]
        return Transform(combined_pos, combined_rot, combined_scale)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": list(self.position),
            "rotation": list(self.rotation),
            "scale": list(self.scale),
        }


@dataclass
class Component:
    component_id: str
    component_type: ComponentType
    schema_version: str = "1.0.0"
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "schema_version": self.schema_version,
            "properties": copy_dict_deterministic(self.properties),
        }


def copy_dict_deterministic(d: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(d, sort_keys=True))


@dataclass
class Entity:
    entity_id: str
    name: str = "Entity"
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    components: Dict[str, Component] = field(default_factory=dict)
    transform: Transform = field(default_factory=Transform)
    prefab_instance_id: Optional[str] = None
    is_active: bool = True
    flags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "children_ids": list(self.children_ids),
            "components": {cid: c.to_dict() for cid, c in sorted(self.components.items())},
            "transform": self.transform.to_dict(),
            "prefab_instance_id": self.prefab_instance_id,
            "is_active": self.is_active,
            "flags": copy_dict_deterministic(self.flags),
        }


@dataclass
class PrefabOverride:
    override_type: OverrideType
    target_entity_id: str
    property_path: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {
            "override_type": self.override_type.value,
            "target_entity_id": self.target_entity_id,
            "property_path": self.property_path,
            "value": self.value,
        }


@dataclass
class Prefab:
    prefab_id: str
    name: str
    root_entity_id: str
    entities: Dict[str, Entity] = field(default_factory=dict)
    nested_prefab_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prefab_id": self.prefab_id,
            "name": self.name,
            "root_entity_id": self.root_entity_id,
            "entities": {eid: e.to_dict() for eid, e in sorted(self.entities.items())},
            "nested_prefab_ids": list(self.nested_prefab_ids),
        }


@dataclass
class PrefabInstance:
    instance_id: str
    prefab_id: str
    root_entity_id: str
    overrides: List[PrefabOverride] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "prefab_id": self.prefab_id,
            "root_entity_id": self.root_entity_id,
            "overrides": [ov.to_dict() for ov in self.overrides],
        }


@dataclass
class Scene:
    scene_id: str
    scene_path: str
    name: str = "NewScene"
    scene_version: int = 1
    root_entity_id: str = "root"
    entities: Dict[str, Entity] = field(default_factory=dict)
    prefabs: Dict[str, Prefab] = field(default_factory=dict)
    prefab_instances: Dict[str, PrefabInstance] = field(default_factory=dict)
    is_dirty: bool = False
    schema_version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_fingerprint: str = ""

    def compute_fingerprint(self) -> str:
        serialized = self.to_json()
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.content_fingerprint:
            self.content_fingerprint = self.compute_fingerprint()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "scene_path": self.scene_path,
            "name": self.name,
            "scene_version": self.scene_version,
            "root_entity_id": self.root_entity_id,
            "entities": {eid: e.to_dict() for eid, e in sorted(self.entities.items())},
            "prefabs": {pid: p.to_dict() for pid, p in sorted(self.prefabs.items())},
            "prefab_instances": {iid: inst.to_dict() for iid, inst in sorted(self.prefab_instances.items())},
            "schema_version": self.schema_version,
            "metadata": copy_dict_deterministic(self.metadata),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


@dataclass
class SceneDiff:
    added_entities: List[str] = field(default_factory=list)
    removed_entities: List[str] = field(default_factory=list)
    modified_entities: List[str] = field(default_factory=list)
    property_changes: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "added_entities": sorted(self.added_entities),
            "removed_entities": sorted(self.removed_entities),
            "modified_entities": sorted(self.modified_entities),
            "property_changes": self.property_changes,
        }


@dataclass
class SceneMergeResult:
    success: bool
    merged_scene: Optional[Scene] = None
    conflicts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SceneBuildArtifact:
    artifact_id: str
    scene_id: str
    build_mode: SceneBuildMode
    output_path: str
    entity_count: int
    content_hash: str
    signature: str = ""

    def compute_signature(self) -> str:
        payload = f"{self.artifact_id}:{self.scene_id}:{self.build_mode.value}:{self.output_path}:{self.entity_count}:{self.content_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.compute_signature()


@dataclass
class SceneStateSnapshot:
    snapshot_id: str
    timestamp: float
    scene_data: Dict[str, Any]
    state_hash: str = ""

    def compute_state_hash(self) -> str:
        payload = f"{self.snapshot_id}:{self.timestamp}:{json.dumps(self.scene_data, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_state_hash()


@dataclass
class SceneDiagnosticBundle:
    bundle_id: str
    timestamp: float
    snapshot: SceneStateSnapshot
    error_log: List[str] = field(default_factory=list)
    signature: str = ""

    def compute_signature(self) -> str:
        payload = f"{self.bundle_id}:{self.timestamp}:{self.snapshot.state_hash}:{','.join(self.error_log)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.compute_signature()
