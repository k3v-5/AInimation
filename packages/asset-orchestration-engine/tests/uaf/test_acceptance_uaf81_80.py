"""
Acceptance Test Suite for UAF-81.80 — Universal Runtime Animation World System.
Validates World Lifecycle, Skeletons, Poses, Clips, Curves, Morph Targets,
Blend Trees, State Machines, Layers, Masking, Two-Bone & Look-At IK,
Constraints, Root Motion, Ragdoll, Retargeting, LOD, Determinism, Snapshots,
Validator, and UE5 Subsystem Packager.
"""

import math
import pytest
from uaf.runtime_animation import (
    AnimConditionOperator,
    AnimEvent,
    AnimEventType,
    AnimationClip,
    AnimationConstraint,
    AnimationCurve,
    AnimationInstance,
    AnimationLayer,
    AnimationLODLevel,
    AnimationLODSettings,
    AnimationSnapshot,
    AnimState,
    AnimStateMachine,
    AnimationTick,
    AnimTransition,
    AnimTransitionCondition,
    AnimationWorld,
    AnimationWorldSettings,
    AnimationWorldState,
    BlendTree,
    BlendTreeNode,
    BlendTreeNodeType,
    BoneMask,
    BoneNode,
    ConstraintType,
    IKSolver,
    IKSolverType,
    InterpolationType,
    Keyframe,
    LayerBlendMode,
    Pose,
    RagdollProfile,
    RagdollState,
    RetargetBoneMapping,
    RetargetProfile,
    RootMotionDelta,
    RootMotionMode,
    SkeletonHierarchy,
    Transform3D,
    UniversalRuntimeAnimationFabricator,
    AnimationValidationIssue,
    UniversalRuntimeAnimationValidator,
    UniversalRuntimeAnimationPackager,
    quat_multiply,
    quat_slerp,
    vec3_add,
    vec3_dot,
    vec3_length,
    vec3_lerp,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)


# ==============================================================================
# TEST FIXTURES & BUILDERS
# ==============================================================================

def make_test_skeleton() -> SkeletonHierarchy:
    skel = SkeletonHierarchy(skeleton_id="skel_humanoid", name="HumanoidSkeleton")
    skel.add_bone(BoneNode("root", "Root", None, Transform3D((0, 0, 0), (0, 0, 0, 1), (1, 1, 1)), length=1.0))
    skel.add_bone(BoneNode("pelvis", "Pelvis", "root", Transform3D((0, 1, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.2))
    skel.add_bone(BoneNode("spine", "Spine", "pelvis", Transform3D((0, 0.5, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.5))
    skel.add_bone(BoneNode("head", "Head", "spine", Transform3D((0, 0.4, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.3))
    # Right arm
    skel.add_bone(BoneNode("shoulder_r", "ShoulderR", "spine", Transform3D((0.3, 0.3, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.1))
    skel.add_bone(BoneNode("elbow_r", "ElbowR", "shoulder_r", Transform3D((0.4, 0, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.4))
    skel.add_bone(BoneNode("hand_r", "HandR", "elbow_r", Transform3D((0.4, 0, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.3))
    # Right leg
    skel.add_bone(BoneNode("hip_r", "HipR", "pelvis", Transform3D((0.2, -0.1, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.1))
    skel.add_bone(BoneNode("knee_r", "KneeR", "hip_r", Transform3D((0, -0.5, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.5))
    skel.add_bone(BoneNode("foot_r", "FootR", "knee_r", Transform3D((0, -0.5, 0), (0, 0, 0, 1), (1, 1, 1)), length=0.2))
    return skel


def make_walk_clip() -> AnimationClip:
    clip = AnimationClip(clip_id="clip_walk", name="Walk", duration=1.0, looping=True)
    # Root moving forward
    root_pos_curve = AnimationCurve(
        curve_id="c_walk_root_pos",
        name="root_pos",
        curve_type="VECTOR3",
        keyframes=[
            Keyframe(0.0, (0.0, 0.0, 0.0)),
            Keyframe(0.5, (0.0, 0.0, 0.5)),
            Keyframe(1.0, (0.0, 0.0, 1.0)),
        ],
    )
    clip.bone_tracks["root"] = {"position": root_pos_curve}

    # Spine slight bounce
    spine_pos_curve = AnimationCurve(
        curve_id="c_walk_spine_pos",
        name="spine_pos",
        curve_type="VECTOR3",
        keyframes=[
            Keyframe(0.0, (0.0, 0.5, 0.0)),
            Keyframe(0.5, (0.0, 0.55, 0.0)),
            Keyframe(1.0, (0.0, 0.5, 0.0)),
        ],
    )
    clip.bone_tracks["spine"] = {"position": spine_pos_curve}

    # Morph target smile
    smile_curve = AnimationCurve(
        curve_id="c_walk_smile",
        name="Smile",
        curve_type="FLOAT",
        keyframes=[Keyframe(0.0, 0.2), Keyframe(0.5, 0.5), Keyframe(1.0, 0.2)],
    )
    clip.morph_tracks["Smile"] = smile_curve

    # Footstep event
    clip.events.append(AnimEvent("ev_step_1", AnimEventType.FOOTSTEP, 0.25, "LeftStep", {"foot": "left"}))
    clip.events.append(AnimEvent("ev_step_2", AnimEventType.FOOTSTEP, 0.75, "RightStep", {"foot": "right"}))
    return clip


def make_run_clip() -> AnimationClip:
    clip = AnimationClip(clip_id="clip_run", name="Run", duration=0.8, looping=True)
    root_pos_curve = AnimationCurve(
        curve_id="c_run_root_pos",
        name="root_pos",
        curve_type="VECTOR3",
        keyframes=[
            Keyframe(0.0, (0.0, 0.0, 0.0)),
            Keyframe(0.8, (0.0, 0.0, 2.5)),
        ],
    )
    clip.bone_tracks["root"] = {"position": root_pos_curve}
    return clip


# ==============================================================================
# 1. LIFECYCLE TESTS
# ==============================================================================

class TestAnimationWorldLifecycle:
    def test_initial_state(self):
        fab = UniversalRuntimeAnimationFabricator()
        assert fab.world.state == AnimationWorldState.CREATED

    def test_lifecycle_full_flow(self):
        fab = UniversalRuntimeAnimationFabricator()
        assert fab.initialize() is True
        assert fab.world.state == AnimationWorldState.READY

        assert fab.start() is True
        assert fab.world.state == AnimationWorldState.RUNNING

        assert fab.pause() is True
        assert fab.world.state == AnimationWorldState.PAUSED

        assert fab.resume() is True
        assert fab.world.state == AnimationWorldState.RUNNING

        assert fab.stop() is True
        assert fab.world.state == AnimationWorldState.STOPPED

        assert fab.destroy() is True
        assert fab.world.state == AnimationWorldState.DESTROYED


# ==============================================================================
# 2. SKELETON & POSE TESTS
# ==============================================================================

class TestSkeletonHierarchy:
    def test_skeleton_creation(self):
        skel = make_test_skeleton()
        assert len(skel.bones) == 10
        assert skel.root_bone_id == "root"
        assert skel.get_bone("spine") is not None
        assert skel.get_bone("spine").parent_id == "pelvis"

    def test_compute_model_space_pose(self):
        skel = make_test_skeleton()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")
        model_pose = fab.compute_model_space_pose(inst.current_pose, skel)

        assert "root" in model_pose
        assert "pelvis" in model_pose
        assert "spine" in model_pose
        # Pelvis position is root(0,0,0) + pelvis(0,1,0) = (0, 1, 0)
        assert model_pose["pelvis"].position == (0.0, 1.0, 0.0)
        # Spine position is pelvis(0,1,0) + spine(0,0.5,0) = (0, 1.5, 0)
        assert model_pose["spine"].position == (0.0, 1.5, 0.0)


# ==============================================================================
# 3. CURVE & CLIP TESTS
# ==============================================================================

class TestCurvesAndClips:
    def test_linear_curve_interpolation(self):
        curve = AnimationCurve(
            curve_id="c1",
            name="test",
            curve_type="FLOAT",
            keyframes=[Keyframe(0.0, 10.0), Keyframe(1.0, 20.0)],
            interpolation=InterpolationType.LINEAR,
        )
        assert curve.evaluate(0.0) == 10.0
        assert curve.evaluate(0.5) == 15.0
        assert curve.evaluate(1.0) == 20.0
        assert curve.evaluate(1.5) == 20.0  # Clamp upper
        assert curve.evaluate(-0.5) == 10.0  # Clamp lower

    def test_quaternion_slerp_curve(self):
        q1 = (0.0, 0.0, 0.0, 1.0)
        # 90 degrees around Y axis
        q2 = (0.0, math.sin(math.pi / 4), 0.0, math.cos(math.pi / 4))
        curve = AnimationCurve(
            curve_id="c_rot",
            name="rot",
            curve_type="QUATERNION",
            keyframes=[Keyframe(0.0, q1), Keyframe(1.0, q2)],
            interpolation=InterpolationType.SPHERICAL_SLERP,
        )
        mid_q = curve.evaluate(0.5)
        # Midpoint rotation should be 45 deg around Y
        expected_y = math.sin(math.pi / 8)
        assert abs(mid_q[1] - expected_y) < 1e-4

    def test_clip_sampling(self):
        skel = make_test_skeleton()
        clip = make_walk_clip()
        pose_0 = clip.sample_pose(0.0, skel)
        assert pose_0.bone_transforms["root"].position == (0.0, 0.0, 0.0)
        assert pose_0.morph_weights["Smile"] == 0.2

        pose_mid = clip.sample_pose(0.5, skel)
        assert pose_mid.bone_transforms["root"].position == (0.0, 0.0, 0.5)
        assert pose_mid.morph_weights["Smile"] == 0.5


# ==============================================================================
# 4. BLEND TREE TESTS
# ==============================================================================

class TestBlendTrees:
    def test_blend_tree_1d_lerp(self):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        run = make_run_clip()

        tree = BlendTree(
            tree_id="tree_locomotion",
            name="Locomotion",
            root_node=BlendTreeNode(
                node_id="root_1d",
                node_type=BlendTreeNodeType.LERP_1D,
                parameter_name_x="speed",
                children=[
                    BlendTreeNode(node_id="n_walk", node_type=BlendTreeNodeType.CLIP, clip_id="clip_walk", threshold=1.0),
                    BlendTreeNode(node_id="n_run", node_type=BlendTreeNodeType.CLIP, clip_id="clip_run", threshold=5.0),
                ],
            ),
        )

        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)
        fab.register_clip(run)
        fab.register_blend_tree(tree)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")

        # Speed 1.0 (pure walk)
        fab.set_instance_parameter("inst1", "speed", 1.0)
        pose_walk = fab.evaluate_blend_tree(tree, inst, skel, 0.5)
        assert pose_walk.bone_transforms["root"].position[2] == pytest.approx(0.5, abs=1e-4)

        # Speed 3.0 (halfway between walk (0.5) and run (1.5625 at 0.5s))
        fab.set_instance_parameter("inst1", "speed", 3.0)
        pose_mid = fab.evaluate_blend_tree(tree, inst, skel, 0.5)
        assert pose_mid.bone_transforms["root"].position[2] > 0.5

    def test_blend_tree_2d_cartesian(self):
        skel = make_test_skeleton()
        c_center = AnimationClip("c_center", "Center", 1.0)
        c_right = AnimationClip("c_right", "Right", 1.0)
        c_right.bone_tracks["spine"] = {
            "position": AnimationCurve("c_sp_pos", "sp", "VECTOR3", [Keyframe(0.0, (0.5, 0.5, 0.0)), Keyframe(1.0, (0.5, 0.5, 0.0))])
        }

        tree = BlendTree(
            tree_id="tree_2d",
            name="Strafe",
            root_node=BlendTreeNode(
                node_id="root_2d",
                node_type=BlendTreeNodeType.BLEND_2D_CARTESIAN,
                parameter_name_x="dir_x",
                parameter_name_y="dir_y",
                children=[
                    BlendTreeNode(node_id="n1", node_type=BlendTreeNodeType.CLIP, clip_id="c_center", position_2d=(0.0, 0.0)),
                    BlendTreeNode(node_id="n2", node_type=BlendTreeNodeType.CLIP, clip_id="c_right", position_2d=(1.0, 0.0)),
                ],
            ),
        )

        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(c_center)
        fab.register_clip(c_right)
        fab.register_blend_tree(tree)

        inst = fab.create_instance("inst2", "ent2", "skel_humanoid")
        fab.set_instance_parameter("inst2", "dir_x", 1.0)
        fab.set_instance_parameter("inst2", "dir_y", 0.0)

        pose = fab.evaluate_blend_tree(tree, inst, skel, 0.0)
        assert pose.bone_transforms["spine"].position[0] == pytest.approx(0.5, abs=1e-4)


# ==============================================================================
# 5. STATE MACHINE TESTS
# ==============================================================================

class TestAnimationStateMachines:
    def test_state_machine_transition_trigger(self):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        run = make_run_clip()

        sm = AnimStateMachine(
            sm_id="sm_loco",
            name="LocoSM",
            default_state_id="idle",
            states={
                "idle": AnimState("idle", "Idle", motion_type="CLIP", motion_id="clip_walk"),
                "running": AnimState("running", "Running", motion_type="CLIP", motion_id="clip_run"),
            },
            transitions=[
                AnimTransition(
                    source_state_id="idle",
                    target_state_id="running",
                    duration=0.2,
                    conditions=[
                        AnimTransitionCondition("is_running", AnimConditionOperator.IS_TRUE, True)
                    ],
                )
            ],
        )

        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)
        fab.register_clip(run)
        fab.register_state_machine(sm)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid", "sm_loco")
        fab.start()

        # Tick 1: Still idle
        fab.tick(0.05)
        assert inst.current_state_id == "idle"

        # Trigger condition
        fab.set_instance_parameter("inst1", "is_running", True)
        fab.tick(0.1)
        assert inst.transition_target_state_id == "running"

        # Finish transition duration (0.2s)
        fab.tick(0.15)
        assert inst.current_state_id == "running"
        assert inst.transition_target_state_id is None


# ==============================================================================
# 6. LAYERS & BONE MASKING TESTS
# ==============================================================================

class TestLayersAndMasks:
    def test_upper_body_mask(self):
        skel = make_test_skeleton()
        # Mask only spine, head, arms
        mask = BoneMask(
            mask_id="mask_upper",
            name="UpperBody",
            bone_weights={
                "root": 0.0,
                "pelvis": 0.0,
                "hip_r": 0.0,
                "knee_r": 0.0,
                "foot_r": 0.0,
                "spine": 1.0,
                "head": 1.0,
                "shoulder_r": 1.0,
                "elbow_r": 1.0,
                "hand_r": 1.0,
            },
        )
        assert mask.get_weight("root") == 0.0
        assert mask.get_weight("spine") == 1.0

        p1 = Pose("skel_humanoid", {"root": Transform3D((0, 0, 0)), "spine": Transform3D((0, 0, 0))})
        p2 = Pose("skel_humanoid", {"root": Transform3D((10, 0, 0)), "spine": Transform3D((0, 10, 0))})

        fab = UniversalRuntimeAnimationFabricator()
        blended = fab.blend_poses(p1, p2, 1.0, mask)

        # Root has 0.0 weight so stays p1
        assert blended.bone_transforms["root"].position == (0.0, 0.0, 0.0)
        # Spine has 1.0 weight so becomes p2
        assert blended.bone_transforms["spine"].position == (0.0, 10.0, 0.0)


# ==============================================================================
# 7. IK & CONSTRAINTS TESTS
# ==============================================================================

class TestIKAndConstraints:
    def test_two_bone_ik_solver(self):
        skel = make_test_skeleton()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)

        solver = IKSolver(
            solver_id="ik_leg_r",
            solver_type=IKSolverType.TWO_BONE_IK,
            root_bone_id="hip_r",
            mid_bone_id="knee_r",
            end_effector_bone_id="foot_r",
            target_position=(0.2, -0.7, 0.2),
            weight=1.0,
        )
        fab.register_ik_solver(solver)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")
        init_rot = inst.current_pose.bone_transforms["knee_r"].rotation
        fab.apply_two_bone_ik(inst.current_pose, skel, solver)
        new_rot = inst.current_pose.bone_transforms["knee_r"].rotation

        # Knee should bend to reach target
        assert new_rot != init_rot

    def test_look_at_ik_aim(self):
        skel = make_test_skeleton()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)

        solver = IKSolver(
            solver_id="ik_look_at",
            solver_type=IKSolverType.LOOK_AT,
            root_bone_id="head",
            target_position=(5.0, 1.9, 0.0),
            weight=1.0,
        )
        fab.register_ik_solver(solver)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")
        init_rot = inst.current_pose.bone_transforms["head"].rotation
        fab.apply_look_at_ik(inst.current_pose, skel, solver)
        new_rot = inst.current_pose.bone_transforms["head"].rotation
        assert new_rot != init_rot

    def test_position_constraint(self):
        skel = make_test_skeleton()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)

        constraint = AnimationConstraint(
            constraint_id="c_hand_lock",
            constraint_type=ConstraintType.POSITION,
            source_bone_id="hand_r",
            target_static_transform=Transform3D((1.0, 2.0, 3.0)),
            weight=1.0,
        )
        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")
        fab.apply_constraints(inst.current_pose, skel, constraint)
        assert inst.current_pose.bone_transforms["hand_r"].position == (1.0, 2.0, 3.0)


# ==============================================================================
# 8. ROOT MOTION & EVENTS TESTS
# ==============================================================================

class TestRootMotionAndEvents:
    def test_root_motion_delta_extraction(self):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)

        sm = AnimStateMachine(
            sm_id="sm1",
            name="SM",
            default_state_id="s1",
            states={"s1": AnimState("s1", "S1", "CLIP", "clip_walk")},
        )
        fab.register_state_machine(sm)

        inst = fab.create_instance("inst1", "ent1", "skel_humanoid", "sm1")
        inst.root_motion_mode = RootMotionMode.EXTRACT_DELTA
        fab.start()

        # Step 0.5s -> root moves to z=0.5
        fab.tick(0.5)
        assert inst.accumulated_root_motion.translation[2] == pytest.approx(0.5, abs=1e-4)

    def test_event_dispatch(self):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)

        sm = AnimStateMachine(
            sm_id="sm1",
            name="SM",
            default_state_id="s1",
            states={"s1": AnimState("s1", "S1", "CLIP", "clip_walk")},
        )
        fab.register_state_machine(sm)

        fab.create_instance("inst1", "ent1", "skel_humanoid", "sm1")
        fab.start()

        # Walk clip has step at 0.25s
        evs = fab.tick(0.3)
        assert len(evs) >= 1
        assert evs[0].event_type == AnimEventType.FOOTSTEP


# ==============================================================================
# 9. RETARGETING & LOD TESTS
# ==============================================================================

class TestRetargetingAndLOD:
    def test_retarget_pose(self):
        profile = RetargetProfile(
            profile_id="retarget_h2small",
            source_skeleton_id="skel_humanoid",
            target_skeleton_id="skel_small",
            mappings={
                "root": RetargetBoneMapping("root", "small_root", translation_scale=0.5),
                "spine": RetargetBoneMapping("spine", "small_spine", translation_scale=0.5),
            },
        )
        src_pose = Pose("skel_humanoid", {
            "root": Transform3D((0, 0, 10)),
            "spine": Transform3D((0, 2, 0)),
        })

        fab = UniversalRuntimeAnimationFabricator()
        tgt_pose = fab.retarget_pose(src_pose, profile)

        assert tgt_pose.skeleton_id == "skel_small"
        assert tgt_pose.bone_transforms["small_root"].position == (0, 0, 5)
        assert tgt_pose.bone_transforms["small_spine"].position == (0, 1, 0)

    def test_lod_level_selection(self):
        lod_settings = AnimationLODSettings(
            enabled=True,
            levels=[
                AnimationLODLevel(0, max_distance=10.0, tick_rate_divisor=1),
                AnimationLODLevel(1, max_distance=30.0, tick_rate_divisor=2),
                AnimationLODLevel(2, max_distance=100.0, tick_rate_divisor=4),
            ],
        )
        assert lod_settings.get_lod_for_distance(5.0).level == 0
        assert lod_settings.get_lod_for_distance(20.0).level == 1
        assert lod_settings.get_lod_for_distance(50.0).level == 2


# ==============================================================================
# 10. DETERMINISM, SNAPSHOTS & REPLAY
# ==============================================================================

class TestDeterminismAndReplay:
    def test_deterministic_state_hash(self):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        fab.register_skeleton(skel)
        fab.create_instance("inst1", "ent1", "skel_humanoid")
        fab.start()

        snap1 = fab.take_snapshot()
        snap2 = fab.take_snapshot()

        # State hash must be identical for unchanged state
        assert snap1.state_hash == snap2.state_hash
        assert len(snap1.state_hash) == 64

    def test_snapshot_restore(self):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        fab.register_skeleton(skel)
        inst = fab.create_instance("inst1", "ent1", "skel_humanoid")
        inst.current_pose.bone_transforms["root"].position = (42.0, 0.0, 0.0)

        snap = fab.take_snapshot()

        # Mutate
        inst.current_pose.bone_transforms["root"].position = (0.0, 0.0, 0.0)

        # Restore
        fab.restore_snapshot(snap)
        restored_inst = fab.get_instance("inst1")
        assert restored_inst.current_pose.bone_transforms["root"].position == (42.0, 0.0, 0.0)


# ==============================================================================
# 11. VALIDATOR & PACKAGER TESTS
# ==============================================================================

class TestValidatorAndPackager:
    def test_validator_cycle_detection(self):
        skel = SkeletonHierarchy("skel_cyclic", "Cyclic")
        skel.add_bone(BoneNode("b1", "B1", "b2"))
        skel.add_bone(BoneNode("b2", "B2", "b1"))

        issues = UniversalRuntimeAnimationValidator.validate_skeleton(skel)
        assert any(i.code == "ANIM_SKEL_CYCLE_DETECTED" for i in issues)

    def test_validator_clean_world(self):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab.register_skeleton(skel)
        fab.register_clip(walk)
        fab.create_instance("inst1", "ent1", "skel_humanoid")

        issues = UniversalRuntimeAnimationValidator.validate_world(fab.world)
        errors = [i for i in issues if i.severity == "ERROR"]
        assert len(errors) == 0

    def test_packager_ue5_export(self):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab.register_skeleton(skel)
        fab.register_clip(walk)

        sm = AnimStateMachine(
            sm_id="sm_player",
            name="PlayerAnimBP",
            default_state_id="locomotion",
            states={"locomotion": AnimState("locomotion", "Locomotion", "CLIP", "clip_walk")},
        )
        fab.register_state_machine(sm)

        pkg = UniversalRuntimeAnimationPackager.package_world(fab.world)
        assert "package_hash" in pkg
        assert "ue5_subsystem" in pkg
        assert "sm_player" in pkg["ue5_subsystem"]["AnimBlueprints"]
        assert pkg["ue5_subsystem"]["AnimBlueprints"]["sm_player"]["AnimBlueprintClass"] == "ABP_PlayerAnimBP"


# ==============================================================================
# 12. GOLDEN TESTS
# ==============================================================================

class TestGoldenScenarios:
    def test_golden_complete_character_pipeline(self):
        """End-to-end golden test combining skeleton, clip, state machine, IK, events, and snapshots."""
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        walk = make_walk_clip()
        run = make_run_clip()

        fab.register_skeleton(skel)
        fab.register_clip(walk)
        fab.register_clip(run)

        # State Machine
        sm = AnimStateMachine(
            sm_id="sm_hero",
            name="HeroLocomotion",
            default_state_id="walk",
            states={
                "walk": AnimState("walk", "WalkState", "CLIP", "clip_walk"),
                "run": AnimState("run", "RunState", "CLIP", "clip_run"),
            },
            transitions=[
                AnimTransition(
                    source_state_id="walk",
                    target_state_id="run",
                    duration=0.2,
                    conditions=[AnimTransitionCondition("speed", AnimConditionOperator.GREATER, 3.0)],
                )
            ],
        )
        fab.register_state_machine(sm)

        # Look-At IK
        ik = IKSolver("ik_look", IKSolverType.LOOK_AT, "head", target_position=(10, 1.9, 5))
        fab.register_ik_solver(ik)

        # Create character instance
        inst = fab.create_instance("hero_1", "entity_hero", "skel_humanoid", "sm_hero")
        fab.start()

        # 1. Walk phase
        fab.set_instance_parameter("hero_1", "speed", 1.5)
        events_walk = fab.tick(0.3)
        assert len(events_walk) >= 1  # Footstep event triggered
        assert inst.current_state_id == "walk"

        # 2. Transition to Run
        fab.set_instance_parameter("hero_1", "speed", 4.0)
        fab.tick(0.1)
        assert inst.transition_target_state_id == "run"
        fab.tick(0.2)
        assert inst.current_state_id == "run"

        # 3. Take snapshot
        snap = fab.take_snapshot()
        assert len(snap.state_hash) == 64
        assert snap.world_state == AnimationWorldState.RUNNING

        # 4. Package
        pkg = UniversalRuntimeAnimationPackager.package_world(fab.world)
        assert pkg["clips_count"] == 2
        assert pkg["skeletons_count"] == 1
        assert "package_hash" in pkg


# ==============================================================================
# 13. EXTENDED MATH & TRANSFORM TESTS
# ==============================================================================

class TestMathAndTransformUtilities:
    def test_vec3_operations(self):
        v1 = (1.0, 2.0, 3.0)
        v2 = (4.0, 5.0, 6.0)
        assert vec3_add(v1, v2) == (5.0, 7.0, 9.0)
        assert vec3_sub(v2, v1) == (3.0, 3.0, 3.0)
        assert vec3_scale(v1, 2.0) == (2.0, 4.0, 6.0)
        assert vec3_dot(v1, v2) == 1*4 + 2*5 + 3*6  # 32
        assert vec3_length((3.0, 4.0, 0.0)) == 5.0

    def test_quat_identity_and_multiplication(self):
        q_id = (0.0, 0.0, 0.0, 1.0)
        q1 = (0.0, math.sin(math.pi / 4), 0.0, math.cos(math.pi / 4))
        # Multiplying by identity leaves quaternion unchanged
        res = quat_multiply(q1, q_id)
        assert abs(res[0] - q1[0]) < 1e-6
        assert abs(res[1] - q1[1]) < 1e-6
        assert abs(res[2] - q1[2]) < 1e-6
        assert abs(res[3] - q1[3]) < 1e-6

    def test_transform_serialization(self):
        t = Transform3D((1.0, 2.0, 3.0), (0.0, 0.7071, 0.0, 0.7071), (2.0, 2.0, 2.0))
        d = t.to_dict()
        t2 = Transform3D.from_dict(d)
        assert t2.position == (1.0, 2.0, 3.0)
        assert t2.scale == (2.0, 2.0, 2.0)


# ==============================================================================
# 14. EXTENDED CURVES & CLIPS TESTS
# ==============================================================================

class TestCurvesAndClipsDeep:
    def test_empty_curve_defaults(self):
        c_flt = AnimationCurve("c_f", "f", "FLOAT", [])
        c_v3 = AnimationCurve("c_v", "v", "VECTOR3", [])
        c_quat = AnimationCurve("c_q", "q", "QUATERNION", [])

        assert c_flt.evaluate(0.0) == 0.0
        assert c_v3.evaluate(0.0) == (0.0, 0.0, 0.0)
        assert c_quat.evaluate(0.0) == (0.0, 0.0, 0.0, 1.0)

    def test_step_interpolation_curve(self):
        curve = AnimationCurve(
            curve_id="c_step",
            name="step",
            curve_type="FLOAT",
            keyframes=[Keyframe(0.0, 10.0), Keyframe(1.0, 20.0), Keyframe(2.0, 30.0)],
            interpolation=InterpolationType.STEP,
        )
        assert curve.evaluate(0.0) == 10.0
        assert curve.evaluate(0.5) == 10.0
        assert curve.evaluate(0.99) == 10.0
        assert curve.evaluate(1.0) == 20.0
        assert curve.evaluate(1.5) == 20.0

    def test_clip_without_looping(self):
        skel = make_test_skeleton()
        clip = AnimationClip("clip_clamp", "Clamp", duration=1.0, looping=False)
        clip.bone_tracks["root"] = {
            "position": AnimationCurve("cp", "p", "VECTOR3", [Keyframe(0.0, (0, 0, 0)), Keyframe(1.0, (0, 0, 10))])
        }
        # Evaluation past duration must clamp to 1.0 duration
        pose_past = clip.sample_pose(2.5, skel)
        assert pose_past.bone_transforms["root"].position == (0.0, 0.0, 10.0)


# ==============================================================================
# 15. EXTENDED BLEND TREES & STATE MACHINES
# ==============================================================================

class TestBlendTreesAndStateMachinesDeep:
    def test_additive_blend_tree_node(self):
        skel = make_test_skeleton()
        base_clip = AnimationClip("base", "Base", 1.0)
        add_clip = AnimationClip("add", "Add", 1.0)
        add_clip.bone_tracks["head"] = {
            "position": AnimationCurve("ch", "h", "VECTOR3", [Keyframe(0.0, (0.0, 0.5, 0.0)), Keyframe(1.0, (0.0, 0.5, 0.0))])
        }

        tree = BlendTree(
            tree_id="tree_add",
            name="AdditiveTree",
            root_node=BlendTreeNode(
                node_id="add_node",
                node_type=BlendTreeNodeType.ADDITIVE,
                parameter_name_x="add_weight",
                children=[
                    BlendTreeNode(node_id="c_base", node_type=BlendTreeNodeType.CLIP, clip_id="base"),
                    BlendTreeNode(node_id="c_add", node_type=BlendTreeNodeType.CLIP, clip_id="add"),
                ],
            ),
        )

        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(base_clip)
        fab.register_clip(add_clip)
        fab.register_blend_tree(tree)

        inst = fab.create_instance("inst_add", "ent", "skel_humanoid")
        fab.set_instance_parameter("inst_add", "add_weight", 0.5)

        pose = fab.evaluate_blend_tree(tree, inst, skel, 0.0)
        # Bind pose for head is (0, 0.4, 0), additive is (0, 0.5*0.5, 0) -> (0, 0.65, 0)
        head_pos = pose.bone_transforms["head"].position
        assert head_pos[1] == pytest.approx(0.65, abs=1e-4)

    def test_condition_operators(self):
        cond_eq = AnimTransitionCondition("mode", AnimConditionOperator.EQUAL, "COMBAT")
        cond_ne = AnimTransitionCondition("mode", AnimConditionOperator.NOT_EQUAL, "STEALTH")
        cond_gt = AnimTransitionCondition("stamina", AnimConditionOperator.GREATER, 50)
        cond_le = AnimTransitionCondition("stamina", AnimConditionOperator.LESS_EQUAL, 20)

        params = {"mode": "COMBAT", "stamina": 80}
        assert cond_eq.evaluate(params) is True
        assert cond_ne.evaluate(params) is True
        assert cond_gt.evaluate(params) is True
        assert cond_le.evaluate(params) is False


# ==============================================================================
# 16. EXTENDED IK, CONSTRAINTS & ROOT MOTION
# ==============================================================================

class TestIKAndRootMotionDeep:
    def test_look_at_zero_weight(self):
        skel = make_test_skeleton()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)

        solver = IKSolver("ik_look_zero", IKSolverType.LOOK_AT, "head", target_position=(10, 10, 10), weight=0.0)
        inst = fab.create_instance("inst_zero", "ent", "skel_humanoid")
        init_rot = inst.current_pose.bone_transforms["head"].rotation
        fab.apply_look_at_ik(inst.current_pose, skel, solver)
        assert inst.current_pose.bone_transforms["head"].rotation == init_rot

    def test_root_motion_multiple_ticks(self):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)

        sm = AnimStateMachine(
            sm_id="sm_loop",
            name="LoopSM",
            default_state_id="w",
            states={"w": AnimState("w", "W", "CLIP", "clip_walk")},
        )
        fab.register_state_machine(sm)

        inst = fab.create_instance("inst_multi", "ent", "skel_humanoid", "sm_loop")
        inst.root_motion_mode = RootMotionMode.EXTRACT_DELTA
        fab.start()

        # Step 1: 0.25s
        fab.tick(0.25)
        # Step 2: 0.25s (total 0.5s)
        fab.tick(0.25)
        assert inst.accumulated_root_motion.translation[2] == pytest.approx(0.5, abs=1e-4)


# ==============================================================================
# 17. EXTENDED VALIDATOR & SERIALIZATION TESTS
# ==============================================================================

class TestValidatorAndSerializationDeep:
    def test_validator_detects_negative_length(self):
        skel = SkeletonHierarchy("skel_neg", "Negative")
        skel.add_bone(BoneNode("b1", "B1", None, length=-2.0))
        issues = UniversalRuntimeAnimationValidator.validate_skeleton(skel)
        assert any(i.code == "ANIM_SKEL_NEGATIVE_LENGTH" for i in issues)

    def test_validator_detects_zero_clip_duration(self):
        clip = AnimationClip("clip_zero", "Zero", duration=0.0)
        issues = UniversalRuntimeAnimationValidator.validate_clip(clip)
        assert any(i.code == "ANIM_CLIP_ZERO_DURATION" for i in issues)

    def test_validator_detects_event_out_of_bounds(self):
        clip = AnimationClip("clip_ev", "Ev", duration=1.0)
        clip.events.append(AnimEvent("e1", AnimEventType.NOTIFY, 2.5))
        issues = UniversalRuntimeAnimationValidator.validate_clip(clip)
        assert any(i.code == "ANIM_EVENT_OUT_OF_BOUNDS" for i in issues)

    def test_validator_detects_invalid_state_machine(self):
        sm = AnimStateMachine(
            sm_id="sm_bad",
            name="BadSM",
            default_state_id="missing_state",
            states={"s1": AnimState("s1", "S1")},
            transitions=[AnimTransition("s1", "missing_tgt", 0.2)],
        )
        issues = UniversalRuntimeAnimationValidator.validate_state_machine(sm)
        assert any(i.code == "ANIM_SM_INVALID_DEFAULT" for i in issues)
        assert any(i.code == "ANIM_SM_TRANSITION_INVALID_TGT" for i in issues)

    def test_snapshot_roundtrip_dict(self):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        fab.register_skeleton(skel)
        fab.create_instance("inst1", "ent1", "skel_humanoid")
        fab.start()

        snap = fab.take_snapshot()
        d = snap.to_dict()
        assert d["snapshot_id"] == snap.snapshot_id
        assert d["state_hash"] == snap.state_hash
        assert d["world_state"] == AnimationWorldState.RUNNING.value


# ==============================================================================
# 18. PARAMETRIC COVERAGE & EDGE CASE SUITES
# ==============================================================================

class TestParametricSuites:
    @pytest.mark.parametrize("dt", [0.001, 0.016, 0.033, 0.05, 0.1, 0.25])
    def test_parametric_simulation_ticks(self, dt):
        fab = UniversalRuntimeAnimationFabricator()
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab.register_skeleton(skel)
        fab.register_clip(walk)
        fab.create_instance("inst_p", "ent_p", "skel_humanoid")
        fab.start()

        fab.tick(dt)
        assert fab.simulation_time == pytest.approx(dt, abs=1e-6)
        assert fab.current_tick_index == 1

    @pytest.mark.parametrize(
        "op,val,thresh,expected",
        [
            (AnimConditionOperator.EQUAL, 10, 10, True),
            (AnimConditionOperator.EQUAL, 10, 20, False),
            (AnimConditionOperator.NOT_EQUAL, 10, 20, True),
            (AnimConditionOperator.NOT_EQUAL, 10, 10, False),
            (AnimConditionOperator.GREATER, 15, 10, True),
            (AnimConditionOperator.GREATER, 5, 10, False),
            (AnimConditionOperator.LESS, 5, 10, True),
            (AnimConditionOperator.LESS, 15, 10, False),
            (AnimConditionOperator.GREATER_EQUAL, 10, 10, True),
            (AnimConditionOperator.GREATER_EQUAL, 9, 10, False),
            (AnimConditionOperator.LESS_EQUAL, 10, 10, True),
            (AnimConditionOperator.LESS_EQUAL, 11, 10, False),
            (AnimConditionOperator.IS_TRUE, True, True, True),
            (AnimConditionOperator.IS_TRUE, False, True, False),
            (AnimConditionOperator.IS_FALSE, False, False, True),
            (AnimConditionOperator.IS_FALSE, True, False, False),
        ],
    )
    def test_parametric_transition_conditions(self, op, val, thresh, expected):
        cond = AnimTransitionCondition("var", op, thresh)
        assert cond.evaluate({"var": val}) is expected

    @pytest.mark.parametrize(
        "weight,mask_val,expected_root_x",
        [
            (0.0, 1.0, 0.0),
            (0.5, 1.0, 5.0),
            (1.0, 1.0, 10.0),
            (1.0, 0.0, 0.0),
            (1.0, 0.5, 5.0),
            (0.5, 0.5, 2.5),
        ],
    )
    def test_parametric_mask_and_layer_blending(self, weight, mask_val, expected_root_x):
        fab = UniversalRuntimeAnimationFabricator()
        p1 = Pose("skel", {"root": Transform3D((0, 0, 0))})
        p2 = Pose("skel", {"root": Transform3D((10, 0, 0))})
        mask = BoneMask("m", "M", {"root": mask_val})

        res = fab.blend_poses(p1, p2, weight, mask)
        assert res.bone_transforms["root"].position[0] == pytest.approx(expected_root_x, abs=1e-4)

    @pytest.mark.parametrize(
        "distance,expected_lod",
        [
            (0.0, 0),
            (5.0, 0),
            (10.0, 0),
            (10.1, 1),
            (25.0, 1),
            (30.0, 1),
            (30.1, 2),
            (80.0, 2),
            (150.0, 2),
        ],
    )
    def test_parametric_lod_selection(self, distance, expected_lod):
        settings = AnimationLODSettings(
            enabled=True,
            levels=[
                AnimationLODLevel(0, max_distance=10.0),
                AnimationLODLevel(1, max_distance=30.0),
                AnimationLODLevel(2, max_distance=100.0),
            ],
        )
        assert settings.get_lod_for_distance(distance).level == expected_lod

    @pytest.mark.parametrize("mode", [RootMotionMode.IGNORE, RootMotionMode.EXTRACT_DELTA, RootMotionMode.APPLY_TO_ACTOR])
    def test_parametric_root_motion_modes(self, mode):
        skel = make_test_skeleton()
        walk = make_walk_clip()
        fab = UniversalRuntimeAnimationFabricator()
        fab.register_skeleton(skel)
        fab.register_clip(walk)

        sm = AnimStateMachine(
            sm_id="sm_rm",
            name="RM",
            default_state_id="w",
            states={"w": AnimState("w", "W", "CLIP", "clip_walk")},
        )
        fab.register_state_machine(sm)

        inst = fab.create_instance("inst_rm", "ent", "skel_humanoid", "sm_rm")
        inst.root_motion_mode = mode
        fab.start()

        fab.tick(0.5)
        if mode == RootMotionMode.EXTRACT_DELTA:
            assert inst.accumulated_root_motion.translation[2] > 0.0
        else:
            assert inst.accumulated_root_motion.translation[2] == 0.0


