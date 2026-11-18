"""
Universal Runtime UI World Data Models (UAF-81.78).
Strict dataclasses and enums for UI hierarchy, widgets, layout, events,
styles, themes, animations, bindings, localization, accessibility, and replay.
"""

from __future__ import annotations

import enum
import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union


def copy_dict_deterministic(data: Any) -> Any:
    """Recursively formats and sorts dictionary structures deterministically."""
    if isinstance(data, dict):
        return {k: copy_dict_deterministic(data[k]) for k in sorted(data.keys())}
    elif isinstance(data, list):
        return [copy_dict_deterministic(item) for item in data]
    elif isinstance(data, tuple):
        return tuple(copy_dict_deterministic(item) for item in data)
    elif isinstance(data, set):
        return sorted([copy_dict_deterministic(item) for item in data], key=lambda x: str(x))
    elif isinstance(data, float):
        if math.isnan(data):
            return "NaN"
        if math.isinf(data):
            return "Infinity" if data > 0 else "-Infinity"
        return round(float(data), 6)
    elif isinstance(data, enum.Enum):
        return data.value
    return data


class UIWorldState(str, enum.Enum):
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class UINodeType(str, enum.Enum):
    ROOT = "ROOT"
    PANEL = "PANEL"
    CONTAINER = "CONTAINER"
    BUTTON = "BUTTON"
    LABEL = "LABEL"
    TEXT_FIELD = "TEXT_FIELD"
    TEXT_AREA = "TEXT_AREA"
    IMAGE = "IMAGE"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    SLIDER = "SLIDER"
    PROGRESS_BAR = "PROGRESS_BAR"
    PROGRESS = "PROGRESS"
    SCROLL_VIEW = "SCROLL_VIEW"
    LIST_VIEW = "LIST_VIEW"
    LIST = "LIST"
    GRID_VIEW = "GRID_VIEW"
    GRID = "GRID"
    DROPDOWN = "DROPDOWN"
    WINDOW = "WINDOW"
    CANVAS = "CANVAS"


class WidgetState(str, enum.Enum):
    NORMAL = "NORMAL"
    HOVER = "HOVER"
    PRESSED = "PRESSED"
    FOCUSED = "FOCUSED"
    DISABLED = "DISABLED"
    SELECTED = "SELECTED"
    ACTIVE = "ACTIVE"


class LayoutType(str, enum.Enum):
    STACK = "STACK"
    FLEX = "FLEX"
    GRID = "GRID"
    ABSOLUTE = "ABSOLUTE"
    DOCKED = "DOCKED"


class FlexDirection(str, enum.Enum):
    ROW = "ROW"
    COLUMN = "COLUMN"
    ROW_REVERSE = "ROW_REVERSE"
    COLUMN_REVERSE = "COLUMN_REVERSE"


class Alignment(str, enum.Enum):
    START = "START"
    CENTER = "CENTER"
    END = "END"
    STRETCH = "STRETCH"
    SPACE_BETWEEN = "SPACE_BETWEEN"
    SPACE_AROUND = "SPACE_AROUND"


class SizeMode(str, enum.Enum):
    FIXED = "FIXED"
    CONTENT = "CONTENT"
    STRETCH = "STRETCH"
    FILL = "FILL"


class UIVisibility(str, enum.Enum):
    VISIBLE = "VISIBLE"
    INVISIBLE = "INVISIBLE"
    COLLAPSED = "COLLAPSED"
    HIDDEN = "HIDDEN"


class OverflowPolicy(str, enum.Enum):
    VISIBLE = "VISIBLE"
    CLIP = "CLIP"
    SCROLL = "SCROLL"


class HitTestMode(str, enum.Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    SELF_ONLY = "SELF_ONLY"
    CHILDREN_ONLY = "CHILDREN_ONLY"
    NONE = "NONE"


class UIEventType(str, enum.Enum):
    POINTER_ENTER = "POINTER_ENTER"
    POINTER_EXIT = "POINTER_EXIT"
    POINTER_DOWN = "POINTER_DOWN"
    POINTER_UP = "POINTER_UP"
    POINTER_MOVE = "POINTER_MOVE"
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    DRAG_START = "DRAG_START"
    DRAG = "DRAG"
    DRAG_END = "DRAG_END"
    SCROLL = "SCROLL"
    FOCUS_GAINED = "FOCUS_GAINED"
    FOCUS_LOST = "FOCUS_LOST"
    KEY_DOWN = "KEY_DOWN"
    KEY_UP = "KEY_UP"
    VALUE_CHANGED = "VALUE_CHANGED"
    TEXT_CHANGED = "TEXT_CHANGED"
    SUBMIT = "SUBMIT"


class EventRoutingPhase(str, enum.Enum):
    CAPTURE = "CAPTURE"
    TARGET = "TARGET"
    BUBBLE = "BUBBLE"


class NavigationDirection(str, enum.Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"
    PREV = "PREV"


class TextAlignment(str, enum.Enum):
    LEFT = "LEFT"
    CENTER = "CENTER"
    RIGHT = "RIGHT"
    JUSTIFY = "JUSTIFY"


class TextOverflow(str, enum.Enum):
    CLIP = "CLIP"
    ELLIPSIS = "ELLIPSIS"
    WRAP = "WRAP"


class BindingMode(str, enum.Enum):
    ONE_WAY = "ONE_WAY"
    TWO_WAY = "TWO_WAY"
    ONE_TIME = "ONE_TIME"


class InvalidationFlags(str, enum.Enum):
    STYLE_DIRTY = "STYLE_DIRTY"
    MEASURE_DIRTY = "MEASURE_DIRTY"
    LAYOUT_DIRTY = "LAYOUT_DIRTY"
    RENDER_DIRTY = "RENDER_DIRTY"
    ACCESSIBILITY_DIRTY = "ACCESSIBILITY_DIRTY"


class AccessibilityRole(str, enum.Enum):
    NONE = "NONE"
    BUTTON = "BUTTON"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    SLIDER = "SLIDER"
    TEXT = "TEXT"
    TEXT_FIELD = "TEXT_FIELD"
    LIST = "LIST"
    LIST_ITEM = "LIST_ITEM"
    WINDOW = "WINDOW"
    IMAGE = "IMAGE"
    CONTAINER = "CONTAINER"
    DIALOG = "DIALOG"


@dataclass
class UIRect:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    def contains(self, px: float, py: float) -> bool:
        return (
            self.x <= px <= (self.x + self.width) and
            self.y <= py <= (self.y + self.height)
        )

    def intersects(self, other: UIRect) -> bool:
        return not (
            self.x + self.width < other.x or
            other.x + other.width < self.x or
            self.y + self.height < other.y or
            other.y + other.height < self.y
        )

    def intersect(self, other: UIRect) -> UIRect:
        nx = max(self.x, other.x)
        ny = max(self.y, other.y)
        nw = max(0.0, min(self.x + self.width, other.x + other.width) - nx)
        nh = max(0.0, min(self.y + self.height, other.y + other.height) - ny)
        return UIRect(x=nx, y=ny, width=nw, height=nh)

    def to_dict(self) -> Dict[str, float]:
        return {
            "x": round(float(self.x), 6),
            "y": round(float(self.y), 6),
            "width": round(float(self.width), 6),
            "height": round(float(self.height), 6),
        }


@dataclass
class UIPadding:
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom

    def to_dict(self) -> Dict[str, float]:
        return {
            "left": round(float(self.left), 6),
            "top": round(float(self.top), 6),
            "right": round(float(self.right), 6),
            "bottom": round(float(self.bottom), 6),
        }


@dataclass
class UIMargins:
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom

    def to_dict(self) -> Dict[str, float]:
        return {
            "left": round(float(self.left), 6),
            "top": round(float(self.top), 6),
            "right": round(float(self.right), 6),
            "bottom": round(float(self.bottom), 6),
        }


@dataclass
class UIConstraints:
    min_width: float = 0.0
    max_width: float = float("inf")
    min_height: float = 0.0
    max_height: float = float("inf")

    def clamp_width(self, w: float) -> float:
        if math.isnan(w) or math.isinf(w):
            raise ValueError(f"Invalid width constraint value: {w}")
        return max(self.min_width, min(self.max_width, w))

    def clamp_height(self, h: float) -> float:
        if math.isnan(h) or math.isinf(h):
            raise ValueError(f"Invalid height constraint value: {h}")
        return max(self.min_height, min(self.max_height, h))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_width": round(float(self.min_width), 6),
            "max_width": "Infinity" if math.isinf(self.max_width) else round(float(self.max_width), 6),
            "min_height": round(float(self.min_height), 6),
            "max_height": "Infinity" if math.isinf(self.max_height) else round(float(self.max_height), 6),
        }


@dataclass
class UIAnchors:
    min_x: float = 0.0
    min_y: float = 0.0
    max_x: float = 0.0
    max_y: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "min_x": round(float(self.min_x), 6),
            "min_y": round(float(self.min_y), 6),
            "max_x": round(float(self.max_x), 6),
            "max_y": round(float(self.max_y), 6),
            "offset_x": round(float(self.offset_x), 6),
            "offset_y": round(float(self.offset_y), 6),
        }


@dataclass
class UIFontResource:
    font_id: str
    family: str = "Inter"
    size: float = 14.0
    weight: str = "normal"
    line_height: float = 1.2
    letter_spacing: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "font_id": self.font_id,
            "family": self.family,
            "size": round(float(self.size), 6),
            "weight": self.weight,
            "line_height": round(float(self.line_height), 6),
            "letter_spacing": round(float(self.letter_spacing), 6),
        }


@dataclass
class UIIconResource:
    icon_id: str
    name: str = ""
    source: str = ""
    width: float = 16.0
    height: float = 16.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "icon_id": self.icon_id,
            "name": self.name,
            "source": self.source,
            "width": round(float(self.width), 6),
            "height": round(float(self.height), 6),
        }


@dataclass
class UIStyle:
    style_id: str
    name: str = ""
    color: str = "#FFFFFF"
    background_color: str = "#00000000"
    border_color: str = "#00000000"
    border_width: float = 0.0
    border_radius: float = 0.0
    opacity: Optional[float] = None
    font_id: Optional[str] = None
    font_size: float = 14.0
    padding: UIPadding = field(default_factory=UIPadding)
    margin: UIMargins = field(default_factory=UIMargins)
    parent_style_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style_id": self.style_id,
            "name": self.name,
            "color": self.color,
            "background_color": self.background_color,
            "border_color": self.border_color,
            "border_width": round(float(self.border_width), 6),
            "border_radius": round(float(self.border_radius), 6),
            "opacity": 1.0 if self.opacity is None else round(float(self.opacity), 6),
            "font_id": self.font_id,
            "font_size": round(float(self.font_size), 6),
            "padding": self.padding.to_dict(),
            "margin": self.margin.to_dict(),
            "parent_style_id": self.parent_style_id,
        }


@dataclass
class UITheme:
    theme_id: str
    name: str = ""
    styles: Dict[str, UIStyle] = field(default_factory=dict)
    palette: Dict[str, str] = field(default_factory=dict)
    parent_theme_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "theme_id": self.theme_id,
            "name": self.name,
            "styles": {k: s.to_dict() for k, s in sorted(self.styles.items())},
            "palette": dict(sorted(self.palette.items())),
            "parent_theme_id": self.parent_theme_id,
        }


@dataclass
class UIAnimation:
    animation_id: str
    target_node_id: str
    property_name: str
    start_value: Any
    end_value: Any
    duration: float = 1.0
    elapsed: float = 0.0
    easing: str = "linear"
    is_playing: bool = True
    is_completed: bool = False
    loop: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "animation_id": self.animation_id,
            "target_node_id": self.target_node_id,
            "property_name": self.property_name,
            "start_value": copy_dict_deterministic(self.start_value),
            "end_value": copy_dict_deterministic(self.end_value),
            "duration": round(float(self.duration), 6),
            "elapsed": round(float(self.elapsed), 6),
            "easing": self.easing,
            "is_playing": self.is_playing,
            "is_completed": self.is_completed,
            "loop": self.loop,
        }


@dataclass
class UIDataBinding:
    binding_id: str
    source_path: str
    target_node_id: str
    target_property: str
    mode: BindingMode = BindingMode.ONE_WAY
    transformer: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "source_path": self.source_path,
            "target_node_id": self.target_node_id,
            "target_property": self.target_property,
            "mode": self.mode.value,
            "transformer": self.transformer,
        }


@dataclass
class UILocalizationTable:
    locale: str
    translations: Dict[str, str] = field(default_factory=dict)
    plural_rules: Dict[str, Dict[str, str]] = field(default_factory=dict)
    is_rtl: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "locale": self.locale,
            "translations": dict(sorted(self.translations.items())),
            "plural_rules": {k: dict(sorted(v.items())) for k, v in sorted(self.plural_rules.items())},
            "is_rtl": self.is_rtl,
        }


@dataclass
class UIAccessibilityNode:
    node_id: str
    automation_id: str = ""
    role: AccessibilityRole = AccessibilityRole.NONE
    name: str = ""
    value: Optional[str] = None
    is_focused: bool = False
    is_disabled: bool = False
    is_selected: bool = False
    is_checked: bool = False
    is_expanded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "automation_id": self.automation_id,
            "role": self.role.value,
            "name": self.name,
            "value": self.value,
            "is_focused": self.is_focused,
            "is_disabled": self.is_disabled,
            "is_selected": self.is_selected,
            "is_checked": self.is_checked,
            "is_expanded": self.is_expanded,
        }


@dataclass
class UIEvent:
    event_type: UIEventType
    target_id: str
    pointer_x: float = 0.0
    pointer_y: float = 0.0
    delta_x: float = 0.0
    delta_y: float = 0.0
    key_code: str = ""
    is_consumed: bool = False
    timestamp: float = 0.0
    phase: EventRoutingPhase = EventRoutingPhase.TARGET
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "target_id": self.target_id,
            "pointer_x": round(float(self.pointer_x), 6),
            "pointer_y": round(float(self.pointer_y), 6),
            "delta_x": round(float(self.delta_x), 6),
            "delta_y": round(float(self.delta_y), 6),
            "key_code": self.key_code,
            "is_consumed": self.is_consumed,
            "timestamp": round(float(self.timestamp), 6),
            "phase": self.phase.value,
            "metadata": copy_dict_deterministic(self.metadata),
        }


@dataclass
class UINode:
    ui_node_id: str
    parent_id: Optional[str] = None
    node_type: UINodeType = UINodeType.PANEL
    visibility: UIVisibility = UIVisibility.VISIBLE
    state: WidgetState = WidgetState.NORMAL
    layout_type: LayoutType = LayoutType.STACK
    flex_direction: FlexDirection = FlexDirection.COLUMN
    alignment: Alignment = Alignment.START
    cross_alignment: Alignment = Alignment.START
    size_mode_x: SizeMode = SizeMode.CONTENT
    size_mode_y: SizeMode = SizeMode.CONTENT
    constraints: UIConstraints = field(default_factory=UIConstraints)
    anchors: UIAnchors = field(default_factory=UIAnchors)
    padding: UIPadding = field(default_factory=UIPadding)
    margins: UIMargins = field(default_factory=UIMargins)
    overflow_x: OverflowPolicy = OverflowPolicy.VISIBLE
    overflow_y: OverflowPolicy = OverflowPolicy.VISIBLE
    children: List[str] = field(default_factory=list)
    style_id: Optional[str] = None
    desired_width: float = 0.0
    desired_height: float = 0.0
    assigned_rect: UIRect = field(default_factory=UIRect)
    clip_rect: Optional[UIRect] = None
    scroll_offset_x: float = 0.0
    scroll_offset_y: float = 0.0
    content_width: float = 0.0
    content_height: float = 0.0
    hit_test_mode: HitTestMode = HitTestMode.ENABLED
    z_index: int = 0
    is_focused: bool = False
    is_enabled: bool = True
    tab_index: int = 0
    nav_up: Optional[str] = None
    nav_down: Optional[str] = None
    nav_left: Optional[str] = None
    nav_right: Optional[str] = None
    automation_id: str = ""
    accessibility_role: AccessibilityRole = AccessibilityRole.NONE
    accessibility_name: str = ""
    text: str = ""
    translation_key: Optional[str] = None
    font_id: Optional[str] = None
    font_size: float = 14.0
    text_alignment: TextAlignment = TextAlignment.LEFT
    text_overflow: TextOverflow = TextOverflow.WRAP
    value: Any = None
    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0
    is_checked: bool = False
    is_selected: bool = False
    is_expanded: bool = False
    image_source: str = ""
    dirty_flags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def actual_rect(self) -> UIRect:
        return self.assigned_rect

    @actual_rect.setter
    def actual_rect(self, rect: UIRect) -> None:
        self.assigned_rect = rect

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ui_node_id": self.ui_node_id,
            "parent_id": self.parent_id,
            "node_type": self.node_type.value,
            "visibility": self.visibility.value,
            "state": self.state.value,
            "layout_type": self.layout_type.value,
            "flex_direction": self.flex_direction.value,
            "alignment": self.alignment.value,
            "cross_alignment": self.cross_alignment.value,
            "size_mode_x": self.size_mode_x.value,
            "size_mode_y": self.size_mode_y.value,
            "constraints": self.constraints.to_dict(),
            "anchors": self.anchors.to_dict(),
            "padding": self.padding.to_dict(),
            "margins": self.margins.to_dict(),
            "overflow_x": self.overflow_x.value,
            "overflow_y": self.overflow_y.value,
            "children": list(self.children),
            "style_id": self.style_id,
            "desired_width": round(float(self.desired_width), 6),
            "desired_height": round(float(self.desired_height), 6),
            "assigned_rect": self.assigned_rect.to_dict(),
            "clip_rect": self.clip_rect.to_dict() if self.clip_rect else None,
            "scroll_offset_x": round(float(self.scroll_offset_x), 6),
            "scroll_offset_y": round(float(self.scroll_offset_y), 6),
            "content_width": round(float(self.content_width), 6),
            "content_height": round(float(self.content_height), 6),
            "hit_test_mode": self.hit_test_mode.value,
            "z_index": self.z_index,
            "is_focused": self.is_focused,
            "is_enabled": self.is_enabled,
            "tab_index": self.tab_index,
            "nav_up": self.nav_up,
            "nav_down": self.nav_down,
            "nav_left": self.nav_left,
            "nav_right": self.nav_right,
            "automation_id": self.automation_id,
            "accessibility_role": self.accessibility_role.value,
            "accessibility_name": self.accessibility_name,
            "text": self.text,
            "translation_key": self.translation_key,
            "font_id": self.font_id,
            "font_size": round(float(self.font_size), 6),
            "text_alignment": self.text_alignment.value,
            "text_overflow": self.text_overflow.value,
            "value": copy_dict_deterministic(self.value),
            "min_value": round(float(self.min_value), 6),
            "max_value": round(float(self.max_value), 6),
            "step": round(float(self.step), 6),
            "is_checked": self.is_checked,
            "is_selected": self.is_selected,
            "is_expanded": self.is_expanded,
            "image_source": self.image_source,
            "dirty_flags": sorted(list(self.dirty_flags)),
            "metadata": copy_dict_deterministic(self.metadata),
        }


# Widget is a subclass/alias of UINode for convenience
class UIWidget(UINode):
    pass


@dataclass
class UISnapshot:
    snapshot_id: str
    ui_world_id: str
    state: str
    timestamp: float
    nodes: Dict[str, Dict[str, Any]]
    active_theme_id: Optional[str]
    active_locale: str
    focused_node_id: Optional[str]
    scroll_positions: Dict[str, Tuple[float, float]]
    data_store: Dict[str, Any]
    fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "ui_world_id": self.ui_world_id,
            "state": self.state,
            "timestamp": round(float(self.timestamp), 6),
            "nodes": {k: copy_dict_deterministic(v) for k, v in sorted(self.nodes.items())},
            "active_theme_id": self.active_theme_id,
            "active_locale": self.active_locale,
            "focused_node_id": self.focused_node_id,
            "scroll_positions": {k: (round(float(v[0]), 6), round(float(v[1]), 6)) for k, v in sorted(self.scroll_positions.items())},
            "data_store": copy_dict_deterministic(self.data_store),
            "fingerprint": self.fingerprint,
        }


@dataclass
class UIRecord:
    record_id: str
    event: UIEvent
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "event": self.event.to_dict(),
            "timestamp": round(float(self.timestamp), 6),
        }


@dataclass
class UIReplaySession:
    session_id: str
    initial_snapshot: UISnapshot
    events: List[UIEvent]
    current_index: int = 0
    is_finished: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "initial_snapshot": self.initial_snapshot.to_dict(),
            "events": [e.to_dict() for e in self.events],
            "current_index": self.current_index,
            "is_finished": self.is_finished,
        }


@dataclass
class UIWorldSettings:
    max_nodes: int = 10000
    max_tree_depth: int = 64
    max_children_per_node: int = 1000
    max_events_per_frame: int = 1000
    max_bindings: int = 5000
    max_animations: int = 1000
    viewport_width: float = 1920.0
    viewport_height: float = 1080.0
    dpi_scale: float = 1.0
    default_locale: str = "en-US"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_nodes": self.max_nodes,
            "max_tree_depth": self.max_tree_depth,
            "max_children_per_node": self.max_children_per_node,
            "max_events_per_frame": self.max_events_per_frame,
            "max_bindings": self.max_bindings,
            "max_animations": self.max_animations,
            "viewport_width": round(float(self.viewport_width), 6),
            "viewport_height": round(float(self.viewport_height), 6),
            "dpi_scale": round(float(self.dpi_scale), 6),
            "default_locale": self.default_locale,
        }


@dataclass
class UIWorld:
    ui_world_id: str
    runtime_world_id: str = "runtime_world_default"
    state: UIWorldState = UIWorldState.CREATED
    settings: UIWorldSettings = field(default_factory=UIWorldSettings)
    root_ids: List[str] = field(default_factory=list)
    nodes: Dict[str, UINode] = field(default_factory=dict)
    styles: Dict[str, UIStyle] = field(default_factory=dict)
    themes: Dict[str, UITheme] = field(default_factory=dict)
    active_theme_id: Optional[str] = None
    fonts: Dict[str, UIFontResource] = field(default_factory=dict)
    icons: Dict[str, UIIconResource] = field(default_factory=dict)
    localization_tables: Dict[str, UILocalizationTable] = field(default_factory=dict)
    active_locale: str = "en-US"
    bindings: Dict[str, UIDataBinding] = field(default_factory=dict)
    animations: Dict[str, UIAnimation] = field(default_factory=dict)
    focused_node_id: Optional[str] = None
    pointer_captured_node_id: Optional[str] = None
    event_queue: List[UIEvent] = field(default_factory=list)
    data_store: Dict[str, Any] = field(default_factory=dict)
    events_history: List[UIEvent] = field(default_factory=list)
    current_time: float = 0.0

    def compute_fingerprint(self) -> str:
        """Computes deterministic SHA-256 fingerprint representing the full UI state."""
        canonical_dict = self.to_dict()
        serialized = json.dumps(canonical_dict, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ui_world_id": self.ui_world_id,
            "runtime_world_id": self.runtime_world_id,
            "state": self.state.value,
            "settings": self.settings.to_dict(),
            "root_ids": list(self.root_ids),
            "nodes": {k: n.to_dict() for k, n in sorted(self.nodes.items())},
            "styles": {k: s.to_dict() for k, s in sorted(self.styles.items())},
            "themes": {k: t.to_dict() for k, t in sorted(self.themes.items())},
            "active_theme_id": self.active_theme_id,
            "fonts": {k: f.to_dict() for k, f in sorted(self.fonts.items())},
            "icons": {k: i.to_dict() for k, i in sorted(self.icons.items())},
            "localization_tables": {k: l.to_dict() for k, l in sorted(self.localization_tables.items())},
            "active_locale": self.active_locale,
            "bindings": {k: b.to_dict() for k, b in sorted(self.bindings.items())},
            "animations": {k: a.to_dict() for k, a in sorted(self.animations.items())},
            "focused_node_id": self.focused_node_id,
            "pointer_captured_node_id": self.pointer_captured_node_id,
            "event_queue": [e.to_dict() for e in self.event_queue],
            "data_store": copy_dict_deterministic(self.data_store),
            "current_time": round(float(self.current_time), 6),
        }
