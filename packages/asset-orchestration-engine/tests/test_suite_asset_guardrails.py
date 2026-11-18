import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.asset_guardrails import (
    GuardrailSeverity, SkeletalDiscrepancyType,
    SpatialViolationType, CoplanarConflictType, RemediationStrategy,
    BoneNode, SkeletalHierarchySpec, SkeletalDiscrepancy,
    SkeletalReconciliationResult, EntitySpatialSpec,
    SpatialClearanceViolation, SpatialClearanceResult,
    SurfacePlaneSpec, CoplanarConflict, CoplanarRemediationResult,
    SkeletalHierarchyGuard, SpatialClearanceGuard, CoplanarSurfaceGuard,
    AssetGuardrailsAPI
)

class TestSuiteAssetGuardrails(unittest.TestCase):
    """
    Exhaustive test suite for agnostic asset guardrails in Asset Orchestrator Engine.
    Validates skeletal reconciliation, ground datum / entity clearance, and coplanar anti-Z-fighting.
    """

    def setUp(self):
        self.api = AssetGuardrailsAPI()

    # --------------------------------------------------------------------------
    # 1. Skeletal Hierarchy Guard Tests
    # --------------------------------------------------------------------------

    def test_01_skeletal_complete_match(self):
        skel = SkeletalHierarchySpec(skeleton_id="SK_Humanoid_Skeleton")
        skel.add_bone(BoneNode(name="root"))
        skel.add_bone(BoneNode(name="pelvis", parent="root"))
        skel.add_bone(BoneNode(name="spine", parent="pelvis"))

        mesh = SkeletalHierarchySpec(skeleton_id="SK_Humanoid_Mesh")
        mesh.add_bone(BoneNode(name="root"))
        mesh.add_bone(BoneNode(name="pelvis", parent="root"))
        mesh.add_bone(BoneNode(name="spine", parent="pelvis"))

        res = self.api.reconcile_skeletal_hierarchy(skel, [mesh])
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.discrepancies), 0)
        self.assertFalse(res.auto_save_required)

    def test_02_skeletal_missing_bones_detection_and_reconciliation(self):
        """Replicates exact Detonador case where fang_L and fang_R are missing from master skeleton."""
        skel = SkeletalHierarchySpec(skeleton_id="SK_Detonador_Skeleton")
        skel.add_bone(BoneNode(name="root"))
        skel.add_bone(BoneNode(name="body", parent="root"))
        skel.add_bone(BoneNode(name="leg_FL", parent="body"))

        mesh = SkeletalHierarchySpec(skeleton_id="SK_Detonador")
        mesh.add_bone(BoneNode(name="root"))
        mesh.add_bone(BoneNode(name="body", parent="root"))
        mesh.add_bone(BoneNode(name="leg_FL", parent="body"))
        mesh.add_bone(BoneNode(name="fang_L", parent="body", head=(-0.08, -0.32, 0.38)))
        mesh.add_bone(BoneNode(name="fang_R", parent="body", head=(0.08, -0.32, 0.38)))

        res = self.api.reconcile_skeletal_hierarchy(skel, [mesh])
        self.assertFalse(res.is_valid)
        self.assertEqual(len(res.discrepancies), 2)
        missing_names = [d.bone_name for d in res.discrepancies]
        self.assertIn("fang_L", missing_names)
        self.assertIn("fang_R", missing_names)

        # Verify auto-reconciliation and auto-save requirement
        self.assertTrue(res.auto_save_required)
        self.assertIn("fang_L", res.reconciled_skeleton.bones)
        self.assertIn("fang_R", res.reconciled_skeleton.bones)
        self.assertEqual(res.reconciled_skeleton.bones["fang_L"].parent, "body")
        self.assertEqual(res.reconciled_skeleton.bones["fang_R"].parent, "body")

    def test_03_skeletal_cycle_detection(self):
        skel = SkeletalHierarchySpec(skeleton_id="SK_Corrupt_Skeleton")
        skel.add_bone(BoneNode(name="root", parent="bone_B"))
        skel.add_bone(BoneNode(name="bone_A", parent="root"))
        skel.add_bone(BoneNode(name="bone_B", parent="bone_A"))

        res = self.api.reconcile_skeletal_hierarchy(skel)
        self.assertFalse(res.is_valid)
        cycle_disc = [d for d in res.discrepancies if d.discrepancy_type == SkeletalDiscrepancyType.CYCLIC_HIERARCHY]
        self.assertTrue(len(cycle_disc) > 0)

    def test_04_skeletal_animation_orphan_bones(self):
        skel = SkeletalHierarchySpec(skeleton_id="SK_Robot_Skeleton")
        skel.add_bone(BoneNode(name="root"))
        skel.add_bone(BoneNode(name="torso", parent="root"))

        anim_bones = {"A_Robot_Overload": ["torso", "exhaust_flame_FX"]}
        res = self.api.reconcile_skeletal_hierarchy(skel, anim_bone_sets=anim_bones)

        self.assertFalse(res.is_valid)
        self.assertTrue(res.auto_save_required)
        self.assertIn("exhaust_flame_FX", res.reconciled_skeleton.bones)
        self.assertEqual(res.reconciled_skeleton.bones["exhaust_flame_FX"].parent, "root")

    def test_05_skeletal_parent_mismatch(self):
        skel = SkeletalHierarchySpec(skeleton_id="SK_Test_Skeleton")
        skel.add_bone(BoneNode(name="root"))
        skel.add_bone(BoneNode(name="arm_L", parent="root"))

        mesh = SkeletalHierarchySpec(skeleton_id="SK_Test_Mesh")
        mesh.add_bone(BoneNode(name="root"))
        mesh.add_bone(BoneNode(name="clavicle_L", parent="root"))
        mesh.add_bone(BoneNode(name="arm_L", parent="clavicle_L"))

        res = self.api.reconcile_skeletal_hierarchy(skel, [mesh])
        mismatch = [d for d in res.discrepancies if d.discrepancy_type == SkeletalDiscrepancyType.MISMATCHED_PARENT]
        self.assertEqual(len(mismatch), 1)
        self.assertEqual(mismatch[0].bone_name, "arm_L")

    # --------------------------------------------------------------------------
    # 2. Spatial Clearance & Ground Datum Guard Tests
    # --------------------------------------------------------------------------

    def test_06_spatial_ground_datum_calibration(self):
        """Verifies that an entity whose mesh offset is misaligned with capsule base is auto-calibrated."""
        ent = EntitySpatialSpec(
            entity_id="detonador_01",
            position=(0.0, 0.0, 42.0),
            capsule_radius=36.0,
            capsule_half_height=42.0,
            mesh_bottom_offset_z=-15.0, # Incorrect: does not touch floor!
            is_grounded=True
        )

        res = self.api.enforce_spatial_clearance([ent])
        self.assertFalse(res.is_valid)
        self.assertEqual(len(res.violations), 1)
        self.assertEqual(res.violations[0].violation_type, SpatialViolationType.GROUND_FLOATING)

        # Check auto-calibration
        adj = res.adjusted_entities[0]
        self.assertEqual(adj.mesh_bottom_offset_z, -42.0)

    def test_07_spatial_ground_surface_clamping(self):
        """Verifies entity sunken below ground surface is lifted to contact datum."""
        ent = EntitySpatialSpec(
            entity_id="detonador_sunken",
            position=(100.0, 200.0, 50.0), # Floor is at 100.0, entity is sunk into floor
            capsule_radius=36.0,
            capsule_half_height=42.0,
            mesh_bottom_offset_z=-42.0,
            is_grounded=True
        )

        def ground_sampler(x, y):
            return 100.0 # Floor surface Z = 100.0 cm

        res = self.api.enforce_spatial_clearance([ent], ground_height_sampler=ground_sampler)
        self.assertFalse(res.is_valid)
        # Position Z should be adjusted to ground (100.0) + capsule_half_height (42.0) = 142.0
        self.assertAlmostEqual(res.adjusted_entities[0].position[2], 142.0, places=1)

    def test_08_spatial_entity_overlap_detection(self):
        """Two entities spawned at the exact same location must be flagged."""
        e1 = EntitySpatialSpec(entity_id="mob_1", position=(500.0, 500.0, 96.0), capsule_radius=40.0, capsule_half_height=96.0)
        e2 = EntitySpatialSpec(entity_id="mob_2", position=(500.0, 500.0, 96.0), capsule_radius=40.0, capsule_half_height=96.0)

        res = self.api.enforce_spatial_clearance([e1, e2], clearance_margin=20.0)
        self.assertFalse(res.is_valid)
        overlaps = [v for v in res.violations if v.violation_type == SpatialViolationType.ENTITY_OVERLAP]
        self.assertEqual(len(overlaps), 1)

    def test_09_spatial_repulsion_solver_dispersion(self):
        """Multiple overlapping entities must be pushed apart until mutual exclusion is met."""
        entities = [
            EntitySpatialSpec(entity_id=f"mob_{i}", position=(500.0, 500.0, 96.0), capsule_radius=40.0, capsule_half_height=96.0)
            for i in range(4)
        ]

        res = self.api.enforce_spatial_clearance(entities, clearance_margin=10.0, max_repulsion_iterations=50)
        adj = res.adjusted_entities

        # Verify all pairwise distances are strictly >= R1 + R2
        for i in range(len(adj)):
            for j in range(i + 1, len(adj)):
                dx = adj[j].position[0] - adj[i].position[0]
                dy = adj[j].position[1] - adj[i].position[1]
                dist = (dx * dx + dy * dy) ** 0.5
                min_req = adj[i].capsule_radius + adj[j].capsule_radius
                self.assertGreaterEqual(dist, min_req - 1.0)

    # --------------------------------------------------------------------------
    # 3. Coplanar Surface & Anti-Z-Fighting Guard Tests
    # --------------------------------------------------------------------------

    def test_10_coplanar_same_facing_overlap_detection(self):
        """Two horizontal floor planes at the identical height and normal must be detected."""
        s1 = SurfacePlaneSpec(
            surface_id="floor_tile_A",
            normal=(0.0, 0.0, 1.0),
            distance=100.0,
            vertices=[(0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)]
        )
        s2 = SurfacePlaneSpec(
            surface_id="floor_tile_B",
            normal=(0.0, 0.0, 1.0),
            distance=100.0,
            vertices=[(50, 50, 100), (150, 50, 100), (150, 150, 100), (50, 150, 100)]
        )

        res = self.api.resolve_coplanar_surfaces([s1, s2])
        self.assertFalse(res.is_valid)
        self.assertEqual(len(res.conflicts), 1)
        self.assertEqual(res.conflicts[0].conflict_type, CoplanarConflictType.IDENTICAL_PLANE_OVERLAP)

    def test_11_coplanar_micro_layering_separation(self):
        """Verifies that an overlapping same-facing plane receives a micro-layering offset along normal."""
        s1 = SurfacePlaneSpec(
            surface_id="floor_base",
            normal=(0.0, 0.0, 1.0),
            distance=100.0,
            vertices=[(0, 0, 100), (100, 0, 100), (100, 100, 100), (0, 100, 100)]
        )
        s2 = SurfacePlaneSpec(
            surface_id="puddle_decal",
            normal=(0.0, 0.0, 1.0),
            distance=100.0,
            vertices=[(20, 20, 100), (80, 20, 100), (80, 80, 100), (20, 80, 100)]
        )

        res = self.api.resolve_coplanar_surfaces([s1, s2], micro_offset_step=0.05)
        self.assertEqual(res.micro_offsets_applied, 1)
        adj_s2 = res.adjusted_surfaces[1]
        self.assertAlmostEqual(adj_s2.distance, 100.05, places=3)
        self.assertAlmostEqual(adj_s2.vertices[0][2], 100.05, places=3)

    def test_12_coplanar_back_to_back_face_culling(self):
        """Two abutting modular blocks with opposite normals at the contact plane have internal faces culled."""
        s1 = SurfacePlaneSpec(
            surface_id="block_left_east_face",
            normal=(1.0, 0.0, 0.0),
            distance=100.0, # Plane x = 100
            vertices=[(100, 0, 0), (100, 100, 0), (100, 100, 100), (100, 0, 100)]
        )
        s2 = SurfacePlaneSpec(
            surface_id="block_right_west_face",
            normal=(-1.0, 0.0, 0.0),
            distance=-100.0, # Plane -x = -100 -> x = 100
            vertices=[(100, 0, 0), (100, 100, 0), (100, 100, 100), (100, 0, 100)]
        )

        res = self.api.resolve_coplanar_surfaces([s1, s2], cull_internal_faces=True)
        self.assertFalse(res.is_valid)
        self.assertEqual(res.faces_culled, 2)
        self.assertTrue(res.adjusted_surfaces[0].is_culled)
        self.assertTrue(res.adjusted_surfaces[1].is_culled)

    def test_13_modular_tile_grid_snapping(self):
        positions = [(99.98, 200.02, 0.01), (299.95, -0.05, 99.99)]
        snapped = CoplanarSurfaceGuard.snap_modular_tiles(positions, tile_size=100.0)
        self.assertEqual(snapped, [(100.0, 200.0, 0.0), (300.0, 0.0, 100.0)])

    # --------------------------------------------------------------------------
    # 4. Holistic API and Save Instructions Tests
    # --------------------------------------------------------------------------

    def test_14_api_holistic_audit(self):
        skel = SkeletalHierarchySpec(skeleton_id="MasterSkel")
        skel.add_bone(BoneNode(name="root"))

        entities = [
            EntitySpatialSpec(entity_id="e1", position=(0, 0, 50), capsule_half_height=50, mesh_bottom_offset_z=-50)
        ]

        report = self.api.audit_and_remediate_all(master_skeleton=skel, entities=entities)
        self.assertTrue(report["all_passed"])
        self.assertTrue(report["skeletal"].is_valid)
        self.assertTrue(report["spatial"].is_valid)

    def test_15_engine_save_instructions_generation(self):
        skel = SkeletalHierarchySpec(skeleton_id="SK_Test_Skeleton")
        skel.add_bone(BoneNode(name="root"))
        mesh = SkeletalHierarchySpec(skeleton_id="SK_Test_Mesh")
        mesh.add_bone(BoneNode(name="root"))
        mesh.add_bone(BoneNode(name="fang_L", parent="root"))

        res = self.api.reconcile_skeletal_hierarchy(skel, [mesh])
        instructions = SkeletalHierarchyGuard.generate_engine_save_instructions(res, "/Game/DarX/Characters/SK_Test_Skeleton")

        self.assertTrue(instructions["auto_save_required"])
        self.assertEqual(instructions["mutations_count"], 1)
        self.assertIn("fang_L", instructions["missing_bones_reconciled"])
        self.assertEqual(instructions["skeleton_asset_path"], "/Game/DarX/Characters/SK_Test_Skeleton")

if __name__ == "__main__":
    unittest.main()
