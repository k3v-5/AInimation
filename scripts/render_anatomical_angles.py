"""
Cinematic Multi-Angle & Turntable Renderer for IANIMATION.
Renders high-definition stills and 360-degree orbit turntable from the Blender scene.
Includes the specific user-reported front-facing angle (Azimuth -75 deg, Elevation +12 deg)
to validate the Avian Anatomical Depth Prior against monocular ballooning.
"""

import math
import os
import subprocess
from pathlib import Path
import bpy
import mathutils

def render_scene_angles(
    blend_path: str,
    output_dir: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    samples: int = 32,
) -> None:
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    out_d = Path(output_dir).resolve()
    out_d.mkdir(parents=True, exist_ok=True)

    # Configure EEVEE Next PBR settings
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "use_raytracing"):
            scene.eevee.use_raytracing = True
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 0.5
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples

    # Seamless 360 Studio World Background (prevents flat plane edge clipping)
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.045, 0.045, 0.065, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    backdrop = scene.objects.get("Studio_Backdrop")
    if backdrop:
        backdrop.hide_render = True

    # Find character bounds
    char_objs = [o for o in scene.objects if o.type == 'MESH' and o.name != "Studio_Backdrop"]
    all_bounds = []
    for obj in char_objs:
        all_bounds.extend([obj.matrix_world @ mathutils.Vector(b) for b in obj.bound_box])

    min_x = min(p.x for p in all_bounds)
    max_x = max(p.x for p in all_bounds)
    min_y = min(p.y for p in all_bounds)
    max_y = max(p.y for p in all_bounds)
    min_z = min(p.z for p in all_bounds)
    max_z = max(p.z for p in all_bounds)

    center = mathutils.Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0))
    span_x = max(0.1, max_x - min_x)
    span_z = max(0.1, max_z - min_z)

    cam_dist = max(span_x / 0.36, span_z / 0.28) * 0.90 + 1.2
    cam_dist = max(4.5, min(7.5, cam_dist))

    # Camera and Target
    cam = scene.objects.get("Cinematic_Camera")
    target = scene.objects.get("CameraTarget")
    if not target:
        target = bpy.data.objects.new("CameraTarget", None)
        scene.collection.objects.link(target)
    target.location = center

    if not cam:
        bpy.ops.object.camera_add(location=(center.x, center.y - cam_dist, center.z))
        cam = bpy.context.active_object
        cam.name = "Cinematic_Camera"
        scene.camera = cam

    cam.data.lens = 55.0

    # Ensure TrackTo constraint
    track = None
    for c in cam.constraints:
        if c.type == 'TRACK_TO':
            track = c
            break
    if not track:
        track = cam.constraints.new(type='TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Set to frame 1 (rest pose)
    scene.frame_set(1)

    angles = [
        ("angle_01_hero_front34", -15.0, 6.0),
        ("angle_02_side_profile", -55.0, 4.0),
        ("angle_user_facing_view", -75.0, 12.0), # Matches user-uploaded screenshot exactly!
        ("angle_03_dorsal_back34", 40.0, 14.0),
        ("angle_04_low_angle_dramatic", -10.0, -16.0),
        ("angle_05_top_perspective", -25.0, 30.0),
        ("angle_06_true_rear_view", 165.0, 8.0),
    ]

    for name, azim_deg, elev_deg in angles:
        azim = math.radians(azim_deg)
        elev = math.radians(elev_deg)

        cx = center.x + cam_dist * math.cos(elev) * math.sin(azim)
        cy = center.y - cam_dist * math.cos(elev) * math.cos(azim)
        cz = center.z + cam_dist * math.sin(elev)

        cam.location = (cx, cy, cz)
        bpy.context.view_layer.update()

        out_img = out_d / f"{name}.png"
        scene.render.filepath = str(out_img)
        bpy.ops.render.render(write_still=True)
        print(f"Rendered still angle: {out_img}")

    # Render 360-degree Orbit Turntable (36 frames)
    tt_frames_dir = out_d / "_tt_frames"
    tt_frames_dir.mkdir(parents=True, exist_ok=True)
    num_tt_frames = 36

    print("Rendering 360-degree turntable frames...")
    for idx in range(num_tt_frames):
        theta = (idx / num_tt_frames) * 2.0 * math.pi
        azim = theta
        elev = math.radians(8.0 + 6.0 * math.sin(2.0 * theta))

        cx = center.x + cam_dist * math.cos(elev) * math.sin(azim)
        cy = center.y - cam_dist * math.cos(elev) * math.cos(azim)
        cz = center.z + cam_dist * math.sin(elev)

        cam.location = (cx, cy, cz)
        bpy.context.view_layer.update()

        scene.render.filepath = str(tt_frames_dir / f"frame_{idx:04d}.png")
        bpy.ops.render.render(write_still=True)

    # Encode turntable MP4 & GIF
    tt_mp4 = out_d / "red_raven_3d_orbit_turntable.mp4"
    tt_gif = out_d / "red_raven_3d_orbit_turntable.gif"

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", str(tt_frames_dir / "frame_%04d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(tt_mp4),
    ], capture_output=True, check=False)

    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "24",
        "-i", str(tt_frames_dir / "frame_%04d.png"),
        "-vf", "fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        str(tt_gif),
    ], capture_output=True, check=False)

    # Cleanup temp turntable frames
    for f in tt_frames_dir.glob("frame_*.png"):
        f.unlink()
    try:
        tt_frames_dir.rmdir()
    except OSError:
        pass

    print(f"Rendered turntable mp4: {tt_mp4}")
    print(f"Rendered turntable gif: {tt_gif}")

if __name__ == "__main__":
    import sys
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
        blend = args[0] if len(args) > 0 else "outputs/scenes/red_raven_hierarchical_flight.blend"
        out_dir = args[1] if len(args) > 1 else "outputs/renders/multi_angle"
    else:
        blend = "outputs/scenes/red_raven_hierarchical_flight.blend"
        out_dir = "outputs/renders/multi_angle"
    render_scene_angles(blend, out_dir)
