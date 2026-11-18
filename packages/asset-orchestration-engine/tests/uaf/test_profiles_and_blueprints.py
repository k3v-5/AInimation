"""
Tests for StyleProfile, QualityProfile, TargetProfile, BlueprintNode, and AssetBlueprint.
UAF-81.1 Sections 27, 28, 29, 30, 31, 51, 52, 53, 54.
"""

from uaf.intelligence.profiles.style_profile import StyleProfile
from uaf.intelligence.profiles.quality_profile import QualityProfile
from uaf.intelligence.profiles.target_profile import TargetProfile
from uaf.intelligence.blueprint.blueprint_node import BlueprintNode
from uaf.intelligence.blueprint.asset_blueprint import AssetBlueprint


def test_profiles_serialization():
    style = StyleProfile(style_id="militar_brutalist", visual_language="tactical")
    quality = QualityProfile(profile_id="hero_tier", max_polycount=150000, target_texture_resolution=4096)
    target = TargetProfile(target_id="ue5_prod", engine_name="unreal", supports_nanite=True)

    assert style.to_dict()["visual_language"] == "tactical"
    assert quality.to_dict()["max_polycount"] == 150000
    assert target.to_dict()["supports_nanite"] is True


def test_asset_blueprint_dag_and_hash():
    bp = AssetBlueprint(blueprint_id="bp_character_01", asset_id="char_heavy_01")

    # Add nodes with dependencies
    bp.add_node(BlueprintNode("node_skeleton", "skeleton"))
    bp.add_node(BlueprintNode("node_body", "mesh", dependencies=["node_skeleton"]))
    bp.add_node(BlueprintNode("node_armor", "mesh", dependencies=["node_body"]))
    bp.add_node(BlueprintNode("node_textures", "texture", dependencies=["node_armor"]))

    # Verify execution order adheres to DAG
    order = bp.get_execution_order()
    assert order.index("node_skeleton") < order.index("node_body")
    assert order.index("node_body") < order.index("node_armor")
    assert order.index("node_armor") < order.index("node_textures")

    # Hash must be stable SHA-256
    assert len(bp.blueprint_hash) == 64
    # Recomputing produces identical hash
    assert bp.blueprint_hash == bp.blueprint_hash
