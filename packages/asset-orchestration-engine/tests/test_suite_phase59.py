import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import VisualSpecificationAPI, VisualCompilationInput
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI
from src.material_surface_generation import (
    MaterialSurfaceAPI, SurfaceTypeTag, InvalidationState,
    ColorSpaceType, BakeChannelType
)

class TestMaterialSurfaceGenerationPhase59(unittest.TestCase):
    def setUp(self):
        self.vas_api = VisualSpecificationAPI()
        self.msp_api = ProceduralModelingStrategyAPI()
        self.geom_api = GeometryGenerationAPI()
        self.surf_api = MaterialSurfaceAPI()

    def _get_barrel_geometry(self):
        vas_in = VisualCompilationInput(
            prompt="Barril medieval de roble con aros de hierro",
            asset_class_hint="PROP.BARREL",
            semantic_context={"semantic_id": "barrel_01.root", "asset_id": "barrel_01"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        return self.geom_api.generate_geometry(msp)

    def _get_sword_geometry(self):
        vas_in = VisualCompilationInput(
            prompt="Espada de acero templado con empuñadura de metal",
            asset_class_hint="WEAPON.SWORD",
            semantic_context={"semantic_id": "sword_01.root", "asset_id": "sword_01"}
        )
        vas = self.vas_api.compile_specification(vas_in)
        msp = self.msp_api.plan_strategy(vas)
        return self.geom_api.generate_geometry(msp)

    def test_01_case_a_metal_surface(self):
        """Case A: Superficie de metal genera material metálico, UV y variación."""
        geom = self._get_sword_geometry()
        surf = self.surf_api.generate_surface(geom)
        metal_mats = [m for m in surf.material_definitions.values() if m.material_class == SurfaceTypeTag.METAL]
        self.assertGreater(len(metal_mats), 0)
        self.assertGreaterEqual(metal_mats[0].metallic, 0.8)
        self.assertGreater(len(surf.uv_layouts), 0)

    def test_02_case_b_painted_hard_surface_wear_mask(self):
        """Case B: Hard surface con pintura y máscara de desgaste."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        self.assertIn("WEAR", [a.attribute_name for a in surf.vertex_attributes])
        self.assertIn("curvature", surf.masks)

    def test_03_case_c_wood_surface_pbr(self):
        """Case C: Superficie de madera con rugosidad no metálica."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        wood_mats = [m for m in surf.material_definitions.values() if m.material_class == SurfaceTypeTag.WOOD]
        self.assertGreater(len(wood_mats), 0)
        self.assertEqual(wood_mats[0].metallic, 0.0)
        self.assertGreater(wood_mats[0].roughness, 0.5)

    def test_04_case_d_material_reuse(self):
        """Case D: Reutilización de material compatible en la librería."""
        m1 = self.surf_api.generate_material({"material_class": SurfaceTypeTag.WOOD})
        m2 = self.surf_api.generate_material({"material_class": SurfaceTypeTag.WOOD})
        self.assertEqual(m1.material_id, m2.material_id)

    def test_05_case_e_material_variant_creation(self):
        """Case E: Creación de variante paramétrica compartiendo clase base."""
        m_base = self.surf_api.generate_material({"material_class": SurfaceTypeTag.METAL})
        m_var = self.surf_api.generate_material({
            "material_class": SurfaceTypeTag.METAL,
            "parameters": {"roughness": 0.12, "metallic": 0.99}
        })
        self.assertTrue(m_var.is_instance)
        self.assertEqual(m_var.parent_material_id, m_base.material_id)

    def test_06_case_f_uv_generation_no_overlaps(self):
        """Case F: Generación de UV layouts con cero overlaps."""
        geom = self._get_barrel_geometry()
        uvs, _ = self.surf_api.generate_uv(geom)
        self.assertGreater(len(uvs), 0)
        self.assertEqual(uvs[0].overlap_count, 0)
        self.assertEqual(uvs[0].out_of_bounds_count, 0)

    def test_07_case_g_texel_density_calculation(self):
        """Case G: Cálculo de texel density dentro de límites de tolerancia."""
        geom = self._get_barrel_geometry()
        _, td_rep = self.surf_api.generate_uv(geom)
        self.assertTrue(td_rep.is_compliant)
        self.assertGreater(td_rep.current_texel_density, 0.0)

    def test_08_case_h_partial_regeneration_preserves_geometry(self):
        """Case H: Regeneración de material no modifica el estado geométrico."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        regen_surf = self.surf_api.regenerate_surface(["M_Wood_Oak"], {"geometry": geom})
        self.assertEqual(regen_surf.geometry_generation_id, geom.generation_id)

    def test_09_case_i_dependency_invalidation(self):
        """Case I: InvalidationTracker marca UVs y bakes como STALE ante cambio geométrico."""
        from src.material_surface_generation.engine.surface_invalidation_tracker import SurfaceInvalidationTracker
        inv_map = SurfaceInvalidationTracker.handle_geometry_change({})
        self.assertEqual(inv_map["uv_layouts"], InvalidationState.STALE)
        self.assertEqual(inv_map["materials"], InvalidationState.VALID)

    def test_10_case_j_deterministic_surface_hash(self):
        """Case J: Dos ejecuciones idénticas producen el mismo surface_hash."""
        geom = self._get_barrel_geometry()
        surf1 = self.surf_api.generate_surface(geom, generation_seed=42)
        surf2 = self.surf_api.generate_surface(geom, generation_seed=42)
        self.assertEqual(surf1.surface_hash, surf2.surface_hash)

    def test_11_pbr_parameter_ranges(self):
        """Test 11: Parámetros PBR dentro de rangos válidos [0.0, 1.0]."""
        mat = self.surf_api.generate_material({"material_class": SurfaceTypeTag.PLASTIC})
        self.assertGreaterEqual(mat.roughness, 0.0)
        self.assertLessEqual(mat.roughness, 1.0)
        self.assertGreaterEqual(mat.metallic, 0.0)
        self.assertLessEqual(mat.metallic, 1.0)

    def test_12_shader_graph_abstraction(self):
        """Test 12: Generación de grafo de shader abstracto."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        self.assertGreater(len(surf.shader_graphs), 0)
        first_graph = list(surf.shader_graphs.values())[0]
        node_types = [n.node_type for n in first_graph.nodes]
        self.assertIn("ShaderNodeBsdfPrincipled", node_types)
        self.assertIn("ShaderNodeOutputMaterial", node_types)

    def test_13_vertex_color_attributes(self):
        """Test 13: Definición de atributos de vértices (AO, WEAR, DAMAGE)."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        att_names = {a.attribute_name for a in surf.vertex_attributes}
        self.assertIn("AO", att_names)
        self.assertIn("WEAR", att_names)

    def test_14_bake_plan_orm_channels(self):
        """Test 14: Bake plan con empaquetado ORM (R=AO, G=Roughness, B=Metallic)."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        bake = self.surf_api.generate_bake_plan(surf)
        self.assertIn(BakeChannelType.ORM, bake.maps_to_bake)
        self.assertEqual(bake.orm_channels["R"], "AO")
        self.assertEqual(bake.orm_channels["G"], "Roughness")
        self.assertEqual(bake.orm_channels["B"], "Metallic")

    def test_15_color_space_management(self):
        """Test 15: Asignación correcta de ColorSpace (sRGB vs Non-Color)."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        tex_by_channel = {t.channel: t for t in surf.texture_requirements}
        self.assertEqual(tex_by_channel["BaseColor"].color_space, ColorSpaceType.SRGB)
        self.assertEqual(tex_by_channel["Normal"].color_space, ColorSpaceType.NON_COLOR)
        self.assertEqual(tex_by_channel["ORM"].color_space, ColorSpaceType.NON_COLOR)

    def test_16_unreal_material_interface(self):
        """Test 16: Interfaz para Unreal Engine con Master Material y parámetros."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        self.assertGreater(len(surf.unreal_material_interface), 0)
        first_unreal = list(surf.unreal_material_interface.values())[0]
        self.assertTrue(first_unreal.nanite_compatible)
        self.assertEqual(first_unreal.blend_mode, "BLEND_Opaque")

    def test_17_surface_validation_clean_result(self):
        """Test 17: Validación de resultado limpio retorna is_valid = True."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        val = self.surf_api.validate_surface(surf)
        self.assertTrue(val.is_valid)

    def test_18_surface_regions_count(self):
        """Test 18: Creación de regiones de superficie para cada objeto geométrico."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        self.assertEqual(len(surf.surface_regions), len(geom.geometry_objects))

    def test_19_procedural_variation_parameters(self):
        """Test 19: Parámetros de variación procedural registrados."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom, generation_seed=99)
        self.assertEqual(surf.variation_parameters["seed"], 99)

    def test_20_end_to_end_material_surface_pipeline(self):
        """Test 20: Flujo E2E Completo: Prompt -> F56 -> F57 -> F58 -> F59 -> Listo para F60."""
        geom = self._get_barrel_geometry()
        surf = self.surf_api.generate_surface(geom)
        val = self.surf_api.validate_surface(surf)
        self.assertTrue(val.is_valid)
        self.assertGreater(len(surf.material_definitions), 0)
        self.assertGreater(len(surf.uv_layouts), 0)
        self.assertIsNotNone(surf.baking_plan)

if __name__ == "__main__":
    unittest.main()
