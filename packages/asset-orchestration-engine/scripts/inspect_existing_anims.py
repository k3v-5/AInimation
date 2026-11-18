"""inspect_existing_anims.py
Inspecciona como estan posados los brazos en las animaciones canónicas de Rifle y FPS.
"""
import bpy
import math

print("=== INSPECTING A_FPS_Idle.fbx ===")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Idle.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"Action: {arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else 'None'}")
bpy.context.scene.frame_set(0)
for pb in arm.pose.bones:
    rot = [math.degrees(a) for a in pb.rotation_euler]
    loc = [round(v, 4) for v in pb.location]
    if any(abs(a) > 0.001 for a in rot) or any(abs(v) > 0.001 for v in loc):
        print(f"  FPS {pb.name}: rot={rot}, loc={loc}")

print("\n=== INSPECTING A_Player_Rifle_Idle.fbx ===")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Rifle_Idle.fbx")
arm2 = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"Action: {arm2.animation_data.action.name if arm2.animation_data and arm2.animation_data.action else 'None'}")
bpy.context.scene.frame_set(0)
for pb in arm2.pose.bones:
    rot = [math.degrees(a) for a in pb.rotation_euler]
    loc = [round(v, 4) for v in pb.location]
    if any(abs(a) > 0.001 for a in rot) or any(abs(v) > 0.001 for v in loc):
        print(f"  Player {pb.name}: rot={rot}, loc={loc}")
