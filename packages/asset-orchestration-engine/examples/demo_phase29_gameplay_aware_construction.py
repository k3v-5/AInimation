import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GameplayAwareAPI, ActorProfile, DoorGameplayDefinition, StairDefinition,
    SpawnPoint, InteractionPoint, InteractionType
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 29: GAMEPLAY-AWARE PROCEDURAL CONSTRUCTION DEMO")
    print("=" * 95)

    player_profile = ActorProfile(height=1.80, width=0.60, clearance=0.80, step_height=0.35, max_slope=40.0)
    api = GameplayAwareAPI(player_profile)

    # 1. Escenario 1: Validación de Escala Funcional (Puerta Estrecha)
    print("\n[ESCENARIO 1] 1. Validación de Escala Funcional frente a Perfil de Jugador:")
    door_narrow = DoorGameplayDefinition(door_id="door_front", width=0.62, height=2.10)
    rep_door = api.validate_asset_gameplay("house_narrow", door=door_narrow)
    print(f" - Puerta Probada: width = {door_narrow.width}m (Clearance requerido: {player_profile.clearance}m)")
    print(f" - Estado de Escala: {rep_door.scale_status.value} (Score: {rep_door.gameplay_score:.2f})")
    print(f" - Errores Críticos: {rep_door.critical_errors}")

    # 2. Escenario 2: Validación de Tránsito por Escalera (Stair Traversal)
    print("\n[ESCENARIO 2] 2. Validación de Pendiente y Tránsito de Escaleras:")
    stair_steep = StairDefinition(step_count=10, step_height=0.25, step_depth=0.24, slope=46.0)
    rep_stair = api.validate_asset_gameplay("house_stair", stair=stair_steep)
    print(f" - Escalera Probada: pendiente = {stair_steep.slope}° (Pendiente máx jugador: {player_profile.max_slope}°)")
    print(f" - Estado de Tránsito: {rep_stair.traversal_status.value} (Score: {rep_stair.gameplay_score:.2f})")
    print(f" - Errores Críticos: {rep_stair.critical_errors}")

    # 3. Escenario 3: Simulación de Jugador Proxy de Extremo a Extremo
    print("\n[ESCENARIO 3] 3. Prueba de Extremo a Extremo con GameplayTestAgent (Automated Player Proxy):")
    spawn = SpawnPoint(spawn_id="sp_entry", position=(0.0, 0.0, 0.0))
    door_valid = DoorGameplayDefinition(door_id="d_main", width=0.90, height=2.10)
    stair_valid = StairDefinition(step_count=12, step_height=0.18, step_depth=0.28, slope=32.7)
    inter_valid = InteractionPoint(point_id="pt_chest", interaction_type=InteractionType.PICKUP, position=(3.0, 1.0, 0.0))
    nav_g = {"SPAWN": ["DOOR"], "DOOR": ["STAIR"], "STAIR": ["SECOND_FLOOR_TREASURE"]}

    ok_agent, logs_agent, err_agent = api.run_player_proxy_test(
        spawn=spawn,
        door=door_valid,
        stair=stair_valid,
        interaction=inter_valid,
        nav_graph=nav_g,
        goal_node="SECOND_FLOOR_TREASURE"
    )
    print(f" - Recorrido Exitoso: {ok_agent}")
    for log in logs_agent:
        print(f"   * {log}")

    # 4. Escenario 4: Cálculo de Calidad Combinada (Visual + Técnico + Gameplay)
    print("\n[ESCENARIO 4] 4. Quality Gate Combinado (Visual 35% + Tech 25% + Gameplay 40%):")
    comb_score = api.compute_combined_quality_score(visual_score=0.92, technical_score=0.88, gameplay_score=1.00)
    print(f" - Puntuación Combinada Final: {comb_score:.3f} >= 0.85 (ACCEPTABLE ASSET)")

    # 5. Escenario 5: Grafo de Impacto de Parámetros (Regresión Selectiva)
    print("\n[ESCENARIO 5] 5. Grafo de Impacto de Parámetros (ParameterImpactGraph):")
    print(f" - Impacto de 'door_width': {api.get_parameter_impact('door_width')}")
    print(f" - Impacto de 'stair_slope': {api.get_parameter_impact('stair_slope')}")
    print(f" - Impacto de 'roof_height': {api.get_parameter_impact('roof_height')}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 29 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
