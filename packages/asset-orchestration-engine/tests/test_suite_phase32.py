import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ProceduralAssetAPI, IntentSpecificationAPI, AssetDNA, QualityLevel
)

class TestProceduralAssetBuildSystemPhase32(unittest.TestCase):
    def setUp(self):
        self.spec_api = IntentSpecificationAPI()
        self.proc_api = ProceduralAssetAPI()
        prompt = (
            "Quiero una casa medieval rural pequeña, vieja y ligeramente inclinada, "
            "con una puerta grande de madera, dos ventanas estrechas, "
            "una escalera interior al segundo piso y que el jugador pueda entrar."
        )
        self.spec, _, _ = self.spec_api.compile_intent(prompt, spec_id="house_rural_01")

    def test_01_full_procedural_house_generation_scenario_152(self):
        """Test 1: Scenario 152 - Generación completa de grafo de construcción a partir de AssetSpec."""
        graph = self.proc_api.build_asset(self.spec)
        self.assertEqual(graph.asset_id, "house_rural_01")
        self.assertIn("HOUSE.FOUNDATION", graph.nodes)
        self.assertIn("HOUSE.WALL.NORTH", graph.nodes)
        self.assertIn("HOUSE.WALL.SOUTH", graph.nodes)
        self.assertIn("HOUSE.DOOR.MAIN", graph.nodes)
        self.assertIn("HOUSE.ROOF", graph.nodes)
        self.assertIn("HOUSE.STAIRS", graph.nodes)
        self.assertIn("HOUSE.COLLISION", graph.nodes)
        self.assertGreaterEqual(len(graph.nodes), 8)

    def test_02_surgical_door_regeneration_scenario_153(self):
        """Test 2: Scenario 153 - Aumentar ancho de puerta un 15% regenera SOLO puerta y muro sur."""
        graph = self.proc_api.build_asset(self.spec)
        new_door_w = round(self.spec.door.width_m * 1.15, 2) # 0.90 * 1.15 = 1.04m

        rebuilt_nodes = self.proc_api.regenerate_door_width(graph, new_door_w)
        self.assertEqual(rebuilt_nodes, ["HOUSE.DOOR.MAIN", "HOUSE.WALL.SOUTH"])
        self.assertEqual(graph.dna.parameters["door_width"], new_door_w)

        # Verificar que techo y escaleras no fueron reconstruidos
        self.assertNotIn("HOUSE.ROOF", rebuilt_nodes)
        self.assertNotIn("HOUSE.STAIRS", rebuilt_nodes)

    def test_03_deterministic_geometry_hash_stability_scenario_154(self):
        """Test 3: Scenario 154 - Cinco ejecuciones idénticas producen exactamente el mismo geometry_hash."""
        hashes = []
        for _ in range(5):
            g = self.proc_api.build_asset(self.spec)
            hashes.append(g.compute_geometry_hash())
        self.assertEqual(len(set(hashes)), 1)

    def test_04_seed_separation_scenario_155(self):
        """Test 4: Scenario 155 - Cambiar detail_seed no altera el hash estructural."""
        dna1 = AssetDNA(spec_reference="house_01", structural_seed=42, detail_seed=1001)
        dna2 = AssetDNA(spec_reference="house_01", structural_seed=42, detail_seed=2002) # Cambia solo detalle

        g1 = self.proc_api.build_asset(self.spec, dna1)
        g2 = self.proc_api.build_asset(self.spec, dna2)

        self.assertEqual(g1.compute_geometry_hash(), g2.compute_geometry_hash())

    def test_05_unauthorized_feature_rejection_scenario_156(self):
        """Test 5: Scenario 156 - Intento de añadir características no autorizadas es bloqueado."""
        self.spec.unauthorized_requested = True
        with self.assertRaises(ValueError) as ctx:
            self.proc_api.build_asset(self.spec)
        self.assertIn("UNAUTHORIZED_FEATURE", str(ctx.exception))

    def test_06_blender_adapter_staging_and_atomic_commit(self):
        """Test 6: BlenderGeometryAdapter aisla en colección temporal y comitea atómicamente."""
        graph = self.proc_api.build_asset(self.spec)
        self.assertIn(f"__BUILD_{graph.asset_id}__", self.proc_api.adapter.temp_collections)

        prod_col = self.proc_api.commit_asset(graph)
        self.assertEqual(prod_col, f"ASSET_{graph.asset_id}")
        self.assertNotIn(f"__BUILD_{graph.asset_id}__", self.proc_api.adapter.temp_collections)

    def test_07_geometry_report_metrics(self):
        """Test 7: GeometryReport genera métricas de polígonos, vértices y cajas de colisión."""
        graph = self.proc_api.build_asset(self.spec)
        rep = self.proc_api.generate_geometry_report(graph)
        self.assertTrue(rep.is_valid)
        self.assertGreater(rep.triangle_count, 50)
        self.assertEqual(rep.quality_level, QualityLevel.FINAL)
        self.assertIn("STONE_FOUNDATION", rep.materials)

    def test_08_stair_step_geometry_and_navigation(self):
        """Test 8: StairBuilder genera escalones transitables con tags de navegación."""
        graph = self.proc_api.build_asset(self.spec)
        stair_node = graph.nodes["HOUSE.STAIRS"]
        self.assertEqual(len(stair_node.primitives), 12)
        self.assertIn("NAVIGATION", stair_node.primitives[0].tags)

    def test_09_segmented_wall_openings(self):
        """Test 9: Muro sur se divide en secciones dejando el hueco de la puerta."""
        graph = self.proc_api.build_asset(self.spec)
        south_wall = graph.nodes["HOUSE.WALL.SOUTH"]
        self.assertEqual(len(south_wall.primitives), 3) # Izquierda, derecha, dintel

    def test_10_ordered_construction_passes(self):
        """Test 10: Grafo contiene nodos clasificados en pasadas estructurales, funcionales y de detalle."""
        graph = self.proc_api.build_asset(self.spec)
        passes = {n.pass_level.value for n in graph.nodes.values()}
        self.assertIn("STRUCTURAL", passes)
        self.assertIn("FUNCTIONAL", passes)
        self.assertIn("DETAIL", passes)

if __name__ == "__main__":
    unittest.main()
