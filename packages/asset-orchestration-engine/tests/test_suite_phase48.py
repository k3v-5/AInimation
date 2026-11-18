import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.production_pipeline_unreal import (
    ProductionPipelineAPI, BlenderExportContract, PivotType,
    SocketDefinition, ChangeClass, QualityGateStatus, AssetLifecycle
)

class TestProductionPipelinePhase48(unittest.TestCase):
    def setUp(self):
        self.api = ProductionPipelineAPI()

    def test_01_mandatory_case_1_medieval_house_pipeline(self):
        """Mandatory Case 1: MedievalHouse_001 produce SM_, MI_, UCX_, LODs, sockets y metadata DataAsset."""
        sockets = [
            SocketDefinition(socket_name="entrance", relative_location=(0.0, 0.0, 0.0), is_critical=True),
            SocketDefinition(socket_name="chimney_smoke", relative_location=(0.0, 2.0, 4.0), is_critical=False)
        ]
        manifest, is_cached = self.api.process_and_export_asset(
            "MedievalHouse_001",
            "1.0.0",
            {"width": 8.0, "wall_height": 3.0, "roof_height": 1.45},
            sockets=sockets
        )
        self.assertEqual(manifest.mesh_name, "SM_MedievalHouse_001")
        self.assertEqual(manifest.collision_name, "UCX_MedievalHouse_001")
        self.assertEqual(manifest.material_instances, ["MI_MedievalHouse_001"])
        self.assertEqual(manifest.lod_count, 4)
        self.assertEqual(len(manifest.sockets), 2)
        self.assertEqual(manifest.metadata["data_asset"], "DA_MedievalHouse_001")
        self.assertFalse(is_cached)

    def test_02_mandatory_case_2_geometry_changed_isolation(self):
        """Mandatory Case 2: Modificar roof_height altera el fingerprint geométrico pero mantiene nombres de materiales."""
        manifest1, _ = self.api.process_and_export_asset("HOUSE_G1", "1.0.0", {"roof_height": 1.40})
        manifest2, _ = self.api.process_and_export_asset("HOUSE_G1", "1.0.1", {"roof_height": 1.60})
        self.assertNotEqual(manifest1.pipeline_fingerprint, manifest2.pipeline_fingerprint)
        self.assertEqual(manifest1.material_instances, manifest2.material_instances)

    def test_03_mandatory_case_3_material_change_isolation(self):
        """Mandatory Case 3: Modificar solo color de material no altera la malla base."""
        manifest1, _ = self.api.process_and_export_asset("HOUSE_M1", "1.0.0", {"wall_color": "GREY"})
        manifest2, _ = self.api.process_and_export_asset("HOUSE_M1", "1.0.1", {"wall_color": "RED"})
        self.assertEqual(manifest1.mesh_name, manifest2.mesh_name)
        self.assertEqual(manifest1.collision_name, manifest2.collision_name)

    def test_04_mandatory_case_4_socket_removal_breaking_change(self):
        """Mandatory Case 4: Eliminar socket crítico 'entrance' genera cambio BREAKING."""
        prev = [SocketDefinition(socket_name="entrance", is_critical=True)]
        new_sock = [SocketDefinition(socket_name="chimney_smoke", is_critical=False)]
        change_class, missing = self.api.evaluate_socket_compatibility(prev, new_sock)
        self.assertEqual(change_class, ChangeClass.BREAKING)
        self.assertIn("entrance", missing)

    def test_05_mandatory_case_5_manual_modification_protection(self):
        """Mandatory Case 5: Modificación manual en Unreal bloquea sobreescritura ciega (MANUAL_MODIFICATION_PROTECTED)."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_MANUAL", "1.0.0", {"width": 8.0})
        self.api.stage_asset_in_unreal(manifest)
        self.api.publish_asset_to_unreal("HOUSE_MANUAL")
        
        # Artista modifica manualmente en Unreal
        self.api.mark_manual_modified_in_unreal("HOUSE_MANUAL")

        with self.assertRaises(PermissionError) as ctx:
            self.api.publish_asset_to_unreal("HOUSE_MANUAL")
        self.assertIn("MANUAL_MODIFICATION_PROTECTED", str(ctx.exception))

    def test_06_mandatory_case_6_publish_failure_rollback(self):
        """Mandatory Case 6: Fallo en publicación ejecuta rollback a versión previa."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_ROLLBACK", "1.0.0", {"width": 8.0})
        self.api.stage_asset_in_unreal(manifest)
        pub_rec = self.api.publish_asset_to_unreal("HOUSE_ROLLBACK", simulate_failure=True)
        self.assertEqual(pub_rec.status, "ROLLED_BACK")

    def test_07_mandatory_case_7_cache_reuse_identical_fingerprint(self):
        """Mandatory Case 7: Mismo asset con mismos parámetros produce CACHE HIT."""
        params = {"width": 8.0, "wall_height": 3.0}
        _, is_cached1 = self.api.process_and_export_asset("HOUSE_CACHE", "1.0.0", params)
        _, is_cached2 = self.api.process_and_export_asset("HOUSE_CACHE", "1.0.0", params)
        self.assertFalse(is_cached1)
        self.assertTrue(is_cached2)

    def test_08_naming_policy_prefixes(self):
        """Test 8: Prefijos deterministas de Unreal."""
        from src.production_pipeline_unreal.contracts.naming_path_policy import NamingPathPolicy
        self.assertEqual(NamingPathPolicy.get_mesh_name("Prop"), "SM_Prop")
        self.assertEqual(NamingPathPolicy.get_material_instance_name("Prop"), "MI_Prop")
        self.assertEqual(NamingPathPolicy.get_collision_name("Prop"), "UCX_Prop")
        self.assertEqual(NamingPathPolicy.get_data_asset_name("Prop"), "DA_Prop")

    def test_09_staging_path_isolation(self):
        """Test 9: Aislamiento en carpeta /Game/_Staging/."""
        from src.production_pipeline_unreal.contracts.naming_path_policy import NamingPathPolicy
        self.assertEqual(NamingPathPolicy.get_staging_path("Tower"), "/Game/_Staging/Tower/")

    def test_10_published_path_formatting(self):
        """Test 10: Formato de carpeta publicada /Game/Published/Environment/."""
        from src.production_pipeline_unreal.contracts.naming_path_policy import NamingPathPolicy
        self.assertEqual(NamingPathPolicy.get_published_path("Environment", "Tower"), "/Game/Published/Environment/Tower/")

    def test_11_centimeters_unit_policy(self):
        """Test 11: Política de unidades en centímetros."""
        contract = BlenderExportContract(units="CENTIMETERS")
        self.assertEqual(contract.units, "CENTIMETERS")

    def test_12_base_pivot_policy(self):
        """Test 12: Política de pivote en BASE."""
        contract = BlenderExportContract(pivot_type=PivotType.BASE)
        self.assertEqual(contract.pivot_type, PivotType.BASE)

    def test_13_manifold_geometry_validation(self):
        """Test 13: Validación de geometría manifold."""
        contract = BlenderExportContract(validate_manifold=True)
        self.assertTrue(contract.validate_manifold)

    def test_14_lod_chain_verification(self):
        """Test 14: Verificación de cadena de 4 LODs."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_LOD", "1.0.0", {"width": 8.0})
        self.assertEqual(manifest.lod_count, 4)

    def test_15_collision_contract_convex(self):
        """Test 15: Contrato de colisión UCX convexo."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_COL", "1.0.0", {"width": 8.0})
        self.assertTrue(manifest.collision_name.startswith("UCX_"))

    def test_16_content_hash_reproducibility(self):
        """Test 16: Reproducibilidad determinista del content_hash."""
        m1, _ = self.api.process_and_export_asset("HOUSE_H1", "1.0.0", {"width": 8.0})
        m2, _ = self.api.process_and_export_asset("HOUSE_H1", "1.0.0", {"width": 8.0})
        self.assertEqual(m1.content_hash, m2.content_hash)

    def test_17_pipeline_fingerprint_calculation(self):
        """Test 17: Cálculo del pipeline fingerprint."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_FP", "1.0.0", {"width": 8.0})
        self.assertGreater(len(manifest.pipeline_fingerprint), 8)

    def test_18_quality_gate_pass(self):
        """Test 18: Quality Gate aprueba asset conforme a contrato."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_QG_PASS", "1.0.0", {"width": 8.0})
        qg = self.api.validate_quality_gate(manifest)
        self.assertEqual(qg.status, QualityGateStatus.PASS)
        self.assertEqual(len(qg.errors), 0)

    def test_19_quality_gate_fail_invalid_units(self):
        """Test 19: Quality Gate rechaza asset con unidades no métricas."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_QG_FAIL", "1.0.0", {"width": 8.0})
        bad_contract = BlenderExportContract(units="INCHES")
        qg = self.api.validate_quality_gate(manifest, bad_contract)
        self.assertEqual(qg.status, QualityGateStatus.FAIL)
        self.assertIn("units_centimeters", qg.errors)

    def test_20_end_to_end_blender_to_unreal_publication(self):
        """Test 20: Flujo E2E: Blender Export -> Staging -> Quality Gate -> Unreal Publish."""
        manifest, _ = self.api.process_and_export_asset("HOUSE_E2E", "1.0.0", {"width": 8.0})
        
        # 1. Staging
        staged = self.api.stage_asset_in_unreal(manifest)
        self.assertEqual(staged.status, AssetLifecycle.STAGING)
        self.assertIn("/Game/_Staging/", staged.unreal_path)

        # 2. Quality Gate
        qg = self.api.validate_quality_gate(manifest)
        self.assertEqual(qg.status, QualityGateStatus.PASS)

        # 3. Publish
        pub = self.api.publish_asset_to_unreal("HOUSE_E2E", category="Environment/Houses")
        self.assertEqual(pub.status, "COMMITTED")
        self.assertIn("/Game/Published/Environment/Houses/", pub.target_path)

if __name__ == "__main__":
    unittest.main()
