from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from .twin_types import (
    GraphNodeType, GraphRelationType, ReconciliationState,
    ComponentLifecycleState, AssetLifecycleState, ImpactLevel, DiffType
)

@dataclass
class AssetIdentity:
    asset_id: str
    asset_type: str = "PROP.BARREL"
    version: str = "1.0.0"
    specification_id: str = "SPEC_DEFAULT"
    generation_id: str = "GEN_DEFAULT"
    project_id: str = "DARX"

@dataclass
class ComponentIdentity:
    component_id: str
    asset_id: str
    semantic_type: str
    semantic_id: str
    version: str = "1.0.0"

@dataclass
class SemanticComponentNode:
    component_id: str
    semantic_id: str
    semantic_type: str
    blender_object_name: str
    transform: Dict[str, Any] = field(default_factory=lambda: {"location": (0,0,0), "rotation": (0,0,0), "scale": (1,1,1)})
    material_name: str = "DEFAULT_MATERIAL"
    lifecycle_state: ComponentLifecycleState = ComponentLifecycleState.ACTIVE
    tags: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    is_locked: bool = False

@dataclass
class SemanticRelationship:
    source_id: str
    target_id: str
    relation_type: GraphRelationType
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SemanticAnchor:
    anchor_id: str
    component_id: str
    local_transform: Dict[str, Any] = field(default_factory=dict)
    semantic_type: str = "GRIP"

@dataclass
class SemanticSocket:
    socket_id: str
    component_id: str
    local_transform: Dict[str, Any] = field(default_factory=dict)
    socket_name: str = "grab_socket"

@dataclass
class AssetSnapshot:
    snapshot_id: str
    asset_id: str
    timestamp: float
    nodes: Dict[str, SemanticComponentNode] = field(default_factory=dict)
    relationships: List[SemanticRelationship] = field(default_factory=list)

@dataclass
class SemanticDiff:
    diff_type: DiffType
    component_id: str
    previous_value: Any
    new_value: Any
    description: str = ""

@dataclass
class RegenerationBoundary:
    target_component_id: str
    boundary_components: List[str]
    reason: str
    impact_level: ImpactLevel = ImpactLevel.LOW
