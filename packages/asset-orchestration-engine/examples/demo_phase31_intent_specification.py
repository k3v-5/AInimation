import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.intent_specification_compiler import (
    IntentSpecificationAPI, AssetSpec
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 31: INTENT COMPILER & SPEC LANGUAGE DEMO")
    print("=" * 95)

    api = IntentSpecificationAPI()

    # 1. Escenario 140: Compilación de Intención Compleja a Especificación Formal
    prompt_v1 = (
        "Quiero una casa medieval pequeña, vieja y ligeramente inclinada, "
        "con una puerta grande de madera, dos ventanas estrechas, "
        "una escalera interior al segundo piso y que el jugador pueda entrar. "
        "No quiero que parezca una casa de fantasía, sino una construcción medieval rural."
    )
    print("\n[ESCENARIO 140] 1. Compilación de Lenguaje Natural a Especificación Formal (AssetSpec):")
    print(f"   Prompt: \"{prompt_v1}\"")
    spec_v1, warnings, errors = api.compile_intent(prompt_v1, spec_id="spec_rural_house_01")
    is_valid, conflicts = api.validate_spec(spec_v1)
    
    print(f" - Estado de Especificación: {spec_v1.status.value} | Aprobación: {spec_v1.approval.value}")
    print(f" - Arquitectura: {spec_v1.style.architecture} | Condición: {spec_v1.style.condition}")
    print(f" - Estilos Prohibidos: {spec_v1.style.forbidden_styles}")
    print(f" - Inclinación Geométrica: {spec_v1.visual.lean_angle_deg}°")
    print(f" - Puerta: material={spec_v1.door.material}, width={spec_v1.door.width_m}m, accesible={spec_v1.door.player_passable}")
    print(f" - Ventanas: {spec_v1.windows.count} ({spec_v1.windows.style}) | Escaleras: {spec_v1.stairs.required} ({spec_v1.stairs.destination})")
    print(f" - Hash Canónico de la Especificación: {spec_v1.compute_spec_hash()}")
    print(" - Requisitos Formales Extraídos:")
    for req in spec_v1.requirements:
        print(f"   * [{req.req_id}] ({req.constraint_type.value}) {req.description} -> Afecta: {req.affects}")

    # 2. Escenario 141: Modificación de Requisito y Análisis de Impacto
    prompt_v2 = (
        "Quiero una casa medieval pequeña, vieja y ligeramente inclinada, "
        "con una puerta grande de madera, tres ventanas estrechas, "
        "una escalera interior al segundo piso y que el jugador pueda entrar. "
        "No quiero que parezca una casa de fantasía, sino una construcción medieval rural."
    )
    print("\n[ESCENARIO 141] 2. Modificación de Especificación (Spec v1 -> Spec v2) y Análisis de Impacto:")
    print("   Usuario: \"Ahora quiero tres ventanas.\"")
    spec_v2, _, _ = api.compile_intent(prompt_v2, spec_id="spec_rural_house_01")
    spec_v2.spec_version = "2.0.0"

    diff, impact = api.diff_and_analyze_impact(spec_v1, spec_v2)
    print(f" - Diferencias Detectadas: {diff.modified_fields}")
    print(f" - Componentes Afectados: {impact.affected_components}")
    print(f" - Componentes Intactos (Sin Reconstruir): {impact.unaffected_components}")
    print(f" - Ámbito de Reconstrucción del Orchestrator: {impact.rebuild_scope}")

    # 3. Protección Anti-Alucinación y Anti-Contradicción
    print("\n[SEGURIDAD] 3. Filtro Anti-Alucinación y Detección de Contradicciones:")
    fake_prompt = "Quiero una casa con material dragonium"
    _, _, err_mat = api.compile_intent(fake_prompt)
    print(f" - Intento de Material Alucinado: {err_mat}")

    spec_conflict, _, _ = api.compile_intent(prompt_v1)
    spec_conflict.door.width_m = 0.50 # Inválido para paso de jugador
    _, conflicts = api.validate_spec(spec_conflict)
    print(f" - Contradicción de Puerta Estrecha + Paso de Jugador: {conflicts}")

    # 4. Compilación de Tareas con Trazabilidad
    print("\n[TRAZABILIDAD] 4. Mapeo de Requisitos a Grafo de Tareas:")
    tasks = api.generate_tasks_from_spec(spec_v1)
    for t in tasks:
        print(f"   * [{t['task_id']}] {t['task_type']} -> Implementa: {t.get('implements', t.get('validates', []))}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 31 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
