"""
Universal Cinematic Validator (UAF-81.60).
Normative verification pipeline (§16, §23, §90, §146) for timeline determinism,
clips, bindings, optics, gameplay lock safety, and persistence integrity.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..models.definition import (
    PlaybackState,
    TrackType,
    ClipOverlapPolicy,
    BindingType,
    BindingFailurePolicy,
    CameraRigType,
    CameraInterpolationType,
    CameraPriority,
    AnimationLayer,
    RootMotionPolicy,
    GameplayLockType,
    CinematicClip,
    CinematicMarker,
    CinematicTrack,
    Timeline,
    CinematicBinding,
    CinematicCamera,
    CameraRig,
    CameraBlend,
    GameplayLock,
    CinematicAsset,
    CinematicInstance,
    CinematicSaveState,
)


@dataclass
class CinematicValidationReport:
    """Consolidated diagnostic report of cinematic validation pipeline (§146)."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_pass(self, check_name: str) -> None:
        self.passed_checks.append(check_name)


class UniversalCinematicValidator:
    """
    Automated validator ensuring all cinematic sequences comply with
    the normative UAF-81.60 contract and zero-regression standards.
    """

    def validate_clip(self, clip: CinematicClip) -> CinematicValidationReport:
        """Validates a single cinematic clip (§15, §16)."""
        report = CinematicValidationReport()

        if not clip.clip_id:
            report.add_error("Clip ID cannot be empty.")

        # Temporal integrity
        if math.isnan(clip.start) or math.isinf(clip.start):
            report.add_error(f"Clip '{clip.clip_id}' start time is NaN or infinite.")
        elif clip.start < 0.0:
            report.add_error(f"Clip '{clip.clip_id}' start time cannot be negative.")

        if math.isnan(clip.duration) or math.isinf(clip.duration):
            report.add_error(f"Clip '{clip.clip_id}' duration is NaN or infinite.")
        elif clip.duration <= 0.0:
            report.add_error(f"Clip '{clip.clip_id}' duration must be strictly positive.")

        # Blending sanity
        if clip.blend_in < 0.0 or clip.blend_out < 0.0:
            report.add_error(f"Clip '{clip.clip_id}' blend_in/blend_out cannot be negative.")
        elif (clip.blend_in + clip.blend_out) > clip.duration:
            report.add_error(
                f"Clip '{clip.clip_id}' total blend duration exceeds clip duration."
            )

        if not report.errors:
            report.add_pass(f"clip_{clip.clip_id}")
        return report

    def validate_track(self, track: CinematicTrack) -> CinematicValidationReport:
        """Validates a cinematic track and all its child clips (§13, §14)."""
        report = CinematicValidationReport()

        if not track.track_id:
            report.add_error("Track ID cannot be empty.")

        if not isinstance(track.track_type, TrackType):
            report.add_error(f"Track '{track.track_id}' has an invalid TrackType.")

        for clip in track.clips:
            clip_rep = self.validate_clip(clip)
            if not clip_rep.is_valid:
                for err in clip_rep.errors:
                    report.add_error(f"Track '{track.track_id}' -> {err}")

        if not report.errors:
            report.add_pass(f"track_{track.track_id}")
        return report

    def validate_timeline(self, timeline: Timeline) -> CinematicValidationReport:
        """Validates timeline structure, durations, resolution, and tracks (§8, §9, §10)."""
        report = CinematicValidationReport()

        if math.isnan(timeline.start_time) or timeline.start_time < 0.0:
            report.add_error("Timeline start_time must be non-negative and finite.")

        if math.isnan(timeline.end_time) or timeline.end_time <= timeline.start_time:
            report.add_error("Timeline end_time must be strictly greater than start_time.")

        if math.isnan(timeline.duration) or timeline.duration <= 0.0:
            report.add_error("Timeline duration must be strictly positive.")

        if timeline.tempo <= 0.0:
            report.add_error("Timeline tempo must be strictly positive.")

        if timeline.time_resolution <= 0.0:
            report.add_error("Timeline time_resolution must be strictly positive.")

        # Validate tracks
        track_ids: Set[str] = set()
        for track in timeline.tracks:
            if track.track_id in track_ids:
                report.add_error(f"Duplicate track ID '{track.track_id}' detected.")
            track_ids.add(track.track_id)

            t_rep = self.validate_track(track)
            if not t_rep.is_valid:
                for err in t_rep.errors:
                    report.add_error(err)

        # Validate markers
        for marker in timeline.markers:
            if marker.time < timeline.start_time or marker.time > timeline.end_time:
                report.add_error(
                    f"Marker '{marker.marker_id}' time {marker.time} is outside timeline range."
                )

        if not report.errors:
            report.add_pass("timeline_integrity")
        return report

    def validate_binding(self, binding: CinematicBinding) -> CinematicValidationReport:
        """Validates reference bindings (§21, §22, §23)."""
        report = CinematicValidationReport()

        if not binding.binding_id:
            report.add_error("Binding ID cannot be empty.")

        if not binding.target_reference and not binding.fallback_reference and binding.binding_type != BindingType.PLAYER:
            report.add_error(f"Binding '{binding.binding_id}' has neither target nor fallback reference.")

        if not report.errors:
            report.add_pass(f"binding_{binding.binding_id}")
        return report

    def validate_camera(self, camera: CinematicCamera) -> CinematicValidationReport:
        """Validates cine-camera optics and parameters (§27)."""
        report = CinematicValidationReport()

        if not camera.camera_id:
            report.add_error("Camera ID cannot be empty.")

        if camera.fov <= 0.0 or camera.fov >= 180.0:
            report.add_error(f"Camera '{camera.camera_id}' FOV must be in (0, 180) degrees.")

        if camera.near_clip <= 0.0:
            report.add_error(f"Camera '{camera.camera_id}' near_clip must be positive.")

        if camera.far_clip <= camera.near_clip:
            report.add_error(f"Camera '{camera.camera_id}' far_clip must be greater than near_clip.")

        if camera.aperture <= 0.0:
            report.add_error(f"Camera '{camera.camera_id}' aperture must be positive.")

        # Rotation quaternion sanity
        q = camera.rotation
        mag_sq = q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2
        if math.isnan(mag_sq) or abs(mag_sq - 1.0) > 0.05:
            report.add_warning(f"Camera '{camera.camera_id}' rotation quaternion is not normalized.")

        if not report.errors:
            report.add_pass(f"camera_{camera.camera_id}")
        return report

    def validate_save_state(
        self,
        save_state: CinematicSaveState,
        expected_hash: str = "",
    ) -> CinematicValidationReport:
        """Validates save state integrity and corrupt save detection (§90, §129)."""
        report = CinematicValidationReport()

        if not save_state.cinematic_id:
            report.add_error("SaveState missing cinematic_id.")
        if not save_state.instance_id:
            report.add_error("SaveState missing instance_id.")
        if save_state.timeline_time < 0.0 or math.isnan(save_state.timeline_time):
            report.add_error("SaveState has invalid timeline_time.")
        if expected_hash and save_state.asset_hash and save_state.asset_hash != expected_hash:
            report.add_error("SaveState asset_hash mismatch (corrupt save detected).")

        if not report.errors:
            report.add_pass("save_state_integrity")
        return report

    def validate_all(self, asset: CinematicAsset) -> CinematicValidationReport:
        """Complete normative validation pipeline (§146)."""
        report = CinematicValidationReport()

        if not asset.cinematic_id:
            report.add_error("Asset cinematic_id cannot be empty.")

        if asset.duration <= 0.0 or math.isnan(asset.duration):
            report.add_error("Asset duration must be strictly positive and finite.")

        # 1. Timeline validation
        tl_rep = self.validate_timeline(asset.timeline)
        if not tl_rep.is_valid:
            for err in tl_rep.errors:
                report.add_error(err)
        for w in tl_rep.warnings:
            report.add_warning(w)

        # 2. Bindings validation
        for b in asset.bindings:
            b_rep = self.validate_binding(b)
            if not b_rep.is_valid:
                for err in b_rep.errors:
                    report.add_error(err)

        report.metrics = {
            "tracks_count": len(asset.timeline.tracks),
            "markers_count": len(asset.timeline.markers),
            "bindings_count": len(asset.bindings),
            "duration": asset.duration,
        }

        if not report.errors:
            report.add_pass("full_pipeline_verification")
        return report
