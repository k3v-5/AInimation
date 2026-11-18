"""
Universal Gameplay Models & Definitions for UAF-81.58.
Covers Gameplay State, Commands, Interaction Graph, Quests, Missions, Dialogue,
Inventory, Equipment, Crafting, Loot, Rewards, Progression, Skills, Abilities,
Status Effects, Economy, Factions, World Flags, Transactions, Diagnostics and State Hash.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple, Set
import math
from ...core.hashing.canonical_hasher import CanonicalHasher


# --- SECTION 5: ENTITY TYPES ---
class EntityType(Enum):
    PLAYER = "PLAYER"
    NPC = "NPC"
    CREATURE = "CREATURE"
    OBJECT = "OBJECT"
    VEHICLE = "VEHICLE"
    LOCATION = "LOCATION"
    FACTION = "FACTION"
    QUEST_GIVER = "QUEST_GIVER"
    MERCHANT = "MERCHANT"
    CUSTOM = "CUSTOM"


# --- SECTION 6, 7: GAMEPLAY TAGS ---
@dataclass(frozen=True)
class GameplayTag:
    tag: str

    def is_valid(self) -> bool:
        if not self.tag or "." not in self.tag:
            return False
        parts = self.tag.split(".")
        return all(len(p) > 0 and p.isalnum() or "_" in p for p in parts)


# --- SECTION 8, 9, 11: COMMANDS ---
class GameplayCommandType(Enum):
    INTERACT = "INTERACT"
    TALK = "TALK"
    ACCEPT_QUEST = "ACCEPT_QUEST"
    ABANDON_QUEST = "ABANDON_QUEST"
    COMPLETE_OBJECTIVE = "COMPLETE_OBJECTIVE"
    USE_ITEM = "USE_ITEM"
    EQUIP_ITEM = "EQUIP_ITEM"
    UNEQUIP_ITEM = "UNEQUIP_ITEM"
    DROP_ITEM = "DROP_ITEM"
    PICKUP_ITEM = "PICKUP_ITEM"
    BUY = "BUY"
    SELL = "SELL"
    CRAFT = "CRAFT"
    LEARN_SKILL = "LEARN_SKILL"
    USE_ABILITY = "USE_ABILITY"
    START_MISSION = "START_MISSION"
    COMPLETE_MISSION = "COMPLETE_MISSION"
    CUSTOM = "CUSTOM"


class CommandFailureCode(Enum):
    NONE = "NONE"
    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_TARGET = "INVALID_TARGET"
    CONDITION_FAILED = "CONDITION_FAILED"
    INSUFFICIENT_RESOURCE = "INSUFFICIENT_RESOURCE"
    INVENTORY_FULL = "INVENTORY_FULL"
    QUEST_NOT_AVAILABLE = "QUEST_NOT_AVAILABLE"
    QUEST_NOT_ACTIVE = "QUEST_NOT_ACTIVE"
    COOLDOWN_ACTIVE = "COOLDOWN_ACTIVE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    INVALID_STATE = "INVALID_STATE"


@dataclass
class GameplayCommand:
    command_id: str
    source: str
    target: str
    command_type: GameplayCommandType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class CommandResult:
    success: bool
    failure_code: CommandFailureCode = CommandFailureCode.NONE
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


# --- SECTION 12, 13, 14: INTERACTION GRAPH ---
class InteractionConditionType(Enum):
    HAS_ITEM = "HAS_ITEM"
    HAS_TAG = "HAS_TAG"
    HAS_SKILL = "HAS_SKILL"
    HAS_LEVEL = "HAS_LEVEL"
    HAS_REPUTATION = "HAS_REPUTATION"
    QUEST_ACTIVE = "QUEST_ACTIVE"
    QUEST_COMPLETED = "QUEST_COMPLETED"
    OBJECTIVE_COMPLETED = "OBJECTIVE_COMPLETED"
    WORLD_FLAG = "WORLD_FLAG"
    TIME = "TIME"
    WEATHER = "WEATHER"
    LOCATION = "LOCATION"
    FACTION = "FACTION"
    CUSTOM = "CUSTOM"


@dataclass
class InteractionCondition:
    condition_type: InteractionConditionType
    target_key: str
    expected_value: Any


class InteractionActionType(Enum):
    SET_FLAG = "SET_FLAG"
    CLEAR_FLAG = "CLEAR_FLAG"
    GIVE_ITEM = "GIVE_ITEM"
    REMOVE_ITEM = "REMOVE_ITEM"
    GIVE_CURRENCY = "GIVE_CURRENCY"
    REMOVE_CURRENCY = "REMOVE_CURRENCY"
    START_QUEST = "START_QUEST"
    COMPLETE_OBJECTIVE = "COMPLETE_OBJECTIVE"
    START_DIALOGUE = "START_DIALOGUE"
    CHANGE_REPUTATION = "CHANGE_REPUTATION"
    APPLY_EFFECT = "APPLY_EFFECT"
    REMOVE_EFFECT = "REMOVE_EFFECT"
    SPAWN_ENTITY = "SPAWN_ENTITY"
    DESPAWN_ENTITY = "DESPAWN_ENTITY"
    TRIGGER_EVENT = "TRIGGER_EVENT"


@dataclass
class InteractionAction:
    action_type: InteractionActionType
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionNode:
    node_id: str
    actor: str
    target: str
    conditions: List[InteractionCondition] = field(default_factory=list)
    actions: List[InteractionAction] = field(default_factory=list)


@dataclass
class InteractionGraph:
    nodes: Dict[str, InteractionNode] = field(default_factory=dict)


# --- SECTION 15-30: QUEST SYSTEM & OBJECTIVES ---
class QuestState(Enum):
    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    OFFERED = "OFFERED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"
    EXPIRED = "EXPIRED"


class ObjectiveType(Enum):
    KILL = "KILL"
    COLLECT = "COLLECT"
    INTERACT = "INTERACT"
    REACH_LOCATION = "REACH_LOCATION"
    TALK = "TALK"
    ESCORT = "ESCORT"
    SURVIVE = "SURVIVE"
    CRAFT = "CRAFT"
    DELIVER = "DELIVER"
    CUSTOM = "CUSTOM"


class ObjectiveState(Enum):
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    OPTIONAL_SKIPPED = "OPTIONAL_SKIPPED"


@dataclass
class QuestObjective:
    objective_id: str
    title: str
    objective_type: ObjectiveType
    target_id: str
    target_count: int = 1
    current_count: int = 0
    state: ObjectiveState = ObjectiveState.INACTIVE
    is_optional: bool = False

    def is_complete(self) -> bool:
        return self.current_count >= self.target_count


@dataclass
class QuestPrerequisite:
    min_level: int = 1
    required_quests: List[str] = field(default_factory=list)
    required_flags: List[str] = field(default_factory=list)


@dataclass
class RewardDefinition:
    xp: int = 0
    currency: int = 0
    items: List[Tuple[str, int]] = field(default_factory=list)  # (item_id, count)
    reputation: Dict[str, float] = field(default_factory=dict)  # faction_id -> delta


@dataclass
class QuestDefinition:
    quest_id: str
    title: str
    description: str
    giver: str
    prerequisites: QuestPrerequisite = field(default_factory=QuestPrerequisite)
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: RewardDefinition = field(default_factory=RewardDefinition)
    state: QuestState = QuestState.LOCKED
    failure_conditions: List[str] = field(default_factory=list)
    priority: int = 1
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "state": self.state.value,
            "objectives": [
                {
                    "id": o.objective_id,
                    "type": o.objective_type.value,
                    "count": o.current_count,
                    "target": o.target_count,
                    "state": o.state.value,
                }
                for o in self.objectives
            ],
            "reward_xp": self.rewards.xp,
            "reward_currency": self.rewards.currency,
        }


# --- SECTION 41-50: MISSIONS & CHECKPOINTS ---
class MissionState(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class MissionCheckpoint:
    checkpoint_id: str
    location: Tuple[float, float, float]
    is_reached: bool = False
    timestamp: float = 0.0


@dataclass
class MissionPhase:
    phase_id: str
    title: str
    objectives: List[QuestObjective] = field(default_factory=list)
    is_completed: bool = False


@dataclass
class MissionDefinition:
    mission_id: str
    title: str
    phases: List[MissionPhase] = field(default_factory=list)
    checkpoints: List[MissionCheckpoint] = field(default_factory=list)
    current_phase_index: int = 0
    state: MissionState = MissionState.NOT_STARTED


# --- SECTION 51-65: DIALOGUE SYSTEM ---
@dataclass
class DialogueChoice:
    choice_id: str
    text: str
    target_node_id: str
    conditions: List[InteractionCondition] = field(default_factory=list)
    actions: List[InteractionAction] = field(default_factory=list)


@dataclass
class DialogueNode:
    node_id: str
    speaker: str
    text: str
    choices: List[DialogueChoice] = field(default_factory=list)
    is_terminal: bool = False


@dataclass
class DialogueGraph:
    dialogue_id: str
    root_node_id: str
    nodes: Dict[str, DialogueNode] = field(default_factory=dict)


@dataclass
class DialogueHistoryRecord:
    dialogue_id: str
    node_id: str
    speaker: str
    choice_taken: Optional[str] = None
    timestamp: float = 0.0


# --- SECTION 66-95: ITEMS, INVENTORY & EQUIPMENT ---
class ItemRarity(Enum):
    COMMON = "COMMON"
    UNCOMMON = "UNCOMMON"
    RARE = "RARE"
    EPIC = "EPIC"
    LEGENDARY = "LEGENDARY"
    ARTIFACT = "ARTIFACT"
    UNIQUE = "UNIQUE"
    CUSTOM = "CUSTOM"


class ItemCategory(Enum):
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    CONSUMABLE = "CONSUMABLE"
    MATERIAL = "MATERIAL"
    QUEST = "QUEST"
    CURRENCY = "CURRENCY"
    AMMO = "AMMO"
    MISC = "MISC"
    CUSTOM = "CUSTOM"


class EquipmentSlot(Enum):
    MAIN_HAND = "MAIN_HAND"
    OFF_HAND = "OFF_HAND"
    HEAD = "HEAD"
    CHEST = "CHEST"
    LEGS = "LEGS"
    FEET = "FEET"
    HANDS = "HANDS"
    RING = "RING"
    AMULET = "AMULET"
    BACK = "BACK"
    NONE = "NONE"


class StatType(Enum):
    HEALTH = "HEALTH"
    STAMINA = "STAMINA"
    MANA = "MANA"
    DAMAGE = "DAMAGE"
    ARMOR = "ARMOR"
    CRIT_CHANCE = "CRIT_CHANCE"
    SPEED = "SPEED"
    RESISTANCE = "RESISTANCE"


@dataclass
class StatModifier:
    stat_type: StatType
    value: float
    is_percentage: bool = False


@dataclass
class ItemDefinition:
    item_id: str
    name: str
    description: str = ""
    category: ItemCategory = ItemCategory.MISC
    rarity: ItemRarity = ItemRarity.COMMON
    max_stack: int = 1
    weight: float = 0.5
    value: int = 10
    stat_modifiers: List[StatModifier] = field(default_factory=list)
    equipment_slot: EquipmentSlot = EquipmentSlot.NONE
    usable: bool = False


@dataclass
class ItemInstance:
    instance_id: str
    definition_id: str
    quantity: int = 1
    durability: float = 100.0
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InventorySlot:
    slot_index: int
    item: Optional[ItemInstance] = None


@dataclass
class Inventory:
    inventory_id: str
    owner_id: str
    max_slots: int = 30
    max_weight: float = 100.0
    items: List[ItemInstance] = field(default_factory=list)

    @property
    def current_weight(self) -> float:
        # Note: caller or engine resolves item weights, rough estimation default
        return sum(it.quantity * 1.0 for it in self.items)

    def is_full(self) -> bool:
        return len(self.items) >= self.max_slots


@dataclass
class EquipmentLoadout:
    slots: Dict[EquipmentSlot, Optional[ItemInstance]] = field(
        default_factory=lambda: {s: None for s in EquipmentSlot if s != EquipmentSlot.NONE}
    )


# --- SECTION 96-115: CRAFTING, LOOT & REWARDS ---
@dataclass
class RecipeIngredient:
    item_id: str
    quantity: int = 1


@dataclass
class CraftingRecipe:
    recipe_id: str
    name: str
    station: str = "WORKBENCH"
    ingredients: List[RecipeIngredient] = field(default_factory=list)
    results: List[RecipeIngredient] = field(default_factory=list)
    craft_time: float = 1.0
    unlocked: bool = True


@dataclass
class LootEntry:
    item_id: str
    weight: float = 1.0
    min_count: int = 1
    max_count: int = 1
    drop_chance: float = 1.0


@dataclass
class LootTable:
    table_id: str
    entries: List[LootEntry] = field(default_factory=list)
    roll_count: int = 1


# --- SECTION 116-140: PROGRESSION, SKILLS & ABILITIES ---
@dataclass
class SkillNode:
    skill_id: str
    name: str
    max_rank: int = 3
    current_rank: int = 0
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class SkillTree:
    tree_id: str
    name: str
    skills: Dict[str, SkillNode] = field(default_factory=dict)


@dataclass
class AbilityCost:
    resource_type: str = "MANA"
    amount: float = 10.0


@dataclass
class AbilityDefinition:
    ability_id: str
    name: str
    cooldown: float = 5.0
    current_cooldown: float = 0.0
    costs: List[AbilityCost] = field(default_factory=list)
    range_radius: float = 500.0
    effect_id: Optional[str] = None


@dataclass
class ProgressionProfile:
    entity_id: str
    current_level: int = 1
    current_xp: int = 0
    xp_for_next_level: int = 100
    skill_points: int = 0
    attribute_points: int = 0

    def add_xp(self, amount: int) -> bool:
        """Adds XP and returns True if leveled up."""
        leveled_up = False
        self.current_xp += amount
        while self.current_xp >= self.xp_for_next_level:
            self.current_xp -= self.xp_for_next_level
            self.current_level += 1
            self.skill_points += 1
            self.attribute_points += 2
            self.xp_for_next_level = int(self.xp_for_next_level * 1.5)
            leveled_up = True
        return leveled_up


# --- SECTION 141-160: STATUS EFFECTS & TRIGGERS ---
class EffectType(Enum):
    BUFF = "BUFF"
    DEBUFF = "DEBUFF"
    DAMAGE_OVER_TIME = "DAMAGE_OVER_TIME"
    HEAL_OVER_TIME = "HEAL_OVER_TIME"
    CROWD_CONTROL = "CROWD_CONTROL"
    STAT_BOOST = "STAT_BOOST"
    IMMUNITY = "IMMUNITY"
    CUSTOM = "CUSTOM"


@dataclass
class StatusEffectInstance:
    effect_id: str
    name: str
    effect_type: EffectType
    duration: float = 10.0
    remaining_duration: float = 10.0
    tick_interval: float = 1.0
    tick_timer: float = 0.0
    magnitude: float = 5.0

    def is_expired(self) -> bool:
        return self.remaining_duration <= 0.0


class TriggerType(Enum):
    ON_ENTER_AREA = "ON_ENTER_AREA"
    ON_EXIT_AREA = "ON_EXIT_AREA"
    ON_HEALTH_BELOW = "ON_HEALTH_BELOW"
    ON_INTERACTION = "ON_INTERACTION"
    ON_TIME = "ON_TIME"
    ON_CUSTOM = "ON_CUSTOM"


@dataclass
class GameplayTrigger:
    trigger_id: str
    trigger_type: TriggerType
    conditions: List[InteractionCondition] = field(default_factory=list)
    actions: List[InteractionAction] = field(default_factory=list)
    is_active: bool = True


# --- SECTION 161-175: ECONOMY & TRANSACTIONS ---
class CurrencyType(Enum):
    GOLD = "GOLD"
    SILVER = "SILVER"
    COPPER = "COPPER"
    GEMS = "GEMS"
    TOKENS = "TOKENS"
    FACTION_CREDITS = "FACTION_CREDITS"
    CUSTOM = "CUSTOM"


@dataclass
class Wallet:
    balances: Dict[CurrencyType, int] = field(default_factory=lambda: {CurrencyType.GOLD: 0})

    def get_balance(self, c_type: CurrencyType = CurrencyType.GOLD) -> int:
        return self.balances.get(c_type, 0)

    def add(self, amount: int, c_type: CurrencyType = CurrencyType.GOLD) -> None:
        self.balances[c_type] = self.balances.get(c_type, 0) + amount

    def spend(self, amount: int, c_type: CurrencyType = CurrencyType.GOLD) -> bool:
        cur = self.balances.get(c_type, 0)
        if cur >= amount:
            self.balances[c_type] = cur - amount
            return True
        return False


@dataclass
class MerchantDefinition:
    merchant_id: str
    name: str
    inventory: Inventory
    wallet: Wallet = field(default_factory=Wallet)
    buy_multiplier: float = 1.0
    sell_multiplier: float = 0.5


class TransactionType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    REWARD = "REWARD"
    CRAFT = "CRAFT"
    DROP = "DROP"
    LOOT = "LOOT"
    TRANSFER = "TRANSFER"


@dataclass
class TransactionRecord:
    transaction_id: str
    transaction_type: TransactionType
    source: str
    target: str
    amount: int = 0
    currency: CurrencyType = CurrencyType.GOLD
    item_id: Optional[str] = None
    item_count: int = 0
    timestamp: float = 0.0


# --- SECTION 176-185: FACTIONS & REPUTATION ---
class FactionReputationTier(Enum):
    HATED = "HATED"
    HOSTILE = "HOSTILE"
    UNFRIENDLY = "UNFRIENDLY"
    NEUTRAL = "NEUTRAL"
    FRIENDLY = "FRIENDLY"
    HONORED = "HONORED"
    EXALTED = "EXALTED"


@dataclass
class FactionReputation:
    faction_id: str
    score: float = 0.0  # -1000..1000

    @property
    def tier(self) -> FactionReputationTier:
        if self.score <= -500:
            return FactionReputationTier.HATED
        elif self.score <= -200:
            return FactionReputationTier.HOSTILE
        elif self.score < 0:
            return FactionReputationTier.UNFRIENDLY
        elif self.score < 200:
            return FactionReputationTier.NEUTRAL
        elif self.score < 500:
            return FactionReputationTier.FRIENDLY
        elif self.score < 800:
            return FactionReputationTier.HONORED
        else:
            return FactionReputationTier.EXALTED


# --- SECTION 186-191: WORLD FLAGS & UNLOCKS ---
@dataclass
class WorldFlag:
    flag_id: str
    value: Any = True
    is_set: bool = True


@dataclass
class WorldUnlock:
    unlock_id: str
    required_flags: List[str] = field(default_factory=list)
    unlocked_content: str = ""
    is_unlocked: bool = False


# --- SECTION 4, 5, 201, 203: COMPLETE GAMEPLAY ENTITY & STATE ---
@dataclass
class GameplayEntity:
    entity_id: str
    entity_type: EntityType = EntityType.NPC
    tags: List[GameplayTag] = field(default_factory=list)
    health: float = 100.0
    max_health: float = 100.0
    wallet: Wallet = field(default_factory=Wallet)
    inventory: Inventory = field(default_factory=lambda: Inventory("INV_DEFAULT", "OWNER_DEFAULT"))
    equipment: EquipmentLoadout = field(default_factory=EquipmentLoadout)
    progression: ProgressionProfile = field(default_factory=lambda: ProgressionProfile("DEFAULT"))
    active_effects: List[StatusEffectInstance] = field(default_factory=list)

    def is_alive(self) -> bool:
        return self.health > 0.0


@dataclass
class GameplayDiagnosticReport:
    active_quests: int = 0
    active_missions: int = 0
    inventory_count: int = 0
    transaction_count: int = 0
    economy_operations: int = 0
    dialogue_sessions: int = 0
    effect_count: int = 0
    event_count: int = 0
    failed_commands: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class GameplaySaveState:
    save_id: str
    state_id: str
    seed: int
    current_tick: int
    serialized_entities: List[Dict[str, Any]] = field(default_factory=list)
    serialized_quests: List[Dict[str, Any]] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    state_hash: str = ""
    timestamp: float = 0.0
    schema_version: str = "1.0.0"


@dataclass
class GameplayState:
    state_id: str
    seed: int = 98765
    entities: Dict[str, GameplayEntity] = field(default_factory=dict)
    quests: Dict[str, QuestDefinition] = field(default_factory=dict)
    missions: Dict[str, MissionDefinition] = field(default_factory=dict)
    dialogues: Dict[str, DialogueGraph] = field(default_factory=dict)
    items: Dict[str, ItemDefinition] = field(default_factory=dict)
    crafting_recipes: Dict[str, CraftingRecipe] = field(default_factory=dict)
    loot_tables: Dict[str, LootTable] = field(default_factory=dict)
    merchants: Dict[str, MerchantDefinition] = field(default_factory=dict)
    skill_trees: Dict[str, SkillTree] = field(default_factory=dict)
    abilities: Dict[str, AbilityDefinition] = field(default_factory=dict)
    triggers: Dict[str, GameplayTrigger] = field(default_factory=dict)
    factions: Dict[str, FactionReputation] = field(default_factory=dict)
    world_flags: Dict[str, Any] = field(default_factory=dict)
    world_unlocks: Dict[str, WorldUnlock] = field(default_factory=dict)
    transactions: List[TransactionRecord] = field(default_factory=list)
    current_tick: int = 0
    simulation_version: str = "1.0.0"

    @property
    def gameplay_state_hash(self) -> str:
        payload = {
            "state_id": self.state_id,
            "seed": self.seed,
            "entity_count": len(self.entities),
            "quest_count": len(self.quests),
            "mission_count": len(self.missions),
            "item_count": len(self.items),
            "flag_count": len(self.world_flags),
            "transaction_count": len(self.transactions),
            "current_tick": self.current_tick,
            "simulation_version": self.simulation_version,
        }
        return CanonicalHasher.compute_hash(payload)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "seed": self.seed,
            "entity_count": len(self.entities),
            "quest_count": len(self.quests),
            "mission_count": len(self.missions),
            "current_tick": self.current_tick,
            "gameplay_state_hash": self.gameplay_state_hash,
        }
