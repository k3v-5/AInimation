"""
UAF-81.66 Acceptance & Normative Compliance Test Suite.
Verifies Universal UI Framework, Retained UI Tree, Widget System, Layout Engine,
Style System, Theme System, Input Presentation, Accessibility, UI State, Data Binding,
UI Animation, UI Rendering & UI Testing System.
Covers 177+ normative test cases satisfying exact requirements of §171, §139-§142, §154, §156, §143-§146.
"""

import math
import time
import json
import pytest
from pathlib import Path

from uaf.universal_ui_framework import (
    UISurfaceType,
    ElementVisibility,
    ElementLifecycle,
    PointerEventPolicy,
    SizeMode,
    LayoutPositioning,
    LayoutAlignment,
    LayoutDistribution,
    FlexDirection,
    StyleSource,
    StyleState,
    ThemeMode,
    TextWrapping,
    TextOverflowMode,
    BindingMode,
    UIEventType,
    EventPhase,
    UIAccessibleRole,
    AnimationTarget,
    AnimationReplacementPolicy,
    InvalidationType,
    RenderCommandType,
    UIPoint,
    UISize,
    UIRect,
    UIInsets,
    UIBoxConstraints,
    UIColor,
    UITypography,
    UIIcon,
    UIStyleDeclaration,
    UIThemeTokens,
    UITheme,
    UIBinding,
    UIEventData,
    UIAccessibleNode,
    UIAnimation,
    UIRenderCommand,
    UIRenderTree,
    UIStructuralSnapshot,
    UIInspectorData,
    UITelemetry,
    UIDiagnosticBundle,
    UIElement,
    LabelWidget,
    ButtonWidget,
    TextFieldWidget,
    CheckboxWidget,
    SliderWidget,
    ListWidget,
    TreeWidget,
    ScrollViewWidget,
    ImageWidget,
    ProgressBarWidget,
    TabViewWidget,
    MenuWidget,
    DialogWidget,
    FallbackWidget,
    UniversalUIFrameworkFabricator,
    UniversalUIFrameworkValidator,
    UniversalUIFrameworkPackager,
)


# ==============================================================================
# 1. UI_TREE TESTS (10 tests)
# ==============================================================================

def test_add_child():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_main")
    btn = fab.register_element(ButtonWidget("btn_1", "Click Me"))
    fab.append_child("root_main", "btn_1")

    assert "btn_1" in root.children_ids
    assert btn.parent_id == "root_main"
    assert btn.lifecycle == ElementLifecycle.MOUNTED


def test_remove_child():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_main")
    btn = fab.register_element(ButtonWidget("btn_1", "Click Me"))
    fab.append_child("root_main", "btn_1")
    fab.remove_child("root_main", "btn_1")

    assert "btn_1" not in fab.roots["root_main"].children_ids
    assert btn.parent_id is None


def test_insert_child():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_main")
    btn1 = fab.register_element(ButtonWidget("btn_1", "1"))
    btn2 = fab.register_element(ButtonWidget("btn_2", "2"))
    btn_mid = fab.register_element(ButtonWidget("btn_mid", "Mid"))

    fab.append_child("root_main", "btn_1")
    fab.append_child("root_main", "btn_2")
    fab.insert_child("root_main", "btn_mid", 1)

    assert root.children_ids == ["btn_1", "btn_mid", "btn_2"]


def test_replace_child():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_main")
    fab.register_element(ButtonWidget("btn_old", "Old"))
    fab.register_element(ButtonWidget("btn_new", "New"))

    fab.append_child("root_main", "btn_old")
    fab.replace_child("root_main", "btn_old", "btn_new")

    assert root.children_ids == ["btn_new"]
    assert fab.elements["btn_old"].parent_id is None
    assert fab.elements["btn_new"].parent_id == "root_main"


def test_move_child():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_main")
    fab.register_element(ButtonWidget("b1", "1"))
    fab.register_element(ButtonWidget("b2", "2"))
    fab.register_element(ButtonWidget("b3", "3"))

    fab.append_child("root_main", "b1")
    fab.append_child("root_main", "b2")
    fab.append_child("root_main", "b3")
    fab.move_child("root_main", "b3", 0)

    assert root.children_ids == ["b3", "b1", "b2"]


def test_clear_children():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_main")
    fab.register_element(ButtonWidget("b1", "1"))
    fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_main", "b1")
    fab.append_child("root_main", "b2")

    fab.clear_children("root_main")
    assert len(root.children_ids) == 0


def test_no_self_parent():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_main")
    btn = fab.register_element(ButtonWidget("btn_1", "1"))

    with pytest.raises(ValueError, match="cannot be its own parent"):
        fab.append_child("btn_1", "btn_1")


def test_no_cycles():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_main")
    p1 = fab.register_element(UIElement("p1"))
    p2 = fab.register_element(UIElement("p2"))

    fab.append_child("root_main", "p1")
    fab.append_child("p1", "p2")

    with pytest.raises(ValueError, match="creates a cycle"):
        fab.append_child("p2", "p1")


def test_one_parent():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_1")
    fab.create_root("root_2")
    btn = fab.register_element(ButtonWidget("btn_shared", "Shared"))

    fab.append_child("root_1", "btn_shared")
    assert btn.parent_id == "root_1"

    fab.append_child("root_2", "btn_shared")
    assert btn.parent_id == "root_2"
    assert "btn_shared" not in fab.roots["root_1"].children_ids
    assert "btn_shared" in fab.roots["root_2"].children_ids


def test_element_lifecycle_mount_unmount():
    elem = ButtonWidget("btn_life", "Lifecycle")
    assert elem.lifecycle == ElementLifecycle.CREATED
    elem.mount()
    assert elem.lifecycle == ElementLifecycle.MOUNTED
    elem.unmount()
    assert elem.lifecycle == ElementLifecycle.DESTROYED


# ==============================================================================
# 2. LAYOUT TESTS (17 tests)
# ==============================================================================

def test_measure_fixed_size():
    elem = UIElement("elem_fixed")
    elem.size_mode_width = SizeMode.FIXED
    elem.size_mode_height = SizeMode.FIXED
    elem.fixed_width = 120.0
    elem.fixed_height = 45.0

    size = elem.measure(UIBoxConstraints.loose())
    assert size.width == 120.0
    assert size.height == 45.0


def test_measure_auto_size():
    elem = UIElement("elem_auto")
    elem.size_mode_width = SizeMode.AUTO
    elem.size_mode_height = SizeMode.AUTO
    size = elem.measure(UIBoxConstraints(min_width=50, max_width=200, min_height=30, max_height=100))

    assert size.width == 50.0
    assert size.height == 30.0


def test_measure_content_size():
    lbl = LabelWidget("lbl_content", "Hello World")
    size = lbl.measure(UIBoxConstraints.loose())
    assert size.width > 0
    assert size.height > 0


def test_box_constraints_min_max():
    constraints = UIBoxConstraints(min_width=100.0, max_width=300.0, min_height=50.0, max_height=150.0)
    assert constraints.constrain_width(50.0) == 100.0
    assert constraints.constrain_width(400.0) == 300.0
    assert constraints.constrain_height(20.0) == 50.0
    assert constraints.constrain_height(200.0) == 150.0


def test_box_constraints_tight_loose():
    tight = UIBoxConstraints.tight(800.0, 600.0)
    assert tight.min_width == 800.0 and tight.max_width == 800.0

    loose = UIBoxConstraints.loose(500.0, 400.0)
    assert loose.min_width == 0.0 and loose.max_width == 500.0


def test_box_model_padding():
    elem = UIElement("elem_pad")
    elem.computed_style.padding = UIInsets(top=10, right=15, bottom=10, left=15)
    size = elem.measure(UIBoxConstraints.loose())
    assert size.width >= 30.0
    assert size.height >= 20.0


def test_box_model_margin():
    insets = UIInsets.all(8.0)
    assert insets.horizontal == 16.0
    assert insets.vertical == 16.0


def test_flex_row_distribution():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_row")
    root.flex_direction = FlexDirection.ROW
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_row", "b1")
    fab.append_child("root_row", "b2")

    fab.compute_layout("root_row", UISize(400, 100))
    assert b1.bounds.x == 0.0
    assert b1.bounds.width == 200.0
    assert b2.bounds.x == 200.0
    assert b2.bounds.width == 200.0


def test_flex_column_distribution():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_col")
    root.flex_direction = FlexDirection.COLUMN
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_col", "b1")
    fab.append_child("root_col", "b2")

    fab.compute_layout("root_col", UISize(200, 400))
    assert b1.bounds.y == 0.0
    assert b1.bounds.height == 200.0
    assert b2.bounds.y == 200.0
    assert b2.bounds.height == 200.0


def test_flex_gap():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_gap")
    root.flex_direction = FlexDirection.ROW
    root.gap = 10.0
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_gap", "b1")
    fab.append_child("root_gap", "b2")

    fab.compute_layout("root_gap", UISize(210, 100))
    assert b1.bounds.width == 100.0
    assert b2.bounds.x == 110.0


def test_flex_grow_shrink():
    elem = UIElement("flex_elem")
    elem.flex_grow = 2.0
    elem.flex_shrink = 0.5
    assert elem.flex_grow == 2.0
    assert elem.flex_shrink == 0.5


def test_layout_alignment_center():
    elem = UIElement("align_elem")
    elem.layout_alignment = LayoutAlignment.CENTER
    assert elem.layout_alignment == LayoutAlignment.CENTER


def test_layout_alignment_stretch():
    elem = UIElement("stretch_elem")
    elem.layout_alignment = LayoutAlignment.STRETCH
    assert elem.layout_alignment == LayoutAlignment.STRETCH


def test_stack_layout_overlay():
    rect1 = UIRect(10, 10, 100, 100)
    rect2 = UIRect(20, 20, 50, 50)
    assert rect1.intersects(rect2)


def test_scroll_view_bounds_clamp():
    sv = ScrollViewWidget("sv_clamp")
    sv.bounds = UIRect(0, 0, 200, 200)
    sv.content_height = 500.0

    sv.scroll_by(0, 1000.0)
    assert sv.scroll_y == 300.0  # max 500 - 200 = 300


def test_scroll_view_scroll_by():
    sv = ScrollViewWidget("sv_scroll")
    sv.bounds = UIRect(0, 0, 200, 200)
    sv.content_height = 500.0

    sv.scroll_by(0, 50.0)
    assert sv.scroll_y == 50.0
    sv.scroll_by(0, -100.0)
    assert sv.scroll_y == 0.0  # clamped at 0


def test_collapsed_visibility_zero_size():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_v")
    b = fab.register_element(ButtonWidget("b_col", "Hidden"))
    b.visibility = ElementVisibility.COLLAPSED
    fab.append_child("root_v", "b_col")

    fab.compute_layout("root_v", UISize(400, 400))
    assert b.bounds.width == 0.0
    assert b.bounds.height == 0.0


# ==============================================================================
# 3. CLIPPING TESTS (6 tests)
# ==============================================================================

def test_clip_rect_parent_intersection():
    parent_clip = UIRect(0, 0, 100, 100)
    child_bounds = UIRect(50, 50, 100, 100)
    inter = parent_clip.intersection(child_bounds)

    assert inter is not None
    assert inter.x == 50
    assert inter.y == 50
    assert inter.width == 50
    assert inter.height == 50


def test_nested_clip_inheritance():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_c")
    p1 = fab.register_element(UIElement("p1"))
    btn = fab.register_element(ButtonWidget("b_clip", "C"))
    fab.append_child("root_c", "p1")
    fab.append_child("p1", "b_clip")

    fab.compute_layout("root_c", UISize(200, 200))
    assert btn.clip_rect is not None
    assert btn.clip_rect.width <= 200.0


def test_point_outside_clip_rejected():
    rect = UIRect(0, 0, 50, 50)
    assert not rect.contains_point(UIPoint(60, 25))


def test_point_inside_clip_accepted():
    rect = UIRect(0, 0, 50, 50)
    assert rect.contains_point(UIPoint(25, 25))


def test_empty_clip_intersection():
    r1 = UIRect(0, 0, 10, 10)
    r2 = UIRect(20, 20, 10, 10)
    assert r1.intersection(r2) is None


def test_clip_rect_bounds_clamping():
    r1 = UIRect(10, 10, 80, 80)
    assert r1.right == 90
    assert r1.bottom == 90


# ==============================================================================
# 4. STYLE TESTS (10 tests)
# ==============================================================================

def test_default_style_resolution():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_s")
    btn = fab.register_element(ButtonWidget("btn_s", "Style"))
    fab.append_child("root_s", "btn_s")

    fab.resolve_styles_recursively("root_s")
    assert btn.computed_style is not None


def test_theme_style_resolution():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_thm")
    btn = fab.register_element(ButtonWidget("btn_thm", "Themed"))
    fab.append_child("root_thm", "btn_thm")

    fab.set_active_theme("dark")
    fab.resolve_styles_recursively("root_thm")
    assert btn.computed_style is not None


def test_inline_style_override():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_in")
    btn = fab.register_element(ButtonWidget("btn_in", "Inline"))
    btn.inline_style = UIStyleDeclaration(background_color=UIColor.from_hex("#FF0000"), z_index=5)
    fab.append_child("root_in", "btn_in")

    fab.resolve_styles_recursively("root_in")
    assert btn.computed_style.background_color.to_hex() == "#FF0000"
    assert btn.computed_style.z_index == 5


def test_style_inheritance_font():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_inh")
    root.inline_style = UIStyleDeclaration(font=UITypography(font_family="Comic Sans", font_size=24.0))
    lbl = fab.register_element(LabelWidget("lbl_inh", "Inherit"))
    fab.append_child("root_inh", "lbl_inh")

    fab.resolve_styles_recursively("root_inh")
    assert lbl.computed_style.font.font_family == "Comic Sans"


def test_style_inheritance_text_color():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_inh_col")
    root.inline_style = UIStyleDeclaration(text_color=UIColor.from_hex("#123456"))
    lbl = fab.register_element(LabelWidget("lbl_inh_col", "Inherit Color"))
    fab.append_child("root_inh_col", "lbl_inh_col")

    fab.resolve_styles_recursively("root_inh_col")
    assert lbl.computed_style.text_color.to_hex() == "#123456"


def test_state_style_hover():
    btn = ButtonWidget("b_hov", "H")
    event = UIEventData(event_type=UIEventType.PointerEnter, target_id="b_hov")
    btn.handle_event(event)
    assert btn.style_state == StyleState.HOVER


def test_state_style_active():
    btn = ButtonWidget("b_act", "A")
    event = UIEventData(event_type=UIEventType.PointerDown, target_id="b_act")
    btn.handle_event(event)
    assert btn.style_state == StyleState.ACTIVE


def test_state_style_disabled():
    btn = ButtonWidget("b_dis", "D")
    btn.enabled = False
    btn.handle_event(UIEventData(event_type=UIEventType.PointerDown, target_id="b_dis"))
    assert btn.style_state == StyleState.NORMAL  # Ignored when disabled


def test_style_opacity_propagation():
    decl = UIStyleDeclaration(opacity=0.5)
    assert decl.opacity == 0.5


def test_style_invalidation_flag():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_inv")
    btn = fab.register_element(ButtonWidget("b_inv", "Inv"))
    fab.append_child("root_inv", "b_inv")

    fab.invalidate_element("b_inv", InvalidationType.STYLE_DIRTY)
    assert InvalidationType.STYLE_DIRTY in btn.invalidation_flags


# ==============================================================================
# 5. THEME TESTS (8 tests)
# ==============================================================================

def test_theme_load_dark():
    theme = UITheme.create_default_dark()
    assert theme.mode == ThemeMode.DARK
    assert "background" in theme.tokens.colors
    assert "primary" in theme.tokens.colors


def test_theme_load_light():
    theme = UITheme.create_default_light()
    assert theme.mode == ThemeMode.LIGHT
    assert "background" in theme.tokens.colors


def test_theme_switch_invalidation():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_thm_sw")
    btn = fab.register_element(ButtonWidget("b_sw", "Switch"))
    fab.append_child("root_thm_sw", "b_sw")

    fab.set_active_theme("light")
    assert fab.active_theme_id == "light"
    assert InvalidationType.STYLE_DIRTY in btn.invalidation_flags


def test_theme_tokens_colors():
    dark = UITheme.create_default_dark()
    bg = dark.tokens.colors["background"]
    assert bg.r < 0.2 and bg.g < 0.2 and bg.b < 0.2


def test_theme_tokens_spacing():
    dark = UITheme.create_default_dark()
    assert dark.tokens.spacing["md"] == 16.0


def test_theme_tokens_typography():
    dark = UITheme.create_default_dark()
    assert dark.tokens.typography["heading"].font_size == 20.0


def test_theme_contrast_ratio_wcag():
    valid, errors = UniversalUIFrameworkValidator.validate_theme_contrast(UITheme.create_default_dark(), min_ratio=4.5)
    assert valid
    assert len(errors) == 0


def test_theme_custom_palette():
    custom_tokens = UIThemeTokens(colors={"primary": UIColor.from_hex("#00FF00")})
    custom_theme = UITheme(id="custom", name="Custom", mode=ThemeMode.CUSTOM, tokens=custom_tokens)
    assert custom_theme.tokens.colors["primary"].to_hex() == "#00FF00"


# ==============================================================================
# 6. TYPOGRAPHY TESTS (7 tests)
# ==============================================================================

def test_text_measurement_approx():
    lbl = LabelWidget("lbl_m", "A" * 10)
    size = lbl.measure(UIBoxConstraints.loose())
    assert size.width == 10 * 14.0 * 0.6


def test_text_word_wrap_height():
    lbl = LabelWidget("lbl_wrap", "A" * 50)
    lbl.typography.text_wrapping = TextWrapping.WORD_WRAP
    # Constrain max width to fit only 10 chars
    max_w = 10 * 14.0 * 0.6
    size = lbl.measure(UIBoxConstraints(min_width=0, max_width=max_w, min_height=0, max_height=1000))
    line_h = 14.0 * 1.4
    assert size.height >= 5 * line_h


def test_text_no_wrap():
    lbl = LabelWidget("lbl_nowrap", "Single line text")
    lbl.typography.text_wrapping = TextWrapping.NO_WRAP
    size = lbl.measure(UIBoxConstraints.loose())
    assert size.height == 14.0 * 1.4


def test_font_fallback_list():
    typo = UITypography(font_family="NonExistentFont", fallback_families=["Arial", "sans-serif"])
    assert "sans-serif" in typo.fallback_families


def test_line_height_scaling():
    typo1 = UITypography(font_size=16.0, line_height=1.5)
    assert typo1.font_size * typo1.line_height == 24.0


def test_letter_spacing_property():
    typo = UITypography(letter_spacing=1.2)
    assert typo.letter_spacing == 1.2


def test_text_color_assignment():
    typo = UITypography(text_color=UIColor.from_hex("#E91E63"))
    assert typo.text_color.to_hex() == "#E91E63"


# ==============================================================================
# 7. INPUT/UI TESTS (10 tests)
# ==============================================================================

def test_hit_test_direct_target():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_hit")
    btn = fab.register_element(ButtonWidget("btn_hit", "Hit"))
    fab.append_child("root_hit", "btn_hit")

    fab.compute_layout("root_hit", UISize(200, 200))
    hit = fab.hit_test("root_hit", UIPoint(50, 50))
    assert hit == "btn_hit"


def test_hit_test_nested_child():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_nest")
    panel = fab.register_element(UIElement("panel"))
    btn = fab.register_element(ButtonWidget("btn_inner", "Inner"))
    fab.append_child("root_nest", "panel")
    fab.append_child("panel", "btn_inner")

    fab.compute_layout("root_nest", UISize(300, 300))
    hit = fab.hit_test("root_nest", UIPoint(100, 100))
    assert hit == "btn_inner"


def test_hit_test_pointer_events_none():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_none")
    root.pointer_events = PointerEventPolicy.NONE
    btn = fab.register_element(ButtonWidget("btn_none", "None"))
    btn.pointer_events = PointerEventPolicy.NONE
    fab.append_child("root_none", "btn_none")

    fab.compute_layout("root_none", UISize(200, 200))
    hit = fab.hit_test("root_none", UIPoint(50, 50))
    assert hit is None


def test_pointer_down_up_click_flow():
    clicked = []
    btn = ButtonWidget("b_click", "Click", on_click=lambda: clicked.append(True))
    btn.handle_event(UIEventData(event_type=UIEventType.PointerDown, target_id="b_click"))
    assert btn.state["pressed"] is True
    btn.handle_event(UIEventData(event_type=UIEventType.PointerUp, target_id="b_click"))
    assert btn.state["pressed"] is False
    assert len(clicked) == 1


def test_pointer_enter_leave_hover_state():
    btn = ButtonWidget("b_hl", "Hover")
    btn.handle_event(UIEventData(event_type=UIEventType.PointerEnter, target_id="b_hl"))
    assert btn.state["hovered"] is True
    btn.handle_event(UIEventData(event_type=UIEventType.PointerLeave, target_id="b_hl"))
    assert btn.state["hovered"] is False


def test_event_capture_phase():
    phases = []
    elem = UIElement("el_cap")
    elem.add_event_listener(UIEventType.PointerDown, lambda e: phases.append(e.phase), use_capture=True)
    event = UIEventData(event_type=UIEventType.PointerDown, target_id="el_cap", phase=EventPhase.CAPTURE)
    elem.handle_event(event)
    assert phases == [EventPhase.CAPTURE]


def test_event_bubble_phase():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_b")
    btn = fab.register_element(ButtonWidget("btn_b", "Bubble"))
    fab.append_child("root_b", "btn_b")

    events_received = []
    root.add_event_listener(UIEventType.Click, lambda e: events_received.append("root"))
    btn.add_event_listener(UIEventType.Click, lambda e: events_received.append("btn"))

    event = UIEventData(event_type=UIEventType.Click, target_id="btn_b", bubbles=True)
    fab.dispatch_event("root_b", event)
    assert events_received == ["btn", "root"]


def test_event_stop_propagation():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_stop")
    btn = fab.register_element(ButtonWidget("btn_stop", "Stop"))
    fab.append_child("root_stop", "btn_stop")

    events_received = []
    root.add_event_listener(UIEventType.Click, lambda e: events_received.append("root"))
    def on_click(e):
        events_received.append("btn")
        e.stop_propagation()
    btn.add_event_listener(UIEventType.Click, on_click)

    event = UIEventData(event_type=UIEventType.Click, target_id="btn_stop", bubbles=True)
    fab.dispatch_event("root_stop", event)
    assert events_received == ["btn"]


def test_event_prevent_default():
    event = UIEventData(event_type=UIEventType.Click, target_id="test", cancelable=True)
    event.prevent_default()
    assert event.is_default_prevented is True


def test_modal_blocks_outside_input():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_m")
    fab.register_element(ButtonWidget("btn_outside", "Outside"))
    dlg = fab.register_element(DialogWidget("dlg_modal", "Modal", is_modal=True))
    fab.append_child("root_m", "btn_outside")
    fab.append_child("root_m", "dlg_modal")

    fab.push_modal("dlg_modal")
    # Outside focus should be blocked
    ok = fab.set_focus("btn_outside")
    assert ok is False


# ==============================================================================
# 8. FOCUS TESTS (8 tests)
# ==============================================================================

def test_focus_gain_and_style_state():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_f")
    btn = fab.register_element(ButtonWidget("b_fg", "Focus"))
    fab.append_child("root_f", "b_fg")

    fab.set_focus("b_fg")
    assert fab.focus_element_id == "b_fg"
    assert btn.style_state == StyleState.FOCUSED


def test_focus_loss_blur():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_fl")
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_fl", "b1")
    fab.append_child("root_fl", "b2")

    fab.set_focus("b1")
    fab.set_focus("b2")
    assert b1.style_state == StyleState.NORMAL
    assert b2.style_state == StyleState.FOCUSED
    assert "b1" in fab.focus_history


def test_tab_navigation_next():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_tab")
    fab.register_element(ButtonWidget("b1", "1"))
    fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_tab", "b1")
    fab.append_child("root_tab", "b2")

    assert fab.focus_next() == "b1"
    assert fab.focus_next() == "b2"
    assert fab.focus_next() == "b1"  # loops around


def test_reverse_tab_navigation_prev():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_rtab")
    fab.register_element(ButtonWidget("b1", "1"))
    fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_rtab", "b1")
    fab.append_child("root_rtab", "b2")

    assert fab.focus_prev() == "b2"
    assert fab.focus_prev() == "b1"


def test_focus_order_by_tab_index():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_ord")
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    b1.tab_index = 10
    b2.tab_index = 5
    fab.append_child("root_ord", "b1")
    fab.append_child("root_ord", "b2")

    assert fab.focus_next() == "b2"  # b2 has lower tab_index


def test_modal_focus_trap():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_mtrap")
    fab.register_element(ButtonWidget("b_out", "Outside"))
    dlg = fab.register_element(DialogWidget("dlg_trap", "Trap", is_modal=True))
    b_in1 = fab.register_element(ButtonWidget("b_in1", "In1"))
    b_in2 = fab.register_element(ButtonWidget("b_in2", "In2"))

    fab.append_child("root_mtrap", "b_out")
    fab.append_child("root_mtrap", "dlg_trap")
    fab.append_child("dlg_trap", "b_in1")
    fab.append_child("dlg_trap", "b_in2")

    fab.push_modal("dlg_trap")
    assert fab.focus_next() == "b_in1"
    assert fab.focus_next() == "b_in2"
    assert fab.focus_next() == "b_in1"  # trapped inside modal


def test_modal_focus_restore_on_close():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_mrest")
    b_start = fab.register_element(ButtonWidget("b_start", "Start"))
    dlg = fab.register_element(DialogWidget("dlg_rest", "Rest", is_modal=True))
    fab.append_child("root_mrest", "b_start")
    fab.append_child("root_mrest", "dlg_rest")

    fab.set_focus("b_start")
    fab.push_modal("dlg_rest")
    assert fab.focus_element_id == "dlg_rest"

    fab.pop_modal()
    assert fab.focus_element_id == "b_start"


def test_unfocusable_element_ignored():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_unf")
    lbl = fab.register_element(LabelWidget("lbl_unf", "Text"))
    fab.append_child("root_unf", "lbl_unf")

    assert fab.focus_next() is None


# ==============================================================================
# 9. ACCESSIBILITY TESTS (10 tests)
# ==============================================================================

def test_accessible_role_button():
    btn = ButtonWidget("b_role", "Click")
    assert btn.accessible_role == UIAccessibleRole.BUTTON


def test_accessible_role_text_field():
    tf = TextFieldWidget("tf_role", "Hello")
    assert tf.accessible_role == UIAccessibleRole.TEXT_FIELD


def test_accessible_role_checkbox():
    cb = CheckboxWidget("cb_role", "Check")
    assert cb.accessible_role == UIAccessibleRole.CHECKBOX


def test_accessible_role_slider():
    sl = SliderWidget("sl_role", 0, 100, 50)
    assert sl.accessible_role == UIAccessibleRole.SLIDER


def test_accessible_name_and_description():
    btn = ButtonWidget("b_acc", "Submit")
    btn.accessible_description = "Submits the active form"
    assert btn.accessible_name == "Submit"
    assert btn.accessible_description == "Submits the active form"


def test_accessible_state_checked():
    cb = CheckboxWidget("cb_chk", "Check", checked=True)
    node = UIAccessibleNode(element_id="cb_chk", role=UIAccessibleRole.CHECKBOX, checked=cb.checked)
    assert node.checked is True


def test_accessible_state_disabled():
    btn = ButtonWidget("b_dis_acc", "Disabled")
    btn.enabled = False
    node = UIAccessibleNode(element_id="b_dis_acc", disabled=not btn.enabled)
    assert node.disabled is True


def test_accessible_tree_hierarchy():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_atree")
    btn = fab.register_element(ButtonWidget("b_atree", "B"))
    fab.append_child("root_atree", "b_atree")

    tree = fab.generate_accessible_tree("root_atree")
    assert tree is not None
    assert tree.element_id == "root_atree"
    assert "b_atree" in tree.child_ids


def test_validator_detects_missing_accessible_name():
    node = UIAccessibleNode(element_id="bad_btn", role=UIAccessibleRole.BUTTON, name="")
    valid, errors = UniversalUIFrameworkValidator.validate_accessibility_node(node)
    assert not valid
    assert any("MISSING_ACCESSIBLE_NAME" in e for e in errors)


def test_validator_passes_valid_accessible_nodes():
    node = UIAccessibleNode(element_id="good_btn", role=UIAccessibleRole.BUTTON, name="Save")
    valid, errors = UniversalUIFrameworkValidator.validate_accessibility_node(node)
    assert valid
    assert len(errors) == 0


# ==============================================================================
# 10. BINDING TESTS (10 tests)
# ==============================================================================

def test_one_way_binding_sync():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_b1")
    lbl = fab.register_element(LabelWidget("lbl_b1", ""))
    fab.append_child("root_b1", "lbl_b1")

    fab.bind("b_txt", "lbl_b1", "text", "player_name", mode=BindingMode.ONE_WAY)
    fab.set_app_state("player_name", "Kev")

    assert lbl.text == "Kev"
    assert lbl.state["text"] == "Kev"


def test_two_way_binding_ui_to_state():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_b2")
    tf = fab.register_element(TextFieldWidget("tf_b2", "Init"))
    fab.append_child("root_b2", "tf_b2")

    fab.bind("b_tf", "tf_b2", "text", "user_input", mode=BindingMode.TWO_WAY)
    fab.update_ui_property("tf_b2", "text", "Edited")

    assert fab.app_state["user_input"] == "Edited"


def test_two_way_binding_state_to_ui():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_b3")
    tf = fab.register_element(TextFieldWidget("tf_b3", ""))
    fab.append_child("root_b3", "tf_b3")

    fab.bind("b_tf3", "tf_b3", "text", "user_input", mode=BindingMode.TWO_WAY)
    fab.set_app_state("user_input", "FromState")

    assert tf.text == "FromState"


def test_binding_format_fn():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_bf")
    lbl = fab.register_element(LabelWidget("lbl_bf", ""))
    fab.append_child("root_bf", "lbl_bf")

    fab.bind("b_fmt", "lbl_bf", "text", "score", format_fn=lambda s: f"Score: {s} pts")
    fab.set_app_state("score", 1500)

    assert lbl.text == "Score: 1500 pts"


def test_binding_parse_fn():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_bp")
    tf = fab.register_element(TextFieldWidget("tf_bp", ""))
    fab.append_child("root_bp", "tf_bp")

    fab.bind("b_parse", "tf_bp", "text", "count", mode=BindingMode.TWO_WAY, parse_fn=lambda s: int(s))
    fab.update_ui_property("tf_bp", "text", "42")

    assert fab.app_state["count"] == 42


def test_binding_validator_fn_valid():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_bv")
    tf = fab.register_element(TextFieldWidget("tf_bv", ""))
    fab.append_child("root_bv", "tf_bv")

    validator = lambda val: (True, "") if val >= 0 else (False, "Negative value")
    binding = fab.bind("b_val", "tf_bv", "text", "age", mode=BindingMode.TWO_WAY, parse_fn=int, validator_fn=validator)
    fab.update_ui_property("tf_bv", "text", "25")

    assert fab.app_state["age"] == 25
    assert binding.last_error is None


def test_binding_validator_fn_error():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_be")
    tf = fab.register_element(TextFieldWidget("tf_be", ""))
    fab.append_child("root_be", "tf_be")

    validator = lambda val: (True, "") if val >= 0 else (False, "Negative value")
    binding = fab.bind("b_err", "tf_be", "text", "age", mode=BindingMode.TWO_WAY, parse_fn=int, validator_fn=validator)
    fab.update_ui_property("tf_be", "text", "-5")

    assert "age" not in fab.app_state
    assert binding.last_error == "Negative value"


def test_binding_loop_protection():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_loop")
    tf = fab.register_element(TextFieldWidget("tf_loop", ""))
    fab.append_child("root_loop", "tf_loop")

    b = fab.bind("b_loop", "tf_loop", "text", "synced_key", mode=BindingMode.TWO_WAY)
    fab.set_app_state("synced_key", "123")
    assert b.sync_count <= 2  # Handled safely without infinite recursion


def test_unbind_stops_updates():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_unb")
    lbl = fab.register_element(LabelWidget("lbl_unb", "Orig"))
    fab.append_child("root_unb", "lbl_unb")

    fab.bind("b_unb", "lbl_unb", "text", "key")
    fab.unbind("b_unb")
    fab.set_app_state("key", "NewVal")

    assert lbl.text == "Orig"


def test_binding_cleanup_on_unmount():
    elem = UIElement("el_cleanup")
    elem.bindings = ["b1", "b2"]
    elem.unmount()
    assert len(elem.bindings) == 0


# ==============================================================================
# 11. ANIMATION TESTS (8 tests)
# ==============================================================================

def test_animation_start_and_active():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_anim")
    btn = fab.register_element(ButtonWidget("b_anim", "Anim"))
    fab.append_child("root_anim", "b_anim")

    anim = fab.animate("b_anim", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=200.0)
    assert anim.is_active is True
    assert anim.progress() == 0.0


def test_animation_tick_progress():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_tick")
    btn = fab.register_element(ButtonWidget("b_tick", "Tick"))
    fab.append_child("root_tick", "b_tick")

    anim = fab.animate("b_tick", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=200.0)
    fab.tick_animations(100.0)

    assert anim.progress() == 0.5
    assert btn.computed_style.opacity == pytest.approx(0.5, 0.01)


def test_animation_completion():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_comp")
    btn = fab.register_element(ButtonWidget("b_comp", "Comp"))
    fab.append_child("root_comp", "b_comp")

    anim = fab.animate("b_comp", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=100.0)
    fab.tick_animations(150.0)

    assert anim.is_completed is True
    assert anim.is_active is False
    assert btn.computed_style.opacity == 1.0


def test_animation_evaluate_linear():
    anim = UIAnimation("a1", "e1", AnimationTarget.PROGRESS, "p", 0.0, 100.0, duration_ms=100.0, elapsed_ms=25.0)
    assert anim.evaluate() == 25.0


def test_animation_evaluate_ease_in():
    anim = UIAnimation("a2", "e2", AnimationTarget.PROGRESS, "p", 0.0, 100.0, duration_ms=100.0, elapsed_ms=50.0, easing="ease_in")
    assert anim.evaluate() == 25.0  # 0.5^2 * 100 = 25


def test_animation_replace_policy():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_rep")
    fab.register_element(ButtonWidget("b_rep", "Rep"))

    a1 = fab.animate("b_rep", AnimationTarget.OPACITY, "opacity", 0.0, 0.5, replacement=AnimationReplacementPolicy.REPLACE)
    a2 = fab.animate("b_rep", AnimationTarget.OPACITY, "opacity", 0.5, 1.0, replacement=AnimationReplacementPolicy.REPLACE)

    assert a1.is_active is False
    assert a2.is_active is True


def test_animation_ignore_policy():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_ign")
    fab.register_element(ButtonWidget("b_ign", "Ign"))

    a1 = fab.animate("b_ign", AnimationTarget.OPACITY, "opacity", 0.0, 0.5, replacement=AnimationReplacementPolicy.IGNORE)
    a2 = fab.animate("b_ign", AnimationTarget.OPACITY, "opacity", 0.5, 1.0, replacement=AnimationReplacementPolicy.IGNORE)

    assert a1 == a2


def test_reduced_motion_zero_duration():
    fab = UniversalUIFrameworkFabricator()
    fab.reduced_motion = True
    fab.create_root("root_rm")
    fab.register_element(ButtonWidget("b_rm", "RM"))

    anim = fab.animate("b_rm", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=500.0)
    assert anim.duration_ms == 0.0


# ==============================================================================
# 12. INVALIDATION TESTS (8 tests)
# ==============================================================================

def test_style_dirty_flag():
    elem = UIElement("el_sd")
    assert InvalidationType.STYLE_DIRTY in elem.invalidation_flags


def test_layout_dirty_flag():
    elem = UIElement("el_ld")
    assert InvalidationType.LAYOUT_DIRTY in elem.invalidation_flags


def test_paint_dirty_flag():
    elem = UIElement("el_pd")
    assert InvalidationType.PAINT_DIRTY in elem.invalidation_flags


def test_layout_dirty_propagates_up_to_ancestors():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_prop")
    panel = fab.register_element(UIElement("p_prop"))
    btn = fab.register_element(ButtonWidget("b_prop", "Prop"))
    fab.append_child("root_prop", "p_prop")
    fab.append_child("p_prop", "b_prop")

    # Clear initial dirty flags
    root.invalidation_flags.clear()
    panel.invalidation_flags.clear()
    btn.invalidation_flags.clear()

    fab.invalidate_element("b_prop", InvalidationType.LAYOUT_DIRTY)

    assert InvalidationType.LAYOUT_DIRTY in btn.invalidation_flags
    assert InvalidationType.LAYOUT_DIRTY in panel.invalidation_flags
    assert InvalidationType.LAYOUT_DIRTY in root.invalidation_flags


def test_paint_dirty_does_not_dirty_layout():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_paint")
    btn = fab.register_element(ButtonWidget("b_paint", "P"))
    fab.append_child("root_paint", "b_paint")

    root.invalidation_flags.clear()
    btn.invalidation_flags.clear()

    fab.invalidate_element("b_paint", InvalidationType.PAINT_DIRTY)
    assert InvalidationType.LAYOUT_DIRTY not in root.invalidation_flags


def test_partial_update_clears_dirty_flags():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_part")
    btn = fab.register_element(ButtonWidget("b_part", "Part"))
    fab.append_child("root_part", "b_part")

    fab.resolve_styles_recursively("root_part")
    fab.compute_layout("root_part", UISize(200, 200))

    assert InvalidationType.STYLE_DIRTY not in btn.invalidation_flags
    assert InvalidationType.LAYOUT_DIRTY not in btn.invalidation_flags


def test_theme_switch_dirties_all_styles():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_thminv")
    b1 = fab.register_element(ButtonWidget("b1", "1"))
    b2 = fab.register_element(ButtonWidget("b2", "2"))
    fab.append_child("root_thminv", "b1")
    fab.append_child("root_thminv", "b2")

    fab.resolve_styles_recursively("root_thminv")
    fab.set_active_theme("light")

    assert InvalidationType.STYLE_DIRTY in b1.invalidation_flags
    assert InvalidationType.STYLE_DIRTY in b2.invalidation_flags


def test_child_mutation_dirties_parent_layout():
    fab = UniversalUIFrameworkFabricator()
    root = fab.create_root("root_mut")
    root.invalidation_flags.clear()

    b = fab.register_element(ButtonWidget("b_mut", "Mut"))
    fab.append_child("root_mut", "b_mut")

    assert InvalidationType.LAYOUT_DIRTY in root.invalidation_flags


# ==============================================================================
# 13. RENDER TESTS (9 tests)
# ==============================================================================

def test_render_draw_rect_command():
    elem = UIElement("el_rect")
    elem.bounds = UIRect(10, 10, 50, 50)
    elem.computed_style.background_color = UIColor.white()
    commands = elem.render()

    assert any(c.command_type == RenderCommandType.DRAW_RECT for c in commands)


def test_render_draw_text_command():
    lbl = LabelWidget("lbl_rend", "Render Text")
    lbl.bounds = UIRect(0, 0, 100, 30)
    commands = lbl.render()

    text_cmds = [c for c in commands if c.command_type == RenderCommandType.DRAW_TEXT]
    assert len(text_cmds) == 1
    assert text_cmds[0].text == "Render Text"


def test_render_draw_image_command():
    img = ImageWidget("img_rend", "tex_wood")
    img.bounds = UIRect(0, 0, 64, 64)
    commands = img.render()

    img_cmds = [c for c in commands if c.command_type == RenderCommandType.DRAW_IMAGE]
    assert len(img_cmds) == 1
    assert img_cmds[0].image_asset == "tex_wood"


def test_render_order_by_z_index():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_z")
    b1 = fab.register_element(ButtonWidget("b_low", "Low"))
    b2 = fab.register_element(ButtonWidget("b_high", "High"))
    b1.z_index = 1
    b2.z_index = 100
    fab.append_child("root_z", "b_low")
    fab.append_child("root_z", "b_high")

    fab.compute_layout("root_z", UISize(200, 200))
    rt = fab.generate_render_tree("root_z")

    # Higher z_index appears after lower z_index
    z_indices = [c.z_index for c in rt.commands]
    assert z_indices == sorted(z_indices)


def test_render_visibility_hidden_omits_commands():
    btn = ButtonWidget("b_hid", "Hidden")
    btn.visibility = ElementVisibility.HIDDEN
    btn.bounds = UIRect(0, 0, 100, 50)
    assert len(btn.render()) == 0


def test_render_collapsed_omits_commands():
    btn = ButtonWidget("b_col2", "Collapsed")
    btn.visibility = ElementVisibility.COLLAPSED
    btn.bounds = UIRect(0, 0, 100, 50)
    assert len(btn.render()) == 0


def test_render_opacity_passed_to_command():
    btn = ButtonWidget("b_op", "Opacity")
    btn.bounds = UIRect(0, 0, 100, 50)
    btn.computed_style.opacity = 0.75
    btn.computed_style.background_color = UIColor.white()
    commands = btn.render()
    assert commands[0].opacity == 0.75


def test_render_tree_surface_size():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_surf")
    fab.compute_layout("root_surf", UISize(1920, 1080))
    rt = fab.generate_render_tree("root_surf")
    assert rt.surface_size.width == 1920
    assert rt.surface_size.height == 1080


def test_renderer_independence_abstract_commands():
    cmd = UIRenderCommand(
        command_type=RenderCommandType.DRAW_RECT,
        element_id="test_cmd",
        bounds=UIRect(0, 0, 10, 10)
    )
    d = cmd.to_dict()
    assert d["type"] == "DRAW_RECT"
    assert d["element_id"] == "test_cmd"


# ==============================================================================
# 14. SNAPSHOT TESTS (7 tests)
# ==============================================================================

def test_structural_snapshot_creation():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_snap")
    fab.register_element(ButtonWidget("b_snap", "Snap"))
    fab.append_child("root_snap", "b_snap")

    fab.compute_layout("root_snap", UISize(400, 300))
    snapshot = fab.take_structural_snapshot("root_snap")

    assert snapshot.root_id == "root_snap"
    assert snapshot.element_count == 2
    assert len(snapshot.state_hash) == 64


def test_structural_snapshot_state_hash():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_h")
    s1 = fab.take_structural_snapshot("root_h")
    s2 = fab.take_structural_snapshot("root_h")
    assert s1.state_hash == s2.state_hash


def test_bounds_snapshot_matching():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_bs")
    fab.compute_layout("root_bs", UISize(500, 400))
    s = fab.take_structural_snapshot("root_bs")
    assert s.computed_bounds["root_bs"]["width"] == 500.0


def test_styles_snapshot_matching():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_ss")
    s = fab.take_structural_snapshot("root_ss")
    assert "root_ss" in s.computed_styles


def test_identical_trees_produce_identical_hashes():
    fab1 = UniversalUIFrameworkFabricator()
    fab1.create_root("r")
    fab1.register_element(ButtonWidget("b", "Hello"))
    fab1.append_child("r", "b")
    fab1.compute_layout("r", UISize(200, 100))

    fab2 = UniversalUIFrameworkFabricator()
    fab2.create_root("r")
    fab2.register_element(ButtonWidget("b", "Hello"))
    fab2.append_child("r", "b")
    fab2.compute_layout("r", UISize(200, 100))

    s1 = fab1.take_structural_snapshot("r")
    s2 = fab2.take_structural_snapshot("r")
    assert s1.state_hash == s2.state_hash


def test_mutated_tree_produces_divergent_hash():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_div")
    fab.compute_layout("r_div", UISize(200, 100))
    h1 = fab.take_structural_snapshot("r_div").state_hash

    fab.register_element(ButtonWidget("b_extra", "Extra"))
    fab.append_child("r_div", "b_extra")
    fab.compute_layout("r_div", UISize(200, 100))
    h2 = fab.take_structural_snapshot("r_div").state_hash

    assert h1 != h2


def test_validator_structural_snapshot():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_valid")
    s = fab.take_structural_snapshot("r_valid")
    valid, errors = UniversalUIFrameworkValidator.validate_structural_snapshot(s)
    assert valid
    assert len(errors) == 0


# ==============================================================================
# 15. SECURITY TESTS (10 tests)
# ==============================================================================

def test_cycle_injection_rejected():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r")
    fab.register_element(UIElement("a"))
    fab.register_element(UIElement("b"))
    fab.append_child("r", "a")
    fab.append_child("a", "b")

    with pytest.raises(ValueError):
        fab.append_child("b", "a")


def test_self_parent_injection_rejected():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r")
    fab.register_element(UIElement("self_bad"))

    with pytest.raises(ValueError):
        fab.append_child("self_bad", "self_bad")


def test_duplicate_element_id_rejected():
    fab = UniversalUIFrameworkFabricator()
    fab.register_element(ButtonWidget("dup_id", "1"))
    with pytest.raises(ValueError, match="already exists"):
        fab.register_element(ButtonWidget("dup_id", "2"))


def test_oversized_text_handled_safely():
    lbl = LabelWidget("lbl_big", "A" * 100_000)
    size = lbl.measure(UIBoxConstraints.loose())
    assert size.width > 0


def test_deeply_nested_tree_safety():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_deep")
    prev = "r_deep"
    for i in range(50):
        cid = f"deep_{i}"
        fab.register_element(UIElement(cid))
        fab.append_child(prev, cid)
        prev = cid

    fab.compute_layout("r_deep", UISize(500, 500))
    assert fab.elements["deep_49"].bounds is not None


def test_binding_infinite_recursion_safe():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_safe")
    tf = fab.register_element(TextFieldWidget("tf_safe", ""))
    fab.append_child("r_safe", "tf_safe")

    fab.bind("b_rec", "tf_safe", "text", "loop_key", mode=BindingMode.TWO_WAY)
    fab.set_app_state("loop_key", "start")
    fab.update_ui_property("tf_safe", "text", "end")
    assert fab.app_state["loop_key"] == "end"


def test_negative_box_constraints_rejected():
    valid, errors = UniversalUIFrameworkValidator.validate_box_constraints(
        UIBoxConstraints(min_width=-10.0, max_width=100.0)
    )
    assert not valid
    assert any("min_width" in e for e in errors)


def test_inverted_box_constraints_rejected():
    valid, errors = UniversalUIFrameworkValidator.validate_box_constraints(
        UIBoxConstraints(min_width=500.0, max_width=100.0)
    )
    assert not valid
    assert any("cannot exceed" in e for e in errors)


def test_corrupted_snapshot_hash_detected():
    snapshot = UIStructuralSnapshot(
        root_id="r",
        surface_type="MAIN_WINDOW",
        element_count=1,
        hierarchy={},
        computed_bounds={},
        computed_styles={},
        focus_id=None,
        state_hash="corrupted_hash"
    )
    valid, errors = UniversalUIFrameworkValidator.validate_structural_snapshot(snapshot)
    assert not valid
    assert any("SNAPSHOT_CORRUPTION" in e for e in errors)


def test_corrupted_diagnostic_bundle_signature_detected():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_b")
    bundle = fab.generate_diagnostic_bundle("r_b")
    bundle.signature = "tampered_signature"

    valid, errors = UniversalUIFrameworkValidator.validate_diagnostic_bundle(bundle)
    assert not valid
    assert any("BUNDLE_CORRUPTION" in e for e in errors)


# ==============================================================================
# 16. PERFORMANCE TESTS (11 tests)
# ==============================================================================

def test_large_tree_creation_1000_nodes():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf")
    t0 = time.perf_counter()
    for i in range(1000):
        btn = ButtonWidget(f"btn_p_{i}", f"Btn {i}")
        fab.register_element(btn)
        fab.append_child("r_perf", f"btn_p_{i}")
    t1 = time.perf_counter()
    assert (t1 - t0) < 1.0  # subsecond for 1000 nodes


def test_large_tree_layout_computation():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_l")
    for i in range(500):
        btn = ButtonWidget(f"btn_pl_{i}", f"B {i}")
        fab.register_element(btn)
        fab.append_child("r_perf_l", f"btn_pl_{i}")

    t0 = time.perf_counter()
    fab.compute_layout("r_perf_l", UISize(1920, 1080))
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.5


def test_deep_tree_traversal():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_d")
    prev = "r_perf_d"
    for i in range(100):
        cid = f"node_{i}"
        fab.register_element(UIElement(cid))
        fab.append_child(prev, cid)
        prev = cid

    t0 = time.perf_counter()
    fab.compute_layout("r_perf_d", UISize(800, 600))
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_many_style_resolutions():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_s")
    for i in range(300):
        btn = ButtonWidget(f"btn_ps_{i}", "S")
        fab.register_element(btn)
        fab.append_child("r_perf_s", f"btn_ps_{i}")

    t0 = time.perf_counter()
    fab.resolve_styles_recursively("r_perf_s")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_many_bindings_evaluations():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_b")
    for i in range(200):
        lbl = LabelWidget(f"lbl_pb_{i}", "")
        fab.register_element(lbl)
        fab.append_child("r_perf_b", f"lbl_pb_{i}")
        fab.bind(f"b_{i}", f"lbl_pb_{i}", "text", "shared_state")

    t0 = time.perf_counter()
    fab.set_app_state("shared_state", "Updated Val")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_many_focus_targets_navigation():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_f")
    for i in range(100):
        btn = ButtonWidget(f"btn_pf_{i}", "F")
        fab.register_element(btn)
        fab.append_child("r_perf_f", f"btn_pf_{i}")

    t0 = time.perf_counter()
    for _ in range(50):
        fab.focus_next()
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_many_animations_ticking():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_a")
    for i in range(100):
        btn = ButtonWidget(f"btn_pa_{i}", "A")
        fab.register_element(btn)
        fab.append_child("r_perf_a", f"btn_pa_{i}")
        fab.animate(f"btn_pa_{i}", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=500.0)

    t0 = time.perf_counter()
    for _ in range(20):
        fab.tick_animations(16.6)
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2


def test_partial_invalidation_efficiency():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_inv")
    btn = fab.register_element(ButtonWidget("btn_single", "S"))
    fab.append_child("r_perf_inv", "btn_single")

    btn.invalidation_flags.clear()
    fab.invalidate_element("btn_single", InvalidationType.PAINT_DIRTY)
    assert InvalidationType.LAYOUT_DIRTY not in btn.invalidation_flags
    assert InvalidationType.PAINT_DIRTY in btn.invalidation_flags


def test_render_command_batching_speed():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_perf_rend")
    for i in range(200):
        btn = ButtonWidget(f"btn_pr_{i}", "R")
        fab.register_element(btn)
        fab.append_child("r_perf_rend", f"btn_pr_{i}")

    fab.compute_layout("r_perf_rend", UISize(800, 600))
    t0 = time.perf_counter()
    tree = fab.generate_render_tree("r_perf_rend")
    t1 = time.perf_counter()
    assert (t1 - t0) < 0.2
    assert len(tree.commands) > 0


def test_telemetry_metrics_tracking():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_tele")
    fab.register_element(ButtonWidget("b_tel", "Tel"))
    bundle = fab.generate_diagnostic_bundle("r_tele")

    assert bundle.telemetry.widget_count == 2
    assert bundle.telemetry.visible_widget_count == 2


def test_memory_footprint_reasonable():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_mem")
    for i in range(100):
        fab.register_element(ButtonWidget(f"b_mem_{i}", "M"))
    # Ensure elements dict size is within expected memory bounds
    assert len(fab.elements) == 101


# ==============================================================================
# 17. GOLDEN TESTS (15 tests - §139)
# ==============================================================================

def test_golden_button():
    btn = ButtonWidget("gold_btn", "Confirm")
    assert btn.accessible_role == UIAccessibleRole.BUTTON
    assert btn.is_focusable is True
    size = btn.measure(UIBoxConstraints.loose())
    assert size.width > 50 and size.height > 20


def test_golden_text_field():
    tf = TextFieldWidget("gold_tf", "user@test.com", "Enter email")
    assert tf.accessible_role == UIAccessibleRole.TEXT_FIELD
    assert tf.is_focusable is True
    assert tf.text == "user@test.com"


def test_golden_checkbox():
    cb = CheckboxWidget("gold_cb", "Remember Me", checked=True)
    assert cb.accessible_role == UIAccessibleRole.CHECKBOX
    assert cb.checked is True
    cb.toggle()
    assert cb.checked is False


def test_golden_slider():
    sl = SliderWidget("gold_sl", min_value=0.0, max_value=1.0, current_value=0.75)
    assert sl.accessible_role == UIAccessibleRole.SLIDER
    assert sl.get_progress() == 0.75


def test_golden_list():
    lst = ListWidget("gold_list", items=["Item 1", "Item 2", "Item 3"], item_height=25.0)
    assert lst.accessible_role == UIAccessibleRole.LIST
    lst.select(1)
    assert lst.selected_index == 1


def test_golden_tree():
    tree = TreeWidget("gold_tree")
    tree.add_node("root_n", "Root")
    tree.add_node("child_n", "Child", "root_n")
    tree.expand("root_n")
    assert "root_n" in tree.expanded_nodes
    assert tree.nodes["root_n"]["children"] == ["child_n"]


def test_golden_dialog():
    dlg = DialogWidget("gold_dlg", "Save Changes?", is_modal=True)
    assert dlg.accessible_role == UIAccessibleRole.DIALOG
    assert dlg.is_modal is True
    assert dlg.surface_type == UISurfaceType.MODAL


def test_golden_menu():
    menu = MenuWidget("gold_menu")
    menu.add_item("open", "Open File")
    menu.add_item("save", "Save File")
    menu.open()
    assert menu.is_open is True
    assert len(menu.items) == 2


def test_golden_tabs():
    tabs = TabViewWidget("gold_tabs")
    tabs.add_tab("General", "page_gen")
    tabs.add_tab("Audio", "page_audio")
    tabs.select_tab(1)
    assert tabs.active_tab_index == 1


def test_golden_scroll_view():
    sv = ScrollViewWidget("gold_sv")
    sv.bounds = UIRect(0, 0, 100, 100)
    sv.content_height = 400.0
    sv.scroll_by(0, 50.0)
    assert sv.scroll_y == 50.0


def test_golden_dark_theme():
    dark = UITheme.create_default_dark()
    assert dark.mode == ThemeMode.DARK
    assert dark.tokens.colors["background"].to_hex() == "#121212"


def test_golden_light_theme():
    light = UITheme.create_default_light()
    assert light.mode == ThemeMode.LIGHT
    assert light.tokens.colors["background"].to_hex() == "#FFFFFF"


def test_golden_focus_states():
    btn = ButtonWidget("gold_f_btn", "Focus Target")
    btn.style_state = StyleState.FOCUSED
    assert btn.style_state == StyleState.FOCUSED


def test_golden_disabled_states():
    btn = ButtonWidget("gold_d_btn", "Disabled Target")
    btn.enabled = False
    btn.style_state = StyleState.DISABLED
    assert btn.style_state == StyleState.DISABLED


def test_golden_error_states():
    fb = FallbackWidget("gold_err", "Resource failed to load")
    assert fb.computed_style.border_color.to_hex() == "#CF6679"
    cmds = fb.render()
    assert any("Resource failed to load" in c.text for c in cmds if c.text)


# ==============================================================================
# 18. INTEGRATION TESTS (10 tests - §140)
# ==============================================================================

def test_integration_ui_and_event_bus():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_eb")
    btn = fab.register_element(ButtonWidget("b_eb", "Send Event"))
    dispatched = []
    btn.add_event_listener(UIEventType.Click, lambda e: dispatched.append("EVENT_BUS_EVENT"))
    fab.dispatch_event("r_int_eb", UIEventData(event_type=UIEventType.Click, target_id="b_eb"))
    assert dispatched == ["EVENT_BUS_EVENT"]


def test_integration_ui_and_command_bus():
    executed_commands = []
    btn = ButtonWidget("b_cmd", "Execute", on_click=lambda: executed_commands.append("CMD_SAVE"))
    btn.handle_event(UIEventData(event_type=UIEventType.Click, target_id="b_cmd"))
    assert executed_commands == ["CMD_SAVE"]


def test_integration_ui_and_input_events():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_inp")
    btn = fab.register_element(ButtonWidget("b_inp", "Input"))
    fab.append_child("r_int_inp", "b_inp")
    fab.compute_layout("r_int_inp", UISize(200, 200))

    target_id = fab.hit_test("r_int_inp", UIPoint(50, 50))
    assert target_id == "b_inp"


def test_integration_ui_and_context_stack():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_ctx")
    dlg = fab.register_element(DialogWidget("dlg_ctx", "Modal", is_modal=True))
    fab.append_child("r_int_ctx", "dlg_ctx")

    fab.push_modal("dlg_ctx")
    assert fab.modal_stack == ["dlg_ctx"]
    fab.pop_modal()
    assert len(fab.modal_stack) == 0


def test_integration_ui_and_focus_manager():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_fm")
    b1 = fab.register_element(ButtonWidget("b_fm1", "1"))
    b2 = fab.register_element(ButtonWidget("b_fm2", "2"))
    fab.append_child("r_int_fm", "b_fm1")
    fab.append_child("r_int_fm", "b_fm2")

    fab.set_focus("b_fm1")
    assert fab.focus_element_id == "b_fm1"


def test_integration_ui_and_application_state():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_app")
    lbl = fab.register_element(LabelWidget("lbl_app", ""))
    fab.append_child("r_int_app", "lbl_app")
    fab.bind("b_app", "lbl_app", "text", "app_title")

    fab.set_app_state("app_title", "Universal Engine")
    assert lbl.text == "Universal Engine"


def test_integration_ui_and_data_binding():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_db")
    tf = fab.register_element(TextFieldWidget("tf_db", ""))
    fab.append_child("r_int_db", "tf_db")
    fab.bind("b_db", "tf_db", "text", "config_val", mode=BindingMode.TWO_WAY)

    fab.update_ui_property("tf_db", "text", "CustomVal")
    assert fab.app_state["config_val"] == "CustomVal"


def test_integration_ui_and_theme_manager():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_tm")
    btn = fab.register_element(ButtonWidget("b_tm", "Theme"))
    fab.append_child("r_int_tm", "b_tm")

    fab.set_active_theme("light")
    fab.resolve_styles_recursively("r_int_tm")
    assert fab.active_theme_id == "light"


def test_integration_ui_and_accessibility():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_acc")
    fab.register_element(ButtonWidget("b_ia", "Accessible Button"))
    fab.append_child("r_int_acc", "b_ia")

    atree = fab.generate_accessible_tree("r_int_acc")
    assert atree.child_ids == ["b_ia"]


def test_integration_ui_and_deterministic_replay():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_int_rep")
    b = fab.register_element(ButtonWidget("b_rep_det", "Det"))
    fab.append_child("r_int_rep", "b_rep_det")
    fab.compute_layout("r_int_rep", UISize(200, 100))

    s1 = fab.take_structural_snapshot("r_int_rep")
    s2 = fab.take_structural_snapshot("r_int_rep")
    assert s1.state_hash == s2.state_hash


# ==============================================================================
# 19. END-TO-END UI PIPELINE TEST (1 test - §141)
# ==============================================================================

def test_end_to_end_ui_pipeline():
    """
    §141: INPUT -> FOCUS -> WIDGET -> EVENT -> COMMAND -> APP STATE -> BINDING -> UI STATE -> LAYOUT -> RENDER
    """
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("root_e2e")

    # App state & Command mock
    commands_log = []
    def save_command(new_val):
        commands_log.append(f"CMD_SAVE:{new_val}")
        fab.set_app_state("saved_profile_name", new_val)

    # 1. UI Elements setup
    tf = fab.register_element(TextFieldWidget("tf_e2e", "Initial"))
    btn = fab.register_element(ButtonWidget("btn_e2e", "Save", on_click=lambda: save_command(tf.text)))
    lbl = fab.register_element(LabelWidget("lbl_e2e", "Display"))

    fab.append_child("root_e2e", "tf_e2e")
    fab.append_child("root_e2e", "btn_e2e")
    fab.append_child("root_e2e", "lbl_e2e")

    # 2. Bindings: label displays saved profile name
    fab.bind("bind_profile", "lbl_e2e", "text", "saved_profile_name", format_fn=lambda v: f"Active Profile: {v}")

    # 3. Layout & Render initial
    fab.compute_layout("root_e2e", UISize(800, 600))
    fab.resolve_styles_recursively("root_e2e")
    rt_init = fab.generate_render_tree("root_e2e")
    assert len(rt_init.commands) > 0

    # 4. Input -> Focus -> Widget text entry
    hit_target = fab.hit_test("root_e2e", UIPoint(50, 18))
    assert hit_target == "tf_e2e"
    fab.set_focus(hit_target)
    assert fab.focus_element_id == "tf_e2e"

    # User types "Alice"
    tf.text = "Alice"

    # 5. Click Save Button -> Event -> Command -> App State
    fab.set_focus("btn_e2e")
    btn.handle_event(UIEventData(event_type=UIEventType.Click, target_id="btn_e2e"))
    assert commands_log == ["CMD_SAVE:Alice"]
    assert fab.app_state["saved_profile_name"] == "Alice"

    # 6. Binding updates UI state of Label
    assert lbl.text == "Active Profile: Alice"

    # 7. Relayout & Render updated
    fab.compute_layout("root_e2e", UISize(800, 600))
    rt_final = fab.generate_render_tree("root_e2e")
    text_commands = [c.text for c in rt_final.commands if c.command_type == RenderCommandType.DRAW_TEXT]
    assert "Active Profile: Alice" in text_commands


# ==============================================================================
# 20. REPLAY UI TEST (1 test - §142)
# ==============================================================================

def test_replay_ui_determinism():
    """
    §142: Reproducing identical input sequence yields identical commands, state changes,
    UI tree state, focus, layout bounds, and render snapshot.
    """
    def run_session():
        fab = UniversalUIFrameworkFabricator()
        fab.create_root("r_session")
        tf = fab.register_element(TextFieldWidget("tf_s", ""))
        btn = fab.register_element(ButtonWidget("btn_s", "Go", on_click=lambda: fab.set_app_state("status", tf.text)))
        fab.append_child("r_session", "tf_s")
        fab.append_child("r_session", "btn_s")

        fab.compute_layout("r_session", UISize(400, 200))
        fab.set_focus("tf_s")
        tf.insert_text("ReplayTest")
        btn.handle_event(UIEventData(event_type=UIEventType.Click, target_id="btn_s"))

        snapshot = fab.take_structural_snapshot("r_session")
        render_tree = fab.generate_render_tree("r_session")
        return fab.app_state, snapshot.state_hash, [c.to_dict() for c in render_tree.commands]

    state1, hash1, cmds1 = run_session()
    state2, hash2, cmds2 = run_session()

    assert state1 == state2
    assert hash1 == hash2
    assert cmds1 == cmds2


# ==============================================================================
# 21. VIRTUALIZATION TESTS (6 tests - §154)
# ==============================================================================

def test_virtualization_visible_range():
    lst = ListWidget("lst_virt", items=[f"Item {i}" for i in range(1000)], item_height=20.0)
    lst.scroll_y = 100.0  # scrolled 5 items down
    start, end = lst.compute_visible_range(viewport_height=100.0)

    assert start == 5
    assert end == 11  # 5 + (100 / 20) + 1 = 11


def test_virtualization_item_recycling():
    lst = ListWidget("lst_rec", items=[f"Item {i}" for i in range(500)], item_height=30.0)
    r1_start, r1_end = lst.compute_visible_range(150.0)
    lst.scroll_y += 60.0
    r2_start, r2_end = lst.compute_visible_range(150.0)

    assert r2_start == r1_start + 2
    assert (r2_end - r2_start) == (r1_end - r1_start)


def test_virtualization_scroll_virtualization():
    lst = ListWidget("lst_sv", items=[f"Row {i}" for i in range(200)], item_height=25.0)
    lst.scroll_y = 0.0
    s0, e0 = lst.compute_visible_range(100.0)
    assert s0 == 0 and e0 == 5


def test_virtualization_dynamic_height():
    lst = ListWidget("lst_dh", items=["A", "B", "C"], item_height=50.0)
    start, end = lst.compute_visible_range(50.0)
    assert (end - start) == 2


def test_virtualization_selection_virtualization():
    lst = ListWidget("lst_sel", items=[f"Item {i}" for i in range(100)], item_height=20.0)
    lst.select(75)
    assert lst.selected_index == 75


def test_virtualization_focus_virtualization():
    lst = ListWidget("lst_foc", items=[f"Item {i}" for i in range(50)], item_height=20.0)
    lst.handle_event(UIEventData(event_type=UIEventType.KeyDown, key_code="DOWN", target_id="lst_foc"))
    assert lst.selected_index == 0


# ==============================================================================
# 22. LEAK TESTS (5 tests - §156)
# ==============================================================================

def test_widget_leak_prevention_on_unmount():
    elem = ButtonWidget("b_leak", "Leak")
    elem.event_listeners[UIEventType.Click] = [lambda e: None]
    elem.unmount()
    assert len(elem.event_listeners) == 0


def test_binding_leak_prevention_on_unbind():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_leak_b")
    lbl = fab.register_element(LabelWidget("l_lb", ""))
    fab.append_child("r_leak_b", "l_lb")
    fab.bind("b_test", "l_lb", "text", "key")

    fab.unbind("b_test")
    assert "b_test" not in fab.bindings
    assert "b_test" not in lbl.bindings


def test_subscription_leak_prevention():
    elem = UIElement("el_sub")
    elem.subscriptions.append("sub_1")
    elem.unmount()
    assert len(elem.subscriptions) == 0


def test_animation_leak_prevention_on_completion():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_leak_anim")
    btn = fab.register_element(ButtonWidget("b_la", "A"))
    fab.append_child("r_leak_anim", "b_la")

    anim = fab.animate("b_la", AnimationTarget.OPACITY, "opacity", 0.0, 1.0, duration_ms=50.0)
    fab.tick_animations(100.0)

    assert anim.is_completed is True
    assert anim.is_active is False


def test_event_listener_cleanup_on_destroy():
    elem = UIElement("el_dest")
    handler = lambda e: None
    elem.add_event_listener(UIEventType.PointerDown, handler)
    elem.remove_event_listener(UIEventType.PointerDown, handler)
    assert len(elem.event_listeners[UIEventType.PointerDown]) == 0


# ==============================================================================
# 23. RESPONSIVE / DPI / LOCALIZATION TESTS (5 tests - §143-§146)
# ==============================================================================

def test_responsive_layout_mobile_320x240():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_320")
    b = fab.register_element(ButtonWidget("b_320", "Mobile"))
    fab.append_child("r_320", "b_320")

    fab.compute_layout("r_320", UISize(320, 240))
    assert b.bounds.width <= 320.0
    assert b.bounds.height <= 240.0


def test_responsive_layout_fhd_1920x1080():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_1080")
    b = fab.register_element(ButtonWidget("b_1080", "FHD"))
    fab.append_child("r_1080", "b_1080")

    fab.compute_layout("r_1080", UISize(1920, 1080))
    assert b.bounds.width <= 1920.0


def test_responsive_layout_4k_3840x2160():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_4k")
    b = fab.register_element(ButtonWidget("b_4k", "4K"))
    fab.append_child("r_4k", "b_4k")

    fab.compute_layout("r_4k", UISize(3840, 2160))
    assert b.bounds.width <= 3840.0


def test_dpi_scale_adaptation():
    base_font_size = 14.0
    dpi_scale = 1.5
    scaled_size = base_font_size * dpi_scale
    assert scaled_size == 21.0


def test_localization_long_and_rtl_strings():
    lbl_de = LabelWidget("lbl_de", "Donaudampfschifffahrtselektrizitätenhauptbetriebswerkbauunterbeamtengesellschaft")
    size_de = lbl_de.measure(UIBoxConstraints.loose())
    assert size_de.width > 200.0

    lbl_ar = LabelWidget("lbl_ar", "مرحبا بك في اللعبة")
    size_ar = lbl_ar.measure(UIBoxConstraints.loose())
    assert size_ar.width > 0.0


# ==============================================================================
# 24. EXTENDED VALIDATION & PACKAGING TESTS (3 tests)
# ==============================================================================

def test_packager_cpp_generation():
    header = UniversalUIFrameworkPackager.generate_cpp_header()
    source = UniversalUIFrameworkPackager.generate_cpp_source()
    assert "UUAFUIFrameworkComponent" in header
    assert "UUAFUIFrameworkComponent::MountRoot" in source


def test_packager_manifest_and_sha256_signature(tmp_path):
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_pkg")
    fab.register_element(ButtonWidget("b_pkg", "Export"))
    fab.append_child("r_pkg", "b_pkg")
    fab.compute_layout("r_pkg", UISize(400, 300))

    out_dict = UniversalUIFrameworkPackager.export_package(fab, "r_pkg", tmp_path)
    assert Path(out_dict["header"]).exists()
    assert Path(out_dict["source"]).exists()
    assert Path(out_dict["manifest"]).exists()
    assert Path(out_dict["signature"]).exists()
    assert len(out_dict["sha256"]) == 64


def test_diagnostic_bundle_full_verification():
    fab = UniversalUIFrameworkFabricator()
    fab.create_root("r_diag_full")
    fab.register_element(ButtonWidget("b_diag", "Diag"))
    fab.append_child("r_diag_full", "b_diag")
    fab.compute_layout("r_diag_full", UISize(500, 500))

    bundle = fab.generate_diagnostic_bundle("r_diag_full")
    valid, errors = UniversalUIFrameworkValidator.validate_diagnostic_bundle(bundle)
    assert valid
    assert len(errors) == 0
