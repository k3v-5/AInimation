"""
Universal UI, HUD, Menu, Input, Navigation, Accessibility, Localization & User Interaction Models (UAF-81.61).
Normative domain models, enums, data contracts, layout definitions and accessibility standards.
"""

from __future__ import annotations
import math
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class UILifecycleState(str, Enum):
    """Lifecycle states for UI screens and instances (§6)."""
    CREATED = "CREATED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"
    DISABLED = "DISABLED"
    CLOSING = "CLOSING"
    DESTROYED = "DESTROYED"
    FAILED = "FAILED"


class WidgetType(str, Enum):
    """Primitive and composite widget types (§16)."""
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    ICON = "ICON"
    BUTTON = "BUTTON"
    TOGGLE = "TOGGLE"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    SLIDER = "SLIDER"
    PROGRESS_BAR = "PROGRESS_BAR"
    LIST = "LIST"
    GRID = "GRID"
    SCROLL_VIEW = "SCROLL_VIEW"
    DROPDOWN = "DROPDOWN"
    TAB = "TAB"
    INPUT_FIELD = "INPUT_FIELD"
    TOOLTIP = "TOOLTIP"
    PANEL = "PANEL"
    WINDOW = "WINDOW"
    CONTAINER = "CONTAINER"


class LayoutMode(str, Enum):
    """Layout engine placement algorithms (§21)."""
    ABSOLUTE = "ABSOLUTE"
    ANCHOR = "ANCHOR"
    STACK = "STACK"
    GRID = "GRID"
    FLEX = "FLEX"
    OVERLAY = "OVERLAY"
    CONSTRAINT = "CONSTRAINT"


class Anchor(str, Enum):
    """Widget anchoring coordinates relative to parent container (§22)."""
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    CENTER = "CENTER"
    TOP_LEFT = "TOP_LEFT"
    TOP_RIGHT = "TOP_RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"


class SafeAreaPolicy(str, Enum):
    """Handling display safe areas like notches and overscans (§25)."""
    IGNORE = "IGNORE"
    RESPECT = "RESPECT"
    PARTIAL = "PARTIAL"


class InputDevice(str, Enum):
    """Supported input hardware devices (§48)."""
    KEYBOARD = "KEYBOARD"
    MOUSE = "MOUSE"
    GAMEPAD = "GAMEPAD"
    TOUCH = "TOUCH"
    PEN = "PEN"
    REMOTE = "REMOTE"
    VIRTUAL = "VIRTUAL"
    ACCESSIBILITY = "ACCESSIBILITY"


class InputContextType(str, Enum):
    """Layered input contexts (§52)."""
    GAMEPLAY = "GAMEPLAY"
    UI = "UI"
    MENU = "MENU"
    DIALOGUE = "DIALOGUE"
    INVENTORY = "INVENTORY"
    MAP = "MAP"
    SETTINGS = "SETTINGS"
    PHOTO_MODE = "PHOTO_MODE"
    DEBUG = "DEBUG"
    TEXT_INPUT = "TEXT_INPUT"


class InputConsumption(str, Enum):
    """Input event routing decisions (§55)."""
    CONSUMED = "CONSUMED"
    PASSED = "PASSED"
    BLOCKED = "BLOCKED"
    IGNORED = "IGNORED"


class FocusState(str, Enum):
    """Interactive focus states (§68)."""
    UNFOCUSED = "UNFOCUSED"
    FOCUSED = "FOCUSED"
    PRESSED = "PRESSED"
    DISABLED = "DISABLED"
    SELECTED = "SELECTED"
    HOVERED = "HOVERED"


class FocusFallbackPolicy(str, Enum):
    """Policy when focused widget is removed (§71)."""
    PARENT = "PARENT"
    NEXT_VALID = "NEXT_VALID"
    PREVIOUS_VALID = "PREVIOUS_VALID"
    FIRST_VALID = "FIRST_VALID"
    NONE = "NONE"


class NavigationDirection(str, Enum):
    """Spatial and sequential navigation directions (§73)."""
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"


class NavigationMode(str, Enum):
    """Navigation path computation models (§74)."""
    EXPLICIT = "EXPLICIT"
    GEOMETRIC = "GEOMETRIC"
    GRAPH = "GRAPH"
    HYBRID = "HYBRID"


class NavigationWrap(str, Enum):
    """Boundary wrapping behavior (§79)."""
    WRAP = "WRAP"
    NO_WRAP = "NO_WRAP"
    CUSTOM = "CUSTOM"


class AccessibilityRole(str, Enum):
    """Semantic accessibility role (§81)."""
    BUTTON = "BUTTON"
    CHECKBOX = "CHECKBOX"
    SLIDER = "SLIDER"
    TEXT = "TEXT"
    HEADING = "HEADING"
    LIST = "LIST"
    LIST_ITEM = "LIST_ITEM"
    IMAGE = "IMAGE"
    DIALOG = "DIALOG"
    TAB = "TAB"
    MENU = "MENU"
    PROGRESS = "PROGRESS"


class ColorblindMode(str, Enum):
    """Color vision accessibility profiles (§87)."""
    NORMAL = "NORMAL"
    PROTAN = "PROTAN"
    DEUTERAN = "DEUTERAN"
    TRITAN = "TRITAN"
    CUSTOM = "CUSTOM"


class HighContrastMode(str, Enum):
    """Visual contrast profiles (§86)."""
    NORMAL = "NORMAL"
    HIGH_CONTRAST = "HIGH_CONTRAST"
    CUSTOM = "CUSTOM"


class MotionReduction(str, Enum):
    """Animation motion reduction settings (§89)."""
    NORMAL_MOTION = "NORMAL_MOTION"
    REDUCED_MOTION = "REDUCED_MOTION"
    NO_MOTION = "NO_MOTION"


class TextOverflow(str, Enum):
    """Text truncation and wrapping strategies (§45)."""
    CLIP = "CLIP"
    ELLIPSIS = "ELLIPSIS"
    WRAP = "WRAP"
    SCALE = "SCALE"
    EXPAND = "EXPAND"
    SCROLL = "SCROLL"


class TextDirection(str, Enum):
    """Text writing direction (§40)."""
    LTR = "LTR"
    RTL = "RTL"
    AUTO = "AUTO"


class ScreenModalPolicy(str, Enum):
    """Modality and input occlusion policies (§10)."""
    NON_MODAL = "NON_MODAL"
    MODAL = "MODAL"
    FULLSCREEN_MODAL = "FULLSCREEN_MODAL"
    SYSTEM_MODAL = "SYSTEM_MODAL"


class HUDLayer(str, Enum):
    """Ordering layers for HUD presentation (§13)."""
    BACKGROUND = "BACKGROUND"
    WORLD = "WORLD"
    GAMEPLAY = "GAMEPLAY"
    ALERT = "ALERT"
    PROMPT = "PROMPT"
    OVERLAY = "OVERLAY"
    SYSTEM = "SYSTEM"
    DEBUG = "DEBUG"


class HUDVisibility(str, Enum):
    """Visibility control for HUD components (§14)."""
    VISIBLE = "VISIBLE"
    HIDDEN = "HIDDEN"
    CONDITIONAL = "CONDITIONAL"


class NotificationPriority(str, Enum):
    """Priority grading for system and gameplay toast alerts."""
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UIAudioCue(str, Enum):
    """Standardized UI audio events (§166)."""
    HOVER = "HOVER"
    FOCUS = "FOCUS"
    PRESS = "PRESS"
    CONFIRM = "CONFIRM"
    CANCEL = "CANCEL"
    ERROR = "ERROR"
    NOTIFICATION = "NOTIFICATION"


class UIAnimationType(str, Enum):
    """Visual transitions and micro-animations (§165)."""
    FADE = "FADE"
    SLIDE = "SLIDE"
    SCALE = "SCALE"
    ROTATE = "ROTATE"
    COLOR = "COLOR"
    VALUE = "VALUE"
    ENTER = "ENTER"
    EXIT = "EXIT"


class ScreenReaderOrderPolicy(str, Enum):
    """Traversal order for assistive screen readers (§84)."""
    EXPLICIT = "EXPLICIT"
    GEOMETRIC = "GEOMETRIC"
    HIERARCHICAL = "HIERARCHICAL"


# ==============================================================================
# DATA STRUCTURES & VALUE OBJECTS
# ==============================================================================

@dataclass
class UIBounds:
    """Bounding box in normalized or pixel space (§15)."""
    x: float = 0.0
    y: float = 0.0
    width: float = 100.0
    height: float = 100.0

    def contains(self, px: float, py: float) -> bool:
        """Hit test check for coordinate inside bounds."""
        return self.x <= px <= (self.x + self.width) and self.y <= py <= (self.y + self.height)


@dataclass
class UISafeArea:
    """Safe area inset margins (§24)."""
    top: float = 0.0
    bottom: float = 0.0
    left: float = 0.0
    right: float = 0.0


@dataclass
class UIStyle:
    """Declarative visual styling properties."""
    color: str = "#FFFFFF"
    background_color: str = "#000000"
    font_size: int = 14
    font_family: str = "Roboto"
    opacity: float = 1.0
    border_width: float = 0.0
    border_color: str = "#000000"
    border_radius: float = 0.0
    padding: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    margin: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)


@dataclass
class UIWidget:
    """Atomic interactive or visual UI node (§15, §16, §17)."""
    widget_id: str
    widget_type: WidgetType = WidgetType.PANEL
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    bounds: UIBounds = field(default_factory=UIBounds)
    visibility: bool = True
    enabled: bool = True
    focusable: bool = False
    style: UIStyle = field(default_factory=UIStyle)
    state: FocusState = FocusState.UNFOCUSED
    parameters: Dict[str, Any] = field(default_factory=dict)
    accessibility_role: AccessibilityRole = AccessibilityRole.BUTTON
    accessibility_label: str = ""
    accessibility_description: str = ""
    accessibility_hint: str = ""
    navigation_explicit: Dict[str, str] = field(default_factory=dict)
    layout_mode: LayoutMode = LayoutMode.ABSOLUTE
    anchor: Anchor = Anchor.TOP_LEFT
    z_order: int = 0


@dataclass
class UIScreen:
    """A full screen or top-level UI presentation layer (§7, §8)."""
    screen_id: str
    layer: str = "MAIN"
    priority: int = 10
    input_context: InputContextType = InputContextType.UI
    root_widget_id: str = "root"
    modal_policy: ScreenModalPolicy = ScreenModalPolicy.NON_MODAL
    safe_area_policy: SafeAreaPolicy = SafeAreaPolicy.RESPECT
    owner: str = "ui_manager"
    widgets: Dict[str, UIWidget] = field(default_factory=dict)

    def add_widget(self, widget: UIWidget, parent_id: Optional[str] = None) -> None:
        """Adds widget with deterministic parent-child hierarchy (§18)."""
        if parent_id is not None:
            widget.parent_id = parent_id
        self.widgets[widget.widget_id] = widget
        pid = widget.parent_id
        if pid and pid in self.widgets:
            if widget.widget_id not in self.widgets[pid].children:
                self.widgets[pid].children.append(widget.widget_id)


@dataclass
class UIScreenStack:
    """Stack managing screen transitions and modal blocks (§8)."""
    stack: List[UIScreen] = field(default_factory=list)

    def push(self, screen: UIScreen) -> None:
        self.stack.append(screen)

    def pop(self) -> Optional[UIScreen]:
        if self.stack:
            return self.stack.pop()
        return None

    def top(self) -> Optional[UIScreen]:
        if self.stack:
            return self.stack[-1]
        return None

    def clear(self) -> None:
        self.stack.clear()


@dataclass
class UIInputAction:
    """Resolved input event (§50)."""
    action_id: str
    device: InputDevice = InputDevice.KEYBOARD
    button: str = ""
    axis: Tuple[float, float] = (0.0, 0.0)
    value: float = 1.0
    timestamp: float = 0.0
    context: InputContextType = InputContextType.UI
    is_down: bool = True
    modifiers: Set[str] = field(default_factory=set)


@dataclass
class InputContext:
    """Priority layer controlling active input mapping (§51, §52, §53)."""
    context_id: str
    context_type: InputContextType = InputContextType.UI
    priority: int = 10
    blocks_lower: bool = False
    active_actions: Set[str] = field(default_factory=set)


@dataclass
class InputRemappingProfile:
    """User-customizable key and button mappings (§93)."""
    profile_id: str
    device: InputDevice = InputDevice.KEYBOARD
    mappings: Dict[str, str] = field(default_factory=dict)  # action_id -> button/key


@dataclass
class InputPrompt:
    """Visual button icon prompt based on active input device (§96, §97)."""
    action_id: str
    device: InputDevice
    glyph: str
    description: str = ""


@dataclass
class UINotification:
    """HUD toast or system notification (§167)."""
    notification_id: str
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    duration: float = 3.0
    created_at: Optional[float] = None
    icon: str = ""
    sound: Optional[UIAudioCue] = None
    coalescing_key: str = ""
    is_expired: bool = False


@dataclass
class LocalizationRecord:
    """Translatable string table entry (§31, §33)."""
    key: str
    translations: Dict[str, str] = field(default_factory=dict)
    default_language: str = "en"


@dataclass
class UIPreferences:
    """Persisted user settings for interface, controls, and accessibility (§175)."""
    language: str = "en"
    text_direction: TextDirection = TextDirection.LTR
    ui_scale: float = 1.0
    font_scale: float = 1.0
    high_contrast: HighContrastMode = HighContrastMode.NORMAL
    colorblind_mode: ColorblindMode = ColorblindMode.NORMAL
    motion_reduction: MotionReduction = MotionReduction.NORMAL_MOTION
    audio_enabled: bool = True
    screen_reader: bool = False


@dataclass
class UIAsset:
    """Declarative specification of an interface asset (§4)."""
    ui_id: str
    version: str = "1.0.0"
    root_screen: UIScreen = field(default_factory=lambda: UIScreen(screen_id="root_screen"))
    styles: Dict[str, UIStyle] = field(default_factory=dict)
    templates: Dict[str, Any] = field(default_factory=dict)
    bindings: Dict[str, str] = field(default_factory=dict)
    localization_keys: List[str] = field(default_factory=list)
    accessibility_metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class UIInstance:
    """Active runtime evaluation instance of a UI asset (§5)."""
    instance_id: str
    ui_id: str
    lifecycle_state: UILifecycleState = UILifecycleState.CREATED
    current_screen_id: str = ""
    active_context: InputContextType = InputContextType.UI
    focused_widget_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    owner: str = "system"


@dataclass
class UIDiagnosticReport:
    """Runtime metrics, hierarchy health, and performance checks."""
    ui_id: str
    instance_id: str
    is_healthy: bool = True
    widget_count: int = 0
    screen_stack_depth: int = 0
    active_notifications_count: int = 0
    memory_kb: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
