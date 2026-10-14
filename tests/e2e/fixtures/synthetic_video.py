"""
Synthetic video and mocap fixture generators for IANIMATION E2E tests.
Provides synthetic MP4 video files, synthetic 3D pose sequences, and corrupt media.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List
import struct


def _create_minimal_mp4_box(box_type: bytes, payload: bytes) -> bytes:
    """Pack an ISO Base Media File Format (ISOBMFF / MP4) box."""
    box_len = len(payload) + 8
    return struct.pack(">I", box_len) + box_type + payload


def create_dummy_video(
    file_path: Path,
    duration_seconds: float = 1.0,
    fps: int = 30,
) -> Path:
    """
    Generate a lightweight synthetic MP4 video file.
    Attempts encoding via imageio-ffmpeg if available, with a robust pure-binary fallback.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import imageio
        import numpy as np
        
        num_frames = int(duration_seconds * fps)
        writer = imageio.get_writer(str(file_path), fps=fps, codec="libx264")
        for i in range(max(1, num_frames)):
            # Generate animated gradient frame 128x128
            frame = np.zeros((128, 128, 3), dtype=np.uint8)
            intensity = int(127 * (1.0 + math.sin(2.0 * math.pi * i / max(1, num_frames))))
            frame[:, :, 0] = intensity
            frame[:, :, 1] = (i * 8) % 255
            frame[:, :, 2] = 200
            writer.append_data(frame)
        writer.close()
        return file_path
    except Exception:
        # Pure-binary ISO BMFF MP4 fallback container
        # ftyp box: major brand isom, minor 512, compatible isom/iso2/mp41
        ftyp_data = b"isom" + struct.pack(">I", 512) + b"isomiso2mp41"
        ftyp_box = _create_minimal_mp4_box(b"ftyp", ftyp_data)
        
        # mdat box: dummy payload
        mdat_box = _create_minimal_mp4_box(b"mdat", b"\x00" * 256)
        
        file_path.write_bytes(ftyp_box + mdat_box)
        return file_path


def create_synthetic_pose_sequence(
    num_frames: int = 30,
    fps: int = 30,
    bpm: float = 120.0,
) -> List[Dict[str, float]]:
    """
    Generate synthetic 3D kinematic pose frames with periodic oscillatory motion.
    Conforms to standard biped landmark keys for mocap validation.
    """
    poses: List[Dict[str, float]] = []
    beat_period = 60.0 / bpm
    
    for frame_idx in range(num_frames):
        time_sec = float(frame_idx) / float(fps)
        phase = 2.0 * math.pi * (time_sec % beat_period) / beat_period
        
        pose_frame: Dict[str, float] = {
            "timestamp": time_sec,
            "root_x": 0.0,
            "root_y": 0.0,
            "root_z": 90.0 + 5.0 * math.sin(phase),  # Rhythmic vertical bounce
            "spine_pitch": 2.0 * math.sin(phase),
            "left_arm_pitch": 30.0 * math.sin(phase),
            "right_arm_pitch": -30.0 * math.sin(phase),
            "left_leg_pitch": -20.0 * math.cos(phase),
            "right_leg_pitch": 20.0 * math.cos(phase),
            "confidence": 0.98,
        }
        poses.append(pose_frame)
        
    return poses


def create_corrupt_video(file_path: Path) -> Path:
    """Generate a corrupt video file with an invalid header."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(b"\x00\x00\x00\x18ftypCORRUPT_INVALID_BOX_DATA_TRUNCATED")
    return file_path
