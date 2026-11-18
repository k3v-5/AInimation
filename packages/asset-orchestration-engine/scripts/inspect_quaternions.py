"""inspect_quaternions.py
Inspecciona los canales de rotacion (quaternion / euler) de las animaciones existentes.
"""
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Rifle_Idle.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print("--- A_Player_Rifle_Idle bones at frame 0 ---")
bpy.context.scene.frame_set(0)
for pb in arm.pose.bones:
    q = pb.rotation_quaternion
    e = q.to_euler('XYZ')
    rot_deg = [round(math.degrees(a), 2) for a in e]
    if any(abs(a) > 0.5 for a in rot_deg):
        print(f"  {pb.name}: rot={rot_deg}, loc={[round(v, 4) for v in pb.location]}")

print("\n--- A_FPS_Pistol_Idle.fbx bones at frame 0 ---")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Pistol_Idle.fbx")
arm2 = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
bpy.context.scene.frame_set(0)
for pb in arm2.pose.bones:
    q = pb.rotation_quaternion
    e = q.to_euler('XYZ')
    rot_deg = [round(math.degrees(a), 2) for a in e]
    if any(abs(a) > 0.5 for a in rot_deg):
        print(f"  {pb.name}: rot={rot_deg}, loc={[round(v, 4) for v in pb.location]}")
