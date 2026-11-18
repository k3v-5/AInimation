"""test_player_camera_angles.py — Ajuste exacto de iluminación y cámaras para el render de 4 vistas.
"""

import sys, os, math
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
# PIL run from external script

OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
IMG_FINAL = os.path.join(OUT_DIR, "player_redesign_4views.png")
V1_PATH = os.path.join(OUT_DIR, "v1_front.png")
V2_PATH = os.path.join(OUT_DIR, "v2_back.png")
V3_PATH = os.path.join(OUT_DIR, "v3_action.png")
V4_PATH = os.path.join(OUT_DIR, "v4_fps.png")

R = math.radians
TAU = math.pi * 2

def setup_lights():
    for o in list(bpy.data.objects):
        if "Light" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

    # 1. Luz frontal potente (para ver peto, casco, visor y armas)
    l_front_data = bpy.data.lights.new("LightFront", 'AREA')
    l_front_data.energy = 2200
    l_front_data.size = 3.5
    l_front_data.color = (1.0, 1.0, 1.0)
    l_front = bpy.data.objects.new("LightFront", l_front_data)
    l_front.location = (1.5, -3.2, 2.2)
    l_front.rotation_euler = (R(55), 0, R(25))
    bpy.context.scene.collection.objects.link(l_front)

    # 2. Luz trasera potente con tinte violeta (para iluminar la exo-espina neural)
    l_back_data = bpy.data.lights.new("LightBack", 'AREA')
    l_back_data.energy = 2600
    l_back_data.size = 3.5
    l_back_data.color = (0.85, 0.20, 1.0)
    l_back = bpy.data.objects.new("LightBack", l_back_data)
    l_back.location = (-1.5, 3.2, 2.2)
    l_back.rotation_euler = (R(-55), 0, R(-155))
    bpy.context.scene.collection.objects.link(l_back)

    # 3. Luz lateral fría (relleno)
    l_fill_data = bpy.data.lights.new("LightFill", 'AREA')
    l_fill_data.energy = 800
    l_fill_data.size = 4.0
    l_fill_data.color = (0.60, 0.80, 1.0)
    l_fill = bpy.data.objects.new("LightFill", l_fill_data)
    l_fill.location = (-3.2, 0.0, 1.8)
    l_fill.rotation_euler = (R(15), R(60), 0)
    bpy.context.scene.collection.objects.link(l_fill)

def render_camera_view(cam_pos, target_pos, lens, out_path, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = cam_pos

    empty = bpy.data.objects.new("Target", None)
    scene.collection.objects.link(empty)
    empty.location = target_pos

    tt = cam.constraints.new('TRACK_TO')
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.camera = cam
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)

def main():
    sys.path.append(r"E:\Darx_Proyect\Art\Blender")
    import darx_player as dp
    import darx_fps as dfps

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    if scene.world:
        scene.world.use_nodes = True
        bg = scene.world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.08, 0.09, 0.12, 1.0)
            bg.inputs["Strength"].default_value = 0.9

    setup_lights()

    # 1. Construir SK_Player en colección dedicada
    col_p = bpy.data.collections.new("Col_Player")
    scene.collection.children.link(col_p)
    p_mesh, p_arm = dp.build_all(col=col_p)

    # Vista 1: Frontal (cámara en -Y)
    print("Renderizando Vista 1: Frontal...")
    render_camera_view((0.0, -3.2, 1.25), (0.0, 0.0, 1.10), 45.0, V1_PATH)

    # Vista 2: Trasera (cámara en +Y para ver la exo-espina dorsal)
    print("Renderizando Vista 2: Trasera...")
    render_camera_view((0.0, 3.2, 1.25), (0.0, 0.0, 1.10), 45.0, V2_PATH)

    # Vista 3: Acción 3/4 (cámara lateral-frontal)
    print("Renderizando Vista 3: Acción...")
    render_camera_view((2.4, -2.4, 1.40), (0.0, 0.0, 1.10), 40.0, V3_PATH)

    # Ocultar 3ª persona y construir FPS
    p_mesh.hide_render = True
    p_arm.hide_render = True

    col_fps = bpy.data.collections.new("Col_FPS")
    scene.collection.children.link(col_fps)
    fps_mesh, fps_arm = dfps.build_all(col=col_fps)

    # Vista 4: Primera Persona (FPS View - ajustada exactamente al punto de vista del jugador)
    print("Renderizando Vista 4: Primera Persona FPS...")
    # El arma está en GUN_POS = (0.098, -0.226, -0.088). La cámara mira hacia el frente (-Y).
    render_camera_view((0.0, 0.10, -0.04), (0.05, -0.45, -0.10), 30.0, V4_PATH)

    print("=== RENDERS GENERADOS CON ÉXITO ===")

if __name__ == "__main__":
    main()
