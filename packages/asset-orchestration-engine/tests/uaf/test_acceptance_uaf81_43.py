"""
UAF-81.43 Acceptance Tests (Sections 149, 144, 158, 159, 160, 166, 178).
Verifies:
- Section 149: Final Acceptance Criteria (Generates and validates all 10 Golden Materials:
  Skin, Metal, Painted Metal, Fabric, Leather, Concrete, Glass, Organic, Emissive, Technical).
- Sections 144, 158, 159, 160: Hard Fail Conditions Test (Zero tolerance for PBR range violations, non-POT resolutions,
  missing normal/AO maps, or absolute machine-dependent paths; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.pbr_surface.engine.pbr_surface_fabricator import PBRSurfaceFabricationPlatform
from uaf.pbr_surface.validation.pbr_surface_validator import PBRSurfaceValidator
from uaf.pbr_surface.models.definition import (
    PBRSurfaceSpecification,
    MaterialCategory43,
    PBRProperties43,
)
from uaf.pbr_surface.package.pbr_surface_package import PBRSurfacePackage


def test_final_pbr_surface_acceptance_section_149():
    """
    Acceptance Test Section 149:
    Synthesizes and validates all 10 Golden Materials.
    """
    builders = [
        ("Mat_Gold_Skin", PBRSurfaceFabricationPlatform.build_golden_skin),
        ("Mat_Gold_Metal", PBRSurfaceFabricationPlatform.build_golden_metal),
        ("Mat_Gold_PaintedMetal", PBRSurfaceFabricationPlatform.build_golden_painted_metal),
        ("Mat_Gold_Fabric", PBRSurfaceFabricationPlatform.build_golden_fabric),
        ("Mat_Gold_Leather", PBRSurfaceFabricationPlatform.build_golden_leather),
        ("Mat_Gold_Concrete", PBRSurfaceFabricationPlatform.build_golden_concrete),
        ("Mat_Gold_Glass", PBRSurfaceFabricationPlatform.build_golden_glass),
        ("Mat_Gold_Organic", PBRSurfaceFabricationPlatform.build_golden_organic),
        ("Mat_Gold_Emissive", PBRSurfaceFabricationPlatform.build_golden_emissive),
        ("Mat_Gold_Technical", PBRSurfaceFabricationPlatform.build_golden_technical),
    ]

    for mat_id, builder_fn in builders:
        spec, master_path, mi_path, tex_path = builder_fn(mat_id)
        assert spec.is_valid_surface is True

        report = PBRSurfaceValidator.validate_pbr_surface(spec, master_path, mi_path, tex_path)
        assert report.is_valid is True, f"Failed for {mat_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = PBRSurfacePackage(
            material_id=mat_id,
            spec=spec,
            master_material_path=master_path,
            material_instance_path=mi_path,
            texture_set_path=tex_path,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["material_id"] == mat_id


def test_hard_fail_conditions_section_144_158_159_160():
    """
    Acceptance Test Sections 144, 158, 159, 160:
    Hard fail conditions:
    1. INVALID_PBR_RANGE: Metallic or roughness outside [0, 1], emissive < 0.
    2. INVALID_RESOLUTION: Non-power-of-two or < 256.
    3. MISSING_TEXTURE_MAPS: Missing normal map or AO map.
    4. Path purity: Absolute machine-dependent reference paths.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    spec, master_path, mi_path, tex_path = PBRSurfaceFabricationPlatform.build_golden_metal("Mat_Fault_Test")

    # 1. PBR range violation: metallic = 1.8
    bad_pbr_met = PBRProperties43(metallic=1.8)
    bad_spec_met = PBRSurfaceSpecification("Mat_BadMet", MaterialCategory43.METAL, pbr=bad_pbr_met)
    rep_met = PBRSurfaceValidator.validate_pbr_surface(bad_spec_met, master_path, mi_path, tex_path)
    assert rep_met.is_valid is False
    assert rep_met.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_PBR_RANGE" in iss for iss in rep_met.issues)

    # 2. Resolution violation: 500 (not POT)
    bad_pbr_res = PBRProperties43(resolution=500)
    bad_spec_res = PBRSurfaceSpecification("Mat_BadRes", MaterialCategory43.METAL, pbr=bad_pbr_res)
    rep_res = PBRSurfaceValidator.validate_pbr_surface(bad_spec_res, master_path, mi_path, tex_path)
    assert rep_res.is_valid is False
    assert rep_res.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("INVALID_RESOLUTION" in iss for iss in rep_res.issues)

    # 3. Missing texture maps
    bad_spec_map = PBRSurfaceSpecification("Mat_NoNormal", MaterialCategory43.METAL, has_normal_map=False)
    rep_map = PBRSurfaceValidator.validate_pbr_surface(bad_spec_map, master_path, mi_path, tex_path)
    assert rep_map.is_valid is False
    assert rep_map.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("MISSING_TEXTURE_MAPS" in iss for iss in rep_map.issues)

    # 4. Path purity violation: Absolute machine path
    bad_tex_path = "D:\\UnrealProjects\\Textures\\T_Metal_D.uasset"
    rep_path = PBRSurfaceValidator.validate_pbr_surface(spec, master_path, mi_path, bad_tex_path)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Absolute machine-dependent path" in iss for iss in rep_path.issues)
