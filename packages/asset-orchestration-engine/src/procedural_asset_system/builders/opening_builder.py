from typing import List
from ..core.procedural_types import PrimitiveType, ConstructionPass
from ..core.procedural_schema import GeometryPrimitive, GraphNode

class DoorBuilder:
    @staticmethod
    def build(width: float = 0.90, height: float = 2.10, depth_pos: float = -2.0) -> GraphNode:
        door_panel = GeometryPrimitive(
            primitive_id="prim_door_panel",
            primitive_type=PrimitiveType.PANEL,
            position=(0.0, depth_pos, height / 2.0 + 0.40),
            dimensions=(width - 0.05, 0.08, height),
            material="WOOD_PLANKS",
            tags=["DOOR", "INTERACTIVE"]
        )
        door_frame = GeometryPrimitive(
            primitive_id="prim_door_frame",
            primitive_type=PrimitiveType.FRAME,
            position=(0.0, depth_pos, height / 2.0 + 0.40),
            dimensions=(width + 0.10, 0.12, height + 0.10),
            material="TIMBER_FRAME",
            tags=["FRAME"]
        )
        return GraphNode(
            node_id="HOUSE.DOOR.MAIN",
            node_type="DOOR",
            parent_id="HOUSE.WALL.SOUTH",
            primitives=[door_panel, door_frame],
            parameters={"width": width, "height": height},
            pass_level=ConstructionPass.FUNCTIONAL,
            builder_owner="DoorBuilder"
        )

class WindowBuilder:
    @staticmethod
    def build_windows(count: int = 2, wall_width: float = 4.0, wall_pos_y: float = 0.0) -> List[GraphNode]:
        nodes = []
        for i in range(count):
            offset_x = -1.2 + (i * (2.4 / max(1, count - 1))) if count > 1 else 0.0
            w_node_id = f"HOUSE.WINDOW.{i+1:02d}"
            prim_win = GeometryPrimitive(
                primitive_id=f"prim_win_{i+1:02d}",
                primitive_type=PrimitiveType.FRAME,
                position=(round(offset_x, 2), wall_pos_y, 1.80),
                dimensions=(0.60, 0.15, 0.90),
                material="TIMBER_WINDOW",
                tags=["WINDOW"]
            )
            nodes.append(GraphNode(
                node_id=w_node_id,
                node_type="WINDOW",
                parent_id="HOUSE.WALL.EAST",
                primitives=[prim_win],
                parameters={"index": i + 1, "count": count},
                pass_level=ConstructionPass.DETAIL,
                builder_owner="WindowBuilder"
            ))
        return nodes
