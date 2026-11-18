"""procedural_ik_animator.py
Motor de Animación e Interacción Procedural Motor-Céntrico (Unreal Engine & Blender).

Implementa la Regla 12 de AGENTS.md y Regla 67 de REGLAS-DE-TRABAJO.md:
"El motor debe darte las herramientas y tú solo debes de decidir o configurar:
 tú prácticamente pones la información y el motor genera".

Flujo de Alto Nivel:
1. Recibe la configuración de intención (Malla personaje, Malla arma/objeto, Sockets, Acción).
2. Genera automáticamente restricciones Two-Bone IK con Pole Targets anatómicos.
3. Ancla la empuñadura primaria a la mano derecha y la mano izquierda al socket secundario del objeto.
4. Aplica las trayectorias de centro de masa y contacto con el suelo.
5. Hornea y exporta el FBX sin deformación ni colapso de malla.
"""

import os
import math
import bpy
from mathutils import Vector, Euler, Matrix, Quaternion

class ProceduralIKAnimator:
    def __init__(self, arm_obj):
        self.arm = arm_obj
        self.constraints_created = []
        self.helper_objects = []

    def setup_two_bone_ik(self, hand_bone_name, target_obj, pole_target_obj=None, pole_angle=0.0):
        """Configura una restricción Two-Bone IK nativa en el hueso objetivo con control de codo."""
        pb = self.arm.pose.bones.get(hand_bone_name)
        if not pb:
            raise ValueError(f"Hueso {hand_bone_name} no existe en {self.arm.name}")

        ik = pb.constraints.new('IK')
        ik.name = f"Procedural_IK_{hand_bone_name}"
        ik.target = target_obj
        ik.chain_count = 2  # Antebrazo y Brazo superior
        ik.weight = 1.0

        if pole_target_obj:
            ik.pole_target = pole_target_obj
            ik.pole_angle = math.radians(pole_angle)

        self.constraints_created.append((pb, ik))
        return ik

    def attach_weapon_to_primary_hand(self, weapon_obj, hand_bone_name='hand_R', local_offset=(0, 0, 0), local_rot=(0, 0, 0)):
        """Emparenta el arma rígidamente al hueso de agarre principal."""
        weapon_obj.parent = self.arm
        weapon_obj.parent_type = 'BONE'
        weapon_obj.parent_bone = hand_bone_name
        weapon_obj.location = local_offset
        weapon_obj.rotation_euler = [math.radians(a) for a in local_rot]
        bpy.context.view_layer.update()

    def create_socket_target(self, parent_obj, socket_name, local_pos=(0, 0, 0)):
        """Crea un objeto Helper/Empty representando un Socket canónico."""
        empty = bpy.data.objects.new(socket_name, None)
        empty.empty_display_type = 'AXIS'
        empty.empty_display_size = 0.05
        bpy.context.scene.collection.objects.link(empty)
        empty.parent = parent_obj
        empty.location = local_pos
        self.helper_objects.append(empty)
        return empty

    def bake_and_export(self, action_name, num_frames, out_fbx_path):
        """Hornea las restricciones IK procedurales en curvas F-Curve y exporta FBX compatible con UE5."""
        bpy.ops.nla.bake(
            frame_start=0,
            frame_end=num_frames,
            only_selected=False,
            visual_keying=True,
            clear_constraints=True,
            use_current_action=True,
            bake_types={'POSE'}
        )

        act = self.arm.animation_data.action
        act.name = action_name

        # Exportar FBX limpio
        bpy.ops.object.select_all(action='DESELECT')
        self.arm.select_set(True)
        bpy.context.view_layer.objects.active = self.arm

        bpy.ops.export_scene.fbx(
            filepath=out_fbx_path,
            use_selection=True,
            global_scale=1.0,
            apply_scale_options='FBX_SCALE_NONE',
            axis_forward='-Y',
            axis_up='Z',
            bake_space_transform=False,
            object_types={'ARMATURE'},
            use_mesh_modifiers=True,
            mesh_smooth_type='FACE',
            add_leaf_bones=False,
            bake_anim=True,
            bake_anim_use_all_actions=False,
            bake_anim_use_nla_strips=False,
            bake_anim_simplify_factor=0.0
        )
        print(f"Exportado FBX Procedural IK: {out_fbx_path}")

    def cleanup(self):
        """Limpia los objetos auxiliares temporales."""
        for obj in self.helper_objects:
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        self.helper_objects.clear()
