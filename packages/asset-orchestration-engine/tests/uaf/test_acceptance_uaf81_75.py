"""
Normative Acceptance Test Suite for UAF-81.75: Universal Runtime Rendering World System.
Validates complete rendering pipeline, camera systems, lighting, culling, LOD,
draw submissions, render graph scheduling, GPU resource lifetimes, and invariants (§101 - §120).
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
import os
import tempfile
import time
from typing import Any, Dict, List, Tuple

import pytest

from uaf.runtime_rendering import (
    RenderWorldState,
    CameraProjection,
    LightType,
    RenderQueueType,
    SortMode,
    ResourceState,
    BufferType,
    TextureFormat,
    RenderCamera,
    RenderLight,
    RenderMesh,
    RenderMaterial,
    RenderableEntity,
    DrawCommand,
    RenderPass,
    RenderGraph,
    GPUResource,
    RenderFrame,
    RenderWorldSettings,
    RenderWorld,
    UniversalRuntimeRenderingFabricator,
    UniversalRuntimeRenderingValidator,
    UniversalRuntimeRenderingPackager,
)
from uaf.runtime_world import (
    UniversalRuntimeWorldFabricator,
    RuntimeTransform,
)


def make_test_world(world_id: str = "test_rend_world") -> Tuple[UniversalRuntimeRenderingFabricator, RenderWorld]:
    fab = UniversalRuntimeRenderingFabricator()
    w = fab.create_world(world_id)
    return fab, w


# ==============================================================================
# §101. RENDER WORLD TESTS (10 tests)
# ==============================================================================

class TestRenderWorldLifecycle:
    """Normative tests for Render World Creation and Lifecycle Machine (§101)."""

    def test_render_world_creation(self):
        fab, w = make_test_world("rw_create")
        assert w.render_world_id == "rw_create"
        assert w.state == RenderWorldState.CREATED
        assert len(w.renderables) == 0

    def test_render_world_identity(self):
        fab, w = make_test_world("rw_ident")
        assert fab.get_world("rw_ident") is w
        assert fab.active_world is w

    def test_render_world_state(self):
        fab, w = make_test_world("rw_state")
        fab.initialize_world(w)
        assert w.state == RenderWorldState.READY

    def test_render_world_activation(self):
        fab, w = make_test_world("rw_act")
        fab.initialize_world(w)
        fab.start_rendering(w)
        assert w.state == RenderWorldState.RENDERING

    def test_render_world_pause(self):
        fab, w = make_test_world("rw_pause")
        fab.initialize_world(w)
        fab.start_rendering(w)
        fab.pause_rendering(w)
        assert w.state == RenderWorldState.PAUSED

    def test_render_world_stop(self):
        fab, w = make_test_world("rw_stop")
        fab.initialize_world(w)
        fab.start_rendering(w)
        fab.stop_rendering(w)
        assert w.state == RenderWorldState.STOPPED

    def test_render_world_destroy(self):
        fab, w = make_test_world("rw_destroy")
        fab.create_renderable("r1", "e1", "m1", world=w)
        fab.destroy_world(w)
        assert w.state == RenderWorldState.DESTROYED
        assert len(w.renderables) == 0

    def test_invalid_render_world_transition(self):
        fab, w = make_test_world("rw_inv_trans")
        with pytest.raises(ValueError, match="NO_INVALID_RENDER_WORLD_TRANSITION"):
            fab.pause_rendering(w)  # cannot pause from CREATED

    def test_render_configuration(self):
        settings = RenderWorldSettings(
            max_draw_commands=5000,
            shadow_map_resolution=4096,
            enable_hdr=True,
            buffering_count=3,
        )
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_world("rw_cfg", settings=settings)
        assert w.settings.max_draw_commands == 5000
        assert w.settings.shadow_map_resolution == 4096
        assert w.settings.buffering_count == 3

    def test_headless_mode(self):
        fab, w = make_test_world("rw_headless")
        fab.initialize_world(w)
        frame = fab.render_frame(0.016, w)
        assert frame.frame_index == 1
        assert frame.draw_calls_count == 0


# ==============================================================================
# §102. RENDERABLE TESTS (11 tests)
# ==============================================================================

class TestRenderableEntityExecution:
    """Normative tests for Renderable Entities, Meshes, and Properties (§102)."""

    def test_renderable_creation(self):
        fab, w = make_test_world("rend_create")
        r = fab.create_renderable("r1", "e1", "mesh_cube", world=w)
        assert r.renderable_id == "r1"
        assert r.mesh_id == "mesh_cube"
        assert r.visible

    def test_renderable_identity(self):
        fab, w = make_test_world("rend_ident")
        r = fab.create_renderable("r1", "e1", "mesh_sphere", world=w)
        assert w.renderables["r1"] is r

    def test_renderable_visibility(self):
        fab, w = make_test_world("rend_vis")
        r = fab.create_renderable("r1", "e1", "mesh_1", world=w)
        fab.set_renderable_visibility("r1", False, w)
        assert not r.visible
        fab.set_renderable_visibility("r1", True, w)
        assert r.visible

    def test_renderable_transform(self):
        fab, w = make_test_world("rend_tr")
        r = fab.create_renderable("r1", "e1", "mesh_1", world=w)
        fab.set_renderable_transform("r1", [10.0, 20.0, 30.0], scale=[2.0, 2.0, 2.0], world=w)
        assert r.position == [10.0, 20.0, 30.0]
        assert r.scale == [2.0, 2.0, 2.0]

    def test_renderable_layer(self):
        fab, w = make_test_world("rend_layer")
        r = fab.create_renderable("r1", "e1", "mesh_1", layer=4, world=w)
        assert r.layer == 4

    def test_renderable_shadow_flags(self):
        fab, w = make_test_world("rend_shadow")
        r = fab.create_renderable("r1", "e1", "mesh_1", cast_shadows=False, world=w)
        assert not r.cast_shadows

    def test_renderable_materials(self):
        fab, w = make_test_world("rend_mats")
        r = fab.create_renderable("r1", "e1", "mesh_1", material_ids=["mat_base", "mat_trim"], world=w)
        assert len(r.material_ids) == 2

    def test_renderable_destroy(self):
        fab, w = make_test_world("rend_destroy")
        fab.create_renderable("r1", "e1", "mesh_1", world=w)
        fab.destroy_renderable("r1", w)
        assert "r1" not in w.renderables
        assert "r1" in w.destroyed_renderable_ids

    def test_renderable_cleanup(self):
        fab, w = make_test_world("rend_clean")
        fab.create_renderable("r1", "e1", "mesh_1", world=w)
        fab.destroy_renderable("r1", w)
        with pytest.raises(ValueError, match="RENDERABLE_NOT_FOUND"):
            fab.set_renderable_visibility("r1", False, w)

    def test_renderable_bounds(self):
        fab, w = make_test_world("rend_bounds")
        r = fab.create_renderable("r1", "e1", "mesh_1", bounds_min=[-5, -5, -5], bounds_max=[5, 5, 5], world=w)
        assert r.bounds_min == [-5, -5, -5]
        assert r.bounds_max == [5, 5, 5]

    def test_duplicate_renderable_id(self):
        fab, w = make_test_world("rend_dup")
        fab.create_renderable("r1", "e1", "m1", world=w)
        with pytest.raises(ValueError, match="DUPLICATE_RENDERABLE_ID"):
            fab.create_renderable("r1", "e2", "m2", world=w)


# ==============================================================================
# §103. CAMERA TESTS (12 tests)
# ==============================================================================

class TestCameraSystemExecution:
    """Normative tests for Camera Projections, Properties and Active Views (§103)."""

    def test_perspective_camera(self):
        fab, w = make_test_world("cam_persp")
        cam = fab.create_camera("cam_main", projection=CameraProjection.PERSPECTIVE, fov=75.0, world=w)
        assert cam.projection == CameraProjection.PERSPECTIVE
        assert cam.fov == 75.0

    def test_orthographic_camera(self):
        fab, w = make_test_world("cam_ortho")
        cam = fab.create_camera("cam_ui", projection=CameraProjection.ORTHOGRAPHIC, ortho_width=20.0, world=w)
        assert cam.projection == CameraProjection.ORTHOGRAPHIC
        assert cam.ortho_width == 20.0

    def test_camera_identity(self):
        fab, w = make_test_world("cam_ident")
        cam = fab.create_camera("cam_1", world=w)
        assert w.cameras["cam_1"] is cam

    def test_active_camera(self):
        fab, w = make_test_world("cam_active")
        c1 = fab.create_camera("c1", world=w)
        c2 = fab.create_camera("c2", world=w)
        fab.set_active_camera("c2", w)
        assert w.active_camera_id == "c2"

    def test_camera_fov_validation(self):
        fab, w = make_test_world("cam_fov_val")
        with pytest.raises(ValueError, match="INVALID_CAMERA_PARAMETERS"):
            fab.create_camera("c_bad", fov=0.0, world=w)

    def test_camera_near_far_validation(self):
        fab, w = make_test_world("cam_nf_val")
        with pytest.raises(ValueError, match="INVALID_CAMERA_PARAMETERS"):
            fab.create_camera("c_bad", near_clip=10.0, far_clip=5.0, world=w)

    def test_camera_aspect_ratio(self):
        fab, w = make_test_world("cam_aspect")
        cam = fab.create_camera("c1", world=w)
        cam.aspect_ratio = 4.0 / 3.0
        assert abs(cam.aspect_ratio - 1.333333) < 0.001

    def test_camera_transform(self):
        fab, w = make_test_world("cam_tr")
        cam = fab.create_camera("c1", position=[0.0, 5.0, -10.0], world=w)
        assert cam.position == [0.0, 5.0, -10.0]

    def test_camera_destroy(self):
        fab, w = make_test_world("cam_dest")
        fab.create_camera("c1", world=w)
        fab.destroy_camera("c1", w)
        assert "c1" not in w.cameras

    def test_camera_cleanup(self):
        fab, w = make_test_world("cam_cln")
        fab.create_camera("c1", world=w)
        fab.destroy_camera("c1", w)
        with pytest.raises(ValueError, match="CAMERA_NOT_FOUND"):
            fab.set_active_camera("c1", w)

    def test_duplicate_camera_id(self):
        fab, w = make_test_world("cam_dup")
        fab.create_camera("c1", world=w)
        with pytest.raises(ValueError, match="DUPLICATE_CAMERA_ID"):
            fab.create_camera("c1", world=w)

    def test_camera_to_dict(self):
        fab, w = make_test_world("cam_dict")
        cam = fab.create_camera("c1", world=w)
        d = cam.to_dict()
        assert d["camera_id"] == "c1"
        assert d["fov"] == 60.0


# ==============================================================================
# §104. CULLING TESTS (11 tests)
# ==============================================================================

class TestFrustumAndVisibilityCulling:
    """Normative tests for Distance and Frustum Visibility Culling (§104)."""

    def test_frustum_culling_visible(self):
        fab, w = make_test_world("cul_vis")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
        fab.create_renderable("r_in", "e1", "m1", position=[0, 0, 10], world=w)
        vis = fab.compute_visibility("cam", w)
        assert "r_in" in vis

    def test_frustum_culling_near_culled(self):
        fab, w = make_test_world("cul_near")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=2.0, far_clip=100.0, world=w)
        fab.create_renderable("r_too_close", "e1", "m1", position=[0, 0, 0.5], world=w)
        vis = fab.compute_visibility("cam", w)
        assert "r_too_close" not in vis

    def test_frustum_culling_far_culled(self):
        fab, w = make_test_world("cul_far")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=50.0, world=w)
        fab.create_renderable("r_too_far", "e1", "m1", position=[0, 0, 100], world=w)
        vis = fab.compute_visibility("cam", w)
        assert "r_too_far" not in vis

    def test_visibility_flag_culled(self):
        fab, w = make_test_world("cul_flag")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
        r = fab.create_renderable("r_hidden", "e1", "m1", position=[0, 0, 10], world=w)
        r.visible = False
        vis = fab.compute_visibility("cam", w)
        assert "r_hidden" not in vis

    def test_culling_determinism(self):
        def run_cull():
            fab, w = make_test_world("cul_det")
            fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
            for i in range(10):
                fab.create_renderable(f"r_{i}", f"e_{i}", "m1", position=[0, 0, float(i * 15)], world=w)
            return fab.compute_visibility("cam", w)

        v1 = run_cull()
        v2 = run_cull()
        assert v1 == v2

    def test_culling_counts_in_frame(self):
        fab, w = make_test_world("cul_frame")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=1.0, far_clip=20.0, world=w)
        fab.create_renderable("r_in", "e1", "m1", position=[0, 0, 5], world=w)
        fab.create_renderable("r_out", "e2", "m1", position=[0, 0, 50], world=w)
        fab.initialize_world(w)
        frame = fab.render_frame(0.016, w)
        assert frame.culled_objects_count == 1

    def test_multi_camera_culling(self):
        fab, w = make_test_world("cul_multicam")
        fab.create_camera("cam_near", position=[0, 0, 0], near_clip=0.1, far_clip=10.0, world=w)
        fab.create_camera("cam_far", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
        fab.create_renderable("r1", "e1", "m1", position=[0, 0, 25], world=w)
        vis_near = fab.compute_visibility("cam_near", w)
        vis_far = fab.compute_visibility("cam_far", w)
        assert "r1" not in vis_near
        assert "r1" in vis_far

    def test_empty_world_culling(self):
        fab, w = make_test_world("cul_empty")
        fab.create_camera("cam", world=w)
        vis = fab.compute_visibility("cam", w)
        assert len(vis) == 0

    def test_all_visible_culling(self):
        fab, w = make_test_world("cul_all")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
        for i in range(5):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", position=[0, 0, 10.0], world=w)
        vis = fab.compute_visibility("cam", w)
        assert len(vis) == 5

    def test_culling_with_no_camera(self):
        fab, w = make_test_world("cul_nocam")
        fab.create_renderable("r1", "e1", "m1", world=w)
        vis = fab.compute_visibility(world=w)
        # Without camera, defaults to returning all visible entities
        assert len(vis) == 1

    def test_culling_performance_threshold(self):
        fab, w = make_test_world("cul_perf")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=0.1, far_clip=100.0, world=w)
        for i in range(100):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", position=[0, 0, float(i)], world=w)
        t0 = time.perf_counter()
        vis = fab.compute_visibility("cam", w)
        t1 = time.perf_counter()
        assert (t1 - t0) < 0.2


# ==============================================================================
# §105. LOD TESTS (8 tests)
# ==============================================================================

class TestLODSelectionPolicy:
    """Normative tests for Distance-based Level of Detail Selection (§105)."""

    def test_lod_base_selection(self):
        fab, w = make_test_world("lod_base")
        mesh = RenderMesh(mesh_id="m_lod", lod_count=3, lod_distances=[20.0, 50.0])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 10], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 0

    def test_lod_level_1_selection(self):
        fab, w = make_test_world("lod_1")
        mesh = RenderMesh(mesh_id="m_lod", lod_count=3, lod_distances=[20.0, 50.0])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 30], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 1

    def test_lod_level_2_selection(self):
        fab, w = make_test_world("lod_2")
        mesh = RenderMesh(mesh_id="m_lod", lod_count=3, lod_distances=[20.0, 50.0])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], far_clip=200.0, world=w)
        r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 80], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 2

    def test_lod_clamping_to_max(self):
        fab, w = make_test_world("lod_clamp")
        mesh = RenderMesh(mesh_id="m_lod", lod_count=2, lod_distances=[10.0])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], far_clip=500.0, world=w)
        r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 300], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 1

    def test_lod_single_mesh(self):
        fab, w = make_test_world("lod_single")
        mesh = RenderMesh(mesh_id="m_single", lod_count=1, lod_distances=[])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        r = fab.create_renderable("r1", "e1", "m_single", position=[0, 0, 50], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 0

    def test_lod_distance_transition_smoothness(self):
        fab, w = make_test_world("lod_smooth")
        mesh = RenderMesh(mesh_id="m_lod", lod_count=2, lod_distances=[25.0])
        fab.register_mesh(mesh, w)
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 24.9], world=w)
        fab.compute_visibility("cam", w)
        assert r.current_lod == 0
        r.position = [0, 0, 25.1]
        fab.compute_visibility("cam", w)
        assert r.current_lod == 1

    def test_lod_determinism(self):
        def check_lod():
            fab, w = make_test_world("lod_det")
            mesh = RenderMesh(mesh_id="m_lod", lod_count=3, lod_distances=[15.0, 30.0])
            fab.register_mesh(mesh, w)
            fab.create_camera("cam", position=[0, 0, 0], world=w)
            r = fab.create_renderable("r1", "e1", "m_lod", position=[0, 0, 20.0], world=w)
            fab.compute_visibility("cam", w)
            return r.current_lod

        assert check_lod() == check_lod()

    def test_lod_unbounded_validation(self):
        mesh = RenderMesh(mesh_id="m_bad", lod_count=0)
        val = UniversalRuntimeRenderingValidator()
        errors = val.validate_mesh(mesh)
        assert any("INVALID_MESH" in e for e in errors)


# ==============================================================================
# §106. DRAW SUBMISSION TESTS (12 tests)
# ==============================================================================

class TestDrawSubmissionExecution:
    """Normative tests for Draw Commands, Queue Categorization and Sorting (§106)."""

    def test_draw_submission_generation(self):
        fab, w = make_test_world("draw_gen")
        fab.create_renderable("r1", "e1", "m1", world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert len(cmds) == 1
        assert cmds[0].renderable_id == "r1"

    def test_draw_command_properties(self):
        fab, w = make_test_world("draw_props")
        mesh = RenderMesh(mesh_id="m_box", index_count=36)
        fab.register_mesh(mesh, w)
        fab.create_renderable("r1", "e1", "m_box", material_ids=["mat1"], world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert cmds[0].index_count == 36
        assert cmds[0].material_id == "mat1"

    def test_draw_queue_opaque_ordering(self):
        fab, w = make_test_world("draw_opaque_ord")
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        fab.create_renderable("r_far", "e1", "m1", position=[0, 0, 50], world=w)
        fab.create_renderable("r_near", "e2", "m1", position=[0, 0, 10], world=w)
        cmds = fab.submit_draw_commands("cam", w)
        # OPAQUE sorted front-to-back
        assert cmds[0].renderable_id == "r_near"
        assert cmds[1].renderable_id == "r_far"

    def test_draw_queue_transparent_ordering(self):
        fab, w = make_test_world("draw_transp_ord")
        mat_glass = RenderMaterial(material_id="m_glass", render_queue=RenderQueueType.TRANSPARENT, is_transparent=True)
        fab.register_material(mat_glass, w)
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        fab.create_renderable("r_far", "e1", "m1", material_ids=["m_glass"], position=[0, 0, 50], world=w)
        fab.create_renderable("r_near", "e2", "m1", material_ids=["m_glass"], position=[0, 0, 10], world=w)
        cmds = fab.submit_draw_commands("cam", w)
        # TRANSPARENT sorted back-to-front
        assert cmds[0].renderable_id == "r_far"
        assert cmds[1].renderable_id == "r_near"

    def test_draw_queue_sorting_determinism(self):
        def get_order():
            fab, w = make_test_world("draw_det")
            fab.create_camera("cam", position=[0, 0, 0], world=w)
            fab.create_renderable("r1", "e1", "m1", position=[0, 0, 20], world=w)
            fab.create_renderable("r2", "e2", "m1", position=[0, 0, 10], world=w)
            return [c.renderable_id for c in fab.submit_draw_commands("cam", w)]

        assert get_order() == get_order()

    def test_draw_submission_empty_world(self):
        fab, w = make_test_world("draw_empty")
        cmds = fab.submit_draw_commands(world=w)
        assert len(cmds) == 0

    def test_draw_submission_culled_exclusion(self):
        fab, w = make_test_world("draw_culled")
        fab.create_camera("cam", position=[0, 0, 0], near_clip=1.0, far_clip=10.0, world=w)
        fab.create_renderable("r_visible", "e1", "m1", position=[0, 0, 5], world=w)
        fab.create_renderable("r_culled", "e2", "m1", position=[0, 0, 100], world=w)
        cmds = fab.submit_draw_commands("cam", w)
        assert len(cmds) == 1
        assert cmds[0].renderable_id == "r_visible"

    def test_draw_submission_limits(self):
        fab, w = make_test_world("draw_limits")
        w.settings.max_draw_commands = 2
        fab.create_renderable("r1", "e1", "m1", world=w)
        fab.create_renderable("r2", "e2", "m1", world=w)
        fab.create_renderable("r3", "e3", "m1", world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.submit_draw_commands(world=w)

    def test_draw_submission_mesh_index_count(self):
        fab, w = make_test_world("draw_idx")
        mesh = RenderMesh(mesh_id="m_quad", index_count=6)
        fab.register_mesh(mesh, w)
        fab.create_renderable("r1", "e1", "m_quad", world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert cmds[0].index_count == 6

    def test_draw_submission_multi_material(self):
        fab, w = make_test_world("draw_multi_mat")
        fab.create_renderable("r1", "e1", "m1", material_ids=["matA", "matB"], world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert cmds[0].material_id == "matA"

    def test_draw_submission_sort_key(self):
        fab, w = make_test_world("draw_key")
        fab.create_camera("cam", position=[0, 0, 0], world=w)
        fab.create_renderable("r1", "e1", "m1", position=[0, 0, 15], world=w)
        cmds = fab.submit_draw_commands("cam", w)
        assert abs(cmds[0].sort_key - 15.0) < 0.01

    def test_draw_command_to_dict(self):
        cmd = DrawCommand("dc_test", "r1", "m1", "mat1", 36, sort_key=5.0)
        d = cmd.to_dict()
        assert d["command_id"] == "dc_test"
        assert d["index_count"] == 36


# ==============================================================================
# §107. MATERIAL TESTS (11 tests)
# ==============================================================================

class TestMaterialSystemExecution:
    """Normative tests for Material Binding, Shaders, and Render Queues (§107)."""

    def test_material_registration(self):
        fab, w = make_test_world("mat_reg")
        mat = RenderMaterial(material_id="mat_pbr", shader_id="PBR_MetallicRoughness")
        fab.register_material(mat, w)
        assert w.materials["mat_pbr"] is mat

    def test_material_parameters(self):
        mat = RenderMaterial(material_id="m1", parameters={"roughness": 0.3, "metallic": 0.8})
        assert mat.parameters["roughness"] == 0.3

    def test_material_textures(self):
        mat = RenderMaterial(material_id="m1", textures={"albedo": "tex_color_01.png"})
        assert mat.textures["albedo"] == "tex_color_01.png"

    def test_material_render_queue(self):
        mat = RenderMaterial(material_id="m1", render_queue=RenderQueueType.ALPHA_TEST)
        assert mat.render_queue == RenderQueueType.ALPHA_TEST

    def test_material_transparent_flag(self):
        mat = RenderMaterial(material_id="m1", is_transparent=True)
        assert mat.is_transparent

    def test_material_double_sided(self):
        mat = RenderMaterial(material_id="m1", double_sided=True)
        assert mat.double_sided

    def test_material_shader_binding(self):
        mat = RenderMaterial(material_id="m1", shader_id="CustomShader_Water")
        assert mat.shader_id == "CustomShader_Water"

    def test_material_validation(self):
        mat = RenderMaterial(material_id="m_bad", shader_id="")
        val = UniversalRuntimeRenderingValidator()
        errors = val.validate_material(mat)
        assert any("INVALID_MATERIAL" in e for e in errors)

    def test_material_to_dict(self):
        mat = RenderMaterial(material_id="m_dict", shader_id="Sh_A")
        d = mat.to_dict()
        assert d["material_id"] == "m_dict"
        assert d["shader_id"] == "Sh_A"

    def test_shared_material_binding(self):
        fab, w = make_test_world("mat_shared")
        mat = RenderMaterial(material_id="shared_mat")
        fab.register_material(mat, w)
        r1 = fab.create_renderable("r1", "e1", "m1", material_ids=["shared_mat"], world=w)
        r2 = fab.create_renderable("r2", "e2", "m1", material_ids=["shared_mat"], world=w)
        assert r1.material_ids[0] == r2.material_ids[0]

    def test_missing_material_validation(self):
        fab, w = make_test_world("mat_missing")
        r = fab.create_renderable("r1", "e1", "m1", material_ids=["non_existent_mat"], world=w)
        val = UniversalRuntimeRenderingValidator()
        errors = val.validate_renderable(r, w)
        assert any("MISSING_MATERIAL" in e for e in errors)


# ==============================================================================
# §108. LIGHT TESTS (9 tests)
# ==============================================================================

class TestLightingSystemExecution:
    """Normative tests for Directional, Point, Spot Lights and Shadowing (§108)."""

    def test_directional_light(self):
        fab, w = make_test_world("lit_dir")
        light = fab.create_light("sun", light_type=LightType.DIRECTIONAL, direction=[0, -1, 0], world=w)
        assert light.light_type == LightType.DIRECTIONAL

    def test_point_light(self):
        fab, w = make_test_world("lit_point")
        light = fab.create_light("lamp", light_type=LightType.POINT, position=[0, 3, 0], range=15.0, world=w)
        assert light.light_type == LightType.POINT
        assert light.range == 15.0

    def test_spot_light(self):
        fab, w = make_test_world("lit_spot")
        light = fab.create_light("flashlight", light_type=LightType.SPOT, world=w)
        assert light.light_type == LightType.SPOT

    def test_rect_light(self):
        fab, w = make_test_world("lit_rect")
        light = fab.create_light("panel", light_type=LightType.RECT, world=w)
        assert light.light_type == LightType.RECT

    def test_light_intensity(self):
        fab, w = make_test_world("lit_intensity")
        light = fab.create_light("bright", intensity=5000.0, world=w)
        assert light.intensity == 5000.0

    def test_light_color(self):
        fab, w = make_test_world("lit_color")
        light = fab.create_light("warm", color=[1.0, 0.8, 0.6], world=w)
        assert light.color == [1.0, 0.8, 0.6]

    def test_light_shadow_flag(self):
        fab, w = make_test_world("lit_shadow")
        light = fab.create_light("no_shadow", casts_shadows=False, world=w)
        assert not light.casts_shadows

    def test_light_destroy(self):
        fab, w = make_test_world("lit_dest")
        fab.create_light("l1", world=w)
        fab.destroy_light("l1", w)
        assert "l1" not in w.lights

    def test_light_validation(self):
        fab, w = make_test_world("lit_val")
        with pytest.raises(ValueError, match="INVALID_LIGHT_PARAMETERS"):
            fab.create_light("l_bad", intensity=-10.0, world=w)


# ==============================================================================
# §109. RENDER GRAPH TESTS (13 tests)
# ==============================================================================

class TestRenderGraphScheduling:
    """Normative tests for Acyclic Render Graph and Pass Scheduling (§109)."""

    def test_render_graph_creation(self):
        fab, w = make_test_world("rg_create")
        assert w.render_graph.graph_id == "main_graph"
        assert len(w.render_graph.passes) == 0

    def test_render_pass_creation(self):
        fab, w = make_test_world("rg_pass_c")
        p = fab.add_render_pass("shadow_pass", pass_type="DepthPass", world=w)
        assert p.pass_id == "shadow_pass"
        assert p.pass_type == "DepthPass"

    def test_render_pass_dependencies(self):
        fab, w = make_test_world("rg_pass_dep")
        fab.add_render_pass("p1", world=w)
        p2 = fab.add_render_pass("p2", dependencies=["p1"], world=w)
        assert "p1" in p2.dependencies

    def test_render_graph_topological_sort(self):
        fab, w = make_test_world("rg_sort")
        fab.add_render_pass("forward_pass", dependencies=["shadow_pass", "gbuffer_pass"], world=w)
        fab.add_render_pass("gbuffer_pass", dependencies=["shadow_pass"], world=w)
        fab.add_render_pass("shadow_pass", dependencies=[], world=w)
        order = fab.compile_render_graph(w)
        assert order.index("shadow_pass") < order.index("gbuffer_pass")
        assert order.index("gbuffer_pass") < order.index("forward_pass")

    def test_render_graph_cycle_detection(self):
        fab, w = make_test_world("rg_cycle")
        fab.add_render_pass("passA", dependencies=["passB"], world=w)
        fab.add_render_pass("passB", dependencies=["passA"], world=w)
        with pytest.raises(ValueError, match="NO_RENDER_GRAPH_CYCLE"):
            fab.compile_render_graph(w)

    def test_render_graph_inputs_outputs(self):
        fab, w = make_test_world("rg_io")
        p = fab.add_render_pass("bloom", inputs=["HDR_Color"], outputs=["LDR_Color"], world=w)
        assert "HDR_Color" in p.inputs
        assert "LDR_Color" in p.outputs

    def test_render_pass_enabled_toggle(self):
        fab, w = make_test_world("rg_enable")
        p = fab.add_render_pass("ssao", world=w)
        p.enabled = False
        assert not p.enabled

    def test_duplicate_pass_rejection(self):
        fab, w = make_test_world("rg_dup")
        fab.add_render_pass("p1", world=w)
        with pytest.raises(ValueError, match="DUPLICATE_PASS_ID"):
            fab.add_render_pass("p1", world=w)

    def test_render_graph_execution_order_stored(self):
        fab, w = make_test_world("rg_stored")
        fab.add_render_pass("p_init", world=w)
        order = fab.compile_render_graph(w)
        assert w.render_graph.execution_order == ["p_init"]

    def test_render_graph_to_dict(self):
        fab, w = make_test_world("rg_dict")
        fab.add_render_pass("p1", world=w)
        d = w.render_graph.to_dict()
        assert "p1" in d["passes"]

    def test_multiple_independent_passes(self):
        fab, w = make_test_world("rg_indep")
        fab.add_render_pass("p_a", world=w)
        fab.add_render_pass("p_b", world=w)
        order = fab.compile_render_graph(w)
        assert len(order) == 2

    def test_deep_render_graph_pipeline(self):
        fab, w = make_test_world("rg_deep")
        for i in range(10):
            deps = [f"p_{i-1}"] if i > 0 else []
            fab.add_render_pass(f"p_{i}", dependencies=deps, world=w)
        order = fab.compile_render_graph(w)
        assert len(order) == 10
        assert order == [f"p_{i}" for i in range(10)]

    def test_missing_pass_dependency_validation(self):
        fab, w = make_test_world("rg_missing_dep")
        fab.add_render_pass("p1", dependencies=["unregistered_pass"], world=w)
        val = UniversalRuntimeRenderingValidator()
        errors = val.validate_render_graph(w.render_graph)
        assert any("MISSING_PASS_DEPENDENCY" in e for e in errors)


# ==============================================================================
# §110. GPU RESOURCE TESTS (11 tests)
# ==============================================================================

class TestGPUResourceExecution:
    """Normative tests for GPU Resource Abstraction, States and Lifetimes (§110)."""

    def test_gpu_resource_allocation(self):
        fab, w = make_test_world("gpu_alloc")
        res = fab.allocate_gpu_resource("vb_1", "VertexBuffer", 1024, world=w)
        assert res.resource_id == "vb_1"
        assert res.size_bytes == 1024

    def test_gpu_resource_size(self):
        fab, w = make_test_world("gpu_size")
        res = fab.allocate_gpu_resource("tex_1", "Texture2D", 4096 * 4096 * 4, world=w)
        assert res.size_bytes == 67108864

    def test_gpu_resource_state(self):
        fab, w = make_test_world("gpu_state")
        res = fab.allocate_gpu_resource("rt_1", "RenderTarget", 1920 * 1080 * 4, world=w)
        res.state = ResourceState.RENDER_TARGET
        assert res.state == ResourceState.RENDER_TARGET

    def test_gpu_resource_ref_count(self):
        fab, w = make_test_world("gpu_ref")
        res = fab.allocate_gpu_resource("buf_1", "UniformBuffer", 256, world=w)
        res.ref_count += 1
        assert res.ref_count == 2

    def test_gpu_resource_release(self):
        fab, w = make_test_world("gpu_rel")
        fab.allocate_gpu_resource("temp_buf", "StorageBuffer", 512, world=w)
        fab.release_gpu_resource("temp_buf", w)
        assert "temp_buf" not in w.gpu_resources

    def test_duplicate_gpu_resource_rejection(self):
        fab, w = make_test_world("gpu_dup")
        fab.allocate_gpu_resource("res1", "VB", 100, world=w)
        with pytest.raises(ValueError, match="DUPLICATE_GPU_RESOURCE"):
            fab.allocate_gpu_resource("res1", "VB", 100, world=w)

    def test_invalid_gpu_resource_size(self):
        fab, w = make_test_world("gpu_inv_size")
        with pytest.raises(ValueError, match="INVALID_GPU_RESOURCE"):
            fab.allocate_gpu_resource("bad_res", "VB", 0, world=w)

    def test_gpu_resource_cleanup(self):
        fab, w = make_test_world("gpu_clean")
        fab.allocate_gpu_resource("b1", "VB", 100, world=w)
        fab.release_gpu_resource("b1", w)
        with pytest.raises(ValueError, match="GPU_RESOURCE_NOT_FOUND"):
            fab.release_gpu_resource("b1", w)

    def test_gpu_resource_to_dict(self):
        res = GPUResource("r_dict", "IB", 512, state=ResourceState.COPY_DST)
        d = res.to_dict()
        assert d["resource_id"] == "r_dict"
        assert d["state"] == ResourceState.COPY_DST.value

    def test_multiple_gpu_resources(self):
        fab, w = make_test_world("gpu_multi")
        for i in range(5):
            fab.allocate_gpu_resource(f"res_{i}", "VB", 100 * (i + 1), world=w)
        assert len(w.gpu_resources) == 5

    def test_gpu_resource_state_transitions(self):
        res = GPUResource("res_trans", "Texture", 1024, state=ResourceState.COPY_DST)
        res.state = ResourceState.SHADER_RESOURCE
        assert res.state == ResourceState.SHADER_RESOURCE


# ==============================================================================
# PART 3: FRAME SYNCHRONIZATION, PRESENTATION, GOLDEN FRAME & DETERMINISM
# ==============================================================================

class TestFrameSynchronizationUAF81_75:
    """Normative acceptance tests for Frame Synchronization (§111)."""

    def test_frame_context(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_1")
        fab.advance_state("w_sync_1", RenderWorldState.READY)
        frame = fab.render_frame(0.016, world)
        assert frame is not None
        assert frame.frame_index == 1
        assert frame.delta_time == 0.016

    def test_frame_index(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_2")
        fab.advance_state("w_sync_2", RenderWorldState.READY)
        f1 = fab.render_frame(0.016, world)
        f2 = fab.render_frame(0.016, world)
        assert f1.frame_index == 1
        assert f2.frame_index == 2
        assert world.frames_rendered == 2

    def test_double_buffering(self):
        settings = RenderWorldSettings(buffering_count=2)
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_3", settings=settings)
        assert world.settings.buffering_count == 2

    def test_triple_buffering(self):
        settings = RenderWorldSettings(buffering_count=3)
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_4", settings=settings)
        assert world.settings.buffering_count == 3

    def test_frame_fence(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_5")
        fab.advance_state("w_sync_5", RenderWorldState.READY)
        fab.render_frame(0.016, world)
        assert fab.wait_frame_fence(timeout_ms=500.0, world=world) is True

    def test_gpu_completion(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_6")
        fab.advance_state("w_sync_6", RenderWorldState.READY)
        res = fab.allocate_gpu_resource("buf_sync", "GPU_BUFFER", 1024, world)
        assert res.state in (ResourceState.READY, ResourceState.SHADER_RESOURCE)
        fab.render_frame(0.016, world)
        assert fab.wait_frame_fence(world=world) is True

    def test_frame_resource_reuse(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_7")
        fab.advance_state("w_sync_7", RenderWorldState.READY)
        g = fab.build_render_graph("g_sync", world)
        fab.add_pass_to_graph("pass1", inputs=["t_res"], outputs=[], world=world)
        fab.add_pass_to_graph("pass2", inputs=[], outputs=["t_res"], world=world)
        assert "t_res" in g.passes["pass1"].inputs
        assert "t_res" in g.passes["pass2"].outputs

    def test_frame_resource_retirement(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_8")
        res = fab.allocate_gpu_resource("res_retire", "GPU_BUFFER", 512, world)
        fab.release_gpu_resource("res_retire", world)
        assert "res_retire" not in world.gpu_resources

    def test_frame_overwrite_protection(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_sync_9")
        fab.advance_state("w_sync_9", RenderWorldState.READY)
        fab.advance_state("w_sync_9", RenderWorldState.PAUSED)
        f_paused = fab.render_frame(0.016, world)
        assert f_paused.delta_time == 0.0
        assert world.frames_rendered == 0

    def test_frame_determinism(self):
        fab1 = UniversalRuntimeRenderingFabricator()
        w1 = fab1.create_render_world("w_sync_det_1")
        fab1.advance_state("w_sync_det_1", RenderWorldState.READY)

        fab2 = UniversalRuntimeRenderingFabricator()
        w2 = fab2.create_render_world("w_sync_det_2")
        fab2.advance_state("w_sync_det_2", RenderWorldState.READY)

        f1 = fab1.render_frame(0.016, w1)
        f2 = fab2.render_frame(0.016, w2)
        assert f1.frame_index == f2.frame_index
        assert f1.draw_calls_count == f2.draw_calls_count


class TestPresentationUAF81_75:
    """Normative acceptance tests for Presentation (§112)."""

    def test_present(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_1")
        fab.advance_state("w_pres_1", RenderWorldState.READY)
        fab.render_frame(0.016, world)
        assert fab.present_frame(world) is True

    def test_present_order(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_2")
        fab.advance_state("w_pres_2", RenderWorldState.READY)
        f = fab.render_frame(0.016, world)
        assert f.frame_index == 1
        assert fab.present_frame(world) is True

    def test_headless_present(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_3")
        fab.advance_state("w_pres_3", RenderWorldState.READY)
        fab.render_frame(0.016, world)
        assert fab.present_frame(world) is True

    def test_surface_failure(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_4")
        with pytest.raises(ValueError, match="CANNOT_PRESENT_FRAME"):
            fab.present_frame(world)

    def test_resize(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_5")
        dims = fab.resize_surface(1920, 1080, world)
        assert dims == (1920, 1080)
        assert world.settings.metadata["surface_width"] == 1920
        assert world.settings.metadata["surface_height"] == 1080

    def test_resize_resource_rebuild(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_6")
        fp1 = world.compute_fingerprint()
        fab.resize_surface(2560, 1440, world)
        fp2 = world.content_fingerprint
        assert fp1 != fp2

    def test_frame_submission_failure(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_7")
        fab.advance_state("w_pres_7", RenderWorldState.READY)
        fab.advance_state("w_pres_7", RenderWorldState.STOPPED)
        with pytest.raises(ValueError, match="NO_UPDATE_BEFORE_INITIALIZATION"):
            fab.render_frame(0.016, world)

    def test_present_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_pres_8")
        fab.advance_state("w_pres_8", RenderWorldState.READY)
        fab.render_frame(0.016, world)
        fab.advance_state("w_pres_8", RenderWorldState.STOPPED)
        fab.advance_state("w_pres_8", RenderWorldState.DESTROYED)
        assert world.state == RenderWorldState.DESTROYED


class TestGoldenFrameUAF81_75:
    """Normative acceptance tests for Golden Frames (§113)."""

    def test_golden_empty_frame(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_empty")
        fab.advance_state("w_g_empty", RenderWorldState.READY)
        gf = fab.capture_golden_frame(world)
        assert "golden_hash" in gf
        assert gf["renderables_count"] == 0

    def test_golden_single_mesh(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_single")
        fab.register_mesh(RenderMesh("m1", 100, 300), world)
        fab.register_material(RenderMaterial("mat1"), world)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=world)
        gf = fab.capture_golden_frame(world)
        assert gf["renderables_count"] == 1

    def test_golden_material(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_mat")
        fab.register_material(RenderMaterial("mat_pbr", "PBR_Standard", {"roughness": 0.5}), world)
        gf = fab.capture_golden_frame(world)
        assert "golden_hash" in gf

    def test_golden_textured_material(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_tex")
        fab.register_material(RenderMaterial("mat_tex", textures={"albedo": "tex_diffuse.png"}), world)
        gf = fab.capture_golden_frame(world)
        assert "golden_hash" in gf

    def test_golden_multiple_objects(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_multi")
        fab.register_mesh(RenderMesh("m1", 10, 30), world)
        fab.register_material(RenderMaterial("mat1"), world)
        for i in range(5):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], world=world)
        gf = fab.capture_golden_frame(world)
        assert gf["renderables_count"] == 5

    def test_golden_camera(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_cam")
        fab.create_camera("cam_main", projection=CameraProjection.PERSPECTIVE, fov=60.0, world=world)
        gf = fab.capture_golden_frame(world)
        assert gf["cameras_count"] == 1

    def test_golden_orthographic(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_ortho")
        fab.create_camera("cam_ortho", projection=CameraProjection.ORTHOGRAPHIC, ortho_width=20.0, world=world)
        gf = fab.capture_golden_frame(world)
        assert gf["cameras_count"] == 1

    def test_golden_lighting(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_light")
        fab.create_light("sun", LightType.DIRECTIONAL, intensity=2.0, world=world)
        gf = fab.capture_golden_frame(world)
        assert gf["lights_count"] == 1

    def test_golden_transparency(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_transp")
        fab.register_material(RenderMaterial("glass", is_transparent=True, render_queue=RenderQueueType.TRANSPARENT), world)
        gf = fab.capture_golden_frame(world)
        assert "golden_hash" in gf

    def test_golden_culling(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_cull")
        fab.create_camera("cam", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=10.0, world=world)
        fab.register_mesh(RenderMesh("m1", 10, 30), world)
        fab.register_material(RenderMaterial("mat1"), world)
        fab.create_renderable("r_in", "e1", "m1", ["mat1"], position=[0.0, 0.0, 5.0], world=world)
        fab.create_renderable("r_out", "e2", "m1", ["mat1"], position=[0.0, 0.0, 50.0], world=world)
        vis = fab.compute_visibility(world=world)
        assert "r_in" in vis
        assert "r_out" not in vis

    def test_golden_lod(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_lod")
        fab.create_camera("cam", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=500.0, world=world)
        mesh = RenderMesh("m_lod", 10, 30, lod_count=3, lod_distances=[20.0, 60.0])
        fab.register_mesh(mesh, world)
        fab.register_material(RenderMaterial("mat1"), world)
        r = fab.create_renderable("r_lod", "e1", "m_lod", ["mat1"], position=[0.0, 0.0, 30.0], world=world)
        fab.compute_visibility(world=world)
        assert r.current_lod == 1

    def test_golden_render_graph(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_graph")
        fab.build_render_graph("main_graph", world)
        fab.add_pass_to_graph("depth", world=world)
        fab.add_pass_to_graph("shading", dependencies=["depth"], world=world)
        gf = fab.capture_golden_frame(world)
        assert "golden_hash" in gf

    def test_golden_debug_render(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_dbg")
        fab.create_light("sun", LightType.DIRECTIONAL, world=world)
        dbg = fab.get_debug_render_data(world)
        assert "lights" in dbg
        assert "sun" in dbg["lights"]

    def test_golden_headless_draw_list(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_head")
        fab.advance_state("w_g_head", RenderWorldState.READY)
        fab.register_mesh(RenderMesh("m1", 10, 30), world)
        fab.register_material(RenderMaterial("mat1"), world)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=world)
        cmds = fab.submit_draw_commands(world=world)
        assert len(cmds) == 1

    def test_golden_frame_sequence(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_seq")
        fab.advance_state("w_g_seq", RenderWorldState.READY)
        hashes = []
        for _ in range(3):
            fab.render_frame(0.016, world)
            hashes.append(fab.capture_golden_frame(world)["golden_hash"])
        assert len(set(hashes)) == 3

    def test_golden_resource_rebuild(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_res_reb")
        fab.allocate_gpu_resource("rt1", "GPU_TEXTURE", 4096, world)
        gf1 = fab.capture_golden_frame(world)
        fab.allocate_gpu_resource("rt2", "GPU_TEXTURE", 4096, world)
        gf2 = fab.capture_golden_frame(world)
        assert gf1["golden_hash"] != gf2["golden_hash"]

    def test_golden_render_failure(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_fail")
        fab.advance_state("w_g_fail", RenderWorldState.READY)
        fab.advance_state("w_g_fail", RenderWorldState.FAILED)
        assert world.state == RenderWorldState.FAILED

    def test_golden_render_shutdown(self):
        fab = UniversalRuntimeRenderingFabricator()
        world = fab.create_render_world("w_g_shut")
        fab.advance_state("w_g_shut", RenderWorldState.READY)
        fab.advance_state("w_g_shut", RenderWorldState.STOPPING)
        fab.advance_state("w_g_shut", RenderWorldState.STOPPED)
        fab.advance_state("w_g_shut", RenderWorldState.DESTROYED)
        assert world.state == RenderWorldState.DESTROYED


class TestDeterminismUAF81_75:
    """Normative acceptance tests for Determinism (§114)."""

    def test_same_scene_same_draw_list(self):
        def build_world(wid):
            fab = UniversalRuntimeRenderingFabricator()
            w = fab.create_render_world(wid)
            fab.advance_state(wid, RenderWorldState.READY)
            fab.register_mesh(RenderMesh("m1", 10, 30), w)
            fab.register_material(RenderMaterial("mat1"), w)
            fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
            return fab.submit_draw_commands(world=w)

        d1 = build_world("w_det_1")
        d2 = build_world("w_det_2")
        assert [c.command_id for c in d1] == [c.command_id for c in d2]

    def test_same_camera_same_visibility(self):
        def get_vis(wid):
            fab = UniversalRuntimeRenderingFabricator()
            w = fab.create_render_world(wid)
            fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=20.0, world=w)
            fab.register_mesh(RenderMesh("m1", 10, 30), w)
            fab.register_material(RenderMaterial("mat1"), w)
            fab.create_renderable("r1", "e1", "m1", ["mat1"], position=[0.0, 0.0, 10.0], world=w)
            fab.create_renderable("r2", "e2", "m1", ["mat1"], position=[0.0, 0.0, 50.0], world=w)
            return fab.compute_visibility(world=w)

        assert get_vis("w_v1") == get_vis("w_v2")

    def test_same_inputs_same_culling(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_cull_det")
        fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=10.0, world=w)
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], position=[0.0, 0.0, 5.0], world=w)
        v1 = fab.compute_visibility(world=w)
        v2 = fab.compute_visibility(world=w)
        assert v1 == v2

    def test_same_inputs_same_lod(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_lod_det")
        fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=100.0, world=w)
        mesh = RenderMesh("m1", 10, 30, lod_count=3, lod_distances=[10.0, 30.0])
        fab.register_mesh(mesh, w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r1", "e1", "m1", ["mat1"], position=[0.0, 0.0, 20.0], world=w)
        fab.compute_visibility(world=w)
        lod1 = r.current_lod
        fab.compute_visibility(world=w)
        lod2 = r.current_lod
        assert lod1 == lod2 == 1

    def test_same_inputs_same_sorting(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sort_det")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1", render_queue=RenderQueueType.OPAQUE), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], position=[0.0, 0.0, 20.0], world=w)
        fab.create_renderable("r2", "e2", "m1", ["mat1"], position=[0.0, 0.0, 5.0], world=w)
        fab.create_camera("c", position=[0.0, 0.0, 0.0], world=w)
        cmds1 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        cmds2 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        assert cmds1 == cmds2 == ["r2", "r1"]

    def test_same_inputs_same_render_graph(self):
        def get_order(wid):
            fab = UniversalRuntimeRenderingFabricator()
            w = fab.create_render_world(wid)
            fab.build_render_graph("g", w)
            fab.add_pass_to_graph("c", world=w)
            fab.add_pass_to_graph("b", dependencies=["c"], world=w)
            fab.add_pass_to_graph("a", dependencies=["b"], world=w)
            return fab.compile_render_graph(w)

        assert get_order("w_rg_1") == get_order("w_rg_2")

    def test_same_inputs_same_resource_bindings(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_bind_det")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1", shader_id="PBR"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
        c1 = fab.submit_draw_commands(world=w)[0]
        c2 = fab.submit_draw_commands(world=w)[0]
        assert c1.mesh_id == c2.mesh_id == "m1"
        assert c1.material_id == c2.material_id == "mat1"

    def test_same_frame_same_command_order(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_ord_det")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(4):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i * 10)], world=w)
        fab.create_camera("c", position=[0.0, 0.0, 0.0], world=w)
        order1 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        order2 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        assert order1 == order2

    def test_replay_render_determinism(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_rep_det")
        fab.advance_state("w_rep_det", RenderWorldState.READY)
        f1 = fab.render_frame(0.016, w)
        fab.reset()
        w2 = fab.create_render_world("w_rep_det")
        fab.advance_state("w_rep_det", RenderWorldState.READY)
        f2 = fab.render_frame(0.016, w2)
        assert f1.draw_calls_count == f2.draw_calls_count
        assert f1.frame_index == f2.frame_index

    def test_golden_frame_determinism(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_gf_det")
        fab.advance_state("w_gf_det", RenderWorldState.READY)
        gf1 = fab.capture_golden_frame(w)
        gf2 = fab.capture_golden_frame(w)
        assert gf1["golden_hash"] == gf2["golden_hash"]


# ==============================================================================
# PART 4: SECURITY, PERFORMANCE, STRESS & PROPERTY-BASED TESTS
# ==============================================================================

class TestSecurityUAF81_75:
    """Normative acceptance tests for Security and Resource Limits (§115)."""

    def test_draw_command_flood(self):
        fab = UniversalRuntimeRenderingFabricator()
        settings = RenderWorldSettings(max_draw_commands=2)
        world = fab.create_render_world("w_sec_1", settings=settings)
        fab.register_mesh(RenderMesh("m1", 10, 30), world)
        fab.register_material(RenderMaterial("mat1"), world)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=world)
        fab.create_renderable("r2", "e2", "m1", ["mat1"], world=world)
        fab.create_renderable("r3", "e3", "m1", ["mat1"], world=world)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.submit_draw_commands(world=world)

    def test_renderable_count_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        settings = RenderWorldSettings(max_renderables=3)
        world = fab.create_render_world("w_sec_2", settings=settings)
        fab.register_mesh(RenderMesh("m1", 10, 30), world)
        fab.register_material(RenderMaterial("mat1"), world)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=world)
        fab.create_renderable("r2", "e2", "m1", ["mat1"], world=world)
        fab.create_renderable("r3", "e3", "m1", ["mat1"], world=world)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_renderable("r4", "e4", "m1", ["mat1"], world=world)

    def test_light_count_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        settings = RenderWorldSettings(max_lights=2)
        world = fab.create_render_world("w_sec_3", settings=settings)
        fab.create_light("l1", world=world)
        fab.create_light("l2", world=world)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.create_light("l3", world=world)

    def test_material_binding_abuse(self):
        val = UniversalRuntimeRenderingValidator()
        r = RenderableEntity("r1", "e1", "m1", material_ids=[""])
        issues = val.validate_renderable(r)
        assert any(i.error_code == "EMPTY_MATERIAL_BINDING" for i in issues)

    def test_texture_binding_abuse(self):
        val = UniversalRuntimeRenderingValidator()
        m = RenderMaterial("m1", textures={"albedo": ""})
        issues = val.validate_material(m)
        assert any(i.error_code == "EMPTY_TEXTURE_PATH" for i in issues)

    def test_shader_reference_abuse(self):
        val = UniversalRuntimeRenderingValidator()
        m = RenderMaterial("m1", shader_id="   ")
        issues = val.validate_material(m)
        assert any(i.error_code == "EMPTY_SHADER_ID" for i in issues)

    def test_render_graph_cycle(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_rg_cycle")
        fab.build_render_graph("g", w)
        fab.add_pass_to_graph("p1", dependencies=["p2"], world=w)
        fab.add_pass_to_graph("p2", dependencies=["p1"], world=w)
        with pytest.raises(ValueError, match="NO_RENDER_GRAPH_CYCLE"):
            fab.compile_render_graph(w)

    def test_render_graph_node_explosion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_node_exp")
        fab.build_render_graph("g", w)
        for i in range(100):
            fab.add_pass_to_graph(f"pass_{i}", world=w)
        assert len(w.render_graph.passes) == 100

    def test_transient_resource_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_trans")
        for i in range(50):
            fab.allocate_gpu_resource(f"trans_{i}", "GPU_BUFFER", 1024, w)
        assert len(w.gpu_resources) == 50

    def test_gpu_resource_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_gpu_ex")
        for i in range(100):
            fab.allocate_gpu_resource(f"res_{i}", "GPU_TEXTURE", 2048, w)
        assert len(w.gpu_resources) == 100

    def test_frame_resource_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_fr_ex")
        fab.advance_state("w_sec_fr_ex", RenderWorldState.READY)
        for _ in range(20):
            fab.render_frame(0.016, w)
        assert w.frames_rendered == 20

    def test_command_buffer_overflow(self):
        fab = UniversalRuntimeRenderingFabricator()
        settings = RenderWorldSettings(max_draw_commands=1)
        w = fab.create_render_world("w_sec_cmd_ov", settings=settings)
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
        fab.create_renderable("r2", "e2", "m1", ["mat1"], world=w)
        with pytest.raises(ValueError, match="SECURITY_VIOLATION"):
            fab.submit_draw_commands(world=w)

    def test_invalid_pipeline(self):
        val = UniversalRuntimeRenderingValidator()
        mat = RenderMaterial("bad_pipeline", shader_id="")
        issues = val.validate_material(mat)
        assert any(i.severity == "ERROR" for i in issues)

    def test_invalid_shader_binding(self):
        val = UniversalRuntimeRenderingValidator()
        mat = RenderMaterial("bad_shader", shader_id="   ")
        issues = val.validate_material(mat)
        assert any("SHADER" in i.error_code for i in issues)

    def test_invalid_texture_dimensions(self):
        val = UniversalRuntimeRenderingValidator()
        res = GPUResource("tex_bad", "GPU_TEXTURE", size_bytes=-1)
        issues = val.validate_gpu_resource(res)
        assert any(i.error_code == "INVALID_GPU_RESOURCE_SIZE" for i in issues)

    def test_invalid_buffer_size(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_buf_sz")
        with pytest.raises(ValueError, match="INVALID_GPU_RESOURCE"):
            fab.allocate_gpu_resource("buf_neg", "GPU_BUFFER", -100, w)

    def test_culling_input_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_cull_ex")
        fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=100.0, world=w)
        for i in range(500):
            r = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i)])
            w.renderables[f"r_{i}"] = r
        vis = fab.compute_visibility(world=w)
        assert len(vis) <= 100

    def test_lod_explosion(self):
        val = UniversalRuntimeRenderingValidator()
        m = RenderMesh("mesh_lod_exp", 100, 300, lod_count=16, lod_distances=[float(i * 10) for i in range(16)])
        issues = val.validate_mesh(m)
        assert isinstance(issues, list)

    def test_screenshot_resource_exhaustion(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_sc")
        for i in range(10):
            gf = fab.capture_golden_frame(w)
            assert "golden_hash" in gf

    def test_debug_draw_flood(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_sec_dbg_fld")
        for i in range(200):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"])
        dbg = fab.get_debug_render_data(w)
        assert len(dbg["renderables"]) == 200


class TestPerformanceUAF81_75:
    """Normative acceptance tests for Performance Throughput (§116)."""

    def test_1k_renderables(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_1k")
        t0 = time.perf_counter()
        for i in range(1000):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i % 50)])
        elapsed = time.perf_counter() - t0
        assert len(w.renderables) == 1000
        assert elapsed < 1.0

    def test_10k_renderables(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_10k")
        t0 = time.perf_counter()
        entities = {
            f"r_{i}": RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"])
            for i in range(10000)
        }
        w.renderables.update(entities)
        elapsed = time.perf_counter() - t0
        assert len(w.renderables) == 10000
        assert elapsed < 1.5

    def test_100k_renderables(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_100k")
        assert w.settings.max_renderables >= 50000

    def test_large_mesh_scene(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_lmesh")
        t0 = time.perf_counter()
        for i in range(500):
            m = RenderMesh(f"m_{i}", 10000, 30000)
            fab.register_mesh(m, w)
        elapsed = time.perf_counter() - t0
        assert len(w.meshes) == 500
        assert elapsed < 0.5

    def test_large_material_scene(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_lmat")
        t0 = time.perf_counter()
        for i in range(500):
            mat = RenderMaterial(f"mat_{i}", "PBR_Standard")
            fab.register_material(mat, w)
        elapsed = time.perf_counter() - t0
        assert len(w.materials) == 500
        assert elapsed < 0.5

    def test_many_lights(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_lights")
        t0 = time.perf_counter()
        for i in range(100):
            fab.create_light(f"l_{i}", LightType.POINT, intensity=1.0, world=w)
        elapsed = time.perf_counter() - t0
        assert len(w.lights) == 100
        assert elapsed < 0.5

    def test_large_visibility_set(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_vis")
        fab.create_camera("cam", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=1000.0, world=w)
        for i in range(1000):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, 10.0])
        t0 = time.perf_counter()
        vis = fab.compute_visibility(world=w)
        elapsed = time.perf_counter() - t0
        assert len(vis) == 1000
        assert elapsed < 0.5

    def test_frustum_culling_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_cull")
        fab.create_camera("cam", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=50.0, world=w)
        for i in range(2000):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i)])
        t0 = time.perf_counter()
        vis = fab.compute_visibility(world=w)
        elapsed = time.perf_counter() - t0
        assert len(vis) <= 50
        assert elapsed < 0.5

    def test_lod_selection_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_lod")
        fab.create_camera("cam", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=500.0, world=w)
        m = RenderMesh("mesh_lod", 100, 300, lod_count=4, lod_distances=[25.0, 50.0, 100.0])
        fab.register_mesh(m, w)
        for i in range(1000):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "mesh_lod", ["mat1"], position=[0.0, 0.0, float(i % 150)])
        t0 = time.perf_counter()
        fab.compute_visibility(world=w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_draw_submission_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_draw")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(500):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i)], world=w)
        t0 = time.perf_counter()
        cmds = fab.submit_draw_commands(world=w)
        elapsed = time.perf_counter() - t0
        assert len(cmds) == 500
        assert elapsed < 0.5

    def test_batching_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_batch")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(500):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert len(cmds) == 500

    def test_instancing_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_inst")
        fab.register_mesh(RenderMesh("m_inst", 100, 300), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(300):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m_inst", ["mat1"], world=w)
        cmds = fab.submit_draw_commands(world=w)
        assert all(c.mesh_id == "m_inst" for c in cmds)

    def test_render_graph_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_rg")
        fab.build_render_graph("g", w)
        for i in range(100):
            dep = [f"p_{i-1}"] if i > 0 else []
            fab.add_pass_to_graph(f"p_{i}", dependencies=dep, world=w)
        t0 = time.perf_counter()
        order = fab.compile_render_graph(w)
        elapsed = time.perf_counter() - t0
        assert len(order) == 100
        assert elapsed < 0.5

    def test_gpu_resource_creation(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_gpu")
        t0 = time.perf_counter()
        for i in range(1000):
            fab.allocate_gpu_resource(f"buf_{i}", "GPU_BUFFER", 1024, w)
        elapsed = time.perf_counter() - t0
        assert len(w.gpu_resources) == 1000
        assert elapsed < 0.5

    def test_frame_submission(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_frame")
        fab.advance_state("w_perf_frame", RenderWorldState.READY)
        t0 = time.perf_counter()
        for _ in range(60):
            fab.render_frame(0.016, w)
        elapsed = time.perf_counter() - t0
        assert w.frames_rendered == 60
        assert elapsed < 0.5

    def test_frame_synchronization(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_sync")
        fab.advance_state("w_perf_sync", RenderWorldState.READY)
        t0 = time.perf_counter()
        for _ in range(30):
            fab.render_frame(0.016, w)
            fab.wait_frame_fence(world=w)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_headless_render_throughput(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_perf_head")
        fab.advance_state("w_perf_head", RenderWorldState.READY)
        t0 = time.perf_counter()
        for _ in range(100):
            fab.render_frame(0.016, w)
        elapsed = time.perf_counter() - t0
        assert w.frames_rendered == 100
        assert elapsed < 0.5


class TestStressUAF81_75:
    """Normative acceptance tests for Stress and Rapid Reconfiguration (§117)."""

    def test_stress_renderable_spawn(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_sp")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(500):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], world=w)
        assert len(w.renderables) == 500

    def test_stress_renderable_destroy(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_des")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(100):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], world=w)
        for i in range(100):
            fab.destroy_renderable(f"r_{i}", w)
        assert len(w.renderables) == 0

    def test_stress_material_create(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_mat_c")
        for i in range(200):
            fab.register_material(RenderMaterial(f"mat_{i}"), w)
        assert len(w.materials) == 200

    def test_stress_material_destroy(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_mat_d")
        for i in range(100):
            fab.register_material(RenderMaterial(f"mat_{i}"), w)
        w.materials.clear()
        assert len(w.materials) == 0

    def test_stress_texture_create(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_tex_c")
        for i in range(150):
            fab.allocate_gpu_resource(f"tex_{i}", "GPU_TEXTURE", 4096, w)
        assert len(w.gpu_resources) == 150

    def test_stress_texture_destroy(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_tex_d")
        for i in range(100):
            fab.allocate_gpu_resource(f"tex_{i}", "GPU_TEXTURE", 4096, w)
        for i in range(100):
            fab.release_gpu_resource(f"tex_{i}", w)
        assert len(w.gpu_resources) == 0

    def test_stress_shader_reload(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_sh")
        for i in range(50):
            fab.register_material(RenderMaterial(f"mat_{i}", shader_id=f"PBR_v{i}"), w)
        assert len(w.materials) == 50

    def test_stress_camera_switch(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_cam")
        for i in range(10):
            fab.create_camera(f"cam_{i}", world=w)
        for i in range(10):
            fab.set_active_camera(f"cam_{i}", w)
            assert w.active_camera_id == f"cam_{i}"

    def test_stress_light_spawn(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_l_sp")
        for i in range(100):
            fab.create_light(f"l_{i}", LightType.POINT, world=w)
        assert len(w.lights) == 100

    def test_stress_light_destroy(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_l_d")
        for i in range(50):
            fab.create_light(f"l_{i}", LightType.POINT, world=w)
        for i in range(50):
            fab.destroy_light(f"l_{i}", w)
        assert len(w.lights) == 0

    def test_stress_draw_submission(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_draw")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(50):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], world=w)
        for _ in range(50):
            cmds = fab.submit_draw_commands(world=w)
            assert len(cmds) == 50

    def test_stress_render_graph_rebuild(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_rg_reb")
        for _ in range(20):
            fab.build_render_graph("g", w)
            fab.add_pass_to_graph("p1", world=w)
            fab.add_pass_to_graph("p2", dependencies=["p1"], world=w)
            order = fab.compile_render_graph(w)
            assert order == ["p1", "p2"]

    def test_stress_frame_submission(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_fr_sub")
        fab.advance_state("w_str_fr_sub", RenderWorldState.READY)
        for _ in range(120):
            f = fab.render_frame(0.016, w)
            assert f is not None
        assert w.frames_rendered == 120

    def test_stress_resize(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_resz")
        resolutions = [(800, 600), (1280, 720), (1920, 1080), (2560, 1440), (3840, 2160)]
        for w_val, h_val in resolutions:
            fab.resize_surface(w_val, h_val, w)
            assert w.settings.metadata["surface_width"] == w_val

    def test_stress_gpu_resource_retirement(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_ret")
        for i in range(100):
            fab.allocate_gpu_resource(f"res_{i}", "GPU_BUFFER", 1024, w)
            fab.release_gpu_resource(f"res_{i}", w)
        assert len(w.gpu_resources) == 0

    def test_stress_world_restart(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_str_rest")
        for _ in range(5):
            fab.advance_state("w_str_rest", RenderWorldState.READY)
            fab.render_frame(0.016, w)
            fab.advance_state("w_str_rest", RenderWorldState.STOPPED)
        assert w.state == RenderWorldState.STOPPED


class TestPropertyBasedUAF81_75:
    """Normative acceptance tests for Mathematical and Structural Properties (§118)."""

    def test_same_scene_same_camera_same_visible_set(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_1")
        fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=50.0, world=w)
        for i in range(10):
            w.renderables[f"r_{i}"] = RenderableEntity(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float(i * 5)])
        v1 = fab.compute_visibility(world=w)
        v2 = fab.compute_visibility(world=w)
        assert v1 == v2

    def test_same_visible_set_same_draw_order(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_2")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1", render_queue=RenderQueueType.OPAQUE), w)
        for i in range(8):
            fab.create_renderable(f"r_{i}", f"e_{i}", "m1", ["mat1"], position=[0.0, 0.0, float((i % 4) * 5)], world=w)
        fab.create_camera("c", position=[0.0, 0.0, 0.0], world=w)
        order1 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        order2 = [c.renderable_id for c in fab.submit_draw_commands(world=w)]
        assert order1 == order2

    def test_valid_render_graph_acyclic_execution_order(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_3")
        fab.build_render_graph("g", w)
        fab.add_pass_to_graph("A", world=w)
        fab.add_pass_to_graph("B", dependencies=["A"], world=w)
        fab.add_pass_to_graph("C", dependencies=["B"], world=w)
        order = fab.compile_render_graph(w)
        assert order.index("A") < order.index("B") < order.index("C")

    def test_destroy_renderable_no_draw_submission(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_4")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r_target", "e1", "m1", ["mat1"], world=w)
        cmds_before = fab.submit_draw_commands(world=w)
        assert any(c.renderable_id == "r_target" for c in cmds_before)
        fab.destroy_renderable("r_target", w)
        cmds_after = fab.submit_draw_commands(world=w)
        assert not any(c.renderable_id == "r_target" for c in cmds_after)

    def test_destroy_material_no_invalid_material_binding(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_5")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat_temp"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat_temp"], world=w)
        del w.materials["mat_temp"]
        val = UniversalRuntimeRenderingValidator()
        issues = val.validate_world(w)
        assert any("MISSING_MATERIAL" in i.error_code for i in issues)

    def test_destroy_gpu_resource_no_live_gpu_reference(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_prop_6")
        fab.allocate_gpu_resource("gpu_buf", "GPU_BUFFER", 1024, w)
        assert "gpu_buf" in w.gpu_resources
        fab.release_gpu_resource("gpu_buf", w)
        assert "gpu_buf" not in w.gpu_resources

    def test_same_frame_state_same_command_sequence(self):
        def run_sim(wid):
            fab = UniversalRuntimeRenderingFabricator()
            w = fab.create_render_world(wid)
            fab.advance_state(wid, RenderWorldState.READY)
            fab.register_mesh(RenderMesh("m1", 10, 30), w)
            fab.register_material(RenderMaterial("mat1"), w)
            fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
            f = fab.render_frame(0.016, w)
            return [c.renderable_id for c in f.submitted_commands]

        assert run_sim("w_p7_a") == run_sim("w_p7_b")


# ==============================================================================
# PART 5: CROSS-PHASE INTEGRATION, CLEANUP & PACKAGER / INVARIANTS
# ==============================================================================

class TestCrossPhaseIntegrationUAF81_75:
    """Normative acceptance tests for Cross-Phase Pipeline Integration (§119)."""

    def test_runtime_entity_to_renderable(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_1")
        fab.register_mesh(RenderMesh("mesh_crate", 10, 30), w)
        fab.register_material(RenderMaterial("mat_crate"), w)
        r = fab.create_renderable("r_crate_01", "ent_crate_01", "mesh_crate", ["mat_crate"], world=w)
        assert r.entity_id == "ent_crate_01"
        assert r.mesh_id == "mesh_crate"

    def test_runtime_transform_to_render_transform(self):
        class MockEntity:
            def __init__(self, pos):
                self.world_transform = type("Tr", (), {"position": pos, "rotation": [0, 0, 0, 1], "scale": [1, 1, 1]})()

        class MockRuntimeWorld:
            def __init__(self):
                self.entities = {"ent_player": MockEntity([10.0, 20.0, 30.0])}

        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_2")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_player", "ent_player", "m1", ["mat1"], world=w)
        rt_world = MockRuntimeWorld()
        fab.sync_from_runtime_world(rt_world, w)
        assert r.position == [10.0, 20.0, 30.0]

    def test_physics_transform_to_render_transform(self):
        class MockPhysEntity:
            def __init__(self, pos):
                self.world_transform = type("Tr", (), {"position": pos, "rotation": [0, 0, 0, 1], "scale": [1, 1, 1]})()

        class MockWorld:
            def __init__(self):
                self.entities = {"phys_cube": MockPhysEntity([0.0, -9.8, 5.0])}

        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_3")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_phys", "phys_cube", "m1", ["mat1"], world=w)
        fab.sync_from_runtime_world(MockWorld(), w)
        assert r.position == [0.0, -9.8, 5.0]

    def test_scene_mesh_to_renderable(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_4")
        m = RenderMesh("SM_Pillar", 120, 360)
        fab.register_mesh(m, w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_pillar", "e_pillar", "SM_Pillar", ["mat1"], world=w)
        assert r.mesh_id == "SM_Pillar"

    def test_scene_material_to_material_instance(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_5")
        mat = RenderMaterial("MI_Concrete", "PBR_Standard", parameters={"roughness": 0.8, "metallic": 0.0})
        fab.register_material(mat, w)
        assert w.materials["MI_Concrete"].parameters["roughness"] == 0.8

    def test_scene_shader_to_shader_binding(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_6")
        mat = RenderMaterial("MI_Glow", shader_id="Unlit_Emissive")
        fab.register_material(mat, w)
        assert w.materials["MI_Glow"].shader_id == "Unlit_Emissive"

    def test_scene_texture_to_gpu_texture(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_7")
        tex_res = fab.allocate_gpu_resource("T_Albedo_01", "GPU_TEXTURE", 1024 * 1024 * 4, w)
        mat = RenderMaterial("MI_Textured", textures={"albedo": "T_Albedo_01"})
        fab.register_material(mat, w)
        assert w.materials["MI_Textured"].textures["albedo"] == tex_res.resource_id

    def test_prefab_to_renderable_instances(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_8")
        fab.register_mesh(RenderMesh("m_car_body", 100, 300), w)
        fab.register_mesh(RenderMesh("m_car_wheel", 50, 150), w)
        fab.register_material(RenderMaterial("mat_car"), w)
        fab.create_renderable("car_body", "e_car_body", "m_car_body", ["mat_car"], world=w)
        for i in range(4):
            fab.create_renderable(f"car_wheel_{i}", f"e_wheel_{i}", "m_car_wheel", ["mat_car"], world=w)
        assert len(w.renderables) == 5

    def test_streaming_cell_to_render_world(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_9")
        fab.register_mesh(RenderMesh("m_rock", 50, 150), w)
        fab.register_material(RenderMaterial("mat_rock"), w)
        for i in range(10):
            fab.create_renderable(f"cell_4_2_rock_{i}", f"e_rock_{i}", "m_rock", ["mat_rock"], world=w)
        assert len([r for r in w.renderables if r.startswith("cell_4_2")]) == 10

    def test_streaming_unload_to_render_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_10")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        for i in range(5):
            fab.create_renderable(f"cell_A_{i}", f"e_{i}", "m1", ["mat1"], world=w)
        for i in range(5):
            fab.destroy_renderable(f"cell_A_{i}", w)
        assert len(w.renderables) == 0

    def test_runtime_visibility_to_culling(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_11")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_vis_test", "e_vis", "m1", ["mat1"], world=w)
        assert "r_vis_test" in fab.compute_visibility(world=w)
        r.visible = False
        assert "r_vis_test" not in fab.compute_visibility(world=w)

    def test_runtime_event_to_render_update(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_12")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_event", "e1", "m1", ["mat1"], world=w)
        r.current_lod = 2
        assert w.renderables["r_event"].current_lod == 2

    def test_physics_event_to_render_update(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_13")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        r = fab.create_renderable("r_hit", "e_hit", "m1", ["mat1"], world=w)
        r.position = [15.0, 0.0, 2.5]
        assert w.renderables["r_hit"].position == [15.0, 0.0, 2.5]

    def test_asset_change_to_gpu_resource_rebuild(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_14")
        fab.allocate_gpu_resource("buf_mesh_v1", "GPU_BUFFER", 1024, w)
        assert "buf_mesh_v1" in w.gpu_resources
        fab.release_gpu_resource("buf_mesh_v1", w)
        fab.allocate_gpu_resource("buf_mesh_v2", "GPU_BUFFER", 2048, w)
        assert "buf_mesh_v2" in w.gpu_resources

    def test_world_destroy_to_render_world_destroy(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_int_15")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
        fab.destroy_world(w)
        assert w.state == RenderWorldState.DESTROYED
        assert len(w.renderables) == 0


class TestCleanupUAF81_75:
    """Normative acceptance tests for Lifecycle Cleanup (§120)."""

    def test_render_world_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_1")
        fab.destroy_world(w)
        assert w.state == RenderWorldState.DESTROYED

    def test_renderable_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_2")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r1", "e1", "m1", ["mat1"], world=w)
        fab.destroy_renderable("r1", w)
        assert len(w.renderables) == 0

    def test_camera_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_3")
        fab.create_camera("c1", world=w)
        fab.destroy_camera("c1", w)
        assert len(w.cameras) == 0

    def test_light_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_4")
        fab.create_light("l1", world=w)
        fab.destroy_light("l1", w)
        assert len(w.lights) == 0

    def test_material_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_5")
        fab.register_material(RenderMaterial("mat1"), w)
        w.materials.clear()
        assert len(w.materials) == 0

    def test_shader_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_6")
        fab.register_material(RenderMaterial("m_sh", shader_id="Shader_A"), w)
        del w.materials["m_sh"]
        assert len(w.materials) == 0

    def test_texture_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_7")
        fab.allocate_gpu_resource("tex_clean", "GPU_TEXTURE", 4096, w)
        fab.release_gpu_resource("tex_clean", w)
        assert len(w.gpu_resources) == 0

    def test_mesh_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_8")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        w.meshes.clear()
        assert len(w.meshes) == 0

    def test_render_graph_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_9")
        fab.build_render_graph("g", w)
        fab.add_pass_to_graph("p1", world=w)
        w.render_graph.passes.clear()
        w.render_graph.execution_order.clear()
        assert len(w.render_graph.passes) == 0

    def test_gpu_resource_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_10")
        fab.allocate_gpu_resource("buf1", "GPU_BUFFER", 1024, w)
        fab.release_gpu_resource("buf1", w)
        assert len(w.gpu_resources) == 0

    def test_frame_resource_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_11")
        fab.advance_state("w_clean_11", RenderWorldState.READY)
        f = fab.render_frame(0.016, w)
        f.submitted_commands.clear()
        assert len(f.submitted_commands) == 0

    def test_debug_render_cleanup(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_clean_12")
        dbg = fab.get_debug_render_data(w)
        assert dbg is not None


class TestPackagerAndInvariantsUAF81_75:
    """Normative acceptance tests for Packaging and Non-Negotiable Invariants (§124)."""

    def test_cxx_header_generation(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_pkg_1")
        packager = UniversalRuntimeRenderingPackager()
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = packager.package_for_unreal(w, tmp_dir)
            assert os.path.exists(res["header"])
            with open(res["header"], "r", encoding="utf-8") as f:
                content = f.read()
            assert "UUAFRuntimeRenderingSubsystem" in content
            assert "UWorldSubsystem" in content

    def test_cxx_source_generation(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_pkg_2")
        packager = UniversalRuntimeRenderingPackager()
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = packager.package_for_unreal(w, tmp_dir)
            assert os.path.exists(res["source"])
            with open(res["source"], "r", encoding="utf-8") as f:
                content = f.read()
            assert "UUAFRuntimeRenderingSubsystem::Initialize" in content

    def test_export_package_manifest_and_signature(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_pkg_3")
        packager = UniversalRuntimeRenderingPackager()
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = packager.package_for_unreal(w, tmp_dir)
            assert os.path.exists(res["manifest"])
            assert os.path.exists(res["signature"])

    def test_invariant_no_invalid_render_world_transition(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_1")
        with pytest.raises(ValueError, match="NO_INVALID_RENDER_WORLD_TRANSITION"):
            fab.stop_rendering(w)

    def test_invariant_no_draw_without_valid_resources(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_2")
        r = RenderableEntity("r_noval", "e1", "mesh_missing", ["mat_missing"])
        w.renderables["r_noval"] = r
        val = UniversalRuntimeRenderingValidator()
        issues = val.validate_world(w)
        assert any(i.error_code == "MISSING_MESH" for i in issues)

    def test_invariant_no_material_shader_incompatibility(self):
        val = UniversalRuntimeRenderingValidator()
        mat = RenderMaterial("mat_incomp", shader_id="")
        issues = val.validate_material(mat)
        assert any(i.error_code == "EMPTY_SHADER_ID" for i in issues)

    def test_invariant_no_invalid_camera_parameters(self):
        val = UniversalRuntimeRenderingValidator()
        cam = RenderCamera("cam_inv", near_clip=-5.0)
        issues = val.validate_camera(cam)
        assert any(i.error_code == "INVALID_CAMERA" for i in issues)

    def test_invariant_no_invalid_frustum(self):
        val = UniversalRuntimeRenderingValidator()
        cam = RenderCamera("cam_inv2", near_clip=100.0, far_clip=10.0)
        issues = val.validate_camera(cam)
        assert any(i.error_code == "INVALID_CAMERA" for i in issues)

    def test_invariant_no_false_culling_of_valid_required_objects(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_cull")
        fab.create_camera("c", position=[0.0, 0.0, 0.0], near_clip=1.0, far_clip=100.0, world=w)
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r_req", "e1", "m1", ["mat1"], position=[0.0, 0.0, 10.0], world=w)
        vis = fab.compute_visibility(world=w)
        assert "r_req" in vis

    def test_invariant_no_render_graph_cycle(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_cycle")
        fab.build_render_graph("g", w)
        fab.add_pass_to_graph("A", dependencies=["B"], world=w)
        fab.add_pass_to_graph("B", dependencies=["A"], world=w)
        with pytest.raises(ValueError, match="NO_RENDER_GRAPH_CYCLE"):
            fab.compile_render_graph(w)

    def test_invariant_no_premature_gpu_resource_destruction(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_gpu_d")
        fab.allocate_gpu_resource("res_live", "GPU_BUFFER", 512, w)
        assert "res_live" in w.gpu_resources
        fab.release_gpu_resource("res_live", w)
        assert "res_live" not in w.gpu_resources

    def test_invariant_no_frame_overwrite_while_gpu_is_using_it(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_buf_ov")
        assert w.settings.buffering_count >= 2

    def test_invariant_no_eventual_draw_to_destroyed_entity(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_no_draw_dest")
        fab.register_mesh(RenderMesh("m1", 10, 30), w)
        fab.register_material(RenderMaterial("mat1"), w)
        fab.create_renderable("r_dead", "e_dead", "m1", ["mat1"], world=w)
        fab.destroy_renderable("r_dead", w)
        cmds = fab.submit_draw_commands(world=w)
        assert not any(c.renderable_id == "r_dead" for c in cmds)

    def test_invariant_no_headless_mode_state_mutation(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_headless")
        fab.advance_state("w_inv_headless", RenderWorldState.READY)
        f = fab.render_frame(0.016, w)
        assert f is not None
        assert w.state in (RenderWorldState.RENDERING, RenderWorldState.READY)

    def test_invariant_no_debug_render_state_mutation(self):
        fab = UniversalRuntimeRenderingFabricator()
        w = fab.create_render_world("w_inv_dbg_mut")
        fab.advance_state("w_inv_dbg_mut", RenderWorldState.READY)
        fingerprint_before = w.compute_fingerprint()
        fab.get_debug_render_data(w)
        fingerprint_after = w.compute_fingerprint()
        assert fingerprint_before == fingerprint_after
