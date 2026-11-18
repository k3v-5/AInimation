"""
Tests for Economy, Currency, Trading, and Transactions (UAF-81.58 Sections 126-140, 187).
"""
import pytest
from src.uaf.universal_gameplay.models.definition import (
    CurrencyType,
    Wallet,
    MerchantDefinition,
    TransactionType,
    TransactionRecord,
    ItemDefinition,
    ItemInstance,
    Inventory,
    EntityType,
    GameplayCommand,
    GameplayCommandType,
    CommandFailureCode,
    GameplayState,
)
from src.uaf.universal_gameplay.engine.universal_gameplay_fabricator import (
    UniversalGameplayFabricator,
)


def test_currency_type_enum():
    currencies = {c.value for c in CurrencyType}
    expected = {"GOLD", "SILVER", "COPPER", "GEMS", "TOKENS", "FACTION_CREDITS", "CUSTOM"}
    assert currencies == expected


def test_wallet_add_and_get():
    w = Wallet()
    assert w.get_balance(CurrencyType.GOLD) == 0
    w.add(100, CurrencyType.GOLD)
    assert w.get_balance(CurrencyType.GOLD) == 100
    w.add(50, CurrencyType.GOLD)
    assert w.get_balance(CurrencyType.GOLD) == 150


def test_wallet_spend_success_and_failure():
    w = Wallet()
    w.add(50, CurrencyType.GOLD)
    spent = w.spend(30, CurrencyType.GOLD)
    assert spent is True
    assert w.get_balance(CurrencyType.GOLD) == 20

    fail_spent = w.spend(25, CurrencyType.GOLD)
    assert fail_spent is False
    assert w.get_balance(CurrencyType.GOLD) == 20


def test_wallet_multiple_currencies():
    w = Wallet()
    w.add(100, CurrencyType.GOLD)
    w.add(500, CurrencyType.SILVER)
    w.add(10, CurrencyType.GEMS)
    assert w.get_balance(CurrencyType.GOLD) == 100
    assert w.get_balance(CurrencyType.SILVER) == 500
    assert w.get_balance(CurrencyType.GEMS) == 10


def test_merchant_definition_initialization():
    inv = Inventory("INV_BOB", "BOB")
    merchant = MerchantDefinition(
        merchant_id="MERCHANT_BOB",
        name="Bob's General Store",
        inventory=inv,
        buy_multiplier=1.2,
        sell_multiplier=0.4,
    )
    assert merchant.merchant_id == "MERCHANT_BOB"
    assert merchant.buy_multiplier == 1.2
    assert merchant.sell_multiplier == 0.4
    assert merchant.wallet.get_balance(CurrencyType.GOLD) == 0


def test_buy_item_success():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.wallet.add(200, CurrencyType.GOLD)
    state.entities[player.entity_id] = player

    potion = ItemDefinition(item_id="POTION_HEAL", name="Healing Potion", value=20)
    state.items[potion.item_id] = potion

    m_inv = Inventory("INV_SHOP", "SHOP")
    merchant = MerchantDefinition(
        merchant_id="SHOP",
        name="Apothecary",
        inventory=m_inv,
        buy_multiplier=1.0,
    )
    merchant.wallet.add(50, CurrencyType.GOLD)
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_buy_pot",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.BUY,
        payload={"item_id": "POTION_HEAL", "count": 2},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    # 2 * 20 = 40 gold spent
    assert player.wallet.get_balance(CurrencyType.GOLD) == 160
    assert merchant.wallet.get_balance(CurrencyType.GOLD) == 90
    assert any(it.definition_id == "POTION_HEAL" and it.quantity == 2 for it in player.inventory.items)
    assert len(state.transactions) == 1
    assert state.transactions[0].transaction_type == TransactionType.BUY


def test_buy_insufficient_gold():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.wallet.add(10, CurrencyType.GOLD)
    state.entities[player.entity_id] = player

    sword = ItemDefinition(item_id="SWORD_ELITE", name="Elite Sword", value=100)
    state.items[sword.item_id] = sword

    merchant = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"), buy_multiplier=1.0)
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_poor",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.BUY,
        payload={"item_id": "SWORD_ELITE", "count": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_buy_undefined_item():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.wallet.add(500, CurrencyType.GOLD)
    state.entities[player.entity_id] = player

    merchant = MerchantDefinition("SHOP", "Shop", inventory=Inventory("I", "S"))
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_undef",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.BUY,
        payload={"item_id": "NON_EXISTENT"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_buy_merchant_not_found():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    cmd = GameplayCommand(
        command_id="cmd_no_shop",
        source=player.entity_id,
        target="GHOST_SHOP",
        command_type=GameplayCommandType.BUY,
        payload={"item_id": "ANYTHING"},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INVALID_TARGET


def test_sell_item_success():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i_gem", "RUBY_RAW", 3))
    state.entities[player.entity_id] = player

    gem_def = ItemDefinition(item_id="RUBY_RAW", name="Raw Ruby", value=40)
    state.items[gem_def.item_id] = gem_def

    merchant = MerchantDefinition("JEWELER", "Jeweler", inventory=Inventory("I", "J"), sell_multiplier=0.5)
    merchant.wallet.add(200, CurrencyType.GOLD)
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_sell_gem",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.SELL,
        payload={"item_id": "RUBY_RAW", "count": 2},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert res.success
    # Price = 40 * 0.5 * 2 = 40 gold
    assert player.wallet.get_balance(CurrencyType.GOLD) == 40
    assert merchant.wallet.get_balance(CurrencyType.GOLD) == 160
    assert player.inventory.items[0].quantity == 1
    assert len(state.transactions) == 1
    assert state.transactions[0].transaction_type == TransactionType.SELL


def test_sell_item_not_in_inventory():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    state.entities[player.entity_id] = player

    iron_def = ItemDefinition(item_id="IRON_ORE", name="Iron Ore", value=10)
    state.items[iron_def.item_id] = iron_def

    merchant = MerchantDefinition("SMITH", "Blacksmith", inventory=Inventory("I", "S"))
    merchant.wallet.add(100, CurrencyType.GOLD)
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_sell_missing",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.SELL,
        payload={"item_id": "IRON_ORE", "count": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.CONDITION_FAILED


def test_sell_merchant_out_of_funds():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.inventory.items.append(ItemInstance("i_crown", "CROWN", 1))
    state.entities[player.entity_id] = player

    crown_def = ItemDefinition(item_id="CROWN", name="Royal Crown", value=1000)
    state.items[crown_def.item_id] = crown_def

    merchant = MerchantDefinition("POOR_MERCHANT", "Pauper Shop", inventory=Inventory("I", "P"), sell_multiplier=1.0)
    merchant.wallet.balances[CurrencyType.GOLD] = 50  # Only 50 gold
    state.merchants[merchant.merchant_id] = merchant

    cmd = GameplayCommand(
        command_id="cmd_sell_cant_afford",
        source=player.entity_id,
        target=merchant.merchant_id,
        command_type=GameplayCommandType.SELL,
        payload={"item_id": "CROWN", "count": 1},
    )
    res = UniversalGameplayFabricator.execute_command(state, cmd)
    assert not res.success
    assert res.failure_code == CommandFailureCode.INSUFFICIENT_RESOURCE


def test_transaction_record_model():
    tx = TransactionRecord(
        transaction_id="TX_101",
        transaction_type=TransactionType.TRANSFER,
        source="PLAYER_1",
        target="PLAYER_2",
        amount=50,
        currency=CurrencyType.GOLD,
        item_id="SWORD_IRON",
        item_count=1,
        timestamp=33.5,
    )
    assert tx.transaction_id == "TX_101"
    assert tx.transaction_type == TransactionType.TRANSFER
    assert tx.amount == 50
    assert tx.item_count == 1
    assert tx.timestamp == 33.5


def test_transaction_audit_log_growth():
    state = GameplayState("SIM_ECONOMY")
    player = UniversalGameplayFabricator.spawn_entity("HERO", EntityType.PLAYER)
    player.wallet.add(500, CurrencyType.GOLD)
    state.entities[player.entity_id] = player

    bread = ItemDefinition(item_id="BREAD", name="Loaf of Bread", value=5)
    state.items[bread.item_id] = bread

    merchant = MerchantDefinition("BAKER", "Bakery", inventory=Inventory("I", "B"), buy_multiplier=1.0)
    state.merchants[merchant.merchant_id] = merchant

    for i in range(3):
        cmd = GameplayCommand(
            command_id=f"cmd_buy_{i}",
            source=player.entity_id,
            target=merchant.merchant_id,
            command_type=GameplayCommandType.BUY,
            payload={"item_id": "BREAD", "count": 1},
        )
        res = UniversalGameplayFabricator.execute_command(state, cmd)
        assert res.success

    assert len(state.transactions) == 3
    assert all(tx.transaction_type == TransactionType.BUY for tx in state.transactions)
