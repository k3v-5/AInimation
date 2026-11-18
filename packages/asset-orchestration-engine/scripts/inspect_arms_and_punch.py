# -*- coding: utf-8 -*-
import sys, os, math
import bpy
from mathutils import Vector

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
PUNCH_FBX = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx"
RELOAD_FBX = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Pistol_Reload.fbx"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')

print(f"=== SK_FPS_Arms REST POSE ===")
print(f"Armature: {arm.name}, Mesh: {mesh.name}")
print(f"Mesh dimension: {mesh.dimensions}")
bb = [mesh.matrix_world @ Vector(corner) for corner in mesh.bound_box]
min_x = min(c.x for c in bb); max_x = max(c.x for c in bb)
min_y = min(c.y for c in bb); max_y = max(c.y for c in bb)
min_z = min(c.z for c in bb); max_z = max(c.z for c in bb)
print(f"Mesh Bounds (Blender coords): X=[{min_x:.3f}, {max_x:.3f}], Y=[{min_y:.3f}, {max_y:.3f}], Z=[{min_z:.3f}, {max_z:.3f}]")

print("\n--- Bone Rest Head Locations (World) ---")
for b in arm.data.bones:
    h = arm.matrix_world @ b.head_local
    print(f"  {b.name:15s}: head=({h.x:.3f}, {h.y:.3f}, {h.z:.3f})")

# Now test PUNCH animation
print(f"\n=== INSPECTING PUNCH ANIMATION ===")
bpy.ops.import_scene.fbx(filepath=PUNCH_FBX)
anim_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
act_punch = anim_arm.animation_data.action
arm.animation_data_create()
arm.animation_data.action = act_punch
if hasattr(act_punch, "slots") and len(act_punch.slots):
    arm.animation_data.action_slot = act_punch.slots[0]
bpy.data.objects.remove(anim_arm, do_unlink=True)

scene = bpy.context.scene
print("Punch frame range:", int(act_punch.frame_range[0]), "to", int(act_punch.frame_range[1]))
for f in range(int(act_punch.frame_range[0]), int(act_punch.frame_range[1]) + 1, 2):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    root = arm.matrix_world @ arm.pose.bones["root"].matrix.translation
    print(f"  Punch F{f:2d}: root=({root.x:.3f}, {root.y:.3f}, {root.z:.3f}) | hand_R=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f}) | hand_L=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")

# Now test RELOAD animation
print(f"\n=== INSPECTING RELOAD ANIMATION ===")
bpy.ops.import_scene.fbx(filepath=RELOAD_FBX)
anim_arm2 = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
act_reload = anim_arm2.animation_data.action
arm.animation_data.action = act_reload
if hasattr(act_reload, "slots") and len(act_reload.slots):
    arm.animation_data.action_slot = act_reload.slots[0]
bpy.data.objects.remove(anim_arm2, do_unlink=True)

for f in range(int(act_reload.frame_range[0]), int(act_reload.frame_range[1]) + 1, 10):
    scene.frame_set(f)
    bpy.context.view_layer.update()
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    root = arm.matrix_world @ arm.pose.bones["root"].matrix.translation
    print(f"  Reload F{f:2d}: root=({root.x:.3f}, {root.y:.3f}, {root.z:.3f}) | hand_R=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f}) | hand_L=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")

print("\n=== COMPLETED INSPECTION ===")
