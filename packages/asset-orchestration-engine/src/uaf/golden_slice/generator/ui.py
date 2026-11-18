"""HUD widgets, menu screens, and accessibility configuration generator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AccessibilitySettings:
    high_contrast: bool = True
    ui_scale: float = 1.0
    colorblind_filter: str = "Deuteranopia"  # None, Protanopia, Deuteranopia, Tritanopia
    input_remapping_enabled: bool = True
    subtitles_enabled: bool = True
    subtitle_font_size: int = 18
    text_readability_mode: bool = True


@dataclass
class UISlice:
    hud_widgets: List[str] = field(default_factory=lambda: [
        "health_bar",
        "stamina_bar",
        "ability_cooldowns",
        "resource_counter",
        "objective_tracker",
        "interaction_prompt",
        "enemy_health_bar",
        "pause_menu",
    ])
    accessibility: AccessibilitySettings = field(default_factory=AccessibilitySettings)

    def validate(self) -> List[str]:
        errors: List[str] = []
        required_widgets = [
            "health_bar",
            "stamina_bar",
            "ability_cooldowns",
            "objective_tracker",
            "interaction_prompt",
            "enemy_health_bar",
            "pause_menu",
        ]
        for w in required_widgets:
            if w not in self.hud_widgets:
                errors.append(f"Missing required HUD widget '{w}'")
        return errors


class UIGenerator:
    """Generates complete HUD layout and accessibility configuration."""

    def generate(self) -> UISlice:
        return UISlice()
