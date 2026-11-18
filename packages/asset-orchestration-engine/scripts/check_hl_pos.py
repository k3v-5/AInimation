"""check_hl_pos.py
Verifica donde esta hand_L en test_player_perfect_two_hands
"""
import bpy
from mathutils import Vector

# Importar y ejecutar
import sys
sys.path.append(r"E:\Darx_Proyect\Tools\AssetEngine\scripts")
import test_player_perfect_two_hands

arm = bpy.data.objects['ARM_Player']
smg = bpy.data.objects['SMG']

hl = arm.pose.bones['hand_L']
hr = arm.pose.bones['hand_R']

p_foregrip = smg.matrix_world @ Vector((0.0, 0.232, -0.060))
p_rear_grip = smg.matrix_world @ Vector((0.0, 0.008, 0.012))

print(f"p_foregrip world:  {p_foregrip}")
print(f"hand_L head world: {arm.matrix_world @ hl.head}")
print(f"p_rear_grip world: {p_rear_grip}")
print(f"hand_R head world: {arm.matrix_world @ hr.head}")
