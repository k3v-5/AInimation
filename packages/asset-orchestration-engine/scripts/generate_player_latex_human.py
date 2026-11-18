"""generate_player_latex_human.py
Generador procedural AAA para Blender:
Personaje Humanoide con Piel Pura de Látex sin Ojos (Eyeless).
- Rostro hermético continuo sin ojos (eyeless mask) con puente nasal, pómulos y labios anatómicos esculpidos bajo látex.
- Anatomía humana atlética impecable (1.82 m de altura, proporciones canónicas de 8 cabezas).
- Cero bultos extraños o desconexiones: fusión determinista por Voxel Remesh (5.5 mm) + Smooth.
- Manos de 5 dedos con falanges articuladas y pulgar oponible.
- Pectorales mayores humanos con hendidura esternal limpia, abdomen six-pack y espalda en V-Taper.
- Postura atlética de sigilo/acción con guardia natural.
- Shader PBR de látex líquido puro: Dieléctrico estricto, Base Color negro obsidiana, Coat 1.0 pulido, Roughness 0.060.
- Renderizado y composición de 4 cuadrantes reglamentarios (Reglas 4, 5, 11 y 60-63).
"""

import sys
import os
import math
import bpy
import bmesh
from mathutils import Matrix, Vector, Euler

R = math.radians

def clean_scene():
    """Limpia la escena de objetos y mallas previas."""
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for lgt in list(bpy.data.lights):
        bpy.data.lights.remove(lgt)

def setup_latex_studio_lighting(scene):
    """Configura iluminación de estudio de alta gama para destacar los reflejos del látex."""
    if not scene.world:
        scene.world = bpy.data.worlds.new("World_LatexStudio")
    scene.world.use_nodes = True
    nt = scene.world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (0.010, 0.012, 0.016, 1.0)
    bg.inputs['Strength'].default_value = 0.50
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # Suelo reflectante mate
    me_floor = bpy.data.meshes.new("StudioFloor")
    bm_fl = bmesh.new()
    bmesh.ops.create_grid(bm_fl, x_segments=16, y_segments=16, size=24.0, matrix=Matrix.Translation((0, 0, 0.0)))
    bm_fl.to_mesh(me_floor)
    bm_fl.free()

    m_floor = bpy.data.materials.new("M_StudioFloor")
    m_floor.use_nodes = True
    bsdf_fl = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_fl:
        bsdf_fl.inputs['Base Color'].default_value = (0.012, 0.014, 0.018, 1.0)
        bsdf_fl.inputs['Metallic'].default_value = 0.10
        bsdf_fl.inputs['Roughness'].default_value = 0.22
    me_floor.materials.append(m_floor)
    o_floor = bpy.data.objects.new("StudioFloor", me_floor)
    scene.collection.objects.link(o_floor)

    # 1. Key Light Frontal (Desde -Y hacia el personaje)
    l1_data = bpy.data.lights.new("LGT_KeyFront", 'AREA')
    l1_data.energy = 4600.0
    l1_data.size = 2.4
    l1_data.color = (1.0, 0.99, 0.97)
    l1 = bpy.data.objects.new("LGT_KeyFront", l1_data)
    l1.location = (2.2, -2.8, 2.3)
    l1.rotation_euler = (R(50), R(-8), R(-35))
    scene.collection.objects.link(l1)

    # 2. Fill Light Suave Frontal-Izquierda
    l2_data = bpy.data.lights.new("LGT_FillCool", 'AREA')
    l2_data.energy = 1800.0
    l2_data.size = 3.2
    l2_data.color = (0.75, 0.85, 1.0)
    l2 = bpy.data.objects.new("LGT_FillCool", l2_data)
    l2.location = (-2.6, -2.4, 1.8)
    l2.rotation_euler = (R(42), R(12), R(45))
    scene.collection.objects.link(l2)

    # 3. Rim Light Trasera Derecha
    l3_data = bpy.data.lights.new("LGT_RimRight", 'SPOT')
    l3_data.energy = 11000.0
    l3_data.spot_size = R(75)
    l3_data.color = (1.0, 1.0, 1.0)
    l3 = bpy.data.objects.new("LGT_RimRight", l3_data)
    l3.location = (2.6, 2.6, 2.4)
    l3.rotation_euler = (R(-42), R(15), R(-135))
    scene.collection.objects.link(l3)

    # 4. Rim Light Trasera Izquierda (Acento Violeta Profundo)
    l4_data = bpy.data.lights.new("LGT_RimLeft", 'SPOT')
    l4_data.energy = 12000.0
    l4_data.spot_size = R(70)
    l4_data.color = (0.65, 0.15, 1.0)
    l4 = bpy.data.objects.new("LGT_RimLeft", l4_data)
    l4.location = (-2.6, 2.5, 2.2)
    l4.rotation_euler = (R(-45), R(-15), R(130))
    scene.collection.objects.link(l4)

    # 5. Top Light Cenital
    l5_data = bpy.data.lights.new("LGT_TopAccent", 'AREA')
    l5_data.energy = 2600.0
    l5_data.size = 1.6
    l5_data.color = (0.95, 0.98, 1.0)
    l5 = bpy.data.objects.new("LGT_TopAccent", l5_data)
    l5.location = (0.0, -0.2, 3.2)
    l5.rotation_euler = (R(-15), 0, 0)
    scene.collection.objects.link(l5)

def create_pure_black_latex_material(name="M_DarX_LatexSkin_Pure"):
    """Crea el shader PBR de piel de látex pura (dieléctrico estricto con coat reflectante)."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (1200, 0)

    bsdf = nt.nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (800, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Color Base: Látex Negro Obsidiana Profundo
    bsdf.inputs["Base Color"].default_value = (0.005, 0.005, 0.007, 1.0)
    # Regla 63: Dieléctrico estricto
    bsdf.inputs["Metallic"].default_value = 0.0
    # Rugosidad base de goma satinada
    bsdf.inputs["Roughness"].default_value = 0.058
    # Índice de refracción del látex natural (1.52)
    bsdf.inputs["IOR"].default_value = 1.52

    # Clearcoat / Coat (Capa líquida de látex pulido)
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.018
        if 'Coat IOR' in bsdf.inputs:
            bsdf.inputs['Coat IOR'].default_value = 1.54
    elif 'Clearcoat' in bsdf.inputs:
        bsdf.inputs['Clearcoat'].default_value = 1.0
        bsdf.inputs['Clearcoat Roughness'].default_value = 0.018

    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = 0.020
        bsdf.inputs['Subsurface Radius'].default_value = (0.02, 0.01, 0.005)
    elif 'Subsurface' in bsdf.inputs:
        bsdf.inputs['Subsurface'].default_value = 0.020

    # Micro-relieve de estiramiento elástico
    tex_coord = nt.nodes.new(type="ShaderNodeTexCoord")
    mapping = nt.nodes.new(type="ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (16.0, 16.0, 16.0)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    noise = nt.nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 24.0
    noise.inputs["Detail"].default_value = 3.0
    noise.inputs["Roughness"].default_value = 0.4
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    bump = nt.nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.008
    bump.inputs["Distance"].default_value = 0.004
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat

def add_smooth_capsule(bm, p1, p2, r1, r2, seg=24):
    """Construye una cápsula cónica orientada estrictamente con rotation_difference (Regla 61)."""
    v1, v2 = Vector(p1), Vector(p2)
    d = v2 - v1
    length = d.length
    if length < 0.0005:
        return
    mid = (v1 + v2) * 0.5
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r1, matrix=Matrix.Translation(v1))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r2, matrix=Matrix.Translation(v2))
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r1, radius2=r2, depth=length,
                          matrix=Matrix.Translation(mid) @ rot)

def build_human_hand_5fingers(bm, wrist_pos, forward_dir, up_dir, is_right=True, scale=1.0):
    """Construye mano humana realista de 5 dedos anatómicos articulados."""
    fwd = Vector(forward_dir).normalized()
    up = Vector(up_dir).normalized()
    right = fwd.cross(up).normalized()
    if not is_right:
        right = -right

    s_thick = scale * 0.95
    s_len = scale * 1.02
    p_wrist = Vector(wrist_pos)

    # 1. Palma Humana
    p_palm = p_wrist + fwd * (0.046 * s_len) - up * (0.003 * s_thick)
    mat_palm = (Matrix.Translation(p_palm) @
                Matrix((right, up, fwd)).transposed().to_4x4() @
                Matrix.Diagonal((0.036 * s_thick, 0.014 * s_thick, 0.044 * s_len, 1.0)))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_palm)

    # Eminencia Tenar
    p_thenar = p_wrist + right * (-0.016 * s_thick) + fwd * (0.022 * s_len) - up * (0.004 * s_thick)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.015 * s_thick, matrix=Matrix.Translation(p_thenar))

    # 2. Pulgar Oponible (3 falanges)
    th_dir = (fwd * 0.70 - right * 0.62 - up * 0.32).normalized()
    p_th1 = p_thenar + th_dir * (0.024 * s_len)
    p_th2 = p_th1 + th_dir * (0.022 * s_len)
    p_th_tip = p_th2 + th_dir * (0.018 * s_len)

    add_smooth_capsule(bm, p_thenar, p_th1, 0.012 * s_thick, 0.010 * s_thick, seg=12)
    add_smooth_capsule(bm, p_th1, p_th2, 0.010 * s_thick, 0.0085 * s_thick, seg=12)
    add_smooth_capsule(bm, p_th2, p_th_tip, 0.0085 * s_thick, 0.0070 * s_thick, seg=12)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * s_thick, matrix=Matrix.Translation(p_th_tip))

    # 3. 4 Dedos (Índice, Medio, Anular, Meñique)
    finger_specs = [
        (-0.016 * s_thick, -0.06, 0.93, 0.0088 * s_thick), # Índice
        ( 0.000 * s_thick,  0.00, 1.00, 0.0090 * s_thick), # Medio
        ( 0.016 * s_thick,  0.06, 0.94, 0.0085 * s_thick), # Anular
        ( 0.030 * s_thick,  0.15, 0.80, 0.0075 * s_thick), # Meñique
    ]

    p_knuckle_base = p_palm + fwd * (0.036 * s_len)

    for off_x, abd_r, len_f, r_b in finger_specs:
        p_mcp = p_knuckle_base + right * off_x + up * (0.002 * s_thick)
        f_dir = (fwd * 0.90 + right * abd_r - up * 0.35).normalized()

        l1 = 0.030 * s_len * len_f
        l2 = 0.022 * s_len * len_f
        l3 = 0.016 * s_len * len_f

        p_pip = p_mcp + f_dir * l1
        p_dip = p_pip + (f_dir - up * 0.12).normalized() * l2
        p_tip = p_dip + (f_dir - up * 0.24).normalized() * l3

        add_smooth_capsule(bm, p_mcp, p_pip, r_b, r_b * 0.88, seg=10)
        add_smooth_capsule(bm, p_pip, p_dip, r_b * 0.88, r_b * 0.76, seg=10)
        add_smooth_capsule(bm, p_dip, p_tip, r_b * 0.76, r_b * 0.62, seg=10)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r_b * 0.62, matrix=Matrix.Translation(p_tip))

def build_eyeless_human_head(bm):
    """Construye cabeza humana anatómica eyeless:
    Rostro hermético continuo sin ojos, con mandíbula definida, pómulos y puente nasal esculpido bajo látex tenso.
    """
    # 1. Bóveda Craneal (Cráneo ovoide)
    mat_cranium = (Matrix.Translation((0, 0.010, 1.70)) @
                   Euler((R(6), 0, 0), 'XYZ').to_matrix().to_4x4() @
                   Matrix.Diagonal((0.076, 0.094, 0.106, 1.0)))
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0, matrix=mat_cranium)

    # 2. Mandíbula Humana Esculpida
    mat_jaw = (Matrix.Translation((0, -0.030, 1.62)) @
               Euler((R(-10), 0, 0), 'XYZ').to_matrix().to_4x4() @
               Matrix.Diagonal((0.060, 0.068, 0.062, 1.0)))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_jaw)

    # Mentón definido
    p_chin = (0, -0.054, 1.58)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.022, matrix=Matrix.Translation(p_chin))

    # 3. Pómulos
    for sx in (1, -1):
        p_cheek = (0.046 * sx, -0.032, 1.66)
        mat_cheek = Matrix.Translation(p_cheek) @ Matrix.Diagonal((0.024, 0.030, 0.026, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cheek)

    # 4. ZONA DE LOS OJOS (EYELESS): Membrana continua de látex lisa y hermética
    p_eyeless_mask = (0, -0.046, 1.67)
    mat_mask = (Matrix.Translation(p_eyeless_mask) @
                Euler((R(-8), 0, 0), 'XYZ').to_matrix().to_4x4() @
                Matrix.Diagonal((0.064, 0.024, 0.038, 1.0)))
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0, matrix=mat_mask)

    # 5. Nariz Humana bajo Látex
    p_nasal_top = (0, -0.052, 1.69)
    p_nasal_tip = (0, -0.068, 1.63)
    add_smooth_capsule(bm, p_nasal_top, p_nasal_tip, 0.013, 0.010, seg=14)

    for sx in (1, -1):
        p_ala = (0.010 * sx, -0.062, 1.625)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.008, matrix=Matrix.Translation(p_ala))

    # 6. Labios sutiles bajo la membrana
    p_lips = (0, -0.058, 1.59)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.011, matrix=Matrix.Translation(p_lips))

    # 7. Relieve de Orejas Humanas bajo Látex
    for sx in (1, -1):
        p_ear = (0.072 * sx, 0.008, 1.66)
        mat_ear = (Matrix.Translation(p_ear) @
                   Euler((R(8), R(sx * 15), 0), 'XYZ').to_matrix().to_4x4() @
                   Matrix.Diagonal((0.012, 0.022, 0.034, 1.0)))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_ear)

    # 8. Cuello Anatómico Cilíndrico Continuo (sin bultos)
    # Cilindro continuo desde la base del cráneo hasta el tórax superior
    add_smooth_capsule(bm, (0, 0.002, 1.66), (0, -0.006, 1.48), 0.046, 0.054, seg=24)

    # Tendones Esternocleidomastoideos
    for sx in (1, -1):
        p_mastoid = (0.048 * sx, 0.010, 1.63)
        p_sternal_notch = (0.016 * sx, -0.034, 1.48)
        add_smooth_capsule(bm, p_mastoid, p_sternal_notch, 0.015, 0.011, seg=14)

def build_latex_human_character(col):
    """Construye el cuerpo humano atlético eyeless cubierto 100% de látex continuo."""
    bm = bmesh.new()

    # --------------------------------------------------------------------------
    # 1. CABEZA EYELESS
    # --------------------------------------------------------------------------
    build_eyeless_human_head(bm)

    # --------------------------------------------------------------------------
    # 2. PELVIS Y COLUMNA VERTEBRAL ATLÉTICA
    # --------------------------------------------------------------------------
    # Pelvis humana atlética (proporción masculina/esbelta: 24 cm de ancho)
    p_pelvis = (0, -0.005, 0.91)
    mat_pelvis = (Matrix.Translation(p_pelvis) @
                  Euler((R(5), 0, 0), 'XYZ').to_matrix().to_4x4() @
                  Matrix.Diagonal((0.088, 0.080, 0.090, 1.0)))
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0, matrix=mat_pelvis)

    # Columna vertebral y torso continuo
    torso_chain = [
        ((0, -0.005, 0.91), (0, 0.008, 1.06), 0.086, 0.082), # Pelvis a cintura baja
        ((0, 0.008, 1.06), (0, 0.016, 1.20), 0.082, 0.088),  # Cintura esbelta
        ((0, 0.016, 1.20), (0, 0.010, 1.34), 0.088, 0.118),  # Caja torácica
        ((0, 0.010, 1.34), (0, -0.004, 1.48), 0.118, 0.130), # Pecho atlético
    ]
    for p1, p2, r1, r2 in torso_chain:
        add_smooth_capsule(bm, p1, p2, r1, r2, seg=24)

    # --------------------------------------------------------------------------
    # 3. PECTORALES MAYORES Y ESPALDA DORSAL
    # --------------------------------------------------------------------------
    for sx in (1, -1):
        # Clavícula humana
        p_clav_in = (0.014 * sx, -0.034, 1.48)
        p_clav_out = (0.145 * sx, -0.016, 1.45)
        add_smooth_capsule(bm, p_clav_in, p_clav_out, 0.018, 0.015, seg=16)

        # Porción Clavicular (Pectoral Superior)
        p_pec_up = (0.056 * sx, -0.042, 1.43)
        mat_pec_up = (Matrix.Translation(p_pec_up) @
                      Euler((R(-8), R(sx * 10), R(-sx * 6)), 'XYZ').to_matrix().to_4x4() @
                      Matrix.Diagonal((0.058, 0.026, 0.038, 1.0)))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_up)

        # Porción Esternal (Masa Pectoral Principal con hendidura esternal limpia)
        p_pec_main = (0.064 * sx, -0.048, 1.36)
        mat_pec_main = (Matrix.Translation(p_pec_main) @
                        Euler((R(-6), R(sx * 8), R(-sx * 4)), 'XYZ').to_matrix().to_4x4() @
                        Matrix.Diagonal((0.064, 0.030, 0.056, 1.0)))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec_main)

        # Pliegue Inframamario
        add_smooth_capsule(bm, (0.022 * sx, -0.044, 1.31), (0.110 * sx, -0.034, 1.32), 0.024, 0.018, seg=16)

        # Tendón Axilar
        add_smooth_capsule(bm, (0.088 * sx, -0.040, 1.38), (0.148 * sx, -0.014, 1.42), 0.028, 0.022, seg=16)

        # Músculo Dorsal Ancho (Latissimus Dorsi / "V-Taper")
        p_lat_top = (0.105 * sx, 0.020, 1.34)
        p_lat_low = (0.082 * sx, 0.016, 1.15)
        add_smooth_capsule(bm, p_lat_top, p_lat_low, 0.034, 0.024, seg=16)

        # Glúteos atléticos
        p_glute = (0.052 * sx, 0.038, 0.88)
        mat_glute = Matrix.Translation(p_glute) @ Matrix.Diagonal((0.046, 0.042, 0.058, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_glute)

    # Abdomen Six-Pack bajo la tensión del látex
    for z_abs, r_abs in [(1.24, 0.022), (1.16, 0.021), (1.08, 0.020), (1.00, 0.018)]:
        for sx in (1, -1):
            p_ab = (0.028 * sx, -0.038, z_abs)
            mat_ab = Matrix.Translation(p_ab) @ Matrix.Diagonal((0.024, 0.015, 0.030, 1.0))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_ab)

    # --------------------------------------------------------------------------
    # 4. HOMBROS Y BRAZOS EN POSTURA HEROICA ATENTA
    # --------------------------------------------------------------------------
    for sx in (1, -1):
        # Trapecio
        add_smooth_capsule(bm, (0.028 * sx, 0.010, 1.54), (0.085 * sx, 0.010, 1.49), 0.032, 0.028, seg=16)
        add_smooth_capsule(bm, (0.085 * sx, 0.010, 1.49), (0.155 * sx, 0.006, 1.43), 0.028, 0.026, seg=16)

        # Hombro / Deltoides
        p_sh = (0.170 * sx, 0.000, 1.42)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.044, matrix=Matrix.Translation(p_sh))
        p_delt_mid = (0.178 * sx, 0.000, 1.36)
        add_smooth_capsule(bm, p_sh, p_delt_mid, 0.042, 0.036, seg=16)

        # Pose de Guardia Atlética Natural (antebrazos orientados hacia adelante, visibles en FPS y hero)
        if sx == 1:
            # Brazo Derecho: Puño en guardia táctica frontal
            p_elbow = (0.220, -0.100, 1.18)
            p_wrist = (0.170, -0.360, 1.25)
            fwd_hand = (-0.12, -0.92, 0.32)
            up_hand = (0.08, 0.32, 0.94)
        else:
            # Brazo Izquierdo: Guardia lateral equilibrada
            p_elbow = (-0.225, -0.090, 1.16)
            p_wrist = (-0.180, -0.340, 1.22)
            fwd_hand = (0.15, -0.92, 0.30)
            up_hand = (-0.10, 0.30, 0.94)

        # Brazo superior (Húmero)
        add_smooth_capsule(bm, p_sh, p_elbow, 0.040, 0.032, seg=18)
        # Codo
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.034, matrix=Matrix.Translation(p_elbow))

        # Bíceps
        p_biceps = (p_sh[0] * 0.5 + p_elbow[0] * 0.5, p_sh[1] * 0.5 + p_elbow[1] * 0.5 - 0.012, (p_sh[2] + p_elbow[2]) * 0.5)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.030, matrix=Matrix.Translation(p_biceps))

        # Antebrazo
        add_smooth_capsule(bm, p_elbow, p_wrist, 0.032, 0.024, seg=18)
        # Vientre del antebrazo
        p_forearm_belly = (p_elbow[0] * 0.55 + p_wrist[0] * 0.45, p_elbow[1] * 0.55 + p_wrist[1] * 0.45, p_elbow[2] * 0.55 + p_wrist[2] * 0.45)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.026, matrix=Matrix.Translation(p_forearm_belly))

        # Muñeca
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.024, matrix=Matrix.Translation(p_wrist))

        # Mano Humana de 5 Dedos
        build_human_hand_5fingers(bm, p_wrist, fwd_hand, up_hand, is_right=(sx == 1), scale=0.96)

    # --------------------------------------------------------------------------
    # 5. PIERNAS HUMANAS ATLÉTICAS (CADENA CONTINUA Y PROPORCIONADA)
    # --------------------------------------------------------------------------
    for sx in (1, -1):
        # Postura de piernas atléticas (separación elegante: 10 cm a cada lado)
        p_hip = (0.078 * sx, -0.005, 0.86)
        p_knee = (0.082 * sx, -0.025, 0.48)
        p_ank = (0.084 * sx, 0.015, 0.080)
        p_foot_heel = (0.084 * sx, 0.045, 0.020)
        p_foot_toe = (0.084 * sx, -0.140, 0.020)

        # Unión pélvica armónica (sin jorobas ni salientes)
        add_smooth_capsule(bm, (0.025 * sx, -0.005, 0.90), p_hip, 0.076, 0.068, seg=18)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.068, matrix=Matrix.Translation(p_hip))

        # Muslo (Fémur)
        add_smooth_capsule(bm, p_hip, p_knee, 0.070, 0.046, seg=20)

        # Cuádriceps: Recto Femoral
        p_rect_top = (0.076 * sx, -0.026, 0.78)
        p_rect_low = (0.080 * sx, -0.042, 0.56)
        add_smooth_capsule(bm, p_rect_top, p_rect_low, 0.034, 0.028, seg=16)

        # Vasto Lateral
        p_vast_lat = (0.100 * sx, -0.016, 0.67)
        mat_vast_lat = Matrix.Translation(p_vast_lat) @ Matrix.Diagonal((0.026, 0.032, 0.075, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_vast_lat)

        # Vasto Medial ("gota" sobre la rodilla)
        p_vast_med = (0.058 * sx, -0.028, 0.54)
        mat_vast_med = Matrix.Translation(p_vast_med) @ Matrix.Diagonal((0.020, 0.024, 0.036, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_vast_med)

        # Isquiotibiales (curva trasera)
        p_ham_top = (0.076 * sx, 0.018, 0.78)
        p_ham_low = (0.080 * sx, 0.010, 0.56)
        add_smooth_capsule(bm, p_ham_top, p_ham_low, 0.032, 0.026, seg=16)

        # Rodilla y Rótula (Patella)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.046, matrix=Matrix.Translation(p_knee))
        p_patella = (0.082 * sx, -0.045, 0.48)
        mat_pat = Matrix.Translation(p_patella) @ Matrix.Diagonal((0.020, 0.014, 0.024, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pat)

        # Pierna baja (Tibia/Peroné)
        add_smooth_capsule(bm, p_knee, p_ank, 0.044, 0.026, seg=20)

        # Gemelos (Gastrocnemio medial y lateral)
        p_gas_med = (0.068 * sx, 0.024, 0.36)
        mat_gas_med = Matrix.Translation(p_gas_med) @ Matrix.Diagonal((0.022, 0.026, 0.048, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_gas_med)

        p_gas_lat = (0.096 * sx, 0.020, 0.38)
        mat_gas_lat = Matrix.Translation(p_gas_lat) @ Matrix.Diagonal((0.020, 0.024, 0.044, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_gas_lat)

        # Tendón de Aquiles
        add_smooth_capsule(bm, (0.084 * sx, 0.018, 0.28), p_ank, 0.026, 0.020, seg=16)

        # Tobillo
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.026, matrix=Matrix.Translation(p_ank))

        # Pie Humano en Látex
        add_smooth_capsule(bm, p_foot_heel, p_foot_toe, 0.026, 0.018, seg=16)
        add_smooth_capsule(bm, p_ank, (0.084 * sx, -0.035, 0.022), 0.024, 0.020, seg=16)
        mat_foot = (Matrix.Translation((0.084 * sx, -0.045, 0.018)) @
                    Matrix.Diagonal((0.032, 0.080, 0.018, 1.0)))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_foot)

    # --------------------------------------------------------------------------
    # 6. FUSIÓN DETERMINISTA POR EVALUATED DEPSGRAPH (Regla 62)
    # --------------------------------------------------------------------------
    me = bpy.data.meshes.new("Mesh_DarX_LatexHuman_Eyeless")
    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SK_DarX_LatexHuman_Eyeless", me)
    col.objects.link(obj)

    # Remesh de Vóxeles para fundir 100% de articulaciones en piel de látex continua
    rem = obj.modifiers.new("VoxelRemesh", 'REMESH')
    rem.mode = 'VOXEL'
    rem.voxel_size = 0.0055 # Resolución fina para musculatura limpia
    rem.use_smooth_shade = True

    # Suavizado elástico de tensión
    sm = obj.modifiers.new("Smooth", 'SMOOTH')
    sm.factor = 0.50
    sm.iterations = 3

    # Hornear modificadores determinísticamente usando depsgraph evaluado
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eo = obj.evaluated_get(dg)
    me_final = bpy.data.meshes.new_from_object(eo)
    obj.modifiers.clear()
    obj.data = me_final

    for p in obj.data.polygons:
        p.use_smooth = True

    return obj

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(1080, 1080)):
    """Renderiza una vista de cámara con objetivo Track-To fijo."""
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_name = "CAM_LatexHuman"
    if cam_name in bpy.data.objects:
        cam_obj = bpy.data.objects[cam_name]
    else:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        scene.collection.objects.link(cam_obj)

    cam_obj.location = cam_pos
    cam_obj.data.lens = lens
    cam_obj.constraints.clear()

    tgt_name = "CAM_Target_LatexHuman"
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

def main():
    clean_scene()
    col = bpy.data.collections.new("AOE_Player_LatexHuman")
    bpy.context.scene.collection.children.link(col)

    setup_latex_studio_lighting(bpy.context.scene)

    body_obj = build_latex_human_character(col)

    mat_latex = create_pure_black_latex_material("M_DarX_LatexSkin_Pure")
    body_obj.data.materials.clear()
    body_obj.data.materials.append(mat_latex)

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_latex_human"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Hero 3/4 Action View (Mirando hacia -Y, cámara en (+X, -Y, +Z))
    hero_path = os.path.join(out_dir, "latex_hero_action.png")
    render_camera_view(cam_pos=(1.80, -2.40, 1.35), target_pos=(0.0, 0.0, 1.15), lens=42.0, out_path=hero_path, res=(1080, 1080))

    # 2. Front View (Cuerpo entero frontal desde -Y)
    front_path = os.path.join(out_dir, "latex_view_front.png")
    render_camera_view(cam_pos=(0.0, -2.90, 1.02), target_pos=(0.0, 0.0, 0.95), lens=48.0, out_path=front_path, res=(1080, 1080))

    # 3. Back View (Cuerpo entero dorsal desde +Y)
    back_path = os.path.join(out_dir, "latex_view_back.png")
    render_camera_view(cam_pos=(0.0, 2.90, 1.02), target_pos=(0.0, 0.0, 0.95), lens=48.0, out_path=back_path, res=(1080, 1080))

    # 4. FPS Arms View (Vista en primera persona: cámara a la altura de los ojos mirando hacia los puños en guardia)
    fps_path = os.path.join(out_dir, "latex_view_fps.png")
    render_camera_view(cam_pos=(0.0, -0.05, 1.62), target_pos=(0.0, -1.20, 1.25), lens=24.0, out_path=fps_path, res=(1080, 1080))

    blend_out = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_LatexHuman_V1.blend"
    os.makedirs(os.path.dirname(blend_out), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"BLEND_FILE_SAVED: {blend_out}")

if __name__ == "__main__":
    main()
