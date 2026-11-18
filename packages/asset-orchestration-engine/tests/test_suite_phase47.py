import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cross_asset_dependency_world import (
    WorldDependencyAPI, NodeType, EdgeType, ChangeCategory
)

class TestCrossAssetDependencyPhase47(unittest.TestCase):
    def setUp(self):
        self.api = WorldDependencyAPI()

    def test_01_mandatory_case_1_shared_asset_consumers(self):
        """Mandatory Case 1: HOUSE_01, 02, 03 comparten WALL_SYSTEM_V3. Cambiar WALL_WIDTH afecta a los 3 y deja árboles intactos."""
        self.api.register_node("WALL_SYSTEM_V3", "Modular Walls v3", NodeType.COMPONENT)
        self.api.register_node("HOUSE_01", "House 01", NodeType.ASSET)
        self.api.register_node("HOUSE_02", "House 02", NodeType.ASSET)
        self.api.register_node("HOUSE_03", "House 03", NodeType.ASSET)
        self.api.register_node("TREE_OAK_01", "Oak Tree", NodeType.ASSET)
        self.api.register_node("ROCK_BOULDER_01", "Boulder", NodeType.ASSET)

        self.api.register_dependency("E1", "HOUSE_01", "WALL_SYSTEM_V3", EdgeType.USES)
        self.api.register_dependency("E2", "HOUSE_02", "WALL_SYSTEM_V3", EdgeType.USES)
        self.api.register_dependency("E3", "HOUSE_03", "WALL_SYSTEM_V3", EdgeType.USES)

        impact = self.api.analyze_change_impact("WALL_SYSTEM_V3", ChangeCategory.STRUCTURAL)
        self.assertIn("HOUSE_01", impact.direct_impacts)
        self.assertIn("HOUSE_02", impact.direct_impacts)
        self.assertIn("HOUSE_03", impact.direct_impacts)
        self.assertIn("TREE_OAK_01", impact.unaffected_nodes)
        self.assertIn("ROCK_BOULDER_01", impact.unaffected_nodes)

    def test_02_mandatory_case_2_material_change_no_geom_regen(self):
        """Mandatory Case 2: Cambiar WALL_MATERIAL actualiza instancias de material pero NO geometría."""
        self.api.register_node("MAT_STONE", "Stone Master Material", NodeType.MATERIAL)
        self.api.register_node("WALL_INSTANCE", "Wall Instance", NodeType.COMPONENT)
        self.api.register_dependency("E_MAT", "WALL_INSTANCE", "MAT_STONE", EdgeType.USES)

        impact = self.api.analyze_change_impact("MAT_STONE", ChangeCategory.MATERIAL)
        self.assertTrue(impact.requires_material_update)
        self.assertFalse(impact.requires_geometry_regeneration)

    def test_03_mandatory_case_3_wall_height_dependencies(self):
        """Mandatory Case 3: Cambiar WALL_HEIGHT detecta dependencias de ventanas, tejado, colisiones y LODs."""
        self.api.register_node("WALL_MAIN", "Main Wall", NodeType.COMPONENT)
        self.api.register_node("WINDOW_01", "Window", NodeType.COMPONENT)
        self.api.register_node("ROOF_01", "Roof", NodeType.COMPONENT)
        self.api.register_node("COLLISION_WALL", "Wall Collision", NodeType.COLLISION)
        self.api.register_node("LOD_WALL_01", "Wall LOD1", NodeType.LOD)

        self.api.register_dependency("E_WIN", "WINDOW_01", "WALL_MAIN", EdgeType.ATTACHED_TO)
        self.api.register_dependency("E_ROOF", "ROOF_01", "WALL_MAIN", EdgeType.ATTACHED_TO)
        self.api.register_dependency("E_COL", "COLLISION_WALL", "WALL_MAIN", EdgeType.GENERATED_FROM)
        self.api.register_dependency("E_LOD", "LOD_WALL_01", "WALL_MAIN", EdgeType.GENERATED_FROM)

        impact = self.api.analyze_change_impact("WALL_MAIN", ChangeCategory.STRUCTURAL)
        self.assertIn("WINDOW_01", impact.direct_impacts)
        self.assertIn("ROOF_01", impact.direct_impacts)
        self.assertIn("COLLISION_WALL", impact.potential_impacts)
        self.assertIn("LOD_WALL_01", impact.potential_impacts)

    def test_04_mandatory_case_4_delete_safety_gameplay_references(self):
        """Mandatory Case 4: Eliminar DOOR_MAIN detecta referencias de Blueprints y navegación antes de permitir borrado."""
        self.api.register_node("DOOR_MAIN", "Main Entrance Door", NodeType.COMPONENT)
        self.api.register_node("BP_DOOR_INTERACT", "Door Interaction BP", NodeType.BLUEPRINT)
        self.api.register_node("NAV_MESH_ENTRY", "Navmesh Entry Node", NodeType.NAVIGATION)

        self.api.register_dependency("E_BP", "BP_DOOR_INTERACT", "DOOR_MAIN", EdgeType.REFERENCES)
        self.api.register_dependency("E_NAV", "NAV_MESH_ENTRY", "DOOR_MAIN", EdgeType.DEPENDS_ON)

        safety = self.api.evaluate_delete_safety("DOOR_MAIN")
        self.assertFalse(safety["is_safe_to_delete"])
        self.assertIn("BP_DOOR_INTERACT", safety["critical_dependencies"])
        self.assertIn("NAV_MESH_ENTRY", safety["critical_dependencies"])

    def test_05_mandatory_case_5_impact_preview_shared_asset(self):
        """Mandatory Case 5: Modificar shared asset ofrece vista previa de impacto antes de ejecutar."""
        self.api.register_node("SHARED_BEAM", "Timber Beam", NodeType.COMPONENT)
        self.api.register_node("HOUSE_A", "House A", NodeType.ASSET)
        self.api.register_dependency("E_BEAM", "HOUSE_A", "SHARED_BEAM", EdgeType.USES)

        impact = self.api.analyze_change_impact("SHARED_BEAM", ChangeCategory.STRUCTURAL)
        self.assertEqual(len(impact.direct_impacts), 1)
        self.assertIn("HOUSE_A", impact.direct_impacts)

    def test_06_mandatory_case_6_circular_dependency_blocked(self):
        """Mandatory Case 6: Dependencia circular es detectada, bloqueada y explicada."""
        self.api.register_node("NODE_A", "Node A", NodeType.COMPONENT)
        self.api.register_node("NODE_B", "Node B", NodeType.COMPONENT)

        self.api.register_dependency("E_AB", "NODE_A", "NODE_B", EdgeType.DEPENDS_ON)
        self.api.register_dependency("E_BA", "NODE_B", "NODE_A", EdgeType.DEPENDS_ON)

        cycles = self.api.detect_cycles()
        self.assertIsNotNone(cycles)

        with self.assertRaises(ValueError) as ctx:
            self.api.plan_regeneration(["NODE_A", "NODE_B"])
        self.assertIn("DEPENDENCY_CYCLE_DETECTED", str(ctx.exception))

    def test_07_mandatory_case_7_world_context_isolation(self):
        """Mandatory Case 7: Dos mundos (WORLD_A, WORLD_B). Modificar asset de WORLD_A deja WORLD_B intacto."""
        self.api.register_node("ASSET_A1", "House in World A", NodeType.ASSET, world_id="WORLD_A")
        self.api.register_node("ASSET_B1", "Castle in World B", NodeType.ASSET, world_id="WORLD_B")

        # Planificar regeneración aislada para WORLD_A
        plan = self.api.plan_regeneration(["ASSET_A1", "ASSET_B1"], world_context_id="WORLD_A")
        self.assertIn("ASSET_A1", plan.execution_order)
        self.assertNotIn("ASSET_B1", plan.execution_order)

    def test_08_node_registration_and_query(self):
        """Test 8: Registro formal de nodos en el grafo."""
        node = self.api.register_node("TOWER_01", "Watchtower", NodeType.ASSET)
        self.assertEqual(node.node_id, "TOWER_01")
        self.assertEqual(self.api.graph.nodes["TOWER_01"].name, "Watchtower")

    def test_09_edge_registration_strength(self):
        """Test 9: Registro de aristas con fuerza de dependencia."""
        self.api.register_node("N1", "N1", NodeType.ASSET)
        self.api.register_node("N2", "N2", NodeType.COMPONENT)
        edge = self.api.register_dependency("E12", "N1", "N2")
        self.assertEqual(edge.strength.value, "HARD")

    def test_10_get_consumers(self):
        """Test 10: get_consumers devuelve nodos que consumen el target."""
        self.api.register_node("BASE", "Base", NodeType.COMPONENT)
        self.api.register_node("TOP", "Top", NodeType.COMPONENT)
        self.api.register_dependency("E_TOP", "TOP", "BASE")
        self.assertEqual(self.api.get_consumers("BASE"), ["TOP"])

    def test_11_get_dependencies(self):
        """Test 11: get_dependencies devuelve nodos requeridos."""
        self.api.register_node("BASE", "Base", NodeType.COMPONENT)
        self.api.register_node("TOP", "Top", NodeType.COMPONENT)
        self.api.register_dependency("E_TOP", "TOP", "BASE")
        self.assertEqual(self.api.get_dependencies("TOP"), ["BASE"])

    def test_12_topological_regeneration_order(self):
        """Test 12: Ordenamiento topológico: base se regenera antes que los muros."""
        self.api.register_node("FOUNDATION", "Foundation", NodeType.COMPONENT)
        self.api.register_node("WALLS", "Walls", NodeType.COMPONENT)
        self.api.register_dependency("E_FW", "WALLS", "FOUNDATION")

        plan = self.api.plan_regeneration(["FOUNDATION", "WALLS"])
        self.assertEqual(plan.execution_order, ["FOUNDATION", "WALLS"])

    def test_13_parallel_batch_grouping(self):
        """Test 13: Agrupación en lotes paralelos para nodos independientes."""
        self.api.register_node("DOOR_L", "Left Door", NodeType.COMPONENT)
        self.api.register_node("DOOR_R", "Right Door", NodeType.COMPONENT)
        plan = self.api.plan_regeneration(["DOOR_L", "DOOR_R"])
        self.assertEqual(len(plan.parallel_batches), 1)
        self.assertEqual(len(plan.parallel_batches[0]), 2)

    def test_14_graph_health_score(self):
        """Test 14: Cálculo de salud del grafo (1.0 saludable)."""
        self.api.register_node("N1", "N1", NodeType.ASSET)
        self.assertEqual(self.api.graph.calculate_health_score(), 1.0)

    def test_15_delete_safety_leaf_node(self):
        """Test 15: Nodo hoja sin dependientes es seguro de eliminar."""
        self.api.register_node("LEAF_DECORATION", "Flower Pot", NodeType.PROP)
        safety = self.api.evaluate_delete_safety("LEAF_DECORATION")
        self.assertTrue(safety["is_safe_to_delete"])

    def test_16_world_snapshot_creation(self):
        """Test 16: Creación y registro de snapshot de mundo."""
        self.api.register_node("N1", "N1", NodeType.ASSET)
        snap = self.api.create_snapshot("WORLD_01")
        self.assertIn("SNAP_WORLD_01", snap.snapshot_id)
        self.assertEqual(snap.node_count, 1)

    def test_17_multi_level_indirect_propagation(self):
        """Test 17: Propagación multinivel: Foundation -> Walls -> Roof -> Chimney."""
        self.api.register_node("FOUND", "Found", NodeType.COMPONENT)
        self.api.register_node("WALL", "Wall", NodeType.COMPONENT)
        self.api.register_node("ROOF", "Roof", NodeType.COMPONENT)
        self.api.register_node("CHIM", "Chim", NodeType.COMPONENT)

        self.api.register_dependency("E1", "WALL", "FOUND")
        self.api.register_dependency("E2", "ROOF", "WALL")
        self.api.register_dependency("E3", "CHIM", "ROOF")

        impact = self.api.analyze_change_impact("FOUND", ChangeCategory.STRUCTURAL)
        self.assertEqual(impact.direct_impacts, ["WALL"])
        self.assertIn("ROOF", impact.indirect_impacts)
        self.assertIn("CHIM", impact.indirect_impacts)

    def test_18_missing_source_edge_rejection(self):
        """Test 18: Arista con nodo origen inexistente lanza KeyError."""
        self.api.register_node("TARGET_OK", "Target", NodeType.COMPONENT)
        with self.assertRaises(KeyError):
            self.api.register_dependency("E_BAD", "SOURCE_GHOST", "TARGET_OK")

    def test_19_missing_target_edge_rejection(self):
        """Test 19: Arista con nodo destino inexistente lanza KeyError."""
        self.api.register_node("SOURCE_OK", "Source", NodeType.COMPONENT)
        with self.assertRaises(KeyError):
            self.api.register_dependency("E_BAD", "SOURCE_OK", "TARGET_GHOST")

    def test_20_end_to_end_world_dependency_pipeline(self):
        """Test 20: Flujo E2E: Grafo -> Análisis de Impacto -> Plan de Regeneración Topológico."""
        self.api.register_node("SHARED_WALL", "Wall", NodeType.COMPONENT)
        self.api.register_node("HOUSE_ALPHA", "House Alpha", NodeType.ASSET)
        self.api.register_node("HOUSE_BETA", "House Beta", NodeType.ASSET)

        self.api.register_dependency("E_A", "HOUSE_ALPHA", "SHARED_WALL")
        self.api.register_dependency("E_B", "HOUSE_BETA", "SHARED_WALL")

        impact = self.api.analyze_change_impact("SHARED_WALL", ChangeCategory.STRUCTURAL)
        self.assertEqual(len(impact.direct_impacts), 2)

        plan = self.api.plan_regeneration(["SHARED_WALL", "HOUSE_ALPHA", "HOUSE_BETA"])
        self.assertEqual(plan.execution_order[0], "SHARED_WALL")

if __name__ == "__main__":
    unittest.main()
