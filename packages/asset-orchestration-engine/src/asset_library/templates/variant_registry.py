from typing import Dict, Optional
from ..core.library_schema import VariantDefinition

class VariantRegistry:
    def __init__(self):
        self.variants: Dict[str, VariantDefinition] = {}
        self._init_defaults()

    def register_variant(self, variant: VariantDefinition):
        self.variants[variant.variant_id] = variant

    def get_variant(self, variant_id: str) -> Optional[VariantDefinition]:
        return self.variants.get(variant_id)

    def _init_defaults(self):
        self.register_variant(VariantDefinition(
            variant_id="Medieval",
            template_id="weapon.sword.standard",
            component_selection={"blade": "blade_standard", "guard": "guard_cross", "handle": "handle_leather", "pommel": "pommel_round"},
            parameter_overrides={"blade_length": 0.90, "guard_width": 0.18},
            style_rules={"realism": "STYLIZED"}
        ))
        self.register_variant(VariantDefinition(
            variant_id="Heavy",
            template_id="weapon.sword.standard",
            component_selection={"blade": "blade_broad", "guard": "guard_cross", "handle": "handle_wood", "pommel": "pommel_round"},
            parameter_overrides={"blade_length": 0.85, "blade_width": 0.08, "guard_width": 0.22},
            style_rules={"realism": "REALISTIC"}
        ))
