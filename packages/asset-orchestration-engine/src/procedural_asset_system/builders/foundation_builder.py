from ..core.procedural_types import PrimitiveType, ConstructionPass
from ..core.procedural_schema import GeometryPrimitive, GraphNode

class FoundationBuilder:
    @staticmethod
    def build(width: float, depth: float, height: float = 0.40) -> GraphNode:
        prim = GeometryPrimitive(
            primitive_id="prim_foundation_01",
            primitive_type=PrimitiveType.BOX,
            position=(0.0, 0.0, height / 2.0),
            dimensions=(width + 0.20, depth + 0.20, height),
            material="STONE_FOUNDATION",
            tags=["FOUNDATION", "STRUCTURE"]
        )
        return GraphNode(
            node_id="HOUSE.FOUNDATION",
            node_type="FOUNDATION",
            primitives=[prim],
            parameters={"width": width, "depth": depth, "height": height},
            pass_level=ConstructionPass.STRUCTURAL,
            builder_owner="FoundationBuilder"
        )
