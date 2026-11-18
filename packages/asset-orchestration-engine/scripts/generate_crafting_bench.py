"""generate_crafting_bench.py
Construye la Mesa de Crafteo Modular Sci-Fi definitiva (SM_CraftingBench)
fiel a la imagen de referencia del usuario:
- Chasis cerámico blanco con tapas de esquina biseladas en titanio oscuro.
- Superficie encastrada con placas de metal cepillado y cubierta de cristal protector.
- Fosa central con vórtice holográfico de plasma violeta en espiral (textura procedural de alta resolución).
- Receptáculo circular de contención con anillo de energía morado.
- Herramienta de intervención técnica en hendidura ergonómica (acabado cromo espejo).
- Pad modular de control con indicador LED.
- Proyector angular con pantalla holográfica HUD translúcida cian/violeta (retícula circular, telemetría y datos).
- Cajones laterales con tirador empotrado y conducciones de suelo con codos a 90°.
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

R = math.radians
TAU = math.pi * 2

OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
TEX_DIR = r"E:\Darx_Proyect\Art\Textures"
MASTER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend"

VORTEX_TEX_PATH = os.path.join(TEX_DIR, "T_Bench_Vortex.png")
HOLO_TEX_PATH = os.path.join(TEX_DIR, "T_Bench_HoloHUD.png")

def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    # Color Management fílmico para contraste sci-fi
    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

    # Suelo oscuro de estudio con rugosidad difusa
    me_floor = bpy.data.meshes.new("Floor")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=4, y_segments=4, size=18.0)
    bm_f.to_mesh(me_floor)
    bm_f.free()

    obj_floor = bpy.data.objects.new("Studio_Floor", me_floor)
    scene.collection.objects.link(obj_floor)

    m_floor = bpy.data.materials.new("M_Floor_DarkStudio")
    bsdf_f = m_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.015, 0.015, 0.020, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.40
        bsdf_f.inputs['Roughness'].default_value = 0.55
    me_floor.materials.append(m_floor)

    # Iluminación de estudio
    # 1. Key Light Frontal Derecha (Luz suave blanca cálida)
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 110.0
    l1_data.size = 2.4
    l1_data.color = (1.0, 0.98, 0.96)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (2.2, -2.4, 2.2)
    l1.rotation_euler = (R(52), R(12), R(42))
    scene.collection.objects.link(l1)

    # 2. Fill Light Frontal Izquierda (Azul suave táctico)
    l2_data = bpy.data.lights.new("LGT_Fill", 'AREA')
    l2_data.energy = 55.0
    l2_data.size = 2.8
    l2_data.color = (0.80, 0.92, 1.0)
    l2 = bpy.data.objects.new("LGT_Fill", l2_data)
    l2.location = (-2.4, -1.8, 1.8)
    l2.rotation_euler = (R(52), R(-18), R(-45))
    scene.collection.objects.link(l2)

    # 3. Rim Light Trasera Derecha
    l3_data = bpy.data.lights.new("LGT_RimR", 'AREA')
    l3_data.energy = 90.0
    l3_data.size = 1.8
    l3_data.color = (0.92, 0.96, 1.0)
    l3 = bpy.data.objects.new("LGT_RimR", l3_data)
    l3.location = (2.0, 2.0, 1.8)
    l3.rotation_euler = (R(-45), R(18), R(-135))
    scene.collection.objects.link(l3)

    # 4. Rim Light Violeta Neón de Acento (Acento suave, no deslumbrante)
    l4_data = bpy.data.lights.new("LGT_RimViolet", 'AREA')
    l4_data.energy = 50.0
    l4_data.size = 1.4
    l4_data.color = (0.75, 0.12, 1.0)
    l4 = bpy.data.objects.new("LGT_RimViolet", l4_data)
    l4.location = (-2.0, 2.0, 1.8)
    l4.rotation_euler = (R(-45), R(-18), R(135))
    scene.collection.objects.link(l4)

    # 5. Luz de emisión sutil para el Holograma HUD
    l_holo_data = bpy.data.lights.new("LGT_Holo_Glow", 'POINT')
    l_holo_data.energy = 10.0
    l_holo_data.color = (0.05, 0.85, 1.0)
    l_holo = bpy.data.objects.new("LGT_Holo_Glow", l_holo_data)
    l_holo.location = (0.42, 0.42, 1.02)
    scene.collection.objects.link(l_holo)

def create_shaders():
    mats = {}

    # 1. Chasis Cerámico Blanco Táctico (Acabado satinado mate de alta tecnología)
    m_white = bpy.data.materials.new("M_Bench_Ceramic_White")
    bsdf = m_white.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.88, 0.90, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.02
        bsdf.inputs['Roughness'].default_value = 0.38
    mats['white'] = m_white

    # 2. Refuerzos Metálicos de Esquina y Tiradores (Titanio Carbón Oscuro)
    m_dark = bpy.data.materials.new("M_Bench_Corner_Metal")
    bsdf = m_dark.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.095, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.30
    mats['dark_metal'] = m_dark

    # 3. Placas de Trabajo de Metal Cepillado (Satinado industrial sin reflejos de espejo)
    m_metal = bpy.data.materials.new("M_Bench_Plates_Brushed")
    bsdf = m_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.38, 0.40, 0.43, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.80
        bsdf.inputs['Roughness'].default_value = 0.42
    mats['brushed_metal'] = m_metal

    # 4. Herramientas de Precisión Cromo Pulido
    m_chrome = bpy.data.materials.new("M_Bench_Chrome_Tool")
    bsdf = m_chrome.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.92, 0.93, 0.96, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.98
        bsdf.inputs['Roughness'].default_value = 0.08
    mats['chrome'] = m_chrome

    # 5. Cubierta de Cristal Templado Encastrado (Transparente y limpio con reflejo sutil)
    m_glass = bpy.data.materials.new("M_Bench_Glass")
    m_glass.blend_method = 'BLEND'
    bsdf = m_glass.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.02
        bsdf.inputs['Transmission Weight'].default_value = 0.98
        bsdf.inputs['Alpha'].default_value = 0.08
        bsdf.inputs['IOR'].default_value = 1.48
    mats['glass'] = m_glass

    # 6. Vórtice de Plasma Violeta en Espiral (Textura Procedural Hi-Res UV)
    m_vortex = bpy.data.materials.new("M_Bench_Vortex_Plasma")
    m_vortex.blend_method = 'BLEND'
    nt = m_vortex.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    
    # Coordenadas UV explícitas
    tex_coord = nt.nodes.new('ShaderNodeTexCoord')
    
    # Cargar textura PNG con canal alfa
    tex_vort = nt.nodes.new('ShaderNodeTexImage')
    if os.path.exists(VORTEX_TEX_PATH):
        tex_vort.image = bpy.data.images.load(VORTEX_TEX_PATH)
    
    nt.links.new(tex_coord.outputs['UV'], tex_vort.inputs['Vector'])
    
    bsdf.inputs['Base Color'].default_value = (0.02, 0.0, 0.05, 1.0)
    nt.links.new(tex_vort.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 6.5
    nt.links.new(tex_vort.outputs['Alpha'], bsdf.inputs['Alpha'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['vortex'] = m_vortex

    # 7. Receptáculo Anillo de Energía Violeta
    m_ring = bpy.data.materials.new("M_Bench_Ring_Glow")
    nt = m_ring.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.85, 0.20, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 7.5
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['ring'] = m_ring

    # 8. Barra Emisora Proyector
    m_proj_bar = bpy.data.materials.new("M_Bench_Projector_Bar")
    nt = m_proj_bar.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = (0.10, 0.90, 1.0, 1.0)
    emis.inputs['Strength'].default_value = 8.5
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mats['proj_bar'] = m_proj_bar

    # 9. Holograma HUD Táctico Translúcido (Textura Hi-Res Fiel a la Referencia)
    m_holo = bpy.data.materials.new("M_Bench_HoloHUD")
    m_holo.blend_method = 'BLEND'
    nt = m_holo.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    
    tex_holo = nt.nodes.new('ShaderNodeTexImage')
    if os.path.exists(HOLO_TEX_PATH):
        tex_holo.image = bpy.data.images.load(HOLO_TEX_PATH)
        
    bsdf.inputs['Base Color'].default_value = (0.01, 0.05, 0.08, 1.0)
    nt.links.new(tex_holo.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = 3.2
    nt.links.new(tex_holo.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['Transmission Weight'].default_value = 0.85
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mats['holo'] = m_holo

    return mats

def add_box(bm, size, loc=(0,0,0), rot=(0,0,0)):
    rot_m = Euler((R(rot[0]), R(rot[1]), R(rot[2])), 'XYZ').to_matrix().to_4x4()
    mat = Matrix.Translation(Vector(loc)) @ rot_m @ Matrix.Diagonal((size[0], size[1], size[2], 1.0))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)['verts']

def add_cylinder(bm, radius, depth, loc=(0,0,0), rot=(0,0,0), seg=24):
    rot_m = Euler((R(rot[0]), R(rot[1]), R(rot[2])), 'XYZ').to_matrix().to_4x4()
    mat = Matrix.Translation(Vector(loc)) @ rot_m
    return bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=radius, radius2=radius, depth=depth, matrix=mat)['verts']

def build_crafting_bench(mats):
    col = bpy.data.collections.new("Col_SM_CraftingBench")
    bpy.context.scene.collection.children.link(col)

    bench_obj = bpy.data.objects.new("SM_CraftingBench", bpy.data.meshes.new("SM_CraftingBench_Mesh"))
    col.objects.link(bench_obj)
    bm = bmesh.new()

    # Cotas Canónicas Métricas: Ancho: 1.40 m, Fondo: 1.40 m, Altura de trabajo: 0.88 m
    # 1. CUATRO PATAS CUADRADAS CON ARISTA BISELADA
    leg_x = 0.55
    leg_y = 0.55
    for sx in (1, -1):
        for sy in (1, -1):
            # Pata principal
            add_box(bm, (0.19, 0.19, 0.76), loc=(leg_x * sx, leg_y * sy, 0.38))
            # Zapata inferior en contacto con suelo
            add_box(bm, (0.20, 0.20, 0.04), loc=(leg_x * sx, leg_y * sy, 0.02))

    # 2. CUATRO PANELES LATERALES EMPOTRADOS CON CAJONES
    for sx in (1, -1):
        # Lados X (+X, -X)
        add_box(bm, (0.04, 0.91, 0.44), loc=(0.55 * sx, 0, 0.52))
        add_box(bm, (0.05, 0.82, 0.36), loc=(0.565 * sx, 0, 0.52))
        # Tirador empotrado
        add_box(bm, (0.025, 0.16, 0.035), loc=(0.595 * sx, 0, 0.66))

        # Lados Y (+Y, -Y)
        add_box(bm, (0.91, 0.04, 0.44), loc=(0, 0.55 * sx, 0.52))
        add_box(bm, (0.82, 0.05, 0.36), loc=(0, 0.565 * sx, 0.52))
        # Tirador empotrado
        add_box(bm, (0.16, 0.025, 0.035), loc=(0, 0.595 * sx, 0.66))

    # 3. MARCO PERIMETRAL SUPERIOR (Cerámica Blanca)
    bar_w = 0.19
    add_box(bm, (1.42, bar_w, 0.12), loc=(0, 0.615, 0.82))
    add_box(bm, (1.42, bar_w, 0.12), loc=(0, -0.615, 0.82))
    add_box(bm, (bar_w, 1.04, 0.12), loc=(0.615, 0, 0.82))
    add_box(bm, (bar_w, 1.04, 0.12), loc=(-0.615, 0, 0.82))

    # Ranuras de ventilación longitudinales en el marco
    add_box(bm, (0.04, 0.28, 0.015), loc=(-0.615, 0.15, 0.885))
    add_box(bm, (0.28, 0.04, 0.015), loc=(0.15, -0.615, 0.885))

    # 4. CUATRO TAPAS METÁLICAS OSCURAS DE ESQUINA ("CORNER BUMPERS / CAPS")
    for sx in (1, -1):
        for sy in (1, -1):
            add_box(bm, (0.22, 0.22, 0.13), loc=(0.60 * sx, 0.60 * sy, 0.825))

    # 5. SUPERFICIE DE TRABAJO ENCASTRADA (Z = 0.81 m)
    # Bandeja base
    add_box(bm, (1.04, 1.04, 0.04), loc=(0, 0, 0.78))

    # Placa central con fosa de síntesis
    add_box(bm, (0.54, 0.54, 0.02), loc=(0, 0, 0.805))
    # Fosa hundida central
    add_box(bm, (0.40, 0.40, 0.03), loc=(0, 0, 0.79))

    # Placa izquierda con estrías horizontales de refrigeración
    add_box(bm, (0.24, 0.98, 0.02), loc=(-0.38, 0, 0.81))
    for iy in range(4):
        add_box(bm, (0.03, 0.14, 0.012), loc=(-0.38, -0.30 + iy * 0.20, 0.825))

    # Placas derechas de trabajo
    add_box(bm, (0.24, 0.52, 0.02), loc=(0.38, -0.23, 0.81))
    add_box(bm, (0.48, 0.22, 0.02), loc=(0, -0.38, 0.81))

    # 6. RECEPTÁCULO CILÍNDRICO DE CONTENCIÓN (Hacia Y = +0.32, X = -0.06)
    add_cylinder(bm, radius=0.11, depth=0.035, loc=(-0.06, 0.32, 0.805), seg=24)
    add_cylinder(bm, radius=0.085, depth=0.040, loc=(-0.06, 0.32, 0.81), seg=24)

    # 7. PAD MODULAR DE INTERFAZ (Esquina frontal derecha, X=0.10, Y=-0.36)
    add_box(bm, (0.16, 0.16, 0.035), loc=(0.10, -0.36, 0.82))
    add_box(bm, (0.10, 0.10, 0.040), loc=(0.10, -0.36, 0.825))
    add_cylinder(bm, radius=0.025, depth=0.045, loc=(0.10, -0.36, 0.83), seg=16)

    # 8. HENDIDURA DE HERRAMIENTAS Y HERRAMIENTAS DE PRECISIÓN (X=0.36, Y=0.04)
    add_box(bm, (0.16, 0.36, 0.020), loc=(0.36, 0.14, 0.81))
    # Herramienta / Tenaza de intervención con cabezal circular cromado y mangos dobles
    add_cylinder(bm, radius=0.034, depth=0.016, loc=(0.31, 0.04, 0.825), seg=16)
    add_cylinder(bm, radius=0.016, depth=0.022, loc=(0.31, 0.04, 0.828), seg=16)
    add_box(bm, (0.018, 0.18, 0.012), loc=(0.33, 0.16, 0.825), rot=(0, 0, 12))
    add_box(bm, (0.018, 0.18, 0.012), loc=(0.40, 0.16, 0.825), rot=(0, 0, -12))

    # 9. BASE DEL PROYECTOR HOLOGRÁFICO (Esquina posterior derecha: X=0.44, Y=0.44)
    add_box(bm, (0.36, 0.16, 0.07), loc=(0.44, 0.44, 0.90), rot=(-12, 0, -18))
    add_box(bm, (0.31, 0.12, 0.08), loc=(0.44, 0.44, 0.91), rot=(-12, 0, -18))

    # 10. CONDUCCIONES / TUBERÍAS DE SUELO (Z = 0.02 m)
    add_box(bm, (0.025, 1.35, 0.025), loc=(-0.74, 0, 0.02))
    add_box(bm, (0.025, 1.35, 0.025), loc=(-0.78, 0, 0.02))
    add_box(bm, (0.82, 0.025, 0.025), loc=(-0.36, -0.70, 0.02))
    add_box(bm, (0.82, 0.025, 0.025), loc=(-0.36, -0.74, 0.02))
    add_box(bm, (0.025, 0.85, 0.025), loc=(0.74, -0.30, 0.02))

    # Finalizar malla de chasis
    bm.to_mesh(bench_obj.data)
    bm.free()

    bench_obj.data.materials.append(mats['white'])
    bench_obj.data.materials.append(mats['dark_metal'])
    bench_obj.data.materials.append(mats['brushed_metal'])
    bench_obj.data.materials.append(mats['chrome'])

    for p in bench_obj.data.polygons:
        p.use_smooth = True
        c = p.center
        # Esquinas exteriores reforzadas -> dark_metal
        if abs(c.x) > 0.45 and abs(c.y) > 0.45 and c.z > 0.74:
            p.material_index = 1
        # Tiradores y patas inferiores -> dark_metal
        elif c.z < 0.05 or (abs(c.z - 0.66) < 0.05 and (abs(c.x) > 0.57 or abs(c.y) > 0.57)):
            p.material_index = 1
        # Base del proyector -> dark_metal
        elif c.x > 0.28 and c.y > 0.28 and c.z > 0.86:
            p.material_index = 1
        # Herramientas de precisión -> chrome
        elif 0.25 < c.x < 0.45 and -0.05 < c.y < 0.30 and c.z > 0.815:
            p.material_index = 3
        # Placas interiores de trabajo -> brushed_metal
        elif abs(c.x) < 0.52 and abs(c.y) < 0.52 and c.z > 0.76:
            p.material_index = 2
        else:
            p.material_index = 0

    # 11. CUBIERTA DE CRISTAL TEMPLADO ENCASTRADO (Plano simple anti-ruido)
    glass_mesh = bpy.data.meshes.new("SM_CraftingBench_Glass_Mesh")
    bm_g = bmesh.new()
    bmesh.ops.create_grid(bm_g, x_segments=1, y_segments=1, size=0.58, matrix=Matrix.Translation(Vector((0, 0, 0.828))))
    bm_g.to_mesh(glass_mesh)
    bm_g.free()
    glass_obj = bpy.data.objects.new("SM_CraftingBench_Glass", glass_mesh)
    col.objects.link(glass_obj)
    mats['glass'].use_backface_culling = False
    glass_mesh.materials.append(mats['glass'])
    for p in glass_mesh.polygons:
        p.use_smooth = True

    # 12. VÓRTICE DE PLASMA VIOLETA EN ESPIRAL (Plano Cuadrado con UV Mapping Canónico [0,1]x[0,1])
    vortex_mesh = bpy.data.meshes.new("SM_CraftingBench_Vortex_Mesh")
    bm_v = bmesh.new()
    
    s_v = 0.42
    bmesh.ops.create_grid(bm_v, x_segments=1, y_segments=1, size=s_v, matrix=Matrix.Translation(Vector((0, 0, 0.818))))
    bm_v.faces.ensure_lookup_table()
    
    uv_layer = bm_v.loops.layers.uv.verify()
    f_v = bm_v.faces[0]
    f_v.loops[0][uv_layer].uv = Vector((0.0, 0.0))
    f_v.loops[1][uv_layer].uv = Vector((1.0, 0.0))
    f_v.loops[2][uv_layer].uv = Vector((1.0, 1.0))
    f_v.loops[3][uv_layer].uv = Vector((0.0, 1.0))

    bm_v.to_mesh(vortex_mesh)
    bm_v.free()
    vortex_obj = bpy.data.objects.new("SM_CraftingBench_Vortex", vortex_mesh)
    col.objects.link(vortex_obj)
    mats['vortex'].use_backface_culling = False
    vortex_mesh.materials.append(mats['vortex'])
    for p in vortex_mesh.polygons:
        p.use_smooth = True

    # Anillo de contención en receptáculo circular
    ring_mesh = bpy.data.meshes.new("SM_CraftingBench_Ring_Mesh")
    bm_r = bmesh.new()
    # Anillo emisor violeta
    add_cylinder(bm_r, radius=0.082, depth=0.012, loc=(-0.06, 0.32, 0.822), seg=28)
    # LED en pad modular
    add_cylinder(bm_r, radius=0.022, depth=0.010, loc=(0.10, -0.36, 0.835), seg=16)
    bm_r.to_mesh(ring_mesh)
    bm_r.free()
    ring_obj = bpy.data.objects.new("SM_CraftingBench_Ring", ring_mesh)
    col.objects.link(ring_obj)
    ring_mesh.materials.append(mats['ring'])

    # 13. PANTALLA HOLOGRÁFICA HUD TÁCTICA (Plano UV con Textura de Alta Definición)
    holo_mesh = bpy.data.meshes.new("SM_CraftingBench_HoloHUD_Mesh")
    bm_h = bmesh.new()
    holo_w = 0.44
    holo_h = 0.28
    holo_loc = (0.44, 0.44, 1.13)
    holo_rot = (-12, 0, -18)

    rot_m = Euler((R(holo_rot[0]), R(holo_rot[1]), R(holo_rot[2])), 'XYZ').to_matrix().to_4x4()
    center_v = Vector(holo_loc)
    
    # Crear plano rectangular con coordenadas UV directas
    # Vértices locales en el plano XY orientados hacia Z
    half_w = holo_w / 2.0
    half_h = holo_h / 2.0
    
    # 4 vértices del panel holográfico (en espacio local Y=0, X=[-hw, hw], Z=[-hh, hh])
    p0 = center_v + rot_m @ Vector((-half_w, 0, -half_h))
    p1 = center_v + rot_m @ Vector(( half_w, 0, -half_h))
    p2 = center_v + rot_m @ Vector(( half_w, 0,  half_h))
    p3 = center_v + rot_m @ Vector((-half_w, 0,  half_h))

    v0 = bm_h.verts.new(p0)
    v1 = bm_h.verts.new(p1)
    v2 = bm_h.verts.new(p2)
    v3 = bm_h.verts.new(p3)

    f_front = bm_h.faces.new((v0, v1, v2, v3))

    uv_h = bm_h.loops.layers.uv.verify()
    # Mapeo UV frontal
    f_front.loops[0][uv_h].uv = Vector((0.0, 0.0))
    f_front.loops[1][uv_h].uv = Vector((1.0, 0.0))
    f_front.loops[2][uv_h].uv = Vector((1.0, 1.0))
    f_front.loops[3][uv_h].uv = Vector((0.0, 1.0))

    bm_h.to_mesh(holo_mesh)
    bm_h.free()
    holo_obj = bpy.data.objects.new("SM_CraftingBench_HoloHUD", holo_mesh)
    col.objects.link(holo_obj)
    mats['holo'].use_backface_culling = False
    holo_mesh.materials.append(mats['holo'])
    for p in holo_mesh.polygons:
        p.use_smooth = True

    # 14. Barra emisora del proyector
    bar_mesh = bpy.data.meshes.new("SM_CraftingBench_Bar_Mesh")
    bm_b = bmesh.new()
    add_box(bm_b, (0.28, 0.05, 0.018), loc=(0.44, 0.44, 0.965), rot=(-12, 0, -18))
    bm_b.to_mesh(bar_mesh)
    bm_b.free()
    bar_obj = bpy.data.objects.new("SM_CraftingBench_ProjBar", bar_mesh)
    col.objects.link(bar_obj)
    bar_mesh.materials.append(mats['proj_bar'])

    return bench_obj, vortex_obj, holo_obj

def render_shot(cam_obj, loc, target, fov, fname):
    scene = bpy.context.scene
    cam_obj.location = Vector(loc)
    dir_vec = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.data.angle = R(fov)
    p = os.path.join(OUT_DIR, fname)
    scene.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED: {fname}")
    return p

def main():
    print("=== [1/4] INICIALIZANDO ESCENA Y CONFIGURACIÓN PBR ===")
    setup_scene()
    mats = create_shaders()

    print("=== [2/4] MODELANDO MESA DE CRAFTEO SCI-FI ===")
    bench_obj, vortex_obj, holo_obj = build_crafting_bench(mats)

    cam_data = bpy.data.cameras.new("Cam_Workbench")
    cam_obj = bpy.data.objects.new("Cam_Workbench", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    print("=== [3/4] RENDERIZANDO LAS 4 VISTAS CANÓNICAS ===")
    # 1. Hero 3/4 Perspective (Ángulo de referencia exacto)
    v_hero = render_shot(cam_obj, (2.2, -2.3, 1.85), (0.05, 0.05, 0.82), 43, "bench_hero_3quarter.png")

    # 2. Top-Down Surface View (Cenital de la superficie de trabajo y vórtice)
    v_top = render_shot(cam_obj, (0.05, -0.05, 3.1), (0.05, 0.0, 0.82), 34, "bench_top_surface.png")

    # 3. Frontal Ergonomic View (Nivel del operador)
    v_front = render_shot(cam_obj, (0.0, -2.7, 0.92), (0.0, 0.0, 0.78), 40, "bench_front_ergonomic.png")

    # 4. Close-Up Holo-HUD & Vortex View (Detalle de holograma y remolino)
    v_close = render_shot(cam_obj, (1.05, -0.85, 1.30), (0.22, 0.18, 0.96), 36, "bench_closeup_holo.png")

    # Guardar archivo .blend maestro
    os.makedirs(os.path.dirname(MASTER_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=MASTER_BLEND)
    print(f"ARCHIVO .BLEND MAESTRO GUARDADO: {MASTER_BLEND}")
    print("=== RENDERIZADO COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    main()
