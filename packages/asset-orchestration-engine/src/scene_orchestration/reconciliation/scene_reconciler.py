from typing import Dict, List, Tuple, Any
from ..core.scene_graph import SceneGraph
from ..core.scene_status import ReconciliationStatus
from ...correction_execution.providers.blender_provider import IBlenderProvider

class SceneReconciler:
    @staticmethod
    def reconcile_scene(scene_id: str, graph: SceneGraph, provider: IBlenderProvider) -> Dict[str, Any]:
        result = {
            "status": ReconciliationStatus.MATCH,
            "missing_assets": [],
            "orphan_assets": [],
            "matched_assets": []
        }

        graph_ids = {f"{scene_id}_{nid}": nid for nid in graph.nodes}
        provider_ids = set(provider.assets.keys())

        # Missing check (en graph pero no en provider)
        for full_id, nid in graph_ids.items():
            if full_id not in provider_ids:
                result["missing_assets"].append(nid)
            else:
                result["matched_assets"].append(nid)

        # Orphan check (en provider con prefijo de escena pero no en graph)
        prefix = f"{scene_id}_"
        for p_id in provider_ids:
            if p_id.startswith(prefix) and p_id not in graph_ids:
                result["orphan_assets"].append(p_id)

        if result["missing_assets"]:
            result["status"] = ReconciliationStatus.MISSING
        elif result["orphan_assets"]:
            result["status"] = ReconciliationStatus.ORPHAN

        return result
