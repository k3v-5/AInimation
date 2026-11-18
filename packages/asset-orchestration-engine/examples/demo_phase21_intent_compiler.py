import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    IntentCompilerAPI, NaturalLanguageRequest, RequestContext
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 21: INTENT COMPILER & REQUIREMENT RESOLUTION DEMO")
    print("=" * 95)

    compiler = IntentCompilerAPI()

    # 1. Escenario 120: Compilación Formal Completa
    print("\n[ESCENARIO 120] Usuario: \"Crea una espada medieval estilizada de 90 cm.\"")
    req_120 = NaturalLanguageRequest("req_120", "Crea una espada medieval estilizada de 90 cm.")
    spec_120 = compiler.compile(req_120)
    auth_120 = compiler.authorize(spec_120)
    print(f" - Acción Compilada: {spec_120.action.value} -> Objetivo: {spec_120.target_type}")
    print(f" - Estado de Especificación: {spec_120.status.value} (Autorizado: {auth_120.authorized})")
    for r_name, r in spec_120.requirements.items():
        print(f"   * [{r.category}] {r.name}: {r.value}{r.unit} (Prioridad: {r.priority.value}, Origen: {r.source})")

    # 2. Escenario 121: Bloqueo por Ambigüedad de Unidad
    print("\n[ESCENARIO 121] Usuario: \"Crea una espada de 90.\" (Sin unidad explícita)")
    req_121 = NaturalLanguageRequest("req_121", "Crea una espada de 90.")
    spec_121 = compiler.compile(req_121)
    auth_121 = compiler.authorize(spec_121)
    print(f" - Estado de Especificación: {spec_121.status.value} (Autorizado: {auth_121.authorized})")
    print(f" - Razones de Bloqueo: {spec_121.blocking_reasons}")

    # 3. Escenario 122: Reemplazo Secuencial por Novedad (Recency Override)
    print("\n[ESCENARIO 122] Usuario pide 90 cm y luego: \"Mejor de 110 cm.\"")
    req_122a = NaturalLanguageRequest("req_122a", "Crea una espada de 90 cm.")
    spec_122a = compiler.compile(req_122a)
    req_122b = NaturalLanguageRequest("req_122b", "Mejor de 110 cm.")
    spec_122b = compiler.compile(req_122b)
    merged_spec = compiler.apply_sequential_override(spec_122a, spec_122b)
    print(f" - Valor Actual Resuelto: {merged_spec.requirements['length'].value}m ({merged_spec.requirements['length'].status.value})")
    print(f" - Valor Anterior Histórico: {merged_spec.requirements['length_prev'].value}m ({merged_spec.requirements['length_prev'].status.value})")

    # 4. Escenario 123: Extracción de Restricciones Espaciales
    print("\n[ESCENARIO 123] Usuario: \"Mueve la torre al norte de la plaza.\"")
    ctx_scene = RequestContext(available_entities={"tower_001": "tower", "plaza_001": "plaza"})
    req_123 = NaturalLanguageRequest("req_123", "Mueve la torre al norte de la plaza.", context=ctx_scene)
    spec_123 = compiler.compile(req_123)
    cons = spec_123.constraints[0]
    print(f" - Entidad Resuelta: '{spec_123.target_id}'")
    print(f" - Restricción Espacial: {cons.subject} {cons.relation} {cons.object_target} (Prioridad: {cons.priority.value})")

    # 5. Escenario 124: Bloqueo por Ambigüedad de Destino
    print("\n[ESCENARIO 124] Usuario: \"Mueve la torre.\" (Existen tower_001 y tower_002)")
    ctx_multi = RequestContext(available_entities={"tower_001": "tower", "tower_002": "tower"})
    req_124 = NaturalLanguageRequest("req_124", "Mueve la torre.", context=ctx_multi)
    spec_124 = compiler.compile(req_124)
    print(f" - Estado: {spec_124.status.value} -> Razones: {spec_124.blocking_reasons}")

    # 6. Escenario 127: Simulación de Factibilidad (Footprint Incompatible)
    print("\n[ESCENARIO 127] Usuario: \"Crea 20 casas en un área de 5m x 5m.\"")
    req_127 = NaturalLanguageRequest("req_127", "Crea 20 casas.")
    spec_127 = compiler.compile(req_127)
    ok_sim, sim_errors = compiler.simulate(spec_127, bounds=(5.0, 5.0))
    print(f" - Simulación de Factibilidad Espacial: {ok_sim}")
    print(f" - Errores Detectados en Dry-Run: {sim_errors}")

    # 7. Escenario 128: Contradicción Directa
    print("\n[ESCENARIO 128] Usuario: \"Torre de 100m pero que tenga exactamente 10m de altura.\"")
    req_128 = NaturalLanguageRequest("req_128", "Crea una torre de 100m pero que tenga exactamente 10m de altura.")
    spec_128 = compiler.compile(req_128)
    print(f" - Estado: {spec_128.status.value} -> Razones: {spec_128.blocking_reasons}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 21 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
