"""
Blender 4.3.2 Studio Renderer for Volumetric 3D Red Raven.
Renders high-resolution 3/4 perspective still and 3D rotational turntable animation.
"""

from __future__ import annotations

import math
from pathlib import Path
import sys


def setup_and_render_volumetric_raven(
    obj_path: str,
    albedo_path: str,
    normal_path: str,
    output_still: str,
    output_video: str,
    resolution: tuple[int, int] = (1920, 1080),
    samples: int = 48,
    frame_count: int = 48,
) -> None:
    import bpy

    # 1. Reset factory scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100
    scene.render.fps = 24

    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = samples

    # 2. Import Volumetric 3D OBJ Mesh
    bpy.ops.wm.obj_import(filepath=str(Path(obj_path).resolve()))
    selected = bpy.context.selected_objects
    if not selected:
        raise RuntimeError("Failed to import OBJ mesh into Blender scene")

    raven_obj = selected[0]
    raven_obj.name = "Volumetric_Red_Raven_3D"

    # Center object origin to geometry and smooth shading
    bpy.context.view_layer.objects.active = raven_obj
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    raven_obj.location = (0.0, 0.0, 0.0)
    bpy.ops.object.shade_smooth()

    # 3. Setup High-Fidelity PBR Shader Material
    mat = bpy.data.materials.new(name="PBR_Volumetric_Raven")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_out.location = (600, 0)

    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.location = (200, 0)
    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    # Albedo Texture
    img_albedo = bpy.data.images.load(str(Path(albedo_path).resolve()))
    node_albedo = nodes.new(type="ShaderNodeTexImage")
    node_albedo.image = img_albedo
    node_albedo.location = (-400, 150)
    links.new(node_albedo.outputs["Color"], node_bsdf.inputs["Base Color"])
    links.new(node_albedo.outputs["Alpha"], node_bsdf.inputs["Alpha"])

    # Tangent Space Normal Map
    img_normal = bpy.data.images.load(str(Path(normal_path).resolve()))
    img_normal.colorspace_settings.name = "Non-Color"
    node_norm_tex = nodes.new(type="ShaderNodeTexImage")
    node_norm_tex.image = img_normal
    node_norm_tex.location = (-400, -150)

    node_norm_map = nodes.new(type="ShaderNodeNormalMap")
    node_norm_map.inputs["Strength"].default_value = 1.2
    node_norm_map.location = (-100, -150)
    links.new(node_norm_tex.outputs["Color"], node_norm_map.inputs["Color"])
    links.new(node_norm_map.outputs["Normal"], node_bsdf.inputs["Normal"])

    # Material properties
    node_bsdf.inputs["Roughness"].default_value = 0.42
    if "Specular IOR Level" in node_bsdf.inputs:
        node_bsdf.inputs["Specular IOR Level"].default_value = 0.55

    # EEVEE Next in Blender 4.3+ handles transparency directly via BSDF Alpha
    raven_obj.data.materials.clear()
    raven_obj.data.materials.append(mat)

    # 4. Studio Backdrop Curved Wall
    bpy.ops.mesh.primitive_plane_add(size=14.0, location=(0.0, 3.5, 0.0))
    backdrop = bpy.context.active_object
    backdrop.name = "Studio_Backdrop"
    backdrop.rotation_euler = (math.radians(90), 0, 0)

    mat_bg = bpy.data.materials.new(name="Backdrop_Material")
    mat_bg.use_nodes = True
    bsdf_bg = mat_bg.node_tree.nodes.get("Principled BSDF")
    if bsdf_bg:
        bsdf_bg.inputs["Base Color"].default_value = (0.05, 0.05, 0.08, 1.0)  # Dark charcoal studio
        bsdf_bg.inputs["Roughness"].default_value = 0.95
    backdrop.data.materials.append(mat_bg)

    # 5. Cinematic 3-Point Studio Lighting Rig
    # Key Light (Warm golden primary light at 45 degrees, casts dynamic 3D relief shadows)
    bpy.ops.object.light_add(type="AREA", radius=1.8, location=(3.2, -3.2, 2.8))
    key = bpy.context.active_object
    key.name = "Studio_KeyLight"
    key.data.energy = 550.0
    key.data.color = (1.0, 0.92, 0.84)

    # Fill Light (Cool ambient soft fill)
    bpy.ops.object.light_add(type="AREA", radius=3.2, location=(-3.8, -2.4, 1.6))
    fill = bpy.context.active_object
    fill.name = "Studio_FillLight"
    fill.data.energy = 220.0
    fill.data.color = (0.84, 0.91, 1.0)

    # Rim / Kicker Light (High-intensity contour edge light behind subject)
    bpy.ops.object.light_add(type="SPOT", radius=0.5, location=(0.6, 2.8, 2.4))
    rim = bpy.context.active_object
    rim.name = "Studio_RimLight"
    rim.data.energy = 850.0
    rim.data.color = (1.0, 0.88, 0.82)
    rim.data.spot_size = math.radians(45)

    # 6. Cinematic 85mm Camera
    # Placed at an angle so the 3D volume, protruding beak, chest curvature, and depth are undeniable
    bpy.ops.object.camera_add(location=(0.0, -3.8, 0.2), rotation=(math.radians(88), 0, 0))
    cam = bpy.context.active_object
    cam.name = "Cinematic_Camera"
    cam.data.lens = 85.0
    scene.camera = cam

    # Add Track-To constraint
    track = cam.constraints.new(type="TRACK_TO")
    track.target = raven_obj
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Save .blend file
    blend_path = Path(output_still).with_suffix(".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    # 7. Render 3/4 Perspective Still (Raven rotated 28 degrees in Yaw)
    raven_obj.rotation_euler = (math.radians(-4), math.radians(4), math.radians(28))

    scene.render.filepath = str(Path(output_still).resolve())
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)
    print(f"[SUCCESS] 3/4 Perspective 3D Still rendered to: {output_still}")

    # 8. Animate 3D Turntable (Rotational Parallax Loop)
    scene.frame_start = 1
    scene.frame_end = frame_count

    for f in range(1, frame_count + 1):
        t = (f - 1) / (frame_count - 1)
        # Smooth sinusoidal oscillation: Yaw [-32 deg, +32 deg], Pitch [-6 deg, +6 deg]
        yaw_angle = math.sin(t * 2 * math.pi) * math.radians(32)
        pitch_angle = math.cos(t * 2 * math.pi) * math.radians(6)

        raven_obj.rotation_euler = (pitch_angle, 0, yaw_angle)
        raven_obj.keyframe_insert(data_path="rotation_euler", frame=f)

    # Configure Video Render (FFMPEG H.264)
    vid_file = Path(output_video).resolve()
    vid_file.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(vid_file)
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"

    bpy.ops.render.render(animation=True)
    print(f"[SUCCESS] 3D Turntable Animation rendered to: {output_video}")


if __name__ == "__main__":
    obj = "outputs/raven_3d/raven_volumetric_3d.obj"
    albedo = "outputs/raven_3d/raven_cutout.png"
    normal = "outputs/raven_3d/raven_pbr_normal.png"
    still = "outputs/renders/red_raven_3d_volumetric.png"
    video = "outputs/renders/red_raven_3d_turntable.mp4"

    setup_and_render_volumetric_raven(
        obj_path=obj,
        albedo_path=albedo,
        normal_path=normal,
        output_still=still,
        output_video=video,
        resolution=(1280, 720),
        samples=32,
        frame_count=48,
    )
