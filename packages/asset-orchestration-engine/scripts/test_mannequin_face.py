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

col = bpy.data.collections.new("Test_Head")
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

m_white = create_pbr_mat("M_WhiteMannequin", (0.93, 0.94, 0.96), rough=0.20, metal=0.05)
m_cyan = create_pbr_mat("M_Cyan", (0.0, 0.95, 1.0), rough=0.05, metal=0.0, emis_rgb=(0.0, 0.95, 1.0), emis_str=20.0)
m_magenta = create_pbr_mat("M_Magenta", (1.0, 0.02, 0.45), rough=0.05, metal=0.0, emis_rgb=(1.0, 0.02, 0.45), emis_str=20.0)
m_core_w = create_pbr_mat("M_CoreW", (1.0, 1.0, 1.0), rough=0.05, metal=0.0, emis_rgb=(1.0, 1.0, 1.0), emis_str=30.0)

mesh = bpy.data.meshes.new("Test_Mannequin_Head_Mesh")
obj = bpy.data.objects.new("Test_Mannequin_Head", mesh)
col.objects.link(obj)

obj.data.materials.append(m_white)  # 0
obj.data.materials.append(m_cyan)   # 1
obj.data.materials.append(m_magenta)# 2
obj.data.materials.append(m_core_w) # 3

bm = bmesh.new()

def tag(old_count, mat_idx):
    for f in bm.faces[old_count:]:
        f.material_index = mat_idx

# 1. CRANIUM (Human skull proportions: elongated back, narrow front)
fc = len(bm.faces)
bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=24, radius=0.10,
                          matrix=Matrix.Translation((0, 0.015, 1.76)) @ Matrix.Diagonal((1.0, 1.25, 1.30, 1.0)))
tag(fc, 0)

# 2. FOREHEAD & BROW
fc = len(bm.faces)
mat_brow = Matrix.Translation((0, -0.075, 1.80)) @ Matrix.Rotation(math.radians(-10), 4, 'X') @ Matrix.Diagonal((0.095, 0.045, 0.035, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, matrix=mat_brow)
tag(fc, 0)

# 3. NOSE (Sculpted human mannequin nose)
# Bridge
fc = len(bm.faces)
mat_bridge = Matrix.Translation((0, -0.098, 1.75)) @ Matrix.Rotation(math.radians(-20), 4, 'X') @ Matrix.Diagonal((0.014, 0.030, 0.055, 1.0))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_bridge)
tag(fc, 0)

# Nose tip (Subtle rounded dome)
fc = len(bm.faces)
mat_tip = Matrix.Translation((0, -0.125, 1.72)) @ Matrix.Diagonal((0.018, 0.022, 0.016, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_tip)
tag(fc, 0)

# Nostrils
for side in [1.0, -1.0]:
    fc = len(bm.faces)
    mat_nostril = Matrix.Translation((side * 0.016, -0.114, 1.715)) @ Matrix.Diagonal((0.010, 0.014, 0.010, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_nostril)
    tag(fc, 0)

# 4. EYES & ORBITS (Almond closed eyelids of classic mannequin)
for side in [1.0, -1.0]:
    # Orbit indent
    fc = len(bm.faces)
    mat_orbit = Matrix.Translation((side * 0.045, -0.082, 1.765)) @ Matrix.Rotation(math.radians(8), 4, 'X') @ Matrix.Diagonal((0.025, 0.020, 0.018, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_orbit)
    tag(fc, 0)

    # Stylized eyelid almond shape
    fc = len(bm.faces)
    mat_lid = Matrix.Translation((side * 0.045, -0.092, 1.765)) @ Matrix.Diagonal((0.024, 0.012, 0.010, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_lid)
    tag(fc, 0)

    # Subtle mannequin closed eye slit
    fc = len(bm.faces)
    mat_crease = Matrix.Translation((side * 0.045, -0.098, 1.765)) @ Matrix.Diagonal((0.022, 0.004, 0.002, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_crease)
    tag(fc, 0)

# 5. CHEEKBONES & TEMPLES
for side in [1.0, -1.0]:
    fc = len(bm.faces)
    mat_cheek = Matrix.Translation((side * 0.065, -0.065, 1.72)) @ Matrix.Rotation(math.radians(12), 4, 'X') @ Matrix.Rotation(math.radians(-10 * side), 4, 'Z') @ Matrix.Diagonal((0.035, 0.045, 0.040, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_cheek)
    tag(fc, 0)

# 6. LIPS / MOUTH
# Upper lip (Cupid's bow)
fc = len(bm.faces)
mat_ulip = Matrix.Translation((0, -0.108, 1.678)) @ Matrix.Diagonal((0.035, 0.015, 0.010, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_ulip)
tag(fc, 0)

# Lower lip
fc = len(bm.faces)
mat_llip = Matrix.Translation((0, -0.105, 1.662)) @ Matrix.Diagonal((0.032, 0.016, 0.011, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_llip)
tag(fc, 0)

# Mouth seam line
fc = len(bm.faces)
mat_mseam = Matrix.Translation((0, -0.112, 1.670)) @ Matrix.Diagonal((0.038, 0.005, 0.002, 1.0))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_mseam)
tag(fc, 0)

# 7. CHIN & JAWLINE
fc = len(bm.faces)
mat_chin = Matrix.Translation((0, -0.095, 1.625)) @ Matrix.Diagonal((0.032, 0.035, 0.026, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_chin)
tag(fc, 0)

# Jawline sweep
for side in [1.0, -1.0]:
    fc = len(bm.faces)
    mat_jaw = Matrix.Translation((side * 0.042, -0.045, 1.645)) @ Matrix.Rotation(math.radians(-25), 4, 'X') @ Matrix.Rotation(math.radians(-18 * side), 4, 'Z') @ Matrix.Diagonal((0.024, 0.060, 0.024, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_jaw)
    tag(fc, 0)

# 8. SUBTLE GLITCH CRACK / RIFT ACROSS FACE (Thin hairline fissure that reveals the energy inside WITHOUT obscuring the face)
# Thin cyan crack down left side of face
fc = len(bm.faces)
mat_crack_c = Matrix.Translation((-0.008, -0.126, 1.74)) @ Matrix.Rotation(math.radians(3), 4, 'Y') @ Matrix.Diagonal((0.003, 0.015, 0.24, 1.0))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_crack_c)
tag(fc, 1)

# Thin white core crack
fc = len(bm.faces)
mat_crack_w = Matrix.Translation((0.0, -0.127, 1.74)) @ Matrix.Diagonal((0.002, 0.016, 0.24, 1.0))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_crack_w)
tag(fc, 3)

# Thin magenta crack down right side of face
fc = len(bm.faces)
mat_crack_m = Matrix.Translation((0.008, -0.126, 1.74)) @ Matrix.Rotation(math.radians(-3), 4, 'Y') @ Matrix.Diagonal((0.003, 0.015, 0.24, 1.0))
bmesh.ops.create_cube(bm, size=1.0, matrix=mat_crack_m)
tag(fc, 2)

# Broken halo porcelain shards above head
halo_shards = [
    ((-0.12,  0.02, 1.94), (math.radians(15), math.radians(25), math.radians(-20))),
    (( 0.12,  0.02, 1.94), (math.radians(15), -math.radians(25), math.radians(20))),
    (( 0.00,  0.12, 1.96), (math.radians(-25), 0, 0)),
]
for loc, rot in halo_shards:
    fc = len(bm.faces)
    mat_sh = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((0.03, 0.03, 0.09, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat_sh)
    tag(fc, 0)

bm.to_mesh(mesh)
bm.free()
mesh.update()

# Set smooth shading
for p in mesh.polygons:
    p.use_smooth = True

# Studio Lighting & Camera for Test
if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs["Strength"].default_value = 0.8

cam_data = bpy.data.cameras.new("Cam_Test")
cam_obj = bpy.data.objects.new("Cam_Test", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 65.0

empty = bpy.data.objects.new("Target", None)
scene.collection.objects.link(empty)
empty.location = (0, -0.06, 1.73)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'
cam_obj.location = (0.35, -0.85, 1.80)

key_data = bpy.data.lights.new("Light_Key", type='AREA')
key_obj = bpy.data.objects.new("Light_Key", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 180.0
key_data.size = 2.0
key_obj.location = (1.5, -1.8, 2.5)

fill_data = bpy.data.lights.new("Light_Fill", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 70.0
fill_data.size = 3.0
fill_data.color = (0.0, 0.85, 1.0)
fill_obj.location = (-1.5, -1.5, 1.8)

rim_data = bpy.data.lights.new("Light_Rim", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 160.0
rim_data.size = 2.0
rim_data.color = (1.0, 0.05, 0.60)
rim_obj.location = (-0.3, 1.5, 2.2)

out_test = os.path.join(output_dir, "test_mannequin_face.png")
scene.render.filepath = out_test
bpy.ops.render.render(write_still=True)
print(f"RENDERED TEST FACE -> {out_test}")
