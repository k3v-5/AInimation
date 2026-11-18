"""
UAF-81.66: Universal UI Framework Domain Models.
Provides standard models, enums, contracts, geometry structures, and cryptographic diagnostics
for the retained UI tree, layout engine, style system, theme system, accessibility, animations,
render commands, and structural snapshots.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class UISurfaceType(str, Enum):
    MAIN_WINDOW = "MAIN_WINDOW"
    SECONDARY_WINDOW = "SECONDARY_WINDOW"
    POPUP = "POPUP"
    OVERLAY = "OVERLAY"
    MODAL = "MODAL"
    TOOLTIP = "TOOLTIP"
    OFFSCREEN = "OFFSCREEN"


class ElementVisibility(str, Enum):
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"
    COLLAPSED = "COLLAPSED"


class ElementLifecycle(str, Enum):
    CREATED = "CREATED"
    MOUNTED = "MOUNTED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    UNMOUNTING = "UNMOUNTING"
    DESTROYED = "DESTROYED"


class PointerEventPolicy(str, Enum):
    AUTO = "AUTO"
    NONE = "NONE"
    CHILDREN_ONLY = "CHILDREN_ONLY"


class SizeMode(str, Enum):
    AUTO = "AUTO"
    FIXED = "FIXED"
    PERCENT = "PERCENT"
    FILL = "FILL"
    CONTENT = "CONTENT"


class LayoutPositioning(str, Enum):
    FLOW = "FLOW"
    ABSOLUTE = "ABSOLUTE"
    OVERLAY = "OVERLAY"


class LayoutAlignment(str, Enum):
    START = "START"
    CENTER = "CENTER"
    END = "END"
    STRETCH = "STRETCH"


class LayoutDistribution(str, Enum):
    SPACE_START = "SPACE_START"
    SPACE_BETWEEN = "SPACE_BETWEEN"
    SPACE_AROUND = "SPACE_AROUND"
    SPACE_END = "SPACE_END"


class FlexDirection(str, Enum):
    ROW = "ROW"
    COLUMN = "COLUMN"
    ROW_REVERSE = "ROW_REVERSE"
    COLUMN_REVERSE = "COLUMN_REVERSE"


class StyleSource(str, Enum):
    DEFAULT = "DEFAULT"
    THEME = "THEME"
    CLASS = "CLASS"
    ID = "ID"
    STATE = "STATE"
    INLINE = "INLINE"
    PARENT = "PARENT"


class StyleState(str, Enum):
    NORMAL = "NORMAL"
    HOVER = "HOVER"
    ACTIVE = "ACTIVE"
    FOCUSED = "FOCUSED"
    DISABLED = "DISABLED"
    SELECTED = "SELECTED"
    CHECKED = "CHECKED"
    ERROR = "ERROR"


class ThemeMode(str, Enum):
    LIGHT = "LIGHT"
    DARK = "DARK"
    HIGH_CONTRAST = "HIGH_CONTRAST"
    CUSTOM = "CUSTOM"


class TextWrapping(str, Enum):
    NO_WRAP = "NO_WRAP"
    WORD_WRAP = "WORD_WRAP"
    CHAR_WRAP = "CHAR_WRAP"


class TextOverflowMode(str, Enum):
    CLIP = "CLIP"
    ELLIPSIS = "ELLIPSIS"
    WRAP = "WRAP"


class BindingMode(str, Enum):
    ONE_WAY = "ONE_WAY"
    TWO_WAY = "TWO_WAY"


class UIEventType(str, Enum):
    Click = "Click"
    DoubleClick = "DoubleClick"
    PointerDown = "PointerDown"
    PointerUp = "PointerUp"
    PointerMove = "PointerMove"
    PointerEnter = "PointerEnter"
    PointerLeave = "PointerLeave"
    KeyDown = "KeyDown"
    KeyUp = "KeyUp"
    TextInput = "TextInput"
    Focus = "Focus"
    Blur = "Blur"
    Change = "Change"
    Submit = "Submit"


class EventPhase(str, Enum):
    CAPTURE = "CAPTURE"
    TARGET = "TARGET"
    BUBBLE = "BUBBLE"


class UIAccessibleRole(str, Enum):
    BUTTON = "BUTTON"
    CHECKBOX = "CHECKBOX"
    TEXT_FIELD = "TEXT_FIELD"
    SLIDER = "SLIDER"
    LIST = "LIST"
    TREE = "TREE"
    DIALOG = "DIALOG"
    TAB = "TAB"
    IMAGE = "IMAGE"
    LABEL = "LABEL"
    PANEL = "PANEL"


class AnimationTarget(str, Enum):
    OPACITY = "OPACITY"
    POSITION = "POSITION"
    SCALE = "SCALE"
    COLOR = "COLOR"
    SIZE = "SIZE"
    PROGRESS = "PROGRESS"


class AnimationReplacementPolicy(str, Enum):
    REPLACE = "REPLACE"
    QUEUE = "QUEUE"
    MERGE = "MERGE"
    IGNORE = "IGNORE"


class InvalidationType(str, Enum):
    STYLE_DIRTY = "STYLE_DIRTY"
    LAYOUT_DIRTY = "LAYOUT_DIRTY"
    PAINT_DIRTY = "PAINT_DIRTY"
    TEXT_DIRTY = "TEXT_DIRTY"
    CHILDREN_DIRTY = "CHILDREN_DIRTY"


class RenderCommandType(str, Enum):
    DRAW_RECT = "DRAW_RECT"
    DRAW_TEXT = "DRAW_TEXT"
    DRAW_IMAGE = "DRAW_IMAGE"
    DRAW_PATH = "DRAW_PATH"
    PUSH_CLIP = "PUSH_CLIP"
    POP_CLIP = "POP_CLIP"
    PUSH_TRANSFORM = "PUSH_TRANSFORM"
    POP_TRANSFORM = "POP_TRANSFORM"


# ==============================================================================
# GEOMETRY & BOX MODEL
# ==============================================================================

@dataclass
class UIPoint:
    x: float = 0.0
    y: float = 0.0

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass
class UISize:
    width: float = 0.0
    height: float = 0.0

    def to_tuple(self) -> Tuple[float, float]:
        return (self.width, self.height)


@dataclass
class UIRect:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains_point(self, point: UIPoint) -> bool:
        return (self.x <= point.x <= self.right) and (self.y <= point.y <= self.bottom)

    def intersects(self, other: UIRect) -> bool:
        return not (
            self.right <= other.x or
            self.x >= other.right or
            self.bottom <= other.y or
            self.y >= other.bottom
        )

    def intersection(self, other: UIRect) -> Optional[UIRect]:
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.right, other.right)
        y2 = min(self.bottom, other.bottom)
        if x1 < x2 and y1 < y2:
            return UIRect(x1, y1, x2 - x1, y2 - y1)
        return None

    def to_dict(self) -> Dict[str, float]:
        return {"x": round(self.x, 3), "y": round(self.y, 3), "width": round(self.width, 3), "height": round(self.height, 3)}


@dataclass
class UIInsets:
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    @classmethod
    def all(cls, value: float) -> UIInsets:
        return cls(value, value, value, value)

    @classmethod
    def symmetric(cls, vertical: float = 0.0, horizontal: float = 0.0) -> UIInsets:
        return cls(vertical, horizontal, vertical, horizontal)

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom


@dataclass
class UIBoxConstraints:
    min_width: float = 0.0
    max_width: float = float("inf")
    min_height: float = 0.0
    max_height: float = float("inf")

    def constrain_width(self, width: float) -> float:
        return max(self.min_width, min(self.max_width, width))

    def constrain_height(self, height: float) -> float:
        return max(self.min_height, min(self.max_height, height))

    def constrain(self, size: UISize) -> UISize:
        return UISize(
            width=self.constrain_width(size.width),
            height=self.constrain_height(size.height)
        )

    @classmethod
    def tight(cls, width: float, height: float) -> UIBoxConstraints:
        return cls(min_width=width, max_width=width, min_height=height, max_height=height)

    @classmethod
    def loose(cls, width: float = float("inf"), height: float = float("inf")) -> UIBoxConstraints:
        return cls(min_width=0.0, max_width=width, min_height=0.0, max_height=height)


# ==============================================================================
# COLOR, TYPOGRAPHY & ICONS
# ==============================================================================

@dataclass
class UIColor:
    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

    def __post_init__(self):
        self.r = max(0.0, min(1.0, float(self.r)))
        self.g = max(0.0, min(1.0, float(self.g)))
        self.b = max(0.0, min(1.0, float(self.b)))
        self.a = max(0.0, min(1.0, float(self.a)))

    def to_hex(self) -> str:
        r_int = int(round(self.r * 255))
        g_int = int(round(self.g * 255))
        b_int = int(round(self.b * 255))
        a_int = int(round(self.a * 255))
        if a_int == 255:
            return f"#{r_int:02X}{g_int:02X}{b_int:02X}"
        return f"#{r_int:02X}{g_int:02X}{b_int:02X}{a_int:02X}"

    @classmethod
    def from_hex(cls, hex_str: str) -> UIColor:
        clean = hex_str.strip().lstrip("#")
        if len(clean) == 6:
            r = int(clean[0:2], 16) / 255.0
            g = int(clean[2:4], 16) / 255.0
            b = int(clean[4:6], 16) / 255.0
            return cls(r, g, b, 1.0)
        elif len(clean) == 8:
            r = int(clean[0:2], 16) / 255.0
            g = int(clean[2:4], 16) / 255.0
            b = int(clean[4:6], 16) / 255.0
            a = int(clean[6:8], 16) / 255.0
            return cls(r, g, b, a)
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def black(cls) -> UIColor:
        return cls(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def white(cls) -> UIColor:
        return cls(1.0, 1.0, 1.0, 1.0)

    @classmethod
    def transparent(cls) -> UIColor:
        return cls(0.0, 0.0, 0.0, 0.0)

    def relative_luminance(self) -> float:
        def adjust(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else math.pow((c + 0.055) / 1.055, 2.4)
        r = adjust(self.r)
        g = adjust(self.g)
        b = adjust(self.b)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def contrast_ratio(self, other: UIColor) -> float:
        l1 = self.relative_luminance()
        l2 = other.relative_luminance()
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)


@dataclass
class UITypography:
    font_family: str = "Inter"
    fallback_families: List[str] = field(default_factory=lambda: ["Roboto", "Segoe UI", "sans-serif"])
    font_size: float = 14.0
    font_weight: int = 400
    line_height: float = 1.4
    letter_spacing: float = 0.0
    text_color: UIColor = field(default_factory=UIColor.black)
    text_wrapping: TextWrapping = TextWrapping.NO_WRAP
    overflow_mode: TextOverflowMode = TextOverflowMode.CLIP


@dataclass
class UIIcon:
    name: str = ""
    asset_id: Optional[str] = None
    glyph: Optional[str] = None
    size: float = 16.0
    color: UIColor = field(default_factory=UIColor.black)


# ==============================================================================
# STYLES & THEMES
# ==============================================================================

@dataclass
class UIStyleDeclaration:
    background_color: Optional[UIColor] = None
    border_color: Optional[UIColor] = None
    border_width: float = 0.0
    border_radius: float = 0.0
    text_color: Optional[UIColor] = None
    font: Optional[UITypography] = None
    padding: UIInsets = field(default_factory=UIInsets)
    margin: UIInsets = field(default_factory=UIInsets)
    opacity: float = 1.0
    z_index: int = 0
    transform_translate: UIPoint = field(default_factory=UIPoint)
    transform_scale: UIPoint = field(default_factory=lambda: UIPoint(1.0, 1.0))
    transform_rotation_deg: float = 0.0
    cursor: str = "default"
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    def merge(self, override: Optional[UIStyleDeclaration]) -> UIStyleDeclaration:
        if override is None:
            return self
        return UIStyleDeclaration(
            background_color=override.background_color if override.background_color is not None else self.background_color,
            border_color=override.border_color if override.border_color is not None else self.border_color,
            border_width=override.border_width if override.border_width != 0.0 else self.border_width,
            border_radius=override.border_radius if override.border_radius != 0.0 else self.border_radius,
            text_color=override.text_color if override.text_color is not None else self.text_color,
            font=override.font if override.font is not None else self.font,
            padding=override.padding if (override.padding.top != 0 or override.padding.bottom != 0 or override.padding.left != 0 or override.padding.right != 0) else self.padding,
            margin=override.margin if (override.margin.top != 0 or override.margin.bottom != 0 or override.margin.left != 0 or override.margin.right != 0) else self.margin,
            opacity=override.opacity if override.opacity != 1.0 else self.opacity,
            z_index=override.z_index if override.z_index != 0 else self.z_index,
            transform_translate=override.transform_translate if (override.transform_translate.x != 0 or override.transform_translate.y != 0) else self.transform_translate,
            transform_scale=override.transform_scale if (override.transform_scale.x != 1.0 or override.transform_scale.y != 1.0) else self.transform_scale,
            transform_rotation_deg=override.transform_rotation_deg if override.transform_rotation_deg != 0.0 else self.transform_rotation_deg,
            cursor=override.cursor if override.cursor != "default" else self.cursor,
            custom_properties={**self.custom_properties, **override.custom_properties}
        )


@dataclass
class UIThemeTokens:
    colors: Dict[str, UIColor] = field(default_factory=dict)
    spacing: Dict[str, float] = field(default_factory=dict)
    radii: Dict[str, float] = field(default_factory=dict)
    borders: Dict[str, float] = field(default_factory=dict)
    typography: Dict[str, UITypography] = field(default_factory=dict)
    durations_ms: Dict[str, float] = field(default_factory=dict)


@dataclass
class UITheme:
    id: str = "default_theme"
    name: str = "Default Theme"
    mode: ThemeMode = ThemeMode.DARK
    tokens: UIThemeTokens = field(default_factory=UIThemeTokens)
    component_styles: Dict[str, Dict[StyleState, UIStyleDeclaration]] = field(default_factory=dict)

    @classmethod
    def create_default_dark(cls) -> UITheme:
        tokens = UIThemeTokens(
            colors={
                "background": UIColor.from_hex("#121212"),
                "surface": UIColor.from_hex("#1E1E1E"),
                "primary": UIColor.from_hex("#BB86FC"),
                "primary_variant": UIColor.from_hex("#3700B3"),
                "secondary": UIColor.from_hex("#03DAC6"),
                "error": UIColor.from_hex("#CF6679"),
                "on_background": UIColor.from_hex("#FFFFFF"),
                "on_surface": UIColor.from_hex("#E0E0E0"),
                "on_primary": UIColor.from_hex("#000000"),
                "border": UIColor.from_hex("#333333"),
                "focus_ring": UIColor.from_hex("#80D8FF"),
            },
            spacing={"xs": 4.0, "sm": 8.0, "md": 16.0, "lg": 24.0, "xl": 32.0},
            radii={"none": 0.0, "sm": 4.0, "md": 8.0, "lg": 16.0, "full": 999.0},
            borders={"thin": 1.0, "medium": 2.0, "thick": 4.0},
            typography={
                "body": UITypography(font_family="Inter", font_size=14.0, text_color=UIColor.from_hex("#E0E0E0")),
                "button": UITypography(font_family="Inter", font_size=14.0, font_weight=600, text_color=UIColor.from_hex("#FFFFFF")),
                "heading": UITypography(font_family="Inter", font_size=20.0, font_weight=700, text_color=UIColor.from_hex("#FFFFFF")),
            },
            durations_ms={"fast": 150.0, "normal": 300.0, "slow": 500.0}
        )
        return cls(id="dark", name="Default Dark Theme", mode=ThemeMode.DARK, tokens=tokens)

    @classmethod
    def create_default_light(cls) -> UITheme:
        tokens = UIThemeTokens(
            colors={
                "background": UIColor.from_hex("#FFFFFF"),
                "surface": UIColor.from_hex("#F5F5F5"),
                "primary": UIColor.from_hex("#6200EE"),
                "primary_variant": UIColor.from_hex("#3700B3"),
                "secondary": UIColor.from_hex("#03DAC6"),
                "error": UIColor.from_hex("#B00020"),
                "on_background": UIColor.from_hex("#000000"),
                "on_surface": UIColor.from_hex("#212121"),
                "on_primary": UIColor.from_hex("#FFFFFF"),
                "border": UIColor.from_hex("#E0E0E0"),
                "focus_ring": UIColor.from_hex("#2979FF"),
            },
            spacing={"xs": 4.0, "sm": 8.0, "md": 16.0, "lg": 24.0, "xl": 32.0},
            radii={"none": 0.0, "sm": 4.0, "md": 8.0, "lg": 16.0, "full": 999.0},
            borders={"thin": 1.0, "medium": 2.0, "thick": 4.0},
            typography={
                "body": UITypography(font_family="Inter", font_size=14.0, text_color=UIColor.from_hex("#212121")),
                "button": UITypography(font_family="Inter", font_size=14.0, font_weight=600, text_color=UIColor.from_hex("#FFFFFF")),
                "heading": UITypography(font_family="Inter", font_size=20.0, font_weight=700, text_color=UIColor.from_hex("#000000")),
            },
            durations_ms={"fast": 150.0, "normal": 300.0, "slow": 500.0}
        )
        return cls(id="light", name="Default Light Theme", mode=ThemeMode.LIGHT, tokens=tokens)


# ==============================================================================
# DATA BINDINGS & UI EVENTS
# ==============================================================================

@dataclass
class UIBinding:
    binding_id: str
    element_id: str
    target_property: str
    source_key: str
    mode: BindingMode = BindingMode.ONE_WAY
    format_fn: Optional[Callable[[Any], Any]] = None
    parse_fn: Optional[Callable[[Any], Any]] = None
    validator_fn: Optional[Callable[[Any], Tuple[bool, str]]] = None
    last_error: Optional[str] = None
    is_active: bool = True
    sync_count: int = 0


@dataclass
class UIEventData:
    event_type: UIEventType
    target_id: str
    current_target_id: str = ""
    phase: EventPhase = EventPhase.BUBBLE
    bubbles: bool = True
    cancelable: bool = True
    is_default_prevented: bool = False
    is_propagation_stopped: bool = False
    pointer_pos: UIPoint = field(default_factory=UIPoint)
    key_code: Optional[str] = None
    modifiers: Set[str] = field(default_factory=set)
    text_content: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def prevent_default(self) -> None:
        if self.cancelable:
            self.is_default_prevented = True

    def stop_propagation(self) -> None:
        self.is_propagation_stopped = True


# ==============================================================================
# ACCESSIBILITY & ANIMATION
# ==============================================================================

@dataclass
class UIAccessibleNode:
    element_id: str
    role: UIAccessibleRole = UIAccessibleRole.PANEL
    name: str = ""
    description: str = ""
    disabled: bool = False
    checked: Optional[bool] = None
    expanded: Optional[bool] = None
    selected: Optional[bool] = None
    focused: bool = False
    value: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)


@dataclass
class UIAnimation:
    animation_id: str
    element_id: str
    target: AnimationTarget
    property_name: str
    start_value: Any
    end_value: Any
    duration_ms: float = 300.0
    elapsed_ms: float = 0.0
    replacement_policy: AnimationReplacementPolicy = AnimationReplacementPolicy.REPLACE
    easing: str = "linear"
    is_active: bool = True
    is_completed: bool = False

    def progress(self) -> float:
        if self.duration_ms <= 0.0:
            return 1.0
        return max(0.0, min(1.0, self.elapsed_ms / self.duration_ms))

    def evaluate(self) -> Any:
        t = self.progress()
        if self.easing == "ease_in":
            t = t * t
        elif self.easing == "ease_out":
            t = 1.0 - (1.0 - t) * (1.0 - t)
        elif self.easing == "ease_in_out":
            t = 0.5 * (1.0 - math.cos(t * math.pi))

        if isinstance(self.start_value, (int, float)) and isinstance(self.end_value, (int, float)):
            return self.start_value + (self.end_value - self.start_value) * t
        elif isinstance(self.start_value, UIPoint) and isinstance(self.end_value, UIPoint):
            return UIPoint(
                x=self.start_value.x + (self.end_value.x - self.start_value.x) * t,
                y=self.start_value.y + (self.end_value.y - self.start_value.y) * t
            )
        return self.end_value if t >= 1.0 else self.start_value


# ==============================================================================
# RENDER COMMANDS & TREE
# ==============================================================================

@dataclass
class UIRenderCommand:
    command_type: RenderCommandType
    element_id: str
    bounds: UIRect
    color: Optional[UIColor] = None
    text: Optional[str] = None
    font: Optional[UITypography] = None
    image_asset: Optional[str] = None
    clip_rect: Optional[UIRect] = None
    transform_translate: UIPoint = field(default_factory=UIPoint)
    z_index: int = 0
    border_color: Optional[UIColor] = None
    border_width: float = 0.0
    border_radius: float = 0.0
    opacity: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.command_type.value,
            "element_id": self.element_id,
            "bounds": self.bounds.to_dict(),
            "color": self.color.to_hex() if self.color else None,
            "text": self.text,
            "z_index": self.z_index,
            "opacity": round(self.opacity, 3)
        }


@dataclass
class UIRenderTree:
    commands: List[UIRenderCommand] = field(default_factory=list)
    surface_size: UISize = field(default_factory=UISize)
    timestamp: float = 0.0

    def get_draw_order(self) -> List[UIRenderCommand]:
        return sorted(self.commands, key=lambda cmd: cmd.z_index)


# ==============================================================================
# SNAPSHOTS, INSPECTOR & TELEMETRY
# ==============================================================================

@dataclass
class UIStructuralSnapshot:
    root_id: str
    surface_type: str
    element_count: int
    hierarchy: Dict[str, Any]
    computed_bounds: Dict[str, Dict[str, float]]
    computed_styles: Dict[str, Dict[str, Any]]
    focus_id: Optional[str]
    state_hash: str = ""

    def compute_hash(self) -> str:
        serialized = json.dumps({
            "root_id": self.root_id,
            "element_count": self.element_count,
            "hierarchy": self.hierarchy,
            "computed_bounds": self.computed_bounds,
            "focus_id": self.focus_id
        }, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()


@dataclass
class UIInspectorData:
    root_id: str
    element_count: int
    tree: Dict[str, Any]
    styles: Dict[str, Any]
    bounds: Dict[str, Any]
    states: Dict[str, Any]
    active_focus: Optional[str]
    active_bindings: List[str]
    recent_events: List[str]
    render_commands_count: int


@dataclass
class UITelemetry:
    frame_time_ms: float = 0.0
    layout_time_ms: float = 0.0
    style_time_ms: float = 0.0
    paint_time_ms: float = 0.0
    render_time_ms: float = 0.0
    dirty_nodes_count: int = 0
    widget_count: int = 0
    visible_widget_count: int = 0
    accessible_nodes_count: int = 0
    missing_accessible_names: int = 0
    memory_bytes: int = 0


@dataclass
class UIDiagnosticBundle:
    bundle_id: str
    timestamp: float
    root_id: str
    snapshot: UIStructuralSnapshot
    inspector: UIInspectorData
    telemetry: UITelemetry
    signature: str = ""

    def sign(self) -> str:
        data = f"{self.bundle_id}:{self.timestamp}:{self.root_id}:{self.snapshot.state_hash}:{self.telemetry.widget_count}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.sign()
