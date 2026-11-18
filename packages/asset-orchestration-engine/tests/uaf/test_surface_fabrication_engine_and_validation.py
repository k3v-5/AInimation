"""
Tests for Surface Fabrication Engine, Validator, and Package.
UAF-81.15 Sections 163, 177, 200, 211.
"""

from uaf.surface_fabrication.engine.fabrication_engine import SurfaceFabricationEngine
from uaf.surface_fabrication.validation.fabrication_validator import SurfaceFabricationValidator
from uaf.surface_fabrication.package.fabrication_package import SurfaceFabricationPackage


def test_fabrication_engine_ten_canonical_surfaces():
    builders = [
        SurfaceFabricationEngine.build_skin_surface,
        SurfaceFabricationEngine.build_metal_surface,
        SurfaceFabricationEngine.build_fabric_surface,
        SurfaceFabricationEngine.build_concrete_surface,
        SurfaceFabricationEngine.build_wood_surface,
        SurfaceFabricationEngine.build_stone_surface,
        SurfaceFabricationEngine.build_glass_surface,
        SurfaceFabricationEngine.build_vegetation_surface,
        SurfaceFabricationEngine.build_terrain_surface,
        SurfaceFabricationEngine.build_energy_surface,
    ]

    for builder in builders:
        prof, graph, textures = builder()
        assert prof.surface_type != ""
        assert graph.master_material_id != ""
        assert len(textures) > 0


def test_surface_fabrication_package_validation_and_serialization():
    prof, graph, textures = SurfaceFabricationEngine.build_metal_surface("Surf_Gold_Bar")

    report = SurfaceFabricationValidator.validate_surface_fabrication(prof, graph, textures)
    assert report.is_valid is True
    assert report.review_status == "PASSED"
    assert report.quality_score.aggregate_score >= 0.85

    pkg = SurfaceFabricationPackage(
        asset_id="Surf_Gold_Bar",
        surface_profile=prof,
        graph_contract=graph,
        textures=textures,
        validation_report=report,
    )

    assert len(pkg.package_hash) == 64
    data = pkg.to_dict()
    assert data["surface_profile"]["surface_type"] == "METAL"
    assert data["validation_report"]["review_status"] == "PASSED"
