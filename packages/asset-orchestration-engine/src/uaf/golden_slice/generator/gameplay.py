"""Combat rules, inventory, quest objectives, and gameplay interaction generator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.golden_slice.manifest.models import GameplayConfig
from uaf.golden_slice.manifest.seeds import SeedManager


@dataclass
class CombatAction:
    action_name: str
    base_damage: float
    stamina_cost: float
    cooldown_s: float
    damage_type: str = "Physical"  # Physical, Fire, Electric
    can_crit: bool = True
    crit_multiplier: float = 1.5


@dataclass
class InventoryItem:
    item_id: str
    name: str
    item_type: str  # "Weapon", "Potion", "Armor", "Key"
    quantity: int = 1
    max_stack: int = 99
    is_equipped: bool = False


@dataclass
class ObjectiveState:
    objective_id: str
    title: str
    target_score: int = 100
    current_score: int = 0
    is_completed: bool = False

    def progress(self, amount: int = 25) -> None:
        self.current_score = min(self.target_score, self.current_score + amount)
        if self.current_score >= self.target_score:
            self.is_completed = True


@dataclass
class GameplaySlice:
    actions: Dict[str, CombatAction] = field(default_factory=dict)
    initial_inventory: List[InventoryItem] = field(default_factory=list)
    objective: ObjectiveState = field(default_factory=lambda: ObjectiveState("obj_main", "Capture Fortress Point"))

    def compute_damage(
        self,
        action_name: str,
        attacker_base: float,
        is_critical: bool = False,
        is_blocked: bool = False,
    ) -> float:
        action = self.actions.get(action_name)
        base = (action.base_damage if action else 10.0) + attacker_base
        if is_critical and (action is None or action.can_crit):
            mult = action.crit_multiplier if action else 1.5
            base *= mult
        if is_blocked:
            base *= 0.3  # 70% damage reduction on block
        return max(1.0, round(base, 1))


class GameplayGenerator:
    """Generates deterministic gameplay combat actions, items, and objectives."""

    def __init__(self, config: GameplayConfig, seeds: SeedManager) -> None:
        self.config = config
        self.rng = seeds.get_rng("gameplay")

    def generate(self) -> GameplaySlice:
        actions = {
            "light_attack": CombatAction("light_attack", base_damage=20.0, stamina_cost=10.0, cooldown_s=0.3),
            "heavy_attack": CombatAction("heavy_attack", base_damage=45.0, stamina_cost=25.0, cooldown_s=0.9),
            "whirlwind_ability": CombatAction("whirlwind_ability", base_damage=60.0, stamina_cost=40.0, cooldown_s=4.0),
        }

        inventory = [
            InventoryItem("item_sword_01", "Steel Longsword", "Weapon", quantity=1, is_equipped=True),
            InventoryItem("item_shield_01", "Knight's Heater Shield", "Armor", quantity=1, is_equipped=True),
            InventoryItem("item_health_potion", "Healing Elixir", "Potion", quantity=3),
        ]

        objective = ObjectiveState(
            objective_id="obj_capture_core",
            title="Capture Outpost Command Node",
            target_score=100,
        )

        return GameplaySlice(actions=actions, initial_inventory=inventory, objective=objective)
