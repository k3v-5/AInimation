"""
UAF-81.66: Universal UI Framework Fabricator Engine.
Authoritative retained UI tree, layout engine, style resolver, theme manager,
data binding system, focus & accessibility manager, animation clock, and render command generator.
"""

from __future__ import annotations
import math
import time
import copy
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from uaf.universal_ui_framework.models.definition import (
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
)


# ==============================================================================
# UI ELEMENT BASE CLASS
# ==============================================================================

class UIElement:
    """Base class for all elements in the retained UI tree."""
    def __init__(
        self,
        element_id: str,
        surface_type: UISurfaceType = UISurfaceType.MAIN_WINDOW,
        accessible_role: UIAccessibleRole = UIAccessibleRole.PANEL,
        accessible_name: str = "",
        accessible_description: str = ""
    ):
        self.element_id = element_id
        self.surface_type = surface_type
        self.parent_id: Optional[str] = None
        self.children_ids: List[str] = []
        self.visibility = ElementVisibility.VISIBLE
        self.enabled = True
        self.lifecycle = ElementLifecycle.CREATED
        self.pointer_events = PointerEventPolicy.AUTO
        self.bounds = UIRect(0, 0, 0, 0)
        self.local_bounds = UIRect(0, 0, 0, 0)
        self.clip_rect: Optional[UIRect] = None
        self.style_state = StyleState.NORMAL
        self.class_names: Set[str] = set()
        self.inline_style: Optional[UIStyleDeclaration] = None
        self.computed_style = UIStyleDeclaration()
        self.state: Dict[str, Any] = {}
        self.bindings: List[str] = []
        self.subscriptions: List[str] = []

        # Sizing & Constraints
        self.size_mode_width = SizeMode.AUTO
        self.size_mode_height = SizeMode.AUTO
        self.fixed_width: float = 0.0
        self.fixed_height: float = 0.0
        self.percent_width: float = 100.0
        self.percent_height: float = 100.0
        self.min_width: float = 0.0
        self.max_width: float = float("inf")
        self.min_height: float = 0.0
        self.max_height: float = float("inf")

        # Flex & Box
        self.flex_direction = FlexDirection.COLUMN
        self.flex_grow: float = 0.0
        self.flex_shrink: float = 1.0
        self.flex_basis: float = 0.0
        self.gap: float = 0.0
        self.layout_alignment = LayoutAlignment.START
        self.layout_distribution = LayoutDistribution.SPACE_START
        self.layout_positioning = LayoutPositioning.FLOW
        self.z_index: int = 0

        # Focus & Accessibility
        self.is_focusable = False
        self.tab_index: int = 0
        self.accessible_role = accessible_role
        self.accessible_name = accessible_name
        self.accessible_description = accessible_description

        # Invalidation
        self.invalidation_flags: Set[InvalidationType] = {
            InvalidationType.STYLE_DIRTY,
            InvalidationType.LAYOUT_DIRTY,
            InvalidationType.PAINT_DIRTY
        }

        # Event Handlers: list of (handler, use_capture)
        self.event_listeners: Dict[UIEventType, List[Tuple[Callable[[UIEventData], None], bool]]] = {}

    def add_event_listener(self, event_type: UIEventType, handler: Callable[[UIEventData], None], use_capture: bool = False) -> None:
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append((handler, use_capture))

    def remove_event_listener(self, event_type: UIEventType, handler: Callable[[UIEventData], None]) -> None:
        if event_type in self.event_listeners:
            self.event_listeners[event_type] = [(h, c) for (h, c) in self.event_listeners[event_type] if h != handler]

    def mount(self) -> None:
        self.lifecycle = ElementLifecycle.MOUNTED
        self.on_mount()

    def unmount(self) -> None:
        self.lifecycle = ElementLifecycle.UNMOUNTING
        self.on_unmount()
        self.lifecycle = ElementLifecycle.DESTROYED

    def on_mount(self) -> None:
        pass

    def on_unmount(self) -> None:
        self.event_listeners.clear()
        self.bindings.clear()
        self.subscriptions.clear()

    def measure(self, constraints: UIBoxConstraints) -> UISize:
        w = self.fixed_width if self.size_mode_width == SizeMode.FIXED else self.min_width
        h = self.fixed_height if self.size_mode_height == SizeMode.FIXED else self.min_height
        style_padding = self.computed_style.padding.horizontal
        style_padding_v = self.computed_style.padding.vertical
        w += style_padding
        h += style_padding_v
        return constraints.constrain(UISize(w, h))

    def layout(self, bounds: UIRect) -> None:
        self.bounds = bounds
        self.local_bounds = UIRect(0, 0, bounds.width, bounds.height)

    def render(self) -> List[UIRenderCommand]:
        commands: List[UIRenderCommand] = []
        if self.visibility != ElementVisibility.VISIBLE or self.bounds.width <= 0 or self.bounds.height <= 0:
            return commands

        bg_color = self.computed_style.background_color
        border_color = self.computed_style.border_color
        border_width = self.computed_style.border_width
        border_radius = self.computed_style.border_radius
        opacity = self.computed_style.opacity

        if bg_color or (border_color and border_width > 0):
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_RECT,
                element_id=self.element_id,
                bounds=self.bounds,
                color=bg_color,
                border_color=border_color,
                border_width=border_width,
                border_radius=border_radius,
                opacity=opacity,
                z_index=self.computed_style.z_index or self.z_index,
                clip_rect=self.clip_rect
            ))
        return commands

    def handle_event(self, event: UIEventData) -> None:
        event.current_target_id = self.element_id
        if event.event_type in self.event_listeners:
            for handler, use_capture in self.event_listeners[event.event_type]:
                if event.phase == EventPhase.CAPTURE and not use_capture:
                    continue
                if event.phase == EventPhase.BUBBLE and use_capture:
                    continue
                handler(event)
                if event.is_propagation_stopped:
                    break


# ==============================================================================
# STANDARD WIDGET IMPLEMENTATIONS
# ==============================================================================

class LabelWidget(UIElement):
    """Text rendering label."""
    def __init__(self, element_id: str, text: str = "", typography: Optional[UITypography] = None):
        super().__init__(element_id, accessible_role=UIAccessibleRole.LABEL, accessible_name=text)
        self.text = text
        self.typography = typography or UITypography()
        self.size_mode_width = SizeMode.CONTENT
        self.size_mode_height = SizeMode.CONTENT

    def measure(self, constraints: UIBoxConstraints) -> UISize:
        # Approximate text measurement based on font size and character count
        char_w = self.typography.font_size * 0.6
        line_h = self.typography.font_size * self.typography.line_height
        raw_w = len(self.text) * char_w
        raw_h = line_h

        if self.typography.text_wrapping == TextWrapping.WORD_WRAP and raw_w > constraints.max_width:
            lines = math.ceil(raw_w / max(1.0, constraints.max_width))
            raw_w = constraints.max_width
            raw_h = lines * line_h

        w = raw_w + self.computed_style.padding.horizontal
        h = raw_h + self.computed_style.padding.vertical
        return constraints.constrain(UISize(w, h))

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE and self.text:
            text_color = self.computed_style.text_color or self.typography.text_color
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_TEXT,
                element_id=self.element_id,
                bounds=self.bounds,
                color=text_color,
                text=self.text,
                font=self.typography,
                z_index=self.computed_style.z_index or self.z_index + 1,
                clip_rect=self.clip_rect,
                opacity=self.computed_style.opacity
            ))
        return commands


class ButtonWidget(UIElement):
    """Interactive clickable button."""
    def __init__(self, element_id: str, text: str = "", on_click: Optional[Callable[[], None]] = None):
        super().__init__(element_id, accessible_role=UIAccessibleRole.BUTTON, accessible_name=text)
        self.text = text
        self.on_click_callback = on_click
        self.is_focusable = True
        self.size_mode_width = SizeMode.CONTENT
        self.size_mode_height = SizeMode.CONTENT
        self.state["pressed"] = False
        self.state["hovered"] = False

    def measure(self, constraints: UIBoxConstraints) -> UISize:
        font_size = self.computed_style.font.font_size if self.computed_style.font else 14.0
        char_w = font_size * 0.6
        w = len(self.text) * char_w + 24.0 + self.computed_style.padding.horizontal
        h = font_size * 1.5 + 16.0 + self.computed_style.padding.vertical
        return constraints.constrain(UISize(w, h))

    def handle_event(self, event: UIEventData) -> None:
        super().handle_event(event)
        if not self.enabled:
            return

        if event.event_type == UIEventType.PointerDown:
            self.state["pressed"] = True
            self.style_state = StyleState.ACTIVE
        elif event.event_type == UIEventType.PointerUp:
            if self.state.get("pressed", False):
                self.state["pressed"] = False
                self.style_state = StyleState.HOVER if self.state.get("hovered", False) else StyleState.NORMAL
                if self.on_click_callback:
                    self.on_click_callback()
        elif event.event_type == UIEventType.PointerEnter:
            self.state["hovered"] = True
            if not self.state.get("pressed", False):
                self.style_state = StyleState.HOVER
        elif event.event_type == UIEventType.PointerLeave:
            self.state["hovered"] = False
            self.state["pressed"] = False
            self.style_state = StyleState.NORMAL
        elif event.event_type == UIEventType.Click:
            if self.on_click_callback:
                self.on_click_callback()

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE and self.text:
            text_color = self.computed_style.text_color or UIColor.white()
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_TEXT,
                element_id=self.element_id,
                bounds=self.bounds,
                color=text_color,
                text=self.text,
                font=self.computed_style.font,
                z_index=self.computed_style.z_index or self.z_index + 1,
                clip_rect=self.clip_rect,
                opacity=self.computed_style.opacity
            ))
        return commands


class TextFieldWidget(UIElement):
    """Editable single-line text input field."""
    def __init__(self, element_id: str, initial_text: str = "", placeholder: str = ""):
        super().__init__(element_id, accessible_role=UIAccessibleRole.TEXT_FIELD, accessible_name=placeholder)
        self.text = initial_text
        self.placeholder = placeholder
        self.cursor_position = len(initial_text)
        self.selection_range: Optional[Tuple[int, int]] = None
        self.is_focusable = True
        self.size_mode_width = SizeMode.FIXED
        self.size_mode_height = SizeMode.FIXED
        self.fixed_width = 200.0
        self.fixed_height = 36.0
        self.state["text"] = initial_text

    def insert_text(self, new_text: str) -> None:
        self.text = self.text[:self.cursor_position] + new_text + self.text[self.cursor_position:]
        self.cursor_position += len(new_text)
        self.state["text"] = self.text

    def delete_backward(self) -> None:
        if self.cursor_position > 0:
            self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
            self.cursor_position -= 1
            self.state["text"] = self.text

    def handle_event(self, event: UIEventData) -> None:
        super().handle_event(event)
        if not self.enabled:
            return
        if event.event_type == UIEventType.TextInput and event.text_content:
            self.insert_text(event.text_content)
        elif event.event_type == UIEventType.KeyDown:
            if event.key_code == "BACKSPACE":
                self.delete_backward()
            elif event.key_code == "LEFT":
                self.cursor_position = max(0, self.cursor_position - 1)
            elif event.key_code == "RIGHT":
                self.cursor_position = min(len(self.text), self.cursor_position + 1)

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE:
            display_text = self.text if self.text else self.placeholder
            text_color = self.computed_style.text_color if self.text else UIColor.from_hex("#888888")
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_TEXT,
                element_id=self.element_id,
                bounds=self.bounds,
                color=text_color,
                text=display_text,
                font=self.computed_style.font,
                z_index=self.computed_style.z_index or self.z_index + 1,
                clip_rect=self.clip_rect
            ))
        return commands


class CheckboxWidget(UIElement):
    """Toggleable checkbox."""
    def __init__(self, element_id: str, label: str = "", checked: bool = False):
        super().__init__(element_id, accessible_role=UIAccessibleRole.CHECKBOX, accessible_name=label)
        self.label = label
        self.checked = checked
        self.is_focusable = True
        self.state["checked"] = checked
        self.size_mode_width = SizeMode.CONTENT
        self.size_mode_height = SizeMode.CONTENT

    def toggle(self) -> None:
        if self.enabled:
            self.checked = not self.checked
            self.state["checked"] = self.checked

    def handle_event(self, event: UIEventData) -> None:
        super().handle_event(event)
        if self.enabled and (event.event_type == UIEventType.Click or (event.event_type == UIEventType.KeyDown and event.key_code == "SPACE")):
            self.toggle()

    def measure(self, constraints: UIBoxConstraints) -> UISize:
        w = 20.0 + len(self.label) * 8.0 + 8.0 + self.computed_style.padding.horizontal
        h = 24.0 + self.computed_style.padding.vertical
        return constraints.constrain(UISize(w, h))

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE:
            box_rect = UIRect(self.bounds.x + 2, self.bounds.y + 2, 16, 16)
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_RECT,
                element_id=f"{self.element_id}_box",
                bounds=box_rect,
                color=UIColor.from_hex("#03DAC6") if self.checked else UIColor.transparent(),
                border_color=UIColor.white(),
                border_width=1.5,
                border_radius=3.0,
                z_index=self.z_index + 1
            ))
            if self.label:
                text_rect = UIRect(self.bounds.x + 24, self.bounds.y, self.bounds.width - 24, self.bounds.height)
                commands.append(UIRenderCommand(
                    command_type=RenderCommandType.DRAW_TEXT,
                    element_id=f"{self.element_id}_lbl",
                    bounds=text_rect,
                    color=self.computed_style.text_color or UIColor.white(),
                    text=self.label,
                    z_index=self.z_index + 1
                ))
        return commands


class SliderWidget(UIElement):
    """Numeric continuous range slider."""
    def __init__(self, element_id: str, min_value: float = 0.0, max_value: float = 100.0, current_value: float = 50.0):
        super().__init__(element_id, accessible_role=UIAccessibleRole.SLIDER, accessible_name=element_id)
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = max(min_value, min(max_value, current_value))
        self.is_focusable = True
        self.fixed_width = 160.0
        self.fixed_height = 24.0
        self.size_mode_width = SizeMode.FIXED
        self.size_mode_height = SizeMode.FIXED
        self.state["value"] = self.current_value

    def set_value(self, val: float) -> None:
        self.current_value = max(self.min_value, min(self.max_value, val))
        self.state["value"] = self.current_value

    def get_progress(self) -> float:
        span = self.max_value - self.min_value
        return (self.current_value - self.min_value) / span if span > 0 else 0.0

    def handle_event(self, event: UIEventData) -> None:
        super().handle_event(event)
        if not self.enabled:
            return
        if event.event_type in (UIEventType.PointerDown, UIEventType.PointerMove) and self.bounds.width > 0:
            rel_x = max(0.0, min(self.bounds.width, event.pointer_pos.x - self.bounds.x))
            frac = rel_x / self.bounds.width
            self.set_value(self.min_value + frac * (self.max_value - self.min_value))
        elif event.event_type == UIEventType.KeyDown:
            step = (self.max_value - self.min_value) * 0.05
            if event.key_code == "LEFT":
                self.set_value(self.current_value - step)
            elif event.key_code == "RIGHT":
                self.set_value(self.current_value + step)

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE:
            track_rect = UIRect(self.bounds.x, self.bounds.y + self.bounds.height / 2 - 2, self.bounds.width, 4)
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_RECT,
                element_id=f"{self.element_id}_track",
                bounds=track_rect,
                color=UIColor.from_hex("#444444"),
                border_radius=2.0,
                z_index=self.z_index + 1
            ))
            handle_x = self.bounds.x + self.get_progress() * self.bounds.width
            handle_rect = UIRect(handle_x - 6, self.bounds.y + self.bounds.height / 2 - 8, 12, 16)
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_RECT,
                element_id=f"{self.element_id}_handle",
                bounds=handle_rect,
                color=UIColor.from_hex("#BB86FC"),
                border_radius=3.0,
                z_index=self.z_index + 2
            ))
        return commands


class ListWidget(UIElement):
    """Selectable list with item recycling / virtualization."""
    def __init__(self, element_id: str, items: Optional[List[str]] = None, item_height: float = 30.0):
        super().__init__(element_id, accessible_role=UIAccessibleRole.LIST, accessible_name=element_id)
        self.items = items or []
        self.item_height = item_height
        self.selected_index: int = -1
        self.scroll_y: float = 0.0
        self.is_focusable = True
        self.state["selected_index"] = self.selected_index

    def select(self, index: int) -> None:
        if 0 <= index < len(self.items):
            self.selected_index = index
            self.state["selected_index"] = index

    def compute_visible_range(self, viewport_height: float) -> Tuple[int, int]:
        if not self.items or self.item_height <= 0:
            return (0, 0)
        start = max(0, int(self.scroll_y // self.item_height))
        visible_count = math.ceil(viewport_height / self.item_height) + 1
        end = min(len(self.items), start + visible_count)
        return (start, end)

    def handle_event(self, event: UIEventData) -> None:
        super().handle_event(event)
        if not self.enabled:
            return
        if event.event_type == UIEventType.KeyDown:
            if event.key_code == "DOWN":
                self.select(min(len(self.items) - 1, self.selected_index + 1))
            elif event.key_code == "UP":
                self.select(max(0, self.selected_index - 1))
        elif event.event_type == UIEventType.PointerDown and self.item_height > 0:
            rel_y = event.pointer_pos.y - self.bounds.y + self.scroll_y
            idx = int(rel_y // self.item_height)
            self.select(idx)


class TreeWidget(UIElement):
    """Hierarchical collapsible tree."""
    def __init__(self, element_id: str):
        super().__init__(element_id, accessible_role=UIAccessibleRole.TREE, accessible_name=element_id)
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.expanded_nodes: Set[str] = set()
        self.selected_node_id: Optional[str] = None
        self.is_focusable = True

    def add_node(self, node_id: str, label: str, parent_node_id: Optional[str] = None) -> None:
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "parent_id": parent_node_id,
            "children": []
        }
        if parent_node_id and parent_node_id in self.nodes:
            self.nodes[parent_node_id]["children"].append(node_id)

    def expand(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.expanded_nodes.add(node_id)

    def collapse(self, node_id: str) -> None:
        self.expanded_nodes.discard(node_id)

    def select(self, node_id: str) -> None:
        if node_id in self.nodes:
            self.selected_node_id = node_id
            self.state["selected_node"] = node_id


class ScrollViewWidget(UIElement):
    """Container with scrolling offsets and scrollbars."""
    def __init__(self, element_id: str):
        super().__init__(element_id, accessible_role=UIAccessibleRole.PANEL)
        self.scroll_x: float = 0.0
        self.scroll_y: float = 0.0
        self.content_width: float = 0.0
        self.content_height: float = 0.0
        self.state["scroll_x"] = 0.0
        self.state["scroll_y"] = 0.0

    def scroll_by(self, dx: float, dy: float) -> None:
        max_scroll_x = max(0.0, self.content_width - self.bounds.width)
        max_scroll_y = max(0.0, self.content_height - self.bounds.height)
        self.scroll_x = max(0.0, min(max_scroll_x, self.scroll_x + dx))
        self.scroll_y = max(0.0, min(max_scroll_y, self.scroll_y + dy))
        self.state["scroll_x"] = self.scroll_x
        self.state["scroll_y"] = self.scroll_y


class ImageWidget(UIElement):
    """Bitmap or vector image renderer."""
    def __init__(self, element_id: str, asset_id: str = ""):
        super().__init__(element_id, accessible_role=UIAccessibleRole.IMAGE, accessible_name=asset_id)
        self.asset_id = asset_id

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE and self.asset_id:
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_IMAGE,
                element_id=self.element_id,
                bounds=self.bounds,
                image_asset=self.asset_id,
                z_index=self.z_index + 1,
                clip_rect=self.clip_rect
            ))
        return commands


class ProgressBarWidget(UIElement):
    """Linear progress indicator."""
    def __init__(self, element_id: str, progress: float = 0.0):
        super().__init__(element_id, accessible_role=UIAccessibleRole.SLIDER)
        self.progress = max(0.0, min(1.0, progress))
        self.fixed_height = 12.0
        self.size_mode_height = SizeMode.FIXED

    def set_progress(self, val: float) -> None:
        self.progress = max(0.0, min(1.0, val))

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        if self.visibility == ElementVisibility.VISIBLE and self.progress > 0:
            fill_rect = UIRect(self.bounds.x, self.bounds.y, self.bounds.width * self.progress, self.bounds.height)
            commands.append(UIRenderCommand(
                command_type=RenderCommandType.DRAW_RECT,
                element_id=f"{self.element_id}_fill",
                bounds=fill_rect,
                color=UIColor.from_hex("#03DAC6"),
                border_radius=self.computed_style.border_radius,
                z_index=self.z_index + 1
            ))
        return commands


class TabViewWidget(UIElement):
    """Multi-tab page switcher."""
    def __init__(self, element_id: str):
        super().__init__(element_id, accessible_role=UIAccessibleRole.TAB)
        self.tabs: List[Tuple[str, str]] = []  # (title, content_id)
        self.active_tab_index: int = 0

    def add_tab(self, title: str, content_element_id: str) -> None:
        self.tabs.append((title, content_element_id))

    def select_tab(self, index: int) -> None:
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index
            self.state["active_tab"] = index


class MenuWidget(UIElement):
    """Popup or dropdown context menu."""
    def __init__(self, element_id: str):
        super().__init__(element_id, accessible_role=UIAccessibleRole.PANEL)
        self.items: List[Dict[str, Any]] = []
        self.is_open: bool = False
        self.active_item_index: int = -1

    def add_item(self, item_id: str, label: str, action: Optional[Callable[[], None]] = None) -> None:
        self.items.append({"id": item_id, "label": label, "action": action})

    def open(self) -> None:
        self.is_open = True
        self.visibility = ElementVisibility.VISIBLE

    def close(self) -> None:
        self.is_open = False
        self.visibility = ElementVisibility.HIDDEN


class DialogWidget(UIElement):
    """Modal or modeless dialog overlay."""
    def __init__(self, element_id: str, title: str = "", is_modal: bool = True):
        super().__init__(element_id, surface_type=UISurfaceType.MODAL if is_modal else UISurfaceType.POPUP, accessible_role=UIAccessibleRole.DIALOG, accessible_name=title)
        self.title = title
        self.is_modal = is_modal
        self.is_open: bool = False
        self.focus_trap: bool = is_modal
        self.restored_focus_id: Optional[str] = None
        self.z_index = 1000

    def open(self) -> None:
        self.is_open = True
        self.visibility = ElementVisibility.VISIBLE

    def close(self) -> None:
        self.is_open = False
        self.visibility = ElementVisibility.HIDDEN


class FallbackWidget(UIElement):
    """Graceful error-boundary fallback for invalid/corrupted elements."""
    def __init__(self, element_id: str, error_message: str = "Widget Error"):
        super().__init__(element_id, accessible_role=UIAccessibleRole.PANEL, accessible_name="Error Fallback")
        self.error_message = error_message
        self.computed_style = UIStyleDeclaration(
            background_color=UIColor.from_hex("#331111"),
            border_color=UIColor.from_hex("#CF6679"),
            border_width=1.0,
            text_color=UIColor.from_hex("#CF6679")
        )

    def render(self) -> List[UIRenderCommand]:
        commands = super().render()
        commands.append(UIRenderCommand(
            command_type=RenderCommandType.DRAW_TEXT,
            element_id=f"{self.element_id}_err",
            bounds=self.bounds,
            color=UIColor.from_hex("#CF6679"),
            text=f"⚠ {self.error_message}",
            z_index=self.z_index + 1
        ))
        return commands


# ==============================================================================
# UNIVERSAL UI FRAMEWORK FABRICATOR
# ==============================================================================

class UniversalUIFrameworkFabricator:
    """
    Authoritative Universal UI Framework Fabricator.
    Manages multi-surface root ownership, retained element hierarchy, flex/grid/stack layout,
    cascading style resolution, light/dark theming, input routing, focus navigation & traps,
    two-way data bindings, deterministic animations, invalidation, snapshots and telemetry.
    """

    def __init__(self):
        self.roots: Dict[str, UIElement] = {}
        self.elements: Dict[str, UIElement] = {}
        self.themes: Dict[str, UITheme] = {
            "dark": UITheme.create_default_dark(),
            "light": UITheme.create_default_light()
        }
        self.active_theme_id: str = "dark"
        self.bindings: Dict[str, UIBinding] = {}
        self.app_state: Dict[str, Any] = {}
        self.animations: Dict[str, UIAnimation] = {}
        self.focus_element_id: Optional[str] = None
        self.focus_history: List[str] = []
        self.modal_stack: List[str] = []
        self.reduced_motion: bool = False
        self.event_queue: List[UIEventData] = []
        self.telemetry = UITelemetry()
        self._syncing_bindings: Set[str] = set()

    # --------------------------------------------------------------------------
    # Tree Management & Invariants
    # --------------------------------------------------------------------------

    def create_root(self, root_id: str, surface_type: UISurfaceType = UISurfaceType.MAIN_WINDOW) -> UIElement:
        root = UIElement(element_id=root_id, surface_type=surface_type)
        root.mount()
        self.roots[root_id] = root
        self.elements[root_id] = root
        return root

    def register_element(self, element: UIElement) -> UIElement:
        if element.element_id in self.elements:
            raise ValueError(f"Element ID '{element.element_id}' already exists in UI framework.")
        self.elements[element.element_id] = element
        return element

    def append_child(self, parent_id: str, child_id: str) -> None:
        if parent_id == child_id:
            raise ValueError(f"Tree invariant violated: Element '{parent_id}' cannot be its own parent.")
        if parent_id not in self.elements or child_id not in self.elements:
            raise KeyError(f"Parent '{parent_id}' or Child '{child_id}' not found.")

        # Cycle check
        if self._would_create_cycle(parent_id, child_id):
            raise ValueError(f"Tree invariant violated: Appending '{child_id}' to '{parent_id}' creates a cycle.")

        child = self.elements[child_id]
        if child.parent_id and child.parent_id != parent_id:
            self.remove_child(child.parent_id, child_id)

        parent = self.elements[parent_id]
        if child_id not in parent.children_ids:
            parent.children_ids.append(child_id)
        child.parent_id = parent_id
        child.surface_type = parent.surface_type
        if child.lifecycle == ElementLifecycle.CREATED:
            child.mount()
        self.invalidate_element(parent_id, InvalidationType.LAYOUT_DIRTY)

    def insert_child(self, parent_id: str, child_id: str, index: int) -> None:
        if parent_id == child_id:
            raise ValueError(f"Tree invariant violated: Self-parenting forbidden for '{parent_id}'.")
        if parent_id not in self.elements or child_id not in self.elements:
            raise KeyError(f"Parent '{parent_id}' or Child '{child_id}' not found.")
        if self._would_create_cycle(parent_id, child_id):
            raise ValueError(f"Tree invariant violated: Cycle detected.")

        child = self.elements[child_id]
        if child.parent_id:
            self.remove_child(child.parent_id, child_id)

        parent = self.elements[parent_id]
        idx = max(0, min(len(parent.children_ids), index))
        parent.children_ids.insert(idx, child_id)
        child.parent_id = parent_id
        child.surface_type = parent.surface_type
        if child.lifecycle == ElementLifecycle.CREATED:
            child.mount()
        self.invalidate_element(parent_id, InvalidationType.LAYOUT_DIRTY)

    def remove_child(self, parent_id: str, child_id: str) -> None:
        if parent_id in self.elements and child_id in self.elements:
            parent = self.elements[parent_id]
            if child_id in parent.children_ids:
                parent.children_ids.remove(child_id)
            child = self.elements[child_id]
            if child.parent_id == parent_id:
                child.parent_id = None
            self.invalidate_element(parent_id, InvalidationType.LAYOUT_DIRTY)

    def replace_child(self, parent_id: str, old_child_id: str, new_child_id: str) -> None:
        if parent_id not in self.elements:
            raise KeyError(f"Parent '{parent_id}' not found.")
        parent = self.elements[parent_id]
        if old_child_id not in parent.children_ids:
            raise ValueError(f"Old child '{old_child_id}' not in parent '{parent_id}'.")
        idx = parent.children_ids.index(old_child_id)
        self.remove_child(parent_id, old_child_id)
        self.insert_child(parent_id, new_child_id, idx)

    def move_child(self, parent_id: str, child_id: str, new_index: int) -> None:
        if parent_id not in self.elements:
            raise KeyError(f"Parent '{parent_id}' not found.")
        parent = self.elements[parent_id]
        if child_id not in parent.children_ids:
            raise ValueError(f"Child '{child_id}' not in parent '{parent_id}'.")
        parent.children_ids.remove(child_id)
        idx = max(0, min(len(parent.children_ids), new_index))
        parent.children_ids.insert(idx, child_id)
        self.invalidate_element(parent_id, InvalidationType.LAYOUT_DIRTY)

    def clear_children(self, parent_id: str) -> None:
        if parent_id in self.elements:
            parent = self.elements[parent_id]
            for child_id in list(parent.children_ids):
                self.remove_child(parent_id, child_id)

    def _would_create_cycle(self, parent_id: str, candidate_child_id: str) -> bool:
        curr = parent_id
        while curr:
            if curr == candidate_child_id:
                return True
            elem = self.elements.get(curr)
            curr = elem.parent_id if elem else None
        return False

    # --------------------------------------------------------------------------
    # Invalidation System
    # --------------------------------------------------------------------------

    def invalidate_element(self, element_id: str, inv_type: InvalidationType) -> None:
        if element_id not in self.elements:
            return
        elem = self.elements[element_id]
        elem.invalidation_flags.add(inv_type)
        if inv_type in (InvalidationType.LAYOUT_DIRTY, InvalidationType.CHILDREN_DIRTY):
            curr = elem.parent_id
            while curr:
                if curr in self.elements:
                    self.elements[curr].invalidation_flags.add(InvalidationType.LAYOUT_DIRTY)
                    curr = self.elements[curr].parent_id
                else:
                    break

    # --------------------------------------------------------------------------
    # Style Resolution & Theming
    # --------------------------------------------------------------------------

    def set_active_theme(self, theme_id: str) -> None:
        if theme_id not in self.themes:
            raise KeyError(f"Theme '{theme_id}' not found.")
        self.active_theme_id = theme_id
        for elem in self.elements.values():
            self.invalidate_element(elem.element_id, InvalidationType.STYLE_DIRTY)

    def resolve_styles_recursively(self, element_id: str, inherited_style: Optional[UIStyleDeclaration] = None) -> None:
        if element_id not in self.elements:
            return
        elem = self.elements[element_id]
        theme = self.themes.get(self.active_theme_id, self.themes["dark"])

        # Base style from inheritance (e.g. font, text color)
        computed = UIStyleDeclaration()
        if inherited_style:
            computed.font = inherited_style.font
            computed.text_color = inherited_style.text_color

        # Apply Theme component style if registered
        comp_styles = theme.component_styles.get(elem.accessible_role.value, {})
        theme_decl = comp_styles.get(elem.style_state) or comp_styles.get(StyleState.NORMAL)
        if theme_decl:
            computed = computed.merge(theme_decl)

        # Apply Inline style
        if elem.inline_style:
            computed = computed.merge(elem.inline_style)

        elem.computed_style = computed
        elem.invalidation_flags.discard(InvalidationType.STYLE_DIRTY)

        for child_id in elem.children_ids:
            self.resolve_styles_recursively(child_id, computed)

    # --------------------------------------------------------------------------
    # Layout Engine (2-Pass: Measure & Layout)
    # --------------------------------------------------------------------------

    def compute_layout(self, root_id: str, surface_size: UISize) -> None:
        if root_id not in self.roots:
            return
        root = self.roots[root_id]
        root.bounds = UIRect(0, 0, surface_size.width, surface_size.height)
        root.local_bounds = UIRect(0, 0, surface_size.width, surface_size.height)
        root.clip_rect = root.bounds

        # Pass 1: Measure from bottom up
        constraints = UIBoxConstraints.tight(surface_size.width, surface_size.height)
        self._measure_element(root_id, constraints)

        # Pass 2: Layout from top down
        self._layout_element(root_id, root.bounds, root.clip_rect)

    def _measure_element(self, element_id: str, constraints: UIBoxConstraints) -> UISize:
        elem = self.elements[element_id]
        if elem.visibility == ElementVisibility.COLLAPSED:
            return UISize(0, 0)

        # Measure children first
        child_sizes = []
        for child_id in elem.children_ids:
            child_constraints = UIBoxConstraints.loose(constraints.max_width, constraints.max_height)
            child_sizes.append(self._measure_element(child_id, child_constraints))

        # Intrinsic size from widget contract
        measured = elem.measure(constraints)

        # Aggregate children if container
        if elem.children_ids and elem.size_mode_width == SizeMode.AUTO:
            if elem.flex_direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE):
                measured.width = sum(cs.width for cs in child_sizes) + elem.gap * max(0, len(child_sizes) - 1)
            else:
                measured.width = max((cs.width for cs in child_sizes), default=measured.width)

        if elem.children_ids and elem.size_mode_height == SizeMode.AUTO:
            if elem.flex_direction in (FlexDirection.COLUMN, FlexDirection.COLUMN_REVERSE):
                measured.height = sum(cs.height for cs in child_sizes) + elem.gap * max(0, len(child_sizes) - 1)
            else:
                measured.height = max((cs.height for cs in child_sizes), default=measured.height)

        return constraints.constrain(measured)

    def _layout_element(self, element_id: str, bounds: UIRect, parent_clip: Optional[UIRect]) -> None:
        elem = self.elements[element_id]
        if elem.visibility == ElementVisibility.COLLAPSED:
            elem.bounds = UIRect(0, 0, 0, 0)
            return

        elem.bounds = bounds
        elem.local_bounds = UIRect(0, 0, bounds.width, bounds.height)

        # Compute clipping intersection
        if parent_clip:
            elem.clip_rect = parent_clip.intersection(bounds) or bounds
        else:
            elem.clip_rect = bounds

        if not elem.children_ids:
            elem.invalidation_flags.discard(InvalidationType.LAYOUT_DIRTY)
            return

        # Flex layout algorithm for children
        padding = elem.computed_style.padding
        content_x = bounds.x + padding.left
        content_y = bounds.y + padding.top
        content_w = max(0.0, bounds.width - padding.horizontal)
        content_h = max(0.0, bounds.height - padding.vertical)

        visible_children = [self.elements[cid] for cid in elem.children_ids if self.elements[cid].visibility != ElementVisibility.COLLAPSED]
        if not visible_children:
            elem.invalidation_flags.discard(InvalidationType.LAYOUT_DIRTY)
            return

        is_row = elem.flex_direction in (FlexDirection.ROW, FlexDirection.ROW_REVERSE)
        total_gap = elem.gap * max(0, len(visible_children) - 1)

        # Distribute sizes
        if is_row:
            avail_w = max(0.0, content_w - total_gap)
            item_w = avail_w / len(visible_children) if len(visible_children) > 0 else 0.0
            curr_x = content_x
            for child in visible_children:
                cw = child.fixed_width if child.size_mode_width == SizeMode.FIXED else item_w
                ch = child.fixed_height if child.size_mode_height == SizeMode.FIXED else content_h
                child_bounds = UIRect(curr_x, content_y, cw, ch)
                self._layout_element(child.element_id, child_bounds, elem.clip_rect)
                curr_x += cw + elem.gap
        else:
            avail_h = max(0.0, content_h - total_gap)
            item_h = avail_h / len(visible_children) if len(visible_children) > 0 else 0.0
            curr_y = content_y
            for child in visible_children:
                cw = child.fixed_width if child.size_mode_width == SizeMode.FIXED else content_w
                ch = child.fixed_height if child.size_mode_height == SizeMode.FIXED else item_h
                child_bounds = UIRect(content_x, curr_y, cw, ch)
                self._layout_element(child.element_id, child_bounds, elem.clip_rect)
                curr_y += ch + elem.gap

        elem.invalidation_flags.discard(InvalidationType.LAYOUT_DIRTY)

    # --------------------------------------------------------------------------
    # Hit Testing & Event Dispatching
    # --------------------------------------------------------------------------

    def hit_test(self, root_id: str, point: UIPoint) -> Optional[str]:
        if root_id not in self.roots:
            return None
        return self._hit_test_recursive(root_id, point)

    def _hit_test_recursive(self, element_id: str, point: UIPoint) -> Optional[str]:
        elem = self.elements[element_id]
        if elem.visibility != ElementVisibility.VISIBLE:
            return None
        if not elem.bounds.contains_point(point):
            return None
        if elem.clip_rect and not elem.clip_rect.contains_point(point):
            return None

        # Check children in reverse order (topmost z-index / last rendered)
        sorted_children = sorted(elem.children_ids, key=lambda cid: self.elements[cid].z_index, reverse=True)
        for child_id in sorted_children:
            hit = self._hit_test_recursive(child_id, point)
            if hit:
                return hit

        if elem.pointer_events == PointerEventPolicy.NONE:
            return None
        return elem.element_id

    def dispatch_event(self, root_id: str, event: UIEventData) -> None:
        target_id = event.target_id
        if target_id not in self.elements:
            return

        # Capture path (root down to target)
        path = []
        curr = target_id
        while curr:
            path.append(curr)
            curr = self.elements[curr].parent_id
        path.reverse()

        # Phase 1: CAPTURE
        event.phase = EventPhase.CAPTURE
        for elem_id in path[:-1]:
            if event.is_propagation_stopped:
                return
            self.elements[elem_id].handle_event(event)

        # Phase 2: TARGET
        if not event.is_propagation_stopped:
            event.phase = EventPhase.TARGET
            self.elements[target_id].handle_event(event)

        # Phase 3: BUBBLE
        if event.bubbles and not event.is_propagation_stopped:
            event.phase = EventPhase.BUBBLE
            for elem_id in reversed(path[:-1]):
                if event.is_propagation_stopped:
                    return
                self.elements[elem_id].handle_event(event)

    # --------------------------------------------------------------------------
    # Focus Management
    # --------------------------------------------------------------------------

    def set_focus(self, element_id: Optional[str]) -> bool:
        if element_id and element_id not in self.elements:
            return False

        if self.focus_element_id == element_id:
            return True

        # Blur old focus
        if self.focus_element_id and self.focus_element_id in self.elements:
            old_elem = self.elements[self.focus_element_id]
            old_elem.style_state = StyleState.NORMAL
            old_elem.handle_event(UIEventData(event_type=UIEventType.Blur, target_id=self.focus_element_id))
            self.focus_history.append(self.focus_element_id)

        # Check modal trap
        if self.modal_stack:
            active_modal_id = self.modal_stack[-1]
            if element_id and not self._is_descendant(element_id, active_modal_id) and element_id != active_modal_id:
                return False

        self.focus_element_id = element_id
        if element_id:
            new_elem = self.elements[element_id]
            new_elem.style_state = StyleState.FOCUSED
            new_elem.handle_event(UIEventData(event_type=UIEventType.Focus, target_id=element_id))
        return True

    def focus_next(self) -> Optional[str]:
        focusable = self._get_focusable_elements()
        if not focusable:
            return None
        if not self.focus_element_id or self.focus_element_id not in focusable:
            next_id = focusable[0]
        else:
            idx = focusable.index(self.focus_element_id)
            next_id = focusable[(idx + 1) % len(focusable)]
        self.set_focus(next_id)
        return next_id

    def focus_prev(self) -> Optional[str]:
        focusable = self._get_focusable_elements()
        if not focusable:
            return None
        if not self.focus_element_id or self.focus_element_id not in focusable:
            prev_id = focusable[-1]
        else:
            idx = focusable.index(self.focus_element_id)
            prev_id = focusable[(idx - 1) % len(focusable)]
        self.set_focus(prev_id)
        return prev_id

    def _get_focusable_elements(self) -> List[str]:
        scope = self.modal_stack[-1] if self.modal_stack else None
        candidates = []
        for elem in self.elements.values():
            if elem.is_focusable and elem.enabled and elem.visibility == ElementVisibility.VISIBLE:
                if scope is None or self._is_descendant(elem.element_id, scope) or elem.element_id == scope:
                    candidates.append(elem)
        candidates.sort(key=lambda e: (e.tab_index, e.bounds.y, e.bounds.x))
        return [e.element_id for e in candidates]

    def _is_descendant(self, element_id: str, ancestor_id: str) -> bool:
        curr = self.elements.get(element_id)
        while curr and curr.parent_id:
            if curr.parent_id == ancestor_id:
                return True
            curr = self.elements.get(curr.parent_id)
        return False

    def push_modal(self, modal_id: str) -> None:
        if modal_id in self.elements:
            self.modal_stack.append(modal_id)
            modal = self.elements[modal_id]
            if isinstance(modal, DialogWidget):
                modal.restored_focus_id = self.focus_element_id
                modal.open()
            self.set_focus(modal_id)

    def pop_modal(self) -> Optional[str]:
        if not self.modal_stack:
            return None
        modal_id = self.modal_stack.pop()
        modal = self.elements.get(modal_id)
        if isinstance(modal, DialogWidget):
            modal.close()
            if modal.restored_focus_id:
                self.set_focus(modal.restored_focus_id)
        return modal_id

    # --------------------------------------------------------------------------
    # Data Binding System
    # --------------------------------------------------------------------------

    def bind(
        self,
        binding_id: str,
        element_id: str,
        target_property: str,
        source_key: str,
        mode: BindingMode = BindingMode.ONE_WAY,
        format_fn: Optional[Callable[[Any], Any]] = None,
        parse_fn: Optional[Callable[[Any], Any]] = None,
        validator_fn: Optional[Callable[[Any], Tuple[bool, str]]] = None
    ) -> UIBinding:
        binding = UIBinding(
            binding_id=binding_id,
            element_id=element_id,
            target_property=target_property,
            source_key=source_key,
            mode=mode,
            format_fn=format_fn,
            parse_fn=parse_fn,
            validator_fn=validator_fn
        )
        self.bindings[binding_id] = binding
        if element_id in self.elements:
            self.elements[element_id].bindings.append(binding_id)

        # Initial synchronization if source exists in app_state
        if source_key in self.app_state:
            self._sync_state_to_ui(binding)
        return binding

    def unbind(self, binding_id: str) -> None:
        if binding_id in self.bindings:
            binding = self.bindings.pop(binding_id)
            elem = self.elements.get(binding.element_id)
            if elem and binding_id in elem.bindings:
                elem.bindings.remove(binding_id)

    def set_app_state(self, key: str, value: Any) -> None:
        self.app_state[key] = value
        # Sync to all active bindings for this key
        for binding in list(self.bindings.values()):
            if binding.source_key == key and binding.is_active:
                self._sync_state_to_ui(binding)

    def update_ui_property(self, element_id: str, property_name: str, value: Any) -> bool:
        if element_id not in self.elements:
            return False
        elem = self.elements[element_id]
        if hasattr(elem, property_name):
            setattr(elem, property_name, value)
        elem.state[property_name] = value

        # Sync back to state if two-way binding exists
        for binding_id in elem.bindings:
            binding = self.bindings.get(binding_id)
            if binding and binding.target_property == property_name and binding.mode == BindingMode.TWO_WAY and binding.is_active:
                self._sync_ui_to_state(binding, value)
        return True

    def _sync_state_to_ui(self, binding: UIBinding) -> None:
        if binding.binding_id in self._syncing_bindings:
            return
        self._syncing_bindings.add(binding.binding_id)
        try:
            val = self.app_state.get(binding.source_key)
            if binding.format_fn:
                val = binding.format_fn(val)
            elem = self.elements.get(binding.element_id)
            if elem:
                if hasattr(elem, binding.target_property):
                    setattr(elem, binding.target_property, val)
                elem.state[binding.target_property] = val
                binding.sync_count += 1
                self.invalidate_element(binding.element_id, InvalidationType.PAINT_DIRTY)
        finally:
            self._syncing_bindings.remove(binding.binding_id)

    def _sync_ui_to_state(self, binding: UIBinding, raw_ui_value: Any) -> None:
        if binding.binding_id in self._syncing_bindings:
            return
        self._syncing_bindings.add(binding.binding_id)
        try:
            val = raw_ui_value
            if binding.parse_fn:
                val = binding.parse_fn(raw_ui_value)
            if binding.validator_fn:
                valid, msg = binding.validator_fn(val)
                if not valid:
                    binding.last_error = msg
                    return
            binding.last_error = None
            self.app_state[binding.source_key] = val
            binding.sync_count += 1
        finally:
            self._syncing_bindings.remove(binding.binding_id)

    # --------------------------------------------------------------------------
    # Animation Clock & Transitions
    # --------------------------------------------------------------------------

    def animate(
        self,
        element_id: str,
        target: AnimationTarget,
        property_name: str,
        start_val: Any,
        end_val: Any,
        duration_ms: float = 300.0,
        replacement: AnimationReplacementPolicy = AnimationReplacementPolicy.REPLACE,
        easing: str = "linear"
    ) -> UIAnimation:
        anim_id = f"anim_{element_id}_{property_name}_{len(self.animations)}"
        if self.reduced_motion:
            duration_ms = 0.0

        existing = [a for a in self.animations.values() if a.element_id == element_id and a.property_name == property_name and a.is_active]
        if existing:
            if replacement == AnimationReplacementPolicy.REPLACE:
                for a in existing:
                    a.is_active = False
            elif replacement == AnimationReplacementPolicy.IGNORE:
                return existing[0]

        anim = UIAnimation(
            animation_id=anim_id,
            element_id=element_id,
            target=target,
            property_name=property_name,
            start_value=start_val,
            end_value=end_val,
            duration_ms=duration_ms,
            replacement_policy=replacement,
            easing=easing
        )
        self.animations[anim_id] = anim
        return anim

    def tick_animations(self, delta_ms: float) -> None:
        completed = []
        for anim in list(self.animations.values()):
            if not anim.is_active:
                continue
            anim.elapsed_ms += delta_ms
            curr_val = anim.evaluate()
            elem = self.elements.get(anim.element_id)
            if elem:
                if anim.property_name == "opacity":
                    elem.computed_style.opacity = max(0.0, min(1.0, float(curr_val)))
                elif hasattr(elem, anim.property_name):
                    setattr(elem, anim.property_name, curr_val)
                elem.state[anim.property_name] = curr_val
                self.invalidate_element(elem.element_id, InvalidationType.PAINT_DIRTY)

            if anim.progress() >= 1.0:
                anim.is_completed = True
                anim.is_active = False
                completed.append(anim.animation_id)

    # --------------------------------------------------------------------------
    # Accessibility Tree Generation
    # --------------------------------------------------------------------------

    def generate_accessible_tree(self, root_id: str) -> Optional[UIAccessibleNode]:
        if root_id not in self.roots:
            return None
        return self._build_accessible_node(root_id)

    def _build_accessible_node(self, element_id: str) -> UIAccessibleNode:
        elem = self.elements[element_id]
        child_nodes = []
        for cid in elem.children_ids:
            if self.elements[cid].visibility != ElementVisibility.COLLAPSED:
                child_nodes.append(cid)

        return UIAccessibleNode(
            element_id=elem.element_id,
            role=elem.accessible_role,
            name=elem.accessible_name or elem.state.get("text", "") or elem.element_id,
            description=elem.accessible_description,
            disabled=not elem.enabled,
            checked=elem.state.get("checked"),
            expanded=elem.state.get("expanded"),
            selected=elem.state.get("selected") or (elem.state.get("selected_index", -1) >= 0),
            focused=(self.focus_element_id == elem.element_id),
            value=str(elem.state.get("value", "")) if "value" in elem.state else None,
            child_ids=child_nodes
        )

    # --------------------------------------------------------------------------
    # Render Tree Generation & Batching
    # --------------------------------------------------------------------------

    def generate_render_tree(self, root_id: str) -> UIRenderTree:
        if root_id not in self.roots:
            return UIRenderTree()

        root = self.roots[root_id]
        commands: List[UIRenderCommand] = []
        self._collect_render_commands(root_id, commands)

        # Batch draw order
        sorted_commands = sorted(commands, key=lambda c: c.z_index)
        return UIRenderTree(
            commands=sorted_commands,
            surface_size=UISize(root.bounds.width, root.bounds.height),
            timestamp=time.time()
        )

    def _collect_render_commands(self, element_id: str, commands: List[UIRenderCommand]) -> None:
        elem = self.elements[element_id]
        if elem.visibility != ElementVisibility.VISIBLE:
            return

        # Render self
        commands.extend(elem.render())

        # Render children
        for child_id in elem.children_ids:
            self._collect_render_commands(child_id, commands)

    # --------------------------------------------------------------------------
    # Snapshots, Inspector & Diagnostics
    # --------------------------------------------------------------------------

    def take_structural_snapshot(self, root_id: str) -> UIStructuralSnapshot:
        if root_id not in self.roots:
            raise KeyError(f"Root '{root_id}' not found.")

        root = self.roots[root_id]
        computed_bounds = {eid: elem.bounds.to_dict() for eid, elem in self.elements.items() if self._is_descendant(eid, root_id) or eid == root_id}
        computed_styles = {eid: {"opacity": elem.computed_style.opacity, "z_index": elem.computed_style.z_index} for eid, elem in self.elements.items() if self._is_descendant(eid, root_id) or eid == root_id}

        def serialize_tree(eid: str) -> Dict[str, Any]:
            el = self.elements[eid]
            return {
                "id": el.element_id,
                "role": el.accessible_role.value,
                "visibility": el.visibility.value,
                "enabled": el.enabled,
                "children": [serialize_tree(cid) for cid in el.children_ids]
            }

        hierarchy = serialize_tree(root_id)
        return UIStructuralSnapshot(
            root_id=root_id,
            surface_type=root.surface_type.value,
            element_count=len(computed_bounds),
            hierarchy=hierarchy,
            computed_bounds=computed_bounds,
            computed_styles=computed_styles,
            focus_id=self.focus_element_id
        )

    def get_inspector_data(self, root_id: str) -> UIInspectorData:
        snapshot = self.take_structural_snapshot(root_id)
        render_tree = self.generate_render_tree(root_id)
        return UIInspectorData(
            root_id=root_id,
            element_count=snapshot.element_count,
            tree=snapshot.hierarchy,
            styles=snapshot.computed_styles,
            bounds=snapshot.computed_bounds,
            states={eid: elem.state for eid, elem in self.elements.items() if self._is_descendant(eid, root_id) or eid == root_id},
            active_focus=self.focus_element_id,
            active_bindings=list(self.bindings.keys()),
            recent_events=[e.event_type.value for e in self.event_queue[-10:]],
            render_commands_count=len(render_tree.commands)
        )

    def generate_diagnostic_bundle(self, root_id: str) -> UIDiagnosticBundle:
        snapshot = self.take_structural_snapshot(root_id)
        inspector = self.get_inspector_data(root_id)
        self.telemetry.widget_count = len(self.elements)
        self.telemetry.visible_widget_count = sum(1 for e in self.elements.values() if e.visibility == ElementVisibility.VISIBLE)
        return UIDiagnosticBundle(
            bundle_id=f"diag_bundle_{int(time.time()*1000)}",
            timestamp=time.time(),
            root_id=root_id,
            snapshot=snapshot,
            inspector=inspector,
            telemetry=self.telemetry
        )
