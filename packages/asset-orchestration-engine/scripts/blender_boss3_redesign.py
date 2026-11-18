import bpy
import bmesh
import math
from mathutils import Matrix, Vector, Euler
import os

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = bpy.data.collections.new("DARX_Boss3_V2")
scene.collection.children.link(col)

# --------------------------------------------------------------------------
# MATERIALS (SINISTER TENEBROUS HORROR PALETTE: SCORCHED OBSIDIAN + BLOOD CRT + TOXIC VOLTAGE)
# --------------------------------------------------------------------------

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

# Pitch-black scorched heavy industrial iron
m_dark_chassis = create_pbr_mat("M_Matrix_ScorchedIron", (0.008, 0.008, 0.010), rough=0.40, metal=0.92)

# Abyssal smoked obsidian glass
m_glass_dark = create_pbr_mat("M_Matrix_ObsidianGlass", (0.004, 0.005, 0.007), rough=0.06, metal=0.60)

# Charred burned copper coil
m_copper_coil = create_pbr_mat("M_Matrix_CharredCopper", (0.40, 0.16, 0.06), rough=0.30, metal=0.90)

# INTENSE SINISTER BLOOD-RED CRT CATHODE (Deep menacing saturated crimson)
m_crt_blood = create_pbr_mat("M_Matrix_BloodCRT", (1.0, 0.005, 0.02), rough=0.08, metal=0.0, emis_rgb=(1.0, 0.005, 0.02), emis_str=28.0)

# SICKLY TOXIC PHOSPHOR HIGH-VOLTAGE
m_toxic_phosphor = create_pbr_mat("M_Matrix_ToxicPhosphor", (0.02, 1.0, 0.25), rough=0.08, metal=0.0, emis_rgb=(0.02, 1.0, 0.25), emis_str=26.0)

# SCORCHED DIELECTRIC INSULATORS (Replaced friendly white with burned dark slate/crimson)
m_insulator_scorched = create_pbr_mat("M_Matrix_ScorchedInsulator", (0.025, 0.015, 0.018), rough=0.25, metal=0.30)

# CURSED CATHODE SCREEN GLASS (Ultra-dark mirror with faint bloody tint)
m_crt_glass_dark = create_pbr_mat("M_Matrix_CurseGlass", (0.015, 0.008, 0.010), rough=0.05, metal=0.25)

# --------------------------------------------------------------------------
# GEOMETRY HELPERS
# --------------------------------------------------------------------------

def add_box(bm, size, loc, rot=(0,0,0)):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1.0))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

def add_cone(bm, r1, r2, depth, loc, rot=(0,0,0), seg=16):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    return bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=depth, matrix=mat)

def add_cylinder(bm, r, depth, loc, rot=(0,0,0), seg=16):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    return bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth, matrix=mat)

mesh = bpy.data.meshes.new("SK_Boss_StaticMatrix_V2_Mesh")
obj = bpy.data.objects.new("SK_Boss_StaticMatrix_V2", mesh)
col.objects.link(obj)

obj.data.materials.append(m_dark_chassis)       # 0
obj.data.materials.append(m_glass_dark)         # 1
obj.data.materials.append(m_copper_coil)        # 2
obj.data.materials.append(m_crt_blood)          # 3
obj.data.materials.append(m_toxic_phosphor)     # 4
obj.data.materials.append(m_insulator_scorched) # 5
obj.data.materials.append(m_crt_glass_dark)     # 6

bm = bmesh.new()

def tag(old_count, mat_idx):
    for f in bm.faces[old_count:]:
        f.material_index = mat_idx

# ==========================================================================
# 1. BASE: TESLA COIL SPECTRAL TAIL & ORBITAL SICKLE ELECTRODES
# ==========================================================================
fc = len(bm.faces)
add_box(bm, (0.34, 0.28, 0.16), (0, 0, 0.95))
tag(fc, 0)

for side in [1.0, -1.0]:
    fc = len(bm.faces)
    add_box(bm, (0.06, 0.30, 0.14), (side * 0.18, 0, 0.95))
    tag(fc, 5)

# Stepped Tesla Coil Tail
coil_tiers = [
    (0.80, 0.14, 0.11, 0.16),
    (0.64, 0.11, 0.08, 0.16),
    (0.48, 0.08, 0.05, 0.16),
    (0.32, 0.05, 0.02, 0.16),
]
for pz, r1, r2, h in coil_tiers:
    fc = len(bm.faces)
    add_cone(bm, r1, r2, h, (0, 0, pz), rot=(math.radians(180), 0, 0), seg=16)
    tag(fc, 0)
    # Intense blood red & toxic voltage rings
    fc = len(bm.faces)
    add_cylinder(bm, r1 * 1.15, 0.025, (0, 0, pz + h * 0.3), seg=16)
    tag(fc, 3 if pz > 0.6 else 4)
    # Charred copper winding
    fc = len(bm.faces)
    add_cylinder(bm, r1 * 1.08, 0.020, (0, 0, pz - h * 0.2), seg=16)
    tag(fc, 2)

# Sharp Tungsten Grounding Spike Tip (Glowing blood red)
fc = len(bm.faces)
add_cone(bm, 0.025, 0.002, 0.14, (0, 0, 0.18), rot=(math.radians(180), 0, 0), seg=8)
tag(fc, 3)

# 4 Floating Obsidian Daggers Orbiting the Tail
orbit_coords = [
    ((-0.24,  0.12, 0.46), (math.radians(25),  math.radians(30), math.radians(15)), 3),
    (( 0.24,  0.12, 0.46), (math.radians(25), -math.radians(30), math.radians(-15)), 3),
    (( 0.00, -0.26, 0.40), (math.radians(-35), 0,                 0),                 4),
    (( 0.00,  0.26, 0.40), (math.radians(35),  0,                 0),                 4),
]
for loc, rot, em_idx in orbit_coords:
    fc = len(bm.faces)
    add_box(bm, (0.05, 0.14, 0.26), loc, rot=rot)
    tag(fc, 1)
    fc = len(bm.faces)
    add_box(bm, (0.015, 0.025, 0.24), loc, rot=rot)
    tag(fc, em_idx)

# ==========================================================================
# 2. TORSO: SKELETAL CAGE & INTERNAL TESLA SPARK CORE
# ==========================================================================
fc = len(bm.faces)
add_box(bm, (0.16, 0.14, 0.40), (0, 0.04, 1.28))
tag(fc, 0)

# Central Radiant Blood-Red Spark Core (Tenebrous glowing heart)
fc = len(bm.faces)
add_cylinder(bm, 0.065, 0.36, (0, -0.02, 1.28), seg=16)
tag(fc, 3)

for cz in [1.14, 1.22, 1.30, 1.38, 1.44]:
    fc = len(bm.faces)
    add_cylinder(bm, 0.085, 0.020, (0, -0.02, cz), seg=16)
    tag(fc, 2)

# Demonic Scythe Chest Plates
fc = len(bm.faces)
add_box(bm, (0.18, 0.14, 0.24), (-0.13, -0.12, 1.40), rot=(math.radians(16), math.radians(-12), math.radians(-15)))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.18, 0.14, 0.24), (0.13, -0.12, 1.40), rot=(math.radians(16), math.radians(12), math.radians(15)))
tag(fc, 0)

# 4 Tiers of Curved Black Obsidian Ribs
rib_z = [1.16, 1.24, 1.32, 1.40]
for idx, rz in enumerate(rib_z):
    span_x = 0.20 - idx * 0.012
    for side, sx in [(1, 1), (-1, -1)]:
        fc = len(bm.faces)
        r_rot = (0, math.radians((22 - idx * 4) * sx), math.radians(12 * sx))
        add_box(bm, (0.04, 0.16, 0.045), (sx * span_x * 0.6, -0.08, rz), rot=r_rot)
        tag(fc, 1)
        # Intense fiery blood phosphor vein
        fc = len(bm.faces)
        add_box(bm, (0.015, 0.14, 0.018), (sx * span_x * 0.6, -0.09, rz), rot=r_rot)
        tag(fc, 3 if idx % 2 == 0 else 4)

for idx, spz in enumerate([1.24, 1.34, 1.44, 1.54]):
    fc = len(bm.faces)
    add_box(bm, (0.04, 0.14, 0.16 + idx * 0.04), (0, 0.18 + idx * 0.02, spz), rot=(math.radians(-28), 0, 0))
    tag(fc, 1)

# ==========================================================================
# 3. HEAD: TENEBROUS CRT DEMON & HORROR STATIC MASK
# ==========================================================================
fc = len(bm.faces)
add_box(bm, (0.38, 0.34, 0.30), (0, -0.02, 1.76), rot=(math.radians(14), 0, 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.42, 0.06, 0.32), (0, -0.17, 1.78), rot=(math.radians(14), 0, 0))
tag(fc, 0)

fc = len(bm.faces)
add_box(bm, (0.34, 0.03, 0.25), (0, -0.19, 1.78), rot=(math.radians(14), 0, 0))
tag(fc, 6)

# HORROR ANALOG DEMONIC FACE ON CRT SCREEN (Blood-Red Glitch Smile & Cursed Slit Eye)
# 1. Menacing Blood-Red Slit Eye
fc = len(bm.faces)
add_box(bm, (0.30, 0.015, 0.065), (0, -0.210, 1.82), rot=(math.radians(14), 0, 0))
tag(fc, 3)

# 2. Piercing Toxic Slit Pupil
fc = len(bm.faces)
add_box(bm, (0.025, 0.020, 0.14), (0, -0.215, 1.82), rot=(math.radians(14), 0, 0))
tag(fc, 4)

# 3. Demonic Jagged Audio-Wave / Glitch Smile Mouth
fc = len(bm.faces)
add_box(bm, (0.22, 0.015, 0.030), (0, -0.210, 1.72), rot=(math.radians(14), 0, 0))
tag(fc, 3)

# Jagged static fangs in the mouth
for tooth_x in [-0.08, -0.04, 0.0, 0.04, 0.08]:
    fc = len(bm.faces)
    add_cone(bm, 0.012, 0.002, 0.045, (tooth_x, -0.212, 1.70), rot=(math.radians(194), 0, 0), seg=6)
    tag(fc, 3)

# CRT Cathode Ray Tube Fangs below screen
for side, sx in [(1, 1), (-1, -1)]:
    fc = len(bm.faces)
    add_cone(bm, 0.025, 0.005, 0.14, (sx * 0.10, -0.19, 1.62), rot=(math.radians(165), math.radians(12 * sx), 0), seg=8)
    tag(fc, 0)
    fc = len(bm.faces)
    add_cylinder(bm, 0.008, 0.06, (sx * 0.10, -0.19, 1.58), seg=8)
    tag(fc, 3)

# HIGH-VOLTAGE TESLA CHOKE HORNS (Scorched dark metal with intense glowing crimson tips)
for side, sx in [(1, 1), (-1, -1)]:
    fc = len(bm.faces)
    h_loc1 = (sx * 0.14, 0.02, 1.95)
    h_rot1 = (math.radians(-22), math.radians(-25 * sx), math.radians(10 * sx))
    add_cone(bm, 0.045, 0.030, 0.22, h_loc1, rot=h_rot1, seg=12)
    tag(fc, 0)

    # Dark scorched dielectric ring
    fc = len(bm.faces)
    add_cylinder(bm, 0.055, 0.035, (sx * 0.17, 0.04, 2.02), rot=h_rot1, seg=12)
    tag(fc, 5)

    # Razor horn tip burning with intense blood red voltage
    fc = len(bm.faces)
    h_loc2 = (sx * 0.22, 0.10, 2.18)
    h_rot2 = (math.radians(-38), math.radians(-32 * sx), math.radians(15 * sx))
    add_cone(bm, 0.028, 0.003, 0.28, h_loc2, rot=h_rot2, seg=8)
    tag(fc, 3)

    # Ring 2
    fc = len(bm.faces)
    add_cylinder(bm, 0.042, 0.030, (sx * 0.20, 0.08, 2.12), rot=h_rot2, seg=12)
    tag(fc, 5)

# Vacuum Tubes on Back of CRT
for tx in [-0.08, 0.08]:
    fc = len(bm.faces)
    add_cylinder(bm, 0.030, 0.14, (tx, 0.18, 1.82), rot=(math.radians(90), 0, 0), seg=12)
    tag(fc, 1)
    fc = len(bm.faces)
    add_cylinder(bm, 0.012, 0.12, (tx, 0.18, 1.82), rot=(math.radians(90), 0, 0), seg=8)
    tag(fc, 3) # Blood red filament

# ==========================================================================
# 4. ARMS & 30CM TUNGSTEN NEEDLE CLAWS
# ==========================================================================
for side, sx in [(1, 1), (-1, -1)]:
    fc = len(bm.faces)
    sh_loc = (sx * 0.32, 0, 1.54)
    sh_rot = (math.radians(-10), math.radians(24 * sx), math.radians(16 * sx))
    add_box(bm, (0.16, 0.20, 0.26), sh_loc, rot=sh_rot)
    tag(fc, 0)

    # Scorched collar
    fc = len(bm.faces)
    add_box(bm, (0.18, 0.22, 0.06), (sx * 0.32, 0, 1.58), rot=sh_rot)
    tag(fc, 5)

    fc = len(bm.faces)
    add_box(bm, (0.12, 0.12, 0.28), (sx * 0.38, 0, 1.30), rot=(0, math.radians(-6 * sx), 0))
    tag(fc, 0)

    fc = len(bm.faces)
    add_cylinder(bm, 0.020, 0.24, (sx * 0.42, -0.04, 1.30), seg=8)
    tag(fc, 2)

    fc = len(bm.faces)
    add_box(bm, (0.11, 0.14, 0.30), (sx * 0.41, -0.04, 0.98), rot=(math.radians(8), math.radians(-4 * sx), 0))
    tag(fc, 1)

    fc = len(bm.faces)
    add_box(bm, (0.03, 0.12, 0.16), (sx * 0.46, 0.08, 1.05), rot=(math.radians(35), 0, 0))
    tag(fc, 0)

    h_pos = (sx * 0.42, -0.06, 0.74)
    fc = len(bm.faces)
    add_box(bm, (0.10, 0.08, 0.10), h_pos)
    tag(fc, 0)

    fc = len(bm.faces)
    add_cylinder(bm, 0.06, 0.04, h_pos, seg=12)
    tag(fc, 5)

    # 3x 30CM TUNGSTEN NEEDLE CLAWS (Pure menacing blood-red and toxic voltage glow)
    claw_offsets = [(-0.038, 0.28, 3), (0.0, 0.32, 3), (0.038, 0.28, 4)]
    for coff_x, c_len, em_mat in claw_offsets:
        fc = len(bm.faces)
        c_loc = (h_pos[0] + coff_x * sx, h_pos[1] - 0.02, h_pos[2] - c_len * 0.5)
        c_rot = (math.radians(176), math.radians(6 * (coff_x / 0.038) * sx), 0)
        add_cone(bm, 0.016, 0.002, c_len, c_loc, rot=c_rot, seg=8)
        tag(fc, 0)
        fc = len(bm.faces)
        tip_loc = (c_loc[0], c_loc[1], c_loc[2] - c_len * 0.4)
        add_cone(bm, 0.006, 0.001, 0.08, tip_loc, rot=c_rot, seg=6)
        tag(fc, em_mat)

bm.to_mesh(mesh)
bm.free()
mesh.update()

bev = obj.modifiers.new("Bevel", type='BEVEL')
bev.width = 0.008
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35)

# --------------------------------------------------------------------------
# TENEBROUS MOODY STUDIO LIGHTING & CAMERA
# --------------------------------------------------------------------------

if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.06, 0.07, 0.09, 1.0)
    bg.inputs["Strength"].default_value = 0.6

cam_data = bpy.data.cameras.new("Cam_Boss3_V2")
cam_obj = bpy.data.objects.new("Cam_Boss3_V2", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss3_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.06, 1.10)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.2
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.10 + dist * 0.30)

# Sinister Key Light (Cold High-Contrast)
key_data = bpy.data.lights.new("Light_Key_B3", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B3", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 210.0
key_data.size = 2.5
key_data.color = (0.85, 0.88, 0.95)
key_obj.location = (2.2, -2.4, 3.2)

# Toxic Ambient Underlight / Fill
fill_data = bpy.data.lights.new("Light_Fill_B3", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B3", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 60.0
fill_data.size = 3.5
fill_data.color = (0.05, 0.85, 0.3)
fill_obj.location = (-2.2, -2.2, 1.8)

# Fiery Blood-Red Rim Light
rim_data = bpy.data.lights.new("Light_Rim_B3", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B3", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 320.0
rim_data.size = 3.0
rim_data.color = (1.0, 0.01, 0.08)
rim_obj.location = (-0.6, 3.2, 2.8)

out_despues = os.path.join(output_dir, "boss3_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED TENEBROUS BOSS 3 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss3_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")
