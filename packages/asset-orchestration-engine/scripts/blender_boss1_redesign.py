import bpy
import bmesh
import math
from mathutils import Matrix, Vector, Euler
import os

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = bpy.data.collections.new("DARX_Boss1_V2")
scene.collection.children.link(col)

def create_pbr_mat(name, rgb, rough=0.35, metal=0.85, emis_rgb=None, emis_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if emis_rgb:
            for em_col_name in ["Emission Color", "Emission"]:
                if em_col_name in bsdf.inputs:
                    bsdf.inputs[em_col_name].default_value = (*emis_rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emis_str
    return mat

m_armor_white = create_pbr_mat("M_Mecha_CeramicWhite", (0.90, 0.91, 0.94), rough=0.25, metal=0.10)
m_chassis_dark = create_pbr_mat("M_Mecha_ChassisDark", (0.06, 0.065, 0.08), rough=0.45, metal=0.80)
m_steel_machined = create_pbr_mat("M_Mecha_HydraulicSteel", (0.45, 0.48, 0.54), rough=0.18, metal=0.95)
m_core_crimson = create_pbr_mat("M_Mecha_CoreCrimson", (1.0, 0.01, 0.0), rough=0.10, metal=0.0, emis_rgb=(1.0, 0.01, 0.0), emis_str=10.0)
# SOLID SATURATED BLOOD RED VISOR
m_visor_crimson = create_pbr_mat("M_Mecha_VisorCrimson", (0.98, 0.0, 0.0), rough=0.05, metal=0.0, emis_rgb=(1.0, 0.0, 0.0), emis_str=2.2)
m_accent_red = create_pbr_mat("M_Mecha_AccentRed", (0.92, 0.02, 0.01), rough=0.30, metal=0.20, emis_rgb=(0.92, 0.02, 0.01), emis_str=0.8)

def add_box(bm, size, loc, rot=(0,0,0)):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1.0))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

def add_cylinder(bm, r, depth, loc, rot=(0,0,0), seg=16):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    return bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth, matrix=mat)

mesh = bpy.data.meshes.new("SK_Robot_Contencion_V2_Mesh")
obj = bpy.data.objects.new("SK_Robot_Contencion_V2", mesh)
col.objects.link(obj)

obj.data.materials.append(m_armor_white)      # 0
obj.data.materials.append(m_chassis_dark)      # 1
obj.data.materials.append(m_steel_machined)    # 2
obj.data.materials.append(m_core_crimson)      # 3
obj.data.materials.append(m_visor_crimson)     # 4
obj.data.materials.append(m_accent_red)        # 5

bm = bmesh.new()

def tag(old_count, mat_idx):
    for f in bm.faces[old_count:]:
        f.material_index = mat_idx

# 1. PELVIS & WAIST
fc = len(bm.faces)
add_box(bm, (0.52, 0.42, 0.24), (0, -0.02, 0.92))
tag(fc, 1)

fc = len(bm.faces)
add_box(bm, (0.36, 0.18, 0.22), (0, -0.22, 0.88), rot=(math.radians(18), 0, 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.12, 0.03, 0.10), (0, -0.32, 0.88), rot=(math.radians(18), 0, 0))
tag(fc, 5)

fc = len(bm.faces)
add_cylinder(bm, 0.28, 0.10, (0, -0.02, 1.06), seg=24)
tag(fc, 2)

# 2. TORSO & CHASSIS
fc = len(bm.faces)
add_box(bm, (0.76, 0.54, 0.62), (0, 0.02, 1.42))
tag(fc, 1)

fc = len(bm.faces)
add_box(bm, (0.84, 0.44, 0.18), (0, -0.08, 1.72))
tag(fc, 0)

for side in [1.0, -1.0]:
    fc = len(bm.faces)
    add_box(bm, (0.24, 0.48, 0.40), (side * 0.36, -0.12, 1.42), rot=(0, math.radians(-12 * side), 0))
    tag(fc, 0)

for vz in [1.30, 1.38, 1.46, 1.54, 1.62]:
    fc = len(bm.faces)
    add_box(bm, (0.52, 0.08, 0.04), (0, 0.32, vz))
    tag(fc, 2)

# 3. GLOWING CRIMSON PLASMA REACTOR CORE
fc = len(bm.faces)
add_cylinder(bm, 0.20, 0.22, (0, -0.06, 1.42), rot=(math.radians(90), 0, 0), seg=24)
tag(fc, 1)

fc = len(bm.faces)
bmesh.ops.create_icosphere(bm, subdivisions=3, radius=0.14, matrix=Matrix.Translation((0, -0.10, 1.42)))
tag(fc, 3)

for ang in [0, 60, 120, 180, 240, 300]:
    fc = len(bm.faces)
    rad = math.radians(ang)
    px = 0.16 * math.cos(rad)
    pz = 1.42 + 0.16 * math.sin(rad)
    add_box(bm, (0.04, 0.10, 0.04), (px, -0.14, pz))
    tag(fc, 2)

# 4. BLAST DOORS WITH VIBRANT RED CHEVRONS
fc = len(bm.faces)
add_box(bm, (0.19, 0.06, 0.36), (-0.16, -0.28, 1.42), rot=(0, math.radians(30), 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.14, 0.03, 0.09), (-0.16, -0.32, 1.42), rot=(0, math.radians(30), 0))
tag(fc, 5)

fc = len(bm.faces)
add_box(bm, (0.19, 0.06, 0.36), (0.16, -0.28, 1.42), rot=(0, math.radians(-30), 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.14, 0.03, 0.09), (0.16, -0.32, 1.42), rot=(0, math.radians(-30), 0))
tag(fc, 5)

fc = len(bm.faces)
add_box(bm, (0.06, 0.04, 0.16), (0, -0.26, 1.42))
tag(fc, 3)

# 5. HEAD & SOLID PURE RED VISOR
fc = len(bm.faces)
add_box(bm, (0.42, 0.36, 0.22), (0, -0.14, 1.88), rot=(math.radians(10), 0, 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.36, 0.12, 0.12), (0, -0.28, 1.88), rot=(math.radians(10), 0, 0))
tag(fc, 1)

# Solid Crimson Red Visor (Matches exact red)
fc = len(bm.faces)
add_box(bm, (0.32, 0.04, 0.07), (0, -0.33, 1.89), rot=(math.radians(10), 0, 0))
tag(fc, 4)

# Comm mast
fc = len(bm.faces)
add_cylinder(bm, 0.015, 0.32, (0.16, 0.02, 2.08), seg=8)
tag(fc, 2)

fc = len(bm.faces)
bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.025, matrix=Matrix.Translation((0.16, 0.02, 2.24)))
tag(fc, 5)

# 6. HEAVY ARMS & BATTERING RAM FISTS
for side, sx in [(1.0, 1.0), (-1.0, -1.0)]:
    bx = 0.58 * sx
    
    fc = len(bm.faces)
    add_box(bm, (0.34, 0.52, 0.28), (bx, -0.06, 1.68), rot=(0, math.radians(18 * sx), math.radians(-8 * sx)))
    tag(fc, 0)

    fc = len(bm.faces)
    add_box(bm, (0.36, 0.08, 0.29), (bx, -0.06, 1.68), rot=(0, math.radians(18 * sx), math.radians(-8 * sx)))
    tag(fc, 5)

    fc = len(bm.faces)
    add_cylinder(bm, 0.12, 0.26, (bx - 0.06 * sx, -0.06, 1.58), rot=(math.radians(90), 0, 0), seg=16)
    tag(fc, 2)

    fc = len(bm.faces)
    add_box(bm, (0.24, 0.28, 0.40), (bx + 0.06 * sx, -0.08, 1.40), rot=(math.radians(8), math.radians(6 * sx), 0))
    tag(fc, 1)

    fc = len(bm.faces)
    add_cylinder(bm, 0.045, 0.36, (bx, 0.04, 1.40), seg=12)
    tag(fc, 2)

    fc = len(bm.faces)
    add_cylinder(bm, 0.12, 0.24, (bx + 0.08 * sx, -0.12, 1.16), rot=(0, math.radians(90), 0), seg=16)
    tag(fc, 1)

    fc = len(bm.faces)
    add_box(bm, (0.28, 0.34, 0.44), (bx + 0.10 * sx, -0.18, 0.94), rot=(math.radians(-10), 0, 0))
    tag(fc, 1)

    fc = len(bm.faces)
    add_box(bm, (0.30, 0.14, 0.38), (bx + 0.10 * sx, -0.32, 0.94), rot=(math.radians(-15), 0, 0))
    tag(fc, 0)

    fc = len(bm.faces)
    add_box(bm, (0.28, 0.30, 0.24), (bx + 0.10 * sx, -0.24, 0.68))
    tag(fc, 2)

    for off in [-0.08, 0.0, 0.08]:
        fc = len(bm.faces)
        add_box(bm, (0.06, 0.10, 0.18), (bx + 0.10 * sx + off, -0.38, 0.68), rot=(math.radians(15), 0, 0))
        tag(fc, 1)

# 7. LEGS
for side, sx in [(1.0, 1.0), (-1.0, -1.0)]:
    lx = 0.34 * sx

    fc = len(bm.faces)
    add_cylinder(bm, 0.11, 0.24, (lx * 0.75, -0.02, 0.88), rot=(0, math.radians(90), 0), seg=16)
    tag(fc, 2)

    fc = len(bm.faces)
    add_box(bm, (0.26, 0.32, 0.42), (lx, -0.02, 0.68), rot=(0, math.radians(4 * sx), 0))
    tag(fc, 0)

    fc = len(bm.faces)
    add_cylinder(bm, 0.045, 0.36, (lx, 0.12, 0.68), seg=12)
    tag(fc, 2)

    fc = len(bm.faces)
    add_box(bm, (0.28, 0.32, 0.18), (lx, -0.04, 0.48))
    tag(fc, 1)

    fc = len(bm.faces)
    add_cylinder(bm, 0.035, 0.24, (lx + 0.11 * sx, -0.04, 0.48), rot=(math.radians(90), 0, 0), seg=12)
    tag(fc, 2)

    fc = len(bm.faces)
    add_box(bm, (0.28, 0.34, 0.40), (lx, -0.05, 0.28))
    tag(fc, 1)

    fc = len(bm.faces)
    add_box(bm, (0.26, 0.14, 0.36), (lx, -0.20, 0.28), rot=(math.radians(-12), 0, 0))
    tag(fc, 0)

    fc = len(bm.faces)
    add_box(bm, (0.16, 0.04, 0.10), (lx, -0.28, 0.36), rot=(math.radians(-12), 0, 0))
    tag(fc, 5)

    fc = len(bm.faces)
    add_box(bm, (0.34, 0.48, 0.12), (lx, -0.10, 0.06))
    tag(fc, 1)

    for fx_off in [-0.10, 0.0, 0.10]:
        fc = len(bm.faces)
        add_box(bm, (0.07, 0.16, 0.08), (lx + fx_off, -0.32, 0.04), rot=(math.radians(10), 0, 0))
        tag(fc, 2)

bm.to_mesh(mesh)
bm.free()
mesh.update()

bev = obj.modifiers.new("Bevel", type='BEVEL')
bev.width = 0.010
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35)

# --------------------------------------------------------------------------
# LIGHTING & CAMERA (Dark studio background)
# --------------------------------------------------------------------------

if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs["Strength"].default_value = 0.8

cam_data = bpy.data.cameras.new("Cam_Boss1_V2")
cam_obj = bpy.data.objects.new("Cam_Boss1_V2", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss1_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.08, -0.09, 0.96)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.6
cam_obj.location = (0.08 + dist * 0.65, -0.09 - dist * 0.85, 0.96 + dist * 0.30)

key_data = bpy.data.lights.new("Light_Key", type='AREA')
key_obj = bpy.data.objects.new("Light_Key", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 250.0
key_data.size = 3.5
key_data.color = (1.0, 0.98, 0.95)
key_obj.location = (2.8, -2.8, 3.8)

fill_data = bpy.data.lights.new("Light_Fill", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 80.0
fill_data.size = 4.0
fill_data.color = (0.65, 0.75, 0.90)
fill_obj.location = (-2.8, -2.8, 2.2)

rim_data = bpy.data.lights.new("Light_Rim", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 200.0
rim_data.size = 3.0
rim_data.color = (0.80, 0.40, 1.0)
rim_obj.location = (-0.5, 3.5, 2.8)

out_despues = os.path.join(output_dir, "boss1_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED BOSS 1 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss1_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")
