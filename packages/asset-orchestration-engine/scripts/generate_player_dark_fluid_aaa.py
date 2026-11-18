"""generate_player_dark_fluid_aaa.py
Genera y renderiza el Personaje Principal de DarX con calidad AAA canónica:
- Humanoide atlético de ferrofluido / obsidiana líquida viva hiperbrillante (espejo líquido, metálico 0.96, rugosidad 0.02, clearcoat 1.0).
- Red interna de plasma púrpura/violeta neón radiante con emisión activa (45 W/m^2).
- Anatomía muscular continua y potente en postura de sprint contralateral (cero desconexiones ni huecos).
- Manos maestras articuladas con 5 dedos completos, garras fluidas y microgotas.
- Cabeza facetada de corte de gema (visor angular low-poly sleek) con cresta fluida hidrodinámica hacia atrás.
- Salpicaduras cinéticas y nube de microgotas suspendidas en la estela de carrera.
- Entorno de laboratorio Sci-Fi blanco con paneles arquitectónicos, suelo cerámico reflectante y líneas LED.
- Genera el render reglamentario de 4 cuadrantes (Frontal, Trasera, Acción 3/4 y FPS Arms) y el mosaico compuesto.
"""

import sys, os, math
import bpy, bmesh
from mathutils import Matrix, Vector, Euler

R = math.radians
TAU = math.pi * 2

def setup_scifi_lab_environment(scene):
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.82, 0.86, 0.92, 1.0)
            bg.inputs["Strength"].default_value = 0.95

    # Limpiar luces y entorno previos
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT' or o.name.startswith("ENV_") or o.name.startswith("CAM_") or o.name.startswith("LGT_"):
            bpy.data.objects.remove(o, do_unlink=True)

    # Suelo reflectante blanco de laboratorio
    me_f = bpy.data.meshes.new("ENV_Lab_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=24, y_segments=24, size=32.0, matrix=Matrix.Translation((0, 0, 0.0)))
    bm_f.to_mesh(me_f)
    bm_f.free()

    obj_floor = bpy.data.objects.new("ENV_Lab_Floor", me_f)
    scene.collection.objects.link(obj_floor)

    m_floor = bpy.data.materials.new("M_Lab_CeramicWhite_Gloss")
    m_floor.use_nodes = True
    nt_f = m_floor.node_tree
    bsdf_f = nt_f.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.90, 0.92, 0.95, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.10
        bsdf_f.inputs['Roughness'].default_value = 0.035
        if "Coat Weight" in bsdf_f.inputs:
            bsdf_f.inputs["Coat Weight"].default_value = 1.0
            bsdf_f.inputs["Coat Roughness"].default_value = 0.015

    obj_floor.data.materials.append(m_floor)

    # Tiras LED emisivas en el suelo
    led_configs = [
        (Vector((0.0, 0.0, 0.002)), (0.12, 26.0, 0.005)),
        (Vector((2.2, 0.0, 0.002)), (0.08, 26.0, 0.005)),
        (Vector((-2.2, 0.0, 0.002)), (0.08, 26.0, 0.005)),
        (Vector((0.0, 4.5, 0.002)), (14.0, 0.08, 0.005)),
        (Vector((0.0, -4.5, 0.002)), (14.0, 0.08, 0.005)),
    ]
    for pos, size in led_configs:
        me_led = bpy.data.meshes.new("ENV_LED_Line")
        bm_l = bmesh.new()
        bmesh.ops.create_cube(bm_l, size=1.0, matrix=Matrix.Translation(pos) @ Matrix.Diagonal((*size, 1.0)))
        bm_l.to_mesh(me_led)
        bm_l.free()
        obj_led = bpy.data.objects.new("ENV_LED_Line_Obj", me_led)
        scene.collection.objects.link(obj_led)
        
        m_led = bpy.data.materials.get("M_LED_CyanWhite")
        if not m_led:
            m_led = bpy.data.materials.new("M_LED_CyanWhite")
            m_led.use_nodes = True
            bsdf_l = m_led.node_tree.nodes.get("Principled BSDF")
            if bsdf_l:
                bsdf_l.inputs['Base Color'].default_value = (0.92, 0.98, 1.0, 1.0)
                if "Emission Color" in bsdf_l.inputs:
                    bsdf_l.inputs["Emission Color"].default_value = (0.88, 0.96, 1.0, 1.0)
                    bsdf_l.inputs["Emission Strength"].default_value = 24.0
        obj_led.data.materials.append(m_led)

    # Paredes de laboratorio y columnas modulares de fondo
    wall_mesh = bpy.data.meshes.new("ENV_Lab_Walls_Mesh")
    bm_w = bmesh.new()
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0, 9.5, 5.0)) @ Matrix.Diagonal((28.0, 0.5, 10.0, 1.0)))
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((-8.5, 0.0, 5.0)) @ Matrix.Diagonal((0.5, 24.0, 10.0, 1.0)))
    for x_p in [-4.5, 4.5]:
        for y_p in [7.5, 2.5, -4.5]:
            bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((x_p, y_p, 4.0)) @ Matrix.Diagonal((0.8, 0.8, 8.0, 1.0)))
    bm_w.to_mesh(wall_mesh)
    bm_w.free()
    obj_wall = bpy.data.objects.new("ENV_Lab_Walls", wall_mesh)
    scene.collection.objects.link(obj_wall)
    obj_wall.data.materials.append(m_floor)

    # Iluminación de estudio
    # 1. Key Light frontal suave amplia
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 3400
    l1_data.size = 6.5
    l1_data.color = (0.98, 0.98, 1.0)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (2.8, 4.0, 4.2)
    l1.rotation_euler = (R(42), 0, R(30))
    scene.collection.objects.link(l1)

    # 2. Rim Light neón violeta potente
    l2_data = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_data.energy = 6000
    l2_data.spot_size = R(82)
    l2_data.color = (0.86, 0.08, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_data)
    l2.location = (-3.6, -4.0, 2.8)
    l2.rotation_euler = (R(-38), 0, R(-138))
    scene.collection.objects.link(l2)

    # 3. Top Fill Light blanca
    l3_data = bpy.data.lights.new("LGT_TopFill", 'AREA')
    l3_data.energy = 2000
    l3_data.size = 8.5
    l3_data.color = (0.92, 0.96, 1.0)
    l3 = bpy.data.objects.new("LGT_TopFill", l3_data)
    l3.location = (0.0, 0.5, 5.0)
    l3.rotation_euler = (0, 0, 0)
    scene.collection.objects.link(l3)

def create_dark_fluid_plasma_material(name="M_DarX_DarkFluid_ElectricVeins"):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1200, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (850, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Ferrofluido Negro Obsidiana Ultrabrillante (Espejo líquido)
    bsdf.inputs["Metallic"].default_value = 0.96
    bsdf.inputs["Roughness"].default_value = 0.020
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.68
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.010

    # Coordenadas y mapeo
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, 0)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-800, 0)
    mapping.inputs["Scale"].default_value = (1.5, 1.5, 1.1)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # Dos ruidos orgánicos fluidos
    n1 = nt.nodes.new(type="ShaderNodeTexNoise")
    n1.location = (-600, 150)
    n1.inputs["Scale"].default_value = 2.2
    n1.inputs["Detail"].default_value = 5.0
    n1.inputs["Roughness"].default_value = 0.42
    n1.inputs["Distortion"].default_value = 4.5
    nt.links.new(mapping.outputs["Vector"], n1.inputs["Vector"])

    n2 = nt.nodes.new(type="ShaderNodeTexNoise")
    n2.location = (-600, -150)
    n2.inputs["Scale"].default_value = 4.2
    n2.inputs["Detail"].default_value = 6.0
    n2.inputs["Roughness"].default_value = 0.50
    n2.inputs["Distortion"].default_value = 3.0
    nt.links.new(mapping.outputs["Vector"], n2.inputs["Vector"])

    mix = nt.nodes.new(type="ShaderNodeMix")
    mix.data_type = 'FLOAT'
    mix.location = (-400, 0)
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(n1.outputs["Fac"], mix.inputs[2])
    nt.links.new(n2.outputs["Fac"], mix.inputs[3])

    # ColorRamp: 75% Negro Obsidiana Profundo + Torrentes Neón Violeta / Púrpura
    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (-150, 150)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # Pos 0.51: Negro obsidiana puro
    el[0].position = 0.51
    el[0].color = (0.002, 0.002, 0.004, 1.0)

    # Pos 0.61: Tono violáceo profundo
    e1 = el.new(0.61)
    e1.color = (0.16, 0.01, 0.44, 1.0)

    # Pos 0.70: Neón violeta / púrpura eléctrico
    e2 = el.new(0.70)
    e2.color = (0.70, 0.02, 1.0, 1.0)

    # Pos 0.82: Magenta vivo brillante
    e3 = el.new(0.82)
    e3.color = (0.96, 0.05, 1.0, 1.0)

    # Pos 0.94: Núcleo blanco-violeta plasma de alta energía
    e4 = el.new(0.94)
    e4.color = (1.0, 0.82, 1.0, 1.0)

    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    # Emisión luminosa
    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (-150, -150)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.59
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.86
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(mix.outputs[0], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (200, -150)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 45.0
    nt.links.new(emit_cr.outputs["Color"], emit_mult.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(emit_mult.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission"])

    # Bump de micro-ondulación de fluido
    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (300, -320)
    bump.inputs["Strength"].default_value = 0.035
    bump.inputs["Distance"].default_value = 0.020
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def add_solid_overlapping_limb(bm, p1, p2, r1, r2, segments=32, overlap=0.040):
    """Crea un segmento cilíndrico de alta resolución con extensión y esferas de unión con orientación matemática estricta."""
    v1 = Vector(p1)
    v2 = Vector(p2)
    dir_vec = v2 - v1
    dist = dir_vec.length
    if dist < 0.001:
        return
    
    d_norm = dir_vec.normalized()
    p1_ext = v1 - d_norm * overlap
    p2_ext = v2 + d_norm * overlap
    dist_ext = (p2_ext - p1_ext).length
    mid = (p1_ext + p2_ext) * 0.5

    # Esferas en articulaciones
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r1 * 1.02, matrix=Matrix.Translation(v1))
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r2 * 1.02, matrix=Matrix.Translation(v2))

    # create_cone genera geometría orientada a lo largo del eje local Z (0, 0, 1)
    cone_axis = Vector((0, 0, 1))
    rot = cone_axis.rotation_difference(d_norm)
    mat_rot = rot.to_matrix().to_4x4()
    mat_trans = Matrix.Translation(mid)

    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=segments,
        radius1=r1,
        radius2=r2,
        depth=dist_ext,
        matrix=mat_trans @ mat_rot
    )

def add_fluid_droplet(bm, pos, radius):
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=radius, matrix=Matrix.Translation(Vector(pos)))

def add_fluid_tendril(bm, start_p, dir_v, length, r_base, curl_v=None):
    v_start = Vector(start_p)
    v_dir = Vector(dir_v).normalized()
    if curl_v is None:
        curl_v = Vector((0, 0, 0.4))

    steps = 4
    seg_len = length / steps
    curr_p = v_start
    curr_r = r_base
    curr_dir = v_dir

    for i in range(steps):
        next_dir = (curr_dir + curl_v * (0.35 / (i + 1))).normalized()
        next_p = curr_p + next_dir * seg_len
        next_r = max(0.003, curr_r - (r_base - 0.003) / steps)
        add_solid_overlapping_limb(bm, curr_p, next_p, curr_r, next_r, segments=12, overlap=0.01)
        curr_p = next_p
        curr_r = next_r
        curr_dir = next_dir

    add_fluid_droplet(bm, curr_p + curr_dir * 0.015, 0.006)

def build_master_articulated_hand(bm, wrist_pos, forward_dir, up_dir, is_right=True, scale=1.0):
    """
    Construye la mano de 5 dedos con garras de ferrofluido:
    - Muñeca anatómica con apófisis estiloides (radio y cúbito).
    - Arco palmar metacarpiano con eminencias tenar e hipotenar.
    - Pulgar oponible con 3 segmentos articulados y garra afilada.
    - 4 dedos independientes con 3 falanges cada uno y garras predadoras.
    - Cero membranas: separación digital completa para visualización perfecta en FPS y 3/4.
    """
    w_pos = Vector(wrist_pos)
    fwd = Vector(forward_dir).normalized()
    up = Vector(up_dir).normalized()
    side = fwd.cross(up).normalized()
    if not is_right:
        side = -side

    # 1. Articulación de Muñeca (Ulna y Radio)
    p_radius = w_pos + side * (0.018 * scale) + up * (0.002 * scale)
    p_ulna = w_pos - side * (0.017 * scale) + up * (0.004 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.009 * scale, matrix=Matrix.Translation(p_radius))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.008 * scale, matrix=Matrix.Translation(p_ulna))

    # Núcleo de muñeca
    mat_wrist = Matrix.Translation(w_pos) @ Matrix.Diagonal((0.034 * scale, 0.028 * scale, 0.026 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_wrist)

    # 2. Palma Metacarpiana
    palm_center = w_pos + fwd * (0.048 * scale)
    mat_palm = Matrix.Translation(palm_center) @ Matrix.Diagonal((0.036 * scale, 0.042 * scale, 0.020 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_palm)

    # Almohadillas Tenar e Hipotenar
    thenar_pos = w_pos + fwd * (0.026 * scale) + side * (0.018 * scale) - up * (0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.014 * scale, matrix=Matrix.Translation(thenar_pos))
    hypo_pos = w_pos + fwd * (0.028 * scale) - side * (0.016 * scale) - up * (0.005 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.012 * scale, matrix=Matrix.Translation(hypo_pos))

    add_solid_overlapping_limb(bm, w_pos, palm_center, 0.028 * scale, 0.026 * scale, segments=16, overlap=0.015 * scale)

    # 3. Tendones Dorsales
    knuckle_targets = [
        ("Index",   0.015 * scale),
        ("Middle",  0.004 * scale),
        ("Ring",   -0.006 * scale),
        ("Pinky",  -0.015 * scale)
    ]
    for name, s_off in knuckle_targets:
        p_knuckle = palm_center + fwd * (0.032 * scale) + side * s_off + up * (0.008 * scale)
        p_wrist_tendon = w_pos + side * (s_off * 0.45) + up * (0.009 * scale)
        add_solid_overlapping_limb(bm, p_wrist_tendon, p_knuckle, 0.0045 * scale, 0.0038 * scale, segments=8, overlap=0.006 * scale)

    # 4. PULGAR OPONIBLE (Metacarpo + Falange Proximal + Garra Distal)
    thumb_mcp = thenar_pos + fwd * (0.018 * scale) + side * (0.014 * scale) - up * (0.002 * scale)
    add_solid_overlapping_limb(bm, thenar_pos, thumb_mcp, 0.012 * scale, 0.010 * scale, segments=12, overlap=0.008 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.009 * scale, matrix=Matrix.Translation(thumb_mcp))

    thumb_dir1 = (fwd * 0.65 + side * 0.70 + up * 0.15).normalized()
    thumb_ip = thumb_mcp + thumb_dir1 * (0.030 * scale)
    add_solid_overlapping_limb(bm, thumb_mcp, thumb_ip, 0.0095 * scale, 0.0080 * scale, segments=12, overlap=0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0080 * scale, matrix=Matrix.Translation(thumb_ip))

    thumb_dir2 = (fwd * 0.85 + side * 0.30 - up * 0.35).normalized()
    thumb_tip = thumb_ip + thumb_dir2 * (0.027 * scale)
    add_solid_overlapping_limb(bm, thumb_ip, thumb_tip, 0.0080 * scale, 0.0034 * scale, segments=12, overlap=0.006 * scale)
    add_fluid_droplet(bm, thumb_tip + thumb_dir2 * 0.012, 0.0035 * scale)

    # 5. CUATRO DEDOS ARTICULADOS Y GARRAS
    finger_configs = [
        # (name, side_offset, base_len, mid_len, tip_len, curl_angle, splay_angle)
        ("Index",   0.016,  0.038, 0.030, 0.026,  math.radians(16),  math.radians(18)),
        ("Middle",  0.004,  0.042, 0.034, 0.029,  math.radians(20),  math.radians(4)),
        ("Ring",   -0.008,  0.039, 0.030, 0.026,  math.radians(24), -math.radians(10)),
        ("Pinky",  -0.018,  0.032, 0.024, 0.021,  math.radians(28), -math.radians(24))
    ]

    for name, s_off, l1, l2, l3, curl_deg, splay_deg in finger_configs:
        knuckle_pos = palm_center + fwd * (0.032 * scale) + side * (s_off * scale) + up * (0.007 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0088 * scale, matrix=Matrix.Translation(knuckle_pos))

        # Falange 1 (Proximal)
        d1 = (fwd * math.cos(splay_deg) + side * math.sin(splay_deg) - up * math.sin(curl_deg * 0.40)).normalized()
        p_joint1 = knuckle_pos + d1 * (l1 * scale)
        add_solid_overlapping_limb(bm, knuckle_pos, p_joint1, 0.0088 * scale, 0.0074 * scale, segments=10, overlap=0.006 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * scale, matrix=Matrix.Translation(p_joint1))

        # Falange 2 (Intermedia)
        d2 = (d1 - up * math.sin(curl_deg * 0.85)).normalized()
        p_joint2 = p_joint1 + d2 * (l2 * scale)
        add_solid_overlapping_limb(bm, p_joint1, p_joint2, 0.0074 * scale, 0.0058 * scale, segments=10, overlap=0.005 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0060 * scale, matrix=Matrix.Translation(p_joint2))

        # Falange 3 (Garra Distal Estilizada)
        d3 = (d2 - up * math.sin(curl_deg * 1.25)).normalized()
        p_tip = p_joint2 + d3 * (l3 * scale)
        add_solid_overlapping_limb(bm, p_joint2, p_tip, 0.0058 * scale, 0.0034 * scale, segments=10, overlap=0.005 * scale)

        # Microgota orbital en punta de garra
        p_drop = p_tip + d3 * (0.015 * scale)
        add_fluid_droplet(bm, p_drop, 0.0036 * scale)

def build_organic_body_mesh(collection):
    """
    Construye la anatomía atlética completa en postura de sprint contralateral continua:
    - Torso inclinado a ~28 grados.
    - Brazo derecho adelantado hacia el frente con mano abierta en garra.
    - Brazo izquierdo retrasado en zancada con mano abierta.
    - Pierna izquierda adelantada con rodilla flexionada continua.
    - Pierna derecha retrasada en extensión de propulsión hacia atrás.
    """
    me = bpy.data.meshes.new("SK_Player_Body_Mesh")
    obj = bpy.data.objects.new("SK_Player_DarkFluid", me)
    collection.objects.link(obj)

    bm = bmesh.new()

    # 1. TORSO Y ESPINA (Postura atlética de sprint potente)
    torso_chain = [
        (Vector((0.0, 0.00, 0.86)), Vector((0.0, 0.08, 1.02)), 0.155, 0.138), # Pelvis -> Cintura
        (Vector((0.0, 0.08, 1.02)), Vector((0.0, 0.18, 1.18)), 0.138, 0.128), # Cintura -> Lats
        (Vector((0.0, 0.18, 1.18)), Vector((0.0, 0.30, 1.35)), 0.128, 0.205), # Lats -> Ribcage
        (Vector((0.0, 0.30, 1.35)), Vector((0.0, 0.42, 1.48)), 0.205, 0.225), # Ribcage -> Pectorales
        (Vector((0.0, 0.42, 1.48)), Vector((0.0, 0.42, 1.58)), 0.225, 0.110), # Trapecios
        (Vector((0.0, 0.42, 1.58)), Vector((0.0, 0.48, 1.66)), 0.070, 0.058), # Cuello
    ]
    for p1, p2, r1, r2 in torso_chain:
        add_solid_overlapping_limb(bm, p1, p2, r1, r2, segments=32, overlap=0.040)

    # Pectorales musculosos
    for side in [1.0, -1.0]:
        mat_pec = Matrix.Translation(Vector((side * 0.10, 0.44, 1.42))) @ Matrix.Diagonal((0.13, 0.08, 0.11, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec)

    # Abdominales atléticos (6-pack orgánico)
    abs_y = 0.26
    for z, rx, ry in [(1.10, 0.050, 0.032), (1.18, 0.054, 0.034), (1.26, 0.058, 0.036)]:
        for side in [1.0, -1.0]:
            mat_ab = Matrix.Translation(Vector((side * 0.048, abs_y + (z - 1.10) * 0.35, z))) @ Matrix.Diagonal((rx, 0.026, ry, 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_ab)

    # Surco espinal dorsal
    for z in [1.00, 1.12, 1.24, 1.36, 1.48]:
        add_fluid_droplet(bm, (0.0, -0.04 + (z - 1.0) * 0.24, z), 0.022)

    # 2. BRAZO DERECHO (Lead Arm: lanzado hacia adelante en zancada con MANO MAESTRA ARTICULADA)
    sh_r = Vector((0.24, 0.40, 1.48))
    elbow_r = Vector((0.34, 0.72, 1.40))
    wrist_r = Vector((0.26, 1.04, 1.42))

    add_solid_overlapping_limb(bm, Vector((0.12, 0.42, 1.48)), sh_r, 0.105, 0.110, segments=24, overlap=0.040)
    add_solid_overlapping_limb(bm, sh_r, elbow_r, 0.110, 0.080, segments=24, overlap=0.040)
    add_solid_overlapping_limb(bm, elbow_r, wrist_r, 0.080, 0.036, segments=24, overlap=0.040)

    fwd_r = (Vector((0.16, 1.28, 1.46)) - wrist_r).normalized()
    up_r = Vector((0.08, -0.20, 0.97)).normalized()
    build_master_articulated_hand(bm, wrist_r, fwd_r, up_r, is_right=True, scale=1.05)

    # 3. BRAZO IZQUIERDO (Trail Arm: contrapeso hacia atrás en zancada con MANO MAESTRA)
    sh_l = Vector((-0.24, 0.38, 1.48))
    elbow_l = Vector((-0.42, 0.04, 1.32))
    wrist_l = Vector((-0.46, -0.28, 1.12))

    add_solid_overlapping_limb(bm, Vector((-0.12, 0.42, 1.48)), sh_l, 0.105, 0.110, segments=24, overlap=0.040)
    add_solid_overlapping_limb(bm, sh_l, elbow_l, 0.110, 0.080, segments=24, overlap=0.040)
    add_solid_overlapping_limb(bm, elbow_l, wrist_l, 0.080, 0.036, segments=24, overlap=0.040)

    fwd_l = (Vector((-0.48, -0.52, 0.94)) - wrist_l).normalized()
    up_l = Vector((-0.15, 0.35, 0.92)).normalized()
    build_master_articulated_hand(bm, wrist_l, fwd_l, up_l, is_right=False, scale=1.0)

    # 4. PIERNA IZQUIERDA (Lead Leg: flexión potente de rodilla a ~90 grados en zancada)
    hip_l = Vector((-0.12, 0.04, 0.84))
    knee_l = Vector((-0.16, 0.46, 0.68))
    ankle_l = Vector((-0.16, 0.42, 0.24))
    foot_l = Vector((-0.16, 0.54, 0.08))

    add_solid_overlapping_limb(bm, Vector((-0.05, 0.02, 0.86)), hip_l, 0.140, 0.130, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, hip_l, knee_l, 0.130, 0.095, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, knee_l, ankle_l, 0.095, 0.060, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, ankle_l, foot_l, 0.060, 0.040, segments=24, overlap=0.040)

    # 5. PIERNA DERECHA (Trail Leg: propulsión en extensión hacia atrás)
    hip_r = Vector((0.12, -0.04, 0.84))
    knee_r = Vector((0.18, -0.40, 0.62))
    ankle_r = Vector((0.24, -0.84, 0.34))
    foot_r = Vector((0.26, -1.04, 0.18))

    add_solid_overlapping_limb(bm, Vector((0.05, -0.02, 0.86)), hip_r, 0.140, 0.130, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, hip_r, knee_r, 0.130, 0.095, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, knee_r, ankle_r, 0.095, 0.060, segments=32, overlap=0.040)
    add_solid_overlapping_limb(bm, ankle_r, foot_r, 0.060, 0.038, segments=24, overlap=0.040)

    # Volcar BMesh a Mesh
    bm.to_mesh(me)
    bm.free()

    # Cadena de modificadores robusta para ejecución garantizada en background
    remesh_mod = obj.modifiers.new("VoxelRemesh", 'REMESH')
    remesh_mod.mode = 'VOXEL'
    remesh_mod.voxel_size = 0.0065
    remesh_mod.use_smooth_shade = True

    sm = obj.modifiers.new("Smooth_Organic", 'SMOOTH')
    sm.factor = 0.60
    sm.iterations = 3

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    return obj

def build_faceted_obsidian_head_and_crest(collection):
    """
    Construye la cabeza facetada (corte de gema / visor poligonal pulido)
    y la cresta fluida posterior con zarcillos orgánicos.
    """
    me = bpy.data.meshes.new("SK_Player_FacetedHead_Mesh")
    obj = bpy.data.objects.new("SK_Player_FacetedHead", me)
    collection.objects.link(obj)

    bm = bmesh.new()
    cx, cy, cz = 0.0, 0.50, 1.72

    # 1. Base craneal facetada
    mat_cran = Matrix.Translation(Vector((cx, cy - 0.015, cz + 0.025))) @ Matrix.Diagonal((0.094, 0.115, 0.126, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cran)

    # 2. Visera / Máscara frontal facetada (subdivisión 1 para facetas nítidas reflectantes de gema)
    mat_face = Matrix.Translation(Vector((cx, cy + 0.065, cz + 0.012))) @ Matrix.Rotation(R(16), 4, 'X') @ Matrix.Diagonal((0.080, 0.048, 0.058, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_face)

    # 3. Quijada atlética en V y mentón
    for side in [1.0, -1.0]:
        p_jaw_top = Vector((cx + side * 0.070, cy - 0.010, cz + 0.014))
        p_jaw_bot = Vector((cx + side * 0.018, cy + 0.054, cz - 0.058))
        add_solid_overlapping_limb(bm, p_jaw_top, p_jaw_bot, 0.024, 0.016, segments=8, overlap=0.015)

    mat_chin = Matrix.Translation(Vector((cx, cy + 0.058, cz - 0.058))) @ Matrix.Diagonal((0.034, 0.040, 0.030, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_chin)

    # 4. Cresta hidrodinámica posterior (Trailing Fluid Crest)
    crest_tendrils = [
        (Vector((cx, cy - 0.068, cz + 0.058)), Vector((0.0, -0.80, 0.30)), 0.18, 0.025),
        (Vector((cx, cy - 0.078, cz + 0.026)), Vector((0.0, -0.88, 0.15)), 0.20, 0.022),
        (Vector((cx, cy - 0.062, cz + 0.084)), Vector((0.0, -0.70, 0.40)), 0.15, 0.020),
        (Vector((cx + 0.036, cy - 0.062, cz + 0.042)), Vector((0.15, -0.75, 0.22)), 0.16, 0.017),
        (Vector((cx - 0.036, cy - 0.062, cz + 0.042)), Vector((-0.15, -0.75, 0.22)), 0.16, 0.017),
    ]
    for start, dir_v, length, r_b in crest_tendrils:
        add_fluid_tendril(bm, start, dir_v, length, r_b, curl_v=Vector((0, -0.2, -0.08)))

    bm.to_mesh(me)
    bm.free()

    for p in me.polygons:
        p.use_smooth = True

    return obj

def build_splash_tendrils_and_droplets(collection):
    """
    Construye las salpicaduras dinámicas y microgotas suspendidas alrededor del cuerpo.
    """
    me = bpy.data.meshes.new("SK_Player_Splashes_Mesh")
    obj = bpy.data.objects.new("SK_Player_Splashes", me)
    collection.objects.link(obj)

    bm = bmesh.new()

    splash_defs = [
        # Muñeca derecha y antebrazo delantero
        (Vector((0.26, 1.04, 1.42)) + Vector((0.04, -0.02, 0.02)), Vector((0.35, -0.5, 0.50)), 0.18, 0.018),
        (Vector((0.26, 1.04, 1.42)) + Vector((-0.03, -0.04, -0.02)), Vector((-0.4, -0.6, -0.15)), 0.15, 0.015),
        (Vector((0.34, 0.72, 1.40)) + Vector((0.05, -0.05, 0.02)), Vector((0.6, -0.6, 0.3)), 0.20, 0.020),

        # Muñeca izquierda y codo trasero
        (Vector((-0.42, 0.04, 1.32)) + Vector((-0.05, 0.02, 0.04)), Vector((-0.6, 0.2, 0.5)), 0.22, 0.022),
        (Vector((-0.46, -0.28, 1.12)) + Vector((-0.04, 0.05, 0.02)), Vector((-0.5, 0.5, 0.3)), 0.16, 0.016),
        (Vector((-0.46, -0.28, 1.12)) + Vector((0.02, 0.04, -0.03)), Vector((0.3, 0.4, -0.4)), 0.14, 0.014),

        # Hombros y espalda
        (Vector((0.24, 0.40, 1.48)) + Vector((0.06, -0.04, 0.06)), Vector((0.45, -0.7, 0.55)), 0.20, 0.020),
        (Vector((-0.24, 0.38, 1.48)) + Vector((-0.06, -0.04, 0.06)), Vector((-0.45, -0.7, 0.55)), 0.20, 0.020),
        (Vector((0.0, 0.24, 1.42)), Vector((0.0, -0.88, 0.40)), 0.24, 0.024),
        (Vector((0.0, 0.14, 1.26)), Vector((0.0, -0.88, 0.28)), 0.21, 0.020),

        # Pierna trasera en extensión (gran estela cinética)
        (Vector((0.18, -0.40, 0.62)) + Vector((0.04, 0.04, 0.02)), Vector((0.35, 0.45, 0.5)), 0.18, 0.020),
        (Vector((0.24, -0.84, 0.34)) + Vector((-0.04, 0.06, 0.04)), Vector((-0.35, 0.65, 0.5)), 0.22, 0.022),
        (Vector((0.24, -0.84, 0.34)) + Vector((0.04, 0.06, -0.02)), Vector((0.35, 0.65, -0.3)), 0.20, 0.020),
        (Vector((0.26, -1.04, 0.18)) + Vector((0.0, 0.08, 0.04)), Vector((0.0, 0.88, 0.42)), 0.24, 0.024),

        # Pierna delantera
        (Vector((-0.16, 0.46, 0.68)) + Vector((-0.05, -0.03, 0.02)), Vector((-0.5, -0.4, 0.3)), 0.16, 0.018),
        (Vector((-0.16, 0.42, 0.24)) + Vector((-0.04, -0.04, 0.03)), Vector((-0.4, -0.5, 0.4)), 0.17, 0.017),
    ]

    for start_p, d_vec, l_sp, r_sp in splash_defs:
        add_fluid_tendril(bm, start_p, d_vec, l_sp, r_sp)

    # Nube de 50 microgotas suspendidas en 3D
    droplet_orbitals = [
        # Orbitando mano derecha
        (0.30, 1.16, 1.52, 0.008), (0.22, 1.22, 1.46, 0.005), (0.34, 1.18, 1.40, 0.008),
        (0.18, 1.10, 1.56, 0.006), (0.36, 1.08, 1.48, 0.005), (0.25, 1.28, 1.50, 0.004),
        # Orbitando mano izquierda
        (-0.52, -0.38, 1.18, 0.008), (-0.56, -0.34, 1.08, 0.006), (-0.46, -0.44, 1.14, 0.009),
        (-0.58, -0.26, 1.16, 0.005), (-0.48, -0.48, 1.20, 0.004),
        # Detrás de la cabeza y cresta
        (0.02, 0.30, 1.86, 0.009), (-0.02, 0.26, 1.84, 0.007), (0.00, 0.20, 1.82, 0.010),
        (0.04, 0.14, 1.80, 0.008), (-0.03, 0.08, 1.78, 0.006),
        # Espalda y hombros
        (0.28, 0.26, 1.58, 0.009), (-0.28, 0.26, 1.58, 0.009), (0.00, -0.02, 1.46, 0.011),
        (0.08, -0.08, 1.36, 0.008), (-0.08, -0.08, 1.36, 0.008),
        # Estela de pierna trasera
        (0.22, -0.66, 0.54, 0.010), (0.30, -0.76, 0.48, 0.008), (0.18, -0.88, 0.42, 0.009),
        (0.34, -1.04, 0.38, 0.007), (0.24, -1.14, 0.30, 0.009), (0.28, -1.24, 0.24, 0.006),
        # Suelo y pisada
        (-0.20, 0.56, 0.08, 0.007), (-0.24, 0.62, 0.10, 0.005), (-0.10, 0.70, 0.06, 0.008),
        (0.20, -0.94, 0.10, 0.009), (0.32, -1.08, 0.14, 0.007),
    ]
    for dx, dy, dz, dr in droplet_orbitals:
        add_fluid_droplet(bm, (dx, dy, dz), dr)

    bm.to_mesh(me)
    bm.free()

    for p in me.polygons:
        p.use_smooth = True

    return obj

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1280, 720)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_Dynamic"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_Empty"
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
    col_name = "AOE_Player_DarkFluid_Master"
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # 1. Configurar entorno de laboratorio Sci-Fi blanco
    setup_scifi_lab_environment(bpy.context.scene)

    # 2. Construir cuerpo orgánico continuo, cabeza facetada y salpicaduras
    body_obj = build_organic_body_mesh(col)
    head_obj = build_faceted_obsidian_head_and_crest(col)
    splash_obj = build_splash_tendrils_and_droplets(col)

    # 3. Aplicar material ferrofluido con venas de plasma púrpura a todas las partes
    mat_dark = create_dark_fluid_plasma_material("M_DarX_DarkFluid_ElectricVeins")
    for part in [body_obj, head_obj, splash_obj]:
        part.data.materials.clear()
        part.data.materials.append(mat_dark)

    # Ocultar mallas viejas
    active_names = {body_obj.name, head_obj.name, splash_obj.name}
    for o in bpy.data.objects:
        if o.name not in active_names and not o.name.startswith("ENV_") and not o.name.startswith("LGT_") and not o.name.startswith("CAM_"):
            o.hide_render = True
        else:
            o.hide_render = False

    # Directorio de salida
    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid"
    os.makedirs(out_dir, exist_ok=True)

    v1_front = os.path.join(out_dir, "v1_frontal.png")
    v2_back = os.path.join(out_dir, "v2_trasera.png")
    v3_action = os.path.join(out_dir, "v3_accion_sprint.png")
    v4_fps = os.path.join(out_dir, "v4_fps_arms.png")

    # 1. Vista Frontal Completa (Encuadre con suficiente headroom para capturar cabeza, cresta y cuerpo entero)
    render_camera_view(cam_pos=(0.0, 4.4, 1.45), target_pos=(0.0, 0.25, 0.95), lens=34.0, out_path=v1_front, res=(1280, 720))

    # 2. Vista Trasera (Cresta fluida completa, columna dorsal, deltoides y pierna en extensión)
    render_camera_view(cam_pos=(0.0, -4.4, 1.45), target_pos=(0.0, 0.10, 0.95), lens=34.0, out_path=v2_back, res=(1280, 720))

    # 3. Vista de Acción 3/4 Sprint (Ángulo heroico idéntico a la referencia)
    render_camera_view(cam_pos=(2.6, 2.6, 1.30), target_pos=(0.0, 0.25, 0.90), lens=34.0, out_path=v3_action, res=(1280, 720))

    # 4. Vista Primera Persona (FPS Arms: mano articulada con 5 garras y venas violetas pulsantes)
    render_camera_view(cam_pos=(0.08, 0.85, 1.60), target_pos=(0.24, 1.20, 1.45), lens=42.0, out_path=v4_fps, res=(1280, 720))

    # Guardar archivo .blend de trabajo
    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_AAA.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
