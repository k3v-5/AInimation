from typing import Dict, Optional
from ..core.library_schema import PresetDefinition

class PresetRegistry:
    def __init__(self):
        self.presets: Dict[str, PresetDefinition] = {}
        self._init_defaults()

    def register_preset(self, preset: PresetDefinition):
        self.presets[preset.preset_id] = preset

    def get_preset(self, preset_id: str) -> Optional[PresetDefinition]:
        return self.presets.get(preset_id)

    def _init_defaults(self):
        self.register_preset(PresetDefinition(
            preset_id="ShortSword",
            template_id="weapon.sword.standard",
            parameter_overrides={"blade_length": 0.65, "handle_length": 0.18, "guard_width": 0.14}
        ))
        self.register_preset(PresetDefinition(
            preset_id="StandardSword",
            template_id="weapon.sword.standard",
            parameter_overrides={"blade_length": 0.90, "handle_length": 0.22, "guard_width": 0.18}
        ))
        self.register_preset(PresetDefinition(
            preset_id="HeavySword",
            template_id="weapon.sword.standard",
            parameter_overrides={"blade_length": 1.05, "blade_width": 0.08, "blade_thickness": 0.03, "handle_length": 0.28, "guard_width": 0.24}
        ))
