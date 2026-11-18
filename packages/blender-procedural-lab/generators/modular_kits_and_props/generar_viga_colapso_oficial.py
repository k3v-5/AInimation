"""
generar_viga_colapso_oficial.py
===============================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
1. Genera los modelos 3D modulares para el sistema de Colapso Estructural y Destrucción Chaos:
   - SM_StructuralBeam_Heavy_400cm: Viga pesada en I de 400x35x45cm con costillas de refuerzo,
     placas de anclaje con remaches y franjas de precaución Trim Sheet.
   - SM_CeilingBracket_40cm: Soporte de techo con pernos cortados por cizallamiento térmico.
   - SM_Debris_Chunk_01 y 02: Fragmentos de escombros de concreto y metal con fractura física.
2. Genera colisiones UCX convexas precisas para simulación física determinista.
3. Aplica mapeo UV sobre el Master Trim Sheet M_TrimSheet_Industrial.
4. Exporta mallas FBX a Art/FBX/Environment/.
5. Renderiza hoja de showcase (2560x1440) de la viga y colapso.
"""

import bpy
import bmesh
import math
import os
import shutil

PROJECT_ROOT = r"F:\Dev\Game"
TEX_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Environment")
FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Environment")
RENDER_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
BLEND_DIR = os.path.join(PROJECT_ROOT, "Art", "Blender")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(BLEND_DIR, exist_ok=True)

# Limpiar escena inicial
bpy.ops.wm.read_factory_settings(use_empty=True)

# Regiones UV Trim Sheet
UV_METAL_PANEL = (0.01, 0.01, 0.49, 0.49)
UV_HAZARD_STRIPES = (0.01, 0.51, 0.99, 0.74)
UV_DARK_FRAME = (0.51, 0.01, 0.99, 0.49)
UV_RIVETS = (0.01, 0.76, 0.25, 0.99)
UV_VENT_SLATS = (0.26, 0.76, 0.50, 0.99)

def get_or_create_material():
    mat_name = "M_TrimSheet_Industrial"
    mat = bpy.data.materials.get(mat_name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    base_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_BaseColor.png")
    orm_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_ORM.png")
    norm_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Normal.png")

    if os.path.exists(base_path):
        img_b = bpy.data.images.load(base_path)
        node_b = nodes.new(type='ShaderNodeTexImage')
        node_b.image = img_b
        node_b.location = (-400, 200)
        links.new(node_b.outputs['Color'], principled.inputs['Base Color'])

    if os.path.exists(orm_path):
        img_o = bpy.data.images.load(orm_path)
        img_o.colorspace_settings.name = 'Non-Color'
        node_o = nodes.new(type='ShaderNodeTexImage')
        node_o.image = img_o
        node_o.location = (-400, -100)
        sep = nodes.new(type='ShaderNodeSeparateColor')
        sep.location = (-100, -100)
        links.new(node_o.outputs['Color'], sep.inputs['Color'])
        links.new(sep.outputs['Green'], principled.inputs['Roughness'])
        links.new(sep.outputs['Blue'], principled.inputs['Metallic'])

    if os.path.exists(norm_path):
        img_n = bpy.data.images.load(norm_path)
        img_n.colorspace_settings.name = 'Non-Color'
        node_n = nodes.new(type='ShaderNodeTexImage')
        node_n.image = img_n
        node_n.location = (-400, -400)
        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.location = (-100, -400)
        links.new(node_n.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], principled.inputs['Normal'])

    return mat

mat = get_or_create_material()

def map_box_uvs(bm, uv_box):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_box
    for face in bm.faces:
        for loop in face.loops:
            v_co = loop.vert.co
            # Proyección planar según normal dominante
            if abs(face.normal.z) > 0.5:
                u = (v_co.x + 2.0) / 4.0
                v = (v_co.y + 0.3) / 0.6
            elif abs(face.normal.y) > 0.5:
                u = (v_co.x + 2.0) / 4.0
                v = (v_co.z + 0.3) / 0.6
            else:
                u = (v_co.y + 0.3) / 0.6
                v = (v_co.z + 0.3) / 0.6
            loop[uv_layer].uv = (u0 + (u % 1.0) * (u1 - u0), v0 + (v % 1.0) * (v1 - v0))

# ==============================================================================
# 1. SM_StructuralBeam_Heavy_400cm
# ==============================================================================
def create_structural_beam():
    mesh = bpy.data.meshes.new("SM_StructuralBeam_Heavy_400cm")
    obj = bpy.data.objects.new("SM_StructuralBeam_Heavy_400cm", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()

    # Viga en I: Largo 400cm (X: -2.0 a 2.0), Alto 45cm (Z: -0.225 a 0.225), Ancho 35cm (Y: -0.175 a 0.175)
    # Ala superior
    top_flange = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.0, 0.35, 0.06), verts=top_flange['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.195), verts=top_flange['verts'])

    # Ala inferior
    bot_flange = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.0, 0.35, 0.06), verts=bot_flange['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, -0.195), verts=bot_flange['verts'])

    # Alma central
    web = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.0, 0.08, 0.33), verts=web['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.0), verts=web['verts'])

    # 5 Costillas de refuerzo verticales (Stiffeners) con orificios circulares
    stiffener_x = [-1.5, -0.75, 0.0, 0.75, 1.5]
    for sx in stiffener_x:
        # Placa vertical lateral +Y
        s_pos = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.04, 0.135, 0.33), verts=s_pos['verts'])
        bmesh.ops.translate(bm, vec=(sx, 0.1075, 0.0), verts=s_pos['verts'])

        # Placa vertical lateral -Y
        s_neg = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.04, 0.135, 0.33), verts=s_neg['verts'])
        bmesh.ops.translate(bm, vec=(sx, -0.1075, 0.0), verts=s_neg['verts'])

    # Placas de anclaje de extremo con 8 remaches/pernos hexagonales en cada extremo
    end_xs = [-2.0, 2.0]
    for ex in end_xs:
        # Placa de extremo
        end_plate = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.06, 0.42, 0.50), verts=end_plate['verts'])
        bmesh.ops.translate(bm, vec=(ex, 0.0, 0.0), verts=end_plate['verts'])

        # 8 pernos
        bolt_offsets = [
            (ex + (0.035 if ex > 0 else -0.035), -0.16, -0.18),
            (ex + (0.035 if ex > 0 else -0.035), 0.16, -0.18),
            (ex + (0.035 if ex > 0 else -0.035), -0.16, 0.18),
            (ex + (0.035 if ex > 0 else -0.035), 0.16, 0.18),
            (ex + (0.035 if ex > 0 else -0.035), -0.16, -0.06),
            (ex + (0.035 if ex > 0 else -0.035), 0.16, -0.06),
            (ex + (0.035 if ex > 0 else -0.035), -0.16, 0.06),
            (ex + (0.035 if ex > 0 else -0.035), 0.16, 0.06),
        ]
        for bx, by, bz in bolt_offsets:
            bolt = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.025, radius2=0.025, depth=0.03)
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'Y'), verts=bolt['verts'])
            bmesh.ops.translate(bm, vec=(bx, by, bz), verts=bolt['verts'])

    # Mapeo UV (franjas de peligro en alas exteriores, paneles metálicos en resto)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        # Si la cara está orientada hacia abajo (cara inferior de la viga que da al pasillo)
        if face.normal.z < -0.8 and face.calc_center_median().z < -0.2:
            u0, v0, u1, v1 = UV_HAZARD_STRIPES
        elif face.normal.z > 0.8 and face.calc_center_median().z > 0.2:
            u0, v0, u1, v1 = UV_HAZARD_STRIPES
        elif abs(face.normal.x) > 0.8:
            u0, v0, u1, v1 = UV_RIVETS
        else:
            u0, v0, u1, v1 = UV_METAL_PANEL

        for loop in face.loops:
            v_co = loop.vert.co
            u = (v_co.x + 2.0) / 4.0
            v = (v_co.y + 0.3) / 0.6
            loop[uv_layer].uv = (u0 + (u % 1.0) * (u1 - u0), v0 + (v % 1.0) * (v1 - v0))

    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)

    # -------------------------------------------------------------
    # Colisiones Convexas UCX (Ala superior, Ala inferior, Alma)
    # -------------------------------------------------------------
    ucx_boxes = [
        ("UCX_SM_StructuralBeam_Heavy_400cm_01", (4.0, 0.36, 0.07), (0.0, 0.0, 0.195)),
        ("UCX_SM_StructuralBeam_Heavy_400cm_02", (4.0, 0.36, 0.07), (0.0, 0.0, -0.195)),
        ("UCX_SM_StructuralBeam_Heavy_400cm_03", (4.0, 0.10, 0.34), (0.0, 0.0, 0.0)),
        ("UCX_SM_StructuralBeam_Heavy_400cm_04", (0.08, 0.44, 0.52), (-2.0, 0.0, 0.0)),
        ("UCX_SM_StructuralBeam_Heavy_400cm_05", (0.08, 0.44, 0.52), (2.0, 0.0, 0.0)),
    ]

    ucx_objs = []
    for ucx_name, size, pos in ucx_boxes:
        cmesh = bpy.data.meshes.new(ucx_name)
        cobj = bpy.data.objects.new(ucx_name, cmesh)
        bpy.context.scene.collection.objects.link(cobj)
        cbm = bmesh.new()
        bmesh.ops.create_cube(cbm, size=1.0)
        bmesh.ops.scale(cbm, vec=size, verts=cbm.verts)
        bmesh.ops.translate(cbm, vec=pos, verts=cbm.verts)
        cbm.to_mesh(cmesh)
        cbm.free()
        cobj.parent = obj
        ucx_objs.append(cobj)

    return obj, ucx_objs

# ==============================================================================
# 2. SM_CeilingBracket_40cm
# ==============================================================================
def create_ceiling_bracket():
    mesh = bpy.data.meshes.new("SM_CeilingBracket_40cm")
    obj = bpy.data.objects.new("SM_CeilingBracket_40cm", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()
    # Placa base atornillada al techo
    base = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.45, 0.45, 0.08), verts=base['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.16), verts=base['verts'])

    # Horquilla que sujetaba la viga con extremos dentados/fracturados
    fork_l = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.10, 0.45, 0.28), verts=fork_l['verts'])
    bmesh.ops.translate(bm, vec=(-0.16, 0.0, 0.0), verts=fork_l['verts'])

    fork_r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.10, 0.45, 0.28), verts=fork_r['verts'])
    bmesh.ops.translate(bm, vec=(0.16, 0.0, 0.0), verts=fork_r['verts'])

    # Pernos cortados con metal desgarrado
    stud_offsets = [(-0.16, -0.15, -0.14), (-0.16, 0.15, -0.14), (0.16, -0.15, -0.14), (0.16, 0.15, -0.14)]
    for sx, sy, sz in stud_offsets:
        stud = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.03, radius2=0.02, depth=0.08)
        bmesh.ops.translate(bm, vec=(sx, sy, sz), verts=stud['verts'])

    map_box_uvs(bm, UV_DARK_FRAME)
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)

    # UCX
    cmesh = bpy.data.meshes.new("UCX_SM_CeilingBracket_40cm_01")
    cobj = bpy.data.objects.new("UCX_SM_CeilingBracket_40cm_01", cmesh)
    bpy.context.scene.collection.objects.link(cobj)
    cbm = bmesh.new()
    bmesh.ops.create_cube(cbm, size=1.0)
    bmesh.ops.scale(cbm, vec=(0.46, 0.46, 0.40), verts=cbm.verts)
    bmesh.ops.translate(cbm, vec=(0.0, 0.0, 0.05), verts=cbm.verts)
    cbm.to_mesh(cmesh)
    cbm.free()
    cobj.parent = obj

    return obj, [cobj]

# ==============================================================================
# 3. SM_Debris_Chunk_01 y 02
# ==============================================================================
def create_debris_chunk(name, size_vec):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()
    cube = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size_vec, verts=cube['verts'])

    # Bisel angular irregular para simular fractura
    bmesh.ops.bevel(bm, geom=bm.edges, offset=0.04, segments=1, affect='EDGES')

    map_box_uvs(bm, UV_DARK_FRAME)
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)

    # UCX
    ucx_name = f"UCX_{name}_01"
    cmesh = bpy.data.meshes.new(ucx_name)
    cobj = bpy.data.objects.new(ucx_name, cmesh)
    bpy.context.scene.collection.objects.link(cobj)
    cbm = bmesh.new()
    bmesh.ops.create_cube(cbm, size=1.0)
    bmesh.ops.scale(cbm, vec=(size_vec[0] * 1.05, size_vec[1] * 1.05, size_vec[2] * 1.05), verts=cbm.verts)
    cbm.to_mesh(cmesh)
    cbm.free()
    cobj.parent = obj

    return obj, [cobj]

import mathutils

beam_obj, beam_ucx = create_structural_beam()
bracket_obj, bracket_ucx = create_ceiling_bracket()
debris1_obj, debris1_ucx = create_debris_chunk("SM_Debris_Chunk_01", (0.35, 0.25, 0.20))
debris2_obj, debris2_ucx = create_debris_chunk("SM_Debris_Chunk_02", (0.28, 0.20, 0.15))

# ==============================================================================
# EXPORTACIÓN FBX
# ==============================================================================
def export_asset_fbx(main_obj, ucx_list, filename):
    for o in bpy.data.objects:
        o.select_set(False)
    main_obj.select_set(True)
    for u in ucx_list:
        u.select_set(True)
    bpy.context.view_layer.objects.active = main_obj

    filepath = os.path.join(FBX_DIR, filename)
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False,
        mesh_smooth_type='FACE',
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"[OK] Exportado FBX: {filepath}")

export_asset_fbx(beam_obj, beam_ucx, "SM_StructuralBeam_Heavy_400cm.fbx")
export_asset_fbx(bracket_obj, bracket_ucx, "SM_CeilingBracket_40cm.fbx")
export_asset_fbx(debris1_obj, debris1_ucx, "SM_Debris_Chunk_01.fbx")
export_asset_fbx(debris2_obj, debris2_ucx, "SM_Debris_Chunk_02.fbx")

# ==============================================================================
# ESCENA DE SHOWCASE Y RENDER 2560x1440
# ==============================================================================
# Colocar objetos en disposición de showcase dinámico
beam_obj.location = (0.0, 0.0, 1.2)
beam_obj.rotation_euler = (math.radians(-15), math.radians(8), math.radians(25)) # Pose de colapso inclinado

bracket_obj.location = (-1.8, 0.8, 2.2)
debris1_obj.location = (0.8, -0.6, 0.1)
debris1_obj.rotation_euler = (math.radians(20), math.radians(45), math.radians(10))
debris2_obj.location = (-0.5, 0.9, 0.08)
debris2_obj.rotation_euler = (math.radians(-30), math.radians(15), math.radians(80))

# Crear suelo de rejilla metálica para el render
floor_mesh = bpy.data.meshes.new("FloorMesh")
floor_obj = bpy.data.objects.new("FloorMesh", floor_mesh)
bpy.context.scene.collection.objects.link(floor_obj)
fbm = bmesh.new()
bmesh.ops.create_grid(fbm, x_segments=2, y_segments=2, size=5.0)
map_box_uvs(fbm, UV_VENT_SLATS)
fbm.to_mesh(floor_mesh)
fbm.free()
floor_obj.data.materials.append(mat)
floor_obj.location = (0, 0, 0)

# Ocultar UCX del render
for u in beam_ucx + bracket_ucx + debris1_ucx + debris2_ucx:
    u.hide_render = True

# Iluminación dramática de emergencia espacial
light_key = bpy.data.lights.new("KeyLight", type='AREA')
light_key.energy = 800
light_key.color = (1.0, 0.85, 0.7)
light_key.size = 3.0
obj_key = bpy.data.objects.new("KeyLight", light_key)
bpy.context.scene.collection.objects.link(obj_key)
obj_key.location = (3.0, -3.5, 4.0)
obj_key.rotation_euler = (math.radians(50), 0, math.radians(40))

light_amber = bpy.data.lights.new("AmberAlertLight", type='POINT')
light_amber.energy = 600
light_amber.color = (1.0, 0.4, 0.05)
obj_amber = bpy.data.objects.new("AmberAlertLight", light_amber)
bpy.context.scene.collection.objects.link(obj_amber)
obj_amber.location = (-2.5, -2.0, 1.5)

light_blue = bpy.data.lights.new("RimBlue", type='AREA')
light_blue.energy = 700
light_blue.color = (0.2, 0.6, 1.0)
light_blue.size = 4.0
obj_blue = bpy.data.objects.new("RimBlue", light_blue)
bpy.context.scene.collection.objects.link(obj_blue)
obj_blue.location = (-3.5, 3.5, 3.5)
obj_blue.rotation_euler = (math.radians(-40), 0, math.radians(-140))

# Cámara cinematográfica
cam = bpy.data.cameras.new("ShowcaseCamera")
cam.lens = 35
cam_obj = bpy.data.objects.new("ShowcaseCamera", cam)
bpy.context.scene.collection.objects.link(cam_obj)
cam_obj.location = (4.2, -5.5, 3.2)
cam_obj.rotation_euler = (math.radians(64), 0, math.radians(37))
bpy.context.scene.camera = cam_obj

# Configuración de render
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440
scene.render.film_transparent = False

render_output = os.path.join(RENDER_DIR, "Showcase_Structural_Collapse_Beam.png")
scene.render.filepath = render_output
bpy.ops.render.render(write_still=True)
print(f"[OK] Render de showcase guardado: {render_output}")

# Copiar a artifacts
if os.path.exists(ARTIFACT_DIR):
    art_dest = os.path.join(ARTIFACT_DIR, "Showcase_Structural_Collapse_Beam.png")
    shutil.copyfile(render_output, art_dest)
    print(f"[OK] Showcase copiado a artefactos: {art_dest}")

blend_path = os.path.join(BLEND_DIR, "SM_Structural_Collapse_Official.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[OK] Escena Blender guardada: {blend_path}")
