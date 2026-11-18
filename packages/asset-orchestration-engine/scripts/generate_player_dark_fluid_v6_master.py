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
        bg.inputs["Color"].default_value = (0.92, 0.94, 0.97, 1.0)
        bg.inputs["Strength"].default_value = 1.2

    # Suelo reflectante blanco
    m_floor = bpy.data.materials.new(name="M_LabFloor")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs["Base Color"].default_value = (0.93, 0.95, 0.97, 1.0)
        bsdf_f.inputs["Roughness"].default_value = 0.12
        if "Specular IOR Level" in bsdf_f.inputs:
            bsdf_f.inputs["Specular IOR Level"].default_value = 0.8
        elif "Specular" in bsdf_f.inputs:
            bsdf_f.inputs["Specular"].default_value = 0.8

    me_floor = bpy.data.meshes.new("ENV_Floor_Mesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=4, y_segments=4, size=40.0)
    bm_f.to_mesh(me_floor)
    bm_f.free()
    o_floor = bpy.data.objects.new("ENV_Floor", me_floor)
    scene.collection.objects.link(o_floor)
    o_floor.data.materials.append(m_floor)

    # Tiras LED emisivas blancas
    m_led = bpy.data.materials.new(name="M_FloorLED")
    m_led.use_nodes = True
    bsdf_l = m_led.node_tree.nodes.get("Principled BSDF")
    if bsdf_l:
        bsdf_l.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
        if "Emission Color" in bsdf_l.inputs:
            bsdf_l.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            bsdf_l.inputs["Emission Strength"].default_value = 20.0
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

    # Paredes Sci-Fi
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

    # Iluminación de estudio
    l1_d = bpy.data.lights.new("LGT_FrontKey", 'AREA')
    l1_d.energy = 6000.0
    l1_d.size = 8.0
    l1_d.color = (0.98, 0.99, 1.0)
    l1 = bpy.data.objects.new("LGT_FrontKey", l1_d)
    l1.location = (2.8, 3.0, 3.5)
    l1.rotation_euler = (R(42), R(12), R(38))
    scene.collection.objects.link(l1)

    l2_d = bpy.data.lights.new("LGT_RimViolet", 'SPOT')
    l2_d.energy = 10500.0
    l2_d.spot_size = R(92)
    l2_d.color = (0.86, 0.06, 1.0)
    l2 = bpy.data.objects.new("LGT_RimViolet", l2_d)
    l2.location = (-4.0, -4.0, 3.0)
    l2.rotation_euler = (R(-38), R(15), R(-135))
    scene.collection.objects.link(l2)

    l3_d = bpy.data.lights.new("LGT_TopFill", 'AREA')
    l3_d.energy = 2600.0
    l3_d.size = 12.0
    l3_d.color = (0.94, 0.97, 1.0)
    l3 = bpy.data.objects.new("LGT_TopFill", l3_d)
    l3.location = (0.0, 0.0, 6.0)
    scene.collection.objects.link(l3)

def create_liquid_obsidian_plasma_material(name="M_DarX_DarkFluid_ElectricVeins"):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1600, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (1200, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Base: Obsidiana líquida negra hiperreflectante
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

    # Lectura del Color Attribute "Plasma" pintado anatómicamente
    attr = nt.nodes.new(type="ShaderNodeAttribute")
    attr.location = (-1000, 200)
    attr.attribute_name = "Plasma"

    # Texturas procedurales para detalle eléctrico dentro de las venas
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    tex_coord.location = (-1000, -150)

    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.location = (-800, -150)
    mapping.inputs["Scale"].default_value = (2.5, 2.5, 0.6)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    voro = nt.nodes.new(type="ShaderNodeTexVoronoi")
    voro.location = (-580, -50)
    voro.voronoi_dimensions = '3D'
    voro.feature = 'SMOOTH_F1' if hasattr(voro, 'feature') else 'F1'
    voro.inputs["Scale"].default_value = 4.2
    nt.links.new(mapping.outputs["Vector"], voro.inputs["Vector"])

    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-580, -250)
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 3.5
    noise.inputs["Roughness"].default_value = 0.55
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    tex_mix = nt.nodes.new(type="ShaderNodeMix")
    tex_mix.location = (-350, -150)
    tex_mix.data_type = 'FLOAT'
    tex_mix.blend_type = 'MULTIPLY'
    tex_mix.inputs["Factor"].default_value = 0.85
    nt.links.new(voro.outputs[0], tex_mix.inputs[2])
    nt.links.new(noise.outputs["Fac"], tex_mix.inputs[3])

    # Modular el atributo anatómico con la turbulencia de plasma
    plasma_mult = nt.nodes.new(type="ShaderNodeMath")
    plasma_mult.location = (-120, 50)
    plasma_mult.operation = 'MULTIPLY'
    nt.links.new(attr.outputs["Fac"], plasma_mult.inputs[0])
    nt.links.new(tex_mix.outputs[0], plasma_mult.inputs[1])

    # ColorRamp para el gradiente de plasma púrpura/magenta eléctrico
    cr = nt.nodes.new(type="ShaderNodeValToRGB")
    cr.location = (150, 100)
    el = cr.color_ramp.elements
    el.remove(el[1])

    # Base: Obsidiana pura negra
    el[0].position = 0.12
    el[0].color = (0.001, 0.001, 0.002, 1.0)

    # Violeta oscuro terciopelo
    e1 = el.new(0.24)
    e1.color = (0.22, 0.01, 0.55, 1.0)

    # Púrpura neón eléctrico saturado
    e2 = el.new(0.42)
    e2.color = (0.76, 0.00, 1.0, 1.0)

    # Magenta brillante
    e3 = el.new(0.68)
    e3.color = (0.98, 0.12, 0.96, 1.0)

    # Núcleo blanco-lavanda radiante
    e4 = el.new(0.86)
    e4.color = (1.0, 0.95, 1.0, 1.0)

    nt.links.new(plasma_mult.outputs["Value"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

    # Máscara de emisión luminosa
    emit_cr = nt.nodes.new(type="ShaderNodeValToRGB")
    emit_cr.location = (150, -180)
    eel = emit_cr.color_ramp.elements
    eel[0].position = 0.16
    eel[0].color = (0, 0, 0, 1)
    eel[1].position = 0.72
    eel[1].color = (1, 1, 1, 1)
    nt.links.new(plasma_mult.outputs["Value"], emit_cr.inputs["Fac"])

    emit_mult = nt.nodes.new(type="ShaderNodeMath")
    emit_mult.location = (450, -180)
    emit_mult.operation = 'MULTIPLY'
    emit_mult.inputs[1].default_value = 65.0
    nt.links.new(emit_cr.outputs["Color"], emit_mult.inputs[0])

    if "Emission Color" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission Color"])
        nt.links.new(emit_mult.outputs["Value"], bsdf.inputs["Emission Strength"])
    elif "Emission" in bsdf.inputs:
        nt.links.new(cr.outputs["Color"], bsdf.inputs["Emission"])

    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.location = (650, -380)
    bump.inputs["Strength"].default_value = 0.020
    bump.inputs["Distance"].default_value = 0.012
    nt.links.new(tex_mix.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def build_master_player_v6(col):
    """
    Construcción poligonal anatómica precisa:
    - Torso y extremidades con musculatura atlética definida (pectoral, 6-pack, deltoides).
    - Cabeza con visera facetada de diamante / stealth cut y cresta fluida.
    - Manos con 5 dedos extendidos en garra de sprint.
    - Pintado anatómico del canal 'Plasma' para guiar las venas eléctricas con exactitud.
    - Gotas orbitales de ferrofluido y cortinas desprendiéndose.
    """
    me = bpy.data.meshes.new("SK_Player_Master_Mesh")
    bm = bmesh.new()

    # --- 1. TORSO ANATÓMICO CON LOFTING DE ANILLOS (16 vértices por anillo) ---
    # Inclinado 38° hacia adelante en zancada de sprint
    cross_sections = [
        # (cx, cy, cz, rx, ry, front_pec, abs_fac, back_flat)
        (0.00, 0.00, 0.84, 0.165, 0.130, 0.00, 0.00, 0.015), # Pelvis / Cadera
        (0.02, 0.10, 0.96, 0.145, 0.115, 0.00, 0.02, 0.012), # Cintura baja
        (0.04, 0.20, 1.08, 0.138, 0.108, 0.00, 0.035, 0.010), # Cintura media (oblicuos)
        (0.06, 0.30, 1.20, 0.165, 0.125, 0.01, 0.040, 0.015), # Arco costal / Abs sup
        (0.07, 0.38, 1.30, 0.198, 0.150, 0.045, 0.020, 0.025), # Pectoral bajo
        (0.08, 0.44, 1.38, 0.225, 0.165, 0.065, 0.000, 0.030), # Pectoral medio (máximo)
        (0.08, 0.50, 1.45, 0.220, 0.150, 0.040, 0.000, 0.035), # Clavículas
        (0.08, 0.54, 1.50, 0.170, 0.120, 0.010, 0.000, 0.040), # Hombros / Trapecios
        (0.08, 0.58, 1.55, 0.100, 0.095, 0.000, 0.000, 0.015), # Cuello base
        (0.08, 0.62, 1.60, 0.085, 0.080, 0.000, 0.000, 0.010), # Cuello medio
        (0.08, 0.65, 1.64, 0.090, 0.090, 0.000, 0.000, 0.010), # Base cráneo
    ]

    ring_verts = []
    for cx, cy, cz, rx, ry, f_pec, f_abs, b_flat in cross_sections:
        ring = []
        for i in range(16):
            theta = 2.0 * math.pi * i / 16.0
            x_b = rx * math.cos(theta)
            y_b = ry * math.sin(theta)

            # Modulación de pectorales: dos lóbulos frontales prominentes con surco esternal
            if y_b > 0 and f_pec > 0:
                pec_bump = math.sin(theta) * abs(math.cos(theta)) * 2.2
                y_b += f_pec * pec_bump
            # Modulación de abdominales: 6-pack central
            elif y_b > 0 and f_abs > 0:
                abs_bump = math.sin(theta) * (0.8 + 0.6 * math.cos(2 * theta))
                y_b += f_abs * abs_bump
            # Espalda: surco espinal
            elif y_b < 0 and b_flat > 0:
                y_b += b_flat * (0.25 - 0.75 * abs(math.cos(theta)))

            pos = Vector((cx + x_b, cy + y_b, cz))
            v = bm.verts.new(pos)
            ring.append(v)
        ring_verts.append(ring)

    for r in range(len(ring_verts) - 1):
        r1 = ring_verts[r]
        r2 = ring_verts[r + 1]
        for i in range(16):
            i_next = (i + 1) % 16
            bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])

    # Tapa de pelvis inferior
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=[bm.edges.get([ring_verts[0][i], ring_verts[0][(i+1)%16]]) for i in range(16)])

    # --- 2. CABEZA FACETADA DE CORTE DE DIAMANTE / STEALTH VISOR ---
    # Centro en (0.08, 0.68, 1.70), ángulo hacia el frente-abajo
    c_head = Vector((0.08, 0.68, 1.70))
    # Bóveda craneal
    mat_cran = Matrix.Translation(c_head) @ Matrix.Rotation(R(-26), 4, 'X') @ Matrix.Diagonal((0.095, 0.125, 0.120, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cran)

    # Visera frontal de facetas planas (corte geométrico de gema idéntico a la referencia)
    mat_visor = Matrix.Translation(c_head + Vector((0.015, 0.080, -0.015))) @ Matrix.Rotation(R(-24), 4, 'X') @ Matrix.Diagonal((0.082, 0.048, 0.072, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_visor)

    # Quijada angular atlética
    mat_jaw = Matrix.Translation(c_head + Vector((0.010, 0.055, -0.075))) @ Matrix.Rotation(R(-30), 4, 'X') @ Matrix.Diagonal((0.058, 0.070, 0.046, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0, matrix=mat_jaw)

    # Cresta posterior aerodinámica con espinas líquidas que se desprenden
    crest_spines = [
        (c_head + Vector((-0.01, -0.07, 0.08)), Vector((-0.05, -0.86, 0.40)), 0.28, 0.022),
        (c_head + Vector((0.01, -0.08, 0.04)), Vector((0.02, -0.92, 0.22)), 0.30, 0.020),
        (c_head + Vector((-0.03, -0.06, 0.11)), Vector((-0.08, -0.76, 0.50)), 0.22, 0.016),
        (c_head + Vector((0.04, -0.06, 0.06)), Vector((0.12, -0.82, 0.30)), 0.24, 0.016),
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

    # --- 3. EXTREMIDADES MEDIANTE SECCIONES POLIGONALES ANATÓMICAS ---
    def build_anatomical_limb(joint_nodes, num_segments=10):
        # joint_nodes: [(Vector pos, rx, ry, euler_rot)]
        limb_rings = []
        for pos, rx, ry in joint_nodes:
            ring = []
            for i in range(num_segments):
                th = 2.0 * math.pi * i / num_segments
                # Proyección ortogonal perpendicular al hueso
                p_v = Vector(pos) + Vector((rx * math.cos(th), ry * math.sin(th) * 0.7, ry * math.sin(th) * 0.7))
                v = bm.verts.new(p_v)
                ring.append(v)
            limb_rings.append(ring)
        for r in range(len(limb_rings) - 1):
            r1 = limb_rings[r]
            r2 = limb_rings[r + 1]
            for i in range(num_segments):
                i_next = (i + 1) % num_segments
                bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])

    # Función auxiliar para cápsulas y conos de musculatura
    def add_capsule(p1, p2, r1, r2, segs=12):
        v1 = Vector(p1)
        v2 = Vector(p2)
        d = v2 - v1
        dist = d.length
        if dist < 0.001:
            return
        mid = (v1 + v2) * 0.5
        rot = Vector((0, 0, 1)).rotation_difference(d.normalized())
        mat_cone = Matrix.Translation(mid) @ rot.to_matrix().to_4x4()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=dist * 1.04, matrix=mat_cone)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r1 * 1.01, matrix=Matrix.Translation(v1))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2 * 1.01, matrix=Matrix.Translation(v2))

    # BRAZO IZQUIERDO (Adelantado, codo flexionado a ~95°, antebrazo hacia arriba-adelante)
    sh_l = Vector((-0.24, 0.48, 1.40))
    bicep_l = Vector((-0.30, 0.64, 1.28))
    elb_l = Vector((-0.32, 0.78, 1.18))
    fore_l = Vector((-0.26, 0.96, 1.34))
    wrist_l = Vector((-0.20, 1.12, 1.50))
    palm_l = Vector((-0.16, 1.22, 1.58))

    # Deltoides izquierdo prominente
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=Matrix.Translation(sh_l) @ Matrix.Diagonal((0.115, 0.115, 0.125, 1.0)))
    # Clavícula a hombro
    add_capsule(Vector((-0.08, 0.50, 1.45)), sh_l, 0.110, 0.100)
    # Brazo superior (bicep / tricep)
    add_capsule(sh_l, bicep_l, 0.105, 0.096)
    add_capsule(bicep_l, elb_l, 0.096, 0.082)
    # Antebrazo (brachioradialis y flexores)
    add_capsule(elb_l, fore_l, 0.085, 0.072)
    add_capsule(fore_l, wrist_l, 0.072, 0.048)
    add_capsule(wrist_l, palm_l, 0.048, 0.038)

    # 5 Dedos extendidos en garra de sprint (mano izquierda)
    f_l_config = [
        ((-0.06, 0.05, -0.04), 0.016, 0.010, 0.07), # Pulgar
        ((-0.03, 0.12, 0.05), 0.015, 0.009, 0.10),  # Índice
        ((0.01, 0.14, 0.06), 0.016, 0.010, 0.11),   # Medio
        ((0.05, 0.13, 0.04), 0.015, 0.009, 0.10),   # Anular
        ((0.08, 0.09, 0.02), 0.013, 0.008, 0.08),   # Meñique
    ]
    for d_vec, r1, r2, flen in f_l_config:
        d_norm = Vector(d_vec).normalized()
        p_j1 = palm_l + d_norm * (flen * 0.55)
        p_tip = palm_l + d_norm * flen
        add_capsule(palm_l, p_j1, r1, (r1+r2)*0.5, segs=6)
        add_capsule(p_j1, p_tip, (r1+r2)*0.5, r2, segs=6)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2*1.1, matrix=Matrix.Translation(p_tip + d_norm * 0.01))

    # BRAZO DERECHO (Retrasado, estela fluida hacia atrás)
    sh_r = Vector((0.30, 0.36, 1.34))
    bicep_r = Vector((0.40, 0.18, 1.24))
    elb_r = Vector((0.46, 0.00, 1.14))
    fore_r = Vector((0.50, -0.20, 1.00))
    wrist_r = Vector((0.52, -0.38, 0.88))
    palm_r = Vector((0.52, -0.50, 0.78))

    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=Matrix.Translation(sh_r) @ Matrix.Diagonal((0.115, 0.115, 0.125, 1.0)))
    add_capsule(Vector((0.18, 0.44, 1.40)), sh_r, 0.110, 0.100)
    add_capsule(sh_r, bicep_r, 0.105, 0.096)
    add_capsule(bicep_r, elb_r, 0.096, 0.082)
    add_capsule(elb_r, fore_r, 0.085, 0.072)
    add_capsule(fore_r, wrist_r, 0.072, 0.048)
    add_capsule(wrist_r, palm_r, 0.048, 0.038)

    f_r_config = [
        ((0.04, -0.06, 0.02), 0.016, 0.010, 0.07),
        ((0.03, -0.12, -0.04), 0.015, 0.009, 0.10),
        ((0.00, -0.14, -0.06), 0.016, 0.010, 0.11),
        ((-0.03, -0.13, -0.05), 0.015, 0.009, 0.10),
        ((-0.06, -0.09, -0.03), 0.013, 0.008, 0.08),
    ]
    for d_vec, r1, r2, flen in f_r_config:
        d_norm = Vector(d_vec).normalized()
        p_j1 = palm_r + d_norm * (flen * 0.55)
        p_tip = palm_r + d_norm * flen
        add_capsule(palm_r, p_j1, r1, (r1+r2)*0.5, segs=6)
        add_capsule(p_j1, p_tip, (r1+r2)*0.5, r2, segs=6)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2*1.1, matrix=Matrix.Translation(p_tip + d_norm * 0.01))

    # PIERNA DERECHA (Adelantada, rodilla flexionada atacando hacia el frente a 85°)
    hip_r = Vector((0.14, -0.02, 0.80))
    thigh_r = Vector((0.18, 0.24, 0.70))
    knee_r = Vector((0.20, 0.48, 0.58))
    calf_r = Vector((0.18, 0.44, 0.36))
    ank_r = Vector((0.14, 0.38, 0.16))
    foot_r = Vector((0.13, 0.48, 0.06))

    add_capsule(hip_r, thigh_r, 0.140, 0.125)
    add_capsule(thigh_r, knee_r, 0.125, 0.096)
    # Rótula / Rodilla prominente
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=Matrix.Translation(knee_r) @ Matrix.Diagonal((0.088, 0.088, 0.092, 1.0)))
    add_capsule(knee_r, calf_r, 0.094, 0.096)
    add_capsule(calf_r, ank_r, 0.096, 0.056)
    add_capsule(ank_r, foot_r, 0.056, 0.042)

    # PIERNA IZQUIERDA (Retrasada en extensión elástica)
    hip_l = Vector((-0.12, -0.04, 0.80))
    thigh_l = Vector((-0.15, -0.32, 0.70))
    knee_l = Vector((-0.16, -0.62, 0.58))
    calf_l = Vector((-0.15, -0.90, 0.42))
    ank_l = Vector((-0.13, -1.14, 0.26))
    foot_l = Vector((-0.11, -1.26, 0.14))

    add_capsule(hip_l, thigh_l, 0.140, 0.125)
    add_capsule(thigh_l, knee_l, 0.125, 0.096)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=Matrix.Translation(knee_l) @ Matrix.Diagonal((0.088, 0.088, 0.092, 1.0)))
    add_capsule(knee_l, calf_l, 0.094, 0.096)
    add_capsule(calf_l, ank_l, 0.096, 0.056)
    add_capsule(ank_l, foot_l, 0.056, 0.042)

    # --- 4. CORTINAS FLUIDAS CURVADAS (SPLASH CURTAINS) ---
    def add_fluid_ribbon(base_pos, flow_dir, length, width, thickness=0.016):
        bp = Vector(base_pos)
        fd = Vector(flow_dir).normalized()
        up = Vector((0, 0, 1))
        side = fd.cross(up).normalized()
        for i in range(5):
            frac = i / 4.0
            p_b = bp + side * ((frac - 0.5) * width)
            ribbon_len = length * (0.5 + 0.5 * math.sin(frac * math.pi))
            curl_dir = (fd + up * (0.18 * (1.0 - frac))).normalized()
            p_t = p_b + curl_dir * ribbon_len
            mid_c = (p_b + p_t) * 0.5
            dist_c = (p_t - p_b).length
            rot_c = Vector((0, 0, 1)).rotation_difference((p_t - p_b).normalized())
            mat_c = Matrix.Translation(mid_c) @ rot_c.to_matrix().to_4x4()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=thickness, radius2=0.003, depth=dist_c, matrix=mat_c)
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.007, matrix=Matrix.Translation(p_t + curl_dir * 0.015))

    splash_locs = [
        ((0.46, 0.00, 1.14), (0.35, -0.85, -0.15), 0.26, 0.14),
        ((0.50, -0.20, 1.00), (0.40, -0.80, -0.20), 0.28, 0.16),
        ((0.52, -0.38, 0.88), (0.35, -0.82, -0.25), 0.24, 0.12),
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

    # --- 5. ENJAMBRE ORBITAL DE FERROFLUIDO EN LA ESTELA (>160 GOTAS) ---
    droplet_zones = [
        (Vector((0.52, -0.46, 0.80)), 0.38, 38),
        (Vector((-0.18, 1.20, 1.56)), 0.30, 30),
        (Vector((0.08, 0.50, 1.76)), 0.34, 32),
        (Vector((0.04, 0.08, 1.20)), 0.36, 30),
        (Vector((-0.14, -1.20, 0.28)), 0.40, 36),
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

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SK_Player_Master", me)
    col.objects.link(obj)

    # Fusión orgánica ligera (conserva la definición de los músculos)
    remesh = obj.modifiers.new("VoxelRemesh", 'REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0072
    remesh.use_smooth_shade = True

    smooth = obj.modifiers.new("Smooth", 'SMOOTH')
    smooth.factor = 0.50
    smooth.iterations = 2

    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    # Evaluar malla para poder pintar el Color Attribute "Plasma"
    dg = bpy.context.evaluated_depsgraph_get()
    eo = obj.evaluated_get(dg)
    me_final = bpy.data.meshes.new_from_object(eo)
    obj.modifiers.clear()
    obj.data = me_final

    # --- 6. PINTADO ANATÓMICO DEL COLOR ATTRIBUTE "Plasma" ---
    # Asigna peso 1.0 exactamente en las zonas donde corren los ríos de plasma en la referencia
    ca = me_final.color_attributes.new(name="Plasma", type='FLOAT_COLOR', domain='POINT')
    for i, v in enumerate(me_final.vertices):
        p = v.co
        weight = 0.0

        # Pecho y surco pectoral / clavículas (Z entre 1.25 y 1.48, Y frontal > 0.28)
        if p.z > 1.25 and p.z < 1.50 and p.y > 0.25:
            # Línea central y crestas pectorales
            dist_center = abs(p.x - 0.04)
            if dist_center < 0.16:
                weight = max(weight, 1.0 - (dist_center / 0.16) * 0.4)

        # Abdominales centrales (Z entre 0.95 y 1.25, Y frontal > 0.10)
        if p.z > 0.95 and p.z < 1.25 and p.y > 0.10:
            dist_abs = abs(p.x - 0.03)
            if dist_abs < 0.10:
                weight = max(weight, 0.95 - (dist_abs / 0.10) * 0.3)

        # Brazo izquierdo delantero (Bíceps y antebrazo: X < -0.15, Y > 0.50, Z > 1.15)
        if p.x < -0.15 and p.y > 0.50 and p.z > 1.15:
            weight = max(weight, 0.95)

        # Pierna derecha delantera (Muslo y rodilla: X > 0.08, Y > 0.20, Z < 0.75)
        if p.x > 0.08 and p.y > 0.20 and p.z < 0.75 and p.z > 0.15:
            weight = max(weight, 0.90)

        # Cabeza y cresta (Z > 1.62)
        if p.z > 1.62:
            weight = max(weight, 0.85)

        # Brazo derecho trasero (X > 0.30, Y < 0.10)
        if p.x > 0.30 and p.y < 0.10 and p.z > 0.70:
            weight = max(weight, 0.80)

        ca.data[i].color = (weight, weight, weight, 1.0)

    for p in me_final.polygons:
        p.use_smooth = True

    return obj

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_DarkFluid_V6"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_V6"
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
    col = bpy.data.collections.new("AOE_Player_DarkFluid_V6")
    bpy.context.scene.collection.children.link(col)

    setup_scifi_lab(bpy.context.scene)

    body_obj = build_master_player_v6(col)

    mat_dark = create_liquid_obsidian_plasma_material("M_DarX_DarkFluid_ElectricVeins")
    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_dark)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_dark_fluid_v6"
    os.makedirs(out_dir, exist_ok=True)

    # RENDER PRINCIPAL HEROICO 1:1
    hero_path = os.path.join(out_dir, "v6_hero_reference_match.png")
    render_camera_view(cam_pos=(2.25, 2.10, 1.18), target_pos=(0.04, 0.22, 0.94), lens=42.0, out_path=hero_path, res=(1080, 1080))

    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V6.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
