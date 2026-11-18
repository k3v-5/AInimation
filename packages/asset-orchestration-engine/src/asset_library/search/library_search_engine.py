from typing import List, Dict, Any
from ..components.component_registry import ComponentRegistry
from ..templates.variant_registry import VariantRegistry
from ..templates.preset_registry import PresetRegistry

class LibrarySearchEngine:
    def __init__(
        self,
        comp_registry: ComponentRegistry,
        variant_registry: VariantRegistry,
        preset_registry: PresetRegistry
    ):
        self.comp_registry = comp_registry
        self.variant_registry = variant_registry
        self.preset_registry = preset_registry

    def search(self, query: str) -> Dict[str, List[str]]:
        q = query.lower()
        res = {"templates": [], "variants": [], "presets": [], "components": []}

        if "sword" in q or "espada" in q:
            res["templates"].append("weapon.sword.standard")
        if "medieval" in q:
            res["variants"].append("Medieval")
        if "heavy" in q or "pesada" in q:
            res["variants"].append("Heavy")
            res["presets"].append("HeavySword")
        if "short" in q or "corta" in q:
            res["presets"].append("ShortSword")

        for comp_id in self.comp_registry.components:
            if q in comp_id:
                res["components"].append(comp_id)

        return res
