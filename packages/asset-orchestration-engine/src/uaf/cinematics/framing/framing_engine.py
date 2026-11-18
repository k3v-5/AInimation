"""
UAF-81.97: Cinematic Framing Engine.
Implements Rule of Thirds, Golden Ratio, Over-The-Shoulder (OTS), 180-Degree Conversational
Axis compliance, and Orbit Boss Reveal compositions.
"""

import math
from typing import Dict, List, Optional, Tuple

from ..core.contracts import (
    Vector3D,
    Rotator3D,
    Transform3D,
    CinematicSubject,
    FramingRule,
    LensSettings,
    CinematicShot,
    CinematicShotType,
    CameraKeyframe,
)


class CinematicFramingEngine:
    """
    Computes mathematically aligned camera transforms according to classical and dynamic
    cinematographic composition principles.
    """

    @staticmethod
    def compute_look_at_rotation(cam_pos: Vector3D, target_pos: Vector3D, roll_deg: float = 0.0) -> Rotator3D:
        """
        Computes pitch, yaw, roll in degrees pointing from cam_pos toward target_pos.
        """
        dx = target_pos.x - cam_pos.x
        dy = target_pos.y - cam_pos.y
        dz = target_pos.z - cam_pos.z

        yaw = math.degrees(math.atan2(dy, dx))
        planar_dist = math.sqrt(dx ** 2 + dy ** 2)
        pitch = math.degrees(math.atan2(dz, max(1e-5, planar_dist)))

        return Rotator3D(pitch=round(pitch, 3), yaw=round(yaw, 3), roll=round(roll_deg, 3))

    @staticmethod
    def frame_subject(
        cam_pos: Vector3D,
        subject: CinematicSubject,
        rule: FramingRule = FramingRule.RULE_OF_THIRDS,
        lens: Optional[LensSettings] = None,
        use_right_side: bool = True,
    ) -> Transform3D:
        """
        Calculates camera orientation placing the subject at the designated composition line
        (Rule of Thirds, Golden Ratio, Center Symmetry, or Low/High Angle).
        """
        lens = lens or LensSettings()
        target_pos = subject.eye_level_pos if subject.eye_level_pos.z != 0 else subject.world_pos

        dist = cam_pos.distance_to(target_pos)
        forward = (target_pos - cam_pos).normalized()
        up = Vector3D(x=0.0, y=0.0, z=1.0)
        right = forward.cross(up).normalized()

        fov_h_rad = lens.compute_horizontal_fov_rad()
        half_width_at_dist = dist * math.tan(fov_h_rad * 0.5)

        aim_pos = target_pos

        if rule == FramingRule.RULE_OF_THIRDS:
            # Place subject at 1/3 (u=0.333) or 2/3 (u=0.667)
            # Offset the aim point in opposite direction
            u = 2.0 / 3.0 if use_right_side else 1.0 / 3.0
            offset_factor = (0.5 - u) * 2.0
            aim_pos = target_pos + right * (offset_factor * half_width_at_dist)

        elif rule == FramingRule.GOLDEN_RATIO:
            # Golden ratio phi: 0.618
            phi = 0.618
            u = phi if use_right_side else (1.0 - phi)
            offset_factor = (0.5 - u) * 2.0
            aim_pos = target_pos + right * (offset_factor * half_width_at_dist)

        elif rule == FramingRule.LOW_ANGLE_HERO:
            # Camera placed lower, looking upwards
            rot = CinematicFramingEngine.compute_look_at_rotation(cam_pos, target_pos)
            return Transform3D(position=cam_pos, rotation=rot)

        elif rule == FramingRule.HIGH_ANGLE_VULNERABLE:
            # Camera placed higher, looking down
            rot = CinematicFramingEngine.compute_look_at_rotation(cam_pos, target_pos)
            return Transform3D(position=cam_pos, rotation=rot)

        # Default: Center Symmetry
        rot = CinematicFramingEngine.compute_look_at_rotation(cam_pos, aim_pos)
        return Transform3D(position=cam_pos, rotation=rot)

    @staticmethod
    def create_over_the_shoulder_shot(
        observer: CinematicSubject,
        target: CinematicSubject,
        shot_id: str = "shot_ots",
        over_right_shoulder: bool = True,
        camera_distance_m: float = 1.8,
        shoulder_offset_m: float = 0.45,
        duration_s: float = 3.5,
        lens: Optional[LensSettings] = None,
    ) -> CinematicShot:
        """
        Creates an Over-The-Shoulder shot looking from behind observer toward target.
        """
        lens = lens or LensSettings(focal_length_mm=50.0, current_aperture_fstop=2.0)
        p_obs = observer.eye_level_pos if observer.eye_level_pos.z != 0 else observer.world_pos
        p_tar = target.eye_level_pos if target.eye_level_pos.z != 0 else target.world_pos

        line_of_sight = (p_tar - p_obs).normalized()
        up = Vector3D(x=0.0, y=0.0, z=1.0)
        right = line_of_sight.cross(up).normalized()

        side_sign = 1.0 if over_right_shoulder else -1.0
        cam_pos = (
            p_obs
            - (line_of_sight * camera_distance_m)
            + (right * (shoulder_offset_m * side_sign))
            + Vector3D(x=0.0, y=0.0, z=0.1)  # Slightly above eye
        )

        transform = CinematicFramingEngine.frame_subject(
            cam_pos=cam_pos,
            subject=target,
            rule=FramingRule.RULE_OF_THIRDS,
            lens=lens,
            use_right_side=not over_right_shoulder,
        )

        keyframe = CameraKeyframe(
            time_seconds=0.0,
            transform=transform,
            focal_length_mm=lens.focal_length_mm,
            aperture_fstop=lens.current_aperture_fstop,
            focus_distance_m=round(cam_pos.distance_to(p_tar), 2),
        )

        return CinematicShot(
            shot_id=shot_id,
            shot_type=CinematicShotType.OVER_THE_SHOULDER,
            framing_rule=FramingRule.RULE_OF_THIRDS,
            duration_s=duration_s,
            primary_subject_id=target.actor_id,
            secondary_subject_id=observer.actor_id,
            lens=lens,
            keyframes=[keyframe],
        )

    @staticmethod
    def verify_180_degree_rule(
        cam_pos_a: Vector3D,
        cam_pos_b: Vector3D,
        subject_a: Vector3D,
        subject_b: Vector3D,
    ) -> bool:
        """
        Verifies that both camera positions lie strictly on the same side of the 2D action line.
        """
        # 2D line from subject_a to subject_b
        dx = subject_b.x - subject_a.x
        dy = subject_b.y - subject_a.y

        # Normal vector in 2D
        nx = -dy
        ny = dx

        # Dot product with normal for cam A
        dot_a = (cam_pos_a.x - subject_a.x) * nx + (cam_pos_a.y - subject_a.y) * ny
        # Dot product with normal for cam B
        dot_b = (cam_pos_b.x - subject_a.x) * nx + (cam_pos_b.y - subject_a.y) * ny

        # If signs match, both cameras are on the same side of the 180 axis line
        return (dot_a * dot_b) > 0.0

    @staticmethod
    def create_shot_reverse_shot_pair(
        subject_a: CinematicSubject,
        subject_b: CinematicSubject,
        duration_each_s: float = 3.0,
    ) -> Tuple[CinematicShot, CinematicShot]:
        """
        Creates a pair of conversational shots conforming strictly to the 180° line of action.
        """
        shot_a = CinematicFramingEngine.create_over_the_shoulder_shot(
            observer=subject_a,
            target=subject_b,
            shot_id="shot_dialogue_to_B",
            over_right_shoulder=True,
            duration_s=duration_each_s,
        )

        shot_b = CinematicFramingEngine.create_over_the_shoulder_shot(
            observer=subject_b,
            target=subject_a,
            shot_id="shot_dialogue_to_A",
            over_right_shoulder=False,  # Kept on same side of 180 line
            duration_s=duration_each_s,
        )

        p_a = subject_a.world_pos
        p_b = subject_b.world_pos
        cam_a = shot_a.keyframes[0].transform.position
        cam_b = shot_b.keyframes[0].transform.position

        # Verify compliance
        is_compliant = CinematicFramingEngine.verify_180_degree_rule(cam_a, cam_b, p_a, p_b)
        if not is_compliant:
            # Flip side if needed
            shot_b = CinematicFramingEngine.create_over_the_shoulder_shot(
                observer=subject_b,
                target=subject_a,
                shot_id="shot_dialogue_to_A",
                over_right_shoulder=True,
                duration_s=duration_each_s,
            )

        return shot_a, shot_b

    @staticmethod
    def create_orbit_boss_reveal(
        boss: CinematicSubject,
        radius_m: float = 6.0,
        start_height_m: float = 0.5,
        end_height_m: float = 3.5,
        total_rotation_deg: float = 120.0,
        duration_s: float = 4.0,
        sample_count: int = 10,
        lens: Optional[LensSettings] = None,
    ) -> CinematicShot:
        """
        Generates an ascending spiral reveal shot orbiting around a boss or landmark.
        """
        lens = lens or LensSettings(focal_length_mm=24.0, current_aperture_fstop=2.8)
        boss_pos = boss.world_pos
        boss_aim = boss.eye_level_pos if boss.eye_level_pos.z != 0 else boss_pos + Vector3D(x=0.0, y=0.0, z=2.0)

        keyframes: List[CameraKeyframe] = []
        for i in range(sample_count):
            fraction = i / max(1, sample_count - 1)
            angle_rad = math.radians(fraction * total_rotation_deg)
            h = start_height_m + (end_height_m - start_height_m) * fraction

            cam_x = boss_pos.x + radius_m * math.cos(angle_rad)
            cam_y = boss_pos.y + radius_m * math.sin(angle_rad)
            cam_z = boss_pos.z + h

            cam_pos = Vector3D(x=round(cam_x, 3), y=round(cam_y, 3), z=round(cam_z, 3))
            rot = CinematicFramingEngine.compute_look_at_rotation(cam_pos, boss_aim)

            keyframes.append(
                CameraKeyframe(
                    time_seconds=round(fraction * duration_s, 2),
                    transform=Transform3D(position=cam_pos, rotation=rot),
                    focal_length_mm=lens.focal_length_mm,
                    aperture_fstop=lens.current_aperture_fstop,
                    focus_distance_m=round(cam_pos.distance_to(boss_aim), 2),
                )
            )

        return CinematicShot(
            shot_id="shot_orbit_boss_reveal",
            shot_type=CinematicShotType.ORBIT_BOSS_REVEAL,
            framing_rule=FramingRule.LOW_ANGLE_HERO,
            duration_s=duration_s,
            primary_subject_id=boss.actor_id,
            lens=lens,
            keyframes=keyframes,
        )
