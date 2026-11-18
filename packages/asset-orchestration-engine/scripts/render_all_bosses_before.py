import bpy
from mathutils import Vector
import math
import os

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

bosses = [
    ("boss1_antes.png", "SK_Robot_Contencion"),
    ("boss2_antes.png", "SK_Boss_Error"),
    ("boss3_antes.png", "SK_Boss_StaticMatrix"),
    ("boss4_antes.png", "SK_Boss_Flora"),
    ("boss5_antes.png", "SK_Boss_Amalgam"),
    ("boss6_antes.png", "SK_Boss_Telekinetic")
]

scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

# Turn off all existing lights
for l in bpy.data.objects:
    if l.type == 'LIGHT':
        l.hide_render = True

# Ensure dark studio background
if scene.world:
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.04, 0.05, 0.07, 1.0)
        bg.inputs["Strength"].default_value = 0.5

# Camera
if "Cam_Boss_Inspect" in bpy.data.objects:
    cam_obj = bpy.data.objects["Cam_Boss_Inspect"]
else:
    cam_data = bpy.data.cameras.new("Cam_Boss_Inspect")
    cam_obj = bpy.data.objects.new("Cam_Boss_Inspect", cam_data)
    scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.data.lens = 45.0

# Target Empty
if "Cam_Boss_Target" in bpy.data.objects:
    empty_obj = bpy.data.objects["Cam_Boss_Target"]
else:
    empty_obj = bpy.data.objects.new("Cam_Boss_Target", None)
    scene.collection.objects.link(empty_obj)

cam_obj.constraints.clear()
tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_obj
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
def get_or_create_light(name, ltype):
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
    else:
        data = bpy.data.lights.new(name, type=ltype)
        obj = bpy.data.objects.new(name, data)
        scene.collection.objects.link(obj)
    obj.hide_render = False
    return obj

key_obj = get_or_create_light("Light_Key_Boss", 'AREA')
key_obj.data.energy = 250.0
key_obj.data.size = 3.0
key_obj.data.color = (1.0, 0.98, 0.95)

fill_obj = get_or_create_light("Light_Fill_Boss", 'AREA')
fill_obj.data.energy = 80.0
fill_obj.data.size = 4.0
fill_obj.data.color = (0.65, 0.75, 0.90)

rim_obj = get_or_create_light("Light_Rim_Boss", 'AREA')
rim_obj.data.energy = 200.0
rim_obj.data.size = 3.0
rim_obj.data.color = (0.75, 0.35, 1.0)

# Hide all mesh objects initially
mesh_objects = [o for o in bpy.data.objects if o.type in ['MESH', 'ARMATURE']]
for o in mesh_objects:
    o.hide_render = True

for filename, mesh_name in bosses:
    target_mesh = bpy.data.objects.get(mesh_name)
    if not target_mesh:
        print(f"Skipping {mesh_name} (not found)")
        continue

    for o in mesh_objects:
        o.hide_render = True
    
    target_mesh.hide_render = False
    for child in target_mesh.children_recursive:
        child.hide_render = False

    for col in target_mesh.users_collection:
        for co in col.objects:
            if co.type in ['MESH', 'ARMATURE']:
                co.hide_render = False

    bbox = [target_mesh.matrix_world @ Vector(corner) for corner in target_mesh.bound_box]
    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)
    min_z = min(v.z for v in bbox)
    max_z = max(v.z for v in bbox)

    cx = (min_x + max_x) * 0.5
    cy = (min_y + max_y) * 0.5
    cz = (min_z + max_z) * 0.5
    max_dim = max(max_x - min_x, max_y - min_y, max_z - min_z)

    empty_obj.location = (cx, cy, cz)

    dist = max(max_dim * 1.6, 2.8)
    cam_obj.location = (cx + dist * 0.65, cy - dist * 0.85, cz + dist * 0.30)

    # Position lights relative to boss
    key_obj.location = (cx + dist * 0.8, cy - dist * 0.7, cz + dist * 0.9)
    fill_obj.location = (cx - dist * 0.8, cy - dist * 0.7, cz + dist * 0.5)
    rim_obj.location = (cx - dist * 0.3, cy + dist * 0.9, cz + dist * 0.7)

    out_path = os.path.join(output_dir, filename)
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED {mesh_name} -> {out_path}")

print("ALL BOSSES (ANTES) RENDERED SUCCESSFULLY!")
