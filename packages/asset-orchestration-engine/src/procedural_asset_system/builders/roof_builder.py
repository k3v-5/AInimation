from ..core.procedural_types import PrimitiveType, ConstructionPass
from ..core.procedural_schema import GeometryPrimitive, GraphNode

class RoofBuilder:
    @staticmethod
    def build(width: float, depth: float, wall_height: float, pitch_deg: float = 40.0, overhang: float = 0.40) -> GraphNode:
        roof_h = 1.80
        prim_roof = GeometryPrimitive(
            primitive_id="prim_roof_gable",
            primitive_type=PrimitiveType.ROOF_SECTION,
            position=(0.0, 0.0, wall_height + roof_h / 2.0 + 0.40),
            dimensions=(width + overhang * 2.0, depth + overhang * 2.0, roof_h),
            material="THATCH_ROOF",
            tags=["ROOF", "STRUCTURE"]
        )
        return GraphNode(
            node_id="HOUSE.ROOF",
            node_type="ROOF",
            parent_id="HOUSE.WALL.NORTH",
            primitives=[prim_roof],
            parameters={"pitch_deg": pitch_deg, "overhang": overhang},
            pass_level=ConstructionPass.STRUCTURAL,
            builder_owner="RoofBuilder"
        )
