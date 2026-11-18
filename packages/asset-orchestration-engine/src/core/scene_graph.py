from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Any
import copy
from ..specification.asset_schema import PrimitiveType, DimensionsSpec

@dataclass
class Transform:
    location: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)

@dataclass
class SceneNode:
    id: str
    name: str
    type: str = "mesh"
    primitive_type: PrimitiveType = PrimitiveType.BOX
    parent_id: Optional[str] = None
    local_transform: Transform = field(default_factory=Transform)
    dimensions: DimensionsSpec = field(default_factory=DimensionsSpec)
    material_references: List[str] = field(default_factory=list)
    geometry_reference: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_operation: Optional[str] = None
    version: int = 1
    children_ids: List[str] = field(default_factory=list)
    is_locked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneNode':
        d = copy.deepcopy(data)
        lt_data = d.get("local_transform", {})
        d["local_transform"] = Transform(**lt_data) if isinstance(lt_data, dict) else Transform()
        dim_data = d.get("dimensions", {})
        d["dimensions"] = DimensionsSpec(**dim_data) if isinstance(dim_data, dict) else DimensionsSpec()
        if "primitive_type" in d and isinstance(d["primitive_type"], str):
            d["primitive_type"] = PrimitiveType(d["primitive_type"])
        return cls(**d)

class SceneGraph:
    def __init__(self, asset_id: str, root_name: str = "Root"):
        self.asset_id = asset_id
        self.root_id = asset_id
        self.nodes: Dict[str, SceneNode] = {}
        root_node = SceneNode(
            id=self.root_id,
            name=root_name,
            type="group",
            primitive_type=PrimitiveType.CUSTOM,
            parent_id=None
        )
        self.nodes[self.root_id] = root_node

    def add_node(self, node: SceneNode, parent_id: Optional[str] = None) -> bool:
        if node.id in self.nodes:
            return False
        p_id = parent_id or self.root_id
        if p_id not in self.nodes:
            p_id = self.root_id
        node.parent_id = p_id
        self.nodes[node.id] = node
        if node.id not in self.nodes[p_id].children_ids:
            self.nodes[p_id].children_ids.append(node.id)
        return True

    def get_node(self, node_id: str) -> Optional[SceneNode]:
        return self.nodes.get(node_id)

    def find_node_by_name(self, name: str) -> Optional[SceneNode]:
        for n in self.nodes.values():
            if n.name == name or n.id.endswith(f".{name}"):
                return n
        return None

    def remove_node(self, node_id: str, recursive: bool = True) -> bool:
        if node_id not in self.nodes or node_id == self.root_id:
            return False
        node = self.nodes[node_id]
        if node.parent_id and node.parent_id in self.nodes:
            if node_id in self.nodes[node.parent_id].children_ids:
                self.nodes[node.parent_id].children_ids.remove(node_id)
        if recursive:
            for child_id in list(node.children_ids):
                self.remove_node(child_id, recursive=True)
        del self.nodes[node_id]
        return True

    def modify_node(self, node_id: str, **kwargs) -> bool:
        node = self.nodes.get(node_id)
        if not node or node.is_locked:
            return False
        for k, v in kwargs.items():
            if hasattr(node, k):
                setattr(node, k, v)
        node.version += 1
        return True

    def get_children(self, node_id: str) -> List[SceneNode]:
        node = self.nodes.get(node_id)
        if not node:
            return []
        return [self.nodes[cid] for cid in node.children_ids if cid in self.nodes]

    def clone(self) -> 'SceneGraph':
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "root_id": self.root_id,
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SceneGraph':
        sg = cls(asset_id=data["asset_id"])
        sg.root_id = data["root_id"]
        sg.nodes = {nid: SceneNode.from_dict(ndata) for nid, ndata in data["nodes"].items()}
        return sg
