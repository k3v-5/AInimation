"""
Tests for Surface Baking and Dirty Dependency Tracking Graph.
UAF-81.4 Sections 28, 30, 31, 79, 94.
"""

from uaf.surface.baking.bake_plan import BakePlan, BakeType, BakeResult
from uaf.surface.baking.bake_engine import BakeEngine
from uaf.surface.graph.dirty_tracker import SurfaceDependencyTracker


def test_bake_engine_execution_and_results():
    plan = BakePlan(
        plan_id="bake_hero_01",
        high_res_mesh_id="mesh_body_high",
        low_res_mesh_id="mesh_body_low",
        bake_types=[BakeType.NORMAL, BakeType.AO, BakeType.CURVATURE],
        resolution=2048,
    )

    result = BakeEngine.execute_bake(plan)
    assert result.is_success is True
    assert len(result.generated_maps) == 3
    assert "NORMAL" in result.generated_maps
    assert "AO" in result.generated_maps
    assert "CURVATURE" in result.generated_maps
    assert "mesh_body_low" in result.generated_maps["NORMAL"]


def test_surface_dependency_tracker_selective_invalidation():
    """
    CRITICAL INVARIANT (Section 94):
    Verify that modifying armor surface does NOT invalidate body geometry,
    and modifying body geometry invalidates only body-derived surface artifacts.
    """
    tracker = SurfaceDependencyTracker()

    # Setup Body dependency chain:
    # geom_body -> bake_body -> mask_body -> tex_body -> MI_body
    tracker.add_dependency("bake_body", "geom_body")
    tracker.add_dependency("mask_body", "bake_body")
    tracker.add_dependency("tex_body", "mask_body")
    tracker.add_dependency("MI_body", "tex_body")

    # Setup Armor dependency chain:
    # geom_armor -> bake_armor -> mask_armor -> tex_armor -> MI_armor
    tracker.add_dependency("bake_armor", "geom_armor")
    tracker.add_dependency("mask_armor", "bake_armor")
    tracker.add_dependency("tex_armor", "mask_armor")
    tracker.add_dependency("MI_armor", "tex_armor")

    # CASE 1: Modify armor material instance only
    # Changing armor material properties should invalidate MI_armor only
    invalidated_armor = tracker.mark_dirty("MI_armor")
    assert "MI_armor" in invalidated_armor
    assert not tracker.is_dirty("geom_body")
    assert not tracker.is_dirty("geom_armor")
    assert not tracker.is_dirty("tex_body")
    assert not tracker.is_dirty("MI_body")

    # Clear state
    tracker.clear_dirty("MI_armor")

    # CASE 2: Modify body geometry
    # Invalidation must cascade to bake_body, mask_body, tex_body, MI_body
    # BUT armor components must remain 100% clean!
    invalidated_body = tracker.mark_dirty("geom_body")
    assert "geom_body" in invalidated_body
    assert "bake_body" in invalidated_body
    assert "mask_body" in invalidated_body
    assert "tex_body" in invalidated_body
    assert "MI_body" in invalidated_body

    # Armor chain MUST NOT be dirty!
    assert not tracker.is_dirty("geom_armor")
    assert not tracker.is_dirty("bake_armor")
    assert not tracker.is_dirty("mask_armor")
    assert not tracker.is_dirty("tex_armor")
    assert not tracker.is_dirty("MI_armor")
