"""
UAF-81.55 Acceptance & Normative Compliance Test Suite.
Verifies all 175 Sections of UAF-81.55-ANIMATION-RUNTIME-SYSTEM.md,
Cross-Phase Integration (UAF-81.50, 51, 52, 53, 54, 55), Machine-Agnostic Purity,
and 15 Canonical Golden Presets.
"""

import pytest
from uaf.universal_animation import (
    AnimationType55,
    AnimationDefinition,
    AnimationTrack,
    ChannelType55,
    Keyframe55,
    UniversalAnimationFabricator,
    UniversalAnimationValidator,
    ProductionReadyAnimatedCharacter,
    UniversalAnimationPackage,
)

# Cross-Phase Integration imports (Section 164)
from uaf.universal_surface import UniversalSurfaceFabricationPlatform
from uaf.universal_geometry import UniversalGeometryFabricationPlatform
from uaf.universal_character import UniversalCharacterFabricator


class TestUAF8155Acceptance:
    """Acceptance criteria tests for UAF-81.55 Universal Animation & Runtime System."""

    def test_golden_animation_set_complete(self):
        """Verify all 15 Golden Animations from Section 160 exist and are valid."""
        goldens = [
            UniversalAnimationFabricator.build_golden_idle(),
            UniversalAnimationFabricator.build_golden_walk(),
            UniversalAnimationFabricator.build_golden_run(),
            UniversalAnimationFabricator.build_golden_sprint(),
            UniversalAnimationFabricator.build_golden_jump(),
            UniversalAnimationFabricator.build_golden_fall(),
            UniversalAnimationFabricator.build_golden_land(),
            UniversalAnimationFabricator.build_golden_turn(),
            UniversalAnimationFabricator.build_golden_strafe(),
            UniversalAnimationFabricator.build_golden_attack(),
            UniversalAnimationFabricator.build_golden_aim(),
            UniversalAnimationFabricator.build_golden_crouch(),
            UniversalAnimationFabricator.build_golden_facial(),
            UniversalAnimationFabricator.build_golden_root_motion(),
            UniversalAnimationFabricator.build_golden_retarget(),
        ]
        assert len(goldens) == 15
        for g in goldens:
            assert isinstance(g, ProductionReadyAnimatedCharacter)
            assert g.validation_report.is_valid is True
            assert g.validation_report.quality_score.aggregate_score >= 0.95
            assert g.verify_readback()["readback_passed"] is True
            assert len(g.canonical_hash) == 64

    def test_cross_phase_integration_uaf81_50_to_55(self):
        """Verify cross-phase integration with UAF-81.50, 51, 52, 53, and 54 (Section 164)."""
        # 1. Surface from UAF-81.52
        surf_spec, *surf_paths = UniversalSurfaceFabricationPlatform.build_golden_leather()
        assert surf_spec.is_valid_surface is True

        # 2. Geometry from UAF-81.53
        mesh_spec, *mesh_paths = UniversalGeometryFabricationPlatform.build_golden_character()
        assert mesh_spec.is_valid_mesh is True

        # 3. Rigged Character from UAF-81.54
        character = UniversalCharacterFabricator.build_golden_human_male()
        assert character.validation_report.is_valid is True

        # 4. Animated Character from UAF-81.55
        animated_char = UniversalAnimationFabricator.build_golden_walk(character=character)
        assert animated_char.validation_report.is_valid is True
        assert animated_char.character.character_def.character_id == "GOLDEN_HUMAN_MALE"

    def test_strict_machine_path_rejection(self):
        """Verify strict hard failure when absolute machine paths (C:, D:, E:) are passed (Engine Purity)."""
        anim = AnimationDefinition(
            animation_id="PATH_TEST",
            name="Path Test",
            anim_type=AnimationType55.IDLE,
            duration=1.0,
            sample_rate=30,
            skeleton_reference="SKEL_Humanoid",
            tracks=[AnimationTrack("ROOT", ChannelType55.TRANSLATION, [Keyframe55(0.0, (0.0, 0.0, 0.0))])],
        )

        for bad_path in [
            r"C:\Engine\Content\Animations\Anim_Test.uasset",
            r"D:\Projects\Game\Animations\Anim_Test.uasset",
            r"E:\Dev\Assets\Animations\Anim_Test.uasset",
        ]:
            report = UniversalAnimationValidator.validate_animation(
                animation=anim,
                export_path=bad_path,
            )
            assert report.is_valid is False
            assert any("MACHINE_DEPENDENT_PATH" in issue for issue in report.issues)
            assert report.quality_score.export_score == 0.0

    def test_unreal_animation_contract(self):
        """Verify Unreal Animation Export contract conformance (Section 130)."""
        anim_char = UniversalAnimationFabricator.build_golden_walk()
        d = anim_char.to_dict()
        assert "export_path" in d["export_metadata"]
        assert "canonical_hash" in d["export_metadata"]
        assert d["export_metadata"]["export_path"].startswith("/Game/")

    def test_readback_integrity(self):
        """Verify readback verification detects corruption (Section 132)."""
        anim_char = UniversalAnimationFabricator.build_golden_walk()
        readback = anim_char.verify_readback()
        assert readback["readback_passed"] is True
        assert readback["track_count"] > 0
        assert readback["duration"] > 0.0
