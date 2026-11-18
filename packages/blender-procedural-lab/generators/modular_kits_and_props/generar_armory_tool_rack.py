"""
Art/Blender/generar_armory_tool_rack.py
=======================================
Genera en Blender 5.2 LTS el banco de armería y soporte ranurado industrial
(SM_Armory_Tool_Rack) acorde al prototipo aprobado Concept_03_AirlockRack_And_BlackoutCeiling.jpg
(estilo Industrial/Cartoon biselado, base Z=0.0 cm, franjas de peligro y cunas engomadas).
"""

import os
import sys
import math
import bpy

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import astra_blender_styling as abs_style

FBX_OUT = os.path.join("F:/Dev/Game/Art/FBX/Props", "SM_Armory_Tool_Rack.fbx")
BLEND_OUT = os.path.join("F:/Dev/Game/Art/Blender", "SM_Armory_Tool_Rack.blend")
os.makedirs(os.path.dirname(FBX_OUT), exist_ok=True)


def build_armory_tool_rack():
    abs_style.reset_comic_scene(bg_color=(0.03, 0.035, 0.045, 1.0), bg_strength=0.4)
    col = abs_style.create_collection("ArmoryToolRack")

    mat_steel = abs_style.get_comic_material("M_DarkTitanium", base_color=(0.14, 0.16, 0.19), roughness=0.35, metallic=0.82)
    mat_rubber = abs_style.get_comic_material("M_RubberBlack", base_color=(0.06, 0.06, 0.07), roughness=0.85, metallic=0.05)
    mat_yellow = abs_style.get_comic_material("M_HazardYellow", base_color=(0.95, 0.70, 0.06), roughness=0.32, metallic=0.12)
    mat_chrome = abs_style.get_comic_material("M_ChromeSteel", base_color=(0.82, 0.85, 0.88), roughness=0.18, metallic=0.95)
    mat_brass = abs_style.get_comic_material("Mat_Machinery_Brass", base_color=(0.88, 0.68, 0.18), roughness=0.25, metallic=0.90)

    root = bpy.data.objects.new("Root_SM_Armory_Tool_Rack", None)
    root.location = (0, 0, 0)
    col.objects.link(root)

    parts = []
    # 1. Estructura de banco pesado (2.20 m ancho Y, 0.72 m fondo X, 0.56 m altura mesa Z)
    # Frente mirando hacia +X (el personaje mira desde +X hacia el respaldo en -X)
    frame_legs = [
        (-0.28, -0.96), (-0.28, 0.0), (-0.28, 0.96),
        (0.28, -0.96), (0.28, 0.0), (0.28, 0.96),
    ]
    for idx, (lx, ly) in enumerate(frame_legs):
        leg = abs_style.create_box(f"Bench_Leg_{idx}", size=(0.10, 0.10, 0.50), bevel_w=0.012,
                                   loc=(lx, ly, 0.25), mat=mat_steel, col=col)
        leg.parent = root
        parts.append(leg)
        foot = abs_style.create_box(f"Bench_Foot_{idx}", size=(0.14, 0.14, 0.03), bevel_w=0.008,
                                    loc=(lx, ly, 0.015), mat=mat_rubber, col=col)
        foot.parent = root
        parts.append(foot)

    # Travesaños inferiores de refuerzo
    for sy in (-0.96, 0.0, 0.96):
        brace = abs_style.create_box(f"Bench_CrossBrace_{sy:.2f}", size=(0.56, 0.07, 0.07), bevel_w=0.01,
                                     loc=(0.0, sy, 0.12), mat=mat_steel, col=col)
        brace.parent = root
        parts.append(brace)

    long_rail_f = abs_style.create_box("Bench_LowerRailF", size=(0.07, 2.02, 0.07), bevel_w=0.01,
                                       loc=(0.28, 0.0, 0.12), mat=mat_steel, col=col)
    long_rail_b = abs_style.create_box("Bench_LowerRailB", size=(0.07, 2.02, 0.07), bevel_w=0.01,
                                       loc=(-0.28, 0.0, 0.12), mat=mat_steel, col=col)
    for r in (long_rail_f, long_rail_b):
        r.parent = root
        parts.append(r)

    # Cubierta superior del banco con borde amarillo de seguridad (Z = 0.50 .. 0.57 m)
    bench_top = abs_style.create_box("Bench_TopDeck", size=(0.72, 2.18, 0.07), bevel_w=0.015,
                                     loc=(0.0, 0.0, 0.535), mat=mat_steel, col=col)
    bench_pad = abs_style.create_box("Bench_RubberMat", size=(0.60, 2.04, 0.02), bevel_w=0.008,
                                     loc=(0.03, 0.0, 0.575), mat=mat_rubber, col=col)
    trim_front = abs_style.create_box("Bench_YellowTrimF", size=(0.025, 2.18, 0.045), bevel_w=0.006,
                                      loc=(0.365, 0.0, 0.535), mat=mat_yellow, col=col)
    for o in (bench_top, bench_pad, trim_front):
        o.parent = root
        parts.append(o)

    # 2. Panel ranurado vertical trasero (Z = 0.56 .. 1.44 m)
    backboard = abs_style.create_box("Rack_Backboard", size=(0.10, 2.16, 0.88), bevel_w=0.02,
                                     loc=(-0.30, 0.0, 1.00), mat=mat_steel, col=col)
    backboard.parent = root
    parts.append(backboard)

    # Moldura superior e inferior amarilla de advertencia + bloques negros alternados
    for bar_z, bar_name in [(1.41, "TopBar"), (0.61, "BotBar")]:
        y_bar = abs_style.create_box(f"Rack_{bar_name}", size=(0.115, 2.14, 0.06), bevel_w=0.008,
                                     loc=(-0.295, 0.0, bar_z), mat=mat_yellow, col=col)
        y_bar.parent = root
        parts.append(y_bar)
        for idx, hy in enumerate([-0.90, -0.60, -0.30, 0.0, 0.30, 0.60, 0.90]):
            blk = abs_style.create_box(f"Rack_{bar_name}_Blk_{idx}", size=(0.122, 0.12, 0.062), bevel_w=0.004,
                                       loc=(-0.295, hy, bar_z), mat=mat_rubber, col=col)
            blk.parent = root
            parts.append(blk)

    # Ranuras horizontales empotradas en la pared del panel
    for rz in (0.78, 0.94, 1.10, 1.26):
        slot_rib = abs_style.create_box(f"Rack_SlotChannel_{rz:.2f}", size=(0.03, 1.96, 0.03), bevel_w=0.004,
                                        loc=(-0.24, 0.0, rz), mat=mat_rubber, col=col)
        slot_rib.parent = root
        parts.append(slot_rib)

    # 3. Cunas U-Hooks para hacha / cañones en pared y abrazadera de cilindro
    for hy, hz in [(-0.78, 0.94), (-0.30, 0.94), (0.35, 1.10), (0.78, 1.10)]:
        hook_arm = abs_style.create_box(f"Rack_HookArm_{hy:.2f}", size=(0.13, 0.045, 0.04), bevel_w=0.006,
                                        loc=(-0.18, hy, hz), mat=mat_yellow, col=col)
        hook_tip = abs_style.create_box(f"Rack_HookTip_{hy:.2f}", size=(0.035, 0.045, 0.08), bevel_w=0.006,
                                        loc=(-0.12, hy, hz + 0.02), mat=mat_yellow, col=col)
        hook_bolt = abs_style.create_cylinder(f"Rack_HookBolt_{hy:.2f}", radius=0.015, depth=0.03, segments=6,
                                              rot=(0, math.radians(90), 0), loc=(-0.23, hy, hz), mat=mat_brass, col=col)
        for h_part in (hook_arm, hook_tip, hook_bolt):
            h_part.parent = root
            parts.append(h_part)

    # Abrazadera lateral cromada para botella de extintor vertical en lado derecho (Y = +0.76)
    clamp_ring = abs_style.create_torus("Rack_CylinderClamp", major_r=0.115, minor_r=0.018,
                                        loc=(-0.15, 0.78, 0.88), mat=mat_chrome, col=col)
    clamp_ring.parent = root
    parts.append(clamp_ring)

    # Unir todo en SM_Armory_Tool_Rack con pivote base Z=0.0
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()

    joined = bpy.context.active_object
    joined.name = "SM_Armory_Tool_Rack"
    joined.parent = None
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Normalizar Z min = 0.0 y centrado XY
    min_z = min(v.co.z for v in joined.data.vertices)
    for v in joined.data.vertices:
        v.co.z -= min_z
    joined.data.update()

    # Colisión simple UCX para no atrapar al jugador en bordes
    ucx = abs_style.create_box("UCX_SM_Armory_Tool_Rack_01", size=(0.74, 2.20, 1.44),
                               loc=(0.0, 0.0, 0.72), bevel=False, col=col)
    ucx.parent = None

    bpy.ops.object.select_all(action='DESELECT')
    joined.select_set(True)
    ucx.select_set(True)
    bpy.context.view_layer.objects.active = joined

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE',
    )
    print(f"[OK] SM_Armory_Tool_Rack exportado -> {FBX_OUT}")


if __name__ == "__main__":
    build_armory_tool_rack()
