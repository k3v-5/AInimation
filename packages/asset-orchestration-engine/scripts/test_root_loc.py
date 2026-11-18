# -*- coding: utf-8 -*-
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
pb_root = arm.pose.bones['root']

# We want world offset: X=0, Y=-0.10 (forward), Z=+0.15 (up)
# Since root bone has: Y_bone = Z_world, Z_bone = -Y_world
# loc_x = 0, loc_y = +0.15 (world Z), loc_z = +0.10 (world -Y)
pb_root.location = (0.0, 0.15, 0.10)
bpy.context.view_layer.update()

world_trans = arm.matrix_world @ pb_root.matrix.translation
print("Desired world: (0, -0.10, +0.15)")
print(f"Actual world:  ({world_trans.x:.3f}, {world_trans.y:.3f}, {world_trans.z:.3f})")
