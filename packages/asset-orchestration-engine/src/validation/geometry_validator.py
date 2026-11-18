from typing import Dict, Any, List, Optional
from ..core.scene_graph import SceneGraph
from ..specification.asset_schema import AssetSpecification

class GeometryValidator:
    @staticmethod
    def validate(graph: SceneGraph, spec: Optional[AssetSpecification] = None) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Verificar origen en (0,0,0) del nodo raíz
        root = graph.get_node(graph.root_id)
        if root and root.local_transform.location != (0.0, 0.0, 0.0):
            errors.append(f"Root origin must be at (0,0,0), found: {root.local_transform.location}")

        # 2. Verificar que los componentes tienen dimensiones válidas (>0)
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            if node.dimensions.height <= 0 or node.dimensions.width <= 0 or node.dimensions.depth <= 0:
                errors.append(f"Component '{node.name}' has invalid zero or negative dimensions: ({node.dimensions.width}, {node.dimensions.depth}, {node.dimensions.height})")

        return {
            "category": "geometric",
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
