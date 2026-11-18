from ..core.procedural_types import PrimitiveType, ConstructionPass
from ..core.procedural_schema import GeometryPrimitive, GraphNode

class StairBuilder:
    @staticmethod
    def build_internal_stairs(total_height: float = 2.50, step_count: int = 12, width: float = 1.0) -> GraphNode:
        riser = total_height / float(step_count)
        tread = 0.28
        prims = []
        for i in range(step_count):
            p = GeometryPrimitive(
                primitive_id=f"prim_stair_step_{i+1:02d}",
                primitive_type=PrimitiveType.STAIR,
                position=(0.0, round(i * tread, 2), round(i * riser + riser / 2.0 + 0.40, 2)),
                dimensions=(width, tread, riser),
                material="WOOD_PLANKS",
                tags=["STAIRS", "NAVIGATION"]
            )
            prims.append(p)

        return GraphNode(
            node_id="HOUSE.STAIRS",
            node_type="STAIR",
            parent_id="HOUSE.FOUNDATION",
            primitives=prims,
            parameters={"step_count": step_count, "riser_height": round(riser, 3), "tread_depth": tread},
            pass_level=ConstructionPass.FUNCTIONAL,
            builder_owner="StairBuilder"
        )
