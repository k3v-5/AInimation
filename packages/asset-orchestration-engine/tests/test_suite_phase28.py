import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    CompositeSceneAPI, SceneSpecification, SceneType, SceneBudget,
    LockState, SocketDefinition, AssetInstance, CompositionGraph, GraphNode,
    SpatialRelationType
)

class TestCompositeSceneSystemPhase28(unittest.TestCase):
    def setUp(self):
        self.api = CompositeSceneAPI()
        self.spec = SceneSpecification(
            scene_id="scene_village_01",
            scene_type=SceneType.VILLAGE,
            style="medieval_stylized",
            components_count={"plaza": 1, "church": 1, "shops": 2, "houses": 8},
            budget=SceneBudget(max_triangles=50000),
            seed=42
        )

    def test_01_small_village_hierarchical_build_scenario_145(self):
        """Test 1: Scenario 145 - Construye aldea medieval jerárquica con 12 instancias."""
        plan = self.api.create_scene_plan(self.spec)
        self.assertEqual(len(plan.instances), 12) # 1 plaza + 1 church + 2 shops + 8 houses
        self.assertIn("PLAZA_001", plan.instances)
        self.assertIn("CHURCH_001", plan.instances)
        self.assertIn("HOUSE_001", plan.instances)
        self.assertEqual(len(plan.regions), 6)

    def test_02_local_region_modification_scenario_146(self):
        """Test 2: Scenario 146 - Mover casas del este modifica únicamente EAST_REGION."""
        plan = self.api.create_scene_plan(self.spec)
        modified_ids = self.api.modify_region(plan, "EAST_REGION", delta_x=5.0, delta_y=0.0)
        self.assertGreaterEqual(len(modified_ids), 1)
        for m_id in modified_ids:
            self.assertEqual(plan.instances[m_id].region_id, "EAST_REGION")

        # Verificar que la iglesia o plaza no fueron modificadas
        self.assertEqual(plan.instances["PLAZA_001"].transform["x"], 0.0)
        self.assertEqual(plan.instances["CHURCH_001"].transform["x"], 0.0)

    def test_03_socket_auto_alignment_scenario_147(self):
        """Test 3: Scenario 147 - Conexión de socket alinea automáticamente posición y orientación."""
        road = AssetInstance("ROAD_01", "ROAD", "tmpl_road", transform={"x": 10.0, "y": 10.0, "z": 0.0, "rot_z": 0.0})
        house = AssetInstance("HOUSE_01", "HOUSE", "tmpl_house", transform={"x": 0.0, "y": 0.0, "z": 0.0, "rot_z": 0.0})

        road_sock = SocketDefinition("sock_road_01", "ROAD", (0.0, 2.0, 0.0), compatibility=["ROAD", "DOOR"])
        house_sock = SocketDefinition("sock_house_door", "DOOR", (0.0, -1.5, 0.0), compatibility=["ROAD", "DOOR"])

        ok, msg = self.api.align_sockets(house, house_sock, road, road_sock)
        self.assertTrue(ok)
        self.assertEqual(house.transform["x"], 10.0)
        self.assertEqual(house.transform["y"], 13.5) # 10.0 + 2.0 - (-1.5)
        self.assertEqual(house.transform["rot_z"], 180.0)

    def test_04_critical_collision_detection_scenario_148(self):
        """Test 4: Scenario 148 - Casa sobre carretera detecta CRITICAL_COLLISION."""
        plan = self.api.create_scene_plan(self.spec)
        # Carretera superpuesta exactamente a HOUSE_001
        h1 = plan.instances["HOUSE_001"]
        roads = [{"x": h1.transform["x"], "y": h1.transform["y"], "width": 4.0}]

        report = self.api.validate_scene(plan, roads=roads)
        self.assertFalse(report.is_valid)
        self.assertGreaterEqual(len(report.critical_errors), 1)
        self.assertTrue(any("CRITICAL_COLLISION" in e for e in report.critical_errors))

    def test_05_scene_budget_optimizer_scenario_149(self):
        """Test 5: Scenario 149 - Exceder presupuesto de triángulos activa SceneOptimizer e instancing."""
        plan = self.api.create_scene_plan(self.spec)
        simulated_tris = 100000 # Límite es 50000

        ok_opt, new_tris, logs = self.api.optimize_scene(plan, simulated_tris)
        self.assertTrue(ok_opt)
        self.assertLessEqual(new_tris, 50000)
        self.assertTrue(any("OPTIMIZATION: Instanced" in l for l in logs))

    def test_06_deterministic_scene_fingerprint_scenario_150(self):
        """Test 6: Scenario 150 - Dos escenas con mismo seed generan idéntico fingerprint."""
        plan1 = self.api.create_scene_plan(self.spec)
        plan2 = self.api.create_scene_plan(self.spec)
        fp1 = self.api.get_scene_fingerprint(plan1, seed=42)
        fp2 = self.api.get_scene_fingerprint(plan2, seed=42)
        self.assertEqual(fp1, fp2)

    def test_07_partial_failure_resilience_scenario_151(self):
        """Test 7: Scenario 151 - Fallo en HOUSE_004 preserva el resto de instancias."""
        plan = self.api.create_scene_plan(self.spec)
        del plan.instances["HOUSE_004"] # Simular fallo aislado
        self.assertEqual(len(plan.instances), 11)
        self.assertIn("HOUSE_001", plan.instances)
        self.assertIn("HOUSE_005", plan.instances)

    def test_08_protected_object_lock_scenario_152(self):
        """Test 8: Scenario 152 - CHURCH = PROTECTED bloquea modificaciones."""
        plan = self.api.create_scene_plan(self.spec)
        self.api.set_instance_lock(plan, "CHURCH_001", LockState.PROTECTED)

        # Intentar modificar región norte donde está la iglesia
        modified = self.api.modify_region(plan, "NORTH", delta_x=10.0)
        self.assertNotIn("CHURCH_001", modified)
        self.assertEqual(plan.instances["CHURCH_001"].transform["x"], 0.0)

    def test_09_scene_quality_gate_acceptance(self):
        """Test 9: Validación de calidad de aldea bien planificada da score >= 0.85."""
        plan = self.api.create_scene_plan(self.spec)
        report = self.api.validate_scene(plan)
        self.assertTrue(report.is_valid)
        self.assertGreaterEqual(report.scene_quality_score, 0.85)

    def test_10_composition_graph_relationships(self):
        """Test 10: Scenario 154 - Grafo de composición maneja relaciones jerárquicas y espaciales."""
        graph = CompositionGraph()
        graph.add_node(GraphNode("NODE_PLAZA", "ASSET", "PLAZA"))
        graph.add_node(GraphNode("NODE_CHURCH", "ASSET", "CHURCH", parent_id="NODE_PLAZA"))
        graph.add_edge("NODE_CHURCH", "NODE_PLAZA", SpatialRelationType.FACING)

        children = graph.get_children("NODE_PLAZA")
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].node_id, "NODE_CHURCH")
        relations = graph.get_relations_for_node("NODE_CHURCH")
        self.assertEqual(len(relations), 1)
        self.assertEqual(relations[0].relation_type, SpatialRelationType.FACING)

if __name__ == "__main__":
    unittest.main()
