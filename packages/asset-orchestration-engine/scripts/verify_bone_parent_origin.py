"""verify_bone_parent_origin.py
Verifica si smg con loc=(0,0,0) queda en el head o en el tail de hand_R.
"""
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

# Crear un empty parented a hand_R
emp = bpy.data.objects.new("TestEmp", None)
emp.parent = arm
emp.parent_type = 'BONE'
emp.parent_bone = 'hand_R'
emp.location = (0, 0, 0)
bpy.context.scene.collection.objects.link(emp)

bpy.context.view_layer.update()

pb = arm.pose.bones['hand_R']
print(f"hand_R head world: {arm.matrix_world @ pb.head}")
print(f"hand_R tail world: {arm.matrix_world @ pb.tail}")
print(f"emp world loc:     {emp.matrix_world.translation}")
