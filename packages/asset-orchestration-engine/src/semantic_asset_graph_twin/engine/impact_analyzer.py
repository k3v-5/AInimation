from typing import Dict, Any, List, Optional
from ..core.twin_types import ImpactLevel
from ..core.twin_schema import RegenerationBoundary
from ..graph.semantic_asset_graph import SemanticAssetGraph

class AssetImpactAnalyzer:
    @classmethod
    def calculate_regeneration_boundary(
        cls,
        graph: SemanticAssetGraph,
        target_component_id: str,
        parameter_modified: Optional[str] = None
    ) -> RegenerationBoundary:
        target_node = graph.nodes.get(target_component_id)
        if not target_node:
            return RegenerationBoundary(target_component_id, [target_component_id], "Unknown component", ImpactLevel.NONE)

        # Si el cambio es local (ej. posición de un aro)
        if "ring" in target_node.semantic_type.lower() or parameter_modified in ["position", "transform"]:
            return RegenerationBoundary(
                target_component_id=target_component_id,
                boundary_components=[target_component_id],
                reason=f"Local modification of '{target_component_id}' has zero dependent impact.",
                impact_level=ImpactLevel.LOW
            )

        # Si el cambio es estructural (ej. altura del cuerpo)
        if "body" in target_node.semantic_type.lower() or parameter_modified in ["height", "scale"]:
            dependents = graph.get_dependents(target_component_id)
            boundary = [target_component_id] + dependents
            return RegenerationBoundary(
                target_component_id=target_component_id,
                boundary_components=boundary,
                reason=f"Structural modification of '{target_component_id}' propagates to {len(dependents)} dependent component(s): {dependents}.",
                impact_level=ImpactLevel.HIGH
            )

        return RegenerationBoundary(
            target_component_id=target_component_id,
            boundary_components=[target_component_id],
            reason="Isolated component modification",
            impact_level=ImpactLevel.LOW
        )
