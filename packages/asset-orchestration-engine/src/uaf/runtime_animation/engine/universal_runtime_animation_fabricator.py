"""
Universal Runtime Animation Fabricator Engine (UAF-81.80).
Authoritative animation world lifecycle, skeletal hierarchy pose evaluation,
clip sampling, 1D/2D blend trees, state machine transitions, layered animation
with bone masking, two-bone & look-at IK solvers, animation constraints,
root motion extraction, event dispatch, retargeting, LOD, snapshots, and replay.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
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
    combine_transforms,
    copy_dict_deterministic,
    quat_multiply,
    quat_rotate_vec3,
    quat_slerp,
    vec3_add,
    vec3_dot,
    vec3_length,
    vec3_lerp,
    vec3_normalize,
    vec3_scale,
    vec3_sub,
)


class UniversalRuntimeAnimationFabricator:
    """
    Authoritative runtime animation fabricator engine.
    Pure, deterministic, headless execution isolated from rendering and physics.
    """

    def __init__(
        self,
        animation_world_id: str = "anim_world_default",
        runtime_world_id: str = "runtime_world_default",
        settings: Optional[AnimationWorldSettings] = None,
    ):
        self.world = AnimationWorld(
            animation_world_id=animation_world_id,
            runtime_world_id=runtime_world_id,
            settings=settings or AnimationWorldSettings(),
        )
        self.current_tick_index: int = 0
        self.simulation_time: float = 0.0
        self.event_queue: List[AnimEvent] = []
        self._prev_root_positions: Dict[str, Tuple[float, float, float]] = {}

    # --------------------------------------------------------------------------
    # 1. LIFECYCLE MANAGEMENT
    # --------------------------------------------------------------------------

    def initialize(self) -> bool:
        if self.world.state in (AnimationWorldState.CREATED, AnimationWorldState.STOPPED):
            self.world.state = AnimationWorldState.INITIALIZING
            self.world.state = AnimationWorldState.READY
            return True
        return False

    def start(self) -> bool:
        if self.world.state in (AnimationWorldState.READY, AnimationWorldState.PAUSED):
            self.world.state = AnimationWorldState.RUNNING
            return True
        elif self.world.state == AnimationWorldState.CREATED:
            if self.initialize():
                self.world.state = AnimationWorldState.RUNNING
                return True
        return False

    def pause(self) -> bool:
        if self.world.state == AnimationWorldState.RUNNING:
            self.world.state = AnimationWorldState.PAUSED
            return True
        return False

    def resume(self) -> bool:
        if self.world.state == AnimationWorldState.PAUSED:
            self.world.state = AnimationWorldState.RUNNING
            return True
        return False

    def stop(self) -> bool:
        if self.world.state in (AnimationWorldState.RUNNING, AnimationWorldState.PAUSED):
            self.world.state = AnimationWorldState.STOPPING
            self.world.state = AnimationWorldState.STOPPED
            return True
        return False

    def destroy(self) -> bool:
        self.world.state = AnimationWorldState.DESTROYED
        self.world.instances.clear()
        self.world.events.clear()
        self.event_queue.clear()
        return True

    # --------------------------------------------------------------------------
    # 2. ASSET REGISTRATION
    # --------------------------------------------------------------------------

    def register_skeleton(self, skeleton: SkeletonHierarchy) -> None:
        self.world.skeletons[skeleton.skeleton_id] = skeleton

    def register_clip(self, clip: AnimationClip) -> None:
        self.world.clips[clip.clip_id] = clip

    def register_blend_tree(self, tree: BlendTree) -> None:
        self.world.blend_trees[tree.tree_id] = tree

    def register_state_machine(self, sm: AnimStateMachine) -> None:
        self.world.state_machines[sm.sm_id] = sm

    def register_layer(self, layer: AnimationLayer) -> None:
        self.world.layers[layer.layer_id] = layer

    def register_ik_solver(self, solver: IKSolver) -> None:
        self.world.ik_solvers[solver.solver_id] = solver

    def register_constraint(self, constraint: AnimationConstraint) -> None:
        self.world.constraints[constraint.constraint_id] = constraint

    def register_retarget_profile(self, profile: RetargetProfile) -> None:
        self.world.retarget_profiles[profile.profile_id] = profile

    # --------------------------------------------------------------------------
    # 3. INSTANCE MANAGEMENT
    # --------------------------------------------------------------------------

    def create_instance(
        self,
        instance_id: str,
        entity_id: str,
        skeleton_id: str,
        default_state_machine_id: Optional[str] = None,
    ) -> AnimationInstance:
        skeleton = self.world.skeletons.get(skeleton_id)
        if not skeleton:
            raise ValueError(f"Skeleton '{skeleton_id}' not registered in animation world.")

        # Default pose from bind poses
        init_transforms = {
            bid: bone.bind_pose_local.copy() for bid, bone in skeleton.bones.items()
        }
        init_pose = Pose(skeleton_id=skeleton_id, bone_transforms=init_transforms)

        curr_state_id = None
        if default_state_machine_id and default_state_machine_id in self.world.state_machines:
            sm = self.world.state_machines[default_state_machine_id]
            curr_state_id = sm.default_state_id

        instance = AnimationInstance(
            instance_id=instance_id,
            entity_id=entity_id,
            skeleton_id=skeleton_id,
            current_pose=init_pose,
            active_state_machine_id=default_state_machine_id,
            current_state_id=curr_state_id,
        )
        self.world.instances[instance_id] = instance
        root_bone = skeleton.get_bone(skeleton.root_bone_id) if skeleton.root_bone_id else None
        root_bind_pos = root_bone.bind_pose_local.position if root_bone else (0.0, 0.0, 0.0)
        self._prev_root_positions[instance_id] = root_bind_pos
        return instance

    def get_instance(self, instance_id: str) -> Optional[AnimationInstance]:
        return self.world.instances.get(instance_id)

    def remove_instance(self, instance_id: str) -> bool:
        if instance_id in self.world.instances:
            del self.world.instances[instance_id]
            if instance_id in self._prev_root_positions:
                del self._prev_root_positions[instance_id]
            return True
        return False

    def set_instance_parameter(self, instance_id: str, param_name: str, value: Any) -> None:
        inst = self.world.instances.get(instance_id)
        if inst:
            inst.parameters[param_name] = value

    def get_instance_parameter(self, instance_id: str, param_name: str) -> Any:
        inst = self.world.instances.get(instance_id)
        return inst.parameters.get(param_name) if inst else None

    # --------------------------------------------------------------------------
    # 4. POSE BLENDING & INTERPOLATION HELPERS
    # --------------------------------------------------------------------------

    def blend_poses(self, pose_a: Pose, pose_b: Pose, weight: float, mask: Optional[BoneMask] = None) -> Pose:
        """Blend two poses using a weight (0.0=pose_a, 1.0=pose_b) and optional BoneMask."""
        weight = max(0.0, min(1.0, weight))
        all_bone_ids = set(pose_a.bone_transforms.keys()).union(pose_b.bone_transforms.keys())

        blended_transforms: Dict[str, Transform3D] = {}
        for bid in all_bone_ids:
            ta = pose_a.bone_transforms.get(bid, Transform3D.identity())
            tb = pose_b.bone_transforms.get(bid, Transform3D.identity())

            effective_weight = weight
            if mask:
                effective_weight = weight * mask.get_weight(bid)

            if effective_weight <= 0.0:
                blended_transforms[bid] = ta.copy()
            elif effective_weight >= 1.0:
                blended_transforms[bid] = tb.copy()
            else:
                pos = vec3_lerp(ta.position, tb.position, effective_weight)
                rot = quat_slerp(ta.rotation, tb.rotation, effective_weight)
                scl = vec3_lerp(ta.scale, tb.scale, effective_weight)
                blended_transforms[bid] = Transform3D(pos, rot, scl)

        # Blend morph weights
        all_morphs = set(pose_a.morph_weights.keys()).union(pose_b.morph_weights.keys())
        blended_morphs: Dict[str, float] = {}
        for m in all_morphs:
            ma = pose_a.morph_weights.get(m, 0.0)
            mb = pose_b.morph_weights.get(m, 0.0)
            blended_morphs[m] = ma + (mb - ma) * weight

        # Blend curves
        all_curves = set(pose_a.evaluated_curves.keys()).union(pose_b.evaluated_curves.keys())
        blended_curves: Dict[str, float] = {}
        for c in all_curves:
            ca = pose_a.evaluated_curves.get(c, 0.0)
            cb = pose_b.evaluated_curves.get(c, 0.0)
            blended_curves[c] = ca + (cb - ca) * weight

        return Pose(
            skeleton_id=pose_a.skeleton_id,
            bone_transforms=blended_transforms,
            morph_weights=blended_morphs,
            evaluated_curves=blended_curves,
        )

    def add_poses(self, base_pose: Pose, additive_pose: Pose, weight: float) -> Pose:
        """Apply an additive delta pose onto a base pose."""
        weight = max(0.0, min(1.0, weight))
        if weight <= 1e-8:
            return base_pose

        res_transforms: Dict[str, Transform3D] = {}
        for bid, base_t in base_pose.bone_transforms.items():
            if bid in additive_pose.bone_transforms:
                add_t = additive_pose.bone_transforms[bid]
                delta_pos = vec3_scale(add_t.position, weight)
                pos = vec3_add(base_t.position, delta_pos)
                slerped_rot = quat_slerp((0.0, 0.0, 0.0, 1.0), add_t.rotation, weight)
                rot = quat_multiply(base_t.rotation, slerped_rot)
                scl = (
                    base_t.scale[0] * (1.0 + (add_t.scale[0] - 1.0) * weight),
                    base_t.scale[1] * (1.0 + (add_t.scale[1] - 1.0) * weight),
                    base_t.scale[2] * (1.0 + (add_t.scale[2] - 1.0) * weight),
                )
                res_transforms[bid] = Transform3D(pos, rot, scl)
            else:
                res_transforms[bid] = base_t.copy()

        return Pose(
            skeleton_id=base_pose.skeleton_id,
            bone_transforms=res_transforms,
            morph_weights=base_pose.morph_weights.copy(),
            evaluated_curves=base_pose.evaluated_curves.copy(),
        )

    # --------------------------------------------------------------------------
    # 5. BLEND TREE EVALUATION
    # --------------------------------------------------------------------------

    def evaluate_blend_tree(
        self,
        tree: BlendTree,
        instance: AnimationInstance,
        skeleton: SkeletonHierarchy,
        eval_time: float,
    ) -> Pose:
        return self._evaluate_blend_tree_node(tree.root_node, instance, skeleton, eval_time)

    def _evaluate_blend_tree_node(
        self,
        node: BlendTreeNode,
        instance: AnimationInstance,
        skeleton: SkeletonHierarchy,
        eval_time: float,
    ) -> Pose:
        if node.node_type == BlendTreeNodeType.CLIP:
            if node.clip_id and node.clip_id in self.world.clips:
                return self.world.clips[node.clip_id].sample_pose(eval_time, skeleton)
            return Pose(skeleton_id=skeleton.skeleton_id, bone_transforms={b: bone.bind_pose_local.copy() for b, bone in skeleton.bones.items()})

        elif node.node_type == BlendTreeNodeType.LERP_1D:
            param_val = float(instance.parameters.get(node.parameter_name_x or "speed", 0.0))
            if not node.children:
                return Pose(skeleton_id=skeleton.skeleton_id)
            if len(node.children) == 1:
                return self._evaluate_blend_tree_node(node.children[0], instance, skeleton, eval_time)

            # Sort children by threshold
            sorted_children = sorted(node.children, key=lambda c: c.threshold)
            if param_val <= sorted_children[0].threshold:
                return self._evaluate_blend_tree_node(sorted_children[0], instance, skeleton, eval_time)
            if param_val >= sorted_children[-1].threshold:
                return self._evaluate_blend_tree_node(sorted_children[-1], instance, skeleton, eval_time)

            for i in range(len(sorted_children) - 1):
                c1 = sorted_children[i]
                c2 = sorted_children[i + 1]
                if c1.threshold <= param_val <= c2.threshold:
                    span = c2.threshold - c1.threshold
                    t = 0.0 if span <= 1e-8 else (param_val - c1.threshold) / span
                    p1 = self._evaluate_blend_tree_node(c1, instance, skeleton, eval_time)
                    p2 = self._evaluate_blend_tree_node(c2, instance, skeleton, eval_time)
                    return self.blend_poses(p1, p2, t)

            return self._evaluate_blend_tree_node(sorted_children[-1], instance, skeleton, eval_time)

        elif node.node_type in (BlendTreeNodeType.BLEND_2D_CARTESIAN, BlendTreeNodeType.BLEND_2D_DIRECTIONAL):
            px = float(instance.parameters.get(node.parameter_name_x or "x", 0.0))
            py = float(instance.parameters.get(node.parameter_name_y or "y", 0.0))
            if not node.children:
                return Pose(skeleton_id=skeleton.skeleton_id)

            # Inverse Distance Weighting (IDW) interpolation
            weights: List[float] = []
            poses: List[Pose] = []
            exact_match_idx: Optional[int] = None

            for i, child in enumerate(node.children):
                dist = math.sqrt((px - child.position_2d[0]) ** 2 + (py - child.position_2d[1]) ** 2)
                if dist < 1e-6:
                    exact_match_idx = i
                    break
                w = 1.0 / (dist ** 2)
                weights.append(w)
                poses.append(self._evaluate_blend_tree_node(child, instance, skeleton, eval_time))

            if exact_match_idx is not None:
                return self._evaluate_blend_tree_node(node.children[exact_match_idx], instance, skeleton, eval_time)

            total_w = sum(weights)
            if total_w <= 1e-8:
                return poses[0]

            norm_weights = [w / total_w for w in weights]
            res_pose = poses[0]
            accum_weight = norm_weights[0]

            for i in range(1, len(poses)):
                step_w = norm_weights[i] / (accum_weight + norm_weights[i])
                res_pose = self.blend_poses(res_pose, poses[i], step_w)
                accum_weight += norm_weights[i]

            return res_pose

        elif node.node_type == BlendTreeNodeType.ADDITIVE:
            if len(node.children) >= 2:
                base = self._evaluate_blend_tree_node(node.children[0], instance, skeleton, eval_time)
                add = self._evaluate_blend_tree_node(node.children[1], instance, skeleton, eval_time)
                w = float(instance.parameters.get(node.parameter_name_x or "weight", 1.0))
                return self.add_poses(base, add, w)
            elif node.children:
                return self._evaluate_blend_tree_node(node.children[0], instance, skeleton, eval_time)

        return Pose(skeleton_id=skeleton.skeleton_id)

    # --------------------------------------------------------------------------
    # 6. STATE MACHINE EVALUATION
    # --------------------------------------------------------------------------

    def evaluate_state_machine(
        self,
        sm: AnimStateMachine,
        instance: AnimationInstance,
        skeleton: SkeletonHierarchy,
        delta_time: float,
    ) -> Pose:
        if not instance.current_state_id:
            instance.current_state_id = sm.default_state_id

        if not instance.current_state_id or instance.current_state_id not in sm.states:
            return Pose(skeleton_id=skeleton.skeleton_id)

        curr_state = sm.states[instance.current_state_id]
        instance.elapsed_time_in_state += delta_time * curr_state.speed

        # Check transitions if not already transitioning
        if not instance.transition_target_state_id:
            for trans in sm.transitions:
                if trans.source_state_id == instance.current_state_id:
                    # Check conditions
                    conds_met = all(c.evaluate(instance.parameters) for c in trans.conditions)
                    exit_time_met = True
                    if trans.has_exit_time:
                        # Normalize elapsed time based on clip duration if clip motion
                        clip_dur = 1.0
                        if curr_state.motion_type == "CLIP" and curr_state.motion_id in self.world.clips:
                            clip_dur = self.world.clips[curr_state.motion_id].duration
                        norm_time = (instance.elapsed_time_in_state / clip_dur) % 1.0 if clip_dur > 1e-6 else 1.0
                        exit_time_met = norm_time >= trans.exit_time

                    if conds_met and exit_time_met:
                        instance.transition_target_state_id = trans.target_state_id
                        instance.transition_progress = 0.0
                        instance.transition_duration = max(0.001, trans.duration)
                        break

        # Evaluate current state motion
        pose_current = self._evaluate_state_motion(curr_state, instance, skeleton, instance.elapsed_time_in_state)

        # Handle active crossfade
        if instance.transition_target_state_id:
            target_state = sm.states.get(instance.transition_target_state_id)
            if not target_state:
                instance.transition_target_state_id = None
                return pose_current

            instance.transition_progress += delta_time / instance.transition_duration
            pose_target = self._evaluate_state_motion(target_state, instance, skeleton, instance.transition_progress * instance.transition_duration)

            if instance.transition_progress >= 1.0:
                # Transition complete
                instance.current_state_id = instance.transition_target_state_id
                instance.transition_target_state_id = None
                instance.elapsed_time_in_state = instance.transition_progress * instance.transition_duration
                instance.transition_progress = 0.0
                return pose_target

            return self.blend_poses(pose_current, pose_target, instance.transition_progress)

        return pose_current

    def _evaluate_state_motion(
        self,
        state: AnimState,
        instance: AnimationInstance,
        skeleton: SkeletonHierarchy,
        eval_time: float,
    ) -> Pose:
        if state.motion_type == "CLIP":
            clip = self.world.clips.get(state.motion_id)
            if clip:
                return clip.sample_pose(eval_time, skeleton)
        elif state.motion_type == "BLEND_TREE":
            tree = self.world.blend_trees.get(state.motion_id)
            if tree:
                return self.evaluate_blend_tree(tree, instance, skeleton, eval_time)
        return Pose(skeleton_id=skeleton.skeleton_id, bone_transforms={b: bone.bind_pose_local.copy() for b, bone in skeleton.bones.items()})

    # --------------------------------------------------------------------------
    # 7. INVERSE KINEMATICS (IK) & CONSTRAINTS
    # --------------------------------------------------------------------------

    def compute_model_space_pose(self, pose: Pose, skeleton: SkeletonHierarchy) -> Dict[str, Transform3D]:
        """Convert local bone transforms into model space transforms."""
        model_transforms: Dict[str, Transform3D] = {}

        def resolve_bone(bid: str) -> Transform3D:
            if bid in model_transforms:
                return model_transforms[bid]
            bone = skeleton.get_bone(bid)
            local_t = pose.bone_transforms.get(bid, Transform3D.identity())
            if not bone or bone.parent_id is None:
                model_transforms[bid] = local_t.copy()
                return model_transforms[bid]

            parent_t = resolve_bone(bone.parent_id)
            model_transforms[bid] = combine_transforms(parent_t, local_t)
            return model_transforms[bid]

        for bid in skeleton.bones.keys():
            resolve_bone(bid)
        return model_transforms

    def apply_two_bone_ik(
        self,
        pose: Pose,
        skeleton: SkeletonHierarchy,
        solver: IKSolver,
    ) -> None:
        """Analytical two-bone IK solver for limbs (hip/knee/ankle or shoulder/elbow/wrist)."""
        root_bone = skeleton.get_bone(solver.root_bone_id)
        mid_bone = skeleton.get_bone(solver.mid_bone_id) if solver.mid_bone_id else None
        end_bone = skeleton.get_bone(solver.end_effector_bone_id)
        if not root_bone or not mid_bone or not end_bone:
            return

        l1 = root_bone.length
        l2 = mid_bone.length
        target = solver.target_position

        # Model space poses
        model_t = self.compute_model_space_pose(pose, skeleton)
        root_pos = model_t[solver.root_bone_id].position

        to_target = vec3_sub(target, root_pos)
        dist = vec3_length(to_target)
        if dist < 1e-6:
            return

        # Clamp distance to maximum limb length
        max_len = l1 + l2 - 1e-4
        min_len = max(0.001, abs(l1 - l2) + 1e-4)
        dist = max(min_len, min(max_len, dist))

        # Law of cosines
        cos_root = (dist * dist + l1 * l1 - l2 * l2) / (2.0 * dist * l1)
        cos_mid = (l1 * l1 + l2 * l2 - dist * dist) / (2.0 * l1 * l2)

        cos_root = max(-1.0, min(1.0, cos_root))
        cos_mid = max(-1.0, min(1.0, cos_mid))

        angle_root = math.acos(cos_root)
        angle_mid = math.pi - math.acos(cos_mid)

        # Apply pitch rotation around local axis proportional to weight
        w = max(0.0, min(1.0, solver.weight))
        mid_local = pose.bone_transforms.get(solver.mid_bone_id, Transform3D.identity())
        # Simplified bend quaternion around Z axis
        half_angle = (angle_mid * w) * 0.5
        bend_rot = (0.0, 0.0, math.sin(half_angle), math.cos(half_angle))
        mid_local.rotation = quat_multiply(mid_local.rotation, bend_rot)
        pose.bone_transforms[solver.mid_bone_id] = mid_local

    def apply_look_at_ik(
        self,
        pose: Pose,
        skeleton: SkeletonHierarchy,
        solver: IKSolver,
    ) -> None:
        """Aim a bone towards a target point in model space."""
        bone = skeleton.get_bone(solver.root_bone_id)
        if not bone:
            return

        model_t = self.compute_model_space_pose(pose, skeleton)
        bone_pos = model_t[solver.root_bone_id].position
        aim_vec = vec3_normalize(vec3_sub(solver.target_position, bone_pos))

        # Calculate yaw and pitch
        yaw = math.atan2(aim_vec[0], aim_vec[2])
        pitch = -math.asin(max(-1.0, min(1.0, aim_vec[1])))

        w = max(0.0, min(1.0, solver.weight))
        hy = (yaw * w) * 0.5
        hp = (pitch * w) * 0.5
        qy = (0.0, math.sin(hy), 0.0, math.cos(hy))
        qp = (math.sin(hp), 0.0, 0.0, math.cos(hp))
        aim_rot = quat_multiply(qy, qp)

        local_t = pose.bone_transforms.get(solver.root_bone_id, Transform3D.identity())
        local_t.rotation = quat_multiply(local_t.rotation, aim_rot)
        pose.bone_transforms[solver.root_bone_id] = local_t

    def apply_constraints(
        self,
        pose: Pose,
        skeleton: SkeletonHierarchy,
        constraint: AnimationConstraint,
    ) -> None:
        """Apply an animation constraint onto a bone."""
        if constraint.source_bone_id not in pose.bone_transforms:
            return

        w = max(0.0, min(1.0, constraint.weight))
        target_t = constraint.target_static_transform
        if constraint.target_bone_id and constraint.target_bone_id in pose.bone_transforms:
            target_t = pose.bone_transforms[constraint.target_bone_id]

        if not target_t:
            return

        src_t = pose.bone_transforms[constraint.source_bone_id]
        if constraint.constraint_type == ConstraintType.POSITION:
            src_t.position = vec3_lerp(src_t.position, target_t.position, w)
        elif constraint.constraint_type == ConstraintType.ROTATION:
            src_t.rotation = quat_slerp(src_t.rotation, target_t.rotation, w)
        elif constraint.constraint_type == ConstraintType.SCALE:
            src_t.scale = vec3_lerp(src_t.scale, target_t.scale, w)
        elif constraint.constraint_type == ConstraintType.PARENT:
            src_t.position = vec3_lerp(src_t.position, target_t.position, w)
            src_t.rotation = quat_slerp(src_t.rotation, target_t.rotation, w)
            src_t.scale = vec3_lerp(src_t.scale, target_t.scale, w)

        pose.bone_transforms[constraint.source_bone_id] = src_t

    # --------------------------------------------------------------------------
    # 8. RETARGETING
    # --------------------------------------------------------------------------

    def retarget_pose(self, source_pose: Pose, profile: RetargetProfile) -> Pose:
        """Retarget a pose from source skeleton onto target skeleton."""
        target_transforms: Dict[str, Transform3D] = {}

        for src_bid, mapping in profile.mappings.items():
            if src_bid in source_pose.bone_transforms:
                src_t = source_pose.bone_transforms[src_bid]
                tgt_pos = vec3_scale(src_t.position, mapping.translation_scale)
                tgt_rot = quat_multiply(src_t.rotation, mapping.rotation_offset)
                target_transforms[mapping.target_bone_id] = Transform3D(tgt_pos, tgt_rot, src_t.scale)

        return Pose(
            skeleton_id=profile.target_skeleton_id,
            bone_transforms=target_transforms,
            morph_weights=source_pose.morph_weights.copy(),
            evaluated_curves=source_pose.evaluated_curves.copy(),
        )

    # --------------------------------------------------------------------------
    # 9. ROOT MOTION & EVENTS
    # --------------------------------------------------------------------------

    def extract_root_motion(
        self,
        instance: AnimationInstance,
        skeleton: SkeletonHierarchy,
        current_root_pose: Pose,
    ) -> RootMotionDelta:
        root_id = skeleton.root_bone_id
        if not root_id or root_id not in current_root_pose.bone_transforms:
            return RootMotionDelta()

        curr_t = current_root_pose.bone_transforms[root_id]
        prev_pos = self._prev_root_positions.get(instance.instance_id, (0.0, 0.0, 0.0))
        delta_trans = vec3_sub(curr_t.position, prev_pos)
        self._prev_root_positions[instance.instance_id] = curr_t.position

        delta = RootMotionDelta(translation=delta_trans, rotation=curr_t.rotation)
        if instance.root_motion_mode == RootMotionMode.EXTRACT_DELTA:
            instance.accumulated_root_motion.translation = vec3_add(
                instance.accumulated_root_motion.translation, delta.translation
            )
        return delta

    def check_clip_events(
        self,
        clip: AnimationClip,
        prev_time: float,
        curr_time: float,
    ) -> List[AnimEvent]:
        """Collect animation events that trigger between prev_time and curr_time."""
        events: List[AnimEvent] = []
        if not clip.events:
            return events

        # Handle wrap around if looping
        t_start = prev_time % clip.duration if clip.duration > 1e-6 else 0.0
        t_end = curr_time % clip.duration if clip.duration > 1e-6 else 0.0

        for ev in clip.events:
            if t_start <= t_end:
                if t_start <= ev.time <= t_end:
                    events.append(ev)
            else:
                # Wrap-around across loop boundary
                if ev.time >= t_start or ev.time <= t_end:
                    events.append(ev)
        return events

    # --------------------------------------------------------------------------
    # 10. SIMULATION TICK
    # --------------------------------------------------------------------------

    def tick(self, delta_time: float = 1.0 / 60.0) -> List[AnimEvent]:
        """Perform a single deterministic simulation tick of the animation world."""
        if self.world.state != AnimationWorldState.RUNNING:
            return []

        effective_dt = delta_time
        self.simulation_time += effective_dt
        self.current_tick_index += 1
        dispatched_events: List[AnimEvent] = []

        for inst_id, instance in self.world.instances.items():
            skeleton = self.world.skeletons.get(instance.skeleton_id)
            if not skeleton:
                continue

            # LOD evaluation
            lod_settings = self.world.settings.lod_settings
            lod_level = lod_settings.get_lod_for_distance(instance.camera_distance)
            instance.current_lod_level = lod_level.level
            instance.ticks_since_last_eval += 1

            if instance.ticks_since_last_eval < lod_level.tick_rate_divisor:
                # Skip evaluation this tick according to LOD divisor
                continue
            instance.ticks_since_last_eval = 0

            prev_time = instance.elapsed_time_in_state

            # 1. Evaluate base motion (State Machine or Clip)
            if instance.active_state_machine_id and instance.active_state_machine_id in self.world.state_machines:
                sm = self.world.state_machines[instance.active_state_machine_id]
                evaluated_pose = self.evaluate_state_machine(sm, instance, skeleton, effective_dt)
            else:
                # Default pose from bind poses
                evaluated_pose = Pose(
                    skeleton_id=skeleton.skeleton_id,
                    bone_transforms={b: bone.bind_pose_local.copy() for b, bone in skeleton.bones.items()},
                )

            # 2. Evaluate Layers
            for layer_id in instance.active_layers:
                layer = self.world.layers.get(layer_id)
                if not layer:
                    continue
                layer_pose = evaluated_pose
                if layer.state_machine_id and layer.state_machine_id in self.world.state_machines:
                    l_sm = self.world.state_machines[layer.state_machine_id]
                    layer_pose = self.evaluate_state_machine(l_sm, instance, skeleton, effective_dt)
                elif layer.blend_tree_id and layer.blend_tree_id in self.world.blend_trees:
                    l_tree = self.world.blend_trees[layer.blend_tree_id]
                    layer_pose = self.evaluate_blend_tree(l_tree, instance, skeleton, instance.elapsed_time_in_state)

                if layer.blend_mode == LayerBlendMode.OVERRIDE:
                    evaluated_pose = self.blend_poses(evaluated_pose, layer_pose, layer.weight, layer.bone_mask)
                elif layer.blend_mode == LayerBlendMode.ADDITIVE:
                    evaluated_pose = self.add_poses(evaluated_pose, layer_pose, layer.weight)

            # 3. Apply Constraints if enabled
            if self.world.settings.enable_constraints:
                for constraint in self.world.constraints.values():
                    self.apply_constraints(evaluated_pose, skeleton, constraint)

            # 4. Apply IK Solvers if enabled by world and LOD
            if self.world.settings.enable_ik and lod_level.enable_ik:
                for solver in self.world.ik_solvers.values():
                    if solver.solver_type == IKSolverType.TWO_BONE_IK:
                        self.apply_two_bone_ik(evaluated_pose, skeleton, solver)
                    elif solver.solver_type == IKSolverType.LOOK_AT:
                        self.apply_look_at_ik(evaluated_pose, skeleton, solver)

            # 5. Extract Root Motion
            if self.world.settings.enable_root_motion:
                self.extract_root_motion(instance, skeleton, evaluated_pose)

            # 6. Check Events
            if instance.active_state_machine_id and instance.active_state_machine_id in self.world.state_machines:
                sm = self.world.state_machines[instance.active_state_machine_id]
                curr_state = sm.states.get(instance.current_state_id or "")
                if curr_state and curr_state.motion_type == "CLIP":
                    clip = self.world.clips.get(curr_state.motion_id)
                    if clip:
                        evs = self.check_clip_events(clip, prev_time, instance.elapsed_time_in_state)
                        dispatched_events.extend(evs)

            instance.current_pose = evaluated_pose

        self.event_queue.extend(dispatched_events)
        self.world.events.extend(dispatched_events)
        return dispatched_events

    # --------------------------------------------------------------------------
    # 11. SNAPSHOTS, DETERMINISM & REPLAY
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> AnimationSnapshot:
        """Create a deterministic snapshot of the animation world state."""
        snap_id = f"snap_anim_{int(time.time() * 1000)}"
        inst_data = {
            iid: inst.to_dict() for iid, inst in sorted(self.world.instances.items())
        }
        events_data = [e.to_dict() for e in self.world.events]

        snapshot = AnimationSnapshot(
            snapshot_id=snap_id,
            timestamp=self.simulation_time,
            world_state=self.world.state,
            instances=inst_data,
            events_dispatched=events_data,
        )
        self.world.snapshots.append(snapshot)
        return snapshot

    def restore_snapshot(self, snapshot: AnimationSnapshot) -> bool:
        """Restore the animation world state from a snapshot."""
        self.world.state = snapshot.world_state
        self.simulation_time = snapshot.timestamp
        self.world.instances.clear()

        for iid, idata in snapshot.instances.items():
            pose = Pose.from_dict(idata["current_pose"])
            inst = AnimationInstance(
                instance_id=idata["instance_id"],
                entity_id=idata["entity_id"],
                skeleton_id=idata["skeleton_id"],
                current_pose=pose,
                parameters=idata.get("parameters", {}),
                active_state_machine_id=idata.get("active_state_machine_id"),
                current_state_id=idata.get("current_state_id"),
                transition_target_state_id=idata.get("transition_target_state_id"),
                transition_progress=idata.get("transition_progress", 0.0),
                transition_duration=idata.get("transition_duration", 0.0),
                elapsed_time_in_state=idata.get("elapsed_time_in_state", 0.0),
                active_layers=idata.get("active_layers", []),
                root_motion_mode=RootMotionMode(idata.get("root_motion_mode", RootMotionMode.EXTRACT_DELTA.value)),
                ragdoll_state=RagdollState(idata.get("ragdoll_state", RagdollState.ANIMATED.value)),
                ragdoll_blend_weight=idata.get("ragdoll_blend_weight", 0.0),
                camera_distance=idata.get("camera_distance", 0.0),
                current_lod_level=idata.get("current_lod_level", 0),
                ticks_since_last_eval=idata.get("ticks_since_last_eval", 0),
            )
            self.world.instances[iid] = inst
        return True
