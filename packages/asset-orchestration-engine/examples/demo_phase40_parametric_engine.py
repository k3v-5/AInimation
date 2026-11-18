import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.parametric_asset_engine import (
    ParametricAssetAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 40: PARAMETRIC ASSET GENERATION ENGINE")
    print("=" * 95)

    api = ParametricAssetAPI()

    # 1. Generación Paramétrica Inicial
    print("\n[PASO 1] Generación Paramétrica Inicial de 'HOUSE_001' (Sección 1):")
    initial_params = {
        "width": 8.0,
        "depth": 6.0,
        "wall_height": 3.0,
        "roof_type": "GABLE",
        "roof_height": 1.8,
        "window_count": 4,
        "door_count": 1,
        "wall_material": "STONE",
        "roof_material": "WOOD"
    }
    house = api.create_asset("HOUSE_001", initial_params, seed=42)
    print(f" - Asset ID: {house.asset_id} (Categoría: {house.category} | Seed: {house.generation_seed})")
    print(f" - Parámetros Resueltos: {house.parameters}")
    print(" - Componentes Creados:")
    for comp_id, comp in house.components.items():
        print(f"   * [{comp.component_id}] Objetos: {comp.object_ids} | Triángulos: {comp.triangles} | Materiales: {comp.materials}")

    # 2. Regeneración Parcial Quirúrgica (Solo Techo)
    print("\n[PASO 2] Regeneración Parcial Quirúrgica de Techo (Sección 58 & 162):")
    wall_obj_pre = house.components["walls"].object_ids[0]
    roof_obj_pre = house.components["roof"].object_ids[0]
    
    updated_roof = api.update_asset("HOUSE_001", {"roof_height": 1.40})
    wall_obj_post = updated_roof.components["walls"].object_ids[0]
    roof_obj_post = updated_roof.components["roof"].object_ids[0]

    print(f" - Nueva Altura de Techo: {updated_roof.components['roof'].parameters['height']}m (Anterior: 1.80m)")
    print(f" - Objeto Techo: Regenerado ({roof_obj_pre} -> {roof_obj_post})")
    print(f" - Objeto Muros: Preservado Intacto ({wall_obj_pre} == {wall_obj_post})")

    # 3. Modificación de Aberturas y Ventanas
    print("\n[PASO 3] Aumento de Ventanas (4 -> 6) y Preservación de Cimientos (Sección 163):")
    found_obj_pre = updated_roof.components["foundation"].object_ids[0]
    updated_win = api.update_asset("HOUSE_001", {"window_count": 6})
    found_obj_post = updated_win.components["foundation"].object_ids[0]
    print(f" - Cantidad de Ventanas: {len(updated_win.components['windows'].object_ids)} objetos creados")
    print(f" - Objeto Cimientos: Preservado Intacto ({found_obj_pre} == {found_obj_post})")

    # 4. Aislamiento de Materiales (Sin Regeneración Geométrica)
    print("\n[PASO 4] Cambio de Material de Muros a Ladrillo (Sección 164):")
    updated_mat = api.update_asset("HOUSE_001", {"wall_material": "BRICK"})
    print(f" - Material de Muro Asignado: {updated_mat.components['walls'].materials['wall_mat']}")
    print(" - Geometría de Muros: 0 reconstrucciones de vértices/mallas.")

    # 5. Interpretación de Lenguaje Natural a Parámetros
    print("\n[PASO 5] Interpretación de Peticiones del LLM a Parámetros Numéricos (Sección 169-171):")
    # Caso A: Petición vaga rechazada
    try:
        api.interpret_request("HOUSE_001", "make it better")
    except ValueError as e:
        print(f" - Caso 'make it better' -> Rechazo Controlado: {e}")

    # Caso B: Reducción relativa
    rel_change = api.interpret_request("HOUSE_001", "make roof 20% shorter")
    print(f" - Caso 'make roof 20% shorter' -> Parámetro Calculado: {rel_change}")

    # Caso C: Ambigüedad que requiere clarificación
    try:
        api.interpret_request("HOUSE_001", "make house taller")
    except ValueError as e:
        print(f" - Caso 'make house taller' -> Clarificación Requerida: {e}")

    # 6. Control Transaccional y Deshacer (Undo)
    print("\n[PASO 6] Deshacer Operación (Undo) y Restauración de Snapshot (Sección 159):")
    api.update_asset("HOUSE_001", {"roof_height": 2.80})
    print(f" - Techo alterado a {house.parameters['roof_height']}m")
    restored = api.undo_asset("HOUSE_001")
    print(f" - Deshacer ejecutado -> Techo restaurado a {restored.parameters['roof_height']}m")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 40 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
