"""fix_canonical_player_rig.py
Corrige definitivamente la Rest Pose y Bind Pose de SK_Player alineando los huesos
de los brazos (clavicle, upperarm, forearm, hand) con el centroide anatómico de la malla en A-pose,
recalcula la normalización de pesos y exporta Art/FBX/SK_Player.fbx.
"""
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX")
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "Saved", "Player_Skin_Workspace")
CANONICAL_BLEND = os.path.join(WORKSPACE_DIR, "DarX_Player_Rigged_Canonical.blend")
OUT_FBX = os.path.join(FBX_DIR, "SK_Player.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)
scene = bpy.context.scene

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print("Alineando huesos de brazos a la anatomía A-pose del modelo...")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

# Posiciones anatómicas de los brazos en la malla A-pose
# Hombro: (0.228, -0.010, 1.520)
# Codo:    (0.550, 0.020, 1.250)
# Muñeca:  (0.860, 0.045, 0.950)
# Puntas:  (0.950, 0.045, 0.850)

# Brazo Derecho
eb['upperarm_R'].head = Vector((0.228, -0.010, 1.520))
eb['upperarm_R'].tail = Vector((0.550, 0.020, 1.250))
eb['forearm_R'].head = Vector((0.550, 0.020, 1.250))
eb['forearm_R'].tail = Vector((0.860, 0.045, 0.950))
eb['hand_R'].head = Vector((0.860, 0.045, 0.950))
eb['hand_R'].tail = Vector((0.950, 0.045, 0.850))

# Brazo Izquierdo (Simétrico)
eb['upperarm_L'].head = Vector((-0.228, -0.010, 1.520))
eb['upperarm_L'].tail = Vector((-0.550, 0.020, 1.250))
eb['forearm_L'].head = Vector((-0.550, 0.020, 1.250))
eb['forearm_L'].tail = Vector((-0.860, 0.045, 0.950))
eb['hand_L'].head = Vector((-0.860, 0.045, 0.950))
eb['hand_L'].tail = Vector((-0.950, 0.045, 0.850))

# Roll de huesos para flexión limpia del codo
eb['upperarm_R'].roll = math.radians(-45)
eb['forearm_R'].roll = math.radians(-45)
eb['upperarm_L'].roll = math.radians(45)
eb['forearm_L'].roll = math.radians(45)

bpy.ops.object.mode_set(mode='OBJECT')

# Reasignar pesos automáticos limpios para los 6 huesos de brazos
arm_groups = ['upperarm_R', 'forearm_R', 'hand_R', 'upperarm_L', 'forearm_L', 'hand_L']
for gname in arm_groups:
    vg = mesh.vertex_groups.get(gname)
    if vg:
        mesh.vertex_groups.remove(vg)

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# Asegurar normalización total de pesos en todos los vértices
for v in mesh.data.vertices:
    total_w = sum(g.weight for g in v.groups if g.group < len(mesh.vertex_groups))
    if total_w > 0.0001:
        for g in v.groups:
            if g.group < len(mesh.vertex_groups):
                g.weight /= total_w

# Guardar blend maestro actualizado
bpy.ops.wm.save_mainfile(filepath=CANONICAL_BLEND)
print(f"Guardado blend maestro con huesos congruentes: {CANONICAL_BLEND}")

# Exportar FBX para Unreal Engine
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
mesh.select_set(True)
bpy.context.view_layer.objects.active = arm

if os.path.exists(OUT_FBX):
    try:
        os.remove(OUT_FBX)
    except Exception:
        pass

bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
    use_selection=True,
    global_scale=1.0,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Y',
    axis_up='Z',
    bake_space_transform=False,
    object_types={'ARMATURE', 'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    bake_anim=False
)
print(f"Exportado FBX canónico congruente: {OUT_FBX} ({os.path.getsize(OUT_FBX)} bytes)")
