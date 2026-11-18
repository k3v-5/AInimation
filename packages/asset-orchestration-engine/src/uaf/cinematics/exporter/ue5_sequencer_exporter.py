"""
UAF-81.97: UE5 Sequencer & LevelSequence Manifest Exporter.
Serializes procedural cinematics specifications into native Unreal Engine 5 LevelSequence JSON
manifests and Python automation scripts for CineCameraActor and MovieScene tracks.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from ..core.contracts import (
    CinematicSequenceSpec,
    UE5LevelSequenceManifest,
    CameraKeyframe,
)


class UE5SequencerExporter:
    """
    Exports cinematic sequences into UE5-compatible LevelSequence asset manifests.
    """

    @staticmethod
    def build_level_sequence_manifest(
        spec: CinematicSequenceSpec,
        camera_actor_name: str = "CineCameraActor_Auto",
    ) -> UE5LevelSequenceManifest:
        """
        Converts sequence shots and keyframes into structured MovieScene track channels.
        """
        fps = spec.frame_rate
        total_frames = int(round(spec.total_duration_s * fps))

        transform_keys: List[Dict[str, Any]] = []
        focal_length_keys: List[Dict[str, Any]] = []
        aperture_keys: List[Dict[str, Any]] = []
        focus_dist_keys: List[Dict[str, Any]] = []
        camera_cuts: List[Dict[str, Any]] = []

        cumulative_time = 0.0

        for shot in spec.shots:
            shot_start_frame = int(round(cumulative_time * fps))
            shot_end_frame = int(round((cumulative_time + shot.duration_s) * fps))

            camera_cuts.append(
                {
                    "shot_id": shot.shot_id,
                    "shot_type": shot.shot_type.value,
                    "start_frame": shot_start_frame,
                    "end_frame": shot_end_frame,
                    "primary_target": shot.primary_subject_id,
                }
            )

            # Process keyframes
            for kf in shot.keyframes:
                frame_idx = int(round((cumulative_time + kf.time_seconds) * fps))
                ue5_pos = kf.transform.position.to_ue5_cm()

                transform_keys.append(
                    {
                        "frame": frame_idx,
                        "time_seconds": round(cumulative_time + kf.time_seconds, 3),
                        "position": {"x": round(ue5_pos.x, 2), "y": round(ue5_pos.y, 2), "z": round(ue5_pos.z, 2)},
                        "rotation": {
                            "pitch": kf.transform.rotation.pitch,
                            "yaw": kf.transform.rotation.yaw,
                            "roll": kf.transform.rotation.roll,
                        },
                    }
                )

                focal_length_keys.append({"frame": frame_idx, "value": kf.focal_length_mm})
                aperture_keys.append({"frame": frame_idx, "value": kf.aperture_fstop})
                # Focus distance in centimeters for UE5
                focus_dist_keys.append({"frame": frame_idx, "value": round(kf.focus_distance_m * 100.0, 2)})

            cumulative_time += shot.duration_s

        tracks = [
            {
                "track_type": "MovieScene3DTransformTrack",
                "binding": camera_actor_name,
                "keyframes": transform_keys,
            },
            {
                "track_type": "MovieSceneFloatTrack",
                "property_name": "CurrentFocalLength",
                "keyframes": focal_length_keys,
            },
            {
                "track_type": "MovieSceneFloatTrack",
                "property_name": "CurrentAperture",
                "keyframes": aperture_keys,
            },
            {
                "track_type": "MovieSceneFloatTrack",
                "property_name": "ManualFocusDistance",
                "keyframes": focus_dist_keys,
            },
            {
                "track_type": "MovieSceneCameraCutTrack",
                "cuts": camera_cuts,
            },
        ]

        if spec.audio_cue_track:
            tracks.append(
                {
                    "track_type": "MovieSceneAudioTrack",
                    "sound_cue_path": spec.audio_cue_track,
                    "start_frame": 0,
                    "end_frame": total_frames,
                }
            )

        asset_name = f"LS_{spec.sequence_id}" if not spec.sequence_id.startswith("LS_") else spec.sequence_id
        python_helper = UE5SequencerExporter._generate_python_import_script(asset_name, tracks, fps)

        return UE5LevelSequenceManifest(
            asset_name=asset_name,
            total_frames=total_frames,
            frame_rate=fps,
            camera_actor_name=camera_actor_name,
            tracks=tracks,
            python_script_helper=python_helper,
        )

    @staticmethod
    def _generate_python_import_script(asset_name: str, tracks: List[Dict[str, Any]], fps: float) -> str:
        return f'''# Auto-generated Unreal Engine 5 Python LevelSequence Importer for {asset_name}
import unreal

def import_level_sequence():
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.LevelSequenceFactoryNew()
    package_path = "/Game/Cinematics"
    
    sequence = asset_tools.create_asset("{asset_name}", package_path, unreal.LevelSequence, factory)
    sequence.set_display_rate(unreal.FrameRate(numerator=int({fps}), denominator=1))
    
    print(f"Successfully generated LevelSequence: {{sequence.get_path_name()}}")
    return sequence

if __name__ == "__main__":
    import_level_sequence()
'''

    @staticmethod
    def export_to_json(
        spec: CinematicSequenceSpec,
        target_path: Optional[Path] = None,
    ) -> str:
        """
        Serializes the sequence manifest into structured JSON.
        """
        manifest = UE5SequencerExporter.build_level_sequence_manifest(spec)
        json_str = json.dumps(manifest.model_dump(), indent=2)

        if target_path:
            target_path = Path(target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(json_str, encoding="utf-8")

        return json_str
