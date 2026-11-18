from typing import List
from ..core.procedural_types import PrimitiveType, ConstructionPass
from ..core.procedural_schema import GeometryPrimitive, GraphNode

class WallBuilder:
    @staticmethod
    def build_segmented_walls(
        width: float,
        depth: float,
        height: float,
        door_width: float = 0.90,
        lean_angle_deg: float = 0.0
    ) -> List[GraphNode]:
        """
        Construye paredes segmentadas dejando espacio estructural para la puerta frontal (sur).
        """
        nodes = []
        thickness = 0.25
        rot_y = round(lean_angle_deg, 2) # Inclinación controlada

        # 1. Pared Norte (Sólida)
        p_north = GeometryPrimitive(
            primitive_id="prim_wall_north",
            primitive_type=PrimitiveType.BOX,
            position=(0.0, depth / 2.0, height / 2.0 + 0.40),
            rotation=(0.0, rot_y, 0.0),
            dimensions=(width, thickness, height),
            material="PLASTER_TIMBER"
        )
        nodes.append(GraphNode(
            node_id="HOUSE.WALL.NORTH",
            node_type="WALL",
            parent_id="HOUSE.FOUNDATION",
            primitives=[p_north],
            builder_owner="WallBuilder"
        ))

        # 2. Pared Sur (Segmentada: Izquierda, Apertura Puerta, Derecha, Dintel Superior)
        side_w = (width - door_width) / 2.0
        p_south_left = GeometryPrimitive(
            primitive_id="prim_wall_south_left",
            primitive_type=PrimitiveType.BOX,
            position=(-(width / 2.0 - side_w / 2.0), -depth / 2.0, height / 2.0 + 0.40),
            dimensions=(side_w, thickness, height),
            material="PLASTER_TIMBER"
        )
        p_south_right = GeometryPrimitive(
            primitive_id="prim_wall_south_right",
            primitive_type=PrimitiveType.BOX,
            position=((width / 2.0 - side_w / 2.0), -depth / 2.0, height / 2.0 + 0.40),
            dimensions=(side_w, thickness, height),
            material="PLASTER_TIMBER"
        )
        p_south_top = GeometryPrimitive(
            primitive_id="prim_wall_south_top",
            primitive_type=PrimitiveType.BOX,
            position=(0.0, -depth / 2.0, height - 0.30 + 0.40),
            dimensions=(door_width, thickness, 0.60),
            material="PLASTER_TIMBER"
        )
        nodes.append(GraphNode(
            node_id="HOUSE.WALL.SOUTH",
            node_type="WALL",
            parent_id="HOUSE.FOUNDATION",
            primitives=[p_south_left, p_south_right, p_south_top],
            builder_owner="WallBuilder"
        ))

        # 3. Paredes Este y Oeste
        p_east = GeometryPrimitive(
            primitive_id="prim_wall_east",
            primitive_type=PrimitiveType.BOX,
            position=(width / 2.0, 0.0, height / 2.0 + 0.40),
            dimensions=(thickness, depth, height),
            material="PLASTER_TIMBER"
        )
        nodes.append(GraphNode("HOUSE.WALL.EAST", "WALL", "HOUSE.FOUNDATION", [p_east], builder_owner="WallBuilder"))

        p_west = GeometryPrimitive(
            primitive_id="prim_wall_west",
            primitive_type=PrimitiveType.BOX,
            position=(-width / 2.0, 0.0, height / 2.0 + 0.40),
            dimensions=(thickness, depth, height),
            material="PLASTER_TIMBER"
        )
        nodes.append(GraphNode("HOUSE.WALL.WEST", "WALL", "HOUSE.FOUNDATION", [p_west], builder_owner="WallBuilder"))

        return nodes
