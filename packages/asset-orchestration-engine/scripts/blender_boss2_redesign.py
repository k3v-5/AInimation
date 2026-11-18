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

col = bpy.data.collections.new("DARX_Boss2_V2")
scene.collection.children.link(col)

# --------------------------------------------------------------------------
# MATERIALS (SYNTHETIC ALABASTER WHITE MANNEQUIN + FRACTURED VOID & GLITCH)
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

m_mannequin_white = create_pbr_mat("M_Error_MannequinWhite", (0.93, 0.94, 0.97), rough=0.20, metal=0.05)
m_void = create_pbr_mat("M_Error_Void", (0.012, 0.013, 0.018), rough=0.20, metal=0.85)
m_cyan = create_pbr_mat("M_Error_Glitch_Cyan", (0.0, 0.95, 1.0), rough=0.05, metal=0.0, emis_rgb=(0.0, 0.95, 1.0), emis_str=20.0)
m_magenta = create_pbr_mat("M_Error_Glitch_Magenta", (1.0, 0.02, 0.45), rough=0.05, metal=0.0, emis_rgb=(1.0, 0.02, 0.45), emis_str=20.0)
m_white_core = create_pbr_mat("M_Error_Glitch_White", (1.0, 1.0, 1.0), rough=0.05, metal=0.0, emis_rgb=(1.0, 1.0, 1.0), emis_str=30.0)

# --------------------------------------------------------------------------
# GEOMETRY HELPERS
# --------------------------------------------------------------------------

def add_box(bm, size, loc, rot=(0,0,0)):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1.0))
    return bmesh.ops.create_cube(bm, size=1.0, matrix=mat)

def add_cone(bm, r1, r2, depth, loc, rot=(0,0,0), seg=16):
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    return bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=depth, matrix=mat)

# ==========================================================================
# 1. BODY MESH (PELVIS, RIBS, ARMS, CLAWS, NEEDLE VORTEX)
# ==========================================================================
mesh_body = bpy.data.meshes.new("SK_Boss_Error_Body_Mesh")
obj_body = bpy.data.objects.new("SK_Boss_Error_Body", mesh_body)
col.objects.link(obj_body)

for m in [m_mannequin_white, m_void, m_cyan, m_magenta, m_white_core]:
    obj_body.data.materials.append(m)

bm_body = bmesh.new()

def tag_b(old_count, mat_idx):
    for f in bm_body.faces[old_count:]:
        f.material_index = mat_idx

# Core Pelvis
fc = len(bm_body.faces)
bmesh.ops.create_icosphere(bm_body, subdivisions=2, radius=0.12, matrix=Matrix.Translation((0, 0, 0.98)))
tag_b(fc, 1)

fc = len(bm_body.faces)
add_cone(bm_body, 0.16, 0.16, 0.04, (0, 0, 0.98), seg=24)
tag_b(fc, 2)

for ang in [45, -45, 135, -135]:
    fc = len(bm_body.faces)
    rad = math.radians(ang)
    px = 0.16 * math.cos(rad)
    py = 0.16 * math.sin(rad)
    add_box(bm_body, (0.08, 0.12, 0.05), (px, py, 1.00), rot=(math.radians(15), math.radians(15 * math.cos(rad)), rad))
    tag_b(fc, 0)

# Inverted Needle Spire & Satellite Blades
fc = len(bm_body.faces)
add_cone(bm_body, 0.14, 0.008, 0.72, (0, 0, 0.61), rot=(math.radians(180), 0, 0), seg=16)
tag_b(fc, 0)

for ang, mat_idx in [(0, 2), (90, 3), (180, 2), (270, 3)]:
    fc = len(bm_body.faces)
    rad = math.radians(ang)
    px = 0.07 * math.cos(rad)
    py = 0.07 * math.sin(rad)
    add_box(bm_body, (0.02, 0.02, 0.46), (px, py, 0.66), rot=(0, 0, rad))
    tag_b(fc, mat_idx)

blade_coords = [
    ((-0.24,  0.12, 0.44), (math.radians(25),  math.radians(18), math.radians(-35))),
    (( 0.24,  0.12, 0.44), (math.radians(25), -math.radians(18),  math.radians(35))),
    (( 0.00, -0.26, 0.36), (math.radians(-30), 0,                 math.radians(180))),
    (( 0.00,  0.22, 0.52), (math.radians(20),  0,                 0)),
]
for loc, rot in blade_coords:
    fc = len(bm_body.faces)
    add_box(bm_body, (0.05, 0.22, 0.04), loc, rot=rot)
    tag_b(fc, 0)
    fc = len(bm_body.faces)
    edge_loc = (loc[0], loc[1], loc[2] + 0.01)
    add_box(bm_body, (0.015, 0.20, 0.015), edge_loc, rot=rot)
    tag_b(fc, 2 if loc[0] <= 0 else 3)

# Torso & Floating Ribs
fc = len(bm_body.faces)
add_box(bm_body, (0.12, 0.10, 0.36), (0, 0.02, 1.30))
tag_b(fc, 1)

for i, pz in enumerate([1.16, 1.25, 1.34, 1.43, 1.52]):
    fc = len(bm_body.faces)
    add_box(bm_body, (0.08, 0.06, 0.05), (0, 0.10, pz), rot=(math.radians(10 + i * 2), 0, 0))
    tag_b(fc, 0)

fc = len(bm_body.faces)
add_box(bm_body, (0.16, 0.12, 0.22), (-0.11, -0.10, 1.38), rot=(math.radians(14), math.radians(-10), math.radians(-12)))
tag_b(fc, 0)

fc = len(bm_body.faces)
add_box(bm_body, (0.16, 0.12, 0.22), (0.11, -0.10, 1.38), rot=(math.radians(14), math.radians(10), math.radians(12)))
tag_b(fc, 0)

rib_tiers = [
    (1.22, 0.18, math.radians(-25), 2),
    (1.32, 0.21, math.radians(-15), 3),
    (1.42, 0.23, math.radians(-5),  2),
]
for rz, rx_span, r_rot, m_idx in rib_tiers:
    for side, sx in [(1, 1), (-1, -1)]:
        fc = len(bm_body.faces)
        r_loc = (sx * rx_span, -0.04, rz)
        add_box(bm_body, (0.04, 0.14, 0.03), r_loc, rot=(0, math.radians(18 * sx), r_rot * sx))
        tag_b(fc, 0)
        fc = len(bm_body.faces)
        add_box(bm_body, (0.015, 0.12, 0.015), (sx * (rx_span - 0.02), -0.05, rz), rot=(0, math.radians(18 * sx), r_rot * sx))
        tag_b(fc, m_idx)

fc = len(bm_body.faces)
add_box(bm_body, (0.04, 0.04, 0.16), (0, -0.12, 1.38))
tag_b(fc, 4)

# Arms & Needle Claws
for side, sx in [(1, 1), (-1, -1)]:
    fc = len(bm_body.faces)
    sh_pos = (sx * 0.28, 0, 1.50)
    add_box(bm_body, (0.13, 0.16, 0.16), sh_pos, rot=(0, math.radians(14 * sx), math.radians(-10 * sx)))
    tag_b(fc, 0)

    fc = len(bm_body.faces)
    add_box(bm_body, (0.04, 0.08, 0.12), (sx * 0.32, -0.04, 1.54), rot=(0, math.radians(25 * sx), 0))
    tag_b(fc, 2 if sx < 0 else 3)

    fc = len(bm_body.faces)
    arm_pos = (sx * 0.36, -0.02, 1.28)
    add_cone(bm_body, 0.09, 0.05, 0.26, arm_pos, rot=(math.radians(180), 0, math.radians(10 * sx)), seg=12)
    tag_b(fc, 0)

    fc = len(bm_body.faces)
    fore_pos = (sx * 0.38, -0.06, 0.98)
    add_box(bm_body, (0.08, 0.12, 0.28), fore_pos, rot=(math.radians(12), 0, math.radians(-6 * sx)))
    tag_b(fc, 0)

    fc = len(bm_body.faces)
    add_box(bm_body, (0.015, 0.10, 0.24), (sx * 0.38, -0.13, 0.98), rot=(math.radians(12), 0, math.radians(-6 * sx)))
    tag_b(fc, 2 if sx < 0 else 3)

    h_pos = (sx * 0.40, -0.08, 0.72)
    fc = len(bm_body.faces)
    add_box(bm_body, (0.08, 0.06, 0.08), h_pos, rot=(0, math.radians(6 * sx), 0))
    tag_b(fc, 0)

    claw_offsets = [-0.030, -0.010, 0.010, 0.030]
    for c_idx, coff in enumerate(claw_offsets):
        fc = len(bm_body.faces)
        c_pos = (h_pos[0] + coff * sx, h_pos[1] - 0.02, h_pos[2] - 0.12)
        c_len = 0.18 if (c_idx in [1, 2]) else 0.15
        add_cone(bm_body, 0.018, 0.002, c_len, c_pos, rot=(math.radians(180), 0, 0), seg=6)
        tag_b(fc, 0)
        fc = len(bm_body.faces)
        add_cone(bm_body, 0.006, 0.001, 0.05, (c_pos[0], c_pos[1], c_pos[2] - c_len * 0.5), rot=(math.radians(180), 0, 0), seg=6)
        tag_b(fc, 2 if sx < 0 else 3)

# Clean head without any floating shards or ears above face

bm_body.to_mesh(mesh_body)
bm_body.free()
mesh_body.update()

bev = obj_body.modifiers.new("Bevel", type='BEVEL')
bev.width = 0.006
bev.segments = 2
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(35)

# ==========================================================================
# 2. CONTIGUOUS SCULPTED HUMAN MANNEQUIN HEAD MESH (SEAMLESS PORCELAIN)
# ==========================================================================
mesh_head = bpy.data.meshes.new("SK_Boss_Error_Head_Mesh")
obj_head = bpy.data.objects.new("SK_Boss_Error_Head", mesh_head)
col.objects.link(obj_head)

for m in [m_mannequin_white, m_cyan, m_magenta, m_white_core]:
    obj_head.data.materials.append(m)

bm_head = bmesh.new()
bmesh.ops.create_uvsphere(bm_head, u_segments=48, v_segments=32, radius=1.0)

for v in bm_head.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    sx = 0.080
    sy = 0.100
    sz = 0.120
    
    if z < 0.0:
        taper = 1.0 + z * 0.45
        sx *= taper
        if y > 0:
            sy *= (1.0 + z * 0.3)
    else:
        sy *= 1.05
        
    nx = x * sx
    ny = y * sy
    nz = z * sz + 1.74
    
    # Anatomical Human Mannequin Facial Sculpting
    if y < -0.2:
        rel_z = (nz - 1.74) / 0.120 # -1.0 to 1.0
        dist_x = abs(nx)
        
        # 1. Brow Ridge
        if 0.22 < rel_z < 0.52:
            brow = math.sin((rel_z - 0.22) / 0.30 * math.pi) * 0.012
            ny -= brow * (1.0 - min(dist_x / 0.07, 1.0))
            
        # 2. Eye Orbits (Subtle indent for closed mannequin eyes)
        if 0.02 < rel_z < 0.32 and 0.016 < dist_x < 0.065:
            indent = math.sin((rel_z - 0.02) / 0.30 * math.pi) * math.sin((dist_x - 0.016) / 0.049 * math.pi) * 0.015
            ny += indent
            
        # 3. Sculpted Nose Bridge and Tip
        if -0.38 < rel_z < 0.18 and dist_x < 0.026:
            prog = (rel_z - (-0.38)) / 0.56
            if prog < 0.28: # tip
                nose_h = 0.032 * math.sin(prog / 0.28 * math.pi * 0.5)
            else: # bridge
                nose_h = 0.012 + 0.020 * (1.0 - (prog - 0.28) / 0.72)
            fall = 1.0 - (dist_x / 0.026)
            ny -= nose_h * fall
            
        # 4. Sculpted Mannequin Lips
        if -0.66 < rel_z < -0.40 and dist_x < 0.038:
            m_fall = 1.0 - (dist_x / 0.038)
            if rel_z > -0.52:
                lip = math.sin((rel_z - (-0.52)) / 0.12 * math.pi) * 0.011
            else:
                lip = math.sin((rel_z - (-0.66)) / 0.14 * math.pi) * 0.009
            ny -= lip * m_fall
            
        # 5. Chin Protrusion
        if -0.96 < rel_z < -0.68 and dist_x < 0.034:
            chin = math.sin((rel_z - (-0.96)) / 0.28 * math.pi) * (1.0 - dist_x / 0.034) * 0.014
            ny -= chin
            
    v.co = Vector((nx, ny, nz))

# Material assignment: White porcelain face with clean vertical chromatic rift seam
for f in bm_head.faces:
    f.material_index = 0
    cx = f.calc_center_bounds().x
    cy = f.calc_center_bounds().y
    if cy < -0.05:
        if -0.0045 <= cx <= 0.0:
            f.material_index = 1 # Cyan
        elif 0.0 < cx <= 0.0045:
            f.material_index = 2 # Magenta

bm_head.to_mesh(mesh_head)
bm_head.free()
mesh_head.update()

for p in mesh_head.polygons:
    p.use_smooth = True

subd = obj_head.modifiers.new("Subsurf", type='SUBSURF')
subd.levels = 1
subd.render_levels = 2

# --------------------------------------------------------------------------
# LIGHTING & CAMERA (Studio Slate Background)
# --------------------------------------------------------------------------

if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs["Strength"].default_value = 0.8

cam_data = bpy.data.cameras.new("Cam_Boss2_V2")
cam_obj = bpy.data.objects.new("Cam_Boss2_V2", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss2_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (-0.00, -0.04, 1.05)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.0
cam_obj.location = (-0.00 + dist * 0.65, -0.04 - dist * 0.85, 1.05 + dist * 0.30)

key_data = bpy.data.lights.new("Light_Key_B2", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B2", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 220.0
key_data.size = 3.0
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (2.2, -2.2, 3.2)

fill_data = bpy.data.lights.new("Light_Fill_B2", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B2", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 80.0
fill_data.size = 4.0
fill_data.color = (0.0, 0.85, 1.0)
fill_obj.location = (-2.2, -2.2, 2.0)

rim_data = bpy.data.lights.new("Light_Rim_B2", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B2", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 200.0
rim_data.size = 3.0
rim_data.color = (1.0, 0.05, 0.60)
rim_obj.location = (-0.5, 2.8, 2.4)

out_despues = os.path.join(output_dir, "boss2_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED BOSS 2 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss2_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")
