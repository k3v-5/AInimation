import bpy
import os
import math

CANONICAL_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
OUTPUT_FBX = r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx"
RENDER_OUT = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_darkfluid_clean.png"

bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)

# 1. Purgar todo objeto que no sea ARM_Player o SK_Player
for o in list(bpy.data.objects):
    if o.name not in ["ARM_Player", "SK_Player"]:
        bpy.data.objects.remove(o, do_unlink=True)

arm_obj = bpy.data.objects.get("ARM_Player")
mesh_obj = bpy.data.objects.get("SK_Player")

if not arm_obj or not mesh_obj:
    raise RuntimeError("No se encontró ARM_Player o SK_Player en DarX_Player_Rigged_Canonical.blend")

# 2. Validar huesos canónicos
bone_names = [b.name for b in arm_obj.data.bones]
print(f"Huesos encontrados en ARM_Player ({len(bone_names)}): {bone_names}")
assert len(bone_names) == 22, f"Se esperaban 22 huesos, se encontraron {len(bone_names)}"

# 3. Forzar Rest Pose y actualización
arm_obj.data.pose_position = 'REST'
bpy.context.view_layer.update()

# 4. Dimensiones y límites
coords = [v.co for v in mesh_obj.data.vertices]
min_z = min(c.z for c in coords)
max_z = max(c.z for c in coords)
print(f"Límites Z de SK_Player: [{min_z:.4f}, {max_z:.4f}]m (Estatura: {max_z - min_z:.4f}m)")

# 5. Exportación Atómica de FBX
for o in bpy.data.objects:
    o.select_set(False)

arm_obj.select_set(True)
mesh_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj

if os.path.exists(OUTPUT_FBX):
    os.remove(OUTPUT_FBX)

bpy.ops.export_scene.fbx(
    filepath=OUTPUT_FBX,
    use_selection=True,
    global_scale=1.0,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Y',
    axis_up='Z',
    bake_space_transform=False,
    object_types={'ARMATURE', 'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    bake_anim=False
)
print(f"[OK] Exportado Art/FBX/SK_Player.fbx limpio ({os.path.getsize(OUTPUT_FBX)} bytes)")

# 6. Renderizar Previsualización Frontal y 3/4
world = bpy.data.worlds.new("W_PlayerPreview")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

def add_light(name, ltype, energy, loc, rot, color=(1,1,1)):
    ld = bpy.data.lights.new(name, ltype)
    ld.energy = energy
    ld.color = color
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.rotation_euler = rot
    bpy.context.scene.collection.objects.link(lo)

add_light("Key", 'SUN', 4.5, (0,0,0), (math.radians(50), math.radians(10), math.radians(-35)), (1, 0.98, 0.95))
add_light("Fill", 'SUN', 2.5, (0,0,0), (math.radians(45), math.radians(-20), math.radians(145)), (0.75, 0.85, 1.0))
add_light("Rim_Violet", 'SUN', 8.0, (0,0,0), (math.radians(-45), math.radians(25), math.radians(45)), (0.85, 0.15, 1.0))

cam_data = bpy.data.cameras.new("Cam_Preview")
cam_obj = bpy.data.objects.new("Cam_Preview", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Vista de cuerpo entero ligeramente en perspectiva 3/4
cam_obj.location = (0.5, -2.8, 1.0)
cam_obj.rotation_euler = (math.radians(88), 0, math.radians(10))

bpy.context.scene.render.filepath = RENDER_OUT
bpy.context.scene.render.resolution_x = 768
bpy.context.scene.render.resolution_y = 768
bpy.ops.render.render(write_still=True)
print(f"[OK] Render de SK_Player guardado en {RENDER_OUT}")
