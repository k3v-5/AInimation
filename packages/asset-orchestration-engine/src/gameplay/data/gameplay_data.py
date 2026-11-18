from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class WeaponData:
    damage: float = 25.0
    attack_speed: float = 1.2
    range_cm: float = 150.0
    damage_type: str = "physical"

@dataclass
class ActorGameplayData:
    actor_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    instance_overrides: Dict[str, Any] = field(default_factory=dict)

    def get_effective(self, attr_name: str, default: Any = None) -> Any:
        if attr_name in self.instance_overrides:
            return self.instance_overrides[attr_name]
        return self.attributes.get(attr_name, default)
