from typing import Dict, Any, List, Optional
from ..graph.semantic_asset_graph import SemanticAssetGraph

class SemanticResolver:
    @classmethod
    def resolve_natural_reference(
        cls,
        graph: SemanticAssetGraph,
        query_text: str
    ) -> Optional[str]:
        t = query_text.lower()
        candidates = list(graph.nodes.values())

        # 1. Filtro semántico
        if "aro" in t or "anillo" in t or "ring" in t:
            candidates = [c for c in candidates if "ring" in c.semantic_type.lower()]
        elif "cuerpo" in t or "body" in t:
            candidates = [c for c in candidates if "body" in c.semantic_type.lower()]

        # 2. Filtro de material
        if "metálico" in t or "metal" in t or "hierro" in t:
            candidates = [c for c in candidates if "iron" in c.material_name.lower() or "metal" in c.material_name.lower()]
        elif "madera" in t or "wood" in t:
            candidates = [c for c in candidates if "wood" in c.material_name.lower()]

        # 3. Filtro espacial (arriba vs abajo)
        if "arriba" in t or "superior" in t or "top" in t:
            if candidates:
                candidates.sort(key=lambda c: c.transform.get("location", (0,0,0))[2], reverse=True)
                return candidates[0].component_id
        elif "abajo" in t or "inferior" in t or "bottom" in t:
            if candidates:
                candidates.sort(key=lambda c: c.transform.get("location", (0,0,0))[2])
                return candidates[0].component_id

        if candidates:
            return candidates[0].component_id

        return None
