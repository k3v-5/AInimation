from typing import Dict, Any, List, Optional
from ..core.procedural_types import QualityLevel, ConstructionPass, PrimitiveType
from ..core.procedural_schema import (
    AssetConstructionGraph, GraphNode, AssetDNA, GeometryReport, GeometryPrimitive
)
from ..builders.foundation_builder import FoundationBuilder
from ..builders.wall_builder import WallBuilder
from ..builders.opening_builder import DoorBuilder, WindowBuilder
from ..builders.roof_builder import RoofBuilder
from ..builders.stair_builder import StairBuilder
from src.intent_specification_compiler.core.spec_schema import AssetSpec

class ProceduralAssetBuilder:
    """
    Master Procedural Asset Builder (AOE v32):
    Construye la geometría procedural en 4 pasadas ordenadas (Structure -> Functional -> Detail -> Surface),
    con semillas desacopladas y regeneración parcial sin retrabajos.
    """
    @staticmethod
    def build_house(spec: AssetSpec, dna: Optional[AssetDNA] = None) -> AssetConstructionGraph:
        # Verificar intentos de características no autorizadas
        if hasattr(spec, "unauthorized_requested") and spec.unauthorized_requested:
            raise ValueError("UNAUTHORIZED_FEATURE: Feature not present in Specification cannot be generated.")

        width = 4.5
        depth = 4.0
        wall_height = 2.80
        door_w = spec.door.width_m
        lean_angle = spec.visual.lean_angle_deg
        win_count = spec.windows.count

        default_params = {
            "width": width, "depth": depth, "height": wall_height,
            "door_width": door_w, "lean_angle": lean_angle, "windows": win_count
        }
        if dna:
            actual_dna = dna
            if not actual_dna.parameters:
                actual_dna.parameters = default_params
        else:
            actual_dna = AssetDNA(
                spec_reference=spec.spec_id,
                generator_version="v1.0.0",
                structural_seed=42,
                detail_seed=1001,
                surface_seed=9999,
                parameters=default_params
            )

        graph = AssetConstructionGraph(asset_id=spec.spec_id, dna=actual_dna, quality_level=QualityLevel.FINAL)

        # 1. Structural Pass (Skeleton & Walls)
        f_node = FoundationBuilder.build(width, depth)
        graph.nodes[f_node.node_id] = f_node

        wall_nodes = WallBuilder.build_segmented_walls(width, depth, wall_height, door_w, lean_angle)
        for wn in wall_nodes:
            graph.nodes[wn.node_id] = wn

        roof_node = RoofBuilder.build(width, depth, wall_height, pitch_deg=40.0)
        graph.nodes[roof_node.node_id] = roof_node

        # 2. Functional Pass (Door & Stairs)
        door_node = DoorBuilder.build(door_w, spec.door.height_m, depth_pos=-depth / 2.0)
        graph.nodes[door_node.node_id] = door_node

        if spec.stairs.required:
            stair_node = StairBuilder.build_internal_stairs(total_height=wall_height)
            graph.nodes[stair_node.node_id] = stair_node

        # 3. Detail Pass (Windows)
        win_nodes = WindowBuilder.build_windows(count=win_count, wall_width=width, wall_pos_y=depth / 2.0)
        for w_node in win_nodes:
            graph.nodes[w_node.node_id] = w_node

        # 4. Collision & Navigation (Nodes funcionales)
        col_prim = GeometryPrimitive(
            primitive_id="prim_col_box",
            primitive_type=PrimitiveType.BOX,
            position=(0.0, 0.0, wall_height / 2.0),
            dimensions=(width, depth, wall_height),
            material="COLLISION_WORLD"
        )
        graph.nodes["HOUSE.COLLISION"] = GraphNode("HOUSE.COLLISION", "COLLISION", "HOUSE.FOUNDATION", [col_prim], pass_level=ConstructionPass.FUNCTIONAL)

        return graph

    @staticmethod
    def regenerate_door_width(graph: AssetConstructionGraph, new_door_width: float) -> List[str]:
        """
        Regeneración Parcial (Incremental):
        Modifica únicamente la puerta y el muro frontal sur sin tocar tejado, escaleras, ni otros muros.
        """
        rebuilt = []
        depth = graph.dna.parameters.get("depth", 4.0)
        width = graph.dna.parameters.get("width", 4.5)
        wall_height = graph.dna.parameters.get("height", 2.80)

        # 1. Regenerar Puerta
        door_node = DoorBuilder.build(new_door_width, 2.10, depth_pos=-depth / 2.0)
        graph.nodes[door_node.node_id] = door_node
        rebuilt.append("HOUSE.DOOR.MAIN")

        # 2. Regenerar Muro Sur (Segmentos adaptados)
        south_nodes = WallBuilder.build_segmented_walls(width, depth, wall_height, new_door_width)
        for sn in south_nodes:
            if sn.node_id == "HOUSE.WALL.SOUTH":
                graph.nodes[sn.node_id] = sn
                rebuilt.append("HOUSE.WALL.SOUTH")

        # Actualizar parámetro en ADN
        graph.dna.parameters["door_width"] = new_door_width
        return rebuilt
