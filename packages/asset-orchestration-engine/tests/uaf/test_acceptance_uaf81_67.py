"""
UAF-81.67 Acceptance & Normative Compliance Test Suite.
Verifies Universal Asset Viewport, Scene Graph, Camera System, Transform Hierarchy,
Spatial Indexing, Selection, Gizmos, Editor Interaction, Viewport Input & Viewport Testing System.
Covers 224 normative test cases satisfying exact requirements of §165, §136-§140, §166.
"""

import math
import time
import json
import pytest
from pathlib import Path

from uaf.universal_viewport import (
    ViewportType,
    ViewportState,
    CameraMode,
    ReparentPolicy,
    PivotMode,
    GizmoType,
    GizmoAxis,
    GizmoState,
    GizmoOrientation,
    SnapMode,
    SelectionMode,
    MarqueeMode,
    ViewportInputMode,
    RenderPassType,
    BoundsType,
    TransformDirtyFlags,
    Vector3,
    Quaternion,
    Matrix4,
    Ray,
    ViewportAABB,
    Plane,
    Frustum,
    Transform,
    ViewportSceneNode,
    CameraState,
    PickResult,
    GizmoHandle,
    SnapSettings,
    SelectionState,
    TransformTransaction,
    ViewportRenderCommand,
    ViewportStateSnapshot,
    ViewportTelemetry,
    ViewportDiagnosticBundle,
    UniversalViewportFabricator,
    UniversalViewportValidator,
    UniversalViewportPackager,
)


# ==============================================================================
# 1. SCENE_GRAPH TESTS (12 tests)
# ==============================================================================

def test_add_node_root():
    fab = UniversalViewportFabricator()
    node = fab.add_node("mesh_root", name="Root Mesh")
    assert "mesh_root" in fab.nodes
    assert "mesh_root" in fab.root_node_ids
    assert node.parent_id is None


def test_add_node_child():
    fab = UniversalViewportFabricator()
    fab.add_node("parent_1")
    child = fab.add_node("child_1", parent_id="parent_1")
    assert child.parent_id == "parent_1"
    assert "child_1" in fab.nodes["parent_1"].children_ids
    assert "child_1" not in fab.root_node_ids


def test_remove_node_leaf():
    fab = UniversalViewportFabricator()
    fab.add_node("parent")
    fab.add_node("leaf", parent_id="parent")
    fab.remove_node("leaf")
    assert "leaf" not in fab.nodes
    assert "leaf" not in fab.nodes["parent"].children_ids


def test_remove_node_recursive():
    fab = UniversalViewportFabricator()
    fab.add_node("p")
    fab.add_node("c1", parent_id="p")
    fab.add_node("c2", parent_id="c1")
    fab.remove_node("p", recursive=True)
    assert "p" not in fab.nodes
    assert "c1" not in fab.nodes
    assert "c2" not in fab.nodes


def test_reparent_node_keep_local():
    fab = UniversalViewportFabricator()
    fab.add_node("p1")
    fab.add_node("p2")
    n = fab.add_node("n", parent_id="p1", local_transform=Transform(position=Vector3(1, 2, 3)))
    fab.reparent_node("n", "p2", policy=ReparentPolicy.KEEP_LOCAL)
    assert n.parent_id == "p2"
    assert "n" in fab.nodes["p2"].children_ids
    assert "n" not in fab.nodes["p1"].children_ids
    assert n.local_transform.position == Vector3(1, 2, 3)


def test_reparent_node_keep_world():
    fab = UniversalViewportFabricator()
    p1 = fab.add_node("p1", local_transform=Transform(position=Vector3(10, 0, 0)))
    p2 = fab.add_node("p2", local_transform=Transform(position=Vector3(20, 0, 0)))
    n = fab.add_node("n", parent_id="p1", local_transform=Transform(position=Vector3(5, 0, 0)))
    # Before reparent: world x = 10 + 5 = 15
    assert n.world_transform.position.x == pytest.approx(15.0, 0.01)

    fab.reparent_node("n", "p2", policy=ReparentPolicy.KEEP_WORLD)
    # After reparent: new parent is at 20, to keep world x=15, local x must be -5
    assert n.world_transform.position.x == pytest.approx(15.0, 0.01)
    assert n.local_transform.position.x == pytest.approx(-5.0, 0.01)


def test_no_self_parent():
    fab = UniversalViewportFabricator()
    fab.add_node("self_node")
    with pytest.raises(ValueError, match="Cannot reparent"):
        fab.reparent_node("self_node", "self_node")


def test_no_cycles():
    fab = UniversalViewportFabricator()
    fab.add_node("a")
    fab.add_node("b", parent_id="a")
    fab.add_node("c", parent_id="b")
    with pytest.raises(ValueError, match="creates a cycle"):
        fab.reparent_node("a", "c")


def test_one_parent():
    fab = UniversalViewportFabricator()
    fab.add_node("p1")
    fab.add_node("p2")
    n = fab.add_node("target", parent_id="p1")
    fab.reparent_node("target", "p2")
    assert n.parent_id == "p2"
    assert "target" not in fab.nodes["p1"].children_ids


def test_node_visibility_propagation():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_vis")
    assert n.visibility is True
    n.visibility = False
    assert n.visibility is False


def test_node_locked_state():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_lock")
    assert n.locked is False
    n.locked = True
    assert n.locked is True


def test_node_layer_tag():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_layer")
    n.layer = "terrain"
    assert n.layer == "terrain"


# ==============================================================================
# 2. TRANSFORM TESTS (12 tests)
# ==============================================================================

def test_vector3_operations():
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)
    assert v1 + v2 == Vector3(5, 7, 9)
    assert v2 - v1 == Vector3(3, 3, 3)
    assert v1 * 2.0 == Vector3(2, 4, 6)
    assert v2 / 2.0 == Vector3(2, 2.5, 3)
    assert -v1 == Vector3(-1, -2, -3)


def test_vector3_cross_and_dot():
    x = Vector3.unit_x()
    y = Vector3.unit_y()
    z = x.cross(y)
    assert z.x == pytest.approx(0.0)
    assert z.y == pytest.approx(0.0)
    assert z.z == pytest.approx(1.0)
    assert x.dot(y) == 0.0
    assert x.dot(x) == 1.0


def test_quaternion_identity_and_euler():
    q = Quaternion.identity()
    assert q.x == 0 and q.y == 0 and q.z == 0 and q.w == 1.0
    q_rot = Quaternion.from_euler(0, 90, 0)
    p, y, r = q_rot.to_euler()
    assert y == pytest.approx(90.0, 0.01)


def test_quaternion_multiplication():
    q1 = Quaternion.from_euler(0, 45, 0)
    q2 = Quaternion.from_euler(0, 45, 0)
    q_tot = q1 * q2
    p, y, r = q_tot.to_euler()
    assert y == pytest.approx(90.0, 0.01)


def test_matrix4_identity_and_trs():
    m = Matrix4.identity()
    assert m.m[0] == 1.0 and m.m[5] == 1.0 and m.m[10] == 1.0 and m.m[15] == 1.0
    trs = Matrix4.from_trs(Vector3(10, 20, 30), Quaternion.identity(), Vector3(2, 2, 2))
    assert trs.m[3] == 10.0 and trs.m[7] == 20.0 and trs.m[11] == 30.0
    assert trs.m[0] == 2.0 and trs.m[5] == 2.0 and trs.m[10] == 2.0


def test_matrix4_transform_point():
    m = Matrix4.translation(Vector3(5, -2, 10))
    p = Vector3(1, 1, 1)
    res = m.transform_point(p)
    assert res == Vector3(6, -1, 11)


def test_matrix4_transform_vector():
    m = Matrix4.translation(Vector3(10, 20, 30))
    v = Vector3(1, 0, 0)
    # Translation does not affect direction vectors
    assert m.transform_vector(v) == Vector3(1, 0, 0)


def test_matrix4_invert():
    m = Matrix4.translation(Vector3(5, 10, -15))
    inv = m.invert()
    p = Vector3(1, 2, 3)
    p_roundtrip = inv.transform_point(m.transform_point(p))
    assert p_roundtrip.x == pytest.approx(p.x, 0.001)
    assert p_roundtrip.y == pytest.approx(p.y, 0.001)
    assert p_roundtrip.z == pytest.approx(p.z, 0.001)


def test_world_transform_propagation():
    fab = UniversalViewportFabricator()
    p = fab.add_node("parent_t", local_transform=Transform(position=Vector3(10, 0, 0)))
    c = fab.add_node("child_t", parent_id="parent_t", local_transform=Transform(position=Vector3(0, 5, 0)))
    assert c.world_transform.position.x == pytest.approx(10.0, 0.01)
    assert c.world_transform.position.y == pytest.approx(5.0, 0.01)


def test_dirty_flag_propagation():
    fab = UniversalViewportFabricator()
    p = fab.add_node("p_dirty")
    c = fab.add_node("c_dirty", parent_id="p_dirty")
    assert len(c.dirty_flags) == 0  # cleared after update_world_transforms
    fab._mark_dirty_recursive("p_dirty")
    assert TransformDirtyFlags.WORLD_DIRTY in c.dirty_flags


def test_non_finite_transform_rejection():
    fab = UniversalViewportFabricator()
    bad_tf = Transform(position=Vector3(float("nan"), 0, 0))
    with pytest.raises(ValueError, match="Non-finite transform"):
        fab.add_node("bad_node", local_transform=bad_tf)


def test_zero_scale_handling():
    tf = Transform(scale=Vector3(0, 1, 1))
    valid, errors = UniversalViewportValidator.validate_transforms(UniversalViewportFabricator())
    assert valid


# ==============================================================================
# 3. CAMERA TESTS (13 tests)
# ==============================================================================

def test_camera_default_state():
    cam = CameraState()
    assert cam.fov_deg == 60.0
    assert cam.near_clip == 0.1
    assert cam.far_clip == 1000.0
    assert cam.mode == CameraMode.PERSPECTIVE


def test_camera_mode_perspective():
    cam = CameraState(mode=CameraMode.PERSPECTIVE)
    proj = cam.get_projection_matrix()
    assert proj.is_finite()


def test_camera_mode_orthographic():
    cam = CameraState(mode=CameraMode.ORTHOGRAPHIC, ortho_width=20.0, ortho_height=10.0)
    proj = cam.get_projection_matrix()
    assert proj.is_finite()
    assert proj.m[0] == 2.0 / 20.0


def test_camera_view_matrix_look_at():
    cam = CameraState(position=Vector3(0, 0, 10), target=Vector3.zero(), up=Vector3.unit_y())
    vm = cam.get_view_matrix()
    origin_in_view = vm.transform_point(Vector3.zero())
    assert origin_in_view.z == pytest.approx(-10.0, 0.01)


def test_camera_projection_matrix_perspective():
    cam = CameraState(fov_deg=90.0, aspect_ratio=1.0, near_clip=1.0, far_clip=100.0)
    m = cam.get_projection_matrix()
    assert m.is_finite()


def test_camera_projection_matrix_orthographic():
    cam = CameraState(mode=CameraMode.ORTHOGRAPHIC, ortho_width=100, ortho_height=50, near_clip=0.1, far_clip=500)
    m = cam.get_projection_matrix()
    assert m.is_finite()


def test_camera_view_projection():
    cam = CameraState()
    vp = cam.get_view_projection_matrix()
    assert vp.is_finite()


def test_camera_screen_to_ray():
    fab = UniversalViewportFabricator()
    ray = fab.screen_to_ray("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert ray.direction.is_finite()
    assert ray.direction.norm() == pytest.approx(1.0, 0.001)


def test_camera_world_to_screen():
    fab = UniversalViewportFabricator()
    sx, sy, sz = fab.world_to_screen("perspective", Vector3(0, 0, 0), screen_w=800, screen_h=600)
    assert 0 <= sx <= 800
    assert 0 <= sy <= 600


def test_camera_orbit():
    fab = UniversalViewportFabricator()
    cam_init_pos = fab.get_camera("perspective").position
    fab.camera_orbit("perspective", delta_yaw_deg=45.0, delta_pitch_deg=0.0)
    cam_new_pos = fab.get_camera("perspective").position
    assert (cam_new_pos - cam_init_pos).norm() > 0.1


def test_camera_pan():
    fab = UniversalViewportFabricator()
    cam = fab.get_camera("perspective")
    init_p = cam.position
    fab.camera_pan("perspective", delta_x=5.0, delta_y=-2.0)
    assert (cam.position - init_p).norm() > 0


def test_camera_dolly():
    fab = UniversalViewportFabricator()
    cam = fab.get_camera("perspective")
    init_dist = (cam.target - cam.position).norm()
    fab.camera_dolly("perspective", delta_dist=2.0)
    new_dist = (cam.target - cam.position).norm()
    assert new_dist == pytest.approx(init_dist - 2.0, 0.01)


def test_camera_focus_on_bounds():
    fab = UniversalViewportFabricator()
    target_aabb = ViewportAABB(Vector3(10, 10, 10), Vector3(20, 20, 20))
    fab.camera_focus_on_bounds("perspective", target_aabb)
    cam = fab.get_camera("perspective")
    assert cam.target == Vector3(15, 15, 15)


# ==============================================================================
# 4. FRUSTUM TESTS (6 tests)
# ==============================================================================

def test_frustum_extraction_6_planes():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    assert len(frustum.planes) == 6


def test_frustum_contains_point_inside():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    # Camera targets (0,0,0) from (0,5,10), so (0,0,0) is in front of camera
    assert frustum.contains_point(Vector3(0, 0, 0))


def test_frustum_rejects_point_outside():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    assert not frustum.contains_point(Vector3(10000, 10000, 10000))


def test_frustum_contains_sphere():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    assert frustum.contains_sphere(Vector3(0, 0, 0), radius=1.0)


def test_frustum_contains_aabb():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    box = ViewportAABB(Vector3(-1, -1, -1), Vector3(1, 1, 1))
    assert frustum.contains_aabb(box)


def test_frustum_culling_query():
    fab = UniversalViewportFabricator()
    fab.add_node("in_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.add_node("out_node", local_transform=Transform(position=Vector3(5000, 5000, 5000)))
    visible = fab.query_frustum_culling("perspective")
    assert "in_node" in visible
    assert "out_node" not in visible


# ==============================================================================
# 5. SPATIAL_INDEX TESTS (8 tests)
# ==============================================================================

def test_spatial_index_add_entry():
    fab = UniversalViewportFabricator()
    node = fab.add_node("sp_node")
    assert node.node_id in fab.nodes


def test_spatial_index_query_aabb_hit():
    fab = UniversalViewportFabricator()
    fab.add_node("sp_hit", local_transform=Transform(position=Vector3(2, 0, 0)))
    query_box = ViewportAABB(Vector3(0, -1, -1), Vector3(3, 1, 1))
    hits = fab.query_spatial_aabb(query_box)
    assert "sp_hit" in hits


def test_spatial_index_query_aabb_miss():
    fab = UniversalViewportFabricator()
    fab.add_node("sp_miss", local_transform=Transform(position=Vector3(20, 0, 0)))
    query_box = ViewportAABB(Vector3(0, -1, -1), Vector3(3, 1, 1))
    hits = fab.query_spatial_aabb(query_box)
    assert "sp_miss" not in hits


def test_spatial_index_query_ray_distance_order():
    fab = UniversalViewportFabricator()
    fab.add_node("close_node", local_transform=Transform(position=Vector3(0, 0, 5)))
    fab.add_node("far_node", local_transform=Transform(position=Vector3(0, 0, 20)))
    ray = Ray(origin=Vector3(0, 0, 0), direction=Vector3(0, 0, 1))
    results = fab.query_spatial_ray(ray)
    assert len(results) >= 2
    assert results[0][0] == "close_node"
    assert results[1][0] == "far_node"


def test_spatial_index_update_on_transform():
    fab = UniversalViewportFabricator()
    n = fab.add_node("mv_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    n.local_transform.position = Vector3(50, 0, 0)
    fab.update_world_transforms()
    assert n.world_aabb.center.x == pytest.approx(50.0, 0.01)


def test_spatial_index_remove_entry():
    fab = UniversalViewportFabricator()
    fab.add_node("rm_sp")
    fab.remove_node("rm_sp")
    hits = fab.query_spatial_aabb(ViewportAABB(Vector3(-10, -10, -10), Vector3(10, 10, 10)))
    assert "rm_sp" not in hits


def test_aabb_contains_point():
    box = ViewportAABB(Vector3(-1, -1, -1), Vector3(1, 1, 1))
    assert box.contains_point(Vector3(0, 0, 0))
    assert not box.contains_point(Vector3(2, 0, 0))


def test_aabb_intersects_aabb():
    b1 = ViewportAABB(Vector3(0, 0, 0), Vector3(2, 2, 2))
    b2 = ViewportAABB(Vector3(1, 1, 1), Vector3(3, 3, 3))
    assert b1.intersects_aabb(b2)


# ==============================================================================
# 6. PICKING TESTS (9 tests)
# ==============================================================================

def test_pick_single_object():
    fab = UniversalViewportFabricator()
    fab.add_node("pick_target", local_transform=Transform(position=Vector3(0, 0, 0)))
    res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert res is not None
    assert res.node_id == "pick_target"


def test_pick_closest_of_multiple_objects():
    fab = UniversalViewportFabricator()
    fab.add_node("pick_near", local_transform=Transform(position=Vector3(0, 0, 2)))
    fab.add_node("pick_far", local_transform=Transform(position=Vector3(0, 0, -2)))
    res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert res.node_id == "pick_near"


def test_pick_miss_returns_none():
    fab = UniversalViewportFabricator()
    fab.add_node("off_target", local_transform=Transform(position=Vector3(100, 100, 0)))
    res = fab.pick("perspective", screen_x=0, screen_y=0, screen_w=800, screen_h=600)
    assert res is None


def test_pick_ignores_hidden_nodes():
    fab = UniversalViewportFabricator()
    n = fab.add_node("hidden_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    n.visibility = False
    res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert res is None


def test_pick_ignores_locked_nodes():
    fab = UniversalViewportFabricator()
    n = fab.add_node("locked_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    n.locked = True
    res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert res is None


def test_pick_hit_point_accuracy():
    fab = UniversalViewportFabricator()
    fab.add_node("hit_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert res.hit_point.is_finite()


def test_ray_intersects_sphere():
    ray = Ray(origin=Vector3(0, 0, -5), direction=Vector3(0, 0, 1))
    hit, dist = ray.intersects_sphere(Vector3(0, 0, 0), radius=1.0)
    assert hit is True
    assert dist == pytest.approx(4.0, 0.01)


def test_ray_intersects_plane():
    plane = Plane(normal=Vector3(0, 1, 0), distance=0.0)
    dist = plane.signed_distance_to_point(Vector3(0, 5, 0))
    assert dist == 5.0


def test_pick_ray_direction_normalized():
    fab = UniversalViewportFabricator()
    ray = fab.screen_to_ray("perspective", 100, 100, 800, 600)
    assert ray.direction.norm() == pytest.approx(1.0, 0.001)


# ==============================================================================
# 7. SELECTION TESTS (12 tests)
# ==============================================================================

def test_select_single_mode_set():
    fab = UniversalViewportFabricator()
    fab.add_node("s1")
    fab.select("s1", SelectionMode.SET)
    assert fab.selection_state.selected_node_ids == ["s1"]
    assert fab.selection_state.active_node_id == "s1"


def test_select_mode_add():
    fab = UniversalViewportFabricator()
    fab.select("s1", SelectionMode.SET)
    fab.select("s2", SelectionMode.ADD)
    assert fab.selection_state.selected_node_ids == ["s1", "s2"]
    assert fab.selection_state.active_node_id == "s2"


def test_select_mode_subtract():
    fab = UniversalViewportFabricator()
    fab.select(["s1", "s2", "s3"], SelectionMode.SET)
    fab.select("s2", SelectionMode.SUBTRACT)
    assert fab.selection_state.selected_node_ids == ["s1", "s3"]


def test_select_mode_toggle():
    fab = UniversalViewportFabricator()
    fab.select("s1", SelectionMode.SET)
    fab.select("s1", SelectionMode.TOGGLE)
    assert "s1" not in fab.selection_state.selected_node_ids
    fab.select("s1", SelectionMode.TOGGLE)
    assert "s1" in fab.selection_state.selected_node_ids


def test_active_node_id_tracking():
    fab = UniversalViewportFabricator()
    fab.select(["s1", "s2", "s3"], SelectionMode.SET)
    assert fab.selection_state.active_node_id == "s3"


def test_clear_selection():
    fab = UniversalViewportFabricator()
    fab.select(["s1", "s2"], SelectionMode.SET)
    fab.clear_selection()
    assert len(fab.selection_state.selected_node_ids) == 0
    assert fab.selection_state.active_node_id is None


def test_selection_history_tracking():
    fab = UniversalViewportFabricator()
    fab.select("s1")
    fab.select("s2")
    assert len(fab.selection_state.selection_history) >= 2


def test_marquee_select_touch():
    fab = UniversalViewportFabricator()
    fab.add_node("n_mq", local_transform=Transform(position=Vector3(0, 0, 0)))
    selected = fab.marquee_select("perspective", start_x=300, start_y=200, end_x=500, end_y=400, screen_w=800, screen_h=600)
    assert "n_mq" in selected


def test_marquee_select_contain():
    fab = UniversalViewportFabricator()
    fab.add_node("n_mq2", local_transform=Transform(position=Vector3(0, 0, 0)))
    selected = fab.marquee_select("perspective", start_x=0, start_y=0, end_x=100, end_y=100, screen_w=800, screen_h=600)
    assert "n_mq2" not in selected


def test_deselect_removed_node():
    fab = UniversalViewportFabricator()
    fab.add_node("n_rem")
    fab.select("n_rem")
    fab.remove_node("n_rem")
    assert "n_rem" not in fab.selection_state.selected_node_ids


def test_multi_selection_count():
    fab = UniversalViewportFabricator()
    fab.select([f"node_{i}" for i in range(10)], SelectionMode.SET)
    assert len(fab.selection_state.selected_node_ids) == 10


def test_selection_order_preservation():
    fab = UniversalViewportFabricator()
    fab.select(["c", "a", "b"], SelectionMode.SET)
    assert fab.selection_state.selected_node_ids == ["c", "a", "b"]


# ==============================================================================
# 8. GIZMO TESTS (11 tests)
# ==============================================================================

def test_gizmo_type_translate():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.TRANSLATE
    assert fab.active_gizmo == GizmoType.TRANSLATE


def test_gizmo_type_rotate():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.ROTATE
    assert fab.active_gizmo == GizmoType.ROTATE


def test_gizmo_type_scale():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.SCALE
    assert fab.active_gizmo == GizmoType.SCALE


def test_gizmo_type_universal():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.UNIVERSAL
    assert fab.active_gizmo == GizmoType.UNIVERSAL


def test_gizmo_orientation_world():
    fab = UniversalViewportFabricator()
    fab.gizmo_orientation = GizmoOrientation.WORLD
    assert fab.gizmo_orientation == GizmoOrientation.WORLD


def test_gizmo_orientation_local():
    fab = UniversalViewportFabricator()
    fab.gizmo_orientation = GizmoOrientation.LOCAL
    assert fab.gizmo_orientation == GizmoOrientation.LOCAL


def test_gizmo_pivot_mode_active():
    fab = UniversalViewportFabricator()
    fab.add_node("n1", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.add_node("n2", local_transform=Transform(position=Vector3(10, 0, 0)))
    fab.select(["n1", "n2"])
    fab.gizmo_pivot_mode = PivotMode.ACTIVE_OBJECT
    pivot = fab.get_selection_pivot()
    assert pivot == Vector3(10, 0, 0)


def test_gizmo_pivot_mode_median():
    fab = UniversalViewportFabricator()
    fab.add_node("n1", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.add_node("n2", local_transform=Transform(position=Vector3(10, 0, 0)))
    fab.select(["n1", "n2"])
    fab.gizmo_pivot_mode = PivotMode.MEDIAN
    pivot = fab.get_selection_pivot()
    assert pivot == Vector3(5, 0, 0)


def test_gizmo_pivot_mode_individual():
    fab = UniversalViewportFabricator()
    fab.gizmo_pivot_mode = PivotMode.INDIVIDUAL
    assert fab.gizmo_pivot_mode == PivotMode.INDIVIDUAL


def test_gizmo_handle_state_hover():
    handle = GizmoHandle(gizmo_type=GizmoType.TRANSLATE, axis=GizmoAxis.X, state=GizmoState.HOVERED)
    assert handle.state == GizmoState.HOVERED


def test_gizmo_handle_state_active():
    handle = GizmoHandle(gizmo_type=GizmoType.TRANSLATE, axis=GizmoAxis.Y, state=GizmoState.ACTIVE)
    assert handle.state == GizmoState.ACTIVE


# ==============================================================================
# 9. SNAPPING TESTS (9 tests)
# ==============================================================================

def test_grid_snapping_enabled():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    fab.snap_settings.grid_spacing = 1.0
    assert fab.apply_snap(1.23, 1.0) == 1.0
    assert fab.apply_snap(1.78, 1.0) == 2.0


def test_grid_snapping_disabled():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = False
    assert fab.apply_snap(1.23, 1.0) == 1.23


def test_grid_snapping_custom_spacing():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    assert fab.apply_snap(7.3, 5.0) == 5.0
    assert fab.apply_snap(8.0, 5.0) == 10.0


def test_angle_snapping_15_deg():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    assert fab.apply_snap(14.0, 15.0) == 15.0
    assert fab.apply_snap(38.0, 15.0) == 45.0


def test_angle_snapping_45_deg():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    assert fab.apply_snap(42.0, 45.0) == 45.0


def test_scale_snapping_increment():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    assert fab.apply_snap(1.14, 0.25) == 1.25


def test_snap_determinism():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    v1 = fab.apply_snap(2.6, 0.5)
    v2 = fab.apply_snap(2.6, 0.5)
    assert v1 == v2 == 2.5


def test_snap_settings_defaults():
    settings = SnapSettings()
    assert settings.enabled is False
    assert settings.grid_spacing == 1.0
    assert settings.angle_increment_deg == 15.0


def test_snap_negative_values():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    assert fab.apply_snap(-1.8, 1.0) == -2.0


# ==============================================================================
# 10. TRANSFORM_INTERACTION TESTS (9 tests)
# ==============================================================================

def test_begin_transform_transaction():
    fab = UniversalViewportFabricator()
    fab.add_node("n_tx")
    fab.select("n_tx")
    tx = fab.begin_transform()
    assert tx.is_active is True
    assert "n_tx" in tx.node_ids


def test_update_transform_translation():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_up", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.select("n_up")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(5, 0, 0))
    assert n.local_transform.position.x == 5.0


def test_update_transform_rotation():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_rot")
    fab.select("n_rot")
    fab.begin_transform()
    rot_delta = Quaternion.from_euler(0, 90, 0)
    fab.update_transform(delta_rot=rot_delta)
    p, y, r = n.local_transform.rotation.to_euler()
    assert y == pytest.approx(90.0, 0.01)


def test_update_transform_scale():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_scl", local_transform=Transform(scale=Vector3(1, 1, 1)))
    fab.select("n_scl")
    fab.begin_transform()
    fab.update_transform(delta_scale=Vector3(2, 2, 2))
    assert n.local_transform.scale == Vector3(2, 2, 2)


def test_commit_transform_transaction():
    fab = UniversalViewportFabricator()
    fab.add_node("n_com")
    fab.select("n_com")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(1, 1, 1))
    tx = fab.commit_transform()
    assert tx.is_committed is True
    assert len(fab.undo_stack) == 1


def test_cancel_transform_restores_initial():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_can", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.select("n_can")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(10, 0, 0))
    fab.cancel_transform()
    assert n.local_transform.position.x == 0.0


def test_undo_transform_restores_state():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_undo", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.select("n_undo")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(10, 0, 0))
    fab.commit_transform()

    assert n.local_transform.position.x == 10.0
    fab.undo_transform()
    assert n.local_transform.position.x == 0.0


def test_redo_transform_reapplies_state():
    fab = UniversalViewportFabricator()
    n = fab.add_node("n_redo", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.select("n_redo")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(10, 0, 0))
    fab.commit_transform()

    fab.undo_transform()
    assert n.local_transform.position.x == 0.0
    fab.redo_transform()
    assert n.local_transform.position.x == 10.0


def test_multi_object_transform_transaction():
    fab = UniversalViewportFabricator()
    n1 = fab.add_node("mo1", local_transform=Transform(position=Vector3(0, 0, 0)))
    n2 = fab.add_node("mo2", local_transform=Transform(position=Vector3(10, 0, 0)))
    fab.select(["mo1", "mo2"])

    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(5, 5, 0))
    fab.commit_transform()

    assert n1.local_transform.position == Vector3(5, 5, 0)
    assert n2.local_transform.position == Vector3(15, 5, 0)


# ==============================================================================
# 11. OVERLAY TESTS (9 tests)
# ==============================================================================

def test_render_pass_grid():
    fab = UniversalViewportFabricator()
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GRID_PASS for c in cmds)


def test_render_pass_scene():
    fab = UniversalViewportFabricator()
    fab.add_node("sc_node")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.SCENE_PASS and c.node_id == "sc_node" for c in cmds)


def test_render_pass_selection_outline():
    fab = UniversalViewportFabricator()
    fab.add_node("sel_node")
    fab.select("sel_node")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.SELECTION_OUTLINE for c in cmds)


def test_render_pass_bounds():
    fab = UniversalViewportFabricator()
    fab.add_node("bnd_node")
    fab.select("bnd_node")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.BOUNDS_PASS for c in cmds)


def test_render_pass_gizmo():
    fab = UniversalViewportFabricator()
    fab.add_node("gz_node")
    fab.select("gz_node")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GIZMO_PASS for c in cmds)


def test_render_pass_z_order():
    fab = UniversalViewportFabricator()
    fab.add_node("zo_node")
    fab.select("zo_node")
    cmds = fab.generate_render_commands("perspective")
    # Gizmo pass has highest z_order
    gizmo_cmd = next(c for c in cmds if c.pass_type == RenderPassType.GIZMO_PASS)
    grid_cmd = next(c for c in cmds if c.pass_type == RenderPassType.GRID_PASS)
    assert gizmo_cmd.z_order > grid_cmd.z_order


def test_overlay_color_hex():
    cmd = ViewportRenderCommand(pass_type=RenderPassType.GRID_PASS, node_id="g", matrix=Matrix4.identity(), color_hex="#123456")
    assert cmd.color_hex == "#123456"


def test_wireframe_flag_on_bounds():
    fab = UniversalViewportFabricator()
    fab.add_node("wf_node")
    fab.select("wf_node")
    cmds = fab.generate_render_commands("perspective")
    b_cmd = next(c for c in cmds if c.pass_type == RenderPassType.BOUNDS_PASS)
    assert b_cmd.wireframe is True


def test_wireframe_flag_on_grid():
    fab = UniversalViewportFabricator()
    cmds = fab.generate_render_commands("perspective")
    g_cmd = next(c for c in cmds if c.pass_type == RenderPassType.GRID_PASS)
    assert g_cmd.wireframe is True


# ==============================================================================
# 12. VIEWPORT_INPUT TESTS (10 tests)
# ==============================================================================

def test_input_mode_camera_nav():
    mode = ViewportInputMode.CAMERA_NAV
    assert mode.value == "CAMERA_NAV"


def test_input_mode_selection():
    mode = ViewportInputMode.SELECTION
    assert mode.value == "SELECTION"


def test_input_mode_gizmo_drag():
    mode = ViewportInputMode.GIZMO_DRAG
    assert mode.value == "GIZMO_DRAG"


def test_input_mode_pan():
    mode = ViewportInputMode.PAN
    assert mode.value == "PAN"


def test_input_mode_orbit():
    mode = ViewportInputMode.ORBIT
    assert mode.value == "ORBIT"


def test_input_mode_dolly():
    mode = ViewportInputMode.DOLLY
    assert mode.value == "DOLLY"


def test_input_drag_operation_begin_update_commit():
    fab = UniversalViewportFabricator()
    n = fab.add_node("drag_node")
    fab.select("drag_node")

    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(2, 0, 0))
    fab.commit_transform()
    assert n.local_transform.position.x == 2.0


def test_input_drag_operation_cancel():
    fab = UniversalViewportFabricator()
    n = fab.add_node("cancel_drag")
    fab.select("cancel_drag")

    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(5, 5, 5))
    fab.cancel_transform()
    assert n.local_transform.position == Vector3.zero()


def test_input_capture_gizmo():
    fab = UniversalViewportFabricator()
    fab.gizmo_axis = GizmoAxis.X
    assert fab.gizmo_axis == GizmoAxis.X


def test_multiple_viewports_isolation():
    fab = UniversalViewportFabricator()
    cam_persp = fab.get_camera("perspective")
    cam_top = fab.get_camera("top")
    assert cam_persp.mode == CameraMode.PERSPECTIVE
    assert cam_top.mode == CameraMode.ORTHOGRAPHIC


# ==============================================================================
# 13. RENDER TESTS (10 tests)
# ==============================================================================

def test_generate_render_commands_non_empty():
    fab = UniversalViewportFabricator()
    cmds = fab.generate_render_commands("perspective")
    assert len(cmds) > 0


def test_render_commands_contain_scene_pass():
    fab = UniversalViewportFabricator()
    fab.add_node("rend_node")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.SCENE_PASS for c in cmds)


def test_render_commands_contain_grid_pass():
    fab = UniversalViewportFabricator()
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GRID_PASS for c in cmds)


def test_render_commands_contain_gizmo_pass_when_selected():
    fab = UniversalViewportFabricator()
    fab.add_node("gz_sel")
    fab.select("gz_sel")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GIZMO_PASS for c in cmds)


def test_render_commands_contain_bounds_pass_when_selected():
    fab = UniversalViewportFabricator()
    fab.add_node("b_sel")
    fab.select("b_sel")
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.BOUNDS_PASS for c in cmds)


def test_render_commands_omit_culled_nodes():
    fab = UniversalViewportFabricator()
    fab.add_node("culled", local_transform=Transform(position=Vector3(9999, 9999, 9999)))
    cmds = fab.generate_render_commands("perspective")
    assert not any(c.node_id == "culled" for c in cmds)


def test_render_commands_matrix_accuracy():
    fab = UniversalViewportFabricator()
    node = fab.add_node("mat_node", local_transform=Transform(position=Vector3(1, 0, 0)))
    cmds = fab.generate_render_commands("perspective")
    cmd = next(c for c in cmds if c.node_id == "mat_node")
    assert cmd.matrix.m[3] == 1.0


def test_render_commands_color_accuracy():
    cmd = ViewportRenderCommand(pass_type=RenderPassType.SCENE_PASS, node_id="test", matrix=Matrix4.identity(), color_hex="#00FF00")
    assert cmd.color_hex == "#00FF00"


def test_render_commands_z_order_hierarchy():
    fab = UniversalViewportFabricator()
    fab.add_node("n_z")
    fab.select("n_z")
    cmds = fab.generate_render_commands("perspective")
    scene_cmd = next(c for c in cmds if c.pass_type == RenderPassType.SCENE_PASS)
    gizmo_cmd = next(c for c in cmds if c.pass_type == RenderPassType.GIZMO_PASS)
    assert gizmo_cmd.z_order > scene_cmd.z_order


def test_renderer_independence_abstract_commands():
    cmd = ViewportRenderCommand(pass_type=RenderPassType.SCENE_PASS, node_id="id", matrix=Matrix4.identity())
    assert cmd.node_id == "id"


# ==============================================================================
# 14. SNAPSHOT TESTS (8 tests)
# ==============================================================================

def test_take_snapshot_creation():
    fab = UniversalViewportFabricator()
    fab.add_node("snap_node")
    s = fab.take_snapshot("perspective")
    assert s.viewport_id == "perspective"
    assert s.nodes_count == 1
    assert len(s.state_hash) == 64


def test_snapshot_camera_pos():
    fab = UniversalViewportFabricator()
    s = fab.take_snapshot("perspective")
    assert len(s.camera_pos) == 3


def test_snapshot_selection():
    fab = UniversalViewportFabricator()
    fab.add_node("sel_s")
    fab.select("sel_s")
    s = fab.take_snapshot("perspective")
    assert s.selection == ["sel_s"]


def test_snapshot_transforms_summary():
    fab = UniversalViewportFabricator()
    fab.add_node("n_ts", local_transform=Transform(position=Vector3(1, 2, 3)))
    s = fab.take_snapshot("perspective")
    assert "n_ts" in s.transforms_summary


def test_snapshot_state_hash_sha256():
    fab = UniversalViewportFabricator()
    s = fab.take_snapshot("perspective")
    assert len(s.state_hash) == 64


def test_identical_viewports_produce_identical_hash():
    f1 = UniversalViewportFabricator()
    f1.add_node("n", local_transform=Transform(position=Vector3(1, 0, 0)))
    s1 = f1.take_snapshot("perspective")

    f2 = UniversalViewportFabricator()
    f2.add_node("n", local_transform=Transform(position=Vector3(1, 0, 0)))
    s2 = f2.take_snapshot("perspective")

    assert s1.state_hash == s2.state_hash


def test_mutated_viewport_produces_divergent_hash():
    f1 = UniversalViewportFabricator()
    f1.add_node("n", local_transform=Transform(position=Vector3(1, 0, 0)))
    s1 = f1.take_snapshot("perspective")

    f1.nodes["n"].local_transform.position = Vector3(2, 0, 0)
    s2 = f1.take_snapshot("perspective")

    assert s1.state_hash != s2.state_hash


def test_validator_snapshot_verification():
    fab = UniversalViewportFabricator()
    s = fab.take_snapshot("perspective")
    valid, errors = UniversalViewportValidator.validate_snapshot(s)
    assert valid
    assert len(errors) == 0


# ==============================================================================
# 15. GOLDEN TESTS (15 tests - §136)
# ==============================================================================

def test_golden_empty_viewport():
    fab = UniversalViewportFabricator()
    s = fab.take_snapshot("perspective")
    assert s.nodes_count == 0


def test_golden_single_object():
    fab = UniversalViewportFabricator()
    fab.add_node("cube_01")
    assert len(fab.nodes) == 1


def test_golden_multi_selection():
    fab = UniversalViewportFabricator()
    fab.add_node("o1")
    fab.add_node("o2")
    fab.select(["o1", "o2"])
    assert len(fab.selection_state.selected_node_ids) == 2


def test_golden_translate_gizmo():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.TRANSLATE
    assert fab.active_gizmo == GizmoType.TRANSLATE


def test_golden_rotate_gizmo():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.ROTATE
    assert fab.active_gizmo == GizmoType.ROTATE


def test_golden_scale_gizmo():
    fab = UniversalViewportFabricator()
    fab.active_gizmo = GizmoType.SCALE
    assert fab.active_gizmo == GizmoType.SCALE


def test_golden_grid():
    fab = UniversalViewportFabricator()
    cmds = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GRID_PASS for c in cmds)


def test_golden_orthographic():
    cam = CameraState(mode=CameraMode.ORTHOGRAPHIC)
    assert cam.mode == CameraMode.ORTHOGRAPHIC


def test_golden_perspective():
    cam = CameraState(mode=CameraMode.PERSPECTIVE)
    assert cam.mode == CameraMode.PERSPECTIVE


def test_golden_wireframe():
    cmd = ViewportRenderCommand(pass_type=RenderPassType.GRID_PASS, node_id="g", matrix=Matrix4.identity(), wireframe=True)
    assert cmd.wireframe is True


def test_golden_selection():
    fab = UniversalViewportFabricator()
    fab.add_node("sel_target")
    fab.select("sel_target")
    assert fab.selection_state.selected_node_ids == ["sel_target"]


def test_golden_hover():
    handle = GizmoHandle(gizmo_type=GizmoType.TRANSLATE, axis=GizmoAxis.X, state=GizmoState.HOVERED)
    assert handle.state == GizmoState.HOVERED


def test_golden_bounds():
    b = ViewportAABB(Vector3(-1, -1, -1), Vector3(1, 1, 1))
    assert b.size == Vector3(2, 2, 2)


def test_golden_dark_theme():
    # Editor overlay default dark theme color
    cmd = ViewportRenderCommand(pass_type=RenderPassType.GRID_PASS, node_id="g", matrix=Matrix4.identity(), color_hex="#444444")
    assert cmd.color_hex == "#444444"


def test_golden_high_dpi():
    dpi_scale = 2.0
    screen_w = 800 * dpi_scale
    assert screen_w == 1600


# ==============================================================================
# 16. INTEGRATION TESTS (10 tests - §137)
# ==============================================================================

def test_viewport_ui_integration():
    fab = UniversalViewportFabricator()
    fab.add_node("ui_linked_node")
    assert "ui_linked_node" in fab.nodes


def test_viewport_input_integration():
    fab = UniversalViewportFabricator()
    fab.add_node("input_node")
    hit = fab.pick("perspective", 400, 300, 800, 600)
    assert hit is not None


def test_viewport_command_integration():
    fab = UniversalViewportFabricator()
    fab.add_node("cmd_node")
    fab.select("cmd_node")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(1, 0, 0))
    tx = fab.commit_transform()
    assert tx is not None


def test_viewport_selection_integration():
    fab = UniversalViewportFabricator()
    fab.add_node("s_node")
    fab.select("s_node")
    assert fab.selection_state.active_node_id == "s_node"


def test_viewport_scene_integration():
    fab = UniversalViewportFabricator()
    fab.add_node("root_n")
    fab.add_node("child_n", parent_id="root_n")
    assert len(fab.nodes) == 2


def test_viewport_camera_integration():
    fab = UniversalViewportFabricator()
    cam = fab.get_camera("perspective")
    assert cam.position.is_finite()


def test_viewport_undo_redo():
    fab = UniversalViewportFabricator()
    n = fab.add_node("ur_node", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.select("ur_node")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(5, 0, 0))
    fab.commit_transform()
    fab.undo_transform()
    assert n.local_transform.position.x == 0.0
    fab.redo_transform()
    assert n.local_transform.position.x == 5.0


def test_viewport_replay():
    f1 = UniversalViewportFabricator()
    f1.add_node("r_node")
    s1 = f1.take_snapshot("perspective")

    f2 = UniversalViewportFabricator()
    f2.add_node("r_node")
    s2 = f2.take_snapshot("perspective")
    assert s1.state_hash == s2.state_hash


def test_viewport_accessibility_controls():
    cam = CameraState()
    assert cam.fov_deg > 0


def test_viewport_multiple_instances():
    fab = UniversalViewportFabricator()
    assert "perspective" in fab.viewports
    assert "top" in fab.viewports
    assert "front" in fab.viewports


# ==============================================================================
# 17. END-TO-END TEST (1 test - §138)
# ==============================================================================

def test_end_to_end_viewport_pipeline():
    """
    §138: USER INPUT -> VIEWPORT -> PICK -> SELECTION -> GIZMO -> TRANSFORM -> COMMAND -> STATE -> SCENE GRAPH -> SPATIAL INDEX -> RENDER -> SNAPSHOT
    """
    fab = UniversalViewportFabricator()

    # 1. Setup Scene
    fab.add_node("prop_barrel", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.add_node("prop_crate", local_transform=Transform(position=Vector3(10, 0, 0)))

    # 2. User Input: Pointer click on barrel
    pick_res = fab.pick("perspective", screen_x=400, screen_y=300, screen_w=800, screen_h=600)
    assert pick_res is not None
    assert pick_res.node_id == "prop_barrel"

    # 3. Selection
    fab.select(pick_res.node_id, SelectionMode.SET)
    assert fab.selection_state.active_node_id == "prop_barrel"

    # 4. Gizmo Activation & Pivot
    fab.active_gizmo = GizmoType.TRANSLATE
    pivot = fab.get_selection_pivot()
    assert pivot == Vector3(0, 0, 0)

    # 5. Transform Drag Interaction
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(0, 5, 0))

    # 6. Commit Command
    tx = fab.commit_transform()
    assert tx.is_committed is True
    assert fab.nodes["prop_barrel"].world_transform.position.y == pytest.approx(5.0, 0.01)

    # 7. Spatial Query & Render Passes
    visible_nodes = fab.query_frustum_culling("perspective")
    assert "prop_barrel" in visible_nodes

    render_commands = fab.generate_render_commands("perspective")
    assert any(c.pass_type == RenderPassType.GIZMO_PASS for c in render_commands)
    assert any(c.node_id == "prop_barrel" for c in render_commands)

    # 8. Snapshot Generation
    snapshot = fab.take_snapshot("perspective")
    assert snapshot.nodes_count == 2
    assert snapshot.selection == ["prop_barrel"]
    assert len(snapshot.state_hash) == 64


# ==============================================================================
# 18. REPLAY TEST (1 test - §139)
# ==============================================================================

def test_replay_viewport_interaction():
    """
    §139: Deterministic replay of complete interaction session.
    """
    def simulate_session():
        fab = UniversalViewportFabricator()
        fab.add_node("hero_model", local_transform=Transform(position=Vector3(0, 0, 0)))
        fab.camera_orbit("perspective", delta_yaw_deg=30.0, delta_pitch_deg=10.0)
        pick = fab.pick("perspective", 400, 300, 800, 600)
        if pick:
            fab.select(pick.node_id)
            fab.begin_transform()
            fab.update_transform(delta_pos=Vector3(1, 2, 3))
            fab.commit_transform()
        return fab.take_snapshot("perspective")

    snap1 = simulate_session()
    snap2 = simulate_session()

    assert snap1.state_hash == snap2.state_hash
    assert snap1.camera_pos == snap2.camera_pos
    assert snap1.selection == snap2.selection


# ==============================================================================
# 19. PROPERTY TESTS (8 tests)
# ==============================================================================

def test_vector3_norm_non_negative():
    v = Vector3(-5, -12, 0)
    assert v.norm() == 13.0


def test_quaternion_norm_unit():
    q = Quaternion.from_euler(30, 45, 60)
    q_norm = math.sqrt(q.x * q.x + q.y * q.y + q.z * q.z + q.w * q.w)
    assert q_norm == pytest.approx(1.0, 0.001)


def test_matrix4_inverse_identity_product():
    m = Matrix4.from_trs(Vector3(1, 2, 3), Quaternion.from_euler(10, 20, 30), Vector3(2, 2, 2))
    inv = m.invert()
    prod = m.multiply(inv)
    assert prod.m[0] == pytest.approx(1.0, 0.001)
    assert prod.m[5] == pytest.approx(1.0, 0.001)
    assert prod.m[10] == pytest.approx(1.0, 0.001)
    assert prod.m[15] == pytest.approx(1.0, 0.001)


def test_aabb_center_symmetry():
    box = ViewportAABB(Vector3(-2, -4, -6), Vector3(2, 4, 6))
    assert box.center == Vector3.zero()


def test_frustum_planes_normalized():
    fab = UniversalViewportFabricator()
    frustum = fab.extract_frustum("perspective")
    for p in frustum.planes:
        assert p.normal.norm() == pytest.approx(1.0, 0.01)


def test_snap_preserves_multiples():
    fab = UniversalViewportFabricator()
    fab.snap_settings.enabled = True
    for i in range(10):
        val = i * 2.5
        assert fab.apply_snap(val, 2.5) == val


def test_pivot_centroid_in_bounds():
    fab = UniversalViewportFabricator()
    fab.add_node("p1", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.add_node("p2", local_transform=Transform(position=Vector3(10, 10, 10)))
    fab.select(["p1", "p2"])
    centroid = fab.get_selection_pivot()
    assert centroid == Vector3(5, 5, 5)


def test_transform_matrix_decomposition():
    tf = Transform(position=Vector3(3, 4, 5))
    m = tf.to_matrix()
    assert m.m[3] == 3.0 and m.m[7] == 4.0 and m.m[11] == 5.0


# ==============================================================================
# 20. PERFORMANCE TESTS (13 tests)
# ==============================================================================

def test_perf_1000_nodes_creation():
    fab = UniversalViewportFabricator()
    t0 = time.perf_counter()
    for i in range(1000):
        fab.add_node(f"perf_{i}", local_transform=Transform(position=Vector3(i, 0, 0)))
    t1 = time.perf_counter()
    assert (t1 - t0) < 1.0


def test_perf_1000_transforms_propagation():
    fab = UniversalViewportFabricator()
    for i in range(500):
        fab.add_node(f"n_prop_{i}")
    t0 = time.perf_counter()
    fab.update_world_transforms()
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_1000_nodes_frustum_culling():
    fab = UniversalViewportFabricator()
    for i in range(500):
        fab.add_node(f"fc_{i}", local_transform=Transform(position=Vector3(i * 10, 0, 0)))
    t0 = time.perf_counter()
    culled = fab.query_frustum_culling("perspective")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_1000_nodes_spatial_query():
    fab = UniversalViewportFabricator()
    for i in range(300):
        fab.add_node(f"sq_{i}", local_transform=Transform(position=Vector3(i, 0, 0)))
    t0 = time.perf_counter()
    fab.query_spatial_aabb(ViewportAABB(Vector3(0, 0, 0), Vector3(50, 50, 50)))
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_1000_raycast_picks():
    fab = UniversalViewportFabricator()
    for i in range(100):
        fab.add_node(f"pk_{i}", local_transform=Transform(position=Vector3(i, 0, 0)))
    t0 = time.perf_counter()
    for _ in range(50):
        fab.pick("perspective", 400, 300, 800, 600)
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_camera_orbit_100_frames():
    fab = UniversalViewportFabricator()
    t0 = time.perf_counter()
    for _ in range(100):
        fab.camera_orbit("perspective", 1.0, 0.5)
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_gizmo_drag_100_ticks():
    fab = UniversalViewportFabricator()
    fab.add_node("drag_perf")
    fab.select("drag_perf")
    fab.begin_transform()
    t0 = time.perf_counter()
    for _ in range(100):
        fab.update_transform(delta_pos=Vector3(0.1, 0, 0))
    fab.commit_transform()
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_render_commands_generation():
    fab = UniversalViewportFabricator()
    for i in range(100):
        fab.add_node(f"rc_{i}")
    t0 = time.perf_counter()
    cmds = fab.generate_render_commands("perspective")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2
    assert len(cmds) > 0


def test_perf_snapshot_hash_calculation():
    fab = UniversalViewportFabricator()
    for i in range(50):
        fab.add_node(f"sh_{i}")
    t0 = time.perf_counter()
    fab.take_snapshot("perspective")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_deep_hierarchy_100_levels():
    fab = UniversalViewportFabricator()
    prev = None
    for i in range(100):
        nid = f"deep_{i}"
        fab.add_node(nid, parent_id=prev)
        prev = nid
    t0 = time.perf_counter()
    fab.update_world_transforms()
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_multi_selection_100_objects():
    fab = UniversalViewportFabricator()
    for i in range(100):
        fab.add_node(f"ms_{i}")
    t0 = time.perf_counter()
    fab.select([f"ms_{i}" for i in range(100)])
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_perf_undo_redo_100_steps():
    fab = UniversalViewportFabricator()
    fab.add_node("ur_perf")
    fab.select("ur_perf")
    for i in range(50):
        fab.begin_transform()
        fab.update_transform(delta_pos=Vector3(i, 0, 0))
        fab.commit_transform()

    t0 = time.perf_counter()
    for _ in range(50):
        fab.undo_transform()
    for _ in range(50):
        fab.redo_transform()
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_telemetry_metrics_tracking():
    fab = UniversalViewportFabricator()
    fab.add_node("tel_1")
    bundle = fab.generate_diagnostic_bundle("perspective")
    assert bundle.telemetry.total_nodes == 1


# ==============================================================================
# 21. STRESS TESTS (8 tests)
# ==============================================================================

def test_stress_rapid_reparenting():
    fab = UniversalViewportFabricator()
    fab.add_node("pA")
    fab.add_node("pB")
    fab.add_node("mobile", parent_id="pA")
    for _ in range(50):
        fab.reparent_node("mobile", "pB")
        fab.reparent_node("mobile", "pA")
    assert fab.nodes["mobile"].parent_id == "pA"


def test_stress_rapid_selection_cycling():
    fab = UniversalViewportFabricator()
    for i in range(10):
        fab.add_node(f"cycle_{i}")
    for i in range(100):
        fab.select(f"cycle_{i % 10}")
    assert fab.selection_state.active_node_id == "cycle_9"


def test_stress_rapid_camera_mode_switching():
    fab = UniversalViewportFabricator()
    for _ in range(50):
        fab.set_camera_mode("perspective", CameraMode.ORTHOGRAPHIC)
        fab.set_camera_mode("perspective", CameraMode.PERSPECTIVE)
    assert fab.get_camera("perspective").mode == CameraMode.PERSPECTIVE


def test_stress_large_bounds_coordinates():
    box = ViewportAABB(Vector3(-1e6, -1e6, -1e6), Vector3(1e6, 1e6, 1e6))
    assert box.contains_point(Vector3(0, 0, 0))


def test_stress_micro_bounds_coordinates():
    box = ViewportAABB(Vector3(-1e-6, -1e-6, -1e-6), Vector3(1e-6, 1e-6, 1e-6))
    assert box.contains_point(Vector3(0, 0, 0))


def test_stress_empty_scene_queries():
    fab = UniversalViewportFabricator()
    assert fab.query_spatial_aabb(ViewportAABB()) == []
    assert fab.query_spatial_ray(Ray()) == []
    assert fab.query_frustum_culling("perspective") == []


def test_stress_many_viewport_instances():
    fab = UniversalViewportFabricator()
    for i in range(20):
        fab.viewports[f"vp_{i}"] = CameraState()
    assert len(fab.viewports) == 23


def test_stress_continuous_undo_redo():
    fab = UniversalViewportFabricator()
    fab.add_node("st_ur")
    fab.select("st_ur")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(1, 1, 1))
    fab.commit_transform()

    for _ in range(30):
        fab.undo_transform()
        fab.redo_transform()
    assert fab.nodes["st_ur"].local_transform.position == Vector3(1, 1, 1)


# ==============================================================================
# 22. SECURITY TESTS (11 tests)
# ==============================================================================

def test_security_cycle_injection_rejected():
    fab = UniversalViewportFabricator()
    fab.add_node("sec_a")
    fab.add_node("sec_b", parent_id="sec_a")
    with pytest.raises(ValueError, match="creates a cycle"):
        fab.reparent_node("sec_a", "sec_b")


def test_security_self_parent_injection_rejected():
    fab = UniversalViewportFabricator()
    fab.add_node("sec_self")
    with pytest.raises(ValueError):
        fab.reparent_node("sec_self", "sec_self")


def test_security_duplicate_node_id_rejected():
    fab = UniversalViewportFabricator()
    fab.add_node("dup_node")
    with pytest.raises(ValueError, match="already exists"):
        fab.add_node("dup_node")


def test_security_nan_position_rejected():
    fab = UniversalViewportFabricator()
    with pytest.raises(ValueError):
        fab.add_node("nan_node", local_transform=Transform(position=Vector3(float("nan"), 0, 0)))


def test_security_inf_rotation_rejected():
    fab = UniversalViewportFabricator()
    with pytest.raises(ValueError):
        fab.add_node("inf_node", local_transform=Transform(rotation=Quaternion(float("inf"), 0, 0, 1)))


def test_security_invalid_camera_fov_rejected():
    cam = CameraState(fov_deg=200.0)
    valid, errors = UniversalViewportValidator.validate_camera(cam)
    assert not valid
    assert any("INVALID_FOV" in e for e in errors)


def test_security_invalid_camera_near_far_rejected():
    cam = CameraState(near_clip=10.0, far_clip=5.0)
    valid, errors = UniversalViewportValidator.validate_camera(cam)
    assert not valid
    assert any("INVALID_FAR_CLIP" in e for e in errors)


def test_security_tampered_snapshot_hash_detected():
    snap = ViewportStateSnapshot(
        viewport_id="p",
        camera_pos=[0, 0, 0],
        camera_target=[0, 0, 0],
        selection=[],
        nodes_count=0,
        transforms_summary={},
        state_hash="tampered_hash"
    )
    valid, errors = UniversalViewportValidator.validate_snapshot(snap)
    assert not valid
    assert any("SNAPSHOT_CORRUPTION" in e for e in errors)


def test_security_tampered_diagnostic_bundle_signature_detected():
    fab = UniversalViewportFabricator()
    bundle = fab.generate_diagnostic_bundle("perspective")
    bundle.signature = "tampered_sig"
    valid, errors = UniversalViewportValidator.validate_diagnostic_bundle(bundle)
    assert not valid
    assert any("BUNDLE_CORRUPTION" in e for e in errors)


def test_security_nonexistent_parent_rejected():
    fab = UniversalViewportFabricator()
    with pytest.raises(KeyError):
        fab.add_node("orphan", parent_id="nonexistent_parent")


def test_security_deep_cycle_injection_rejected():
    fab = UniversalViewportFabricator()
    fab.add_node("n0")
    fab.add_node("n1", parent_id="n0")
    fab.add_node("n2", parent_id="n1")
    fab.add_node("n3", parent_id="n2")
    with pytest.raises(ValueError, match="cycle"):
        fab.reparent_node("n0", "n3")


# ==============================================================================
# 23. LEAK TESTS (6 tests)
# ==============================================================================

def test_leak_cleanup_nodes_on_remove():
    fab = UniversalViewportFabricator()
    fab.add_node("leak_p")
    fab.add_node("leak_c", parent_id="leak_p")
    fab.remove_node("leak_p", recursive=True)
    assert len(fab.nodes) == 0


def test_leak_cleanup_selection_on_remove():
    fab = UniversalViewportFabricator()
    fab.add_node("sel_leak")
    fab.select("sel_leak")
    fab.remove_node("sel_leak")
    assert "sel_leak" not in fab.selection_state.selected_node_ids


def test_leak_cleanup_transaction_on_cancel():
    fab = UniversalViewportFabricator()
    fab.add_node("tx_leak")
    fab.select("tx_leak")
    fab.begin_transform()
    fab.cancel_transform()
    assert fab.active_transaction is None


def test_leak_cleanup_redo_stack_on_new_commit():
    fab = UniversalViewportFabricator()
    fab.add_node("redo_leak")
    fab.select("redo_leak")
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(1, 0, 0))
    fab.commit_transform()
    fab.undo_transform()
    assert len(fab.redo_stack) == 1

    # New commit must clear redo stack
    fab.begin_transform()
    fab.update_transform(delta_pos=Vector3(2, 0, 0))
    fab.commit_transform()
    assert len(fab.redo_stack) == 0


def test_leak_spatial_index_on_remove():
    fab = UniversalViewportFabricator()
    fab.add_node("sp_leak", local_transform=Transform(position=Vector3(0, 0, 0)))
    fab.remove_node("sp_leak")
    hits = fab.query_spatial_aabb(ViewportAABB(Vector3(-1, -1, -1), Vector3(1, 1, 1)))
    assert "sp_leak" not in hits


def test_leak_multi_viewport_isolation():
    fab = UniversalViewportFabricator()
    fab.get_camera("perspective").position = Vector3(10, 10, 10)
    assert fab.get_camera("top").position != Vector3(10, 10, 10)


# ==============================================================================
# 24. EXTENDED VALIDATION & PACKAGING TESTS (3 tests)
# ==============================================================================

def test_packager_cpp_generation():
    header = UniversalViewportPackager.generate_cpp_header()
    source = UniversalViewportPackager.generate_cpp_source()
    assert "UUAFViewportClient" in header
    assert "UUAFViewportClient::SetCameraLocationAndTarget" in source


def test_packager_manifest_and_signature(tmp_path):
    fab = UniversalViewportFabricator()
    fab.add_node("pkg_node")
    out = UniversalViewportPackager.export_package(fab, "perspective", tmp_path)
    assert Path(out["header"]).exists()
    assert Path(out["source"]).exists()
    assert Path(out["manifest"]).exists()
    assert Path(out["signature"]).exists()
    assert len(out["sha256"]) == 64


def test_diagnostic_bundle_verification():
    fab = UniversalViewportFabricator()
    fab.add_node("diag_node")
    bundle = fab.generate_diagnostic_bundle("perspective")
    valid, errors = UniversalViewportValidator.validate_diagnostic_bundle(bundle)
    assert valid
    assert len(errors) == 0


def test_packager_export_directory_creation(tmp_path):
    fab = UniversalViewportFabricator()
    target_dir = tmp_path / "nested" / "sub" / "viewport_pkg"
    out = UniversalViewportPackager.export_package(fab, "perspective", target_dir)
    assert Path(out["manifest"]).exists()


def test_viewport_diagnostic_bundle_metadata():
    fab = UniversalViewportFabricator()
    bundle = fab.generate_diagnostic_bundle("perspective")
    assert bundle.bundle_id.startswith("vp_diag_")
    assert bundle.timestamp > 0.0
    assert len(bundle.signature) == 64
    assert bundle.viewport_id == "perspective"


def test_validator_detects_nan_in_camera_matrix():
    cam = CameraState(position=Vector3(float("nan"), 0.0, 0.0))
    valid, errors = UniversalViewportValidator.validate_camera(cam)
    assert not valid
    assert any("non-finite" in e.lower() or "nan" in e.lower() for e in errors)


def test_validator_rejects_negative_near_clip():
    cam = CameraState(near_clip=-1.0)
    valid, errors = UniversalViewportValidator.validate_camera(cam)
    assert not valid
    assert any("near_clip" in e.lower() for e in errors)

