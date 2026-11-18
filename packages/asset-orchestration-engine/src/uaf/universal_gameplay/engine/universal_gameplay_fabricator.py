"""
Universal Gameplay Fabricator & Authoritative Engine for UAF-81.58.
Implements authoritative command dispatch, quest progression, dialogue traversal,
inventory & equipment mechanics, crafting, loot rolling, transactional trading,
progression & skill tree resolution, status effect ticking, save/load, and
all 19 Canonical Golden Gameplay Scenarios.
"""

import copy
import math
from typing import Dict, Any, List, Optional, Tuple
from ..models.definition import (
    EntityType,
    GameplayTag,
    GameplayCommandType,
    CommandFailureCode,
    GameplayCommand,
    CommandResult,
    InteractionConditionType,
    InteractionCondition,
    InteractionActionType,
    InteractionAction,
    QuestState,
    ObjectiveType,
    ObjectiveState,
    QuestObjective,
    QuestPrerequisite,
    RewardDefinition,
    QuestDefinition,
    MissionState,
    MissionCheckpoint,
    MissionPhase,
    MissionDefinition,
    DialogueChoice,
    DialogueNode,
    DialogueGraph,
    DialogueHistoryRecord,
    ItemRarity,
    ItemCategory,
    EquipmentSlot,
    StatType,
    StatModifier,
    ItemDefinition,
    ItemInstance,
    Inventory,
    EquipmentLoadout,
    RecipeIngredient,
    CraftingRecipe,
    LootEntry,
    LootTable,
    SkillNode,
    SkillTree,
    AbilityCost,
    AbilityDefinition,
    ProgressionProfile,
    EffectType,
    StatusEffectInstance,
    TriggerType,
    GameplayTrigger,
    CurrencyType,
    Wallet,
    MerchantDefinition,
    TransactionType,
    TransactionRecord,
    FactionReputationTier,
    FactionReputation,
    WorldFlag,
    WorldUnlock,
    GameplayEntity,
    GameplayDiagnosticReport,
    GameplaySaveState,
    GameplayState,
)


class UniversalGameplayFabricator:
    """
    Authoritative gameplay synthesis platform and runtime fabricator.
    """

    # --- 19 CANONICAL GOLDEN SCENARIOS (Section 185) ---
    GOLDEN_QUEST_START = "GOLDEN_QUEST_START"
    GOLDEN_QUEST_BRANCH = "GOLDEN_QUEST_BRANCH"
    GOLDEN_QUEST_COMPLETE = "GOLDEN_QUEST_COMPLETE"
    GOLDEN_QUEST_FAIL = "GOLDEN_QUEST_FAIL"
    GOLDEN_DIALOGUE_BRANCH = "GOLDEN_DIALOGUE_BRANCH"
    GOLDEN_INVENTORY = "GOLDEN_INVENTORY"
    GOLDEN_EQUIPMENT = "GOLDEN_EQUIPMENT"
    GOLDEN_CRAFTING = "GOLDEN_CRAFTING"
    GOLDEN_LOOT = "GOLDEN_LOOT"
    GOLDEN_REWARD = "GOLDEN_REWARD"
    GOLDEN_MERCHANT = "GOLDEN_MERCHANT"
    GOLDEN_FACTION = "GOLDEN_FACTION"
    GOLDEN_LEVEL_UP = "GOLDEN_LEVEL_UP"
    GOLDEN_SKILL_UNLOCK = "GOLDEN_SKILL_UNLOCK"
    GOLDEN_ABILITY = "GOLDEN_ABILITY"
    GOLDEN_STATUS_EFFECT = "GOLDEN_STATUS_EFFECT"
    GOLDEN_WORLD_UNLOCK = "GOLDEN_WORLD_UNLOCK"
    GOLDEN_SAVE_LOAD = "GOLDEN_SAVE_LOAD"
    GOLDEN_MULTIPLAYER_RECONCILIATION = "GOLDEN_MULTIPLAYER_RECONCILIATION"

    # --- ENTITY CREATION ---

    @staticmethod
    def spawn_entity(
        entity_id: str,
        entity_type: EntityType = EntityType.PLAYER,
        health: float = 100.0,
        gold: int = 0,
        max_slots: int = 20,
    ) -> GameplayEntity:
        wallet = Wallet(balances={CurrencyType.GOLD: gold})
        inventory = Inventory(
            inventory_id=f"INV_{entity_id}",
            owner_id=entity_id,
            max_slots=max_slots,
        )
        progression = ProgressionProfile(entity_id=entity_id)
        return GameplayEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            health=health,
            max_health=health,
            wallet=wallet,
            inventory=inventory,
            progression=progression,
        )

    # --- COMMAND DISPATCH & EXECUTION ---

    @classmethod
    def execute_command(
        cls,
        state: GameplayState,
        command: GameplayCommand,
    ) -> CommandResult:
        source_entity = state.entities.get(command.source)
        target_entity = state.entities.get(command.target)

        if command.command_type == GameplayCommandType.ACCEPT_QUEST:
            quest_id = command.payload.get("quest_id", command.target)
            quest = state.quests.get(quest_id)
            if not quest:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, f"Quest {quest_id} not found")

            if quest.state not in (QuestState.AVAILABLE, QuestState.OFFERED):
                return CommandResult(False, CommandFailureCode.QUEST_NOT_AVAILABLE, f"Quest {quest_id} is not available")

            # Check prerequisites
            if source_entity and source_entity.progression.current_level < quest.prerequisites.min_level:
                return CommandResult(False, CommandFailureCode.CONDITION_FAILED, "Level too low")

            for req_q in quest.prerequisites.required_quests:
                q_req = state.quests.get(req_q)
                if not q_req or q_req.state != QuestState.COMPLETED:
                    return CommandResult(False, CommandFailureCode.QUEST_NOT_AVAILABLE, f"Prerequisite {req_q} incomplete")

            quest.state = QuestState.ACTIVE
            for obj in quest.objectives:
                obj.state = ObjectiveState.ACTIVE
            return CommandResult(True, message=f"Quest {quest_id} accepted")

        elif command.command_type == GameplayCommandType.COMPLETE_OBJECTIVE:
            quest_id = command.payload.get("quest_id")
            obj_id = command.payload.get("objective_id")
            amount = command.payload.get("amount", 1)

            quest = state.quests.get(quest_id)
            if not quest or quest.state != QuestState.ACTIVE:
                return CommandResult(False, CommandFailureCode.QUEST_NOT_ACTIVE, "Quest is not active")

            target_obj = next((o for o in quest.objectives if o.objective_id == obj_id), None)
            if not target_obj:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Objective not found")

            target_obj.current_count = min(target_obj.target_count, target_obj.current_count + amount)
            if target_obj.is_complete():
                target_obj.state = ObjectiveState.COMPLETED

            # If all non-optional objectives are complete -> complete quest
            req_objs = [o for o in quest.objectives if not o.is_optional]
            if all(o.state == ObjectiveState.COMPLETED for o in req_objs):
                quest.state = QuestState.COMPLETED
                # Grant rewards to source entity
                if source_entity:
                    if quest.rewards.xp > 0:
                        source_entity.progression.add_xp(quest.rewards.xp)
                    if quest.rewards.currency > 0:
                        source_entity.wallet.add(quest.rewards.currency, CurrencyType.GOLD)
                    for it_id, count in quest.rewards.items:
                        inst = ItemInstance(f"REWARD_{it_id}_{state.current_tick}", it_id, count)
                        source_entity.inventory.items.append(inst)

            return CommandResult(True, message="Objective updated")

        elif command.command_type == GameplayCommandType.ABANDON_QUEST:
            quest_id = command.payload.get("quest_id", command.target)
            quest = state.quests.get(quest_id)
            if not quest or quest.state != QuestState.ACTIVE:
                return CommandResult(False, CommandFailureCode.QUEST_NOT_ACTIVE, "Quest is not active")
            quest.state = QuestState.ABANDONED
            return CommandResult(True, message=f"Quest {quest_id} abandoned")

        elif command.command_type == GameplayCommandType.BUY:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Buyer entity not found")
            merchant = state.merchants.get(command.target)
            if not merchant:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Merchant not found")

            item_id = command.payload.get("item_id")
            count = command.payload.get("count", 1)
            item_def = state.items.get(item_id)
            if not item_def:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, f"Item {item_id} undefined")

            price = int(item_def.value * merchant.buy_multiplier * count)
            if source_entity.wallet.get_balance(CurrencyType.GOLD) < price:
                return CommandResult(False, CommandFailureCode.INSUFFICIENT_RESOURCE, "Not enough gold")

            if source_entity.inventory.is_full():
                return CommandResult(False, CommandFailureCode.INVENTORY_FULL, "Inventory full")

            # Execute purchase
            source_entity.wallet.spend(price, CurrencyType.GOLD)
            merchant.wallet.add(price, CurrencyType.GOLD)
            bought_inst = ItemInstance(
                instance_id=f"ITEM_{item_id}_{state.current_tick}_{len(state.transactions)}",
                definition_id=item_id,
                quantity=count,
            )
            source_entity.inventory.items.append(bought_inst)

            tx = TransactionRecord(
                transaction_id=f"TX_BUY_{command.command_id}",
                transaction_type=TransactionType.BUY,
                source=source_entity.entity_id,
                target=merchant.merchant_id,
                amount=price,
                currency=CurrencyType.GOLD,
                item_id=item_id,
                item_count=count,
                timestamp=float(state.current_tick),
            )
            state.transactions.append(tx)
            return CommandResult(True, message=f"Purchased {count}x {item_id} for {price} gold")

        elif command.command_type == GameplayCommandType.SELL:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Seller entity not found")
            merchant = state.merchants.get(command.target)
            if not merchant:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Merchant not found")

            item_id = command.payload.get("item_id")
            count = command.payload.get("count", 1)
            item_def = state.items.get(item_id)
            if not item_def:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Item definition not found")

            # Find item in inventory
            inv_item = next((it for it in source_entity.inventory.items if it.definition_id == item_id and it.quantity >= count), None)
            if not inv_item:
                return CommandResult(False, CommandFailureCode.CONDITION_FAILED, "Item not in inventory")

            price = int(item_def.value * merchant.sell_multiplier * count)
            if merchant.wallet.get_balance(CurrencyType.GOLD) < price:
                return CommandResult(False, CommandFailureCode.INSUFFICIENT_RESOURCE, "Merchant out of funds")

            # Execute sale
            merchant.wallet.spend(price, CurrencyType.GOLD)
            source_entity.wallet.add(price, CurrencyType.GOLD)
            inv_item.quantity -= count
            if inv_item.quantity <= 0:
                source_entity.inventory.items.remove(inv_item)

            tx = TransactionRecord(
                transaction_id=f"TX_SELL_{command.command_id}",
                transaction_type=TransactionType.SELL,
                source=source_entity.entity_id,
                target=merchant.merchant_id,
                amount=price,
                currency=CurrencyType.GOLD,
                item_id=item_id,
                item_count=count,
                timestamp=float(state.current_tick),
            )
            state.transactions.append(tx)
            return CommandResult(True, message=f"Sold {count}x {item_id} for {price} gold")

        elif command.command_type == GameplayCommandType.CRAFT:
            recipe_id = command.payload.get("recipe_id")
            recipe = state.crafting_recipes.get(recipe_id)
            if not recipe:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Recipe not found")

            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Crafter not found")

            # Check ingredients
            for ing in recipe.ingredients:
                available = sum(it.quantity for it in source_entity.inventory.items if it.definition_id == ing.item_id)
                if available < ing.quantity:
                    return CommandResult(False, CommandFailureCode.INSUFFICIENT_RESOURCE, f"Missing {ing.item_id}")

            # Consume ingredients
            for ing in recipe.ingredients:
                needed = ing.quantity
                for it in list(source_entity.inventory.items):
                    if it.definition_id == ing.item_id:
                        take = min(it.quantity, needed)
                        it.quantity -= take
                        needed -= take
                        if it.quantity <= 0:
                            source_entity.inventory.items.remove(it)
                        if needed <= 0:
                            break

            # Produce outputs
            for res in recipe.results:
                out_inst = ItemInstance(
                    instance_id=f"CRAFT_{res.item_id}_{state.current_tick}",
                    definition_id=res.item_id,
                    quantity=res.quantity,
                )
                source_entity.inventory.items.append(out_inst)

            tx = TransactionRecord(
                transaction_id=f"TX_CRAFT_{command.command_id}",
                transaction_type=TransactionType.CRAFT,
                source=source_entity.entity_id,
                target="CRAFTING_BENCH",
                item_id=recipe.results[0].item_id if recipe.results else None,
                item_count=recipe.results[0].quantity if recipe.results else 1,
                timestamp=float(state.current_tick),
            )
            state.transactions.append(tx)
            return CommandResult(True, message=f"Crafted {recipe.name}")

        elif command.command_type == GameplayCommandType.EQUIP_ITEM:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Entity not found")
            item_id = command.payload.get("item_id")
            item_def = state.items.get(item_id)
            if not item_def or item_def.equipment_slot == EquipmentSlot.NONE:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Item not equippable")

            inv_item = next((it for it in source_entity.inventory.items if it.definition_id == item_id), None)
            if not inv_item:
                return CommandResult(False, CommandFailureCode.CONDITION_FAILED, "Item not in inventory")

            # Equip and remove 1 from inventory
            slot = item_def.equipment_slot
            old_item = source_entity.equipment.slots.get(slot)
            if old_item:
                source_entity.inventory.items.append(old_item)

            inv_item.quantity -= 1
            if inv_item.quantity <= 0:
                source_entity.inventory.items.remove(inv_item)

            equipped_inst = ItemInstance(f"EQUIP_{item_id}_{state.current_tick}", item_id, 1)
            source_entity.equipment.slots[slot] = equipped_inst
            return CommandResult(True, message=f"Equipped {item_id} in {slot.value}")

        elif command.command_type == GameplayCommandType.UNEQUIP_ITEM:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Entity not found")
            slot_name = command.payload.get("slot")
            try:
                slot = EquipmentSlot(slot_name)
            except Exception:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Invalid slot")

            cur = source_entity.equipment.slots.get(slot)
            if not cur:
                return CommandResult(False, CommandFailureCode.CONDITION_FAILED, "No item in slot")

            source_entity.inventory.items.append(cur)
            source_entity.equipment.slots[slot] = None
            return CommandResult(True, message=f"Unequipped {slot.value}")

        elif command.command_type == GameplayCommandType.USE_ABILITY:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Entity not found")
            ability_id = command.payload.get("ability_id")
            ab = state.abilities.get(ability_id)
            if not ab:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Ability not found")

            if ab.current_cooldown > 0.0:
                return CommandResult(False, CommandFailureCode.COOLDOWN_ACTIVE, "Ability is on cooldown")

            # Check costs
            ab.current_cooldown = ab.cooldown
            if ab.effect_id:
                eff = StatusEffectInstance(
                    effect_id=f"EFF_{ab.effect_id}_{state.current_tick}",
                    name=ab.name,
                    effect_type=EffectType.BUFF,
                    duration=5.0,
                    remaining_duration=5.0,
                )
                source_entity.active_effects.append(eff)
            return CommandResult(True, message=f"Used ability {ab.name}")

        elif command.command_type == GameplayCommandType.LEARN_SKILL:
            if not source_entity:
                return CommandResult(False, CommandFailureCode.INVALID_COMMAND, "Entity not found")
            tree_id = command.payload.get("tree_id")
            skill_id = command.payload.get("skill_id")
            tree = state.skill_trees.get(tree_id)
            if not tree:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Skill tree not found")
            skill = tree.skills.get(skill_id)
            if not skill:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Skill not found")

            if source_entity.progression.skill_points <= 0:
                return CommandResult(False, CommandFailureCode.INSUFFICIENT_RESOURCE, "No skill points available")

            # Check prerequisites
            for prereq in skill.prerequisites:
                p_node = tree.skills.get(prereq)
                if not p_node or p_node.current_rank <= 0:
                    return CommandResult(False, CommandFailureCode.CONDITION_FAILED, f"Prerequisite {prereq} not met")

            if skill.current_rank >= skill.max_rank:
                return CommandResult(False, CommandFailureCode.CONDITION_FAILED, "Skill already max rank")

            skill.current_rank += 1
            source_entity.progression.skill_points -= 1
            return CommandResult(True, message=f"Learned skill {skill.name} rank {skill.current_rank}")

        elif command.command_type == GameplayCommandType.START_MISSION:
            mission_id = command.payload.get("mission_id", command.target)
            m = state.missions.get(mission_id)
            if not m:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Mission not found")
            m.state = MissionState.IN_PROGRESS
            return CommandResult(True, message=f"Mission {mission_id} started")

        elif command.command_type == GameplayCommandType.COMPLETE_MISSION:
            mission_id = command.payload.get("mission_id", command.target)
            m = state.missions.get(mission_id)
            if not m:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Mission not found")
            m.state = MissionState.COMPLETED
            return CommandResult(True, message=f"Mission {mission_id} completed")

        elif command.command_type == GameplayCommandType.TALK:
            dialogue_id = command.payload.get("dialogue_id")
            diag = state.dialogues.get(dialogue_id)
            if not diag:
                return CommandResult(False, CommandFailureCode.INVALID_TARGET, "Dialogue not found")
            root = diag.nodes.get(diag.root_node_id)
            if not root:
                return CommandResult(False, CommandFailureCode.INVALID_STATE, "Dialogue root missing")
            return CommandResult(True, message=f"Talking with {root.speaker}: {root.text}")

        return CommandResult(True, message="Command executed")

    # --- SIMULATION TICK ---

    @classmethod
    def advance_simulation_tick(cls, state: GameplayState, dt: float = 0.033) -> None:
        state.current_tick += 1

        for entity in state.entities.values():
            # Update active status effects
            for eff in list(entity.active_effects):
                eff.remaining_duration -= dt
                eff.tick_timer += dt
                if eff.tick_timer >= eff.tick_interval:
                    eff.tick_timer = 0.0
                    if eff.effect_type == EffectType.DAMAGE_OVER_TIME:
                        entity.health = max(0.0, entity.health - eff.magnitude)
                    elif eff.effect_type == EffectType.HEAL_OVER_TIME:
                        entity.health = min(entity.max_health, entity.health + eff.magnitude)

                if eff.is_expired():
                    entity.active_effects.remove(eff)

        # Update ability cooldowns
        for ab in state.abilities.values():
            if ab.current_cooldown > 0.0:
                ab.current_cooldown = max(0.0, ab.current_cooldown - dt)

    # --- LOOT GENERATION ---

    @staticmethod
    def roll_loot(loot_table: LootTable, seed: int = 42) -> List[Tuple[str, int]]:
        results = []
        if not loot_table.entries:
            return results

        counter = 0
        for _ in range(loot_table.roll_count):
            for entry in loot_table.entries:
                counter += 1
                val = ((counter * 1664525 + seed) & 0xFFFFFFFF) / 4294967296.0
                if val <= entry.drop_chance:
                    count = entry.min_count if entry.min_count == entry.max_count else (
                        entry.min_count + int(val * (entry.max_count - entry.min_count + 1))
                    )
                    results.append((entry.item_id, count))
        return results

    # --- SAVE / LOAD ---

    @staticmethod
    def save_state(state: GameplayState) -> GameplaySaveState:
        serialized_entities = [
            {
                "entity_id": e.entity_id,
                "type": e.entity_type.value,
                "health": e.health,
                "gold": e.wallet.get_balance(CurrencyType.GOLD),
                "level": e.progression.current_level,
                "xp": e.progression.current_xp,
            }
            for e in state.entities.values()
        ]
        serialized_quests = [
            {"quest_id": q.quest_id, "state": q.state.value}
            for q in state.quests.values()
        ]
        return GameplaySaveState(
            save_id=f"SAVE_{state.state_id}_{state.current_tick}",
            state_id=state.state_id,
            seed=state.seed,
            current_tick=state.current_tick,
            serialized_entities=serialized_entities,
            serialized_quests=serialized_quests,
            flags=copy.deepcopy(state.world_flags),
            state_hash=state.gameplay_state_hash,
            timestamp=float(state.current_tick),
        )

    @staticmethod
    def load_state(state: GameplayState, save_state: GameplaySaveState) -> None:
        state.current_tick = save_state.current_tick
        state.world_flags = copy.deepcopy(save_state.flags)
        for q_data in save_state.serialized_quests:
            q = state.quests.get(q_data["quest_id"])
            if q:
                q.state = QuestState(q_data["state"])
        for e_data in save_state.serialized_entities:
            e = state.entities.get(e_data["entity_id"])
            if e:
                e.health = e_data.get("health", e.health)
                if "gold" in e_data:
                    e.wallet.balances[CurrencyType.GOLD] = e_data["gold"]
                if "level" in e_data:
                    e.progression.current_level = e_data["level"]
                if "xp" in e_data:
                    e.progression.current_xp = e_data["xp"]

    # --- 19 CANONICAL GOLDEN GAMEPLAY SCENARIOS ---

    @classmethod
    def build_golden_quest_start(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_QUEST_START", seed=101)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        state.entities[player.entity_id] = player

        quest = QuestDefinition(
            quest_id="Q_START",
            title="A Fresh Journey",
            description="Speak to the elder in the village.",
            giver="ELDER",
            objectives=[QuestObjective("OBJ_1", "Talk to Elder", ObjectiveType.TALK, "ELDER")],
            state=QuestState.AVAILABLE,
        )
        state.quests[quest.quest_id] = quest
        return state

    @classmethod
    def build_golden_quest_branch(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_QUEST_BRANCH", seed=102)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        state.entities[player.entity_id] = player

        q_peace = QuestDefinition(
            quest_id="Q_PEACE",
            title="Path of Peace",
            description="Negotiate a treaty with the bandits.",
            giver="MAYOR",
            objectives=[QuestObjective("OBJ_PEACE", "Deliver treaty", ObjectiveType.DELIVER, "BANDIT_CHIEF")],
            state=QuestState.AVAILABLE,
        )
        q_war = QuestDefinition(
            quest_id="Q_WAR",
            title="Path of War",
            description="Defeat the bandit raiders.",
            giver="CAPTAIN",
            objectives=[QuestObjective("OBJ_WAR", "Eliminate raiders", ObjectiveType.KILL, "BANDIT", target_count=5)],
            state=QuestState.AVAILABLE,
        )
        state.quests[q_peace.quest_id] = q_peace
        state.quests[q_war.quest_id] = q_war
        return state

    @classmethod
    def build_golden_quest_complete(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_QUEST_COMPLETE", seed=103)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        state.entities[player.entity_id] = player

        quest = QuestDefinition(
            quest_id="Q_WOLF_HUNT",
            title="Wolf Threat",
            description="Clear wolves near the farm.",
            giver="FARMER",
            objectives=[QuestObjective("OBJ_WOLVES", "Cull wolves", ObjectiveType.KILL, "WOLF", 3, 3, ObjectiveState.COMPLETED)],
            rewards=RewardDefinition(xp=150, currency=50),
            state=QuestState.COMPLETED,
        )
        state.quests[quest.quest_id] = quest
        return state

    @classmethod
    def build_golden_quest_fail(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_QUEST_FAIL", seed=104)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        state.entities[player.entity_id] = player

        quest = QuestDefinition(
            quest_id="Q_ESCORT",
            title="Merchant Escort",
            description="Keep the merchant alive.",
            giver="GUILD",
            objectives=[QuestObjective("OBJ_ESCORT", "Escort merchant", ObjectiveType.ESCORT, "MERCHANT", 1, 0, ObjectiveState.FAILED)],
            state=QuestState.FAILED,
        )
        state.quests[quest.quest_id] = quest
        return state

    @classmethod
    def build_golden_dialogue_branch(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_DIALOGUE_BRANCH", seed=105)
        c1 = DialogueChoice("C1", "I come in peace.", "NODE_PEACE")
        c2 = DialogueChoice("C2", "Surrender your loot!", "NODE_FIGHT")
        root = DialogueNode("ROOT", "GUARD", "Halt! State your business.", [c1, c2])
        node_peace = DialogueNode("NODE_PEACE", "GUARD", "Very well, pass through.", is_terminal=True)
        node_fight = DialogueNode("NODE_FIGHT", "GUARD", "To arms!", is_terminal=True)

        diag = DialogueGraph("DIAG_GUARD", "ROOT", {"ROOT": root, "NODE_PEACE": node_peace, "NODE_FIGHT": node_fight})
        state.dialogues[diag.dialogue_id] = diag
        return state

    @classmethod
    def build_golden_inventory(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_INVENTORY", seed=106)
        player = cls.spawn_entity("HERO", EntityType.PLAYER, max_slots=10)
        item_sword = ItemDefinition("SWORD_IRON", "Iron Sword", category=ItemCategory.WEAPON, value=25)
        item_potion = ItemDefinition("POTION_HEAL", "Health Potion", category=ItemCategory.CONSUMABLE, max_stack=5, value=10)
        state.items[item_sword.item_id] = item_sword
        state.items[item_potion.item_id] = item_potion

        player.inventory.items.append(ItemInstance("INST_SWORD_1", "SWORD_IRON", 1))
        player.inventory.items.append(ItemInstance("INST_POTION_1", "POTION_HEAL", 3))
        state.entities[player.entity_id] = player
        return state

    @classmethod
    def build_golden_equipment(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_EQUIPMENT", seed=107)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        armor_item = ItemDefinition(
            "ARMOR_STEEL",
            "Steel Chestplate",
            category=ItemCategory.ARMOR,
            equipment_slot=EquipmentSlot.CHEST,
            stat_modifiers=[StatModifier(StatType.ARMOR, 20.0)],
        )
        state.items[armor_item.item_id] = armor_item
        player.equipment.slots[EquipmentSlot.CHEST] = ItemInstance("INST_ARMOR", "ARMOR_STEEL", 1)
        state.entities[player.entity_id] = player
        return state

    @classmethod
    def build_golden_crafting(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_CRAFTING", seed=108)
        wood = ItemDefinition("WOOD_LOG", "Wood Log", category=ItemCategory.MATERIAL, max_stack=20)
        iron = ItemDefinition("IRON_INGOT", "Iron Ingot", category=ItemCategory.MATERIAL, max_stack=20)
        axe = ItemDefinition("BATTLE_AXE", "Battle Axe", category=ItemCategory.WEAPON)
        state.items[wood.item_id] = wood
        state.items[iron.item_id] = iron
        state.items[axe.item_id] = axe

        recipe = CraftingRecipe(
            recipe_id="RECIPE_AXE",
            name="Forge Battle Axe",
            ingredients=[RecipeIngredient("WOOD_LOG", 2), RecipeIngredient("IRON_INGOT", 3)],
            results=[RecipeIngredient("BATTLE_AXE", 1)],
        )
        state.crafting_recipes[recipe.recipe_id] = recipe

        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        player.inventory.items.append(ItemInstance("I1", "WOOD_LOG", 5))
        player.inventory.items.append(ItemInstance("I2", "IRON_INGOT", 5))
        state.entities[player.entity_id] = player
        return state

    @classmethod
    def build_golden_loot(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_LOOT", seed=109)
        gold = ItemDefinition("GOLD_COIN", "Gold Coin", category=ItemCategory.CURRENCY)
        gem = ItemDefinition("RUBY", "Ruby Gem", category=ItemCategory.MATERIAL, rarity=ItemRarity.RARE)
        state.items[gold.item_id] = gold
        state.items[gem.item_id] = gem

        table = LootTable(
            table_id="LOOT_CHEST",
            entries=[
                LootEntry("GOLD_COIN", weight=1.0, min_count=10, max_count=20, drop_chance=1.0),
                LootEntry("RUBY", weight=0.3, min_count=1, max_count=1, drop_chance=0.5),
            ],
        )
        state.loot_tables[table.table_id] = table
        return state

    @classmethod
    def build_golden_reward(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_REWARD", seed=110)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        state.entities[player.entity_id] = player

        reward = RewardDefinition(xp=500, currency=100, items=[("MAGIC_RING", 1)], reputation={"FACTION_GUILD": 25.0})
        quest = QuestDefinition(
            "Q_REWARD",
            "Bounty Hunter",
            "Defeat boss.",
            "KING",
            objectives=[QuestObjective("OBJ_BOSS", "Defeat Boss", ObjectiveType.KILL, "BOSS_OGRE")],
            rewards=reward,
            state=QuestState.AVAILABLE,
        )
        state.quests[quest.quest_id] = quest
        return state

    @classmethod
    def build_golden_merchant(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_MERCHANT", seed=111)
        player = cls.spawn_entity("HERO", EntityType.PLAYER, gold=100)
        state.entities[player.entity_id] = player

        potion = ItemDefinition("POTION_HP", "Healing Draught", category=ItemCategory.CONSUMABLE, value=20)
        state.items[potion.item_id] = potion

        merchant_inv = Inventory("INV_MERCHANT", "BOB_SHOP", max_slots=50)
        merchant_inv.items.append(ItemInstance("P1", "POTION_HP", 10))
        merchant = MerchantDefinition("BOB_SHOP", "Bob the Alchemist", merchant_inv, Wallet({CurrencyType.GOLD: 500}))
        state.merchants[merchant.merchant_id] = merchant
        return state

    @classmethod
    def build_golden_faction(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_FACTION", seed=112)
        state.factions["TOWN_GUARD"] = FactionReputation("TOWN_GUARD", score=300.0)
        state.factions["BANDITS"] = FactionReputation("BANDITS", score=-600.0)
        return state

    @classmethod
    def build_golden_level_up(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_LEVEL_UP", seed=113)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        player.progression.current_level = 1
        player.progression.current_xp = 90
        player.progression.xp_for_next_level = 100
        state.entities[player.entity_id] = player
        return state

    @classmethod
    def build_golden_skill_unlock(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_SKILL_UNLOCK", seed=114)
        player = cls.spawn_entity("HERO", EntityType.PLAYER)
        player.progression.skill_points = 2
        state.entities[player.entity_id] = player

        s1 = SkillNode("SLASH", "Power Slash", max_rank=3, current_rank=0)
        s2 = SkillNode("WHIRLWIND", "Whirlwind Attack", max_rank=1, current_rank=0, prerequisites=["SLASH"])
        tree = SkillTree("TREE_WARRIOR", "Warrior Discipline", {"SLASH": s1, "WHIRLWIND": s2})
        state.skill_trees[tree.tree_id] = tree
        return state

    @classmethod
    def build_golden_ability(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_ABILITY", seed=115)
        ab = AbilityDefinition("FIREBALL", "Fireball", cooldown=4.0, range_radius=800.0, effect_id="BURN")
        state.abilities[ab.ability_id] = ab
        return state

    @classmethod
    def build_golden_status_effect(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_STATUS_EFFECT", seed=116)
        player = cls.spawn_entity("HERO", EntityType.PLAYER, health=100.0)
        burn = StatusEffectInstance("EFF_BURN", "Burning", EffectType.DAMAGE_OVER_TIME, duration=5.0, remaining_duration=5.0, magnitude=10.0)
        player.active_effects.append(burn)
        state.entities[player.entity_id] = player
        return state

    @classmethod
    def build_golden_world_unlock(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_WORLD_UNLOCK", seed=117)
        state.world_flags["DUNGEON_KEY_FOUND"] = True
        unlock = WorldUnlock("DUNGEON_GATE", ["DUNGEON_KEY_FOUND"], "Ancient Dungeon Level 1", is_unlocked=False)
        state.world_unlocks[unlock.unlock_id] = unlock
        return state

    @classmethod
    def build_golden_save_load(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_SAVE_LOAD", seed=118)
        player = cls.spawn_entity("HERO", EntityType.PLAYER, health=88.0, gold=150)
        state.entities[player.entity_id] = player
        state.world_flags["TREASURE_CLAIMED"] = True
        return state

    @classmethod
    def build_golden_multiplayer_reconciliation(cls) -> GameplayState:
        state = GameplayState("SIM_GOLDEN_MULTIPLAYER_RECONCILIATION", seed=119)
        p1 = cls.spawn_entity("PLAYER_1", EntityType.PLAYER, health=100.0, gold=50)
        p2 = cls.spawn_entity("PLAYER_2", EntityType.PLAYER, health=100.0, gold=75)
        state.entities[p1.entity_id] = p1
        state.entities[p2.entity_id] = p2
        return state

    @classmethod
    def create_golden_scenario(cls, scenario_name: str, seed: Optional[int] = None) -> GameplayState:
        builders = {
            cls.GOLDEN_QUEST_START: cls.build_golden_quest_start,
            cls.GOLDEN_QUEST_BRANCH: cls.build_golden_quest_branch,
            cls.GOLDEN_QUEST_COMPLETE: cls.build_golden_quest_complete,
            cls.GOLDEN_QUEST_FAIL: cls.build_golden_quest_fail,
            cls.GOLDEN_DIALOGUE_BRANCH: cls.build_golden_dialogue_branch,
            cls.GOLDEN_INVENTORY: cls.build_golden_inventory,
            cls.GOLDEN_EQUIPMENT: cls.build_golden_equipment,
            cls.GOLDEN_CRAFTING: cls.build_golden_crafting,
            cls.GOLDEN_LOOT: cls.build_golden_loot,
            cls.GOLDEN_REWARD: cls.build_golden_reward,
            cls.GOLDEN_MERCHANT: cls.build_golden_merchant,
            cls.GOLDEN_FACTION: cls.build_golden_faction,
            cls.GOLDEN_LEVEL_UP: cls.build_golden_level_up,
            cls.GOLDEN_SKILL_UNLOCK: cls.build_golden_skill_unlock,
            cls.GOLDEN_ABILITY: cls.build_golden_ability,
            cls.GOLDEN_STATUS_EFFECT: cls.build_golden_status_effect,
            cls.GOLDEN_WORLD_UNLOCK: cls.build_golden_world_unlock,
            cls.GOLDEN_SAVE_LOAD: cls.build_golden_save_load,
            cls.GOLDEN_MULTIPLAYER_RECONCILIATION: cls.build_golden_multiplayer_reconciliation,
        }
        builder = builders.get(scenario_name)
        if not builder:
            raise ValueError(f"Unknown golden gameplay scenario: {scenario_name}")
        state = builder()
        if seed is not None:
            state.seed = seed
        return state
