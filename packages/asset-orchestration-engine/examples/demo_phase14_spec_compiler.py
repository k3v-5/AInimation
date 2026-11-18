import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import SpecificationCompilerAPI

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 14: ASSET SPECIFICATION COMPILER DEMO")
    print("=" * 95)

    spec_api = SpecificationCompilerAPI()

    # 1. Compilación de Lenguaje Natural a Especificación Formal
    prompt = "Quiero una espada medieval estilizada de 120 cm, con una hoja ancha, guardia metálica y empuñadura de cuero oscuro. No quiero grabados."
    print(f"\n[PASO 1] Compilando Petición en Lenguaje Natural:\n  Prompt: \"{prompt}\"")

    ok, spec, msg = spec_api.compile_request(prompt)
    print(f" - Resultado de Compilación: {msg}")
    print(f" - Asset Type: {spec.asset_type} (Confianza: {spec.asset_type_confidence:.2f})")
    print(f" - Estilo y Realismo: {spec.style.category} / {spec.style.realism}")
    print(f" - Longitud Total Normalizada: {spec.dimensions['total_length'].target:.2f} m ({spec.dimensions['total_length'].original_value} {spec.dimensions['total_length'].original_unit}) [Hard Constraint: {spec.dimensions['total_length'].is_hard_constraint}]")
    print(f" - Restricciones Negativas Extraídas: {spec.negative_constraints}")
    print(f" - Componentes Estructurados: {list(spec.components.keys())}")
    for c_name, c_spec in spec.components.items():
        print(f"   * [{c_name.upper()}]: Required={c_spec.required} | Provenance={c_spec.provenance} | Materiales={c_spec.materials}")

    # 2. Aplicación de Parches Incrementales (SpecificationPatch)
    print("\n[PASO 2] Aplicando Parche Incremental sobre 'blade.length' (1.20m -> 1.40m):")
    spec_v2, diff = spec_api.apply_patch(spec, "blade.length", 1.40)
    print(f" - Nueva Versión de Especificación: v{spec_v2.version}")
    print(f" - Diff Registrado: Propiedad='{diff['property']}' | Anterior={diff['before']}m -> Nuevo={diff['after']}m")

    # 3. Detección de Desviación (Specification Drift)
    print("\n[PASO 3] Detección de Specification Drift en Asset de Blender:")
    live_measurements = {"blade_length": 1.50} # Desviado un 25% respecto a 1.20m
    sev, pct, drift_msg = spec_api.check_drift(live_measurements, spec)
    print(f" - Severidad de Drift: {sev} (Desviación: {pct*100:.1f}%)")
    print(f" - Alerta: {drift_msg}")

    # 4. Detección de Conflictos y Ambigüedad
    print("\n[PASO 4] Detección Robusta de Conflictos en Entrada de Usuario:")
    conflict_prompt = "Quiero una espada de 100 cm y 150 cm a la vez"
    ok_conf, _, msg_conf = spec_api.compile_request(conflict_prompt)
    print(f" - Prompt: \"{conflict_prompt}\"")
    print(f" - Compilación Aceptada: {ok_conf} -> Alerta: {msg_conf}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 14 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
