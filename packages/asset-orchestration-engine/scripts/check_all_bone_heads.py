"""check_all_bone_heads.py
Imprime la posicion mundial de cada hueso en la escena.
"""
import bpy

arm = bpy.data.objects['ARM_Player']
for pb in arm.pose.bones:
    if 'arm' in pb.name.lower() or 'hand' in pb.name.lower():
        head_w = arm.matrix_world @ pb.head
        tail_w = arm.matrix_world @ pb.tail
        print(f"{pb.name:12s}: head X={head_w.x:+.3f}, Y={head_w.y:+.3f}, Z={head_w.z:+.3f} | tail X={tail_w.x:+.3f}, Y={tail_w.y:+.3f}, Z={tail_w.z:+.3f}")
