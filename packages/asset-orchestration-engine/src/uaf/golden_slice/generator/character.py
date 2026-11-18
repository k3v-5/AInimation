"""Player and enemy character archetype generator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from uaf.golden_slice.manifest.models import PlayerConfig, EnemyConfig
from uaf.golden_slice.manifest.seeds import SeedManager


@dataclass
class CharacterProfile:
    character_id: str
    name: str
    archetype: str  # "player", "scout", "melee", "heavy", "ranged"
    health: float
    stamina: float
    walk_speed: float
    run_speed: float
    attack_damage: float
    attack_range: float
    attack_cooldown_s: float
    skeleton_id: str
    animations: List[str] = field(default_factory=lambda: ["idle", "walk", "run", "attack", "hit", "death"])
    has_control_rig: bool = True
    has_animbp: bool = True


@dataclass
class CharacterSlice:
    player: CharacterProfile
    enemies: Dict[str, CharacterProfile] = field(default_factory=dict)

    def get_all(self) -> List[CharacterProfile]:
        return [self.player] + list(self.enemies.values())


class CharacterGenerator:
    """Generates player character and differentiated enemy archetypes."""

    def __init__(self, player_cfg: PlayerConfig, enemy_cfg: EnemyConfig, seeds: SeedManager) -> None:
        self.player_cfg = player_cfg
        self.enemy_cfg = enemy_cfg
        self.rng = seeds.get_rng("character")

    def generate(self) -> CharacterSlice:
        player = CharacterProfile(
            character_id="hero_player_01",
            name="GoldenHero",
            archetype=self.player_cfg.archetype,
            health=self.player_cfg.max_health,
            stamina=self.player_cfg.max_stamina,
            walk_speed=self.player_cfg.walk_speed,
            run_speed=self.player_cfg.sprint_speed,
            attack_damage=35.0,
            attack_range=200.0,
            attack_cooldown_s=0.6,
            skeleton_id="SKEL_Humanoid_Master",
        )

        enemies: Dict[str, CharacterProfile] = {
            "scout": CharacterProfile(
                character_id="enemy_scout",
                name="Forest Scout",
                archetype="scout",
                health=45.0,
                stamina=60.0,
                walk_speed=350.0,
                run_speed=700.0,
                attack_damage=15.0,
                attack_range=150.0,
                attack_cooldown_s=0.4,
                skeleton_id="SKEL_Humanoid_Master",
            ),
            "melee": CharacterProfile(
                character_id="enemy_melee",
                name="Foot Soldier",
                archetype="melee",
                health=100.0,
                stamina=80.0,
                walk_speed=250.0,
                run_speed=500.0,
                attack_damage=28.0,
                attack_range=180.0,
                attack_cooldown_s=0.8,
                skeleton_id="SKEL_Humanoid_Master",
            ),
            "heavy": CharacterProfile(
                character_id="enemy_heavy",
                name="Iron Juggernaut",
                archetype="heavy",
                health=250.0,
                stamina=120.0,
                walk_speed=180.0,
                run_speed=350.0,
                attack_damage=60.0,
                attack_range=220.0,
                attack_cooldown_s=1.5,
                skeleton_id="SKEL_Humanoid_Heavy",
            ),
            "ranged": CharacterProfile(
                character_id="enemy_ranged",
                name="Sharpshooter",
                archetype="ranged",
                health=50.0,
                stamina=50.0,
                walk_speed=260.0,
                run_speed=520.0,
                attack_damage=22.0,
                attack_range=1200.0,
                attack_cooldown_s=1.1,
                skeleton_id="SKEL_Humanoid_Master",
            ),
        }

        return CharacterSlice(player=player, enemies=enemies)
