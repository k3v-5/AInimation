import bpy
import math
from mathutils import Vector, Euler

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

def test_bone(bname):
    print(f"\n--- Probando {bname} ---")
    base_loc = (arm_obj.matrix_world @ pb[bname].matrix).to_translation()
    print(f"Base location: {base_loc}")
    
    # Probar X
    for ang in [-45, 45]:
        pb[bname].rotation_euler = Euler((math.radians(ang), 0, 0))
        bpy.context.view_layer.update()
        loc = (arm_obj.matrix_world @ pb[bname].matrix).to_translation()
        child_loc = (arm_obj.matrix_world @ pb['hand_r' if '_r' in bname else 'hand_l'].matrix).to_translation()
        print(f"  Rot X={ang:+d}° -> hand pos: ({child_loc.x:.3f}, {child_loc.y:.3f}, {child_loc.z:.3f})")

    # Probar Y
    for ang in [-45, 45]:
        pb[bname].rotation_euler = Euler((0, math.radians(ang), 0))
        bpy.context.view_layer.update()
        child_loc = (arm_obj.matrix_world @ pb['hand_r' if '_r' in bname else 'hand_l'].matrix).to_translation()
        print(f"  Rot Y={ang:+d}° -> hand pos: ({child_loc.x:.3f}, {child_loc.y:.3f}, {child_loc.z:.3f})")

    # Probar Z
    for ang in [-45, 45]:
        pb[bname].rotation_euler = Euler((0, 0, math.radians(ang)))
        bpy.context.view_layer.update()
        child_loc = (arm_obj.matrix_world @ pb['hand_r' if '_r' in bname else 'hand_l'].matrix).to_translation()
        print(f"  Rot Z={ang:+d}° -> hand pos: ({child_loc.x:.3f}, {child_loc.y:.3f}, {child_loc.z:.3f})")

test_bone('upperarm_r')
test_bone('lowerarm_r')
test_bone('upperarm_l')
test_bone('lowerarm_l')
