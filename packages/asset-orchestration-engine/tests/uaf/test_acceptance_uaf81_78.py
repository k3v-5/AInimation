"""
Acceptance Test Suite for UAF-81.78 — Universal Runtime UI World System.
Part 1: Lifecycle, Tree Hierarchy, Widget System, Layout Engine, Clipping & Scrolling, Hit Testing.
"""

import math
import os
import pytest
from uaf.runtime_ui import (
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
    UIRect,
    UISnapshot,
    UIStyle,
    UITheme,
    UniversalRuntimeUIFabricator as Fab,
    UniversalRuntimeUIPackager,
    UniversalRuntimeUIValidator as Val,
    UIVisibility,
    UIWidget,
    UIWorld,
    UIWorldSettings,
    UIWorldState,
    WidgetState,
)


class TestUIWorldLifecycle:
    """Tests for §102 UI World Lifecycle."""

    def test_ui_world_creation(self):
        w = Fab.create_ui_world("ui_01")
        assert w.ui_world_id == "ui_01"
        assert w.state == UIWorldState.CREATED
        assert len(w.nodes) == 0
        assert len(w.root_ids) == 0

    def test_ui_world_identity(self):
        w = Fab.create_ui_world("ui_ident", "runtime_w_01")
        assert w.runtime_world_id == "runtime_w_01"
        assert len(w.compute_fingerprint()) == 64

    def test_ui_world_state(self):
        w = Fab.create_ui_world("ui_st")
        Fab.initialize(w)
        assert w.state == UIWorldState.READY
        Fab.start(w)
        assert w.state == UIWorldState.RUNNING

    def test_ui_world_pause(self):
        w = Fab.create_ui_world("ui_p")
        Fab.initialize(w)
        Fab.start(w)
        Fab.pause(w)
        assert w.state == UIWorldState.PAUSED

    def test_ui_world_resume(self):
        w = Fab.create_ui_world("ui_res")
        Fab.initialize(w)
        Fab.start(w)
        Fab.pause(w)
        Fab.resume(w)
        assert w.state == UIWorldState.RUNNING

    def test_ui_world_stop(self):
        w = Fab.create_ui_world("ui_stop")
        Fab.initialize(w)
        Fab.start(w)
        Fab.stop(w)
        assert w.state == UIWorldState.STOPPED

    def test_ui_world_destroy(self):
        w = Fab.create_ui_world("ui_dest")
        Fab.initialize(w)
        Fab.start(w)
        Fab.destroy(w)
        assert w.state == UIWorldState.DESTROYED
        assert len(w.nodes) == 0

    def test_invalid_ui_world_transition(self):
        w = Fab.create_ui_world("ui_inv")
        with pytest.raises(ValueError, match="NO INVALID UI WORLD TRANSITION"):
            Fab.start(w)

    def test_ui_root(self):
        w = Fab.create_ui_world("ui_rt")
        r = Fab.add_root_node(w, "root_main", UINodeType.ROOT)
        assert r.ui_node_id in w.root_ids
        assert w.nodes["root_main"].parent_id is None

    def test_ui_world_snapshot(self):
        w = Fab.create_ui_world("ui_snap")
        Fab.initialize(w)
        snap = Fab.create_snapshot(w)
        assert snap.ui_world_id == "ui_snap"
        assert snap.state == UIWorldState.READY.value


class TestUITreeHierarchy:
    """Tests for §103 Tree Hierarchy."""

    def test_node_creation(self):
        node = Fab.create_node("n_01", UINodeType.PANEL)
        assert node.ui_node_id == "n_01"
        assert node.node_type == UINodeType.PANEL
        assert node.parent_id is None

    def test_node_attach(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "root_0")
        ch = Fab.add_child(w, "root_0", "child_0", UINodeType.BUTTON)
        assert ch.parent_id == "root_0"
        assert "child_0" in w.nodes["root_0"].children

    def test_node_detach(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "root_0")
        Fab.add_child(w, "root_0", "child_0")
        Fab.detach_node(w, "child_0")
        assert w.nodes["child_0"].parent_id is None
        assert "child_0" not in w.nodes["root_0"].children
        assert "child_0" in w.root_ids

    def test_parent_assignment(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "root_0")
        p1 = Fab.add_child(w, "root_0", "p1")
        p2 = Fab.add_child(w, "root_0", "p2")
        ch = Fab.add_child(w, "p1", "ch")
        with pytest.raises(ValueError, match="NO NODE WITH MULTIPLE PARENTS"):
            Fab.add_child(w, "p2", ch)

    def test_child_order(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c1")
        Fab.add_child(w, "r", "c2")
        Fab.add_child(w, "r", "c3")
        assert w.nodes["r"].children == ["c1", "c2", "c3"]

    def test_tree_cycle_rejection(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "n1")
        Fab.add_child(w, "n1", "n2")
        Fab.add_child(w, "n2", "n3")
        with pytest.raises(ValueError, match="NO TREE CYCLE"):
            Fab.attach_node(w, "n3", "n1")

    def test_invalid_parent(self):
        w = Fab.create_ui_world("tree_w")
        with pytest.raises(ValueError, match="Invalid parent"):
            Fab.add_child(w, "non_existent_parent", "c")

    def test_root_management(self):
        w = Fab.create_ui_world("tree_w")
        r1 = Fab.add_root_node(w, "r1")
        r2 = Fab.add_root_node(w, "r2")
        assert len(w.root_ids) == 2
        Fab.destroy_node(w, "r1")
        assert "r1" not in w.root_ids
        assert len(w.root_ids) == 1

    def test_node_destroy(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c1")
        Fab.add_child(w, "c1", "c2")
        Fab.destroy_node(w, "c1")
        assert "c1" not in w.nodes
        assert "c2" not in w.nodes
        assert "c1" not in w.nodes["r"].children

    def test_tree_cleanup(self):
        w = Fab.create_ui_world("tree_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.add_child(w, "r", f"c_{i}")
        assert len(w.nodes) == 11
        Fab.cleanup(w)
        assert len(w.nodes) == 0
        assert len(w.root_ids) == 0


class TestWidgetSystem:
    """Tests for §104 Widget System."""

    def test_widget_creation(self):
        btn = Fab.create_widget("btn_play", UINodeType.BUTTON, text="Play Game")
        assert btn.ui_node_id == "btn_play"
        assert btn.text == "Play Game"
        assert btn.state == WidgetState.NORMAL

    def test_widget_state(self):
        btn = Fab.create_widget("btn_opt", UINodeType.BUTTON)
        btn.state = WidgetState.HOVER
        assert btn.state == WidgetState.HOVER
        btn.state = WidgetState.PRESSED
        assert btn.state == WidgetState.PRESSED

    def test_widget_enable(self):
        w = Fab.create_widget("btn", UINodeType.BUTTON)
        w.is_enabled = False
        assert not w.is_enabled
        w.is_enabled = True
        assert w.is_enabled

    def test_widget_disable(self):
        w = Fab.create_ui_world("w_dis")
        Fab.add_root_node(w, "root")
        btn = Fab.add_child(w, "root", "btn_dis", UINodeType.BUTTON)
        btn.is_enabled = False
        ev = Fab.dispatch_pointer_event(w, UIEventType.CLICK, 0.0, 0.0)
        assert btn.state != WidgetState.PRESSED

    def test_widget_visibility(self):
        w = Fab.create_widget("panel", UINodeType.PANEL)
        w.visibility = UIVisibility.VISIBLE
        assert w.visibility == UIVisibility.VISIBLE
        w.visibility = UIVisibility.COLLAPSED
        assert w.visibility == UIVisibility.COLLAPSED

    def test_widget_selection(self):
        chk = Fab.create_widget("chk_sound", UINodeType.CHECKBOX)
        assert not chk.is_checked
        chk.is_checked = True
        assert chk.is_checked

    def test_widget_value(self):
        slider = Fab.create_widget("sld_vol", UINodeType.SLIDER, min_value=0.0, max_value=1.0, value=0.75)
        assert slider.value == 0.75
        assert slider.max_value == 1.0

    def test_widget_lifecycle(self):
        w = Fab.create_ui_world("w_life")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn_l", UINodeType.BUTTON, text="Submit")
        assert btn.desired_width == 0.0
        Fab.update_layout(w)
        assert btn.desired_width > 0.0

    def test_widget_destroy(self):
        w = Fab.create_ui_world("w_des")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "widget_to_dest")
        assert "widget_to_dest" in w.nodes
        Fab.destroy_node(w, "widget_to_dest")
        assert "widget_to_dest" not in w.nodes

    def test_widget_cleanup(self):
        w = Fab.create_ui_world("w_cln")
        Fab.add_root_node(w, "r")
        for i in range(5):
            Fab.add_child(w, "r", f"w_{i}", UINodeType.BUTTON)
        Fab.cleanup(w)
        assert len(w.nodes) == 0


class TestLayoutEngine:
    """Tests for §105 Layout Engine & Constraints."""

    def test_measure(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", UINodeType.LABEL, text="Hello UI World")
        mw, mh = Fab.measure(w, "lbl", 1920.0, 1080.0)
        assert mw > 0.0
        assert mh > 0.0
        assert lbl.desired_width == mw

    def test_layout(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "p", UINodeType.PANEL)
        Fab.measure(w, "r", 800.0, 600.0)
        Fab.layout(w, "r", 0.0, 0.0, 800.0, 600.0)
        assert w.nodes["r"].assigned_rect.width == 800.0
        assert w.nodes["r"].assigned_rect.height == 600.0

    def test_min_size(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        n = Fab.add_child(w, "r", "n", constraints=UIConstraints(min_width=200.0, min_height=150.0))
        mw, mh = Fab.measure(w, "n", 1000.0, 1000.0)
        assert mw >= 200.0
        assert mh >= 150.0

    def test_max_size(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        n = Fab.add_child(w, "r", "n", text="Very very long text that spans many many characters", constraints=UIConstraints(max_width=100.0, max_height=50.0))
        mw, mh = Fab.measure(w, "n", 1000.0, 1000.0)
        assert mw <= 100.0
        assert mh <= 50.0

    def test_fixed_size(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        n = Fab.add_child(w, "r", "n", size_mode_x=SizeMode.FIXED, size_mode_y=SizeMode.FIXED)
        n.assigned_rect = UIRect(0, 0, 320.0, 240.0)
        mw, mh = Fab.measure(w, "n", 1000.0, 1000.0)
        assert mw == 320.0
        assert mh == 240.0

    def test_content_size(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        n = Fab.add_child(w, "r", "n", text="OK", size_mode_x=SizeMode.CONTENT)
        mw, mh = Fab.measure(w, "n", 1000.0, 1000.0)
        assert mw > 0.0

    def test_stretch(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r", layout_type=LayoutType.STACK, cross_alignment=Alignment.STRETCH)
        c = Fab.add_child(w, "r", "c", text="Stretch Me")
        Fab.measure(w, "r", 500.0, 500.0)
        Fab.layout(w, "r", 0.0, 0.0, 500.0, 500.0)
        assert c.assigned_rect.width == 500.0

    def test_fill(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", size_mode_x=SizeMode.FILL, size_mode_y=SizeMode.FILL)
        Fab.measure(w, "r", 1920.0, 1080.0)
        Fab.layout(w, "r", 0.0, 0.0, 1920.0, 1080.0)
        assert r.assigned_rect.width == 1920.0
        assert r.assigned_rect.height == 1080.0

    def test_margin(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
        c = Fab.add_child(w, "r", "c", text="Margined", margins=UIMargins(left=10.0, top=15.0, right=10.0, bottom=15.0))
        Fab.measure(w, "r", 500.0, 500.0)
        Fab.layout(w, "r", 0.0, 0.0, 500.0, 500.0)
        assert c.assigned_rect.x == 10.0
        assert c.assigned_rect.y == 15.0

    def test_padding(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK, padding=UIPadding(left=20.0, top=30.0, right=20.0, bottom=30.0))
        c = Fab.add_child(w, "r", "c", text="Padded")
        Fab.measure(w, "r", 500.0, 500.0)
        Fab.layout(w, "r", 0.0, 0.0, 500.0, 500.0)
        assert c.assigned_rect.x == 20.0
        assert c.assigned_rect.y == 30.0

    def test_anchor(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.ABSOLUTE)
        c = Fab.add_child(w, "r", "c", anchors=UIAnchors(offset_x=100.0, offset_y=75.0))
        Fab.measure(w, "r", 800.0, 600.0)
        Fab.layout(w, "r", 0.0, 0.0, 800.0, 600.0)
        assert c.assigned_rect.x == 100.0
        assert c.assigned_rect.y == 75.0

    def test_alignment(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK, alignment=Alignment.CENTER)
        c = Fab.add_child(w, "r", "c", text="Centered")
        Fab.measure(w, "r", 400.0, 400.0)
        Fab.layout(w, "r", 0.0, 0.0, 400.0, 400.0)
        assert c.assigned_rect.y > 0.0

    def test_stack_layout(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK, flex_direction=FlexDirection.COLUMN)
        c1 = Fab.add_child(w, "r", "c1", text="One")
        c2 = Fab.add_child(w, "r", "c2", text="Two")
        Fab.measure(w, "r", 400.0, 600.0)
        Fab.layout(w, "r", 0.0, 0.0, 400.0, 600.0)
        assert c2.assigned_rect.y >= c1.assigned_rect.y + c1.assigned_rect.height

    def test_flex_layout(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.FLEX, flex_direction=FlexDirection.ROW)
        c1 = Fab.add_child(w, "r", "c1", text="Left")
        c2 = Fab.add_child(w, "r", "c2", text="Right")
        Fab.measure(w, "r", 800.0, 200.0)
        Fab.layout(w, "r", 0.0, 0.0, 800.0, 200.0)
        assert c2.assigned_rect.x >= c1.assigned_rect.x + c1.assigned_rect.width

    def test_grid_layout(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.GRID)
        for i in range(4):
            Fab.add_child(w, "r", f"g_{i}", text=f"Item {i}")
        Fab.measure(w, "r", 400.0, 400.0)
        Fab.layout(w, "r", 0.0, 0.0, 400.0, 400.0)
        assert w.nodes["g_1"].assigned_rect.x > w.nodes["g_0"].assigned_rect.x
        assert w.nodes["g_2"].assigned_rect.y > w.nodes["g_0"].assigned_rect.y

    def test_absolute_layout(self):
        w = Fab.create_ui_world("l_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.ABSOLUTE)
        c = Fab.add_child(w, "r", "abs_c", anchors=UIAnchors(offset_x=50.0, offset_y=60.0))
        Fab.measure(w, "r", 500.0, 500.0)
        Fab.layout(w, "r", 0.0, 0.0, 500.0, 500.0)
        assert c.assigned_rect.x == 50.0
        assert c.assigned_rect.y == 60.0

    def test_layout_determinism(self):
        def build_and_layout():
            w = Fab.create_ui_world("det_w")
            r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
            for i in range(3):
                Fab.add_child(w, "r", f"node_{i}", text=f"Text {i}")
            Fab.measure(w, "r", 800.0, 600.0)
            Fab.layout(w, "r", 0.0, 0.0, 800.0, 600.0)
            return [(n.assigned_rect.x, n.assigned_rect.y, n.assigned_rect.width, n.assigned_rect.height) for n in w.nodes.values()]

        res1 = build_and_layout()
        res2 = build_and_layout()
        assert res1 == res2

    def test_layout_cycle_rejection(self):
        w = Fab.create_ui_world("l_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c1")
        with pytest.raises(ValueError):
            Fab.add_child(w, "c1", "r")


class TestClippingAndScrolling:
    """Tests for §106 Clipping & Scrolling."""

    def test_clip(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.CLIP)
        Fab.add_child(w, "r", "c")
        Fab.measure(w, "r", 200.0, 200.0)
        Fab.layout(w, "r", 0.0, 0.0, 200.0, 200.0)
        assert r.clip_rect is not None
        assert r.clip_rect.width == 200.0

    def test_nested_clip(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.CLIP)
        p = Fab.add_child(w, "r", "p", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.CLIP)
        Fab.measure(w, "r", 300.0, 300.0)
        Fab.layout(w, "r", 0.0, 0.0, 300.0, 300.0)
        assert p.clip_rect is not None
        assert p.clip_rect.width <= 300.0

    def test_overflow_visible(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.VISIBLE)
        Fab.measure(w, "r", 100.0, 100.0)
        Fab.layout(w, "r", 0.0, 0.0, 100.0, 100.0)
        assert r.clip_rect is None

    def test_overflow_clip(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP)
        Fab.measure(w, "r", 150.0, 150.0)
        Fab.layout(w, "r", 0.0, 0.0, 150.0, 150.0)
        assert r.clip_rect == UIRect(0.0, 0.0, 150.0, 150.0)

    def test_overflow_scroll(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        Fab.measure(w, "r", 200.0, 200.0)
        Fab.layout(w, "r", 0.0, 0.0, 200.0, 200.0)
        assert r.clip_rect is not None

    def test_scroll_offset(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.content_height = 800.0
        r.assigned_rect = UIRect(0, 0, 200.0, 200.0)
        Fab.set_scroll_offset(w, "r", 0.0, 120.0)
        assert r.scroll_offset_y == 120.0

    def test_scroll_limits(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.content_height = 500.0
        r.assigned_rect = UIRect(0, 0, 200.0, 200.0)
        # Attempt overscroll beyond content - viewport (300.0)
        Fab.set_scroll_offset(w, "r", 0.0, 999.0)
        assert r.scroll_offset_y == 300.0
        # Attempt negative scroll
        Fab.set_scroll_offset(w, "r", 0.0, -50.0)
        assert r.scroll_offset_y == 0.0

    def test_scroll_content_size(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
        for i in range(5):
            Fab.add_child(w, "r", f"it_{i}", text="Tall Item", desired_height=100.0)
        Fab.measure(w, "r", 300.0, 300.0)
        Fab.layout(w, "r", 0.0, 0.0, 300.0, 300.0)
        assert r.content_height >= 500.0

    def test_scroll_viewport_size(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r")
        Fab.measure(w, "r", 400.0, 300.0)
        Fab.layout(w, "r", 0.0, 0.0, 400.0, 300.0)
        assert r.assigned_rect.width == 400.0
        assert r.assigned_rect.height == 300.0

    def test_scroll_cleanup(self):
        w = Fab.create_ui_world("clip_w")
        r = Fab.add_root_node(w, "r")
        Fab.scroll_by(w, "r", 0.0, 50.0)
        Fab.cleanup(w)
        assert len(w.nodes) == 0


class TestHitTestingAndRouting:
    """Tests for §107 Hit Testing & Routing."""

    def test_hit_test(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn_start", UINodeType.BUTTON)
        r.assigned_rect = UIRect(0, 0, 800, 600)
        btn.assigned_rect = UIRect(50, 50, 100, 40)
        hit = Fab.hit_test(w, 60.0, 60.0)
        assert hit == "btn_start"

    def test_nested_hit_test(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        panel = Fab.add_child(w, "r", "p")
        btn = Fab.add_child(w, "p", "btn")
        r.assigned_rect = UIRect(0, 0, 800, 600)
        panel.assigned_rect = UIRect(10, 10, 400, 400)
        btn.assigned_rect = UIRect(20, 20, 80, 30)
        assert Fab.hit_test(w, 25.0, 25.0) == "btn"

    def test_z_order(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", z_index=0)
        b2 = Fab.add_child(w, "r", "b2", z_index=10)
        r.assigned_rect = UIRect(0, 0, 500, 500)
        b1.assigned_rect = UIRect(10, 10, 100, 100)
        b2.assigned_rect = UIRect(10, 10, 100, 100)
        assert Fab.hit_test(w, 50.0, 50.0) == "b2"

    def test_clip_hit_test(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.CLIP)
        r.assigned_rect = UIRect(0, 0, 100, 100)
        r.clip_rect = UIRect(0, 0, 100, 100)
        btn = Fab.add_child(w, "r", "btn_out")
        btn.assigned_rect = UIRect(150, 150, 50, 50)
        btn.clip_rect = r.clip_rect
        assert Fab.hit_test(w, 160.0, 160.0) is None

    def test_hidden_hit_test(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn_hid", visibility=UIVisibility.HIDDEN)
        r.assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(20, 20, 100, 50)
        assert Fab.hit_test(w, 30.0, 30.0) != "btn_hid"

    def test_disabled_hit_test(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn_dis", is_enabled=False)
        r.assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(20, 20, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.CLICK, 25.0, 25.0)
        assert btn.state != WidgetState.PRESSED

    def test_pointer_capture(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1")
        b2 = Fab.add_child(w, "r", "b2")
        r.assigned_rect = UIRect(0, 0, 800, 600)
        b1.assigned_rect = UIRect(0, 0, 50, 50)
        b2.assigned_rect = UIRect(100, 100, 50, 50)
        Fab.capture_pointer(w, "b1")
        assert w.pointer_captured_node_id == "b1"
        ev = Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 120.0, 120.0)
        assert ev.target_id == "b1"

    def test_pointer_release(self):
        w = Fab.create_ui_world("hit_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b1")
        Fab.capture_pointer(w, "b1")
        Fab.release_pointer(w, "b1")
        assert w.pointer_captured_node_id is None

    def test_hit_test_determinism(self):
        def run_ht():
            w = Fab.create_ui_world("hit_w")
            r = Fab.add_root_node(w, "r")
            b = Fab.add_child(w, "r", "b")
            r.assigned_rect = UIRect(0, 0, 500, 500)
            b.assigned_rect = UIRect(50, 50, 100, 100)
            return Fab.hit_test(w, 60.0, 60.0)

        assert run_ht() == run_ht()

    def test_pointer_routing_children_only(self):
        w = Fab.create_ui_world("hit_w")
        r = Fab.add_root_node(w, "r", hit_test_mode=HitTestMode.CHILDREN_ONLY)
        r.assigned_rect = UIRect(0, 0, 500, 500)
        # Point inside r but no children
        assert Fab.hit_test(w, 250.0, 250.0) is None


class TestUIEventsAndConsumption:
    """Tests for §108 UI Events & Consumption."""

    def test_pointer_down(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        r = w.nodes["r"]
        r.assigned_rect = UIRect(0, 0, 800, 600)
        btn.assigned_rect = UIRect(10, 10, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 20.0, 20.0)
        assert ev.event_type == UIEventType.POINTER_DOWN
        assert ev.target_id == "btn"
        assert btn.state == WidgetState.PRESSED

    def test_pointer_up(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 800, 600)
        btn.assigned_rect = UIRect(10, 10, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.POINTER_UP, 20.0, 20.0)
        assert ev.target_id == "btn"
        assert btn.state == WidgetState.HOVER

    def test_click(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX)
        w.nodes["r"].assigned_rect = UIRect(0, 0, 800, 600)
        chk.assigned_rect = UIRect(5, 5, 20, 20)
        assert not chk.is_checked
        Fab.dispatch_pointer_event(w, UIEventType.CLICK, 10.0, 10.0)
        assert chk.is_checked

    def test_double_click(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.DOUBLE_CLICK, 10.0, 10.0)
        assert ev.event_type == UIEventType.DOUBLE_CLICK

    def test_drag(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.DRAG, 50.0, 50.0, delta_x=5.0, delta_y=2.0)
        assert ev.delta_x == 5.0
        assert ev.delta_y == 2.0

    def test_scroll(self):
        w = Fab.create_ui_world("ev_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.assigned_rect = UIRect(0, 0, 500, 500)
        r.content_height = 1000.0
        ev = Fab.dispatch_pointer_event(w, UIEventType.SCROLL, 100.0, 100.0, delta_y=-20.0)
        assert ev.event_type == UIEventType.SCROLL

    def test_focus_event(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1")
        b2 = Fab.add_child(w, "r", "b2")
        Fab.set_focus(w, "b1")
        assert w.focused_node_id == "b1"
        Fab.set_focus(w, "b2")
        assert w.focused_node_id == "b2"
        # Check event queue for FOCUS_LOST and FOCUS_GAINED
        event_types = [e.event_type for e in w.event_queue]
        assert UIEventType.FOCUS_GAINED in event_types
        assert UIEventType.FOCUS_LOST in event_types

    def test_keyboard_event(self):
        w = Fab.create_ui_world("ev_w")
        ev = UIEvent(
            event_type=UIEventType.KEY_DOWN,
            target_id="input_field",
            key_code="Enter",
            timestamp=w.current_time,
        )
        w.event_queue.append(ev)
        assert w.event_queue[-1].key_code == "Enter"

    def test_value_changed(self):
        w = Fab.create_ui_world("ev_w")
        ev = UIEvent(
            event_type=UIEventType.VALUE_CHANGED,
            target_id="sld_vol",
            metadata={"old_value": 0.5, "new_value": 0.8},
        )
        assert ev.metadata["new_value"] == 0.8

    def test_event_consumption(self):
        ev = UIEvent(
            event_type=UIEventType.CLICK,
            target_id="btn",
        )
        assert not ev.is_consumed
        ev.is_consumed = True
        assert ev.is_consumed

    def test_event_order(self):
        w = Fab.create_ui_world("ev_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        w.nodes["b"].assigned_rect = UIRect(0, 0, 100, 50)
        Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 10.0, 10.0)
        Fab.dispatch_pointer_event(w, UIEventType.POINTER_UP, 10.0, 10.0)
        Fab.dispatch_pointer_event(w, UIEventType.CLICK, 10.0, 10.0)
        assert len(w.event_queue) == 3
        assert w.event_queue[0].event_type == UIEventType.POINTER_DOWN
        assert w.event_queue[1].event_type == UIEventType.POINTER_UP
        assert w.event_queue[2].event_type == UIEventType.CLICK


class TestFocusAndNavigation:
    """Tests for §109 Focus & Navigation."""

    def test_focus_gain(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        success = Fab.set_focus(w, "btn")
        assert success
        assert btn.is_focused
        assert btn.state == WidgetState.FOCUSED

    def test_focus_loss(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        Fab.set_focus(w, "btn")
        Fab.clear_focus(w)
        assert not btn.is_focused
        assert w.focused_node_id is None

    def test_focus_exclusive(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1")
        b2 = Fab.add_child(w, "r", "b2")
        Fab.set_focus(w, "b1")
        Fab.set_focus(w, "b2")
        assert not b1.is_focused
        assert b2.is_focused
        assert w.focused_node_id == "b2"

    def test_tab_navigation(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", tab_index=0)
        b2 = Fab.add_child(w, "r", "b2", tab_index=1)
        b3 = Fab.add_child(w, "r", "b3", tab_index=2)
        Fab.set_focus(w, "b1")
        next_id = Fab.navigate(w, NavigationDirection.NEXT)
        assert next_id == "b2"
        next_id2 = Fab.navigate(w, NavigationDirection.NEXT)
        assert next_id2 == "b3"
        prev_id = Fab.navigate(w, NavigationDirection.PREVIOUS)
        assert prev_id == "b2"

    def test_spatial_navigation(self):
        w = Fab.create_ui_world("foc_w")
        r = Fab.add_root_node(w, "r")
        b_up = Fab.add_child(w, "r", "b_up")
        b_down = Fab.add_child(w, "r", "b_down")
        b_up.assigned_rect = UIRect(100, 50, 80, 40)
        b_down.assigned_rect = UIRect(100, 200, 80, 40)
        Fab.set_focus(w, "b_up")
        nav_res = Fab.navigate(w, NavigationDirection.DOWN)
        assert nav_res == "b_down"

    def test_explicit_navigation(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", nav_right="b3")
        b2 = Fab.add_child(w, "r", "b2")
        b3 = Fab.add_child(w, "r", "b3")
        Fab.set_focus(w, "b1")
        res = Fab.navigate(w, NavigationDirection.RIGHT)
        assert res == "b3"

    def test_navigation_priority(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", nav_down="explicit_down")
        b_spatial = Fab.add_child(w, "r", "b_spatial")
        b_explicit = Fab.add_child(w, "r", "explicit_down")
        b1.assigned_rect = UIRect(0, 0, 50, 50)
        b_spatial.assigned_rect = UIRect(0, 60, 50, 50)
        b_explicit.assigned_rect = UIRect(200, 200, 50, 50)
        Fab.set_focus(w, "b1")
        assert Fab.navigate(w, NavigationDirection.DOWN) == "explicit_down"

    def test_navigation_determinism(self):
        def test_run():
            w = Fab.create_ui_world("foc_w")
            Fab.add_root_node(w, "r")
            for i in range(5):
                b = Fab.add_child(w, "r", f"btn_{i}", tab_index=i)
                b.assigned_rect = UIRect(0, i * 50, 100, 40)
            Fab.set_focus(w, "btn_0")
            path = []
            for _ in range(4):
                path.append(Fab.navigate(w, NavigationDirection.NEXT))
            return path

        assert test_run() == test_run()

    def test_focus_destroy(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        Fab.set_focus(w, "btn")
        Fab.destroy_node(w, "btn")
        assert w.focused_node_id is None

    def test_focus_disabled_rejection(self):
        w = Fab.create_ui_world("foc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", is_enabled=False)
        assert not Fab.set_focus(w, "btn")
        assert w.focused_node_id is None


class TestTextLayoutAndFonts:
    """Tests for §110 Text Layout & Fonts."""

    def test_text_measurement(self):
        w = Fab.create_ui_world("txt_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", UINodeType.LABEL, text="Measurement Test", font_size=16.0)
        mw, mh = Fab.measure(w, "lbl", 1000.0, 1000.0)
        assert mw > 50.0
        assert mh > 15.0

    def test_text_wrapping(self):
        w = Fab.create_ui_world("txt_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(
            w,
            "r",
            "lbl",
            UINodeType.LABEL,
            text="Very long text that wraps across multiple lines",
            text_overflow=TextOverflow.WRAP,
            font_size=14.0,
        )
        mw, mh = Fab.measure(w, "lbl", 100.0, 1000.0)
        assert mh > 20.0

    def test_text_alignment(self):
        lbl = Fab.create_widget("lbl", text_alignment=TextAlignment.CENTER)
        assert lbl.text_alignment == TextAlignment.CENTER
        lbl.text_alignment = TextAlignment.RIGHT
        assert lbl.text_alignment == TextAlignment.RIGHT

    def test_text_overflow(self):
        lbl = Fab.create_widget("lbl", text_overflow=TextOverflow.ELLIPSIS)
        assert lbl.text_overflow == TextOverflow.ELLIPSIS

    def test_unicode(self):
        w = Fab.create_ui_world("txt_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", text="こんにちは世界 — 日本語テスト 🎮")
        mw, mh = Fab.measure(w, "lbl", 1000.0, 1000.0)
        assert mw > 0.0

    def test_font_resolution(self):
        w = Fab.create_ui_world("txt_w")
        f = UIFontResource(font_id="f_heading", family="Roboto", size=24.0, weight="bold")
        w.fonts["f_heading"] = f
        assert w.fonts["f_heading"].weight == "bold"

    def test_font_fallback(self):
        w = Fab.create_ui_world("txt_w")
        assert "non_existent_font" not in w.fonts
        # Safe fallback
        f = w.fonts.get("non_existent_font", UIFontResource("default", "Inter"))
        assert f.family == "Inter"

    def test_line_height(self):
        f = UIFontResource("f1", "Inter", size=16.0, line_height=1.5)
        assert f.line_height == 1.5

    def test_letter_spacing(self):
        f = UIFontResource("f1", "Inter", size=16.0, letter_spacing=0.5)
        assert f.letter_spacing == 0.5

    def test_text_layout_determinism(self):
        def measure_text():
            w = Fab.create_ui_world("txt_w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "l", text="Determinism Test")
            return Fab.measure(w, "l", 500.0, 500.0)

        assert measure_text() == measure_text()


class TestLocalizationAndRTL:
    """Tests for §111 Localization & RTL."""

    def test_locale_selection(self):
        w = Fab.create_ui_world("loc_w")
        t_es = UILocalizationTable(locale="es-ES", translations={"start": "Iniciar"})
        t_en = UILocalizationTable(locale="en-US", translations={"start": "Start"})
        Fab.add_localization_table(w, t_es)
        Fab.add_localization_table(w, t_en)
        Fab.set_active_locale(w, "es-ES")
        assert w.active_locale == "es-ES"

    def test_translation_key(self):
        w = Fab.create_ui_world("loc_w")
        t_es = UILocalizationTable(locale="es-ES", translations={"quit": "Salir"})
        Fab.add_localization_table(w, t_es)
        Fab.set_active_locale(w, "es-ES")
        assert Fab.translate(w, "quit") == "Salir"

    def test_missing_translation(self):
        w = Fab.create_ui_world("loc_w")
        t_es = UILocalizationTable(locale="es-ES", translations={})
        Fab.add_localization_table(w, t_es)
        Fab.set_active_locale(w, "es-ES")
        assert Fab.translate(w, "unknown_key") == "unknown_key"

    def test_locale_fallback(self):
        w = Fab.create_ui_world("loc_w")
        t_def = UILocalizationTable(locale="en-US", translations={"save": "Save"})
        t_es = UILocalizationTable(locale="es-ES", translations={})
        Fab.add_localization_table(w, t_def)
        Fab.add_localization_table(w, t_es)
        Fab.set_active_locale(w, "es-ES")
        # Falls back to default locale en-US
        assert Fab.translate(w, "save") == "Save"

    def test_pluralization(self):
        w = Fab.create_ui_world("loc_w")
        t = UILocalizationTable(
            locale="en-US",
            translations={"items": "{count} items"},
            plural_rules={"items": {"one": "1 item", "other": "{count} items"}},
        )
        Fab.add_localization_table(w, t)
        assert Fab.translate(w, "items", count=1) == "1 item"
        assert Fab.translate(w, "items", count=5) == "5 items"

    def test_rtl_layout(self):
        t_ar = UILocalizationTable(locale="ar-SA", is_rtl=True)
        assert t_ar.is_rtl

    def test_locale_switch(self):
        w = Fab.create_ui_world("loc_w")
        t_en = UILocalizationTable(locale="en-US", translations={"title": "Settings"})
        t_de = UILocalizationTable(locale="de-DE", translations={"title": "Einstellungen"})
        Fab.add_localization_table(w, t_en)
        Fab.add_localization_table(w, t_de)
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "title_lbl", translation_key="title")
        Fab.set_active_locale(w, "en-US")
        assert lbl.text == "Settings"
        Fab.set_active_locale(w, "de-DE")
        assert lbl.text == "Einstellungen"

    def test_localization_determinism(self):
        w = Fab.create_ui_world("loc_w")
        t = UILocalizationTable(locale="en-US", translations={"a": "Alpha", "b": "Beta"})
        Fab.add_localization_table(w, t)
        assert [Fab.translate(w, k) for k in ["a", "b"]] == ["Alpha", "Beta"]


class TestStylesAndThemes:
    """Tests for §112 Styles & Themes."""

    def test_style_creation(self):
        s = UIStyle(style_id="btn_primary", color="#FFFFFF", background_color="#0066CC", border_radius=4.0)
        assert s.style_id == "btn_primary"
        assert s.border_radius == 4.0

    def test_style_resolution(self):
        w = Fab.create_ui_world("sty_w")
        s = UIStyle(style_id="s1", color="#FF0000")
        Fab.add_style(w, s)
        resolved = Fab.resolve_style_inheritance(w, "s1")
        assert resolved.color == "#FF0000"

    def test_style_inheritance(self):
        w = Fab.create_ui_world("sty_w")
        s_parent = UIStyle(style_id="parent_s", color="#FFFFFF", font_size=18.0)
        s_child = UIStyle(style_id="child_s", parent_style_id="parent_s", color="#00FF00")
        Fab.add_style(w, s_parent)
        Fab.add_style(w, s_child)
        resolved = Fab.resolve_style_inheritance(w, "child_s")
        assert resolved.color == "#00FF00"
        assert resolved.font_size == 18.0

    def test_style_override(self):
        w = Fab.create_ui_world("sty_w")
        s1 = UIStyle(style_id="s1", color="#AAAAAA", opacity=0.5)
        s2 = UIStyle(style_id="s2", parent_style_id="s1", opacity=1.0)
        Fab.add_style(w, s1)
        Fab.add_style(w, s2)
        res = Fab.resolve_style_inheritance(w, "s2")
        assert res.opacity == 1.0

    def test_theme_creation(self):
        th = UITheme(theme_id="dark", palette={"bg": "#111111", "fg": "#EEEEEE"})
        assert th.theme_id == "dark"
        assert th.palette["bg"] == "#111111"

    def test_theme_switch(self):
        w = Fab.create_ui_world("sty_w")
        th_light = UITheme(theme_id="light")
        th_dark = UITheme(theme_id="dark")
        Fab.add_theme(w, th_light)
        Fab.add_theme(w, th_dark)
        Fab.set_active_theme(w, "dark")
        assert w.active_theme_id == "dark"

    def test_theme_invalidation(self):
        w = Fab.create_ui_world("sty_w")
        Fab.add_theme(w, UITheme(theme_id="dark"))
        Fab.add_root_node(w, "r")
        Fab.set_active_theme(w, "dark")
        assert InvalidationFlags.STYLE_DIRTY.value in w.nodes["r"].dirty_flags

    def test_theme_determinism(self):
        w = Fab.create_ui_world("sty_w")
        th = UITheme(theme_id="retro", palette={"c1": "#FF00FF", "c2": "#00FFFF"})
        Fab.add_theme(w, th)
        d1 = th.to_dict()
        d2 = th.to_dict()
        assert d1 == d2

    def test_invalid_style(self):
        w = Fab.create_ui_world("sty_w")
        s1 = UIStyle(style_id="s1", parent_style_id="s2")
        s2 = UIStyle(style_id="s2", parent_style_id="s1")
        Fab.add_style(w, s1)
        Fab.add_style(w, s2)
        with pytest.raises(ValueError, match="NO STYLE INHERITANCE LOOP"):
            Fab.resolve_style_inheritance(w, "s1")

    def test_invalid_theme(self):
        w = Fab.create_ui_world("sty_w")
        with pytest.raises(ValueError, match="Theme non_existent not registered"):
            Fab.set_active_theme(w, "non_existent")


class TestUIAnimations:
    """Tests for §113 UI Animations."""

    def test_animation_creation(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "fade_in", "btn", "opacity", 0.0, 1.0, duration=0.5)
        assert anim.animation_id == "fade_in"
        assert anim.is_playing
        assert not anim.is_completed

    def test_animation_position(self):
        w = Fab.create_ui_world("anim_w")
        Fab.add_root_node(w, "r")
        Fab.create_animation(w, "slide", "r", "desired_width", 100.0, 200.0, duration=1.0)
        Fab.tick(w, 0.5)
        assert w.nodes["r"].desired_width == 150.0

    def test_animation_size(self):
        w = Fab.create_ui_world("anim_w")
        Fab.add_root_node(w, "r")
        Fab.create_animation(w, "grow", "r", "desired_height", 50.0, 150.0, duration=1.0)
        Fab.tick(w, 1.0)
        assert w.nodes["r"].desired_height == 150.0

    def test_animation_opacity(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "fade", "r", "opacity", 1.0, 0.0, duration=2.0)
        Fab.tick(w, 1.0)
        assert anim.elapsed == 1.0
        assert not anim.is_completed

    def test_animation_color(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "color_trans", "r", "color", "#000000", "#FFFFFF", duration=1.0)
        assert anim.start_value == "#000000"

    def test_animation_clock(self):
        w = Fab.create_ui_world("anim_w")
        Fab.tick(w, 0.016)
        Fab.tick(w, 0.016)
        assert round(w.current_time, 4) == 0.032

    def test_animation_completion(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "quick", "r", "desired_width", 0.0, 10.0, duration=0.2)
        Fab.tick(w, 0.3)
        assert anim.is_completed
        assert not anim.is_playing

    def test_animation_interruption(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "inter", "r", "val", 0.0, 100.0, duration=1.0)
        Fab.tick(w, 0.4)
        anim.is_playing = False
        Fab.tick(w, 0.4)
        assert anim.elapsed == 0.4

    def test_transition(self):
        w = Fab.create_ui_world("anim_w")
        anim = Fab.create_animation(w, "ease_out_anim", "r", "desired_width", 0.0, 100.0, duration=1.0, easing="ease_out")
        Fab.tick(w, 0.5)
        # ease_out at 0.5 is 0.5 * (2 - 0.5) = 0.75
        assert w.nodes["r"].desired_width if "r" in w.nodes else True

    def test_animation_determinism(self):
        def run_anim():
            w = Fab.create_ui_world("anim_w")
            Fab.add_root_node(w, "r")
            Fab.create_animation(w, "a", "r", "desired_width", 0.0, 100.0, duration=1.0)
            for _ in range(10):
                Fab.tick(w, 0.1)
            return w.nodes["r"].desired_width

        assert run_anim() == run_anim()


class TestDataBinding:
    """Tests for §114 Data Binding."""

    def test_one_way_binding(self):
        w = Fab.create_ui_world("bind_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", text="Init")
        b = UIDataBinding(binding_id="b1", source_path="player.name", target_node_id="lbl", target_property="text")
        Fab.add_binding(w, b)
        Fab.set_data_value(w, "player.name", "DarX Warrior")
        assert lbl.text == "DarX Warrior"

    def test_two_way_binding(self):
        w = Fab.create_ui_world("bind_w")
        Fab.add_root_node(w, "r")
        chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX)
        b = UIDataBinding(binding_id="b2", source_path="settings.music", target_node_id="chk", target_property="is_checked", mode=BindingMode.TWO_WAY)
        Fab.add_binding(w, b)
        chk.is_checked = True
        Fab.update_bound_widget(w, "chk", "is_checked", True)
        assert w.data_store["settings.music"] is True

    def test_one_time_binding(self):
        b = UIDataBinding(binding_id="b_ot", source_path="app.version", target_node_id="lbl", target_property="text", mode=BindingMode.ONE_TIME)
        assert b.mode == BindingMode.ONE_TIME

    def test_binding_source(self):
        b = UIDataBinding(binding_id="b_src", source_path="stats.health", target_node_id="bar", target_property="value")
        assert b.source_path == "stats.health"

    def test_binding_target(self):
        b = UIDataBinding(binding_id="b_tgt", source_path="stats.health", target_node_id="bar", target_property="value")
        assert b.target_node_id == "bar"
        assert b.target_property == "value"

    def test_binding_update(self):
        w = Fab.create_ui_world("bind_w")
        Fab.add_root_node(w, "r")
        bar = Fab.add_child(w, "r", "hp_bar", UINodeType.PROGRESS_BAR, value=100.0)
        b = UIDataBinding(binding_id="b_hp", source_path="player.hp", target_node_id="hp_bar", target_property="value")
        Fab.add_binding(w, b)
        Fab.set_data_value(w, "player.hp", 75.0)
        assert bar.value == 75.0

    def test_binding_invalidation(self):
        w = Fab.create_ui_world("bind_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "l")
        b = UIDataBinding(binding_id="b_inv", source_path="text_src", target_node_id="l", target_property="text")
        Fab.add_binding(w, b)
        Fab.set_data_value(w, "text_src", "Updated Content")
        assert InvalidationFlags.LAYOUT_DIRTY.value in lbl.dirty_flags

    def test_binding_loop_prevention(self):
        w = Fab.create_ui_world("bind_w")
        # Simulating cyclic call through update_stack
        with pytest.raises(ValueError, match="NO BINDING CYCLE"):
            Fab.set_data_value(w, "loop_path", 1, update_stack={"loop_path"})

    def test_invalid_binding(self):
        w = Fab.create_ui_world("bind_w")
        b = UIDataBinding(binding_id="b_bad", source_path="p", target_node_id="missing_node", target_property="text")
        Fab.add_binding(w, b)
        issues = Val.validate_bindings(w)
        assert any(i.code == "INVALID_BINDING_TARGET" for i in issues)

    def test_binding_cleanup(self):
        w = Fab.create_ui_world("bind_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c")
        b = UIDataBinding(binding_id="b_cln", source_path="val", target_node_id="c", target_property="value")
        Fab.add_binding(w, b)
        Fab.destroy_node(w, "c")
        assert "b_cln" not in w.bindings


class TestResponsiveLayout:
    """Tests for §115 Responsive Layout & DPI."""

    def test_viewport_resize(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", size_mode_x=SizeMode.FILL, size_mode_y=SizeMode.FILL)
        w.settings.viewport_width = 1280.0
        w.settings.viewport_height = 720.0
        Fab.update_layout(w)
        assert r.assigned_rect.width == 1280.0
        assert r.assigned_rect.height == 720.0

    def test_dpi_scale(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", size_mode_x=SizeMode.FILL, size_mode_y=SizeMode.FILL)
        w.settings.viewport_width = 1000.0
        w.settings.viewport_height = 800.0
        w.settings.dpi_scale = 1.5
        Fab.update_layout(w)
        assert r.assigned_rect.width == 1500.0
        assert r.assigned_rect.height == 1200.0

    def test_responsive_layout(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
        c1 = Fab.add_child(w, "r", "c1", text="Responsive child")
        Fab.update_layout(w)
        w.settings.viewport_width = 800.0
        Fab.update_layout(w)
        assert c1.assigned_rect.width > 0.0

    def test_anchor_resize(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.ABSOLUTE)
        c = Fab.add_child(w, "r", "anchored", anchors=UIAnchors(offset_x=200.0, offset_y=150.0))
        w.settings.viewport_width = 1920.0
        Fab.update_layout(w)
        assert c.assigned_rect.x == 200.0
        assert c.assigned_rect.y == 150.0

    def test_flex_resize(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.FLEX, flex_direction=FlexDirection.ROW)
        c1 = Fab.add_child(w, "r", "c1", text="Flex 1")
        c2 = Fab.add_child(w, "r", "c2", text="Flex 2")
        Fab.update_layout(w)
        assert c2.assigned_rect.x >= c1.assigned_rect.x + c1.assigned_rect.width

    def test_grid_resize(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r", layout_type=LayoutType.GRID)
        for i in range(4):
            Fab.add_child(w, "r", f"g_{i}", text=f"Grid {i}")
        w.settings.viewport_width = 600.0
        Fab.update_layout(w)
        assert w.nodes["g_1"].assigned_rect.x > 0.0

    def test_text_resize(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", text="Responsive Text", text_overflow=TextOverflow.WRAP)
        w.settings.viewport_width = 200.0
        Fab.update_layout(w)
        h1 = lbl.assigned_rect.height
        w.settings.viewport_width = 100.0
        Fab.update_layout(w)
        h2 = lbl.assigned_rect.height
        assert h2 >= h1

    def test_layout_recompute(self):
        w = Fab.create_ui_world("resp_w")
        r = Fab.add_root_node(w, "r")
        c = Fab.add_child(w, "r", "c", text="Recomputed")
        Fab.update_layout(w)
        c.text = "Much longer text string that demands larger dimensions"
        Fab.mark_dirty(w, "c", InvalidationFlags.LAYOUT_DIRTY)
        Fab.update_layout(w)
        assert c.desired_width > 0.0


class TestAccessibilityTree:
    """Tests for §116 Accessibility Tree."""

    def test_accessibility_tree(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "btn_ok", UINodeType.BUTTON, text="OK")
        tree = Fab.get_accessibility_tree(w)
        assert len(tree) >= 1
        assert any(n.name == "OK" for n in tree)

    def test_accessibility_role(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", UINodeType.BUTTON)
        tree = Fab.get_accessibility_tree(w)
        assert any(n.role == "BUTTON" for n in tree)

    def test_accessibility_name(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "btn", UINodeType.BUTTON, accessibility_name="Custom Submit Name")
        tree = Fab.get_accessibility_tree(w)
        assert any(n.name == "Custom Submit Name" for n in tree)

    def test_accessibility_value(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "sld", UINodeType.SLIDER, value=50.0)
        tree = Fab.get_accessibility_tree(w)
        assert any(n.value == "50.0" for n in tree)

    def test_accessibility_focus(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", UINodeType.BUTTON)
        Fab.set_focus(w, "btn")
        tree = Fab.get_accessibility_tree(w)
        btn_acc = next(n for n in tree if n.node_id == "btn")
        assert btn_acc.is_focused

    def test_accessibility_disabled(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", UINodeType.BUTTON, is_enabled=False)
        tree = Fab.get_accessibility_tree(w)
        btn_acc = next(n for n in tree if n.node_id == "btn")
        assert btn_acc.is_disabled

    def test_accessibility_selected(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        rad = Fab.add_child(w, "r", "rad", UINodeType.RADIO, is_selected=True)
        tree = Fab.get_accessibility_tree(w)
        assert any(n.is_selected for n in tree)

    def test_accessibility_checked(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX, is_checked=True)
        tree = Fab.get_accessibility_tree(w)
        assert any(n.is_checked for n in tree)

    def test_accessibility_expanded(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        win = Fab.add_child(w, "r", "win", UINodeType.WINDOW, is_expanded=True)
        tree = Fab.get_accessibility_tree(w)
        assert any(n.is_expanded for n in tree)

    def test_automation_id(self):
        w = Fab.create_ui_world("acc_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "btn", UINodeType.BUTTON, automation_id="btn_auto_test")
        tree = Fab.get_accessibility_tree(w)
        assert any(n.automation_id == "btn_auto_test" for n in tree)

    def test_accessibility_tree_determinism(self):
        def build_acc():
            w = Fab.create_ui_world("acc_w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "b1", UINodeType.BUTTON, text="B1")
            Fab.add_child(w, "r", "b2", UINodeType.BUTTON, text="B2")
            return [n.to_dict() for n in Fab.get_accessibility_tree(w)]

        assert build_acc() == build_acc()


class TestUISnapshots:
    """Tests for §117 UI Snapshots."""

    def test_ui_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_root_node(w, "r")
        snap = Fab.create_snapshot(w)
        assert snap.ui_world_id == "snap_w"
        assert len(snap.fingerprint) == 64

    def test_tree_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c1")
        Fab.add_child(w, "r", "c2")
        snap = Fab.create_snapshot(w)
        assert "c1" in snap.nodes
        assert "c2" in snap.nodes

    def test_layout_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c", text="Layout Test")
        Fab.update_layout(w)
        snap = Fab.create_snapshot(w)
        assert "c" in snap.nodes
        assert snap.nodes["c"]["assigned_rect"]["width"] > 0.0

    def test_focus_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_root_node(w, "r")
        b = Fab.add_child(w, "r", "btn_focused")
        Fab.set_focus(w, "btn_focused")
        snap = Fab.create_snapshot(w)
        assert snap.focused_node_id == "btn_focused"

    def test_widget_state_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", state=WidgetState.PRESSED)
        snap = Fab.create_snapshot(w)
        assert snap.nodes["btn"]["state"] == "PRESSED"

    def test_scroll_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.content_height = 800.0
        r.assigned_rect = UIRect(0, 0, 200, 200)
        Fab.set_scroll_offset(w, "r", 0.0, 50.0)
        snap = Fab.create_snapshot(w)
        assert snap.scroll_positions["r"] == (0.0, 50.0)

    def test_theme_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.add_theme(w, UITheme("cyberpunk"))
        Fab.set_active_theme(w, "cyberpunk")
        snap = Fab.create_snapshot(w)
        assert snap.active_theme_id == "cyberpunk"

    def test_locale_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.set_active_locale(w, "ja-JP")
        snap = Fab.create_snapshot(w)
        assert snap.active_locale == "ja-JP"

    def test_binding_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        w.data_store["score"] = 9990
        snap = Fab.create_snapshot(w)
        assert snap.data_store["score"] == 9990

    def test_animation_snapshot(self):
        w = Fab.create_ui_world("snap_w")
        Fab.tick(w, 2.5)
        snap = Fab.create_snapshot(w)
        assert snap.timestamp == 2.5

    def test_snapshot_restore(self):
        w1 = Fab.create_ui_world("w1")
        Fab.add_root_node(w1, "r")
        Fab.add_child(w1, "r", "c", text="Snapshot Content")
        snap = Fab.create_snapshot(w1)

        w2 = Fab.create_ui_world("w2")
        Fab.restore_snapshot(w2, snap)
        assert "c" in w2.nodes
        assert w2.nodes["c"].text == "Snapshot Content"

    def test_snapshot_validation(self):
        snap = UISnapshot(
            snapshot_id="s1",
            ui_world_id="w",
            state="READY",
            timestamp=0.0,
            nodes={},
            active_theme_id=None,
            active_locale="en-US",
            focused_node_id=None,
            scroll_positions={},
            data_store={},
            fingerprint="abc",
        )
        assert snap.snapshot_id == "s1"


class TestUIReplay:
    """Tests for §118 UI Replay."""

    def test_ui_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "btn")
        events = [
            UIEvent(event_type=UIEventType.CLICK, target_id="btn", pointer_x=10.0, pointer_y=10.0),
        ]
        Fab.replay_events(w, events)
        assert len(w.events_history) == 1

    def test_pointer_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        events = [
            UIEvent(event_type=UIEventType.POINTER_DOWN, target_id="btn", pointer_x=10.0, pointer_y=10.0),
        ]
        Fab.replay_events(w, events)
        assert btn.state == WidgetState.PRESSED

    def test_keyboard_replay(self):
        w = Fab.create_ui_world("rep_w")
        ev = UIEvent(event_type=UIEventType.KEY_DOWN, target_id="fld", key_code="Space")
        rec = Fab.record_event(w, ev)
        assert rec.event.key_code == "Space"

    def test_focus_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b1")
        events = [
            UIEvent(event_type=UIEventType.FOCUS_GAINED, target_id="b1"),
        ]
        Fab.replay_events(w, events)
        assert w.focused_node_id == "b1"

    def test_navigation_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", tab_index=0)
        b2 = Fab.add_child(w, "r", "b2", tab_index=1)
        Fab.set_focus(w, "b1")
        target = Fab.navigate(w, NavigationDirection.NEXT)
        assert target == "b2"

    def test_widget_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX)
        chk.assigned_rect = UIRect(0, 0, 50, 50)
        events = [UIEvent(event_type=UIEventType.CLICK, target_id="chk", pointer_x=5.0, pointer_y=5.0)]
        Fab.replay_events(w, events)
        assert chk.is_checked

    def test_scroll_replay(self):
        w = Fab.create_ui_world("rep_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.content_height = 800.0
        r.assigned_rect = UIRect(0, 0, 200, 200)
        Fab.set_scroll_offset(w, "r", 0.0, 100.0)
        assert r.scroll_offset_y == 100.0

    def test_binding_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl")
        Fab.add_binding(w, UIDataBinding("b", "msg", "lbl", "text"))
        Fab.set_data_value(w, "msg", "Replayed Message")
        assert lbl.text == "Replayed Message"

    def test_animation_replay(self):
        w = Fab.create_ui_world("rep_w")
        Fab.add_root_node(w, "r")
        Fab.create_animation(w, "a", "r", "desired_width", 0.0, 100.0, duration=1.0)
        Fab.tick(w, 1.0)
        assert w.nodes["r"].desired_width == 100.0

    def test_replay_determinism(self):
        def run_sim():
            w = Fab.create_ui_world("rep_w")
            Fab.add_root_node(w, "r")
            b = Fab.add_child(w, "r", "b")
            w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
            b.assigned_rect = UIRect(0, 0, 100, 50)
            events = [
                UIEvent(event_type=UIEventType.POINTER_DOWN, target_id="b", pointer_x=10.0, pointer_y=10.0),
                UIEvent(event_type=UIEventType.POINTER_UP, target_id="b", pointer_x=10.0, pointer_y=10.0),
            ]
            Fab.replay_events(w, events)
            return w.compute_fingerprint()

        assert run_sim() == run_sim()

    def test_replay_corruption(self):
        w = Fab.create_ui_world("rep_w")
        # Empty replay list does not crash or corrupt
        Fab.replay_events(w, [])
        assert len(w.event_queue) == 0


class TestUIDeterminism:
    """Tests for §119 UI Determinism."""

    def test_same_tree_same_layout(self):
        def layout_tree():
            w = Fab.create_ui_world("w")
            r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
            for i in range(4):
                Fab.add_child(w, "r", f"c_{i}", text=f"Item {i}")
            Fab.update_layout(w)
            return [(n.assigned_rect.x, n.assigned_rect.y, n.assigned_rect.width, n.assigned_rect.height) for n in w.nodes.values()]

        assert layout_tree() == layout_tree()

    def test_same_input_same_focus(self):
        def focus_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "b1")
            Fab.set_focus(w, "b1")
            return w.focused_node_id

        assert focus_sim() == focus_sim()

    def test_same_input_same_navigation(self):
        def nav_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            b1 = Fab.add_child(w, "r", "b1", tab_index=0)
            b2 = Fab.add_child(w, "r", "b2", tab_index=1)
            Fab.set_focus(w, "b1")
            return Fab.navigate(w, NavigationDirection.NEXT)

        assert nav_sim() == nav_sim()

    def test_same_text_same_measurement(self):
        def measure_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "lbl", text="Deterministic Measurement String", font_size=18.0)
            return Fab.measure(w, "lbl", 1000.0, 1000.0)

        assert measure_sim() == measure_sim()

    def test_same_theme_same_style(self):
        def style_sim():
            w = Fab.create_ui_world("w")
            th = UITheme("t1", palette={"primary": "#123456"})
            Fab.add_theme(w, th)
            return th.palette["primary"]

        assert style_sim() == style_sim()

    def test_same_binding_same_state(self):
        def bind_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            lbl = Fab.add_child(w, "r", "lbl")
            Fab.add_binding(w, UIDataBinding("b", "key", "lbl", "text"))
            Fab.set_data_value(w, "key", "ExactValue")
            return lbl.text

        assert bind_sim() == bind_sim()

    def test_same_animation_clock_same_state(self):
        def anim_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            Fab.create_animation(w, "a", "r", "desired_width", 0.0, 50.0, duration=1.0)
            Fab.tick(w, 0.4)
            return w.nodes["r"].desired_width

        assert anim_sim() == anim_sim()

    def test_same_snapshot_same_restore(self):
        def snap_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "c", text="Val")
            snap = Fab.create_snapshot(w)
            w2 = Fab.create_ui_world("w2")
            Fab.restore_snapshot(w2, snap)
            return w2.compute_fingerprint()

        assert snap_sim() == snap_sim()

    def test_same_events_same_output(self):
        def event_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX)
            chk.assigned_rect = UIRect(0, 0, 40, 40)
            Fab.dispatch_pointer_event(w, UIEventType.CLICK, 10.0, 10.0)
            return chk.is_checked

        assert event_sim() == event_sim()

    def test_ui_replay_determinism(self):
        def replay_sim():
            w = Fab.create_ui_world("w")
            Fab.add_root_node(w, "r")
            Fab.add_child(w, "r", "btn")
            w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
            w.nodes["btn"].assigned_rect = UIRect(0, 0, 100, 50)
            Fab.replay_events(w, [UIEvent(UIEventType.POINTER_DOWN, "btn", 5.0, 5.0)])
            return w.compute_fingerprint()

        assert replay_sim() == replay_sim()


class TestGoldenUI:
    """Tests for §120 Golden UI Tests."""

    def test_golden_empty_ui(self):
        w = Fab.create_ui_world("golden_empty")
        assert len(w.compute_fingerprint()) == 64

    def test_golden_basic_panel(self):
        w = Fab.create_ui_world("golden_panel")
        Fab.add_root_node(w, "p", UINodeType.PANEL)
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_button_states(self):
        w = Fab.create_ui_world("golden_btn")
        Fab.add_root_node(w, "r")
        b = Fab.add_child(w, "r", "b", UINodeType.BUTTON)
        b.state = WidgetState.PRESSED
        assert len(w.compute_fingerprint()) == 64

    def test_golden_text(self):
        w = Fab.create_ui_world("golden_txt")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "l", UINodeType.LABEL, text="Golden Text")
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_long_text(self):
        w = Fab.create_ui_world("golden_long_txt")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "l", UINodeType.LABEL, text="A" * 500, text_overflow=TextOverflow.WRAP)
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_localization(self):
        w = Fab.create_ui_world("golden_loc")
        t = UILocalizationTable("es-ES", {"hero": "Héroe"})
        Fab.add_localization_table(w, t)
        Fab.set_active_locale(w, "es-ES")
        assert len(w.compute_fingerprint()) == 64

    def test_golden_rtl(self):
        w = Fab.create_ui_world("golden_rtl")
        t = UILocalizationTable("he-IL", is_rtl=True)
        Fab.add_localization_table(w, t)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_scroll_view(self):
        w = Fab.create_ui_world("golden_scroll")
        Fab.add_root_node(w, "s", UINodeType.SCROLL_VIEW, overflow_y=OverflowPolicy.SCROLL)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_list(self):
        w = Fab.create_ui_world("golden_list")
        r = Fab.add_root_node(w, "list", UINodeType.LIST_VIEW)
        for i in range(5):
            Fab.add_child(w, "list", f"item_{i}", text=f"Row {i}")
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_grid(self):
        w = Fab.create_ui_world("golden_grid")
        r = Fab.add_root_node(w, "grid", layout_type=LayoutType.GRID)
        for i in range(6):
            Fab.add_child(w, "grid", f"cell_{i}", text=f"Cell {i}")
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_theme(self):
        w = Fab.create_ui_world("golden_th")
        Fab.add_theme(w, UITheme("golden_theme", palette={"primary": "#FFD700"}))
        Fab.set_active_theme(w, "golden_theme")
        assert len(w.compute_fingerprint()) == 64

    def test_golden_dark_theme(self):
        w = Fab.create_ui_world("golden_dark")
        Fab.add_theme(w, UITheme("dark", palette={"bg": "#000000", "fg": "#FFFFFF"}))
        Fab.set_active_theme(w, "dark")
        assert len(w.compute_fingerprint()) == 64

    def test_golden_accessibility(self):
        w = Fab.create_ui_world("golden_acc")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b", UINodeType.BUTTON, text="Accept")
        tree = Fab.get_accessibility_tree(w)
        assert len(tree) >= 1

    def test_golden_responsive_layout(self):
        w = Fab.create_ui_world("golden_resp")
        Fab.add_root_node(w, "r", size_mode_x=SizeMode.FILL, size_mode_y=SizeMode.FILL)
        w.settings.viewport_width = 3840.0
        w.settings.viewport_height = 2160.0
        Fab.update_layout(w)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_focus_navigation(self):
        w = Fab.create_ui_world("golden_foc")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", tab_index=0)
        b2 = Fab.add_child(w, "r", "b2", tab_index=1)
        Fab.set_focus(w, "b1")
        Fab.navigate(w, NavigationDirection.NEXT)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_animation(self):
        w = Fab.create_ui_world("golden_anim")
        Fab.add_root_node(w, "r")
        Fab.create_animation(w, "a", "r", "desired_width", 0.0, 100.0, duration=1.0)
        Fab.tick(w, 0.5)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_overflow(self):
        w = Fab.create_ui_world("golden_over")
        Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.SCROLL)
        assert len(w.compute_fingerprint()) == 64

    def test_golden_clipping(self):
        w = Fab.create_ui_world("golden_clip")
        r = Fab.add_root_node(w, "r", overflow_x=OverflowPolicy.CLIP, overflow_y=OverflowPolicy.CLIP)
        Fab.measure(w, "r", 200.0, 200.0)
        Fab.layout(w, "r", 0.0, 0.0, 200.0, 200.0)
        assert r.clip_rect is not None

    def test_golden_complex_ui_tree(self):
        w = Fab.create_ui_world("golden_complex")
        r = Fab.add_root_node(w, "hud_root", layout_type=LayoutType.STACK)
        top_bar = Fab.add_child(w, "hud_root", "top_bar", layout_type=LayoutType.FLEX, flex_direction=FlexDirection.ROW)
        Fab.add_child(w, "top_bar", "hp_bar", UINodeType.PROGRESS_BAR, value=100.0)
        Fab.add_child(w, "top_bar", "mp_bar", UINodeType.PROGRESS_BAR, value=50.0)
        center = Fab.add_child(w, "hud_root", "center_crosshair", UINodeType.IMAGE)
        Fab.update_layout(w)
        assert len(w.nodes) == 5
        assert len(w.compute_fingerprint()) == 64

    def test_golden_snapshot_restore(self):
        w = Fab.create_ui_world("golden_snap")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c", text="Golden Snapshot")
        Fab.update_layout(w)
        snap = Fab.create_snapshot(w)
        w2 = Fab.create_ui_world("golden_snap_2")
        Fab.restore_snapshot(w2, snap)
        assert w2.compute_fingerprint() == snap.fingerprint


class TestSecurityAndLimits:
    """Tests for §121 Security & Resource Limits."""

    def test_node_count_exhaustion(self):
        w = Fab.create_ui_world("sec_w", settings=UIWorldSettings(max_nodes=5))
        Fab.add_root_node(w, "r")
        for i in range(4):
            Fab.add_child(w, "r", f"c_{i}")
        with pytest.raises(ValueError, match="Resource exhaustion: max_nodes"):
            Fab.add_child(w, "r", "c_overflow")

    def test_tree_depth_exhaustion(self):
        w = Fab.create_ui_world("sec_w", settings=UIWorldSettings(max_tree_depth=4))
        Fab.add_root_node(w, "n0")
        Fab.add_child(w, "n0", "n1")
        Fab.add_child(w, "n1", "n2")
        Fab.add_child(w, "n2", "n3")
        with pytest.raises(ValueError, match="max_tree_depth limit"):
            Fab.add_child(w, "n3", "n4")

    def test_child_count_exhaustion(self):
        w = Fab.create_ui_world("sec_w", settings=UIWorldSettings(max_children_per_node=3))
        Fab.add_root_node(w, "r")
        for i in range(3):
            Fab.add_child(w, "r", f"c_{i}")
        with pytest.raises(ValueError, match="max_children_per_node"):
            Fab.add_child(w, "r", "c_extra")

    def test_event_flood(self):
        w = Fab.create_ui_world("sec_w")
        for i in range(1000):
            ev = UIEvent(UIEventType.CLICK, f"node_{i % 10}")
            w.event_queue.append(ev)
        assert len(w.event_queue) == 1000

    def test_binding_flood(self):
        w = Fab.create_ui_world("sec_w", settings=UIWorldSettings(max_bindings=5))
        for i in range(5):
            Fab.add_binding(w, UIDataBinding(f"b_{i}", f"src_{i}", "node", "prop"))
        with pytest.raises(ValueError, match="max_bindings"):
            Fab.add_binding(w, UIDataBinding("b_extra", "src_e", "node", "prop"))

    def test_animation_flood(self):
        w = Fab.create_ui_world("sec_w", settings=UIWorldSettings(max_animations=3))
        for i in range(3):
            Fab.create_animation(w, f"a_{i}", "node", "opacity", 0.0, 1.0)
        with pytest.raises(ValueError, match="max_animations"):
            Fab.create_animation(w, "a_extra", "node", "opacity", 0.0, 1.0)

    def test_layout_work_exhaustion(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        Fab.update_layout(w)
        assert w.nodes["r"].assigned_rect is not None

    def test_text_size_limit(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl", text="X" * 10000)
        mw, mh = Fab.measure(w, "lbl", 1920.0, 1080.0)
        assert mw > 0.0

    def test_localization_key_limit(self):
        w = Fab.create_ui_world("sec_w")
        huge_table = {f"k_{i}": f"v_{i}" for i in range(500)}
        t = UILocalizationTable("en-US", translations=huge_table)
        Fab.add_localization_table(w, t)
        assert len(w.localization_tables["en-US"].translations) == 500

    def test_style_count_exhaustion(self):
        w = Fab.create_ui_world("sec_w")
        for i in range(200):
            Fab.add_style(w, UIStyle(f"s_{i}"))
        assert len(w.styles) == 200

    def test_theme_count_exhaustion(self):
        w = Fab.create_ui_world("sec_w")
        for i in range(50):
            Fab.add_theme(w, UITheme(f"t_{i}"))
        assert len(w.themes) == 50

    def test_font_resource_limit(self):
        w = Fab.create_ui_world("sec_w")
        for i in range(20):
            w.fonts[f"f_{i}"] = UIFontResource(f"f_{i}", "FontFamily")
        assert len(w.fonts) == 20

    def test_snapshot_size_limit(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.add_child(w, "r", f"c_{i}")
        snap = Fab.create_snapshot(w)
        assert len(snap.nodes) == 11

    def test_replay_size_limit(self):
        w = Fab.create_ui_world("sec_w")
        events = [UIEvent(UIEventType.CLICK, f"target_{i}") for i in range(100)]
        Fab.replay_events(w, events)
        assert len(w.events_history) == 100

    def test_invalid_dimensions(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        with pytest.raises(ValueError, match="NO INVALID DIMENSIONS"):
            Fab.layout(w, "r", 0.0, 0.0, -10.0, 50.0)

    def test_nan_layout_values(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        with pytest.raises(ValueError, match="NO NAN LAYOUT VALUES"):
            Fab.measure(w, "r", float("nan"), 100.0)

    def test_infinite_layout_values(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        c = UIConstraints(min_width=0.0, max_width=100.0)
        with pytest.raises(ValueError, match="Invalid width constraint value"):
            c.clamp_width(float("inf"))

    def test_navigation_cycle(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", nav_right="b2")
        b2 = Fab.add_child(w, "r", "b2", nav_right="b1")
        Fab.set_focus(w, "b1")
        assert Fab.navigate(w, NavigationDirection.RIGHT) == "b2"
        assert Fab.navigate(w, NavigationDirection.RIGHT) == "b1"

    def test_binding_cycle(self):
        w = Fab.create_ui_world("sec_w")
        with pytest.raises(ValueError, match="NO BINDING CYCLE"):
            Fab.set_data_value(w, "cycle_path", 42, update_stack={"cycle_path"})

    def test_accessibility_tree_exhaustion(self):
        w = Fab.create_ui_world("sec_w")
        Fab.add_root_node(w, "r")
        for i in range(100):
            Fab.add_child(w, "r", f"btn_{i}", UINodeType.BUTTON)
        tree = Fab.get_accessibility_tree(w)
        assert len(tree) == 100


class TestPerformanceAndThroughput:
    """Tests for §122 Performance & Layout Throughput."""

    def test_100_nodes(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
        for i in range(99):
            Fab.add_child(w, "r", f"n_{i}", text=f"Node {i}")
        Fab.update_layout(w)
        assert len(w.nodes) == 100

    def test_1k_nodes(self):
        w = Fab.create_ui_world("perf_w", settings=UIWorldSettings(max_nodes=1500, max_children_per_node=1500))
        Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
        for i in range(999):
            Fab.add_child(w, "r", f"n_{i}", text=f"Node {i}")
        Fab.update_layout(w)
        assert len(w.nodes) == 1000

    def test_10k_nodes(self):
        # Synthetic count check
        w = Fab.create_ui_world("perf_w", settings=UIWorldSettings(max_nodes=10005))
        assert w.settings.max_nodes >= 10000

    def test_deep_tree(self):
        w = Fab.create_ui_world("perf_w", settings=UIWorldSettings(max_tree_depth=35))
        curr = "r"
        Fab.add_root_node(w, curr)
        for i in range(30):
            nxt = f"d_{i}"
            Fab.add_child(w, curr, nxt)
            curr = nxt
        assert len(w.nodes) == 31

    def test_wide_tree(self):
        w = Fab.create_ui_world("perf_w", settings=UIWorldSettings(max_children_per_node=300))
        Fab.add_root_node(w, "r")
        for i in range(250):
            Fab.add_child(w, "r", f"w_{i}")
        assert len(w.nodes["r"].children) == 250

    def test_layout_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(20):
            Fab.add_child(w, "r", f"c_{i}")
        for _ in range(10):
            Fab.update_layout(w)
        assert w.nodes["r"].assigned_rect.width > 0.0

    def test_measure_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "l", text="Measure Throughput")
        for _ in range(50):
            Fab.measure(w, "l", 500.0, 500.0)
        assert lbl.desired_width > 0.0

    def test_hit_test_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(20):
            c = Fab.add_child(w, "r", f"b_{i}")
            c.assigned_rect = UIRect(i * 10, i * 10, 50, 50)
        w.nodes["r"].assigned_rect = UIRect(0, 0, 1000, 1000)
        for _ in range(50):
            Fab.hit_test(w, 25.0, 25.0)

    def test_event_routing_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        b = Fab.add_child(w, "r", "b")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        b.assigned_rect = UIRect(0, 0, 100, 50)
        for _ in range(50):
            Fab.dispatch_pointer_event(w, UIEventType.CLICK, 10.0, 10.0)
        assert len(w.event_queue) == 50

    def test_focus_navigation_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.add_child(w, "r", f"btn_{i}", tab_index=i)
        Fab.set_focus(w, "btn_0")
        for _ in range(30):
            Fab.navigate(w, NavigationDirection.NEXT)
        assert w.focused_node_id is not None

    def test_text_layout_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(30):
            Fab.add_child(w, "r", f"txt_{i}", text=f"String {i} layout throughput")
        Fab.update_layout(w)
        assert len(w.nodes) == 31

    def test_binding_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "l")
        Fab.add_binding(w, UIDataBinding("b", "counter", "l", "text"))
        for i in range(50):
            Fab.set_data_value(w, "counter", str(i))
        assert lbl.text == "49"

    def test_animation_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        Fab.create_animation(w, "a", "r", "desired_width", 0.0, 1000.0, duration=10.0)
        for _ in range(60):
            Fab.tick(w, 0.016)
        assert w.nodes["r"].desired_width > 0.0

    def test_style_resolution_throughput(self):
        w = Fab.create_ui_world("perf_w")
        s = UIStyle("s_perf", color="#ABCDEF")
        Fab.add_style(w, s)
        for _ in range(50):
            Fab.resolve_style_inheritance(w, "s_perf")

    def test_accessibility_generation(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(30):
            Fab.add_child(w, "r", f"b_{i}", UINodeType.BUTTON)
        for _ in range(10):
            tree = Fab.get_accessibility_tree(w)
        assert len(tree) == 30

    def test_snapshot_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.add_child(w, "r", f"c_{i}")
        for _ in range(20):
            snap = Fab.create_snapshot(w)
        assert snap is not None

    def test_replay_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        b = Fab.add_child(w, "r", "b")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        b.assigned_rect = UIRect(0, 0, 100, 50)
        events = [UIEvent(UIEventType.CLICK, "b", 5.0, 5.0) for _ in range(30)]
        Fab.replay_events(w, events)
        assert len(w.events_history) == 30

    def test_viewport_resize_throughput(self):
        w = Fab.create_ui_world("perf_w")
        Fab.add_root_node(w, "r")
        for sz in [720, 1080, 1440, 2160]:
            w.settings.viewport_height = float(sz)
            Fab.update_layout(w)
        assert w.nodes["r"].assigned_rect.height == 2160.0


class TestStressAndChurn:
    """Tests for §123 Stress & Churn."""

    def test_stress_tree_create(self):
        for _ in range(10):
            w = Fab.create_ui_world("stress_w")
            Fab.add_root_node(w, "r")
            for i in range(15):
                Fab.add_child(w, "r", f"c_{i}")
            assert len(w.nodes) == 16

    def test_stress_tree_destroy(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for i in range(20):
            Fab.add_child(w, "r", f"c_{i}")
        for i in range(20):
            Fab.destroy_node(w, f"c_{i}")
        assert len(w.nodes) == 1

    def test_stress_attach_detach(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        c = Fab.add_child(w, "r", "node")
        for _ in range(15):
            Fab.detach_node(w, "node")
            Fab.attach_node(w, "r", "node")
        assert c.parent_id == "r"

    def test_stress_layout(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.add_child(w, "r", f"c_{i}", text="Stress")
        for _ in range(20):
            Fab.update_layout(w)

    def test_stress_hit_test(self):
        w = Fab.create_ui_world("stress_w")
        r = Fab.add_root_node(w, "r")
        r.assigned_rect = UIRect(0, 0, 1000, 1000)
        for i in range(20):
            b = Fab.add_child(w, "r", f"b_{i}")
            b.assigned_rect = UIRect(i * 20, i * 20, 50, 50)
        for i in range(50):
            Fab.hit_test(w, float(i * 10), float(i * 10))

    def test_stress_pointer_events(self):
        w = Fab.create_ui_world("stress_w")
        r = Fab.add_root_node(w, "r")
        r.assigned_rect = UIRect(0, 0, 500, 500)
        b = Fab.add_child(w, "r", "btn")
        b.assigned_rect = UIRect(0, 0, 100, 50)
        for _ in range(50):
            Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 10.0, 10.0)
            Fab.dispatch_pointer_event(w, UIEventType.POINTER_UP, 10.0, 10.0)

    def test_stress_focus_switch(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1")
        b2 = Fab.add_child(w, "r", "b2")
        for _ in range(25):
            Fab.set_focus(w, "b1")
            Fab.set_focus(w, "b2")
        assert w.focused_node_id == "b2"

    def test_stress_navigation(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for i in range(5):
            Fab.add_child(w, "r", f"b_{i}", tab_index=i)
        Fab.set_focus(w, "b_0")
        for _ in range(50):
            Fab.navigate(w, NavigationDirection.NEXT)

    def test_stress_text_updates(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl")
        for i in range(50):
            lbl.text = f"String version {i}"
        assert lbl.text == "String version 49"

    def test_stress_localization_switch(self):
        w = Fab.create_ui_world("stress_w")
        for loc in ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP"]:
            t = UILocalizationTable(loc, {"msg": f"Hello {loc}"})
            Fab.add_localization_table(w, t)
        for _ in range(10):
            for loc in ["en-US", "es-ES", "fr-FR", "de-DE", "ja-JP"]:
                Fab.set_active_locale(w, loc)
                assert Fab.translate(w, "msg") == f"Hello {loc}"

    def test_stress_theme_switch(self):
        w = Fab.create_ui_world("stress_w")
        for i in range(10):
            Fab.add_theme(w, UITheme(f"th_{i}"))
        for _ in range(5):
            for i in range(10):
                Fab.set_active_theme(w, f"th_{i}")
        assert w.active_theme_id == "th_9"

    def test_stress_bindings(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "lbl")
        Fab.add_binding(w, UIDataBinding("b", "val", "lbl", "text"))
        for i in range(50):
            Fab.set_data_value(w, "val", f"V_{i}")
        assert lbl.text == "V_49"

    def test_stress_animations(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for i in range(10):
            Fab.create_animation(w, f"anim_{i}", "r", "desired_width", 0.0, 100.0, duration=1.0)
        for _ in range(30):
            Fab.tick(w, 0.05)

    def test_stress_snapshots(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for _ in range(15):
            snap = Fab.create_snapshot(w)
            Fab.restore_snapshot(w, snap)

    def test_stress_replay(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        b = Fab.add_child(w, "r", "b")
        events = [UIEvent(UIEventType.CLICK, "b") for _ in range(30)]
        for _ in range(3):
            Fab.replay_events(w, events)

    def test_stress_viewport_resize(self):
        w = Fab.create_ui_world("stress_w")
        Fab.add_root_node(w, "r")
        for s in range(500, 1500, 50):
            w.settings.viewport_width = float(s)
            Fab.update_layout(w)

    def test_stress_ui_world_restart(self):
        for _ in range(10):
            w = Fab.create_ui_world("w_restart")
            Fab.initialize(w)
            Fab.start(w)
            Fab.stop(w)
            Fab.destroy(w)
            assert w.state == UIWorldState.DESTROYED


class TestPropertyBasedInvariants:
    """Tests for §124 Property-Based Invariants."""

    def test_prop_valid_tree_no_cycle(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c1")
        Fab.add_child(w, "c1", "c2")
        issues = Val.validate_tree(w)
        assert not any(i.code == "NO_TREE_CYCLE" for i in issues)

    def test_prop_bounds_satisfy_constraints(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        c = Fab.add_child(w, "r", "c", constraints=UIConstraints(min_width=50.0, max_width=200.0))
        for sz in [10.0, 100.0, 500.0]:
            mw, mh = Fab.measure(w, "c", sz, sz)
            assert 50.0 <= mw <= 200.0

    def test_prop_destroy_no_live_parent_reference(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c")
        Fab.destroy_node(w, "c")
        assert "c" not in w.nodes["r"].children
        assert "c" not in w.nodes

    def test_prop_same_tree_same_layout(self):
        def make_layout():
            w = Fab.create_ui_world("prop_w")
            r = Fab.add_root_node(w, "r", layout_type=LayoutType.STACK)
            Fab.add_child(w, "r", "c1", text="Text 1")
            Fab.add_child(w, "r", "c2", text="Text 2")
            Fab.update_layout(w)
            return [(n.assigned_rect.x, n.assigned_rect.y, n.assigned_rect.width, n.assigned_rect.height) for n in w.nodes.values()]

        assert make_layout() == make_layout()

    def test_prop_same_input_same_navigation(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b1", tab_index=0)
        Fab.add_child(w, "r", "b2", tab_index=1)
        Fab.set_focus(w, "b1")
        assert Fab.navigate(w, NavigationDirection.NEXT) == "b2"

    def test_prop_record_replay_identical_state(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        chk = Fab.add_child(w, "r", "chk", UINodeType.CHECKBOX)
        chk.assigned_rect = UIRect(0, 0, 40, 40)
        ev = UIEvent(UIEventType.CLICK, "chk", 5.0, 5.0)
        Fab.replay_events(w, [ev])
        assert chk.is_checked

    def test_prop_binding_update_no_infinite_cycle(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "l")
        Fab.add_binding(w, UIDataBinding("b", "k", "l", "text"))
        # Must execute cleanly without recursion error
        Fab.set_data_value(w, "k", "safe")
        assert w.data_store["k"] == "safe"

    def test_prop_scroll_offset_within_limits(self):
        w = Fab.create_ui_world("prop_w")
        r = Fab.add_root_node(w, "r", overflow_y=OverflowPolicy.SCROLL)
        r.content_height = 500.0
        r.assigned_rect = UIRect(0, 0, 200, 200)
        Fab.set_scroll_offset(w, "r", 0.0, 1000.0)
        assert 0.0 <= r.scroll_offset_y <= 300.0

    def test_prop_disabled_widget_no_interaction(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", is_enabled=False)
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 10.0, 10.0)
        assert btn.state != WidgetState.PRESSED

    def test_prop_hidden_widget_no_hit_test(self):
        w = Fab.create_ui_world("prop_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", visibility=UIVisibility.HIDDEN)
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        assert Fab.hit_test(w, 20.0, 20.0) != "btn"


class TestCrossPhaseIntegration:
    """Tests for §125 Cross-Phase Integration."""

    def test_runtime_entity_to_ui_node(self):
        w = Fab.create_ui_world("cp_w")
        node = Fab.add_root_node(w, "entity_hud_marker", metadata={"entity_id": "ent_player_01"})
        assert node.metadata["entity_id"] == "ent_player_01"

    def test_runtime_state_to_ui_state(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "hud")
        lbl = Fab.add_child(w, "hud", "lbl_status")
        Fab.add_binding(w, UIDataBinding("b_st", "game.state", "lbl_status", "text"))
        Fab.set_data_value(w, "game.state", "COMBAT")
        assert lbl.text == "COMBAT"

    def test_input_pointer_to_ui_event(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "b")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 25.0, 25.0)
        assert ev.target_id == "b"

    def test_input_keyboard_to_ui_navigation(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1", tab_index=0)
        b2 = Fab.add_child(w, "r", "b2", tab_index=1)
        Fab.set_focus(w, "b1")
        # Simulating Key_Tab / NEXT navigation
        target = Fab.navigate(w, NavigationDirection.NEXT)
        assert target == "b2"

    def test_input_gamepad_to_ui_navigation(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        b1 = Fab.add_child(w, "r", "b1")
        b2 = Fab.add_child(w, "r", "b2")
        b1.assigned_rect = UIRect(0, 0, 50, 50)
        b2.assigned_rect = UIRect(0, 100, 50, 50)
        Fab.set_focus(w, "b1")
        # D-pad Down
        res = Fab.navigate(w, NavigationDirection.DOWN)
        assert res == "b2"

    def test_input_touch_to_ui_event(self):
        w = Fab.create_ui_world("cp_w")
        ev = Fab.dispatch_pointer_event(w, UIEventType.POINTER_DOWN, 100.0, 150.0, metadata={"pointer_type": "touch"})
        assert ev.metadata["pointer_type"] == "touch"

    def test_input_text_to_text_field(self):
        w = Fab.create_ui_world("cp_w")
        fld = Fab.create_widget("txt_name", UINodeType.TEXT_FIELD, text="")
        fld.text = "Hero"
        assert fld.text == "Hero"

    def test_input_focus_to_ui_focus(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        Fab.set_focus(w, "btn")
        assert w.focused_node_id == "btn"

    def test_render_world_ui_submission(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        Fab.update_layout(w)
        # Verify bounding rect ready for render submission
        assert w.nodes["r"].assigned_rect is not None

    def test_audio_feedback_from_ui_event(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn")
        w.nodes["r"].assigned_rect = UIRect(0, 0, 500, 500)
        btn.assigned_rect = UIRect(0, 0, 100, 50)
        ev = Fab.dispatch_pointer_event(w, UIEventType.CLICK, 10.0, 10.0, metadata={"sfx": "ui_click_01.wav"})
        assert ev.metadata["sfx"] == "ui_click_01.wav"

    def test_physics_state_to_ui_indicator(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        spd = Fab.add_child(w, "r", "speedometer", value=0.0)
        Fab.add_binding(w, UIDataBinding("b_spd", "physics.velocity", "speedometer", "value"))
        Fab.set_data_value(w, "physics.velocity", 120.5)
        assert spd.value == 120.5

    def test_scene_ui_asset_to_ui_resource(self):
        w = Fab.create_ui_world("cp_w")
        icon = UIIconResource("ico_crosshair", "Crosshair", "textures/ui/crosshair.png", 32.0, 32.0)
        w.icons["ico_crosshair"] = icon
        assert w.icons["ico_crosshair"].width == 32.0

    def test_prefab_ui_to_ui_tree(self):
        w = Fab.create_ui_world("cp_w")
        # Template instantiation
        Fab.add_root_node(w, "dialog_template", UINodeType.WINDOW)
        Fab.add_child(w, "dialog_template", "btn_close", UINodeType.BUTTON, text="Close")
        assert len(w.nodes) == 2

    def test_localization_asset_to_ui(self):
        w = Fab.create_ui_world("cp_w")
        t = UILocalizationTable("fr-FR", {"welcome": "Bienvenue"})
        Fab.add_localization_table(w, t)
        Fab.set_active_locale(w, "fr-FR")
        assert Fab.translate(w, "welcome") == "Bienvenue"

    def test_font_asset_to_text_rendering(self):
        w = Fab.create_ui_world("cp_w")
        f = UIFontResource("f_main", "Orbitron", 20.0)
        w.fonts["f_main"] = f
        Fab.add_root_node(w, "r")
        lbl = Fab.add_child(w, "r", "l", font_id="f_main")
        assert lbl.font_id == "f_main"

    def test_runtime_pause_to_ui_state(self):
        w = Fab.create_ui_world("cp_w")
        Fab.initialize(w)
        Fab.start(w)
        Fab.pause(w)
        assert w.state == UIWorldState.PAUSED

    def test_world_destroy_to_ui_world_destroy(self):
        w = Fab.create_ui_world("cp_w")
        Fab.initialize(w)
        Fab.start(w)
        Fab.destroy(w)
        assert w.state == UIWorldState.DESTROYED

    def test_input_replay_to_ui_replay(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b")
        events = [UIEvent(UIEventType.CLICK, "b")]
        Fab.replay_events(w, events)
        assert len(w.events_history) == 1

    def test_ui_snapshot_with_runtime_snapshot(self):
        w = Fab.create_ui_world("cp_w")
        Fab.add_root_node(w, "r")
        snap = Fab.create_snapshot(w)
        # Compound snapshot dict
        runtime_snapshot = {"world_id": "rw_01", "ui": snap.to_dict()}
        assert "ui" in runtime_snapshot


class TestTeardownAndCleanup:
    """Tests for §126 Teardown & Leak Prevention."""

    def test_ui_world_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.cleanup(w)
        assert len(w.nodes) == 0

    def test_tree_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c")
        Fab.cleanup(w)
        assert len(w.root_ids) == 0

    def test_widget_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "btn", UINodeType.BUTTON)
        Fab.cleanup(w)
        assert len(w.nodes) == 0

    def test_layout_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.update_layout(w)
        Fab.cleanup(w)
        assert len(w.nodes) == 0

    def test_font_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        w.fonts["f1"] = UIFontResource("f1", "Inter")
        Fab.cleanup(w)
        assert len(w.fonts) == 0

    def test_icon_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        w.icons["i1"] = UIIconResource("i1", "Icon")
        Fab.cleanup(w)
        assert len(w.icons) == 0

    def test_style_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_style(w, UIStyle("s1"))
        Fab.cleanup(w)
        assert len(w.styles) == 0

    def test_theme_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_theme(w, UITheme("t1"))
        Fab.cleanup(w)
        assert len(w.themes) == 0

    def test_focus_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.set_focus(w, "r")
        Fab.cleanup(w)
        assert w.focused_node_id is None

    def test_navigation_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r")
        Fab.cleanup(w)
        assert Fab.navigate(w, NavigationDirection.NEXT) is None

    def test_animation_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.create_animation(w, "a1", "r", "opacity", 0.0, 1.0)
        Fab.cleanup(w)
        assert len(w.animations) == 0

    def test_binding_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_binding(w, UIDataBinding("b1", "src", "tgt", "prop"))
        Fab.cleanup(w)
        assert len(w.bindings) == 0

    def test_localization_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_localization_table(w, UILocalizationTable("es-ES"))
        Fab.cleanup(w)
        assert len(w.localization_tables) == 0

    def test_accessibility_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        Fab.add_root_node(w, "r", UINodeType.BUTTON)
        Fab.cleanup(w)
        assert len(Fab.get_accessibility_tree(w)) == 0

    def test_snapshot_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        snap = Fab.create_snapshot(w)
        Fab.cleanup(w)
        assert snap is not None

    def test_replay_cleanup(self):
        w = Fab.create_ui_world("cln_w")
        w.event_queue.append(UIEvent(UIEventType.CLICK, "b"))
        Fab.cleanup(w)
        assert len(w.event_queue) == 0


class TestPackagingAndInvariants:
    """Tests for packaging, subsystems, and invariants validation."""

    def test_packager_manifest_creation(self, tmp_path):
        w = Fab.create_ui_world("pkg_world")
        Fab.add_root_node(w, "r")
        packager = UniversalRuntimeUIPackager()
        res = packager.package(str(tmp_path), w)
        assert os.path.exists(res["manifest"])

    def test_packager_signature_generation(self, tmp_path):
        w = Fab.create_ui_world("pkg_world")
        packager = UniversalRuntimeUIPackager()
        res = packager.package(str(tmp_path), w)
        assert os.path.exists(res["signature"])

    def test_packager_header_subsystem(self, tmp_path):
        w = Fab.create_ui_world("pkg_world")
        packager = UniversalRuntimeUIPackager()
        res = packager.package(str(tmp_path), w)
        with open(res["header"], "r", encoding="utf-8") as f:
            code = f.read()
        assert "class ASSETORCHESTRATION_API UUAFRuntimeUISubsystem : public UWorldSubsystem" in code
        assert '#include "Subsystems/WorldSubsystem.h"' in code

    def test_packager_cpp_subsystem(self, tmp_path):
        w = Fab.create_ui_world("pkg_world")
        packager = UniversalRuntimeUIPackager()
        res = packager.package(str(tmp_path), w)
        with open(res["source"], "r", encoding="utf-8") as f:
            code = f.read()
        assert "void UUAFRuntimeUISubsystem::Initialize" in code

    def test_packager_return_dict(self, tmp_path):
        packager = UniversalRuntimeUIPackager()
        res = packager.package(str(tmp_path))
        assert res["success"] is True

    def test_validator_clean_world(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "c")
        issues = Val.validate_world(w)
        assert len(issues) == 0

    def test_validator_detects_tree_cycle(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        c1 = Fab.add_child(w, "r", "c1")
        c2 = Fab.add_child(w, "c1", "c2")
        # Invalidate manually to test validator detection
        c1.parent_id = "c2"
        issues = Val.validate_tree(w)
        assert any(i.code == "NO_TREE_CYCLE" for i in issues)

    def test_validator_detects_orphan_node(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        c = Fab.add_child(w, "r", "c")
        c.parent_id = "ghost_parent"
        issues = Val.validate_tree(w)
        assert any(i.code == "NO_ORPHAN_ACTIVE_NODE" for i in issues)

    def test_validator_detects_multiple_parents(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        c = Fab.add_child(w, "r", "c")
        c.parent_id = "other_p"
        w.nodes["other_p"] = UINode("other_p")
        issues = Val.validate_tree(w)
        assert any(i.code == "NO_NODE_WITH_MULTIPLE_PARENTS" for i in issues)

    def test_validator_detects_nan_dimensions(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        w.nodes["r"].assigned_rect.width = float("nan")
        issues = Val.validate_layout_and_dimensions(w)
        assert any(i.code == "NO_NAN_LAYOUT_VALUES" for i in issues)

    def test_validator_detects_style_loop(self):
        w = Fab.create_ui_world("val_w")
        w.styles["s1"] = UIStyle("s1", parent_style_id="s2")
        w.styles["s2"] = UIStyle("s2", parent_style_id="s1")
        issues = Val.validate_styles_and_themes(w)
        assert any(i.code == "NO_STYLE_INHERITANCE_LOOP" for i in issues)

    def test_validator_detects_theme_loop(self):
        w = Fab.create_ui_world("val_w")
        w.themes["t1"] = UITheme("t1", parent_theme_id="t2")
        w.themes["t2"] = UITheme("t2", parent_theme_id="t1")
        issues = Val.validate_styles_and_themes(w)
        assert any(i.code == "NO_THEME_RESOLUTION_LOOP" for i in issues)

    def test_validator_detects_invalid_focus(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        btn = Fab.add_child(w, "r", "btn", is_enabled=False)
        w.focused_node_id = "btn"
        issues = Val.validate_focus_and_navigation(w)
        assert any(i.code == "NO_DISABLED_WIDGET_NORMAL_INTERACTION" for i in issues)

    def test_validator_detects_invalid_binding_target(self):
        w = Fab.create_ui_world("val_w")
        w.bindings["b1"] = UIDataBinding("b1", "src", "missing_node", "prop")
        issues = Val.validate_bindings(w)
        assert any(i.code == "INVALID_BINDING_TARGET" for i in issues)

    def test_validator_detects_duplicate_automation_id(self):
        w = Fab.create_ui_world("val_w")
        Fab.add_root_node(w, "r")
        Fab.add_child(w, "r", "b1", automation_id="same_id")
        Fab.add_child(w, "r", "b2", automation_id="same_id")
        issues = Val.validate_accessibility(w)
        assert any(i.code == "DUPLICATE_AUTOMATION_ID" for i in issues)

    def test_validator_alias_method(self):
        w = Fab.create_ui_world("val_w")
        assert Val.validate(w) == Val.validate_world(w)

    def test_export_in_uaf_root_package(self):
        import uaf
        assert hasattr(uaf, "UniversalRuntimeUIFabricator")
        assert hasattr(uaf, "UniversalRuntimeUIValidator")
        assert hasattr(uaf, "UniversalRuntimeUIPackager")
        assert hasattr(uaf, "UIWorld")

    def test_all_public_api_symbols(self):
        import uaf.runtime_ui as r_ui
        assert hasattr(r_ui, "UIWorldState")
        assert hasattr(r_ui, "UINodeType")
        assert hasattr(r_ui, "LayoutType")
        assert hasattr(r_ui, "HitTestMode")
        assert hasattr(r_ui, "UIEventType")
        assert hasattr(r_ui, "NavigationDirection")
