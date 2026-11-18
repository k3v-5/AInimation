"""inspect_player_bash.py
Inspecciona qué curvas y valores tiene A_Player_Bash.fbx
"""
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Bash.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act = arm.animation_data.action
print(f"Action: {act.name}, range: {act.frame_range}")

for f in (0, 5, 10, 15, 20):
    bpy.context.scene.frame_set(f)
    print(f"\n--- Frame {f} ---")
    for pb in arm.pose.bones:
        q = pb.rotation_quaternion
        e = q.to_euler('XYZ')
        rot = [round(math.degrees(a), 1) for a in e]
        if any(abs(a) > 2.0 for a in rot):
            print(f"  {pb.name}: rot={rot}, loc={[round(v, 3) for v in pb.location]}")
