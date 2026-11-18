# -*- coding: utf-8 -*-
"""weapon_muzzle_calculator.py
================================================================================
CALCULADOR DE BOQUILLA (MUZZLE) Y VALIDADOR DE ORIENTACIÓN FORWARD DE ARMAS
================================================================================
Módulo integrado en AssetEngine para:
1. Determinar matemáticamente hacia dónde apunta un arma u objeto (eje forward).
2. Forzar y corregir que el arma apunte al eje canónico (-Y en Blender, que mapea a +X en Unreal).
3. Calcular con precisión milimétrica las coordenadas 3D de la boquilla (Muzzle tip)
   según la posición, dimensiones y extremo frontal del cañón.
4. Crear o actualizar el socket/Empty canónico 'Muzzle' en la jerarquía del arma.
"""

from typing import Dict, Any, Tuple, Optional, List
import math

class WeaponMuzzleCalculator:
    CANONICAL_FORWARD_BLENDER = "-Y"
    CANONICAL_FORWARD_UNREAL = "+X"

    @staticmethod
    def determinar_orientacion_forward(obj) -> Dict[str, Any]:
        """
        Determina hacia dónde apunta el cañón del arma en Blender.
        En armas de fuego, el cañón está en la parte superior del arma (Z > 0 respecto al gatillo)
        y se proyecta a lo largo del eje longitudinal (Y o X).
        """
        if not obj or obj.type != 'MESH':
            return {"error": "Objeto no válido o no es de tipo MESH", "forward": None}

        mesh = obj.data
        if len(mesh.vertices) == 0:
            return {"error": "La malla no tiene vértices", "forward": None}

        coords = [v.co for v in mesh.vertices]
        min_x = min(c.x for c in coords); max_x = max(c.x for c in coords)
        min_y = min(c.y for c in coords); max_y = max(c.y for c in coords)
        min_z = min(c.z for c in coords); max_z = max(c.z for c in coords)

        len_x = max_x - min_x
        len_y = max_y - min_y
        len_z = max_z - min_z

        eje_mayor = "Y" if len_y >= len_x else "X"

        if eje_mayor == "Y":
            # Comparar los extremos min_y y max_y
            # Vértices en el 8% más extremo de cada lado
            umbral_neg = min_y + len_y * 0.08
            umbral_pos = max_y - len_y * 0.08
            verts_neg = [c for c in coords if c.y <= umbral_neg]
            verts_pos = [c for c in coords if c.y >= umbral_pos]

            z_neg = sum(c.z for c in verts_neg) / len(verts_neg) if verts_neg else min_z
            z_pos = sum(c.z for c in verts_pos) / len(verts_pos) if verts_pos else min_z

            # Para saber cuál es el cañón:
            # 1. El cañón se ubica en la mitad superior de la altura del arma (Z > (min_z + max_z)*0.4)
            # 2. La culata o empuñadura suele descender hacia Z negativo
            # 3. Si ambos están elevados, el cañón suele tener menor área transversal que la culata
            x_spread_neg = (max(c.x for c in verts_neg) - min(c.x for c in verts_neg)) if verts_neg else 999.0
            x_spread_pos = (max(c.x for c in verts_pos) - min(c.x for c in verts_pos)) if verts_pos else 999.0

            # Prioridad 1: Altura Z media (el cañón está arriba)
            if z_neg > z_pos + 0.015:
                sentido = "-Y"
                punto_boquilla = (0.0, min_y, z_neg)
            elif z_pos > z_neg + 0.015:
                sentido = "+Y"
                punto_boquilla = (0.0, max_y, z_pos)
            else:
                # Si la altura es muy similar, el cañón es más estrecho en X
                if x_spread_neg <= x_spread_pos:
                    sentido = "-Y"
                    punto_boquilla = (0.0, min_y, z_neg)
                else:
                    sentido = "+Y"
                    punto_boquilla = (0.0, max_y, z_pos)

        else:
            umbral_neg = min_x + len_x * 0.08
            umbral_pos = max_x - len_x * 0.08
            verts_neg = [c for c in coords if c.x <= umbral_neg]
            verts_pos = [c for c in coords if c.x >= umbral_pos]
            z_neg = sum(c.z for c in verts_neg) / len(verts_neg) if verts_neg else min_z
            z_pos = sum(c.z for c in verts_pos) / len(verts_pos) if verts_pos else min_z

            if z_neg >= z_pos:
                sentido = "-X"
                punto_boquilla = (min_x, 0.0, z_neg)
            else:
                sentido = "+X"
                punto_boquilla = (max_x, 0.0, z_pos)

        return {
            "eje_mayor": eje_mayor,
            "forward": sentido,
            "es_canonico": (sentido == WeaponMuzzleCalculator.CANONICAL_FORWARD_BLENDER),
            "bounds": {
                "X": (min_x, max_x, len_x),
                "Y": (min_y, max_y, len_y),
                "Z": (min_z, max_z, len_z)
            },
            "punto_boquilla_aprox": punto_boquilla
        }

    @staticmethod
    def calcular_posicion_boquilla(obj) -> Tuple[float, float, float]:
        """
        Calcula la coordenada exacta (X, Y, Z) de la boquilla (Muzzle)
        en el extremo frontal del cañón.
        """
        res = WeaponMuzzleCalculator.determinar_orientacion_forward(obj)
        coords = [v.co for v in obj.data.vertices]
        min_y = min(c.y for c in coords)
        max_y = max(c.y for c in coords)

        if res.get("forward") == "-Y":
            umbral_y = min_y + (max_y - min_y) * 0.05
            verts_front = [c for c in coords if c.y <= umbral_y]
            if verts_front:
                avg_x = sum(c.x for c in verts_front) / len(verts_front)
                avg_z = sum(c.z for c in verts_front) / len(verts_front)
                return (avg_x, min_y, avg_z)
            return (0.0, min_y, res["punto_boquilla_aprox"][2])

        elif res.get("forward") == "+Y":
            umbral_y = max_y - (max_y - min_y) * 0.05
            verts_front = [c for c in coords if c.y >= umbral_y]
            if verts_front:
                avg_x = sum(c.x for c in verts_front) / len(verts_front)
                avg_z = sum(c.z for c in verts_front) / len(verts_front)
                return (avg_x, max_y, avg_z)
            return (0.0, max_y, res["punto_boquilla_aprox"][2])

        return res.get("punto_boquilla_aprox", (0.0, min_y, 0.0))

    @staticmethod
    def asegurar_socket_muzzle_en_blender(bpy_module, obj) -> Tuple[float, float, float]:
        """
        Crea o actualiza un Empty de tipo Flecha/Eje denominado 'SOCKET_Muzzle'
        emparentado al arma en la ubicación calculada de la boquilla.
        """
        muzzle_loc = WeaponMuzzleCalculator.calcular_posicion_boquilla(obj)

        socket_obj = None
        for child in obj.children:
            if child.name == "Muzzle" or child.name.startswith("SOCKET_Muzzle"):
                socket_obj = child
                break

        if not socket_obj:
            socket_obj = bpy_module.data.objects.new("SOCKET_Muzzle", None)
            socket_obj.empty_display_type = 'SINGLE_ARROW'
            socket_obj.empty_display_size = 0.05
            bpy_module.context.scene.collection.objects.link(socket_obj)
            socket_obj.parent = obj

        socket_obj.location = muzzle_loc
        socket_obj.rotation_euler = (0, 0, 0)
        return muzzle_loc

    @staticmethod
    def corregir_orientacion_si_es_necesario(bpy_module, obj) -> bool:
        """
        Si el arma no apunta a -Y (canónico), la rota para que su cañón apunte a -Y.
        """
        res = WeaponMuzzleCalculator.determinar_orientacion_forward(obj)
        if res.get("forward") == "+Y":
            print(f"[WeaponMuzzleCalculator] Corrigiendo inversión 180° en '{obj.name}'...")
            obj.rotation_euler = (0, 0, math.radians(180))
            bpy_module.context.view_layer.objects.active = obj
            bpy_module.ops.object.transform_apply(location=False, rotation=True, scale=False)
            return True
        return False
