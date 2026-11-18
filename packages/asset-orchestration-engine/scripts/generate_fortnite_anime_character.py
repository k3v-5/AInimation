"""
Generador Maestro de Personaje Anime Cel-Shaded Estilo Fortnite (Techwear Hoodie)
Basado en la referencia visual:
- Sudadera blanca extragrande con capucha envolvente levantada y visera frontal parabólica
- Auriculares circumaurales naranja ámbar con almohadillas negras y cable colgante
- Cabello teal oscuro con flequillo recto
- Ojos rojo rubí vibrantes con contorno estilo cómic
- Cuello alto estructurado con parches de velcro
- Cremallera diagonal en el pecho derecho con tirador
- Parche táctico 'hazard' naranja con franjas diagonales en el hombro
- Sombreado Cel-Shaded Toon (ShaderToRGB) y contornos Inverted Hull
- Rig en A-Pose relajada (3/4 anime stance)
- Previsualización en 4 cuadrantes (Regla 5 de DarX)
"""

import bpy
import bmesh
import math
import os
import mathutils
from mathutils import Vector, Euler, Quaternion

def run():
    print("=" * 80)
    print("INICIANDO GENERACIÓN DE PERSONAJE FORTNITE ANIME (TECHWEAR HOODIE)")
    print("=" * 80)

    # 1. LIMPIAR ESCENA COMPLETAMENTE
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    col = bpy.data.collections.new("Fortnite_Anime_Character")
    scene.collection.children.link(col)

    # Configuración de Mundo (Estudio NPR)
    world = bpy.data.worlds.new("NPR_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.08, 0.09, 0.12, 1.0)
        bg_node.inputs['Strength'].default_value = 0.5

    # 2. IMPORTAR BASE HUMANOIDE ANIME (VRM GLTF 2.0)
    vrm_path = r"E:\Darx_Proyect\Saved\Anime_Benchmark_Workspace\Seed-san.vrm"
    if not os.path.exists(vrm_path):
        raise FileNotFoundError(f"No se encontró el avatar base: {vrm_path}")

    bpy.ops.import_scene.gltf(filepath=vrm_path)

    for obj in list(scene.collection.objects):
        col.objects.link(obj)
        scene.collection.objects.unlink(obj)

    # 3. ELIMINAR ACCESORIOS INNECESARIOS (Brazo robótico y cola de caballo)
    for obj_name in ['robo_arm', 'hair_tail']:
        o = bpy.data.objects.get(obj_name)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)

    # Eliminar mochila de wear
    w = bpy.data.objects.get('wear')
    if w:
        bm = bmesh.new()
        bm.from_mesh(w.data)
        del_mats = {'backpack_metal', 'backpack_nm', 'backpack_plastic', 'anim_logo', 'robo_face', 'glass', 'green_emit'}
        del_indices = {i for i, m in enumerate(w.data.materials) if m.name in del_mats}
        faces_to_del = [f for f in bm.faces if f.material_index in del_indices]
        bmesh.ops.delete(bm, geom=faces_to_del, context='FACES_ONLY')
        bm.to_mesh(w.data)
        bm.free()

    # 4. CONFIGURAR MATERIALES Y SHADERS FORTNITE CEL-SHADED
    def get_sock(sockets, identifier):
        return next(s for s in sockets if s.identifier == identifier)

    # A. Ojos Rubí Vibrantes
    m_eye = bpy.data.materials.get('eye')
    if m_eye and m_eye.use_nodes:
        nodes = m_eye.node_tree.nodes
        tex = nodes.get('Image Texture')
        emit = nodes.get('Emission')
        if tex and emit:
            mix_eye = nodes.new('ShaderNodeMix')
            mix_eye.data_type = 'RGBA'
            mix_eye.blend_type = 'COLOR'
            get_sock(mix_eye.inputs, 'Factor_Float').default_value = 0.95
            get_sock(mix_eye.inputs, 'B_Color').default_value = (0.95, 0.04, 0.12, 1.0)
            m_eye.node_tree.links.new(tex.outputs['Color'], get_sock(mix_eye.inputs, 'A_Color'))
            m_eye.node_tree.links.new(get_sock(mix_eye.outputs, 'Result_Color'), emit.inputs['Color'])

    # B. Cabello Teal / Turquesa Petróleo Oscuro
    m_hair = bpy.data.materials.get('hair')
    if m_hair and m_hair.use_nodes:
        nodes = m_hair.node_tree.nodes
        tex = nodes.get('Image Texture')
        emit = nodes.get('Emission')
        if tex and emit:
            mix_hair = nodes.new('ShaderNodeMix')
            mix_hair.data_type = 'RGBA'
            mix_hair.blend_type = 'COLOR'
            get_sock(mix_hair.inputs, 'Factor_Float').default_value = 0.92
            get_sock(mix_hair.inputs, 'B_Color').default_value = (0.04, 0.35, 0.40, 1.0)
            m_hair.node_tree.links.new(tex.outputs['Color'], get_sock(mix_hair.inputs, 'A_Color'))
            m_hair.node_tree.links.new(get_sock(mix_hair.outputs, 'Result_Color'), emit.inputs['Color'])

    # Material de Tinta Negra Inverted Hull
    m_ink = bpy.data.materials.new(name="M_Fortnite_Ink_Outline")
    m_ink.use_backface_culling = True
    nodes_ink = m_ink.node_tree.nodes
    nodes_ink.clear()
    out_ink = nodes_ink.new('ShaderNodeOutputMaterial')
    emit_ink = nodes_ink.new('ShaderNodeEmission')
    emit_ink.inputs['Color'].default_value = (0.03, 0.02, 0.04, 1.0)
    emit_ink.inputs['Strength'].default_value = 1.0
    m_ink.node_tree.links.new(emit_ink.outputs['Emission'], out_ink.inputs['Surface'])

    # Shaders Toon de 2 bandas
    def create_cel_mat(name, base_col, shadow_col, cutoff=0.46, rough=0.35):
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (800, 0)
        
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = base_col
        bsdf.inputs['Roughness'].default_value = rough
        
        s2rgb = nodes.new('ShaderNodeShaderToRGB')
        s2rgb.location = (250, 0)
        mat.node_tree.links.new(bsdf.outputs['BSDF'], s2rgb.inputs['Shader'])
        
        cramp = nodes.new('ShaderNodeValToRGB')
        cramp.location = (450, 0)
        cramp.color_ramp.interpolation = 'CONSTANT'
        cramp.color_ramp.elements[0].position = 0.0
        cramp.color_ramp.elements[0].color = shadow_col
        cramp.color_ramp.elements[1].position = cutoff
        cramp.color_ramp.elements[1].color = base_col
        mat.node_tree.links.new(s2rgb.outputs['Color'], cramp.inputs['Fac'])
        
        emit = nodes.new('ShaderNodeEmission')
        emit.location = (650, 0)
        mat.node_tree.links.new(cramp.outputs['Color'], emit.inputs['Color'])
        mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
        return mat

    m_hoodie_white = create_cel_mat("M_Fortnite_Hoodie_White", 
                                    base_col=(0.95, 0.95, 0.97, 1.0), 
                                    shadow_col=(0.74, 0.77, 0.83, 1.0), cutoff=0.45)
    
    m_amber_orange = create_cel_mat("M_Fortnite_Amber_Orange", 
                                    base_col=(1.0, 0.48, 0.01, 1.0), 
                                    shadow_col=(0.78, 0.28, 0.00, 1.0), cutoff=0.42)

    m_dark_tech = create_cel_mat("M_Fortnite_Dark_Tech", 
                                 base_col=(0.14, 0.15, 0.19, 1.0), 
                                 shadow_col=(0.06, 0.07, 0.09, 1.0), cutoff=0.40)

    m_velcro_grey = create_cel_mat("M_Fortnite_Velcro_Grey", 
                                   base_col=(0.62, 0.65, 0.70, 1.0), 
                                   shadow_col=(0.45, 0.48, 0.53, 1.0), cutoff=0.45)

    def apply_inverted_hull(obj, thickness=0.0028):
        if obj.type != 'MESH':
            return
        if m_ink.name not in [m.name for m in obj.data.materials if m]:
            obj.data.materials.append(m_ink)
        mat_idx = [i for i, m in enumerate(obj.data.materials) if m and m.name == m_ink.name][0]
        
        mod = obj.modifiers.new(name="NPR_InvertedHull", type='SOLIDIFY')
        mod.thickness = thickness
        mod.offset = 1.0
        mod.use_flip_normals = True
        mod.use_rim = True
        mod.material_offset = mat_idx
        mod.material_offset_rim = mat_idx
        mod.use_quality_normals = True
        return mod

    # 5. POSE DEL ESQUELETO (A-POSE RELAJADA Y VISTA 3/4)
    arm = [o for o in col.objects if o.type == 'ARMATURE']
    if arm:
        arm_obj = arm[0]
        pb = arm_obj.pose.bones
        if 'upper_arm.L' in pb:
            pb['upper_arm.L'].rotation_quaternion = pb['upper_arm.L'].rotation_quaternion @ Euler((0, math.radians(10), math.radians(-48)), 'XYZ').to_quaternion()
        if 'upper_arm.R' in pb:
            pb['upper_arm.R'].rotation_quaternion = pb['upper_arm.R'].rotation_quaternion @ Euler((0, math.radians(-10), math.radians(48)), 'XYZ').to_quaternion()
        if 'forearm.L' in pb:
            pb['forearm.L'].rotation_quaternion = pb['forearm.L'].rotation_quaternion @ Euler((0, math.radians(10), math.radians(-8)), 'XYZ').to_quaternion()
        if 'forearm.R' in pb:
            pb['forearm.R'].rotation_quaternion = pb['forearm.R'].rotation_quaternion @ Euler((0, math.radians(-10), math.radians(8)), 'XYZ').to_quaternion()
        if 'head 1' in pb:
            pb['head 1'].rotation_quaternion = pb['head 1'].rotation_quaternion @ Euler((math.radians(-2), math.radians(3), math.radians(12)), 'XYZ').to_quaternion()

    # 6. CAPUCHA TÁCTICA EXTRAGRANDE CON ALERO/VISERA Y CAÍDA A HOMBROS
    bm_hood = bmesh.new()
    bmesh.ops.create_uvsphere(bm_hood, u_segments=48, v_segments=36, radius=0.175)

    to_del = []
    for v in bm_hood.verts:
        v.co.x *= 1.16
        v.co.y *= 1.16
        v.co.z *= 1.20
        v.co.y += 0.015
        v.co.z += 1.480
        
        # Caída continua hacia los hombros en nuca y laterales (Y > -0.04)
        if v.co.z < 1.38 and v.co.y > -0.04:
            drop = (1.38 - v.co.z) * 1.5
            v.co.z -= drop
            v.co.x *= 1.08
            v.co.y *= 1.08
            
        # Apertura facial en arco elíptico (desde Z=1.28 hasta Z=1.46)
        ell = (v.co.x / 0.125)**2 + ((v.co.z - 1.375) / 0.105)**2
        if v.co.y < 0.010 and ell < 1.0 and v.co.z > 1.28:
            to_del.append(v)
        elif v.co.y < 0.0 and v.co.z >= 1.46 and v.co.z <= 1.58:
            factor = max(0.0, 1.0 - (v.co.x / 0.125)**2)
            v.co.y -= 0.065 * factor
            v.co.z -= 0.018 * factor

    bmesh.ops.delete(bm_hood, geom=to_del, context='VERTS')
    bmesh.ops.recalc_face_normals(bm_hood, faces=bm_hood.faces)
    mesh_hood = bpy.data.meshes.new("CH_Fortnite_Hood_Mesh")
    bm_hood.to_mesh(mesh_hood)
    bm_hood.free()

    obj_hood = bpy.data.objects.new("CH_Fortnite_Hood", mesh_hood)
    obj_hood.data.materials.append(m_hoodie_white)
    mesh_hood.shade_smooth()
    
    mod_solid = obj_hood.modifiers.new("Hood_Thickness", 'SOLIDIFY')
    mod_solid.thickness = 0.007
    mod_solid.offset = -1.0
    mod_sub = obj_hood.modifiers.new("Hood_Subsurf", 'SUBSURF')
    mod_sub.levels = 2
    apply_inverted_hull(obj_hood, thickness=0.0030)
    col.objects.link(obj_hood)

    # 7. CUELLO ALTO ESTRUCTURADO (HIGH COLLAR - JUSTO DEBAJO DE LA BARBILLA)
    bm_col = bmesh.new()
    bmesh.ops.create_cone(bm_col, cap_ends=False, segments=32, radius1=0.100, radius2=0.088, depth=0.075)
    for v in bm_col.verts:
        v.co.y *= 0.88
        v.co.z += 1.238
        v.co.y -= 0.010
    bmesh.ops.recalc_face_normals(bm_col, faces=bm_col.faces)
    mesh_col = bpy.data.meshes.new("CH_Fortnite_Collar_Mesh")
    bm_col.to_mesh(mesh_col)
    bm_col.free()

    obj_collar = bpy.data.objects.new("CH_Fortnite_Collar", mesh_col)
    obj_collar.data.materials.append(m_hoodie_white)
    mesh_col.shade_smooth()
    col_s = obj_collar.modifiers.new("Collar_Solid", 'SOLIDIFY')
    col_s.thickness = 0.004
    apply_inverted_hull(obj_collar, thickness=0.0026)
    col.objects.link(obj_collar)

    # Parches Rectangulares de Velcro Gris en el frente del cuello
    for idx, z_off in enumerate([1.260, 1.222]):
        bm_v = bmesh.new()
        bmesh.ops.create_cube(bm_v, size=1.0)
        for v in bm_v.verts:
            v.co.x *= 0.014
            v.co.y *= 0.003
            v.co.z *= 0.013
        mesh_v = bpy.data.meshes.new(f"CH_Fortnite_Velcro_{idx}_Mesh")
        bm_v.to_mesh(mesh_v)
        bm_v.free()
        obj_v = bpy.data.objects.new(f"CH_Fortnite_Velcro_{idx}", mesh_v)
        obj_v.location = (0.006, -0.092, z_off)
        obj_v.rotation_euler = (math.radians(10), 0, math.radians(-3))
        obj_v.data.materials.append(m_velcro_grey)
        apply_inverted_hull(obj_v, thickness=0.0018)
        col.objects.link(obj_v)

    # 8. CREMALLERA DIAGONAL NEGRA EN PECHO DERECHO CON TIRADOR
    bm_zip = bmesh.new()
    bmesh.ops.create_cube(bm_zip, size=1.0)
    for v in bm_zip.verts:
        v.co.x *= 0.010
        v.co.y *= 0.004
        v.co.z *= 0.055
    mesh_zip = bpy.data.meshes.new("CH_Fortnite_Zipper_Mesh")
    bm_zip.to_mesh(mesh_zip)
    bm_zip.free()
    obj_zip = bpy.data.objects.new("CH_Fortnite_Zipper", mesh_zip)
    obj_zip.location = (-0.055, -0.092, 1.205)
    obj_zip.rotation_euler = (math.radians(12), math.radians(18), math.radians(38))
    obj_zip.data.materials.append(m_dark_tech)
    apply_inverted_hull(obj_zip, thickness=0.0020)
    col.objects.link(obj_zip)

    # Tirador de cremallera
    bm_pull = bmesh.new()
    bmesh.ops.create_cube(bm_pull, size=1.0)
    for v in bm_pull.verts:
        v.co.x *= 0.007
        v.co.y *= 0.003
        v.co.z *= 0.018
    mesh_pull = bpy.data.meshes.new("CH_Fortnite_ZipPull_Mesh")
    bm_pull.to_mesh(mesh_pull)
    bm_pull.free()
    obj_pull = bpy.data.objects.new("CH_Fortnite_ZipPull", mesh_pull)
    obj_pull.location = (-0.072, -0.095, 1.180)
    obj_pull.rotation_euler = (math.radians(12), math.radians(18), math.radians(38))
    obj_pull.data.materials.append(m_dark_tech)
    col.objects.link(obj_pull)

    # 9. PARCHE TÁCTICO HAZARD NARANJA EN HOMBRO DERECHO
    bm_patch = bmesh.new()
    bmesh.ops.create_cube(bm_patch, size=1.0)
    for v in bm_patch.verts:
        v.co.x *= 0.012
        v.co.y *= 0.045
        v.co.z *= 0.032
        v.co.x -= (v.co.y / 0.045)**2 * 0.004
    mesh_patch = bpy.data.meshes.new("CH_Fortnite_HazardPatch_Mesh")
    bm_patch.to_mesh(mesh_patch)
    bm_patch.free()
    obj_patch = bpy.data.objects.new("CH_Fortnite_HazardPatch", mesh_patch)
    obj_patch.location = (-0.178, -0.012, 1.22)
    obj_patch.rotation_euler = (math.radians(10), math.radians(22), math.radians(-10))
    obj_patch.data.materials.append(m_amber_orange)
    apply_inverted_hull(obj_patch, thickness=0.0024)
    col.objects.link(obj_patch)

    # Franjas oscuras diagonales de peligro
    for s_i in range(3):
        bm_s = bmesh.new()
        bmesh.ops.create_cube(bm_s, size=1.0)
        for v in bm_s.verts:
            v.co.x *= 0.003
            v.co.y *= 0.008
            v.co.z *= 0.024
        mesh_s = bpy.data.meshes.new(f"CH_Fortnite_Stripe_{s_i}_Mesh")
        bm_s.to_mesh(mesh_s)
        bm_s.free()
        obj_s = bpy.data.objects.new(f"CH_Fortnite_Stripe_{s_i}", mesh_s)
        obj_s.location = (-0.190, -0.026 + s_i * 0.018, 1.22)
        obj_s.rotation_euler = (math.radians(10), math.radians(22), math.radians(-32))
        obj_s.data.materials.append(m_dark_tech)
        col.objects.link(obj_s)

    # 10. AURICULARES CIRCUMAURALES TÁCTICOS (HEADPHONES)
    for side, sign in [("L", 1), ("R", -1)]:
        bm_c = bmesh.new()
        bmesh.ops.create_cone(bm_c, cap_ends=True, segments=24, radius1=0.042, radius2=0.042, depth=0.024)
        mesh_c = bpy.data.meshes.new(f"CH_Fortnite_Cup_{side}_Mesh")
        bm_c.to_mesh(mesh_c)
        bm_c.free()
        obj_c = bpy.data.objects.new(f"CH_Fortnite_Cup_{side}", mesh_c)
        obj_c.location = (sign * 0.108, -0.012, 1.44)
        obj_c.rotation_euler = (0, math.radians(90), 0)
        obj_c.data.materials.append(m_amber_orange)
        mesh_c.shade_smooth()
        apply_inverted_hull(obj_c, thickness=0.0024)
        col.objects.link(obj_c)

        bm_p = bmesh.new()
        bmesh.ops.create_cone(bm_p, cap_ends=True, segments=24, radius1=0.036, radius2=0.036, depth=0.015)
        mesh_p = bpy.data.meshes.new(f"CH_Fortnite_Pad_{side}_Mesh")
        bm_p.to_mesh(mesh_p)
        bm_p.free()
        obj_p = bpy.data.objects.new(f"CH_Fortnite_Pad_{side}", mesh_p)
        obj_p.location = (sign * 0.096, -0.012, 1.44)
        obj_p.rotation_euler = (0, math.radians(90), 0)
        obj_p.data.materials.append(m_dark_tech)
        mesh_p.shade_smooth()
        col.objects.link(obj_p)

    # Diadema conectora
    band_c = bpy.data.curves.new("CH_Fortnite_Headband_Curve", type='CURVE')
    band_c.dimensions = '3D'
    band_c.resolution_u = 16
    band_c.bevel_depth = 0.009
    band_c.bevel_resolution = 3
    spline_b = band_c.splines.new('BEZIER')
    b_pts = [
        (-0.108, -0.012, 1.44),
        (-0.075, -0.012, 1.55),
        ( 0.000, -0.012, 1.58),
        ( 0.075, -0.012, 1.55),
        ( 0.108, -0.012, 1.44)
    ]
    spline_b.bezier_points.add(len(b_pts) - 1)
    for i, pt in enumerate(b_pts):
        bp = spline_b.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj_band = bpy.data.objects.new("CH_Fortnite_Headband", band_c)
    obj_band.data.materials.append(m_dark_tech)
    col.objects.link(obj_band)

    # Cable de Audio Naranja Estilizado
    cable_c = bpy.data.curves.new("CH_Fortnite_AudioCord_Curve", type='CURVE')
    cable_c.dimensions = '3D'
    cable_c.resolution_u = 24
    cable_c.bevel_depth = 0.0040
    cable_c.bevel_resolution = 3
    spline_c = cable_c.splines.new('BEZIER')
    cord_pts = [
        ( 0.108, -0.015, 1.415),
        ( 0.096, -0.045, 1.360),
        ( 0.082, -0.078, 1.290),
        ( 0.072, -0.096, 1.220),
        ( 0.065, -0.102, 1.140)
    ]
    spline_c.bezier_points.add(len(cord_pts) - 1)
    for i, pt in enumerate(cord_pts):
        bp = spline_c.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj_cord = bpy.data.objects.new("CH_Fortnite_AudioCord", cable_c)
    obj_cord.data.materials.append(m_amber_orange)
    col.objects.link(obj_cord)

    # 11. CONTORNOS INVERTED HULL EN CUERPO Y CABELLO
    for obj in col.objects:
        if obj.type == 'MESH' and obj.name in ['head', 'hair', 'wear']:
            apply_inverted_hull(obj, thickness=0.0026)

    # 12. ILUMINACIÓN CEL-SHADED ESTILO FORTNITE
    l_key = bpy.data.objects.new("L_Key_Frontal", bpy.data.lights.new("L_Key_Frontal", 'AREA'))
    l_key.data.energy = 95.0
    l_key.data.size = 2.8
    l_key.data.color = (1.0, 0.97, 0.94)
    l_key.location = (1.2, -2.0, 1.9)
    l_key.rotation_euler = (math.radians(50), 0, math.radians(30))
    col.objects.link(l_key)

    l_fill = bpy.data.objects.new("L_Fill_Soft", bpy.data.lights.new("L_Fill_Soft", 'AREA'))
    l_fill.data.energy = 35.0
    l_fill.data.size = 3.6
    l_fill.data.color = (0.78, 0.88, 1.0)
    l_fill.location = (-1.8, -1.8, 1.5)
    l_fill.rotation_euler = (math.radians(45), 0, math.radians(-42))
    col.objects.link(l_fill)

    l_rim = bpy.data.objects.new("L_Rim_Back", bpy.data.lights.new("L_Rim_Back", 'SPOT'))
    l_rim.data.energy = 140.0
    l_rim.data.spot_size = math.radians(70)
    l_rim.data.color = (0.92, 0.95, 1.0)
    l_rim.location = (-0.4, 2.2, 2.5)
    l_rim.rotation_euler = (math.radians(-130), math.radians(-8), math.radians(-160))
    col.objects.link(l_rim)

    # Ciclorama Gris Pizarra Neutro
    bm_bg = bmesh.new()
    bmesh.ops.create_grid(bm_bg, x_segments=20, y_segments=20, size=12.0)
    for v in bm_bg.verts:
        if v.co.y > 0:
            v.co.z += (v.co.y / 3.0)**2 * 4.0
        v.co.y += 2.4
    bmesh.ops.recalc_face_normals(bm_bg, faces=bm_bg.faces)
    mesh_bg = bpy.data.meshes.new("Studio_Backdrop_Mesh")
    bm_bg.to_mesh(mesh_bg)
    bm_bg.free()
    obj_bg = bpy.data.objects.new("Studio_Backdrop", mesh_bg)
    m_bg = create_cel_mat("M_Studio_Backdrop", (0.13, 0.15, 0.20, 1.0), (0.08, 0.09, 0.12, 1.0))
    obj_bg.data.materials.append(m_bg)
    col.objects.link(obj_bg)

    # 13. CONFIGURACIÓN DE LAS 4 CÁMARAS OBLIGATORIAS (REGLA 5)
    output_dir = r"E:\Darx_Proyect\Saved\Fortnite_Anime_Workspace"
    os.makedirs(output_dir, exist_ok=True)

    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    cameras_fortnite = [
        # Vista 1: Retrato 3/4 idéntico al ángulo y encuadre de la imagen de referencia (Bust Shot)
        ("Cam_01_Retrato_Ref", 70.0, (-0.42, -1.15, 1.37), (-0.03, -0.02, 1.34), "view_03_retrato.png"),
        # Vista 2: Frontal Completa (Proporciones y silueta en A-Pose)
        ("Cam_02_Frontal", 45.0, (0.0, -3.0, 0.95), (0.0, 0.0, 0.90), "view_01_frontal.png"),
        # Vista 3: Trasera (Capucha levantada, drapeado dorsal)
        ("Cam_03_Trasera", 45.0, (0.0, 3.0, 0.95), (0.0, 0.0, 0.90), "view_02_trasera.png"),
        # Vista 4: Acción / Perspectiva 3/4 Dinámica de Fortnite
        ("Cam_04_Accion34", 42.0, (1.6, -2.6, 1.20), (0.0, 0.0, 0.90), "view_04_accion34.png")
    ]

    for name, lens, loc, target, filename in cameras_fortnite:
        cam_d = bpy.data.cameras.new(name)
        cam_d.lens = lens
        cam_o = bpy.data.objects.new(name, cam_d)
        cam_o.location = loc
        direction = Vector(target) - Vector(loc)
        cam_o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        col.objects.link(cam_o)
        scene.camera = cam_o

        out_p = os.path.join(output_dir, filename)
        scene.render.filepath = out_p
        print(f"Renderizando {name} -> {out_p}...")
        bpy.ops.render.render(write_still=True)

    # 14. EXPORTACIÓN FBX
    fbx_path = os.path.join(output_dir, "SK_Fortnite_Anime.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    char_objs = [o for o in col.objects if o.type == 'MESH' and not o.name.startswith("Studio_")]
    for o in char_objs:
        o.select_set(True)
    if char_objs:
        bpy.context.view_layer.objects.active = char_objs[0]
        bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, apply_scale_options='FBX_SCALE_UNITS')
        print(f"FBX Fortnite Anime Exportado: {fbx_path} ({len(char_objs)} mallas)")

    # Guardar escena .blend
    blend_out = os.path.join(output_dir, "CH_Fortnite_Anime.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"Escena .blend guardada en: {blend_out}")
    print("=" * 80)
    print("PERSONAJE FORTNITE ANIME COMPLETADO EXITOSAMENTE")
    print("=" * 80)

if __name__ == '__main__':
    run()
