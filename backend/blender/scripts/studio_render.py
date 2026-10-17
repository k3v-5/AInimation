"""
Blender Studio Headless Render Script.
Executed inside Blender's embedded Python interpreter (bpy) via:
    blender -b -P backend/blender/scripts/studio_render.py -- [arguments]
"""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
import sys


def setup_studio_scene(
    mesh_path: str | None,
    output_path: str,
    resolution: tuple[int, int] = (1920, 1080),
    render_engine: str = "CYCLES",
    samples: int = 64,
    save_blend_path: str | None = None,
) -> None:
    import bpy

    # 1. Clear existing objects in default scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. Configure Render Engine & Output
    scene = bpy.context.scene
    scene.render.engine = render_engine
    if render_engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
        # Use CPU if GPU device is not set or in test environment
        scene.cycles.device = "CPU"
    elif render_engine == "BLENDER_EEVEE_NEXT":
        scene.eevee.taa_render_samples = samples

    scene.render.resolution_x = resolution[0]
    scene.render.resolution_y = resolution[1]
    scene.render.resolution_percentage = 100

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out_file)

    if out_file.suffix.lower() in [".png", ".jpg", ".jpeg"]:
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA"
    elif out_file.suffix.lower() in [".mp4", ".mov"]:
        scene.render.image_settings.file_format = "FFMPEG"
        scene.render.ffmpeg.format = "MPEG4"
        scene.render.ffmpeg.codec = "H264"

    # 3. Import or generate target 3D Subject
    target_object = None
    if mesh_path and Path(mesh_path).exists():
        suffix = Path(mesh_path).suffix.lower()
        if suffix in [".glb", ".gltf"]:
            bpy.ops.import_scene.gltf(filepath=str(Path(mesh_path).resolve()))
        elif suffix == ".obj":
            bpy.ops.wm.obj_import(filepath=str(Path(mesh_path).resolve()))

        # Select imported objects
        selected = bpy.context.selected_objects
        if selected:
            target_object = selected[0]
    else:
        # Fallback: create a smooth parametric sculptural torus/sphere
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 1.0))
        target_object = bpy.context.active_object
        bpy.ops.object.shade_smooth()

    # 4. Cinematic 3-Point Studio Lighting Setup
    # Key Light (Warm, primary directional)
    bpy.ops.object.light_add(type="AREA", radius=2.0, location=(3.0, -3.5, 4.0))
    key_light = bpy.context.active_object
    key_light.data.energy = 500.0
    key_light.data.color = (1.0, 0.95, 0.88)  # 5500K Warm

    # Fill Light (Cool, soft contrast fill)
    bpy.ops.object.light_add(type="AREA", radius=3.5, location=(-4.0, -2.5, 2.5))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 220.0
    fill_light.data.color = (0.85, 0.92, 1.0)  # 7500K Cool

    # Rim / Kicker Light (High-energy silhouette edge light)
    bpy.ops.object.light_add(type="SPOT", radius=0.5, location=(0.0, 4.0, 3.5))
    rim_light = bpy.context.active_object
    rim_light.data.energy = 700.0
    rim_light.data.color = (1.0, 0.98, 0.95)
    rim_light.data.spot_size = math.radians(45)

    # 5. Cinematic Portrait Camera (85mm Lens with Look-At)
    bpy.ops.object.camera_add(location=(0.0, -4.2, 1.4), rotation=(math.radians(82), 0, 0))
    cam = bpy.context.active_object
    cam.data.lens = 85.0  # 85mm portrait telephoto
    scene.camera = cam

    # Add Track-To constraint pointing at subject center
    if target_object:
        constraint = cam.constraints.new(type="TRACK_TO")
        constraint.target = target_object
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

    # 6. Save .blend file if requested
    if save_blend_path:
        blend_file = Path(save_blend_path).resolve()
        blend_file.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))

    # 7. Render frame
    bpy.ops.render.render(write_still=True)
    print(f"[BLENDER_STUDIO_RENDER] Output rendered successfully to: {out_file}")


def main() -> None:
    argv = sys.argv
    if "--" in argv:
        args_list = argv[argv.index("--") + 1 :]
    else:
        args_list = []

    parser = argparse.ArgumentParser(description="Blender Studio Render CLI")
    parser.add_argument("--mesh", type=str, default=None, help="Path to 3D mesh (.glb/.obj)")
    parser.add_argument("--output", type=str, required=True, help="Destination render output path")
    parser.add_argument("--resolution", type=str, default="1280x720", help="Resolution string (WxH)")
    parser.add_argument("--engine", type=str, default="CYCLES", choices=["CYCLES", "BLENDER_EEVEE_NEXT"])
    parser.add_argument("--samples", type=int, default=32, help="Render sampling quality")
    parser.add_argument("--save-blend", type=str, default=None, help="Optional .blend output path")

    parsed = parser.parse_args(args_list)

    res_parts = parsed.resolution.split("x")
    res_x = int(res_parts[0])
    res_y = int(res_parts[1])

    setup_studio_scene(
        mesh_path=parsed.mesh,
        output_path=parsed.output,
        resolution=(res_x, res_y),
        render_engine=parsed.engine,
        samples=parsed.samples,
        save_blend_path=parsed.save_blend,
    )


if __name__ == "__main__":
    main()
