"""
UAF-81.99: Chaos GeometryCollection Compiler.
Assembles fractured Voronoi pieces, computes physical mass and material properties,
assigns hierarchical damage thresholds, and applies Anchor Fields for structural stability.
"""

from typing import Dict, List, Optional

from ..core.contracts import (
    BoundingBox3D,
    Vector3D,
    VoronoiSite,
    FracturedPiece,
    AnchorFieldSpec,
    AnchorMode,
    DestructionMaterialType,
    ClusterHierarchyLevel,
    GeometryCollectionSpec,
)
from ..fracture.voronoi_engine import VoronoiFractureEngine


class ChaosGeometryCollectionCompiler:
    """
    Compiles raw geometric Voronoi tessellations into physically simulated Chaos GeometryCollections.
    """

    @staticmethod
    def create_anchor_field(
        bounds: BoundingBox3D,
        mode: AnchorMode = AnchorMode.BASE_GROUNDED,
        thickness_m: float = 0.3,
    ) -> AnchorFieldSpec:
        """
        Creates an anchor volume to secure a structure to the floor, ceiling, or lateral supports.
        """
        if mode == AnchorMode.BASE_GROUNDED:
            anchor_box = BoundingBox3D(
                min_x=bounds.min_x,
                max_x=bounds.max_x,
                min_y=bounds.min_y,
                max_y=bounds.max_y,
                min_z=bounds.min_z,
                max_z=bounds.min_z + thickness_m,
            )
        elif mode == AnchorMode.CEILING_SUSPENDED:
            anchor_box = BoundingBox3D(
                min_x=bounds.min_x,
                max_x=bounds.max_x,
                min_y=bounds.min_y,
                max_y=bounds.max_y,
                min_z=bounds.max_z - thickness_m,
                max_z=bounds.max_z,
            )
        elif mode == AnchorMode.LATERAL_PILLARS:
            anchor_box = BoundingBox3D(
                min_x=bounds.min_x,
                max_x=bounds.min_x + thickness_m,
                min_y=bounds.min_y,
                max_y=bounds.max_y,
                min_z=bounds.min_z,
                max_z=bounds.max_z,
            )
        else:
            # None / Empty dynamic box
            anchor_box = BoundingBox3D(min_x=0.0, max_x=0.0, min_y=0.0, max_y=0.0, min_z=0.0, max_z=0.0)

        return AnchorFieldSpec(
            field_id=f"anchor_{mode.value.lower()}",
            anchor_mode=mode,
            bounding_box=anchor_box,
            stiffness=1.0,
        )

    @staticmethod
    def compile_geometry_collection(
        collection_id: str,
        base_mesh_name: str,
        bounds: BoundingBox3D,
        material_type: DestructionMaterialType = DestructionMaterialType.CONCRETE,
        sites: Optional[List[VoronoiSite]] = None,
        anchor_fields: Optional[List[AnchorFieldSpec]] = None,
        impact_point: Optional[Vector3D] = None,
        macro_damage_threshold: float = 1200.0,
        micro_damage_threshold: float = 350.0,
    ) -> GeometryCollectionSpec:
        """
        Generates and compiles a full GeometryCollectionSpec with calculated mass and anchors.
        """
        sites = sites or VoronoiFractureEngine.generate_uniform_sites(bounds, count=12)
        anchor_fields = anchor_fields or [ChaosGeometryCollectionCompiler.create_anchor_field(bounds)]

        raw_pieces = VoronoiFractureEngine.partition_volume_into_pieces(
            bounds=bounds,
            sites=sites,
            impact_point=impact_point,
        )

        pieces_dict: Dict[str, FracturedPiece] = {}
        density = material_type.density_kg_per_m3

        for piece in raw_pieces:
            # Physical mass: volume * density
            mass = round(max(0.01, piece.volume_m3 * density), 3)
            piece.mass_kg = mass

            # Damage threshold
            if piece.cluster_level == ClusterHierarchyLevel.MACRO_CHUNK:
                piece.damage_threshold_joules = macro_damage_threshold
            else:
                piece.damage_threshold_joules = micro_damage_threshold

            # Anchor check: is centroid inside any anchor field?
            piece.is_anchored = any(
                af.bounding_box.contains(piece.centroid, margin=0.05) for af in anchor_fields
            )

            pieces_dict[piece.piece_id] = piece

        return GeometryCollectionSpec(
            collection_id=collection_id,
            base_mesh_name=base_mesh_name,
            material_type=material_type,
            total_pieces=len(pieces_dict),
            pieces=pieces_dict,
            density_kg_m3=density,
            macro_damage_threshold=macro_damage_threshold,
            micro_damage_threshold=micro_damage_threshold,
            anchor_fields=anchor_fields,
        )
