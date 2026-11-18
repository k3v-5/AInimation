"""
UAF-81.99: UE5 Chaos Destruction & GeometryCollection Exporter.
Serializes procedural GeometryCollection specifications into Unreal Engine 5 JSON manifests
and Python automation scripts for in-editor Chaos asset generation.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..core.contracts import (
    GeometryCollectionSpec,
    DebrisParticlePreset,
    ChaosDestructionBundle,
    DestructionMaterialType,
)
from ..debris.debris_emitter import DebrisFieldEmitter


class UE5ChaosExporter:
    """
    Exports physical GeometryCollection specifications into Unreal Engine 5 Chaos asset bundles.
    """

    @staticmethod
    def build_chaos_bundle(
        collection_spec: GeometryCollectionSpec,
        debris_preset: Optional[DebrisParticlePreset] = None,
    ) -> ChaosDestructionBundle:
        """
        Constructs a complete ChaosDestructionBundle with UE5-compatible manifest data.
        """
        debris_preset = debris_preset or DebrisFieldEmitter.get_preset_for_material(collection_spec.material_type)

        pieces_manifest: List[Dict[str, Any]] = []

        for p_id, piece in collection_spec.pieces.items():
            pos_ue5 = piece.centroid.to_ue5_cm()
            pieces_manifest.append(
                {
                    "piece_id": p_id,
                    "parent_piece_id": piece.parent_piece_id,
                    "cluster_level": piece.cluster_level.value,
                    "centroid_cm": {"x": round(pos_ue5.x, 2), "y": round(pos_ue5.y, 2), "z": round(pos_ue5.z, 2)},
                    "mass_kg": piece.mass_kg,
                    "volume_m3": piece.volume_m3,
                    "damage_threshold_joules": piece.damage_threshold_joules,
                    "is_anchored": piece.is_anchored,
                    "neighbor_count": len(piece.neighbor_piece_ids),
                    "neighbors": piece.neighbor_piece_ids,
                }
            )

        anchors_manifest = [
            {
                "field_id": af.field_id,
                "anchor_mode": af.anchor_mode.value,
                "bounding_box_cm": {
                    "min_x": af.bounding_box.min_x * 100.0,
                    "max_x": af.bounding_box.max_x * 100.0,
                    "min_y": af.bounding_box.min_y * 100.0,
                    "max_y": af.bounding_box.max_y * 100.0,
                    "min_z": af.bounding_box.min_z * 100.0,
                    "max_z": af.bounding_box.max_z * 100.0,
                },
                "stiffness": af.stiffness,
            }
            for af in collection_spec.anchor_fields
        ]

        ue5_manifest = {
            "asset_class": "GeometryCollection",
            "collection_name": collection_spec.collection_id,
            "base_mesh": collection_spec.base_mesh_name,
            "material_type": collection_spec.material_type.value,
            "density_kg_per_m3": collection_spec.density_kg_m3,
            "total_pieces": collection_spec.total_pieces,
            "macro_damage_threshold": collection_spec.macro_damage_threshold,
            "micro_damage_threshold": collection_spec.micro_damage_threshold,
            "pieces": pieces_manifest,
            "anchor_fields": anchors_manifest,
            "niagara_debris_preset": debris_preset.model_dump(),
        }

        asset_name = f"GC_{collection_spec.collection_id}"
        return ChaosDestructionBundle(
            asset_name=asset_name,
            collection_spec=collection_spec,
            debris_preset=debris_preset,
            ue5_manifest=ue5_manifest,
        )

    @staticmethod
    def export_to_json(
        bundle: ChaosDestructionBundle,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Serializes the destruction bundle into a structured JSON string and file.
        """
        json_str = json.dumps(bundle.model_dump(), indent=2)

        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(json_str, encoding="utf-8")

        return json_str

    @staticmethod
    def generate_ue5_import_script(bundle: ChaosDestructionBundle) -> str:
        """
        Generates Unreal Engine 5 Python automation script for importing the GeometryCollection.
        """
        return f'''# Auto-generated Unreal Engine 5 GeometryCollection Builder for {bundle.asset_name}
import unreal

def build_geometry_collection():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.GeometryCollectionFactoryNew()
    package_path = "/Game/DestructibleAssets"
    
    gc_asset = asset_tools.create_asset("{bundle.asset_name}", package_path, unreal.GeometryCollection, factory)
    print(f"Created GeometryCollection: {{gc_asset.get_path_name()}} with {bundle.collection_spec.total_pieces} pieces.")
    return gc_asset

if __name__ == "__main__":
    build_geometry_collection()
'''
