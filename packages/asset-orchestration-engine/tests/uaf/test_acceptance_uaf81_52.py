"""
UAF-81.52 Acceptance Tests (Sections 143, 141, 144, 151, 152, 147, 150).
Verifies:
- Section 143: Final Acceptance Criteria (Generates and validates all 10 Golden Materials:
  Metal, Wood, Stone, Concrete, Fabric, Glass, Leather, Terrain, Vegetation, Water).
- Sections 141, 144, 151, 152: Hard Fail Conditions Test (Zero tolerance for PBR values outside [0, 1],
  non-POT resolution, missing core maps [normal, roughness, metallic, AO], or absolute machine-dependent paths;
  violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.universal_surface.engine.universal_surface_fabricator import UniversalSurfaceFabricationPlatform
from uaf.universal_surface.validation.universal_surface_validator import UniversalSurfaceValidator
from uaf.universal_surface.models.definition import (
    UniversalSurfaceSpecification,
    SurfaceType52,
    PBRSurfaceProperties52,
    TextureResolution52,
)
from uaf.universal_surface.package.universal_surface_package import UniversalSurfacePackage


def test_final_universal_surface_acceptance_section_143():
    """
    Acceptance Test Section 143:
    Synthesizes and validates all 10 Golden Materials.
    """
    builders = [
        ("Surf_Gold_Metal52", UniversalSurfaceFabricationPlatform.build_golden_metal),
        ("Surf_Gold_Wood52", UniversalSurfaceFabricationPlatform.build_golden_wood),
        ("Surf_Gold_Stone52", UniversalSurfaceFabricationPlatform.build_golden_stone),
        ("Surf_Gold_Concrete52", UniversalSurfaceFabricationPlatform.build_golden_concrete),
        ("Surf_Gold_Fabric52", UniversalSurfaceFabricationPlatform.build_golden_fabric),
        ("Surf_Gold_Glass52", UniversalSurfaceFabricationPlatform.build_golden_glass),
        ("Surf_Gold_Leather52", UniversalSurfaceFabricationPlatform.build_golden_leather),
        ("Surf_Gold_Terrain52", UniversalSurfaceFabricationPlatform.build_golden_terrain),
        ("Surf_Gold_Vegetation52", UniversalSurfaceFabricationPlatform.build_golden_vegetation),
        ("Surf_Gold_Water52", UniversalSurfaceFabricationPlatform.build_golden_water),
    ]

    for surf_id, builder_fn in builders:
        spec, mat_path, inst_path, tex_path = builder_fn(surf_id)
        assert spec.is_valid_surface is True

        report = UniversalSurfaceValidator.validate_universal_surface(spec, mat_path, inst_path, tex_path)
        assert report.is_valid is True, f"Failed for {surf_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = UniversalSurfacePackage(
            surface_id=surf_id,
            spec=spec,
            master_material_path=mat_path,
            material_instance_path=inst_path,
            texture_set_path=tex_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["surface_id"] == surf_id


def test_hard_fail_conditions_section_141_144_151_152():
    """
    Acceptance Test Sections 141, 144, 151, 152:
    Hard fail conditions:
    1. INVALID_PBR_RANGE: PBR parameter outside [0, 1].
    2. INVALID_RESOLUTION: Non-power-of-two resolution or < 128.
    3. MISSING_CORE_MAPS: Missing normal, roughness, metallic, or AO.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, mat_path, inst_path, tex_path = UniversalSurfaceFabricationPlatform.build_golden_metal("Surf_Fault_Test")

    # 1. PBR range violation: metallic = 1.5 (> 1.0)
    bad_props = PBRSurfaceProperties52(metallic=1.5)
    bad_spec_pbr = UniversalSurfaceSpecification(
        "Surf_PbrFault",
        SurfaceType52.METAL,
        properties=bad_props,
    )
    rep_pbr = UniversalSurfaceValidator.validate_universal_surface(bad_spec_pbr, mat_path, inst_path, tex_path)
    assert rep_pbr.is_valid is False
    assert rep_pbr.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PBR_RANGE" in iss for iss in rep_pbr.issues)

    # 2. Non-POT resolution: 1000x1000
    bad_res = TextureResolution52(width_px=1000, height_px=1000)
    bad_spec_res = UniversalSurfaceSpecification(
        "Surf_NonPot",
        SurfaceType52.METAL,
        resolution=bad_res,
    )
    rep_res = UniversalSurfaceValidator.validate_universal_surface(bad_spec_res, mat_path, inst_path, tex_path)
    assert rep_res.is_valid is False
    assert rep_res.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_RESOLUTION" in iss for iss in rep_res.issues)

    # 3. Missing core maps: normal map disabled
    bad_spec_maps = UniversalSurfaceSpecification(
        "Surf_NoMaps",
        SurfaceType52.METAL,
        has_normal=False,
    )
    rep_maps = UniversalSurfaceValidator.validate_universal_surface(bad_spec_maps, mat_path, inst_path, tex_path)
    assert rep_maps.is_valid is False
    assert rep_maps.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_CORE_MAPS" in iss for iss in rep_maps.issues)

    # 4. Path purity violation: Absolute machine path
    bad_mat_path = "D:\\UnrealProjects\\Materials\\M_Gold.uasset"
    rep_path = UniversalSurfaceValidator.validate_universal_surface(spec, bad_mat_path, inst_path, tex_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
