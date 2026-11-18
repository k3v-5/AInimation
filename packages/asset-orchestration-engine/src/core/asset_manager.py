from typing import Optional, Dict, Any, List
from .id_manager import IdManager
from .scene_graph import SceneGraph, SceneNode, Transform
from .state_manager import StateManager
from ..specification.asset_schema import AssetSpecification, AssetStatus, ComponentSpec, DimensionsSpec

class AssetManager:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def create_from_specification(self, spec: AssetSpecification) -> SceneGraph:
        graph = SceneGraph(asset_id=spec.asset_id, root_name=spec.name)
        for c in spec.components:
            comp_id = IdManager.make_component_id(spec.asset_id, c.id)
            parent_id = IdManager.make_component_id(spec.asset_id, c.parent_id) if c.parent_id else graph.root_id
            dims = c.dimensions or DimensionsSpec()
            node = SceneNode(
                id=comp_id,
                name=c.id,
                type=c.type,
                primitive_type=c.primitive,
                parent_id=parent_id,
                local_transform=Transform(location=c.relative_position, rotation=c.relative_rotation, scale=c.relative_scale),
                dimensions=dims,
                material_references=[c.material_id] if c.material_id else [],
                parameters=c.properties,
                metadata={"category": spec.category.value}
            )
            graph.add_node(node, parent_id=parent_id)

        self.state_manager.register_asset(spec, graph)
        return graph

    def get_asset_graph(self, asset_id: str) -> Optional[SceneGraph]:
        return self.state_manager.get_graph(asset_id)

    def get_asset_spec(self, asset_id: str) -> Optional[AssetSpecification]:
        return self.state_manager.get_spec(asset_id)
