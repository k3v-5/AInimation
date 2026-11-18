import bpy
import os
import sys
from mathutils import Vector, Euler
from math import radians as R

def main():
    blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_LatexHuman_V2.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    char = bpy.data.objects.get("SK_DarX_LatexHuman_Eyeless")
    arm = bpy.data.objects.get("Armature")

    # 1. Calibrar Iluminacion de Estudio Difusa
    for obj in list(scene.collection.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Key Area Light
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 180.0
    l1_data.size = 2.0
    l1_data.color = (1.0, 0.98, 0.95)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (1.6, -2.5, 2.0)
    l1.rotation_euler = (R(50), R(15), R(35))
    scene.collection.objects.link(l1)

    # Fill Area Light
    l2_data = bpy.data.lights.new("LGT_Fill", 'AREA')
    l2_data.energy = 90.0
    l2_data.size = 2.5
    l2_data.color = (0.75, 0.85, 1.0)
    l2 = bpy.data.objects.new("LGT_Fill", l2_data)
    l2.location = (-1.8, -2.0, 1.4)
    l2.rotation_euler = (R(55), R(-20), R(-40))
    scene.collection.objects.link(l2)

    # Rim Area Light Derecho
    l3_data = bpy.data.lights.new("LGT_RimR", 'AREA')
    l3_data.energy = 140.0
    l3_data.size = 1.8
    l3_data.color = (0.9, 0.95, 1.0)
    l3 = bpy.data.objects.new("LGT_RimR", l3_data)
    l3.location = (1.8, 1.8, 1.8)
    l3.rotation_euler = (R(-45), R(20), R(-135))
    scene.collection.objects.link(l3)

    # Rim Area Light Izquierdo (Violeta Neon)
    l4_data = bpy.data.lights.new("LGT_RimL", 'AREA')
    l4_data.energy = 160.0
    l4_data.size = 1.8
    l4_data.color = (0.65, 0.20, 1.0)
    l4 = bpy.data.objects.new("LGT_RimL", l4_data)
    l4.location = (-1.8, 1.8, 1.8)
    l4.rotation_euler = (R(-45), R(-20), R(135))
    scene.collection.objects.link(l4)

    # Top Accent
    l5_data = bpy.data.lights.new("LGT_Top", 'AREA')
    l5_data.energy = 60.0
    l5_data.size = 2.5
    l5_data.color = (0.95, 0.98, 1.0)
    l5 = bpy.data.objects.new("LGT_Top", l5_data)
    l5.location = (0.0, -0.2, 3.2)
    l5.rotation_euler = (R(-15), 0, 0)
    scene.collection.objects.link(l5)

    # 2. Shader PBR Latex Negro Obsidiana
    mat = char.data.materials[0]
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.008, 0.008, 0.012, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.0
        bsdf.inputs['Roughness'].default_value = 0.16
        bsdf.inputs['IOR'].default_value = 1.50
        if 'Coat Weight' in bsdf.inputs:
            bsdf.inputs['Coat Weight'].default_value = 0.90
            bsdf.inputs['Coat Roughness'].default_value = 0.08
            if 'Coat IOR' in bsdf.inputs:
                bsdf.inputs['Coat IOR'].default_value = 1.52

    # 3. Camara fija reutilizable
    cam_obj = bpy.data.objects.get("Cam_RenderMaster")
    if not cam_obj:
        cam_data = bpy.data.cameras.new("Cam_RenderMaster")
        cam_obj = bpy.data.objects.new("Cam_RenderMaster", cam_data)
        scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.engine = 'BLENDER_EEVEE'

    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_latex_human"
    os.makedirs(out_dir, exist_ok=True)

    def render_shot(loc, target, fov, fname):
        cam_obj.location = Vector(loc)
        dir_vec = Vector(target) - cam_obj.location
        cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
        cam_obj.data.angle = R(fov)
        p = os.path.join(out_dir, fname)
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print(f"RENDERED: {fname}")
        return p

    # 1. Hero View 3/4 Accion
    render_shot((1.6, -3.0, 1.25), (0, 0, 0.90), 38, "latex_hero_action.png")

    # 2. Vista Frontal Completa
    render_shot((0, -3.2, 0.90), (0, 0, 0.90), 38, "latex_view_front.png")

    # 3. Vista Trasera Completa
    render_shot((0, 3.2, 0.90), (0, 0, 0.90), 38, "latex_view_back.png")

    # 4. Vista FPS (Mano 5 dedos y antebrazo en guardia)
    render_shot((0.15, -0.10, 1.44), (0.35, -0.38, 1.14), 60, "latex_view_fps.png")

    # 5. Primer Plano Rostro Eyeless
    render_shot((0.12, -0.72, 1.56), (0, 0, 1.54), 25, "latex_face_closeup.png")

    # Guardar cambios en el blend
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print(f"BLEND_SAVED: {blend_path}")

if __name__ == "__main__":
    main()
