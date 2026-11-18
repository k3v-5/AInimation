"""
Tests for Surface Detail Fabricator, Validator, and Package.
UAF-81.22 Sections 146, 153, 156, 157.
"""

from uaf.surface_detail.engine.detail_fabricator import SurfaceDetailFabricationPlatform
from uaf.surface_detail.validation.detail_validator import SurfaceDetailValidator
from uaf.surface_detail.package.detail_package import SurfaceDetailPackage


def test_surface_detail_fabrication_all_fifteen_required_surfaces():
    builders = [
        SurfaceDetailFabricationPlatform.build_painted_metal_with_wear,
        SurfaceDetailFabricationPlatform.build_corroded_metal,
        SurfaceDetailFabricationPlatform.build_fabric_material,
        SurfaceDetailFabricationPlatform.build_leather_material,
        SurfaceDetailFabricationPlatform.build_skin_material,
        SurfaceDetailFabricationPlatform.build_concrete_material,
        SurfaceDetailFabricationPlatform.build_wood_material,
        SurfaceDetailFabricationPlatform.build_glass_material,
        SurfaceDetailFabricationPlatform.build_emissive_material,
        SurfaceDetailFabricationPlatform.build_procedural_tileable_material,
        SurfaceDetailFabricationPlatform.build_trim_sheet_material,
        SurfaceDetailFabricationPlatform.build_texture_atlas_material,
        SurfaceDetailFabricationPlatform.build_decal_set_material,
        SurfaceDetailFabricationPlatform.build_multilayer_composite_material,
        SurfaceDetailFabricationPlatform.build_highpoly_baked_material,
    ]

    for builder in builders:
        s_def, textures, master_id, inst_id = builder()
        assert len(textures) >= 3
        assert master_id.startswith("M_Master_")
        assert inst_id.startswith("MI_")


def test_surface_detail_package_validation_and_serialization():
    s_def, textures, master_id, inst_id = SurfaceDetailFabricationPlatform.build_painted_metal_with_wear("Surf_PkgMetal")

    report = SurfaceDetailValidator.validate_surface(s_def, textures, master_id, inst_id)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceDetailPackage(
        asset_id="Surf_PkgMetal",
        surface_def=s_def,
        textures=textures,
        master_material_id=master_id,
        material_instance_id=inst_id,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Surf_PkgMetal"
    assert len(data["textures"]) >= 3
    assert data["validation_report"]["review_status"] == "PASSED"
