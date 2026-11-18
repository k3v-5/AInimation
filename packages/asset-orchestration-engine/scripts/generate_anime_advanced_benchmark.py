"""
Anime Character Pipeline: Benchmark and Comparative Suite (Blender 5.2 EEVEE)
==============================================================================
Constructs 4 incremental variations to evaluate and compare:
  1. Baseline CSG: Primitivas rígidas (referencia anterior).
  2. Organic + Bezier Hair: Malla continua con subdivisión Catmull-Clark y pelo por curvas Bézier.
  3. Inverted Hull: Modificador Solidify con normales invertidas y backface culling (línea de tinta).
  4. Hybrid Complete: Fusión de anatomía orgánica, curvas Bézier, Inverted Hull, cel-shading de 2 tonos,
     bufanda cibernética ondeante y katana táctica.
"""

import os
import sys
import math
import shutil

try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler, Matrix
except ImportError:
    print("ERROR: Ejecutar dentro de Blender.")
    sys.exit(1)

# 1. SETUP DE ESCENA AISLADA (REGLA 52)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

world = bpy.data.worlds.new("Anime_Benchmark_World")
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.12, 0.14, 0.18, 1.0)
    bg_node.inputs['Strength'].default_value = 0.7
scene.world = world

col = bpy.data.collections.new("AOE_Anime_Benchmark")
scene.collection.children.link(col)

# 2. MATERIALES NPR CEL-SHADED Y OUTLINE INVERTED HULL
# Outline Material (Emisión unlit con backface culling)
m_outline = bpy.data.materials.new(name="M_Anime_NPR_Outline")
m_outline.use_backface_culling = True
nodes_o = m_outline.node_tree.nodes
nodes_o.clear()
out_o = nodes_o.new('ShaderNodeOutputMaterial')
emit_o = nodes_o.new('ShaderNodeEmission')
emit_o.inputs['Color'].default_value = (0.04, 0.02, 0.08, 1.0)
emit_o.inputs['Strength'].default_value = 1.0
m_outline.node_tree.links.new(emit_o.outputs['Emission'], out_o.inputs['Surface'])

def create_toon_mat(name, base_col, shadow_col, rough=0.3):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (800, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
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
    cramp.color_ramp.elements[1].position = 0.46
    cramp.color_ramp.elements[1].color = base_col
    mat.node_tree.links.new(s2rgb.outputs['Color'], cramp.inputs['Fac'])
    
    emit = nodes.new('ShaderNodeEmission')
    emit.location = (650, 0)
    mat.node_tree.links.new(cramp.outputs['Color'], emit.inputs['Color'])
    mat.node_tree.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

m_skin_npr = create_toon_mat("M_Skin_NPR", (0.98, 0.90, 0.85, 1.0), (0.86, 0.74, 0.72, 1.0))
m_hair_npr = create_toon_mat("M_Hair_NPR", (0.34, 0.20, 0.56, 1.0), (0.18, 0.10, 0.32, 1.0))
m_suit_npr = create_toon_mat("M_Suit_NPR", (0.14, 0.16, 0.22, 1.0), (0.07, 0.08, 0.11, 1.0))
m_armor_npr = create_toon_mat("M_Armor_NPR", (0.96, 0.96, 0.98, 1.0), (0.78, 0.82, 0.88, 1.0))
m_scarf_npr = create_toon_mat("M_Scarf_NPR", (0.88, 0.16, 0.32, 1.0), (0.58, 0.08, 0.20, 1.0))
m_eyes_npr = create_toon_mat("M_Eyes_NPR", (0.05, 0.85, 1.0, 1.0), (0.02, 0.50, 0.75, 1.0))

# Flat baseline materials (for model 1)
def create_flat_mat(name, col_rgba):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = col_rgba
    bsdf.inputs['Roughness'].default_value = 0.35
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

m_skin_flat = create_flat_mat("M_Skin_Flat", (0.98, 0.89, 0.83, 1.0))
m_hair_flat = create_flat_mat("M_Hair_Flat", (0.26, 0.16, 0.46, 1.0))
m_suit_flat = create_flat_mat("M_Suit_Flat", (0.11, 0.13, 0.18, 1.0))
m_armor_flat = create_flat_mat("M_Armor_Flat", (0.95, 0.96, 0.98, 1.0))

m_glow = bpy.data.materials.new("M_Glow_NPR")
nodes_gl = m_glow.node_tree.nodes
nodes_gl.clear()
out_gl = nodes_gl.new('ShaderNodeOutputMaterial')
emit_gl = nodes_gl.new('ShaderNodeEmission')
emit_gl.inputs['Color'].default_value = (0.0, 0.92, 1.0, 1.0)
emit_gl.inputs['Strength'].default_value = 5.0
m_glow.node_tree.links.new(emit_gl.outputs['Emission'], out_gl.inputs['Surface'])

# 3. HELPER INVERTED HULL SOLIDIFY
def apply_inverted_hull(obj, outline_mat=m_outline, thickness=0.0035):
    if obj.type != 'MESH':
        return
    if outline_mat.name not in [m.name for m in obj.data.materials if m]:
        obj.data.materials.append(outline_mat)
    mat_idx = [i for i, m in enumerate(obj.data.materials) if m and m.name == outline_mat.name][0]
    
    mod = obj.modifiers.new(name="NPR_InvertedHull", type='SOLIDIFY')
    mod.thickness = thickness
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = True
    mod.material_offset = mat_idx
    mod.material_offset_rim = mat_idx
    mod.use_quality_normals = True
    return mod

# 4. HELPER CURVAS BÉZIER PARA CABELLO
def create_bezier_hair_strand(name, points, r_root=0.022, r_tip=0.002, mat=m_hair_npr, offset_x=0.0):
    curve_data = bpy.data.curves.new(name + "_Data", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_resolution = 3
    curve_data.bevel_depth = r_root
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = (pt[0] + offset_x, pt[1], pt[2])
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        t = i / max(1, len(points) - 1)
        bp.radius = (1.0 - t) + (r_tip / max(0.0001, r_root)) * t

    obj = bpy.data.objects.new(name, curve_data)
    if mat:
        obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

def build_bezier_hair_set(prefix, offset_x, mat=m_hair_npr):
    objects = []
    # Bangs (Centro, Izquierda, Derecha)
    bang_specs = [
        ("Bang_Center", [(0.0, -0.065, 1.635), (0.0, -0.092, 1.585), (0.0, -0.096, 1.515)], 0.016, 0.002),
        ("Bang_L", [(0.030, -0.060, 1.630), (0.040, -0.090, 1.575), (0.045, -0.092, 1.505)], 0.015, 0.002),
        ("Bang_R", [(-0.030, -0.060, 1.630), (-0.040, -0.090, 1.575), (-0.045, -0.092, 1.505)], 0.015, 0.002),
        ("Bang_Out_L", [(0.060, -0.050, 1.620), (0.080, -0.082, 1.555), (0.086, -0.076, 1.485)], 0.018, 0.002),
        ("Bang_Out_R", [(-0.060, -0.050, 1.620), (-0.080, -0.082, 1.555), (-0.086, -0.076, 1.485)], 0.018, 0.002),
    ]
    for bname, pts, r1, r2 in bang_specs:
        o = create_bezier_hair_strand(f"{prefix}_{bname}", pts, r1, r2, mat, offset_x)
        objects.append(o)
    
    # Sideburns (Patillas)
    for side, sign in [("L", 1), ("R", -1)]:
        pts_sb = [
            (sign * 0.085, -0.025, 1.600),
            (sign * 0.092, -0.055, 1.520),
            (sign * 0.086, -0.065, 1.430),
            (sign * 0.075, -0.058, 1.365)
        ]
        o = create_bezier_hair_strand(f"{prefix}_Sideburn_{side}", pts_sb, 0.018, 0.003, mat, offset_x)
        objects.append(o)

    # Ponytail (Coleta Alta)
    pts_pt_main = [
        (0.00, 0.080, 1.640),
        (0.01, 0.160, 1.690),
        (0.02, 0.260, 1.620),
        (0.03, 0.350, 1.490),
        (0.04, 0.420, 1.340)
    ]
    o_main = create_bezier_hair_strand(f"{prefix}_Ponytail_Main", pts_pt_main, 0.040, 0.004, mat, offset_x)
    objects.append(o_main)

    for side, sign in [("L", 1), ("R", -1)]:
        pts_flank = [
            (sign * 0.025, 0.085, 1.635),
            (sign * 0.060, 0.170, 1.670),
            (sign * 0.080, 0.280, 1.580),
            (sign * 0.070, 0.360, 1.410)
        ]
        o = create_bezier_hair_strand(f"{prefix}_Ponytail_Tendril_{side}", pts_flank, 0.024, 0.003, mat, offset_x)
        objects.append(o)

    return objects

# 5. GENERADORES DE MODELOS

# --- VARIANTE 1: BASELINE CSG PRIMITIVES (El modelo de referencia anterior) ---
def build_variant_1_baseline(offset_x=-3.0):
    created = []
    # Cabeza Icosphere deformada
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.10)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.x *= 0.5
            v.co.y *= 0.6
        v.co.z *= 1.15
    mesh = bpy.data.meshes.new("V1_Head_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("V1_Head", mesh)
    obj.location = (offset_x, 0, 1.54)
    obj.data.materials.append(m_skin_flat)
    mesh.shade_smooth()
    col.objects.link(obj)
    created.append(obj)

    # Cabello Icosphere primitivo
    bm_h = bmesh.new()
    bmesh.ops.create_icosphere(bm_h, subdivisions=2, radius=0.11)
    mesh_h = bpy.data.meshes.new("V1_Hair_Mesh")
    bm_h.to_mesh(mesh_h)
    bm_h.free()
    obj_h = bpy.data.objects.new("V1_Hair", mesh_h)
    obj_h.location = (offset_x, 0.02, 1.56)
    obj_h.data.materials.append(m_hair_flat)
    mesh_h.shade_smooth()
    col.objects.link(obj_h)
    created.append(obj_h)

    # Torso cilindro
    bm_t = bmesh.new()
    bmesh.ops.create_cone(bm_t, cap_ends=True, segments=12, radius1=0.09, radius2=0.07, depth=0.35)
    mesh_t = bpy.data.meshes.new("V1_Torso_Mesh")
    bm_t.to_mesh(mesh_t)
    bm_t.free()
    obj_t = bpy.data.objects.new("V1_Torso", mesh_t)
    obj_t.location = (offset_x, 0, 1.25)
    obj_t.data.materials.append(m_suit_flat)
    mesh_t.shade_smooth()
    col.objects.link(obj_t)
    created.append(obj_t)

    # Piernas cilindros
    for side, sign in [("L", 1), ("R", -1)]:
        bm_l = bmesh.new()
        bmesh.ops.create_cone(bm_l, cap_ends=True, segments=8, radius1=0.045, radius2=0.035, depth=0.85)
        mesh_l = bpy.data.meshes.new(f"V1_Leg_{side}_Mesh")
        bm_l.to_mesh(mesh_l)
        bm_l.free()
        obj_l = bpy.data.objects.new(f"V1_Leg_{side}", mesh_l)
        obj_l.location = (offset_x + sign * 0.065, 0, 0.55)
        obj_l.data.materials.append(m_suit_flat)
        mesh_l.shade_smooth()
        col.objects.link(obj_l)
        created.append(obj_l)

    return created

# --- VARIANTE 2: SUBDIVISIÓN ORGÁNICA + CURVAS BÉZIER PARA CABELLO ---
def build_variant_2_organic_bezier(offset_x=-1.0):
    created = []
    # Cabeza Quad-dominant con Subsurf Catmull-Clark
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.105)
    for v in bm.verts:
        if v.co.y < 0:
            v.co.y *= 0.82
        if v.co.z < 0:
            t = abs(v.co.z / 0.105)
            v.co.x *= max(0.28, 1.0 - t * 0.68)
            if v.co.z < -0.05:
                v.co.y *= max(0.35, 1.0 - (t - 0.45) * 0.85)
                v.co.y -= 0.018 * t
        v.co.z *= 1.12
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("V2_Head_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    obj_head = bpy.data.objects.new("V2_Head", mesh)
    obj_head.location = (offset_x, 0, 1.54)
    obj_head.data.materials.append(m_skin_npr)
    mesh.shade_smooth()
    # Modificador Subsurf
    sub = obj_head.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    col.objects.link(obj_head)
    created.append(obj_head)

    # Ojos integrados suaves
    for side, sign in [("L", 1), ("R", -1)]:
        bm_eye = bmesh.new()
        bmesh.ops.create_circle(bm_eye, cap_ends=True, segments=16, radius=0.022)
        for v in bm_eye.verts:
            v.co.y *= 1.35
        mesh_e = bpy.data.meshes.new(f"V2_Eye_{side}_Mesh")
        bm_eye.to_mesh(mesh_e)
        bm_eye.free()
        obj_e = bpy.data.objects.new(f"V2_Eye_{side}", mesh_e)
        obj_e.location = (offset_x + sign * 0.038, -0.082, 1.542)
        obj_e.rotation_euler = (math.radians(90), 0, 0)
        obj_e.data.materials.append(m_eyes_npr)
        mesh_e.shade_smooth()
        col.objects.link(obj_e)
        created.append(obj_e)

    # Torso continuo con forma de reloj de arena anime
    bm_t = bmesh.new()
    bmesh.ops.create_uvsphere(bm_t, u_segments=20, v_segments=16, radius=0.12)
    for v in bm_t.verts:
        v.co.z *= 2.2
        v.co.y *= 0.65
        # Cintura estrecha en el centro
        t_waist = 1.0 - math.exp(-((v.co.z / 0.15)**2))
        v.co.x *= (0.70 + 0.30 * t_waist)
    bmesh.ops.recalc_face_normals(bm_t, faces=bm_t.faces)
    mesh_t = bpy.data.meshes.new("V2_Torso_Mesh")
    bm_t.to_mesh(mesh_t)
    bm_t.free()
    obj_torso = bpy.data.objects.new("V2_Torso", mesh_t)
    obj_torso.location = (offset_x, 0, 1.22)
    obj_torso.data.materials.append(m_suit_npr)
    mesh_t.shade_smooth()
    sub_t = obj_torso.modifiers.new("Subsurf", 'SUBSURF')
    sub_t.levels = 2
    col.objects.link(obj_torso)
    created.append(obj_torso)

    # Piernas continuas estilizadas
    for side, sign in [("L", 1), ("R", -1)]:
        bm_leg = bmesh.new()
        bmesh.ops.create_uvsphere(bm_leg, u_segments=16, v_segments=20, radius=0.065)
        for v in bm_leg.verts:
            v.co.z *= 6.8  # pierna larga 0.88m
            v.co.y *= 0.85
            # Rodilla más delgada
            if abs(v.co.z) < 0.08:
                v.co.x *= 0.75
                v.co.y *= 0.75
        bmesh.ops.recalc_face_normals(bm_leg, faces=bm_leg.faces)
        mesh_leg = bpy.data.meshes.new(f"V2_Leg_{side}_Mesh")
        bm_leg.to_mesh(mesh_leg)
        bm_leg.free()
        obj_leg = bpy.data.objects.new(f"V2_Leg_{side}", mesh_leg)
        obj_leg.location = (offset_x + sign * 0.068, 0, 0.50)
        obj_leg.data.materials.append(m_suit_npr)
        mesh_leg.shade_smooth()
        sub_l = obj_leg.modifiers.new("Subsurf", 'SUBSURF')
        sub_l.levels = 2
        col.objects.link(obj_leg)
        created.append(obj_leg)

    # Cabello con Curvas Bézier
    hair_objs = build_bezier_hair_set("V2_Hair", offset_x, m_hair_npr)
    created.extend(hair_objs)
    return created

# --- VARIANTE 3: INVERTED HULL SOLIDIFY OUTLINES (Línea de Tinta Anime) ---
def build_variant_3_inverted_hull(offset_x=1.0):
    created = build_variant_2_organic_bezier(offset_x=offset_x)
    # Aplicar Inverted Hull Solidify a todas las mallas
    for obj in created:
        if obj.type == 'MESH':
            apply_inverted_hull(obj, m_outline, thickness=0.0035)
    return created

# --- VARIANTE 4: SOLUCIÓN HÍBRIDA COMPLETA (Anime AAA) ---
def build_variant_4_hybrid_complete(offset_x=3.0):
    created = build_variant_3_inverted_hull(offset_x=offset_x)

    # 1. Bufanda Cibernética Ondeante (Curva Bézier extruida)
    scarf_curve = bpy.data.curves.new("V4_Scarf_Curve", type='CURVE')
    scarf_curve.dimensions = '3D'
    scarf_curve.resolution_u = 16
    scarf_curve.bevel_resolution = 2
    scarf_curve.bevel_depth = 0.012
    scarf_curve.extrude = 0.045

    spline_s = scarf_curve.splines.new('BEZIER')
    scarf_pts = [
        (offset_x + 0.00, -0.05, 1.45),
        (offset_x + 0.08, -0.03, 1.44),
        (offset_x + 0.06,  0.07, 1.45),
        (offset_x + 0.09,  0.18, 1.40),
        (offset_x + 0.14,  0.30, 1.34),
        (offset_x + 0.18,  0.42, 1.25),
    ]
    spline_s.bezier_points.add(len(scarf_pts) - 1)
    for i, pt in enumerate(scarf_pts):
        bp = spline_s.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj_scarf = bpy.data.objects.new("V4_Scarf", scarf_curve)
    obj_scarf.data.materials.append(m_scarf_npr)
    col.objects.link(obj_scarf)
    created.append(obj_scarf)

    # 2. Katana Cibernética en Cadera Izquierda
    bm_saya = bmesh.new()
    bmesh.ops.create_cone(bm_saya, cap_ends=True, segments=12, radius1=0.015, radius2=0.012, depth=0.78)
    for v in bm_saya.verts:
        v.co.x *= 0.45
        t = (v.co.z + 0.39) / 0.78
        v.co.y += (t**1.6) * 0.040
    bmesh.ops.recalc_face_normals(bm_saya, faces=bm_saya.faces)
    mesh_saya = bpy.data.meshes.new("V4_Katana_Saya_Mesh")
    bm_saya.to_mesh(mesh_saya)
    bm_saya.free()
    obj_saya = bpy.data.objects.new("V4_Katana_Saya", mesh_saya)
    obj_saya.location = (offset_x - 0.14, 0.03, 0.86)
    obj_saya.rotation_euler = (math.radians(25), math.radians(-15), math.radians(15))
    obj_saya.data.materials.append(m_suit_npr)
    mesh_saya.shade_smooth()
    apply_inverted_hull(obj_saya, m_outline, thickness=0.0025)
    col.objects.link(obj_saya)
    created.append(obj_saya)

    # Tsuba y Tsuka
    bm_tsuka = bmesh.new()
    bmesh.ops.create_cone(bm_tsuka, cap_ends=True, segments=10, radius1=0.013, radius2=0.011, depth=0.20)
    for v in bm_tsuka.verts:
        v.co.x *= 0.55
    mesh_tsuka = bpy.data.meshes.new("V4_Katana_Tsuka_Mesh")
    bm_tsuka.to_mesh(mesh_tsuka)
    bm_tsuka.free()
    obj_tsuka = bpy.data.objects.new("V4_Katana_Tsuka", mesh_tsuka)
    obj_tsuka.location = (offset_x - 0.175, -0.065, 1.29)
    obj_tsuka.rotation_euler = (math.radians(25), math.radians(-15), math.radians(15))
    obj_tsuka.data.materials.append(m_armor_npr)
    mesh_tsuka.shade_smooth()
    apply_inverted_hull(obj_tsuka, m_outline, thickness=0.0025)
    col.objects.link(obj_tsuka)
    created.append(obj_tsuka)

    # 3. Placas Pectorales Cerámicas Anime
    for side, sign in [("L", 1), ("R", -1)]:
        bm_p = bmesh.new()
        bmesh.ops.create_cone(bm_p, cap_ends=True, segments=8, radius1=0.055, radius2=0.025, depth=0.08)
        for v in bm_p.verts:
            v.co.y *= 0.40
        mesh_p = bpy.data.meshes.new(f"V4_ArmorPlate_{side}_Mesh")
        bm_p.to_mesh(mesh_p)
        bm_p.free()
        obj_p = bpy.data.objects.new(f"V4_ArmorPlate_{side}", mesh_p)
        obj_p.location = (offset_x + sign * 0.052, -0.075, 1.32)
        obj_p.rotation_euler = (math.radians(15), math.radians(sign * -12), 0)
        obj_p.data.materials.append(m_armor_npr)
        mesh_p.shade_smooth()
        apply_inverted_hull(obj_p, m_outline, thickness=0.0025)
        col.objects.link(obj_p)
        created.append(obj_p)

    # Núcleo Cian Brillante
    bm_c = bmesh.new()
    bmesh.ops.create_cone(bm_c, cap_ends=True, segments=16, radius1=0.016, radius2=0.016, depth=0.015)
    mesh_c = bpy.data.meshes.new("V4_Core_Mesh")
    bm_c.to_mesh(mesh_c)
    bm_c.free()
    obj_c = bpy.data.objects.new("V4_Core", mesh_c)
    obj_c.location = (offset_x, -0.082, 1.34)
    obj_c.rotation_euler = (math.radians(90), 0, 0)
    obj_c.data.materials.append(m_glow)
    col.objects.link(obj_c)
    created.append(obj_c)

    return created

# 6. INSTANCIACIÓN DE LAS 4 VARIANTES
print("Construyendo Variante 1: Baseline CSG...")
v1_objs = build_variant_1_baseline(offset_x=-3.0)

print("Construyendo Variante 2: Subsurf Orgánica + Bezier Hair...")
v2_objs = build_variant_2_organic_bezier(offset_x=-1.0)

print("Construyendo Variante 3: Inverted Hull Ink Outlines...")
v3_objs = build_variant_3_inverted_hull(offset_x=1.0)

print("Construyendo Variante 4: Hybrid Complete (Anime AAA)...")
v4_objs = build_variant_4_hybrid_complete(offset_x=3.0)

# 7. PEDESTAL CONTINUO Y CICLORAMA ESTUDIO
bm_floor = bmesh.new()
bmesh.ops.create_grid(bm_floor, x_segments=32, y_segments=16, size=12.0)
mesh_floor = bpy.data.meshes.new("Studio_Floor_Mesh")
bm_floor.to_mesh(mesh_floor)
bm_floor.free()
obj_floor = bpy.data.objects.new("Studio_Floor", mesh_floor)
obj_floor.location = (0, 0, 0)
m_floor = create_toon_mat("M_Floor", (0.10, 0.12, 0.16, 1.0), (0.05, 0.06, 0.08, 1.0))
obj_floor.data.materials.append(m_floor)
col.objects.link(obj_floor)

# Backdrop curvo
bm_bg = bmesh.new()
bmesh.ops.create_grid(bm_bg, x_segments=32, y_segments=16, size=14.0)
for v in bm_bg.verts:
    if v.co.y > 0:
        v.co.z += (v.co.y / 3.0)**2 * 3.5
    v.co.y += 2.8
bmesh.ops.recalc_face_normals(bm_bg, faces=bm_bg.faces)
mesh_bg = bpy.data.meshes.new("Studio_BG_Mesh")
bm_bg.to_mesh(mesh_bg)
bm_bg.free()
obj_bg = bpy.data.objects.new("Studio_BG", mesh_bg)
m_bg = create_toon_mat("M_Studio_BG", (0.16, 0.18, 0.24, 1.0), (0.10, 0.12, 0.16, 1.0))
obj_bg.data.materials.append(m_bg)
col.objects.link(obj_bg)

# 8. ILUMINACIÓN DE ESTUDIO UNIFORME
# Key light frontal amplia
l_key = bpy.data.objects.new("Key_Light", bpy.data.lights.new("Key_Light", 'AREA'))
l_key.data.energy = 85.0
l_key.data.size = 8.0
l_key.data.color = (1.0, 0.98, 0.96)
l_key.location = (0.0, -3.8, 2.8)
l_key.rotation_euler = (math.radians(50), 0, 0)
col.objects.link(l_key)

# Fill light superior suave
l_fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("Fill_Light", 'AREA'))
l_fill.data.energy = 45.0
l_fill.data.size = 10.0
l_fill.data.color = (0.80, 0.90, 1.0)
l_fill.location = (0.0, -1.0, 4.0)
l_fill.rotation_euler = (math.radians(20), 0, 0)
col.objects.link(l_fill)

# Rim light trasera
l_rim = bpy.data.objects.new("Rim_Light", bpy.data.lights.new("Rim_Light", 'AREA'))
l_rim.data.energy = 120.0
l_rim.data.size = 10.0
l_rim.data.color = (0.85, 0.85, 1.0)
l_rim.location = (0.0, 3.2, 2.5)
l_rim.rotation_euler = (math.radians(-65), 0, 0)
col.objects.link(l_rim)

# 9. RENDERIZADO DE LAS 5 CÁMARAS DEL BENCHMARK
output_dir = r"E:\Darx_Proyect\Saved\Anime_Benchmark_Workspace"
os.makedirs(output_dir, exist_ok=True)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'

cameras_benchmark = [
    # 1. Close-up 3/4 de la Variante 1 (Baseline CSG)
    ("Cam_01_Baseline", 65.0, (-2.7, -1.8, 1.55), (-3.0, 0.0, 1.45), "bench_01_baseline.png"),
    # 2. Close-up 3/4 de la Variante 2 (Subsurf + Bezier Hair)
    ("Cam_02_Organic_Hair", 65.0, (-0.7, -1.8, 1.55), (-1.0, 0.0, 1.45), "bench_02_organic_hair.png"),
    # 3. Close-up 3/4 de la Variante 3 (Inverted Hull Ink Outlines)
    ("Cam_03_Inverted_Hull", 65.0, (1.3, -1.8, 1.55), (1.0, 0.0, 1.45), "bench_03_inverted_hull.png"),
    # 4. Close-up 3/4 de la Variante 4 (Hybrid Final Anime AAA)
    ("Cam_04_Hybrid_Full", 65.0, (3.3, -1.8, 1.55), (3.0, 0.0, 1.45), "bench_04_hybrid_full.png"),
    # 5. Vista General Lineup de las 4 Variantes lado a lado
    ("Cam_05_Lineup_All4", 32.0, (0.0, -5.2, 1.35), (0.0, 0.0, 1.10), "bench_05_lineup_all4.png")
]

for name, lens, loc, target, filename in cameras_benchmark:
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

# 10. EXPORTACIÓN FBX DEL MODELO HÍBRIDO FINAL
fbx_hybrid_path = os.path.join(output_dir, "SK_Anime_Kira_Hybrid.fbx")
bpy.ops.object.select_all(action='DESELECT')
for o in v4_objs:
    if o.type == 'MESH':
        o.select_set(True)
if bpy.context.selected_objects:
    bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
    bpy.ops.export_scene.fbx(filepath=fbx_hybrid_path, use_selection=True, apply_scale_options='FBX_SCALE_UNITS')
    print(f"FBX Hibrido exportado: {fbx_hybrid_path}")

# Guardar escena .blend
blend_path = os.path.join(output_dir, "CH_Anime_Kira_Benchmark.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"Escena .blend guardada en: {blend_path}")
print("=" * 80)
print("BENCHMARK ANIME COMPLETADO EXITOSAMENTE")
print("=" * 80)
