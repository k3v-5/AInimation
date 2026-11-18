from typing import List, Dict, Any, Optional
from ..core.critic_types import CausalCategory
from ..core.critic_schema import DefectCluster

class DefectClusterer:
    @classmethod
    def cluster_defects(
        cls,
        visual_defects: List[Any],
        geometric_defects: List[Any]
    ) -> List[DefectCluster]:
        clusters: List[DefectCluster] = []
        clusters_by_comp: Dict[str, DefectCluster] = {}

        for vd in visual_defects:
            region = getattr(vd, "region", "root")
            v_id = getattr(vd, "defect_id", "V_DEF")
            if region not in clusters_by_comp:
                clusters_by_comp[region] = DefectCluster(
                    cluster_id=f"CLUSTER_{region.upper()}",
                    name=f"DEFECT_CLUSTER_{region.upper()}",
                    primary_category=CausalCategory.PROPORTION,
                    visual_defects=[v_id],
                    geometric_defects=[],
                    affected_components=[region]
                )
            else:
                clusters_by_comp[region].visual_defects.append(v_id)

        for gd in geometric_defects:
            loc = getattr(gd, "location", "root")
            g_id = getattr(gd, "defect_id", "G_DEF")
            matching_key = "root"
            for k in clusters_by_comp.keys():
                if k in loc or loc in k:
                    matching_key = k
                    break

            if matching_key in clusters_by_comp:
                clusters_by_comp[matching_key].geometric_defects.append(g_id)
            else:
                clusters_by_comp[loc] = DefectCluster(
                    cluster_id=f"CLUSTER_{loc.upper()}",
                    name=f"DEFECT_CLUSTER_{loc.upper()}",
                    primary_category=CausalCategory.TOPOLOGY,
                    visual_defects=[],
                    geometric_defects=[g_id],
                    affected_components=[loc]
                )

        return list(clusters_by_comp.values())
