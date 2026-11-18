from typing import Dict, Any, List, Optional
from ..core.twin_types import ReconciliationState, ComponentLifecycleState
from ..graph.semantic_asset_graph import SemanticAssetGraph

class DigitalTwinReconciler:
    @classmethod
    def reconcile(
        cls,
        graph: SemanticAssetGraph,
        blender_scene_objects: Dict[str, Dict[str, Any]],
        twin_modified_components: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        twin_modified = twin_modified_components or []
        state = ReconciliationState.SYNCHRONIZED
        orphaned = []
        blender_ahead = []
        conflicts = []

        for cid, node in graph.nodes.items():
            b_obj_name = node.blender_object_name
            if b_obj_name not in blender_scene_objects:
                node.lifecycle_state = ComponentLifecycleState.ORPHANED
                orphaned.append(cid)
                state = ReconciliationState.ORPHANED
            else:
                b_data = blender_scene_objects[b_obj_name]
                b_loc = b_data.get("transform", {}).get("location", (0,0,0))
                twin_loc = node.transform.get("location", (0,0,0))
                
                # Si la posición en Blender difiere
                if b_loc != twin_loc:
                    if cid in twin_modified:
                        conflicts.append(cid)
                        state = ReconciliationState.CONFLICT
                    else:
                        blender_ahead.append(cid)
                        if state != ReconciliationState.CONFLICT:
                            state = ReconciliationState.BLENDER_AHEAD

        return {
            "state": state,
            "orphaned_components": orphaned,
            "blender_ahead_components": blender_ahead,
            "conflict_components": conflicts
        }
