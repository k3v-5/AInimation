"""
UAF-81.67: Universal Asset Viewport Domain Models and 3D Mathematics.
Authoritative pure-python 3D mathematics (Vectors, Quaternions, 4x4 Matrices, AABBs, Rays, Frustums),
scene graph contracts, camera states, selection modes, gizmos, and cryptographic state snapshots.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class ViewportType(str, Enum):
    PERSPECTIVE = "PERSPECTIVE"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    FRONT = "FRONT"
    BACK = "BACK"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    ORTHOGRAPHIC = "ORTHOGRAPHIC"


class ViewportState(str, Enum):
    CREATED = "CREATED"
    ATTACHED = "ATTACHED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DESTROYED = "DESTROYED"


class CameraMode(str, Enum):
    PERSPECTIVE = "PERSPECTIVE"
    ORTHOGRAPHIC = "ORTHOGRAPHIC"


class ReparentPolicy(str, Enum):
    KEEP_LOCAL = "KEEP_LOCAL"
    KEEP_WORLD = "KEEP_WORLD"


class PivotMode(str, Enum):
    ACTIVE_OBJECT = "ACTIVE_OBJECT"
    MEDIAN = "MEDIAN"
    INDIVIDUAL = "INDIVIDUAL"


class GizmoType(str, Enum):
    TRANSLATE = "TRANSLATE"
    ROTATE = "ROTATE"
    SCALE = "SCALE"
    UNIVERSAL = "UNIVERSAL"


class GizmoAxis(str, Enum):
    NONE = "NONE"
    X = "X"
    Y = "Y"
    Z = "Z"
    XY = "XY"
    XZ = "XZ"
    YZ = "YZ"
    XYZ = "XYZ"
    SCREEN = "SCREEN"
    VIEW = "VIEW"


class GizmoState(str, Enum):
    IDLE = "IDLE"
    HOVERED = "HOVERED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class GizmoOrientation(str, Enum):
    LOCAL = "LOCAL"
    WORLD = "WORLD"


class SnapMode(str, Enum):
    GRID = "GRID"
    ANGLE = "ANGLE"
    SCALE = "SCALE"
    VERTEX = "VERTEX"
    EDGE = "EDGE"
    SURFACE = "SURFACE"


class SelectionMode(str, Enum):
    SET = "SET"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    TOGGLE = "TOGGLE"


class MarqueeMode(str, Enum):
    TOUCH = "TOUCH"
    CONTAIN = "CONTAIN"


class ViewportInputMode(str, Enum):
    CAMERA_NAV = "CAMERA_NAV"
    SELECTION = "SELECTION"
    GIZMO_DRAG = "GIZMO_DRAG"
    PAN = "PAN"
    ORBIT = "ORBIT"
    DOLLY = "DOLLY"


class RenderPassType(str, Enum):
    SCENE_PASS = "SCENE_PASS"
    GRID_PASS = "GRID_PASS"
    OVERLAY_PASS = "OVERLAY_PASS"
    GIZMO_PASS = "GIZMO_PASS"
    SELECTION_OUTLINE = "SELECTION_OUTLINE"
    BOUNDS_PASS = "BOUNDS_PASS"


class BoundsType(str, Enum):
    AABB = "AABB"
    SPHERE = "SPHERE"
    OBB = "OBB"


class TransformDirtyFlags(str, Enum):
    LOCAL_DIRTY = "LOCAL_DIRTY"
    WORLD_DIRTY = "WORLD_DIRTY"
    BOUNDS_DIRTY = "BOUNDS_DIRTY"


# ==============================================================================
# 3D MATHEMATICAL FOUNDATIONS
# ==============================================================================

@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3:
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vector3:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector3:
        if scalar == 0.0:
            return Vector3(0.0, 0.0, 0.0)
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def dot(self, other: Vector3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3) -> Vector3:
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def norm_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def norm(self) -> float:
        return math.sqrt(self.norm_squared())

    def normalized(self) -> Vector3:
        n = self.norm()
        if n < 1e-9:
            return Vector3(0.0, 0.0, 0.0)
        return self / n

    def distance_to(self, other: Vector3) -> float:
        return (self - other).norm()

    def is_finite(self) -> bool:
        return math.isfinite(self.x) and math.isfinite(self.y) and math.isfinite(self.z)

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @classmethod
    def zero(cls) -> Vector3:
        return cls(0.0, 0.0, 0.0)

    @classmethod
    def one(cls) -> Vector3:
        return cls(1.0, 1.0, 1.0)

    @classmethod
    def unit_x(cls) -> Vector3:
        return cls(1.0, 0.0, 0.0)

    @classmethod
    def unit_y(cls) -> Vector3:
        return cls(0.0, 1.0, 0.0)

    @classmethod
    def unit_z(cls) -> Vector3:
        return cls(0.0, 0.0, 1.0)


@dataclass
class Quaternion:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    @classmethod
    def identity(cls) -> Quaternion:
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def from_euler(cls, pitch_deg: float, yaw_deg: float, roll_deg: float) -> Quaternion:
        p = math.radians(pitch_deg) * 0.5
        y = math.radians(yaw_deg) * 0.5
        r = math.radians(roll_deg) * 0.5

        sin_p = math.sin(p)
        cos_p = math.cos(p)
        sin_y = math.sin(y)
        cos_y = math.cos(y)
        sin_r = math.sin(r)
        cos_r = math.cos(r)

        return cls(
            x=sin_r * cos_p * cos_y - cos_r * sin_p * sin_y,
            y=cos_r * sin_p * cos_y + sin_r * cos_p * sin_y,
            z=cos_r * cos_p * sin_y - sin_r * sin_p * cos_y,
            w=cos_r * cos_p * cos_y + sin_r * sin_p * sin_y
        ).normalized()

    def to_euler(self) -> Tuple[float, float, float]:
        # returns (pitch_deg, yaw_deg, roll_deg)
        sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
        cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (self.w * self.y - self.z * self.x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)
        else:
            pitch = math.asin(sinp)

        siny_cosp = 2 * (self.w * self.z + self.x * self.y)
        cosy_cosp = 1 - 2 * (self.y * self.y + self.z * self.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return (math.degrees(pitch), math.degrees(yaw), math.degrees(roll))

    def multiply(self, other: Quaternion) -> Quaternion:
        return Quaternion(
            w=self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            x=self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            y=self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            z=self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        ).normalized()

    def __mul__(self, other: Quaternion) -> Quaternion:
        return self.multiply(other)

    def normalized(self) -> Quaternion:
        n = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z + self.w * self.w)
        if n < 1e-9:
            return Quaternion.identity()
        return Quaternion(self.x / n, self.y / n, self.z / n, self.w / n)

    def conjugate(self) -> Quaternion:
        return Quaternion(-self.x, -self.y, -self.z, self.w)

    def rotate_vector(self, v: Vector3) -> Vector3:
        q_v = Quaternion(v.x, v.y, v.z, 0.0)
        res = self.multiply(q_v).multiply(self.conjugate())
        return Vector3(res.x, res.y, res.z)

    def is_finite(self) -> bool:
        return math.isfinite(self.x) and math.isfinite(self.y) and math.isfinite(self.z) and math.isfinite(self.w)


@dataclass
class Matrix4:
    """Row-major 4x4 transformation matrix."""
    m: List[float] = field(default_factory=lambda: [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ])

    @classmethod
    def identity(cls) -> Matrix4:
        return cls()

    @classmethod
    def translation(cls, v: Vector3) -> Matrix4:
        return cls([
            1.0, 0.0, 0.0, v.x,
            0.0, 1.0, 0.0, v.y,
            0.0, 0.0, 1.0, v.z,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def scaling(cls, s: Vector3) -> Matrix4:
        return cls([
            s.x, 0.0, 0.0, 0.0,
            0.0, s.y, 0.0, 0.0,
            0.0, 0.0, s.z, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def rotation_quaternion(cls, q: Quaternion) -> Matrix4:
        x2 = q.x + q.x
        y2 = q.y + q.y
        z2 = q.z + q.z
        xx = q.x * x2
        xy = q.x * y2
        xz = q.x * z2
        yy = q.y * y2
        yz = q.y * z2
        zz = q.z * z2
        wx = q.w * x2
        wy = q.w * y2
        wz = q.w * z2

        return cls([
            1.0 - (yy + zz), xy - wz, xz + wy, 0.0,
            xy + wz, 1.0 - (xx + zz), yz - wx, 0.0,
            xz - wy, yz + wx, 1.0 - (xx + yy), 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def from_trs(cls, t: Vector3, r: Quaternion, s: Vector3) -> Matrix4:
        mt = cls.translation(t)
        mr = cls.rotation_quaternion(r)
        ms = cls.scaling(s)
        return mt.multiply(mr).multiply(ms)

    def multiply(self, other: Matrix4) -> Matrix4:
        res = [0.0] * 16
        for r in range(4):
            for c in range(4):
                val = 0.0
                for k in range(4):
                    val += self.m[r * 4 + k] * other.m[k * 4 + c]
                res[r * 4 + c] = val
        return Matrix4(res)

    def __mul__(self, other: Matrix4) -> Matrix4:
        return self.multiply(other)

    def transform_point(self, p: Vector3) -> Vector3:
        w = self.m[12] * p.x + self.m[13] * p.y + self.m[14] * p.z + self.m[15]
        if abs(w) < 1e-9:
            w = 1.0
        return Vector3(
            (self.m[0] * p.x + self.m[1] * p.y + self.m[2] * p.z + self.m[3]) / w,
            (self.m[4] * p.x + self.m[5] * p.y + self.m[6] * p.z + self.m[7]) / w,
            (self.m[8] * p.x + self.m[9] * p.y + self.m[10] * p.z + self.m[11]) / w,
        )

    def transform_vector(self, v: Vector3) -> Vector3:
        return Vector3(
            self.m[0] * v.x + self.m[1] * v.y + self.m[2] * v.z,
            self.m[4] * v.x + self.m[5] * v.y + self.m[6] * v.z,
            self.m[8] * v.x + self.m[9] * v.y + self.m[10] * v.z,
        )

    def invert(self) -> Matrix4:
        # Standard 4x4 matrix inversion
        inv = [0.0] * 16
        m = self.m

        inv[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] + m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10]
        inv[4] = -m[4] * m[10] * m[15] + m[4] * m[11] * m[14] + m[8] * m[6] * m[15] - m[8] * m[7] * m[14] - m[12] * m[6] * m[11] + m[12] * m[7] * m[10]
        inv[8] = m[4] * m[9] * m[15] - m[4] * m[11] * m[13] - m[8] * m[5] * m[15] + m[8] * m[7] * m[13] + m[12] * m[5] * m[11] - m[12] * m[7] * m[9]
        inv[12] = -m[4] * m[9] * m[14] + m[4] * m[10] * m[13] + m[8] * m[5] * m[14] - m[8] * m[6] * m[13] - m[12] * m[5] * m[10] + m[12] * m[6] * m[9]

        inv[1] = -m[1] * m[10] * m[15] + m[1] * m[11] * m[14] + m[9] * m[2] * m[15] - m[9] * m[3] * m[14] - m[13] * m[2] * m[11] + m[13] * m[3] * m[10]
        inv[5] = m[0] * m[10] * m[15] - m[0] * m[11] * m[14] - m[8] * m[2] * m[15] + m[8] * m[3] * m[14] + m[12] * m[2] * m[11] - m[12] * m[3] * m[10]
        inv[9] = -m[0] * m[9] * m[15] + m[0] * m[11] * m[13] + m[8] * m[1] * m[15] - m[8] * m[3] * m[13] - m[12] * m[1] * m[11] + m[12] * m[3] * m[9]
        inv[13] = m[0] * m[9] * m[14] - m[0] * m[10] * m[13] - m[8] * m[1] * m[14] + m[8] * m[2] * m[13] + m[12] * m[1] * m[10] - m[12] * m[2] * m[9]

        inv[2] = m[1] * m[6] * m[15] - m[1] * m[7] * m[14] - m[5] * m[2] * m[15] + m[5] * m[3] * m[14] + m[13] * m[2] * m[7] - m[13] * m[3] * m[6]
        inv[6] = -m[0] * m[6] * m[15] + m[0] * m[7] * m[14] + m[4] * m[2] * m[15] - m[4] * m[3] * m[14] - m[12] * m[2] * m[7] + m[12] * m[3] * m[6]
        inv[10] = m[0] * m[5] * m[15] - m[0] * m[7] * m[13] - m[4] * m[1] * m[15] + m[4] * m[3] * m[13] + m[12] * m[1] * m[7] - m[12] * m[3] * m[5]
        inv[14] = -m[0] * m[5] * m[14] + m[0] * m[6] * m[13] + m[4] * m[1] * m[14] - m[4] * m[2] * m[13] - m[12] * m[1] * m[6] + m[12] * m[2] * m[5]

        inv[3] = -m[1] * m[6] * m[11] + m[1] * m[7] * m[10] + m[5] * m[2] * m[11] - m[5] * m[3] * m[10] - m[9] * m[2] * m[7] + m[9] * m[3] * m[6]
        inv[7] = m[0] * m[6] * m[11] - m[0] * m[7] * m[10] - m[4] * m[2] * m[11] + m[4] * m[3] * m[10] + m[8] * m[2] * m[7] - m[8] * m[3] * m[6]
        inv[11] = -m[0] * m[5] * m[11] + m[0] * m[7] * m[9] + m[4] * m[1] * m[11] - m[4] * m[3] * m[9] - m[8] * m[1] * m[7] + m[8] * m[3] * m[5]
        inv[15] = m[0] * m[5] * m[10] - m[0] * m[6] * m[9] - m[4] * m[1] * m[10] + m[4] * m[2] * m[9] + m[8] * m[1] * m[6] - m[8] * m[2] * m[5]

        det = m[0] * inv[0] + m[1] * inv[4] + m[2] * inv[8] + m[3] * inv[12]
        if abs(det) < 1e-12:
            return Matrix4.identity()

        inv_det = 1.0 / det
        return Matrix4([val * inv_det for val in inv])

    @classmethod
    def look_at(cls, eye: Vector3, target: Vector3, up: Vector3) -> Matrix4:
        f = (target - eye).normalized()
        s = f.cross(up).normalized()
        u = s.cross(f)

        return cls([
            s.x, s.y, s.z, -s.dot(eye),
            u.x, u.y, u.z, -u.dot(eye),
            -f.x, -f.y, -f.z, f.dot(eye),
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def perspective(cls, fov_deg: float, aspect: float, near: float, far: float) -> Matrix4:
        tan_half_fov = math.tan(math.radians(fov_deg) * 0.5)
        m00 = 1.0 / (aspect * tan_half_fov)
        m11 = 1.0 / tan_half_fov
        m22 = -(far + near) / (far - near)
        m23 = -(2.0 * far * near) / (far - near)

        return cls([
            m00, 0.0, 0.0, 0.0,
            0.0, m11, 0.0, 0.0,
            0.0, 0.0, m22, m23,
            0.0, 0.0, -1.0, 0.0,
        ])

    @classmethod
    def orthographic(cls, width: float, height: float, near: float, far: float) -> Matrix4:
        m00 = 2.0 / width
        m11 = 2.0 / height
        m22 = -2.0 / (far - near)
        m23 = -(far + near) / (far - near)

        return cls([
            m00, 0.0, 0.0, 0.0,
            0.0, m11, 0.0, 0.0,
            0.0, 0.0, m22, m23,
            0.0, 0.0, 0.0, 1.0,
        ])

    def is_finite(self) -> bool:
        return all(math.isfinite(x) for x in self.m)


# ==============================================================================
# BOUNDS, RAYS & FRUSTUM
# ==============================================================================

@dataclass
class Ray:
    origin: Vector3 = field(default_factory=Vector3.zero)
    direction: Vector3 = field(default_factory=Vector3.unit_z)

    def point_at(self, t: float) -> Vector3:
        return self.origin + self.direction * t

    def intersects_sphere(self, center: Vector3, radius: float) -> Tuple[bool, float]:
        oc = self.origin - center
        a = self.direction.dot(self.direction)
        b = 2.0 * oc.dot(self.direction)
        c = oc.dot(oc) - radius * radius
        disc = b * b - 4 * a * c
        if disc < 0:
            return (False, 0.0)
        t = (-b - math.sqrt(disc)) / (2.0 * a)
        if t < 0:
            t = (-b + math.sqrt(disc)) / (2.0 * a)
        return (t >= 0, max(0.0, t))


@dataclass
class AABB:
    min_point: Vector3 = field(default_factory=lambda: Vector3(-0.5, -0.5, -0.5))
    max_point: Vector3 = field(default_factory=lambda: Vector3(0.5, 0.5, 0.5))

    @property
    def center(self) -> Vector3:
        return (self.min_point + self.max_point) * 0.5

    @property
    def extents(self) -> Vector3:
        return (self.max_point - self.min_point) * 0.5

    @property
    def size(self) -> Vector3:
        return self.max_point - self.min_point

    def contains_point(self, p: Vector3) -> bool:
        return (self.min_point.x <= p.x <= self.max_point.x and
                self.min_point.y <= p.y <= self.max_point.y and
                self.min_point.z <= p.z <= self.max_point.z)

    def intersects_aabb(self, other: AABB) -> bool:
        return (self.min_point.x <= other.max_point.x and self.max_point.x >= other.min_point.x and
                self.min_point.y <= other.max_point.y and self.max_point.y >= other.min_point.y and
                self.min_point.z <= other.max_point.z and self.max_point.z >= other.min_point.z)

    def intersects_ray(self, ray: Ray) -> Tuple[bool, float]:
        tmin = -float("inf")
        tmax = float("inf")

        for i in range(3):
            orig = (ray.origin.x, ray.origin.y, ray.origin.z)[i]
            dir_ = (ray.direction.x, ray.direction.y, ray.direction.z)[i]
            min_ = (self.min_point.x, self.min_point.y, self.min_point.z)[i]
            max_ = (self.max_point.x, self.max_point.y, self.max_point.z)[i]

            if abs(dir_) < 1e-9:
                if orig < min_ or orig > max_:
                    return (False, 0.0)
            else:
                t1 = (min_ - orig) / dir_
                t2 = (max_ - orig) / dir_
                if t1 > t2:
                    t1, t2 = t2, t1
                tmin = max(tmin, t1)
                tmax = min(tmax, t2)
                if tmin > tmax or tmax < 0:
                    return (False, 0.0)

        dist = tmin if tmin >= 0 else tmax
        return (True, dist)

    def transformed(self, m: Matrix4) -> AABB:
        # Transform 8 corners and find new bounding box
        corners = [
            Vector3(self.min_point.x, self.min_point.y, self.min_point.z),
            Vector3(self.max_point.x, self.min_point.y, self.min_point.z),
            Vector3(self.min_point.x, self.max_point.y, self.min_point.z),
            Vector3(self.max_point.x, self.max_point.y, self.min_point.z),
            Vector3(self.min_point.x, self.min_point.y, self.max_point.z),
            Vector3(self.max_point.x, self.min_point.y, self.max_point.z),
            Vector3(self.min_point.x, self.max_point.y, self.max_point.z),
            Vector3(self.max_point.x, self.max_point.y, self.max_point.z),
        ]
        transformed_corners = [m.transform_point(c) for c in corners]
        min_x = min(c.x for c in transformed_corners)
        min_y = min(c.y for c in transformed_corners)
        min_z = min(c.z for c in transformed_corners)
        max_x = max(c.x for c in transformed_corners)
        max_y = max(c.y for c in transformed_corners)
        max_z = max(c.z for c in transformed_corners)
        return AABB(Vector3(min_x, min_y, min_z), Vector3(max_x, max_y, max_z))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min": [round(self.min_point.x, 3), round(self.min_point.y, 3), round(self.min_point.z, 3)],
            "max": [round(self.max_point.x, 3), round(self.max_point.y, 3), round(self.max_point.z, 3)]
        }


@dataclass
class Plane:
    normal: Vector3 = field(default_factory=Vector3.unit_y)
    distance: float = 0.0

    def signed_distance_to_point(self, point: Vector3) -> float:
        return self.normal.dot(point) + self.distance


@dataclass
class Frustum:
    planes: List[Plane] = field(default_factory=list)  # left, right, bottom, top, near, far

    def contains_point(self, p: Vector3) -> bool:
        return all(plane.signed_distance_to_point(p) >= 0 for plane in self.planes)

    def contains_sphere(self, center: Vector3, radius: float) -> bool:
        return all(plane.signed_distance_to_point(center) >= -radius for plane in self.planes)

    def contains_aabb(self, aabb: AABB) -> bool:
        for plane in self.planes:
            # Positive vertex test
            p_vertex = Vector3(
                aabb.max_point.x if plane.normal.x >= 0 else aabb.min_point.x,
                aabb.max_point.y if plane.normal.y >= 0 else aabb.min_point.y,
                aabb.max_point.z if plane.normal.z >= 0 else aabb.min_point.z
            )
            if plane.signed_distance_to_point(p_vertex) < 0:
                return False
        return True


# ==============================================================================
# SCENE GRAPH & VIEWPORT DATA STRUCTURES
# ==============================================================================

@dataclass
class Transform:
    position: Vector3 = field(default_factory=Vector3.zero)
    rotation: Quaternion = field(default_factory=Quaternion.identity)
    scale: Vector3 = field(default_factory=Vector3.one)

    def to_matrix(self) -> Matrix4:
        return Matrix4.from_trs(self.position, self.rotation, self.scale)

    def is_finite(self) -> bool:
        return self.position.is_finite() and self.rotation.is_finite() and self.scale.is_finite()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pos": [round(self.position.x, 3), round(self.position.y, 3), round(self.position.z, 3)],
            "rot": [round(self.rotation.x, 4), round(self.rotation.y, 4), round(self.rotation.z, 4), round(self.rotation.w, 4)],
            "scale": [round(self.scale.x, 3), round(self.scale.y, 3), round(self.scale.z, 3)]
        }


@dataclass
class SceneNode:
    node_id: str
    name: str = ""
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    local_transform: Transform = field(default_factory=Transform)
    world_transform: Transform = field(default_factory=Transform)
    world_matrix: Matrix4 = field(default_factory=Matrix4.identity)
    local_aabb: AABB = field(default_factory=AABB)
    world_aabb: AABB = field(default_factory=AABB)
    visibility: bool = True
    locked: bool = False
    layer: str = "default"
    dirty_flags: Set[TransformDirtyFlags] = field(default_factory=lambda: {TransformDirtyFlags.WORLD_DIRTY, TransformDirtyFlags.BOUNDS_DIRTY})


@dataclass
class CameraState:
    position: Vector3 = field(default_factory=lambda: Vector3(0.0, 0.0, 10.0))
    target: Vector3 = field(default_factory=Vector3.zero)
    up: Vector3 = field(default_factory=Vector3.unit_y)
    fov_deg: float = 60.0
    aspect_ratio: float = 16.0 / 9.0
    near_clip: float = 0.1
    far_clip: float = 1000.0
    ortho_width: float = 10.0
    ortho_height: float = 10.0
    mode: CameraMode = CameraMode.PERSPECTIVE

    def get_view_matrix(self) -> Matrix4:
        return Matrix4.look_at(self.position, self.target, self.up)

    def get_projection_matrix(self) -> Matrix4:
        if self.mode == CameraMode.ORTHOGRAPHIC:
            return Matrix4.orthographic(self.ortho_width, self.ortho_height, self.near_clip, self.far_clip)
        return Matrix4.perspective(self.fov_deg, self.aspect_ratio, self.near_clip, self.far_clip)

    def get_view_projection_matrix(self) -> Matrix4:
        return self.get_projection_matrix().multiply(self.get_view_matrix())


@dataclass
class PickResult:
    node_id: str
    distance: float
    hit_point: Vector3
    normal: Vector3 = field(default_factory=Vector3.unit_y)


@dataclass
class GizmoHandle:
    gizmo_type: GizmoType
    axis: GizmoAxis
    state: GizmoState = GizmoState.IDLE
    bounds: AABB = field(default_factory=AABB)


@dataclass
class SnapSettings:
    enabled: bool = False
    grid_spacing: float = 1.0
    angle_increment_deg: float = 15.0
    scale_increment: float = 0.1
    threshold_pixels: float = 10.0


@dataclass
class SelectionState:
    selected_node_ids: List[str] = field(default_factory=list)
    active_node_id: Optional[str] = None
    selection_history: List[List[str]] = field(default_factory=list)


@dataclass
class TransformTransaction:
    transaction_id: str
    node_ids: List[str]
    initial_transforms: Dict[str, Transform]
    current_transforms: Dict[str, Transform]
    is_active: bool = True
    is_committed: bool = False


@dataclass
class ViewportRenderCommand:
    pass_type: RenderPassType
    node_id: str
    matrix: Matrix4
    color_hex: str = "#FFFFFF"
    wireframe: bool = False
    z_order: int = 0


@dataclass
class ViewportStateSnapshot:
    viewport_id: str
    camera_pos: List[float]
    camera_target: List[float]
    selection: List[str]
    nodes_count: int
    transforms_summary: Dict[str, Any]
    state_hash: str = ""

    def compute_hash(self) -> str:
        data = {
            "viewport_id": self.viewport_id,
            "camera_pos": self.camera_pos,
            "camera_target": self.camera_target,
            "selection": sorted(self.selection),
            "nodes_count": self.nodes_count,
            "transforms_summary": self.transforms_summary
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()


@dataclass
class ViewportTelemetry:
    fps: float = 60.0
    frame_time_ms: float = 16.6
    total_nodes: int = 0
    visible_nodes: int = 0
    culled_nodes: int = 0
    rendered_nodes: int = 0
    picking_time_ms: float = 0.0
    active_gizmo: str = "NONE"


@dataclass
class ViewportDiagnosticBundle:
    bundle_id: str
    timestamp: float
    viewport_id: str
    snapshot: ViewportStateSnapshot
    telemetry: ViewportTelemetry
    signature: str = ""

    def sign(self) -> str:
        data = f"{self.bundle_id}:{self.timestamp}:{self.viewport_id}:{self.snapshot.state_hash}:{self.telemetry.total_nodes}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.sign()


# Collision-safe aliases for root uaf export
ViewportAABB = AABB
ViewportSceneNode = SceneNode
