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

    # 1. Calibrar Iluminacion de Estudio
    for obj in list(scene.collection.objects):
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

    # Key Area Light
    l1_data = bpy.data.lights.new("LGT_Key", 'AREA')
    l1_data.energy = 160.0
    l1_data.size = 2.0
    l1_data.color = (1.0, 0.98, 0.95)
    l1 = bpy.data.objects.new("LGT_Key", l1_data)
    l1.location = (1.6, -2.5, 2.0)
    l1.rotation_euler = (R(50), R(15), R(35))
    scene.collection.objects.link(l1)

    # Fill Area Light
    l2_data = bpy.data.lights.new("LGT_Fill", 'AREA')
    l2_data.energy = 75.0
    l2_data.size = 2.5
    l2_data.color = (0.75, 0.85, 1.0)
    l2 = bpy.data.objects.new("LGT_Fill", l2_data)
    l2.location = (-1.8, -2.0, 1.4)
    l2.rotation_euler = (R(55), R(-20), R(-40))
    scene.collection.objects.link(l2)

    # Rim Area Light Derecho
    l3_data = bpy.data.lights.new("LGT_RimR", 'AREA')
    l3_data.energy = 130.0
    l3_data.size = 1.8
    l3_data.color = (0.9, 0.95, 1.0)
    l3 = bpy.data.objects.new("LGT_RimR", l3_data)
    l3.location = (1.8, 1.8, 1.8)
    l3.rotation_euler = (R(-45), R(20), R(-135))
    scene.collection.objects.link(l3)

    # Rim Area Light Izquierdo (Violeta Neon de Acento)
    l4_data = bpy.data.lights.new("LGT_RimL", 'AREA')
    l4_data.energy = 180.0
    l4_data.size = 1.8
    l4_data.color = (0.70, 0.15, 1.0)
    l4 = bpy.data.objects.new("LGT_RimL", l4_data)
    l4.location = (-1.8, 1.8, 1.8)
    l4.rotation_euler = (R(-45), R(-20), R(135))
    scene.collection.objects.link(l4)

    # Top Ambient
    l5_data = bpy.data.lights.new("LGT_Top", 'AREA')
    l5_data.energy = 50.0
    l5_data.size = 2.5
    l5_data.color = (0.95, 0.98, 1.0)
    l5 = bpy.data.objects.new("LGT_Top", l5_data)
    l5.location = (0.0, -0.2, 3.2)
    l5.rotation_euler = (R(-15), 0, 0)
    scene.collection.objects.link(l5)

    # 2. Shader PBR Fluido Oscuro con Destellos Morados
    mat = bpy.data.materials.new(name="M_DarX_DarkFluid_PurpleSparks")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out_node = nt.nodes.new("ShaderNodeOutputMaterial")
    out_node.location = (1200, 0)

    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (850, 0)
    nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-900, 0)

    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-700, 0)
    mapping.inputs["Scale"].default_value = (3.5, 3.5, 1.8)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    voronoi = nt.nodes.new("ShaderNodeTexVoronoi")
    voronoi.location = (-450, 150)
    voronoi.feature = 'SMOOTH_F1'
    voronoi.inputs["Scale"].default_value = 6.2
    voronoi.inputs["Smoothness"].default_value = 0.8
    nt.links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = (-450, -150)
    noise.inputs["Scale"].default_value = 7.5
    noise.inputs["Detail"].default_value = 4.0
    noise.inputs["Roughness"].default_value = 0.48
    nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = 'FLOAT'
    mix.location = (-200, 0)
    mix.inputs["Factor"].default_value = 0.80
    nt.links.new(voronoi.outputs["Distance"], mix.inputs[2])
    nt.links.new(noise.outputs["Fac"], mix.inputs[3])

    cr_base = nt.nodes.new("ShaderNodeValToRGB")
    cr_base.location = (150, 150)
    cr_base.color_ramp.interpolation = 'LINEAR'
    cr_base.color_ramp.elements[0].position = 0.52
    cr_base.color_ramp.elements[0].color = (0.001, 0.001, 0.002, 1.0)
    cr_base.color_ramp.elements[1].position = 0.64
    cr_base.color_ramp.elements[1].color = (0.22, 0.0, 0.60, 1.0)
    e3 = cr_base.color_ramp.elements.new(0.76)
    e3.color = (0.68, 0.02, 1.0, 1.0)
    e4 = cr_base.color_ramp.elements.new(0.88)
    e4.color = (0.92, 0.05, 0.90, 1.0)
    e5 = cr_base.color_ramp.elements.new(0.96)
    e5.color = (0.98, 0.75, 1.0, 1.0)
    nt.links.new(mix.outputs["Result"], cr_base.inputs["Fac"])
    nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Base Color"])

    cr_emit = nt.nodes.new("ShaderNodeValToRGB")
    cr_emit.location = (150, -150)
    cr_emit.color_ramp.interpolation = 'B_SPLINE'
    cr_emit.color_ramp.elements[0].position = 0.65
    cr_emit.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    cr_emit.color_ramp.elements[1].position = 0.94
    cr_emit.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(mix.outputs["Result"], cr_emit.inputs["Fac"])

    math_emit = nt.nodes.new("ShaderNodeMath")
    math_emit.location = (450, -150)
    math_emit.operation = 'MULTIPLY'
    math_emit.inputs[1].default_value = 8.0
    nt.links.new(cr_emit.outputs["Color"], math_emit.inputs[0])
    nt.links.new(math_emit.outputs["Value"], bsdf.inputs["Emission Strength"])
    nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Emission Color"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (450, 50)
    bump.inputs["Strength"].default_value = 0.022
    bump.inputs["Distance"].default_value = 0.012
    nt.links.new(mix.outputs["Result"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.048
    bsdf.inputs["IOR"].default_value = 1.62
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 1.0
        bsdf.inputs["Coat Roughness"].default_value = 0.015
        if "Coat IOR" in bsdf.inputs:
            bsdf.inputs["Coat IOR"].default_value = 1.55

    char.data.materials.clear()
    char.data.materials.append(mat)

    # 3. Camara Fija Reutilizable
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

    # Renderizar las 5 Vistas Canonicas
    print("Renderizando Hero View...")
    render_shot((1.6, -3.0, 1.25), (0, 0, 0.90), 38, "darkfluid_hero_action.png")

    print("Renderizando Vista Frontal...")
    render_shot((0, -3.2, 0.90), (0, 0, 0.90), 38, "darkfluid_view_front.png")

    print("Renderizando Vista Trasera...")
    render_shot((0, 3.2, 0.90), (0, 0, 0.90), 38, "darkfluid_view_back.png")

    print("Renderizando Vista FPS...")
    render_shot((0.15, -0.10, 1.44), (0.35, -0.38, 1.14), 60, "darkfluid_view_fps.png")

    print("Renderizando Primer Plano Rostro...")
    render_shot((0.12, -0.72, 1.56), (0, 0, 1.54), 25, "darkfluid_face_closeup.png")

    # Guardar estado maestro en Player_Skin_Workspace
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    v10_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_V10.blend"
    bpy.ops.wm.save_as_mainfile(filepath=v10_path)
    print(f"BLENDS_SAVED: {blend_path} and {v10_path}")

if __name__ == "__main__":
    main()
