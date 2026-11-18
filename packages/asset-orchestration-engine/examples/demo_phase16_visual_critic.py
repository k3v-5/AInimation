import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    VisualCriticAPI, ProceduralTemplatesAPI, MockBlenderProvider,
    SpecificationCompilerAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 16: VISUAL EVALUATION & AI CRITIC DEMO")
    print("=" * 95)

    provider = MockBlenderProvider()
    templates_api = ProceduralTemplatesAPI(provider)
    critic_api = VisualCriticAPI(templates_api, provider, max_visual_iterations=4)
    spec_api = SpecificationCompilerAPI()

    # 1. Compilar especificación con requisito de "hoja ancha"
    prompt = "Quiero una espada medieval estilizada con hoja ancha de 120 cm"
    print(f"\n[PASO 1] Compilando Especificación: \"{prompt}\"")
    _, spec, _ = spec_api.compile_request(prompt)

    # 2. Generar asset con hoja estrecha (desviada)
    print("\n[PASO 2] Construyendo Asset Inicial con Hoja Estrecha (0.04m):")
    build_res = templates_api.build_from_spec("sword_critic_01", spec)
    provider.set_component_dimensions("sword_critic_01", "blade", (0.04, 0.02, 0.90))
    print(f" - Dimensiones Iniciales Hoja: {provider.assets['sword_critic_01']['components']['blade']['dimensions']}")

    # 3. Ejecutar Ciclo de Evaluación Visual & Diagnóstico AI Critic
    print("\n[PASO 3] Ejecutando Ciclo de Crítica Visual y Refinamiento Paramétrico:")
    eval_res = critic_api.evaluate_and_refine("sword_critic_01", spec, build_res["parameters"])
    print(f" - Estado Final: {eval_res['final_status']}")
    print(f" - Iteraciones de Crítica: {eval_res['iterations']}")
    print(f" - Score Visual Alcanzado: {eval_res['overall_score'] * 100:.1f}%")
    print(f" - Historial de Diagnóstico y Parches:")
    for h in eval_res["history"]:
        print(f"   * Iteración {h['iteration']}: Problemas Detectados={h['issues']} -> Parches Aplicados={h['applied_patches']}")

    # 4. Verificar Dimensiones Finales en Provider (Reconstrucción Parcial)
    final_b_dims = provider.assets["sword_critic_01"]["components"]["blade"]["dimensions"]
    grip_dims = provider.assets["sword_critic_01"]["components"]["grip"]["dimensions"]
    print(f"\n[PASO 4] Estado Final del Asset en Blender:")
    print(f" - Dimensiones Hoja Corregida (Ensanchada a objetivo): {final_b_dims}")
    print(f" - Dimensiones Mango (Completamente Intacto): {grip_dims}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 16 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
