import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.anime_character_pipeline import (
    AnimeCharacterAPI,
    AnimeProportionsPreset,
    AnimeEyeStyle,
    AnimeHairStyle,
    NPROutlineMode,
    AnimeShadingModel,
    AnimeCharacterSpec,
    AnimeHeadTopologySpec,
    AnimeBodyTopologySpec,
    NPROutlineSpec
)
from src.anime_character_pipeline.generators.organic_body_generator import OrganicBodyGenerator
from src.anime_character_pipeline.generators.bezier_hair_generator import BezierHairGenerator
from src.anime_character_pipeline.generators.inverted_hull_outlines import InvertedHullOutlines
from src.anime_character_pipeline.generators.npr_shading_generator import NPRShadingGenerator
from src.anime_character_pipeline.generators.tactical_props_generator import TacticalPropsGenerator


class TestAnimeCharacterPipeline(unittest.TestCase):
    """Test cases for the anime character pipeline components."""

    def setUp(self):
        self.api = AnimeCharacterAPI()
        self.default_spec = AnimeCharacterSpec(
            character_id="CH_Anime_Kira_Test",
            character_name="Kira"
        )

    def test_anime_api_initialization(self):
        """Validates API facade instantiates properly."""
        self.assertIsNotNone(self.api)

    def test_anime_spec_validation_valid(self):
        """Valid spec produces 0 validation issues."""
        issues = self.api.validate_spec(self.default_spec)
        self.assertEqual(len(issues), 0)

    def test_anime_spec_validation_invalid_height(self):
        """Invalid height (< 0.5m or > 2.5m) is detected."""
        spec_too_short = AnimeCharacterSpec(
            character_id="CH_Short",
            character_name="Short",
            body_spec=AnimeBodyTopologySpec(total_height=0.3)
        )
        issues = self.api.validate_spec(spec_too_short)
        self.assertTrue(any("height" in i.lower() for i in issues))

    def test_anime_spec_validation_invalid_chin(self):
        """Chin sharpness out of range is detected."""
        spec_invalid_chin = AnimeCharacterSpec(
            character_id="CH_Chin",
            character_name="Chin",
            head_spec=AnimeHeadTopologySpec(chin_sharpness=1.8)
        )
        issues = self.api.validate_spec(spec_invalid_chin)
        self.assertTrue(any("chin" in i.lower() for i in issues))

    def test_anime_spec_validation_invalid_outline(self):
        """Outline thickness out of range is detected."""
        spec_invalid_outline = AnimeCharacterSpec(
            character_id="CH_Outline",
            character_name="Outline",
            outline_spec=NPROutlineSpec(thickness=0.08)  # 8cm is huge
        )
        issues = self.api.validate_spec(spec_invalid_outline)
        self.assertTrue(any("thickness" in i.lower() for i in issues))

    def test_organic_head_profile_rings(self):
        """Head profile rings converge into a sharp V-chin."""
        gen = OrganicBodyGenerator(self.default_spec.head_spec, self.default_spec.body_spec)
        rings = gen.compute_head_profile_rings()
        self.assertGreaterEqual(len(rings), 6)
        # Crown ring should be wider than chin ring
        crown_rx = rings[0]["radius_x"]
        chin_rx = rings[-1]["radius_x"]
        self.assertGreater(crown_rx, chin_rx)

    def test_organic_torso_profile_rings(self):
        """Torso rings model narrow anime waist and hips continuously."""
        gen = OrganicBodyGenerator(self.default_spec.head_spec, self.default_spec.body_spec)
        rings = gen.compute_torso_profile_rings()
        self.assertGreaterEqual(len(rings), 6)
        # Verify waist (around index 4) is narrower than chest and hips
        waist_rx = rings[4]["radius_x"]
        chest_rx = rings[2]["radius_x"]
        hips_rx = rings[-1]["radius_x"]
        self.assertLess(waist_rx, chest_rx)
        self.assertLess(waist_rx, hips_rx)

    def test_bezier_hair_strand_generation(self):
        """Bezier hair generator outputs bangs, sideburns, and ponytail with taper."""
        hair_gen = BezierHairGenerator("high_ponytail_layered")
        strands = hair_gen.generate_hair_strands()
        self.assertGreater(len(strands), 5)
        categories = {s.category for s in strands}
        self.assertIn("bangs", categories)
        self.assertIn("sideburns", categories)
        self.assertIn("ponytail", categories)
        # Ensure all strands taper to sharp tips
        for s in strands:
            self.assertLess(s.bevel_radius_tip, s.bevel_radius_root)
            self.assertGreaterEqual(len(s.control_points), 3)

    def test_inverted_hull_modifier_parameters(self):
        """Inverted hull modifier configures Solidify with flipped normals."""
        outline_gen = InvertedHullOutlines(NPROutlineSpec(thickness=0.0035))
        params = outline_gen.compute_modifier_parameters()
        self.assertEqual(params["type"], "SOLIDIFY")
        self.assertTrue(params["use_flip_normals"])
        self.assertEqual(params["offset"], 1.0)
        self.assertEqual(params["thickness"], 0.0035)

    def test_npr_shading_generation(self):
        """NPR shading code generation contains outline emission and cel-shading ramps."""
        shading_gen = NPRShadingGenerator(AnimeShadingModel.TWO_TONE_BANDED)
        code = shading_gen.get_blender_material_definitions_code()
        self.assertIn("M_Anime_NPR_Outline", code)
        self.assertIn("use_backface_culling", code)
        self.assertIn("ShaderNodeShaderToRGB", code)
        self.assertIn("CONSTANT", code)

    def test_tactical_props_generation(self):
        """Tactical props generator includes Katana Saya, Tsuka and Cyber Scarf."""
        props_gen = TacticalPropsGenerator(include_katana=True, include_scarf=True)
        code = props_gen.get_blender_props_code()
        self.assertIn("CH_Kira_Scarf", code)
        self.assertIn("WP_Katana_Saya", code)
        self.assertIn("WP_Katana_Tsuka", code)

    def test_anime_build_plan(self):
        """Build plan orchestration returns structured execution blueprint."""
        plan = self.api.build_character_plan(self.default_spec)
        self.assertEqual(plan["character_id"], "CH_Anime_Kira_Test")
        self.assertTrue(plan["outline_enabled"])
        self.assertGreater(plan["hair_strands_count"], 0)
        self.assertEqual(plan["status"], "READY_FOR_BLENDER_ORCHESTRATION")


if __name__ == '__main__':
    unittest.main()
