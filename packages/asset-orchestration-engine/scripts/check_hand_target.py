"""check_hand_target.py
Imprime la posicion mundial del foregrip y de hand_L para calibrar el target exacto.
"""
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

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

smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'

bpy.context.view_layer.update()

# Buscar objeto SMG_VerticalForegrip
foregrip_objs = [o for o in bpy.data.objects if 'foregrip' in o.name.lower()]
print(f"Foregrip meshes: {foregrip_objs}")

# Calculemos el centro del mango vertical:
# En el blend original, el objeto SMG_VerticalForegrip estaba centrado en X=0, Y=+0.23, Z=-0.06
target_world = smg.matrix_world @ Vector((0.0, 0.23, -0.06))
print(f"Target vertical foregrip in world: {target_world}")

# En el armature:
hl = arm.pose.bones['hand_L']
print(f"hand_L head in world: {arm.matrix_world @ hl.head}")

# Si hand_L se mueve a target_world, ¿cuál es el vector desde su hombro?
ul = arm.pose.bones['upperarm_L']
sh_world = arm.matrix_world @ ul.head
dist = (target_world - sh_world).length
print(f"Left shoulder world: {sh_world}")
print(f"Distance from left shoulder to foregrip: {dist:.4f} m")
print(f"Arm length (upperarm + forearm): {(ul.tail - ul.head).length + (arm.pose.bones['forearm_L'].tail - arm.pose.bones['forearm_L'].head).length:.4f} m")
