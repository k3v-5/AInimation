import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.semantic_asset_graph_twin import (
    SemanticDigitalTwinAPI, ReconciliationState, ComponentLifecycleState,
    DiffType, ImpactLevel
)

class TestSemanticAssetGraphTwinPhase54(unittest.TestCase):
    def setUp(self):
        self.api = SemanticDigitalTwinAPI()
        self.asset_id = "asset_042"
        
        # Setup estándar de barril
        self.api.register_component(self.asset_id, "comp_body", "asset_042.body", "BODY", "Barrel_Body", {"location": (0,0,0)}, "DarkWood")
        self.api.register_component(self.asset_id, "comp_ring1", "asset_042.ring_01", "RING", "Barrel_Ring_01", {"location": (0,0,1.2)}, "Iron")
        self.api.register_component(self.asset_id, "comp_ring2", "asset_042.ring_02", "RING", "Barrel_Ring_02", {"location": (0,0,0.4)}, "Iron")
        self.api.register_component(self.asset_id, "comp_col", "asset_042.collision", "COLLISION", "UCX_Barrel", {"location": (0,0,0)}, "Physics")

        self.api.add_dependency(self.asset_id, "comp_ring1", "comp_body")
        self.api.add_dependency(self.asset_id, "comp_ring2", "comp_body")
        self.api.add_dependency(self.asset_id, "comp_col", "comp_body")

    def test_01_mandatory_case_1_barrel_semantic_creation(self):
        """Mandatory Case 1: Barril creado con componentes semánticos y stable semantic_ids."""
        graph = self.api.get_or_create_graph(self.asset_id)
        self.assertEqual(len(graph.nodes), 4)
        node_ring1 = graph.get_node_by_semantic_id("asset_042.ring_01")
        self.assertIsNotNone(node_ring1)
        self.assertEqual(node_ring1.blender_object_name, "Barrel_Ring_01")

    def test_02_mandatory_case_2_local_correction_boundary_isolation(self):
        """Mandatory Case 2: 'Ring_01 is 15cm too low' calcula límite mínimo de regeneración [comp_ring1]."""
        boundary = self.api.calculate_regeneration_boundary(self.asset_id, "comp_ring1", parameter_modified="position")
        self.assertEqual(boundary.boundary_components, ["comp_ring1"])
        self.assertEqual(boundary.impact_level, ImpactLevel.LOW)

    def test_03_mandatory_case_3_orphan_component_detection(self):
        """Mandatory Case 3: Eliminar Ring_01 en Blender detecta componente huérfano (ORPHANED)."""
        blender_scene = {
            "Barrel_Body": {"transform": {"location": (0,0,0)}},
            "Barrel_Ring_02": {"transform": {"location": (0,0,0.4)}},
            "UCX_Barrel": {"transform": {"location": (0,0,0)}}
            # Falta Barrel_Ring_01
        }
        res = self.api.reconcile_with_blender(self.asset_id, blender_scene)
        self.assertEqual(res["state"], ReconciliationState.ORPHANED)
        self.assertIn("comp_ring1", res["orphaned_components"])

    def test_04_mandatory_case_4_targeted_recovery_ring_only(self):
        """Mandatory Case 4: Recuperación selectiva restaura comp_ring1 sin reconstruir comp_body."""
        graph = self.api.get_or_create_graph(self.asset_id)
        node = graph.nodes["comp_ring1"]
        node.lifecycle_state = ComponentLifecycleState.ACTIVE
        self.assertEqual(graph.nodes["comp_body"].lifecycle_state, ComponentLifecycleState.ACTIVE)

    def test_05_mandatory_case_5_dependency_impact_propagation(self):
        """Mandatory Case 5: Modificar altura del cuerpo propaga el límite de impacto a los 3 dependientes."""
        boundary = self.api.calculate_regeneration_boundary(self.asset_id, "comp_body", parameter_modified="height")
        self.assertEqual(boundary.impact_level, ImpactLevel.HIGH)
        self.assertIn("comp_body", boundary.boundary_components)
        self.assertIn("comp_ring1", boundary.boundary_components)
        self.assertIn("comp_ring2", boundary.boundary_components)
        self.assertIn("comp_col", boundary.boundary_components)

    def test_06_mandatory_case_6_protected_locked_component(self):
        """Mandatory Case 6: Body = APPROVED + LOCKED (is_locked = True) protege el nodo."""
        graph = self.api.get_or_create_graph(self.asset_id)
        graph.nodes["comp_body"].is_locked = True
        graph.nodes["comp_body"].lifecycle_state = ComponentLifecycleState.APPROVED
        self.assertTrue(graph.nodes["comp_body"].is_locked)

    def test_07_mandatory_case_7_variant_isolation(self):
        """Mandatory Case 7: Modificar variante Barrel_B no altera Barrel_A ni Barrel_Base."""
        self.api.register_component("barrel_base", "c_base", "base.body", "BODY", "SM_Base")
        self.api.register_component("barrel_a", "c_a", "a.body", "BODY", "SM_A")
        self.api.register_component("barrel_b", "c_b", "b.body", "BODY", "SM_B", {"location": (0,0,5)})

        g_a = self.api.get_or_create_graph("barrel_a")
        g_b = self.api.get_or_create_graph("barrel_b")
        self.assertEqual(g_a.nodes["c_a"].transform["location"], (0,0,0))
        self.assertEqual(g_b.nodes["c_b"].transform["location"], (0,0,5))

    def test_08_mandatory_case_8_reconciliation_blender_ahead(self):
        """Mandatory Case 8: Movimiento directo en Blender detecta BLENDER_AHEAD."""
        blender_scene = {
            "Barrel_Body": {"transform": {"location": (0,0,0)}},
            "Barrel_Ring_01": {"transform": {"location": (0,0,1.35)}}, # Movido en Blender
            "Barrel_Ring_02": {"transform": {"location": (0,0,0.4)}},
            "UCX_Barrel": {"transform": {"location": (0,0,0)}}
        }
        res = self.api.reconcile_with_blender(self.asset_id, blender_scene)
        self.assertEqual(res["state"], ReconciliationState.BLENDER_AHEAD)
        self.assertIn("comp_ring1", res["blender_ahead_components"])

    def test_09_mandatory_case_9_reconciliation_conflict_detection(self):
        """Mandatory Case 9: Modificación simultánea en Twin y Blender genera CONFLICT."""
        blender_scene = {
            "Barrel_Body": {"transform": {"location": (0,0,0)}},
            "Barrel_Ring_01": {"transform": {"location": (0,0,1.35)}},
            "Barrel_Ring_02": {"transform": {"location": (0,0,0.4)}},
            "UCX_Barrel": {"transform": {"location": (0,0,0)}}
        }
        res = self.api.reconcile_with_blender(self.asset_id, blender_scene, twin_modified_components=["comp_ring1"])
        self.assertEqual(res["state"], ReconciliationState.CONFLICT)
        self.assertIn("comp_ring1", res["conflict_components"])

    def test_10_mandatory_case_10_natural_query_top_ring(self):
        """Mandatory Case 10: 'el aro metálico de arriba' resuelve exactamente a comp_ring1."""
        target_id = self.api.resolve_natural_query(self.asset_id, "el aro metálico de arriba")
        self.assertEqual(target_id, "comp_ring1")

    def test_11_natural_query_bottom_ring(self):
        """Test 11: 'el aro metálico de abajo' resuelve a comp_ring2."""
        target_id = self.api.resolve_natural_query(self.asset_id, "el aro metálico de abajo")
        self.assertEqual(target_id, "comp_ring2")

    def test_12_natural_query_wood_body(self):
        """Test 12: 'el cuerpo de madera' resuelve a comp_body."""
        target_id = self.api.resolve_natural_query(self.asset_id, "el cuerpo de madera")
        self.assertEqual(target_id, "comp_body")

    def test_13_snapshot_creation_and_restoration(self):
        """Test 13: Creación y restauración de snapshot inmutable."""
        snap1 = self.api.create_snapshot(self.asset_id, "SNAP_1")
        graph = self.api.get_or_create_graph(self.asset_id)
        graph.nodes["comp_ring1"].transform["location"] = (0,0,2.0)
        self.assertEqual(graph.nodes["comp_ring1"].transform["location"], (0,0,2.0))

        graph.restore_snapshot(snap1)
        self.assertEqual(graph.nodes["comp_ring1"].transform["location"], (0,0,1.2))

    def test_14_asset_diff_transform_changed(self):
        """Test 14: AssetDiffEngine detecta COMPONENT_TRANSFORM_CHANGED."""
        snap1 = self.api.create_snapshot(self.asset_id, "SNAP_A")
        graph = self.api.get_or_create_graph(self.asset_id)
        graph.nodes["comp_ring1"].transform["location"] = (0,0,1.35)
        snap2 = self.api.create_snapshot(self.asset_id, "SNAP_B")

        diffs = self.api.compute_diff(snap1, snap2)
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0].diff_type, DiffType.COMPONENT_TRANSFORM_CHANGED)
        self.assertEqual(diffs[0].component_id, "comp_ring1")

    def test_15_asset_diff_component_added(self):
        """Test 15: AssetDiffEngine detecta COMPONENT_ADDED."""
        snap1 = self.api.create_snapshot(self.asset_id, "SNAP_INIT")
        self.api.register_component(self.asset_id, "comp_ring3", "asset_042.ring_03", "RING", "Barrel_Ring_03")
        snap2 = self.api.create_snapshot(self.asset_id, "SNAP_EXTRA")

        diffs = self.api.compute_diff(snap1, snap2)
        self.assertTrue(any(d.diff_type == DiffType.COMPONENT_ADDED for d in diffs))

    def test_16_semantic_id_lookup_fast(self):
        """Test 16: get_node_by_semantic_id devuelve nodo en O(1)."""
        graph = self.api.get_or_create_graph(self.asset_id)
        node = graph.get_node_by_semantic_id("asset_042.collision")
        self.assertIsNotNone(node)
        self.assertEqual(node.component_id, "comp_col")

    def test_17_reconciler_synchronized_state(self):
        """Test 17: Escena sincronizada devuelve SYNCHRONIZED."""
        blender_scene = {
            "Barrel_Body": {"transform": {"location": (0,0,0)}},
            "Barrel_Ring_01": {"transform": {"location": (0,0,1.2)}},
            "Barrel_Ring_02": {"transform": {"location": (0,0,0.4)}},
            "UCX_Barrel": {"transform": {"location": (0,0,0)}}
        }
        res = self.api.reconcile_with_blender(self.asset_id, blender_scene)
        self.assertEqual(res["state"], ReconciliationState.SYNCHRONIZED)

    def test_18_material_changed_diff(self):
        """Test 18: AssetDiffEngine detecta MATERIAL_CHANGED."""
        snap1 = self.api.create_snapshot(self.asset_id, "SNAP_M1")
        graph = self.api.get_or_create_graph(self.asset_id)
        graph.nodes["comp_body"].material_name = "LightWood"
        snap2 = self.api.create_snapshot(self.asset_id, "SNAP_M2")

        diffs = self.api.compute_diff(snap1, snap2)
        self.assertTrue(any(d.diff_type == DiffType.MATERIAL_CHANGED for d in diffs))

    def test_19_dependents_query(self):
        """Test 19: Consulta de dependientes sobre el nodo raíz."""
        graph = self.api.get_or_create_graph(self.asset_id)
        deps = graph.get_dependents("comp_body")
        self.assertEqual(len(deps), 3)

    def test_20_end_to_end_twin_handshake(self):
        """Test 20: Flujo E2E: Graph -> Natural Query -> Regeneration Boundary -> Snapshot Diff."""
        target = self.api.resolve_natural_query(self.asset_id, "el aro superior")
        self.assertEqual(target, "comp_ring1")
        boundary = self.api.calculate_regeneration_boundary(self.asset_id, target, "position")
        self.assertEqual(boundary.boundary_components, ["comp_ring1"])

if __name__ == "__main__":
    unittest.main()
