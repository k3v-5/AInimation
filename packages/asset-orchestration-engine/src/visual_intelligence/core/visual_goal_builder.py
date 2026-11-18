from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class VisualGoalSpec:
    category: str = "ONE_HANDED_MEDIEVAL_SWORD"
    required_components: List[str] = field(default_factory=lambda: ["blade", "guard", "grip", "pommel"])
    forbidden_components: List[str] = field(default_factory=list)
    target_proportions: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "blade_ratio": {"target": 0.72, "min": 0.65, "max": 0.78},
        "guard_ratio": {"target": 0.15, "min": 0.10, "max": 0.20}
    })
    target_materials: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "blade": {"metallic": 0.90, "roughness": 0.25},
        "grip": {"metallic": 0.0, "roughness": 0.75}
    })
    hard_constraints: List[str] = field(default_factory=lambda: ["is_one_handed", "has_blade", "has_guard"])
    soft_constraints: List[str] = field(default_factory=lambda: ["medium_wear", "medieval_style"])
    goal_locked: bool = True
    version: int = 1
