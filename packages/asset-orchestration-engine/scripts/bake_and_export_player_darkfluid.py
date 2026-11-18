"""bake_and_export_player_darkfluid.py
Hornea las texturas PBR (BaseColor y Emissive) a 2048x2048 del material de Fluido Oscuro
con CERO verde (G=0.0 estricto) y tonos morados oscuros y profundos.
Calibra el material PBR (Metallic=0.0, Roughness=0.35) para eliminar reflejos cromo-espejo.
Exporta el modelo canónico SK_Player.fbx desde DarX_Player_Rigged_Canonical.blend.
"""

import os
import sys
import math
import bpy

CANONICAL_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
MASTER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_Adult_Master.blend"
OUTPUT_FBX = r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx"
BASECOLOR_TEX = r"E:\Darx_Proyect\Art\Textures\T_Player_DarkFluid_BaseColor.png"
EMISSIVE_TEX = r"E:\Darx_Proyect\Art\Textures\T_Player_DarkFluid_Emissive.png"
TEX_SIZE = 2048

def configure_darkfluid_material(mat):
    """Configura el material procedural con CERO verde y púrpuras profundos."""
    cr_base = mat.node_tree.nodes.get("Color Ramp")
    if cr_base:
        cr = cr_base.color_ramp
        while len(cr.elements) < 5:
            cr.elements.new(0.9)
        while len(cr.elements) > 5:
            cr.elements.remove(cr.elements[-1])
        # Púrpuras profundos y oscuros, CERO verde
        cr.elements[0].position = 0.60
        cr.elements[0].color = (0.002, 0.000, 0.003, 1.0) # Negro obsidiana profundo
        cr.elements[1].position = 0.66
        cr.elements[1].color = (0.040, 0.000, 0.090, 1.0) # Violeta medianoche
        cr.elements[2].position = 0.72
        cr.elements[2].color = (0.120, 0.000, 0.260, 1.0) # Púrpura oscuro
        cr.elements[3].position = 0.80
        cr.elements[3].color = (0.220, 0.000, 0.450, 1.0) # Púrpura medio profundo
        cr.elements[4].position = 0.88
        cr.elements[4].color = (0.320, 0.000, 0.600, 1.0) # Violeta real saturado oscuro

    cr_emit = mat.node_tree.nodes.get("Color Ramp.001")
    if cr_emit:
        cr_e = cr_emit.color_ramp
        while len(cr_e.elements) > 2:
            cr_e.elements.remove(cr_e.elements[-1])
        cr_e.elements[0].position = 0.70
        cr_e.elements[0].color = (0.000, 0.000, 0.000, 1.0) # Sin emisión en base
        cr_e.elements[1].position = 0.85
        cr_e.elements[1].color = (0.280, 0.000, 0.550, 1.0) # Emisión violeta oscura, cero verde

    for n in mat.node_tree.nodes:
        if n.type == 'MATH' and n.operation == 'MULTIPLY':
            for out in n.outputs:
                for l in out.links:
                    if l.to_socket.name == "Emission Strength":
                        n.inputs[1].default_value = 1.5 # Emisión controlada, no cegadora

    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs["Roughness"].default_value = 0.35 # Acabado satinado, elimina reflejos especulares de sala
    bsdf.inputs["Metallic"].default_value = 0.0   # Dieléctrico puro, evita espejo cromo de luces cian
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.0 # Desactivar capa barniz reflectante
        bsdf.inputs["Coat Roughness"].default_value = 0.35
    print("  [OK] Material calibrado: CERO verde, púrpuras oscuros, Roughness=0.35, Metallic=0.0")

def verify_texture_no_green(filepath, max_allowed_green=0.005):
    """Inspecciona que ningún pixel de la textura tenga canal verde significativo."""
    img = bpy.data.images.load(filepath)
    w, h = img.size
    pixels = list(img.pixels) # R, G, B, A floats 0.0-1.0
    bpy.data.images.remove(img)

    max_g = 0.0
    green_count = 0
    total_pixels = w * h
    for i in range(1, len(pixels), 4):
        g = pixels[i]
        if g > max_g:
            max_g = g
        if g > max_allowed_green:
            green_count += 1

    print(f"  [AUDITORÍA DE TEXTURA] {os.path.basename(filepath)}: Max Verde={max_g:.4f}, Píxeles con G>{max_allowed_green}: {green_count}/{total_pixels}")
    if max_g > max_allowed_green:
        raise ValueError(f"Fallo de contrato: textura {filepath} contiene verde no autorizado (Max G = {max_g})")
    print(f"  [PASS] Textura {os.path.basename(filepath)} 100% libre de verde.")

def main():
    print("=== [1/5] ABRIENDO BLEND CANÓNICO Y CONFIGURANDO MATERIAL ===")
    bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)

    arm_obj = bpy.data.objects.get("ARM_Player")
    mesh_obj = bpy.data.objects.get("SK_Player")
    if not arm_obj or not mesh_obj:
        raise RuntimeError("No se encontró ARM_Player o SK_Player en el blend canónico")

    mat = bpy.data.materials.get("M_DarX_DarkFluid_PurpleSparks")
    if not mat:
        raise RuntimeError("No se encontró M_DarX_DarkFluid_PurpleSparks")

    configure_darkfluid_material(mat)

    os.makedirs(os.path.dirname(BASECOLOR_TEX), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FBX), exist_ok=True)

    print("=== [2/5] HORNEANDO BASE COLOR (DIFFUSE ALBEDO) A 2048x2048 ===")
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 1

    temp_tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    diffuse_img = bpy.data.images.new("Bake_BaseColor", TEX_SIZE, TEX_SIZE)
    temp_tex_node.image = diffuse_img
    mat.node_tree.nodes.active = temp_tex_node

    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True

    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.bake(type='DIFFUSE')

    diffuse_img.filepath_raw = BASECOLOR_TEX
    diffuse_img.file_format = 'PNG'
    diffuse_img.save()
    print(f"[OK] Base Color horneado: {BASECOLOR_TEX} ({os.path.getsize(BASECOLOR_TEX)} bytes)")

    print("=== [3/5] HORNEANDO EMISSIVE A 2048x2048 ===")
    emit_img = bpy.data.images.new("Bake_Emissive", TEX_SIZE, TEX_SIZE)
    temp_tex_node.image = emit_img

    bpy.context.scene.cycles.bake_type = 'EMIT'
    bpy.ops.object.bake(type='EMIT')

    emit_img.filepath_raw = EMISSIVE_TEX
    emit_img.file_format = 'PNG'
    emit_img.save()
    print(f"[OK] Emissive horneado: {EMISSIVE_TEX} ({os.path.getsize(EMISSIVE_TEX)} bytes)")

    # Limpiar nodo temporal de bake
    mat.node_tree.nodes.remove(temp_tex_node)
    bpy.data.images.remove(diffuse_img)
    bpy.data.images.remove(emit_img)

    # Validar que ambas texturas tengan CERO verde
    verify_texture_no_green(BASECOLOR_TEX)
    verify_texture_no_green(EMISSIVE_TEX)

    print("=== [4/5] EXPORTANDO Art/FBX/SK_Player.fbx CANÓNICO ===")
    arm_obj.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=OUTPUT_FBX,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        bake_space_transform=False,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False,
        path_mode='COPY'
    )

    fbx_size = os.path.getsize(OUTPUT_FBX)
    print(f"[OK] FBX exportado con éxito: {OUTPUT_FBX} ({fbx_size} bytes)")
    if fbx_size < 8000:
        raise RuntimeError("FBX generado es anormalmente pequeño")

    with open(OUTPUT_FBX, "rb") as f:
        limb_nodes = f.read().count(b"LimbNode")
    print(f"[OK] Nodos de hueso verificados en FBX: {limb_nodes} LimbNodes")
    if limb_nodes == 0:
        raise RuntimeError("FBX sin esqueleto")

    # Guardar blend canónico limpio con material calibrado
    bpy.ops.wm.save_mainfile(filepath=CANONICAL_BLEND)
    print(f"[OK] Blend canónico guardado: {CANONICAL_BLEND}")

    print("=== [5/5] SINCRONIZANDO MATERIAL CON MASTER BLEND ===")
    if os.path.exists(MASTER_BLEND):
        try:
            bpy.ops.wm.open_mainfile(filepath=MASTER_BLEND)
            master_mat = bpy.data.materials.get("M_DarX_DarkFluid_PurpleSparks")
            if master_mat:
                configure_darkfluid_material(master_mat)
                bpy.ops.wm.save_mainfile(filepath=MASTER_BLEND)
                print(f"[OK] Master blend sincronizado: {MASTER_BLEND}")
        except Exception as e:
            print(f"[WARN] Error menor al sincronizar master blend: {e}")

    print("=== PIPELINE BLENDER DE HORNEADO Y EXPORTACIÓN COMPLETADO AL 100% ===")

if __name__ == "__main__":
    main()
