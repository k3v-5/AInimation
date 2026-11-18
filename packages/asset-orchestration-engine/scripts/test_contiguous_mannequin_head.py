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

col = bpy.data.collections.new("Test_Contiguous_Head")
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

m_white = create_pbr_mat("M_WhiteMannequin", (0.92, 0.93, 0.96), rough=0.22, metal=0.05)
m_cyan = create_pbr_mat("M_Cyan", (0.0, 0.95, 1.0), rough=0.05, metal=0.0, emis_rgb=(0.0, 0.95, 1.0), emis_str=20.0)
m_magenta = create_pbr_mat("M_Magenta", (1.0, 0.02, 0.45), rough=0.05, metal=0.0, emis_rgb=(1.0, 0.02, 0.45), emis_str=20.0)
m_white_core = create_pbr_mat("M_CoreW", (1.0, 1.0, 1.0), rough=0.05, metal=0.0, emis_rgb=(1.0, 1.0, 1.0), emis_str=30.0)

# BUILD CONTIGUOUS ANATOMICAL HUMAN MANNEQUIN HEAD
mesh = bpy.data.meshes.new("Contiguous_Head_Mesh")
obj = bpy.data.objects.new("Contiguous_Head", mesh)
col.objects.link(obj)

obj.data.materials.append(m_white)      # 0
obj.data.materials.append(m_cyan)       # 1
obj.data.materials.append(m_magenta)    # 2
obj.data.materials.append(m_white_core) # 3

bm = bmesh.new()

# Create UV Sphere base: 32 rings, 48 segments, radius 1.0
bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=1.0)

# Deform vertices to match anatomical human mannequin head
# Target dimensions: Width ~ 0.16m, Height ~ 0.24m, Depth ~ 0.20m
# Pivot at neck base / center Z=1.74m
for v in bm.verts:
    x, y, z = v.co.x, v.co.y, v.co.z
    
    # Normalized height from chin (-1) to cranium top (+1)
    # Scale to human skull proportions
    sx = 0.078
    sy = 0.098
    sz = 0.118
    
    # Cranium roundness vs jaw taper
    if z < 0.0:
        # Jaw taper: width narrows towards chin
        taper_factor = 1.0 + z * 0.45 # from 1.0 down to 0.55 at bottom
        sx *= taper_factor
        # Taper backwards slightly at bottom
        if y > 0: # back of jaw
            sy *= (1.0 + z * 0.3)
    else:
        # Cranium top
        sy *= 1.05
    
    nx = x * sx
    ny = y * sy
    nz = z * sz + 1.74
    
    # FACIAL FEATURES DEFORMATION (Front is negative Y: ny < 0)
    if y < -0.2:
        rel_z = (nz - 1.74) / 0.118 # -1.0 (chin) to +1.0 (forehead)
        dist_x = abs(nx)
        
        # 1. BROW RIDGE (rel_z between 0.2 and 0.5)
        if 0.2 < rel_z < 0.5:
            brow_bump = math.sin((rel_z - 0.2) / 0.3 * math.pi) * 0.012
            ny -= brow_bump * (1.0 - min(dist_x / 0.07, 1.0))
            
        # 2. EYE SOCKET RECESSS (rel_z between 0.0 and 0.3, dist_x between 0.02 and 0.06)
        if 0.0 < rel_z < 0.3 and 0.018 < dist_x < 0.065:
            eye_indent = math.sin((rel_z) / 0.3 * math.pi) * math.sin((dist_x - 0.018) / 0.047 * math.pi) * 0.014
            ny += eye_indent
            
        # 3. NOSE PROTRUSION (rel_z between -0.4 and 0.15, dist_x < 0.025)
        if -0.4 < rel_z < 0.15 and dist_x < 0.024:
            # Nose bridge to tip
            progress = (rel_z - (-0.4)) / 0.55 # 0 at base, 1 at bridge
            if progress < 0.25: # tip
                nose_h = 0.028 * math.sin(progress / 0.25 * math.pi * 0.5)
            else: # bridge
                nose_h = 0.012 + 0.016 * (1.0 - (progress - 0.25) / 0.75)
            nose_falloff = 1.0 - (dist_x / 0.024)
            ny -= nose_h * nose_falloff
            
        # 4. LIPS & MOUTH (rel_z between -0.65 and -0.42, dist_x < 0.035)
        if -0.65 < rel_z < -0.42 and dist_x < 0.035:
            # Upper lip: -0.52 to -0.42
            # Lower lip: -0.65 to -0.54
            m_falloff = 1.0 - (dist_x / 0.035)
            if rel_z > -0.53: # upper lip
                lip_bump = math.sin((rel_z - (-0.53)) / 0.11 * math.pi) * 0.008
            else: # lower lip
                lip_bump = math.sin((rel_z - (-0.65)) / 0.12 * math.pi) * 0.007
            ny -= lip_bump * m_falloff
            
        # 5. CHIN PROTRUSION (rel_z between -0.95 and -0.68, dist_x < 0.032)
        if -0.95 < rel_z < -0.68 and dist_x < 0.032:
            chin_bump = math.sin((rel_z - (-0.95)) / 0.27 * math.pi) * (1.0 - dist_x / 0.032) * 0.012
            ny -= chin_bump
            
    v.co = Vector((nx, ny, nz))

# Split or assign the fine dimensional glitch rift down the center
for f in bm.faces:
    f.material_index = 0
    # Check if face is along the central vertical seam
    cx = f.calc_center_bounds().x
    cy = f.calc_center_bounds().y
    if cy < -0.05:
        if -0.005 <= cx <= 0.0:
            f.material_index = 1 # Cyan
        elif 0.0 < cx <= 0.005:
            f.material_index = 2 # Magenta

bm.to_mesh(mesh)
bm.free()
mesh.update()

# Enable smooth shading
for p in mesh.polygons:
    p.use_smooth = True

# Add subdivision modifier for clean porcelain finish
subd = obj.modifiers.new("Subsurf", type='SUBSURF')
subd.levels = 1
subd.render_levels = 2

# Add camera for close-up test
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
cam_data.lens = 75.0

empty = bpy.data.objects.new("Target", None)
scene.collection.objects.link(empty)
empty.location = (0, -0.05, 1.74)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'
cam_obj.location = (0.35, -0.75, 1.80)

key_data = bpy.data.lights.new("Light_Key", type='AREA')
key_obj = bpy.data.objects.new("Light_Key", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 180.0
key_data.size = 2.0
key_obj.location = (1.5, -1.8, 2.5)

fill_data = bpy.data.lights.new("Light_Fill", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 60.0
fill_data.size = 3.0
fill_data.color = (0.0, 0.85, 1.0)
fill_obj.location = (-1.5, -1.5, 1.8)

rim_data = bpy.data.lights.new("Light_Rim", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 150.0
rim_data.size = 2.0
rim_data.color = (1.0, 0.05, 0.60)
rim_obj.location = (-0.3, 1.5, 2.2)

out_test = os.path.join(output_dir, "test_contiguous_mannequin_head.png")
scene.render.filepath = out_test
bpy.ops.render.render(write_still=True)
print(f"RENDERED CONTIGUOUS HEAD -> {out_test}")
