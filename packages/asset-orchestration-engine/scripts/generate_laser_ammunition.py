# -*- coding: utf-8 -*-
"""generate_laser_ammunition.py
Genera las 4 mallas dedicadas de municion laser/plasma para DarX:
1. SM_Ammo_ApexCell: Micro-celda cilindrica de plasma ionico para la Pistola Apex 6.
2. SM_Ammo_PhaseDrum: Tambor toroidal ciclonico con pantalla digital para el Subfusil Phase SMG.
3. SM_Ammo_BreacherSlug: Celula termica cuadruple de alta presion para la Escopeta Breacher S4.
4. SM_Ammo_VanguardPack: Bateria angular en cuna (16 deg) con 3 LEDs para el Rifle Vanguard AR.

Exporta a Art/FBX/Weapons/Ammunition/ y genera un render de 4 cuadrantes para aprobacion visual previa (Reglas 4 y 5 de AGENTS.md).
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

PROJECT_ROOT = r"E:\Darx_Proyect"
OUTPUT_FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Weapons", "Ammunition")
os.makedirs(OUTPUT_FBX_DIR, exist_ok=True)

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
RENDER_OUT = os.path.join(BRAIN_DIR, "preview_laser_ammunition.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ==============================================================================
# 1. SHADERS PBR (TITANIO INDIGO, CRISTAL DE CUARZO, PLASMA VIOLETA, CROMO)
# ==============================================================================
def create_material(name, base_col, roughness, metallic, emissive_col=(0,0,0,1), emissive_str=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_col
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if transmission > 0.0:
            bsdf.inputs['Transmission Weight'].default_value = transmission
            bsdf.inputs['IOR'].default_value = 1.48
        if emissive_str > 0.0:
            bsdf.inputs['Emission Color'].default_value = emissive_col
            bsdf.inputs['Emission Strength'].default_value = emissive_str
    return mat

mat_chassis = create_material("M_Ammo_IndigoChassis", (0.04, 0.03, 0.08, 1.0), 0.25, 0.90)
mat_gunmetal = create_material("M_Ammo_Gunmetal", (0.03, 0.035, 0.04, 1.0), 0.30, 0.85)
mat_chrome = create_material("M_Ammo_Chrome", (0.80, 0.82, 0.85, 1.0), 0.10, 0.98)
mat_glass = create_material("M_Ammo_QuartzGlass", (0.95, 0.92, 1.0, 1.0), 0.05, 0.0, transmission=0.95)
mat_plasma = create_material("M_Ammo_PlasmaViolet", (0.85, 0.20, 1.0, 1.0), 0.15, 0.0, emissive_col=(0.88, 0.25, 1.0, 1.0), emissive_str=18.0)
mat_screen = create_material("M_Ammo_Display", (0.05, 0.15, 0.40, 1.0), 0.20, 0.0, emissive_col=(0.10, 0.60, 1.0, 1.0), emissive_str=9.0)

def apply_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def make_box(name, center, size, chamfer=0.0015, col=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    if col:
        col.objects.link(obj)
    else:
        scene.collection.objects.link(obj)
    if chamfer > 0.0003:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = chamfer
        bev.segments = 2
    return obj

def make_cylinder(name, center, radius, depth, rot_euler=(0,0,0), vertices=32, col=None):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=vertices, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    obj.rotation_euler = rot_euler
    if col:
        col.objects.link(obj)
    else:
        scene.collection.objects.link(obj)
    return obj

# ==============================================================================
# 2. MODELADO DE CADA TIPO DE MUNICION LASER
# ==============================================================================

# --- A. APEX CELL (Micro-celda cilindrica de plasma para Pistola Apex 6) ---
col_apex = bpy.data.collections.new("Col_ApexCell")
scene.collection.children.link(col_apex)

c_body = make_cylinder("ApexCell_Body", (0, 0, 0.05), radius=0.014, depth=0.10, rot_euler=(0,0,0), vertices=32, col=col_apex)
apply_mat(c_body, mat_chassis)

c_glass = make_cylinder("ApexCell_Glass", (0, 0, 0.05), radius=0.0125, depth=0.055, rot_euler=(0,0,0), vertices=32, col=col_apex)
apply_mat(c_glass, mat_glass)

c_plasma = make_cylinder("ApexCell_Plasma", (0, 0, 0.05), radius=0.0055, depth=0.050, rot_euler=(0,0,0), vertices=16, col=col_apex)
apply_mat(c_plasma, mat_plasma)

c_cap_top = make_cylinder("ApexCell_CapTop", (0, 0, 0.098), radius=0.0145, depth=0.006, rot_euler=(0,0,0), vertices=32, col=col_apex)
apply_mat(c_cap_top, mat_chrome)

c_pin = make_cylinder("ApexCell_Pin", (0, 0, 0.103), radius=0.005, depth=0.005, rot_euler=(0,0,0), vertices=16, col=col_apex)
apply_mat(c_pin, mat_chrome)

c_cap_bot = make_cylinder("ApexCell_CapBot", (0, 0, 0.002), radius=0.0145, depth=0.006, rot_euler=(0,0,0), vertices=32, col=col_apex)
apply_mat(c_cap_bot, mat_gunmetal)

c_led_ring = make_cylinder("ApexCell_LEDRing", (0, 0, 0.006), radius=0.0147, depth=0.002, rot_euler=(0,0,0), vertices=32, col=col_apex)
apply_mat(c_led_ring, mat_plasma)


# --- B. PHASE DRUM (Tambor toroidal con display digital para Subfusil Phase SMG) ---
col_drum = bpy.data.collections.new("Col_PhaseDrum")
scene.collection.children.link(col_drum)

d_main = make_cylinder("PhaseDrum_Main", (0, 0, 0.024), radius=0.075, depth=0.046, rot_euler=(0,0,0), vertices=48, col=col_drum)
apply_mat(d_main, mat_chassis)

d_rim = make_cylinder("PhaseDrum_Rim", (0, 0, 0.024), radius=0.077, depth=0.038, rot_euler=(0,0,0), vertices=48, col=col_drum)
apply_mat(d_rim, mat_gunmetal)

d_hub = make_cylinder("PhaseDrum_Hub", (0, 0, 0.024), radius=0.020, depth=0.050, rot_euler=(0,0,0), vertices=32, col=col_drum)
apply_mat(d_hub, mat_chrome)

d_tower = make_box("PhaseDrum_Tower", (0, 0.070, 0.024), (0.040, 0.045, 0.044), chamfer=0.002, col=col_drum)
apply_mat(d_tower, mat_gunmetal)

d_tower_pins = make_cylinder("PhaseDrum_TowerPins", (0, 0.088, 0.024), radius=0.008, depth=0.012, rot_euler=(math.radians(90), 0, 0), vertices=16, col=col_drum)
apply_mat(d_tower_pins, mat_chrome)

d_screen = make_box("PhaseDrum_Display", (0, -0.052, 0.048), (0.028, 0.020, 0.003), chamfer=0.0005, col=col_drum)
apply_mat(d_screen, mat_screen)

d_arc_ring1 = make_cylinder("PhaseDrum_ArcRing1", (0, 0, 0.0475), radius=0.062, depth=0.002, rot_euler=(0,0,0), vertices=40, col=col_drum)
apply_mat(d_arc_ring1, mat_plasma)
d_arc_ring2 = make_cylinder("PhaseDrum_ArcRing2", (0, 0, 0.0475), radius=0.044, depth=0.002, rot_euler=(0,0,0), vertices=32, col=col_drum)
apply_mat(d_arc_ring2, mat_plasma)


# --- C. BREACHER SLUG (Celula termica cuadruple para Escopeta Breacher S4) ---
col_slug = bpy.data.collections.new("Col_BreacherSlug")
scene.collection.children.link(col_slug)

s_housing = make_box("BreacherSlug_Housing", (0, 0, 0.065), (0.046, 0.046, 0.130), chamfer=0.003, col=col_slug)
apply_mat(s_housing, mat_chassis)

quad_offsets = [(-0.013, -0.013), (0.013, -0.013), (-0.013, 0.013), (0.013, 0.013)]
for idx, (qx, qy) in enumerate(quad_offsets):
    v_glass = make_cylinder(f"BreacherSlug_Glass_{idx}", (qx, qy, 0.065), radius=0.008, depth=0.090, rot_euler=(0,0,0), vertices=20, col=col_slug)
    apply_mat(v_glass, mat_glass)
    v_core = make_cylinder(f"BreacherSlug_Core_{idx}", (qx, qy, 0.065), radius=0.0035, depth=0.082, rot_euler=(0,0,0), vertices=12, col=col_slug)
    apply_mat(v_core, mat_plasma)

s_front_collar = make_box("BreacherSlug_FrontCollar", (0, 0, 0.125), (0.048, 0.048, 0.014), chamfer=0.0015, col=col_slug)
apply_mat(s_front_collar, mat_gunmetal)

s_nozzles = make_cylinder("BreacherSlug_Nozzles", (0, 0, 0.134), radius=0.020, depth=0.006, rot_euler=(0,0,0), vertices=24, col=col_slug)
apply_mat(s_nozzles, mat_chrome)

s_rear_handle = make_box("BreacherSlug_RearHandle", (0, 0, 0.004), (0.044, 0.044, 0.010), chamfer=0.0015, col=col_slug)
apply_mat(s_rear_handle, mat_gunmetal)

s_led_stripe = make_box("BreacherSlug_LEDStripe", (0.024, 0, 0.065), (0.002, 0.026, 0.075), chamfer=0.0004, col=col_slug)
apply_mat(s_led_stripe, mat_plasma)


# --- D. VANGUARD PACK (Petaca angular en cuna a 16 deg con 3 LEDs para Rifle Vanguard AR) ---
col_pack = bpy.data.collections.new("Col_VanguardPack")
scene.collection.children.link(col_pack)

bm_vp = bmesh.new()
bmesh.ops.create_cube(bm_vp, size=1.0)
bmesh.ops.scale(bm_vp, vec=(0.036, 0.065, 0.160), verts=bm_vp.verts)
bmesh.ops.translate(bm_vp, vec=(0, 0, 0.080), verts=bm_vp.verts)
for v in bm_vp.verts:
    v.co.y += (v.co.z * math.tan(math.radians(16)))
mesh_vp = bpy.data.meshes.new("VanguardPack_Mesh")
bm_vp.to_mesh(mesh_vp)
bm_vp.free()
vp_main = bpy.data.objects.new("VanguardPack_Main", mesh_vp)
col_pack.objects.link(vp_main)
bev_vp = vp_main.modifiers.new("Bevel", 'BEVEL')
bev_vp.width = 0.0025
apply_mat(vp_main, mat_chassis)

for s_x in [-0.019, 0.019]:
    vp_plate = make_box(f"VanguardPack_Plate_{s_x}", (s_x, 0.022, 0.080), (0.002, 0.055, 0.120), chamfer=0.001, col=col_pack)
    vp_plate.rotation_euler = (math.radians(-16), 0, 0)
    apply_mat(vp_plate, mat_gunmetal)

vp_top_lip = make_box("VanguardPack_TopLip", (0, 0.046, 0.160), (0.034, 0.045, 0.015), chamfer=0.001, col=col_pack)
vp_top_lip.rotation_euler = (math.radians(-16), 0, 0)
apply_mat(vp_top_lip, mat_chrome)

for i_led, z_led in enumerate([0.060, 0.080, 0.100]):
    y_l = z_led * math.tan(math.radians(16))
    led_d = make_cylinder(f"VanguardPack_LED_{i_led}", (0.0195, y_l - 0.018, z_led), radius=0.0025, depth=0.002, rot_euler=(0, math.radians(90), 0), vertices=16, col=col_pack)
    apply_mat(led_d, mat_plasma)


# ==============================================================================
# 3. EXPORTACION ATOMICA DE CADA ASSET A FBX
# ==============================================================================
ammo_configs = [
    ("SM_Ammo_ApexCell.fbx", col_apex),
    ("SM_Ammo_PhaseDrum.fbx", col_drum),
    ("SM_Ammo_BreacherSlug.fbx", col_slug),
    ("SM_Ammo_VanguardPack.fbx", col_pack)
]

for fbx_name, col in ammo_configs:
    fbx_path = os.path.join(OUTPUT_FBX_DIR, fbx_name)
    for o in bpy.data.objects:
        o.select_set(False)
    for o in col.objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = col.objects[0]
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        bake_space_transform=False,
        object_types={'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False
    )
    print(f"[OK] Exportado asset de municion: {fbx_path} ({os.path.getsize(fbx_path)} bytes)")


# ==============================================================================
# 4. RENDER DE VERIFICACION VISUAL (REGLAS 4 Y 5)
# ==============================================================================
# Espaciado horizontal y rotacion 3/4 de cada elemento
for o in col_apex.objects:
    o.location.x -= 0.22
    o.rotation_euler.z = math.radians(25)

for o in col_drum.objects:
    o.location.x -= 0.08
    o.rotation_euler.x = math.radians(-30)
    o.rotation_euler.z = math.radians(20)
    o.location.z += 0.02

for o in col_slug.objects:
    o.location.x += 0.08
    o.rotation_euler.z = math.radians(-25)

for o in col_pack.objects:
    o.location.x += 0.24
    o.rotation_euler.z = math.radians(-35)

podium = make_box("Ammo_DisplayPodium", (0, 0, -0.015), (0.65, 0.35, 0.025), chamfer=0.003)
apply_mat(podium, mat_chassis)

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

world = bpy.data.worlds.new("World_AmmoPreview")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

def add_light(name, l_type, loc, energy, col=(1,1,1)):
    l_data = bpy.data.lights.new(name, l_type)
    l_data.energy = energy
    l_data.color = col
    l_obj = bpy.data.objects.new(name, l_data)
    l_obj.location = loc
    scene.collection.objects.link(l_obj)
    return l_obj

add_light("KeyLight", 'AREA', (0.35, -0.65, 0.60), 65.0, (1.0, 0.95, 0.90))
add_light("FillLight", 'AREA', (-0.45, -0.55, 0.50), 35.0, (0.75, 0.85, 1.0))
add_light("RimLight", 'AREA', (0.0, 0.60, 0.45), 55.0, (0.85, 0.40, 1.0))
add_light("PurpleGlow", 'POINT', (0.0, 0.0, 0.12), 12.0, (0.80, 0.20, 1.0))

cam_data = bpy.data.cameras.new("Cam_AmmoPreview")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("Cam_AmmoPreview", cam_data)
cam_obj.location = (0.0, -0.82, 0.38)
cam_obj.rotation_euler = (math.radians(68), 0, 0)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.filepath = RENDER_OUT
bpy.ops.render.render(write_still=True)
print(f"[OK] Render de verificacion guardado en: {RENDER_OUT}")
