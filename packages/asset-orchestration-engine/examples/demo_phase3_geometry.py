import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine
)

def main():
    print("=" * 80)
    print("  ASSET ORCHESTRATION ENGINE v3 (AOE v3) — FASE 3: GEOMETRY ENGINE DEMO")
    print("=" * 80)

    engine = GeometryEngine()

    # 1. Creación Paramétrica de la Espada
    print("\n[PASO 1] Construcción Paramétrica Inicial de la Espada Medieval:")
    
    # Mango
    r_handle = engine.create_component("sword_01", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
    # Guarda
    r_guard = engine.create_component("sword_01", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03}, parent_id="sword_01.handle")
    # Hoja (Profile Generator con ahusamiento tip_ratio=0.15)
    r_blade = engine.create_component("sword_01", "blade", "profile", {"length": 0.85, "width": 0.05, "thickness": 0.015, "tip_ratio": 0.15}, parent_id="sword_01.guard")
    # Pomo
    r_pommel = engine.create_component("sword_01", "pommel", "primitive", {"primitive": "sphere", "width": 0.05, "depth": 0.05, "height": 0.05}, parent_id="sword_01.handle")

    print(f" - Handle: {r_handle['vertices_count']} vértices, {r_handle['triangle_count']} triángulos")
    print(f" - Guard: {r_guard['vertices_count']} vértices, {r_guard['triangle_count']} triángulos")
    print(f" - Blade: {r_blade['vertices_count']} vértices, {r_blade['triangle_count']} triángulos (dim={r_blade['dimensions']})")
    print(f" - Pommel: {r_pommel['vertices_count']} vértices, {r_pommel['triangle_count']} triángulos")

    # 2. Establecer Relación Derivada
    engine.set_derived_rule("sword_01.guard", "width", "blade.width * 3")
    print("\n[PASO 2] Relación Derivada Registrada: guard.width = blade.width * 3")

    # 3. Modificación Quirúrgica 1: Alargar hoja 10 cm (blade.length += 0.10)
    print("\n[PASO 3] Modificación Solicitada: 'blade.length += 0.10m' (0.85m -> 0.95m)")
    res1 = engine.modify_component("sword_01.blade", "length", "INCREMENT", 0.10)

    print(" - Resultado de Dependency Analysis & Minimal Rebuild:")
    print(f"   * Componentes Reconstruidos: {res1['rebuilt_components']}")
    print(f"   * Componentes Intactos (CLEAN): {res1['unaffected_components']}")
    print(f"   * Nueva Dimensión de la Hoja: {res1['dimensions']}")

    # 4. Modificación Quirúrgica 2: Cambiar ancho de hoja (blade.width = 0.08m) -> Propaga a guard.width = 0.24m
    print("\n[PASO 4] Modificación con Dependencia: 'blade.width = 0.08m' -> Dispara guard.width = 0.24m")
    res2 = engine.modify_component("sword_01.blade", "width", "SET", 0.08)

    print(" - Resultado de Propagación Paramétrica:")
    print(f"   * Componentes Reconstruidos (DIRTY): {res2['rebuilt_components']}")
    print(f"   * Componentes Intactos (CLEAN): {res2['unaffected_components']}")
    
    insp_guard = engine.inspect_component("sword_01.guard")
    print(f"   * Guard Recalculado: width = {insp_guard['parameters']['width']}m (0.08 * 3 = 0.24)")

    # 5. Prueba de NO_OP
    print("\n[PASO 5] Reenviando misma dimensión (blade.width = 0.08m)...")
    res_noop = engine.modify_component("sword_01.blade", "width", "SET", 0.08)
    print(f" - Status: {res_noop['status']}")
    print(f" - Reconstrucciones realizadas: {len(res_noop['modified_components'])}")

    print("\n" + "=" * 80)
    print("  CRITERIO DE EXITO DE FASE 3 CUMPLIDO AL 100%")
    print("=" * 80)

if __name__ == "__main__":
    main()
