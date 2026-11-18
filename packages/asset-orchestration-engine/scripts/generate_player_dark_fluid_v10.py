import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Matrix, Euler

def R(deg):
    return math.radians(deg)

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def setup_scifi_lab(scene):
    world = bpy.data.worlds.new("W_SciFiLab")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        # Contraste de estudio sci-fi
        bg.inputs["Color"].default_value = (0.78, 0.82, 0.88, 1.0)
        bg.inputs["Strength"].default_value = 0.40

    m_floor = bpy.data.materials.new(name="M_LabFloor")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs["Base Color"].default_value = (0.94, 0.95, 0.97, 1.0)
        bsdf_f.inputs["Roughness"].default_value = 0.14
        if "Specular IOR Level" in bsdf_f.inputs:
            bsdf_f.inputs["Specular IOR Level"].default_value = 0.75
        elif "Specular" in bsdf_f.inputs:
            bsdf_f.inputs["Specular"].default_value = 0.75

    me_floor = bpy.data.meshes.new("ENV_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=6, y_segments=6, size=40.0)
    bm_f.to_mesh(me_floor)
    bm_f.free()
    o_floor = bpy.data.objects.new("ENV_Floor", me_floor)
    scene.collection.objects.link(o_floor)
    o_floor.data.materials.append(m_floor)

    m_led = bpy.data.materials.new(name="M_FloorLED")
    m_led.use_nodes = True
    bsdf_l = m_led.node_tree.nodes.get("Principled BSDF")
    if bsdf_l:
        bsdf_l.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        if "Emission Color" in bsdf_l.inputs:
            bsdf_l.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            bsdf_l.inputs["Emission Strength"].default_value = 26.0
        elif "Emission" in bsdf_l.inputs:
            bsdf_l.inputs["Emission"].default_value = (1.0, 1.0, 1.0, 1.0)

    led_lines = [
        ((0.2, 0.0, 0.003), (0.08, 36.0, 0.002)),
        ((-1.5, 0.0, 0.003), (0.05, 36.0, 0.002)),
        ((1.9, 0.0, 0.003), (0.05, 36.0, 0.002)),
        ((0.0, -2.2, 0.003), (32.0, 0.08, 0.002)),
        ((0.0, 2.0, 0.003), (32.0, 0.08, 0.002)),
        ((0.0, 6.4, 0.003), (32.0, 0.08, 0.002)),
        ((0.0, -6.4, 0.003), (32.0, 0.08, 0.002)),
    ]
    for pos, size in led_lines:
        me_led = bpy.data.meshes.new("ENV_LED")
        bm_l = bmesh.new()
        bmesh.ops.create_cube(bm_l, size=1.0, matrix=Matrix.Translation(pos) @ Matrix.Diagonal((*size, 1.0)))
        bm_l.to_mesh(me_led)
        bm_l.free()
        o_led = bpy.data.objects.new("ENV_LED_Obj", me_led)
        scene.collection.objects.link(o_led)
        o_led.data.materials.append(m_led)

    me_w = bpy.data.meshes.new("ENV_Walls_Mesh")
    bm_w = bmesh.new()
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((-8.5, 0.0, 5.0)) @ Matrix.Diagonal((0.6, 36.0, 10.0, 1.0)))
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0.0, -10.5, 5.0)) @ Matrix.Diagonal((36.0, 0.6, 10.0, 1.0)))
    for y_b in [-4.0, 0.0, 4.0]:
        bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0, y_b, 6.5)) @ Matrix.Diagonal((30.0, 0.45, 0.45, 1.0)))
    for x_c in [-4.0, 4.0]:
        for y_c in [-4.0, 4.0]:
            bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((x_c, y_c, 3.8)) @ Matrix.Diagonal((0.75, 0.75, 7.6, 1.0)))
    bm_w.to_mesh(me_w)
    bm_w.free()
    o_wall = bpy.data.objects.new("ENV_Walls", me_w)
    scene.collection.objects.link(o_wall)
    o_wall.data.materials.append(m_floor)

    # 1. Key Light frontal compacto para bordes especulares afilados
    l1_d = bpy.data.lights.new("LGT_FrontKey", 'AREA')
    l1_d.energy = 4500.0
    l1_d.size = 1.8
    l1_d.color = (1.0, 1.0, 1.0)
    l1 = bpy.data.objects.new("LGT_FrontKey", l1_d)
    l1.location = (2.6, 2.8, 2.8)
    l1.rotation_euler = (R(48), R(8), R(42))
    scene.collection.objects.link(l1)

    # 2. Rim Light trasero violeta neón
    l2_d = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_d.energy = 13000.0
    l2_d.spot_size = R(88)
    l2_d.color = (0.70, 0.00, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_d)
    l2.location = (-3.5, -3.5, 2.8)
    l2.rotation_euler = (R(-35), R(12), R(-135))
    scene.collection.objects.link(l2)

    # 3. Luz lateral de recorte
    l3_d = bpy.data.lights.new("LGT_SideRim", 'AREA')
    l3_d.energy = 3200.0
    l3_d.size = 1.4
    l3_d.color = (0.95, 0.98, 1.0)
    l3 = bpy.data.objects.new("LGT_SideRim", l3_d)
    l3.location = (-2.0, 3.5, 2.0)
    l3.rotation_euler = (R(30), R(-20), R(120))
    scene.collection.objects.link(l3)

def create_liquid_obsidian_plasma_material_v10(name="M_DarX_DarkFluid_V10"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1600, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Base: OBSIDIANA LÍQUIDA NEGRA AZABACHE PROFUNDA
    bsdf.inputs["Base Color"].default_value = (0.001, 0.001, 0.0015, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.040
    bsdf.inputs["IOR"].default_value = 1.62
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.95
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = 0.95

    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.008
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 1.0
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.008

    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Scale"].default_value = (2.2, 2.2, 0.52)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    voro = nt.nodes.new(type="ShaderNodeTexVoronoi")
    voro.location = (-580, 120)
    voro.voronoi_dimensions = '3D'
    voro.feature = 'SMOOTH_F1' if hasattr(voro, 'feature') else 'F1'
    voro.inputs["Scale"].default_value = 3.6
    nt.links.new(mapping.outputs["Vector"], voro.inputs["Vector"])

    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-580, -120)
    noise.inputs["Scale"].default_value = 5.2
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.48
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    mix = nt.nodes.new(type="ShaderNodeMix")
    mix.location = (-320, 0)
    mix.data_type = 'FLOAT'
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 0.85
    nt.links.new(voro.outputs[0], mix.inputs[2])
    nt.links.new(noise.outputs["Fac"], mix.inputs[3])

    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (50, 80)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # 0.00 a 0.54: Obsidiana pura negra azabache profunda
    el[0].position = 0.54
    el[0].color = (0.001, 0.001, 0.0015, 1.0)

    # 0.62: Terciopelo violeta profundo saturado
    e1 = el.new(0.62)
    e1.color = (0.22, 0.00, 0.60, 1.0)

    # 0.74: Púrpura neón eléctrico saturado intenso
    e2 = el.new(0.74)
    e2.color = (0.64, 0.00, 1.00, 1.0)

    # 0.86: Magenta neón vibrante radiante
    e3 = el.new(0.86)
    e3.color = (0.90, 0.02, 0.88, 1.0)

    # 0.95: Núcleo lavanda eléctrico brillante
    e4 = el.new(0.95)
    e4.color = (0.95, 0.65, 1.00, 1.0)

    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (50, -180)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.65
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.94
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(mix.outputs[0], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (400, -180)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 8.0
    nt.links.new(emit_cr.outputs["Color"], emit_mult.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(emit_mult.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission"])

    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (500, -380)
    bump.inputs["Strength"].default_value = 0.020
    bump.inputs["Distance"].default_value = 0.012
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def create_capsule(bm, p1, p2, r1, r2=None, segments=12):
    if r2 is None:
        r2 = r1
    p1 = Vector(p1)
    p2 = Vector(p2)
    dir_v = p2 - p1
    dist = dir_v.length
    if dist < 1e-4:
        return
    dir_n = dir_v.normalized()
    mid = (p1 + p2) * 0.5
    rot = Vector((0, 0, 1)).rotation_difference(dir_n)
    mat = Matrix.Translation(mid) @ rot.to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2, depth=dist, matrix=mat)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r1, matrix=Matrix.Translation(p1))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2, matrix=Matrix.Translation(p2))

def build_player_character_v10(col):
    """
    Crea el cuerpo atlético muscular y luego une la visera facetada de diamante
    con sombreado plano (flat shading) para que las facetas de gema resalten idénticas al concepto art.
    """
    me = bpy.data.meshes.new("SK_Player_DarkFluid_V10_Mesh")
    bm = bmesh.new()

    # 1. TORSO Y COLUMNA ANATÓMICA
    p_pelvis = Vector((0.00, 0.00, 0.86))
    p_waist  = Vector((0.02, 0.13, 1.02))
    p_ribs   = Vector((0.04, 0.27, 1.18))
    p_chest  = Vector((0.06, 0.42, 1.34))
    p_clav_c = Vector((0.07, 0.48, 1.42))
    p_neck   = Vector((0.08, 0.54, 1.48))
    p_head   = Vector((0.09, 0.62, 1.56))

    create_capsule(bm, p_pelvis, p_waist, 0.165, 0.140)
    create_capsule(bm, p_waist, p_ribs, 0.140, 0.180)
    create_capsule(bm, p_ribs, p_chest, 0.180, 0.230)
    create_capsule(bm, p_chest, p_clav_c, 0.230, 0.190)
    create_capsule(bm, p_clav_c, p_neck, 0.140, 0.115)
    create_capsule(bm, p_neck, p_head, 0.115, 0.125)

    mat_lat_l = Matrix.Translation(Vector((-0.12, 0.30, 1.22))) @ Matrix.Diagonal((0.11, 0.08, 0.18, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_lat_l)
    mat_lat_r = Matrix.Translation(Vector((0.18, 0.26, 1.20))) @ Matrix.Diagonal((0.11, 0.08, 0.18, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_lat_r)

    mat_pec_l = Matrix.Translation(Vector((-0.04, 0.46, 1.35))) @ Matrix.Rotation(R(-22), 4, 'X') @ Matrix.Rotation(R(-14), 4, 'Z') @ Matrix.Diagonal((0.130, 0.075, 0.105, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_l)

    mat_pec_r = Matrix.Translation(Vector((0.16, 0.42, 1.33))) @ Matrix.Rotation(R(-22), 4, 'X') @ Matrix.Rotation(R(14), 4, 'Z') @ Matrix.Diagonal((0.130, 0.075, 0.105, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_r)

    for z_ab, y_ab, rx, rz in [(1.06, 0.20, 0.055, 0.038), (1.15, 0.29, 0.058, 0.040), (1.24, 0.38, 0.062, 0.042)]:
        m_ab_l = Matrix.Translation(Vector((-0.01, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.032, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_l)
        m_ab_r = Matrix.Translation(Vector((0.09, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.032, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_r)

    # 2. CRÁNEO Y CRESTA FLUIDA POSTERIOR
    mat_cranium = Matrix.Translation(p_head + Vector((0.00, -0.02, 0.02))) @ Matrix.Diagonal((0.110, 0.125, 0.125, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cranium)

    crest_spines = [
        (p_head + Vector((-0.01, -0.06, 0.08)), Vector((-0.05, -0.86, 0.38)), 0.32, 0.026),
        (p_head + Vector((0.01, -0.07, 0.04)), Vector((0.02, -0.92, 0.20)), 0.34, 0.024),
        (p_head + Vector((-0.03, -0.05, 0.11)), Vector((-0.08, -0.76, 0.48)), 0.27, 0.018),
        (p_head + Vector((0.04, -0.05, 0.06)), Vector((0.12, -0.82, 0.28)), 0.28, 0.018),
    ]
    for start_p, dir_v, length, r_b in crest_spines:
        curr_p = Vector(start_p)
        curr_d = Vector(dir_v).normalized()
        for step in range(4):
            next_p = curr_p + curr_d * (length / 4.0)
            next_r = max(0.003, r_b * (1.0 - (step + 1) * 0.22))
            mid_p = (curr_p + next_p) * 0.5
            d_seg = (next_p - curr_p).length
            rot = Vector((0, 0, 1)).rotation_difference(curr_d)
            mat_cone = Matrix.Translation(mid_p) @ rot.to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r_b * (1.0 - step * 0.22), radius2=next_r, depth=d_seg, matrix=mat_cone)
            curr_p = next_p
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.009, matrix=Matrix.Translation(curr_p + curr_d * 0.015))

    # 3. BRAZO IZQUIERDO (Adelantado, codo a ~95°, garra 5 dedos abierta)
    p_sh_l    = Vector((-0.26, 0.46, 1.37))
    p_bicep_l = Vector((-0.30, 0.62, 1.28))
    p_elb_l   = Vector((-0.32, 0.78, 1.18))
    p_fore_l1 = Vector((-0.26, 0.94, 1.32))
    p_fore_l2 = Vector((-0.22, 1.08, 1.46))
    p_wrist_l = Vector((-0.18, 1.20, 1.58))
    p_palm_l  = Vector((-0.14, 1.28, 1.63))

    mat_delt_l = Matrix.Translation(p_sh_l) @ Matrix.Diagonal((0.140, 0.135, 0.140, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_delt_l)
    create_capsule(bm, p_clav_c, p_sh_l, 0.130, 0.125)

    create_capsule(bm, p_sh_l, p_bicep_l, 0.125, 0.110)
    create_capsule(bm, p_bicep_l, p_elb_l, 0.110, 0.095)
    create_capsule(bm, p_elb_l, p_fore_l1, 0.095, 0.088)
    create_capsule(bm, p_fore_l1, p_fore_l2, 0.088, 0.072)
    create_capsule(bm, p_fore_l2, p_wrist_l, 0.072, 0.055)
    create_capsule(bm, p_wrist_l, p_palm_l, 0.055, 0.058)

    finger_l_dirs = [
        ((-0.12, 0.08, -0.07), 0.020, 0.012),
        ((-0.07, 0.20, 0.08), 0.020, 0.012),
        ((0.02, 0.23, 0.11), 0.021, 0.013),
        ((0.12, 0.19, 0.07), 0.020, 0.012),
        ((0.17, 0.13, 0.01), 0.018, 0.011),
    ]
    for (dx, dy, dz), r1, r2 in finger_l_dirs:
        p_f1 = p_palm_l + Vector((dx * 0.55, dy * 0.55, dz * 0.55))
        p_f2 = p_palm_l + Vector((dx, dy, dz))
        create_capsule(bm, p_palm_l, p_f1, r1, r1 * 0.85)
        create_capsule(bm, p_f1, p_f2, r1 * 0.85, r2)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2 * 0.9, matrix=Matrix.Translation(p_f2 + Vector((dx, dy, dz)).normalized() * 0.012))

    # 4. BRAZO DERECHO (Retrasado en la estela)
    p_sh_r    = Vector((0.31, 0.34, 1.32))
    p_bicep_r = Vector((0.39, 0.18, 1.24))
    p_elb_r   = Vector((0.46, 0.00, 1.14))
    p_fore_r1 = Vector((0.50, -0.18, 1.02))
    p_fore_r2 = Vector((0.52, -0.34, 0.90))
    p_wrist_r = Vector((0.52, -0.48, 0.80))
    p_palm_r  = Vector((0.52, -0.58, 0.72))

    mat_delt_r = Matrix.Translation(p_sh_r) @ Matrix.Diagonal((0.140, 0.135, 0.140, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_delt_r)
    create_capsule(bm, p_clav_c, p_sh_r, 0.130, 0.125)

    create_capsule(bm, p_sh_r, p_bicep_r, 0.125, 0.110)
    create_capsule(bm, p_bicep_r, p_elb_r, 0.110, 0.095)
    create_capsule(bm, p_elb_r, p_fore_r1, 0.095, 0.086)
    create_capsule(bm, p_fore_r1, p_fore_r2, 0.086, 0.070)
    create_capsule(bm, p_fore_r2, p_wrist_r, 0.070, 0.055)
    create_capsule(bm, p_wrist_r, p_palm_r, 0.055, 0.058)

    finger_r_dirs = [
        ((0.04, -0.06, 0.02), 0.019, 0.012),
        ((0.03, -0.13, -0.04), 0.019, 0.012),
        ((0.00, -0.15, -0.06), 0.020, 0.013),
        ((-0.03, -0.14, -0.05), 0.019, 0.012),
        ((-0.06, -0.10, -0.03), 0.017, 0.011),
    ]
    for (dx, dy, dz), r1, r2 in finger_r_dirs:
        p_f1 = p_palm_r + Vector((dx * 0.55, dy * 0.55, dz * 0.55))
        p_f2 = p_palm_r + Vector((dx, dy, dz))
        create_capsule(bm, p_palm_r, p_f1, r1, r1 * 0.85)
        create_capsule(bm, p_f1, p_f2, r1 * 0.85, r2)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2 * 0.9, matrix=Matrix.Translation(p_f2 + Vector((dx, dy, dz)).normalized() * 0.012))

    # 5. PIERNA DERECHA (Delantera, ataque con rodilla a 85°)
    p_hip_r    = Vector((0.14, -0.02, 0.80))
    p_thigh_r1 = Vector((0.18, 0.18, 0.74))
    p_thigh_r2 = Vector((0.20, 0.36, 0.66))
    p_knee_r   = Vector((0.20, 0.52, 0.56))
    p_calf_r1  = Vector((0.18, 0.46, 0.36))
    p_calf_r2  = Vector((0.16, 0.40, 0.20))
    p_ank_r    = Vector((0.14, 0.36, 0.10))
    p_foot_r   = Vector((0.13, 0.46, 0.04))

    create_capsule(bm, p_pelvis, p_hip_r, 0.155, 0.140)
    create_capsule(bm, p_hip_r, p_thigh_r1, 0.140, 0.135)
    create_capsule(bm, p_thigh_r1, p_thigh_r2, 0.135, 0.120)
    create_capsule(bm, p_thigh_r2, p_knee_r, 0.120, 0.105)

    mat_patella_r = Matrix.Translation(p_knee_r + Vector((0.00, 0.05, 0.00))) @ Matrix.Diagonal((0.075, 0.065, 0.075, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_patella_r)

    create_capsule(bm, p_knee_r, p_calf_r1, 0.105, 0.110)
    create_capsule(bm, p_calf_r1, p_calf_r2, 0.110, 0.082)
    create_capsule(bm, p_calf_r2, p_ank_r, 0.082, 0.062)
    create_capsule(bm, p_ank_r, p_foot_r, 0.062, 0.065)

    mat_foot_r = Matrix.Translation(p_foot_r + Vector((0.00, 0.04, 0.00))) @ Matrix.Diagonal((0.065, 0.110, 0.045, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_foot_r)

    # 6. PIERNA IZQUIERDA (Trasera, empuje elástico)
    p_hip_l    = Vector((-0.12, -0.04, 0.80))
    p_thigh_l1 = Vector((-0.14, -0.24, 0.74))
    p_thigh_l2 = Vector((-0.15, -0.48, 0.66))
    p_knee_l   = Vector((-0.16, -0.72, 0.56))
    p_calf_l1  = Vector((-0.15, -0.96, 0.42))
    p_calf_l2  = Vector((-0.14, -1.16, 0.28))
    p_ank_l    = Vector((-0.12, -1.30, 0.18))
    p_foot_l   = Vector((-0.11, -1.40, 0.10))

    create_capsule(bm, p_pelvis, p_hip_l, 0.155, 0.140)
    create_capsule(bm, p_hip_l, p_thigh_l1, 0.140, 0.135)
    create_capsule(bm, p_thigh_l1, p_thigh_l2, 0.135, 0.120)
    create_capsule(bm, p_thigh_l2, p_knee_l, 0.120, 0.105)

    mat_patella_l = Matrix.Translation(p_knee_l + Vector((0.00, 0.04, -0.02))) @ Matrix.Diagonal((0.075, 0.065, 0.075, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_patella_l)

    create_capsule(bm, p_knee_l, p_calf_l1, 0.105, 0.110)
    create_capsule(bm, p_calf_l1, p_calf_l2, 0.110, 0.082)
    create_capsule(bm, p_calf_l2, p_ank_l, 0.082, 0.062)
    create_capsule(bm, p_ank_l, p_foot_l, 0.062, 0.065)

    mat_foot_l = Matrix.Translation(p_foot_l + Vector((0.00, -0.06, 0.00))) @ Matrix.Diagonal((0.060, 0.110, 0.042, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_foot_l)

    # 7. CORTINAS FLUIDAS Y TENDRILS
    def add_fluid_ribbon(base_pos, flow_dir, length, width, thickness=0.020):
        bp = Vector(base_pos)
        fd = Vector(flow_dir).normalized()
        up = Vector((0, 0, 1))
        side = fd.cross(up).normalized()
        for i in range(4):
            frac = i / 3.0
            p_b = bp + side * ((frac - 0.5) * width)
            ribbon_len = length * (0.6 + 0.4 * math.sin(frac * math.pi))
            curl_dir = (fd + up * (0.25 * (1.0 - frac))).normalized()
            p_t = p_b + curl_dir * ribbon_len
            create_capsule(bm, p_b, p_t, thickness, 0.005, segments=8)
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.008, matrix=Matrix.Translation(p_t + curl_dir * 0.015))

    splash_locs = [
        ((0.46, 0.00, 1.14), (0.35, -0.85, -0.15), 0.26, 0.14),
        ((0.50, -0.18, 1.02), (0.40, -0.80, -0.20), 0.28, 0.15),
        ((-0.15, -0.48, 0.66), (-0.25, -0.85, 0.35), 0.30, 0.16),
        ((-0.15, -0.96, 0.42), (-0.20, -0.90, 0.20), 0.28, 0.15),
        ((0.20, 0.52, 0.56), (-0.45, -0.75, 0.30), 0.22, 0.12),
        ((0.13, 0.46, 0.04), (0.20, 0.60, 0.25), 0.18, 0.12),
    ]
    for sp_p, sp_d, sp_l, sp_w in splash_locs:
        add_fluid_ribbon(sp_p, sp_d, sp_l, sp_w)

    # 8. ENJAMBRE ORBITAL DE FERROFLUIDO (>150 GOTAS)
    droplet_zones = [
        (Vector((0.52, -0.48, 0.80)), 0.38, 38),
        (Vector((-0.18, 1.20, 1.58)), 0.30, 32),
        (Vector((0.08, 0.50, 1.66)), 0.34, 30),
        (Vector((0.04, 0.08, 1.20)), 0.36, 30),
        (Vector((-0.14, -1.18, 0.28)), 0.40, 36),
        (Vector((0.15, 0.46, 0.06)), 0.25, 20),
    ]
    for center, radius, count in droplet_zones:
        for _ in range(count):
            off = Vector((
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
                random.uniform(-radius, radius) * 0.88
            ))
            p_drop = center + off
            rad_drop = random.uniform(0.004, 0.015)
            mat_drop = Matrix.Translation(p_drop) @ Matrix.Diagonal((rad_drop, rad_drop, rad_drop * random.uniform(1.0, 1.5), 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_drop)

    bm.to_mesh(me)
    bm.free()

    obj_body = bpy.data.objects.new("SK_Player_DarkFluid_V10", me)
    col.objects.link(obj_body)

    # Remesh de Vóxeles para fundir orgánicamente el cuerpo
    remesh = obj_body.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0075
    remesh.use_smooth_shade = True

    smooth = obj_body.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.50
    smooth.iterations = 2

    # Aplicar modificadores de base para poder integrar la visera facetada nítida
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eo = obj_body.evaluated_get(dg)
    me_final = bpy.data.meshes.new_from_object(eo)
    obj_body.modifiers.clear()
    obj_body.data = me_final

    # 9. AÑADIR MÁSCARA FACETADA DE DIAMANTE DIRECTAMENTE EN EL ROSTRO CON FLAT SHADING
    bm_face = bmesh.new()
    bm_face.from_mesh(obj_body.data)

    mat_visor = Matrix.Translation(p_head + Vector((0.015, 0.082, -0.012))) @ Matrix.Rotation(R(-26), 4, 'X') @ Matrix.Diagonal((0.088, 0.052, 0.076, 1.0))
    res_v = bmesh.ops.create_icosphere(bm_face, subdivisions=1, radius=1.0, matrix=mat_visor)
    for v in res_v['verts']:
        for f in v.link_faces:
            f.smooth = False # Facetas planas de diamante que reflejan como gemas

    mat_jaw = Matrix.Translation(p_head + Vector((0.012, 0.062, -0.076))) @ Matrix.Rotation(R(-32), 4, 'X') @ Matrix.Diagonal((0.064, 0.072, 0.054, 1.0))
    res_j = bmesh.ops.create_icosphere(bm_face, subdivisions=1, radius=1.0, matrix=mat_jaw)
    for v in res_j['verts']:
        for f in v.link_faces:
            f.smooth = False

    bm_face.to_mesh(obj_body.data)
    bm_face.free()

    return obj_body

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_V10"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_V10"
    if tgt_name in bpy.data.objects:
        tgt_obj = bpy.data.objects[tgt_name]
    else:
        tgt_obj = bpy.data.objects.new(tgt_name, None)
        scene.collection.objects.link(tgt_obj)
    tgt_obj.location = target_pos

    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = tgt_obj
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    bpy.context.view_layer.update()
    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED: {out_path}")

def compose_quadrants_sheet(front_p, back_p, hero_p, fps_p, out_p):
    """Compone la hoja reglamentaria de 4 cuadrantes (2560x1440) con PIL."""
    from PIL import Image, ImageDraw

    img_h = Image.open(hero_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_f = Image.open(front_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_b = Image.open(back_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_fps = Image.open(fps_p).resize((1280, 720), Image.Resampling.LANCZOS)

    sheet = Image.new('RGB', (2560, 1440), (18, 20, 24))
    sheet.paste(img_h, (0, 0))
    sheet.paste(img_f, (1280, 0))
    sheet.paste(img_b, (0, 720))
    sheet.paste(img_fps, (1280, 720))

    draw = ImageDraw.Draw(sheet)
    # Títulos de cuadrantes
    draw.text((40, 30), "ACCION 3/4 (HERO REFERENCIA 1:1)", fill=(240, 240, 255))
    draw.text((1320, 30), "VISTA FRONTAL", fill=(240, 240, 255))
    draw.text((40, 750), "VISTA TRASERA", fill=(240, 240, 255))
    draw.text((1320, 750), "VISTA PRIMERA PERSONA (FPS ARMS)", fill=(240, 240, 255))

    sheet.save(out_p)
    print(f"QUADRANTS_SHEET_SAVED: {out_p}")

def main():
    clean_scene()
    col = bpy.data.collections.new("AOE_Player_DarkFluid_V10")
    bpy.context.scene.collection.children.link(col)

    setup_scifi_lab(bpy.context.scene)

    body_obj = build_player_character_v10(col)

    mat_dark = create_liquid_obsidian_plasma_material_v10("M_DarX_DarkFluid_V10")
    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_dark)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid_v10"
    os.makedirs(out_dir, exist_ok=True)

    hero_path = os.path.join(out_dir, "v10_hero_reference_match.png")
    render_camera_view(cam_pos=(2.45, 2.25, 1.18), target_pos=(0.04, 0.20, 0.90), lens=38.0, out_path=hero_path, res=(1080, 1080))

    front_path = os.path.join(out_dir, "v10_view_front.png")
    render_camera_view(cam_pos=(0.04, 2.80, 1.05), target_pos=(0.04, 0.15, 0.95), lens=45.0, out_path=front_path, res=(1080, 1080))

    back_path = os.path.join(out_dir, "v10_view_back.png")
    render_camera_view(cam_pos=(0.04, -2.60, 1.05), target_pos=(0.04, 0.05, 0.95), lens=45.0, out_path=back_path, res=(1080, 1080))

    fps_path = os.path.join(out_dir, "v10_view_fps.png")
    render_camera_view(cam_pos=(-0.05, 0.50, 1.52), target_pos=(-0.16, 1.25, 1.58), lens=24.0, out_path=fps_path, res=(1080, 1080))

    quad_path = os.path.join(out_dir, "preview_player_dark_fluid_4quadrants.png")
    compose_quadrants_sheet(front_path, back_path, hero_path, fps_path, quad_path)

    # Copiar también a la raíz de renders para acceso directo
    import shutil
    shutil.copy(quad_path, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_dark_fluid_4quadrants.png")
    shutil.copy(hero_path, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_skin_dark_fluid.png")

    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V10.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
