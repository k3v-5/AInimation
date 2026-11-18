# -*- coding: utf-8 -*-
import bpy
import os

ANIMS = [
    ("A_FPS_Unarmed_Punch_R", r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx", [0, 6, 13]),
    ("A_FPS_Pistol_Reload", r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Pistol_Reload.fbx", [0, 6, 14, 22, 36]),
    ("A_FPS_SMG_Reload", r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_SMG_Reload.fbx", [0, 8, 18, 28, 36, 42, 48]),
    ("A_FPS_Shotgun_Reload", r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Shotgun_Reload.fbx", [0, 8, 18, 26, 34, 42, 48, 54]),
    ("A_FPS_Rifle_Reload", r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Rifle_Reload.fbx", [0, 8, 18, 26, 34, 40, 45]),
]

for name, filepath, frames in ANIMS:
    print(f"\n=== {name} ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=filepath)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    scene = bpy.context.scene
    for f in frames:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
        hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
        w = arm.matrix_world @ arm.pose.bones["weapon"].matrix.translation if "weapon" in arm.pose.bones else None
        print(f"F{f:2d}: hand_L=({hl.x:+.3f}, {hl.y:+.3f}, {hl.z:+.3f}) | hand_R=({hr.x:+.3f}, {hr.y:+.3f}, {hr.z:+.3f}) | wep={f'({w.x:+.3f}, {w.y:+.3f}, {w.z:+.3f})' if w else 'None'}")
