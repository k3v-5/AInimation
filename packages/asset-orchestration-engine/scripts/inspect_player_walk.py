"""inspect_player_walk.py
Inspecciona los rangos de rotacion reales de A_Player_Walk.fbx
"""
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Walk.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act = arm.animation_data.action
print(f"A_Player_Walk Action: {act.name}, range: {act.frame_range}")

for f in range(int(act.frame_range[0]), int(act.frame_range[1]) + 1, 5):
    bpy.context.scene.frame_set(f)
    print(f"\n--- Frame {f} ---")
    for bname in ('pelvis', 'thigh_R', 'calf_R', 'thigh_L', 'calf_L', 'upperarm_R', 'forearm_R', 'upperarm_L', 'forearm_L'):
        pb = arm.pose.bones.get(bname)
        if pb:
            e = pb.rotation_quaternion.to_euler('XYZ')
            rot = [round(math.degrees(a), 1) for a in e]
            print(f"  {bname}: rot={rot}, loc={[round(v, 3) for v in pb.location]}")
