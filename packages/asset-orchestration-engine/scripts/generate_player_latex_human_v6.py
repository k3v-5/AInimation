"""generate_player_latex_human_v6.py
Generador Maestro AAA para Blender:
Personaje Humanoide en Piel Continua de Látex sin Ojos (Eyeless)
Pipeline anatómico profesional (VRM Base):
- Anatomía humana canónica atlética, topología orgánica limpia, manos de 5 dedos anatómicos y piernas atléticas.
- Rostro eyeless hermético impecable: cuencas oculares selladas y unificadas bajo piel de látex tensa, preservando puente nasal, labios, pómulos y mandíbula cincelada.
- Bóveda craneal continua y redondeada (sin conos ni protuberancias).
- Postura atlética: brazo derecho en A-pose relajada, brazo izquierdo en guardia táctica adelantada (antebrazo y mano en primer plano FPS).
- Shader PBR de látex negro obsidiana líquido: Dieléctrico estricto, Base Color (0.004, 0.004, 0.006), Coat 1.0 de alto brillo.
- Mosaico reglamentario de 4 cuadrantes (2560x1440) + Primer plano facial de alta resolución (1080x1080).
"""

import sys
import os
import math
import bpy
import bmesh
from mathutils import Matrix, Vector, Euler

R = math.radians

def clean_scene():
    """Limpia completamente la escena de Blender."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
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

def setup_studio_environment(scene):
    """Configura iluminación de estudio de tres puntos y suelo reflectante para látex líquido."""
    if not scene.world:
        scene.world = bpy.data.worlds.new("World_LatexStudio")
    scene.world.use_nodes = True
    nt = scene.world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (0.008, 0.010, 0.014, 1.0)
    bg.inputs['Strength'].default_value = 0.35
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

    # Suelo oscuro de estudio
    me_floor = bpy.data.meshes.new("StudioFloor")
    bm_fl = bmesh.new()
    bmesh.ops.create_grid(bm_fl, x_segments=16, y_segments=16, size=24.0, matrix=Matrix.Translation((0, 0, 0.0)))
    bm_fl.to_mesh(me_floor)
    bm_fl.free()

    m_floor = bpy.data.materials.new("M_StudioFloor")
    m_floor.use_nodes = True
    bsdf_fl = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_fl:
        bsdf_fl.inputs['Base Color'].default_value = (0.010, 0.012, 0.015, 1.0)
        bsdf_fl.inputs['Roughness'].default_value = 0.22
    me_floor.materials.append(m_floor)
    o_floor = bpy.data.objects.new("StudioFloor", me_floor)
    scene.collection.objects.link(o_floor)

    # 1. Key Light Frontal-Derecha
    l1_data = bpy.data.lights.new("LGT_KeyFront", 'AREA')
    l1_data.energy = 3200.0
    l1_data.size = 2.4
    l1_data.color = (1.0, 0.99, 0.96)
    l1 = bpy.data.objects.new("LGT_KeyFront", l1_data)
    l1.location = (2.0, -2.8, 2.2)
    l1.rotation_euler = (R(50), R(0), R(35))
    scene.collection.objects.link(l1)

    # 2. Fill Light Suave Frontal-Izquierda (Cool)
    l2_data = bpy.data.lights.new("LGT_FillCool", 'AREA')
    l2_data.energy = 1400.0
    l2_data.size = 3.2
    l2_data.color = (0.75, 0.88, 1.0)
    l2 = bpy.data.objects.new("LGT_FillCool", l2_data)
    l2.location = (-2.2, -2.2, 1.8)
    l2.rotation_euler = (R(42), R(0), R(-45))
    scene.collection.objects.link(l2)

    # 3. Rim Light Trasera Derecha
    l3_data = bpy.data.lights.new("LGT_RimRight", 'SPOT')
    l3_data.energy = 6500.0
    l3_data.spot_size = R(75)
    l3_data.color = (1.0, 1.0, 1.0)
    l3 = bpy.data.objects.new("LGT_RimRight", l3_data)
    l3.location = (2.2, 2.2, 2.2)
    l3.rotation_euler = (R(-45), R(15), R(-135))
    scene.collection.objects.link(l3)

    # 4. Rim Light Trasera Izquierda (Acento Violeta Neón)
    l4_data = bpy.data.lights.new("LGT_RimLeft", 'SPOT')
    l4_data.energy = 7000.0
    l4_data.spot_size = R(70)
    l4_data.color = (0.65, 0.12, 1.0)
    l4 = bpy.data.objects.new("LGT_RimLeft", l4_data)
    l4.location = (-2.2, 2.2, 2.2)
    l4.rotation_euler = (R(-45), R(-15), R(135))
    scene.collection.objects.link(l4)

    # 5. Top Light Cenital
    l5_data = bpy.data.lights.new("LGT_TopAccent", 'AREA')
    l5_data.energy = 1600.0
    l5_data.size = 2.0
    l5_data.color = (0.95, 0.98, 1.0)
    l5 = bpy.data.objects.new("LGT_TopAccent", l5_data)
    l5.location = (0.0, -0.2, 3.4)
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
    bsdf.inputs["Base Color"].default_value = (0.004, 0.004, 0.006, 1.0)
    # Regla 63: Dieléctrico estricto
    bsdf.inputs["Metallic"].default_value = 0.0
    # Rugosidad base de goma pulida
    bsdf.inputs["Roughness"].default_value = 0.052
    # Índice de refracción del látex natural (1.52)
    bsdf.inputs["IOR"].default_value = 1.52

    # Clearcoat / Coat (Capa líquida de látex pulido de alto brillo)
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = 1.0
        bsdf.inputs['Coat Roughness'].default_value = 0.014
        if 'Coat IOR' in bsdf.inputs:
            bsdf.inputs['Coat IOR'].default_value = 1.54
    elif 'Clearcoat' in bsdf.inputs:
        bsdf.inputs['Clearcoat'].default_value = 1.0
        bsdf.inputs['Clearcoat Roughness'].default_value = 0.014

    return mat

def process_head_eyeless_dome(h):
    """Procesa la cabeza: remueve shape keys, sella cuencas oculares y cierra la bóveda craneal con curvatura suave."""
    if h.data.shape_keys:
        for sk in list(h.data.shape_keys.key_blocks):
            h.shape_key_remove(sk)

    bm = bmesh.new()
    bm.from_mesh(h.data)

    # Eliminar caras que no pertenezcan al cuerpo
    non_body = [f for f in bm.faces if h.data.materials[f.material_index].name != 'body_bake']
    bmesh.ops.delete(bm, geom=non_body, context='FACES_ONLY')

    # Mantener únicamente la isla principal exterior (elimina decals y mallas internas)
    faces_set = set(bm.faces)
    islands = []
    while faces_set:
        f_start = faces_set.pop()
        island = {f_start}
        queue = [f_start]
        while queue:
            curr = queue.pop()
            for e in curr.edges:
                for n_f in e.link_faces:
                    if n_f in faces_set:
                        faces_set.remove(n_f)
                        island.add(n_f)
                        queue.append(n_f)
        islands.append(island)

    islands.sort(key=len, reverse=True)
    for small_isl in islands[1:]:
        bmesh.ops.delete(bm, geom=list(small_isl), context='FACES_ONLY')

    # Encontrar loops frontera
    b_edges = {e for e in bm.edges if e.is_boundary}
    loops = []
    while b_edges:
        start = b_edges.pop()
        loop = [start]
        v_curr = start.verts[1]
        while True:
            next_e = [e for e in v_curr.link_edges if e in b_edges]
            if not next_e:
                break
            e = next_e[0]
            b_edges.remove(e)
            loop.append(e)
            v_curr = e.other_vert(v_curr)
        loops.append(loop)

    # 1. Sellar Ojos y Scalp Cap limpiamente sin extrusión cónica
    for l in loops:
        z_avg = sum(v.co.z for e in l for v in e.verts) / (len(l) * 2)
        y_avg = sum(v.co.y for e in l for v in e.verts) / (len(l) * 2)
        if z_avg > 1.35 and (y_avg < -0.06 or len(l) > 100):
            res = bmesh.ops.edgeloop_fill(bm, edges=l)
            bmesh.ops.triangulate(bm, faces=res['faces'])

    # 2. Suavizar zona ocular (Eyeless hermético continuo)
    eye_verts = [v for v in bm.verts if v.co.z > 1.38 and v.co.z < 1.45 and v.co.y < -0.06]
    for _ in range(16):
        bmesh.ops.smooth_vert(bm, verts=eye_verts, factor=0.50)

    # 3. Suavizar bóveda craneal (Scalp Dome redondeado anatómico)
    scalp_verts = [v for v in bm.verts if v.co.z > 1.48]
    for _ in range(12):
        bmesh.ops.smooth_vert(bm, verts=scalp_verts, factor=0.40)

    for f in bm.faces:
        f.smooth = True

    bm.to_mesh(h.data)
    bm.free()

def process_wear_body(w):
    """Procesa el cuerpo: aísla la piel anatómica eliminando ropa y accesorios."""
    bm = bmesh.new()
    bm.from_mesh(w.data)

    body_mats = [i for i, m in enumerate(w.data.materials) if 'body' in m.name.lower()]
    non_body = [f for f in bm.faces if f.material_index not in body_mats]
    bmesh.ops.delete(bm, geom=non_body, context='FACES_ONLY')

    for f in bm.faces:
        f.smooth = True

    bm.to_mesh(w.data)
    bm.free()

def build_latex_human_character():
    """Ejecuta el pipeline completo de construcción del personaje de látex."""
    vrm_path = r"E:\Darx_Proyect\Saved\Anime_Benchmark_Workspace\Seed-san.vrm"
    if not os.path.exists(vrm_path):
        raise FileNotFoundError(f"No se encontró la base VRM: {vrm_path}")

    bpy.ops.import_scene.gltf(filepath=vrm_path)

    # Eliminar accesorios innecesarios
    for obj_name in ['hair', 'hair_tail', 'robo_arm', 'Cube', 'Icosphere']:
        o = bpy.data.objects.get(obj_name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    h = bpy.data.objects.get('head')
    w = bpy.data.objects.get('wear')
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

    # Procesar cabeza y cuerpo
    process_head_eyeless_dome(h)
    process_wear_body(w)

    # Unir cabeza y cuerpo
    bpy.context.view_layer.objects.active = w
    h.select_set(True)
    w.select_set(True)
    bpy.ops.object.join()
    w.name = 'SK_DarX_LatexHuman_Eyeless'

    bpy.ops.mesh.customdata_custom_splitnormals_clear()

    # Soldar costura del cuello
    bm_all = bmesh.new()
    bm_all.from_mesh(w.data)
    bmesh.ops.remove_doubles(bm_all, verts=bm_all.verts, dist=0.006)
    bm_all.to_mesh(w.data)
    bm_all.free()

    w.data.polygons.foreach_set('use_smooth', [True] * len(w.data.polygons))

    # Modificador Subsurf suave
    sub = w.modifiers.new('Subsurf', 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 1

    # Aplicar Material PBR Látex Negro
    mat_latex = create_pure_black_latex_material()
    w.data.materials.clear()
    w.data.materials.append(mat_latex)

    # Configurar Postura Atlética Dinámica
    pb = arm.pose.bones
    # Brazo Derecho: A-pose atlética al costado
    if 'upper_arm.R' in pb:
        pb['upper_arm.R'].rotation_quaternion = pb['upper_arm.R'].rotation_quaternion @ Euler((0, R(-10), R(52)), 'XYZ').to_quaternion()
    if 'forearm.R' in pb:
        pb['forearm.R'].rotation_quaternion = pb['forearm.R'].rotation_quaternion @ Euler((0, R(-12), R(10)), 'XYZ').to_quaternion()

    # Brazo Izquierdo: Guardia táctica adelantada (visible en FPS)
    if 'upper_arm.L' in pb:
        pb['upper_arm.L'].rotation_quaternion = pb['upper_arm.L'].rotation_quaternion @ Euler((R(35), R(10), R(-32)), 'XYZ').to_quaternion()
    if 'forearm.L' in pb:
        pb['forearm.L'].rotation_quaternion = pb['forearm.L'].rotation_quaternion @ Euler((R(48), R(-22), R(-32)), 'XYZ').to_quaternion()
    if 'hand.L' in pb:
        pb['hand.L'].rotation_quaternion = pb['hand.L'].rotation_quaternion @ Euler((R(12), R(15), 0), 'XYZ').to_quaternion()

    # Ajuste métrico canónico (1.80m de altura)
    scale_factor = 1.80 / 1.62
    arm.scale = (scale_factor, scale_factor, scale_factor)

    return w, arm

def render_view_camera(scene, cam_obj, loc, target, fov=45, filepath=""):
    """Reutiliza el objeto cámara existente para evitar memory leaks/crashes de OpenGL."""
    cam_obj.location = Vector(loc)
    dir_vec = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.data.angle = R(fov)

    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

def run():
    print("=" * 80)
    print("INICIANDO GENERACIÓN DE HUMANOIDE EYELESS EN PIEL DE LÁTEX PURA (V6)")
    print("=" * 80)

    clean_scene()
    scene = bpy.context.scene
    setup_studio_environment(scene)

    char_obj, arm_obj = build_latex_human_character()

    # Crear una única cámara reutilizable
    cam_data = bpy.data.cameras.new("Cam_RenderMaster")
    cam_obj = bpy.data.objects.new("Cam_RenderMaster", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_latex_human"
    os.makedirs(out_dir, exist_ok=True)

    # 1. Hero View (Perspectiva 3/4 Acción)
    print("Renderizando Hero View...")
    render_view_camera(scene, cam_obj, (1.8, -3.2, 1.35), (0, 0, 0.90), fov=40,
                       filepath=os.path.join(out_dir, "latex_hero_action.png"))

    # 2. Vista Frontal Completa
    print("Renderizando Vista Frontal...")
    render_view_camera(scene, cam_obj, (0, -3.4, 0.90), (0, 0, 0.90), fov=40,
                       filepath=os.path.join(out_dir, "latex_view_front.png"))

    # 3. Vista Trasera Completa
    print("Renderizando Vista Trasera...")
    render_view_camera(scene, cam_obj, (0, 3.4, 0.90), (0, 0, 0.90), fov=40,
                       filepath=os.path.join(out_dir, "latex_view_back.png"))

    # 4. Vista FPS (Brazos y manos 5 dedos en primer plano)
    print("Renderizando Vista FPS...")
    render_view_camera(scene, cam_obj, (-0.05, -0.05, 1.50), (-0.15, -0.65, 1.15), fov=68,
                       filepath=os.path.join(out_dir, "latex_view_fps.png"))

    # 5. Primer Plano Rostro Eyeless
    print("Renderizando Primer Plano Rostro Eyeless...")
    render_view_camera(scene, cam_obj, (0.15, -0.80, 1.58), (0, 0, 1.54), fov=26,
                       filepath=os.path.join(out_dir, "latex_face_closeup.png"))

    # Guardar archivo .blend maestro de trabajo
    save_dir = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace"
    os.makedirs(save_dir, exist_ok=True)
    blend_path = os.path.join(save_dir, "DarX_Player_LatexHuman_V2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Archivo .blend maestro guardado: {blend_path}")
    print("Generación completada con éxito.")

if __name__ == "__main__":
    run()
