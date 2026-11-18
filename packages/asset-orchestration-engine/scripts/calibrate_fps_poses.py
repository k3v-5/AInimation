# -*- coding: utf-8 -*-
import bpy
import math
from mathutils import Vector, Euler

# Importar SK_FPS_Arms
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = bpy.data.objects['ARM_FPS_Arms']

# Reset bones
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

# Camera at eye level
cam_data = bpy.data.cameras.new("Cam_FPS")
cam_data.lens = 22 # ~70 deg FOV
cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
# Eyes at (0, 0, 0) in mesh space
cam_obj.location = (0.0, 0.0, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180)) # Looking straight down -Y
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

def test_pose(pose_dict, desc):
    for bname, vals in pose_dict.items():
        pb = arm.pose.bones.get(bname)
        if pb:
            if 'rot' in vals:
                pb.rotation_euler = [math.radians(a) for a in vals['rot']]
            if 'loc' in vals:
                pb.location = vals['loc']
    bpy.context.view_layer.update()
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    wep = arm.matrix_world @ arm.pose.bones["weapon"].matrix.translation
    print(f"\n[{desc}]")
    print(f"  hand_L: ({hl.x:+.3f}, {hl.y:+.3f}, {hl.z:+.3f}) -> angle from center: {math.degrees(math.atan2(hl.z, -hl.y)):.1f} deg vertical, {math.degrees(math.atan2(hl.x, -hl.y)):.1f} deg horiz")
    print(f"  hand_R: ({hr.x:+.3f}, {hr.y:+.3f}, {hr.z:+.3f}) -> angle from center: {math.degrees(math.atan2(hr.z, -hr.y)):.1f} deg vertical, {math.degrees(math.atan2(hr.x, -hr.y)):.1f} deg horiz")
    print(f"  weapon: ({wep.x:+.3f}, {wep.y:+.3f}, {wep.z:+.3f}) -> angle from center: {math.degrees(math.atan2(wep.z, -wep.y)):.1f} deg vertical, {math.degrees(math.atan2(wep.x, -wep.y)):.1f} deg horiz")

# Rest pose
test_pose({}, "REST POSE")

# Test elevated punch (crosshair punch)
punch_peak = {
    'root': {'loc': (0.0, -0.05, 0.02)},
    'upperarm_R': {'rot': (-45, -60, 45)},
    'forearm_R':  {'rot': (65, -15, 10)},
    'hand_R':     {'rot': (10, -20, 60)},
    'upperarm_L': {'rot': (-10, 20, -5)},
    'forearm_L':  {'rot': (-60, 15, 15)},
    'hand_L':     {'rot': (20, 0, -10)},
}
test_pose(punch_peak, "CROSSHAIR PUNCH")
