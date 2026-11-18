"""
UAF-81.82: Packaging and Unreal Engine 5 AI Interoperability Manifests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from ..engine.universal_runtime_ai_fabricator import UniversalRuntimeAIFabricator


class UniversalRuntimeAIPackager:
    """Packages headless AI world assets for interoperability with Unreal Engine 5."""

    @classmethod
    def package_ai_world(cls, fabricator: UniversalRuntimeAIFabricator) -> Dict[str, Any]:
        mesh = fabricator.navigation_world.nav_mesh

        # Export NavMesh
        nav_polys = []
        for pid in sorted(mesh.polygons.keys()):
            poly = mesh.polygons[pid]
            nav_polys.append({
                "PolygonId": poly.polygon_id,
                "Vertices": [[round(c, 5) for c in v] for v in poly.vertices],
                "Neighbors": list(poly.neighbors),
                "AreaType": poly.area_type,
                "TraversalCost": poly.traversal_cost,
            })

        # Export Agents
        agents_data = []
        for aid in sorted(fabricator.agents.keys()):
            a = fabricator.agents[aid]
            agents_data.append({
                "AgentId": a.agent_id,
                "EntityId": a.entity_id,
                "Position": [round(c, 5) for c in a.position],
                "Velocity": [round(c, 5) for c in a.velocity],
                "Radius": a.radius,
                "Height": a.height,
                "NavigationProfile": a.navigation_profile,
                "TeamId": a.team_id,
                "LOD": a.lod.value,
                "HasBehaviorTree": a.behavior_tree is not None,
            })

        # Assemble UE5 Manifest
        manifest = {
            "SchemaVersion": "1.0.0",
            "UAF_AI_System": "81.82",
            "WorldSeed": fabricator.world_seed,
            "SimulationTick": fabricator.current_tick,
            "WorldRevision": fabricator.world_revision,
            "UE5_NavMesh": {
                "PolygonCount": len(nav_polys),
                "Polygons": nav_polys,
            },
            "UE5_Agents": agents_data,
            "UE5_PerceptionConfig": {
                "DefaultVisionRange": 30.0,
                "DefaultVisionAngle": 120.0,
                "DefaultHearingRange": 50.0,
            },
        }

        raw_json = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        pkg_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        return {
            "package_hash": pkg_hash,
            "ue5_ai_manifest": manifest,
        }
