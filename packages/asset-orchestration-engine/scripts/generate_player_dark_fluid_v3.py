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
    # Fondo y mundo blanco brillante difuso
    world = bpy.data.worlds.new("W_SciFiLab")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.92, 0.94, 0.97, 1.0)
        bg.inputs["Strength"].default_value = 1.2

    # Material del suelo blanco reflectante
    m_floor = bpy.data.materials.new(name="M_LabFloor")
    m_floor.use_nodes = True
    nt_f = m_floor.node_tree
    bsdf_f = nt_f.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs["Base Color"].default_value = (0.94, 0.95, 0.97, 1.0)
        bsdf_f.inputs["Roughness"].default_value = 0.12
        if "Specular IOR Level" in bsdf_f.inputs:
            bsdf_f.inputs["Specular IOR Level"].default_value = 0.7
        elif "Specular" in bsdf_f.inputs:
            bsdf_f.inputs["Specular"].default_value = 0.7

    # Plano de suelo amplio
    me_floor = bpy.data.meshes.new("ENV_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=4, y_segments=4, size=35.0)
    bm_f.to_mesh(me_floor)
    bm_f.free()
    o_floor = bpy.data.objects.new("ENV_Floor", me_floor)
    scene.collection.objects.link(o_floor)
    o_floor.data.materials.append(m_floor)

    # Tiras LED emisivas blancas en el suelo (patrón geométrico futurista)
    m_led = bpy.data.materials.new(name="M_FloorLED")
    m_led.use_nodes = True
    nt_l = m_led.node_tree
    bsdf_l = nt_l.nodes.get("Principled BSDF")
    if bsdf_l:
        bsdf_l.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        if "Emission Color" in bsdf_l.inputs:
            bsdf_l.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            bsdf_l.inputs["Emission Strength"].default_value = 18.0
        elif "Emission" in bsdf_l.inputs:
            bsdf_l.inputs["Emission"].default_value = (1.0, 1.0, 1.0, 1.0)

    led_lines = [
        # Línea guía longitudinal en la dirección de la carrera
        ((0.2, 0.0, 0.003), (0.09, 32.0, 0.002)),
        ((-1.4, 0.0, 0.003), (0.07, 32.0, 0.002)),
        ((1.8, 0.0, 0.003), (0.07, 32.0, 0.002)),
        # Líneas transversales
        ((0.0, -2.5, 0.003), (24.0, 0.08, 0.002)),
        ((0.0, 1.8, 0.003), (24.0, 0.08, 0.002)),
        ((0.0, 6.2, 0.003), (24.0, 0.08, 0.002)),
        ((0.0, -6.8, 0.003), (24.0, 0.08, 0.002)),
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

    # Paredes de laboratorio y vigas arquitectónicas Sci-Fi de fondo
    me_w = bpy.data.meshes.new("ENV_Walls_Mesh")
    bm_w = bmesh.new()
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((-7.5, 0.0, 5.0)) @ Matrix.Diagonal((0.6, 32.0, 10.0, 1.0)))
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0.0, -9.5, 5.0)) @ Matrix.Diagonal((32.0, 0.6, 10.0, 1.0)))
    # Vigas de techo
    for y_b in [-4.0, 0.0, 4.0]:
        bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0, y_b, 6.2)) @ Matrix.Diagonal((26.0, 0.45, 0.45, 1.0)))
    # Columnas verticales de fondo
    for x_c in [-3.5, 3.5]:
        for y_c in [-4.0, 4.0]:
            bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((x_c, y_c, 3.5)) @ Matrix.Diagonal((0.7, 0.7, 7.0, 1.0)))
    bm_w.to_mesh(me_w)
    bm_w.free()
    o_wall = bpy.data.objects.new("ENV_Walls", me_w)
    scene.collection.objects.link(o_wall)
    o_wall.data.materials.append(m_floor)

    # Iluminación de estudio
    # 1. Softbox principal frontal-superior que ilumina pecho, cara y extremidades
    l1_d = bpy.data.lights.new("LGT_FrontKey", 'AREA')
    l1_d.energy = 5500.0
    l1_d.size = 8.0
    l1_d.color = (0.97, 0.98, 1.0)
    l1 = bpy.data.objects.new("LGT_FrontKey", l1_d)
    l1.location = (3.2, 3.5, 3.8)
    l1.rotation_euler = (R(45), R(10), R(40))
    scene.collection.objects.link(l1)

    # 2. Rim Light de recorte púrpura-violeta potente desde atrás
    l2_d = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_d.energy = 9000.0
    l2_d.spot_size = R(90)
    l2_d.color = (0.86, 0.05, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_d)
    l2.location = (-4.2, -4.5, 3.2)
    l2.rotation_euler = (R(-40), R(15), R(-135))
    scene.collection.objects.link(l2)

    # 3. Luz cenital blanca difusa
    l3_d = bpy.data.lights.new("LGT_TopFill", 'AREA')
    l3_d.energy = 2800.0
    l3_d.size = 12.0
    l3_d.color = (0.95, 0.97, 1.0)
    l3 = bpy.data.objects.new("LGT_TopFill", l3_d)
    l3.location = (0.0, 0.0, 6.0)
    scene.collection.objects.link(l3)

def create_liquid_obsidian_plasma_material(name="M_DarX_DarkFluid_ElectricVeins"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1400, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (1000, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Base: Espejo de obsidiana líquida hiperreflectante
    bsdf.inputs["Base Color"].default_value = (0.001, 0.001, 0.003, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.94
    bsdf.inputs["Roughness"].default_value = 0.016
    bsdf.inputs["IOR"].default_value = 1.62
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.012
    elif "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = 1.0
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.012

    # Coordenadas generadas con mapeo estirado (ríos de plasma que fluyen longitudinalmente)
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-900, 0)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-700, 0)
    # Estiramiento en Z para crear venas largas y dinámicas que siguen la musculatura
    mapping.inputs["Scale"].default_value = (2.2, 2.2, 0.75)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # Voronoi Smooth F1 para celdas y canales biológicos orgánicos
    voro = nt.nodes.new(type="ShaderNodeTexVoronoi")
    voro.location = (-480, 100)
    voro.voronoi_dimensions = '3D'
    voro.feature = 'SMOOTH_F1' if hasattr(voro, 'feature') else 'F1'
    voro.inputs["Scale"].default_value = 4.2
    nt.links.new(mapping.outputs["Vector"], voro.inputs["Vector"])

    # Noise Texture para turbulencia de plasma
    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-480, -150)
    noise.inputs["Scale"].default_value = 6.5
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.55
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    mix = nt.nodes.new(type="ShaderNodeMix")
    mix.location = (-260, 0)
    mix.data_type = 'FLOAT'
    mix.blend_type = 'MULTIPLY'
    mix.inputs["Factor"].default_value = 0.85
    nt.links.new(voro.outputs[0], mix.inputs[2])
    nt.links.new(noise.outputs["Fac"], mix.inputs[3])

    # ColorRamp para el gradiente de emisión de plasma violeta idéntico a la referencia
    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (0, 0)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # Base: Obsidiana negra líquida profunda
    el[0].position = 0.56
    el[0].color = (0.001, 0.001, 0.003, 1.0)

    # Vena violeta profunda
    e1 = el.new(0.63)
    e1.color = (0.28, 0.01, 0.65, 1.0)

    # Vena neón púrpura eléctrico saturado
    e2 = el.new(0.72)
    e2.color = (0.78, 0.02, 1.0, 1.0)

    # Borde neón magenta brillante
    e3 = el.new(0.83)
    e3.color = (0.98, 0.15, 0.96, 1.0)

    # Núcleo plasma blanco-violeta radiante
    e4 = el.new(0.94)
    e4.color = (1.0, 0.90, 1.0, 1.0)

    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    # Máscara de emisión luminosa
    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (0, -220)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.62
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.86
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(mix.outputs[0], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (450, -220)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 58.0
    nt.links.new(emit_cr.outputs["Color"], emit_mult.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(emit_mult.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission"])

    # Ondulación orgánica microscópica del fluido
    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (550, -420)
    bump.inputs["Strength"].default_value = 0.025
    bump.inputs["Distance"].default_value = 0.015
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def build_athletic_sprint_character(col):
    """
    Construye el cuerpo muscular del atleta mediante topología anatómica Skin + Subsurf,
    con volúmenes dedicados de pectorales, 6-pack, deltoides y cabeza facetada,
    remesh voxel y curvaturas de fluido orgánico.
    """
    verts = []
    radii = []
    edges = []

    def add_v(pos, rx, ry=None):
        idx = len(verts)
        verts.append(pos)
        radii.append((rx, ry if ry else rx))
        return idx

    # Coordenadas anatómicas precisas:
    # Torso inclinado a 35° hacia adelante (+Y)
    # Pecho orientado hacia el frente (+Y, +X)
    # Pierna derecha adelantada atacando el suelo
    # Pierna izquierda extendida hacia atrás
    # Brazo izquierdo proyectado al frente con dedos extendidos
    # Brazo derecho retrasado con fluidos desprendiéndose

    # --- TORSO / COLUMNA ---
    v_pelvis = add_v((0.00, 0.00, 0.86), 0.165, 0.135)
    v_waist  = add_v((0.02, 0.14, 1.02), 0.140, 0.115)
    v_ribs   = add_v((0.04, 0.28, 1.18), 0.175, 0.140)
    v_chest  = add_v((0.06, 0.42, 1.34), 0.215, 0.165)
    v_neck_b = add_v((0.07, 0.50, 1.44), 0.105, 0.095)
    v_neck_t = add_v((0.08, 0.56, 1.52), 0.075, 0.075)

    edges.extend([
        (v_pelvis, v_waist), (v_waist, v_ribs), (v_ribs, v_chest),
        (v_chest, v_neck_b), (v_neck_b, v_neck_t)
    ])

    # Clavículas y hombros atléticos anchos (V-Taper)
    v_clav_l = add_v((-0.08, 0.45, 1.38), 0.125, 0.110)
    v_clav_r = add_v((0.18, 0.41, 1.36), 0.125, 0.110)
    v_sh_l   = add_v((-0.26, 0.48, 1.37), 0.120, 0.120)
    v_sh_r   = add_v((0.32, 0.35, 1.32), 0.120, 0.120)

    edges.extend([(v_chest, v_clav_l), (v_clav_l, v_sh_l)])
    edges.extend([(v_chest, v_clav_r), (v_clav_r, v_sh_r)])

    # --- BRAZO IZQUIERDO (Adelantado, en sprint alzado hacia +Y, -X) ---
    # Bicep al frente, codo flexionado a ~115°, antebrazo hacia arriba-adelante, mano abierta
    v_bicep_l = add_v((-0.32, 0.62, 1.34), 0.095, 0.090)
    v_elb_l   = add_v((-0.36, 0.78, 1.30), 0.082, 0.075)
    v_fore_l1 = add_v((-0.30, 0.94, 1.40), 0.075, 0.070)
    v_fore_l2 = add_v((-0.24, 1.08, 1.50), 0.062, 0.055)
    v_wrist_l = add_v((-0.18, 1.20, 1.58), 0.046, 0.038)
    v_palm_l  = add_v((-0.14, 1.28, 1.63), 0.052, 0.026)

    edges.extend([
        (v_sh_l, v_bicep_l), (v_bicep_l, v_elb_l), (v_elb_l, v_fore_l1),
        (v_fore_l1, v_fore_l2), (v_fore_l2, v_wrist_l), (v_wrist_l, v_palm_l)
    ])

    # 5 Dedos extendidos en garra de sprint (Índice, Medio, Anular, Meñique, Pulgar)
    finger_l_dirs = [
        # Pulgar
        ((-0.06, 0.05, -0.04), 0.016, 0.011),
        # Índice
        ((-0.04, 0.12, 0.05), 0.016, 0.011),
        # Medio
        ((0.01, 0.14, 0.06), 0.017, 0.012),
        # Anular
        ((0.05, 0.13, 0.04), 0.016, 0.011),
        # Meñique
        ((0.08, 0.09, 0.02), 0.014, 0.010),
    ]
    for (dx, dy, dz), r1, r2 in finger_l_dirs:
        v_f1 = add_v((-0.14 + dx * 0.55, 1.28 + dy * 0.55, 1.63 + dz * 0.55), r1, r1)
        v_f2 = add_v((-0.14 + dx, 1.28 + dy, 1.63 + dz), r2, r2)
        edges.extend([(v_palm_l, v_f1), (v_f1, v_f2)])

    # --- BRAZO DERECHO (Retrasado, estela fluida hacia -Y, +X) ---
    v_bicep_r = add_v((0.40, 0.20, 1.26), 0.095, 0.090)
    v_elb_r   = add_v((0.46, 0.04, 1.18), 0.085, 0.078)
    v_fore_r1 = add_v((0.50, -0.16, 1.06), 0.075, 0.068)
    v_fore_r2 = add_v((0.52, -0.32, 0.94), 0.060, 0.052)
    v_wrist_r = add_v((0.52, -0.46, 0.84), 0.046, 0.038)
    v_palm_r  = add_v((0.52, -0.56, 0.76), 0.050, 0.026)

    edges.extend([
        (v_sh_r, v_bicep_r), (v_bicep_r, v_elb_r), (v_elb_r, v_fore_r1),
        (v_fore_r1, v_fore_r2), (v_fore_r2, v_wrist_r), (v_wrist_r, v_palm_r)
    ])

    finger_r_dirs = [
        ((0.04, -0.06, 0.02), 0.016, 0.011),
        ((0.03, -0.12, -0.04), 0.016, 0.011),
        ((0.00, -0.14, -0.06), 0.017, 0.012),
        ((-0.03, -0.13, -0.05), 0.016, 0.011),
        ((-0.06, -0.09, -0.03), 0.014, 0.010),
    ]
    for (dx, dy, dz), r1, r2 in finger_r_dirs:
        v_f1 = add_v((0.52 + dx * 0.55, -0.56 + dy * 0.55, 0.76 + dz * 0.55), r1, r1)
        v_f2 = add_v((0.52 + dx, -0.56 + dy, 0.76 + dz), r2, r2)
        edges.extend([(v_palm_r, v_f1), (v_f1, v_f2)])

    # --- CADERAS Y PIERNAS ---
    v_hip_l = add_v((-0.12, -0.04, 0.80), 0.125, 0.110)
    v_hip_r = add_v((0.14, -0.02, 0.80), 0.125, 0.110)
    edges.extend([(v_pelvis, v_hip_l), (v_pelvis, v_hip_r)])

    # PIERNA DERECHA (Adelantada, rodilla flexionada atacando hacia el frente +Y)
    v_thigh_r1 = add_v((0.18, 0.16, 0.74), 0.130, 0.115)
    v_thigh_r2 = add_v((0.20, 0.32, 0.66), 0.115, 0.100)
    v_knee_r   = add_v((0.20, 0.48, 0.56), 0.088, 0.080)
    v_calf_r1  = add_v((0.18, 0.44, 0.38), 0.090, 0.078)
    v_calf_r2  = add_v((0.16, 0.38, 0.22), 0.070, 0.060)
    v_ank_r    = add_v((0.14, 0.34, 0.12), 0.052, 0.046)
    v_foot_r   = add_v((0.13, 0.44, 0.05), 0.048, 0.072)

    edges.extend([
        (v_hip_r, v_thigh_r1), (v_thigh_r1, v_thigh_r2), (v_thigh_r2, v_knee_r),
        (v_knee_r, v_calf_r1), (v_calf_r1, v_calf_r2), (v_calf_r2, v_ank_r), (v_ank_r, v_foot_r)
    ])

    # PIERNA IZQUIERDA (Retrasada, empuje hacia atrás -Y)
    v_thigh_l1 = add_v((-0.14, -0.24, 0.74), 0.130, 0.115)
    v_thigh_l2 = add_v((-0.15, -0.46, 0.66), 0.115, 0.100)
    v_knee_l   = add_v((-0.16, -0.68, 0.56), 0.088, 0.080)
    v_calf_l1  = add_v((-0.15, -0.92, 0.42), 0.090, 0.078)
    v_calf_l2  = add_v((-0.14, -1.12, 0.28), 0.070, 0.060)
    v_ank_l    = add_v((-0.12, -1.26, 0.18), 0.052, 0.046)
    v_foot_l   = add_v((-0.11, -1.36, 0.10), 0.048, 0.072)

    edges.extend([
        (v_hip_l, v_thigh_l1), (v_thigh_l1, v_thigh_l2), (v_thigh_l2, v_knee_l),
        (v_knee_l, v_calf_l1), (v_calf_l1, v_calf_l2), (v_calf_l2, v_ank_l), (v_ank_l, v_foot_l)
    ])

    # Construir malla Skin
    me_body = bpy.data.meshes.new("SK_Body_Base_Mesh")
    me_body.from_pydata(verts, edges, [])
    me_body.update()

    obj_body = bpy.data.objects.new("SK_Player_Body", me_body)
    col.objects.link(obj_body)

    skin = obj_body.modifiers.new("Skin", 'SKIN')
    skin_verts = me_body.skin_vertices[0].data
    for i, (rx, ry) in enumerate(radii):
        skin_verts[i].radius = (rx, ry)

    sub_skin = obj_body.modifiers.new("Subsurf", 'SUBSURF')
    sub_skin.levels = 2
    sub_skin.render_levels = 2

    # Evaluar malla Skin + Subsurf
    dg = bpy.context.evaluated_depsgraph_get()
    eo = obj_body.evaluated_get(dg)
    me_eval = bpy.data.meshes.new_from_object(eo)
    obj_body.modifiers.clear()
    obj_body.data = me_eval

    # --- AÑADIR VOLÚMENES MUSCULARES Y CABEZA FACETADA MEDIANTE BMESH ---
    bm = bmesh.new()
    bm.from_mesh(obj_body.data)

    # 1. PECTORALES PROMINENTES ORIENTADOS A CÁMARA
    # Pectoral izquierdo (adelantado) y derecho
    mat_pec_l = Matrix.Translation(Vector((-0.03, 0.44, 1.34))) @ Matrix.Rotation(R(-20), 4, 'X') @ Matrix.Rotation(R(-15), 4, 'Z') @ Matrix.Diagonal((0.11, 0.065, 0.09, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_l)

    mat_pec_r = Matrix.Translation(Vector((0.15, 0.40, 1.32))) @ Matrix.Rotation(R(-20), 4, 'X') @ Matrix.Rotation(R(15), 4, 'Z') @ Matrix.Diagonal((0.11, 0.065, 0.09, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_r)

    # 2. ABDOMINALES (6-Pack atlético)
    for z_ab, y_ab, rx, rz in [(1.06, 0.20, 0.048, 0.032), (1.14, 0.28, 0.052, 0.035), (1.22, 0.36, 0.056, 0.038)]:
        # Izquierdo
        m_ab_l = Matrix.Translation(Vector((0.00, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.024, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_l)
        # Derecho
        m_ab_r = Matrix.Translation(Vector((0.08, y_ab, z_ab))) @ Matrix.Rotation(R(-35), 4, 'X') @ Matrix.Diagonal((rx, 0.024, rz, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m_ab_r)

    # 3. CABEZA FACETADA DE GEMA / CORTE DE DIAMANTE (Visor geométrico sin rostro)
    # Ubicada en (0.09, 0.64, 1.62) inclinada hacia la dirección de la zancada
    c_head = Vector((0.09, 0.65, 1.64))
    # Cráneo principal facetado
    mat_cran = Matrix.Translation(c_head) @ Matrix.Rotation(R(-25), 4, 'X') @ Matrix.Diagonal((0.090, 0.120, 0.125, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cran)

    # Visera frontal de facetas planas (corte de gema idéntico a la referencia)
    mat_visor = Matrix.Translation(c_head + Vector((0.02, 0.07, -0.01))) @ Matrix.Rotation(R(-22), 4, 'X') @ Matrix.Diagonal((0.075, 0.045, 0.060, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_visor)

    # Quijada angular
    mat_jaw = Matrix.Translation(c_head + Vector((0.01, 0.05, -0.08))) @ Matrix.Rotation(R(-28), 4, 'X') @ Matrix.Diagonal((0.050, 0.065, 0.045, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_jaw)

    # 4. CRESTA FLUIDA POSTERIOR DE LA CABEZA (Espinas líquidas aerodinámicas que se desprenden)
    crest_spines = [
        (c_head + Vector((-0.01, -0.08, 0.07)), Vector((-0.05, -0.85, 0.40)), 0.26, 0.022),
        (c_head + Vector((0.01, -0.09, 0.03)), Vector((0.02, -0.92, 0.22)), 0.28, 0.020),
        (c_head + Vector((-0.03, -0.07, 0.10)), Vector((-0.08, -0.75, 0.50)), 0.20, 0.018),
        (c_head + Vector((0.04, -0.07, 0.05)), Vector((0.12, -0.82, 0.30)), 0.22, 0.016),
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
        # Gota en la punta
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.007, matrix=Matrix.Translation(curr_p + curr_d * 0.015))

    # 5. CORTINAS Y ALETAS DE SALPICADURA LÍQUIDA EN LAS EXTREMIDADES (Fluid ribbons peeling off)
    # Aletas orgánicas que nacen del borde posterior de los brazos, hombros y piernas
    def add_fluid_curtain(base_pos, flow_dir, chord_len, thickness=0.016):
        bp = Vector(base_pos)
        fd = Vector(flow_dir).normalized()
        up = Vector((0, 0, 1))
        side = fd.cross(up).normalized()
        for i in range(4):
            frac = i / 3.0
            p_b = bp + side * ((frac - 0.5) * 0.12)
            curtain_len = chord_len * (0.6 + 0.4 * math.sin(frac * math.pi))
            p_t = p_b + (fd + up * 0.15).normalized() * curtain_len
            mid_c = (p_b + p_t) * 0.5
            dist_c = (p_t - p_b).length
            rot_c = Vector((0, 0, 1)).rotation_difference((p_t - p_b).normalized())
            mat_c = Matrix.Translation(mid_c) @ rot_c.to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=thickness, radius2=0.003, depth=dist_c, matrix=mat_c)
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.006, matrix=Matrix.Translation(p_t + fd * 0.012))

    splash_locs = [
        # Tríceps y codo brazo derecho (retrasado)
        ((0.44, 0.10, 1.22), (0.35, -0.85, -0.20), 0.22),
        ((0.48, -0.08, 1.12), (0.40, -0.80, -0.25), 0.24),
        ((0.52, -0.28, 0.98), (0.35, -0.82, -0.30), 0.20),
        # Espalda y dorsal
        ((0.08, 0.18, 1.28), (0.15, -0.90, 0.30), 0.25),
        ((-0.04, 0.20, 1.30), (-0.15, -0.90, 0.30), 0.22),
        # Muslo y pierna retrasada (izquierda)
        ((-0.15, -0.40, 0.68), (-0.25, -0.85, 0.35), 0.26),
        ((-0.16, -0.62, 0.58), (-0.25, -0.88, 0.25), 0.28),
        ((-0.15, -0.86, 0.44), (-0.20, -0.90, 0.20), 0.24),
        # Pierna adelantada (derecha, rodilla)
        ((0.20, 0.44, 0.54), (-0.45, -0.75, 0.30), 0.18),
        ((0.18, 0.36, 0.32), (-0.40, -0.80, 0.25), 0.20),
    ]
    for sp_p, sp_d, sp_l in splash_locs:
        add_fluid_curtain(sp_p, sp_d, sp_l)

    # 6. ENJAMBRE ORBITAL DE MÁS DE 140 MICROGOTAS EN LA ESTELA AERODINÁMICA
    droplet_zones = [
        # Estela mano y antebrazo derecho (retrasado)
        (Vector((0.52, -0.48, 0.82)), 0.36, 32),
        # Estela mano y brazo izquierdo (adelantado)
        (Vector((-0.18, 1.22, 1.60)), 0.28, 25),
        # Cabeza y cresta posterior
        (Vector((0.08, 0.48, 1.76)), 0.32, 28),
        # Espalda dorsal y cadera
        (Vector((0.04, 0.06, 1.20)), 0.35, 26),
        # Pierna izquierda retrasada (pie y talón)
        (Vector((-0.14, -1.15, 0.30)), 0.38, 30),
    ]
    for center, radius, count in droplet_zones:
        for _ in range(count):
            off = Vector((
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
                random.uniform(-radius, radius) * 0.85
            ))
            p_drop = center + off
            rad_drop = random.uniform(0.0035, 0.013)
            # Gotas esféricas con leve estiramiento en lágrima
            mat_drop = Matrix.Translation(p_drop) @ Matrix.Diagonal((rad_drop, rad_drop, rad_drop * random.uniform(1.0, 1.45), 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_drop)

    bm.to_mesh(obj_body.data)
    bm.free()

    # --- MODIFICADORES DE FUSIÓN Y SUAVIZADO ORGÁNICO ---
    # Remesh Voxel fino para soldar la cabeza, músculos, aletas y torso en una piel única
    remesh = obj_body.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0075
    remesh.use_smooth_shade = True

    # Suavizado de tensión superficial de fluido
    smooth = obj_body.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.75
    smooth.iterations = 4

    sub = obj_body.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    return obj_body

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_V3"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_V3"
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
    col = bpy.data.collections.new("AOE_Player_DarkFluid_V3")
    bpy.context.scene.collection.children.link(col)

    # 1. Configurar laboratorio Sci-Fi blanco
    setup_scifi_lab(bpy.context.scene)

    # 2. Construir atleta muscular de obsidiana líquida
    body_obj = build_athletic_sprint_character(col)

    # 3. Asignar material de obsidiana viva con canales de plasma violeta
    mat_dark = create_liquid_obsidian_plasma_material("M_DarX_DarkFluid_ElectricVeins")
    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_dark)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid_v3"
    os.makedirs(out_dir, exist_ok=True)

    # RENDER PRINCIPAL: Encuadre idéntico a la referencia 1:1 (1080x1080)
    # Cámara frontal-derecha mirando al pecho, brazo delantero alzado y zancada
    hero_path = os.path.join(out_dir, "v3_hero_reference_match.png")
    render_camera_view(cam_pos=(2.3, 2.2, 1.18), target_pos=(0.04, 0.24, 0.96), lens=44.0, out_path=hero_path, res=(1080, 1080))

    # Guardar archivo .blend
    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V3.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
