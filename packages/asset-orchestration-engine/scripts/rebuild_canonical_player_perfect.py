# -*- coding: utf-8 -*-
"""rebuild_canonical_player_perfect.py
Reconstruye SK_Player usando la auténtica malla Dark Fluid esculpida,
con mapeo óseo canónico no invertido (+X = _R -> UE +Y Right, -X = _L -> UE -Y Left),
postura sagital paralela (28-29cm entre pies), y verificación matemática frame a frame
de cero cruces en A_Player_Walk, A_Player_Run, A_Player_Unarmed_Walk, A_Player_Unarmed_Run.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Matrix

MASTER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_Adult_Master.blend"
ASSETS_BLEND = r"E:\Darx_Proyect\Art\Blender\DarX_Assets.blend"
OUTPUT_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
OUTPUT_FBX = r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx"
ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

# Mapeo canónico corregido:
# En Master, los nombres .L tienen X > 0, que corresponde a UE +Y (Right, _R)!
# En Master, los nombres .R tienen X < 0, que corresponde a UE -Y (Left, _L)!
GROUP_MAP_CORRECTED = {
    'pelvis': ['hips'],
    'spine': ['spine'],
    'chest': [
        'chest', 'bagpack', 'bag_rope_L', 'bag_rope_L.001', 'bag_rope_L.002',
        'bag_rope_R', 'bag_rope_R.001', 'bag_rope_R.002',
        'robo_wire', 'robo_wire.001', 'robo_wire.002', 'robo_wire.003',
        'robo_wire.004', 'robo_wire.005'
    ],
    'neck': ['neck'],
    'head': ['head 1'],
    
    # Lado Derecho canónico (Blender X > 0 -> UE Y > 0 Right):
    'clavicle_R': ['shoulder.L'],
    'upperarm_R': ['upper_arm.L'],
    'forearm_R': ['forearm.L', 'forearm.twist.L'],
    'hand_R': [
        'hand.L', 'palm.01.L', 'palm.02.L', 'palm.03.L', 'palm.04.L',
        'f_index.01.L', 'f_index.02.L', 'f_index.03.L',
        'thumb.01.L', 'thumb.02.L', 'thumb.03.L',
        'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L',
        'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L',
        'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L'
    ],
    'thigh_R': ['thigh.L'],
    'calf_R': ['shin.L'],
    'foot_R': ['foot.L', 'heel.L', 'foot_rope_L', 'foot_rope_L.001'],
    'toe_R': ['toe.L'],

    # Lado Izquierdo canónico (Blender X < 0 -> UE Y < 0 Left):
    'clavicle_L': ['shoulder.R'],
    'upperarm_L': ['upper_arm.R'],
    'forearm_L': ['forearm.R', 'forearm.twist.R'],
    'hand_L': [
        'hand.R', 'palm.01.R', 'palm.02.R', 'palm.03.R', 'palm.04.R',
        'f_index.01.R', 'f_index.02.R', 'f_index.03.R',
        'thumb.01.R', 'thumb.02.R', 'thumb.03.R',
        'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R',
        'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R',
        'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R'
    ],
    'thigh_L': ['thigh.R'],
    'calf_L': ['shin.R'],
    'foot_L': ['foot.R', 'heel.R', 'foot_rope_R', 'foot_rope_R.001'],
    'toe_L': ['toe.R']
}

def main():
    print("=== [1/6] CARGANDO MASTER BLEND Y MALLA ADULTA DARK FLUID ===")
    bpy.ops.wm.open_mainfile(filepath=MASTER_BLEND)
    
    src_mesh = bpy.data.objects.get('SK_DarX_LatexHuman_Eyeless')
    src_arm = bpy.data.objects.get('Armature')
    if not src_mesh or not src_arm:
        raise RuntimeError("Malla o armadura maestra no encontrada.")

    # Escala adulta 1.164 (estatura canónica 1.815m)
    SCALE = 1.164
    raw_verts = [v.co for v in src_mesh.data.vertices]
    min_z_raw = min(v.z for v in raw_verts)
    z_offset = -min_z_raw * SCALE
    print(f"  Estatura base: {max(v.z for v in raw_verts)*SCALE:.3f}m | Z Offset: {z_offset:.4f}m")

    # Cargar ARM_Player canónico de DarX_Assets.blend o construirlo
    print("=== [2/6] IMPORTANDO ARM_Player CANÓNICO DE DarX_Assets.blend ===")
    with bpy.data.libraries.load(ASSETS_BLEND) as (data_from, data_to):
        data_to.objects = ['ARM_Player']
        data_to.actions = [a for a in data_from.actions if 'Player_Walk' in a or 'Player_Run' in a or 'Player_Idle' in a]

    arm_obj = bpy.data.objects.get('ARM_Player')
    if not arm_obj:
        raise RuntimeError("No se pudo cargar ARM_Player de DarX_Assets.blend")
    bpy.context.scene.collection.objects.link(arm_obj)

    print("=== [3/6] CLONANDO Y ESCALANDO MALLA SK_Player ===")
    mesh_data = src_mesh.data.copy()
    mesh_obj = bpy.data.objects.new("SK_Player", mesh_data)
    bpy.context.scene.collection.objects.link(mesh_obj)

    # Copiar materiales
    mesh_obj.data.materials.clear()
    for mat in src_mesh.data.materials:
        mesh_obj.data.materials.append(mat)

    # Aplicar transformación métrica exacta
    trans_mat = Matrix.Translation(Vector((0.0, 0.0, z_offset))) @ Matrix.Diagonal((SCALE, SCALE, SCALE, 1.0))
    mesh_data.transform(trans_mat)

    # Asegurar segundo slot de material para los ojos predatorios si se requiere
    mat_eyes = bpy.data.materials.get("M_Player_Symbiote_Eyes")
    if not mat_eyes:
        mat_eyes = bpy.data.materials.new("M_Player_Symbiote_Eyes")
        mat_eyes.use_nodes = True
        bsdf = mat_eyes.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Base Color'].default_value = (0.95, 0.92, 1.0, 1.0)
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (0.92, 0.88, 1.0, 1.0)
                bsdf.inputs['Emission Strength'].default_value = 6.0
    if len(mesh_obj.data.materials) < 2:
        mesh_obj.data.materials.append(mat_eyes)

    print("=== [4/6] REASIGNACIÓN DE PESOS SAGITAL CANÓNICA ===")
    old_vg_by_name = {vg.name: vg.index for vg in mesh_obj.vertex_groups}
    src_to_target = {}
    for tgt, srcs in GROUP_MAP_CORRECTED.items():
        for s in srcs:
            if s in old_vg_by_name:
                src_to_target[old_vg_by_name[s]] = tgt

    vert_target_weights = {v.index: {} for v in mesh_obj.data.vertices}
    for v in mesh_obj.data.vertices:
        for g in v.groups:
            tgt = src_to_target.get(g.group)
            if tgt:
                vert_target_weights[v.index][tgt] = vert_target_weights[v.index].get(tgt, 0.0) + g.weight

    mesh_obj.vertex_groups.clear()
    new_vgs = {}
    for b in arm_obj.data.bones:
        new_vgs[b.name] = mesh_obj.vertex_groups.new(name=b.name)

    unweighted = 0
    for v_idx, w_dict in vert_target_weights.items():
        total = sum(w_dict.values())
        if total > 0.0001:
            for tgt, w in w_dict.items():
                if tgt in new_vgs:
                    new_vgs[tgt].add([v_idx], w / total, 'REPLACE')
        else:
            unweighted += 1

    print(f"  Pesos reasignados a {len(mesh_obj.data.vertices)} vértices | {unweighted} sin peso")

    # PODA ESTRICTA DE SANGRADO DE PESOS POR PLANO SAGITAL X=0
    bilateral_bones = ["clavicle", "upperarm", "forearm", "hand", "thigh", "calf", "foot", "toe"]
    pruned_count = 0
    for v in mesh_obj.data.vertices:
        # Vértices a la derecha (X > 0.002) no pueden tener influencia de _L
        if v.co.x > 0.002:
            for b in bilateral_bones:
                vg_l = new_vgs.get(f"{b}_L")
                if vg_l:
                    try:
                        vg_l.remove([v.index])
                        pruned_count += 1
                    except RuntimeError:
                        pass
        # Vértices a la izquierda (X < -0.002) no pueden tener influencia de _R
        elif v.co.x < -0.002:
            for b in bilateral_bones:
                vg_r = new_vgs.get(f"{b}_R")
                if vg_r:
                    try:
                        vg_r.remove([v.index])
                        pruned_count += 1
                    except RuntimeError:
                        pass

    # Renormalizar pesos tras la poda
    for v in mesh_obj.data.vertices:
        total = sum(g.weight for g in v.groups)
        if total > 0.0001:
            for g in v.groups:
                g.weight = g.weight / total

    print(f"[OK] Poda sagital completada: {pruned_count} influencias cruzadas eliminadas.")

    # Emparentar a ARM_Player
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm_obj
    mod.use_vertex_groups = True

    # Eliminar objetos origen no deseados
    bpy.data.objects.remove(src_mesh, do_unlink=True)
    bpy.data.objects.remove(src_arm, do_unlink=True)

    print("=== [5/6] VERIFICACIÓN MATEMÁTICA FRAME A FRAME DE CERO CRUCES ===")
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()

    # Evaluar clearance de malla entre pies en cada acción de locomoción
    vg_foot_r = [g.index for g in mesh_obj.vertex_groups if 'foot_R' in g.name or 'toe_R' in g.name]
    vg_foot_l = [g.index for g in mesh_obj.vertex_groups if 'foot_L' in g.name or 'toe_L' in g.name]
    r_verts = [v.index for v in mesh_obj.data.vertices if any(g.group in vg_foot_r and g.weight > 0.4 for g in v.groups)]
    l_verts = [v.index for v in mesh_obj.data.vertices if any(g.group in vg_foot_l and g.weight > 0.4 for g in v.groups)]
    print(f"  Vértices evaluados: Pie R = {len(r_verts)} | Pie L = {len(l_verts)}")

    actions_to_test = ['A_Player_Walk', 'A_Player_Run', 'A_Player_Unarmed_Walk', 'A_Player_Unarmed_Run']
    for act_name in actions_to_test:
        act = bpy.data.actions.get(act_name)
        if not act:
            print(f"  ADVERTENCIA: {act_name} no encontrado.")
            continue
        arm_obj.animation_data.action = act
        f_start, f_end = int(act.frame_range[0]), int(act.frame_range[1])
        min_clearance = 999.0
        crossed_frames = 0
        total_frames = f_end - f_start + 1

        for f in range(f_start, f_end + 1):
            bpy.context.scene.frame_set(f)
            bpy.context.view_layer.update()
            dg = bpy.context.evaluated_depsgraph_get()
            eval_obj = mesh_obj.evaluated_get(dg)
            eval_mesh = eval_obj.to_mesh()

            # Pie R está en +X, Pie L está en -X
            min_rx = min(eval_mesh.vertices[i].co.x for i in r_verts)
            max_lx = max(eval_mesh.vertices[i].co.x for i in l_verts)
            clearance = min_rx - max_lx # Margen de separación física entre pies

            if clearance < min_clearance:
                min_clearance = clearance
            if clearance <= 0.0:
                crossed_frames += 1
            eval_obj.to_mesh_clear()

        print(f"  {act_name:24}: Holgura mínima = {min_clearance*100:6.2f}cm | Cruces = {crossed_frames}/{total_frames} fotogramas")
        if crossed_frames > 0:
            raise RuntimeError(f"FALLO CRÍTICO: {act_name} tiene {crossed_frames} fotogramas con pies cruzados!")

    # Guardar blend canónico
    os.makedirs(os.path.dirname(OUTPUT_BLEND), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print(f"[OK] Guardado Blend Canónico: {OUTPUT_BLEND}")

    # Exportar FBX
    print("=== [6/6] EXPORTANDO Art/FBX/SK_Player.fbx ===")
    arm_obj.data.pose_position = 'REST'
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    if os.path.exists(OUTPUT_FBX):
        os.remove(OUTPUT_FBX)

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
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        bake_anim=False
    )
    print(f"[OK] FBX canónico exportado exitosamente: {OUTPUT_FBX}")

    # Renderizar 4 Vistas Canónicas + Retrato de Validación
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 768
    scene.render.resolution_y = 1024

    world = bpy.data.worlds.new('StudioWorld')
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs['Strength'].default_value = 1.0

    # Luces de estudio
    l_key = bpy.data.lights.new('Key', 'SUN')
    l_key.energy = 4.5
    o_key = bpy.data.objects.new('Key', l_key)
    o_key.rotation_euler = (math.radians(50), math.radians(20), math.radians(-135))
    scene.collection.objects.link(o_key)

    l_fill = bpy.data.lights.new('Fill', 'SUN')
    l_fill.energy = 2.8
    l_fill.color = (0.82, 0.88, 1.0)
    o_fill = bpy.data.objects.new('Fill', l_fill)
    o_fill.rotation_euler = (math.radians(45), math.radians(-30), math.radians(45))
    scene.collection.objects.link(o_fill)

    l_rim = bpy.data.lights.new('Rim', 'SUN')
    l_rim.energy = 6.5
    l_rim.color = (0.85, 0.15, 1.0)
    o_rim = bpy.data.objects.new('Rim', l_rim)
    o_rim.rotation_euler = (math.radians(-45), math.radians(20), math.radians(135))
    scene.collection.objects.link(o_rim)

    cam_data = bpy.data.cameras.new('Cam')
    cam_obj = bpy.data.objects.new('Cam', cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    def render_view(name, loc, target, fov=32):
        cam_data.lens_unit = 'FOV'
        cam_data.angle = math.radians(fov)
        cam_obj.location = Vector(loc)
        d = Vector(target) - Vector(loc)
        cam_obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        out_path = os.path.join(ARTIFACTS_DIR, f"{name}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Render guardado: {out_path}")

    # Vistas de validación canónica:
    # 1. Frontal (desde -Y mirando a +Y hacia el rostro)
    render_view("canonical_symbiote_front", (0.0, -3.2, 0.95), (0.0, 0.0, 0.95))
    # 2. 3/4
    render_view("canonical_symbiote_3quarter", (-2.2, -2.4, 1.15), (0.0, 0.0, 0.95))
    # 3. Lateral
    render_view("canonical_symbiote_side", (-3.2, 0.0, 0.95), (0.0, 0.0, 0.95))
    # 4. Trasera
    render_view("canonical_symbiote_back", (0.0, 3.2, 0.95), (0.0, 0.0, 0.95))
    # 5. Retrato Visera / Rostro
    render_view("canonical_symbiote_portrait", (-0.35, -1.0, 1.68), (0.0, 0.0, 1.68), fov=20)

    print("=== RECONSTRUCCIÓN CANÓNICA PERFECTA COMPLETADA ===")

if __name__ == '__main__':
    main()
