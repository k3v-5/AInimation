"""blender_export_guard.py
================================================================================
BLINDAJE Y PROTECCION DE EXPORTACION / RENDERIZADO DE BLENDER EN DARX
================================================================================
Previene la sobreescritura accidental o corrupcion de mallas, esqueletos y assets
canonicos del proyecto DarX.

Reglas del Guardian:
1. Proteccion de Assets Canonicos:
   - Prohibido sobrescribir SK_Player.fbx o esqueletos canonicos sin flag explicito.
   - Las animaciones deben canalizarse a carpetas dedicadas (Anim_Player, Anim_FPS).
2. Verificacion Topologica de Esqueleto:
   - Valida la presencia e integridad de los 22 huesos canonicos del jugador.
3. Respaldos Atomicos:
   - Respalda automaticamente los archivos .blend maestros antes de cualquier
     operacion de horneado o exportacion a Saved/Backups_Blend/.
4. Enforzamiento de Headless Limpio:
   - Asegura el flag --factory-startup al invocar blender.exe para evitar fallos
     con addons locales no nativos (BY-GEN, audvis, etc.).
"""

import os
import sys
import shutil
import datetime
from pathlib import Path
from typing import List, Tuple, Optional

PROJECT_ROOT = Path(r"E:\Darx_Proyect")
BACKUP_DIR = PROJECT_ROOT / "Saved" / "Backups_Blend"
CANONICAL_FBX_PLAYER = PROJECT_ROOT / "Art" / "FBX" / "SK_Player.fbx"
CANONICAL_BONES_22 = [
    "root", "pelvis", "spine", "chest", "neck", "head",
    "clavicle_L", "upperarm_L", "forearm_L", "hand_L",
    "clavicle_R", "upperarm_R", "forearm_R", "hand_R",
    "thigh_L", "calf_L", "foot_L", "toe_L",
    "thigh_R", "calf_R", "foot_R", "toe_R"
]


def crear_respaldo_blend(archivo_blend: str) -> Optional[Path]:
    path_blend = Path(archivo_blend)
    if not path_blend.exists():
        print(f"[Guard] ADVERTENCIA: El archivo .blend no existe: {path_blend}")
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{path_blend.stem}_BACKUP_{timestamp}{path_blend.suffix}"
    backup_path = BACKUP_DIR / backup_filename

    shutil.copy2(path_blend, backup_path)
    print(f"[Guard] Respaldo de seguridad creado: {backup_path.name}")
    return backup_path


def validar_ruta_destino_fbx(ruta_fbx: str, permitir_sobreescribir_canonico: bool = False) -> Tuple[bool, str]:
    path_fbx = Path(ruta_fbx).resolve()
    path_canonico = CANONICAL_FBX_PLAYER.resolve()

    if path_fbx == path_canonico and not permitir_sobreescribir_canonico:
        return False, (
            f"ERROR DE SEGURIDAD: Se intento sobrescribir la malla canonica de jugador "
            f"({path_canonico}). Las animaciones deben exportarse a Art/FBX/Anim_Player/."
        )

    path_fbx.parent.mkdir(parents=True, exist_ok=True)
    return True, "Ruta de exportacion valida y autorizada."


def verificar_esqueleto_canonico(arm_obj) -> Tuple[bool, List[str]]:
    if arm_obj is None or arm_obj.type != 'ARMATURE':
        return False, ["El objeto proporcionado no es una armadura valida."]

    nombres_huesos = set(b.name for b in arm_obj.data.bones)
    huesos_faltantes = [b for b in CANONICAL_BONES_22 if b not in nombres_huesos]

    if huesos_faltantes:
        return False, [f"Faltan huesos canonicos: {huesos_faltantes}"]

    return True, []


def validar_orientacion_arma_exportacion(obj) -> Tuple[bool, str, Tuple[float, float, float]]:
    """
    Verifica que el arma u objeto apunte al forward canónico (-Y en Blender).
    Calcula además la posición exacta de la boquilla (Muzzle).
    """
    from .weapon_muzzle_calculator import WeaponMuzzleCalculator
    res = WeaponMuzzleCalculator.determinar_orientacion_forward(obj)
    if not res.get("forward"):
        return False, f"Error al analizar malla: {res.get('error')}", (0.0, 0.0, 0.0)

    muzzle = WeaponMuzzleCalculator.calcular_posicion_boquilla(obj)
    if not res.get("es_canonico"):
        return False, f"Orientación '{res.get('forward')}' NO es canónica (se requiere '-Y').", muzzle

    return True, f"Orientación canónica '-Y' verificada. Boquilla en {muzzle}.", muzzle


def obtener_comando_blender_seguro(script_path: str, blend_file: Optional[str] = None) -> List[str]:
    blender_exe = r"E:\Blender\blender.exe"
    cmd = [blender_exe, "--factory-startup", "--background"]
    if blend_file:
        cmd.extend([blend_file])
    cmd.extend(["--python", script_path])
    return cmd


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="DarX Blender Export Guard")
    parser.add_argument("--backup", type=str, help="Crea un respaldo seguro de un .blend")
    parser.add_argument("--validate-path", type=str, help="Valida ruta de exportacion FBX")
    args = parser.parse_args()

    if args.backup:
        crear_respaldo_blend(args.backup)
    if args.validate_path:
        valido, msg = validar_ruta_destino_fbx(args.validate_path)
        print(f"[{'OK' if valido else 'BLOQUEADO'}] {msg}")
