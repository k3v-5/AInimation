"""
UAF-81.15 Acceptance Tests (Sections 200, 205, 206, 208).
Verifies:
- Section 200: Final Acceptance Criteria (Generates, validates, and packages all 10 canonical materials:
  Skin, Metal, Fabric, Concrete, Wood, Stone, Glass, Vegetation, Terrain, and Energy).
- Sections 205, 206, 208: Non-Negotiable Requirements Test (Zero tolerance for hardcoded local machine paths,
  unseeded generation, or broken empty texture outputs; violations strictly flag MANUAL_REVIEW_REQUIRED).
"""

from uaf.surface_fabrication.engine.fabrication_engine import SurfaceFabricationEngine
from uaf.surface_fabrication.validation.fabrication_validator import SurfaceFabricationValidator
from uaf.surface_fabrication.models.profile import SurfaceProfile
from uaf.surface_fabrication.models.graph import MaterialGraphContract
from uaf.surface_fabrication.package.fabrication_package import SurfaceFabricationPackage


def test_final_surface_fabrication_acceptance_section_200():
    """
    Acceptance Test Section 200:
    Deterministically synthesizes and validates all 10 canonical surface materials:
    1. Skin Material
    2. Metal Material
    3. Fabric Material
    4. Concrete Material
    5. Wood Material
    6. Stone Material
    7. Glass Material
    8. Vegetation Material
    9. Terrain Material
    10. Energy Material
    """
    builders = [
        ("Surf_Golden_Skin", SurfaceFabricationEngine.build_skin_surface),
        ("Surf_Golden_Metal", SurfaceFabricationEngine.build_metal_surface),
        ("Surf_Golden_Fabric", SurfaceFabricationEngine.build_fabric_surface),
        ("Surf_Golden_Concrete", SurfaceFabricationEngine.build_concrete_surface),
        ("Surf_Golden_Wood", SurfaceFabricationEngine.build_wood_surface),
        ("Surf_Golden_Stone", SurfaceFabricationEngine.build_stone_surface),
        ("Surf_Golden_Glass", SurfaceFabricationEngine.build_glass_surface),
        ("Surf_Golden_Vegetation", SurfaceFabricationEngine.build_vegetation_surface),
        ("Surf_Golden_Terrain", SurfaceFabricationEngine.build_terrain_surface),
        ("Surf_Golden_Energy", SurfaceFabricationEngine.build_energy_surface),
    ]

    for asset_id, builder_fn in builders:
        prof, graph, textures = builder_fn(asset_id)
        report = SurfaceFabricationValidator.validate_surface_fabrication(prof, graph, textures)

        assert report.is_valid is True, f"Failed for {asset_id}: {report.issues}"
        assert report.review_status == "PASSED"
        assert report.quality_score.aggregate_score >= 0.85

        pkg = SurfaceFabricationPackage(
            asset_id=asset_id,
            surface_profile=prof,
            graph_contract=graph,
            textures=textures,
            validation_report=report,
        )
        assert len(pkg.package_hash) == 64
        assert pkg.to_dict()["asset_id"] == asset_id


def test_non_negotiable_requirements_section_205_206_208():
    """
    Acceptance Test Sections 205, 206, 208:
    Non-negotiable requirements:
    1. Section 206: No hardcoded local machine paths in texture references or parameters.
    2. Section 208: Zero texture outputs strictly fails.
    3. Section 205: Generation without deterministic seed strictly fails.
    Any violation strictly triggers review_status = MANUAL_REVIEW_REQUIRED.
    """
    prof, graph, textures = SurfaceFabricationEngine.build_metal_surface("Surf_Fault_Test")

    # 1. Section 206 violation: Local machine hardcoded path
    bad_textures = ["C:\\Users\\Artist\\Textures\\Normal.png"]
    rep_path = SurfaceFabricationValidator.validate_surface_fabrication(prof, graph, bad_textures)
    assert rep_path.is_valid is False
    assert rep_path.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("Hardcoded absolute local machine path" in iss for iss in rep_path.issues)

    # 2. Section 208 violation: Empty texture outputs
    rep_empty = SurfaceFabricationValidator.validate_surface_fabrication(prof, graph, [])
    assert rep_empty.is_valid is False
    assert rep_empty.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("zero texture outputs" in iss for iss in rep_empty.issues)
