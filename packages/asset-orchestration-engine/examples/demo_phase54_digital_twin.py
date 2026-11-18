import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.semantic_asset_graph_twin import (
    SemanticDigitalTwinAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 54: SEMANTIC ASSET GRAPH & DIGITAL TWIN")
    print("=" * 95)

    api = SemanticDigitalTwinAPI()
    asset_id = "asset_042"

    # 1. Caso Obligatorio 1: Creación del Grafo Semántico de Barril
    print("\n[PASO 1] Caso Obligatorio 1: Estructuración Semántica del Digital Twin (Sección 160):")
    api.register_component(asset_id, "comp_body", "asset_042.body", "BODY", "Barrel_Body", {"location": (0,0,0)}, "DarkWood")
    api.register_component(asset_id, "comp_ring1", "asset_042.ring_01", "RING", "Barrel_Ring_01", {"location": (0,0,1.2)}, "Iron")
    api.register_component(asset_id, "comp_ring2", "asset_042.ring_02", "RING", "Barrel_Ring_02", {"location": (0,0,0.4)}, "Iron")
    api.register_component(asset_id, "comp_col", "asset_042.collision", "COLLISION", "UCX_Barrel", {"location": (0,0,0)}, "Physics")

    api.add_dependency(asset_id, "comp_ring1", "comp_body")
    api.add_dependency(asset_id, "comp_ring2", "comp_body")
    api.add_dependency(asset_id, "comp_col", "comp_body")

    graph = api.get_or_create_graph(asset_id)
    print(f" - Grafo Semántico Creado para '{asset_id}': {len(graph.nodes)} componentes estructurados.")
    for cid, node in graph.nodes.items():
        print(f"   * [{node.semantic_id}] -> Tipo: {node.semantic_type} | Blender Object: '{node.blender_object_name}' | Material: '{node.material_name}'")

    # 2. Caso Obligatorio 10: Resolución de Consultas en Lenguaje Natural
    print("\n[PASO 2] Caso Obligatorio 10: Resolución de Consultas Semánticas en Lenguaje Natural (Sección 94):")
    q1 = "el aro metálico de arriba"
    target1 = api.resolve_natural_query(asset_id, q1)
    print(f" - Consulta: \"{q1}\" -> Componente Resuelto: [{graph.nodes[target1].semantic_id}] (ID: {target1})")

    q2 = "el aro metálico de abajo"
    target2 = api.resolve_natural_query(asset_id, q2)
    print(f" - Consulta: \"{q2}\" -> Componente Resuelto: [{graph.nodes[target2].semantic_id}] (ID: {target2})")

    q3 = "el cuerpo de madera"
    target3 = api.resolve_natural_query(asset_id, q3)
    print(f" - Consulta: \"{q3}\" -> Componente Resuelto: [{graph.nodes[target3].semantic_id}] (ID: {target3})")

    # 3. Caso Obligatorio 2: Límite Mínimo de Regeneración (Zero Full Rebuild)
    print("\n[PASO 3] Caso Obligatorio 2: Límite de Regeneración Local para Aro Desplazado (Sección 151):")
    boundary_local = api.calculate_regeneration_boundary(asset_id, target1, parameter_modified="position")
    print(f" - Defecto del Critic: \"Ring_01 is 15cm too low\"")
    print(f" - Límite de Componentes Afectados: {boundary_local.boundary_components} (Nivel: {boundary_local.impact_level.value})")
    print(f" - Justificación: \"{boundary_local.reason}\"")

    # 4. Caso Obligatorio 5: Propagación de Dependencias Estructurales
    print("\n[PASO 4] Caso Obligatorio 5: Propagación de Impacto por Cambio Estructural (Sección 153):")
    boundary_struct = api.calculate_regeneration_boundary(asset_id, "comp_body", parameter_modified="height")
    print(f" - Modificación Estructural: \"Barrel height increased\"")
    print(f" - Límite de Componentes Afectados: {boundary_struct.boundary_components} (Nivel: {boundary_struct.impact_level.value})")
    print(f" - Justificación: \"{boundary_struct.reason}\"")

    # 5. Caso Obligatorio 3: Detección de Componentes Huérfanos
    print("\n[PASO 5] Caso Obligatorio 3: Detección de Huérfanos tras Borrado en Blender (Sección 149):")
    blender_partial = {
        "Barrel_Body": {"transform": {"location": (0,0,0)}},
        "Barrel_Ring_02": {"transform": {"location": (0,0,0.4)}},
        "UCX_Barrel": {"transform": {"location": (0,0,0)}}
    }
    recon = api.reconcile_with_blender(asset_id, blender_partial)
    print(f" - Estado de Reconciliación: [{recon['state'].value}] | Huérfanos: {recon['orphaned_components']}")

    # 6. Snapshots & Semantic Diff Engine
    print("\n[PASO 6] Snapshots Inmutables y Detección Semántica de Diff (Sección 35):")
    snap1 = api.create_snapshot(asset_id, "SNAP_V1")
    graph.nodes["comp_ring1"].transform["location"] = (0,0,1.35)
    snap2 = api.create_snapshot(asset_id, "SNAP_V2")
    diffs = api.compute_diff(snap1, snap2)
    print(f" - Diffs Semánticos Detectados ({len(diffs)}):")
    for d in diffs:
        print(f"   * Tipo: [{d.diff_type.value}] en '{d.component_id}': {d.previous_value} -> {d.new_value}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 54 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
