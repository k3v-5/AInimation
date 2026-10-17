"""
Blender Studio Image-to-3D Render Script for IANIMATION.
Imports a 2D concept image, sets up volumetric relief, PBR shader node network,
3-point cinematic lighting rig, and renders a high-quality studio shot.
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import sys


def render_image_to_studio(
    image_path: str,
    output_path: str,
    resolution: tuple[int, int] = (1920, 1080),
    samples: int = 64,
) -> None:
    import bpy

    # 1. Clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_file)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"

    # Configure Eevee Next settings
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = samples

    # 2. Load Image to get dimensions
    img_path = Path(image_path).resolve()
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    img_data = bpy.data.images.load(str(img_path))
    aspect = img_data.size[0] / max(1, img_data.size[1])

    # 3. Create Displaced 3D Sculptural Canvas Plane
    plane_width = 3.0
    plane_height = plane_width / aspect
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0))
    plane = bpy.context.active_object
    plane.name = "Art_Canvas_3D"
    plane.scale = (plane_width, plane_height, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    # Subdivide mesh for geometry depth
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=32)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.shade_smooth()

    # 4. Construct PBR Shader Material
    mat = bpy.data.materials.new(name="PBR_Studio_Art")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Nodes: Output, Principled BSDF, Image Texture, Bump (Normals), ColorRamp (Roughness)
    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_out.location = (600, 0)

    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.location = (200, 0)
    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    # Image Texture node
    node_img = nodes.new(type="ShaderNodeTexImage")
    node_img.image = img_data
    node_img.location = (-400, 100)
    links.new(node_img.outputs["Color"], node_bsdf.inputs["Base Color"])

    # Bump node (generates tangent normals from luminance gradients)
    node_bump = nodes.new(type="ShaderNodeBump")
    node_bump.location = (-100, -200)
    node_bump.inputs["Strength"].default_value = 0.45
    node_bump.inputs["Distance"].default_value = 0.15
    links.new(node_img.outputs["Color"], node_bump.inputs["Height"])
    links.new(node_bump.outputs["Normal"], node_bsdf.inputs["Normal"])

    # Roughness modulation (glossy beak/feathers vs matte parchment)
    node_ramp = nodes.new(type="ShaderNodeValToRGB")
    node_ramp.location = (-100, 50)
    node_ramp.color_ramp.elements[0].position = 0.2
    node_ramp.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0)  # Specular highlights on dark feathers
    node_ramp.color_ramp.elements[1].position = 0.8
    node_ramp.color_ramp.elements[1].color = (0.85, 0.85, 0.85, 1.0)  # Matte paper
    links.new(node_img.outputs["Color"], node_ramp.inputs["Fac"])
    links.new(node_ramp.outputs["Color"], node_bsdf.inputs["Roughness"])

    plane.data.materials.append(mat)

    # 5. Studio Backdrop Curved Cyclorama
    bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0, 2.5, -plane_height / 2))
    backdrop = bpy.context.active_object
    backdrop.name = "Studio_Backdrop"
    backdrop.rotation_euler = (math.radians(90), 0, 0)

    mat_back = bpy.data.materials.new(name="Studio_Backdrop_Mat")
    mat_back.use_nodes = True
    bsdf_back = mat_back.node_tree.nodes.get("Principled BSDF")
    if bsdf_back:
        bsdf_back.inputs["Base Color"].default_value = (0.04, 0.04, 0.06, 1.0)  # Dark slate studio
        bsdf_back.inputs["Roughness"].default_value = 0.95
    backdrop.data.materials.append(mat_back)

    # 6. Cinematic 3-Point Studio Lighting Rig
    # Key Light (Warm golden primary light at 45 degrees)
    bpy.ops.object.light_add(type="AREA", radius=2.5, location=(3.2, -3.8, 3.2))
    key = bpy.context.active_object
    key.name = "Studio_KeyLight"
    key.data.energy = 580.0
    key.data.color = (1.0, 0.92, 0.84)  # 5000K warm

    # Fill Light (Cool diffuse fill)
    bpy.ops.object.light_add(type="AREA", radius=4.0, location=(-4.0, -2.8, 1.8))
    fill = bpy.context.active_object
    fill.name = "Studio_FillLight"
    fill.data.energy = 220.0
    fill.data.color = (0.84, 0.91, 1.0)  # 7500K cool

    # Rim / Kicker Light (Backlight grazing feather contours)
    bpy.ops.object.light_add(type="SPOT", radius=0.6, location=(1.0, 3.2, 2.8))
    rim = bpy.context.active_object
    rim.name = "Studio_RimLight"
    rim.data.energy = 750.0
    rim.data.color = (1.0, 0.85, 0.80)
    rim.data.spot_size = math.radians(50)

    # 7. Cinematic Camera (85mm Lens, subtle orbital angle for 3D depth)
    bpy.ops.object.camera_add(location=(0.4, -4.5, 0.3), rotation=(math.radians(88), 0, math.radians(5)))
    cam = bpy.context.active_object
    cam.name = "Cinematic_Camera"
    cam.data.lens = 75.0  # 75mm portrait focal length
    scene.camera = cam

    # Track to canvas center
    track = cam.constraints.new(type="TRACK_TO")
    track.target = plane
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Save .blend scene for user inspection
    blend_path = out_file.with_suffix(".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    # 8. Render Still Frame
    bpy.ops.render.render(write_still=True)
    print(f"[BLENDER_RENDER_SUCCESS] High-quality render saved to: {out_file}")
    print(f"[BLENDER_SCENE_SAVED] Blender project file saved to: {blend_path}")


def main() -> None:
    argv = sys.argv
    if "--" in argv:
        args_list = argv[argv.index("--") + 1 :]
    else:
        args_list = []

    parser = argparse.ArgumentParser(description="Image to Blender Studio Render CLI")
    parser.add_argument("--image", type=str, required=True, help="Input image path")
    parser.add_argument("--output", type=str, required=True, help="Output render path (.png)")
    parser.add_argument("--resolution", type=str, default="1920x1080", help="Resolution WxH")
    parser.add_argument("--samples", type=int, default=64, help="Render samples")

    parsed = parser.parse_args(args_list)
    res_x, res_y = [int(v) for v in parsed.resolution.split("x")]

    render_image_to_studio(
        image_path=parsed.image,
        output_path=parsed.output,
        resolution=(res_x, res_y),
        samples=parsed.samples,
    )


if __name__ == "__main__":
    main()
