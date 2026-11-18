from typing import Dict, List, Any, Optional, Tuple
from ..core.qa_schema import GeometricDefect, GeometryValidationConfiguration
from .base_rule import IGeometryValidationRule
from .topology_rules import TopologyValidationRule
from .transform_dimension_rules import TransformDimensionRule
from .normal_rules import NormalValidationRule
from .density_budget_rules import DensityBudgetRule
from .collision_lod_rules import CollisionLODRule

class GeometryValidationRegistry:
    def __init__(self):
        self._rules: Dict[str, IGeometryValidationRule] = {}
        self._register_default_rules()

    def _register_default_rules(self):
        self.register(TopologyValidationRule())
        self.register(TransformDimensionRule())
        self.register(NormalValidationRule())
        self.register(DensityBudgetRule())
        self.register(CollisionLODRule())

    def register(self, rule: IGeometryValidationRule):
        self._rules[rule.rule_id] = rule

    def get(self, rule_id: str) -> Optional[IGeometryValidationRule]:
        return self._rules.get(rule_id)

    def evaluate_all(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[Dict[str, float], List[GeometricDefect]]:
        scores: Dict[str, float] = {}
        all_defects: List[GeometricDefect] = []

        for rule in self._rules.values():
            s, defs = rule.validate(geometry_data, context, config)
            scores[rule.rule_id] = round(s, 4)
            all_defects.extend(defs)

        return scores, all_defects
