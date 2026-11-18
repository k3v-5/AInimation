"""
ModularGrammarRule and ModularGrammar models.
UAF-81.12 Sections 16, 17, 18, 19, 20, 21.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ModularGrammarRule:
    rule_id: str
    condition: str          # e.g. "is_boundary"
    placement_action: str   # e.g. "place_wall"
    priority: int = 10

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "condition": self.condition,
            "placement_action": self.placement_action,
            "priority": self.priority,
        }


@dataclass
class ModularGrammar:
    grammar_id: str
    rules: List[ModularGrammarRule] = field(default_factory=list)

    def add_rule(self, rule: ModularGrammarRule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grammar_id": self.grammar_id,
            "rules": [r.to_dict() for r in self.rules],
        }

    @classmethod
    def create_standard_corridor_grammar(cls, grammar_id: str = "Grammar_Corridor") -> "ModularGrammar":
        grammar = cls(grammar_id=grammar_id)
        grammar.add_rule(ModularGrammarRule("R_Floor", "has_ground", "place_floor", priority=100))
        grammar.add_rule(ModularGrammarRule("R_Wall", "is_perimeter", "place_wall", priority=50))
        grammar.add_rule(ModularGrammarRule("R_Ceiling", "has_roof", "place_ceiling", priority=10))
        return grammar
