from typing import Dict, List, Optional, Tuple
from ..templates.base_template import IAssetTemplate
from ..templates.sword_template import SwordTemplate
from ...spec_compiler.core.asset_spec import AssetSpec

class TemplateRegistry:
    def __init__(self):
        self.templates: Dict[str, IAssetTemplate] = {}
        # Registrar plantilla inicial obligatoria
        self.register_template(SwordTemplate())

    def register_template(self, template: IAssetTemplate):
        self.templates[template.template_id] = template

    def match_template(self, spec: AssetSpec) -> Tuple[Optional[IAssetTemplate], float]:
        best_t = None
        best_score = 0.0

        for t_id, t in self.templates.items():
            score = 0.0
            if spec.asset_type in t.supported_asset_types:
                score += 0.70
            if "blade" in spec.components and "guard" in spec.components:
                score += 0.30
            if score > best_score:
                best_score = score
                best_t = t

        if best_score >= 0.70:
            return best_t, round(best_score, 2)
        return None, 0.0
