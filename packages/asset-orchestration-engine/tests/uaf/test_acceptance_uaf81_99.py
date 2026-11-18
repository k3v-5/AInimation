"""
Acceptance Test Suite for UAF-81.99: Physics, Voronoi Fracturing & Chaos Destruction System.
Validates uniform and radial Voronoi seed clustering, hierarchical piece partitioning,
physical mass calculations by material density, anchor fields for structural stability,
kinetic blast impulse physics, Niagara debris presets, and UE5 GeometryCollection JSON export.
"""

import pytest
import tempfile
import json
from pathlib import Path

from uaf.chaos_destruction import (
    DestructionMaterialType,
    FracturePatternType,
    ClusterHierarchyLevel,
    AnchorMode,
    Vector3D,
    BoundingBox3D,
    VoronoiSite,
    FracturedPiece,
    AnchorFieldSpec,
    DebrisParticlePreset,
    GeometryCollectionSpec,
    ChaosDestructionBundle,
    VoronoiFractureEngine,
    ChaosGeometryCollectionCompiler,
    DebrisFieldEmitter,
    UE5ChaosExporter,
)


class TestAcceptanceUAF81_99:

    def test_uaf81_99_contracts_and_models(self):
        """Validates all Pydantic models with keyword arguments."""
        vec = Vector3D(x=2.0, y=3.0, z=1.0)
        assert vec.to_ue5_cm().x == 200.0

        box = BoundingBox3D(min_x=0.0, max_x=10.0, min_y=0.0, max_y=2.0, min_z=0.0, max_z=3.0)
        assert box.volume() == 60.0

        site = VoronoiSite(site_id="s1", position=vec, weight=1.0, cluster_id=0)
        assert site.site_id == "s1"

        piece = FracturedPiece(
            piece_id="p1",
            centroid=vec,
            volume_m3=0.05,
            mass_kg=120.0,
            cluster_level=ClusterHierarchyLevel.MACRO_CHUNK,
        )
        assert piece.mass_kg == 120.0

    def test_uaf81_99_material_properties_and_densities(self):
        """Verifies physical densities for all supported structural materials."""
        assert DestructionMaterialType.CONCRETE.density_kg_per_m3 == 2400.0
        assert DestructionMaterialType.MASONRY_BRICK.density_kg_per_m3 == 1900.0
        assert DestructionMaterialType.REINFORCED_METAL.density_kg_per_m3 == 7850.0
        assert DestructionMaterialType.TEMPERED_GLASS.density_kg_per_m3 == 2500.0
        assert DestructionMaterialType.STRUCTURAL_WOOD.density_kg_per_m3 == 650.0
        assert DestructionMaterialType.COMPOSITE_PLASTIC.density_kg_per_m3 == 1200.0

    def test_uaf81_99_bounding_box_volume_and_containment(self):
        """Tests bounding box volume, containment checks, and center calculation."""
        box = BoundingBox3D(min_x=-2.0, max_x=2.0, min_y=-1.0, max_y=1.0, min_z=0.0, max_z=4.0)
        assert box.volume() == 4.0 * 2.0 * 4.0  # 32.0 m3
        center = box.center()
        assert center.x == 0.0
        assert center.y == 0.0
        assert center.z == 2.0

        p_inside = Vector3D(x=0.0, y=0.0, z=1.0)
        p_outside = Vector3D(x=5.0, y=0.0, z=1.0)
        assert box.contains(p_inside) is True
        assert box.contains(p_outside) is False

    def test_uaf81_99_voronoi_uniform_site_generation(self):
        """Tests uniform distribution of Voronoi sites within bounds."""
        box = BoundingBox3D(min_x=0.0, max_x=5.0, min_y=0.0, max_y=5.0, min_z=0.0, max_z=3.0)
        sites = VoronoiFractureEngine.generate_uniform_sites(bounds=box, count=20, seed=101)

        assert len(sites) == 20
        for s in sites:
            assert box.contains(s.position, margin=0.01) is True

    def test_uaf81_99_voronoi_radial_cluster_generation(self):
        """Verifies that radial cluster sites concentrate near the impact point."""
        box = BoundingBox3D(min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0, min_z=0.0, max_z=3.0)
        impact = Vector3D(x=0.0, y=0.0, z=1.5)

        radial_sites = VoronoiFractureEngine.generate_radial_cluster_sites(
            bounds=box,
            impact_point=impact,
            count=30,
            decay_k=2.0,
            seed=202,
        )
        assert len(radial_sites) == 30

        # Compare average distance to impact with uniform sites
        uniform_sites = VoronoiFractureEngine.generate_uniform_sites(bounds=box, count=30, seed=202)
        avg_radial_dist = sum(s.position.distance_to(impact) for s in radial_sites) / len(radial_sites)
        avg_uniform_dist = sum(s.position.distance_to(impact) for s in uniform_sites) / len(uniform_sites)

        # Radial cluster must have significantly tighter concentration near impact point
        assert avg_radial_dist < avg_uniform_dist

    def test_uaf81_99_hierarchical_volume_partitioning(self):
        """Tests generation of Macro Chunks and Micro Debris with contact area graph."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=4.0, min_y=0.0, max_y=0.4, min_z=0.0, max_z=3.0)
        impact = Vector3D(x=2.0, y=0.2, z=1.5)

        sites = VoronoiFractureEngine.generate_radial_cluster_sites(
            bounds=wall_box,
            impact_point=impact,
            count=15,
            seed=303,
        )

        pieces = VoronoiFractureEngine.partition_volume_into_pieces(
            bounds=wall_box,
            sites=sites,
            impact_point=impact,
            micro_debris_radius_m=1.2,
        )

        assert len(pieces) == 15
        levels = {p.cluster_level for p in pieces}
        assert ClusterHierarchyLevel.MACRO_CHUNK in levels
        assert ClusterHierarchyLevel.MICRO_DEBRIS in levels

        # Check neighbor connectivity
        has_neighbors = any(len(p.neighbor_piece_ids) > 0 for p in pieces)
        assert has_neighbors is True

    def test_uaf81_99_chaos_compiler_mass_calculation(self):
        """Tests that piece mass is correctly calculated from material density and volume."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=2.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=2.0)
        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="GC_ConcreteWall",
            base_mesh_name="SM_Wall_400x300",
            bounds=wall_box,
            material_type=DestructionMaterialType.CONCRETE,
        )

        assert collection.density_kg_m3 == 2400.0
        for p in collection.pieces.values():
            expected_mass = round(p.volume_m3 * 2400.0, 3)
            assert round(p.mass_kg, 1) == round(expected_mass, 1)

    def test_uaf81_99_chaos_compiler_anchor_fields_base_grounded(self):
        """Verifies that ground anchor fields anchor bottom pieces while top pieces remain dynamic."""
        column_box = BoundingBox3D(min_x=0.0, max_x=1.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=4.0)

        # Base anchor on first 0.5 meters
        anchor = ChaosGeometryCollectionCompiler.create_anchor_field(
            bounds=column_box,
            mode=AnchorMode.BASE_GROUNDED,
            thickness_m=0.5,
        )

        sites = [
            VoronoiSite(site_id="s_bottom", position=Vector3D(x=0.5, y=0.5, z=0.2)),
            VoronoiSite(site_id="s_middle", position=Vector3D(x=0.5, y=0.5, z=2.0)),
            VoronoiSite(site_id="s_top", position=Vector3D(x=0.5, y=0.5, z=3.8)),
        ]

        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="GC_Pillar",
            base_mesh_name="SM_Pillar",
            bounds=column_box,
            sites=sites,
            anchor_fields=[anchor],
        )

        piece_bottom = collection.pieces["piece_s_bottom"]
        piece_top = collection.pieces["piece_s_top"]

        assert piece_bottom.is_anchored is True
        assert piece_top.is_anchored is False

    def test_uaf81_99_chaos_compiler_damage_thresholds(self):
        """Verifies that Macro Chunks require more energy to break than Micro Debris."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=3.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=3.0)
        impact = Vector3D(x=1.5, y=0.5, z=1.5)

        sites = [
            VoronoiSite(site_id="s_close", position=Vector3D(x=1.6, y=0.5, z=1.5)),  # Micro
            VoronoiSite(site_id="s_far", position=Vector3D(x=0.1, y=0.5, z=0.1)),    # Macro
        ]

        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="GC_ThresholdTest",
            base_mesh_name="SM_Wall",
            bounds=wall_box,
            sites=sites,
            impact_point=impact,
            macro_damage_threshold=2000.0,
            micro_damage_threshold=500.0,
        )

        p_close = collection.pieces["piece_s_close"]
        p_far = collection.pieces["piece_s_far"]

        assert p_far.damage_threshold_joules == 2000.0
        assert p_close.damage_threshold_joules == 500.0

    def test_uaf81_99_debris_kinetic_impulse_calculation(self):
        """Tests blast impulse velocity calculation with inverse square falloff."""
        impact = Vector3D(x=0.0, y=0.0, z=0.0)
        p_near = Vector3D(x=1.0, y=0.0, z=0.0)
        p_far = Vector3D(x=4.0, y=0.0, z=0.0)

        v_near = DebrisFieldEmitter.calculate_kinetic_impulse(
            piece_centroid=p_near,
            piece_mass_kg=10.0,
            impact_point=impact,
            blast_energy_joules=5000.0,
        )
        v_far = DebrisFieldEmitter.calculate_kinetic_impulse(
            piece_centroid=p_far,
            piece_mass_kg=10.0,
            impact_point=impact,
            blast_energy_joules=5000.0,
        )

        speed_near = (v_near.x**2 + v_near.y**2 + v_near.z**2)**0.5
        speed_far = (v_far.x**2 + v_far.y**2 + v_far.z**2)**0.5

        assert speed_near > speed_far
        # Direction should point away from impact
        assert v_near.x > 0.0

    def test_uaf81_99_material_niagara_presets(self):
        """Verifies customized particle emitter presets by material type."""
        preset_metal = DebrisFieldEmitter.get_preset_for_material(DestructionMaterialType.REINFORCED_METAL)
        preset_glass = DebrisFieldEmitter.get_preset_for_material(DestructionMaterialType.TEMPERED_GLASS)
        preset_concrete = DebrisFieldEmitter.get_preset_for_material(DestructionMaterialType.CONCRETE)

        assert preset_metal.spark_chance > 0.40
        assert preset_glass.spark_chance == 0.0
        assert preset_glass.particle_spawn_rate > preset_metal.particle_spawn_rate
        assert "Concrete" in preset_concrete.preset_name

    def test_uaf81_99_ue5_chaos_exporter_bundle_manifest(self):
        """Tests that exporter correctly maps pieces and anchor fields to UE5 cm coordinates."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=2.0, min_y=0.0, max_y=0.5, min_z=0.0, max_z=3.0)
        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="Vault_Blast_Door",
            base_mesh_name="SM_Door_Frame",
            bounds=wall_box,
            material_type=DestructionMaterialType.REINFORCED_METAL,
        )

        bundle = UE5ChaosExporter.build_chaos_bundle(collection)
        assert bundle.asset_name == "GC_Vault_Blast_Door"
        assert bundle.ue5_manifest["material_type"] == "REINFORCED_METAL"
        assert len(bundle.ue5_manifest["pieces"]) == collection.total_pieces

        # Centroids must be in cm (x 100)
        first_piece = bundle.ue5_manifest["pieces"][0]
        assert "centroid_cm" in first_piece
        assert "x" in first_piece["centroid_cm"]

    def test_uaf81_99_ue5_chaos_exporter_json_export(self):
        """Verifies JSON file export and format integrity."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=1.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=1.0)
        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="Test_Block",
            base_mesh_name="SM_Block",
            bounds=wall_box,
            material_type=DestructionMaterialType.MASONRY_BRICK,
        )
        bundle = UE5ChaosExporter.build_chaos_bundle(collection)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "Test_Block_Chaos.json"
            json_str = UE5ChaosExporter.export_to_json(bundle, out_file)

            assert out_file.exists()
            data = json.loads(json_str)
            assert data["asset_name"] == "GC_Test_Block"
            assert data["ue5_manifest"]["material_type"] == "MASONRY_BRICK"

    def test_uaf81_99_ue5_chaos_exporter_python_script(self):
        """Verifies Python editor automation script generation."""
        wall_box = BoundingBox3D(min_x=0.0, max_x=1.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=1.0)
        collection = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="Script_Test",
            base_mesh_name="SM_Test",
            bounds=wall_box,
        )
        bundle = UE5ChaosExporter.build_chaos_bundle(collection)
        script = UE5ChaosExporter.generate_ue5_import_script(bundle)

        assert "import unreal" in script
        assert "GeometryCollectionFactoryNew" in script
        assert "GC_Script_Test" in script

    def test_uaf81_99_different_structural_materials(self):
        """Tests physical compilation across multiple material types."""
        box = BoundingBox3D(min_x=0.0, max_x=1.0, min_y=0.0, max_y=1.0, min_z=0.0, max_z=1.0)

        col_metal = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="Metal_Prop",
            base_mesh_name="SM_Metal",
            bounds=box,
            material_type=DestructionMaterialType.REINFORCED_METAL,
        )
        col_wood = ChaosGeometryCollectionCompiler.compile_geometry_collection(
            collection_id="Wood_Prop",
            base_mesh_name="SM_Wood",
            bounds=box,
            material_type=DestructionMaterialType.STRUCTURAL_WOOD,
        )

        total_mass_metal = sum(p.mass_kg for p in col_metal.pieces.values())
        total_mass_wood = sum(p.mass_kg for p in col_wood.pieces.values())

        # Metal must be over 10x heavier than wood (7850 vs 650)
        assert total_mass_metal > total_mass_wood * 10.0
