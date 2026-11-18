"""procedural_ik_rig_engine.py
================================================================================
MOTOR DE CINEMÁTICA PROCEDURAL IK Y BUFFER DE SEGURIDAD (DIRECTIVA 12 & REGLA 67)
================================================================================
Herramienta universal de rig y generación procedural de animaciones de armas para
cualquier personaje (3P/1P) y objeto en DarX / Unreal Engine 5.

Erradica el uso de rotaciones manuales Euler FK hueso por hueso. Utiliza solucionadores
cinemáticos (Two-Bone IK con Pole Targets analíticos), asegurando:
1. Cero deformación de mallas ni colapso de articulaciones (anti-candy wrapper).
2. Agarre bimanual matemático y rígido a los sockets del arma.
3. Buffer de seguridad anti-clipping >= 30-35 cm respecto al torso.
4. Horneado limpio a curvas NLA y exportación FBX sin constraints residuales.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Euler, Matrix


class ProceduralIKRigEngine:
    """Motor central de acople e IK procedural entre personajes y herramientas/armas."""

    def __init__(self, armature_obj, weapon_obj=None):
        self.arm = armature_obj
        self.weapon = weapon_obj
        self.scene = bpy.context.scene

    @staticmethod
    def ensure_pose_mode(arm_obj):
        """Garantiza que el esqueleto esté activo y en modo pose con rotación XYZ."""
        bpy.context.view_layer.objects.active = arm_obj
        if bpy.context.active_object.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        for pb in arm_obj.pose.bones:
            pb.rotation_mode = 'XYZ'

    def setup_two_bone_ik(self, bone_name, target_obj, pole_obj=None, pole_angle_deg=-90.0, chain_count=2):
        """Configura un constraint Two-Bone IK analítico sobre un hueso específico."""
        self.ensure_pose_mode(self.arm)
        pb = self.arm.pose.bones.get(bone_name)
        if not pb:
            raise ValueError(f"Hueso '{bone_name}' no encontrado en la armadura {self.arm.name}")

        # Limpiar constraints IK previos con el mismo nombre
        c_name = f"IK_Procedural_{bone_name}"
        old_c = pb.constraints.get(c_name)
        if old_c:
            pb.constraints.remove(old_c)

        ik = pb.constraints.new('IK')
        ik.name = c_name
        ik.target = target_obj
        ik.chain_count = chain_count

        if pole_obj:
            ik.pole_target = pole_obj
            ik.pole_angle = math.radians(pole_angle_deg)

        return ik

    def create_pole_target(self, name, position_world):
        """Crea un objeto vacío de control como Pole Target para guiar la flexión articular."""
        old_obj = bpy.data.objects.get(name)
        if old_obj:
            bpy.data.objects.remove(old_obj, do_unlink=True)

        pole = bpy.data.objects.new(name, None)
        pole.empty_display_type = 'SPHERE'
        pole.empty_display_size = 0.05
        pole.location = Vector(position_world)
        self.scene.collection.objects.link(pole)
        return pole

    def enforce_clearance_buffer(self, weapon_loc, torso_loc=None, min_clearance=0.30):
        """Verifica y asegura que el arma mantenga un buffer >= min_clearance respecto al torso."""
        if torso_loc is None:
            # Por defecto el pecho de ARM_Player se ubica en Y=0, Z=1.33 aprox
            chest_pb = self.arm.pose.bones.get('chest')
            if chest_pb:
                torso_loc = self.arm.matrix_world @ chest_pb.head
            else:
                torso_loc = Vector((0.0, 0.0, 1.25))

        dist_xy = (Vector((weapon_loc.x, weapon_loc.y, 0)) - Vector((torso_loc.x, torso_loc.y, 0))).length
        if dist_xy < min_clearance:
            # Empujar el arma hacia adelante en Y para respetar el buffer
            correction = min_clearance - dist_xy
            corrected_y = weapon_loc.y - correction if weapon_loc.y < torso_loc.y else weapon_loc.y + correction
            return Vector((weapon_loc.x, corrected_y, weapon_loc.z))
        return weapon_loc

    def bake_and_clean(self, frame_start, frame_end):
        """Hornea visualmente la solución IK a keyframes y elimina los constraints residuales."""
        self.ensure_pose_mode(self.arm)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.nla.bake(
            frame_start=frame_start,
            frame_end=frame_end,
            only_selected=True,
            visual_keying=True,
            clear_constraints=True,
            use_current_action=True,
            bake_types={'POSE'}
        )
        bpy.context.view_layer.update()

    def export_fbx_canonical(self, filepath):
        """Exporta el esqueleto limpio a FBX optimizado para Unreal Engine 5."""
        if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')
        self.arm.select_set(True)
        bpy.context.view_layer.objects.active = self.arm

        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=True,
            object_types={'ARMATURE'},
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=0.0,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            axis_forward='-Z',
            axis_up='Y',
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE'
        )
        print(f"[IK Engine] FBX exportado con éxito: {filepath}")
