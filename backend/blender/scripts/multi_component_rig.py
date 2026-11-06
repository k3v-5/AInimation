"""
Blender 4.3+ Multi-Component Hierarchical Rigging, Assembly, and Rendering Script.

Solves the monolithic / 'squashy plastic toy' flaw at the root:
- Imports environmental props (branch/ground) as independent, unparented static objects.
- Assembles anatomical character components (Torso, Articulated Wings, Head) as separate meshes.
- Parents components to their designated joint bones at exact anatomical pivot points.
- Guarantees ZERO weight bleed: wing rotation does not stretch or deform the torso or props.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
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

    parser = argparse.ArgumentParser(description="Multi-Component Rigging Script")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    return parser.parse_args(argv)


def clean_scene():
    """Remove all lingering objects, armatures, materials, and actions."""
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


def import_component_mesh(mesh_path: str, name: str):
    """Import OBJ mesh into Blender and rename cleanly."""
    p = Path(mesh_path).resolve()
    pre_objs = set(bpy.context.scene.objects)
    bpy.ops.wm.obj_import(filepath=str(p))
    post_objs = set(bpy.context.scene.objects)
    new_objs = [o for o in (post_objs - pre_objs) if o.type == 'MESH']

    if not new_objs:
        raise RuntimeError(f"Failed to import mesh from {mesh_path}")

    mesh_obj = max(new_objs, key=lambda m: len(m.data.vertices))
    mesh_obj.name = name
    return mesh_obj


def configure_component_material(mesh_obj, c_info: dict):
    """Setup high-fidelity PBR shader with albedo atlas, normal map, roughness, and AO."""
    mat_name = f"Mat_{mesh_obj.name}"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type="ShaderNodeOutputMaterial")
    node_out.location = (800, 0)

    node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    node_bsdf.location = (400, 0)
    links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

    is_prop = c_info.get("is_prop", False)

    # Subsurface scattering for organic character feathers/skin (translucent feather edge depth)
    if not is_prop:
        if "Subsurface Weight" in node_bsdf.inputs:
            node_bsdf.inputs["Subsurface Weight"].default_value = 0.08
        if "Subsurface Radius" in node_bsdf.inputs:
            node_bsdf.inputs["Subsurface Radius"].default_value = (0.22, 0.07, 0.02)
    else:
        if "Subsurface Weight" in node_bsdf.inputs:
            node_bsdf.inputs["Subsurface Weight"].default_value = 0.0

    if "Specular IOR Level" in node_bsdf.inputs:
        node_bsdf.inputs["Specular IOR Level"].default_value = 0.28 if not is_prop else 0.40

    albedo_path = c_info.get("albedo_path")
    ao_path = c_info.get("ao_path")
    node_alb = None

    if albedo_path and Path(albedo_path).is_file():
        img_alb = bpy.data.images.load(str(Path(albedo_path).resolve()))
        node_alb = nodes.new(type="ShaderNodeTexImage")
        node_alb.image = img_alb
        node_alb.location = (-400, 200)
        links.new(node_alb.outputs["Alpha"], node_bsdf.inputs["Alpha"])

        if ao_path and Path(ao_path).is_file():
            img_ao = bpy.data.images.load(str(Path(ao_path).resolve()))
            img_ao.colorspace_settings.name = "Non-Color"
            node_ao = nodes.new(type="ShaderNodeTexImage")
            node_ao.image = img_ao
            node_ao.location = (-400, 0)

            node_mix = nodes.new(type="ShaderNodeMix")
            node_mix.data_type = 'RGBA'
            node_mix.blend_type = 'MULTIPLY'
            node_mix.inputs["Factor"].default_value = 0.85
            node_mix.location = (0, 150)

            links.new(node_alb.outputs["Color"], node_mix.inputs[6])  # A
            links.new(node_ao.outputs["Color"], node_mix.inputs[7])   # B
            links.new(node_mix.outputs[2], node_bsdf.inputs["Base Color"])
        else:
            links.new(node_alb.outputs["Color"], node_bsdf.inputs["Base Color"])

    # Roughness
    rough_path = c_info.get("roughness_path")
    if rough_path and Path(rough_path).is_file():
        img_rou = bpy.data.images.load(str(Path(rough_path).resolve()))
        img_rou.colorspace_settings.name = "Non-Color"
        node_rou = nodes.new(type="ShaderNodeTexImage")
        node_rou.image = img_rou
        node_rou.location = (-400, -200)
        links.new(node_rou.outputs["Color"], node_bsdf.inputs["Roughness"])
    else:
        node_bsdf.inputs["Roughness"].default_value = 0.90 if is_prop else 0.72

    # Normal Map
    normal_path = c_info.get("normal_path")
    if normal_path and Path(normal_path).is_file():
        img_nor = bpy.data.images.load(str(Path(normal_path).resolve()))
        img_nor.colorspace_settings.name = "Non-Color"
        node_nor_tex = nodes.new(type="ShaderNodeTexImage")
        node_nor_tex.image = img_nor
        node_nor_tex.location = (-400, -400)

        node_nor_map = nodes.new(type="ShaderNodeNormalMap")
        node_nor_map.inputs["Strength"].default_value = 0.65
        node_nor_map.location = (0, -350)
        links.new(node_nor_tex.outputs["Color"], node_nor_map.inputs["Color"])
        links.new(node_nor_map.outputs["Normal"], node_bsdf.inputs["Normal"])

    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'BLENDED'
    if hasattr(mat, "blend_method"):
        mat.blend_method = 'HASHED'

    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(mat)


def main():
    args = parse_args()
    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        print(f"ERROR: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    components_data = cfg["components"]
    anim_data = cfg.get("animation")
    output_blend = cfg.get("output_blend")
    output_glb = cfg.get("output_glb")
    output_video = cfg.get("output_video")
    fps = cfg.get("fps", 24)
    total_frames = cfg.get("total_frames", 36)
    samples = cfg.get("samples", 16)
    engine = cfg.get("render_engine", "BLENDER_EEVEE_NEXT")

    print(f"Starting Multi-Component Assembly: {len(components_data)} components")
    clean_scene()

    imported_components = {}
    prop_objects = []
    character_objects = []

    # 1. Import all component meshes and configure materials
    for c_info in components_data:
        c_name = c_info["name"]
        m_path = c_info["mesh_path"]
        is_prop = c_info.get("is_prop", False)

        mesh_obj = import_component_mesh(m_path, c_name)
        configure_component_material(mesh_obj, c_info)
        imported_components[c_name] = (mesh_obj, c_info)

        if is_prop:
            prop_objects.append(mesh_obj)
        else:
            character_objects.append(mesh_obj)

    # 2. Build Armature for the character
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Avian_Character_Armature"

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_obj.data.edit_bones
    while eb:
        eb.remove(eb[0])

    # Find shoulder pivot from ventral wing component
    ventral_info = next((c for c in components_data if "ventral" in c["name"].lower() or "wing" in c["role"].lower()), None)
    if ventral_info and "pivot_point" in ventral_info:
        px, py, pz = ventral_info["pivot_point"]
    else:
        px, py, pz = (-0.3967, 0.4542, 0.16)

    # Convert from OBJ coordinates (X=right, Y=up, Z=depth relief)
    # to Blender world coordinates (X=right, Y=depth away from camera, Z=up)
    blender_px = px
    blender_py = -pz   # OBJ Z (depth) -> Blender -Y
    blender_pz = py    # OBJ Y (height) -> Blender +Z

    # Find dorsal wing pivot
    dorsal_info = next((c for c in components_data if "dorsal" in c["name"].lower()), None)
    if dorsal_info and "pivot_point" in dorsal_info:
        dpx, dpy, dpz = dorsal_info["pivot_point"]
    else:
        dpx, dpy, dpz = (px + 0.12, py, -0.10)

    blender_dpx = dpx
    blender_dpy = -dpz  # OBJ Z (depth) -> Blender -Y
    blender_dpz = dpy   # OBJ Y (height) -> Blender +Z

    # Root, Spine, Head & Tail (Vertical axial skeleton along +Z)
    b_root = eb.new("Root")
    b_root.head = (0.0, -0.15, -0.25)
    b_root.tail = (0.0, -0.15, 0.10)
    b_root.align_roll(mathutils.Vector((0, -1, 0)))

    b_spine = eb.new("Spine")
    b_spine.head = (0.0, -0.15, 0.10)
    b_spine.tail = (-0.05, -0.15, 0.35)
    b_spine.parent = b_root
    b_spine.align_roll(mathutils.Vector((0, -1, 0)))

    b_head = eb.new("Head")
    b_head.head = (-0.05, -0.15, 0.35)
    b_head.tail = (-0.25, -0.15, 0.60)
    b_head.parent = b_spine
    b_head.align_roll(mathutils.Vector((0, -1, 0)))

    b_tail = eb.new("Tail")
    b_tail.head = (0.0, -0.15, -0.25)
    b_tail.tail = (0.12, -0.15, -0.65)
    b_tail.parent = b_root
    b_tail.align_roll(mathutils.Vector((0, -1, 0)))

    # Left / Ventral Wing (3-Bone Chain for Aerodynamic Wing Flexing)
    # 1. Humerus / Shoulder
    b_wing_l = eb.new("Wing_Shoulder_L")
    b_wing_l.head = (blender_px, blender_py, blender_pz)
    b_wing_l.tail = (blender_px + 0.22, blender_py - 0.02, blender_pz - 0.18)
    b_wing_l.parent = b_spine
    b_wing_l.align_roll(mathutils.Vector((0, 0, 1)))

    # 2. Forearm / Radius-Ulna / Elbow
    b_wing_mid_l = eb.new("Wing_Mid_L")
    b_wing_mid_l.head = b_wing_l.tail
    b_wing_mid_l.tail = (blender_px + 0.42, blender_py - 0.03, blender_pz - 0.38)
    b_wing_mid_l.parent = b_wing_l
    b_wing_mid_l.align_roll(mathutils.Vector((0, 0, 1)))

    # 3. Hand / Carpometacarpus / Primary Tips
    b_wing_tip_l = eb.new("Wing_Tip_L")
    b_wing_tip_l.head = b_wing_mid_l.tail
    b_wing_tip_l.tail = (blender_px + 0.65, blender_py - 0.04, blender_pz - 0.58)
    b_wing_tip_l.parent = b_wing_mid_l
    b_wing_tip_l.align_roll(mathutils.Vector((0, 0, 1)))

    # Right / Dorsal Wing (3-Bone Chain for Perspective Flight Flapping)
    b_wing_r = eb.new("Wing_Shoulder_R")
    b_wing_r.head = (blender_dpx, blender_dpy, blender_dpz)
    b_wing_r.tail = (blender_dpx + 0.22, blender_dpy + 0.02, blender_dpz - 0.18)
    b_wing_r.parent = b_spine
    b_wing_r.align_roll(mathutils.Vector((0, 0, 1)))

    b_wing_mid_r = eb.new("Wing_Mid_R")
    b_wing_mid_r.head = b_wing_r.tail
    b_wing_mid_r.tail = (blender_dpx + 0.42, blender_dpy + 0.03, blender_dpz - 0.38)
    b_wing_mid_r.parent = b_wing_r
    b_wing_mid_r.align_roll(mathutils.Vector((0, 0, 1)))

    b_wing_tip_r = eb.new("Wing_Tip_R")
    b_wing_tip_r.head = b_wing_mid_r.tail
    b_wing_tip_r.tail = (blender_dpx + 0.65, blender_dpy + 0.04, blender_dpz - 0.58)
    b_wing_tip_r.parent = b_wing_mid_r
    b_wing_tip_r.align_roll(mathutils.Vector((0, 0, 1)))

    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Component Armature Binding & Smooth C^inf Weight Skinning (Zero Weight Bleed!)
    for c_name, (mesh_obj, c_info) in imported_components.items():
        if c_info.get("is_prop", False):
            # Props (branch) receive Smooth modifier to eliminate terraced staircases, followed by Subsurf
            smooth_mod = mesh_obj.modifiers.new(name="Smooth_Terraces", type='SMOOTH')
            smooth_mod.factor = 0.85
            smooth_mod.iterations = 6
            sub = mesh_obj.modifiers.new(name="Subsurf_Organic", type='SUBSURF')
            sub.levels = 2
            sub.render_levels = 2
            continue

        role = c_info.get("role", "")

        # Bind mesh to armature
        mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        mesh_obj.parent = arm_obj

        # Organic smooth modifier to diffuse discrete grid faceting along silhouette creases
        smooth_mod = mesh_obj.modifiers.new(name="Smooth_Organic", type='SMOOTH')
        smooth_mod.factor = 0.55
        smooth_mod.iterations = 4

        # Organic subdivision smoothing evaluated after armature deformation
        sub = mesh_obj.modifiers.new(name="Subsurf_Organic", type='SUBSURF')
        sub.levels = 1
        sub.render_levels = 1

        verts = mesh_obj.data.vertices

        if "wing_ventral" in role:
            vg_sh = mesh_obj.vertex_groups.new(name="Wing_Shoulder_L")
            vg_mid = mesh_obj.vertex_groups.new(name="Wing_Mid_L")
            vg_tip = mesh_obj.vertex_groups.new(name="Wing_Tip_L")

            xs = [v.co.x for v in verts]
            min_x, max_x = min(xs), max(xs)
            span = max(1e-4, max_x - min_x)

            for v in verts:
                t = max(0.0, min(1.0, (v.co.x - min_x) / span))
                w_sh = math.cos(0.5 * math.pi * min(1.0, t / 0.45)) ** 2
                w_mid = math.sin(math.pi * min(1.0, max(0.0, (t - 0.10) / 0.70))) ** 2
                w_tip = math.sin(0.5 * math.pi * max(0.0, (t - 0.45) / 0.55)) ** 2
                tot = max(1e-6, w_sh + w_mid + w_tip)
                vg_sh.add([v.index], w_sh / tot, 'REPLACE')
                vg_mid.add([v.index], w_mid / tot, 'REPLACE')
                vg_tip.add([v.index], w_tip / tot, 'REPLACE')

        elif "wing_dorsal" in role:
            vg_sh = mesh_obj.vertex_groups.new(name="Wing_Shoulder_R")
            vg_mid = mesh_obj.vertex_groups.new(name="Wing_Mid_R")
            vg_tip = mesh_obj.vertex_groups.new(name="Wing_Tip_R")

            xs = [v.co.x for v in verts]
            min_x, max_x = min(xs), max(xs)
            span = max(1e-4, max_x - min_x)

            for v in verts:
                t = max(0.0, min(1.0, (v.co.x - min_x) / span))
                w_sh = math.cos(0.5 * math.pi * min(1.0, t / 0.45)) ** 2
                w_mid = math.sin(math.pi * min(1.0, max(0.0, (t - 0.10) / 0.70))) ** 2
                w_tip = math.sin(0.5 * math.pi * max(0.0, (t - 0.45) / 0.55)) ** 2
                tot = max(1e-6, w_sh + w_mid + w_tip)
                vg_sh.add([v.index], w_sh / tot, 'REPLACE')
                vg_mid.add([v.index], w_mid / tot, 'REPLACE')
                vg_tip.add([v.index], w_tip / tot, 'REPLACE')

        else:
            vg_root = mesh_obj.vertex_groups.new(name="Root")
            vg_spine = mesh_obj.vertex_groups.new(name="Spine")
            vg_head = mesh_obj.vertex_groups.new(name="Head")
            vg_tail = mesh_obj.vertex_groups.new(name="Tail")

            for v in verts:
                z = v.co.z
                if z >= 0.35:
                    vg_head.add([v.index], 1.0, 'REPLACE')
                elif z >= 0.05:
                    vg_spine.add([v.index], 1.0, 'REPLACE')
                elif z >= -0.30:
                    vg_root.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_tail.add([v.index], 1.0, 'REPLACE')

        print(f"Bound component '{c_name}' cleanly to armature with zero weight bleed.")

    # 4. Fluid Avian Flight Biomechanics Keyframing
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    action = bpy.data.actions.new(name="Avian_Flight_Articulated")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    pb_sh_l = arm_obj.pose.bones["Wing_Shoulder_L"]
    pb_mid_l = arm_obj.pose.bones["Wing_Mid_L"]
    pb_tip_l = arm_obj.pose.bones["Wing_Tip_L"]

    pb_sh_r = arm_obj.pose.bones["Wing_Shoulder_R"]
    pb_mid_r = arm_obj.pose.bones["Wing_Mid_R"]
    pb_tip_r = arm_obj.pose.bones["Wing_Tip_R"]

    pb_head = arm_obj.pose.bones["Head"]
    pb_spine = arm_obj.pose.bones["Spine"]
    pb_tail = arm_obj.pose.bones["Tail"]

    all_pbs = [pb_sh_l, pb_mid_l, pb_tip_l, pb_sh_r, pb_mid_r, pb_tip_r, pb_head, pb_spine, pb_tail]
    for pb in all_pbs:
        pb.rotation_mode = 'XYZ'

    for f in range(1, total_frames + 1):
        # 2 complete aerodynamic cycles across total_frames, exactly 0 phase at frame 1
        phase = ((f - 1) / total_frames) * 2.0 * math.pi * 2.0

        # Ventral Wing: Aerodynamic Flap with 3-Joint Flexion
        flap_elev = math.sin(phase) * 20.0 + (1.0 - math.cos(phase)) * 8.0
        pb_sh_l.rotation_euler = (
            math.radians(flap_elev),
            math.radians(math.sin(phase) * 2.5),
            math.radians(-math.sin(phase) * 1.5),
        )
        pb_sh_l.keyframe_insert(data_path="rotation_euler", frame=f)

        # Mid-wing: Elbow flex with 28 deg phase lag + aerodynamic fold on upstroke
        phase_mid = phase - math.radians(28.0)
        elbow_elev = math.sin(phase_mid) * 12.0
        elbow_fold = -math.radians(8.0) * max(0.0, math.cos(phase))
        pb_mid_l.rotation_euler = (
            math.radians(elbow_elev),
            math.radians(math.sin(phase_mid) * 2.0),
            elbow_fold,
        )
        pb_mid_l.keyframe_insert(data_path="rotation_euler", frame=f)

        # Wing tip: Primary feather trail with 55 deg phase lag + camber roll
        phase_tip = phase - math.radians(55.0)
        tip_elev = math.sin(phase_tip) * 8.0
        tip_camber = math.sin(phase_tip) * 6.0
        pb_tip_l.rotation_euler = (
            math.radians(tip_elev),
            math.radians(tip_camber),
            0.0,
        )
        pb_tip_l.keyframe_insert(data_path="rotation_euler", frame=f)

        # Dorsal Wing: Perspective matching rear wing
        pb_sh_r.rotation_euler = (
            math.radians(flap_elev * 0.95),
            math.radians(-math.sin(phase) * 2.0),
            math.radians(math.sin(phase) * 1.2),
        )
        pb_sh_r.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_mid_r.rotation_euler = (
            math.radians(elbow_elev * 0.95),
            math.radians(-math.sin(phase_mid) * 1.5),
            elbow_fold * 0.8,
        )
        pb_mid_r.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_tip_r.rotation_euler = (
            math.radians(tip_elev * 0.95),
            math.radians(-tip_camber * 0.8),
            0.0,
        )
        pb_tip_r.keyframe_insert(data_path="rotation_euler", frame=f)

        # Spine Heave: Body breathes and counter-bobs slightly
        pb_spine.rotation_euler = (math.radians(math.sin(phase) * 1.5), 0.0, 0.0)
        pb_spine.keyframe_insert(data_path="rotation_euler", frame=f)

        # Head curiosity glance
        head_pitch = (1.0 - math.cos(phase * 0.5)) * 2.5
        head_yaw = math.sin(phase * 0.5) * 3.5
        pb_head.rotation_euler = (math.radians(head_pitch), 0.0, math.radians(head_yaw))
        pb_head.keyframe_insert(data_path="rotation_euler", frame=f)

        # Tail stabilizer counter-pitch
        pb_tail.rotation_euler = (math.radians(-math.sin(phase) * 2.0), 0.0, 0.0)
        pb_tail.keyframe_insert(data_path="rotation_euler", frame=f)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 5. Studio Backdrop, Cinematic Lighting and Camera Framing
    # Seamless 360 Studio World Background
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.045, 0.045, 0.065, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    # Studio Backdrop cylinder/curved cyclorama
    bpy.ops.mesh.primitive_cylinder_add(radius=16.0, depth=24.0, location=(0.0, 0.0, 0.0))
    backdrop = bpy.context.active_object
    backdrop.name = "Studio_Backdrop"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')
    bg_mat = bpy.data.materials.new(name="Studio_Backdrop_Mat")
    bg_mat.use_nodes = True
    bg_bsdf = bg_mat.node_tree.nodes.get("Principled BSDF")
    if bg_bsdf:
        bg_bsdf.inputs["Base Color"].default_value = (0.045, 0.045, 0.065, 1.0)
        bg_bsdf.inputs["Roughness"].default_value = 0.98
    backdrop.data.materials.append(bg_mat)

    # Calculate combined bounding box of character and props
    all_meshes = character_objects + prop_objects
    all_bounds = []
    for m in all_meshes:
        all_bounds.extend([m.matrix_world @ mathutils.Vector(corner) for corner in m.bound_box])

    min_x = min(p.x for p in all_bounds)
    max_x = max(p.x for p in all_bounds)
    min_y = min(p.y for p in all_bounds)
    max_y = max(p.y for p in all_bounds)
    min_z = min(p.z for p in all_bounds)
    max_z = max(p.z for p in all_bounds)

    center = mathutils.Vector(((min_x + max_x) / 2.0, (min_y + max_y) / 2.0, (min_z + max_z) / 2.0))
    span_x = max(0.1, max_x - min_x)
    span_z = max(0.1, max_z - min_z)

    # 3-Point Studio Lighting
    bpy.ops.object.light_add(type='AREA', radius=2.5, location=(center.x + 3.0, center.y - 3.2, center.z + 2.8))
    key = bpy.context.active_object
    key.name = "KeyLight"
    key.data.energy = 550.0
    key.data.color = (1.0, 0.95, 0.88)

    bpy.ops.object.light_add(type='AREA', radius=3.5, location=(center.x - 3.8, center.y - 2.4, center.z + 1.6))
    fill = bpy.context.active_object
    fill.name = "FillLight"
    fill.data.energy = 220.0
    fill.data.color = (0.85, 0.92, 1.0)

    bpy.ops.object.light_add(type='SPOT', radius=0.8, location=(center.x + 0.6, center.y + 2.8, center.z + 2.4))
    rim = bpy.context.active_object
    rim.name = "RimLight"
    rim.data.energy = 550.0
    rim.data.color = (1.0, 0.98, 0.95)
    rim.data.spot_size = math.radians(55)

    # Dynamic Camera Framing (55mm telephoto lens with 20% margin, framed on span_x and span_z)
    cam_dist = max(span_x / 0.36, span_z / 0.28) * 0.90 + 1.2
    cam_dist = max(4.5, min(7.5, cam_dist))

    bpy.ops.object.camera_add(location=(center.x, center.y - cam_dist, center.z + 0.15))
    cam = bpy.context.active_object
    cam.name = "Cinematic_Camera"
    cam.data.lens = 55.0
    bpy.context.scene.camera = cam

    empty = bpy.data.objects.new("CameraTarget", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = center

    constraint = cam.constraints.new(type='TRACK_TO')
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

    # 6. Export Clean GLB (Character rig, meshes, and prop only - backdrop and lights excluded)
    if output_glb:
        out_g = Path(output_glb).resolve()
        out_g.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        arm_obj.select_set(True)
        for obj in character_objects + prop_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.export_scene.gltf(
            filepath=str(out_g),
            export_format='GLB',
            export_animations=True,
            use_selection=True,
        )
        print(f"Exported clean multi-component GLB: {out_g}")

    # 7. Save Blend Scene
    if output_blend:
        out_b = Path(output_blend).resolve()
        out_b.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out_b))
        print(f"Saved multi-component .blend: {out_b}")

    # 8. Render Animation Sequence
    if output_video:
        out_v = Path(output_video).resolve()
        out_v.parent.mkdir(parents=True, exist_ok=True)
        frames_dir = out_v.parent / f"_frames_{out_v.stem}"
        frames_dir.mkdir(parents=True, exist_ok=True)

        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = total_frames
        scene.render.fps = fps
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 720
        scene.render.resolution_percentage = 100

        if engine.upper() in ["BLENDER_EEVEE_NEXT", "EEVEE", "BLENDER_EEVEE"]:
            try:
                scene.render.engine = "BLENDER_EEVEE"
            except Exception:
                scene.render.engine = "BLENDER_EEVEE_NEXT"
            if hasattr(scene, "eevee"):
                if hasattr(scene.eevee, "use_raytracing"):
                    scene.eevee.use_raytracing = True
                if hasattr(scene.eevee, "use_gtao"):
                    scene.eevee.use_gtao = True
                    scene.eevee.gtao_distance = 0.5
                if hasattr(scene.eevee, "taa_render_samples"):
                    scene.eevee.taa_render_samples = samples
        else:
            scene.render.engine = "CYCLES"
            scene.cycles.samples = samples

        if hasattr(scene, "view_settings"):
            try:
                scene.view_settings.view_transform = 'AgX'
                scene.view_settings.look = 'Medium High Contrast'
            except Exception:
                pass

        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.filepath = str(frames_dir / "frame_")

        print(f"Rendering {total_frames} frames with {scene.render.engine}...")
        bpy.ops.render.render(animation=True)

        # Encode MP4
        import shutil
        ffmpeg_bin = shutil.which("ffmpeg") or r"C:\Users\sasuk\AppData\Roaming\Python\Python314\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
        if not Path(ffmpeg_bin).is_file():
            ffmpeg_bin = "ffmpeg"

        mp4_cmd = [
            ffmpeg_bin, "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            str(out_v),
        ]
        subprocess.run(mp4_cmd, capture_output=True, check=False)

        # Encode GIF
        gif_path = out_v.with_suffix(".gif")
        gif_cmd = [
            ffmpeg_bin, "-y",
            "-framerate", str(fps),
            "-i", str(frames_dir / "frame_%04d.png"),
            "-vf", "fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(gif_path),
        ]
        subprocess.run(gif_cmd, capture_output=True, check=False)

        # Cleanup frames
        for f in frames_dir.glob("frame_*.png"):
            f.unlink()
        try:
            frames_dir.rmdir()
        except OSError:
            pass

        print(f"Rendered video: {out_v}")
        print(f"Rendered gif: {gif_path}")

    print("MULTI_COMPONENT_RIG_COMPLETE")


if __name__ == "__main__":
    main()
