"""
Universal Runtime Animation World System — Models & Definition (UAF-81.80).
Normative domain models, math helpers, bone hierarchies, poses, curves, clips,
blend trees, state machines, layers, IK solvers, constraints, root motion,
ragdoll profiles, events, retargeting, LOD, and deterministic snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union


def copy_dict_deterministic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a recursively sorted canonical dictionary."""
    out = {}
    for k in sorted(data.keys()):
        v = data[k]
        if isinstance(v, dict):
            out[k] = copy_dict_deterministic(v)
        elif isinstance(v, list):
            out[k] = [
                copy_dict_deterministic(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            out[k] = v
    return out


# ==============================================================================
# ENUMS
# ==============================================================================

class AnimationWorldState(str, Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class InterpolationType(str, Enum):
    STEP = "STEP"
    LINEAR = "LINEAR"
    CUBIC_HERMITE = "CUBIC_HERMITE"
    SPHERICAL_SLERP = "SPHERICAL_SLERP"


class BlendTreeNodeType(str, Enum):
    CLIP = "CLIP"
    LERP_1D = "LERP_1D"
    BLEND_2D_CARTESIAN = "BLEND_2D_CARTESIAN"
    BLEND_2D_DIRECTIONAL = "BLEND_2D_DIRECTIONAL"
    ADDITIVE = "ADDITIVE"


class LayerBlendMode(str, Enum):
    OVERRIDE = "OVERRIDE"
    ADDITIVE = "ADDITIVE"


class IKSolverType(str, Enum):
    TWO_BONE_IK = "TWO_BONE_IK"
    LOOK_AT = "LOOK_AT"
    CCD_IK = "CCD_IK"
    FABRIK = "FABRIK"


class ConstraintType(str, Enum):
    POSITION = "POSITION"
    ROTATION = "ROTATION"
    SCALE = "SCALE"
    AIM = "AIM"
    PARENT = "PARENT"


class RootMotionMode(str, Enum):
    IGNORE = "IGNORE"
    EXTRACT_DELTA = "EXTRACT_DELTA"
    APPLY_TO_ACTOR = "APPLY_TO_ACTOR"


class RagdollState(str, Enum):
    ANIMATED = "ANIMATED"
    BLENDING_TO_PHYSICS = "BLENDING_TO_PHYSICS"
    RAGDOLL = "RAGDOLL"
    BLENDING_TO_ANIMATION = "BLENDING_TO_ANIMATION"


class AnimEventType(str, Enum):
    NOTIFY = "NOTIFY"
    FOOTSTEP = "FOOTSTEP"
    SOUND_TRIGGER = "SOUND_TRIGGER"
    VFX_TRIGGER = "VFX_TRIGGER"
    GAMEPLAY_EVENT = "GAMEPLAY_EVENT"
    CUSTOM = "CUSTOM"


class AnimConditionOperator(str, Enum):
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    GREATER = "GREATER"
    LESS = "LESS"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS_EQUAL = "LESS_EQUAL"
    IS_TRUE = "IS_TRUE"
    IS_FALSE = "IS_FALSE"


# ==============================================================================
# MATH & TRANSFORMS
# ==============================================================================

@dataclass
class Transform3D:
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)  # x, y, z, w
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": [round(float(p), 6) for p in self.position],
            "rotation": [round(float(r), 6) for r in self.rotation],
            "scale": [round(float(s), 6) for s in self.scale],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Transform3D:
        pos = tuple(data.get("position", (0.0, 0.0, 0.0)))
        rot = tuple(data.get("rotation", (0.0, 0.0, 0.0, 1.0)))
        scl = tuple(data.get("scale", (1.0, 1.0, 1.0)))
        return cls(position=(pos[0], pos[1], pos[2]),
                   rotation=(rot[0], rot[1], rot[2], rot[3]),
                   scale=(scl[0], scl[1], scl[2]))

    @classmethod
    def identity(cls) -> Transform3D:
        return cls((0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 1.0), (1.0, 1.0, 1.0))

    def copy(self) -> Transform3D:
        return Transform3D(self.position, self.rotation, self.scale)


def vec3_add(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec3_sub(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> Tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec3_scale(a: Tuple[float, float, float], s: float) -> Tuple[float, float, float]:
    return (a[0] * s, a[1] * s, a[2] * s)


def vec3_dot(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vec3_length(a: Tuple[float, float, float]) -> float:
    return math.sqrt(vec3_dot(a, a))


def vec3_normalize(a: Tuple[float, float, float]) -> Tuple[float, float, float]:
    ln = vec3_length(a)
    if ln < 1e-8:
        return (0.0, 0.0, 0.0)
    return (a[0] / ln, a[1] / ln, a[2] / ln)


def vec3_lerp(a: Tuple[float, float, float], b: Tuple[float, float, float], t: float) -> Tuple[float, float, float]:
    t = max(0.0, min(1.0, t))
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def quat_slerp(q1: Tuple[float, float, float, float], q2: Tuple[float, float, float, float], t: float) -> Tuple[float, float, float, float]:
    t = max(0.0, min(1.0, t))
    dot = q1[0] * q2[0] + q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3]

    q2_mod = q2
    if dot < 0.0:
        dot = -dot
        q2_mod = (-q2[0], -q2[1], -q2[2], -q2[3])

    if dot > 0.9995:
        # Linear interpolation for very close orientations
        res = (
            q1[0] + (q2_mod[0] - q1[0]) * t,
            q1[1] + (q2_mod[1] - q1[1]) * t,
            q1[2] + (q2_mod[2] - q1[2]) * t,
            q1[3] + (q2_mod[3] - q1[3]) * t,
        )
        ln = math.sqrt(sum(x * x for x in res))
        return tuple(x / ln for x in res)  # type: ignore

    theta_0 = math.acos(dot)
    theta = theta_0 * t
    sin_theta = math.sin(theta)
    sin_theta_0 = math.sin(theta_0)

    s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
    s1 = sin_theta / sin_theta_0

    res = (
        (q1[0] * s0) + (q2_mod[0] * s1),
        (q1[1] * s0) + (q2_mod[1] * s1),
        (q1[2] * s0) + (q2_mod[2] * s1),
        (q1[3] * s0) + (q2_mod[3] * s1),
    )
    ln = math.sqrt(sum(x * x for x in res))
    return tuple(x / ln for x in res)  # type: ignore


def quat_multiply(q1: Tuple[float, float, float, float], q2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return (
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    )


def quat_rotate_vec3(q: Tuple[float, float, float, float], v: Tuple[float, float, float]) -> Tuple[float, float, float]:
    qx, qy, qz, qw = q
    vx, vy, vz = v
    # Quaternion rotation: q * (0, v) * q^-1
    tx = 2.0 * (qy * vz - qz * vy)
    ty = 2.0 * (qz * vx - qx * vz)
    tz = 2.0 * (qx * vy - qy * vx)
    return (
        vx + qw * tx + (qy * tz - qz * ty),
        vy + qw * ty + (qz * tx - qx * tz),
        vz + qw * tz + (qx * ty - qy * tx),
    )


def combine_transforms(parent: Transform3D, child: Transform3D) -> Transform3D:
    # Scale child pos by parent scale, rotate by parent rot, add to parent pos
    scaled_pos = (
        child.position[0] * parent.scale[0],
        child.position[1] * parent.scale[1],
        child.position[2] * parent.scale[2],
    )
    rotated_pos = quat_rotate_vec3(parent.rotation, scaled_pos)
    world_pos = vec3_add(parent.position, rotated_pos)
    world_rot = quat_multiply(parent.rotation, child.rotation)
    world_scl = (
        parent.scale[0] * child.scale[0],
        parent.scale[1] * child.scale[1],
        parent.scale[2] * child.scale[2],
    )
    return Transform3D(world_pos, world_rot, world_scl)


# ==============================================================================
# SKELETAL DEFINITION & POSES
# ==============================================================================

@dataclass
class BoneNode:
    bone_id: str
    name: str
    parent_id: Optional[str] = None
    bind_pose_local: Transform3D = field(default_factory=Transform3D.identity)
    length: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bone_id": self.bone_id,
            "name": self.name,
            "parent_id": self.parent_id,
            "bind_pose_local": self.bind_pose_local.to_dict(),
            "length": round(float(self.length), 6),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BoneNode:
        return cls(
            bone_id=data["bone_id"],
            name=data.get("name", data["bone_id"]),
            parent_id=data.get("parent_id"),
            bind_pose_local=Transform3D.from_dict(data.get("bind_pose_local", {})),
            length=float(data.get("length", 1.0)),
        )


@dataclass
class SkeletonHierarchy:
    skeleton_id: str
    name: str
    bones: Dict[str, BoneNode] = field(default_factory=dict)
    root_bone_id: Optional[str] = None

    def add_bone(self, bone: BoneNode) -> None:
        self.bones[bone.bone_id] = bone
        if bone.parent_id is None and self.root_bone_id is None:
            self.root_bone_id = bone.bone_id

    def get_bone(self, bone_id: str) -> Optional[BoneNode]:
        return self.bones.get(bone_id)

    def get_children(self, parent_id: str) -> List[BoneNode]:
        return [b for b in self.bones.values() if b.parent_id == parent_id]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "name": self.name,
            "root_bone_id": self.root_bone_id,
            "bones": {k: b.to_dict() for k, b in sorted(self.bones.items())},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SkeletonHierarchy:
        skel = cls(
            skeleton_id=data["skeleton_id"],
            name=data.get("name", data["skeleton_id"]),
            root_bone_id=data.get("root_bone_id"),
        )
        for bid, bdata in data.get("bones", {}).items():
            skel.add_bone(BoneNode.from_dict(bdata))
        return skel


@dataclass
class Pose:
    skeleton_id: str
    bone_transforms: Dict[str, Transform3D] = field(default_factory=dict)
    morph_weights: Dict[str, float] = field(default_factory=dict)
    evaluated_curves: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "bone_transforms": {k: v.to_dict() for k, v in sorted(self.bone_transforms.items())},
            "morph_weights": {k: round(float(v), 6) for k, v in sorted(self.morph_weights.items())},
            "evaluated_curves": {k: round(float(v), 6) for k, v in sorted(self.evaluated_curves.items())},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Pose:
        transforms = {
            k: Transform3D.from_dict(v)
            for k, v in data.get("bone_transforms", {}).items()
        }
        return cls(
            skeleton_id=data.get("skeleton_id", ""),
            bone_transforms=transforms,
            morph_weights=data.get("morph_weights", {}),
            evaluated_curves=data.get("evaluated_curves", {}),
        )


# ==============================================================================
# KEYFRAMES, CURVES & CLIPS
# ==============================================================================

@dataclass
class Keyframe:
    time: float
    value: Any  # float, Tuple[float, float, float], or Tuple[float, float, float, float]
    in_tangent: float = 0.0
    out_tangent: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": round(float(self.time), 6),
            "value": self.value,
            "in_tangent": round(float(self.in_tangent), 6),
            "out_tangent": round(float(self.out_tangent), 6),
        }


@dataclass
class AnimationCurve:
    curve_id: str
    name: str
    curve_type: str = "FLOAT"  # FLOAT, VECTOR3, QUATERNION
    keyframes: List[Keyframe] = field(default_factory=list)
    interpolation: InterpolationType = InterpolationType.LINEAR

    def evaluate(self, time_sec: float) -> Any:
        if not self.keyframes:
            if self.curve_type == "FLOAT":
                return 0.0
            elif self.curve_type == "VECTOR3":
                return (0.0, 0.0, 0.0)
            elif self.curve_type == "QUATERNION":
                return (0.0, 0.0, 0.0, 1.0)
            return 0.0

        if time_sec <= self.keyframes[0].time:
            return self.keyframes[0].value
        if time_sec >= self.keyframes[-1].time:
            return self.keyframes[-1].value

        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i + 1]
            is_last = (i == len(self.keyframes) - 2)
            in_interval = (k1.time <= time_sec < k2.time) or (is_last and k1.time <= time_sec <= k2.time)
            if in_interval:
                span = k2.time - k1.time
                t = 0.0 if span <= 1e-8 else (time_sec - k1.time) / span

                if self.interpolation == InterpolationType.STEP:
                    if is_last and time_sec >= k2.time:
                        return k2.value
                    return k1.value
                elif self.interpolation == InterpolationType.LINEAR or self.interpolation == InterpolationType.CUBIC_HERMITE:
                    if self.curve_type == "FLOAT":
                        return float(k1.value) + (float(k2.value) - float(k1.value)) * t
                    elif self.curve_type == "VECTOR3":
                        return vec3_lerp(tuple(k1.value), tuple(k2.value), t)  # type: ignore
                    elif self.curve_type == "QUATERNION":
                        return quat_slerp(tuple(k1.value), tuple(k2.value), t)  # type: ignore
                elif self.interpolation == InterpolationType.SPHERICAL_SLERP:
                    if self.curve_type == "QUATERNION":
                        return quat_slerp(tuple(k1.value), tuple(k2.value), t)  # type: ignore

        return self.keyframes[-1].value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "curve_id": self.curve_id,
            "name": self.name,
            "curve_type": self.curve_type,
            "interpolation": self.interpolation.value,
            "keyframes": [k.to_dict() for k in self.keyframes],
        }


@dataclass
class AnimEvent:
    event_id: str
    event_type: AnimEventType
    time: float
    name: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "time": round(float(self.time), 6),
            "name": self.name,
            "payload": copy_dict_deterministic(self.payload),
        }


@dataclass
class AnimationClip:
    clip_id: str
    name: str
    duration: float
    frame_rate: float = 30.0
    looping: bool = True
    # bone_id -> {"position": curve, "rotation": curve, "scale": curve}
    bone_tracks: Dict[str, Dict[str, AnimationCurve]] = field(default_factory=dict)
    # morph_target_name -> curve
    morph_tracks: Dict[str, AnimationCurve] = field(default_factory=dict)
    # generic float curve tracks (e.g. speed, footprints)
    curve_tracks: Dict[str, AnimationCurve] = field(default_factory=dict)
    events: List[AnimEvent] = field(default_factory=list)

    def sample_pose(self, time_sec: float, skeleton: SkeletonHierarchy) -> Pose:
        eval_time = time_sec
        if self.duration > 1e-8:
            if self.looping:
                eval_time = time_sec % self.duration
            else:
                eval_time = max(0.0, min(self.duration, time_sec))

        transforms: Dict[str, Transform3D] = {}
        for bone_id, bone in skeleton.bones.items():
            base = bone.bind_pose_local.copy()
            if bone_id in self.bone_tracks:
                tracks = self.bone_tracks[bone_id]
                if "position" in tracks:
                    pos = tracks["position"].evaluate(eval_time)
                    base.position = (pos[0], pos[1], pos[2])
                if "rotation" in tracks:
                    rot = tracks["rotation"].evaluate(eval_time)
                    base.rotation = (rot[0], rot[1], rot[2], rot[3])
                if "scale" in tracks:
                    scl = tracks["scale"].evaluate(eval_time)
                    base.scale = (scl[0], scl[1], scl[2])
            transforms[bone_id] = base

        morph_weights = {
            m_name: float(m_curve.evaluate(eval_time))
            for m_name, m_curve in self.morph_tracks.items()
        }

        curve_vals = {
            c_name: float(c_curve.evaluate(eval_time))
            for c_name, c_curve in self.curve_tracks.items()
        }

        return Pose(
            skeleton_id=skeleton.skeleton_id,
            bone_transforms=transforms,
            morph_weights=morph_weights,
            evaluated_curves=curve_vals,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "name": self.name,
            "duration": round(float(self.duration), 6),
            "frame_rate": round(float(self.frame_rate), 6),
            "looping": self.looping,
            "bone_tracks": {
                b_id: {t_name: crv.to_dict() for t_name, crv in sorted(tracks.items())}
                for b_id, tracks in sorted(self.bone_tracks.items())
            },
            "morph_tracks": {k: v.to_dict() for k, v in sorted(self.morph_tracks.items())},
            "curve_tracks": {k: v.to_dict() for k, v in sorted(self.curve_tracks.items())},
            "events": [e.to_dict() for e in self.events],
        }


# ==============================================================================
# BLEND TREES
# ==============================================================================

@dataclass
class BlendTreeNode:
    node_id: str
    node_type: BlendTreeNodeType
    clip_id: Optional[str] = None
    parameter_name_x: Optional[str] = None
    parameter_name_y: Optional[str] = None
    threshold: float = 0.0
    position_2d: Tuple[float, float] = (0.0, 0.0)
    children: List[BlendTreeNode] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "clip_id": self.clip_id,
            "parameter_name_x": self.parameter_name_x,
            "parameter_name_y": self.parameter_name_y,
            "threshold": round(float(self.threshold), 6),
            "position_2d": [round(float(p), 6) for p in self.position_2d],
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class BlendTree:
    tree_id: str
    name: str
    root_node: BlendTreeNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tree_id": self.tree_id,
            "name": self.name,
            "root_node": self.root_node.to_dict(),
        }


# ==============================================================================
# ANIMATION STATE MACHINES
# ==============================================================================

@dataclass
class AnimTransitionCondition:
    parameter_name: str
    operator: AnimConditionOperator
    threshold: Any

    def evaluate(self, params: Dict[str, Any]) -> bool:
        if self.parameter_name not in params:
            return False
        val = params[self.parameter_name]
        op = self.operator
        if op == AnimConditionOperator.EQUAL:
            return val == self.threshold
        elif op == AnimConditionOperator.NOT_EQUAL:
            return val != self.threshold
        elif op == AnimConditionOperator.GREATER:
            return float(val) > float(self.threshold)
        elif op == AnimConditionOperator.LESS:
            return float(val) < float(self.threshold)
        elif op == AnimConditionOperator.GREATER_EQUAL:
            return float(val) >= float(self.threshold)
        elif op == AnimConditionOperator.LESS_EQUAL:
            return float(val) <= float(self.threshold)
        elif op == AnimConditionOperator.IS_TRUE:
            return bool(val) is True
        elif op == AnimConditionOperator.IS_FALSE:
            return bool(val) is False
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "parameter_name": self.parameter_name,
            "operator": self.operator.value,
            "threshold": self.threshold,
        }


@dataclass
class AnimTransition:
    source_state_id: str
    target_state_id: str
    duration: float = 0.2
    has_exit_time: bool = False
    exit_time: float = 0.9  # normalized
    conditions: List[AnimTransitionCondition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_state_id": self.source_state_id,
            "target_state_id": self.target_state_id,
            "duration": round(float(self.duration), 6),
            "has_exit_time": self.has_exit_time,
            "exit_time": round(float(self.exit_time), 6),
            "conditions": [c.to_dict() for c in self.conditions],
        }


@dataclass
class AnimState:
    state_id: str
    name: str
    motion_type: str = "CLIP"  # "CLIP" or "BLEND_TREE"
    motion_id: str = ""
    speed: float = 1.0
    loop: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "name": self.name,
            "motion_type": self.motion_type,
            "motion_id": self.motion_id,
            "speed": round(float(self.speed), 6),
            "loop": self.loop,
        }


@dataclass
class AnimStateMachine:
    sm_id: str
    name: str
    states: Dict[str, AnimState] = field(default_factory=dict)
    transitions: List[AnimTransition] = field(default_factory=list)
    default_state_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sm_id": self.sm_id,
            "name": self.name,
            "default_state_id": self.default_state_id,
            "states": {k: s.to_dict() for k, s in sorted(self.states.items())},
            "transitions": [t.to_dict() for t in self.transitions],
        }


# ==============================================================================
# ANIMATION LAYERS & BONE MASKS
# ==============================================================================

@dataclass
class BoneMask:
    mask_id: str
    name: str
    # bone_id -> weight (0.0 to 1.0)
    bone_weights: Dict[str, float] = field(default_factory=dict)

    def get_weight(self, bone_id: str) -> float:
        return self.bone_weights.get(bone_id, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mask_id": self.mask_id,
            "name": self.name,
            "bone_weights": {k: round(float(v), 6) for k, v in sorted(self.bone_weights.items())},
        }


@dataclass
class AnimationLayer:
    layer_id: str
    name: str
    weight: float = 1.0
    blend_mode: LayerBlendMode = LayerBlendMode.OVERRIDE
    bone_mask: Optional[BoneMask] = None
    state_machine_id: Optional[str] = None
    blend_tree_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "name": self.name,
            "weight": round(float(self.weight), 6),
            "blend_mode": self.blend_mode.value,
            "bone_mask": self.bone_mask.to_dict() if self.bone_mask else None,
            "state_machine_id": self.state_machine_id,
            "blend_tree_id": self.blend_tree_id,
        }


# ==============================================================================
# IK SOLVERS & CONSTRAINTS
# ==============================================================================

@dataclass
class IKSolver:
    solver_id: str
    solver_type: IKSolverType
    root_bone_id: str
    mid_bone_id: Optional[str] = None
    end_effector_bone_id: str = ""
    target_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    pole_target_position: Optional[Tuple[float, float, float]] = None
    weight: float = 1.0
    max_iterations: int = 15
    tolerance: float = 0.001

    def to_dict(self) -> Dict[str, Any]:
        return {
            "solver_id": self.solver_id,
            "solver_type": self.solver_type.value,
            "root_bone_id": self.root_bone_id,
            "mid_bone_id": self.mid_bone_id,
            "end_effector_bone_id": self.end_effector_bone_id,
            "target_position": [round(float(p), 6) for p in self.target_position],
            "pole_target_position": [round(float(p), 6) for p in self.pole_target_position] if self.pole_target_position else None,
            "weight": round(float(self.weight), 6),
            "max_iterations": self.max_iterations,
            "tolerance": round(float(self.tolerance), 6),
        }


@dataclass
class AnimationConstraint:
    constraint_id: str
    constraint_type: ConstraintType
    source_bone_id: str
    target_bone_id: Optional[str] = None
    target_static_transform: Optional[Transform3D] = None
    weight: float = 1.0
    maintain_offset: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint_id": self.constraint_id,
            "constraint_type": self.constraint_type.value,
            "source_bone_id": self.source_bone_id,
            "target_bone_id": self.target_bone_id,
            "target_static_transform": self.target_static_transform.to_dict() if self.target_static_transform else None,
            "weight": round(float(self.weight), 6),
            "maintain_offset": self.maintain_offset,
        }


# ==============================================================================
# ROOT MOTION & RAGDOLL
# ==============================================================================

@dataclass
class RootMotionDelta:
    translation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "translation": [round(float(p), 6) for p in self.translation],
            "rotation": [round(float(r), 6) for r in self.rotation],
        }


@dataclass
class RagdollProfile:
    profile_id: str
    name: str
    bone_stiffness: Dict[str, float] = field(default_factory=dict)
    joint_damping: float = 0.1
    blend_recovery_time: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "bone_stiffness": {k: round(float(v), 6) for k, v in sorted(self.bone_stiffness.items())},
            "joint_damping": round(float(self.joint_damping), 6),
            "blend_recovery_time": round(float(self.blend_recovery_time), 6),
        }


# ==============================================================================
# RETARGETING & LOD
# ==============================================================================

@dataclass
class RetargetBoneMapping:
    source_bone_id: str
    target_bone_id: str
    translation_scale: float = 1.0
    rotation_offset: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_bone_id": self.source_bone_id,
            "target_bone_id": self.target_bone_id,
            "translation_scale": round(float(self.translation_scale), 6),
            "rotation_offset": [round(float(r), 6) for r in self.rotation_offset],
        }


@dataclass
class RetargetProfile:
    profile_id: str
    source_skeleton_id: str
    target_skeleton_id: str
    mappings: Dict[str, RetargetBoneMapping] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "source_skeleton_id": self.source_skeleton_id,
            "target_skeleton_id": self.target_skeleton_id,
            "mappings": {k: m.to_dict() for k, m in sorted(self.mappings.items())},
        }


@dataclass
class AnimationLODLevel:
    level: int
    max_distance: float
    tick_rate_divisor: int = 1
    enable_ik: bool = True
    enable_morph_targets: bool = True
    culled_bones: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "max_distance": round(float(self.max_distance), 6),
            "tick_rate_divisor": self.tick_rate_divisor,
            "enable_ik": self.enable_ik,
            "enable_morph_targets": self.enable_morph_targets,
            "culled_bones": sorted(list(self.culled_bones)),
        }


@dataclass
class AnimationLODSettings:
    enabled: bool = True
    levels: List[AnimationLODLevel] = field(default_factory=list)

    def get_lod_for_distance(self, distance: float) -> AnimationLODLevel:
        if not self.levels or not self.enabled:
            return AnimationLODLevel(level=0, max_distance=float("inf"))
        for lvl in sorted(self.levels, key=lambda x: x.max_distance):
            if distance <= lvl.max_distance:
                return lvl
        return self.levels[-1]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "levels": [l.to_dict() for l in self.levels],
        }


# ==============================================================================
# ANIMATION INSTANCE & RUNTIME STATE
# ==============================================================================

@dataclass
class AnimationInstance:
    instance_id: str
    entity_id: str
    skeleton_id: str
    current_pose: Pose
    parameters: Dict[str, Any] = field(default_factory=dict)
    active_state_machine_id: Optional[str] = None
    current_state_id: Optional[str] = None
    transition_target_state_id: Optional[str] = None
    transition_progress: float = 0.0  # 0.0 to 1.0
    transition_duration: float = 0.0
    elapsed_time_in_state: float = 0.0
    active_layers: List[str] = field(default_factory=list)
    root_motion_mode: RootMotionMode = RootMotionMode.EXTRACT_DELTA
    accumulated_root_motion: RootMotionDelta = field(default_factory=RootMotionDelta)
    ragdoll_state: RagdollState = RagdollState.ANIMATED
    ragdoll_blend_weight: float = 0.0
    camera_distance: float = 0.0
    current_lod_level: int = 0
    ticks_since_last_eval: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "entity_id": self.entity_id,
            "skeleton_id": self.skeleton_id,
            "current_pose": self.current_pose.to_dict(),
            "parameters": copy_dict_deterministic(self.parameters),
            "active_state_machine_id": self.active_state_machine_id,
            "current_state_id": self.current_state_id,
            "transition_target_state_id": self.transition_target_state_id,
            "transition_progress": round(float(self.transition_progress), 6),
            "transition_duration": round(float(self.transition_duration), 6),
            "elapsed_time_in_state": round(float(self.elapsed_time_in_state), 6),
            "active_layers": list(self.active_layers),
            "root_motion_mode": self.root_motion_mode.value,
            "accumulated_root_motion": self.accumulated_root_motion.to_dict(),
            "ragdoll_state": self.ragdoll_state.value,
            "ragdoll_blend_weight": round(float(self.ragdoll_blend_weight), 6),
            "camera_distance": round(float(self.camera_distance), 6),
            "current_lod_level": self.current_lod_level,
            "ticks_since_last_eval": self.ticks_since_last_eval,
        }


# ==============================================================================
# TICK & WORLD SETTINGS
# ==============================================================================

@dataclass
class AnimationTick:
    tick_index: int
    simulation_time: float
    delta_time: float
    time_dilation: float = 1.0

    def effective_delta_time(self) -> float:
        return self.delta_time * self.time_dilation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick_index": self.tick_index,
            "simulation_time": round(float(self.simulation_time), 6),
            "delta_time": round(float(self.delta_time), 6),
            "time_dilation": round(float(self.time_dilation), 6),
        }


@dataclass
class AnimationWorldSettings:
    tick_rate_hz: float = 60.0
    deterministic_mode: bool = True
    substepping_enabled: bool = False
    max_substeps: int = 4
    enable_ik: bool = True
    enable_morph_targets: bool = True
    enable_constraints: bool = True
    enable_root_motion: bool = True
    lod_settings: AnimationLODSettings = field(default_factory=AnimationLODSettings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick_rate_hz": round(float(self.tick_rate_hz), 6),
            "deterministic_mode": self.deterministic_mode,
            "substepping_enabled": self.substepping_enabled,
            "max_substeps": self.max_substeps,
            "enable_ik": self.enable_ik,
            "enable_morph_targets": self.enable_morph_targets,
            "enable_constraints": self.enable_constraints,
            "enable_root_motion": self.enable_root_motion,
            "lod_settings": self.lod_settings.to_dict(),
        }


# ==============================================================================
# DETERMINISTIC SNAPSHOT
# ==============================================================================

@dataclass
class AnimationSnapshot:
    snapshot_id: str
    timestamp: float
    world_state: AnimationWorldState
    instances: Dict[str, Dict[str, Any]]
    events_dispatched: List[Dict[str, Any]]
    state_hash: str = ""

    def compute_hash(self) -> str:
        # State hash must be 100% deterministic and only depend on state data
        canonical = {
            "world_state": self.world_state.value,
            "instances": {k: v for k, v in sorted(self.instances.items())},
            "events_dispatched": self.events_dispatched,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": round(float(self.timestamp), 6),
            "world_state": self.world_state.value,
            "instances": self.instances,
            "events_dispatched": self.events_dispatched,
            "state_hash": self.state_hash,
        }


# ==============================================================================
# ANIMATION WORLD CONTAINER
# ==============================================================================

@dataclass
class AnimationWorld:
    animation_world_id: str
    runtime_world_id: str
    state: AnimationWorldState = AnimationWorldState.CREATED
    settings: AnimationWorldSettings = field(default_factory=AnimationWorldSettings)
    skeletons: Dict[str, SkeletonHierarchy] = field(default_factory=dict)
    instances: Dict[str, AnimationInstance] = field(default_factory=dict)
    clips: Dict[str, AnimationClip] = field(default_factory=dict)
    state_machines: Dict[str, AnimStateMachine] = field(default_factory=dict)
    blend_trees: Dict[str, BlendTree] = field(default_factory=dict)
    layers: Dict[str, AnimationLayer] = field(default_factory=dict)
    ik_solvers: Dict[str, IKSolver] = field(default_factory=dict)
    constraints: Dict[str, AnimationConstraint] = field(default_factory=dict)
    retarget_profiles: Dict[str, RetargetProfile] = field(default_factory=dict)
    events: List[AnimEvent] = field(default_factory=list)
    snapshots: List[AnimationSnapshot] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "animation_world_id": self.animation_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "skeletons": {k: v.to_dict() for k, v in sorted(self.skeletons.items())},
            "instances": {k: v.to_dict() for k, v in sorted(self.instances.items())},
            "clips": {k: v.to_dict() for k, v in sorted(self.clips.items())},
            "state_machines": {k: v.to_dict() for k, v in sorted(self.state_machines.items())},
            "blend_trees": {k: v.to_dict() for k, v in sorted(self.blend_trees.items())},
            "layers": {k: v.to_dict() for k, v in sorted(self.layers.items())},
            "ik_solvers": {k: v.to_dict() for k, v in sorted(self.ik_solvers.items())},
            "constraints": {k: v.to_dict() for k, v in sorted(self.constraints.items())},
            "retarget_profiles": {k: v.to_dict() for k, v in sorted(self.retarget_profiles.items())},
            "events": [e.to_dict() for e in self.events],
        }
