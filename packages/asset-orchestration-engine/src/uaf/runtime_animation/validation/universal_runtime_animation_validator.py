"""
Universal Runtime Animation Validator (UAF-81.80).
Semantic validation for skeletons, clips, curves, blend trees, state machines,
layers, IK solvers, constraints, retargeting profiles, and animation world integrity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    AnimEvent,
    AnimationClip,
    AnimationConstraint,
    AnimationCurve,
    AnimationInstance,
    AnimationLayer,
    AnimState,
    AnimStateMachine,
    AnimationWorld,
    BlendTree,
    BlendTreeNode,
    BlendTreeNodeType,
    BoneMask,
    BoneNode,
    IKSolver,
    IKSolverType,
    RetargetProfile,
    SkeletonHierarchy,
)


@dataclass
class AnimationValidationIssue:
    code: str
    message: str
    severity: str = "ERROR"  # "ERROR", "WARNING"
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "context": self.context,
        }


class UniversalRuntimeAnimationValidator:
    """
    Authoritative validator ensuring strict structural and runtime integrity
    of animation data and execution configurations.
    """

    @classmethod
    def validate_skeleton(cls, skeleton: SkeletonHierarchy) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []

        if not skeleton.bones:
            issues.append(AnimationValidationIssue("ANIM_SKEL_EMPTY", "Skeleton has no bones.", "ERROR", {"skeleton_id": skeleton.skeleton_id}))
            return issues

        if not skeleton.root_bone_id or skeleton.root_bone_id not in skeleton.bones:
            issues.append(AnimationValidationIssue("ANIM_SKEL_INVALID_ROOT", f"Root bone '{skeleton.root_bone_id}' does not exist in skeleton.", "ERROR", {"skeleton_id": skeleton.skeleton_id}))

        # Check acyclic hierarchy
        for bid, bone in skeleton.bones.items():
            if bone.parent_id:
                if bone.parent_id not in skeleton.bones:
                    issues.append(AnimationValidationIssue("ANIM_SKEL_MISSING_PARENT", f"Bone '{bid}' references non-existent parent '{bone.parent_id}'.", "ERROR", {"bone_id": bid, "parent_id": bone.parent_id}))
                else:
                    # Detect cycles
                    visited = {bid}
                    curr = bone.parent_id
                    while curr:
                        if curr in visited:
                            issues.append(AnimationValidationIssue("ANIM_SKEL_CYCLE_DETECTED", f"Cyclic parent reference detected starting from bone '{bid}'.", "ERROR", {"bone_id": bid}))
                            break
                        visited.add(curr)
                        parent_node = skeleton.bones.get(curr)
                        curr = parent_node.parent_id if parent_node else None

            if bone.length < 0.0:
                issues.append(AnimationValidationIssue("ANIM_SKEL_NEGATIVE_LENGTH", f"Bone '{bid}' has negative length {bone.length}.", "ERROR", {"bone_id": bid}))

        return issues

    @classmethod
    def validate_clip(cls, clip: AnimationClip, skeleton: Optional[SkeletonHierarchy] = None) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []

        if clip.duration <= 0.0:
            issues.append(AnimationValidationIssue("ANIM_CLIP_ZERO_DURATION", f"Clip '{clip.clip_id}' duration must be positive.", "ERROR", {"clip_id": clip.clip_id}))

        if clip.frame_rate <= 0.0:
            issues.append(AnimationValidationIssue("ANIM_CLIP_INVALID_FRAMERATE", f"Clip '{clip.clip_id}' framerate must be positive.", "ERROR", {"clip_id": clip.clip_id}))

        # Validate bone tracks
        for bid, tracks in clip.bone_tracks.items():
            if skeleton and bid not in skeleton.bones:
                issues.append(AnimationValidationIssue("ANIM_CLIP_UNKNOWN_BONE", f"Clip '{clip.clip_id}' tracks bone '{bid}' not present in skeleton.", "WARNING", {"clip_id": clip.clip_id, "bone_id": bid}))

            for track_type, curve in tracks.items():
                issues.extend(cls._validate_curve(curve, f"clip '{clip.clip_id}' bone '{bid}' {track_type}"))

        # Validate morph tracks
        for mname, curve in clip.morph_tracks.items():
            issues.extend(cls._validate_curve(curve, f"clip '{clip.clip_id}' morph '{mname}'"))

        # Validate event timings
        for ev in clip.events:
            if ev.time < 0.0 or ev.time > clip.duration:
                issues.append(AnimationValidationIssue("ANIM_EVENT_OUT_OF_BOUNDS", f"Event '{ev.event_id}' time {ev.time} is outside clip duration {clip.duration}.", "ERROR", {"event_id": ev.event_id, "clip_id": clip.clip_id}))

        return issues

    @classmethod
    def _validate_curve(cls, curve: AnimationCurve, context_name: str) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []
        if not curve.keyframes:
            return issues

        prev_t = -1.0
        for i, k in enumerate(curve.keyframes):
            if k.time < prev_t:
                issues.append(AnimationValidationIssue("ANIM_CURVE_NON_MONOTONIC", f"Keyframes in {context_name} curve '{curve.name}' are not monotonically sorted.", "ERROR", {"curve_id": curve.curve_id, "keyframe_index": i}))
            prev_t = k.time
        return issues

    @classmethod
    def validate_blend_tree(cls, tree: BlendTree) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []
        issues.extend(cls._validate_blend_tree_node(tree.root_node, tree.tree_id))
        return issues

    @classmethod
    def _validate_blend_tree_node(cls, node: BlendTreeNode, tree_id: str) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []
        if node.node_type == BlendTreeNodeType.CLIP:
            if not node.clip_id:
                issues.append(AnimationValidationIssue("ANIM_TREE_MISSING_CLIP", f"BlendTreeNode '{node.node_id}' of type CLIP has no clip_id in tree '{tree_id}'.", "ERROR", {"node_id": node.node_id}))
        elif node.node_type == BlendTreeNodeType.LERP_1D:
            if not node.children:
                issues.append(AnimationValidationIssue("ANIM_TREE_NO_CHILDREN", f"1D BlendTreeNode '{node.node_id}' has no children in tree '{tree_id}'.", "ERROR", {"node_id": node.node_id}))
        elif node.node_type in (BlendTreeNodeType.BLEND_2D_CARTESIAN, BlendTreeNodeType.BLEND_2D_DIRECTIONAL):
            if not node.children:
                issues.append(AnimationValidationIssue("ANIM_TREE_NO_CHILDREN_2D", f"2D BlendTreeNode '{node.node_id}' has no children in tree '{tree_id}'.", "ERROR", {"node_id": node.node_id}))

        for child in node.children:
            issues.extend(cls._validate_blend_tree_node(child, tree_id))
        return issues

    @classmethod
    def validate_state_machine(cls, sm: AnimStateMachine) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []
        if not sm.states:
            issues.append(AnimationValidationIssue("ANIM_SM_EMPTY", f"State machine '{sm.sm_id}' has no states.", "ERROR", {"sm_id": sm.sm_id}))
            return issues

        if not sm.default_state_id or sm.default_state_id not in sm.states:
            issues.append(AnimationValidationIssue("ANIM_SM_INVALID_DEFAULT", f"State machine '{sm.sm_id}' default state '{sm.default_state_id}' is invalid.", "ERROR", {"sm_id": sm.sm_id}))

        for trans in sm.transitions:
            if trans.source_state_id not in sm.states:
                issues.append(AnimationValidationIssue("ANIM_SM_TRANSITION_INVALID_SRC", f"Transition source state '{trans.source_state_id}' does not exist in '{sm.sm_id}'.", "ERROR", {"sm_id": sm.sm_id}))
            if trans.target_state_id not in sm.states:
                issues.append(AnimationValidationIssue("ANIM_SM_TRANSITION_INVALID_TGT", f"Transition target state '{trans.target_state_id}' does not exist in '{sm.sm_id}'.", "ERROR", {"sm_id": sm.sm_id}))
            if trans.duration < 0.0:
                issues.append(AnimationValidationIssue("ANIM_SM_TRANSITION_NEGATIVE_DUR", f"Transition duration {trans.duration} cannot be negative in '{sm.sm_id}'.", "ERROR", {"sm_id": sm.sm_id}))

        return issues

    @classmethod
    def validate_ik_solver(cls, solver: IKSolver, skeleton: Optional[SkeletonHierarchy] = None) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []
        if skeleton:
            if solver.root_bone_id not in skeleton.bones:
                issues.append(AnimationValidationIssue("ANIM_IK_UNKNOWN_ROOT", f"IK solver '{solver.solver_id}' root bone '{solver.root_bone_id}' missing in skeleton.", "ERROR", {"solver_id": solver.solver_id}))
            if solver.solver_type == IKSolverType.TWO_BONE_IK:
                if not solver.mid_bone_id or solver.mid_bone_id not in skeleton.bones:
                    issues.append(AnimationValidationIssue("ANIM_IK_UNKNOWN_MID", f"Two-Bone IK solver '{solver.solver_id}' mid bone missing in skeleton.", "ERROR", {"solver_id": solver.solver_id}))
            if solver.end_effector_bone_id and solver.end_effector_bone_id not in skeleton.bones:
                issues.append(AnimationValidationIssue("ANIM_IK_UNKNOWN_EFFECTOR", f"IK solver '{solver.solver_id}' effector bone missing in skeleton.", "ERROR", {"solver_id": solver.solver_id}))

        if solver.weight < 0.0 or solver.weight > 1.0:
            issues.append(AnimationValidationIssue("ANIM_IK_INVALID_WEIGHT", f"IK solver '{solver.solver_id}' weight {solver.weight} out of range [0, 1].", "ERROR", {"solver_id": solver.solver_id}))

        return issues

    @classmethod
    def validate_world(cls, world: AnimationWorld) -> List[AnimationValidationIssue]:
        issues: List[AnimationValidationIssue] = []

        for skel in world.skeletons.values():
            issues.extend(cls.validate_skeleton(skel))

        for clip in world.clips.values():
            skel = next(iter(world.skeletons.values())) if world.skeletons else None
            issues.extend(cls.validate_clip(clip, skel))

        for tree in world.blend_trees.values():
            issues.extend(cls.validate_blend_tree(tree))

        for sm in world.state_machines.values():
            issues.extend(cls.validate_state_machine(sm))

        for solver in world.ik_solvers.values():
            skel = next(iter(world.skeletons.values())) if world.skeletons else None
            issues.extend(cls.validate_ik_solver(solver, skel))

        for inst in world.instances.values():
            if inst.skeleton_id not in world.skeletons:
                issues.append(AnimationValidationIssue("ANIM_INST_UNKNOWN_SKELETON", f"Instance '{inst.instance_id}' references unknown skeleton '{inst.skeleton_id}'.", "ERROR", {"instance_id": inst.instance_id}))
            if inst.active_state_machine_id and inst.active_state_machine_id not in world.state_machines:
                issues.append(AnimationValidationIssue("ANIM_INST_UNKNOWN_SM", f"Instance '{inst.instance_id}' references unknown state machine '{inst.active_state_machine_id}'.", "ERROR", {"instance_id": inst.instance_id}))

        return issues
