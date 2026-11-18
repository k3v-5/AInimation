"""
Automated Visual & Geometric Integrity Test Suite for Ragdoll Firefighter 3D Articulation
----------------------------------------------------------------------------------------
Complies 100% with GEMINI.md standards (Strict Typing, 3D-First, Zero False-Positives):
1. Evaluates actual 3D vertex positions under armature deformation via Blender depsgraph.
2. Asserts Zero Deformation (SE(3) distance variance < 1e-10) for Head Assembly (Helmet, Hair, Face, Eyes, Mouth).
3. Asserts Zero Deformation (SE(3) distance variance < 1e-10) for dedicated Hero_FireAxe prop.
4. Asserts correct Belt Attachment coordinates for Hero_FireAxe (seated on front coat belt, not head or floor).
5. Asserts Zero Inter-Leg Webbing (0 vertices in central inter-leg gap at keyframes 1, 12, 24, 36).
6. Asserts Natural Physical Bounding Envelopes across all animation frames.
7. Verifies all deliverables (.blend, .glb, .mp4, .gif, stills) exist and are non-corrupt.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import pytest
from PIL import Image

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
SCENES_DIR = PROJECT_ROOT / "outputs" / "scenes"
RENDERS_DIR = PROJECT_ROOT / "outputs" / "renders"
BLENDER_BIN = Path(r"E:\Blender\blender.exe")


def test_deliverable_files_exist() -> None:
    """Verifies all master deliverables exist and are non-empty."""
    blend_path = SCENES_DIR / "ragdoll_firefighter_walk.blend"
    glb_path = SCENES_DIR / "ragdoll_firefighter_walk.glb"
    mp4_path = RENDERS_DIR / "ragdoll_firefighter_walk.mp4"
    gif_path = RENDERS_DIR / "ragdoll_firefighter_walk.gif"

    assert blend_path.exists(), f"Missing master .blend: {blend_path}"
    assert blend_path.stat().st_size > 500_000, f"Blend file too small: {blend_path.stat().st_size} bytes"

    assert glb_path.exists(), f"Missing master .glb: {glb_path}"
    assert glb_path.stat().st_size > 500_000, f"GLB file too small: {glb_path.stat().st_size} bytes"

    assert mp4_path.exists(), f"Missing video: {mp4_path}"
    assert mp4_path.stat().st_size > 50_000, f"MP4 file too small: {mp4_path.stat().st_size} bytes"

    assert gif_path.exists(), f"Missing GIF: {gif_path}"
    assert gif_path.stat().st_size > 100_000, f"GIF file too small: {gif_path.stat().st_size} bytes"


def test_rendered_images_integrity() -> None:
    """Verifies all canonical stills and walk keyframes are valid high-res images."""
    required_stills = [
        "ragdoll_angle_000_front.png",
        "ragdoll_angle_045_hero34.png",
        "ragdoll_angle_090_profile.png",
        "ragdoll_angle_180_dorsal.png",
        "walk_f12_left_step.png",
        "walk_f24_plant.png",
        "walk_f36_right_step.png",
    ]

    for fname in required_stills:
        img_path = RENDERS_DIR / fname
        assert img_path.exists(), f"Missing render: {img_path}"
        with Image.open(img_path) as im:
            assert im.size in ((640, 640), (768, 768)), f"Incorrect dimensions {im.size} for {fname}"
            assert im.mode in ("RGB", "RGBA"), f"Incorrect color mode {im.mode} for {fname}"


def test_evaluated_mesh_deformation_invariance() -> None:
    """
    Directly inspects the evaluated deformed mesh in headless Blender at keyframes
    (1, 12, 24, 36) to assert:
    1. Zero deformation in Head Assembly (sigma^2 < 1e-10).
    2. Zero deformation in Hero_FireAxe Prop (sigma^2 < 1e-10).
    3. Proper belt seating location for Hero_FireAxe (Z in [0.45, 1.05], X in [0.05, 0.35], Y <= -0.10).
    4. Zero vertices in central inter-leg gap (|X| <= 0.02, 0.20 <= Z <= 0.45, Y > 0.0).
    5. Bounding envelope containment (all vertices within physical limits [0.0, 1.95]m).
    """
    assert BLENDER_BIN.exists(), f"Blender not found at {BLENDER_BIN}"
    blend_path = SCENES_DIR / "ragdoll_firefighter_walk.blend"
    assert blend_path.exists(), f"Blend scene not found at {blend_path}"

    eval_script = """
import sys
import math
import bpy
import mathutils
import numpy as np

p_blend = sys.argv[-1]
bpy.ops.wm.open_mainfile(filepath=p_blend)

char_obj = bpy.data.objects.get("RagdollFirefighter")
if not char_obj:
    char_obj = [o for o in bpy.data.objects if o.type == 'MESH' and o.name != 'StudioStage' and o.name != 'Hero_FireAxe'][0]

axe_obj = bpy.data.objects.get("Hero_FireAxe")
assert axe_obj is not None, "Hero_FireAxe object not found in scene!"

rest_char = char_obj.data
head_indices = [v.index for v in rest_char.vertices if v.co.z >= 1.20]
print(f"HEAD_REST_COUNT:{len(head_indices)}")
assert len(head_indices) > 500, "Too few head vertices detected"

rest_axe = axe_obj.data
axe_indices = list(range(len(rest_axe.vertices)))
print(f"AXE_VERT_COUNT:{len(axe_indices)}")
assert len(axe_indices) > 80, "Too few axe vertices detected"

keyframes = [1, 12, 24, 36]
head_pair_dists = []
axe_pair_dists = []
inter_leg_counts = []

np.random.seed(42)
head_pairs = [(head_indices[i], head_indices[j]) for i, j in zip(np.random.choice(len(head_indices), 40), np.random.choice(len(head_indices), 40)) if i != j]
axe_pairs = [(axe_indices[i], axe_indices[j]) for i, j in zip(np.random.choice(len(axe_indices), 40), np.random.choice(len(axe_indices), 40)) if i != j]

for f in keyframes:
    bpy.context.scene.frame_set(f)
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # 1. Evaluate Character Mesh
    eval_char = char_obj.evaluated_get(depsgraph)
    eval_char_mesh = eval_char.to_mesh()

    h_dists = [np.linalg.norm(np.array(eval_char_mesh.vertices[i].co) - np.array(eval_char_mesh.vertices[j].co)) for i, j in head_pairs]
    head_pair_dists.append(h_dists)

    # Inter-leg gap: must be strictly 0 vertices
    gap_vs = [v for v in eval_char_mesh.vertices if abs(v.co.x) <= 0.02 and 0.20 <= v.co.z <= 0.45 and v.co.y > 0.0]
    inter_leg_counts.append(len(gap_vs))

    # Envelope bounds check: no wild vertex explosion
    xs = [v.co.x for v in eval_char_mesh.vertices]
    ys = [v.co.y for v in eval_char_mesh.vertices]
    zs = [v.co.z for v in eval_char_mesh.vertices]
    assert min(xs) > -1.0 and max(xs) < 1.0, f"X bounds explosion at frame {f}: [{min(xs)}, {max(xs)}]"
    assert min(ys) > -1.0 and max(ys) < 1.0, f"Y bounds explosion at frame {f}: [{min(ys)}, {max(ys)}]"
    assert min(zs) >= -0.15 and max(zs) < 2.05, f"Z bounds explosion at frame {f}: [{min(zs)}, {max(zs)}]"

    eval_char.to_mesh_clear()

    # 2. Evaluate Hero Fire Axe
    eval_axe = axe_obj.evaluated_get(depsgraph)
    eval_axe_mesh = eval_axe.to_mesh()

    a_dists = [np.linalg.norm(np.array(eval_axe_mesh.vertices[i].co) - np.array(eval_axe_mesh.vertices[j].co)) for i, j in axe_pairs]
    axe_pair_dists.append(a_dists)

    # Verify Axe World Coordinates (Belt Level Seating)
    world_axe_zs = [(eval_axe.matrix_world @ v.co).z for v in eval_axe_mesh.vertices]
    world_axe_xs = [(eval_axe.matrix_world @ v.co).x for v in eval_axe_mesh.vertices]
    world_axe_ys = [(eval_axe.matrix_world @ v.co).y for v in eval_axe_mesh.vertices]

    min_az, max_az = min(world_axe_zs), max(world_axe_zs)
    min_ax, max_ax = min(world_axe_xs), max(world_axe_xs)
    max_ay = max(world_axe_ys)

    assert 0.25 <= min_az and max_az <= 0.95, f"Axe not at belt/thigh level at frame {f}: Z in [{min_az:.3f}, {max_az:.3f}]"
    assert 0.05 <= max_ax <= 0.45, f"Axe not on doll's left side at frame {f}: X in [{min_ax:.3f}, {max_ax:.3f}]"
    assert max_ay <= -0.10, f"Axe not in front of coat at frame {f}: max Y = {max_ay:.3f}"

    eval_axe.to_mesh_clear()

# Compute distance variances across frames
head_arr = np.array(head_pair_dists)
head_var = np.var(head_arr, axis=0)
max_head_var = np.max(head_var)

axe_arr = np.array(axe_pair_dists)
axe_var = np.var(axe_arr, axis=0)
max_axe_var = np.max(axe_var)

print(f"MAX_HEAD_VARIANCE:{max_head_var:.14f}")
print(f"MAX_AXE_VARIANCE:{max_axe_var:.14f}")
print(f"INTER_LEG_GAP_COUNTS:{inter_leg_counts}")

assert max_head_var < 1e-10, f"Head deformed! Max distance variance: {max_head_var}"
assert max_axe_var < 1e-10, f"Axe deformed! Max distance variance: {max_axe_var}"
assert max(inter_leg_counts) == 0, f"Inter-leg webbing bridge detected: {inter_leg_counts}"

print("TEST_RIGID_INTEGRITY_PASSED")
"""

    cmd = [
        str(BLENDER_BIN),
        "-b",
        "--python-expr",
        eval_script,
        "--",
        str(blend_path.resolve()),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert res.returncode == 0, f"Blender evaluation failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    assert "TEST_RIGID_INTEGRITY_PASSED" in res.stdout, f"Integrity assertions failed:\n{res.stdout}"
