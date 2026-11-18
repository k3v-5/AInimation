import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from .world_types import (
    NodeType, EdgeType, DependencyStrength, DirtyState,
    ImpactLevel, ChangeCategory
)

@dataclass
class WorldNode:
    node_id: str
    name: str
    node_type: NodeType
    world_id: str = "DEFAULT_WORLD"
    version: str = "1.0.0"
    dirty_state: DirtyState = DirtyState.CLEAN
    dirty_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorldEdge:
    edge_id: str
    source_id: str
    target_id: str
    edge_type: EdgeType
    strength: DependencyStrength = DependencyStrength.HARD
    allows_propagation: bool = True
    version_req: Optional[str] = None
    reason: str = ""

@dataclass
class ImpactReport:
    source_node_id: str
    change_category: ChangeCategory
    direct_impacts: List[str] = field(default_factory=list)
    indirect_impacts: List[str] = field(default_factory=list)
    potential_impacts: List[str] = field(default_factory=list)
    unaffected_nodes: List[str] = field(default_factory=list)
    requires_geometry_regeneration: bool = True
    requires_material_update: bool = False

@dataclass
class RegenerationPlan:
    plan_id: str
    execution_order: List[str] = field(default_factory=list)
    dirty_nodes: List[str] = field(default_factory=list)
    parallel_batches: List[List[str]] = field(default_factory=list)
    estimated_mcp_calls: int = 1

@dataclass
class WorldSnapshotRecord:
    snapshot_id: str
    world_id: str
    node_count: int
    edge_count: int
    timestamp: float = field(default_factory=time.time)

@dataclass
class WorldChangeProposal:
    proposal_id: str
    target_node_id: str
    change_desc: str
    risk_level: str = "LOW"
    impact_summary: str = ""
