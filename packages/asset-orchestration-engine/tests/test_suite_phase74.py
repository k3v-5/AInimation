import os
import sys
import unittest
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.knowledge_graph import (
    NodeType, GraphNode, RelationshipType, GraphEdge, ProjectKnowledgeGraphStore,
    DuplicateSemanticIdentityError, GraphQueryEngine, GraphImpactAnalyzer, ImpactReport,
    GraphConsistencyValidator, DependencyCycleDetectedError, GraphDiffEngine,
    GraphSnapshotService, GraphProvenanceTracker, BlenderGraphExtractor,
    GraphGovernanceGuard, GraphPermissionDeniedError, ProjectKnowledgeGraphAPI
)

class TestSuitePhase74ProjectKnowledgeGraph(unittest.TestCase):
    """
    Complete unit and integration test suite for Phase 74: Project Knowledge Graph.
    """
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "test_kg.json")
        self.api = ProjectKnowledgeGraphAPI(persistence_path=self.db_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_01_root_project_node_initialization(self):
        root = self.api.get_node("PROJECT_DARX")
        self.assertIsNotNone(root)
        self.assertEqual(root.node_type, NodeType.PROJECT)
        self.assertEqual(root.project_id, "DarX")
        self.assertTrue(root.verify_integrity())

    def test_02_node_creation_and_retrieval(self):
        node = GraphNode(
            node_id="ASSET_VANDAL_001",
            node_type=NodeType.ASSET,
            semantic_id="weapon.darx.vandal.001",
            metadata={"caliber": "7.62mm"}
        )
        self.api.add_node(node)
        fetched = self.api.get_node("ASSET_VANDAL_001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.semantic_id, "weapon.darx.vandal.001")
        self.assertEqual(fetched.metadata["caliber"], "7.62mm")

    def test_03_duplicate_semantic_id_prevention(self):
        node1 = GraphNode(node_id="ASSET_1", node_type=NodeType.ASSET, semantic_id="weapon.unique.001")
        node2 = GraphNode(node_id="ASSET_2", node_type=NodeType.ASSET, semantic_id="weapon.unique.001")
        self.api.add_node(node1)
        with self.assertRaises(DuplicateSemanticIdentityError):
            self.api.add_node(node2)

    def test_04_typed_edge_creation_and_integrity(self):
        asset = GraphNode(node_id="W_001", node_type=NodeType.ASSET, semantic_id="weapon.carbine.001")
        mat = GraphNode(node_id="M_001", node_type=NodeType.MATERIAL)
        self.api.add_node(asset)
        self.api.add_node(mat)

        edge = GraphEdge(
            edge_id="E_W_M_01",
            source_node="W_001",
            target_node="M_001",
            relationship_type=RelationshipType.USES,
            agent_id="agent.strategy"
        )
        self.api.add_edge(edge)
        self.assertTrue(edge.verify_integrity())
        fetched_edge = self.api.get_edge("E_W_M_01")
        self.assertIsNotNone(fetched_edge)
        self.assertEqual(fetched_edge.relationship_type, RelationshipType.USES)

    def test_05_neighbors_traversal(self):
        n_a = GraphNode(node_id="A", node_type=NodeType.ASSET)
        n_b = GraphNode(node_id="B", node_type=NodeType.MATERIAL)
        self.api.add_node(n_a)
        self.api.add_node(n_b)
        self.api.add_edge(GraphEdge("E1", "A", "B", RelationshipType.USES))

        out_neighbors = self.api.queries.neighbors("A", direction="OUT")
        self.assertEqual(len(out_neighbors), 1)
        self.assertEqual(out_neighbors[0][0].node_id, "B")

        in_neighbors = self.api.queries.neighbors("B", direction="IN")
        self.assertEqual(len(in_neighbors), 1)
        self.assertEqual(in_neighbors[0][0].node_id, "A")

    def test_06_dependency_and_dependent_traversal(self):
        weapon = GraphNode(node_id="WP", node_type=NodeType.ASSET)
        barrel = GraphNode(node_id="COMP_BARREL", node_type=NodeType.ASSET_COMPONENT)
        mat = GraphNode(node_id="MAT_TITANIUM", node_type=NodeType.MATERIAL)

        self.api.add_node(weapon)
        self.api.add_node(barrel)
        self.api.add_node(mat)

        self.api.add_edge(GraphEdge("E_WP_COMP", "WP", "COMP_BARREL", RelationshipType.CONTAINS))
        self.api.add_edge(GraphEdge("E_COMP_MAT", "COMP_BARREL", "MAT_TITANIUM", RelationshipType.USES))

        # Barrel depends on titanium
        deps = self.api.get_dependencies("COMP_BARREL")
        self.assertIn("MAT_TITANIUM", [d.node_id for d in deps])

        # Titanium dependents include Barrel
        dependents = self.api.get_dependents("MAT_TITANIUM")
        self.assertIn("COMP_BARREL", [d.node_id for d in dependents])

    def test_07_shortest_path_search(self):
        for name in ["N1", "N2", "N3", "N4"]:
            self.api.add_node(GraphNode(node_id=name, node_type=NodeType.OPERATION))
        self.api.add_edge(GraphEdge("E12", "N1", "N2", RelationshipType.PRODUCES))
        self.api.add_edge(GraphEdge("E23", "N2", "N3", RelationshipType.PRODUCES))
        self.api.add_edge(GraphEdge("E34", "N3", "N4", RelationshipType.PRODUCES))

        path = self.api.queries.find_path("N1", "N4")
        self.assertEqual(path, ["N1", "N2", "N3", "N4"])

    def test_08_impact_analysis_on_material_change(self):
        weapon = GraphNode(node_id="WP_VANDAL", node_type=NodeType.ASSET)
        receiver = GraphNode(node_id="COMP_REC", node_type=NodeType.ASSET_COMPONENT)
        mat = GraphNode(node_id="MAT_ALLOY", node_type=NodeType.MATERIAL)

        self.api.add_node(weapon)
        self.api.add_node(receiver)
        self.api.add_node(mat)

        self.api.add_edge(GraphEdge("E1", "COMP_REC", "MAT_ALLOY", RelationshipType.USES))
        self.api.add_edge(GraphEdge("E2", "WP_VANDAL", "MAT_ALLOY", RelationshipType.USES))

        report = self.api.analyze_impact("MAT_ALLOY")
        self.assertIn("COMP_REC", report.affected_components)
        self.assertIn("WP_VANDAL", report.affected_assets)
        self.assertIn("WP_VANDAL", report.regeneration_candidates)

    def test_09_consistency_validation_broken_edges(self):
        n1 = GraphNode(node_id="N1", node_type=NodeType.ASSET)
        self.api.add_node(n1)
        # Edge to non-existent node
        self.api.add_edge(GraphEdge("E_BROKEN", "N1", "GHOST_NODE", RelationshipType.USES))

        rep = self.api.validate_consistency()
        self.assertFalse(rep.is_valid)
        self.assertIn("E_BROKEN", rep.broken_edges)

    def test_10_consistency_validation_cycle_detection(self):
        c1 = GraphNode(node_id="C1", node_type=NodeType.ASSET_COMPONENT)
        c2 = GraphNode(node_id="C2", node_type=NodeType.ASSET_COMPONENT)
        self.api.add_node(c1)
        self.api.add_node(c2)

        self.api.add_edge(GraphEdge("E_C12", "C1", "C2", RelationshipType.DEPENDS_ON))
        self.api.add_edge(GraphEdge("E_C21", "C2", "C1", RelationshipType.DEPENDS_ON))

        rep = self.api.validate_consistency()
        self.assertFalse(rep.is_valid)
        self.assertGreaterEqual(len(rep.cycles_detected), 1)

    def test_11_snapshot_and_restore(self):
        n1 = GraphNode(node_id="SNAP_NODE_1", node_type=NodeType.ASSET)
        self.api.add_node(n1)
        snap = self.api.create_snapshot("SNAP_TEST_001")
        self.assertEqual(snap.snapshot_id, "SNAP_TEST_001")

        # Mutate
        self.api.store.remove_node("SNAP_NODE_1")
        self.assertIsNone(self.api.get_node("SNAP_NODE_1"))

        # Restore
        self.api.restore_snapshot("SNAP_TEST_001")
        self.assertIsNotNone(self.api.get_node("SNAP_NODE_1"))

    def test_12_graph_diff_engine(self):
        n1 = GraphNode(node_id="DIFF_N1", node_type=NodeType.ASSET)
        self.api.add_node(n1)
        self.api.create_snapshot("SNAP_BEFORE")

        n2 = GraphNode(node_id="DIFF_N2", node_type=NodeType.MATERIAL)
        self.api.add_node(n2)
        self.api.create_snapshot("SNAP_AFTER")

        diff = self.api.compare_snapshots("SNAP_BEFORE", "SNAP_AFTER")
        self.assertTrue(diff.has_changes)
        self.assertIn("DIFF_N2", diff.nodes_added)

    def test_13_atomic_transactions_commit_and_rollback(self):
        self.api.store.begin_transaction()
        self.api.add_node(GraphNode(node_id="TX_NODE", node_type=NodeType.ASSET))
        self.assertIsNotNone(self.api.get_node("TX_NODE"))
        self.api.store.rollback()
        self.assertIsNone(self.api.get_node("TX_NODE"))

        self.api.store.begin_transaction()
        self.api.add_node(GraphNode(node_id="TX_COMMITTED", node_type=NodeType.ASSET))
        self.api.store.commit()
        self.assertIsNotNone(self.api.get_node("TX_COMMITTED"))

    def test_14_provenance_full_lineage_trace(self):
        ref = GraphNode(node_id="REF_01", node_type=NodeType.REFERENCE)
        req = GraphNode(node_id="REQ_01", node_type=NodeType.REQUIREMENT)
        asset = GraphNode(node_id="WP_VANDAL_LINEAGE", node_type=NodeType.ASSET)
        mat = GraphNode(node_id="MAT_DARK", node_type=NodeType.MATERIAL)

        self.api.add_node(ref)
        self.api.add_node(req)
        self.api.add_node(asset)
        self.api.add_node(mat)

        self.api.add_edge(GraphEdge("E_REF", "REF_01", "WP_VANDAL_LINEAGE", RelationshipType.DERIVED_FROM))
        self.api.add_edge(GraphEdge("E_REQ", "REQ_01", "WP_VANDAL_LINEAGE", RelationshipType.SATISFIES))
        self.api.add_edge(GraphEdge("E_MAT", "WP_VANDAL_LINEAGE", "MAT_DARK", RelationshipType.USES))

        lineage = self.api.trace_lineage("WP_VANDAL_LINEAGE")
        self.assertIn("REF_01", lineage["references"])
        self.assertIn("REQ_01", lineage["requirements"])
        self.assertIn("MAT_DARK", lineage["materials"])

    def test_15_governance_unauthorized_node_creation_denied(self):
        # Visual critic is not allowed to create structural components
        node = GraphNode(node_id="ILLEGAL_COMP", node_type=NodeType.ASSET_COMPONENT)
        with self.assertRaises(GraphPermissionDeniedError):
            self.api.add_node(node, agent_id="agent.visual.critic")

    def test_16_blender_scene_extraction_ingest(self):
        scene_data = {
            "objects": [
                {"name": "WP_Receiver", "materials": ["M_Titanium"]},
                {"name": "WP_Barrel", "materials": ["M_Titanium", "M_Carbon"]}
            ]
        }
        created = self.api.ingest_blender_scene(
            blend_file_path="Art/Blender/DarX_Assets.blend",
            scene_data=scene_data,
            semantic_asset_id="weapon.darx.vandal.001"
        )
        self.assertIn("OBJ_WP_Receiver", created)
        self.assertIn("MAT_M_Titanium", created)
        self.assertIn("MAT_M_Carbon", created)

    def test_17_persistence_reload_across_instances(self):
        self.api.add_node(GraphNode(node_id="PERSIST_NODE", node_type=NodeType.ASSET, semantic_id="weapon.persist.001"))
        
        # New API instance from same disk file
        api2 = ProjectKnowledgeGraphAPI(persistence_path=self.db_path)
        fetched = api2.get_node("PERSIST_NODE")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.semantic_id, "weapon.persist.001")

    def test_18_version_graph_branching(self):
        v1 = GraphNode(node_id="V_1", node_type=NodeType.VERSION, metadata={"version": "1.0"})
        v2 = GraphNode(node_id="V_2", node_type=NodeType.VERSION, metadata={"version": "2.0"})
        v_exp = GraphNode(node_id="V_EXP", node_type=NodeType.VERSION, metadata={"version": "2.0-exp"})

        self.api.add_node(v1)
        self.api.add_node(v2)
        self.api.add_node(v_exp)

        self.api.add_edge(GraphEdge("E_V2_V1", "V_2", "V_1", RelationshipType.PREVIOUS_VERSION))
        self.api.add_edge(GraphEdge("E_VEXP_V1", "V_EXP", "V_1", RelationshipType.PREVIOUS_VERSION))

        # Both branch from V1
        branches = self.api.queries.neighbors("V_1", direction="IN")
        self.assertEqual(len(branches), 2)
        branch_ids = [b[0].node_id for b in branches]
        self.assertIn("V_2", branch_ids)
        self.assertIn("V_EXP", branch_ids)

    def test_19_job_and_checkpoint_graph_integration(self):
        job = GraphNode(node_id="JOB_7401", node_type=NodeType.JOB, metadata={"state": "COMPLETED"})
        cp = GraphNode(node_id="CP_03", node_type=NodeType.CHECKPOINT)
        op = GraphNode(node_id="OP_MESH_BEVEL", node_type=NodeType.OPERATION)

        self.api.add_node(job)
        self.api.add_node(cp)
        self.api.add_node(op)

        self.api.add_edge(GraphEdge("E_CP_JOB", "CP_03", "JOB_7401", RelationshipType.BELONGS_TO))
        self.api.add_edge(GraphEdge("E_OP_JOB", "OP_MESH_BEVEL", "JOB_7401", RelationshipType.BELONGS_TO))

        job_elements = self.api.queries.neighbors("JOB_7401", direction="IN")
        self.assertEqual(len(job_elements), 2)

    def test_20_tampered_node_integrity_failure(self):
        node = GraphNode(node_id="TAMPER_TEST", node_type=NodeType.ASSET, metadata={"val": 10})
        self.assertTrue(node.verify_integrity())
        node.metadata["val"] = 999  # Tampered without recalculating hash
        self.assertFalse(node.verify_integrity())

    def test_21_tampered_edge_integrity_failure(self):
        edge = GraphEdge(edge_id="E_TAMPER", source_node="A", target_node="B", relationship_type=RelationshipType.USES)
        self.assertTrue(edge.verify_integrity())
        edge.target_node = "C"
        self.assertFalse(edge.verify_integrity())

    def test_22_multi_asset_material_impact_propagation(self):
        mat = GraphNode(node_id="MAT_SHARED_TITANIUM", node_type=NodeType.MATERIAL)
        w1 = GraphNode(node_id="WP_RIFLE", node_type=NodeType.ASSET)
        w2 = GraphNode(node_id="WP_PISTOL", node_type=NodeType.ASSET)

        self.api.add_node(mat)
        self.api.add_node(w1)
        self.api.add_node(w2)

        self.api.add_edge(GraphEdge("E1", "WP_RIFLE", "MAT_SHARED_TITANIUM", RelationshipType.USES))
        self.api.add_edge(GraphEdge("E2", "WP_PISTOL", "MAT_SHARED_TITANIUM", RelationshipType.USES))

        report = self.api.analyze_impact("MAT_SHARED_TITANIUM")
        self.assertEqual(len(report.affected_assets), 2)
        self.assertIn("WP_RIFLE", report.affected_assets)
        self.assertIn("WP_PISTOL", report.affected_assets)

    def test_23_query_nodes_by_type(self):
        for i in range(3):
            self.api.add_node(GraphNode(node_id=f"RULE_{i}", node_type=NodeType.RULE))
        rules = self.api.query_nodes(NodeType.RULE)
        self.assertEqual(len(rules), 3)

    def test_24_f72_governance_node_deletion_permission(self):
        self.api.add_node(GraphNode(node_id="DEL_TEST", node_type=NodeType.OPERATION))
        # Strategy agent lacks ASSET_DELETE by default
        with self.assertRaises(GraphPermissionDeniedError):
            self.api.governance.validate_node_deletion("agent.strategy")

    def test_25_graph_diff_no_changes(self):
        snap1 = self.api.create_snapshot("SNAP_S1")
        snap2 = self.api.create_snapshot("SNAP_S2")
        diff = self.api.compare_snapshots("SNAP_S1", "SNAP_S2")
        self.assertFalse(diff.has_changes)

    def test_26_orphan_node_detection(self):
        # Add two connected nodes and one isolated node
        self.api.add_node(GraphNode(node_id="CONN_A", node_type=NodeType.ASSET))
        self.api.add_node(GraphNode(node_id="CONN_B", node_type=NodeType.MATERIAL))
        self.api.add_edge(GraphEdge("E_AB", "CONN_A", "CONN_B", RelationshipType.USES))
        
        self.api.add_node(GraphNode(node_id="ISOLATED_NODE", node_type=NodeType.RULE))
        
        rep = self.api.validate_consistency()
        self.assertIn("ISOLATED_NODE", rep.orphan_nodes)

    def test_27_audit_trail_graph_mutations(self):
        node = GraphNode(node_id="AUDIT_NODE", node_type=NodeType.OPERATION)
        self.api.add_node(node, agent_id="agent.strategy")
        # Node integrity verified
        self.assertTrue(node.verify_integrity())

    def test_28_cross_job_recovery_graph_consistency(self):
        # Add job, asset, checkpoint
        self.api.add_node(GraphNode(node_id="JOB_REC", node_type=NodeType.JOB))
        self.api.add_node(GraphNode(node_id="ASSET_REC", node_type=NodeType.ASSET))
        self.api.add_edge(GraphEdge("E_JOB_ASSET", "ASSET_REC", "JOB_REC", RelationshipType.PROCESSED_BY))

        rep = self.api.validate_consistency()
        self.assertTrue(rep.is_valid)

    def test_29_blender_object_parent_child_edge(self):
        rec = GraphNode(node_id="WP_RECEIVER", node_type=NodeType.BLENDER_OBJECT)
        mag = GraphNode(node_id="WP_MAGAZINE", node_type=NodeType.BLENDER_OBJECT)
        self.api.add_node(rec)
        self.api.add_node(mag)
        self.api.add_edge(GraphEdge("E_PARENT", "WP_MAGAZINE", "WP_RECEIVER", RelationshipType.PART_OF))

        deps = self.api.get_dependencies("WP_MAGAZINE")
        self.assertIn("WP_RECEIVER", [d.node_id for d in deps])

    def test_30_requirement_satisfaction_chain(self):
        req = GraphNode(node_id="REQ_AMBER_EMISSIVE", node_type=NodeType.REQUIREMENT)
        mat = GraphNode(node_id="MAT_AMBER", node_type=NodeType.MATERIAL)
        asset = GraphNode(node_id="WP_VANDAL_EMISSIVE", node_type=NodeType.ASSET)

        self.api.add_node(req)
        self.api.add_node(mat)
        self.api.add_node(asset)

        self.api.add_edge(GraphEdge("E1", "REQ_AMBER_EMISSIVE", "WP_VANDAL_EMISSIVE", RelationshipType.SATISFIES))
        self.api.add_edge(GraphEdge("E2", "WP_VANDAL_EMISSIVE", "MAT_AMBER", RelationshipType.USES))

        lineage = self.api.trace_lineage("WP_VANDAL_EMISSIVE")
        self.assertIn("REQ_AMBER_EMISSIVE", lineage["requirements"])
        self.assertIn("MAT_AMBER", lineage["materials"])

    def test_31_find_related_by_relationship_type(self):
        a = GraphNode(node_id="BASE_ASSET", node_type=NodeType.ASSET)
        m1 = GraphNode(node_id="M_A", node_type=NodeType.MATERIAL)
        m2 = GraphNode(node_id="M_B", node_type=NodeType.MATERIAL)
        self.api.add_node(a)
        self.api.add_node(m1)
        self.api.add_node(m2)

        self.api.add_edge(GraphEdge("E_M1", "BASE_ASSET", "M_A", RelationshipType.USES))
        self.api.add_edge(GraphEdge("E_M2", "BASE_ASSET", "M_B", RelationshipType.USES))

        mats = self.api.queries.find_related("BASE_ASSET", RelationshipType.USES)
        self.assertEqual(len(mats), 2)
        mat_ids = [m.node_id for m in mats]
        self.assertIn("M_A", mat_ids)
        self.assertIn("M_B", mat_ids)

    def test_32_minimal_regeneration_on_subcomponent_mutation(self):
        weapon = GraphNode(node_id="WP_SYSTEM", node_type=NodeType.ASSET)
        grip = GraphNode(node_id="COMP_GRIP", node_type=NodeType.ASSET_COMPONENT)
        stock = GraphNode(node_id="COMP_STOCK", node_type=NodeType.ASSET_COMPONENT)

        self.api.add_node(weapon)
        self.api.add_node(grip)
        self.api.add_node(stock)

        self.api.add_edge(GraphEdge("E_W_G", "WP_SYSTEM", "COMP_GRIP", RelationshipType.CONTAINS))
        self.api.add_edge(GraphEdge("E_W_S", "WP_SYSTEM", "COMP_STOCK", RelationshipType.CONTAINS))
        self.api.add_edge(GraphEdge("E_G_W", "COMP_GRIP", "WP_SYSTEM", RelationshipType.PART_OF))

        report = self.api.analyze_impact("COMP_GRIP")
        self.assertIn("WP_SYSTEM", report.affected_assets)

if __name__ == "__main__":
    unittest.main()
