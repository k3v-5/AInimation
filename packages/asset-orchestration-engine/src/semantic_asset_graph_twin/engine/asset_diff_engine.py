from typing import Dict, Any, List, Optional
from ..core.twin_types import DiffType
from ..core.twin_schema import AssetSnapshot, SemanticDiff

class AssetDiffEngine:
    @classmethod
    def compute_diff(cls, snapshot_a: AssetSnapshot, snapshot_b: AssetSnapshot) -> List[SemanticDiff]:
        diffs = []
        # Nodos añadidos / modificados en B
        for cid, node_b in snapshot_b.nodes.items():
            if cid not in snapshot_a.nodes:
                diffs.append(SemanticDiff(
                    diff_type=DiffType.COMPONENT_ADDED,
                    component_id=cid,
                    previous_value=None,
                    new_value=node_b.semantic_id,
                    description=f"Component '{cid}' added."
                ))
            else:
                node_a = snapshot_a.nodes[cid]
                if node_a.transform != node_b.transform:
                    diffs.append(SemanticDiff(
                        diff_type=DiffType.COMPONENT_TRANSFORM_CHANGED,
                        component_id=cid,
                        previous_value=node_a.transform,
                        new_value=node_b.transform,
                        description=f"Transform changed for '{cid}'."
                    ))
                if node_a.material_name != node_b.material_name:
                    diffs.append(SemanticDiff(
                        diff_type=DiffType.MATERIAL_CHANGED,
                        component_id=cid,
                        previous_value=node_a.material_name,
                        new_value=node_b.material_name,
                        description=f"Material changed for '{cid}'."
                    ))

        # Nodos eliminados en B
        for cid, node_a in snapshot_a.nodes.items():
            if cid not in snapshot_b.nodes:
                diffs.append(SemanticDiff(
                    diff_type=DiffType.COMPONENT_REMOVED,
                    component_id=cid,
                    previous_value=node_a.semantic_id,
                    new_value=None,
                    description=f"Component '{cid}' removed."
                ))

        return diffs
