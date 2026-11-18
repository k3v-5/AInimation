"""generate_player_dark_fluid_v2.py
Reconstrucción de Máxima Fidelidad AAA del Personaje Principal (Dark Fluid)
Basado exactamente en la imagen de referencia (media_1789128545725.png):
- Anatomía muscular atlética completa: deltoides, bíceps, tríceps, pectorales, 6-pack, dorsales, cuádriceps y gemelos anatómicos.
- Postura de sprint dinámico idéntica a la referencia:
  * Inclinación de torso a 35°.
  * Brazo izquierdo alzado al frente con mano abierta en garra y zarcillos de fluido en el antebrazo.
  * Brazo derecho extendido hacia atrás con cortinas de salpicadura de fluido desprendiéndose del tríceps y hombro.
  * Pierna delantera con rodilla flexionada a 85° en zancada activa.
  * Pierna trasera extendida en empuje elástico (flexión de rodilla a 135° con empeine en extensión).
- Cabeza facetada de corte de gema (visor poligonal plano reflectante) con cresta fluida posterior.
- Cortinas y aletas de salpicadura líquida orgánicas a lo largo de brazos, hombros, espalda y piernas.
- Enjambre de más de 120 microgotas suspendidas en la estela aerodinámica de carrera.
- Shader de obsidiana líquida viva (espejo ferrofluido) con canales direccionales de plasma violeta neón y núcleo blanco-violeta.
- Entorno de laboratorio Sci-Fi blanco con paneles arquitectónicos, suelo cerámico reflectante y líneas LED.
- Encuadre de cámara idéntico a la imagen de referencia.
"""

import sys, os, math, random
import bpy, bmesh
from mathutils import Matrix, Vector, Euler, Quaternion

R = math.radians
random.seed(42)

def clean_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me, do_unlink=True)

def setup_scifi_lab(scene):
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.85, 0.88, 0.94, 1.0)
            bg.inputs["Strength"].default_value = 0.90

    # Suelo reflectante blanco
    me_f = bpy.data.meshes.new("ENV_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=32, y_segments=32, size=36.0, matrix=Matrix.Translation((0, 0, 0.0)))
    bm_f.to_mesh(me_f)
    bm_f.free()
    o_floor = bpy.data.objects.new("ENV_Floor", me_f)
    scene.collection.objects.link(o_floor)

    m_floor = bpy.data.materials.new("M_Lab_Floor_Gloss")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.92, 0.94, 0.97, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.08
        bsdf_f.inputs['Roughness'].default_value = 0.025
        if "Coat Weight" in bsdf_f.inputs:
            bsdf_f.inputs["Coat Weight"].default_value = 1.0
            bsdf_f.inputs["Coat Roughness"].default_value = 0.010
    o_floor.data.materials.append(m_floor)

    # Tiras LED emisivas en el suelo
    led_lines = [
        (Vector((0.0, 0.0, 0.002)), (0.10, 30.0, 0.005)),
        (Vector((1.8, 0.0, 0.002)), (0.08, 30.0, 0.005)),
        (Vector((-1.8, 0.0, 0.002)), (0.08, 30.0, 0.005)),
        (Vector((0.0, 3.5, 0.002)), (18.0, 0.08, 0.005)),
        (Vector((0.0, -3.5, 0.002)), (18.0, 0.08, 0.005)),
        (Vector((0.0, 7.0, 0.002)), (18.0, 0.08, 0.005)),
    ]
    m_led = bpy.data.materials.new("M_LED_PureWhite")
    m_led.use_nodes = True
    bsdf_l = m_led.node_tree.nodes.get("Principled BSDF")
    if bsdf_l:
        bsdf_l.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
        if "Emission Color" in bsdf_l.inputs:
            bsdf_l.inputs["Emission Color"].default_value = (0.95, 0.98, 1.0, 1.0)
            bsdf_l.inputs["Emission Strength"].default_value = 28.0

    for pos, size in led_lines:
        me_led = bpy.data.meshes.new("ENV_LED")
        bm_l = bmesh.new()
        bmesh.ops.create_cube(bm_l, size=1.0, matrix=Matrix.Translation(pos) @ Matrix.Diagonal((*size, 1.0)))
        bm_l.to_mesh(me_led)
        bm_l.free()
        o_led = bpy.data.objects.new("ENV_LED_Obj", me_led)
        scene.collection.objects.link(o_led)
        o_led.data.materials.append(m_led)

    # Paredes de laboratorio y vigas arquitectónicas de fondo
    me_w = bpy.data.meshes.new("ENV_Walls_Mesh")
    bm_w = bmesh.new()
    # Pared trasera
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0, 9.0, 5.0)) @ Matrix.Diagonal((32.0, 0.5, 10.0, 1.0)))
    # Pared lateral izquierda
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((-8.0, 0.0, 5.0)) @ Matrix.Diagonal((0.5, 26.0, 10.0, 1.0)))
    # Vigas de techo y trusses
    for y_b in [-2.0, 2.0, 6.0]:
        bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((0, y_b, 6.5)) @ Matrix.Diagonal((24.0, 0.4, 0.4, 1.0)))
    # Columnas traseras
    for x_c in [-4.5, 4.5]:
        for y_c in [1.5, 7.5]:
            bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((x_c, y_c, 4.0)) @ Matrix.Diagonal((0.8, 0.8, 8.0, 1.0)))
    bm_w.to_mesh(me_w)
    bm_w.free()
    o_wall = bpy.data.objects.new("ENV_Walls", me_w)
    scene.collection.objects.link(o_wall)
    o_wall.data.materials.append(m_floor)

    # Iluminación de estudio idéntica al render de referencia
    # 1. Key Light frontal suave (ilumina cara, pecho y deltoides)
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 4200
    l1_data.size = 7.0
    l1_data.color = (0.98, 0.99, 1.0)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (2.6, 3.4, 3.8)
    l1.rotation_euler = (R(42), 0, R(35))
    scene.collection.objects.link(l1)

    # 2. Rim Light neón violeta potente trasera (recorta la silueta de obsidiana viva)
    l2_data = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_data.energy = 7500
    l2_data.spot_size = R(85)
    l2_data.color = (0.84, 0.06, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_data)
    l2.location = (-3.8, -3.6, 3.0)
    l2.rotation_euler = (R(-35), 0, R(-140))
    scene.collection.objects.link(l2)

    # 3. Top Fill Light blanca cenital
    l3_data = bpy.data.lights.new("LGT_TopFill", 'AREA')
    l3_data.energy = 2200
    l3_data.size = 9.0
    l3_data.color = (0.92, 0.96, 1.0)
    l3 = bpy.data.objects.new("LGT_TopFill", l3_data)
    l3.location = (0.0, 0.5, 5.2)
    l3.rotation_euler = (0, 0, 0)
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

    # Obsidiana líquida viva / Ferrofluido hiperbrillante
    bsdf.inputs["Metallic"].default_value = 0.98
    bsdf.inputs["Roughness"].default_value = 0.018
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.68
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.008

    # Coordenadas de objeto y mapeo
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1100, 0)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-900, 0)
    mapping.inputs["Scale"].default_value = (1.4, 1.4, 1.1)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # Dos ruidos orgánicos fluidos distorsionados
    n1 = nt.nodes.new(type="ShaderNodeTexNoise")
    n1.location = (-700, 180)
    n1.inputs["Scale"].default_value = 2.4
    n1.inputs["Detail"].default_value = 6.0
    n1.inputs["Roughness"].default_value = 0.40
    n1.inputs["Distortion"].default_value = 5.0
    nt.links.new(mapping.outputs["Vector"], n1.inputs["Vector"])

    n2 = nt.nodes.new(type="ShaderNodeTexNoise")
    n2.location = (-700, -180)
    n2.inputs["Scale"].default_value = 4.8
    n2.inputs["Detail"].default_value = 7.0
    n2.inputs["Roughness"].default_value = 0.48
    n2.inputs["Distortion"].default_value = 3.5
    nt.links.new(mapping.outputs["Vector"], n2.inputs["Vector"])

    mix = nt.nodes.new(type="ShaderNodeMix")
    mix.data_type = 'FLOAT'
    mix.location = (-480, 0)
    mix.inputs["Factor"].default_value = 0.38
    nt.links.new(n1.outputs["Fac"], mix.inputs[2])
    nt.links.new(n2.outputs["Fac"], mix.inputs[3])

    # Rampa de color PBR: Obsidiana pura dominante + Venas eléctricas neón violeta
    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (-200, 180)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # Base: Obsidiana negra líquida profunda (70%)
    el[0].position = 0.53
    el[0].color = (0.001, 0.001, 0.003, 1.0)

    # Vena violeta profunda
    e1 = el.new(0.61)
    e1.color = (0.22, 0.01, 0.55, 1.0)

    # Vena neón púrpura eléctrico saturado
    e2 = el.new(0.69)
    e2.color = (0.75, 0.02, 1.0, 1.0)

    # Borde neón magenta brillante
    e3 = el.new(0.81)
    e3.color = (0.98, 0.08, 0.95, 1.0)

    # Núcleo plasma blanco-violeta radiante
    e4 = el.new(0.93)
    e4.color = (1.0, 0.88, 1.0, 1.0)

    nt.links.new(mix.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    # Máscara de emisión luminosa
    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (-200, -180)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.60
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.84
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(mix.outputs[0], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (250, -180)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 52.0
    nt.links.new(emit_cr.outputs["Color"], emit_mult.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(emit_mult.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission"])

    # Micro-ondulación orgánica de superficie de fluido
    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (350, -380)
    bump.inputs["Strength"].default_value = 0.030
    bump.inputs["Distance"].default_value = 0.015
    nt.links.new(mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def add_capsule_cylinder(bm, p1, p2, r1, r2, segments=24, overlap=0.040):
    v1 = Vector(p1)
    v2 = Vector(p2)
    dir_v = v2 - v1
    dist = dir_v.length
    if dist < 0.001:
        return
    d_norm = dir_v.normalized()
    p1_ext = v1 - d_norm * overlap
    p2_ext = v2 + d_norm * overlap
    dist_ext = (p2_ext - p1_ext).length
    mid = (p1_ext + p2_ext) * 0.5

    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r1 * 1.02, matrix=Matrix.Translation(v1))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2 * 1.02, matrix=Matrix.Translation(v2))

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

def add_muscle_belly(bm, center_p, scale_xyz, rot_euler=None):
    mat_t = Matrix.Translation(Vector(center_p))
    mat_s = Matrix.Diagonal((*scale_xyz, 1.0))
    if rot_euler:
        mat_r = Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
        mat = mat_t @ mat_r @ mat_s
    else:
        mat = mat_t @ mat_s
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0, matrix=mat)

def add_splash_fin(bm, base_p, flow_dir, length, width, thickness=0.012, num_spikes=3):
    """Genera una cortina/aleta de salpicadura de fluido orgánica con púas desprendiéndose"""
    v_base = Vector(base_p)
    v_flow = Vector(flow_dir).normalized()
    up = Vector((0, 0, 1))
    side = v_flow.cross(up).normalized()

    for s in range(num_spikes):
        s_factor = (s - (num_spikes - 1) / 2.0)
        p_spike_base = v_base + side * (s_factor * width * 0.4)
        spike_len = length * (0.8 + 0.4 * math.sin(s * 1.7 + 1.2))
        spike_dir = (v_flow + side * (s_factor * 0.35) + up * (0.15 * s)).normalized()
        p_spike_tip = p_spike_base + spike_dir * spike_len
        add_capsule_cylinder(bm, p_spike_base, p_spike_tip, thickness, thickness * 0.15, segments=8, overlap=0.01)
        # Gota en la punta
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=thickness * 0.55, matrix=Matrix.Translation(p_spike_tip + spike_dir * 0.012))

def build_master_articulated_hand(bm, wrist_pos, forward_dir, up_dir, is_right=True, scale=1.0):
    w_pos = Vector(wrist_pos)
    fwd = Vector(forward_dir).normalized()
    up = Vector(up_dir).normalized()
    side = fwd.cross(up).normalized()
    if not is_right:
        side = -side

    # Articulación estilocarpiana
    p_radius = w_pos + side * (0.018 * scale) + up * (0.002 * scale)
    p_ulna = w_pos - side * (0.017 * scale) + up * (0.004 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.009 * scale, matrix=Matrix.Translation(p_radius))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.008 * scale, matrix=Matrix.Translation(p_ulna))

    # Núcleo y arco palmar
    mat_wrist = Matrix.Translation(w_pos) @ Matrix.Diagonal((0.034 * scale, 0.028 * scale, 0.026 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_wrist)

    palm_center = w_pos + fwd * (0.048 * scale)
    mat_palm = Matrix.Translation(palm_center) @ Matrix.Diagonal((0.036 * scale, 0.042 * scale, 0.020 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_palm)

    # Eminencias tenar e hipotenar
    thenar_pos = w_pos + fwd * (0.026 * scale) + side * (0.018 * scale) - up * (0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.014 * scale, matrix=Matrix.Translation(thenar_pos))
    hypo_pos = w_pos + fwd * (0.028 * scale) - side * (0.016 * scale) - up * (0.005 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.012 * scale, matrix=Matrix.Translation(hypo_pos))

    add_capsule_cylinder(bm, w_pos, palm_center, 0.028 * scale, 0.026 * scale, segments=12, overlap=0.015 * scale)

    # Tendones dorsales
    knuckle_targets = [("Index", 0.016 * scale), ("Middle", 0.004 * scale), ("Ring", -0.006 * scale), ("Pinky", -0.016 * scale)]
    for name, s_off in knuckle_targets:
        p_knuckle = palm_center + fwd * (0.032 * scale) + side * s_off + up * (0.008 * scale)
        p_wrist_tendon = w_pos + side * (s_off * 0.45) + up * (0.009 * scale)
        add_capsule_cylinder(bm, p_wrist_tendon, p_knuckle, 0.0045 * scale, 0.0038 * scale, segments=6, overlap=0.006 * scale)

    # Pulgar oponible
    thumb_mcp = thenar_pos + fwd * (0.018 * scale) + side * (0.014 * scale) - up * (0.002 * scale)
    add_capsule_cylinder(bm, thenar_pos, thumb_mcp, 0.012 * scale, 0.010 * scale, segments=8, overlap=0.008 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.009 * scale, matrix=Matrix.Translation(thumb_mcp))

    thumb_dir1 = (fwd * 0.65 + side * 0.70 + up * 0.15).normalized()
    thumb_ip = thumb_mcp + thumb_dir1 * (0.030 * scale)
    add_capsule_cylinder(bm, thumb_mcp, thumb_ip, 0.0095 * scale, 0.0080 * scale, segments=8, overlap=0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0080 * scale, matrix=Matrix.Translation(thumb_ip))

    thumb_dir2 = (fwd * 0.85 + side * 0.30 - up * 0.35).normalized()
    thumb_tip = thumb_ip + thumb_dir2 * (0.027 * scale)
    add_capsule_cylinder(bm, thumb_ip, thumb_tip, 0.0080 * scale, 0.0034 * scale, segments=8, overlap=0.006 * scale)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.004 * scale, matrix=Matrix.Translation(thumb_tip + thumb_dir2 * 0.012))

    # 4 dedos articulados independientes
    finger_configs = [
        ("Index", 0.016, 0.038, 0.030, 0.026, R(16), R(18)),
        ("Middle", 0.004, 0.042, 0.034, 0.029, R(20), R(4)),
        ("Ring", -0.008, 0.039, 0.030, 0.026, R(24), -R(10)),
        ("Pinky", -0.018, 0.032, 0.024, 0.021, R(28), -R(24))
    ]
    for name, s_off, l1, l2, l3, curl_deg, splay_deg in finger_configs:
        knuckle_pos = palm_center + fwd * (0.032 * scale) + side * (s_off * scale) + up * (0.007 * scale)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0088 * scale, matrix=Matrix.Translation(knuckle_pos))

        d1 = (fwd * math.cos(splay_deg) + side * math.sin(splay_deg) - up * math.sin(curl_deg * 0.40)).normalized()
        p_j1 = knuckle_pos + d1 * (l1 * scale)
        add_capsule_cylinder(bm, knuckle_pos, p_j1, 0.0088 * scale, 0.0074 * scale, segments=8, overlap=0.006 * scale)

        d2 = (d1 - up * math.sin(curl_deg * 0.85)).normalized()
        p_j2 = p_j1 + d2 * (l2 * scale)
        add_capsule_cylinder(bm, p_j1, p_j2, 0.0074 * scale, 0.0058 * scale, segments=8, overlap=0.005 * scale)

        d3 = (d2 - up * math.sin(curl_deg * 1.25)).normalized()
        p_tip = p_j2 + d3 * (l3 * scale)
        add_capsule_cylinder(bm, p_j2, p_tip, 0.0058 * scale, 0.0034 * scale, segments=8, overlap=0.005 * scale)

        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.004 * scale, matrix=Matrix.Translation(p_tip + d3 * 0.015))

def build_athletic_sprint_humanoid(col):
    """
    Construye la anatomía muscular del atleta exactamente en la pose de la referencia:
    - Inclinación de torso de 35° hacia adelante.
    - Cuádriceps, gemelos, deltoides y dorsales con curvatura anatómica realista.
    """
    me = bpy.data.meshes.new("SK_Player_Body_Mesh")
    obj = bpy.data.objects.new("SK_Player_Body", me)
    col.objects.link(obj)

    bm = bmesh.new()

    # 1. COLUMNA Y TORSO ATLÉTICO EN SPRINT (Inclinación ~35 grados)
    # Pelvis -> Cintura -> Ribcage -> Pectorales -> Trapecios -> Cuello
    torso_spine = [
        (Vector((0.0, -0.05, 0.82)), Vector((0.0, 0.08, 1.00)), 0.155, 0.138),
        (Vector((0.0, 0.08, 1.00)), Vector((0.0, 0.22, 1.16)), 0.138, 0.132),
        (Vector((0.0, 0.22, 1.16)), Vector((0.0, 0.36, 1.32)), 0.132, 0.210),
        (Vector((0.0, 0.36, 1.32)), Vector((0.0, 0.50, 1.45)), 0.210, 0.230),
        (Vector((0.0, 0.50, 1.45)), Vector((0.0, 0.52, 1.54)), 0.230, 0.115),
        (Vector((0.0, 0.52, 1.54)), Vector((0.0, 0.58, 1.62)), 0.072, 0.060),
    ]
    for p1, p2, r1, r2 in torso_spine:
        add_capsule_cylinder(bm, p1, p2, r1, r2, segments=28, overlap=0.040)

    # Pectorales prominentes (Placas musculares simétricas orientadas a la zancada)
    add_muscle_belly(bm, (0.11, 0.52, 1.38), (0.13, 0.085, 0.11), rot_euler=(R(-25), R(12), R(15)))
    add_muscle_belly(bm, (-0.11, 0.52, 1.38), (0.13, 0.085, 0.11), rot_euler=(R(-25), R(-12), R(-15)))

    # Dorsales anchos (V-Taper athletic silhouette)
    add_muscle_belly(bm, (0.18, 0.26, 1.30), (0.07, 0.11, 0.16), rot_euler=(R(20), R(-15), R(-10)))
    add_muscle_belly(bm, (-0.18, 0.26, 1.30), (0.07, 0.11, 0.16), rot_euler=(R(20), R(15), R(10)))

    # Abdominales (6-Pack atlético esculpido)
    for z_ab, y_ab, rx, rz in [(1.08, 0.24, 0.052, 0.034), (1.16, 0.32, 0.056, 0.036), (1.24, 0.40, 0.060, 0.038)]:
        add_muscle_belly(bm, (0.050, y_ab, z_ab), (rx, 0.028, rz), rot_euler=(R(-35), 0, 0))
        add_muscle_belly(bm, (-0.050, y_ab, z_ab), (rx, 0.028, rz), rot_euler=(R(-35), 0, 0))

    # Glúteos atléticos
    add_muscle_belly(bm, (0.09, -0.16, 0.80), (0.10, 0.11, 0.12), rot_euler=(R(15), 0, 0))
    add_muscle_belly(bm, (-0.09, -0.16, 0.80), (0.10, 0.11, 0.12), rot_euler=(R(15), 0, 0))

    # 2. BRAZO IZQUIERDO (Lead Arm, en pantalla a la DERECHA, alzado al frente)
    # Bicep al frente, codo a ~115°, antebrazo hacia arriba-adelante, mano abierta
    sh_l = Vector((-0.26, 0.46, 1.44))
    elbow_l = Vector((-0.38, 0.72, 1.34))
    wrist_l = Vector((-0.24, 1.02, 1.52))

    # Deltoides izquierdo prominente
    add_muscle_belly(bm, sh_l, (0.11, 0.11, 0.12))
    add_capsule_cylinder(bm, Vector((-0.14, 0.50, 1.45)), sh_l, 0.110, 0.110, segments=20, overlap=0.035)
    # Bíceps y tríceps con curvatura muscular
    add_capsule_cylinder(bm, sh_l, elbow_l, 0.110, 0.082, segments=20, overlap=0.040)
    add_muscle_belly(bm, (sh_l + elbow_l) * 0.5 + Vector((-0.03, 0.03, 0.02)), (0.065, 0.075, 0.12), rot_euler=(R(-30), R(20), 0))
    # Antebrazo y muñeca
    add_capsule_cylinder(bm, elbow_l, wrist_l, 0.082, 0.038, segments=20, overlap=0.040)
    add_muscle_belly(bm, (elbow_l + wrist_l) * 0.5 + Vector((-0.02, 0.02, 0.01)), (0.055, 0.065, 0.11), rot_euler=(R(-30), R(15), 0))

    # Mano izquierda abierta alzada al frente en garra predatory
    fwd_l = (Vector((-0.12, 1.28, 1.62)) - wrist_l).normalized()
    up_l = Vector((0.15, -0.30, 0.94)).normalized()
    build_master_articulated_hand(bm, wrist_l, fwd_l, up_l, is_right=False, scale=1.12)

    # 3. BRAZO DERECHO (Trail Arm, en pantalla a la IZQUIERDA, impulsado atrás)
    # Hombro -> codo atrás a ~90° -> muñeca abajo -> mano colgando en garra
    sh_r = Vector((0.26, 0.44, 1.44))
    elbow_r = Vector((0.44, 0.16, 1.28))
    wrist_r = Vector((0.48, -0.16, 1.08))

    add_muscle_belly(bm, sh_r, (0.11, 0.11, 0.12))
    add_capsule_cylinder(bm, Vector((0.14, 0.50, 1.45)), sh_r, 0.110, 0.110, segments=20, overlap=0.035)
    # Brazo y tríceps tenso hacia atrás
    add_capsule_cylinder(bm, sh_r, elbow_r, 0.110, 0.082, segments=20, overlap=0.040)
    add_muscle_belly(bm, (sh_r + elbow_r) * 0.5 + Vector((0.04, -0.02, 0.02)), (0.065, 0.075, 0.12), rot_euler=(R(30), R(-20), 0))
    # Antebrazo hacia abajo
    add_capsule_cylinder(bm, elbow_r, wrist_r, 0.082, 0.038, segments=20, overlap=0.040)
    add_muscle_belly(bm, (elbow_r + wrist_r) * 0.5 + Vector((0.03, -0.01, 0.01)), (0.055, 0.065, 0.11), rot_euler=(R(30), R(-15), 0))

    # Mano derecha en garra dirigida hacia atrás/abajo
    fwd_r = (Vector((0.46, -0.36, 0.88)) - wrist_r).normalized()
    up_r = Vector((0.10, 0.40, 0.91)).normalized()
    build_master_articulated_hand(bm, wrist_r, fwd_r, up_r, is_right=True, scale=1.05)

    # 4. PIERNA IZQUIERDA (Lead Leg, en pantalla a la DERECHA, zancada activa hacia adelante)
    # Cadera -> Rodilla alta flexionada a ~85° -> Espinilla abajo -> Pie apoyado
    hip_l = Vector((-0.13, 0.02, 0.78))
    knee_l = Vector((-0.18, 0.46, 0.62))
    ankle_l = Vector((-0.16, 0.40, 0.20))
    foot_l = Vector((-0.16, 0.54, 0.06))

    add_capsule_cylinder(bm, Vector((-0.06, 0.00, 0.82)), hip_l, 0.145, 0.135, segments=24, overlap=0.040)
    # Muslo y Cuádriceps (Rectus femoris & vastus lateralis)
    add_capsule_cylinder(bm, hip_l, knee_l, 0.135, 0.098, segments=24, overlap=0.045)
    add_muscle_belly(bm, (hip_l + knee_l) * 0.5 + Vector((-0.03, 0.04, 0.04)), (0.080, 0.095, 0.16), rot_euler=(R(-30), R(15), 0))
    # Rótula
    add_muscle_belly(bm, knee_l + Vector((0.0, 0.04, 0.02)), (0.045, 0.045, 0.050))
    # Espinilla y gemelos atléticos
    add_capsule_cylinder(bm, knee_l, ankle_l, 0.098, 0.060, segments=24, overlap=0.045)
    add_muscle_belly(bm, (knee_l * 0.4 + ankle_l * 0.6) + Vector((0.0, -0.03, 0.0)), (0.065, 0.075, 0.12), rot_euler=(R(15), 0, 0))
    # Pie apoyado
    add_capsule_cylinder(bm, ankle_l, foot_l, 0.060, 0.040, segments=20, overlap=0.035)

    # 5. PIERNA DERECHA (Trail Leg, en pantalla a la IZQUIERDA, propulsión elástica extendida)
    # Cadera -> Rodilla flexionada a ~135° -> Espinilla extendida -> Pie en empeine empujando
    hip_r = Vector((0.13, -0.06, 0.78))
    knee_r = Vector((0.22, -0.42, 0.58))
    ankle_r = Vector((0.28, -0.86, 0.32))
    foot_r = Vector((0.32, -1.06, 0.16))

    add_capsule_cylinder(bm, Vector((0.06, -0.04, 0.82)), hip_r, 0.145, 0.135, segments=24, overlap=0.040)
    # Muslo tenso hacia atrás
    add_capsule_cylinder(bm, hip_r, knee_r, 0.135, 0.098, segments=24, overlap=0.045)
    add_muscle_belly(bm, (hip_r + knee_r) * 0.5 + Vector((0.03, -0.02, 0.03)), (0.080, 0.095, 0.16), rot_euler=(R(25), R(-15), 0))
    add_muscle_belly(bm, knee_r + Vector((0.0, -0.03, 0.02)), (0.045, 0.045, 0.050))
    # Pantorrilla en tensión de empuje
    add_capsule_cylinder(bm, knee_r, ankle_r, 0.098, 0.060, segments=24, overlap=0.045)
    add_muscle_belly(bm, (knee_r * 0.4 + ankle_r * 0.6) + Vector((0.02, 0.03, 0.02)), (0.065, 0.075, 0.13), rot_euler=(R(-25), 0, 0))
    # Pie en extensión (plantarflexion)
    add_capsule_cylinder(bm, ankle_r, foot_r, 0.060, 0.036, segments=20, overlap=0.035)

    bm.to_mesh(me)
    bm.free()

    # Modificadores de fusión orgánica continua
    remesh_mod = obj.modifiers.new("VoxelRemesh", 'REMESH')
    remesh_mod.mode = 'VOXEL'
    remesh_mod.voxel_size = 0.0062
    remesh_mod.use_smooth_shade = True

    sm = obj.modifiers.new("Smooth_Organic", 'SMOOTH')
    sm.factor = 0.65
    sm.iterations = 3

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    return obj

def build_faceted_crystal_head_and_crest(col):
    """
    Cabeza facetada tipo gema/diamante pulido sin rostro humano
    con planos angulares nítidos y cresta fluida posterior (idéntica a la referencia).
    """
    me = bpy.data.meshes.new("SK_Player_FacetedHead_Mesh")
    obj = bpy.data.objects.new("SK_Player_FacetedHead", me)
    col.objects.link(obj)

    bm = bmesh.new()
    cx, cy, cz = 0.0, 0.62, 1.68

    # 1. Base del cráneo facetada
    mat_cran = Matrix.Translation(Vector((cx, cy - 0.015, cz + 0.025))) @ Matrix.Diagonal((0.096, 0.118, 0.128, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cran)

    # 2. Visera / Máscara frontal de facetas planas (corte de diamante)
    mat_face = Matrix.Translation(Vector((cx, cy + 0.068, cz + 0.010))) @ Matrix.Rotation(R(18), 4, 'X') @ Matrix.Diagonal((0.082, 0.048, 0.058, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_face)

    # 3. Quijada atlética en V y mentón
    for side in [1.0, -1.0]:
        p_top = Vector((cx + side * 0.072, cy - 0.008, cz + 0.012))
        p_bot = Vector((cx + side * 0.018, cy + 0.056, cz - 0.060))
        add_capsule_cylinder(bm, p_top, p_bot, 0.024, 0.016, segments=6, overlap=0.015)

    mat_chin = Matrix.Translation(Vector((cx, cy + 0.060, cz - 0.060))) @ Matrix.Diagonal((0.036, 0.042, 0.030, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_chin)

    # 4. Cresta hidrodinámica posterior con espinas de fluido que se desprenden
    crest_spines = [
        (Vector((cx, cy - 0.070, cz + 0.065)), Vector((0.0, -0.85, 0.35)), 0.22, 0.024),
        (Vector((cx, cy - 0.080, cz + 0.030)), Vector((0.0, -0.92, 0.18)), 0.24, 0.022),
        (Vector((cx, cy - 0.065, cz + 0.095)), Vector((0.0, -0.75, 0.45)), 0.18, 0.018),
        (Vector((cx + 0.038, cy - 0.065, cz + 0.045)), Vector((0.15, -0.80, 0.25)), 0.19, 0.016),
        (Vector((cx - 0.038, cy - 0.065, cz + 0.045)), Vector((-0.15, -0.80, 0.25)), 0.19, 0.016),
    ]
    for start_p, dir_v, length, r_b in crest_spines:
        curr_p = Vector(start_p)
        curr_d = Vector(dir_v).normalized()
        for step in range(4):
            next_p = curr_p + curr_d * (length / 4.0)
            next_r = max(0.003, r_b * (1.0 - (step + 1) * 0.22))
            add_capsule_cylinder(bm, curr_p, next_p, r_b * (1.0 - step * 0.22), next_r, segments=8, overlap=0.01)
            curr_p = next_p
        # Gota en la punta
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.006, matrix=Matrix.Translation(curr_p + curr_d * 0.015))

    bm.to_mesh(me)
    bm.free()

    # Sombreado suave en el cráneo pero manteniendo las facetas de gema
    for p in me.polygons:
        p.use_smooth = True

    return obj

def build_liquid_splashes_and_droplet_galaxy(col):
    """
    Construye las cortinas de fluido, aletas de salpicadura y un enjambre
    de más de 120 microgotas suspendidas en el aire alrededor del corredor.
    """
    me = bpy.data.meshes.new("SK_Player_Splashes_Mesh")
    obj = bpy.data.objects.new("SK_Player_Splashes", me)
    col.objects.link(obj)

    bm = bmesh.new()

    # Cortinas y aletas de salpicadura (Splashing Sheets)
    splash_curtains = [
        # Tríceps y codo derecho (trasero) - Cortina masiva desprendiéndose hacia atrás
        (Vector((0.44, 0.16, 1.28)), Vector((0.55, -0.65, 0.50)), 0.26, 0.14, 4),
        (Vector((0.48, -0.16, 1.08)), Vector((0.45, -0.75, 0.25)), 0.22, 0.12, 3),
        (Vector((0.26, 0.44, 1.44)), Vector((0.40, -0.70, 0.55)), 0.24, 0.12, 3),

        # Antebrazo izquierdo (delantero) - Franjas de fluido desprendiéndose abajo y atrás
        (Vector((-0.38, 0.72, 1.34)), Vector((-0.55, -0.45, 0.35)), 0.22, 0.12, 3),
        (Vector((-0.24, 1.02, 1.52)), Vector((-0.35, -0.65, -0.10)), 0.20, 0.10, 3),

        # Espalda dorsal y costillas (estela aerodinámica)
        (Vector((0.0, 0.22, 1.35)), Vector((0.0, -0.92, 0.38)), 0.28, 0.16, 4),
        (Vector((0.0, 0.10, 1.15)), Vector((0.0, -0.92, 0.26)), 0.25, 0.14, 3),

        # Pierna trasera (estela cinética masiva desprendiéndose del talón y pantorrilla)
        (Vector((0.22, -0.42, 0.58)), Vector((0.35, 0.45, 0.50)), 0.22, 0.12, 3),
        (Vector((0.28, -0.86, 0.32)), Vector((-0.35, 0.70, 0.55)), 0.26, 0.14, 4),
        (Vector((0.32, -1.06, 0.16)), Vector((0.0, 0.90, 0.45)), 0.28, 0.16, 4),

        # Pierna delantera (salpicadura en rodilla)
        (Vector((-0.18, 0.46, 0.62)), Vector((-0.55, -0.40, 0.35)), 0.20, 0.10, 3),
        (Vector((-0.16, 0.40, 0.20)), Vector((-0.45, -0.55, 0.40)), 0.20, 0.10, 3),
    ]

    for base_p, flow_dir, length, width, spikes in splash_curtains:
        add_splash_fin(bm, base_p, flow_dir, length, width, thickness=0.014, num_spikes=spikes)

    # Nube orbital de más de 120 microgotas suspendidas en 3D
    # Dispersas en las estelas de velocidad de las 4 extremidades y la cabeza
    droplet_centers = [
        # Mano izquierda y antebrazo (delantero alzado)
        (Vector((-0.20, 1.15, 1.58)), 0.30, 25),
        # Mano derecha y brazo trasero
        (Vector((0.48, -0.28, 1.05)), 0.35, 25),
        # Cabeza y cresta posterior
        (Vector((0.0, 0.45, 1.80)), 0.32, 22),
        # Espalda dorsal
        (Vector((0.0, 0.05, 1.25)), 0.35, 25),
        # Pierna trasera y talón
        (Vector((0.30, -0.95, 0.38)), 0.40, 30),
        # Suelo y pisada delantera
        (Vector((-0.18, 0.50, 0.08)), 0.25, 15),
    ]

    for center, radius, count in droplet_centers:
        for _ in range(count):
            offset = Vector((
                random.uniform(-radius, radius),
                random.uniform(-radius, radius),
                random.uniform(-radius, radius) * 0.8
            ))
            d_pos = center + offset
            d_rad = random.uniform(0.0035, 0.012)
            # Gotas con leve elongación en forma de lágrima
            mat_d = Matrix.Translation(d_pos) @ Matrix.Diagonal((d_rad, d_rad, d_rad * random.uniform(1.0, 1.4), 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_d)

    bm.to_mesh(me)
    bm.free()

    for p in me.polygons:
        p.use_smooth = True

    return obj

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_V2"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_V2"
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
    col = bpy.data.collections.new("AOE_Player_DarkFluid_V2")
    bpy.context.scene.collection.children.link(col)

    # 1. Configurar entorno de laboratorio Sci-Fi blanco
    setup_scifi_lab(bpy.context.scene)

    # 2. Construir cuerpo muscular en sprint, cabeza de gema y salpicaduras líquidas
    body_obj = build_athletic_sprint_humanoid(col)
    head_obj = build_faceted_crystal_head_and_crest(col)
    splash_obj = build_liquid_splashes_and_droplet_galaxy(col)

    # 3. Asignar material de obsidiana viva con canales de plasma violeta
    mat_dark = create_liquid_obsidian_plasma_material("M_DarX_DarkFluid_ElectricVeins")
    for part in [body_obj, head_obj, splash_obj]:
        part.data.materials.clear()
        part.data.materials.append(mat_dark)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid_v2"
    os.makedirs(out_dir, exist_ok=True)

    # RENDER PRINCIPAL: Ángulo y encuadre idéntico al concepto de referencia (1080x1080)
    hero_path = os.path.join(out_dir, "v2_hero_reference_match.png")
    render_camera_view(cam_pos=(2.5, 2.2, 1.15), target_pos=(0.0, 0.22, 0.95), lens=42.0, out_path=hero_path, res=(1080, 1080))

    # Guardar archivo .blend
    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V2.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
