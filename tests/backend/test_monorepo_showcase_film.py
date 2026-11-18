"""Automated verification suite for 'Cross-Dimension Rescue' 5-engine monorepo showcase film."""

from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import subprocess
from typing import Dict, List
import wave

import cv2
import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SHOWCASE_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo"
BLENDER_EXE = Path(r"E:\Blender\blender.exe")
FFMPEG_BIN = Path(
    r"C:\Users\sasuk\AppData\Roaming\Python\Python314\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
)

CH_VISEMES: tuple[str, ...] = (
    "Neutral",
    "Ah",
    "D",
    "Ee",
    "F",
    "L",
    "M",
    "Oh",
    "R",
    "S",
    "Uh",
    "W-Oo",
    "Smile",
    "Surprised",
)


def test_showcase_deliverables_exist_and_non_empty() -> None:
    """Every multi-engine showcase asset must exist on disk and be non-empty."""
    required_files: tuple[str, ...] = (
        "cross_dimension_rescue_master.mp4",
        "cross_dimension_rescue_preview.gif",
        "act1_tactical_previz.styk",
        "act1_ik_frames.json",
        "commander_comms_puppet.psd",
        "dialogue_48khz.wav",
        "master_soundtrack_120bpm.wav",
        "audio_beat_analysis.json",
        "viseme_cues.json",
        "cross_dimension_rescue.blend",
        "cross_dimension_rescue.glb",
        "cross_dimension_rescue_comp.jsx",
        "scene_manifest.json",
        "act1_previz_ik.png",
        "act2_blender_corridor_3d.png",
        "act3_adobe_comms_lipsync.png",
        "act4_motion_vfx_climax.png",
        "showcase_4acts_contact_sheet.png",
        "aoe_sector7_wfc_level.json",
        "aoe_sector7_radar.png",
        "aoe_sector7_summary.json",
        "aoe_world/Sector7_ThermalBasin_heightmap.r16",
        "textures/corridor_basecolor.png",
        "textures/corridor_normal.png",
        "textures/corridor_orm.png",
        "textures/corridor_emissive.png",
    )
    for rel in required_files:
        path = SHOWCASE_DIR / rel
        assert path.exists(), f"Missing showcase deliverable: {path}"
        assert path.stat().st_size > 0, f"Empty showcase deliverable: {path}"


def test_audio_48khz_and_master_soundtrack_duration() -> None:
    """Dialogue & soundtrack WAVs must be 48kHz 16-bit PCM with exact 12.0s soundtrack duration."""
    dlg_path = SHOWCASE_DIR / "dialogue_48khz.wav"
    with wave.open(str(dlg_path), "rb") as wf:
        assert wf.getframerate() == 48000
        assert wf.getsampwidth() == 2
        assert wf.getnchannels() == 1
        dlg_dur = wf.getnframes() / float(wf.getframerate())
        assert 2.0 < dlg_dur < 5.0
        pcm_dlg = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        assert float(np.max(np.abs(pcm_dlg))) / 32768.0 > 0.25

    snd_path = SHOWCASE_DIR / "master_soundtrack_120bpm.wav"
    with wave.open(str(snd_path), "rb") as wf:
        assert wf.getframerate() == 48000
        assert wf.getsampwidth() == 2
        assert wf.getnchannels() == 2
        snd_dur = wf.getnframes() / float(wf.getframerate())
        assert abs(snd_dur - 12.0) < 0.02
        pcm_snd = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        assert float(np.max(np.abs(pcm_snd))) / 32768.0 > 0.30

    beat_data = json.loads((SHOWCASE_DIR / "audio_beat_analysis.json").read_text(encoding="utf-8"))
    assert float(beat_data["bpm"]) >= 100.0
    assert len(beat_data["beat_timestamps"]) >= 16


def test_commander_psd_rig_and_viseme_cues() -> None:
    """Adobe Character Animator puppet PSD must be valid 8BPS with 14 CH visemes and section dividers."""
    psd_bytes = (SHOWCASE_DIR / "commander_comms_puppet.psd").read_bytes()
    sig, version, _res, channels, height, width, depth, color_mode = struct.unpack(
        ">4sH6sHIIHH", psd_bytes[:26]
    )
    assert sig == b"8BPS"
    assert version == 1
    assert channels == 4
    assert (width, height) == (256, 256)
    assert depth == 8
    assert color_mode == 3
    assert b"lsct" in psd_bytes
    for viseme in CH_VISEMES:
        assert viseme.encode("ascii") in psd_bytes, f"Missing Character Animator viseme layer: {viseme}"

    vis_data = json.loads((SHOWCASE_DIR / "viseme_cues.json").read_text(encoding="utf-8"))
    assert int(vis_data["sample_rate"]) == 48000
    assert len(vis_data["frames"]) == 288
    assert vis_data["supported_visemes"] == list(CH_VISEMES)
    assert len(vis_data["word_cues"]) >= 6


def test_stick_animator_ik_frames_and_segment_invariance() -> None:
    """Act 1 stykanimate IK frames must cover 72 frames @ 1280x720 with constant bone lengths."""
    ik_data = json.loads((SHOWCASE_DIR / "act1_ik_frames.json").read_text(encoding="utf-8"))
    assert ik_data["canvas_width"] == 1280
    assert ik_data["canvas_height"] == 720
    assert ik_data["fps"] == 24
    frames: List[List[Dict[str, object]]] = ik_data["frames"]
    assert len(frames) == 72

    tracked_lengths: Dict[str, List[float]] = {"Torso": [], "ThighL": [], "CalfL": []}
    for f_drawables in frames:
        for drw in f_drawables:
            name = str(drw.get("name", ""))
            if name in tracked_lengths:
                sx = float(drw["start"]["x"])  # type: ignore[index]
                sy = float(drw["start"]["y"])  # type: ignore[index]
                ex = float(drw["end"]["x"])    # type: ignore[index]
                ey = float(drw["end"]["y"])    # type: ignore[index]
                tracked_lengths[name].append(math.hypot(ex - sx, ey - sy))

    for bone_name, lens in tracked_lengths.items():
        assert len(lens) == 72
        assert max(lens) - min(lens) < 1.0, f"Bone {bone_name} length varied unexpectedly: {min(lens)}..{max(lens)}"


def test_after_effects_jsx_enforces_user_design_preferences() -> None:
    """Generated ExtendScript must follow Editorial Poster / TIME Style and never allow Serif fallbacks."""
    jsx_text = (SHOWCASE_DIR / "cross_dimension_rescue_comp.jsx").read_text(encoding="utf-8")
    assert "ParagraphJustification.CENTER_JUSTIFY" in jsx_text
    assert "comp.motionBlur = true" in jsx_text
    assert "tl.motionBlur = true" in jsx_text
    assert "[1.0, 0.08, 0.14]" in jsx_text
    assert '"Impact"' in jsx_text
    assert "135" in jsx_text
    assert "6 ENGINES // 166 MCP TOOLS" in jsx_text
    assert "Times New Roman" not in jsx_text
    assert "Minion Pro" not in jsx_text


def test_aoe_uaf_world_r16_and_wfc_level_artifacts() -> None:
    """Asset Orchestration Engine (AOE + UAF) showcase terrain .r16 and WFC 7x7 level must be valid."""
    r16_path = SHOWCASE_DIR / "aoe_world" / "Sector7_ThermalBasin_heightmap.r16"
    assert r16_path.stat().st_size == 128 * 128 * 2

    summary = json.loads((SHOWCASE_DIR / "aoe_sector7_summary.json").read_text(encoding="utf-8"))
    assert summary["engine"] == "aoe-blender-mcp"
    assert summary["wfc_level"]["total_tiles_solved"] == 49
    assert summary["landscape"]["r16_bytes"] == 32768

    manifest = json.loads((SHOWCASE_DIR / "scene_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["engines_used"]) == 6
    assert "aoe-blender-mcp" in manifest["engines_used"]


def test_stills_contact_sheet_and_master_mp4_streams() -> None:
    """Stills, 2x2 contact sheet and H.264/AAC MP4 master must match exact dimensions and duration."""
    for still_name in (
        "act1_previz_ik.png",
        "act2_blender_corridor_3d.png",
        "act3_adobe_comms_lipsync.png",
        "act4_motion_vfx_climax.png",
    ):
        img = cv2.imread(str(SHOWCASE_DIR / still_name))
        assert img is not None
        assert img.shape == (720, 1280, 3)

    sheet = cv2.imread(str(SHOWCASE_DIR / "showcase_4acts_contact_sheet.png"))
    assert sheet is not None
    assert sheet.shape == (1440, 2560, 3)

    mp4_path = SHOWCASE_DIR / "cross_dimension_rescue_master.mp4"
    probe = subprocess.run(
        [str(FFMPEG_BIN), "-i", str(mp4_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = probe.stderr
    assert "Duration: 00:00:12" in stderr
    assert "h264" in stderr
    assert "1280x720" in stderr
    assert "24 fps" in stderr
    assert "aac" in stderr
    assert "48000 Hz" in stderr
    assert "stereo" in stderr


@pytest.mark.skipif(not BLENDER_EXE.exists(), reason="Blender 5.2 LTS not found")
def test_showcase_3d_head_and_axe_rigid_se3_in_blend() -> None:
    """Headless Blender depsgraph evaluation must prove rigid SE(3) invariance on Head and Hero_FireAxe."""
    blend_path = SHOWCASE_DIR / "cross_dimension_rescue.blend"
    expr = "\n".join(
        [
            "import bpy, json",
            "import numpy as np",
            "scene = bpy.context.scene",
            "char_obj = bpy.data.objects['RagdollFirefighter']",
            "axe_obj = bpy.data.objects['Hero_FireAxe']",
            "rig_obj = bpy.data.objects['CharacterRig']",
            "scene.frame_set(1)",
            "dg = bpy.context.evaluated_depsgraph_get()",
            "ec_rest = char_obj.evaluated_get(dg)",
            "ea_rest = axe_obj.evaluated_get(dg)",
            "rc = ec_rest.to_mesh()",
            "ra = ea_rest.to_mesh()",
            "head_idx = [v.index for v in rc.vertices if v.co.z >= 1.20][::25]",
            "axe_idx = [v.index for v in ra.vertices][::12]",
            "ec_rest.to_mesh_clear()",
            "ea_rest.to_mesh_clear()",
            "def pdist(verts, idx):",
            "    pts = np.array([verts[i].co[:] for i in idx])",
            "    return np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)",
            "hd, ad, ys = [], [], []",
            "for f in [1, 72, 120, 180, 240, 288]:",
            "    scene.frame_set(f)",
            "    dg = bpy.context.evaluated_depsgraph_get()",
            "    ys.append(float(rig_obj.location.y))",
            "    ec_eval = char_obj.evaluated_get(dg)",
            "    ea_eval = axe_obj.evaluated_get(dg)",
            "    ec = ec_eval.to_mesh()",
            "    ea = ea_eval.to_mesh()",
            "    hd.append(pdist(ec.vertices, head_idx))",
            "    ad.append(pdist(ea.vertices, axe_idx))",
            "    ec_eval.to_mesh_clear()",
            "    ea_eval.to_mesh_clear()",
            "print('SHOWCASE_SE3:' + json.dumps({",
            "    'head_var': float(np.var(np.stack(hd), axis=0).max()),",
            "    'axe_var': float(np.var(np.stack(ad), axis=0).max()),",
            "    'y_start': ys[0],",
            "    'y_end': ys[-1],",
            "}))",
        ]
    )
    proc = subprocess.run(
        [str(BLENDER_EXE), "--factory-startup", "-b", str(blend_path), "--python-expr", expr],
        capture_output=True,
        text=True,
        check=True,
    )
    marker = [line for line in proc.stdout.splitlines() if line.startswith("SHOWCASE_SE3:")]
    assert marker, f"Missing SHOWCASE_SE3 telemetry in Blender output:\n{proc.stdout}\n{proc.stderr}"
    metrics = json.loads(marker[-1].split("SHOWCASE_SE3:", 1)[1])
    assert metrics["head_var"] < 1e-10, f"Head deformed across walk: {metrics['head_var']}"
    assert metrics["axe_var"] < 1e-10, f"Hero_FireAxe deformed across walk: {metrics['axe_var']}"
    assert metrics["y_end"] < metrics["y_start"] - 1.5, "Character did not advance forward down corridor"
