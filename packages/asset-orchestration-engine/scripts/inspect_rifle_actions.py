"""inspect_rifle_actions.py
Inspecciona las acciones y keyframes de todas las animaciones de rifle existentes.
"""
import os
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")

files = [
    os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Walk.fbx"),
    os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Run.fbx"),
    os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Fire.fbx"),
    os.path.join(ART_DIR, "FBX", "Anim_Player", "A_Player_Rifle_Fire.fbx"),
    os.path.join(ART_DIR, "FBX", "Anim_Player", "A_Player_Rifle_Idle.fbx")
]

for fpath in files:
    print("="*60)
    print(f"ARCHIVO: {os.path.basename(fpath)}")
    print("="*60)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fpath)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    act = arm.animation_data.action if arm.animation_data else None
    print(f"Armature: {arm.name}, Action: {act.name if act else 'None'}, FrameRange: {act.frame_range if act else 'None'}")
    
    # Imprimir huesos clave en frame 0
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    for bname in ['hand_R', 'hand_L', 'weapon', 'upperarm_R', 'upperarm_L']:
        pb = arm.pose.bones.get(bname)
        if pb:
            loc = (arm.matrix_world @ pb.matrix).to_translation()
            print(f"  Frame 0 - {bname:12s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")
