"""
Blender Skeletal Rigging and Procedural Articulation Engine for IANIMATION.

Provides automated armature creation, anatomical bone mapping (avian, bipedal, canine),
smooth vertex group skinning (ARMATURE_AUTO with continuous distance fallback),
procedural animation keyframe generation, and high-fidelity rendering via headless Blender 4.3+.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from backend.core.models import AutoRigResult


class BoneDefinition(BaseModel):
    """Specification of an anatomical bone in 3D coordinate space."""

    name: str
    head: Tuple[float, float, float]
    tail: Tuple[float, float, float]
    parent: Optional[str] = None
    roll: float = 0.0


class KeyframePoint(BaseModel):
    """Rotational or positional keyframe for a single bone."""

    frame: int
    rotation_euler_deg: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    location: Optional[Tuple[float, float, float]] = None


class BoneTrack(BaseModel):
    """Animation track containing keyframe curves for a specific bone."""

    bone_name: str
    keyframes: List[KeyframePoint] = Field(default_factory=list)


class AnimationSequenceConfig(BaseModel):
    """Configuration for a procedural animation cycle."""

    name: str = "cycle"
    fps: int = 24
    frame_start: int = 1
    frame_end: int = 48
    tracks: List[BoneTrack] = Field(default_factory=list)


class RiggingConfig(BaseModel):
    """Configuration for rigging a 3D mesh in Blender."""

    mesh_path: str
    skeleton_type: str = "avian"
    animation_action: Optional[str] = "flap_cycle"
    output_blend: Optional[str] = None
    output_glb: Optional[str] = None
    output_video: Optional[str] = None
    fps: int = 24
    total_frames: int = 48
    render_engine: str = "BLENDER_EEVEE_NEXT"
    anti_aliasing_samples: int = 16


class RiggingResult(BaseModel):
    """Result of skeletal rigging and animation in Blender."""

    success: bool
    skeleton_type: str
    bone_count: int
    hierarchy: List[str] = Field(default_factory=list)
    blend_path: Optional[str] = None
    glb_path: Optional[str] = None
    rendered_video_path: Optional[str] = None
    duration_seconds: float = 0.0
    message: str = ""


# Standard Presets for Anatomical Skeletons
AVIAN_BONES: List[BoneDefinition] = [
    BoneDefinition(name="Root", head=(0.0, -0.10, 0.20), tail=(0.0, 0.10, 0.25), parent=None),
    BoneDefinition(name="Spine", head=(0.0, 0.10, 0.25), tail=(-0.10, 0.25, 0.35), parent="Root"),
    BoneDefinition(name="Neck", head=(-0.10, 0.25, 0.35), tail=(-0.20, 0.42, 0.35), parent="Spine"),
    BoneDefinition(name="Head", head=(-0.20, 0.42, 0.35), tail=(-0.35, 0.55, 0.35), parent="Neck"),
    # Left Wing (Ventral / Front)
    BoneDefinition(name="Wing_Shoulder_L", head=(-0.05, 0.22, 0.35), tail=(-0.25, 0.15, 0.30), parent="Spine"),
    BoneDefinition(name="Wing_Mid_L", head=(-0.25, 0.15, 0.30), tail=(-0.55, -0.05, 0.22), parent="Wing_Shoulder_L"),
    BoneDefinition(name="Wing_Tip_L", head=(-0.55, -0.05, 0.22), tail=(-0.85, -0.35, 0.12), parent="Wing_Mid_L"),
    # Right Wing (Dorsal / Back)
    BoneDefinition(name="Wing_Shoulder_R", head=(0.02, 0.22, 0.28), tail=(0.22, 0.30, 0.22), parent="Spine"),
    BoneDefinition(name="Wing_Mid_R", head=(0.22, 0.30, 0.22), tail=(0.48, 0.45, 0.16), parent="Wing_Shoulder_R"),
    BoneDefinition(name="Wing_Tip_R", head=(0.48, 0.45, 0.16), tail=(0.75, 0.60, 0.10), parent="Wing_Mid_R"),
    # Tail & Lower Body
    BoneDefinition(name="Tail", head=(0.0, -0.10, 0.20), tail=(0.12, -0.55, 0.10), parent="Root"),
    BoneDefinition(name="Leg_L", head=(-0.08, -0.15, 0.20), tail=(-0.12, -0.50, 0.15), parent="Root"),
    BoneDefinition(name="Leg_R", head=(0.04, -0.15, 0.18), tail=(0.02, -0.48, 0.15), parent="Root"),
]

CANINE_BONES: List[BoneDefinition] = [
    BoneDefinition(name="Root", head=(0.0, -0.10, 0.0), tail=(0.0, 0.15, 0.0), parent=None),
    BoneDefinition(name="Spine", head=(0.0, 0.15, 0.0), tail=(0.0, 0.40, 0.10), parent="Root"),
    BoneDefinition(name="Neck", head=(0.0, 0.40, 0.10), tail=(-0.15, 0.55, 0.15), parent="Spine"),
    BoneDefinition(name="Head", head=(-0.15, 0.55, 0.15), tail=(-0.35, 0.65, 0.15), parent="Neck"),
    BoneDefinition(name="Jaw", head=(-0.25, 0.55, 0.05), tail=(-0.45, 0.55, -0.05), parent="Head"),
    BoneDefinition(name="Leg_Front_L", head=(-0.20, 0.35, -0.05), tail=(-0.20, -0.30, -0.05), parent="Spine"),
    BoneDefinition(name="Leg_Front_R", head=(0.20, 0.35, -0.05), tail=(0.20, -0.30, -0.05), parent="Spine"),
    BoneDefinition(name="Leg_Hind_L", head=(-0.20, -0.15, -0.05), tail=(-0.20, -0.65, -0.05), parent="Root"),
    BoneDefinition(name="Leg_Hind_R", head=(0.20, -0.15, -0.05), tail=(0.20, -0.65, -0.05), parent="Root"),
    BoneDefinition(name="Tail_Root", head=(0.0, -0.15, 0.05), tail=(0.10, -0.45, 0.10), parent="Root"),
    BoneDefinition(name="Tail_Tip", head=(0.10, -0.45, 0.10), tail=(0.25, -0.70, 0.15), parent="Tail_Root"),
]

BIPEDAL_BONES: List[BoneDefinition] = [
    BoneDefinition(name="Root", head=(0.0, 0.0, -0.05), tail=(0.0, 0.0, 0.15), parent=None),
    BoneDefinition(name="Spine", head=(0.0, 0.0, 0.15), tail=(0.0, 0.0, 0.48), parent="Root"),
    BoneDefinition(name="Neck", head=(0.0, 0.0, 0.48), tail=(0.0, 0.0, 0.62), parent="Spine"),
    BoneDefinition(name="Head", head=(0.0, 0.0, 0.62), tail=(0.0, 0.0, 0.92), parent="Neck"),
    # Right Arm (screen left, X < 0)
    BoneDefinition(name="Clavicle_R", head=(-0.04, 0.0, 0.48), tail=(-0.16, 0.0, 0.45), parent="Spine"),
    BoneDefinition(name="Arm_R", head=(-0.16, 0.0, 0.45), tail=(-0.25, 0.0, 0.20), parent="Clavicle_R"),
    BoneDefinition(name="Forearm_R", head=(-0.25, 0.0, 0.20), tail=(-0.24, 0.0, -0.10), parent="Arm_R"),
    # Left Arm (screen right, X > 0)
    BoneDefinition(name="Clavicle_L", head=(0.04, 0.0, 0.48), tail=(0.16, 0.0, 0.45), parent="Spine"),
    BoneDefinition(name="Arm_L", head=(0.16, 0.0, 0.45), tail=(0.25, 0.0, 0.20), parent="Clavicle_L"),
    BoneDefinition(name="Forearm_L", head=(0.25, 0.0, 0.20), tail=(0.24, 0.0, -0.10), parent="Arm_L"),
    # Right Leg (screen left, X ~ -0.12)
    BoneDefinition(name="Thigh_R", head=(-0.10, 0.0, -0.05), tail=(-0.12, 0.0, -0.32), parent="Root"),
    BoneDefinition(name="Shin_R", head=(-0.12, 0.0, -0.32), tail=(-0.14, 0.0, -0.75), parent="Thigh_R"),
    BoneDefinition(name="Foot_R", head=(-0.14, 0.0, -0.75), tail=(-0.18, -0.10, -0.96), parent="Shin_R"),
    # Left Leg (screen right, X ~ 0.12)
    BoneDefinition(name="Thigh_L", head=(0.10, 0.0, -0.05), tail=(0.12, 0.0, -0.32), parent="Root"),
    BoneDefinition(name="Shin_L", head=(0.12, 0.0, -0.32), tail=(0.12, 0.0, -0.75), parent="Thigh_L"),
    BoneDefinition(name="Foot_L", head=(0.12, 0.0, -0.75), tail=(0.14, -0.10, -0.96), parent="Shin_L"),
]


def generate_avian_flap_animation(total_frames: int = 48, fps: int = 24) -> AnimationSequenceConfig:
    """
    Generate harmonic flapping curves with aerodynamic phase propagation.
    Follows continuous sinusoidal modulation without discontinuous jumps.
    """
    tracks: List[BoneTrack] = []
    frames = list(range(1, total_frames + 1))

    # Left Wing (Main flapping cycle with aerodynamic wave propagation)
    shoulder_l_keys: List[KeyframePoint] = []
    mid_l_keys: List[KeyframePoint] = []
    tip_l_keys: List[KeyframePoint] = []

    # Right Wing (Coordinated bilateral flapping)
    shoulder_r_keys: List[KeyframePoint] = []
    mid_r_keys: List[KeyframePoint] = []
    tip_r_keys: List[KeyframePoint] = []

    # Head and Spine (Subtle organic movement)
    head_keys: List[KeyframePoint] = []
    spine_keys: List[KeyframePoint] = []

    for f in frames:
        phase = (f / total_frames) * 2.0 * math.pi * 2.0  # 2 full flaps per sequence

        # Shoulder: dominant pitch & roll flap
        flap_deg = math.sin(phase) * 26.0
        roll_deg = math.cos(phase) * 14.0
        shoulder_l_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(roll_deg, 0.0, flap_deg))
        )
        shoulder_r_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(-roll_deg, 0.0, -flap_deg * 0.85))
        )

        # Mid-wing: trailing phase delay of 35 degrees (0.61 rad)
        phase_mid = phase - 0.61
        flap_mid = math.sin(phase_mid) * 20.0
        twist_mid = math.cos(phase_mid) * 8.0
        mid_l_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(twist_mid, 0.0, flap_mid))
        )
        mid_r_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(-twist_mid, 0.0, -flap_mid * 0.85))
        )

        # Wing tip: trailing phase delay of 70 degrees (1.22 rad) for feather whip
        phase_tip = phase - 1.22
        flap_tip = math.sin(phase_tip) * 16.0
        twist_tip = math.cos(phase_tip) * 10.0
        tip_l_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(twist_tip, 0.0, flap_tip))
        )
        tip_r_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(-twist_tip, 0.0, -flap_tip * 0.85))
        )

        # Head glances subtly with pitch and yaw
        head_pitch = math.sin(phase * 0.5) * 4.0
        head_yaw = math.cos(phase * 0.5) * 7.0
        head_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(head_pitch, 0.0, head_yaw))
        )

        # Spine bobs vertically with lift oscillation (double frequency of flap)
        spine_bob = math.cos(phase) * 3.5
        spine_keys.append(
            KeyframePoint(frame=f, rotation_euler_deg=(spine_bob, 0.0, 0.0))
        )

    tracks.extend([
        BoneTrack(bone_name="Wing_Shoulder_L", keyframes=shoulder_l_keys),
        BoneTrack(bone_name="Wing_Mid_L", keyframes=mid_l_keys),
        BoneTrack(bone_name="Wing_Tip_L", keyframes=tip_l_keys),
        BoneTrack(bone_name="Wing_Shoulder_R", keyframes=shoulder_r_keys),
        BoneTrack(bone_name="Wing_Mid_R", keyframes=mid_r_keys),
        BoneTrack(bone_name="Wing_Tip_R", keyframes=tip_r_keys),
        BoneTrack(bone_name="Head", keyframes=head_keys),
        BoneTrack(bone_name="Spine", keyframes=spine_keys),
    ])

    return AnimationSequenceConfig(
        name="avian_flap_cycle",
        fps=fps,
        frame_start=1,
        frame_end=total_frames,
        tracks=tracks,
    )


def generate_bipedal_idle_animation(total_frames: int = 48, fps: int = 24) -> AnimationSequenceConfig:
    """
    Generate subtle, fluid tactical breathing and scanning idle animation for bipedal character.
    Guarantees seamless C^inf looping with natural phase propagation.
    """
    tracks: List[BoneTrack] = []
    frames = list(range(1, total_frames + 1))

    root_keys: List[KeyframePoint] = []
    spine_keys: List[KeyframePoint] = []
    neck_keys: List[KeyframePoint] = []
    head_keys: List[KeyframePoint] = []
    arm_l_keys: List[KeyframePoint] = []
    arm_r_keys: List[KeyframePoint] = []
    forearm_l_keys: List[KeyframePoint] = []
    forearm_r_keys: List[KeyframePoint] = []

    for f in frames:
        # Breathing cycle (1 full breath cycle across total_frames)
        phase = (f / total_frames) * 2.0 * math.pi

        # Root: microscopic vertical pelvic shift (0.004 m)
        pelvis_dz = math.sin(phase) * 0.004
        root_keys.append(KeyframePoint(frame=f, location=(0.0, 0.0, pelvis_dz)))

        # Spine: chest expansion/lift (pitch 1.2 deg, roll 0.4 deg)
        spine_pitch = math.sin(phase) * 1.2
        spine_roll = math.cos(phase) * 0.4
        spine_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(spine_pitch, spine_roll, 0.0)))

        # Neck: counter-tilt to stabilize head
        neck_pitch = -math.sin(phase) * 0.5
        neck_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(neck_pitch, 0.0, 0.0)))

        # Head: subtle tactical scanning glance (yaw 2.8 deg, subtle pitch)
        head_yaw = math.sin(phase) * 2.8
        head_pitch = math.cos(phase) * 0.8
        head_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(head_pitch, 0.0, head_yaw)))

        # Arms: gentle synchronous breathing excursion with phase delay
        arm_phase = phase - 0.35
        arm_l_roll = math.sin(arm_phase) * 1.4
        arm_l_pitch = math.cos(arm_phase) * 1.0
        arm_l_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(arm_l_pitch, arm_l_roll, 0.0)))

        arm_r_roll = -math.sin(arm_phase) * 1.4
        arm_r_pitch = math.cos(arm_phase) * 1.0
        arm_r_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(arm_r_pitch, arm_r_roll, 0.0)))

        # Forearms: micro-relaxation
        forearm_l_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(0.0, math.sin(arm_phase) * 0.6, 0.0)))
        forearm_r_keys.append(KeyframePoint(frame=f, rotation_euler_deg=(0.0, -math.sin(arm_phase) * 0.6, 0.0)))

    tracks.extend([
        BoneTrack(bone_name="Root", keyframes=root_keys),
        BoneTrack(bone_name="Spine", keyframes=spine_keys),
        BoneTrack(bone_name="Neck", keyframes=neck_keys),
        BoneTrack(bone_name="Head", keyframes=head_keys),
        BoneTrack(bone_name="Arm_L", keyframes=arm_l_keys),
        BoneTrack(bone_name="Arm_R", keyframes=arm_r_keys),
        BoneTrack(bone_name="Forearm_L", keyframes=forearm_l_keys),
        BoneTrack(bone_name="Forearm_R", keyframes=forearm_r_keys),
    ])

    return AnimationSequenceConfig(
        name="bipedal_tactical_idle",
        fps=fps,
        frame_start=1,
        frame_end=total_frames,
        tracks=tracks,
    )


class BlenderRigger:
    """
    Orchestrates Blender 4.3+ headless armature generation, automatic skinning,
    animation keyframing, and rendering.
    """

    def __init__(self, blender_bin: Optional[str] = None) -> None:
        self.blender_bin: str = self._resolve_blender_binary(blender_bin)
        self.script_path: Path = Path(__file__).resolve().parent / "scripts" / "rig_and_animate.py"

    def _resolve_blender_binary(self, candidate: Optional[str] = None) -> str:
        """Resolve path to executable blender binary."""
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return str(Path(candidate).resolve())

        # Check local project symlink
        project_link = Path(__file__).resolve().parent.parent.parent / "blender"
        if project_link.is_file() and os.access(project_link, os.X_OK):
            return str(project_link.resolve())

        # Check system PATH
        which_blender = shutil.which("blender")
        if which_blender:
            return which_blender

        # Check common local install locations
        user_app = Path.home() / "Aplicaciones" / "blender" / "blender"
        if user_app.is_file() and os.access(user_app, os.X_OK):
            return str(user_app.resolve())

        # Check Windows common install locations
        win_candidates = [
            Path("C:/Program Files/Blender Foundation/Blender 4.4/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
            Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
        ]
        for wc in win_candidates:
            if wc.is_file() and os.access(wc, os.X_OK):
                return str(wc.resolve())

        return "blender"

    def health_check(self) -> bool:
        """Verify Blender binary execution and version."""
        try:
            res = subprocess.run(
                [self.blender_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            return res.returncode == 0 and "Blender" in res.stdout
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            return False

    def get_bones_for_type(self, skeleton_type: str) -> List[BoneDefinition]:
        """Retrieve standard bone definition list for given skeleton type."""
        norm_type = skeleton_type.lower().strip()
        if "avian" in norm_type or "bird" in norm_type or "raven" in norm_type:
            return AVIAN_BONES
        elif "canine" in norm_type or "wolf" in norm_type or "quadruped" in norm_type:
            return CANINE_BONES
        return BIPEDAL_BONES

    def rig_and_animate(self, config: RiggingConfig) -> RiggingResult:
        """
        Execute headless Blender pipeline to rig mesh, apply animation action,
        export .glb and .blend, and optionally render animation video.
        """
        start_time = time.time()
        mesh_file = Path(config.mesh_path).resolve()
        if not mesh_file.is_file():
            return RiggingResult(
                success=False,
                skeleton_type=config.skeleton_type,
                bone_count=0,
                message=f"Mesh file not found: {config.mesh_path}",
            )

        bones = self.get_bones_for_type(config.skeleton_type)
        hierarchy = [b.name for b in bones]

        # Generate animation sequence if requested
        anim_config: Optional[AnimationSequenceConfig] = None
        if config.animation_action:
            if "avian" in config.skeleton_type.lower():
                anim_config = generate_avian_flap_animation(
                    total_frames=config.total_frames, fps=config.fps
                )
            elif any(k in config.skeleton_type.lower() for k in ["biped", "human", "character", "anime"]):
                anim_config = generate_bipedal_idle_animation(
                    total_frames=config.total_frames, fps=config.fps
                )

        # Output targets
        out_blend = config.output_blend or str(mesh_file.parent / f"{mesh_file.stem}_rigged.blend")
        out_glb = config.output_glb or str(mesh_file.parent / f"{mesh_file.stem}_rigged.glb")
        out_video = config.output_video

        # Prepare payload for Blender headless script
        payload = {
            "mesh_path": str(mesh_file),
            "skeleton_type": config.skeleton_type,
            "bones": [b.model_dump() for b in bones],
            "animation": anim_config.model_dump() if anim_config else None,
            "output_blend": str(Path(out_blend).resolve()),
            "output_glb": str(Path(out_glb).resolve()),
            "output_video": str(Path(out_video).resolve()) if out_video else None,
            "render_engine": config.render_engine,
            "samples": config.anti_aliasing_samples,
            "fps": config.fps,
            "total_frames": config.total_frames,
        }

        # Save temporary payload JSON
        payload_file = mesh_file.parent / f"_rig_payload_{mesh_file.stem}.json"
        payload_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        cmd = [
            self.blender_bin,
            "-b",
            "-P",
            str(self.script_path),
            "--",
            "--config",
            str(payload_file.resolve()),
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=240, check=False)
            elapsed = round(time.time() - start_time, 2)
            blend_exists = Path(out_blend).is_file()
            glb_exists = Path(out_glb).is_file()
            video_exists = Path(out_video).is_file() if out_video else True

            success = res.returncode == 0 and blend_exists and glb_exists and video_exists
            msg = "Rigging and animation completed successfully" if success else f"Blender error: {res.stderr or res.stdout}"

            return RiggingResult(
                success=success,
                skeleton_type=config.skeleton_type,
                bone_count=len(bones),
                hierarchy=hierarchy,
                blend_path=str(Path(out_blend).resolve()) if blend_exists else None,
                glb_path=str(Path(out_glb).resolve()) if glb_exists else None,
                rendered_video_path=str(Path(out_video).resolve()) if (out_video and Path(out_video).is_file()) else None,
                duration_seconds=elapsed,
                message=msg,
            )
        except Exception as exc:
            return RiggingResult(
                success=False,
                skeleton_type=config.skeleton_type,
                bone_count=len(bones),
                hierarchy=hierarchy,
                duration_seconds=round(time.time() - start_time, 2),
                message=f"Execution exception: {str(exc)}",
            )
        finally:
            if payload_file.exists():
                try:
                    payload_file.unlink()
                except OSError:
                    pass

    def rig_multi_component_scene(
        self,
        components: List[Dict[str, Any]],
        output_blend: str,
        output_glb: Optional[str] = None,
        output_video: Optional[str] = None,
        fps: int = 24,
        total_frames: int = 36,
        samples: int = 16,
        render_engine: str = "BLENDER_EEVEE_NEXT",
    ) -> RiggingResult:
        """
        Assemble and rig a multi-component scene in Blender 4.3+.
        Decouples environmental props and articulates character limbs with zero weight bleed.
        """
        start_time = time.time()
        multi_script = Path(__file__).resolve().parent / "scripts" / "multi_component_rig.py"

        out_blend_p = Path(output_blend).resolve()
        out_blend_p.parent.mkdir(parents=True, exist_ok=True)
        payload_file = out_blend_p.parent / f"_multi_rig_payload_{out_blend_p.stem}.json"

        payload = {
            "components": components,
            "output_blend": str(out_blend_p),
            "output_glb": str(Path(output_glb).resolve()) if output_glb else None,
            "output_video": str(Path(output_video).resolve()) if output_video else None,
            "fps": fps,
            "total_frames": total_frames,
            "samples": samples,
            "render_engine": render_engine,
        }
        payload_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        cmd = [
            self.blender_bin,
            "-b",
            "-P",
            str(multi_script),
            "--",
            "--config",
            str(payload_file.resolve()),
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=240, check=False)
            elapsed = round(time.time() - start_time, 2)
            blend_exists = out_blend_p.is_file()
            glb_exists = Path(output_glb).is_file() if output_glb else True
            video_exists = Path(output_video).is_file() if output_video else True

            success = res.returncode == 0 and blend_exists and glb_exists and video_exists
            msg = "Multi-component scene assembled and rendered successfully" if success else f"Blender error: {res.stderr or res.stdout}"

            return RiggingResult(
                success=success,
                skeleton_type="multi_component_avian",
                bone_count=5,
                hierarchy=["Root", "Spine", "Head", "Wing_Shoulder_L", "Wing_Shoulder_R"],
                blend_path=str(out_blend_p) if blend_exists else None,
                glb_path=str(Path(output_glb).resolve()) if (output_glb and Path(output_glb).is_file()) else None,
                rendered_video_path=str(Path(output_video).resolve()) if (output_video and Path(output_video).is_file()) else None,
                duration_seconds=elapsed,
                message=msg,
            )
        except Exception as exc:
            return RiggingResult(
                success=False,
                skeleton_type="multi_component",
                bone_count=0,
                duration_seconds=round(time.time() - start_time, 2),
                message=f"Multi-component execution exception: {str(exc)}",
            )
        finally:
            if payload_file.exists():
                try:
                    payload_file.unlink()
                except OSError:
                    pass

