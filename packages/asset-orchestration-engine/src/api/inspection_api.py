from typing import Dict, Any, Optional
from ..core.state_manager import StateManager

class InspectionAPI:
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager

    def inspect_asset(self, asset_id: str) -> Dict[str, Any]:
        graph = self.state_manager.get_graph(asset_id)
        if not graph:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found."}
        
        nodes_info = {}
        for nid, node in graph.nodes.items():
            nodes_info[nid] = {
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "primitive": node.primitive_type.value,
                "parent_id": node.parent_id,
                "dimensions": {
                    "width": node.dimensions.width,
                    "depth": node.dimensions.depth,
                    "height": node.dimensions.height,
                    "unit": node.dimensions.unit
                },
                "location": node.local_transform.location,
                "rotation": node.local_transform.rotation,
                "scale": node.local_transform.scale,
                "materials": node.material_references,
                "version": node.version
            }

        return {
            "success": True,
            "asset_id": asset_id,
            "status": self.state_manager.get_status(asset_id).value,
            "components_count": len(graph.nodes) - 1,
            "nodes": nodes_info
        }

    def inspect_component(self, asset_id: str, component_id: str) -> Dict[str, Any]:
        graph = self.state_manager.get_graph(asset_id)
        if not graph:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found."}

        node = graph.get_node(component_id) or graph.find_node_by_name(component_id)
        if not node:
            return {"success": False, "error_code": "COMPONENT_NOT_FOUND", "message": f"Component '{component_id}' not found in asset '{asset_id}'."}

        return {
            "success": True,
            "asset_id": asset_id,
            "component_id": node.id,
            "name": node.name,
            "primitive": node.primitive_type.value,
            "parent_id": node.parent_id,
            "dimensions": {
                "width": node.dimensions.width,
                "depth": node.dimensions.depth,
                "height": node.dimensions.height
            },
            "location": node.local_transform.location,
            "materials": node.material_references,
            "version": node.version
        }
