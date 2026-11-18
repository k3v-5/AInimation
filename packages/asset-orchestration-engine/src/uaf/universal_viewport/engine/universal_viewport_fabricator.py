"""
UAF-81.67: Universal Asset Viewport Fabricator Engine.
Authoritative 3D scene graph, camera system, frustum culling, spatial indexing,
raycast picking, interactive gizmos, snapping, selection manager, transform transactions,
deterministic replay, and render passes.
"""

from __future__ import annotations
import math
import time
import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from uaf.universal_viewport.models.definition import (
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
    AABB,
    Plane,
    Frustum,
    Transform,
    SceneNode,
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
)


class UniversalViewportFabricator:
    """
    Authoritative Universal Viewport and Scene Graph Fabricator.
    Manages multi-viewport instances, scene node hierarchy, world transform propagation,
    camera projection and navigation, frustum culling, raycast picking, selection,
    gizmo manipulation with snapping, undo/redo transactions, and render passes.
    """

    def __init__(self):
        self.nodes: Dict[str, SceneNode] = {}
        self.root_node_ids: List[str] = []
        self.viewports: Dict[str, CameraState] = {
            "perspective": CameraState(mode=CameraMode.PERSPECTIVE),
            "top": CameraState(position=Vector3(0, 20, 0), target=Vector3.zero(), up=Vector3(0, 0, -1), mode=CameraMode.ORTHOGRAPHIC),
            "front": CameraState(position=Vector3(0, 0, 20), target=Vector3.zero(), up=Vector3.unit_y(), mode=CameraMode.ORTHOGRAPHIC),
        }
        self.active_viewport_id: str = "perspective"
        self.selection_state = SelectionState()
        self.snap_settings = SnapSettings()
        self.active_gizmo = GizmoType.TRANSLATE
        self.gizmo_axis = GizmoAxis.NONE
        self.gizmo_orientation = GizmoOrientation.WORLD
        self.gizmo_pivot_mode = PivotMode.MEDIAN
        self.active_transaction: Optional[TransformTransaction] = None
        self.undo_stack: List[TransformTransaction] = []
        self.redo_stack: List[TransformTransaction] = []
        self.telemetry = ViewportTelemetry()

    # --------------------------------------------------------------------------
    # Scene Graph Hierarchy & Invariants
    # --------------------------------------------------------------------------

    def add_node(
        self,
        node_id: str,
        name: str = "",
        parent_id: Optional[str] = None,
        local_transform: Optional[Transform] = None,
        local_aabb: Optional[AABB] = None
    ) -> SceneNode:
        if node_id in self.nodes:
            raise ValueError(f"SceneNode '{node_id}' already exists in scene graph.")

        if parent_id and parent_id not in self.nodes:
            raise KeyError(f"Parent node '{parent_id}' does not exist.")

        node = SceneNode(
            node_id=node_id,
            name=name or node_id,
            parent_id=parent_id,
            local_transform=local_transform or Transform(),
            local_aabb=local_aabb or AABB()
        )
        self.nodes[node_id] = node

        if parent_id:
            parent = self.nodes[parent_id]
            if node_id not in parent.children_ids:
                parent.children_ids.append(node_id)
            self._evaluate_node_transform(node_id, parent.world_matrix)
        else:
            if node_id not in self.root_node_ids:
                self.root_node_ids.append(node_id)
            self._evaluate_node_transform(node_id, Matrix4.identity())

        return node

    def remove_node(self, node_id: str, recursive: bool = True) -> None:
        if node_id not in self.nodes:
            return

        node = self.nodes[node_id]
        if recursive:
            for child_id in list(node.children_ids):
                self.remove_node(child_id, recursive=True)

        if node.parent_id and node.parent_id in self.nodes:
            parent = self.nodes[node.parent_id]
            if node_id in parent.children_ids:
                parent.children_ids.remove(node_id)
        elif node_id in self.root_node_ids:
            self.root_node_ids.remove(node_id)

        # Deselect if selected
        if node_id in self.selection_state.selected_node_ids:
            self.selection_state.selected_node_ids.remove(node_id)
            if self.selection_state.active_node_id == node_id:
                self.selection_state.active_node_id = self.selection_state.selected_node_ids[-1] if self.selection_state.selected_node_ids else None

        del self.nodes[node_id]

    def reparent_node(self, node_id: str, new_parent_id: Optional[str], policy: ReparentPolicy = ReparentPolicy.KEEP_LOCAL) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' not found.")
        if new_parent_id and new_parent_id not in self.nodes:
            raise KeyError(f"New parent '{new_parent_id}' not found.")
        if node_id == new_parent_id:
            raise ValueError(f"Cannot reparent '{node_id}' to itself.")
        if new_parent_id and self._would_create_cycle(new_parent_id, node_id):
            raise ValueError(f"Reparenting '{node_id}' to '{new_parent_id}' creates a cycle.")

        node = self.nodes[node_id]

        if policy == ReparentPolicy.KEEP_WORLD:
            # Preserve current world transform
            curr_world_m = node.world_matrix
            if new_parent_id:
                new_parent_m = self.nodes[new_parent_id].world_matrix
                new_local_m = new_parent_m.invert().multiply(curr_world_m)
            else:
                new_local_m = curr_world_m

            # Extract local TRS from new_local_m
            new_pos = Vector3(new_local_m.m[3], new_local_m.m[7], new_local_m.m[11])
            sx = Vector3(new_local_m.m[0], new_local_m.m[4], new_local_m.m[8]).norm()
            sy = Vector3(new_local_m.m[1], new_local_m.m[5], new_local_m.m[9]).norm()
            sz = Vector3(new_local_m.m[2], new_local_m.m[6], new_local_m.m[10]).norm()
            node.local_transform.position = new_pos
            node.local_transform.scale = Vector3(sx, sy, sz)

        # Remove from old parent
        if node.parent_id and node.parent_id in self.nodes:
            old_parent = self.nodes[node.parent_id]
            if node_id in old_parent.children_ids:
                old_parent.children_ids.remove(node_id)
        elif node_id in self.root_node_ids:
            self.root_node_ids.remove(node_id)

        # Attach to new parent
        node.parent_id = new_parent_id
        if new_parent_id:
            parent = self.nodes[new_parent_id]
            if node_id not in parent.children_ids:
                parent.children_ids.append(node_id)
        else:
            if node_id not in self.root_node_ids:
                self.root_node_ids.append(node_id)

        self._mark_dirty_recursive(node_id)
        self.update_world_transforms()

    def _would_create_cycle(self, parent_id: str, child_id: str) -> bool:
        curr = parent_id
        while curr:
            if curr == child_id:
                return True
            curr_node = self.nodes.get(curr)
            curr = curr_node.parent_id if curr_node else None
        return False

    def _mark_dirty_recursive(self, node_id: str) -> None:
        if node_id not in self.nodes:
            return
        node = self.nodes[node_id]
        node.dirty_flags.add(TransformDirtyFlags.WORLD_DIRTY)
        node.dirty_flags.add(TransformDirtyFlags.BOUNDS_DIRTY)
        for child_id in node.children_ids:
            self._mark_dirty_recursive(child_id)

    # --------------------------------------------------------------------------
    # Transform Propagation & Evaluation
    # --------------------------------------------------------------------------

    def update_world_transforms(self) -> None:
        for root_id in self.root_node_ids:
            self._evaluate_node_transform(root_id, Matrix4.identity())

    def _evaluate_node_transform(self, node_id: str, parent_world_matrix: Matrix4) -> None:
        node = self.nodes[node_id]
        # Validate numerical stability
        if not node.local_transform.is_finite():
            raise ValueError(f"Non-finite transform detected in node '{node_id}'.")

        local_m = node.local_transform.to_matrix()
        node.world_matrix = parent_world_matrix.multiply(local_m)

        # Decompose position and bounds
        node.world_transform.position = Vector3(node.world_matrix.m[3], node.world_matrix.m[7], node.world_matrix.m[11])
        node.world_aabb = node.local_aabb.transformed(node.world_matrix)
        node.dirty_flags.clear()

        for child_id in node.children_ids:
            self._evaluate_node_transform(child_id, node.world_matrix)

    # --------------------------------------------------------------------------
    # Camera & Projection Pipeline
    # --------------------------------------------------------------------------

    def get_camera(self, viewport_id: Optional[str] = None) -> CameraState:
        vid = viewport_id or self.active_viewport_id
        if vid not in self.viewports:
            raise KeyError(f"Viewport '{vid}' not found.")
        return self.viewports[vid]

    def set_camera_mode(self, viewport_id: str, mode: CameraMode) -> None:
        cam = self.get_camera(viewport_id)
        cam.mode = mode

    def screen_to_ray(self, viewport_id: str, screen_x: float, screen_y: float, screen_w: float, screen_h: float) -> Ray:
        cam = self.get_camera(viewport_id)
        # Map screen pixels to NDC [-1, 1]
        ndc_x = (2.0 * screen_x / screen_w) - 1.0
        ndc_y = 1.0 - (2.0 * screen_y / screen_h)

        vp_inv = cam.get_view_projection_matrix().invert()
        near_p = vp_inv.transform_point(Vector3(ndc_x, ndc_y, -1.0))
        far_p = vp_inv.transform_point(Vector3(ndc_x, ndc_y, 1.0))

        direction = (far_p - near_p).normalized()
        origin = near_p if cam.mode == CameraMode.PERSPECTIVE else cam.position
        return Ray(origin=origin, direction=direction)

    def world_to_screen(self, viewport_id: str, world_pos: Vector3, screen_w: float, screen_h: float) -> Tuple[float, float, float]:
        cam = self.get_camera(viewport_id)
        vp = cam.get_view_projection_matrix()
        clip_p = vp.transform_point(world_pos)

        sx = (clip_p.x + 1.0) * 0.5 * screen_w
        sy = (1.0 - clip_p.y) * 0.5 * screen_h
        return (sx, sy, clip_p.z)

    def camera_orbit(self, viewport_id: str, delta_yaw_deg: float, delta_pitch_deg: float) -> None:
        cam = self.get_camera(viewport_id)
        diff = cam.position - cam.target
        radius = diff.norm()
        if radius < 1e-6:
            radius = 1.0

        yaw = math.atan2(diff.x, diff.z) + math.radians(delta_yaw_deg)
        pitch = math.asin(max(-1.0, min(1.0, diff.y / radius))) + math.radians(delta_pitch_deg)
        pitch = max(-math.pi * 0.49, min(math.pi * 0.49, pitch))

        cam.position = Vector3(
            cam.target.x + radius * math.cos(pitch) * math.sin(yaw),
            cam.target.y + radius * math.sin(pitch),
            cam.target.z + radius * math.cos(pitch) * math.cos(yaw)
        )

    def camera_pan(self, viewport_id: str, delta_x: float, delta_y: float) -> None:
        cam = self.get_camera(viewport_id)
        fwd = (cam.target - cam.position).normalized()
        right = fwd.cross(cam.up).normalized()
        up = right.cross(fwd).normalized()

        offset = right * delta_x + up * delta_y
        cam.position = cam.position + offset
        cam.target = cam.target + offset

    def camera_dolly(self, viewport_id: str, delta_dist: float) -> None:
        cam = self.get_camera(viewport_id)
        fwd = (cam.target - cam.position).normalized()
        dist = (cam.target - cam.position).norm()
        new_dist = max(0.1, dist - delta_dist)
        cam.position = cam.target - fwd * new_dist

    def camera_focus_on_bounds(self, viewport_id: str, aabb: AABB) -> None:
        cam = self.get_camera(viewport_id)
        cam.target = aabb.center
        radius = aabb.extents.norm()
        dist = radius / math.sin(math.radians(cam.fov_deg * 0.5)) if radius > 0 else 5.0
        fwd = (cam.target - cam.position).normalized()
        if fwd.norm() < 1e-6:
            fwd = Vector3(0, 0, -1)
        cam.position = cam.target - fwd * max(2.0, dist * 1.5)

    # --------------------------------------------------------------------------
    # Frustum Culling & Spatial Queries
    # --------------------------------------------------------------------------

    def extract_frustum(self, viewport_id: str) -> Frustum:
        cam = self.get_camera(viewport_id)
        m = cam.get_view_projection_matrix().m

        def _make_plane(a: float, b: float, c: float, d: float) -> Plane:
            n = Vector3(a, b, c)
            length = n.norm()
            if length > 1e-9:
                return Plane(n / length, d / length)
            return Plane(n, d)

        # Row-major Gribb-Hartmann extraction
        # Row 0: m[0..3], Row 1: m[4..7], Row 2: m[8..11], Row 3: m[12..15]
        planes = [
            _make_plane(m[12] + m[0], m[13] + m[1], m[14] + m[2], m[15] + m[3]),  # Left
            _make_plane(m[12] - m[0], m[13] - m[1], m[14] - m[2], m[15] - m[3]),  # Right
            _make_plane(m[12] + m[4], m[13] + m[5], m[14] + m[6], m[15] + m[7]),  # Bottom
            _make_plane(m[12] - m[4], m[13] - m[5], m[14] - m[6], m[15] - m[7]),  # Top
            _make_plane(m[12] + m[8], m[13] + m[9], m[14] + m[10], m[15] + m[11]), # Near
            _make_plane(m[12] - m[8], m[13] - m[9], m[14] - m[10], m[15] - m[11]), # Far
        ]
        return Frustum(planes=planes)

    def query_frustum_culling(self, viewport_id: str) -> List[str]:
        frustum = self.extract_frustum(viewport_id)
        visible_nodes = []
        for node in self.nodes.values():
            if node.visibility and frustum.contains_aabb(node.world_aabb):
                visible_nodes.append(node.node_id)
        return visible_nodes

    def query_spatial_aabb(self, aabb: AABB) -> List[str]:
        return [node.node_id for node in self.nodes.values() if node.visibility and node.world_aabb.intersects_aabb(aabb)]

    def query_spatial_ray(self, ray: Ray) -> List[Tuple[str, float]]:
        results = []
        for node in self.nodes.values():
            if not node.visibility:
                continue
            hit, dist = node.world_aabb.intersects_ray(ray)
            if hit:
                results.append((node.node_id, dist))
        results.sort(key=lambda x: x[1])
        return results

    # --------------------------------------------------------------------------
    # Picking & Selection Management
    # --------------------------------------------------------------------------

    def pick(self, viewport_id: str, screen_x: float, screen_y: float, screen_w: float, screen_h: float) -> Optional[PickResult]:
        ray = self.screen_to_ray(viewport_id, screen_x, screen_y, screen_w, screen_h)
        hits = []
        for node in self.nodes.values():
            if not node.visibility or node.locked:
                continue
            hit, dist = node.world_aabb.intersects_ray(ray)
            if hit:
                hit_pos = ray.point_at(dist)
                hits.append(PickResult(node_id=node.node_id, distance=dist, hit_point=hit_pos))

        if not hits:
            return None
        hits.sort(key=lambda h: h.distance)
        return hits[0]

    def select(self, node_ids: Union[str, List[str]], mode: SelectionMode = SelectionMode.SET) -> None:
        targets = [node_ids] if isinstance(node_ids, str) else list(node_ids)
        current = list(self.selection_state.selected_node_ids)

        if mode == SelectionMode.SET:
            self.selection_state.selected_node_ids = targets
        elif mode == SelectionMode.ADD:
            for t in targets:
                if t not in current:
                    current.append(t)
            self.selection_state.selected_node_ids = current
        elif mode == SelectionMode.SUBTRACT:
            self.selection_state.selected_node_ids = [t for t in current if t not in targets]
        elif mode == SelectionMode.TOGGLE:
            for t in targets:
                if t in current:
                    current.remove(t)
                else:
                    current.append(t)
            self.selection_state.selected_node_ids = current

        self.selection_state.active_node_id = self.selection_state.selected_node_ids[-1] if self.selection_state.selected_node_ids else None
        self.selection_state.selection_history.append(list(self.selection_state.selected_node_ids))

    def clear_selection(self) -> None:
        self.selection_state.selected_node_ids.clear()
        self.selection_state.active_node_id = None

    def marquee_select(
        self,
        viewport_id: str,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        screen_w: float,
        screen_h: float,
        mode: MarqueeMode = MarqueeMode.TOUCH
    ) -> List[str]:
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)

        selected = []
        for node in self.nodes.values():
            if not node.visibility or node.locked:
                continue
            sx, sy, sz = self.world_to_screen(viewport_id, node.world_transform.position, screen_w, screen_h)
            if sz > 0 and (x1 <= sx <= x2) and (y1 <= sy <= y2):
                selected.append(node.node_id)

        self.select(selected, SelectionMode.SET)
        return selected

    # --------------------------------------------------------------------------
    # Gizmos, Snapping & Interactive Transform Transactions
    # --------------------------------------------------------------------------

    def get_selection_pivot(self) -> Vector3:
        if not self.selection_state.selected_node_ids:
            return Vector3.zero()

        if self.gizmo_pivot_mode == PivotMode.ACTIVE_OBJECT and self.selection_state.active_node_id:
            return self.nodes[self.selection_state.active_node_id].world_transform.position

        # Median center
        positions = [self.nodes[nid].world_transform.position for nid in self.selection_state.selected_node_ids if nid in self.nodes]
        if not positions:
            return Vector3.zero()
        total = Vector3.zero()
        for p in positions:
            total = total + p
        return total / float(len(positions))

    def apply_snap(self, val: float, step: float) -> float:
        if not self.snap_settings.enabled or step <= 0:
            return val
        return round(val / step) * step

    def begin_transform(self) -> TransformTransaction:
        tx_id = f"tx_{int(time.time() * 1000)}"
        initial = {nid: copy.deepcopy(self.nodes[nid].local_transform) for nid in self.selection_state.selected_node_ids if nid in self.nodes}
        current = copy.deepcopy(initial)
        tx = TransformTransaction(
            transaction_id=tx_id,
            node_ids=list(initial.keys()),
            initial_transforms=initial,
            current_transforms=current,
            is_active=True
        )
        self.active_transaction = tx
        return tx

    def update_transform(
        self,
        delta_pos: Optional[Vector3] = None,
        delta_rot: Optional[Quaternion] = None,
        delta_scale: Optional[Vector3] = None
    ) -> None:
        if not self.active_transaction or not self.active_transaction.is_active:
            return

        tx = self.active_transaction
        for nid in tx.node_ids:
            node = self.nodes[nid]
            init = tx.initial_transforms[nid]

            if delta_pos:
                dp = Vector3(
                    self.apply_snap(delta_pos.x, self.snap_settings.grid_spacing),
                    self.apply_snap(delta_pos.y, self.snap_settings.grid_spacing),
                    self.apply_snap(delta_pos.z, self.snap_settings.grid_spacing)
                )
                node.local_transform.position = init.position + dp

            if delta_rot:
                node.local_transform.rotation = init.rotation.multiply(delta_rot)

            if delta_scale:
                ds = Vector3(
                    self.apply_snap(delta_scale.x, self.snap_settings.scale_increment),
                    self.apply_snap(delta_scale.y, self.snap_settings.scale_increment),
                    self.apply_snap(delta_scale.z, self.snap_settings.scale_increment)
                )
                node.local_transform.scale = Vector3(init.scale.x * ds.x, init.scale.y * ds.y, init.scale.z * ds.z)

            tx.current_transforms[nid] = copy.deepcopy(node.local_transform)

        self.update_world_transforms()

    def commit_transform(self) -> Optional[TransformTransaction]:
        if not self.active_transaction:
            return None
        tx = self.active_transaction
        tx.is_active = False
        tx.is_committed = True
        self.undo_stack.append(tx)
        self.redo_stack.clear()
        self.active_transaction = None
        return tx

    def cancel_transform(self) -> None:
        if not self.active_transaction:
            return
        tx = self.active_transaction
        for nid, init_tf in tx.initial_transforms.items():
            if nid in self.nodes:
                self.nodes[nid].local_transform = copy.deepcopy(init_tf)
        tx.is_active = False
        self.active_transaction = None
        self.update_world_transforms()

    def undo_transform(self) -> bool:
        if not self.undo_stack:
            return False
        tx = self.undo_stack.pop()
        for nid, init_tf in tx.initial_transforms.items():
            if nid in self.nodes:
                self.nodes[nid].local_transform = copy.deepcopy(init_tf)
        self.redo_stack.append(tx)
        self.update_world_transforms()
        return True

    def redo_transform(self) -> bool:
        if not self.redo_stack:
            return False
        tx = self.redo_stack.pop()
        for nid, curr_tf in tx.current_transforms.items():
            if nid in self.nodes:
                self.nodes[nid].local_transform = copy.deepcopy(curr_tf)
        self.undo_stack.append(tx)
        self.update_world_transforms()
        return True

    # --------------------------------------------------------------------------
    # Render Command Generation
    # --------------------------------------------------------------------------

    def generate_render_commands(self, viewport_id: str) -> List[ViewportRenderCommand]:
        commands: List[ViewportRenderCommand] = []

        # 1. Grid Pass
        commands.append(ViewportRenderCommand(
            pass_type=RenderPassType.GRID_PASS,
            node_id="editor_grid",
            matrix=Matrix4.identity(),
            color_hex="#444444",
            wireframe=True,
            z_order=-100
        ))

        # 2. Scene Pass (Visible and non-culled)
        visible_ids = self.query_frustum_culling(viewport_id)
        for nid in visible_ids:
            node = self.nodes[nid]
            commands.append(ViewportRenderCommand(
                pass_type=RenderPassType.SCENE_PASS,
                node_id=nid,
                matrix=node.world_matrix,
                color_hex="#A0A0A0",
                z_order=0
            ))

        # 3. Selection & Bounds Passes
        for sel_id in self.selection_state.selected_node_ids:
            if sel_id in self.nodes:
                sel_node = self.nodes[sel_id]
                commands.append(ViewportRenderCommand(
                    pass_type=RenderPassType.SELECTION_OUTLINE,
                    node_id=sel_id,
                    matrix=sel_node.world_matrix,
                    color_hex="#FF9800",
                    z_order=10
                ))
                commands.append(ViewportRenderCommand(
                    pass_type=RenderPassType.BOUNDS_PASS,
                    node_id=f"{sel_id}_bounds",
                    matrix=Matrix4.translation(sel_node.world_aabb.center).multiply(Matrix4.scaling(sel_node.world_aabb.size)),
                    color_hex="#00E5FF",
                    wireframe=True,
                    z_order=15
                ))

        # 4. Gizmo Pass
        if self.selection_state.selected_node_ids:
            pivot = self.get_selection_pivot()
            commands.append(ViewportRenderCommand(
                pass_type=RenderPassType.GIZMO_PASS,
                node_id="gizmo_handle",
                matrix=Matrix4.translation(pivot),
                color_hex="#FF0055",
                z_order=100
            ))

        return commands

    # --------------------------------------------------------------------------
    # State Snapshots, Telemetry & Diagnostics
    # --------------------------------------------------------------------------

    def take_snapshot(self, viewport_id: str) -> ViewportStateSnapshot:
        cam = self.get_camera(viewport_id)
        transforms_summary = {nid: node.local_transform.to_dict() for nid, node in sorted(self.nodes.items())}

        return ViewportStateSnapshot(
            viewport_id=viewport_id,
            camera_pos=[round(cam.position.x, 3), round(cam.position.y, 3), round(cam.position.z, 3)],
            camera_target=[round(cam.target.x, 3), round(cam.target.y, 3), round(cam.target.z, 3)],
            selection=list(self.selection_state.selected_node_ids),
            nodes_count=len(self.nodes),
            transforms_summary=transforms_summary
        )

    def generate_diagnostic_bundle(self, viewport_id: str) -> ViewportDiagnosticBundle:
        snapshot = self.take_snapshot(viewport_id)
        self.telemetry.total_nodes = len(self.nodes)
        self.telemetry.visible_nodes = sum(1 for n in self.nodes.values() if n.visibility)
        self.telemetry.rendered_nodes = len(self.query_frustum_culling(viewport_id))
        self.telemetry.active_gizmo = self.active_gizmo.value

        return ViewportDiagnosticBundle(
            bundle_id=f"vp_diag_{int(time.time() * 1000)}",
            timestamp=time.time(),
            viewport_id=viewport_id,
            snapshot=snapshot,
            telemetry=self.telemetry
        )
