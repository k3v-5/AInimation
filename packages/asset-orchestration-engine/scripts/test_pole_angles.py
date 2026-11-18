"""test_pole_angles.py
Prueba empírica de ángulos de polo en Two-Bone IK para encontrar el codo anatómico exacto.
"""
import os
import math
import bpy
from mathutils import Vector

PROJECT_ROOT = r"E:\Darx_Proyect"
BLENDER_DIR = os.path.join(PROJECT_ROOT, "Art", "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
BLEND_PATH = os.path.join(PROJECT_ROOT, "Saved", "Player_Skin_Workspace", "DarX_Player_Rigged_Canonical.blend")

for test_angle in [-90, 0, 90, 180]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    scene = bpy.context.scene

    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

    # Alinear huesos a la geometría A-pose
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones

    eb['upperarm_R'].head = Vector((0.228, -0.010, 1.520))
    eb['upperarm_R'].tail = Vector((0.550, 0.020, 1.250))
    eb['forearm_R'].head = Vector((0.550, 0.020, 1.250))
    eb['forearm_R'].tail = Vector((0.860, 0.045, 0.950))
    eb['hand_R'].head = Vector((0.860, 0.045, 0.950))
    eb['hand_R'].tail = Vector((0.950, 0.045, 0.850))

    eb['upperarm_L'].head = Vector((-0.228, -0.010, 1.520))
    eb['upperarm_L'].tail = Vector((-0.550, 0.020, 1.250))
    eb['forearm_L'].head = Vector((-0.550, 0.020, 1.250))
    eb['forearm_L'].tail = Vector((-0.860, 0.045, 0.950))
    eb['hand_L'].head = Vector((-0.860, 0.045, 0.950))
    eb['hand_L'].tail = Vector((-0.950, 0.045, 0.850))

    bpy.ops.object.mode_set(mode='OBJECT')

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

    bpy.ops.object.mode_set(mode='POSE')
    pb_hr = arm.pose.bones['hand_R']

    # Diana de mano derecha al frente del pecho
    target_R = bpy.data.objects.new("Target_R", None)
    target_R.location = Vector((0.18, -0.35, 1.25))
    scene.collection.objects.link(target_R)

    # Pole target lateral exterior
    pole_R = bpy.data.objects.new("Pole_R", None)
    pole_R.location = Vector((0.70, 0.10, 1.20))
    scene.collection.objects.link(pole_R)

    ik = pb_hr.constraints.new('IK')
    ik.target = target_R
    ik.pole_target = pole_R
    ik.pole_angle = math.radians(test_angle)
    ik.chain_count = 2

    bpy.context.view_layer.update()

    # Evaluar posición del codo (forearm_R head)
    mw_elbow = arm.matrix_world @ arm.pose.bones['forearm_R'].matrix
    elbow_loc = mw_elbow.to_translation()
    print(f"Angle {test_angle:+4d}° -> Elbow Loc: ({elbow_loc.x:.3f}, {elbow_loc.y:.3f}, {elbow_loc.z:.3f})")
