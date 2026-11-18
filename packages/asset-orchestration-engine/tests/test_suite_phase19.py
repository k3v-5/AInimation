import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    SceneOrchestrationAPI, SceneIntent, MockBlenderProvider, ProxyScene,
    SceneNode, ProxyBounds, ReconciliationStatus
)

class TestSceneOrchestrationPhase19(unittest.TestCase):
    def setUp(self):
        self.scene_api = SceneOrchestrationAPI(max_scene_assets=50)
        self.provider = MockBlenderProvider()

    def test_01_scene_planning_and_landmarks(self):
        """Test 1: Plan - Genera plan con 8 casas, plaza, herrería y torre."""
        intent = SceneIntent(
            scene_id="village_01",
            theme="medieval_village",
            style="stylized",
            requirements={"houses": 8, "plaza": 1, "blacksmith": 1, "tower": 1}
        )
        ok, plan, msg = self.scene_api.plan_scene(intent)
        self.assertTrue(ok)
        self.assertEqual(len(plan.nodes), 11)
        self.assertIn("plaza_001", plan.nodes)
        self.assertIn("tower_001", plan.nodes)
        self.assertIn("blacksmith_001", plan.nodes)
        self.assertIn("house_008", plan.nodes)

    def test_02_proxy_spatial_validation(self):
        """Test 2: Proxy - Valida ausencia de colisiones en la distribución inicial."""
        intent = SceneIntent(
            scene_id="village_02",
            theme="medieval_village",
            style="stylized",
            requirements={"houses": 8, "plaza": 1, "blacksmith": 1, "tower": 1}
        )
        _, plan, _ = self.scene_api.plan_scene(intent)
        ok_sp, errors, summary = self.scene_api.preview_scene(plan)
        self.assertTrue(ok_sp)
        self.assertEqual(len(errors), 0)
        self.assertEqual(summary.total_assets, 11)

    def test_03_collision_overlap_detection(self):
        """Test 3: Collision - Detecta solapamiento si dos nodos comparten bounding box."""
        nodes = {
            "box_A": SceneNode("box_A", "house", "tpl", "var", "SECONDARY", bounds=ProxyBounds((0, 0, 0), (5, 5, 5))),
            "box_B": SceneNode("box_B", "house", "tpl", "var", "SECONDARY", bounds=ProxyBounds((2, 2, 2), (7, 7, 7)))
        }
        ok, errors = ProxyScene.validate_spatial_integrity(nodes)
        self.assertFalse(ok)
        self.assertIn("SPATIAL_OVERLAP_ERROR", errors[0])

    def test_04_full_batch_scene_build_scenario_127(self):
        """Test 4: Scenario 127 - Construcción en lote de la aldea en el provider."""
        intent = SceneIntent(
            scene_id="village_127",
            theme="medieval_village",
            style="stylized",
            requirements={"houses": 8, "plaza": 1, "blacksmith": 1, "tower": 1}
        )
        _, plan, _ = self.scene_api.plan_scene(intent)
        built_count, is_idemp, _ = self.scene_api.build_scene(plan, self.provider)
        self.assertEqual(built_count, 11)
        self.assertFalse(is_idemp)
        self.assertIn("village_127_house_001", self.provider.assets)
        self.assertIn("village_127_plaza_001", self.provider.assets)

    def test_05_single_asset_isolated_rebuild_scenario_128(self):
        """Test 5: Scenario 128 - Mover blacksmith_001 reconstruye sólo 1 asset (Rebuild Ratio = 1/11)."""
        intent = SceneIntent(
            scene_id="village_128",
            theme="medieval_village",
            style="stylized",
            requirements={"houses": 8, "plaza": 1, "blacksmith": 1, "tower": 1}
        )
        _, plan, _ = self.scene_api.plan_scene(intent)
        self.scene_api.build_scene(plan, self.provider)

        rebuilt_count, ratio, msg = self.scene_api.rebuild_node("village_128", "blacksmith_001", self.provider)
        self.assertEqual(rebuilt_count, 1)
        self.assertAlmostEqual(ratio, 1 / 11, places=2)

    def test_06_checkpoint_and_resume_scenario_130(self):
        """Test 6: Scenario 130 - Fallo simulado en nodo 4 se reanuda completando los restantes 7."""
        intent = SceneIntent(
            scene_id="village_130",
            theme="medieval_village",
            style="stylized",
            requirements={"houses": 8, "plaza": 1, "blacksmith": 1, "tower": 1}
        )
        _, plan, _ = self.scene_api.plan_scene(intent)

        # Fallo simulado tras 4 nodos
        built_first, _, _ = self.scene_api.build_scene(plan, self.provider, fail_at_index=4)
        self.assertEqual(built_first, 4)

        # Reanudación
        resumed_count, msg = self.scene_api.resume_scene_build("village_130", plan, self.provider)
        self.assertEqual(resumed_count, 7)
        self.assertEqual(len(self.provider.assets), 11)

    def test_07_deterministic_seed_reproduction_scenario_131(self):
        """Test 7: Scenario 131 - Mismo seed produce exactamente la misma distribución de nodos."""
        intent1 = SceneIntent(scene_id="v_seed1", theme="medieval", style="stylized", seed=12345, requirements={"houses": 4})
        intent2 = SceneIntent(scene_id="v_seed2", theme="medieval", style="stylized", seed=12345, requirements={"houses": 4})
        _, plan1, _ = self.scene_api.plan_scene(intent1)
        _, plan2, _ = self.scene_api.plan_scene(intent2)
        self.assertEqual(plan1.nodes["house_001"].location, plan2.nodes["house_001"].location)

    def test_08_scene_budget_enforcement(self):
        """Test 8: Budget - Superar max_assets produce SCENE_BUDGET_EXCEEDED."""
        strict_api = SceneOrchestrationAPI(max_scene_assets=5)
        intent = SceneIntent(scene_id="v_huge", theme="medieval", style="stylized", requirements={"houses": 8})
        ok, _, msg = strict_api.plan_scene(intent)
        self.assertFalse(ok)
        self.assertIn("SCENE_BUDGET_EXCEEDED", msg)

    def test_09_idempotent_build(self):
        """Test 9: Idempotency - Ejecutar build sobre escena limpia devuelve 0 builds y is_idempotent=True."""
        intent = SceneIntent(scene_id="v_idemp", theme="medieval", style="stylized", requirements={"houses": 2})
        _, plan, _ = self.scene_api.plan_scene(intent)
        self.scene_api.build_scene(plan, self.provider)

        # Segunda llamada
        count, is_idemp, _ = self.scene_api.build_scene(plan, self.provider)
        self.assertEqual(count, 0)
        self.assertTrue(is_idemp)

    def test_10_scene_reconciliation(self):
        """Test 10: Reconciliation - Detecta assets creados y assets faltantes."""
        intent = SceneIntent(scene_id="v_rec", theme="medieval", style="stylized", requirements={"houses": 2})
        _, plan, _ = self.scene_api.plan_scene(intent)
        
        # Antes de construir -> MISSING
        res_before = self.scene_api.reconcile_scene("v_rec", self.provider)
        self.assertEqual(res_before["status"], ReconciliationStatus.MISSING)

        # Después de construir -> MATCH
        self.scene_api.build_scene(plan, self.provider)
        res_after = self.scene_api.reconcile_scene("v_rec", self.provider)
        self.assertEqual(res_after["status"], ReconciliationStatus.MATCH)

if __name__ == "__main__":
    unittest.main()
