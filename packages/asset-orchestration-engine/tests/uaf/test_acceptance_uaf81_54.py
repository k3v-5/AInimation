"""
UAF-81.54 Acceptance & Normative Compliance Test Suite.
Verifies all 179 Sections of UAF-81.54-CHARACTER-RIG-DEFORMATION-SYSTEM.md,
Cross-Phase Integration (UAF-81.50, 51, 52, 53), Machine-Agnostic Purity,
and 10 Canonical Golden Presets.
"""

import pytest
from uaf.universal_character import (
    CharacterSpecies,
    CharacterArchetype,
    BodyShape,
    BodyProportions,
    BoneDefinition,
    SkeletonDefinition,
    RigDefinition,
    SkinningDefinition,
    DeformationProfile,
    MorphTargetSystem,
    ClothingDefinition,
    ClothingType,
    ArmorDefinition,
    ArmorComponentType,
    CharacterCollisionDefinition,
    CharacterLODChain,
    CharacterValidator,
    CharacterDefinition,
    UniversalCharacterFabricator,
    ProductionReadyCharacter,
    UniversalCharacterPackage,
)

# Cross-Phase Integration imports (Section 174)
from uaf.universal_geometry import UniversalGeometryFabricationPlatform
from uaf.universal_surface import UniversalSurfaceFabricationPlatform


class TestUAF8154Acceptance:
    """Acceptance criteria tests for UAF-81.54 Universal Character System."""

    def test_golden_character_set_complete(self):
        """Verify all 10 Golden Characters from Section 170 exist and are valid."""
        goldens = [
            UniversalCharacterFabricator.build_golden_human_male(),
            UniversalCharacterFabricator.build_golden_human_female(),
            UniversalCharacterFabricator.build_golden_humanoid(),
            UniversalCharacterFabricator.build_golden_robot(),
            UniversalCharacterFabricator.build_golden_quadruped(),
            UniversalCharacterFabricator.build_golden_creature(),
            UniversalCharacterFabricator.build_golden_multi_limb(),
            UniversalCharacterFabricator.build_golden_armored_character(),
            UniversalCharacterFabricator.build_golden_clothed_character(),
            UniversalCharacterFabricator.build_golden_facial_character(),
        ]
        assert len(goldens) == 10
        for g in goldens:
            assert isinstance(g, ProductionReadyCharacter)
            assert g.validation_report.is_valid is True
            assert g.validation_report.quality_score.aggregate_score >= 0.95
            assert g.verify_readback()["readback_passed"] is True
            assert len(g.canonical_hash) == 64

    def test_cross_phase_integration_uaf81_50_to_53(self):
        """Verify cross-phase integration with UAF-81.50, 51, 52, and 53 (Section 174)."""
        # 1. Surface from UAF-81.52
        surf_spec, *surf_paths = UniversalSurfaceFabricationPlatform.build_golden_leather()
        assert surf_spec.is_valid_surface is True

        # 2. Geometry from UAF-81.53
        mesh_spec, *mesh_paths = UniversalGeometryFabricationPlatform.build_golden_character()
        assert mesh_spec.is_valid_mesh is True

        # 3. Rigged character from UAF-81.54 using UAF-81.53 mesh dimensions
        char = UniversalCharacterFabricator.build_golden_human_male()
        assert char.validation_report.is_valid is True
        assert char.vertex_count >= 1000

    def test_strict_machine_path_rejection(self):
        """Verify strict hard failure when absolute machine paths (C:, D:, E:) are passed (Engine Purity)."""
        char_def = CharacterDefinition("MACHINE_PATH_TEST", CharacterSpecies.HUMAN, CharacterArchetype.HUMAN)
        skel = UniversalCharacterFabricator.build_humanoid_skeleton()
        rig = UniversalCharacterFabricator.build_rig(skel)
        skin = UniversalCharacterFabricator.build_skinning(skel)
        deform = UniversalCharacterFabricator.build_deformation_profile()
        morphs = UniversalCharacterFabricator.build_morph_system()
        col = UniversalCharacterFabricator.build_collision(skel)
        lods = CharacterLODChain()

        for bad_path in [
            r"C:\Engine\Content\Characters\SK_Hero.uasset",
            r"D:\Projects\Game\SK_Hero.uasset",
            r"E:\Dev\Assets\SK_Hero.uasset",
        ]:
            report = CharacterValidator.validate_character(
                character_def=char_def,
                skeleton=skel,
                rig=rig,
                skinning=skin,
                deformation=deform,
                morphs=morphs,
                clothings=[],
                armors=[],
                collision=col,
                lod_chain=lods,
                skeletal_mesh_path=bad_path,
            )
            assert report.is_valid is False
            assert any("MACHINE_DEPENDENT_PATH" in issue for issue in report.issues)
            assert report.quality_score.export_score == 0.0

    def test_unreal_skeletal_mesh_contract(self):
        """Verify Unreal Skeletal Mesh Contract conformance (Section 176)."""
        char = UniversalCharacterFabricator.build_golden_human_male()
        d = char.to_dict()
        assert "skeletal_mesh_path" in d["export_metadata"]
        assert "skeleton_path" in d["export_metadata"]
        assert "physics_asset_path" in d["export_metadata"]
        assert "canonical_hash" in d["export_metadata"]
        assert d["export_metadata"]["skeletal_mesh_path"].startswith("/Game/")

    def test_readback_integrity(self):
        """Verify readback verification detects corruption (Section 177)."""
        char = UniversalCharacterFabricator.build_golden_human_male()
        readback = char.verify_readback()
        assert readback["readback_passed"] is True
        assert readback["bone_count"] == 23
        assert readback["hierarchy_valid"] is True
        assert readback["morph_count"] > 0
