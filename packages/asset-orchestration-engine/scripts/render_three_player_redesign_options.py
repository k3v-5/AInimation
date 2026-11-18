"""render_three_player_redesign_options.py
Genera 3 propuestas de diseño para el Jugador de DarX:
Combina:
1. La textura de la Opción 1: Obsidiana líquida lacada tipo espejo, limpia, con reflejos nítidos y líneas precisas.
2. La paleta de la Opción 2: Base oscura con neón violeta/magenta eléctrico radiante.
3. Las manos de la Opción 2: Manos maestras articuladas con garras estilizadas y micro-gotas suspendidas.

Propuesta A: "Neon Phantom" (Cyber-Infiltrador Esbelto con Visor de Zafiro y Filamentos Violetas)
Propuesta B: "Apex Symbiote" (Nano-Exoesqueleto con Placas Superpuestas y Crestas)
Propuesta C: "Void Spectre" (Armadura Cuántica con Micro-Espina y Visor Panorámico)
"""

import sys, os, math
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
# PIL run from external python script

OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(OUT_DIR, exist_ok=True)

R = math.radians
TAU = math.pi * 2

def setup_environment(scene):
    # Fondo de estudio Sci-Fi oscuro con niebla sutil y suelo reflectante
    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.015, 0.020, 0.035, 1.0)
            bg.inputs["Strength"].default_value = 0.75

    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    # Suelo reflectante de estudio
    me_f = bpy.data.meshes.new("FloorMesh")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=16, y_segments=16, size=16.0, matrix=Matrix.Translation((0, 0, -0.01)))
    bm_f.to_mesh(me_f)
    bm_f.free()

    m_floor = bpy.data.materials.new("M_Floor_Showcase")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.02, 0.025, 0.035, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.50
        bsdf_f.inputs['Roughness'].default_value = 0.20
    me_f.materials.append(m_floor)

    obj_f = bpy.data.objects.new("Floor_Showcase", me_f)
    scene.collection.objects.link(obj_f)

    # Luces de estudio cinematográfico
    # 1. Key Light frontal
    l1 = bpy.data.lights.new("SunFront", 'SUN')
    l1.energy = 4.2
    l1.color = (0.95, 0.98, 1.0)
    o1 = bpy.data.objects.new("SunFront", l1)
    o1.rotation_euler = (R(35), R(10), R(-150))
    scene.collection.objects.link(o1)

    # 2. Rim Light potente azul cian (de la Opción 1)
    l2 = bpy.data.lights.new("SunRimCyan", 'SUN')
    l2.energy = 8.0
    l2.color = (0.0, 0.85, 1.0)
    o2 = bpy.data.objects.new("SunRimCyan", l2)
    o2.rotation_euler = (R(-45), R(20), R(140))
    scene.collection.objects.link(o2)

    # 3. Rim Light neón violeta/magenta (de la Opción 2)
    l3 = bpy.data.lights.new("SunRimViolet", 'SUN')
    l3.energy = 8.5
    l3.color = (0.90, 0.10, 1.0)
    o3 = bpy.data.objects.new("SunRimViolet", l3)
    o3.rotation_euler = (R(-55), R(-25), R(-40))
    scene.collection.objects.link(o3)

    # 4. Fill frontal suave
    l4 = bpy.data.lights.new("SunFill", 'SUN')
    l4.energy = 2.0
    l4.color = (0.45, 0.55, 0.70)
    o4 = bpy.data.objects.new("SunFill", l4)
    o4.rotation_euler = (R(60), R(-10), R(-45))
    scene.collection.objects.link(o4)

def create_hybrid_shaders():
    mats = {}

    # 1. Textura Base: Obsidiana Líquida Espejada (Textura de Opción 1)
    m_obsidian = bpy.data.materials.new("M_Obsidian_Mirror_Clean")
    m_obsidian.use_nodes = True
    nt = m_obsidian.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.004, 0.004, 0.007, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.02
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.01
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['obsidian'] = m_obsidian

    # 2. Nanofibra Grafito Mate (para contraste de paneles secundarios)
    m_carbon = bpy.data.materials.new("M_Carbon_Matte")
    m_carbon.use_nodes = True
    nt_c = m_carbon.node_tree
    nt_c.nodes.clear()
    out_c = nt_c.nodes.new('ShaderNodeOutputMaterial')
    bsdf_c = nt_c.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_c.inputs['Base Color'].default_value = (0.030, 0.032, 0.040, 1.0)
    bsdf_c.inputs['Metallic'].default_value = 0.85
    bsdf_c.inputs['Roughness'].default_value = 0.25
    nt_c.links.new(bsdf_c.outputs['BSDF'], out_c.inputs['Surface'])
    mats['carbon'] = m_carbon

    # 3. Neón Violeta / Plasma Radiante (Paleta de Opción 2)
    m_violet = bpy.data.materials.new("M_Neon_Violet_Core")
    m_violet.use_nodes = True
    nt_v = m_violet.node_tree
    nt_v.nodes.clear()
    out_v = nt_v.nodes.new('ShaderNodeOutputMaterial')
    emis_v = nt_v.nodes.new('ShaderNodeEmission')
    emis_v.inputs['Color'].default_value = (0.85, 0.10, 1.0, 1.0)
    emis_v.inputs['Strength'].default_value = 18.0
    nt_v.links.new(emis_v.outputs['Emission'], out_v.inputs['Surface'])
    mats['violet'] = m_violet

    # 4. Neón Magenta Intenso
    m_magenta = bpy.data.materials.new("M_Neon_Magenta_Pulse")
    m_magenta.use_nodes = True
    nt_m = m_magenta.node_tree
    nt_m.nodes.clear()
    out_m = nt_m.nodes.new('ShaderNodeOutputMaterial')
    emis_m = nt_m.nodes.new('ShaderNodeEmission')
    emis_m.inputs['Color'].default_value = (1.0, 0.05, 0.65, 1.0)
    emis_m.inputs['Strength'].default_value = 18.0
    nt_m.links.new(emis_m.outputs['Emission'], out_m.inputs['Surface'])
    mats['magenta'] = m_magenta

    # 5. Zafiro Blanco-Violeta (Núcleo Visor)
    m_core = bpy.data.materials.new("M_Visor_Core")
    m_core.use_nodes = True
    nt_w = m_core.node_tree
    nt_w.nodes.clear()
    out_w = nt_w.nodes.new('ShaderNodeOutputMaterial')
    emis_w = nt_w.nodes.new('ShaderNodeEmission')
    emis_w.inputs['Color'].default_value = (0.95, 0.85, 1.0, 1.0)
    emis_w.inputs['Strength'].default_value = 24.0
    nt_w.links.new(emis_w.outputs['Emission'], out_w.inputs['Surface'])
    mats['core'] = m_core

    # 6. Titanio Ahumado en Juntas
    m_titanium = bpy.data.materials.new("M_Titanium_Smoked")
    m_titanium.use_nodes = True
    nt_t = m_titanium.node_tree
    nt_t.nodes.clear()
    out_t = nt_t.nodes.new('ShaderNodeOutputMaterial')
    bsdf_t = nt_t.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_t.inputs['Base Color'].default_value = (0.28, 0.30, 0.36, 1.0)
    bsdf_t.inputs['Metallic'].default_value = 0.95
    bsdf_t.inputs['Roughness'].default_value = 0.10
    nt_t.links.new(bsdf_t.outputs['BSDF'], out_t.inputs['Surface'])
    mats['titanium'] = m_titanium

    return mats

def add_capsule(bm, p1, p2, r1, r2, seg=16):
    v1, v2 = Vector(p1), Vector(p2)
    d = v2 - v1
    length = d.length
    if length < 0.001:
        return
    mid = (v1 + v2) * 0.5
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    mat = Matrix.Translation(mid) @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=length, matrix=mat)

def add_box(bm, size, loc=(0,0,0), rot=(0,0,0)):
    mat = Matrix.Translation(Vector(loc)) @ Euler((R(rot[0]), R(rot[1]), R(rot[2])), 'XYZ').to_matrix().to_4x4()
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat @ Matrix.Diagonal((size[0], size[1], size[2], 1.0)))

def build_master_hand(bm, w_pos, fwd, up, is_right=True, scale=1.0):
    """Construye la mano predatoria articulada con garras de la Opción 2."""
    w_pos = Vector(w_pos)
    fwd = Vector(fwd).normalized()
    up = Vector(up).normalized()
    side = fwd.cross(up).normalized()
    if not is_right:
        side = -side

    # 1. Carpal wrist joint
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0085 * scale, matrix=Matrix.Translation(w_pos + side * 0.016 * scale))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * scale, matrix=Matrix.Translation(w_pos - side * 0.015 * scale))

    # 2. Metacarpal Palm
    palm_c = w_pos + fwd * (0.044 * scale)
    mat_palm = Matrix.Translation(palm_c) @ Matrix.Diagonal((0.034 * scale, 0.038 * scale, 0.018 * scale, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_palm)
    add_capsule(bm, w_pos, palm_c, 0.024 * scale, 0.022 * scale, seg=10)

    # 3. Tendones dorsales
    for s_off in [0.012, 0.003, -0.005, -0.012]:
        p_k = palm_c + fwd * 0.028 * scale + side * s_off * scale + up * 0.006 * scale
        p_w = w_pos + side * s_off * 0.45 * scale + up * 0.007 * scale
        add_capsule(bm, p_w, p_k, 0.0032 * scale, 0.0028 * scale, seg=6)

    # 4. Pulgar oponible con garra
    thenar = w_pos + fwd * 0.024 * scale + side * 0.016 * scale - up * 0.005 * scale
    t_mcp = thenar + fwd * 0.015 * scale + side * 0.010 * scale
    add_capsule(bm, thenar, t_mcp, 0.010 * scale, 0.008 * scale, seg=8)
    t_dir1 = (fwd * 0.65 + side * 0.70 + up * 0.15).normalized()
    t_ip = t_mcp + t_dir1 * 0.026 * scale
    add_capsule(bm, t_mcp, t_ip, 0.008 * scale, 0.0065 * scale, seg=8)
    t_dir2 = (fwd * 0.85 + side * 0.30 - up * 0.35).normalized()
    t_tip = t_ip + t_dir2 * 0.024 * scale
    add_capsule(bm, t_ip, t_tip, 0.0065 * scale, 0.0016 * scale, seg=8)

    # 5. 4 Dedos articulados con garras
    f_specs = [
        (0.014, 0.034, 0.026, 0.022, R(18), R(15)),
        (0.004, 0.038, 0.030, 0.025, R(22), R(3)),
        (-0.006, 0.035, 0.026, 0.022, R(26), -R(8)),
        (-0.015, 0.028, 0.020, 0.017, R(30), -R(20))
    ]
    for s_off, l1, l2, l3, curl, splay in f_specs:
        kn = palm_c + fwd * 0.028 * scale + side * s_off * scale + up * 0.005 * scale
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0075 * scale, matrix=Matrix.Translation(kn))
        d1 = (fwd * math.cos(splay) + side * math.sin(splay) - up * math.sin(curl * 0.4)).normalized()
        p1 = kn + d1 * l1 * scale
        add_capsule(bm, kn, p1, 0.0075 * scale, 0.0060 * scale, seg=8)
        d2 = (d1 - up * math.sin(curl * 0.85)).normalized()
        p2 = p1 + d2 * l2 * scale
        add_capsule(bm, p1, p2, 0.0060 * scale, 0.0048 * scale, seg=8)
        d3 = (d2 - up * math.sin(curl * 1.20)).normalized()
        ptip = p2 + d3 * l3 * scale
        add_capsule(bm, p2, ptip, 0.0048 * scale, 0.0015 * scale, seg=6)
        # Micro-gota de ferrofluido suspendida
        pdrop = ptip + d3 * 0.015 * scale
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.0028 * scale, matrix=Matrix.Translation(pdrop))

def render_camera(cam_pos, target_pos, lens, out_path, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = cam_pos

    empty = bpy.data.objects.new("Target", None)
    scene.collection.objects.link(empty)
    empty.location = target_pos

    tt = cam.constraints.new('TRACK_TO')
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.camera = cam
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)

# ==============================================================================
# PROPUESTA A: "NEON PHANTOM" (Cyber-Infiltrador Esbelto con Visor Zafiro)
# ==============================================================================
def build_concept_A(col, mats):
    """Silueta esbelta, acabado de obsidiana líquida con finas ranuras de energía violeta."""
    me = bpy.data.meshes.new("Mesh_Concept_A")
    bm = bmesh.new()

    for m in [mats['obsidian'], mats['violet'], mats['core'], mats['titanium']]:
        me.materials.append(m)

    # 1. Torso anatómico esbelto continuo
    torso_pts = [
        ((0, 0, 0.90), (0, 0.02, 1.06), 0.138, 0.124),
        ((0, 0.02, 1.06), (0, 0.05, 1.22), 0.124, 0.118),
        ((0, 0.05, 1.22), (0, 0.08, 1.40), 0.118, 0.180),
        ((0, 0.08, 1.40), (0, 0.10, 1.54), 0.180, 0.198),
        ((0, 0.10, 1.54), (0, 0.08, 1.63), 0.198, 0.085),
        ((0, 0.08, 1.63), (0, 0.08, 1.70), 0.058, 0.050),
    ]
    for p1, p2, r1, r2 in torso_pts:
        add_capsule(bm, p1, p2, r1, r2, seg=24)

    # 2. Cabeza ovoide aerodinámica con visor zafiro
    mat_hd = Matrix.Translation((0, 0.08, 1.77)) @ Matrix.Diagonal((0.082, 0.098, 0.115, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_hd)
    # Visor cibernético estilete
    f_start = len(bm.faces)
    add_box(bm, (0.135, 0.015, 0.018), loc=(0, -0.018, 1.765))
    for f in bm.faces[f_start:]:
        f.material_index = 2 # Visor core

    # 3. Ranuras de energía violeta en pecho y costados
    for sx in (1, -1):
        f_start = len(bm.faces)
        # Línea de energía en hombro/clavícula
        add_box(bm, (0.075, 0.012, 0.010), loc=(0.095 * sx, 0.020, 1.50), rot=(0, sx * 15, 0))
        # Franja luminosa en cuádriceps
        add_box(bm, (0.012, 0.015, 0.220), loc=(0.105 * sx, -0.045, 0.72), rot=(6, 0, 0))
        for f in bm.faces[f_start:]:
            f.material_index = 1 # Neón violeta

    # 4. Brazos esbeltos con manos maestras articuladas (Opción 2)
    # Brazo derecho
    sh_r = (0.21, 0.08, 1.50)
    el_r = (0.28, 0.26, 1.40)
    wr_r = (0.25, 0.52, 1.46)
    add_capsule(bm, (0.12, 0.09, 1.52), sh_r, 0.085, 0.090, seg=16)
    add_capsule(bm, sh_r, el_r, 0.090, 0.065, seg=16)
    add_capsule(bm, el_r, wr_r, 0.065, 0.034, seg=16)
    build_master_hand(bm, wr_r, (0, 1, 0.2), (0, 0, 1), is_right=True, scale=1.0)

    # Brazo izquierdo
    sh_l = (-0.21, 0.08, 1.50)
    el_l = (-0.28, -0.10, 1.34)
    wr_l = (-0.25, -0.32, 1.18)
    add_capsule(bm, (-0.12, 0.09, 1.52), sh_l, 0.085, 0.090, seg=16)
    add_capsule(bm, sh_l, el_l, 0.090, 0.065, seg=16)
    add_capsule(bm, el_l, wr_l, 0.065, 0.034, seg=16)
    build_master_hand(bm, wr_l, (0, -1, -0.3), (0, 0, 1), is_right=False, scale=0.96)

    # 5. Piernas atléticas esbeltas
    for sx, sign_y in ((1, 0.02), (-1, -0.02)):
        p_hp = (0.10 * sx, sign_y, 0.90)
        p_kn = (0.11 * sx, sign_y + 0.04, 0.52)
        p_ak = (0.10 * sx, sign_y, 0.12)
        p_ft = (0.10 * sx, sign_y - 0.07, 0.04)
        add_capsule(bm, (0.05 * sx, 0, 0.90), p_hp, 0.125, 0.115, seg=16)
        add_capsule(bm, p_hp, p_kn, 0.115, 0.075, seg=16)
        add_capsule(bm, p_kn, p_ak, 0.075, 0.045, seg=16)
        add_capsule(bm, p_ak, p_ft, 0.045, 0.032, seg=12)

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SK_Concept_A", me)
    col.objects.link(obj)

    # Remesh suave para unificar el cuerpo con acabado espejo
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    remesh = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0055
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    smooth = obj.modifiers.new(name="Smooth", type='SMOOTH')
    smooth.factor = 0.85
    smooth.iterations = 16
    bpy.ops.object.modifier_apply(modifier="Smooth")

    for p in obj.data.polygons:
        p.use_smooth = True

    obj.data.materials.clear()
    obj.data.materials.append(mats['obsidian'])

    # Accesorios sobre la malla: Visor y franjas neón
    me_acc = bpy.data.meshes.new("Mesh_Concept_A_Acc")
    bm_a = bmesh.new()
    me_acc.materials.append(mats['violet'])
    me_acc.materials.append(mats['core'])

    # Visor zafiro exterior nítido
    mat_vis = Matrix.Translation((0, -0.022, 1.765)) @ Matrix.Diagonal((0.140, 0.016, 0.020, 1.0))
    bmesh.ops.create_cube(bm_a, size=1.0, matrix=mat_vis)
    for f in bm_a.faces:
        f.material_index = 1

    # Líneas de energía violeta en hombros y piernas
    for sx in (1, -1):
        f_start = len(bm_a.faces)
        add_box(bm_a, (0.080, 0.015, 0.012), loc=(0.110 * sx, 0.035, 1.51), rot=(0, sx * 15, 0))
        add_box(bm_a, (0.014, 0.018, 0.240), loc=(0.108 * sx, -0.065, 0.72), rot=(6, 0, 0))
        # Vértebras dorsales de plasma
        for zv in [1.25, 1.33, 1.41, 1.49]:
            bmesh.ops.create_uvsphere(bm_a, u_segments=10, v_segments=6, radius=0.015,
                                      matrix=Matrix.Translation((0, 0.165, zv)))
        for f in bm_a.faces[f_start:]:
            f.material_index = 0

    bm_a.to_mesh(me_acc)
    bm_a.free()
    obj_acc = bpy.data.objects.new("SK_Concept_A_Acc", me_acc)
    col.objects.link(obj_acc)
    for p in obj_acc.data.polygons:
        p.use_smooth = True

    return [obj, obj_acc]

# ==============================================================================
# PROPUESTA B: "APEX SYMBIOTE" (Nano-Exoesqueleto Depredador con Placas)
# ==============================================================================
def build_concept_B(col, mats):
    """Cuerpo musculoso con placas angulares de obsidiana y núcleo biotecnológico."""
    me = bpy.data.meshes.new("Mesh_Concept_B")
    bm = bmesh.new()

    for m in [mats['obsidian'], mats['carbon'], mats['magenta'], mats['violet'], mats['core']]:
        me.materials.append(m)

    # 1. Torso muscular V-Taper
    torso_pts = [
        ((0, 0, 0.90), (0, 0.03, 1.05), 0.145, 0.130),
        ((0, 0.03, 1.05), (0, 0.07, 1.22), 0.130, 0.125),
        ((0, 0.07, 1.22), (0, 0.12, 1.40), 0.125, 0.190),
        ((0, 0.12, 1.40), (0, 0.15, 1.54), 0.190, 0.210),
        ((0, 0.15, 1.54), (0, 0.13, 1.63), 0.210, 0.092),
        ((0, 0.13, 1.63), (0, 0.13, 1.70), 0.064, 0.054),
    ]
    for p1, p2, r1, r2 in torso_pts:
        add_capsule(bm, p1, p2, r1, r2, seg=24)

    # Pectorales prominentes
    for sx in (1, -1):
        mat_pec = Matrix.Translation((0.10 * sx, 0.19, 1.45)) @ Matrix.Diagonal((0.115, 0.070, 0.095, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec)

    # 2. Cabeza con crestas depredadoras angulares
    mat_hd = Matrix.Translation((0, 0.13, 1.77)) @ Matrix.Diagonal((0.088, 0.105, 0.118, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_hd)
    # Crestas laterales
    for sx in (1, -1):
        mat_cr = Matrix.Translation((0.095 * sx, 0.10, 1.82)) @ Matrix.Diagonal((0.025, 0.085, 0.035, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_cr)

    # 3. Extremidades con manos maestras articuladas
    sh_r = (0.23, 0.14, 1.50)
    el_r = (0.32, 0.36, 1.42)
    wr_r = (0.28, 0.65, 1.48)
    add_capsule(bm, (0.12, 0.14, 1.52), sh_r, 0.095, 0.100, seg=16)
    add_capsule(bm, sh_r, el_r, 0.100, 0.075, seg=16)
    add_capsule(bm, el_r, wr_r, 0.075, 0.038, seg=16)
    build_master_hand(bm, wr_r, (0, 1, 0.15), (0, 0, 1), is_right=True, scale=1.05)

    sh_l = (-0.23, 0.14, 1.50)
    el_l = (-0.32, -0.06, 1.35)
    wr_l = (-0.28, -0.30, 1.18)
    add_capsule(bm, (-0.12, 0.14, 1.52), sh_l, 0.095, 0.100, seg=16)
    add_capsule(bm, sh_l, el_l, 0.100, 0.075, seg=16)
    add_capsule(bm, el_l, wr_l, 0.075, 0.038, seg=16)
    build_master_hand(bm, wr_l, (0, -1, -0.35), (0, 0, 1), is_right=False, scale=1.0)

    # Piernas musculosas
    for sx, sign_y in ((1, 0.03), (-1, -0.03)):
        p_hp = (0.11 * sx, sign_y, 0.90)
        p_kn = (0.13 * sx, sign_y + 0.05, 0.52)
        p_ak = (0.12 * sx, sign_y, 0.12)
        p_ft = (0.12 * sx, sign_y - 0.07, 0.04)
        add_capsule(bm, (0.05 * sx, 0, 0.90), p_hp, 0.135, 0.125, seg=16)
        add_capsule(bm, p_hp, p_kn, 0.125, 0.085, seg=16)
        add_capsule(bm, p_kn, p_ak, 0.085, 0.052, seg=16)
        add_capsule(bm, p_ak, p_ft, 0.052, 0.036, seg=12)

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SK_Concept_B", me)
    col.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    remesh = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0055
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    smooth = obj.modifiers.new(name="Smooth", type='SMOOTH')
    smooth.factor = 0.85
    smooth.iterations = 16
    bpy.ops.object.modifier_apply(modifier="Smooth")

    for p in obj.data.polygons:
        p.use_smooth = True

    obj.data.materials.clear()
    obj.data.materials.append(mats['obsidian'])

    # Accesorios: Hombreras superpuestas, visor angular dividido y exo-placas
    me_acc = bpy.data.meshes.new("Mesh_Concept_B_Acc")
    bm_a = bmesh.new()
    for m in [mats['carbon'], mats['magenta'], mats['core'], mats['obsidian']]:
        me_acc.materials.append(m)

    # Visor dual estilete angular
    for sx in (1, -1):
        f_start = len(bm_a.faces)
        add_box(bm_a, (0.045, 0.015, 0.016), loc=(0.040 * sx, 0.025, 1.765), rot=(0, 0, sx * 15))
        for f in bm_a.faces[f_start:]:
            f.material_index = 2

    # Hombreras flotantes de obsidiana biselada
    for sx in (1, -1):
        f_start = len(bm_a.faces)
        add_box(bm_a, (0.095, 0.125, 0.055), loc=(0.250 * sx, 0.14, 1.56), rot=(0, sx * 18, 0))
        # Ribete magenta emisivo en borde de hombrera
        add_box(bm_a, (0.010, 0.128, 0.058), loc=(0.295 * sx, 0.14, 1.56), rot=(0, sx * 18, 0))
        for f in bm_a.faces[f_start:]:
            f.material_index = 1 if f.index % 2 == 1 else 3

    # Placa pectoral con núcleo biotecnológico
    f_start = len(bm_a.faces)
    bmesh.ops.create_uvsphere(bm_a, u_segments=16, v_segments=12, radius=0.030,
                              matrix=Matrix.Translation((0, 0.055, 1.45)))
    for f in bm_a.faces[f_start:]:
        f.material_index = 1 # Magenta brillante

    bm_a.to_mesh(me_acc)
    bm_a.free()
    obj_acc = bpy.data.objects.new("SK_Concept_B_Acc", me_acc)
    col.objects.link(obj_acc)
    for p in obj_acc.data.polygons:
        p.use_smooth = True

    return [obj, obj_acc]

# ==============================================================================
# PROPUESTA C: "VOID SPECTRE" (Armadura Cuántica con Micro-Espina y Visor Total)
# ==============================================================================
def build_concept_C(col, mats):
    """Silueta aerodinámica con visor panorámico envolvente y micro-espina neural completa."""
    me = bpy.data.meshes.new("Mesh_Concept_C")
    bm = bmesh.new()

    for m in [mats['obsidian'], mats['violet'], mats['core'], mats['titanium']]:
        me.materials.append(m)

    # 1. Torso atlético con micro-curvatura
    torso_pts = [
        ((0, 0, 0.90), (0, 0.02, 1.06), 0.140, 0.126),
        ((0, 0.02, 1.06), (0, 0.06, 1.22), 0.126, 0.120),
        ((0, 0.06, 1.22), (0, 0.10, 1.40), 0.120, 0.185),
        ((0, 0.10, 1.40), (0, 0.12, 1.54), 0.185, 0.205),
        ((0, 0.12, 1.54), (0, 0.10, 1.63), 0.205, 0.088),
        ((0, 0.10, 1.63), (0, 0.10, 1.70), 0.060, 0.052),
    ]
    for p1, p2, r1, r2 in torso_pts:
        add_capsule(bm, p1, p2, r1, r2, seg=24)

    # 2. Cabeza con visor panorámico continuo envolvente (360 frontal)
    mat_hd = Matrix.Translation((0, 0.10, 1.77)) @ Matrix.Diagonal((0.085, 0.100, 0.116, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_hd)

    # 3. Extremidades con manos maestras articuladas
    sh_r = (0.22, 0.10, 1.50)
    el_r = (0.30, 0.32, 1.42)
    wr_r = (0.26, 0.60, 1.48)
    add_capsule(bm, (0.12, 0.11, 1.52), sh_r, 0.090, 0.095, seg=16)
    add_capsule(bm, sh_r, el_r, 0.095, 0.070, seg=16)
    add_capsule(bm, el_r, wr_r, 0.070, 0.036, seg=16)
    build_master_hand(bm, wr_r, (0, 1, 0.18), (0, 0, 1), is_right=True, scale=1.0)

    sh_l = (-0.22, 0.10, 1.50)
    el_l = (-0.30, -0.08, 1.34)
    wr_l = (-0.26, -0.30, 1.18)
    add_capsule(bm, (-0.12, 0.11, 1.52), sh_l, 0.090, 0.095, seg=16)
    add_capsule(bm, sh_l, el_l, 0.095, 0.070, seg=16)
    add_capsule(bm, el_l, wr_l, 0.070, 0.036, seg=16)
    build_master_hand(bm, wr_l, (0, -1, -0.32), (0, 0, 1), is_right=False, scale=0.96)

    # Piernas
    for sx, sign_y in ((1, 0.02), (-1, -0.02)):
        p_hp = (0.105 * sx, sign_y, 0.90)
        p_kn = (0.120 * sx, sign_y + 0.04, 0.52)
        p_ak = (0.110 * sx, sign_y, 0.12)
        p_ft = (0.110 * sx, sign_y - 0.07, 0.04)
        add_capsule(bm, (0.05 * sx, 0, 0.90), p_hp, 0.130, 0.120, seg=16)
        add_capsule(bm, p_hp, p_kn, 0.120, 0.080, seg=16)
        add_capsule(bm, p_kn, p_ak, 0.080, 0.048, seg=16)
        add_capsule(bm, p_ak, p_ft, 0.048, 0.034, seg=12)

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SK_Concept_C", me)
    col.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    remesh = obj.modifiers.new(name="VoxelRemesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0055
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    smooth = obj.modifiers.new(name="Smooth", type='SMOOTH')
    smooth.factor = 0.85
    smooth.iterations = 16
    bpy.ops.object.modifier_apply(modifier="Smooth")

    for p in obj.data.polygons:
        p.use_smooth = True

    obj.data.materials.clear()
    obj.data.materials.append(mats['obsidian'])

    # Accesorios: Visor envolvente curvado y micro-espina neural completa
    me_acc = bpy.data.meshes.new("Mesh_Concept_C_Acc")
    bm_a = bmesh.new()
    for m in [mats['violet'], mats['core'], mats['titanium']]:
        me_acc.materials.append(m)

    # Visor panorámico continuo envolvente (curvo de sien a sien)
    f_start = len(bm_a.faces)
    add_box(bm_a, (0.160, 0.024, 0.024), loc=(0, 0.008, 1.765), rot=(0, 0, 0))
    for f in bm_a.faces[f_start:]:
        f.material_index = 1 # Visor core

    # Micro-Espina Neural Completa (12 nodos dorsales de plasma violeta)
    for i, zv in enumerate([1.08, 1.14, 1.20, 1.26, 1.32, 1.38, 1.44, 1.50, 1.56, 1.62]):
        f_start = len(bm_a.faces)
        # Vértebra de titanio ahumado
        add_box(bm_a, (0.048, 0.028, 0.025), loc=(0, 0.165, zv), rot=(0, 0, 0))
        for f in bm_a.faces[f_start:]:
            f.material_index = 2 # Titanio
        # Nodo central de plasma
        f_start = len(bm_a.faces)
        bmesh.ops.create_uvsphere(bm_a, u_segments=10, v_segments=6, radius=0.016,
                                  matrix=Matrix.Translation((0, 0.182, zv)))
        for f in bm_a.faces[f_start:]:
            f.material_index = 0 # Violeta radiante

    bm_a.to_mesh(me_acc)
    bm_a.free()
    obj_acc = bpy.data.objects.new("SK_Concept_C_Acc", me_acc)
    col.objects.link(obj_acc)
    for p in obj_acc.data.polygons:
        p.use_smooth = True

    return [obj, obj_acc]

def render_concept_quad(build_fn, concept_name, mats, scene):
    print(f"=== GENERANDO Y RENDERIZANDO {concept_name} ===")
    col = bpy.data.collections.new(f"Col_{concept_name}")
    scene.collection.children.link(col)

    objs = build_fn(col, mats)

    out_prefix = os.path.join(OUT_DIR, f"shot_{concept_name}")
    v_front = f"{out_prefix}_front.png"
    v_back = f"{out_prefix}_back.png"
    v_action = f"{out_prefix}_action.png"
    v_closeup = f"{out_prefix}_closeup.png"

    # 1. Frontal (Front-3/4 View)
    render_camera((1.8, -3.2, 1.25), (0.0, 0.0, 1.10), 45.0, v_front)

    # 2. Trasera (Exo-Espina)
    render_camera((-1.8, 3.2, 1.25), (0.0, 0.0, 1.10), 45.0, v_back)

    # 3. Acción (Combat Lunge de cuerpo entero)
    render_camera((2.8, -2.4, 1.40), (0.0, 0.0, 1.00), 40.0, v_action)

    # 4. Primer Plano de Manos y Pecho (Mostrando las garras y el acabado de obsidiana)
    render_camera((0.35, 0.85, 1.62), (0.24, 0.52, 1.46), 35.0, v_closeup)

    # Limpiar objetos del concepto para el siguiente
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)

    final_quad_path = os.path.join(OUT_DIR, f"propuesta_{concept_name.lower()}.png")
    print(f"Renders de {concept_name} completados con éxito.")
    return final_quad_path

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    setup_environment(scene)
    mats = create_hybrid_shaders()

    # Generar Propuesta A: Neon Phantom
    render_concept_quad(build_concept_A, "Neon_Phantom", mats, scene)

    # Generar Propuesta B: Apex Symbiote
    render_concept_quad(build_concept_B, "Apex_Symbiote", mats, scene)

    # Generar Propuesta C: Void Spectre
    render_concept_quad(build_concept_C, "Void_Spectre", mats, scene)

    print("=== TODOS LOS RENDERS DE LAS 3 PROPUESTAS COMPLETADOS CON ÉXITO ===")

if __name__ == "__main__":
    main()
