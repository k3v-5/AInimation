"""Declarative scenario definitions and execution step structures."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ScenarioStep:
    step_id: str
    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_outcome: str = "SUCCESS"


@dataclass
class ScenarioDefinition:
    scenario_id: str
    name: str
    description: str
    steps: List[ScenarioStep] = field(default_factory=list)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "name": self.name,
            "description": self.description,
            "step_count": self.step_count,
            "steps": [vars(s) for s in self.steps],
        }
