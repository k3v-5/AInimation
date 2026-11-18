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
        bg.inputs["Color"].default_value = (0.91, 0.93, 0.96, 1.0)
        bg.inputs["Strength"].default_value = 1.20

    m_floor = bpy.data.materials.new(name="M_LabFloor")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs["Base Color"].default_value = (0.92, 0.94, 0.96, 1.0)
        bsdf_f.inputs["Roughness"].default_value = 0.13
        if "Specular IOR Level" in bsdf_f.inputs:
            bsdf_f.inputs["Specular IOR Level"].default_value = 0.75
        elif "Specular" in bsdf_f.inputs:
            bsdf_f.inputs["Specular"].default_value = 0.75

    me_floor = bpy.data.meshes.new("ENV_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=4, y_segments=4, size=40.0)
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
            bsdf_l.inputs["Emission Strength"].default_value = 16.0
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

    l1_d = bpy.data.lights.new("LGT_FrontKey", 'AREA')
    l1_d.energy = 5200.0
    l1_d.size = 8.0
    l1_d.color = (0.98, 0.99, 1.0)
    l1 = bpy.data.objects.new("LGT_FrontKey", l1_d)
    l1.location = (2.8, 3.0, 3.5)
    l1.rotation_euler = (R(42), R(12), R(38))
    scene.collection.objects.link(l1)

    l2_d = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_d.energy = 9000.0
    l2_d.spot_size = R(92)
    l2_d.color = (0.86, 0.06, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_d)
    l2.location = (-4.0, -4.0, 3.0)
    l2.rotation_euler = (R(-38), R(15), R(-135))
    scene.collection.objects.link(l2)

    l3_d = bpy.data.lights.new("LGT_TopFill", 'AREA')
    l3_d.energy = 2400.0
    l3_d.size = 12.0
    l3_d.color = (0.94, 0.97, 1.0)
    l3 = bpy.data.objects.new("LGT_TopFill", l3_d)
    l3.location = (0.0, 0.0, 6.0)
    scene.collection.objects.link(l3)

def create_liquid_obsidian_plasma_material_v8(name="M_DarX_DarkFluid_ElectricVeins"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1600, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Base: Espejo de obsidiana líquida ultra brillante (75% del cuerpo)
    bsdf.inputs["Base Color"].default_value = (0.001, 0.001, 0.002, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.96
    bsdf.inputs["Roughness"].default_value = 0.016
    bsdf.inputs["IOR"].default_value = 1.65
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.010
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 1.0
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.010

    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    # Mapeo estirado para ríos continuos de plasma longitudinales
    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Scale"].default_value = (2.2, 2.2, 0.50)
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
    noise.inputs["Detail"].default_value = 3.5
    noise.inputs["Roughness"].default_value = 0.52
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    mix = nt.nodes.new(type="ShaderNodeMix")
    mix.location = (-320, 0)
    mix.data_type = 'FLOAT'
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 0.85
    nt.links.new(voro.outputs[0], mix.inputs[2])
    nt.links.new(noise.outputs["Fac"], mix.inputs[3])

    # ColorRamp calibrado con precisión para ~20-25% de ríos de plasma
    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (50, 80)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # Base: Obsidiana pura negra (0.00 a 0.48)
    el[0].position = 0.48
    el[0].color = (0.001, 0.001, 0.002, 1.0)

    # Violeta oscuro terciopelo (0.56)
    e1 = el.new(0.56)
    e1.color = (0.25, 0.01, 0.60, 1.0)

    # Púrpura neón eléctrico saturado (0.68)
    e2 = el.new(0.68)
    e2.color = (0.76, 0.00, 1.0, 1.0)

    # Magenta brillante radiante (0.82)
    e3 = el.new(0.82)
    e3.color = (0.98, 0.12, 0.96, 1.0)

    # Núcleo blanco-lavanda radiante (0.92)
    e4 = el.new(0.92)
    e4.color = (1.0, 0.94, 1.0, 1.0)

    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    # Máscara de emisión luminosa controlada
    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (50, -180)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.52
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.86
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(mix.outputs[0], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (400, -180)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 22.0 # Emisión controlada para no deslavar
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

def build_player_character_v8(col):
    """
    Construye el cuerpo muscular del corredor:
    - Cuello compacto atlético (tucked-in) con cabeza en ángulo de sprint hacia el frente-abajo.
    - Pectorales y 6-pack esculpidos con surco esternal y abdominal.
    - Brazo izquierdo flexionado a 95° con dedos en garra.
    - Piernas en zancada atlética completa.
    - Cresta fluida y cortinas de salpicadura desprendiéndose en la estela.
    """
    verts = []
    radii = []
    edges = []

    def add_v(pos, rx, ry=None):
        idx = len(verts)
        verts.append(pos)
        radii.append((rx, ry if ry else rx))
        return idx

    # --- TORSO / COLUMNA Y CABEZA EN SPRINT (Inclinación 38° hacia +Y) ---
    v_pelvis  = add_v((0.00, 0.00, 0.86), 0.160, 0.130)
    v_waist   = add_v((0.02, 0.12, 1.02), 0.135, 0.110) # Cintura estrecha
    v_ribs    = add_v((0.04, 0.26, 1.18), 0.175, 0.140) # Expansión dorsal
    v_chest   = add_v((0.06, 0.40, 1.34), 0.225, 0.170) # Pectorales
    v_clav_c  = add_v((0.07, 0.46, 1.42), 0.180, 0.130)
    # Cuello corto atlético inclinado hacia adelante
    v_neck    = add_v((0.08, 0.52, 1.48), 0.090, 0.085)
    # Cabeza compacta ubicada en (0.09, 0.60, 1.56)
    v_head    = add_v((0.09, 0.60, 1.56), 0.100, 0.115)

    edges.extend([
        (v_pelvis, v_waist), (v_waist, v_ribs), (v_ribs, v_chest),
        (v_chest, v_clav_c), (v_clav_c, v_neck), (v_neck, v_head)
    ])

    # Clavículas y deltoides amplios (V-Taper)
    v_clav_l = add_v((-0.08, 0.44, 1.38), 0.130, 0.115)
    v_clav_r = add_v((0.18, 0.40, 1.36), 0.130, 0.115)
    v_sh_l   = add_v((-0.26, 0.46, 1.37), 0.125, 0.125)
    v_sh_r   = add_v((0.31, 0.34, 1.32), 0.125, 0.125)

    edges.extend([(v_clav_c, v_clav_l), (v_clav_l, v_sh_l)])
    edges.extend([(v_clav_c, v_clav_r), (v_clav_r, v_sh_r)])

    # --- BRAZO IZQUIERDO (Adelantado, codo flexionado a ~95°) ---
    v_bicep_l = add_v((-0.30, 0.62, 1.28), 0.100, 0.090)
    v_elb_l   = add_v((-0.32, 0.78, 1.18), 0.086, 0.080)
    v_fore_l1 = add_v((-0.26, 0.94, 1.32), 0.078, 0.070)
    v_fore_l2 = add_v((-0.22, 1.08, 1.46), 0.064, 0.056)
    v_wrist_l = add_v((-0.18, 1.20, 1.58), 0.048, 0.040)
    v_palm_l  = add_v((-0.14, 1.28, 1.63), 0.054, 0.028)

    edges.extend([
        (v_sh_l, v_bicep_l), (v_bicep_l, v_elb_l), (v_elb_l, v_fore_l1),
        (v_fore_l1, v_fore_l2), (v_fore_l2, v_wrist_l), (v_wrist_l, v_palm_l)
    ])

    finger_l_dirs = [
        ((-0.06, 0.05, -0.04), 0.016, 0.010),
        ((-0.04, 0.13, 0.05), 0.016, 0.010),
        ((0.01, 0.15, 0.06), 0.017, 0.011),
        ((0.05, 0.14, 0.04), 0.016, 0.010),
        ((0.08, 0.10, 0.02), 0.014, 0.009),
    ]
    for (dx, dy, dz), r1, r2 in finger_l_dirs:
        v_f1 = add_v((-0.14 + dx * 0.55, 1.28 + dy * 0.55, 1.63 + dz * 0.55), r1, r1)
        v_f2 = add_v((-0.14 + dx, 1.28 + dy, 1.63 + dz), r2, r2)
        edges.extend([(v_palm_l, v_f1), (v_f1, v_f2)])

    # --- BRAZO DERECHO (Retrasado hacia atrás) ---
    v_bicep_r = add_v((0.39, 0.18, 1.24), 0.100, 0.090)
    v_elb_r   = add_v((0.46, 0.00, 1.14), 0.086, 0.080)
    v_fore_r1 = add_v((0.50, -0.18, 1.02), 0.076, 0.068)
    v_fore_r2 = add_v((0.52, -0.34, 0.90), 0.060, 0.052)
    v_wrist_r = add_v((0.52, -0.48, 0.80), 0.048, 0.040)
    v_palm_r  = add_v((0.52, -0.58, 0.72), 0.052, 0.028)

    edges.extend([
        (v_sh_r, v_bicep_r), (v_bicep_r, v_elb_r), (v_elb_r, v_fore_r1),
        (v_fore_r1, v_fore_r2), (v_fore_r2, v_wrist_r), (v_wrist_r, v_palm_r)
    ])

    finger_r_dirs = [
        ((0.04, -0.06, 0.02), 0.016, 0.010),
        ((0.03, -0.13, -0.04), 0.016, 0.010),
        ((0.00, -0.15, -0.06), 0.017, 0.011),
        ((-0.03, -0.14, -0.05), 0.016, 0.010),
        ((-0.06, -0.10, -0.03), 0.014, 0.009),
    ]
    for (dx, dy, dz), r1, r2 in finger_r_dirs:
        v_f1 = add_v((0.52 + dx * 0.55, -0.58 + dy * 0.55, 0.72 + dz * 0.55), r1, r1)
        v_f2 = add_v((0.52 + dx, -0.58 + dy, 0.72 + dz), r2, r2)
        edges.extend([(v_palm_r, v_f1), (v_f1, v_f2)])

    # --- CADERAS Y PIERNAS ---
    v_hip_l = add_v((-0.12, -0.04, 0.80), 0.125, 0.112)
    v_hip_r = add_v((0.14, -0.02, 0.80), 0.125, 0.112)
    edges.extend([(v_pelvis, v_hip_l), (v_pelvis, v_hip_r)])

    # Pierna derecha (Adelantada atacando hacia el frente a 85°)
    v_thigh_r1 = add_v((0.18, 0.18, 0.74), 0.138, 0.122)
    v_thigh_r2 = add_v((0.20, 0.36, 0.66), 0.122, 0.108)
    v_knee_r   = add_v((0.20, 0.52, 0.56), 0.094, 0.086)
    v_calf_r1  = add_v((0.18, 0.46, 0.36), 0.096, 0.084)
    v_calf_r2  = add_v((0.16, 0.40, 0.20), 0.074, 0.064)
    v_ank_r    = add_v((0.14, 0.36, 0.10), 0.055, 0.049)
    v_foot_r   = add_v((0.13, 0.46, 0.04), 0.050, 0.075)

    edges.extend([
        (v_hip_r, v_thigh_r1), (v_thigh_r1, v_thigh_r2), (v_thigh_r2, v_knee_r),
        (v_knee_r, v_calf_r1), (v_calf_r1, v_calf_r2), (v_calf_r2, v_ank_r), (v_ank_r, v_foot_r)
    ])

    # Pierna izquierda (Retrasada en extensión elástica)
    v_thigh_l1 = add_v((-0.14, -0.24, 0.74), 0.138, 0.122)
    v_thigh_l2 = add_v((-0.15, -0.48, 0.66), 0.122, 0.108)
    v_knee_l   = add_v((-0.16, -0.72, 0.56), 0.094, 0.086)
    v_calf_l1  = add_v((-0.15, -0.96, 0.42), 0.096, 0.084)
    v_calf_l2  = add_v((-0.14, -1.16, 0.28), 0.074, 0.064)
    v_ank_l    = add_v((-0.12, -1.30, 0.18), 0.055, 0.049)
    v_foot_l   = add_v((-0.11, -1.40, 0.10), 0.050, 0.075)

    edges.extend([
        (v_hip_l, v_thigh_l1), (v_thigh_l1, v_thigh_l2), (v_thigh_l2, v_knee_l),
        (v_knee_l, v_calf_l1), (v_calf_l1, v_calf_l2), (v_calf_l2, v_ank_l), (v_ank_l, v_foot_l)
    ])

    me_body = bpy.data.meshes.new("SK_Body_Mesh_V8")
    me_body.from_pydata(verts, edges, [])
    me_body.update()

    obj_body = bpy.data.objects.new("SK_Player_DarkFluid_V8", me_body)
    col.objects.link(obj_body)

    skin = obj_body.modifiers.new("Skin", 'SKIN')
    skin_verts = me_body.skin_vertices[0].data
    for i, (rx, ry) in enumerate(radii):
        skin_verts[i].radius = (rx, ry)

    sub_skin = obj_body.modifiers.new("Subsurf", 'SUBSURF')
    sub_skin.levels = 2
    sub_skin.render_levels = 2

    dg = bpy.context.evaluated_depsgraph_get()
    eo = obj_body.evaluated_get(dg)
    me_eval = bpy.data.meshes.new_from_object(eo)
    obj_body.modifiers.clear()
    obj_body.data = me_eval

    # --- ESCULPIDO ANATÓMICO Y ELEMENTOS DEDICADOS EN BMESH ---
    bm = bmesh.new()
    bm.from_mesh(obj_body.data)

    # 1. PECTORALES ESCULPIDOS
    mat_pec_l = Matrix.Translation(Vector((-0.03, 0.44, 1.34))) @ Matrix.Rotation(R(-20), 4, 'X') @ Matrix.Rotation(R(-15), 4, 'Z') @ Matrix.Diagonal((0.115, 0.068, 0.095, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_l)

    mat_pec_r = Matrix.Translation(Vector((0.15, 0.40, 1.32))) @ Matrix.Rotation(R(-20), 4, 'X') @ Matrix.Rotation(R(15), 4, 'Z') @ Matrix.Diagonal((0.115, 0.068, 0.095, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_r)

    # 2. ABDOMINALES (6-Pack)
    for z_ab, y_ab, rx, rz in [(1.06, 0.20, 0.052, 0.034), (1.14, 0.28, 0.056, 0.036), (1.22, 0.36, 0.060, 0.038)]:
        m_ab_l = Matrix.Translation(Vector((0.00, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.026, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_l)
        m_ab_r = Matrix.Translation(Vector((0.08, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.026, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_r)

    # 3. CABEZA FACETADA COMPACTA TUCKED-IN
    c_head = Vector((0.09, 0.60, 1.56))
    # Visera facetada en el frente de la cara
    mat_visor = Matrix.Translation(c_head + Vector((0.015, 0.072, -0.012))) @ Matrix.Rotation(R(-24), 4, 'X') @ Matrix.Diagonal((0.078, 0.045, 0.066, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_visor)

    # Quijada angular
    mat_jaw = Matrix.Translation(c_head + Vector((0.010, 0.050, -0.070))) @ Matrix.Rotation(R(-28), 4, 'X') @ Matrix.Diagonal((0.052, 0.065, 0.046, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_jaw)

    # 4. CRESTA FLUIDA POSTERIOR AERODINÁMICA
    crest_spines = [
        (c_head + Vector((-0.01, -0.06, 0.08)), Vector((-0.05, -0.86, 0.38)), 0.28, 0.022),
        (c_head + Vector((0.01, -0.07, 0.04)), Vector((0.02, -0.92, 0.20)), 0.30, 0.020),
        (c_head + Vector((-0.03, -0.05, 0.11)), Vector((-0.08, -0.76, 0.48)), 0.22, 0.016),
        (c_head + Vector((0.04, -0.05, 0.06)), Vector((0.12, -0.82, 0.28)), 0.24, 0.016),
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
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.008, matrix=Matrix.Translation(curr_p + curr_d * 0.015))

    # 5. CORTINAS FLUIDAS CURVADAS EN LA ESTELA
    def add_fluid_ribbon(base_pos, flow_dir, length, width, thickness=0.018):
        bp = Vector(base_pos)
        fd = Vector(flow_dir).normalized()
        up = Vector((0, 0, 1))
        side = fd.cross(up).normalized()
        for i in range(5):
            frac = i / 4.0
            p_b = bp + side * ((frac - 0.5) * width)
            ribbon_len = length * (0.5 + 0.5 * math.sin(frac * math.pi))
            curl_dir = (fd + up * (0.2 * (1.0 - frac))).normalized()
            p_t = p_b + curl_dir * ribbon_len
            mid_c = (p_b + p_t) * 0.5
            dist_c = (p_t - p_b).length
            rot_c = Vector((0, 0, 1)).rotation_difference((p_t - p_b).normalized())
            mat_c = Matrix.Translation(mid_c) @ rot_c.to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=thickness, radius2=0.003, depth=dist_c, matrix=mat_c)
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.007, matrix=Matrix.Translation(p_t + curl_dir * 0.015))

    splash_locs = [
        ((0.46, 0.00, 1.14), (0.35, -0.85, -0.15), 0.26, 0.14),
        ((0.50, -0.18, 1.02), (0.40, -0.80, -0.20), 0.28, 0.16),
        ((0.52, -0.34, 0.90), (0.35, -0.82, -0.25), 0.24, 0.12),
        ((0.08, 0.18, 1.28), (0.15, -0.90, 0.32), 0.30, 0.18),
        ((-0.04, 0.20, 1.30), (-0.15, -0.90, 0.32), 0.26, 0.16),
        ((-0.15, -0.48, 0.66), (-0.25, -0.85, 0.35), 0.30, 0.18),
        ((-0.16, -0.72, 0.56), (-0.25, -0.88, 0.25), 0.32, 0.20),
        ((-0.15, -0.96, 0.42), (-0.20, -0.90, 0.20), 0.28, 0.16),
        ((0.20, 0.52, 0.56), (-0.45, -0.75, 0.30), 0.22, 0.14),
        ((0.18, 0.46, 0.36), (-0.40, -0.80, 0.25), 0.24, 0.14),
    ]
    for sp_p, sp_d, sp_l, sp_w in splash_locs:
        add_fluid_ribbon(sp_p, sp_d, sp_l, sp_w)

    # 6. ENJAMBRE ORBITAL DE FERROFLUIDO (>160 GOTAS)
    droplet_zones = [
        (Vector((0.52, -0.48, 0.80)), 0.38, 38),
        (Vector((-0.18, 1.20, 1.58)), 0.30, 30),
        (Vector((0.08, 0.50, 1.66)), 0.34, 32),
        (Vector((0.04, 0.08, 1.20)), 0.36, 30),
        (Vector((-0.14, -1.18, 0.28)), 0.40, 36),
        (Vector((0.18, 0.48, 0.15)), 0.26, 18),
    ]
    for center, radius, count in droplet_zones:
        for _ in range(count):
            off = Vector((
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
                random.uniform(-radius, radius) * 0.88
            ))
            p_drop = center + off
            rad_drop = random.uniform(0.0035, 0.014)
            mat_drop = Matrix.Translation(p_drop) @ Matrix.Diagonal((rad_drop, rad_drop, rad_drop * random.uniform(1.0, 1.5), 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_drop)

    bm.to_mesh(obj_body.data)
    bm.free()

    remesh = obj_body.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0068
    remesh.use_smooth_shade = True

    smooth = obj_body.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.60
    smooth.iterations = 3

    sub = obj_body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    return obj_body

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_V8"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_V8"
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

    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED: {out_path}")

def main():
    clean_scene()
    col = bpy.data.collections.new("AOE_Player_DarkFluid_V8")
    bpy.context.scene.collection.children.link(col)

    setup_scifi_lab(bpy.context.scene)

    body_obj = build_player_character_v8(col)

    mat_dark = create_liquid_obsidian_plasma_material_v8("M_DarX_DarkFluid_ElectricVeins")
    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_dark)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid_v8"
    os.makedirs(out_dir, exist_ok=True)

    # RENDER HEROICO 1:1
    hero_path = os.path.join(out_dir, "v8_hero_reference_match.png")
    render_camera_view(cam_pos=(2.20, 2.05, 1.15), target_pos=(0.04, 0.22, 0.92), lens=42.0, out_path=hero_path, res=(1080, 1080))

    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V8.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
