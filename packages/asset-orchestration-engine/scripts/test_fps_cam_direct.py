"""test_fps_cam_direct.py
Prueba encuadre FPS directo con rotation_euler fijo (sin Track-To).
"""
import bpy
import math
import shutil

# Usar test_fps_5poses
import sys
sys.path.append(r"E:\Darx_Proyect\Tools\AssetEngine\scripts")
import test_fps_5poses

scene = bpy.context.scene
cam = scene.camera

# Quitar cualquier constraint de la cámara
cam.constraints.clear()
cam.data.lens = 18
cam.location = (0.01, 0.24, 0.06)
cam.rotation_euler = (math.radians(88), 0, math.radians(180))

out_p = r"E:\Darx_Proyect\Art\Blender\test_fps_cam_direct.png"
scene.render.filepath = out_p
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_p, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_cam_direct.png")
print("Rendered test_fps_cam_direct.png")
