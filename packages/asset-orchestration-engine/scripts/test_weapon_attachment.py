"""test_weapon_attachment.py
Verifica la posicion y orientacion exacta del SMG cuando se ancla a SK_FPS_Arms y SK_Player.
"""
import bpy
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

# Importar SMG
with bpy.data.libraries.load(r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend", link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    bpy.context.scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = "SMG"

c = smg.constraints.new('CHILD_OF')
c.target = arm
c.subtarget = 'weapon'
# Si inverse_matrix no se calcula correctamente, vemos que pasa:
bpy.context.view_layer.update()
print("SMG world matrix with default constraint:")
print(smg.matrix_world)

# ¿Cual es la posicion de la empuñadura trasera y el cañón en el espacio del hueso weapon?
# El hueso weapon en rest pose tiene matrix:
wb = arm.pose.bones['weapon']
print("weapon bone world matrix:")
print(arm.matrix_world @ wb.matrix)
