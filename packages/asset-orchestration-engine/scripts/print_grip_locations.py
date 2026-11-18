"""print_grip_locations.py
Imprime las coordenadas mundiales del rear grip y del foregrip en la pose actual de calibrate_player_tucked_stock.
"""
import bpy
import math
from mathutils import Vector

# Reutilizar el script previo
import sys
sys.path.append(r"E:\Darx_Proyect\Tools\AssetEngine\scripts")
import calibrate_player_tucked_stock

smg = bpy.data.objects['SMG']
arm = bpy.data.objects['ARM_Player']

p_rear_grip = smg.matrix_world @ Vector((0.0, 0.008, 0.012))
p_foregrip = smg.matrix_world @ Vector((0.0, 0.232, -0.060))
p_stock = smg.matrix_world @ Vector((0.0, -0.282, 0.065))

print(f"Stock buttpad world: {p_stock}")
print(f"Rear grip (hand_R target): {p_rear_grip}")
print(f"Foregrip (hand_L target):  {p_foregrip}")

print(f"hand_R current world: {arm.matrix_world @ arm.pose.bones['hand_R'].head}")
print(f"hand_L current world: {arm.matrix_world @ arm.pose.bones['hand_L'].head}")
