import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI
from src.material_surface_generation import MaterialSurfaceAPI
from src.presentation_matching import (
    PresentationMatchingAPI, ProjectionType, BackgroundType,
    ViewTransformType, PresentationViewAngle
)

class TestPresentationMatchingPhase60(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()
        self.pres_api = PresentationMatchingAPI()

    def _get_barrel_pipeline(self):
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble con aros de hierro, 1.2m",
            asset_class_hint="PROP.BARREL",
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        geom = self.geom_api.generate_geometry(msp)
        surf = self.surf_api.generate_surface(geom)
        return vas, msp, geom, surf

    def test_01_case_a_product_asset_presentation(self):
        """Case A: Asset de producto genera presentación de 3/4 reproducible con key light y sombras."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc.view_angle, PresentationViewAngle.THREE_QUARTER)
        self.assertEqual(vpc.camera.projection, ProjectionType.PERSPECTIVE)
        self.assertTrue(vpc.lighting.key_light.cast_shadow)
        self.assertGreater(vpc.lighting.key_light.intensity, 0.0)

    def test_02_case_b_orthographic_camera_solving(self):
        """Case B: Detección y resolución de vista ortográfica con orthographic_scale."""
        bounds = {"dimensions": {"x": 1.0, "y": 1.0, "z": 1.2}, "min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.2)}
        cam = self.pres_api.solve_camera(bounds, projection=ProjectionType.ORTHOGRAPHIC)
        self.assertEqual(cam.projection, ProjectionType.ORTHOGRAPHIC)
        self.assertGreater(cam.orthographic_scale, 0.0)

    def test_03_case_c_perspective_camera_occupancy(self):
        """Case C: Resolución de cámara perspectiva con focal de 50mm y encuadre ~78%."""
        bounds = {"dimensions": {"x": 1.0, "y": 1.0, "z": 1.2}, "min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 1.2)}
        cam = self.pres_api.solve_camera(bounds, projection=ProjectionType.PERSPECTIVE)
        self.assertEqual(cam.focal_length, 50.0)
        self.assertGreater(cam.distance, 1.5)

    def test_04_case_d_complex_3point_lighting(self):
        """Case D: Rig de iluminación de 3 puntos (Key, Fill, Rim)."""
        lighting = self.pres_api.build_lighting(distance=3.0)
        self.assertIsNotNone(lighting.key_light)
        self.assertIsNotNone(lighting.fill_light)
        self.assertIsNotNone(lighting.rim_light)
        self.assertGreater(lighting.key_light.intensity, lighting.fill_light.intensity)

    def test_05_case_e_background_configuration(self):
        """Case E: Configuración de fondo neutro sólido."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc.background.background_type, BackgroundType.SOLID)
        self.assertEqual(len(vpc.background.color), 4)

    def test_06_case_f_aspect_ratio_safe_framing(self):
        """Case F: Encuadre seguro sin deformación para 16:9."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc.render_settings.aspect_ratio, 1.7778)
        self.assertGreater(vpc.framing.horizontal_margin, 0.0)
        self.assertGreater(vpc.framing.vertical_margin, 0.0)

    def test_07_case_g_partial_regeneration_preserves_geometry(self):
        """Case G: Regeneración de presentación no altera geometría ni materiales."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        regen_vpc = self.pres_api.regenerate_presentation(["exposure"], {"geometry": geom, "surface": surf})
        self.assertEqual(regen_vpc.geometry_generation_id, geom.generation_id)
        self.assertEqual(regen_vpc.surface_generation_id, surf.surface_generation_id)

    def test_08_case_h_deterministic_presentation_hash(self):
        """Case H: Misma entrada genera idéntico presentation_hash (SHA-256)."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc1 = self.pres_api.build_presentation_context(geom, surf)
        vpc2 = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc1.presentation_hash, vpc2.presentation_hash)

    def test_09_case_i_fallback_uncertainty_tracking(self):
        """Case I: Ausencia de referencia visual utiliza preset seguro con nivel KNOWN."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf, reference_analysis=None)
        self.assertEqual(vpc.camera.inference_level.value, "KNOWN")

    def test_10_case_j_out_of_frame_prevention(self):
        """Case J: Solver ajusta distancia para evitar recortes en objetos grandes."""
        big_bounds = {"dimensions": {"x": 5.0, "y": 5.0, "z": 8.0}, "min": (-2.5, -2.5, 0.0), "max": (2.5, 2.5, 8.0)}
        cam = self.pres_api.solve_camera(big_bounds)
        self.assertGreater(cam.distance, 8.0)

    def test_11_framing_safe_padding(self):
        """Test 11: Margen de seguridad safe frame padding >= 0.05."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertGreaterEqual(vpc.framing.safe_frame_padding, 0.05)

    def test_12_ground_plane_configuration(self):
        """Test 12: Plano de suelo activado con color y rugosidad definidos."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertTrue(vpc.lighting.ground_plane_enabled)
        self.assertGreaterEqual(vpc.lighting.ground_roughness, 0.5)

    def test_13_color_management_filmic(self):
        """Test 13: Gestión de color con View Transform Filmic y exposición 0.0."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc.color_management.view_transform, ViewTransformType.FILMIC)
        self.assertEqual(vpc.color_management.exposure, 0.0)

    def test_14_render_settings_samples(self):
        """Test 14: Configuración de render a 1920x1080 con 128 samples y sombras activadas."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertEqual(vpc.render_settings.resolution_x, 1920)
        self.assertEqual(vpc.render_settings.resolution_y, 1080)
        self.assertTrue(vpc.render_settings.enable_shadows)

    def test_15_presentation_quality_metrics_score(self):
        """Test 15: Métricas de calidad de presentación generan score global >= 0.90."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertGreaterEqual(vpc.quality_metrics.overall_presentation_score, 0.90)

    def test_16_target_position_centered(self):
        """Test 16: Cámara apunta al centro de la altura del sujeto."""
        bounds = {"dimensions": {"x": 1.0, "y": 1.0, "z": 2.0}, "min": (-0.5, -0.5, 0.0), "max": (0.5, 0.5, 2.0)}
        cam = self.pres_api.solve_camera(bounds)
        self.assertEqual(cam.target_position[2], 1.0)

    def test_17_validation_clean_vpc(self):
        """Test 17: Validación de presentación limpia retorna is_valid = True."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        val = self.pres_api.validate_presentation(vpc)
        self.assertTrue(val.is_valid)

    def test_18_environment_intensity(self):
        """Test 18: Luz ambiental de entorno configurada y positiva."""
        _, _, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf)
        self.assertGreater(vpc.lighting.environment_intensity, 0.0)

    def test_19_invalidation_tracker_camera(self):
        """Test 19: InvalidationTracker marca presentation_render como STALE ante cambio de cámara."""
        from src.presentation_matching.engine.presentation_invalidation_tracker import PresentationInvalidationTracker
        inv = PresentationInvalidationTracker.handle_camera_change({})
        self.assertEqual(inv["geometry"], "VALID")
        self.assertEqual(inv["presentation_render"], "STALE")

    def test_20_end_to_end_presentation_matching_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> F60 -> Contrato listo para F61."""
        vas, msp, geom, surf = self._get_barrel_pipeline()
        vpc = self.pres_api.build_presentation_context(geom, surf, specification=vas)
        val = self.pres_api.validate_presentation(vpc)
        self.assertTrue(val.is_valid)
        self.assertEqual(vpc.semantic_id, "barrel_01.root")
        self.assertEqual(vpc.geometry_generation_id, geom.generation_id)
        self.assertEqual(vpc.surface_generation_id, surf.surface_generation_id)
        self.assertGreater(len(vpc.presentation_hash), 0)

if __name__ == "__main__":
    unittest.main()
