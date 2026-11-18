"""check_player_orientation.py
Determina exactamente hacia donde mira SK_Player en reposo.
"""
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Calcular el centro de las caras con normal apuntando en Y positivo vs Y negativo
verts = mesh.data.vertices
min_y = min(v.co.y for v in verts)
max_y = max(v.co.y for v in verts)
print(f"SK_Player mesh Y range: {min_y:.4f} to {max_y:.4f}")

# Buscar donde estan los dedos de los pies (toe) y la nariz/pecho:
# En los humanos, los pies apuntan hacia adelante (+ o -).
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for b in arm.data.bones:
    if any(k in b.name.lower() for k in ('foot', 'toe', 'head', 'chest')):
        print(f"  Bone {b.name}: head={b.head_local}, tail={b.tail_local}")
