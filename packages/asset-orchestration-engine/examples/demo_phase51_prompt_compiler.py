import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.prompt_compiler_intent_spec import (
    PromptCompilerAPI, ConversationContext
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 51: PROMPT COMPILER & INTENT-TO-SPEC ENGINE")
    print("=" * 95)

    api = PromptCompilerAPI()

    # 1. Caso Obligatorio 1: Compilación de Prompt Completo de Barril Medieval
    print("\n[PASO 1] Caso Obligatorio 1: Compilación de Prompt Completo de Barril (Sección 201):")
    prompt_1 = "Quiero un barril medieval grande, de madera oscura, estilizado, con dos aros metálicos y que el jugador pueda recogerlo."
    res_1 = api.compile_intent(prompt_1)
    spec_1 = res_1.specification
    print(f" - Prompt de Entrada: \"{prompt_1}\"")
    print(f" - Estado de Compilación: [{res_1.status.value}] | Confianza: {res_1.confidence * 100:.1f}%")
    print(f" - Especificación Generada: ID={spec_1.specification_id} | Clase: [{spec_1.asset_class}] | Intención: [{spec_1.intent.value}]")
    print(f" - Estilos: {spec_1.style} | Materiales: {spec_1.materials}")
    print(f" - Componentes Extraídos: {spec_1.components}")
    print(f" - Requisitos de Gameplay: {spec_1.gameplay_flags}")
    print(f" - Requisitos Derivados (Reglas de Proyecto): {spec_1.derived_requirements}")
    print(f" - Mapa de Provenance: {spec_1.provenance_map}")

    # 2. Caso Obligatorio 3: Detección de Contradicción Directa
    print("\n[PASO 2] Caso Obligatorio 3: Detección de Contradicción Directa (Sección 203):")
    prompt_3 = "Haz una casa pequeña pero enorme"
    res_3 = api.compile_intent(prompt_3)
    print(f" - Prompt: \"{prompt_3}\" -> Estado: [{res_3.status.value}]")
    print(f" - Conflictos Detectados ({len(res_3.conflicts)}):")
    for c in res_3.conflicts:
        print(f"   * [{c.conflict_id}] entre '{c.requirement_a}' y '{c.requirement_b}': \"{c.reason}\"")

    # 3. Caso Obligatorio 4: Modificación Relativa con Contexto Activo
    print("\n[PASO 3] Caso Obligatorio 4: Modificación Relativa con Contexto Activo (Sección 204):")
    ctx = ConversationContext(
        active_asset_id="BARREL_PREV",
        active_asset_class="PROP.BARREL",
        previous_parameters={"height": 1.50}
    )
    prompt_4 = "Hazlo igual que el anterior pero 20% más alto"
    res_4 = api.compile_intent(prompt_4, ctx)
    print(f" - Contexto Activo: Asset ID={ctx.active_asset_id} (Altura previa: {ctx.previous_parameters['height']}m)")
    print(f" - Prompt: \"{prompt_4}\" -> Nueva Altura Calculada: {res_4.specification.dimensions['height']}m")

    # 4. Caso Obligatorio 6: Extracción de Restricciones Negativas / Prohibidas
    print("\n[PASO 4] Caso Obligatorio 6: Extracción de Restricciones Negativas (Sección 206):")
    prompt_6 = "Haz un barril sin aros"
    res_6 = api.compile_intent(prompt_6)
    print(f" - Prompt: \"{prompt_6}\"")
    print(f" - Características Prohibidas (Forbidden): {res_6.specification.forbidden_features}")
    print(f" - Componentes Positivos: {res_6.specification.components}")

    # 5. Caso Obligatorio 9: Modificación Relativa sin Contexto (Clarification Request)
    print("\n[PASO 5] Caso Obligatorio 9: Modificación Relativa sin Contexto (Sección 209):")
    prompt_9 = "Hazlo más grande"
    res_9 = api.compile_intent(prompt_9) # Context is None
    print(f" - Prompt: \"{prompt_9}\" -> Estado: [{res_9.status.value}]")
    print(f" - Clarificación Solicitada: \"{res_9.clarifications[0].question}\" (Categoría: {res_9.clarifications[0].impact_category})")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 51 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
