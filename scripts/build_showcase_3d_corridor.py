"""Build Master 3D Emergency Corridor Scene in Blender 5.2 LTS for 'Cross-Dimension Rescue'.

Integrates:
- Proven watertight RagdollFirefighter (1.80m matte cloth PBR + clean BVH albedo)
- Rigid SE(3) Hero_FireAxe (4 PBR materials, anchored 100% to Spine)
- Procedural Industrial Sector 7 Corridor textured with 2K BaseColor/Normal/ORM/Emissive maps
- Rotating Thermal Core Reactor gyroscope rings + Recon Drone + 120 BPM pulsed alarm beacons
- 4-Act Cinematic RenderCam choreography with Track-To gimbal lock prevention (1280x720 @ 24 FPS)

Usage:
  E:\\Blender\\blender.exe --factory-startup -b -P scripts\\build_showcase_3d_corridor.py -- --preview
  E:\\Blender\\blender.exe --factory-startup -b -P scripts\\build_showcase_3d_corridor.py
"""

from __future__ import annotations

import math
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple

import bmesh
import bpy
from mathutils import Euler, Vector

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
SCENES_DIR = PROJECT_ROOT / "outputs" / "scenes"
RENDERS_DIR = PROJECT_ROOT / "outputs" / "renders"
OUT_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo"
TEX_DIR = OUT_DIR / "textures"
FRAMES_DIR = PROJECT_ROOT / "outputs" / "cache" / "showcase_3d_frames"

OUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)

IS_PREVIEW = "--preview" in sys.argv


def create_pbr_emissive_mat(
    name: str,
    base_color: Tuple[float, float, float, float],
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: Optional[Tuple[float, float, float, float]] = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    """Create a Principled BSDF material without deprecated use_nodes calls."""
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (400, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission_color is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission_color
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_corridor_textured_pbr_mat(
    name: str,
    uv_scale: Tuple[float, float] = (1.0, 3.5),
    use_emissive: bool = True,
    base_tint: Tuple[float, float, float] = (1.0, 1.0, 1.0),
) -> bpy.types.Material:
    """Create a 2K PBR material driven by BaseColor, ORM, Tangent Normal, and optional Emissive maps."""
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (650, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-850, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (-640, 0)
    mapping.inputs["Scale"].default_value = (uv_scale[0], uv_scale[1], 1.0)
    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])

    def load_tex(filename: str, colorspace: str, loc_y: float) -> bpy.types.ShaderNodeTexImage:
        t_node = nodes.new("ShaderNodeTexImage")
        t_node.location = (-360, loc_y)
        img = bpy.data.images.load(str((TEX_DIR / filename).resolve()), check_existing=True)
        img.colorspace_settings.name = colorspace
        t_node.image = img
        links.new(mapping.outputs["Vector"], t_node.inputs["Vector"])
        return t_node

    t_base = load_tex("corridor_basecolor.png", "sRGB", 360)
    t_orm = load_tex("corridor_orm.png", "Non-Color", 60)
    t_norm = load_tex("corridor_normal.png", "Non-Color", -240)
    t_emis = load_tex("corridor_emissive.png", "sRGB", -500)

    sep_orm = nodes.new("ShaderNodeSeparateColor")
    sep_orm.location = (-60, 60)
    links.new(t_orm.outputs["Color"], sep_orm.inputs["Color"])

    # Multiply BaseColor gently with baked AO (Red channel of ORM) and optional tint
    mix_ao = nodes.new("ShaderNodeMix")
    mix_ao.data_type = "RGBA"
    mix_ao.blend_type = "MULTIPLY"
    mix_ao.location = (-20, 320)
    mix_ao.inputs["Factor"].default_value = 0.75
    links.new(t_base.outputs["Color"], mix_ao.inputs[6])
    links.new(sep_orm.outputs["Red"], mix_ao.inputs[7])

    mix_tint = nodes.new("ShaderNodeMix")
    mix_tint.data_type = "RGBA"
    mix_tint.blend_type = "MULTIPLY"
    mix_tint.location = (130, 320)
    mix_tint.inputs["Factor"].default_value = 1.0
    mix_tint.inputs[7].default_value = (base_tint[0], base_tint[1], base_tint[2], 1.0)
    links.new(mix_ao.outputs[2], mix_tint.inputs[6])
    links.new(mix_tint.outputs[2], bsdf.inputs["Base Color"])

    links.new(sep_orm.outputs["Green"], bsdf.inputs["Roughness"])
    links.new(sep_orm.outputs["Blue"], bsdf.inputs["Metallic"])

    nrm_node = nodes.new("ShaderNodeNormalMap")
    nrm_node.location = (-20, -240)
    nrm_node.inputs["Strength"].default_value = 1.15
    links.new(t_norm.outputs["Color"], nrm_node.inputs["Color"])
    links.new(nrm_node.outputs["Normal"], bsdf.inputs["Normal"])

    if use_emissive and "Emission Color" in bsdf.inputs:
        links.new(t_emis.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 5.5

    return mat


def add_box(
    name: str,
    location: Tuple[float, float, float],
    scale: Tuple[float, float, float],
    mat: bpy.types.Material,
    rotation_deg: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    bevel_width: float = 0.02,
) -> bpy.types.Object:
    """Create a clean beveled box mesh for corridor structural architecture."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = Euler(
        (math.radians(rotation_deg[0]), math.radians(rotation_deg[1]), math.radians(rotation_deg[2])),
        "XYZ",
    )
    bpy.ops.object.transform_apply(scale=True)
    if bevel_width > 0.0:
        bev = obj.modifiers.new("Bevel", "BEVEL")
        bev.width = bevel_width
        bev.segments = 2
    obj.data.materials.append(mat)
    return obj


def create_reactor_fresnel_mat(name: str) -> bpy.types.Material:
    """Create a multi-layered plasma shader for the Thermal Core Reactor."""
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (520, 0)
    emis = nodes.new("ShaderNodeEmission")
    emis.location = (260, 0)
    emis.inputs["Strength"].default_value = 14.0

    lw = nodes.new("ShaderNodeLayerWeight")
    lw.location = (-240, 80)
    lw.inputs["Blend"].default_value = 0.42

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (-20, 80)
    ramp.color_ramp.elements[0].position = 0.08
    ramp.color_ramp.elements[0].color = (1.0, 0.78, 0.28, 1.0)
    e_mid = ramp.color_ramp.elements.new(0.45)
    e_mid.color = (1.0, 0.28, 0.04, 1.0)
    ramp.color_ramp.elements[2].position = 0.85
    ramp.color_ramp.elements[2].color = (0.85, 0.04, 0.08, 1.0)

    links.new(lw.outputs["Facing"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emis.inputs["Color"])
    links.new(emis.outputs["Emission"], out.inputs["Surface"])
    return mat


def create_architectural_metal_mat(
    name: str,
    base_color: Tuple[float, float, float, float],
    metallic: float = 0.86,
    roughness: float = 0.38,
) -> bpy.types.Material:
    """Create a procedural brushed/micro-bumped steel bulkhead material without stretched UVs."""
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (520, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (220, 0)
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-560, 0)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-320, -60)
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.55
    links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    map_r = nodes.new("ShaderNodeMapRange")
    map_r.location = (-60, 60)
    map_r.inputs["To Min"].default_value = max(0.18, roughness - 0.10)
    map_r.inputs["To Max"].default_value = min(0.85, roughness + 0.12)
    links.new(noise.outputs["Fac"], map_r.inputs["Value"])
    links.new(map_r.outputs["Result"], bsdf.inputs["Roughness"])

    bump = nodes.new("ShaderNodeBump")
    bump.location = (-40, -180)
    bump.inputs["Strength"].default_value = 0.08
    bump.inputs["Distance"].default_value = 0.01
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def build_corridor_and_reactor() -> Tuple[bpy.types.Object, bpy.types.Object, bpy.types.Object, List[bpy.types.Material], bpy.types.Object]:
    """Build Sector 7 Emergency Corridor, Thermal Core Reactor, Recon Drone, and Alarm Beacons."""
    mat_floor = create_corridor_textured_pbr_mat("Corridor_Deck_PBR", uv_scale=(1.2, 4.0), use_emissive=True)
    mat_bulkhead = create_architectural_metal_mat("Bulkhead_ArchitecturalSteel", (0.065, 0.078, 0.095, 1.0), metallic=0.84, roughness=0.40)
    mat_trim_steel = create_pbr_emissive_mat("Trim_Alloy", (0.22, 0.24, 0.28, 1.0), metallic=0.90, roughness=0.28)
    mat_hazard = create_pbr_emissive_mat("Hazard_Gold", (0.72, 0.50, 0.04, 1.0), metallic=0.15, roughness=0.45)

    mat_alarm_red = create_pbr_emissive_mat(
        "Alarm_Crimson_LED",
        (0.95, 0.05, 0.08, 1.0),
        metallic=0.1,
        roughness=0.2,
        emission_color=(1.0, 0.08, 0.12, 1.0),
        emission_strength=10.0,
    )
    mat_reactor_core = create_reactor_fresnel_mat("ThermalCore_Plasma")
    mat_cyan_led = create_pbr_emissive_mat(
        "Cyan_Reactor_LED",
        (0.02, 0.85, 1.0, 1.0),
        metallic=0.0,
        roughness=0.15,
        emission_color=(0.05, 0.90, 1.0, 1.0),
        emission_strength=12.0,
    )

    # 1. PBR 2K Floor Deck (Plane from Y=-6.0 to Y=+5.5, centered at Y=-0.25)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, -0.25, 0.0))
    floor = bpy.context.active_object
    floor.name = "Corridor_Floor"
    floor.scale = (3.8, 12.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    floor.data.materials.append(mat_floor)

    # Ceiling Plate
    add_box("Corridor_Ceiling", (0.0, -0.25, 3.65), (4.2, 12.2, 0.20), mat_bulkhead, bevel_width=0.02)

    # Left and Right Walls with Recessed Channels
    add_box("Corridor_Wall_L", (-1.95, -0.25, 1.80), (0.25, 12.0, 3.70), mat_bulkhead, bevel_width=0.02)
    add_box("Corridor_Wall_R", (1.95, -0.25, 1.80), (0.25, 12.0, 3.70), mat_bulkhead, bevel_width=0.02)
    add_box("Corridor_BackWall", (0.0, 5.40, 1.80), (4.0, 0.30, 3.70), mat_bulkhead, bevel_width=0.02)

    # Continuous Cyan Baseboard Light Rails + Upper Crimson Strip
    add_box("Floor_LED_L", (-1.68, -0.25, 0.14), (0.06, 11.4, 0.06), mat_cyan_led, bevel_width=0.005)
    add_box("Floor_LED_R", (1.68, -0.25, 0.14), (0.06, 11.4, 0.06), mat_cyan_led, bevel_width=0.005)

    # 2. Structural Industrial Rib Arches + Overhead Conduits
    rib_ys = [-4.2, -2.2, -0.2, 1.8, 3.8]
    for i, ry in enumerate(rib_ys):
        add_box(f"Rib_Pillar_L_{i}", (-1.70, ry, 1.75), (0.34, 0.32, 3.55), mat_trim_steel)
        add_box(f"Rib_Pillar_R_{i}", (1.70, ry, 1.75), (0.34, 0.32, 3.55), mat_trim_steel)
        add_box(f"Rib_Beam_Top_{i}", (0.0, ry, 3.42), (3.70, 0.36, 0.30), mat_trim_steel)
        # Caution stripe trim on lower pillar
        add_box(f"Rib_Hazard_L_{i}", (-1.52, ry, 0.65), (0.04, 0.34, 0.22), mat_hazard, bevel_width=0.005)
        add_box(f"Rib_Hazard_R_{i}", (1.52, ry, 0.65), (0.04, 0.34, 0.22), mat_hazard, bevel_width=0.005)
        # Alarm Beacon Light Bar
        add_box(f"Beacon_L_{i}", (-1.50, ry, 2.75), (0.08, 0.14, 0.34), mat_alarm_red, bevel_width=0.01)
        add_box(f"Beacon_R_{i}", (1.50, ry, 2.75), (0.08, 0.14, 0.34), mat_alarm_red, bevel_width=0.01)

    # Overhead Coolant Pipes
    for px in (-1.05, 1.05):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=11.6, location=(px, -0.25, 3.12))
        pipe = bpy.context.active_object
        pipe.name = f"OverheadPipe_{px:.1f}"
        pipe.rotation_euler = Euler((math.radians(90.0), 0.0, 0.0), "XYZ")
        pipe.data.materials.append(mat_trim_steel)

    # 3. Unstable Thermal Core Reactor Assembly at (0.0, +3.6, 1.45)
    reactor_pos = (0.0, 3.55, 1.45)
    add_box("Reactor_Pedestal", (0.0, 3.55, 0.32), (1.35, 1.15, 0.64), mat_trim_steel, bevel_width=0.03)
    add_box("Reactor_RingStand", (0.0, 3.55, 0.68), (1.05, 0.85, 0.12), mat_hazard, bevel_width=0.015)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.40, location=reactor_pos)
    core_sphere = bpy.context.active_object
    core_sphere.name = "ThermalCore_PlasmaSphere"
    bpy.ops.object.shade_smooth()
    core_sphere.data.materials.append(mat_reactor_core)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.66, minor_radius=0.055, major_segments=64, minor_segments=24, location=reactor_pos
    )
    rotor_outer = bpy.context.active_object
    rotor_outer.name = "ThermalCore_RotorOuter"
    bpy.ops.object.shade_smooth()
    rotor_outer.data.materials.append(mat_trim_steel)

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.52, minor_radius=0.04, major_segments=64, minor_segments=20, location=reactor_pos
    )
    rotor_inner = bpy.context.active_object
    rotor_inner.name = "ThermalCore_RotorInner"
    bpy.ops.object.shade_smooth()
    rotor_inner.data.materials.append(mat_cyan_led)

    # 4. Hovering Guardian Recon Drone
    drone_pos = (-0.82, 0.45, 1.62)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.15, location=drone_pos)
    drone = bpy.context.active_object
    drone.name = "ReconDrone_Body"
    drone.scale = (1.15, 1.30, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    drone.data.materials.append(mat_trim_steel)

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=20, ring_count=12, radius=0.068, location=(drone_pos[0], drone_pos[1] - 0.14, drone_pos[2])
    )
    drone_eye = bpy.context.active_object
    drone_eye.name = "ReconDrone_Eye"
    bpy.ops.object.shade_smooth()
    drone_eye.parent = drone
    drone_eye.matrix_parent_inverse = drone.matrix_world.inverted()
    drone_eye.data.materials.append(mat_cyan_led)

    for wing_x, w_name in ((-0.20, "ReconDrone_ThrusterL"), (0.20, "ReconDrone_ThrusterR")):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.075, minor_radius=0.018, major_segments=24, minor_segments=12,
            location=(drone_pos[0] + wing_x, drone_pos[1], drone_pos[2] + 0.02)
        )
        thruster = bpy.context.active_object
        thruster.name = w_name
        bpy.ops.object.shade_smooth()
        thruster.parent = drone
        thruster.matrix_parent_inverse = drone.matrix_world.inverted()
        thruster.data.materials.append(mat_cyan_led)

    return core_sphere, rotor_outer, rotor_inner, [mat_alarm_red, mat_reactor_core, mat_cyan_led], drone


def setup_scene() -> None:
    """Open watertight Ragdoll Firefighter master, build Sector 7 corridor, animate 288 frames, and render."""
    ragdoll_blend = SCENES_DIR / "ragdoll_firefighter_walk.blend"
    if not ragdoll_blend.exists():
        raise FileNotFoundError(f"Missing Ragdoll base blend: {ragdoll_blend}")

    bpy.ops.wm.open_mainfile(filepath=str(ragdoll_blend))

    # Remove old studio disc
    old_stage = bpy.data.objects.get("StudioStage")
    if old_stage:
        bpy.data.objects.remove(old_stage, do_unlink=True)

    # Ensure clean albedo and matte burlap finish are active
    char_obj = bpy.data.objects["RagdollFirefighter"]
    rig_obj = bpy.data.objects["CharacterRig"]
    axe_obj = bpy.data.objects["Hero_FireAxe"]

    healed_path = RENDERS_DIR / "clean_firefighter_albedo_healed.png"
    if healed_path.exists():
        img = bpy.data.images.load(str(healed_path.resolve()), check_existing=True)
        img.reload()
        mat_char = char_obj.material_slots[0].material
        for node in mat_char.node_tree.nodes:
            if node.type == "TEX_IMAGE":
                node.image = img
            elif node.type == "BSDF_PRINCIPLED":
                for lnk in list(node.inputs["Roughness"].links):
                    mat_char.node_tree.links.remove(lnk)
                node.inputs["Roughness"].default_value = 0.78
                for lnk in list(node.inputs["Metallic"].links):
                    mat_char.node_tree.links.remove(lnk)
                node.inputs["Metallic"].default_value = 0.0
                if "Specular IOR Level" in node.inputs:
                    node.inputs["Specular IOR Level"].default_value = 0.25

    core_sphere, rotor_outer, rotor_inner, emissive_mats, drone = build_corridor_and_reactor()
    mat_alarm_red, mat_reactor_core, _ = emissive_mats

    # Clear old rig keyframes and build 288-frame continuous 120 BPM walk (6 cycles x 48 frames)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 288
    scene.render.fps = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15

    # Fast high-quality EEVEE configuration
    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "RenderEngineEEVEENext") else "BLENDER_EEVEE"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = 8

    # Atmospheric dark industrial world
    world = scene.world or bpy.data.worlds.new("ShowcaseWorld")
    scene.world = world
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.045, 0.055, 0.075, 1.0)
        bg.inputs[1].default_value = 1.0

    # Dedicated Corridor Lights + Brim-Clearance Face Light
    for lname in ("Key", "Fill", "FrontLight"):
        old_l = bpy.data.objects.get(lname)
        if old_l:
            bpy.data.objects.remove(old_l, do_unlink=True)

    def add_point(name: str, loc: Tuple[float, float, float], energy: float, color: Tuple[float, float, float], radius: float = 0.5) -> bpy.types.Object:
        ldata = bpy.data.lights.new(name, "POINT")
        ldata.energy = energy
        ldata.color = color
        ldata.shadow_soft_size = radius
        lobj = bpy.data.objects.new(name, ldata)
        scene.collection.objects.link(lobj)
        lobj.location = Vector(loc)
        return lobj

    # Tracked Hero Front Fill Light moving with Character so helmet brim never shadows the doll face
    hero_front_light = add_point("Hero_Front_Fill", (0.35, -1.65, 1.15), energy=95.0, color=(1.0, 0.96, 0.92), radius=0.8)
    hero_key_light = add_point("Hero_Key_Side", (-1.15, -1.25, 2.25), energy=140.0, color=(0.88, 0.95, 1.0), radius=0.6)
    reactor_light = add_point("Reactor_Core_Glow", (0.0, 3.0, 1.55), energy=260.0, color=(1.0, 0.40, 0.10), radius=0.6)
    alarm_light = add_point("Corridor_Alarm_Light", (-1.1, 0.2, 2.65), energy=120.0, color=(1.0, 0.10, 0.14), radius=0.5)
    rim_cyan_light = add_point("Corridor_Cyan_Rim", (1.0, 1.8, 2.10), energy=110.0, color=(0.15, 0.85, 1.0), radius=0.5)

    # Clear animations before keyframing clean 288-frame motion
    rig_obj.animation_data_clear()
    rig_obj.animation_data_create()

    # Track-To Target for smooth rock-solid camera framing
    cam_obj = scene.camera
    cam_obj.animation_data_clear()
    for c in list(cam_obj.constraints):
        cam_obj.constraints.remove(c)
    cam_obj.data.lens = 26.0

    cam_target = bpy.data.objects.new("CamTarget", None)
    cam_target.empty_display_type = "PLAIN_AXES"
    scene.collection.objects.link(cam_target)

    track = cam_obj.constraints.new("TRACK_TO")
    track.target = cam_target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Helper to compute Character World Y across frames 1..288 (advances forward along -Y from +0.65 to -1.15)
    def char_y_at(f: int) -> float:
        u = (f - 1) / 287.0
        return 0.65 - 1.80 * u

    # Keyframe bones & animated props across 288 frames
    cycle_frames = 48
    for frame in range(1, 289):
        u = (frame - 1) / 287.0
        cy = char_y_at(frame)
        rig_obj.location = (0.0, cy, 0.0)
        rig_obj.keyframe_insert(data_path="location", frame=frame)

        # Follow hero fill light slightly in front (-Y)
        hero_front_light.location = (0.45, cy - 1.75, 1.05)
        hero_front_light.keyframe_insert(data_path="location", frame=frame)
        hero_key_light.location = (-1.15, cy - 1.10, 2.30)
        hero_key_light.keyframe_insert(data_path="location", frame=frame)

        # Drone bob & flank position (stays clear outside character silhouette across all acts)
        t_cross = 1.0 / (1.0 + math.exp(-0.22 * (frame - 135)))
        drone_x = -0.88 + 1.82 * t_cross
        drone_z = 1.38 + 0.08 * math.cos(u * math.pi * 6.0)
        drone.location = (drone_x, cy - 0.28 + 0.12 * math.sin(u * math.pi * 2.0), drone_z)
        drone.rotation_euler = (0.0, 0.0, math.radians(-18.0 + 36.0 * u))
        drone.keyframe_insert(data_path="location", frame=frame)
        drone.keyframe_insert(data_path="rotation_euler", frame=frame)

        # Reactor Gyroscope Rotation + 120 BPM Pulsation (24 beats over 288 frames -> period = 12 frames)
        beat_phase = ((frame - 1) / 12.0) * math.pi
        pulse = (math.sin(beat_phase) ** 4)
        rotor_outer.rotation_euler = (u * math.pi * 6.0, u * math.pi * 4.0, u * math.pi * 2.0)
        rotor_inner.rotation_euler = (-u * math.pi * 8.0, u * math.pi * 6.0, -u * math.pi * 4.0)
        core_scale = 1.0 + 0.12 * pulse + 0.08 * u
        core_sphere.scale = (core_scale, core_scale, core_scale)
        rotor_outer.keyframe_insert(data_path="rotation_euler", frame=frame)
        rotor_inner.keyframe_insert(data_path="rotation_euler", frame=frame)
        core_sphere.keyframe_insert(data_path="scale", frame=frame)

        alarm_light.data.energy = 35.0 + 185.0 * pulse
        alarm_light.data.keyframe_insert(data_path="energy", frame=frame)
        reactor_light.data.energy = 210.0 + 190.0 * pulse
        reactor_light.data.keyframe_insert(data_path="energy", frame=frame)

        # Animate Emission Strengths on Materials
        bsdf_alarm = mat_alarm_red.node_tree.nodes.get("Principled BSDF")
        if bsdf_alarm and "Emission Strength" in bsdf_alarm.inputs:
            bsdf_alarm.inputs["Emission Strength"].default_value = 3.0 + 16.0 * pulse
            bsdf_alarm.inputs["Emission Strength"].keyframe_insert(data_path="default_value", frame=frame)

        # Walk locomotion cycle (repeating every 48 frames, keeping Head & Hero_FireAxe 100% rigid SE(3))
        phase_l = ((frame - 1) % cycle_frames) / cycle_frames * 2.0 * math.pi
        phase_r = phase_l + math.pi

        pb_root = rig_obj.pose.bones.get("Root")
        if pb_root:
            pb_root.location = (math.sin(phase_l) * 0.025, 0.0, -abs(math.sin(phase_l * 2.0)) * 0.022)
            pb_root.keyframe_insert(data_path="location", frame=frame)

        pb_spine = rig_obj.pose.bones.get("Spine")
        if pb_spine:
            pb_spine.rotation_euler = (math.radians(2.0), -math.sin(phase_l) * math.radians(2.2), -math.sin(phase_l) * math.radians(3.0))
            pb_spine.keyframe_insert(data_path="rotation_euler", frame=frame)

        pb_head = rig_obj.pose.bones.get("Head")
        if pb_head:
            pb_head.rotation_euler = (0.0, math.sin(phase_l) * math.radians(1.5), 0.0)
            pb_head.keyframe_insert(data_path="rotation_euler", frame=frame)

        for bname, pitch in [
            ("UpperLeg_L", math.sin(phase_l) * math.radians(22.0)),
            ("UpperLeg_R", math.sin(phase_r) * math.radians(22.0)),
            ("LowerLeg_L", max(0.0, -math.sin(phase_l)) * math.radians(28.0)),
            ("LowerLeg_R", max(0.0, -math.sin(phase_r)) * math.radians(28.0)),
        ]:
            pb = rig_obj.pose.bones.get(bname)
            if pb:
                pb.rotation_euler = (pitch, 0.0, 0.0)
                pb.keyframe_insert(data_path="rotation_euler", frame=frame)

        pb_arm_l = rig_obj.pose.bones.get("UpperArm_L")
        if pb_arm_l:
            pb_arm_l.rotation_euler = (math.sin(phase_l) * math.radians(12.0), math.radians(15.0), math.radians(-4.0))
            pb_arm_l.keyframe_insert(data_path="rotation_euler", frame=frame)
        pb_arm_r = rig_obj.pose.bones.get("UpperArm_R")
        if pb_arm_r:
            pb_arm_r.rotation_euler = (math.sin(phase_r) * math.radians(12.0), math.radians(-15.0), math.radians(4.0))
            pb_arm_r.keyframe_insert(data_path="rotation_euler", frame=frame)

    # 4-Act Camera Choreography Keyframes (Smooth Bezier interpolation, staying well inside corridor [-1.45..+1.45])
    cam_keys: List[Tuple[int, Tuple[float, float, float], Tuple[float, float, float]]] = [
        # Act 1 (F1..72): Full-body side-3/4 tracking -> Orbit entry (Match-cut from 2D stick figure)
        (1, (-1.28, char_y_at(1) - 2.65, 1.02), (0.0, char_y_at(1) + 0.10, 0.90)),
        (60, (-1.18, char_y_at(60) - 2.85, 1.02), (0.0, char_y_at(60) + 0.15, 0.92)),
        (72, (-1.05, char_y_at(72) - 3.05, 1.05), (0.0, char_y_at(72) + 0.20, 0.92)),
        # Act 2 (F73..144): Sweeping front hero full-body showcasing Fire Axe, boots, Drone & Corridor PBR
        (108, (-0.12, char_y_at(108) - 3.30, 1.08), (0.0, char_y_at(108) + 0.25, 0.94)),
        (144, (0.88, char_y_at(144) - 3.05, 1.06), (0.0, char_y_at(144) + 0.20, 0.94)),
        # Act 3 (F145..216): Shifted target LEFT (-0.55) so Character moves to screen-right, clearing top-left quadrant for Comms PiP
        (156, (0.78, char_y_at(156) - 3.15, 0.96), (-0.54, char_y_at(156) + 0.20, 0.98)),
        (216, (0.65, char_y_at(216) - 2.95, 0.98), (-0.52, char_y_at(216) + 0.20, 1.00)),
        # Act 4 (F217..288): Hero 3/4 Climax Dolly-In preserving full helmet crest + Axe + Thermal Reactor behind
        (228, (0.55, char_y_at(228) - 2.75, 1.02), (0.0, char_y_at(228) + 0.15, 1.04)),
        (288, (0.35, char_y_at(288) - 2.45, 1.04), (0.0, char_y_at(288) + 0.10, 1.05)),
    ]

    for kf, c_loc, t_loc in cam_keys:
        cam_obj.location = Vector(c_loc)
        cam_obj.keyframe_insert(data_path="location", frame=kf)
        cam_target.location = Vector(t_loc)
        cam_target.keyframe_insert(data_path="location", frame=kf)

    # Save master .blend and export .glb
    blend_out = OUT_DIR / "cross_dimension_rescue.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_out.resolve()))
    print(f"Saved master showcase scene: {blend_out}")

    glb_out = OUT_DIR / "cross_dimension_rescue.glb"
    bpy.ops.export_scene.gltf(
        filepath=str(glb_out.resolve()),
        export_format="GLB",
        use_selection=False,
        export_animations=True,
        export_skins=True,
        export_morph=False,
        export_lights=False,
        export_cameras=False,
    )
    print(f"Exported master showcase glTF: {glb_out}")

    if IS_PREVIEW:
        preview_frames = [68, 115, 175, 255]
        for f in preview_frames:
            scene.frame_set(f)
            scene.render.filepath = str((FRAMES_DIR / f"preview_{f:04d}.png").resolve())
            bpy.ops.render.render(write_still=True)
            print(f"Rendered preview frame {f}")
    else:
        scene.render.filepath = str((FRAMES_DIR / "frame_").resolve())
        print("Rendering 288 frames of 3D Sector 7 Corridor sequence (1280x720)...")
        bpy.ops.render.render(animation=True)
        print("Finished rendering all 288 3D frames!")


if __name__ == "__main__":
    setup_scene()
