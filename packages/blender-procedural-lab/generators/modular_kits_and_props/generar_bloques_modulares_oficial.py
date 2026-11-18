"""
Generador Oficial del Kit de Bloques Modulares "Rust-Bucket" (12 Piezas),
Mapeo UV PBR al Master Trim Sheet, Colisiones UCX y Escena Ensamblada de Muestra.
Astra Hazard: Rescue Squad - Unreal Engine 5.8
"""

import bpy
import bmesh
import math
import os
import numpy as np
from PIL import Image, ImageDraw
from mathutils import Matrix, Vector

def R(deg):
    return math.radians(deg)

# Directorios
BASE_DIR = r"f:\Dev\Game"
ART_DIR = os.path.join(BASE_DIR, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Environment")
TEX_DIR = os.path.join(ART_DIR, "Textures", "Environment")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# Limpiar objetos y mallas de la escena sin disparar handlers externos
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for mat in list(bpy.data.materials):
    bpy.data.materials.remove(mat)

main_col = bpy.context.scene.collection

# Bandas UV del Trim Sheet (U_min, V_min, U_max, V_max)
UV_HAZARD = (0.0, 0.00, 1.0, 0.18)
UV_STEEL = (0.0, 0.18, 1.0, 0.40)
UV_TEAL = (0.0, 0.40, 1.0, 0.62)
UV_GRATE = (0.0, 0.62, 1.0, 0.78)
UV_PIPES = (0.0, 0.78, 1.0, 0.90)
UV_EMIS_RED = (0.02, 0.91, 0.23, 0.99)
UV_EMIS_CYAN = (0.27, 0.91, 0.48, 0.99)
UV_EMIS_AMBER = (0.27, 0.90, 0.48, 0.95)
UV_EMIS_SCREEN = (0.52, 0.91, 0.73, 0.99)
UV_EMIS_STROBE = (0.77, 0.91, 0.98, 0.99)

def get_or_create_material():
    mat_name = "M_TrimSheet_Industrial"
    mat = bpy.data.materials.get(mat_name)
    if mat:
        return mat
    
    mat = bpy.data.materials.new(name=mat_name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output_node = nodes.new(type='ShaderNodeOutputMaterial')
    output_node.location = (600, 0)
    
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

    base_tex_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_BaseColor.png")
    orm_tex_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_ORM.png")
    norm_tex_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Normal.png")
    emis_tex_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Emissive.png")

    if os.path.exists(base_tex_path):
        img_base = bpy.data.images.load(base_tex_path)
        node_base = nodes.new(type='ShaderNodeTexImage')
        node_base.image = img_base
        node_base.location = (-400, 200)
        links.new(node_base.outputs['Color'], principled.inputs['Base Color'])

    if os.path.exists(orm_tex_path):
        img_orm = bpy.data.images.load(orm_tex_path)
        img_orm.colorspace_settings.name = 'Non-Color'
        node_orm = nodes.new(type='ShaderNodeTexImage')
        node_orm.image = img_orm
        node_orm.location = (-400, -100)

        sep_rgb = nodes.new(type='ShaderNodeSeparateColor')
        sep_rgb.location = (-100, -100)
        links.new(node_orm.outputs['Color'], sep_rgb.inputs['Color'])
        links.new(sep_rgb.outputs['Green'], principled.inputs['Roughness'])
        links.new(sep_rgb.outputs['Blue'], principled.inputs['Metallic'])

    if os.path.exists(norm_tex_path):
        img_norm = bpy.data.images.load(norm_tex_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        node_norm = nodes.new(type='ShaderNodeTexImage')
        node_norm.image = img_norm
        node_norm.location = (-400, -400)

        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.location = (-100, -400)
        norm_map.inputs['Strength'].default_value = 1.0
        links.new(node_norm.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], principled.inputs['Normal'])

    if os.path.exists(emis_tex_path):
        img_emis = bpy.data.images.load(emis_tex_path)
        node_emis = nodes.new(type='ShaderNodeTexImage')
        node_emis.image = img_emis
        node_emis.location = (-400, 500)
        links.new(node_emis.outputs['Color'], principled.inputs['Emission Color'])
        principled.inputs['Emission Strength'].default_value = 3.5

    return mat

master_mat = get_or_create_material()

def set_face_uv_band(bm, face, band_rect):
    uv_layer = bm.loops.layers.uv.verify()
    u_min, v_min, u_max, v_max = band_rect
    verts = [l.vert.co for l in face.loops]
    normal = face.normal
    nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)
    
    if nz >= nx and nz >= ny:
        coords = [(v.x, v.y) for v in verts]
    elif nx >= ny and nx >= nz:
        coords = [(v.y, v.z) for v in verts]
    else:
        coords = [(v.x, v.z) for v in verts]
        
    c_min_u = min(c[0] for c in coords)
    c_max_u = max(c[0] for c in coords)
    c_min_v = min(c[1] for c in coords)
    c_max_v = max(c[1] for c in coords)
    
    du = max(0.0001, c_max_u - c_min_u)
    dv = max(0.0001, c_max_v - c_min_v)
    
    for i, loop in enumerate(face.loops):
        u_norm = (coords[i][0] - c_min_u) / du
        v_norm = (coords[i][1] - c_min_v) / dv
        loop[uv_layer].uv = (
            u_min + u_norm * (u_max - u_min),
            v_min + v_norm * (v_max - v_min)
        )

def create_box(bm, size=(1, 1, 1), loc=(0, 0, 0), uv_band=UV_STEEL, uv_top=None, uv_front=None):
    faces_before = set(bm.faces)
    mat = Matrix.Translation(loc)
    ret = bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    sx, sy, sz = size
    lx, ly, lz = loc
    for v in ret['verts']:
        v.co.x = (v.co.x - lx) * sx + lx
        v.co.y = (v.co.y - ly) * sy + ly
        v.co.z = (v.co.z - lz) * sz + lz
        
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_faces = set(bm.faces) - faces_before
    for f in new_faces:
        if uv_top and f.normal.z > 0.5:
            set_face_uv_band(bm, f, uv_top)
        elif uv_front and f.normal.y < -0.5:
            set_face_uv_band(bm, f, uv_front)
        else:
            set_face_uv_band(bm, f, uv_band)
    return new_faces

def create_cylinder(bm, radius=0.1, depth=1.0, loc=(0, 0, 0), rot_axis='Z', uv_band=UV_PIPES):
    faces_before = set(bm.faces)
    mat = Matrix.Translation(loc)
    if rot_axis == 'X':
        mat = mat @ Matrix.Rotation(R(90), 4, 'Y')
    elif rot_axis == 'Y':
        mat = mat @ Matrix.Rotation(R(90), 4, 'X')
    bmesh.ops.create_cone(bm, cap_ends=True, radius1=radius, radius2=radius, depth=depth, matrix=mat)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    new_faces = set(bm.faces) - faces_before
    for f in new_faces:
        set_face_uv_band(bm, f, uv_band)
    return new_faces

# ==============================================================================
# CONSTRUCTORES DE LOS 12 BLOQUES MODULARES
# ==============================================================================

def build_floor_metalgrid():
    name = "SM_Floor_MetalGrid_400x400"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 4.0, 0.15), (0, 0, 0.075), uv_band=UV_STEEL, uv_top=UV_HAZARD)
    for qx in [-1.0, 1.0]:
        for qy in [-1.0, 1.0]:
            create_box(bm, (1.6, 1.6, 0.02), (qx, qy, 0.155), uv_band=UV_STEEL, uv_top=UV_GRATE)
    create_box(bm, (4.0, 0.3, 0.02), (0, 0, 0.16), uv_band=UV_STEEL)
    create_box(bm, (0.3, 4.0, 0.02), (0, 0, 0.16), uv_band=UV_STEEL)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 4.0, 0.15), (0, 0, 0.075))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_floor_plate():
    name = "SM_Floor_Plate_400x400"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 4.0, 0.15), (0, 0, 0.075), uv_band=UV_STEEL)
    create_box(bm, (4.0, 0.3, 0.015), (0, 1.85, 0.155), uv_band=UV_HAZARD)
    create_box(bm, (4.0, 0.3, 0.015), (0, -1.85, 0.155), uv_band=UV_HAZARD)
    create_box(bm, (0.3, 3.4, 0.015), (1.85, 0, 0.155), uv_band=UV_HAZARD)
    create_box(bm, (0.3, 3.4, 0.015), (-1.85, 0, 0.155), uv_band=UV_HAZARD)
    for px in [-0.95, 0.95]:
        for py in [-0.95, 0.95]:
            create_box(bm, (1.65, 1.65, 0.02), (px, py, 0.16), uv_band=UV_STEEL)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 4.0, 0.15), (0, 0, 0.075))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_ceiling_girder():
    name = "SM_Ceiling_Girder_400x400"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 4.0, 0.10), (0, 0, 0.35), uv_band=UV_STEEL)
    for gy in [-1.2, 1.2]:
        create_box(bm, (4.0, 0.35, 0.06), (0, gy, 0.28), uv_band=UV_STEEL)
        create_box(bm, (4.0, 0.10, 0.22), (0, gy, 0.15), uv_band=UV_STEEL)
        create_box(bm, (4.0, 0.35, 0.06), (0, gy, 0.03), uv_band=UV_STEEL)
    create_box(bm, (1.2, 0.6, 0.15), (0, 0, 0.25), uv_band=UV_STEEL)
    create_box(bm, (1.0, 0.4, 0.02), (0, 0, 0.165), uv_band=UV_EMIS_CYAN)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 4.0, 0.40), (0, 0, 0.20))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_wall_standard():
    name = "SM_Wall_Standard_400x350"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 0.30, 3.50), (0, 0, 1.75), uv_band=UV_STEEL)
    for px in [-1.0, 1.0]:
        create_box(bm, (1.75, 0.04, 2.60), (px, -0.16, 1.85), uv_band=UV_STEEL, uv_front=UV_TEAL)
    create_box(bm, (4.0, 0.05, 0.50), (0, -0.165, 0.25), uv_band=UV_STEEL, uv_front=UV_HAZARD)
    create_box(bm, (4.0, 0.08, 0.20), (0, -0.17, 3.30), uv_band=UV_PIPES)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 0.35, 3.50), (0, 0, 1.75))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_wall_pipes():
    name = "SM_Wall_Pipes_400x350"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 0.30, 3.50), (0, 0, 1.75), uv_band=UV_STEEL)
    for px in [-1.0, 1.0]:
        create_box(bm, (1.75, 0.04, 2.60), (px, -0.16, 1.85), uv_band=UV_STEEL, uv_front=UV_TEAL)
    create_cylinder(bm, radius=0.09, depth=4.0, loc=(0, -0.28, 2.60), rot_axis='X', uv_band=UV_PIPES)
    for bx in [-1.5, 0, 1.5]:
        create_box(bm, (0.12, 0.20, 0.24), (bx, -0.22, 2.60), uv_band=UV_STEEL)
    create_cylinder(bm, radius=0.12, depth=4.0, loc=(0, -0.32, 1.80), rot_axis='X', uv_band=UV_PIPES)
    create_box(bm, (4.0, 0.15, 0.16), (0, -0.25, 0.90), uv_band=UV_HAZARD)
    create_box(bm, (0.40, 0.15, 0.35), (0, -0.30, 0.90), uv_band=UV_STEEL, uv_front=UV_EMIS_CYAN)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 0.55, 3.50), (0, -0.10, 1.75))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_wall_doorway():
    name = "SM_Wall_Doorway_400x350"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (1.0, 0.35, 3.50), (-1.5, 0, 1.75), uv_band=UV_STEEL)
    create_box(bm, (1.0, 0.35, 3.50), (1.5, 0, 1.75), uv_band=UV_STEEL)
    create_box(bm, (2.0, 0.35, 0.90), (0, 0, 3.05), uv_band=UV_STEEL)
    create_box(bm, (0.16, 0.04, 2.60), (-1.08, -0.19, 1.30), uv_band=UV_HAZARD)
    create_box(bm, (0.16, 0.04, 2.60), (1.08, -0.19, 1.30), uv_band=UV_HAZARD)
    create_box(bm, (2.20, 0.04, 0.16), (0, -0.19, 2.68), uv_band=UV_HAZARD)
    create_box(bm, (0.90, 0.08, 0.25), (0, -0.20, 2.95), uv_band=UV_STEEL, uv_front=UV_EMIS_CYAN)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (1.0, 0.40, 3.50), (-1.5, 0, 1.75))
    create_box(bm_ucx, (1.0, 0.40, 3.50), (1.5, 0, 1.75))
    create_box(bm_ucx, (2.0, 0.40, 0.90), (0, 0, 3.05))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_airlock_doors():
    def build_leaf(side_sign, obj_name):
        mesh = bpy.data.meshes.new(obj_name)
        bm = bmesh.new()
        cx = side_sign * 0.475
        create_box(bm, (1.05, 0.14, 2.55), (cx, 0, 1.28), uv_band=UV_TEAL)
        edge_x = side_sign * 0.02
        create_box(bm, (0.12, 0.03, 2.50), (edge_x, -0.075, 1.28), uv_band=UV_HAZARD)
        create_box(bm, (0.35, 0.04, 0.45), (cx, -0.075, 1.70), uv_band=UV_STEEL, uv_front=UV_EMIS_CYAN)
        create_box(bm, (0.40, 0.08, 0.12), (cx, -0.10, 1.00), uv_band=UV_STEEL)
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(obj_name, mesh)
        obj.data.materials.append(master_mat)
        main_col.objects.link(obj)
        
        ucx_mesh = bpy.data.meshes.new(f"UCX_{obj_name}")
        bm_ucx = bmesh.new()
        create_box(bm_ucx, (1.05, 0.16, 2.55), (cx, 0, 1.28))
        bm_ucx.to_mesh(ucx_mesh)
        bm_ucx.free()
        ucx_obj = bpy.data.objects.new(f"UCX_{obj_name}_01", ucx_mesh)
        main_col.objects.link(ucx_obj)
        return obj, ucx_obj

    dl, ucx_dl = build_leaf(-1, "SM_Door_Airlock_Slide_Left")
    dr, ucx_dr = build_leaf(1, "SM_Door_Airlock_Slide_Right")
    return dl, ucx_dl, dr, ucx_dr

def build_corner_column():
    name = "SM_Wall_Corner_Column_50x350"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (0.50, 0.50, 3.50), (0.25, 0.25, 1.75), uv_band=UV_STEEL)
    create_box(bm, (0.02, 0.40, 3.30), (-0.01, 0.25, 1.75), uv_band=UV_HAZARD)
    create_box(bm, (0.40, 0.02, 3.30), (0.25, -0.01, 1.75), uv_band=UV_HAZARD)
    create_box(bm, (0.60, 0.60, 0.25), (0.25, 0.25, 0.125), uv_band=UV_STEEL)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (0.50, 0.50, 3.50), (0.25, 0.25, 1.75))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_vent_straight():
    name = "SM_VentDuct_Straight_100x100"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (2.0, 1.0, 0.08), (0, 0, 0.04), uv_band=UV_STEEL)
    create_box(bm, (2.0, 1.0, 0.08), (0, 0, 0.96), uv_band=UV_STEEL)
    create_box(bm, (2.0, 0.08, 0.84), (0, -0.46, 0.50), uv_band=UV_STEEL)
    create_box(bm, (2.0, 0.08, 0.84), (0, 0.46, 0.50), uv_band=UV_STEEL)
    for bx in [-0.95, 0.95]:
        create_box(bm, (0.08, 1.10, 1.10), (bx, 0, 0.50), uv_band=UV_HAZARD)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (2.0, 1.0, 0.08), (0, 0, 0.04))
    create_box(bm_ucx, (2.0, 1.0, 0.08), (0, 0, 0.96))
    create_box(bm_ucx, (2.0, 0.08, 0.84), (0, -0.46, 0.50))
    create_box(bm_ucx, (2.0, 0.08, 0.84), (0, 0.46, 0.50))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_vent_corner():
    name = "SM_VentDuct_Corner_100x100"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (1.0, 1.0, 0.08), (0.5, 0.5, 0.04), uv_band=UV_STEEL)
    create_box(bm, (1.0, 1.0, 0.08), (0.5, 0.5, 0.96), uv_band=UV_STEEL)
    create_box(bm, (0.08, 1.0, 0.84), (0.96, 0.5, 0.50), uv_band=UV_STEEL)
    create_box(bm, (1.0, 0.08, 0.84), (0.5, 0.96, 0.50), uv_band=UV_STEEL)
    create_box(bm, (0.08, 1.08, 1.08), (0.04, 0.5, 0.50), uv_band=UV_HAZARD)
    create_box(bm, (1.08, 0.08, 1.08), (0.5, 0.04, 0.50), uv_band=UV_HAZARD)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (1.0, 1.0, 0.08), (0.5, 0.5, 0.04))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_beam_chaos():
    name = "SM_Beam_Structural_Chaos_400"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_box(bm, (4.0, 0.35, 0.05), (0, 0, 0.15), uv_band=UV_STEEL)
    create_box(bm, (4.0, 0.08, 0.25), (0, 0, 0), uv_band=UV_STEEL)
    create_box(bm, (4.0, 0.35, 0.05), (0, 0, -0.15), uv_band=UV_STEEL)
    create_box(bm, (0.10, 0.45, 0.45), (-1.95, 0, 0), uv_band=UV_HAZARD)
    create_box(bm, (0.10, 0.45, 0.45), (1.95, 0, 0), uv_band=UV_HAZARD)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (4.0, 0.35, 0.35), (0, 0, 0))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

def build_pipe_hazard():
    name = "SM_Pipe_Hazard_Leak_300"
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    create_cylinder(bm, radius=0.12, depth=3.0, loc=(0, 0, 0), rot_axis='X', uv_band=UV_PIPES)
    create_cylinder(bm, radius=0.16, depth=0.45, loc=(0, 0, 0), rot_axis='X', uv_band=UV_HAZARD)
    create_cylinder(bm, radius=0.18, depth=0.10, loc=(-1.45, 0, 0), rot_axis='X', uv_band=UV_STEEL)
    create_cylinder(bm, radius=0.18, depth=0.10, loc=(1.45, 0, 0), rot_axis='X', uv_band=UV_STEEL)
    create_cylinder(bm, radius=0.03, depth=0.16, loc=(0, 0, 0.20), rot_axis='Z', uv_band=UV_STEEL)
    create_cylinder(bm, radius=0.14, depth=0.04, loc=(0, 0, 0.28), rot_axis='Z', uv_band=UV_EMIS_RED)
    create_cylinder(bm, radius=0.04, depth=0.15, loc=(0, -0.15, -0.10), rot_axis='Y', uv_band=UV_HAZARD)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(master_mat)
    main_col.objects.link(obj)
    
    ucx_mesh = bpy.data.meshes.new(f"UCX_{name}")
    bm_ucx = bmesh.new()
    create_box(bm_ucx, (3.0, 0.35, 0.40), (0, 0, 0))
    bm_ucx.to_mesh(ucx_mesh)
    bm_ucx.free()
    ucx_obj = bpy.data.objects.new(f"UCX_{name}_01", ucx_mesh)
    main_col.objects.link(ucx_obj)
    return obj, ucx_obj

# ==============================================================================
# EXPORTACIÓN FBX
# ==============================================================================
print("Creando los 12 bloques modulares...")
all_blocks = []

def export_asset_fbx(obj, ucx_obj, asset_name):
    fbx_file = os.path.join(FBX_DIR, f"{asset_name}.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    if ucx_obj:
        ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_file,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f" [FBX OK] {asset_name} -> {fbx_file}")
    all_blocks.append((obj, ucx_obj, asset_name))

f_grid, ucx_f_grid = build_floor_metalgrid()
export_asset_fbx(f_grid, ucx_f_grid, "SM_Floor_MetalGrid_400x400")

f_plate, ucx_f_plate = build_floor_plate()
export_asset_fbx(f_plate, ucx_f_plate, "SM_Floor_Plate_400x400")

c_girder, ucx_c_girder = build_ceiling_girder()
export_asset_fbx(c_girder, ucx_c_girder, "SM_Ceiling_Girder_400x400")

w_std, ucx_w_std = build_wall_standard()
export_asset_fbx(w_std, ucx_w_std, "SM_Wall_Standard_400x350")

w_pipes, ucx_w_pipes = build_wall_pipes()
export_asset_fbx(w_pipes, ucx_w_pipes, "SM_Wall_Pipes_400x350")

w_door, ucx_w_door = build_wall_doorway()
export_asset_fbx(w_door, ucx_w_door, "SM_Wall_Doorway_400x350")

d_left, ucx_d_l, d_right, ucx_d_r = build_airlock_doors()
export_asset_fbx(d_left, ucx_d_l, "SM_Door_Airlock_Slide_Left")
export_asset_fbx(d_right, ucx_d_r, "SM_Door_Airlock_Slide_Right")

col, ucx_col = build_corner_column()
export_asset_fbx(col, ucx_col, "SM_Wall_Corner_Column_50x350")

v_str, ucx_v_str = build_vent_straight()
export_asset_fbx(v_str, ucx_v_str, "SM_VentDuct_Straight_100x100")

v_crn, ucx_v_crn = build_vent_corner()
export_asset_fbx(v_crn, ucx_v_crn, "SM_VentDuct_Corner_100x100")

b_chaos, ucx_b_chaos = build_beam_chaos()
export_asset_fbx(b_chaos, ucx_b_chaos, "SM_Beam_Structural_Chaos_400")

p_leak, ucx_p_leak = build_pipe_hazard()
export_asset_fbx(p_leak, ucx_p_leak, "SM_Pipe_Hazard_Leak_300")


# Ocultar colisiones UCX en renders
for _, ucx, _ in all_blocks:
    if ucx:
        ucx.hide_render = True
        ucx.hide_viewport = True

# Reubicar los 12 originales en la Galería de Exhibición Técnica (para vista Kit_Exhibition)
exhibition_col = bpy.data.collections.new("Exhibition_Catalog")
bpy.context.scene.collection.children.link(exhibition_col)

for i, (obj, _, name) in enumerate(all_blocks):
    obj.hide_render = False
    obj.hide_viewport = False
    row = 0 if i < 6 else 1
    col_idx = i % 6
    x = (col_idx - 2.5) * 3.0
    y = -10.0 if row == 0 else -14.0
    obj.location = (x, y, 0)
    obj.rotation_euler = (0, 0, 0)

# ==============================================================================
# CONSTRUCCIÓN DE LA SALA DE MUESTRA (8x8 metros)
# ==============================================================================
print("Ensamblando la sala conectada de 8x8 metros...")

showcase_col = bpy.data.collections.new("Showcase_Room")
bpy.context.scene.collection.children.link(showcase_col)

def duplicate_to_scene(orig_obj, location, rotation=(0, 0, 0)):
    new_obj = orig_obj.copy()
    new_obj.data = orig_obj.data
    new_obj.location = location
    new_obj.rotation_euler = rotation
    new_obj.hide_render = False
    new_obj.hide_viewport = False
    showcase_col.objects.link(new_obj)
    return new_obj

# Suelos (8x8m)
s1 = duplicate_to_scene(f_plate, (-2.0, -2.0, 0))
s2 = duplicate_to_scene(f_grid, (2.0, -2.0, 0))
s3 = duplicate_to_scene(f_grid, (-2.0, 2.0, 0))
s4 = duplicate_to_scene(f_plate, (2.0, 2.0, 0))

# Techos (Z = 3.5m)
ceiling_tiles = [
    duplicate_to_scene(c_girder, (-2.0, -2.0, 3.5)),
    duplicate_to_scene(c_girder, (2.0, -2.0, 3.5)),
    duplicate_to_scene(c_girder, (-2.0, 2.0, 3.5)),
    duplicate_to_scene(c_girder, (2.0, 2.0, 3.5))
]

# Paredes de fondo (Y = +4.0m)
pw_door = duplicate_to_scene(w_door, (-2.0, 4.0, 0))
pd_left = duplicate_to_scene(d_left, (-2.0, 4.0, 0))
pd_right = duplicate_to_scene(d_right, (-2.0, 4.0, 0))
pw_pipes = duplicate_to_scene(w_pipes, (2.0, 4.0, 0))

# Paredes laterales
pw_l1 = duplicate_to_scene(w_std, (-4.0, -2.0, 0), (0, 0, R(90)))
pw_l2 = duplicate_to_scene(w_std, (-4.0, 2.0, 0), (0, 0, R(90)))
pw_r1 = duplicate_to_scene(w_std, (4.0, -2.0, 0), (0, 0, R(-90)))
pw_r2 = duplicate_to_scene(w_pipes, (4.0, 2.0, 0), (0, 0, R(-90)))

# Columnas de esquina
duplicate_to_scene(col, (-4.0, 4.0, 0))
duplicate_to_scene(col, (4.0, 4.0, 0), (0, 0, R(90)))
duplicate_to_scene(col, (-4.0, -4.0, 0), (0, 0, R(-90)))
duplicate_to_scene(col, (4.0, -4.0, 0), (0, 0, R(180)))

# Conducto de ventilación suspendido
duplicate_to_scene(v_str, (-2.0, 3.4, 2.4))
duplicate_to_scene(v_str, (0.0, 3.4, 2.4))
duplicate_to_scene(v_crn, (1.5, 3.4, 2.4))

# Viga colapsada Chaos
duplicate_to_scene(b_chaos, (1.2, 0.5, 0.2), (R(5), R(12), R(35)))

# Tubería de fuga de vapor
duplicate_to_scene(p_leak, (3.7, 1.2, 1.5), (0, 0, R(90)))


# ==============================================================================
# IMPORTACIÓN Y PINTURA DE PERSONAJES Y EQUIPO
# ==============================================================================
print("Importando y aplicando paleta a personajes y equipo...")
char_fbx = os.path.join(ART_DIR, "FBX", "Characters", "SK_Firefighter_Official_Rigged.fbx")
dummy_fbx = os.path.join(ART_DIR, "FBX", "Characters", "SK_TestDummy_Ragdoll.fbx")
stretcher_fbx = os.path.join(ART_DIR, "FBX", "Equipment", "SM_TandemStretcher.fbx")

# Colores para el bombero espacial
def setup_firefighter_materials():
    colors = {
        'M_Suit_Orange': (0.85, 0.45, 0.12, 1.0),
        'M_Suit_DarkOrange': (0.65, 0.32, 0.08, 1.0),
        'M_Armor_Sage': (0.28, 0.50, 0.25, 1.0),
        'M_Helmet_Grey': (0.35, 0.38, 0.40, 1.0),
        'M_Visor_Tinted': (0.08, 0.12, 0.18, 1.0),
        'M_Stripe_Yellow': (0.95, 0.85, 0.15, 1.0),
        'M_Hose_Red': (0.85, 0.10, 0.08, 1.0),
        'M_Harness_Dark': (0.10, 0.10, 0.12, 1.0),
        'M_LED_Green': (0.15, 1.0, 0.20, 1.0),
        'M_LED_Red': (1.0, 0.08, 0.08, 1.0),
        'M_Weapon_Blue': (0.25, 0.42, 0.55, 1.0),
        'M_Weapon_Stock': (0.55, 0.25, 0.12, 1.0),
        'M_Weapon_Yellow': (0.95, 0.85, 0.15, 1.0),
        'M_Metal_Dark': (0.15, 0.16, 0.18, 1.0),
        'M_Outline_Black': (0.01, 0.01, 0.01, 1.0)
    }
    for mat_name, col in colors.items():
        mat = bpy.data.materials.get(mat_name)
        if mat:
            mat.use_nodes = True
            nt = mat.node_tree
            bsdf = nt.nodes.get('Principled BSDF')
            if bsdf:
                bsdf.inputs['Base Color'].default_value = col
                if 'LED' in mat_name or 'Yellow' in mat_name:
                    bsdf.inputs['Emission Color'].default_value = col
                    bsdf.inputs['Emission Strength'].default_value = 2.0

if os.path.exists(char_fbx):
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=char_fbx)
    new_objs = set(bpy.data.objects) - before_objs
    for o in new_objs:
        if o.parent is None:
            o.location = (-1.2, 1.2, 0.0)
            o.rotation_euler = (0, 0, R(-40))
        showcase_col.objects.link(o)
    setup_firefighter_materials()

if os.path.exists(stretcher_fbx):
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=stretcher_fbx)
    new_objs = set(bpy.data.objects) - before_objs
    for o in new_objs:
        if o.parent is None:
            o.location = (-0.5, -0.6, 0.15)
            o.rotation_euler = (0, 0, R(30))
        showcase_col.objects.link(o)

if os.path.exists(dummy_fbx):
    before_objs = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=dummy_fbx)
    new_objs = set(bpy.data.objects) - before_objs
    for o in new_objs:
        if o.parent is None:
            o.location = (-0.5, -0.6, 0.40)
            o.rotation_euler = (R(80), 0, R(30))
        showcase_col.objects.link(o)


# ==============================================================================
# ILUMINACIÓN DINÁMICA DE EMERGENCIA
# ==============================================================================
print("Configurando iluminación dinámica...")

# Baliza de Alarma Roja
l_alarm = bpy.data.lights.new("AlarmLight_Red", type='POINT')
l_alarm.energy = 1400.0
l_alarm.color = (1.0, 0.06, 0.06)
obj_alarm = bpy.data.objects.new("AlarmLight_Red", l_alarm)
obj_alarm.location = (-2.0, 3.8, 3.2)
showcase_col.objects.link(obj_alarm)

# Luz de Esclusa Cyan
l_cyan = bpy.data.lights.new("Airlock_CyanLight", type='SPOT')
l_cyan.energy = 1000.0
l_cyan.color = (0.05, 0.95, 1.0)
l_cyan.spot_size = R(85)
l_cyan.spot_blend = 0.5
obj_cyan = bpy.data.objects.new("Airlock_CyanLight", l_cyan)
obj_cyan.location = (-2.0, 3.7, 3.1)
obj_cyan.rotation_euler = (R(-60), 0, 0)
showcase_col.objects.link(obj_cyan)

# Luces de Trabajo Ámbar
for lx, ly in [(-2.0, -2.0), (2.0, 2.0)]:
    l_work = bpy.data.lights.new(f"WorkLight_{lx}_{ly}", type='POINT')
    l_work.energy = 650.0
    l_work.color = (1.0, 0.88, 0.70)
    obj_work = bpy.data.objects.new(f"WorkLight_{lx}_{ly}", l_work)
    obj_work.location = (lx, ly, 3.2)
    showcase_col.objects.link(obj_work)

# Foco de Vapor
l_steam = bpy.data.lights.new("SteamHazeLight", type='POINT')
l_steam.energy = 500.0
l_steam.color = (0.75, 0.88, 1.0)
obj_steam = bpy.data.objects.new("SteamHazeLight", l_steam)
obj_steam.location = (3.5, 1.2, 1.6)
showcase_col.objects.link(obj_steam)

# Luz para el Catálogo de Exhibición
l_cat = bpy.data.lights.new("Catalog_Sun", type='SUN')
l_cat.energy = 4.0
l_cat.color = (0.95, 0.98, 1.0)
obj_cat = bpy.data.objects.new("Catalog_Sun", l_cat)
obj_cat.rotation_euler = (R(45), R(20), R(-30))
exhibition_col.objects.link(obj_cat)

world = bpy.data.worlds.new("EmergencySpaceWorld")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.03, 0.035, 0.045, 1.0)
    bg.inputs['Strength'].default_value = 0.4
bpy.context.scene.world = world

scene = bpy.context.scene
scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True

scene.render.resolution_x = 1280
scene.render.resolution_y = 960

cam_data = bpy.data.cameras.new("ShowcaseCam")
cam_data.lens = 30.0
cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
main_col.objects.link(cam_obj)
scene.camera = cam_obj

# Definición de las 4 vistas cinemáticas
views = {
    # 1. Isométrica general: diorama con techo oculto para ver el interior
    "Isometric_Gym": {
        "loc": (6.5, -6.5, 5.5),
        "rot": (R(60), 0, R(45)),
        "hide_ceiling": True,
        "label": "RUST-BUCKET GYM: VISTA ISOMETRICA MODULAR (8x8m)"
    },
    # 2. Acción en la Esclusa: con bombero y camilla
    "Airlock_Action": {
        "loc": (-0.5, -0.8, 1.6),
        "rot": (R(78), 0, R(-18)),
        "hide_ceiling": False,
        "label": "ESCLUSA PRINCIPAL: ACCION CO-OP Y RESCATE EN CAMILLA"
    },
    # 3. Pasillo Técnico: tuberías, viga Chaos y fuga de vapor
    "Maintenance_Corridor": {
        "loc": (1.6, -2.2, 1.4),
        "rot": (R(75), 0, R(12)),
        "hide_ceiling": False,
        "label": "PASILLO TECNICO: TUBERIAS, VIGA CHAOS Y DUCTO DE VENTILACION"
    },
    # 4. Catálogo Técnico: los 12 bloques alineados
    "Kit_Exhibition": {
        "loc": (0.0, -18.0, 7.5),
        "rot": (R(55), 0, 0),
        "hide_ceiling": False,
        "label": "CATALOGO TECNICO: 12 BLOQUES MODULARES CON MASTER TRIM SHEET PBR"
    }
}

rendered_images = []

for view_name, info in views.items():
    cam_obj.location = info["loc"]
    cam_obj.rotation_euler = info["rot"]
    
    # Manejar visibilidad del techo según la toma
    for c_tile in ceiling_tiles:
        c_tile.hide_render = info["hide_ceiling"]
        
    # En Kit_Exhibition, enfocamos los bloques de muestra
    if view_name == "Kit_Exhibition":
        cam_data.lens = 28.0
    else:
        cam_data.lens = 32.0
    
    out_path = os.path.join(RENDERS_DIR, f"Showcase_RustBucket_{view_name}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    rendered_images.append((out_path, info["label"]))
    print(f" [RENDER OK] {view_name} -> {out_path}")

blend_file = os.path.join(ART_DIR, "Blender", "RustBucket_Modular_Showcase.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_file)
print(f" [BLEND OK] Guardado archivo maestro Blender: {blend_file}")

# Collage
print("Creando collage 2x2...")
collage = Image.new("RGB", (2560, 1920), (14, 16, 20))
positions = [(0, 0), (1280, 0), (0, 960), (1280, 960)]

for i, (img_path, label) in enumerate(rendered_images):
    img = Image.open(img_path)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(25, 25), (840, 75)], fill=(12, 15, 22, 230), outline=(255, 170, 30), width=2)
    draw.text((40, 42), label, fill=(255, 200, 50))
    collage.paste(img, positions[i])

collage_path = os.path.join(RENDERS_DIR, "Showcase_RustBucket_ModularGym_4views.png")
collage.save(collage_path, quality=95)

brain_path = os.path.join(BRAIN_DIR, "Showcase_RustBucket_ModularGym_4views.png")
collage.save(brain_path, quality=95)

print(f" [COLLAGE OK] Guardado en: {collage_path} y {brain_path}")

# Generar además el overview 2x2 del Master Trim Sheet PBR (2048x2048)
print("Generando imagen de validación del Master Trim Sheet PBR...")
trim_collage = Image.new("RGB", (2048, 2048), (20, 20, 24))
base_im = Image.open(os.path.join(TEX_DIR, "T_TrimSheet_Industrial_BaseColor.png")).resize((1024, 1024))
orm_im = Image.open(os.path.join(TEX_DIR, "T_TrimSheet_Industrial_ORM.png")).resize((1024, 1024))
norm_im = Image.open(os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Normal.png")).resize((1024, 1024))
emis_im = Image.open(os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Emissive.png")).resize((1024, 1024))

trim_collage.paste(base_im, (0, 0))
trim_collage.paste(orm_im, (1024, 0))
trim_collage.paste(norm_im, (0, 1024))
trim_collage.paste(emis_im, (1024, 1024))

draw_tc = ImageDraw.Draw(trim_collage)
# Labels
draw_tc.rectangle([(20, 20), (450, 60)], fill=(10, 12, 16, 230), outline=(255, 180, 40), width=2)
draw_tc.text((30, 32), "1. BASE COLOR (ALBEDO sRGB)", fill=(255, 200, 50))

draw_tc.rectangle([(1044, 20), (1530, 60)], fill=(10, 12, 16, 230), outline=(255, 180, 40), width=2)
draw_tc.text((1054, 32), "2. PACKED ORM (R:AO, G:Rough, B:Metal)", fill=(255, 200, 50))

draw_tc.rectangle([(20, 1044), (490, 1084)], fill=(10, 12, 16, 230), outline=(255, 180, 40), width=2)
draw_tc.text((30, 1056), "3. NORMAL MAP (TANGENT OpenGL/UE)", fill=(255, 200, 50))

draw_tc.rectangle([(1044, 1044), (1500, 1084)], fill=(10, 12, 16, 230), outline=(255, 180, 40), width=2)
draw_tc.text((1054, 1056), "4. EMISSIVE GLOW (EMERGENCIA)", fill=(255, 200, 50))

trim_dest = os.path.join(RENDERS_DIR, "TrimSheet_Industrial_PBR_Overview.png")
trim_collage.save(trim_dest, quality=95)
trim_brain = os.path.join(BRAIN_DIR, "TrimSheet_Industrial_PBR_Overview.png")
trim_collage.save(trim_brain, quality=95)

print(f" [TRIM OVERVIEW OK] Guardado en: {trim_dest} y {trim_brain}")
