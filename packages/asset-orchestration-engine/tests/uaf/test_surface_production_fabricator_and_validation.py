"""
Tests for Surface Production Fabricator, Validator, and Package.
UAF-81.18 Sections 211, 218, 220.
"""

from uaf.surface_production.models.definition import SurfaceDefinition, MaterialPBRProfile, SurfaceWeatheringState
from uaf.surface_production.engine.production_fabricator import SurfaceProductionFabricator
from uaf.surface_production.validation.production_validator import SurfaceProductionValidator
from uaf.surface_production.package.production_package import SurfaceProductionPackage


def test_surface_production_fabrication_and_validation():
    s_def = SurfaceDefinition("Surf_Titanium_Plate", "METAL", "TITANIUM", resolution=2048)
    mat_prof = MaterialPBRProfile(base_color_hex="#D0D0D0", metallic=0.95, roughness=0.25)

    uv_set, textures, master_id, inst_id, variants = SurfaceProductionFabricator.fabricate_surface("Mesh_Armor_Chest", s_def, mat_prof)

    assert uv_set == "Mesh_Armor_Chest_UVChannel_0"
    assert len(textures) >= 3
    assert master_id.startswith("M_Master_")
    assert inst_id == "MI_Surf_Titanium_Plate"
    assert "CLEAN" in variants

    report = SurfaceProductionValidator.validate_surface(uv_set, s_def, mat_prof, textures, master_id, inst_id, variants)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceProductionPackage(
        asset_id="Surf_Titanium_Plate",
        uv_set_name=uv_set,
        surface_def=s_def,
        material_profile=mat_prof,
        textures=textures,
        master_material_id=master_id,
        material_instance_id=inst_id,
        variants=variants,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["asset_id"] == "Surf_Titanium_Plate"
    assert len(data["textures"]) >= 3
    assert data["validation_report"]["review_status"] == "PASSED"
