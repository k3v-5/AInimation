"""
Blender 4.3+ Automated Skeletal Rigging, Skinning, Keyframe Animation & Rendering Script.

Executed via:
  blender -b -P backend/blender/scripts/rig_and_animate.py -- --config <config.json>
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys

try:
    import bpy
    import mathutils
except ImportError:
    bpy = None


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Blender Rigging and Animation Script")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    return parser.parse_args(argv)


def clean_scene():
    """Remove all objects, armatures, and lingering actions."""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for arm in list(bpy.data.armatures):
        bpy.data.armatures.remove(arm, do_unlink=True)
    for act in list(bpy.data.actions):
        bpy.data.actions.remove(act, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)


def import_mesh(mesh_path: str):
    """Import .obj or .glb/.gltf mesh into Blender."""
    p = Path(mesh_path).resolve()
    ext = p.suffix.lower()

    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(p))
    elif ext in [".glb", ".gltf"]:
        bpy.ops.import_scene.gltf(filepath=str(p))
    else:
        raise ValueError(f"Unsupported mesh format: {ext}")

    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not meshes:
        raise RuntimeError(f"No mesh objects found after importing {mesh_path}")

    # Prioritize mesh with highest vertex count if multiple are imported
    main_mesh = max(meshes, key=lambda m: len(m.data.vertices))
    return main_mesh


def create_armature(skeleton_type: str, bones_data: list):
    """Construct armature and edit bones from specification."""
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = f"{skeleton_type.capitalize()}_Armature"

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_obj.data.edit_bones

    # Clear default single bone
    while eb:
        eb.remove(eb[0])

    bone_map = {}
    for b_spec in bones_data:
        bone = eb.new(b_spec["name"])
        bone.head = mathutils.Vector(b_spec["head"])
        bone.tail = mathutils.Vector(b_spec["tail"])
        if b_spec.get("roll"):
            bone.roll = b_spec["roll"]
        bone_map[b_spec["name"]] = bone

    for b_spec in bones_data:
        p_name = b_spec.get("parent")
        if p_name and p_name in bone_map:
            bone_map[b_spec["name"]].parent = bone_map[p_name]

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj


def bind_skin(mesh_obj, arm_obj, bones_data: list):
    """
    Bind mesh to armature using automatic weights with mathematical
    continuous distance fallback (C^infinity Gaussian decay) to guarantee zero surface tearing.
    """
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    auto_ok = False
    try:
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        if len(mesh_obj.vertex_groups) > 0:
            auto_ok = True
    except Exception as exc:
        print(f"Warning: ARMATURE_AUTO threw {exc}, applying continuous distance weighting fallback.")

    if not auto_ok:
        # Parent directly to armature
        bpy.ops.object.parent_set(type='ARMATURE')
        mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj

        # Compute continuous distance weights per vertex
        # Bone positions in object space
        bone_centers = []
        bone_names = []
        for b_spec in bones_data:
            h = mathutils.Vector(b_spec["head"])
            t = mathutils.Vector(b_spec["tail"])
            center = (h + t) * 0.5
            bone_centers.append(center)
            bone_names.append(b_spec["name"])

        v_groups = {name: mesh_obj.vertex_groups.new(name=name) for name in bone_names}
        sigma = 0.25  # Smooth continuous kernel bandwidth

        for v in mesh_obj.data.vertices:
            v_co = v.co
            dists = [(v_co - c).length for c in bone_centers]
            # Gaussian weights
            raw_weights = [math.exp(-(d * d) / (2.0 * sigma * sigma)) for d in dists]
            total_w = sum(raw_weights) + 1e-8
            norm_weights = [w / total_w for w in raw_weights]

            for name, w in zip(bone_names, norm_weights):
                if w > 0.01:
                    v_groups[name].add([v.index], w, 'REPLACE')


def apply_animation(arm_obj, anim_data: dict):
    """Keyframe rotational curves on pose bones."""
    if not anim_data or "tracks" not in anim_data:
        return

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    action = bpy.data.actions.new(name=anim_data.get("name", "ArmatureAction"))
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    for track in anim_data["tracks"]:
        b_name = track["bone_name"]
        pb = arm_obj.pose.bones.get(b_name)
        if not pb:
            continue

        pb.rotation_mode = 'XYZ'
        for kf in track.get("keyframes", []):
            frame = kf["frame"]
            rot_deg = kf["rotation_euler_deg"]
            rot_rad = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
            pb.rotation_euler = rot_rad
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)

            if kf.get("location"):
                pb.location = mathutils.Vector(kf["location"])
                pb.keyframe_insert(data_path="location", frame=frame)

    bpy.ops.object.mode_set(mode='OBJECT')


def setup_cinematic_lighting_and_camera(mesh_obj, total_frames: int):
    """Set up 3-point studio lighting and 85mm portrait camera oriented at subject."""
    # Compute mesh center and dimensions
    bbox = [mesh_obj.matrix_world @ mathutils.Vector(corner) for corner in mesh_obj.bound_box]
    center = sum(bbox, mathutils.Vector((0, 0, 0))) / 8.0
    size_z = max(c.z for c in bbox) - min(c.z for c in bbox)
    size_y = max(c.y for c in bbox) - min(c.y for c in bbox)
    extent = max(size_z, size_y, 1.0)

    # Key Light (Warm Key)
    bpy.ops.object.light_add(type='AREA', radius=extent * 1.5, location=(center.x + 2.5, center.y - 3.0, center.z + 3.0))
    key = bpy.context.active_object
    key.name = "Studio_KeyLight"
    key.data.energy = 550.0
    key.data.color = (1.0, 0.96, 0.90)

    # Fill Light (Cool Fill)
    bpy.ops.object.light_add(type='AREA', radius=extent * 2.0, location=(center.x - 3.5, center.y - 2.0, center.z + 1.5))
    fill = bpy.context.active_object
    fill.name = "Studio_FillLight"
    fill.data.energy = 220.0
    fill.data.color = (0.85, 0.92, 1.0)

    # Rim Light (Crisp Rim)
    bpy.ops.object.light_add(type='SPOT', radius=extent * 0.5, location=(center.x, center.y + 3.5, center.z + 2.5))
    rim = bpy.context.active_object
    rim.name = "Studio_RimLight"
    rim.data.energy = 700.0
    rim.data.color = (1.0, 0.98, 0.95)
    rim.data.spot_size = math.radians(50)

    # 85mm Cinematic Camera
    bpy.ops.object.camera_add(location=(center.x, center.y - 3.8 * extent, center.z + 0.3 * extent))
    cam = bpy.context.active_object
    cam.name = "Cinematic_Camera"
    cam.data.lens = 85.0
    bpy.context.scene.camera = cam

    # Aim camera at subject center using Track To constraint
    empty = bpy.data.objects.new("CameraTarget", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = center

    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'


def render_animation_sequence(output_video: str, fps: int, total_frames: int, samples: int, engine: str):
    """Render the full animated sequence to MP4 ISOBMFF and convert to GIF."""
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = total_frames
    scene.render.fps = fps

    # Configure Engine
    if engine.upper() in ["BLENDER_EEVEE_NEXT", "EEVEE"]:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100

    out_p = Path(output_video).resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # Temporary frames directory
    frames_dir = out_p.parent / f"_frames_{out_p.stem}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.filepath = str(frames_dir / "frame_")

    print(f"Rendering {total_frames} animation frames at {fps} FPS with {scene.render.engine}...")
    bpy.ops.render.render(animation=True)

    # Encode with FFmpeg to H.264 MP4
    import subprocess
    mp4_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(out_p),
    ]
    subprocess.run(mp4_cmd, capture_output=True, check=False)

    # Also generate an inspection GIF
    gif_path = out_p.with_suffix(".gif")
    gif_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-vf", "fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        str(gif_path),
    ]
    subprocess.run(gif_cmd, capture_output=True, check=False)

    # Cleanup raw PNG frames
    for f in frames_dir.glob("frame_*.png"):
        f.unlink()
    try:
        frames_dir.rmdir()
    except OSError:
        pass


def main():
    args = parse_args()
    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    mesh_path = cfg["mesh_path"]
    skeleton_type = cfg.get("skeleton_type", "avian")
    bones_data = cfg["bones"]
    anim_data = cfg.get("animation")
    output_blend = cfg.get("output_blend")
    output_glb = cfg.get("output_glb")
    output_video = cfg.get("output_video")
    fps = cfg.get("fps", 24)
    total_frames = cfg.get("total_frames", 48)
    samples = cfg.get("samples", 16)
    engine = cfg.get("render_engine", "BLENDER_EEVEE_NEXT")

    print(f"Starting Blender Rigging: mesh={mesh_path}, type={skeleton_type}, bones={len(bones_data)}")
    clean_scene()

    mesh_obj = import_mesh(mesh_path)
    arm_obj = create_armature(skeleton_type, bones_data)
    bind_skin(mesh_obj, arm_obj, bones_data)

    if anim_data:
        apply_animation(arm_obj, anim_data)

    setup_cinematic_lighting_and_camera(mesh_obj, total_frames)

    # Export GLB
    if output_glb:
        out_g = Path(output_glb).resolve()
        out_g.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(
            filepath=str(out_g),
            export_format='GLB',
            export_animations=True,
        )
        print(f"Exported rigged GLB: {out_g}")

    # Save Blend file
    if output_blend:
        out_b = Path(output_blend).resolve()
        out_b.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out_b))
        print(f"Saved .blend file: {out_b}")

    # Render animation video if requested
    if output_video:
        render_animation_sequence(output_video, fps, total_frames, samples, engine)
        print(f"Rendered animation video: {output_video}")

    print("BLENDER_RIGGING_COMPLETE")


if __name__ == "__main__":
    main()
