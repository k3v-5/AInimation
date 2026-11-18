from typing import Dict, List, Any, Optional
from ..core.critic_schema import CriticDiagnosis, CriticConfiguration
from .base_rule import ICriticRule
from .causal_rules import ProportionCausalRule, TopologyCausalRule
from .historical_rules import HistoricalOscillationRule

class CriticRuleRegistry:
    def __init__(self):
        self._rules: Dict[str, ICriticRule] = {}
        self._register_defaults()

    def _register_defaults(self):
        self.register(ProportionCausalRule())
        self.register(TopologyCausalRule())
        self.register(HistoricalOscillationRule())

    def register(self, rule: ICriticRule):
        self._rules[rule.rule_id] = rule

    def get(self, rule_id: str) -> Optional[ICriticRule]:
        return self._rules.get(rule_id)

    def evaluate_all(
        self,
        context: Dict[str, Any],
        config: CriticConfiguration
    ) -> List[CriticDiagnosis]:
        all_diagnoses: List[CriticDiagnosis] = []
        for rule in self._rules.values():
            diag_list = rule.evaluate(context, config)
            all_diagnoses.extend(diag_list)
        return all_diagnoses
