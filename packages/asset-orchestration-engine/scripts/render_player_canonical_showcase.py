"""render_player_canonical_showcase.py
Renderiza el escaparate definitivo del protagonista adulto de DarX
(Fluido Oscuro con Destellos Morados) aparejado a ARM_Player en 4 cuadrantes HD.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Euler

BLEND_PATH = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
IMG_4QUADRANTS = os.path.join(OUT_DIR, "preview_player_canonical_4quadrants.png")

R = math.radians

def setup_studio():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    # Eliminar luces viejas si existen
    for o in list(scene.collection.objects):
        if o.type == 'LIGHT' or o.type == 'CAMERA':
            bpy.data.objects.remove(o, do_unlink=True)

    # Suelo reflectante
    mesh_floor = bpy.data.meshes.new("Floor")
    obj_floor = bpy.data.objects.new("Studio_Floor", mesh_floor)
    scene.collection.objects.link(obj_floor)

    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=15.0)
    bm.to_mesh(mesh_floor)
    bm.free()

    mat_floor = bpy.data.materials.new("M_Floor_Dark")
    mat_floor.use_nodes = True
    bsdf_f = mat_floor.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.015, 0.015, 0.02, 1.0)
        bsdf_f.inputs['Metallic'].default_value = 0.8
        bsdf_f.inputs['Roughness'].default_value = 0.2
    mesh_floor.materials.append(mat_floor)

    # 1. Key Light Frontal Derecha (Cálida Blanca)
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 160.0
    l1_data.size = 2.2
    l1_data.color = (1.0, 0.98, 0.95)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (1.8, -2.8, 2.2)
    l1.rotation_euler = (R(50), R(15), R(35))
    scene.collection.objects.link(l1)

    # 2. Fill Light Frontal Izquierda (Azulada suave)
    l2_data = bpy.data.lights.new("LGT_Fill", 'AREA')
    l2_data.energy = 75.0
    l2_data.size = 2.8
    l2_data.color = (0.7, 0.85, 1.0)
    l2 = bpy.data.objects.new("LGT_Fill", l2_data)
    l2.location = (-2.0, -2.2, 1.6)
    l2.rotation_euler = (R(55), R(-20), R(-40))
    scene.collection.objects.link(l2)

    # 3. Rim Light Trasera Derecha
    l3_data = bpy.data.lights.new("LGT_RimR", 'AREA')
    l3_data.energy = 140.0
    l3_data.size = 2.0
    l3_data.color = (0.9, 0.95, 1.0)
    l3 = bpy.data.objects.new("LGT_RimR", l3_data)
    l3.location = (2.0, 2.0, 2.0)
    l3.rotation_euler = (R(-45), R(20), R(-135))
    scene.collection.objects.link(l3)

    # 4. Rim Light Acento Violeta Neón (Resalta los destellos morados)
    l4_data = bpy.data.lights.new("LGT_RimViolet", 'AREA')
    l4_data.energy = 220.0
    l4_data.size = 2.0
    l4_data.color = (0.75, 0.10, 1.0)
    l4 = bpy.data.objects.new("LGT_RimViolet", l4_data)
    l4.location = (-2.2, 2.0, 1.9)
    l4.rotation_euler = (R(-45), R(-20), R(135))
    scene.collection.objects.link(l4)

    # 5. Top Light Cenital
    l5_data = bpy.data.lights.new("LGT_Top", 'AREA')
    l5_data.energy = 50.0
    l5_data.size = 2.5
    l5_data.color = (0.95, 0.98, 1.0)
    l5 = bpy.data.objects.new("LGT_Top", l5_data)
    l5.location = (0.0, -0.2, 3.5)
    l5.rotation_euler = (R(-15), 0, 0)
    scene.collection.objects.link(l5)

def render_shot(cam_obj, loc, target, fov, fname):
    scene = bpy.context.scene
    cam_obj.location = Vector(loc)
    dir_vec = Vector(target) - cam_obj.location
    cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.data.angle = R(fov)
    p = os.path.join(OUT_DIR, fname)
    scene.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print(f"RENDERED: {fname}")
    return p

def main():
    print("=== [1/4] CARGANDO ARCHIVO CANÓNICO Y CONFIGURANDO ESTUDIO ===")
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    scene = bpy.context.scene

    arm = bpy.data.objects.get("ARM_Player")
    mesh = bpy.data.objects.get("SK_Player")

    setup_studio()

    cam_data = bpy.data.cameras.new("Cam_Render")
    cam_obj = bpy.data.objects.new("Cam_Render", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    print("=== [2/4] RENDERIZANDO VISTAS ORTOGONALES Y PRIMER PLANO ===")
    # 1. Vista Frontal (Adulto 1.82m)
    v_front = render_shot(cam_obj, (0, -3.5, 0.95), (0, 0, 0.95), 40, "canon_view_front.png")

    # 2. Vista Trasera (Espalda V-Taper y Deltoides)
    v_back = render_shot(cam_obj, (0, 3.5, 0.95), (0, 0, 0.95), 40, "canon_view_back.png")

    # 3. Primer plano del rostro y pecho (Detalle destellos morados)
    v_face = render_shot(cam_obj, (0.2, -1.0, 1.62), (0, 0, 1.58), 35, "canon_view_face.png")

    print("=== [3/4] APLICANDO ANIMACIÓN DE COMBATE Y RENDERIZANDO ACCIÓN ===")
    # Aplicar animación de combate / bash
    anim_fbx = r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Bash.fbx"
    if os.path.exists(anim_fbx):
        bpy.ops.import_scene.fbx(filepath=anim_fbx)
        anim_arm = [o for o in bpy.data.objects if o.name.startswith('ARM_Player.')][0]
        arm.animation_data_create()
        arm.animation_data.action = anim_arm.animation_data.action
        bpy.data.objects.remove(anim_arm, do_unlink=True)
        scene.frame_set(10)
        bpy.context.view_layer.update()

    # 4. Vista de Acción 3/4
    v_action = render_shot(cam_obj, (1.8, -3.2, 1.35), (0, 0, 0.95), 40, "canon_view_action.png")

    print("=== [4/4] RENDERIZADO COMPLETADO CON ÉXITO ===")
    print(f"VISTAS: {v_front}, {v_back}, {v_action}, {v_face}")

if __name__ == "__main__":
    main()
