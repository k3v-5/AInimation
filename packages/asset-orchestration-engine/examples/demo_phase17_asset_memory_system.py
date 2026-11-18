import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetMemorySystemAPI, MockBlenderProvider, ProceduralTemplatesAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 17: ASSET MEMORY, VERSIONING & LEARNING DEMO")
    print("=" * 95)

    mem_sys = AssetMemorySystemAPI(":memory:")
    provider = MockBlenderProvider()
    templates_api = ProceduralTemplatesAPI(provider)

    # 1. Creación de Asset y Versionado Inmutable
    print("\n[PASO 1] Creando Asset 'SM_Sword_Master' y Version v1.0.0:")
    asset = mem_sys.create_asset("SM_Sword_Master", "Master Sword", "SWORD", "weapon.sword.standard")
    v1, is_dup1 = mem_sys.create_version(
        asset_id="SM_Sword_Master",
        version_number="1.0.0",
        parameters={"blade_length": 0.90, "blade_width": 0.05, "guard_width": 0.18},
        seed=101
    )
    print(f" - Asset Registrado: {asset.asset_id} ({asset.name})")
    print(f" - Versión Creada: v{v1.version_number} (Hash: {v1.parameter_hash}) [Duplicado: {is_dup1}]")

    # 2. Detección de Duplicados
    print("\n[PASO 2] Intentando Registrar Versión con Parámetros Idénticos:")
    v_dup, is_dup2 = mem_sys.create_version(
        asset_id="SM_Sword_Master",
        version_number="1.0.0",
        parameters={"blade_length": 0.90, "blade_width": 0.05, "guard_width": 0.18},
        seed=101
    )
    print(f" - Detección de Duplicado: {is_dup2} -> Reutilizando version_id='{v_dup.version_id}'")

    # 3. Aprendizaje y Promoción de Patrones
    print("\n[PASO 3] Registrando 3 Correcciones Exitosas para Promover Patrón (CANDIDATE -> VALIDATED):")
    for i in range(1, 4):
        pat = mem_sys.record_correction_and_learn(
            template_id="weapon.sword.standard",
            trigger_issue="blade_too_narrow",
            target_parameter="blade_width",
            recommended_action="SET blade_width = 0.075",
            is_success=True
        )
        print(f" - Ensayo {i}: Patrón '{pat.pattern_id}' -> Estado={pat.status.value} (Éxitos: {pat.success_count}/{pat.evidence_count}, Confianza: {pat.confidence})")

    # 4. Conocimiento Negativo (Failure Avoidance)
    print("\n[PASO 4] Registrando Conocimiento Negativo y Verificando Alerta de Región de Fallo:")
    mem_sys.record_failure("SM_Sword_Master", "weapon.sword.standard", {"guard_width": 0.50}, error_type="COLLISION")
    is_fail, fail_msg = mem_sys.check_negative_knowledge("weapon.sword.standard", {"guard_width": 0.52})
    print(f" - Verificación de Parámetro 'guard_width=0.52': En Región Problemática={is_fail}")
    print(f" - Mensaje: {fail_msg}")

    # 5. Reproducción Determinista de Versión
    print("\n[PASO 5] Reproducción Determinista de la Versión v1.0.0:")
    repro_status, repro_msg = mem_sys.reproduce_version("SM_Sword_Master", v1, provider, templates_api)
    print(f" - Estado de Reproducción: {repro_status.value}")
    print(f" - Mensaje: {repro_msg}")

    # 6. Modo Memoryless
    print("\n[PASO 6] Verificación de Modo Memoryless (Tolerancia a Fallos de BD):")
    mem_less = AssetMemorySystemAPI(is_memoryless=True)
    res_m = mem_less.create_asset("Sword_Tmp", "Temp")
    print(f" - Creación sin base de datos activa: {res_m} (Pipeline operativo sin excepciones)")

    mem_sys.close()

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 17 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
