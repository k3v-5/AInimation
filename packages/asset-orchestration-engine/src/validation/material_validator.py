from typing import Dict, Any, List, Optional
from ..core.scene_graph import SceneGraph
from ..specification.asset_schema import AssetSpecification

class MaterialValidator:
    @staticmethod
    def validate(graph: SceneGraph, spec: Optional[AssetSpecification] = None) -> Dict[str, Any]:
        errors: List[str] = []
        warnings: List[str] = []

        all_materials = set()
        for nid, node in graph.nodes.items():
            if nid == graph.root_id:
                continue
            for m in node.material_references:
                if m:
                    all_materials.add(m)

        if spec and spec.budget:
            if len(all_materials) > spec.budget.max_materials:
                errors.append(f"Material count ({len(all_materials)}) exceeds budget ({spec.budget.max_materials})")

        return {
            "category": "material",
            "passed": len(errors) == 0,
            "materials_count": len(all_materials),
            "errors": errors,
            "warnings": warnings
        }
