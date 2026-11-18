"""inspect_existing_fps_anims.py
Inspecciona si SK_FPS_Arms.fbx tiene animaciones incluidas o cómo están posicionados los brazos en archivos existentes.
"""
import os
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)

print("Acciones en SK_FPS_Arms.fbx:")
for a in bpy.data.actions:
    print(f"  Action: {a.name}, frames: {a.frame_range}")

# También buscar otros FBX de animación en Art/FBX
for root, dirs, files in os.walk(os.path.join(ART_DIR, "FBX")):
    for f in files:
        if f.endswith(".fbx") and "FPS" in f and "SMG" not in f:
            print(f"Encontrado FBX de FPS: {os.path.join(root, f)}")
