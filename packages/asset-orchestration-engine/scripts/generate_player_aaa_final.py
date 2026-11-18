"""generate_player_aaa_final.py
Construye y renderiza el Jugador de DarX AAA con armadura táctica balística,
exo-espina neural violeta, casco zafiro y vista FPS cinemática con arma biomécanica.
Genera player_redesign_4views.png cumpliendo las Reglas 4 y 5 de AGENTS.md.
"""

import sys, os, math
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
# PIL is run from external system python

OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
IMG_FINAL = os.path.join(OUT_DIR, "player_redesign_4views.png")
V1_PATH = os.path.join(OUT_DIR, "v_front.png")
V2_PATH = os.path.join(OUT_DIR, "v_back.png")
V3_PATH = os.path.join(OUT_DIR, "v_action.png")
V4_PATH = os.path.join(OUT_DIR, "v_fps.png")

R = math.radians
TAU = math.pi * 2

def setup_studio():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.09, 0.10, 0.13, 1.0)
            bg.inputs["Strength"].default_value = 0.85

    for o in list(bpy.data.objects):
        if "Light" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    # 1. Key light blanca
    l1_data = bpy.data.lights.new("KeyLight", 'AREA')
    l1_data.energy = 1400
    l1_data.size = 3.0
    l1_data.color = (1.0, 1.0, 1.0)
    l1 = bpy.data.objects.new("KeyLight", l1_data)
    l1.location = (2.2, 2.5, 2.4)
    l1.rotation_euler = (R(45), 0, R(40))
    scene.collection.objects.link(l1)

    # 2. Rim light neón violeta intensa (recorta la silueta oscura y hace brillar la exo-espina)
    l2_data = bpy.data.lights.new("RimViolet", 'SPOT')
    l2_data.energy = 2600
    l2_data.spot_size = R(75)
    l2_data.color = (0.88, 0.15, 1.0)
    l2 = bpy.data.objects.new("RimViolet", l2_data)
    l2.location = (-2.6, -3.2, 2.2)
    l2.rotation_euler = (R(-45), 0, R(-140))
    scene.collection.objects.link(l2)

    # 3. Fill light cian suave
    l3_data = bpy.data.lights.new("FillCian", 'AREA')
    l3_data.energy = 450
    l3_data.size = 4.0
    l3_data.color = (0.55, 0.80, 1.0)
    l3 = bpy.data.objects.new("FillCian", l3_data)
    l3.location = (-2.8, 2.0, 1.6)
    l3.rotation_euler = (R(50), 0, R(-45))
    scene.collection.objects.link(l3)

    # Suelo reflectante de estudio
    me_floor = bpy.data.meshes.new("Studio_Floor")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=16, y_segments=16, size=14.0, matrix=Matrix.Translation((0, 0, 0)))
    bm_f.to_mesh(me_floor)
    bm_f.free()

    m_floor = bpy.data.materials.new("M_Floor_Reflective")
    m_floor.use_nodes = True
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.05, 0.05, 0.07, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.5
        bsdf_f.inputs['Roughness'].default_value = 0.25
    me_floor.materials.append(m_floor)

    obj_f = bpy.data.objects.new("Studio_Floor", me_floor)
    scene.collection.objects.link(obj_f)

def create_shaders():
    mats = {}

    # Piel de obsidiana líquida con vetas violetas
    m_skin = bpy.data.materials.new("M_Player_Skin_DarkFluid")
    m_skin.use_nodes = True
    nt = m_skin.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.005, 0.005, 0.008, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.03
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.015
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['skin'] = m_skin

    # Armadura de grafeno balístico
    m_armor = bpy.data.materials.new("M_Player_Armor_Graphene")
    m_armor.use_nodes = True
    nt = m_armor.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.024, 0.025, 0.030, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.88
    bsdf.inputs['Roughness'].default_value = 0.22
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['armor'] = m_armor

    # Titanio cromo en juntas
    m_chrome = bpy.data.materials.new("M_Player_Chrome")
    m_chrome.use_nodes = True
    nt = m_chrome.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.42, 0.44, 0.48, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.98
    bsdf.inputs['Roughness'].default_value = 0.12
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['chrome'] = m_chrome

    # Exo-espina neural violeta emisiva
    m_spine = bpy.data.materials.new("M_Player_ExoSpine")
    m_spine.use_nodes = True
    nt = m_spine.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.88, 0.12, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 10.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['spine'] = m_spine

    # Visor cibernético zafiro
    m_visor = bpy.data.materials.new("M_Player_Visor")
    m_visor.use_nodes = True
    nt = m_visor.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.95, 0.25, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 12.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['visor'] = m_visor

    # Chasis cerámico blanco del arma
    m_gun_body = bpy.data.materials.new("M_Gun_Body")
    m_gun_body.use_nodes = True
    nt = m_gun_body.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.90, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.08
    bsdf.inputs['Roughness'].default_value = 0.20
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['gun_body'] = m_gun_body

    # Celdas de energía púrpura
    m_charge = bpy.data.materials.new("M_Gun_Charge")
    m_charge.use_nodes = True
    nt = m_charge.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.90, 0.15, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 9.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['charge'] = m_charge

    # Display HUD cian
    m_hud = bpy.data.materials.new("M_Arm_HUD")
    m_hud.use_nodes = True
    nt = m_hud.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.15, 0.90, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 8.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['hud'] = m_hud

    return mats

def add_limb(bm, p1, p2, r1, r2, seg=16):
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

def build_humanoid_body(col, mats):
    # Construcción anatómica atlética unificada
    mesh = bpy.data.meshes.new("Mesh_Player_Hero")
    bm = bmesh.new()

    # 1. Torso atlético V-Taper (Pelvis a Trapecio)
    torso_chain = [
        ((0, 0, 0.90), (0, 0.03, 1.04), 0.140, 0.125),
        ((0, 0.03, 1.04), (0, 0.08, 1.22), 0.125, 0.120),
        ((0, 0.08, 1.22), (0, 0.14, 1.40), 0.120, 0.185),
        ((0, 0.14, 1.40), (0, 0.18, 1.54), 0.185, 0.205),
        ((0, 0.18, 1.54), (0, 0.16, 1.63), 0.205, 0.090),
        ((0, 0.16, 1.63), (0, 0.18, 1.70), 0.062, 0.052),
    ]
    for p1, p2, r1, r2 in torso_chain:
        add_limb(bm, p1, p2, r1, r2, seg=20)

    # Pectorales musculares
    for sx in (1, -1):
        mat_pec = Matrix.Translation((0.095 * sx, 0.21, 1.45)) @ Matrix.Diagonal((0.11, 0.065, 0.09, 1.0))
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_pec)

    # 2. Cabeza y Casco Aerodinámico (Z = 1.70 a 1.885)
    mat_head = Matrix.Translation((0, 0.18, 1.77)) @ Matrix.Diagonal((0.085, 0.095, 0.110, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_head)

    # 3. Extremidades en postura de combate atlética
    # Brazo derecho extendido
    sh_r = (0.21, 0.18, 1.50)
    el_r = (0.32, 0.44, 1.42)
    wr_r = (0.26, 0.76, 1.50)
    add_limb(bm, (0.12, 0.18, 1.52), sh_r, 0.095, 0.100, seg=14)
    add_limb(bm, sh_r, el_r, 0.100, 0.072, seg=14)
    add_limb(bm, el_r, wr_r, 0.072, 0.038, seg=14)
    # Mano derecha articulada
    mat_hand_r = Matrix.Translation((0.24, 0.88, 1.54)) @ Matrix.Diagonal((0.032, 0.045, 0.020, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_hand_r)

    # Brazo izquierdo retrasado
    sh_l = (-0.21, 0.16, 1.50)
    el_l = (-0.32, -0.10, 1.35)
    wr_l = (-0.30, -0.38, 1.18)
    add_limb(bm, (-0.12, 0.18, 1.52), sh_l, 0.095, 0.100, seg=14)
    add_limb(bm, sh_l, el_l, 0.100, 0.072, seg=14)
    add_limb(bm, el_l, wr_l, 0.072, 0.038, seg=14)
    # Mano izquierda
    mat_hand_l = Matrix.Translation((-0.28, -0.50, 1.08)) @ Matrix.Diagonal((0.032, 0.045, 0.020, 1.0))
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=mat_hand_l)

    # Pierna derecha adelantada
    hp_r = (0.11, 0.04, 0.88)
    kn_r = (0.15, 0.42, 0.88)
    ak_r = (0.16, 0.72, 0.48)
    ft_r = (0.16, 0.90, 0.28)
    add_limb(bm, (0.05, 0.02, 0.90), hp_r, 0.130, 0.120, seg=14)
    add_limb(bm, hp_r, kn_r, 0.120, 0.085, seg=14)
    add_limb(bm, kn_r, ak_r, 0.085, 0.050, seg=14)
    add_limb(bm, ak_r, ft_r, 0.050, 0.036, seg=12)

    # Pierna izquierda retrasada
    hp_l = (-0.11, -0.04, 0.88)
    kn_l = (-0.15, -0.30, 0.68)
    ak_l = (-0.16, -0.64, 0.35)
    ft_l = (-0.16, -0.80, 0.18)
    add_limb(bm, (-0.05, -0.02, 0.90), hp_l, 0.130, 0.120, seg=14)
    add_limb(bm, hp_l, kn_l, 0.120, 0.085, seg=14)
    add_limb(bm, kn_l, ak_l, 0.085, 0.050, seg=14)
    add_limb(bm, ak_l, ft_l, 0.050, 0.036, seg=12)

    bm.to_mesh(mesh)
    bm.free()

    obj_body = bpy.data.objects.new("SK_Player_Hero_Body", mesh)
    col.objects.link(obj_body)

    # Voxel Remesh + Smooth para anatomía orgánica sin costuras
    bpy.context.view_layer.objects.active = obj_body
    obj_body.select_set(True)
    remesh = obj_body.modifiers.new(name="VoxelRemesh", type='REMESH')
    remesh.mode = 'VOXEL'
    remesh.voxel_size = 0.0055
    bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

    smooth = obj_body.modifiers.new(name="Smooth", type='SMOOTH')
    smooth.factor = 0.85
    smooth.iterations = 18
    bpy.ops.object.modifier_apply(modifier="Smooth")

    for p in obj_body.data.polygons:
        p.use_smooth = True

    obj_body.data.materials.append(mats['skin'])

    # 4. CAPA DE ARMADURA BALÍSTICA, EXO-ESPINA Y ACCESORIOS (Sobre el cuerpo remasheado)
    mesh_gear = bpy.data.meshes.new("Mesh_Player_Hero_Gear")
    bm_g = bmesh.new()

    for m in [mats['armor'], mats['chrome'], mats['spine'], mats['visor']]:
        mesh_gear.materials.append(m)

    # Visor cibernético zafiro violeta en la cabeza
    mat_vis = Matrix.Translation((0, 0.27, 1.765)) @ Matrix.Diagonal((0.085, 0.016, 0.020, 1.0))
    bmesh.ops.create_cube(bm_g, size=1.0, matrix=mat_vis)
    for f in bm_g.faces:
        f.material_index = 3 # Visor

    # Peto balístico pectoral de grafeno
    f_start = len(bm_g.faces)
    for sx in (1, -1):
        add_box(bm_g, (0.095, 0.040, 0.15), loc=(0.095 * sx, 0.26, 1.46), rot=(-14, sx * 8, 0))
        # Hombrera angular biselada
        add_box(bm_g, (0.085, 0.110, 0.060), loc=(0.220 * sx, 0.18, 1.55), rot=(0, sx * 15, 0))
    for f in bm_g.faces[f_start:]:
        f.material_index = 0 # Armadura

    # Núcleo de energía pectoral
    f_start = len(bm_g.faces)
    bmesh.ops.create_uvsphere(bm_g, u_segments=16, v_segments=12, radius=0.024,
                              matrix=Matrix.Translation((0, 0.255, 1.45)))
    for f in bm_g.faces[f_start:]:
        f.material_index = 2 # Neón violeta

    # EXO-ESPINA NEURAL DORSAL (8 vértebras con conductos de plasma violeta)
    spine_coords = [
        (0.00, 0.03, 1.06),
        (0.00, 0.05, 1.13),
        (0.00, 0.07, 1.20),
        (0.00, 0.09, 1.28),
        (0.00, 0.11, 1.36),
        (0.00, 0.13, 1.44),
        (0.00, 0.15, 1.52),
        (0.00, 0.16, 1.60),
    ]
    for y, x_off, z_pos in [(sc[1], sc[0], sc[2]) for sc in spine_coords]:
        # Vértebra de armadura
        f_start = len(bm_g.faces)
        add_box(bm_g, (0.055, 0.035, 0.038), loc=(0, y - 0.070, z_pos), rot=(0, 0, 0))
        for f in bm_g.faces[f_start:]:
            f.material_index = 0 # Armadura

        # Nodo de plasma violeta luminoso
        f_start = len(bm_g.faces)
        bmesh.ops.create_uvsphere(bm_g, u_segments=12, v_segments=8, radius=0.014,
                                  matrix=Matrix.Translation((0, y - 0.092, z_pos)))
        for f in bm_g.faces[f_start:]:
            f.material_index = 2 # Plasma violeta

    bm_g.to_mesh(mesh_gear)
    bm_g.free()

    obj_gear = bpy.data.objects.new("SK_Player_Hero_Gear", mesh_gear)
    col.objects.link(obj_gear)

    for p in obj_gear.data.polygons:
        p.use_smooth = True

    return [obj_body, obj_gear]

def build_fps_view(col, mats):
    # Brazos en primera persona y arma bio-mecánica blanca/púrpura
    mesh = bpy.data.meshes.new("Mesh_FPS_Arms")
    bm = bmesh.new()

    for m in [mats['skin'], mats['armor'], mats['chrome'], mats['gun_body'], mats['charge'], mats['hud']]:
        mesh.materials.append(m)

    # 1. BRAZO IZQUIERDO CON BRAZALETE HUD
    add_limb(bm, (-0.26, 0.15, -0.18), (-0.12, -0.18, -0.08), 0.044, 0.034, seg=16)
    # Brazalete táctico
    f_start = len(bm.faces)
    add_box(bm, (0.045, 0.065, 0.028), loc=(-0.13, -0.15, -0.065), rot=(15, 20, -10))
    for f in bm.faces[f_start:]:
        f.material_index = 1 # Armadura

    # Pantalla HUD cian
    f_start = len(bm.faces)
    add_box(bm, (0.035, 0.052, 0.005), loc=(-0.13, -0.15, -0.048), rot=(15, 20, -10))
    for f in bm.faces[f_start:]:
        f.material_index = 5 # HUD cian

    # Mano izquierda
    f_start = len(bm.faces)
    add_box(bm, (0.042, 0.060, 0.032), loc=(-0.10, -0.26, -0.07), rot=(10, 15, -5))
    for f in bm.faces[f_start:]:
        f.material_index = 1 # Guante

    # 2. BRAZO DERECHO SUJETANDO EL ARMA
    add_limb(bm, (0.24, 0.18, -0.20), (0.12, -0.15, -0.10), 0.046, 0.036, seg=16)
    f_start = len(bm.faces)
    add_box(bm, (0.042, 0.055, 0.035), loc=(0.10, -0.22, -0.09), rot=(8, -10, 5))
    for f in bm.faces[f_start:]:
        f.material_index = 1 # Guante

    # 3. PISTOLA BIO-MECÁNICA BLANCA CON CELDAS PÚRPURAS
    gun_center = (0.09, -0.32, -0.07)
    # Chasis blanco cerámico
    f_start = len(bm.faces)
    add_box(bm, (0.046, 0.20, 0.075), loc=gun_center, rot=(4, -4, 0))
    # Cañón colimador
    add_box(bm, (0.034, 0.12, 0.042), loc=(gun_center[0], gun_center[1] - 0.13, gun_center[2] + 0.01), rot=(4, -4, 0))
    # Riel superior
    add_box(bm, (0.020, 0.14, 0.016), loc=(gun_center[0], gun_center[1] - 0.02, gun_center[2] + 0.052), rot=(4, -4, 0))
    # Empuñadura
    add_box(bm, (0.035, 0.05, 0.11), loc=(gun_center[0], gun_center[1] + 0.08, gun_center[2] - 0.06), rot=(20, 0, 0))
    for f in bm.faces[f_start:]:
        f.material_index = 3 # Blanco cerámico

    # Boca de cañón en acero
    f_start = len(bm.faces)
    add_box(bm, (0.040, 0.02, 0.048), loc=(gun_center[0], gun_center[1] - 0.195, gun_center[2] + 0.01), rot=(4, -4, 0))
    for f in bm.faces[f_start:]:
        f.material_index = 2 # Cromo / acero

    # Celda cilíndrica con 6 segmentos de plasma púrpura
    cell_pos = (gun_center[0], gun_center[1] - 0.02, gun_center[2] + 0.01)
    for i in range(6):
        ang = TAU * i / 6
        ox, oz = math.sin(ang) * 0.032, math.cos(ang) * 0.032
        f_start = len(bm.faces)
        add_box(bm, (0.011, 0.048, 0.007), loc=(cell_pos[0] + ox, cell_pos[1], cell_pos[2] + oz), rot=(0, -math.degrees(ang), 0))
        for f in bm.faces[f_start:]:
            f.material_index = 4 # Plasma púrpura

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("SK_FPS_Arms_Hero", mesh)
    col.objects.link(obj)

    for p in obj.data.polygons:
        p.use_smooth = True

    return obj

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(960, 540)):
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

def main():
    print("=== CONSTRUYENDO Y RENDERIZANDO JUGADOR AAA ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    col = bpy.data.collections.new("Col_Showcase")
    scene.collection.children.link(col)

    mats = create_shaders()
    setup_studio()

    # 1. Construir modelo Tercera Persona
    player_objs = build_humanoid_body(col, mats)

    # Vista 1: Frontal
    print("Renderizando Vista 1: Frontal...")
    render_camera_view((0.0, 3.2, 1.25), (0.0, 0.0, 1.10), 45.0, V1_PATH)

    # Vista 2: Trasera (Exo-Espina con vértebras y plasma)
    print("Renderizando Vista 2: Trasera (Exo-Espina)...")
    render_camera_view((0.0, -3.2, 1.25), (0.0, 0.0, 1.10), 45.0, V2_PATH)

    # Vista 3: Acción 3/4
    print("Renderizando Vista 3: Acción 3/4...")
    render_camera_view((2.4, 2.4, 1.45), (0.0, 0.0, 1.10), 40.0, V3_PATH)

    # Ocultar 3ª persona y renderizar FPS
    for o in player_objs:
        o.hide_render = True

    fps_obj = build_fps_view(col, mats)

    # Vista 4: Primera Persona (FPS View mirando al arma y manos)
    print("Renderizando Vista 4: Primera Persona FPS...")
    render_camera_view((0.0, 0.05, -0.06), (0.03, -0.32, -0.07), 24.0, V4_PATH)

    print("=== RENDERS INDIVIDUALES COMPLETADOS CON ÉXITO ===")

if __name__ == "__main__":
    main()
