from typing import Dict, Any, List, Optional
from ..core.procedural_types import PrimitiveType, QualityLevel, ConstructionPass
from ..core.procedural_schema import (
    AssetConstructionGraph, GraphNode, AssetDNA, GeometryReport, BuildManifest
)
from ..construction.procedural_asset_builder import ProceduralAssetBuilder
from ..adapter.blender_geometry_adapter import BlenderGeometryAdapter
from src.intent_specification_compiler.core.spec_schema import AssetSpec

class ProceduralAssetAPI:
    """
    Procedural Asset Build System API (AOE v32)
    
    Regla Fundamental:
    LA IA NO CREA DIRECTAMENTE LA GEOMETRÍA FINAL.
    EL MOTOR DETERMINISTA TOMA EL ASSETSPEC Y LO TRANSFORMA EN UN GRAFO ESTRUCTURADO
    (AssetConstructionGraph) CON SEMILLAS DESACOPLADAS Y REGENERACIÓN PARCIAL AISLADA.
    """
    def __init__(self):
        self.adapter = BlenderGeometryAdapter()

    def build_asset(self, spec: AssetSpec, dna: Optional[AssetDNA] = None) -> AssetConstructionGraph:
        graph = ProceduralAssetBuilder.build_house(spec, dna)
        self.adapter.stage_in_temp_collection(graph)
        return graph

    def regenerate_door_width(self, graph: AssetConstructionGraph, new_door_width: float) -> List[str]:
        return ProceduralAssetBuilder.regenerate_door_width(graph, new_door_width)

    def generate_geometry_report(self, graph: AssetConstructionGraph) -> GeometryReport:
        total_prims = sum(len(node.primitives) for node in graph.nodes.values())
        return GeometryReport(
            asset_id=graph.asset_id,
            triangle_count=total_prims * 12, # Estimación canónica de triángulos
            vertex_count=total_prims * 8,
            object_count=len(graph.nodes),
            materials=["STONE_FOUNDATION", "PLASTER_TIMBER", "WOOD_PLANKS", "THATCH_ROOF"],
            bounds={"width": 4.5, "depth": 4.0, "height": 4.60},
            quality_level=graph.quality_level,
            is_valid=True
        )

    def commit_asset(self, graph: AssetConstructionGraph) -> str:
        return self.adapter.commit_atomic(graph)
