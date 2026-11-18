import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI
from src.material_surface_generation import MaterialSurfaceAPI
from src.presentation_matching import PresentationMatchingAPI
from src.automated_visual_evaluation import AutomatedVisualEvaluationAPI
from src.geometric_validation_qa import (
    GeometricValidationAPI, GeometricDefectCategory, DefectSeverity,
    ValidationStatus, GeometryValidationConfiguration, GeometricDefect,
    CorrectionSafetyLevel
)

class TestGeometricValidationPhase62(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()
        self.eval_api = AutomatedVisualEvaluationAPI()
        self.qa_api = GeometricValidationAPI()

    def _get_pipeline_data(self):
        ref_report = DecomposedReferenceReport(
            report_id="REP_F55_BARREL_01",
            reference_ids=["REF_01"],
            silhouette=SilhouetteExtraction(aspect_ratio=1.0),
            proportions=ProportionEstimate(component_ratios={"body": 0.8, "top_ring": 0.1, "bottom_ring": 0.1}),
            parts=[
                DecomposedPart("part_body", "BODY", (0, 0, 1, 1.0), (0, 0, 0), True, 0.98),
                DecomposedPart("part_ring_top", "RING_01", (0, 0.8, 1.02, 0.15), (0, 0, 0.8), False, 0.95),
                DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
            ],
            materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
        )
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble con aros de hierro",
            asset_class_hint="PROP.BARREL",
            reference_reports=[ref_report],
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"},
            project_constraints={"nanite": True, "collision": "CUSTOM_UCX"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        surf = self.surf_api.generate_surface(geom)
        vpc = self.pres_api.build_presentation_context(geom, surf, ref_report, vas)
        v_eval = self.eval_api.evaluate_visuals(ref_report, geom, {"surface": surf, "presentation": vpc})
        return ref_report, vas, geom, surf, vpc, v_eval

    def test_01_case_a_valid_clean_geometry(self):
        """Case A: Geometría válida y limpia produce status PASS y score >= 0.95."""
        _, _, geom, surf, _, v_eval = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval})
        self.assertEqual(res.validation_status, ValidationStatus.PASS)
        self.assertGreaterEqual(res.quality_scores["overall_geometry_score"], 0.95)
        self.assertEqual(len([d for d in res.defects if d.severity == DefectSeverity.CRITICAL]), 0)

    def test_02_case_b_non_manifold_detection(self):
        """Case B: Detección de geometría non-manifold produce status FAIL y defecto crítico."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.topology_summary.is_manifold = False
        res = self.qa_api.validate_geometry(geom)
        self.assertEqual(res.validation_status, ValidationStatus.FAIL)
        nm_defs = [d for d in res.defects if d.category == GeometricDefectCategory.NON_MANIFOLD]
        self.assertGreater(len(nm_defs), 0)
        self.assertEqual(nm_defs[0].severity, DefectSeverity.CRITICAL)

    def test_03_case_c_degenerate_faces_detection(self):
        """Case C: Detección de caras degeneradas con elementos afectados."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.topology_summary.degenerate_faces = 4
        res = self.qa_api.validate_geometry(geom)
        deg_defs = [d for d in res.defects if d.category == GeometricDefectCategory.DEGENERATE_GEOMETRY]
        self.assertGreater(len(deg_defs), 0)
        self.assertEqual(len(deg_defs[0].affected_elements), 4)

    def test_04_case_d_negative_scale_detection(self):
        """Case D: Detección de escala negativa con defecto SCALE_ERROR."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.geometry_objects[0].scale = (1.0, -1.0, 1.0)
        res = self.qa_api.validate_geometry(geom)
        self.assertEqual(res.validation_status, ValidationStatus.FAIL)
        scale_defs = [d for d in res.defects if d.category == GeometricDefectCategory.SCALE_ERROR]
        self.assertGreater(len(scale_defs), 0)

    def test_05_case_e_unapplied_scale_warning(self):
        """Case E: Escala no aplicada genera TRANSFORM_ERROR."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.geometry_objects[0].scale = (2.0, 2.0, 2.0)
        config = GeometryValidationConfiguration(allow_unapplied_transforms=False)
        res = self.qa_api.validate_geometry(geom, configuration=config)
        tf_defs = [d for d in res.defects if d.category == GeometricDefectCategory.TRANSFORM_ERROR]
        self.assertGreater(len(tf_defs), 0)

    def test_06_case_f_polygon_budget_overrun(self):
        """Case F: Exceso de polígonos detecta DENSITY_ERROR."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.triangle_count = 65000 # Límite es 50000
        res = self.qa_api.validate_geometry(geom)
        dens_defs = [d for d in res.defects if d.category == GeometricDefectCategory.DENSITY_ERROR]
        self.assertGreater(len(dens_defs), 0)
        self.assertEqual(dens_defs[0].severity, DefectSeverity.MAJOR)

    def test_07_case_g_missing_collision_mesh(self):
        """Case G: Ausencia de colisión UCX detecta COLLISION_ERROR."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.collision_geometry = None
        geom.collision_mesh = None
        res = self.qa_api.validate_geometry(geom)
        self.assertFalse(res.unreal_readiness.collision_ready)
        col_defs = [d for d in res.defects if d.category == GeometricDefectCategory.COLLISION_ERROR]
        self.assertGreater(len(col_defs), 0)

    def test_08_case_h_cross_correlation_with_f61(self):
        """Case H: Correlación cruzada entre defectos visuales de F61 y QA geométrico de F62."""
        _, _, geom, _, _, v_eval = self._get_pipeline_data()
        geom.geometry_objects[0].scale = (-1.0, 1.0, 1.0) # Introduce defecto geométrico en objeto
        res = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval})
        self.assertIn("correlations", res.generation_metadata)

    def test_09_case_i_deterministic_validation_hash(self):
        """Case I: Dos ejecuciones idénticas producen el mismo validation_hash (SHA-256)."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res1 = self.qa_api.validate_geometry(geom)
        res2 = self.qa_api.validate_geometry(geom)
        self.assertEqual(res1.validation_hash, res2.validation_hash)

    def test_10_case_j_read_only_mesh_preservation(self):
        """Case J: Modo lectura preserva intactos los vértices y triángulos."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        v_before = geom.vertex_count
        tri_before = geom.triangle_count
        _ = self.qa_api.validate_geometry(geom)
        self.assertEqual(geom.vertex_count, v_before)
        self.assertEqual(geom.triangle_count, tri_before)

    def test_11_mesh_inventory_calculation(self):
        """Test 11: Cálculo completo de inventario (volumen, área, vértices, triángulos)."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        inv = res.mesh_inventory
        self.assertGreater(inv.vertex_count, 0)
        self.assertGreater(inv.triangle_count, 0)
        self.assertGreater(inv.surface_area, 0.0)
        self.assertGreater(inv.volume, 0.0)

    def test_12_topology_statistics_summary(self):
        """Test 12: Resumen de estadísticas topológicas."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        self.assertTrue(res.topology_statistics.is_manifold)
        self.assertEqual(res.topology_statistics.degenerate_face_count, 0)

    def test_13_unreal_readiness_report(self):
        """Test 13: Reporte de preparación para exportación a Unreal Engine."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        self.assertTrue(res.unreal_readiness.geometry_ready)
        self.assertTrue(res.unreal_readiness.collision_ready)
        self.assertTrue(res.unreal_readiness.is_export_ready)

    def test_14_rule_registry_executes_all_rules(self):
        """Test 14: GeometryValidationRegistry evalúa todas las reglas estándar."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        self.assertIn("topology_score", res.quality_scores)
        self.assertIn("transform_score", res.quality_scores)
        self.assertIn("normal_score", res.quality_scores)
        self.assertIn("collision_score", res.quality_scores)

    def test_15_correction_hints_safety_level(self):
        """Test 15: Sugerencias de corrección incluyen nivel de seguridad (SAFE_AUTOMATION)."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        geom.topology_summary.degenerate_faces = 2
        res = self.qa_api.validate_geometry(geom)
        self.assertGreater(len(res.correction_hints), 0)
        self.assertEqual(res.correction_hints[0].safety_level, CorrectionSafetyLevel.SAFE_AUTOMATION)

    def test_16_overall_geometry_score_calculation(self):
        """Test 16: Score global geométrico dentro de [0.0, 1.0]."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        score = res.quality_scores["overall_geometry_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_17_validation_clean_qa_result(self):
        """Test 17: Validación de resultado limpio retorna is_valid = True."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        val = self.qa_api.validate_qa_result(res)
        self.assertTrue(val.is_valid)

    def test_18_execution_trace_records_steps(self):
        """Test 18: Traza de ejecución registra etapas de escaneo y evaluación."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom)
        self.assertGreater(len(res.execution_trace), 0)
        steps = [t["step"] for t in res.execution_trace]
        self.assertIn("SCAN_INVENTORY", steps)
        self.assertIn("EVALUATE_RULES", steps)

    def test_19_component_level_validation_api(self):
        """Test 19: API validate_component valida un componente individual."""
        _, _, geom, _, _, _ = self._get_pipeline_data()
        res = self.qa_api.validate_component("part_body", geom)
        self.assertEqual(res.validation_status, ValidationStatus.PASS)

    def test_20_end_to_end_geometric_qa_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> F61 -> F62 -> Listo para F63."""
        _, _, geom, surf, _, v_eval = self._get_pipeline_data()
        res = self.qa_api.validate_geometry(geom, {"visual_evaluation": v_eval, "surface": surf})
        val = self.qa_api.validate_qa_result(res)
        self.assertTrue(val.is_valid)
        self.assertEqual(res.semantic_id, "barrel_01.root")
        self.assertGreater(len(res.validation_hash), 0)
        self.assertTrue(res.unreal_readiness.is_export_ready)

if __name__ == "__main__":
    unittest.main()
