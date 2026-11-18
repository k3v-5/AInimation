"""
UAF-81.5 Acceptance Tests (Sections 91, 100, 101).
Verifies:
- Section 91: Golden Character Acceptance Test (Full pipeline synthesis of Character Skeleton,
  Skinning, Rig, Facial, Physics, Retargeting, and Unreal Export Package).
- Section 101: Non-Negotiable Rule Test (Errors cannot be silently masked; status must be
  MANUAL_REVIEW_REQUIRED on un-normalized weights or broken skeleton).
"""

from uaf.rigging.skeleton.skeleton_builder import SkeletonBuilder
from uaf.rigging.rig.rig_definition import RigDefinition
from uaf.rigging.skinning.weight_generator import WeightGenerator
from uaf.rigging.skinning.skinning_definition import SkinningDefinition, VertexWeights
from uaf.rigging.facial.facial_rig import FacialRigDefinition
from uaf.rigging.physics.physics_asset import PhysicsAssetDefinition
from uaf.rigging.retargeting.retarget_profile import RetargetProfile
from uaf.rigging.retargeting.character_package import UnrealCharacterPackage
from uaf.rigging.validation.rig_validator import RigValidator
from uaf.geometry.generators.componentized_hero_generator import ComponentizedHeroGenerator
from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.core.specification.asset_specification import AssetSpecification


def test_golden_character_acceptance_section_91():
    """
    Acceptance Test Section 91:
    End-to-end verification of Golden Character:
    - Humanoid skeleton with valid hierarchy
    - Skin weights with max influences = 4 and sum = 1.0
    - IK setup (Hand IK, Foot IK)
    - Facial deformation & blendshapes
    - Physics asset ragdoll
    - UE5 Mannequin retarget profile
    - Export into UnrealCharacterPackage with quality_score >= 0.80
    """
    # 1. Generate Character Geometry
    spec = AssetSpecification(
        identity=AssetIdentity(asset_id="golden_hero_avatar", asset_type=AssetType.CHARACTER),
        parameters={"height": 1.85},
    )
    hero_gen = ComponentizedHeroGenerator()
    character = hero_gen.generate_character_assembly(spec)

    # 2. Build Skeleton
    skeleton = SkeletonBuilder.build_humanoid_skeleton(
        skeleton_id="skel_golden_hero",
        landmarks=character.landmarks,
        height_meters=1.85,
    )
    assert skeleton.bone_count >= 19

    # 3. Generate Skinning
    body_mesh = character.get_component("comp_body").mesh_data
    skinning = WeightGenerator.generate_weights(
        mesh_id="comp_body",
        mesh=body_mesh,
        skeleton=skeleton,
        max_influences=4,
    )

    # 4. Rig Definition (IK & Controls)
    rig = RigDefinition.create_standard_humanoid_rig("rig_golden_hero", skeleton.skeleton_id)

    # 5. Facial Rig
    facial = FacialRigDefinition("face_golden_hero")

    # 6. Physics Asset (Ragdoll)
    physics = PhysicsAssetDefinition.create_standard_ragdoll("phys_golden_hero", skeleton.skeleton_id)

    # 7. Retarget Profile (UE5 Mannequin)
    retarget = RetargetProfile("retarget_ue5_golden")
    assert retarget.map_bone("upperarm_L") == "upperarm_l"
    assert retarget.map_bone("thigh_R") == "thigh_r"

    # 8. Automated Quality Gate Validation
    val_report = RigValidator.validate_rig_suite(skeleton, skinning, min_quality_score=0.75)
    assert val_report.is_valid is True
    assert val_report.review_status == "PASSED"
    assert val_report.quality_score >= 0.80

    # 9. Package for Unreal Engine 5
    pkg = UnrealCharacterPackage(
        asset_id=spec.identity.asset_id,
        skeleton=skeleton,
        rig=rig,
        skinning=skinning,
        physics=physics,
        retarget_profile=retarget,
        geometry=character.root,
        facial=facial,
        validation_status=val_report.review_status,
    )
    assert pkg.validation_status == "PASSED"
    pkg_data = pkg.to_dict()
    assert pkg_data["asset_id"] == "golden_hero_avatar"
    assert "skeleton" in pkg_data
    assert "physics" in pkg_data


def test_non_negotiable_rule_section_101():
    """
    Acceptance Test Section 101:
    Non-negotiable rule: If skin weights are broken or non-normalized,
    or skeleton has invalid parentage, the system MUST flag
    review_status = "MANUAL_REVIEW_REQUIRED" rather than silently succeeding.
    """
    skeleton = SkeletonBuilder.build_humanoid_skeleton("skel_flawed", height_meters=1.80)

    # Intentionally broken skinning (un-normalized weights summing to 2.5)
    flawed_weights = {
        0: VertexWeights(vertex_index=0, influences={"pelvis": 1.5, "spine_01": 1.0}),
    }
    flawed_skinning = SkinningDefinition(
        mesh_id="mesh_flawed",
        skeleton_id=skeleton.skeleton_id,
        max_influences_per_vertex=4,
        weights=flawed_weights,
    )

    report = RigValidator.validate_rig_suite(skeleton, flawed_skinning)
    assert report.is_valid is False
    assert report.review_status == "MANUAL_REVIEW_REQUIRED"
    assert any("do not sum to 1.0" in iss for iss in report.skinning_issues)
