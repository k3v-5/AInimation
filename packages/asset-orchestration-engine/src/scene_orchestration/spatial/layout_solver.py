import math
from typing import Dict, List, Tuple
from ..core.scene_schema import SceneIntent, ScenePlan, SceneNode, ProxyBounds

class LayoutSolver:
    @staticmethod
    def solve_layout(intent: SceneIntent) -> ScenePlan:
        plan = ScenePlan(scene_id=intent.scene_id, intent=intent, seed=intent.seed)
        nodes: Dict[str, SceneNode] = {}

        # 1. LANDMARKS: Plaza en el centro (Radio 5m)
        if intent.requirements.get("plaza", 0) > 0:
            nodes["plaza_001"] = SceneNode(
                node_id="plaza_001",
                asset_type="plaza",
                template_id="landmark.plaza.circular",
                variant_id="Medieval",
                role="LANDMARK",
                location=(0.0, 0.0, 0.0),
                bounds=ProxyBounds((-5.0, -5.0, 0.0), (5.0, 5.0, 1.0), radius=5.0)
            )

        # 2. LANDMARKS: Torre al Norte (y = 30m)
        if intent.requirements.get("tower", 0) > 0:
            nodes["tower_001"] = SceneNode(
                node_id="tower_001",
                asset_type="tower",
                template_id="structure.tower.stone",
                variant_id="Medieval",
                role="LANDMARK",
                location=(0.0, 30.0, 0.0),
                bounds=ProxyBounds((-3.0, 27.0, 0.0), (3.0, 33.0, 15.0), radius=3.0)
            )

        # 3. PRIMARY STRUCTURE: Herrería al Este (x = 30m)
        if intent.requirements.get("blacksmith", 0) > 0:
            nodes["blacksmith_001"] = SceneNode(
                node_id="blacksmith_001",
                asset_type="blacksmith",
                template_id="building.blacksmith.standard",
                variant_id="Medieval",
                role="PRIMARY",
                location=(30.0, 0.0, 0.0),
                bounds=ProxyBounds((27.0, -3.0, 0.0), (33.0, 3.0, 6.0), radius=3.0)
            )

        # 4. SECONDARY STRUCTURES: 8 Casas en Anillo (Radio 16m)
        num_houses = intent.requirements.get("houses", 8)
        radius = 16.0
        angle_step = (2 * math.pi) / max(1, num_houses)

        for i in range(num_houses):
            h_id = f"house_{i+1:03d}"
            angle = i * angle_step
            px = round(radius * math.cos(angle), 2)
            py = round(radius * math.sin(angle), 2)

            nodes[h_id] = SceneNode(
                node_id=h_id,
                asset_type="house",
                template_id="building.house.medieval",
                variant_id="Village",
                role="SECONDARY",
                location=(px, py, 0.0),
                rotation=(0.0, 0.0, round(math.degrees(angle + math.pi), 1)),
                bounds=ProxyBounds((px - 2.0, py - 2.0, 0.0), (px + 2.0, py + 2.0, 5.0), radius=2.0)
            )

        plan.nodes = nodes
        return plan
