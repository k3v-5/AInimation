from typing import Dict, Any, List, Optional
from ..core.scene_graph import SceneGraph
from ..specification.asset_schema import AssetSpecification

class MeshValidator:
    @staticmethod
    def validate(graph: SceneGraph, spec: Optional[AssetSpecification] = None) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        # Estimar triángulos aproximados según primitivas
        estimated_triangles = 0
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            prim = node.primitive_type.value
            if prim == "box":
                estimated_triangles += 12
            elif prim == "cylinder":
                estimated_triangles += 64
            elif prim == "sphere":
                estimated_triangles += 128
            else:
                estimated_triangles += 50

        if spec and spec.budget:
            if estimated_triangles > spec.budget.max_triangles:
                errors.append(f"Estimated triangle count ({estimated_triangles}) exceeds budget ({spec.budget.max_triangles})")

        return {
            "category": "mesh",
            "passed": len(errors) == 0,
            "estimated_triangles": estimated_triangles,
            "errors": errors,
            "warnings": warnings
        }
