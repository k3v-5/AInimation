# -*- coding: utf-8 -*-
"""export_player_clean_canonical.py
Construye SK_Player con anatomía humana limpia y canónica de 1.82 m,
esqueleto de 22 huesos derivado directamente de las articulaciones reales de DarX_Player_DarkFluid_Adult_Master.blend,
y congruencia geométrica 1:1 de Rest Pose (Reglas 11, 12 y 13 de AGENTS.md).
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Matrix

MASTER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_DarkFluid_Adult_Master.blend"
OUTPUT_FBX = r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx"
OUTPUT_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
PREVIEW_IMG = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\sk_player_clean_canonical_render.png"

CANONICAL_22_BONES = [
    'root', 'pelvis', 'spine', 'chest', 'neck', 'head',
    'clavicle_R', 'upperarm_R', 'forearm_R', 'hand_R',
    'clavicle_L', 'upperarm_L', 'forearm_L', 'hand_L',
    'thigh_R', 'calf_R', 'foot_R', 'toe_R',
    'thigh_L', 'calf_L', 'foot_L', 'toe_L'
]

BONE_MAP_FROM_MASTER = {
    'pelvis': 'hips',
    'spine': 'spine',
    'chest': 'chest',
    'neck': 'neck',
    'head': 'head 1',
    'clavicle_L': 'shoulder.L',
    'upperarm_L': 'upper_arm.L',
    'forearm_L': 'forearm.L',
    'hand_L': 'hand.L',
    'clavicle_R': 'shoulder.R',
    'upperarm_R': 'upper_arm.R',
    'forearm_R': 'forearm.R',
    'hand_R': 'hand.R',
    'thigh_L': 'thigh.L',
    'calf_L': 'shin.L',
    'foot_L': 'foot.L',
    'toe_L': 'toe.L',
    'thigh_R': 'thigh.R',
    'calf_R': 'shin.R',
    'foot_R': 'foot.R',
    'toe_R': 'toe.R'
}

PARENT_MAP = {
    'pelvis': 'root',
    'spine': 'pelvis',
    'chest': 'spine',
    'neck': 'chest',
    'head': 'neck',
    'clavicle_L': 'chest',
    'upperarm_L': 'clavicle_L',
    'forearm_L': 'upperarm_L',
    'hand_L': 'forearm_L',
    'clavicle_R': 'chest',
    'upperarm_R': 'clavicle_R',
    'forearm_R': 'upperarm_R',
    'hand_R': 'forearm_R',
    'thigh_L': 'pelvis',
    'calf_L': 'thigh_L',
    'foot_L': 'calf_L',
    'toe_L': 'foot_L',
    'thigh_R': 'thigh.R',
    'calf_R': 'thigh_R',
    'foot_R': 'calf_R',
    'toe_R': 'foot_R'
}

GROUP_MAP = {
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
    'clavicle_L': ['shoulder.L'],
    'clavicle_R': ['shoulder.R'],
    'upperarm_L': ['upper_arm.L'],
    'upperarm_R': ['upper_arm.R'],
    'forearm_L': ['forearm.L', 'forearm.twist.L'],
    'forearm_R': ['forearm.R', 'forearm.twist.R'],
    'hand_L': [
        'hand.L', 'palm.01.L', 'palm.02.L', 'palm.03.L', 'palm.04.L',
        'f_index.01.L', 'f_index.02.L', 'f_index.03.L',
        'thumb.01.L', 'thumb.02.L', 'thumb.03.L',
        'f_middle.01.L', 'f_middle.02.L', 'f_middle.03.L',
        'f_ring.01.L', 'f_ring.02.L', 'f_ring.03.L',
        'f_pinky.01.L', 'f_pinky.02.L', 'f_pinky.03.L'
    ],
    'hand_R': [
        'hand.R', 'palm.01.R', 'palm.02.R', 'palm.03.R', 'palm.04.R',
        'f_index.01.R', 'f_index.02.R', 'f_index.03.R',
        'thumb.01.R', 'thumb.02.R', 'thumb.03.R',
        'f_middle.01.R', 'f_middle.02.R', 'f_middle.03.R',
        'f_ring.01.R', 'f_ring.02.R', 'f_ring.03.R',
        'f_pinky.01.R', 'f_pinky.02.R', 'f_pinky.03.R'
    ],
    'thigh_L': ['thigh.L'],
    'thigh_R': ['thigh.R'],
    'calf_L': ['shin.L'],
    'calf_R': ['shin.R'],
    'foot_L': ['foot.L', 'heel.L', 'foot_rope_L', 'foot_rope_L.001'],
    'foot_R': ['foot.R', 'heel.R', 'foot_rope_R', 'foot_rope_R.001'],
    'toe_L': ['toe.L'],
    'toe_R': ['toe.R']
}

def main():
    print("=== [1/6] CARGANDO MASTER BLEND ===")
    bpy.ops.wm.open_mainfile(filepath=MASTER_BLEND)
    
    src_mesh = bpy.data.objects.get('SK_DarX_LatexHuman_Eyeless')
    src_arm = bpy.data.objects.get('Armature')
    
    if not src_mesh or not src_arm:
        raise RuntimeError("No se encontró la malla o la armadura maestra en " + MASTER_BLEND)

    # Forzar posición de descanso natural en el esqueleto maestro
    src_arm.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    # Eliminar otros objetos no requeridos
    for o in list(bpy.data.objects):
        if o not in [src_mesh, src_arm]:
            bpy.data.objects.remove(o, do_unlink=True)

    # Factor de escala adulto 1.16: pasa de 1.56m a 1.81m
    SCALE = 1.16

    # Obtener el offset de Z para que los talones queden exactamente a Z = 0.0000
    # Medir vértices de la suela en posición REST
    raw_verts = [v.co for v in src_mesh.data.vertices]
    min_z_raw = min(v.z for v in raw_verts)
    z_offset = -min_z_raw * SCALE
    print(f"  Ajuste métrico: Min Z Raw = {min_z_raw:.4f}m, Factor = {SCALE}, Z Offset = {z_offset:.4f}m")

    # Extraer las coordenadas exactas de las articulaciones del maestro
    bone_coords = {}
    for canon_name, master_name in BONE_MAP_FROM_MASTER.items():
        mb = src_arm.data.bones.get(master_name)
        if not mb:
            raise RuntimeError(f"Hueso maestro '{master_name}' no encontrado para '{canon_name}'")
        head = mb.head_local.copy() * SCALE
        head.z += z_offset
        tail = mb.tail_local.copy() * SCALE
        tail.z += z_offset
        bone_coords[canon_name] = (head, tail)

    print(f"=== [2/6] CONSTRUYENDO ARM_Player (22 HUESOS CANÓNICOS ANATÓMICOS) ===")
    arm_data = bpy.data.armatures.new("ARM_Player")
    arm_obj = bpy.data.objects.new("ARM_Player", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    # Crear root
    root_b = arm_data.edit_bones.new('root')
    root_b.head = Vector((0.0, 0.0, 0.0))
    root_b.tail = Vector((0.0, -0.20, 0.0))

    edit_bones = {'root': root_b}
    for b_name in CANONICAL_22_BONES:
        if b_name == 'root':
            continue
        head, tail = bone_coords[b_name]
        eb = arm_data.edit_bones.new(b_name)
        eb.head = head
        eb.tail = tail
        edit_bones[b_name] = eb

    # Emparentar jerarquía canónica
    PARENT_MAP_CLEAN = {
        'pelvis': 'root',
        'spine': 'pelvis',
        'chest': 'spine',
        'neck': 'chest',
        'head': 'neck',
        'clavicle_L': 'chest',
        'upperarm_L': 'clavicle_L',
        'forearm_L': 'upperarm_L',
        'hand_L': 'forearm_L',
        'clavicle_R': 'chest',
        'upperarm_R': 'clavicle_R',
        'forearm_R': 'upperarm_R',
        'hand_R': 'forearm_R',
        'thigh_L': 'pelvis',
        'calf_L': 'thigh_L',
        'foot_L': 'calf_L',
        'toe_L': 'foot_L',
        'thigh_R': 'pelvis',
        'calf_R': 'thigh_R',
        'foot_R': 'calf_R',
        'toe_R': 'foot_R'
    }

    for child, parent in PARENT_MAP_CLEAN.items():
        edit_bones[child].parent = edit_bones[parent]

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"ARM_Player creado con {len(arm_data.bones)} huesos congruentes 1:1.")

    print("=== [3/6] TRANSFORMANDO MALLA SK_Player ADULTA CANÓNICA ===")
    # Clonar malla limpia directamente de src_mesh sin distorsiones
    player_mesh_data = src_mesh.data.copy()
    player_mesh = bpy.data.objects.new("SK_Player", player_mesh_data)
    bpy.context.scene.collection.objects.link(player_mesh)

    # Copiar y nombrar materiales canónicamente
    player_mesh.data.materials.clear()
    for mat in src_mesh.data.materials:
        if mat:
            mat.name = "M_Player_DarkFluid"
            player_mesh.data.materials.append(mat)

    # Aplicar transformación métrica a la geometría base (Escala 1.16 y Desplazamiento Z)
    trans_mat = Matrix.Translation(Vector((0.0, 0.0, z_offset))) @ Matrix.Diagonal((SCALE, SCALE, SCALE, 1.0))
    player_mesh_data.transform(trans_mat)

    # Medir bounds reales
    new_verts = [v.co for v in player_mesh_data.vertices]
    min_x = min(v.x for v in new_verts); max_x = max(v.x for v in new_verts)
    min_y = min(v.y for v in new_verts); max_y = max(v.y for v in new_verts)
    min_z = min(v.z for v in new_verts); max_z = max(v.z for v in new_verts)
    print(f"  BOUNDS FINALES: X=[{min_x:.3f}, {max_x:.3f}]m (Ancho total: {(max_x-min_x)*100:.1f}cm)")
    print(f"                  Y=[{min_y:.3f}, {max_y:.3f}]m")
    print(f"                  Z=[{min_z:.3f}, {max_z:.3f}]m (Estatura total: {(max_z-min_z)*100:.1f}cm)")

    print("=== [4/6] MAPEO Y NORMALIZACIÓN DE PESOS A LOS 22 HUESOS ===")
    old_vg_by_name = {vg.name: vg.index for vg in player_mesh.vertex_groups}
    src_to_target = {}
    for tgt, srcs in GROUP_MAP.items():
        for s in srcs:
            if s in old_vg_by_name:
                src_to_target[old_vg_by_name[s]] = tgt

    vert_target_weights = {v.index: {} for v in player_mesh.data.vertices}
    for v in player_mesh.data.vertices:
        for g in v.groups:
            tgt = src_to_target.get(g.group)
            if tgt:
                vert_target_weights[v.index][tgt] = vert_target_weights[v.index].get(tgt, 0.0) + g.weight

    player_mesh.vertex_groups.clear()
    new_vgs = {}
    for b in arm_obj.data.bones:
        new_vgs[b.name] = player_mesh.vertex_groups.new(name=b.name)

    unweighted = 0
    for v_idx, w_dict in vert_target_weights.items():
        total = sum(w_dict.values())
        if total > 0.0001:
            for tgt, w in w_dict.items():
                new_vgs[tgt].add([v_idx], w / total, 'REPLACE')
        else:
            unweighted += 1

    print(f"  Pesos reasignados: {len(player_mesh.data.vertices)} vértices | {unweighted} sin peso")
    if unweighted > 0:
        raise RuntimeError(f"Fallo crítico: {unweighted} vértices quedaron sin peso.")

    # Emparentar con modificador Armature
    player_mesh.parent = arm_obj
    mod = player_mesh.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm_obj
    mod.use_vertex_groups = True

    # Eliminar objetos temporales maestros
    bpy.data.objects.remove(src_mesh, do_unlink=True)
    bpy.data.objects.remove(src_arm, do_unlink=True)

    # Guardar blend canónico
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print(f"[OK] Guardado Blend Canónico: {OUTPUT_BLEND}")

    print("=== [5/6] EXPORTANDO Art/FBX/SK_Player.fbx ===")
    arm_obj.data.pose_position = 'REST'
    bpy.context.view_layer.update()

    # Seleccionar ambos
    for o in bpy.context.selected_objects:
        o.select_set(False)
    arm_obj.select_set(True)
    player_mesh.select_set(True)
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
    print(f"[OK] Exportado FBX canónico: {OUTPUT_FBX}")

    print("=== [6/6] RENDERIZANDO PREVISUALIZACIÓN VISUAL (REGLA 4) ===")
    cam_data = bpy.data.cameras.new("Cam_Preview")
    cam_obj = bpy.data.objects.new("Cam_Preview", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_obj.location = (0.0, -3.2, 0.95)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)

    light_data = bpy.data.lights.new("Sun", 'SUN')
    light_obj = bpy.data.objects.new("Sun", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = (1.0, -2.0, 3.0)
    light_data.energy = 4.0

    bpy.context.scene.render.resolution_x = 1024
    bpy.context.scene.render.resolution_y = 1024
    bpy.context.scene.render.filepath = PREVIEW_IMG
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Render guardado en: {PREVIEW_IMG}")

if __name__ == '__main__':
    main()

