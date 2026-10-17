"""
Cinematic Multi-Angle, Turntable, and Idle Animation Renderer for Anime Tactical Bipedal Model.
Renders high-definition studio stills from 7 canonical camera angles, 360-degree orbit turntable,
and the tactical idle breathing animation cycle with EEVEE Next PBR lighting.
"""

from __future__ import annotations

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


def assemble_and_rig_tactical_model(
    components_dir: str,
    output_blend: str,
    output_glb: str,
    total_frames: int = 48,
) -> None:
    comp_d = Path(components_dir).resolve()
    out_blend = Path(output_blend).resolve()
    out_blend.parent.mkdir(parents=True, exist_ok=True)
    out_glb = Path(output_glb).resolve()
    out_glb.parent.mkdir(parents=True, exist_ok=True)

    # 1. Clean scene
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.armatures):
        bpy.data.armatures.remove(a, do_unlink=True)
    for ac in list(bpy.data.actions):
        bpy.data.actions.remove(ac, do_unlink=True)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m, do_unlink=True)

    # 2. Import 7 True 360-Degree Lofted Anatomical Components
    components = [
        {"name": "Subject_Body", "stem": "subject_body", "role": "humanoid"},
        {"name": "Subject_Head", "stem": "subject_head", "role": "head"},
        {"name": "Subject_Hair", "stem": "subject_hair", "role": "hair"},
        {"name": "Subject_Arm_R", "stem": "subject_arm_r", "role": "arm_r"},
        {"name": "Subject_Arm_L", "stem": "subject_arm_l", "role": "arm_l"},
        {"name": "Subject_Leg_R", "stem": "subject_leg_r", "role": "leg_r"},
        {"name": "Subject_Leg_L", "stem": "subject_leg_l", "role": "leg_l"},
    ]

    imported = {}
    for c in components:
        obj_file = comp_d / f"{c['stem']}.obj"
        if not obj_file.is_file():
            raise FileNotFoundError(f"Missing component mesh: {obj_file}")
        pre = set(bpy.context.scene.objects)
        bpy.ops.wm.obj_import(filepath=str(obj_file))
        post = set(bpy.context.scene.objects)
        mesh_obj = [o for o in (post - pre) if o.type == 'MESH'][0]
        mesh_obj.name = c["name"]

        # Enable clean smooth normal interpolation on the 360-degree quad rings
        for poly in mesh_obj.data.polygons:
            poly.use_smooth = True

        # Setup PBR material
        mat = bpy.data.materials.new(name=f"Mat_{c['name']}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        node_out = nodes.new(type="ShaderNodeOutputMaterial")
        node_out.location = (800, 0)
        node_bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        node_bsdf.location = (400, 0)
        links.new(node_bsdf.outputs["BSDF"], node_out.inputs["Surface"])

        if "Subsurface Weight" in node_bsdf.inputs:
            node_bsdf.inputs["Subsurface Weight"].default_value = 0.05
        if "Subsurface Radius" in node_bsdf.inputs:
            node_bsdf.inputs["Subsurface Radius"].default_value = (0.20, 0.08, 0.03)
        if "Specular IOR Level" in node_bsdf.inputs:
            node_bsdf.inputs["Specular IOR Level"].default_value = 0.28

        alb_f = comp_d / f"{c['stem']}_albedo.png"
        ao_f = comp_d / f"{c['stem']}_ao.png"
        rou_f = comp_d / f"{c['stem']}_roughness.png"
        nor_f = comp_d / f"{c['stem']}_normal.png"

        if alb_f.is_file():
            img_alb = bpy.data.images.load(str(alb_f))
            node_alb = nodes.new(type="ShaderNodeTexImage")
            node_alb.image = img_alb
            node_alb.location = (-400, 200)
            links.new(node_alb.outputs["Alpha"], node_bsdf.inputs["Alpha"])

            if ao_f.is_file():
                img_ao = bpy.data.images.load(str(ao_f))
                img_ao.colorspace_settings.name = "Non-Color"
                node_ao = nodes.new(type="ShaderNodeTexImage")
                node_ao.image = img_ao
                node_ao.location = (-400, 0)

                node_mix = nodes.new(type="ShaderNodeMix")
                node_mix.data_type = 'RGBA'
                node_mix.blend_type = 'MULTIPLY'
                node_mix.inputs[0].default_value = 0.70
                node_mix.location = (0, 150)
                links.new(node_alb.outputs["Color"], node_mix.inputs[6])
                links.new(node_ao.outputs["Color"], node_mix.inputs[7])
                links.new(node_mix.outputs[2], node_bsdf.inputs["Base Color"])
            else:
                links.new(node_alb.outputs["Color"], node_bsdf.inputs["Base Color"])

        if rou_f.is_file():
            img_rou = bpy.data.images.load(str(rou_f))
            img_rou.colorspace_settings.name = "Non-Color"
            node_rou = nodes.new(type="ShaderNodeTexImage")
            node_rou.image = img_rou
            node_rou.location = (-400, -200)
            links.new(node_rou.outputs["Color"], node_bsdf.inputs["Roughness"])

        if nor_f.is_file():
            img_nor = bpy.data.images.load(str(nor_f))
            img_nor.colorspace_settings.name = "Non-Color"
            node_nor = nodes.new(type="ShaderNodeTexImage")
            node_nor.image = img_nor
            node_nor.location = (-400, -400)
            node_nmap = nodes.new(type="ShaderNodeNormalMap")
            node_nmap.inputs["Strength"].default_value = 0.45
            node_nmap.location = (0, -300)
            links.new(node_nor.outputs["Color"], node_nmap.inputs["Color"])
            links.new(node_nmap.outputs["Normal"], node_bsdf.inputs["Normal"])

        mesh_obj.data.materials.clear()
        mesh_obj.data.materials.append(mat)
        imported[c["name"]] = mesh_obj

    # 3. Build Armature
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "Tactical_Bipedal_Armature"

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_obj.data.edit_bones
    while eb:
        eb.remove(eb[0])

    # Axial Skeleton along +Z
    b_root = eb.new("Root")
    b_root.head = (0.0, 0.0, -0.05)
    b_root.tail = (0.0, 0.0, 0.25)
    b_root.align_roll(mathutils.Vector((0, -1, 0)))

    b_spine = eb.new("Spine")
    b_spine.head = (0.0, 0.0, 0.25)
    b_spine.tail = (0.0, -0.01, 0.58)
    b_spine.parent = b_root
    b_spine.align_roll(mathutils.Vector((0, -1, 0)))

    b_neck = eb.new("Neck")
    b_neck.head = (0.0, -0.01, 0.58)
    b_neck.tail = (0.0, -0.01, 0.71)
    b_neck.parent = b_spine
    b_neck.align_roll(mathutils.Vector((0, -1, 0)))

    b_head = eb.new("Head")
    b_head.head = (0.0, -0.01, 0.71)
    b_head.tail = (0.0, -0.01, 0.96)
    b_head.parent = b_neck
    b_head.align_roll(mathutils.Vector((0, -1, 0)))

    # Legs
    b_leg_l = eb.new("Leg_L")
    b_leg_l.head = (0.12, 0.0, -0.05)
    b_leg_l.tail = (0.12, 0.0, -0.45)
    b_leg_l.parent = b_root
    b_leg_l.align_roll(mathutils.Vector((0, -1, 0)))

    b_shin_l = eb.new("Shin_L")
    b_shin_l.head = (0.12, 0.0, -0.45)
    b_shin_l.tail = (0.12, -0.02, -0.95)
    b_shin_l.parent = b_leg_l
    b_shin_l.align_roll(mathutils.Vector((0, -1, 0)))

    b_leg_r = eb.new("Leg_R")
    b_leg_r.head = (-0.12, 0.0, -0.05)
    b_leg_r.tail = (-0.12, 0.0, -0.45)
    b_leg_r.parent = b_root
    b_leg_r.align_roll(mathutils.Vector((0, -1, 0)))

    b_shin_r = eb.new("Shin_R")
    b_shin_r.head = (-0.12, 0.0, -0.45)
    b_shin_r.tail = (-0.12, -0.02, -0.95)
    b_shin_r.parent = b_leg_r
    b_shin_r.align_roll(mathutils.Vector((0, -1, 0)))

    # Right Arm (screen-left)
    b_sh_r = eb.new("Shoulder_R")
    b_sh_r.head = (-0.163, -0.02, 0.549)
    b_sh_r.tail = (-0.20, -0.01, 0.22)
    b_sh_r.parent = b_spine
    b_sh_r.align_roll(mathutils.Vector((0, 0, 1)))

    b_fa_r = eb.new("Forearm_R")
    b_fa_r.head = b_sh_r.tail
    b_fa_r.tail = (-0.21, 0.0, -0.18)
    b_fa_r.parent = b_sh_r
    b_fa_r.align_roll(mathutils.Vector((0, 0, 1)))

    # Left Arm (screen-right)
    b_sh_l = eb.new("Shoulder_L")
    b_sh_l.head = (0.175, -0.02, 0.549)
    b_sh_l.tail = (0.22, -0.01, 0.22)
    b_sh_l.parent = b_spine
    b_sh_l.align_roll(mathutils.Vector((0, 0, 1)))

    b_fa_l = eb.new("Forearm_L")
    b_fa_l.head = b_sh_l.tail
    b_fa_l.tail = (0.23, 0.0, -0.18)
    b_fa_l.parent = b_sh_l
    b_fa_l.align_roll(mathutils.Vector((0, 0, 1)))

    bpy.ops.object.mode_set(mode='OBJECT')

    # 4. Skinning & Modifiers (Zero Weight Bleed across the 7 Lofted Components!)
    for name, m_obj in imported.items():
        mod = m_obj.modifiers.new(name="Armature", type='ARMATURE')
        mod.object = arm_obj
        m_obj.parent = arm_obj

        verts = m_obj.data.vertices
        if name == "Subject_Body":
            vg_root = m_obj.vertex_groups.new(name="Root")
            vg_spine = m_obj.vertex_groups.new(name="Spine")
            for v in verts:
                if v.co.z >= 0.25:
                    vg_spine.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_root.add([v.index], 1.0, 'REPLACE')

        elif name in ["Subject_Head", "Subject_Hair"]:
            vg_neck = m_obj.vertex_groups.new(name="Neck")
            vg_head = m_obj.vertex_groups.new(name="Head")
            for v in verts:
                if v.co.z >= 0.69:
                    vg_head.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_neck.add([v.index], 1.0, 'REPLACE')

        elif name == "Subject_Arm_R":
            vg_sh = m_obj.vertex_groups.new(name="Shoulder_R")
            vg_fa = m_obj.vertex_groups.new(name="Forearm_R")
            for v in verts:
                if v.co.z >= 0.22:
                    vg_sh.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_fa.add([v.index], 1.0, 'REPLACE')

        elif name == "Subject_Arm_L":
            vg_sh = m_obj.vertex_groups.new(name="Shoulder_L")
            vg_fa = m_obj.vertex_groups.new(name="Forearm_L")
            for v in verts:
                if v.co.z >= 0.22:
                    vg_sh.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_fa.add([v.index], 1.0, 'REPLACE')

        elif name == "Subject_Leg_R":
            vg_thigh = m_obj.vertex_groups.new(name="Leg_R")
            vg_shin = m_obj.vertex_groups.new(name="Shin_R")
            for v in verts:
                if v.co.z >= -0.45:
                    vg_thigh.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_shin.add([v.index], 1.0, 'REPLACE')

        elif name == "Subject_Leg_L":
            vg_thigh = m_obj.vertex_groups.new(name="Leg_L")
            vg_shin = m_obj.vertex_groups.new(name="Shin_L")
            for v in verts:
                if v.co.z >= -0.45:
                    vg_thigh.add([v.index], 1.0, 'REPLACE')
                else:
                    vg_shin.add([v.index], 1.0, 'REPLACE')

    # 5. Keyframe Tactical Idle Breathing Animation
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')

    action = bpy.data.actions.new(name="Tactical_Idle_Breathing")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    pb_spine = arm_obj.pose.bones["Spine"]
    pb_neck = arm_obj.pose.bones["Neck"]
    pb_head = arm_obj.pose.bones["Head"]
    pb_sh_r = arm_obj.pose.bones["Shoulder_R"]
    pb_sh_l = arm_obj.pose.bones["Shoulder_L"]
    pb_fa_r = arm_obj.pose.bones["Forearm_R"]
    pb_fa_l = arm_obj.pose.bones["Forearm_L"]

    for pb in [pb_spine, pb_neck, pb_head, pb_sh_r, pb_sh_l, pb_fa_r, pb_fa_l]:
        pb.rotation_mode = 'XYZ'

    for f in range(1, total_frames + 1):
        phase = ((f - 1) / total_frames) * 2.0 * math.pi
        pb_spine.rotation_euler = (math.radians(math.sin(phase) * 1.2), 0.0, 0.0)
        pb_spine.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_neck.rotation_euler = (math.radians(-math.sin(phase) * 0.6), 0.0, 0.0)
        pb_neck.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_head.rotation_euler = (math.radians(-math.sin(phase) * 0.5), 0.0, 0.0)
        pb_head.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_sh_r.rotation_euler = (
            math.radians(math.sin(phase) * 0.8),
            math.radians(math.cos(phase) * 0.5),
            0.0,
        )
        pb_sh_r.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_sh_l.rotation_euler = (
            math.radians(math.sin(phase) * 0.8),
            math.radians(-math.cos(phase) * 0.5),
            0.0,
        )
        pb_sh_l.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_fa_r.rotation_euler = (math.radians(math.sin(phase - 0.4) * 0.4), 0.0, 0.0)
        pb_fa_r.keyframe_insert(data_path="rotation_euler", frame=f)

        pb_fa_l.rotation_euler = (math.radians(math.sin(phase - 0.4) * 0.4), 0.0, 0.0)
        pb_fa_l.keyframe_insert(data_path="rotation_euler", frame=f)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Export clean standard GLB
    bpy.ops.export_scene.gltf(
        filepath=str(out_glb),
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_animations=True,
    )
    print(f"Exported standard articulated GLB to: {out_glb}")

    # Save to blend
    bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
    print(f"Saved tactical bipedal scene to: {out_blend}")


def render_tactical_model(
    blend_path: str,
    output_dir: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    samples: int = 12,
    stills_only: bool = False,
    animations_only: bool = False,
) -> None:
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    out_d = Path(output_dir).resolve()
    out_d.mkdir(parents=True, exist_ok=True)

    # 1. Configure Memory-Safe EEVEE Next PBR Settings
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'

    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "use_raytracing"):
            scene.eevee.use_raytracing = False
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 0.4
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = samples

    # 2. Studio World Background (Deep Slate Blue Cyclorama)
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Studio_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.050, 0.055, 0.080, 1.0)
        bg_node.inputs["Strength"].default_value = 1.2

    # Remove any old lights to avoid clutter
    for obj in list(scene.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # 3. Find character bounds
    char_objs = [o for o in scene.objects if o.type == 'MESH']
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
    span_z = max(0.1, max_z - min_z)
    span_x = max(0.1, max_x - min_x)

    # Camera target slightly above pelvic center towards chest/face
    target_pos = mathutils.Vector((center.x, center.y, center.z + 0.10 * span_z))

    # 4. Target Empty & Professional 360-Degree Studio Lighting
    target = scene.objects.get("CameraTarget")
    if not target:
        target = bpy.data.objects.new("CameraTarget", None)
        scene.collection.objects.link(target)
    target.location = target_pos

    def _point_at_target(obj: bpy.types.Object) -> None:
        c = obj.constraints.new(type='TRACK_TO')
        c.target = target
        c.track_axis = 'TRACK_NEGATIVE_Z'
        c.up_axis = 'UP_Y'

    bpy.ops.object.light_add(
        type='AREA',
        radius=2.2,
        location=(center.x + 2.2, center.y - 3.2, center.z + 1.2),
    )
    key = bpy.context.active_object
    key.name = "Key_Light"
    key.data.energy = 1100.0
    key.data.color = (1.0, 0.97, 0.93)
    _point_at_target(key)

    bpy.ops.object.light_add(
        type='AREA',
        radius=2.6,
        location=(center.x - 2.8, center.y - 2.6, center.z + 0.8),
    )
    fill = bpy.context.active_object
    fill.name = "Fill_Light"
    fill.data.energy = 750.0
    fill.data.color = (0.85, 0.92, 1.0)
    _point_at_target(fill)

    bpy.ops.object.light_add(
        type='AREA',
        radius=2.4,
        location=(center.x + 1.6, center.y + 3.2, center.z + 1.4),
    )
    rim = bpy.context.active_object
    rim.name = "Rim_Light"
    rim.data.energy = 950.0
    rim.data.color = (1.0, 0.98, 0.95)
    _point_at_target(rim)

    bpy.ops.object.light_add(
        type='AREA',
        radius=2.6,
        location=(center.x - 1.8, center.y + 3.0, center.z + 0.6),
    )
    back_fill = bpy.context.active_object
    back_fill.name = "Back_Fill_Light"
    back_fill.data.energy = 750.0
    back_fill.data.color = (0.88, 0.93, 1.0)
    _point_at_target(back_fill)

    bpy.ops.object.light_add(
        type='AREA',
        radius=1.8,
        location=(center.x - 1.2, center.y - 2.5, center.z - 0.9),
    )
    kicker = bpy.context.active_object
    kicker.name = "Kicker_Light"
    kicker.data.energy = 350.0
    kicker.data.color = (0.92, 0.92, 0.96)
    _point_at_target(kicker)

    # 5. Camera Setup
    cam = scene.objects.get("Cinematic_Camera")

    cam_dist = max(span_x / 0.28, span_z / 0.36) * 0.92 + 0.8
    cam_dist = max(4.0, min(6.5, cam_dist))

    if not cam:
        bpy.ops.object.camera_add(location=(target_pos.x, target_pos.y - cam_dist, target_pos.z))
        cam = bpy.context.active_object
        cam.name = "Cinematic_Camera"
        scene.camera = cam

    cam.data.lens = 55.0

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

    if not animations_only:
        # 6. Render 7 Canonical Multi-Angle Stills (at rest frame 1)
        scene.frame_set(1)

        angles = [
            ("angle_01_hero_front34", -18.0, 5.0),
            ("angle_02_side_profile", -65.0, 3.0),
            ("angle_user_facing_view", -75.0, 10.0),
            ("angle_03_dorsal_back34", 138.0, 12.0),
            ("angle_04_low_angle_dramatic", -12.0, -14.0),
            ("angle_05_top_perspective", -22.0, 26.0),
            ("angle_06_true_rear_view", 175.0, 6.0),
        ]

        for name, azim_deg, elev_deg in angles:
            azim = math.radians(azim_deg)
            elev = math.radians(elev_deg)

            cx = target_pos.x + cam_dist * math.cos(elev) * math.sin(azim)
            cy = target_pos.y - cam_dist * math.cos(elev) * math.cos(azim)
            cz = target_pos.z + cam_dist * math.sin(elev)

            cam.location = (cx, cy, cz)
            bpy.context.view_layer.update()

            out_img = out_d / f"{name}.png"
            scene.render.filepath = str(out_img)
            bpy.ops.render.render(write_still=True)
            print(f"Rendered still angle: {out_img}")

    if not stills_only:
        # Use 960x540 for animations to keep RAM/VRAM low and encoding fast
        scene.render.resolution_x = 960
        scene.render.resolution_y = 540

        # 7. Render 360-Degree Orbit Turntable (36 frames @ 24 fps)
        tt_frames_dir = out_d / "_tt_frames"
        tt_frames_dir.mkdir(parents=True, exist_ok=True)
        num_tt_frames = 36

        print("Rendering 360-degree turntable orbit frames...")
        for idx in range(num_tt_frames):
            theta = (idx / num_tt_frames) * 2.0 * math.pi
            azim = theta
            elev = math.radians(6.0 + 4.0 * math.sin(2.0 * theta))

            cx = target_pos.x + cam_dist * math.cos(elev) * math.sin(azim)
            cy = target_pos.y - cam_dist * math.cos(elev) * math.cos(azim)
            cz = target_pos.z + cam_dist * math.sin(elev)

            cam.location = (cx, cy, cz)
            bpy.context.view_layer.update()

            scene.render.filepath = str(tt_frames_dir / f"frame_{idx:04d}.png")
            bpy.ops.render.render(write_still=True)

        tt_mp4 = out_d / "anime_tactical_3d_orbit_turntable.mp4"
        tt_gif = out_d / "anime_tactical_3d_orbit_turntable.gif"

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

        for f in tt_frames_dir.glob("frame_*.png"):
            f.unlink()
        try:
            tt_frames_dir.rmdir()
        except OSError:
            pass

        print(f"Turntable generated: {tt_mp4} and {tt_gif}")

        # 8. Render Tactical Idle Breathing Animation (36 frames @ 24 fps)
        azim = math.radians(-16.0)
        elev = math.radians(5.0)
        cx = target_pos.x + cam_dist * math.cos(elev) * math.sin(azim)
        cy = target_pos.y - cam_dist * math.cos(elev) * math.cos(azim)
        cz = target_pos.z + cam_dist * math.sin(elev)
        cam.location = (cx, cy, cz)
        bpy.context.view_layer.update()

        anim_frames_dir = out_d / "_anim_frames"
        anim_frames_dir.mkdir(parents=True, exist_ok=True)
        scene.frame_start = 1
        scene.frame_end = 36
        scene.render.fps = 24
        scene.render.filepath = str(anim_frames_dir / "frame_")

        print("Rendering illuminated tactical idle animation frames...")
        bpy.ops.render.render(animation=True)

        idle_mp4 = out_d / "anime_tactical_idle.mp4"
        idle_gif = out_d / "anime_tactical_idle.gif"

        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", "24",
            "-i", str(anim_frames_dir / "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            str(idle_mp4),
        ], capture_output=True, check=False)

        subprocess.run([
            "ffmpeg", "-y",
            "-framerate", "24",
            "-i", str(anim_frames_dir / "frame_%04d.png"),
            "-vf", "fps=24,scale=512:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
            str(idle_gif),
        ], capture_output=True, check=False)

        for f in anim_frames_dir.glob("frame_*.png"):
            f.unlink()
        try:
            anim_frames_dir.rmdir()
        except OSError:
            pass

        print(f"Idle animation rendered: {idle_mp4} and {idle_gif}")

    # 9. Save illuminated scene back to .blend
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved illuminated scene to {blend_path}")


if __name__ == "__main__":
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
    else:
        args = []

    c_dir = "outputs/anime_tactical_components"
    b_path = "outputs/scenes/anime_tactical_bipedal.blend"
    g_path = "outputs/scenes/anime_tactical_bipedal.glb"
    o_dir = "outputs/renders/anime_tactical"

    if "--stills-only" in args:
        assemble_and_rig_tactical_model(c_dir, b_path, g_path, total_frames=36)
        render_tactical_model(b_path, o_dir, stills_only=True)
    elif "--animations-only" in args:
        render_tactical_model(b_path, o_dir, animations_only=True)
    else:
        assemble_and_rig_tactical_model(c_dir, b_path, g_path, total_frames=36)
        render_tactical_model(b_path, o_dir)
