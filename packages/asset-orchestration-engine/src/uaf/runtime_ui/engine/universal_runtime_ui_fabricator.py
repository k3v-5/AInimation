"""
Universal Runtime UI Fabricator Engine (UAF-81.78).
Deterministic UI World lifecycle, hierarchical tree management, 2-pass layout engine,
clipping, scrolling, hit testing, pointer routing, focus & spatial navigation,
text measurement & wrapping, localization & RTL, styles & themes, animations,
reactive data binding, accessibility tree generation, snapshots and deterministic replay.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import uuid
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
    copy_dict_deterministic,
    AccessibilityRole,
    Alignment,
    BindingMode,
    EventRoutingPhase,
    FlexDirection,
    HitTestMode,
    InvalidationFlags,
    LayoutType,
    NavigationDirection,
    OverflowPolicy,
    SizeMode,
    TextAlignment,
    TextOverflow,
    UIAccessibilityNode,
    UIAnchors,
    UIAnimation,
    UIConstraints,
    UIDataBinding,
    UIEvent,
    UIEventType,
    UIFontResource,
    UIIconResource,
    UILocalizationTable,
    UIMargins,
    UINode,
    UINodeType,
    UIPadding,
    UIRecord,
    UIRect,
    UIReplaySession,
    UISnapshot,
    UIStyle,
    UITheme,
    UIVisibility,
    UIWidget,
    UIWorld,
    UIWorldSettings,
    UIWorldState,
    WidgetState,
)


class UniversalRuntimeUIFabricator:
    """Production fabricator and runtime engine for the UAF UI World."""

    VALID_TRANSITIONS: Dict[UIWorldState, Set[UIWorldState]] = {
        UIWorldState.CREATED: {UIWorldState.INITIALIZING, UIWorldState.DESTROYED},
        UIWorldState.INITIALIZING: {UIWorldState.READY, UIWorldState.FAILED, UIWorldState.DESTROYED},
        UIWorldState.READY: {UIWorldState.RUNNING, UIWorldState.STOPPING, UIWorldState.DESTROYED},
        UIWorldState.RUNNING: {UIWorldState.PAUSED, UIWorldState.STOPPING, UIWorldState.FAILED, UIWorldState.DESTROYED},
        UIWorldState.PAUSED: {UIWorldState.RUNNING, UIWorldState.STOPPING, UIWorldState.DESTROYED},
        UIWorldState.STOPPING: {UIWorldState.STOPPED, UIWorldState.DESTROYED},
        UIWorldState.STOPPED: {UIWorldState.READY, UIWorldState.RUNNING, UIWorldState.DESTROYED},
        UIWorldState.FAILED: {UIWorldState.INITIALIZING, UIWorldState.DESTROYED},
        UIWorldState.DESTROYED: set(),
    }

    # =========================================================================
    # 1. LIFECYCLE MANAGEMENT
    # =========================================================================

    @classmethod
    def create_ui_world(
        cls,
        ui_world_id: str = "ui_world_default",
        runtime_world_id: str = "runtime_world_default",
        settings: Optional[UIWorldSettings] = None,
    ) -> UIWorld:
        """Instantiates a new UI World in CREATED state."""
        return UIWorld(
            ui_world_id=ui_world_id,
            runtime_world_id=runtime_world_id,
            state=UIWorldState.CREATED,
            settings=settings or UIWorldSettings(),
        )

    @classmethod
    def transition_state(cls, world: UIWorld, new_state: UIWorldState) -> None:
        """Transitions UIWorld state enforcing the transition state machine."""
        allowed = cls.VALID_TRANSITIONS.get(world.state, set())
        if new_state not in allowed:
            raise ValueError(
                f"NO INVALID UI WORLD TRANSITION: Transition from {world.state.value} to {new_state.value} is forbidden."
            )
        world.state = new_state

    @classmethod
    def initialize(cls, world: UIWorld) -> None:
        """Initializes the UI World."""
        cls.transition_state(world, UIWorldState.INITIALIZING)
        cls.transition_state(world, UIWorldState.READY)

    @classmethod
    def start(cls, world: UIWorld) -> None:
        """Starts UI World execution."""
        cls.transition_state(world, UIWorldState.RUNNING)

    @classmethod
    def pause(cls, world: UIWorld) -> None:
        """Pauses UI World execution."""
        cls.transition_state(world, UIWorldState.PAUSED)

    @classmethod
    def resume(cls, world: UIWorld) -> None:
        """Resumes UI World execution."""
        cls.transition_state(world, UIWorldState.RUNNING)

    @classmethod
    def stop(cls, world: UIWorld) -> None:
        """Stops UI World execution."""
        cls.transition_state(world, UIWorldState.STOPPING)
        cls.transition_state(world, UIWorldState.STOPPED)

    @classmethod
    def destroy(cls, world: UIWorld) -> None:
        """Destroys UI World releasing all resources."""
        if world.state != UIWorldState.DESTROYED:
            world.state = UIWorldState.DESTROYED
        cls.cleanup(world)

    # =========================================================================
    # 2. UI TREE & HIERARCHY MANAGEMENT
    # =========================================================================

    @classmethod
    def create_node(
        cls,
        node_id: str,
        node_type: UINodeType = UINodeType.PANEL,
        **kwargs: Any,
    ) -> UINode:
        """Creates a detached UINode."""
        return UINode(ui_node_id=node_id, node_type=node_type, **kwargs)

    @classmethod
    def create_widget(
        cls,
        widget_id: str,
        widget_type: UINodeType = UINodeType.BUTTON,
        **kwargs: Any,
    ) -> UIWidget:
        """Creates a detached UIWidget."""
        return UIWidget(ui_node_id=widget_id, node_type=widget_type, **kwargs)

    @classmethod
    def add_root_node(
        cls,
        world: UIWorld,
        node_or_id: Union[UINode, str],
        node_type: UINodeType = UINodeType.ROOT,
        **kwargs: Any,
    ) -> UINode:
        """Registers a root node in the UI World."""
        if len(world.nodes) >= world.settings.max_nodes:
            raise ValueError(f"Resource exhaustion: max_nodes limit ({world.settings.max_nodes}) reached.")

        if isinstance(node_or_id, str):
            node = UINode(ui_node_id=node_or_id, node_type=node_type, **kwargs)
        else:
            node = node_or_id
            for k, v in kwargs.items():
                setattr(node, k, v)

        node.parent_id = None
        world.nodes[node.ui_node_id] = node
        if node.ui_node_id not in world.root_ids:
            world.root_ids.append(node.ui_node_id)
        return node

    @classmethod
    def _check_cycle(cls, world: UIWorld, parent_id: str, child_id: str) -> None:
        """Validates that attaching child_id to parent_id does not form a hierarchy cycle."""
        if parent_id == child_id:
            raise ValueError(f"NO TREE CYCLE: Node {child_id} cannot be a parent of itself.")

        curr = parent_id
        visited = {child_id}
        while curr:
            if curr in visited:
                raise ValueError(f"NO TREE CYCLE: Cycle detected involving parent {parent_id} and child {child_id}.")
            visited.add(curr)
            parent_node = world.nodes.get(curr)
            curr = parent_node.parent_id if parent_node else None

    @classmethod
    def _compute_depth(cls, world: UIWorld, node_id: str) -> int:
        """Calculates depth of a node in the hierarchy."""
        depth = 1
        curr = world.nodes.get(node_id)
        while curr and curr.parent_id:
            depth += 1
            curr = world.nodes.get(curr.parent_id)
        return depth

    @classmethod
    def add_child(
        cls,
        world: UIWorld,
        parent_id: str,
        child_or_id: Union[UINode, str],
        node_type: UINodeType = UINodeType.PANEL,
        **kwargs: Any,
    ) -> UINode:
        """Adds a child node under an existing parent."""
        if parent_id not in world.nodes:
            raise ValueError(f"Invalid parent: Parent node {parent_id} does not exist in UI World.")

        parent = world.nodes[parent_id]
        if len(parent.children) >= world.settings.max_children_per_node:
            raise ValueError(f"Resource exhaustion: max_children_per_node reached on {parent_id}.")

        if isinstance(child_or_id, str):
            child_id = child_or_id
            if child_id in world.nodes:
                child = world.nodes[child_id]
                for k, v in kwargs.items():
                    setattr(child, k, v)
            else:
                if len(world.nodes) >= world.settings.max_nodes:
                    raise ValueError(f"Resource exhaustion: max_nodes limit ({world.settings.max_nodes}) reached.")
                child = UINode(ui_node_id=child_id, node_type=node_type, **kwargs)
                world.nodes[child_id] = child
        else:
            child = child_or_id
            child_id = child.ui_node_id
            for k, v in kwargs.items():
                setattr(child, k, v)
            world.nodes[child_id] = child

        # Check cycles
        cls._check_cycle(world, parent_id, child_id)

        # Check multiple parents
        if child.parent_id is not None and child.parent_id != parent_id:
            raise ValueError(
                f"NO NODE WITH MULTIPLE PARENTS: Node {child_id} already has parent {child.parent_id}."
            )

        # Check tree depth
        parent_depth = cls._compute_depth(world, parent_id)
        if parent_depth + 1 > world.settings.max_tree_depth:
            raise ValueError(f"Resource exhaustion: max_tree_depth limit ({world.settings.max_tree_depth}) exceeded.")

        child.parent_id = parent_id
        if child_id not in parent.children:
            parent.children.append(child_id)
        if child_id in world.root_ids:
            world.root_ids.remove(child_id)

        cls.mark_dirty(world, parent_id, InvalidationFlags.LAYOUT_DIRTY)
        return child

    @classmethod
    def attach_node(cls, world: UIWorld, parent_id: str, child_id: str) -> None:
        """Attaches an existing node to a parent."""
        if child_id not in world.nodes:
            raise ValueError(f"Child node {child_id} not found in world.")
        child = world.nodes[child_id]
        cls.add_child(world, parent_id, child)

    @classmethod
    def detach_node(cls, world: UIWorld, node_id: str) -> None:
        """Detaches a node from its parent."""
        if node_id not in world.nodes:
            return
        node = world.nodes[node_id]
        if node.parent_id and node.parent_id in world.nodes:
            parent = world.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)
            cls.mark_dirty(world, node.parent_id, InvalidationFlags.LAYOUT_DIRTY)
        node.parent_id = None
        if node_id not in world.root_ids:
            world.root_ids.append(node_id)

    @classmethod
    def destroy_node(cls, world: UIWorld, node_id: str) -> None:
        """Recursively destroys a node and all its descendants."""
        if node_id not in world.nodes:
            return

        node = world.nodes[node_id]
        # Recursively destroy children first
        for ch_id in list(node.children):
            cls.destroy_node(world, ch_id)

        # Detach from parent
        if node.parent_id and node.parent_id in world.nodes:
            parent = world.nodes[node.parent_id]
            if node_id in parent.children:
                parent.children.remove(node_id)

        if node_id in world.root_ids:
            world.root_ids.remove(node_id)

        # Clear focus and pointer capture if held
        if world.focused_node_id == node_id:
            world.focused_node_id = None
        if world.pointer_captured_node_id == node_id:
            world.pointer_captured_node_id = None

        # Clean up bindings and animations targeting this node
        world.bindings = {k: b for k, b in world.bindings.items() if b.target_node_id != node_id}
        world.animations = {k: a for k, a in world.animations.items() if a.target_node_id != node_id}

        del world.nodes[node_id]

    # =========================================================================
    # 3. DIRTY FLAGS & INVALIDATION
    # =========================================================================

    @classmethod
    def mark_dirty(cls, world: UIWorld, node_id: str, flag: InvalidationFlags) -> None:
        """Marks a node dirty and bubbles layout/render dirtiness up to roots."""
        if node_id not in world.nodes:
            return
        curr_id = node_id
        while curr_id and curr_id in world.nodes:
            curr_node = world.nodes[curr_id]
            curr_node.dirty_flags.add(flag.value)
            curr_id = curr_node.parent_id

    # =========================================================================
    # 4. MEASURE & LAYOUT ENGINE (2-PASS)
    # =========================================================================

    @classmethod
    def measure(
        cls,
        world: UIWorld,
        node_id: str,
        available_width: float,
        available_height: float,
    ) -> Tuple[float, float]:
        """Pass 1 (Measure): Computes desired dimensions respecting constraints."""
        if math.isnan(available_width) or math.isnan(available_height):
            raise ValueError("NO NAN LAYOUT VALUES: Measure input dimensions cannot be NaN.")

        node = world.nodes[node_id]

        if node.visibility in (UIVisibility.COLLAPSED,):
            node.desired_width = 0.0
            node.desired_height = 0.0
            return (0.0, 0.0)

        # Calculate base content size
        content_w = node.desired_width if node.desired_width > 0.0 else 0.0
        content_h = node.desired_height if node.desired_height > 0.0 else 0.0

        if node.node_type == UINodeType.LABEL or (node.text and content_w == 0.0 and content_h == 0.0):
            text_len = len(node.text)
            char_w = node.font_size * 0.6
            line_h = node.font_size * 1.2
            if node.text_overflow == TextOverflow.WRAP and available_width > 0:
                max_chars_per_line = max(1, int(available_width / max(1.0, char_w)))
                lines = math.ceil(text_len / max_chars_per_line) if text_len > 0 else 1
                content_w = min(available_width, text_len * char_w)
                content_h = lines * line_h
            else:
                content_w = text_len * char_w
                content_h = line_h
        elif node.node_type in (UINodeType.BUTTON,):
            text_len = len(node.text)
            char_w = node.font_size * 0.6
            content_w = max(40.0, text_len * char_w + 20.0)
            content_h = max(24.0, node.font_size * 1.4)
        elif node.node_type in (UINodeType.SLIDER, UINodeType.PROGRESS_BAR, UINodeType.PROGRESS):
            content_w = 120.0
            content_h = 20.0
        elif node.node_type in (UINodeType.CHECKBOX, UINodeType.RADIO):
            content_w = 20.0 + (len(node.text) * node.font_size * 0.6 if node.text else 0.0)
            content_h = 20.0

        # Measure children for layout containers
        if node.children:
            child_avail_w = max(0.0, available_width - node.padding.horizontal)
            child_avail_h = max(0.0, available_height - node.padding.vertical)

            if node.layout_type == LayoutType.STACK:
                is_vertical = node.flex_direction in (FlexDirection.COLUMN, FlexDirection.COLUMN_REVERSE)
                main_acc = 0.0
                cross_max = 0.0
                for ch_id in node.children:
                    cw, ch = cls.measure(world, ch_id, child_avail_w, child_avail_h)
                    ch_node = world.nodes[ch_id]
                    if ch_node.visibility == UIVisibility.COLLAPSED:
                        continue
                    if is_vertical:
                        main_acc += ch + ch_node.margins.vertical
                        cross_max = max(cross_max, cw + ch_node.margins.horizontal)
                    else:
                        main_acc += cw + ch_node.margins.horizontal
                        cross_max = max(cross_max, ch + ch_node.margins.vertical)
                content_w = max(content_w, cross_max if is_vertical else main_acc)
                content_h = max(content_h, main_acc if is_vertical else cross_max)

            elif node.layout_type == LayoutType.FLEX:
                is_row = node.flex_direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)
                row_w = 0.0
                col_h = 0.0
                for ch_id in node.children:
                    cw, ch = cls.measure(world, ch_id, child_avail_w, child_avail_h)
                    ch_node = world.nodes[ch_id]
                    if ch_node.visibility == UIVisibility.COLLAPSED:
                        continue
                    if is_row:
                        row_w += cw + ch_node.margins.horizontal
                        col_h = max(col_h, ch + ch_node.margins.vertical)
                    else:
                        col_h += ch + ch_node.margins.vertical
                        row_w = max(row_w, cw + ch_node.margins.horizontal)
                content_w = max(content_w, row_w)
                content_h = max(content_h, col_h)

            elif node.layout_type == LayoutType.GRID:
                cols = 2
                max_row_h = 0.0
                grid_w = 0.0
                grid_h = 0.0
                curr_row_w = 0.0
                for idx, ch_id in enumerate(node.children):
                    cw, ch = cls.measure(world, ch_id, child_avail_w / cols, child_avail_h)
                    ch_node = world.nodes[ch_id]
                    curr_row_w += cw + ch_node.margins.horizontal
                    max_row_h = max(max_row_h, ch + ch_node.margins.vertical)
                    if (idx + 1) % cols == 0 or idx == len(node.children) - 1:
                        grid_w = max(grid_w, curr_row_w)
                        grid_h += max_row_h
                        curr_row_w = 0.0
                        max_row_h = 0.0
                content_w = max(content_w, grid_w)
                content_h = max(content_h, grid_h)

            elif node.layout_type == LayoutType.ABSOLUTE:
                abs_w = 0.0
                abs_h = 0.0
                for ch_id in node.children:
                    cw, ch = cls.measure(world, ch_id, child_avail_w, child_avail_h)
                    ch_node = world.nodes[ch_id]
                    abs_w = max(abs_w, ch_node.anchors.offset_x + cw)
                    abs_h = max(abs_h, ch_node.anchors.offset_y + ch)
                content_w = max(content_w, abs_w)
                content_h = max(content_h, abs_h)

        desired_w = content_w + node.padding.horizontal
        desired_h = content_h + node.padding.vertical

        # Apply explicit SizeMode if FIXED
        if node.size_mode_x == SizeMode.FIXED and node.assigned_rect.width > 0:
            desired_w = node.assigned_rect.width
        if node.size_mode_y == SizeMode.FIXED and node.assigned_rect.height > 0:
            desired_h = node.assigned_rect.height

        # Apply constraints
        desired_w = node.constraints.clamp_width(desired_w)
        desired_h = node.constraints.clamp_height(desired_h)

        if math.isnan(desired_w) or math.isnan(desired_h):
            raise ValueError("NO NAN LAYOUT VALUES: Desired dimension cannot be NaN.")
        if math.isinf(desired_w) or math.isinf(desired_h):
            raise ValueError("NO INFINITE LAYOUT VALUES: Desired dimension cannot be infinite.")

        node.desired_width = desired_w
        node.desired_height = desired_h
        return (desired_w, desired_h)

    @classmethod
    def layout(
        cls,
        world: UIWorld,
        node_id: str,
        x: float,
        y: float,
        assigned_width: float,
        assigned_height: float,
        parent_clip: Optional[UIRect] = None,
    ) -> None:
        """Pass 2 (Layout / Arrange): Computes final rect coordinates and clipping boundaries."""
        if math.isnan(x) or math.isnan(y) or math.isnan(assigned_width) or math.isnan(assigned_height):
            raise ValueError("NO NAN LAYOUT VALUES: Layout coordinates and dimensions cannot be NaN.")
        if assigned_width < 0.0 or assigned_height < 0.0:
            raise ValueError("NO INVALID DIMENSIONS: Width and height must be non-negative.")

        node = world.nodes[node_id]

        if node.visibility == UIVisibility.COLLAPSED:
            node.assigned_rect = UIRect(x, y, 0.0, 0.0)
            node.clip_rect = None
            return

        node.assigned_rect = UIRect(x, y, assigned_width, assigned_height)

        # Compute clipping rect
        if node.overflow_x in (OverflowPolicy.CLIP, OverflowPolicy.SCROLL) or node.overflow_y in (OverflowPolicy.CLIP, OverflowPolicy.SCROLL):
            local_clip = UIRect(x, y, assigned_width, assigned_height)
            if parent_clip:
                node.clip_rect = local_clip.intersect(parent_clip)
            else:
                node.clip_rect = local_clip
        else:
            node.clip_rect = parent_clip

        # Arrange children
        inner_x = x + node.padding.left - node.scroll_offset_x
        inner_y = y + node.padding.top - node.scroll_offset_y
        inner_w = max(0.0, assigned_width - node.padding.horizontal)
        inner_h = max(0.0, assigned_height - node.padding.vertical)

        curr_x = inner_x
        curr_y = inner_y
        total_child_w = 0.0
        total_child_h = 0.0

        is_vertical = node.flex_direction in (FlexDirection.COLUMN, FlexDirection.COLUMN_REVERSE)

        if node.layout_type in (LayoutType.STACK, LayoutType.FLEX):
            # Calculate alignment offsets if CENTER or END
            if node.alignment == Alignment.CENTER:
                if is_vertical:
                    total_h = sum(world.nodes[cid].desired_height + world.nodes[cid].margins.vertical for cid in node.children if world.nodes[cid].visibility != UIVisibility.COLLAPSED)
                    curr_y += max(0.0, (inner_h - total_h) * 0.5)
                else:
                    total_w = sum(world.nodes[cid].desired_width + world.nodes[cid].margins.horizontal for cid in node.children if world.nodes[cid].visibility != UIVisibility.COLLAPSED)
                    curr_x += max(0.0, (inner_w - total_w) * 0.5)
            elif node.alignment == Alignment.END:
                if is_vertical:
                    total_h = sum(world.nodes[cid].desired_height + world.nodes[cid].margins.vertical for cid in node.children if world.nodes[cid].visibility != UIVisibility.COLLAPSED)
                    curr_y += max(0.0, inner_h - total_h)
                else:
                    total_w = sum(world.nodes[cid].desired_width + world.nodes[cid].margins.horizontal for cid in node.children if world.nodes[cid].visibility != UIVisibility.COLLAPSED)
                    curr_x += max(0.0, inner_w - total_w)

            for ch_id in node.children:
                ch_node = world.nodes[ch_id]
                if ch_node.visibility == UIVisibility.COLLAPSED:
                    cls.layout(world, ch_id, curr_x, curr_y, 0.0, 0.0, node.clip_rect)
                    continue

                ch_w = ch_node.desired_width
                ch_h = ch_node.desired_height

                if node.cross_alignment == Alignment.STRETCH:
                    if is_vertical:
                        ch_w = inner_w - ch_node.margins.horizontal
                    else:
                        ch_h = inner_h - ch_node.margins.vertical

                cx = curr_x + ch_node.margins.left
                cy = curr_y + ch_node.margins.top

                cls.layout(world, ch_id, cx, cy, ch_w, ch_h, node.clip_rect)

                if is_vertical:
                    curr_y += ch_h + ch_node.margins.vertical
                    total_child_w = max(total_child_w, ch_w + ch_node.margins.horizontal)
                    total_child_h += ch_h + ch_node.margins.vertical
                else:
                    curr_x += ch_w + ch_node.margins.horizontal
                    total_child_w += ch_w + ch_node.margins.horizontal
                    total_child_h = max(total_child_h, ch_h + ch_node.margins.vertical)

        elif node.layout_type == LayoutType.ABSOLUTE:
            for ch_id in node.children:
                ch_node = world.nodes[ch_id]
                ch_w = ch_node.desired_width
                ch_h = ch_node.desired_height
                cx = inner_x + ch_node.anchors.offset_x + ch_node.margins.left
                cy = inner_y + ch_node.anchors.offset_y + ch_node.margins.top
                cls.layout(world, ch_id, cx, cy, ch_w, ch_h, node.clip_rect)
                total_child_w = max(total_child_w, ch_node.anchors.offset_x + ch_w + ch_node.margins.horizontal)
                total_child_h = max(total_child_h, ch_node.anchors.offset_y + ch_h + ch_node.margins.vertical)

        elif node.layout_type == LayoutType.GRID:
            cols = 2
            col_w = inner_w / cols if cols > 0 else inner_w
            gx = inner_x
            gy = inner_y
            row_h = 0.0
            for idx, ch_id in enumerate(node.children):
                ch_node = world.nodes[ch_id]
                ch_w = min(col_w - ch_node.margins.horizontal, ch_node.desired_width)
                ch_h = ch_node.desired_height
                row_h = max(row_h, ch_h + ch_node.margins.vertical)
                cls.layout(world, ch_id, gx + ch_node.margins.left, gy + ch_node.margins.top, ch_w, ch_h, node.clip_rect)
                if (idx + 1) % cols == 0:
                    gx = inner_x
                    gy += row_h
                    total_child_h += row_h
                    row_h = 0.0
                else:
                    gx += col_w
                total_child_w = max(total_child_w, gx - inner_x)

        node.content_width = total_child_w
        node.content_height = total_child_h
        node.dirty_flags.discard(InvalidationFlags.LAYOUT_DIRTY.value)
        node.dirty_flags.discard(InvalidationFlags.MEASURE_DIRTY.value)

    @classmethod
    def update_layout(cls, world: UIWorld) -> None:
        """Executes full measure and layout passes across all registered roots."""
        vw = world.settings.viewport_width * world.settings.dpi_scale
        vh = world.settings.viewport_height * world.settings.dpi_scale
        for root_id in world.root_ids:
            if root_id in world.nodes:
                cls.measure(world, root_id, vw, vh)
                cls.layout(world, root_id, 0.0, 0.0, vw, vh, None)

    # =========================================================================
    # 5. CLIPPING & SCROLLING
    # =========================================================================

    @classmethod
    def set_scroll_offset(cls, world: UIWorld, node_id: str, offset_x: float, offset_y: float) -> None:
        """Sets scroll offset within content limits."""
        if node_id not in world.nodes:
            return
        node = world.nodes[node_id]
        max_scroll_x = max(0.0, node.content_width - (node.assigned_rect.width - node.padding.horizontal))
        max_scroll_y = max(0.0, node.content_height - (node.assigned_rect.height - node.padding.vertical))

        node.scroll_offset_x = max(0.0, min(max_scroll_x, offset_x))
        node.scroll_offset_y = max(0.0, min(max_scroll_y, offset_y))
        cls.mark_dirty(world, node_id, InvalidationFlags.LAYOUT_DIRTY)

    @classmethod
    def scroll_by(cls, world: UIWorld, node_id: str, dx: float, dy: float) -> None:
        """Increments scroll offset."""
        if node_id not in world.nodes:
            return
        node = world.nodes[node_id]
        cls.set_scroll_offset(world, node_id, node.scroll_offset_x + dx, node.scroll_offset_y + dy)

    # =========================================================================
    # 6. HIT TESTING & POINTER ROUTING
    # =========================================================================

    @classmethod
    def _hit_test_node(cls, world: UIWorld, node_id: str, px: float, py: float) -> Optional[str]:
        """Recursive internal hit test visiting top-most children first."""
        node = world.nodes[node_id]

        if node.visibility in (UIVisibility.INVISIBLE, UIVisibility.COLLAPSED, UIVisibility.HIDDEN):
            return None
        if node.hit_test_mode in (HitTestMode.DISABLED, HitTestMode.NONE):
            return None

        # Check clipping bounds
        if node.clip_rect and not node.clip_rect.contains(px, py):
            return None

        # Check self rect
        if not node.assigned_rect.contains(px, py):
            return None

        # If CHILDREN_ONLY, skip self check and only check children
        if node.hit_test_mode == HitTestMode.SELF_ONLY:
            return node_id

        # Visit children in reverse visual order (highest z_index first, then rightmost/bottommost)
        sorted_children = sorted(
            node.children,
            key=lambda cid: (world.nodes[cid].z_index, world.nodes[cid].assigned_rect.y, world.nodes[cid].assigned_rect.x),
            reverse=True,
        )

        for ch_id in sorted_children:
            hit = cls._hit_test_node(world, ch_id, px, py)
            if hit:
                return hit

        if node.hit_test_mode == HitTestMode.CHILDREN_ONLY:
            return None

        return node_id

    @classmethod
    def hit_test(cls, world: UIWorld, px: float, py: float) -> Optional[str]:
        """Finds topmost interactive widget at coordinates (px, py)."""
        sorted_roots = sorted(
            world.root_ids,
            key=lambda rid: world.nodes[rid].z_index if rid in world.nodes else 0,
            reverse=True,
        )
        for rid in sorted_roots:
            if rid in world.nodes:
                hit = cls._hit_test_node(world, rid, px, py)
                if hit:
                    return hit
        return None

    @classmethod
    def capture_pointer(cls, world: UIWorld, node_id: str) -> None:
        """Assigns pointer capture to a node."""
        if node_id in world.nodes:
            world.pointer_captured_node_id = node_id

    @classmethod
    def release_pointer(cls, world: UIWorld, node_id: Optional[str] = None) -> None:
        """Releases pointer capture."""
        if node_id is None or world.pointer_captured_node_id == node_id:
            world.pointer_captured_node_id = None

    @classmethod
    def dispatch_pointer_event(
        cls,
        world: UIWorld,
        event_type: UIEventType,
        px: float,
        py: float,
        delta_x: float = 0.0,
        delta_y: float = 0.0,
        target_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UIEvent:
        """Routes a pointer event to the captured or hit-tested widget."""
        resolved_target = target_id or world.pointer_captured_node_id or cls.hit_test(world, px, py) or ""

        event = UIEvent(
            event_type=event_type,
            target_id=resolved_target,
            pointer_x=px,
            pointer_y=py,
            delta_x=delta_x,
            delta_y=delta_y,
            timestamp=world.current_time,
            phase=EventRoutingPhase.TARGET,
            metadata=metadata or {},
        )

        if resolved_target and resolved_target in world.nodes:
            target_node = world.nodes[resolved_target]
            if not target_node.is_enabled:
                # Disabled widgets do not process normal click/interaction
                return event

            if event_type == UIEventType.POINTER_DOWN:
                target_node.state = WidgetState.PRESSED
            elif event_type == UIEventType.POINTER_UP:
                target_node.state = WidgetState.HOVER
            elif event_type == UIEventType.POINTER_ENTER:
                target_node.state = WidgetState.HOVER
            elif event_type == UIEventType.POINTER_EXIT:
                target_node.state = WidgetState.NORMAL
            elif event_type == UIEventType.CLICK:
                target_node.state = WidgetState.NORMAL
                if target_node.node_type == UINodeType.CHECKBOX:
                    target_node.is_checked = not target_node.is_checked
                    cls.update_bound_widget(world, target_id, "is_checked", target_node.is_checked)
                elif target_node.node_type == UINodeType.RADIO:
                    target_node.is_selected = True
                    cls.update_bound_widget(world, target_id, "is_selected", True)

        world.event_queue.append(event)
        world.events_history.append(event)
        return event

    # =========================================================================
    # 7. FOCUS & NAVIGATION
    # =========================================================================

    @classmethod
    def set_focus(cls, world: UIWorld, node_id: Optional[str]) -> bool:
        """Sets active focus to a node, triggering gain/loss events."""
        if node_id == world.focused_node_id:
            return True

        if node_id is not None:
            if node_id not in world.nodes:
                return False
            node = world.nodes[node_id]
            if not node.is_enabled or node.visibility != UIVisibility.VISIBLE:
                return False

        if world.focused_node_id and world.focused_node_id in world.nodes:
            prev = world.nodes[world.focused_node_id]
            prev.is_focused = False
            prev.state = WidgetState.NORMAL
            loss_event = UIEvent(
                event_type=UIEventType.FOCUS_LOST,
                target_id=prev.ui_node_id,
                timestamp=world.current_time,
            )
            world.event_queue.append(loss_event)
            world.events_history.append(loss_event)

        world.focused_node_id = node_id
        if node_id:
            new_node = world.nodes[node_id]
            new_node.is_focused = True
            new_node.state = WidgetState.FOCUSED
            gain_event = UIEvent(
                event_type=UIEventType.FOCUS_GAINED,
                target_id=node_id,
                timestamp=world.current_time,
            )
            world.event_queue.append(gain_event)
            world.events_history.append(gain_event)

        return True

    @classmethod
    def clear_focus(cls, world: UIWorld) -> None:
        """Clears active focus."""
        cls.set_focus(world, None)

    @classmethod
    def navigate(cls, world: UIWorld, direction: NavigationDirection) -> Optional[str]:
        """Navigates focus spatially or along tab order deterministically."""
        curr_id = world.focused_node_id

        # 1. Explicit navigation overrides
        if curr_id and curr_id in world.nodes:
            curr_node = world.nodes[curr_id]
            target_id = None
            if direction == NavigationDirection.UP:
                target_id = curr_node.nav_up
            elif direction == NavigationDirection.DOWN:
                target_id = curr_node.nav_down
            elif direction == NavigationDirection.LEFT:
                target_id = curr_node.nav_left
            elif direction == NavigationDirection.RIGHT:
                target_id = curr_node.nav_right

            if target_id and target_id in world.nodes and world.nodes[target_id].is_enabled:
                cls.set_focus(world, target_id)
                return target_id

        # 2. Tab Navigation (NEXT, PREVIOUS, PREV)
        if direction in (NavigationDirection.NEXT, NavigationDirection.PREVIOUS, NavigationDirection.PREV):
            candidates = [
                n for n in world.nodes.values()
                if n.is_enabled and n.visibility == UIVisibility.VISIBLE and n.tab_index >= 0 and n.ui_node_id not in world.root_ids
            ]
            if not candidates:
                return None
            sorted_candidates = sorted(
                candidates,
                key=lambda n: (n.tab_index, n.assigned_rect.y, n.assigned_rect.x, n.ui_node_id)
            )
            if not curr_id:
                next_node = sorted_candidates[0]
            else:
                curr_idx = -1
                for i, c in enumerate(sorted_candidates):
                    if c.ui_node_id == curr_id:
                        curr_idx = i
                        break
                if direction == NavigationDirection.NEXT:
                    next_node = sorted_candidates[(curr_idx + 1) % len(sorted_candidates)]
                else:
                    next_node = sorted_candidates[(curr_idx - 1) % len(sorted_candidates)]
            cls.set_focus(world, next_node.ui_node_id)
            return next_node.ui_node_id

        # 3. Spatial Navigation (UP, DOWN, LEFT, RIGHT)
        candidates = [
            n for n in world.nodes.values()
            if n.is_enabled and n.visibility == UIVisibility.VISIBLE and n.ui_node_id != curr_id
        ]
        if not candidates:
            return None

        if not curr_id or curr_id not in world.nodes:
            cls.set_focus(world, candidates[0].ui_node_id)
            return candidates[0].ui_node_id

        curr_rect = world.nodes[curr_id].assigned_rect
        cx = curr_rect.x + curr_rect.width * 0.5
        cy = curr_rect.y + curr_rect.height * 0.5

        best_id: Optional[str] = None
        min_distance = float("inf")

        for c in candidates:
            tc_rect = c.assigned_rect
            tc_x = tc_rect.x + tc_rect.width * 0.5
            tc_y = tc_rect.y + tc_rect.height * 0.5

            dx = tc_x - cx
            dy = tc_y - cy

            is_valid_dir = False
            if direction == NavigationDirection.UP and dy < -1e-3:
                is_valid_dir = True
                dist = abs(dy) * 1.0 + abs(dx) * 2.0
            elif direction == NavigationDirection.DOWN and dy > 1e-3:
                is_valid_dir = True
                dist = abs(dy) * 1.0 + abs(dx) * 2.0
            elif direction == NavigationDirection.LEFT and dx < -1e-3:
                is_valid_dir = True
                dist = abs(dx) * 1.0 + abs(dy) * 2.0
            elif direction == NavigationDirection.RIGHT and dx > 1e-3:
                is_valid_dir = True
                dist = abs(dx) * 1.0 + abs(dy) * 2.0

            if is_valid_dir:
                if dist < min_distance or (abs(dist - min_distance) < 1e-5 and (best_id is None or c.ui_node_id < best_id)):
                    min_distance = dist
                    best_id = c.ui_node_id

        if best_id:
            cls.set_focus(world, best_id)
            return best_id

        return curr_id

    # =========================================================================
    # 8. LOCALIZATION & TEXT
    # =========================================================================

    @classmethod
    def add_localization_table(cls, world: UIWorld, table: UILocalizationTable) -> None:
        """Registers a localization table."""
        world.localization_tables[table.locale] = table

    @classmethod
    def set_active_locale(cls, world: UIWorld, locale: str) -> None:
        """Switches active locale and updates localizable texts."""
        world.active_locale = locale
        for node in world.nodes.values():
            if node.translation_key:
                node.text = cls.translate(world, node.translation_key)
        cls.update_layout(world)

    @classmethod
    def translate(
        cls,
        world: UIWorld,
        key: str,
        locale: Optional[str] = None,
        count: Optional[int] = None,
    ) -> str:
        """Translates a key respecting active locale, fallbacks, and pluralization."""
        loc = locale or world.active_locale
        table = world.localization_tables.get(loc)
        if not table and world.settings.default_locale in world.localization_tables:
            table = world.localization_tables.get(world.settings.default_locale)

        if not table:
            return key

        if count is not None and key in table.plural_rules:
            rules = table.plural_rules[key]
            if count == 1 and "one" in rules:
                return rules["one"].format(count=count)
            elif count == 0 and "zero" in rules:
                return rules["zero"].format(count=count)
            elif "other" in rules:
                return rules["other"].format(count=count)

        if key in table.translations:
            return table.translations[key]

        # Key not found in current table, fallback to default locale if available
        if world.settings.default_locale in world.localization_tables and world.settings.default_locale != table.locale:
            def_table = world.localization_tables[world.settings.default_locale]
            if key in def_table.translations:
                return def_table.translations[key]

        return key

    # =========================================================================
    # 9. STYLES & THEMES
    # =========================================================================

    @classmethod
    def add_style(cls, world: UIWorld, style: UIStyle) -> None:
        """Registers a UIStyle."""
        world.styles[style.style_id] = style

    @classmethod
    def add_theme(cls, world: UIWorld, theme: UITheme) -> None:
        """Registers a UITheme."""
        world.themes[theme.theme_id] = theme

    @classmethod
    def set_active_theme(cls, world: UIWorld, theme_id: str) -> None:
        """Switches active theme and marks nodes dirty."""
        if theme_id not in world.themes:
            raise ValueError(f"Theme {theme_id} not registered.")
        world.active_theme_id = theme_id
        for nid in world.nodes:
            cls.mark_dirty(world, nid, InvalidationFlags.STYLE_DIRTY)

    @classmethod
    def resolve_style_inheritance(cls, world: UIWorld, style_id: str, visited: Optional[Set[str]] = None) -> UIStyle:
        """Resolves style cascade avoiding cycles."""
        vis = visited or set()
        if style_id in vis:
            raise ValueError(f"NO STYLE INHERITANCE LOOP: Inheritance cycle detected in style {style_id}.")
        vis.add(style_id)

        if style_id not in world.styles:
            return UIStyle(style_id=style_id)

        curr = world.styles[style_id]
        if not curr.parent_style_id:
            res = copy.deepcopy(curr)
            if res.opacity is None:
                res.opacity = 1.0
            return res

        parent_style = cls.resolve_style_inheritance(world, curr.parent_style_id, vis)
        # Override parent properties with child properties if specified
        merged = copy.deepcopy(parent_style)
        merged.style_id = curr.style_id
        merged.name = curr.name or merged.name
        if curr.color != "#FFFFFF":
            merged.color = curr.color
        if curr.background_color != "#00000000":
            merged.background_color = curr.background_color
        if curr.border_color != "#00000000":
            merged.border_color = curr.border_color
        if curr.border_width > 0.0:
            merged.border_width = curr.border_width
        if curr.border_radius > 0.0:
            merged.border_radius = curr.border_radius
        if curr.opacity is not None:
            merged.opacity = curr.opacity
        elif merged.opacity is None:
            merged.opacity = 1.0
        if curr.font_id:
            merged.font_id = curr.font_id
        if curr.font_size != 14.0:
            merged.font_size = curr.font_size
        return merged

    # =========================================================================
    # 10. ANIMATIONS
    # =========================================================================

    @classmethod
    def create_animation(
        cls,
        world: UIWorld,
        animation_id: str,
        target_node_id: str,
        property_name: str,
        start_val: Any,
        end_val: Any,
        duration: float = 1.0,
        easing: str = "linear",
        loop: bool = False,
    ) -> UIAnimation:
        """Registers a UI animation."""
        if len(world.animations) >= world.settings.max_animations:
            raise ValueError(f"Resource exhaustion: max_animations ({world.settings.max_animations}) reached.")

        anim = UIAnimation(
            animation_id=animation_id,
            target_node_id=target_node_id,
            property_name=property_name,
            start_value=start_val,
            end_value=end_val,
            duration=max(1e-4, duration),
            easing=easing,
            loop=loop,
        )
        world.animations[animation_id] = anim
        return anim

    @classmethod
    def _evaluate_easing(cls, t: float, easing: str) -> float:
        """Computes interpolation weight t in [0.0, 1.0]."""
        t = max(0.0, min(1.0, t))
        if easing == "ease_in":
            return t * t
        elif easing == "ease_out":
            return t * (2.0 - t)
        elif easing == "ease_in_out":
            return 2.0 * t * t if t < 0.5 else -1.0 + (4.0 - 2.0 * t) * t
        return t

    @classmethod
    def tick(cls, world: UIWorld, dt: float) -> None:
        """Advances clock, updates animations, and ticks UI world."""
        world.current_time += dt

        for anim in list(world.animations.values()):
            if not anim.is_playing or anim.is_completed:
                continue

            anim.elapsed += dt
            t = min(1.0, anim.elapsed / anim.duration)
            factor = cls._evaluate_easing(t, anim.easing)

            if anim.target_node_id in world.nodes:
                node = world.nodes[anim.target_node_id]
                # Interpolate property
                if isinstance(anim.start_value, (int, float)) and isinstance(anim.end_value, (int, float)):
                    interpolated = anim.start_value + (anim.end_value - anim.start_value) * factor
                    if hasattr(node, anim.property_name):
                        setattr(node, anim.property_name, interpolated)
                        cls.mark_dirty(world, anim.target_node_id, InvalidationFlags.LAYOUT_DIRTY)

            if anim.elapsed >= anim.duration:
                if anim.loop:
                    anim.elapsed = 0.0
                else:
                    anim.is_completed = True
                    anim.is_playing = False

    # =========================================================================
    # 11. DATA BINDING
    # =========================================================================

    @classmethod
    def add_binding(cls, world: UIWorld, binding: UIDataBinding) -> None:
        """Registers a data binding."""
        if len(world.bindings) >= world.settings.max_bindings:
            raise ValueError(f"Resource exhaustion: max_bindings ({world.settings.max_bindings}) reached.")

        world.bindings[binding.binding_id] = binding

        # Initial push if source data exists
        if binding.source_path in world.data_store:
            cls.set_data_value(world, binding.source_path, world.data_store[binding.source_path])

    @classmethod
    def set_data_value(
        cls,
        world: UIWorld,
        path: str,
        value: Any,
        update_stack: Optional[Set[str]] = None,
    ) -> None:
        """Updates data store value and propagates to bound widgets with cycle prevention."""
        stack = update_stack or set()
        if path in stack:
            raise ValueError(f"NO BINDING CYCLE: Cyclic data binding detected on path {path}.")
        stack.add(path)

        world.data_store[path] = value

        for b in world.bindings.values():
            if b.source_path == path and b.target_node_id in world.nodes:
                node = world.nodes[b.target_node_id]
                val = value
                if b.transformer == "uppercase" and isinstance(val, str):
                    val = val.upper()
                elif b.transformer == "lowercase" and isinstance(val, str):
                    val = val.lower()
                elif b.transformer == "round" and isinstance(val, (int, float)):
                    val = round(val)

                if hasattr(node, b.target_property):
                    setattr(node, b.target_property, val)
                    cls.mark_dirty(world, b.target_node_id, InvalidationFlags.LAYOUT_DIRTY)

    @classmethod
    def update_bound_widget(cls, world: UIWorld, node_id: str, property_name: str, value: Any) -> None:
        """Updates widget state and propagates back to data store if two-way bound."""
        for b in world.bindings.values():
            if b.target_node_id == node_id and b.target_property == property_name and b.mode == BindingMode.TWO_WAY:
                world.data_store[b.source_path] = value

    # =========================================================================
    # 12. ACCESSIBILITY TREE
    # =========================================================================

    @classmethod
    def get_accessibility_tree(cls, world: UIWorld) -> List[UIAccessibilityNode]:
        """Generates accessibility tree representing interactive and accessible widgets."""
        result: List[UIAccessibilityNode] = []
        for nid in sorted(world.nodes.keys()):
            node = world.nodes[nid]
            if node.visibility in (UIVisibility.INVISIBLE, UIVisibility.COLLAPSED, UIVisibility.HIDDEN):
                continue

            role = node.accessibility_role
            if role == AccessibilityRole.NONE:
                if node.node_type == UINodeType.BUTTON:
                    role = AccessibilityRole.BUTTON
                elif node.node_type in (UINodeType.TEXT_FIELD, UINodeType.TEXT_AREA):
                    role = AccessibilityRole.TEXT_FIELD
                elif node.node_type == UINodeType.CHECKBOX:
                    role = AccessibilityRole.CHECKBOX
                elif node.node_type == UINodeType.RADIO:
                    role = AccessibilityRole.RADIO
                elif node.node_type in (UINodeType.SLIDER, UINodeType.PROGRESS_BAR, UINodeType.PROGRESS):
                    role = AccessibilityRole.SLIDER
                elif node.node_type == UINodeType.LABEL:
                    role = AccessibilityRole.TEXT
                elif node.node_type == UINodeType.WINDOW:
                    role = AccessibilityRole.WINDOW

            if role != AccessibilityRole.NONE:
                acc_node = UIAccessibilityNode(
                    node_id=nid,
                    automation_id=node.automation_id or f"auto_{nid}",
                    role=role,
                    name=node.accessibility_name or node.text or nid,
                    value=str(node.value) if node.value is not None else None,
                    is_focused=node.is_focused,
                    is_disabled=not node.is_enabled,
                    is_selected=node.is_selected,
                    is_checked=node.is_checked,
                    is_expanded=node.is_expanded,
                )
                result.append(acc_node)
        return result

    # =========================================================================
    # 13. SNAPSHOTS & REPLAY
    # =========================================================================

    @classmethod
    def create_snapshot(cls, world: UIWorld, snapshot_id: Optional[str] = None) -> UISnapshot:
        """Captures complete UI state snapshot."""
        sid = snapshot_id or f"snap_{uuid.uuid4().hex[:8]}"
        scroll_pos = {nid: (n.scroll_offset_x, n.scroll_offset_y) for nid, n in world.nodes.items()}
        return UISnapshot(
            snapshot_id=sid,
            ui_world_id=world.ui_world_id,
            state=world.state.value,
            timestamp=world.current_time,
            nodes={nid: n.to_dict() for nid, n in world.nodes.items()},
            active_theme_id=world.active_theme_id,
            active_locale=world.active_locale,
            focused_node_id=world.focused_node_id,
            scroll_positions=scroll_pos,
            data_store=copy.deepcopy(world.data_store),
            fingerprint=world.compute_fingerprint(),
        )

    @classmethod
    def restore_snapshot(cls, world: UIWorld, snapshot: UISnapshot) -> None:
        """Restores UI World to snapshot state."""
        world.nodes.clear()
        world.root_ids.clear()
        for nid, data in snapshot.nodes.items():
            node = UINode(
                ui_node_id=nid,
                parent_id=data.get("parent_id"),
                node_type=UINodeType(data.get("node_type", "PANEL")),
                visibility=UIVisibility(data.get("visibility", "VISIBLE")),
                state=WidgetState(data.get("state", "NORMAL")),
                layout_type=LayoutType(data.get("layout_type", "STACK")),
                children=list(data.get("children", [])),
                desired_width=float(data.get("desired_width", 0.0)),
                desired_height=float(data.get("desired_height", 0.0)),
                assigned_rect=UIRect(**data.get("assigned_rect", {})),
                scroll_offset_x=float(data.get("scroll_offset_x", 0.0)),
                scroll_offset_y=float(data.get("scroll_offset_y", 0.0)),
                content_width=float(data.get("content_width", 0.0)),
                content_height=float(data.get("content_height", 0.0)),
                hit_test_mode=HitTestMode(data.get("hit_test_mode", "ENABLED")),
                z_index=int(data.get("z_index", 0)),
                is_focused=bool(data.get("is_focused", False)),
                is_enabled=bool(data.get("is_enabled", True)),
                text=str(data.get("text", "")),
                value=data.get("value"),
                is_checked=bool(data.get("is_checked", False)),
                is_selected=bool(data.get("is_selected", False)),
            )
            world.nodes[nid] = node
            if node.parent_id is None:
                world.root_ids.append(nid)

        world.ui_world_id = snapshot.ui_world_id
        world.active_theme_id = snapshot.active_theme_id
        world.active_locale = snapshot.active_locale
        world.focused_node_id = snapshot.focused_node_id
        world.data_store = copy.deepcopy(snapshot.data_store)
        world.current_time = snapshot.timestamp
        cls.update_layout(world)

    @classmethod
    def record_event(cls, world: UIWorld, event: UIEvent) -> UIRecord:
        """Records an event for deterministic replay."""
        rec = UIRecord(
            record_id=f"rec_{len(world.events_history)}",
            event=event,
            timestamp=world.current_time,
        )
        return rec

    @classmethod
    def replay_events(cls, world: UIWorld, events: List[UIEvent]) -> None:
        """Replays recorded events sequentially."""
        for ev in events:
            if ev.event_type in (UIEventType.POINTER_DOWN, UIEventType.POINTER_UP, UIEventType.CLICK, UIEventType.POINTER_MOVE):
                cls.dispatch_pointer_event(
                    world,
                    ev.event_type,
                    ev.pointer_x,
                    ev.pointer_y,
                    ev.delta_x,
                    ev.delta_y,
                    target_id=ev.target_id,
                    metadata=ev.metadata,
                )
            elif ev.event_type == UIEventType.FOCUS_GAINED:
                cls.set_focus(world, ev.target_id)
            elif ev.event_type == UIEventType.FOCUS_LOST:
                if world.focused_node_id == ev.target_id:
                    cls.clear_focus(world)

    # =========================================================================
    # 14. CLEANUP & TEARDOWN
    # =========================================================================

    @classmethod
    def cleanup(cls, world: UIWorld) -> None:
        """Cleans up all references and resets world state."""
        world.nodes.clear()
        world.root_ids.clear()
        world.styles.clear()
        world.themes.clear()
        world.fonts.clear()
        world.icons.clear()
        world.localization_tables.clear()
        world.bindings.clear()
        world.animations.clear()
        world.focused_node_id = None
        world.pointer_captured_node_id = None
        world.event_queue.clear()
        world.events_history.clear()
        world.data_store.clear()
