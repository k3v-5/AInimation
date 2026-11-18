from typing import Dict, Any, List, Optional
from ..core.scene_graph import SceneGraph
from ..specification.asset_schema import AssetSpecification, AssetStatus
from .geometry_validator import GeometryValidator
from .mesh_validator import MeshValidator
from .material_validator import MaterialValidator

class QualityGateValidator:
    def __init__(self):
        self.geom_val = GeometryValidator()
        self.mesh_val = MeshValidator()
        self.mat_val = MaterialValidator()

    def validate_asset(self, graph: SceneGraph, spec: Optional[AssetSpecification] = None) -> Dict[str, Any]:
        results = {
            "asset_id": graph.asset_id,
            "status": "VALID",
            "passed": True,
            "reports": []
        }

        # 1. Validación Estructural
        struct_report = {"category": "structural", "passed": True, "errors": [], "warnings": []}
        if len(graph.nodes) <= 1:
            struct_report["passed"] = False
            struct_report["errors"].append("Asset has no child components under root.")
        results["reports"].append(struct_report)

        # 2. Validación Geométrica
        geom_report = self.geom_val.validate(graph, spec)
        results["reports"].append(geom_report)

        # 3. Validación de Malla
        mesh_report = self.mesh_val.validate(graph, spec)
        results["reports"].append(mesh_report)

        # 4. Validación de Materiales
        mat_report = self.mat_val.validate(graph, spec)
        results["reports"].append(mat_report)

        # Determinar resultado global
        all_passed = all(r["passed"] for r in results["reports"])
        results["passed"] = all_passed
        results["status"] = "READY" if all_passed else "INVALID"

        return results
