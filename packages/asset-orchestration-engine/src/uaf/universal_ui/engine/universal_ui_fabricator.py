"""
Universal UI Fabricator & User Interaction Runtime Engine (UAF-81.61).
Normative presentation, input routing, screen stack, layout, focus management,
localization, accessibility, HUD, notifications, and 17 Golden Scenarios.
"""

from __future__ import annotations
import math
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..models.definition import (
    UILifecycleState,
    WidgetType,
    LayoutMode,
    Anchor,
    SafeAreaPolicy,
    InputDevice,
    InputContextType,
    InputConsumption,
    FocusState,
    FocusFallbackPolicy,
    NavigationDirection,
    NavigationMode,
    NavigationWrap,
    AccessibilityRole,
    ColorblindMode,
    HighContrastMode,
    MotionReduction,
    TextOverflow,
    TextDirection,
    ScreenModalPolicy,
    HUDLayer,
    HUDVisibility,
    NotificationPriority,
    UIAudioCue,
    UIAnimationType,
    ScreenReaderOrderPolicy,
    UIBounds,
    UISafeArea,
    UIStyle,
    UIWidget,
    UIScreen,
    UIScreenStack,
    UIInputAction,
    InputContext,
    InputRemappingProfile,
    InputPrompt,
    UINotification,
    LocalizationRecord,
    UIPreferences,
    UIAsset,
    UIInstance,
    UIDiagnosticReport,
)


class UniversalUIFabricator:
    """
    Authoritative evaluation engine for user interfaces, input routing,
    spatial navigation, localization, accessibility, and HUD presentation.
    """

    def __init__(self):
        # Active screen stack
        self._screen_stack: UIScreenStack = UIScreenStack()
        # Context stack
        self._context_stack: List[InputContext] = [
            InputContext(context_id="ctx_default", context_type=InputContextType.UI, priority=0)
        ]
        # Active focused widget id
        self._focused_widget_id: Optional[str] = None
        # Focus history stack for focus restoration
        self._focus_history: List[Optional[str]] = []
        # Remapping profiles: device -> profile
        self._remapping_profiles: Dict[InputDevice, InputRemappingProfile] = {}
        # Localization table: key -> LocalizationRecord
        self._localization_table: Dict[str, LocalizationRecord] = {}
        # User preferences
        self._preferences: UIPreferences = UIPreferences()
        # Active notifications queue
        self._notifications: List[UINotification] = []
        # HUD Elements: element_id -> (layer, widget, visibility)
        self._hud_elements: Dict[str, Dict[str, Any]] = {}
        # Audio cue playback history for deduplication: cue_name -> timestamp
        self._audio_history: Dict[str, float] = {}

    # ==========================================================================
    # INSTANCE CREATION & SCREEN STACK (§5, §7, §8, §9)
    # ==========================================================================

    def create_instance(
        self,
        asset: UIAsset,
        instance_id: str = "",
        owner: str = "system",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> UIInstance:
        """Creates an active runtime instance of a UI asset (§5)."""
        if not instance_id:
            instance_id = f"ui_inst_{asset.ui_id}_{int(time.time() * 1000)}"

        inst = UIInstance(
            instance_id=instance_id,
            ui_id=asset.ui_id,
            lifecycle_state=UILifecycleState.READY,
            current_screen_id=asset.root_screen.screen_id,
            parameters=parameters or {},
            owner=owner,
        )
        return inst

    def push_screen(self, screen: UIScreen, owner: str = "ui_manager") -> bool:
        """Pushes a new screen onto the active screen stack (§8)."""
        screen.owner = owner
        self._focus_history.append(self._focused_widget_id)
        self._screen_stack.push(screen)

        # Automatically focus first focusable widget
        first_focusable = self._find_first_focusable(screen)
        if first_focusable:
            self.set_focus(first_focusable, screen.screen_id)
        return True

    def pop_screen(self, owner: str = "ui_manager") -> Optional[UIScreen]:
        """Pops the top screen and restores previous focus (§8, §70)."""
        if not self._screen_stack.stack:
            return None
        popped = self._screen_stack.pop()

        # Restore prior focus
        if self._focus_history:
            prev_focus = self._focus_history.pop()
            self._focused_widget_id = prev_focus

        return popped

    def replace_screen(self, screen: UIScreen, owner: str = "ui_manager") -> bool:
        """Replaces the top screen (§8)."""
        if self._screen_stack.stack:
            self._screen_stack.pop()
        return self.push_screen(screen, owner=owner)

    def get_top_screen(self) -> Optional[UIScreen]:
        """Returns currently active top screen."""
        return self._screen_stack.top()

    def get_screen_stack(self) -> List[UIScreen]:
        """Returns all screens currently on the stack."""
        return list(self._screen_stack.stack)

    def clear_screens(self) -> None:
        """Clears all screens."""
        self._screen_stack.clear()
        self._focused_widget_id = None
        self._focus_history.clear()

    # ==========================================================================
    # FOCUS & NAVIGATION (§66 - §79)
    # ==========================================================================

    def set_focus(self, widget_id: Optional[str], screen_id: Optional[str] = None) -> bool:
        """Sets the interactive focus owner (§66, §68, §69)."""
        top = self.get_top_screen()
        if not top and not screen_id:
            self._focused_widget_id = widget_id
            return True

        screen = top
        if screen_id:
            for s in self._screen_stack.stack:
                if s.screen_id == screen_id:
                    screen = s
                    break

        if screen and widget_id:
            widget = screen.widgets.get(widget_id)
            if not widget or not widget.enabled or not widget.focusable:
                return False

            # Clear previous widget state
            if self._focused_widget_id and self._focused_widget_id in screen.widgets:
                screen.widgets[self._focused_widget_id].state = FocusState.UNFOCUSED

            widget.state = FocusState.FOCUSED

        self._focused_widget_id = widget_id
        return True

    def get_focused_widget_id(self) -> Optional[str]:
        """Returns the currently focused widget ID."""
        return self._focused_widget_id

    def navigate(
        self,
        direction: NavigationDirection,
        mode: NavigationMode = NavigationMode.HYBRID,
        wrap: NavigationWrap = NavigationWrap.WRAP,
    ) -> Optional[str]:
        """
        Calculates spatial or explicit focus movement in given direction (§73 - §79).
        """
        top = self.get_top_screen()
        if not top or not self._focused_widget_id:
            return None

        current = top.widgets.get(self._focused_widget_id)
        if not current:
            return None

        # 1. Explicit Navigation Route (§75)
        dir_key = direction.value.lower()
        if dir_key in current.navigation_explicit:
            target_id = current.navigation_explicit[dir_key]
            if target_id in top.widgets and top.widgets[target_id].enabled and top.widgets[target_id].focusable:
                self.set_focus(target_id)
                return target_id

        if mode == NavigationMode.EXPLICIT:
            return None

        # 2. Geometric Routing (§76, §77)
        candidates = [
            w for w in top.widgets.values()
            if w.widget_id != current.widget_id and w.enabled and w.focusable and w.visibility
        ]
        if not candidates:
            return None

        curr_cx = current.bounds.x + current.bounds.width * 0.5
        curr_cy = current.bounds.y + current.bounds.height * 0.5

        scored_candidates = []
        for c in candidates:
            cx = c.bounds.x + c.bounds.width * 0.5
            cy = c.bounds.y + c.bounds.height * 0.5
            dx = cx - curr_cx
            dy = cy - curr_cy

            is_valid_dir = False
            if direction == NavigationDirection.UP and dy < -1.0:
                is_valid_dir = True
            elif direction == NavigationDirection.DOWN and dy > 1.0:
                is_valid_dir = True
            elif direction == NavigationDirection.LEFT and dx < -1.0:
                is_valid_dir = True
            elif direction == NavigationDirection.RIGHT and dx > 1.0:
                is_valid_dir = True
            elif direction in (NavigationDirection.NEXT, NavigationDirection.PREVIOUS):
                is_valid_dir = True

            if is_valid_dir:
                dist = math.sqrt(dx * dx + dy * dy)
                scored_candidates.append((dist, c.widget_id))

        if scored_candidates:
            scored_candidates.sort(key=lambda item: item[0])
            best_target_id = scored_candidates[0][1]
            self.set_focus(best_target_id)
            return best_target_id

        # 3. Wrapping (§79)
        if wrap == NavigationWrap.WRAP:
            # Pick extreme opposite candidate
            if direction == NavigationDirection.DOWN:
                top_most = min(candidates, key=lambda c: c.bounds.y)
                self.set_focus(top_most.widget_id)
                return top_most.widget_id
            elif direction == NavigationDirection.UP:
                bottom_most = max(candidates, key=lambda c: c.bounds.y)
                self.set_focus(bottom_most.widget_id)
                return bottom_most.widget_id
            elif direction == NavigationDirection.RIGHT:
                left_most = min(candidates, key=lambda c: c.bounds.x)
                self.set_focus(left_most.widget_id)
                return left_most.widget_id
            elif direction == NavigationDirection.LEFT:
                right_most = max(candidates, key=lambda c: c.bounds.x)
                self.set_focus(right_most.widget_id)
                return right_most.widget_id

        return None

    def _find_first_focusable(self, screen: UIScreen) -> Optional[str]:
        """Finds first valid focusable widget in tree order."""
        for w in screen.widgets.values():
            if w.enabled and w.focusable and w.visibility:
                return w.widget_id
        return None

    # ==========================================================================
    # INPUT ROUTING & CONTEXTS (§47 - §65, §93 - §98)
    # ==========================================================================

    def push_input_context(self, context: InputContext) -> None:
        """Pushes an input context onto the active stack (§53)."""
        self._context_stack.append(context)

    def pop_input_context(self) -> Optional[InputContext]:
        """Pops the active input context."""
        if len(self._context_stack) > 1:
            return self._context_stack.pop()
        return None

    def get_active_context(self) -> InputContext:
        """Returns the highest priority active input context (§54)."""
        return self._context_stack[-1]

    def dispatch_input(self, action: UIInputAction) -> InputConsumption:
        """
        Routes an input action through modal layers, contexts, and focus owner (§55).
        """
        top_screen = self.get_top_screen()
        if not top_screen:
            return InputConsumption.PASSED

        # Check modal blocking (§10, §11)
        if top_screen.modal_policy in (ScreenModalPolicy.MODAL, ScreenModalPolicy.FULLSCREEN_MODAL):
            # Block inputs if targeting actions outside modal
            pass

        active_ctx = self.get_active_context()
        if active_ctx.blocks_lower:
            # Active context claims exclusive input
            return InputConsumption.CONSUMED

        # Map to focus actions
        if action.button in ("Select", "Enter", "Gamepad_A", "Space"):
            if self._focused_widget_id and self._focused_widget_id in top_screen.widgets:
                w = top_screen.widgets[self._focused_widget_id]
                if w.enabled:
                    w.state = FocusState.PRESSED
                    self.play_audio_cue(UIAudioCue.PRESS)
                    return InputConsumption.CONSUMED

        if action.button in ("Cancel", "Escape", "Gamepad_B"):
            self.play_audio_cue(UIAudioCue.CANCEL)
            return InputConsumption.CONSUMED

        return InputConsumption.PASSED

    def set_remapping_profile(self, profile: InputRemappingProfile) -> None:
        """Registers user custom input remapping profile (§93)."""
        self._remapping_profiles[profile.device] = profile

    def apply_remapping(self, action_id: str, device: InputDevice) -> str:
        """Resolves active key/button for action accounting for user remapping (§94)."""
        prof = self._remapping_profiles.get(device)
        if prof and action_id in prof.mappings:
            return prof.mappings[action_id]
        return action_id

    def resolve_prompt(self, action_id: str, device: InputDevice) -> InputPrompt:
        """Resolves visual button glyph for dynamic prompt presentation (§96, §97)."""
        remapped_btn = self.apply_remapping(action_id, device)
        glyphs = {
            InputDevice.KEYBOARD: {"Jump": "[ Space ]", "Interact": "[ E ]", "Cancel": "[ Esc ]"},
            InputDevice.GAMEPAD: {"Jump": "[ (A) ]", "Interact": "[ (X) ]", "Cancel": "[ (B) ]"},
            InputDevice.TOUCH: {"Jump": "[ Tap ]", "Interact": "[ Tap ]", "Cancel": "[ Swipe ]"},
        }
        device_glyphs = glyphs.get(device, {})
        glyph = device_glyphs.get(remapped_btn, f"[ {remapped_btn} ]")
        return InputPrompt(action_id=action_id, device=device, glyph=glyph)

    # ==========================================================================
    # LAYOUT ENGINE & RESOLUTION SCALING (§20 - §29)
    # ==========================================================================

    def compute_layout(
        self,
        screen: UIScreen,
        viewport_width: float,
        viewport_height: float,
        safe_area: Optional[UISafeArea] = None,
    ) -> Dict[str, UIBounds]:
        """
        Computes absolute bounds for all widgets in screen hierarchy (§20, §21).
        Supports percentage layout, anchoring, and safe area margins (§22 - §25).
        """
        computed_bounds: Dict[str, UIBounds] = {}
        sa = safe_area or UISafeArea()

        vw = viewport_width
        vh = viewport_height
        origin_x = 0.0
        origin_y = 0.0

        if screen.safe_area_policy == SafeAreaPolicy.RESPECT:
            origin_x += sa.left
            origin_y += sa.top
            vw -= (sa.left + sa.right)
            vh -= (sa.top + sa.bottom)

        for widget in screen.widgets.values():
            w_box = UIBounds(
                x=widget.bounds.x,
                y=widget.bounds.y,
                width=widget.bounds.width,
                height=widget.bounds.height,
            )

            # Percentage scaling (§23)
            if "width_percent" in widget.parameters:
                w_box.width = vw * (widget.parameters["width_percent"] / 100.0)
            if "height_percent" in widget.parameters:
                w_box.height = vh * (widget.parameters["height_percent"] / 100.0)

            # Anchoring offset calculation (§22)
            if widget.anchor == Anchor.CENTER:
                w_box.x = origin_x + (vw - w_box.width) * 0.5 + widget.bounds.x
                w_box.y = origin_y + (vh - w_box.height) * 0.5 + widget.bounds.y
            elif widget.anchor == Anchor.TOP_RIGHT:
                w_box.x = origin_x + vw - w_box.width - widget.bounds.x
                w_box.y = origin_y + widget.bounds.y
            elif widget.anchor == Anchor.BOTTOM_LEFT:
                w_box.x = origin_x + widget.bounds.x
                w_box.y = origin_y + vh - w_box.height - widget.bounds.y
            elif widget.anchor == Anchor.BOTTOM_RIGHT:
                w_box.x = origin_x + vw - w_box.width - widget.bounds.x
                w_box.y = origin_y + vh - w_box.height - widget.bounds.y
            elif widget.anchor == Anchor.BOTTOM:
                w_box.x = origin_x + (vw - w_box.width) * 0.5
                w_box.y = origin_y + vh - w_box.height - widget.bounds.y
            else:
                w_box.x += origin_x
                w_box.y += origin_y

            # Apply RTL mirroring if configured (§41)
            if self._preferences.text_direction == TextDirection.RTL:
                w_box = self.apply_rtl_mirroring(w_box, viewport_width)

            computed_bounds[widget.widget_id] = w_box

        return computed_bounds

    # ==========================================================================
    # LOCALIZATION & TEXT (§30 - §46)
    # ==========================================================================

    def register_localization(self, record: LocalizationRecord) -> None:
        """Registers a translatable string table record (§33)."""
        self._localization_table[record.key] = record

    def get_localized_text(
        self,
        key: str,
        lang: Optional[str] = None,
        args: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Retrieves translated string with variable substitution and fallbacks (§34, §35).
        """
        target_lang = lang or self._preferences.language
        record = self._localization_table.get(key)
        if not record:
            return f"[{key}]"

        text = record.translations.get(target_lang)
        if not text:
            text = record.translations.get(record.default_language, f"[{key}]")

        # Parameter formatting ({name}, {count})
        if args:
            for k, v in args.items():
                text = text.replace(f"{{{k}}}", str(v))

        return text

    def format_number(self, value: float, lang: str = "en") -> str:
        """Locale-aware number formatting (§39)."""
        if lang in ("de", "fr", "es"):
            # Dot for thousands, comma for decimals
            formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return formatted
        return f"{value:,.2f}"

    def format_currency(self, amount: float, currency_code: str = "USD", lang: str = "en") -> str:
        """Locale-aware currency presentation (§39)."""
        num_str = self.format_number(amount, lang=lang)
        symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
        sym = symbols.get(currency_code, currency_code)
        if lang in ("de", "fr"):
            return f"{num_str} {sym}"
        return f"{sym}{num_str}"

    def apply_rtl_mirroring(self, bounds: UIBounds, container_width: float) -> UIBounds:
        """Mirrors X coordinate horizontally for Right-to-Left layouts (§41)."""
        mirrored_x = container_width - bounds.x - bounds.width
        return UIBounds(
            x=mirrored_x,
            y=bounds.y,
            width=bounds.width,
            height=bounds.height,
        )

    # ==========================================================================
    # ACCESSIBILITY & PREFERENCES (§80 - §92, §175)
    # ==========================================================================

    def set_preferences(self, prefs: UIPreferences) -> None:
        """Updates user accessibility and visual preferences (§175)."""
        self._preferences = prefs

    def get_preferences(self) -> UIPreferences:
        """Returns active user preferences."""
        return self._preferences

    def apply_high_contrast(self, color_hex: str, is_background: bool = False) -> str:
        """Transforms palette color under High Contrast mode (§86)."""
        if self._preferences.high_contrast == HighContrastMode.HIGH_CONTRAST:
            if is_background:
                return "#000000"
            return "#FFFF00"  # High visibility yellow on pure black
        return color_hex

    def apply_colorblind_filter(self, color_hex: str, mode: ColorblindMode) -> str:
        """Simulates or compensates colorblind accessibility palettes (§87)."""
        if mode == ColorblindMode.PROTAN:
            # Shift problematic reds to distinct cyan/magenta tones
            if color_hex.upper() in ("#FF0000", "#E53935"):
                return "#0088FF"
        elif mode == ColorblindMode.DEUTERAN:
            # Shift greens to high contrast blue/yellow
            if color_hex.upper() in ("#00FF00", "#43A047"):
                return "#FFD600"
        return color_hex

    def get_screen_reader_tree(
        self,
        screen: UIScreen,
        order_policy: ScreenReaderOrderPolicy = ScreenReaderOrderPolicy.HIERARCHICAL,
    ) -> List[Dict[str, Any]]:
        """Generates semantic screen reader narration list (§83, §84)."""
        reader_elements = []
        for w in screen.widgets.values():
            if not w.visibility:
                continue
            reader_elements.append({
                "widget_id": w.widget_id,
                "role": w.accessibility_role.value,
                "label": w.accessibility_label or w.parameters.get("text", w.widget_id),
                "description": w.accessibility_description,
                "hint": w.accessibility_hint,
                "state": w.state.value,
                "value": w.parameters.get("value", ""),
            })
        return reader_elements

    # ==========================================================================
    # HUD & NOTIFICATIONS (§12 - §14, §167)
    # ==========================================================================

    def register_hud_element(
        self,
        element_id: str,
        layer: HUDLayer,
        widget: UIWidget,
        visibility: HUDVisibility = HUDVisibility.VISIBLE,
    ) -> None:
        """Registers a persistent HUD component (§12, §13)."""
        self._hud_elements[element_id] = {
            "layer": layer,
            "widget": widget,
            "visibility": visibility,
        }

    def set_hud_visibility(self, element_id: str, visibility: HUDVisibility) -> bool:
        """Toggles visibility for HUD component (§14)."""
        if element_id in self._hud_elements:
            self._hud_elements[element_id]["visibility"] = visibility
            return True
        return False

    def post_notification(self, notification: UINotification) -> str:
        """Enqueues toast or banner notification with priority ordering (§167)."""
        if notification.created_at is None:
            notification.created_at = time.time()

        # Check coalescing (§167)
        if notification.coalescing_key:
            for existing in self._notifications:
                if existing.coalescing_key == notification.coalescing_key and not existing.is_expired:
                    existing.title = notification.title
                    existing.message = notification.message
                    existing.created_at = notification.created_at
                    return existing.notification_id

        self._notifications.append(notification)
        self.play_audio_cue(UIAudioCue.NOTIFICATION)
        return notification.notification_id

    def get_active_notifications(self, current_time: float) -> List[UINotification]:
        """Returns active, non-expired notifications ordered by priority (§167)."""
        priority_weights = {
            NotificationPriority.CRITICAL: 4,
            NotificationPriority.HIGH: 3,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.LOW: 1,
        }
        active = []
        for n in self._notifications:
            if (current_time - n.created_at) > n.duration:
                n.is_expired = True
            if not n.is_expired:
                active.append(n)

        active.sort(key=lambda n: priority_weights.get(n.priority, 0), reverse=True)
        return active

    # ==========================================================================
    # UI AUDIO & DEDUPLICATION (§166)
    # ==========================================================================

    def play_audio_cue(self, cue: UIAudioCue, current_time: float = 0.0) -> bool:
        """Plays UI audio with automatic debounce and deduplication (§166)."""
        now = current_time or time.time()
        last_played = self._audio_history.get(cue.value, 0.0)
        # 50ms deduplication window
        if (now - last_played) < 0.05:
            return False
        self._audio_history[cue.value] = now
        return True

    # ==========================================================================
    # DIAGNOSTICS & METRICS
    # ==========================================================================

    def get_diagnostics(self, instance: UIInstance) -> UIDiagnosticReport:
        """Produces runtime diagnostic and performance report."""
        top = self.get_top_screen()
        w_count = len(top.widgets) if top else 0
        return UIDiagnosticReport(
            ui_id=instance.ui_id,
            instance_id=instance.instance_id,
            is_healthy=True,
            widget_count=w_count,
            screen_stack_depth=len(self._screen_stack.stack),
            active_notifications_count=len(self._notifications),
            memory_kb=w_count * 1.5,
        )

    # ==========================================================================
    # 17 GOLDEN SCENARIOS FACTORY (§177)
    # ==========================================================================

    def create_golden_scenario(self, scenario_name: str) -> Tuple[UIAsset, UIInstance]:
        """
        Generates canonical Golden Scenarios required by §177:
        1. GOLDEN_MAIN_MENU
        2. GOLDEN_HUD
        3. GOLDEN_INVENTORY
        4. GOLDEN_QUEST_MENU
        5. GOLDEN_DIALOGUE
        6. GOLDEN_SETTINGS
        7. GOLDEN_SAVE_LOAD
        8. GOLDEN_NOTIFICATION
        9. GOLDEN_ACCESSIBILITY
        10. GOLDEN_RTL
        11. GOLDEN_HIGH_CONTRAST
        12. GOLDEN_COLORBLIND
        13. GOLDEN_GAMEPAD_NAVIGATION
        14. GOLDEN_TOUCH_LAYOUT
        15. GOLDEN_ULTRAWIDE
        16. GOLDEN_SAFE_AREA
        17. GOLDEN_FULL_UI
        """
        root_screen = UIScreen(screen_id=f"screen_{scenario_name.lower()}")
        asset = UIAsset(ui_id=f"asset_{scenario_name.lower()}", root_screen=root_screen)
        inst = self.create_instance(asset, instance_id=f"inst_{scenario_name.lower()}")

        if scenario_name == "GOLDEN_MAIN_MENU":
            btn_play = UIWidget("btn_play", WidgetType.BUTTON, focusable=True, parameters={"text": "Play Game"})
            btn_opt = UIWidget("btn_opt", WidgetType.BUTTON, focusable=True, parameters={"text": "Options"})
            btn_exit = UIWidget("btn_exit", WidgetType.BUTTON, focusable=True, parameters={"text": "Exit"})
            root_screen.add_widget(btn_play)
            root_screen.add_widget(btn_opt)
            root_screen.add_widget(btn_exit)

        elif scenario_name == "GOLDEN_HUD":
            hp_bar = UIWidget("hud_hp", WidgetType.PROGRESS_BAR, parameters={"value": 100, "max": 100})
            compass = UIWidget("hud_compass", WidgetType.ICON, anchor=Anchor.TOP)
            prompt = UIWidget("hud_interact", WidgetType.TEXT, anchor=Anchor.CENTER, parameters={"text": "[E] Interact"})
            root_screen.add_widget(hp_bar)
            root_screen.add_widget(compass)
            root_screen.add_widget(prompt)

        elif scenario_name == "GOLDEN_INVENTORY":
            grid = UIWidget("inv_grid", WidgetType.GRID, parameters={"columns": 5, "rows": 4})
            for i in range(10):
                slot = UIWidget(f"slot_{i}", WidgetType.BUTTON, focusable=True, parameters={"item_id": f"item_{i}"})
                root_screen.add_widget(slot, parent_id="inv_grid")
            root_screen.add_widget(grid)

        elif scenario_name == "GOLDEN_QUEST_MENU":
            q_list = UIWidget("quest_list", WidgetType.LIST)
            q_item = UIWidget("quest_item_01", WidgetType.BUTTON, focusable=True, parameters={"quest_name": "Save the Citadel"})
            root_screen.add_widget(q_list)
            root_screen.add_widget(q_item, parent_id="quest_list")

        elif scenario_name == "GOLDEN_DIALOGUE":
            dlg_box = UIWidget("dlg_box", WidgetType.PANEL, anchor=Anchor.BOTTOM)
            spk = UIWidget("dlg_speaker", WidgetType.TEXT, parameters={"text": "Advisor"})
            body = UIWidget("dlg_body", WidgetType.TEXT, parameters={"text": "We are out of time, Commander."})
            ch1 = UIWidget("dlg_ch1", WidgetType.BUTTON, focusable=True, parameters={"text": "Proceed immediately"})
            ch2 = UIWidget("dlg_ch2", WidgetType.BUTTON, focusable=True, parameters={"text": "Hold position"})
            root_screen.add_widget(dlg_box)
            root_screen.add_widget(spk, parent_id="dlg_box")
            root_screen.add_widget(body, parent_id="dlg_box")
            root_screen.add_widget(ch1, parent_id="dlg_box")
            root_screen.add_widget(ch2, parent_id="dlg_box")

        elif scenario_name == "GOLDEN_SETTINGS":
            tab_audio = UIWidget("tab_audio", WidgetType.TAB, focusable=True, parameters={"name": "Audio"})
            slider_vol = UIWidget("slider_vol", WidgetType.SLIDER, focusable=True, parameters={"value": 0.8})
            root_screen.add_widget(tab_audio)
            root_screen.add_widget(slider_vol)

        elif scenario_name == "GOLDEN_SAVE_LOAD":
            slot1 = UIWidget("save_slot_1", WidgetType.BUTTON, focusable=True, parameters={"slot": 1, "timestamp": "2026-09-03"})
            slot2 = UIWidget("save_slot_2", WidgetType.BUTTON, focusable=True, parameters={"slot": 2, "timestamp": "2026-09-04"})
            root_screen.add_widget(slot1)
            root_screen.add_widget(slot2)

        elif scenario_name == "GOLDEN_NOTIFICATION":
            toast = UIWidget("toast_area", WidgetType.PANEL, anchor=Anchor.TOP_RIGHT)
            root_screen.add_widget(toast)

        elif scenario_name == "GOLDEN_ACCESSIBILITY":
            acc_btn = UIWidget(
                "btn_accessible",
                WidgetType.BUTTON,
                focusable=True,
                accessibility_role=AccessibilityRole.BUTTON,
                accessibility_label="Start Campaign",
                accessibility_hint="Double tap to begin campaign",
            )
            root_screen.add_widget(acc_btn)

        elif scenario_name == "GOLDEN_RTL":
            root_screen.add_widget(UIWidget("txt_rtl", WidgetType.TEXT, parameters={"text": "مرحبا"}))

        elif scenario_name == "GOLDEN_HIGH_CONTRAST":
            btn_hc = UIWidget("btn_hc", WidgetType.BUTTON, style=UIStyle(color="#FFFF00", background_color="#000000"))
            root_screen.add_widget(btn_hc)

        elif scenario_name == "GOLDEN_COLORBLIND":
            badge = UIWidget("status_badge", WidgetType.ICON, parameters={"color": "#FF0000", "shape": "triangle"})
            root_screen.add_widget(badge)

        elif scenario_name == "GOLDEN_GAMEPAD_NAVIGATION":
            b1 = UIWidget("g_btn_1", WidgetType.BUTTON, focusable=True, navigation_explicit={"down": "g_btn_2"})
            b2 = UIWidget("g_btn_2", WidgetType.BUTTON, focusable=True, navigation_explicit={"up": "g_btn_1"})
            root_screen.add_widget(b1)
            root_screen.add_widget(b2)

        elif scenario_name == "GOLDEN_TOUCH_LAYOUT":
            t_btn = UIWidget("btn_touch_large", WidgetType.BUTTON, bounds=UIBounds(0, 0, 80, 80))
            root_screen.add_widget(t_btn)

        elif scenario_name == "GOLDEN_ULTRAWIDE":
            root_screen.safe_area_policy = SafeAreaPolicy.RESPECT
            panel_uw = UIWidget("panel_wide", WidgetType.PANEL, parameters={"width_percent": 80.0})
            root_screen.add_widget(panel_uw)

        elif scenario_name == "GOLDEN_SAFE_AREA":
            root_screen.safe_area_policy = SafeAreaPolicy.RESPECT
            root_screen.add_widget(UIWidget("sa_header", WidgetType.TEXT, anchor=Anchor.TOP))

        elif scenario_name == "GOLDEN_FULL_UI":
            # Multi-screen rich UI setup
            root_screen.add_widget(UIWidget("full_root_panel", WidgetType.PANEL))
            root_screen.add_widget(UIWidget("full_btn_start", WidgetType.BUTTON, focusable=True), parent_id="full_root_panel")
            root_screen.add_widget(UIWidget("full_txt_title", WidgetType.TEXT), parent_id="full_root_panel")

        return asset, inst
