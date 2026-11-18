from typing import Dict, Any, List
from ..core.procedural_schema import AssetConstructionGraph

class BlenderGeometryAdapter:
    def __init__(self):
        self.temp_collections: Dict[str, List[str]] = {}
        self.published_collections: Dict[str, List[str]] = {}

    def stage_in_temp_collection(self, graph: AssetConstructionGraph) -> str:
        temp_col = f"__BUILD_{graph.asset_id}__"
        self.temp_collections[temp_col] = list(graph.nodes.keys())
        return temp_col

    def commit_atomic(self, graph: AssetConstructionGraph) -> str:
        temp_col = f"__BUILD_{graph.asset_id}__"
        prod_col = f"ASSET_{graph.asset_id}"
        if temp_col in self.temp_collections:
            self.published_collections[prod_col] = self.temp_collections.pop(temp_col)
        else:
            self.published_collections[prod_col] = list(graph.nodes.keys())
        return prod_col
