"""
Tests for BaseRegistry, ContractValidator, and CapabilityRegistry.
Verifies contract validation, discovery registries, and capability queries.
UAF-81.0 Sections 44, 51, 52, 53.
"""

import pytest
from uaf.contracts.registry import BaseRegistry
from uaf.contracts.validator import ContractValidator
from uaf.capabilities.capability_description import CapabilityDescription
from uaf.capabilities.capability_registry import CapabilityRegistry
from uaf.core.identity.asset_types import AssetType
from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.core.operations.operation import Operation
from uaf.core.operations.operation_types import OperationType


def test_base_registry_operations():
    reg = BaseRegistry[str]("TestRegistry")
    reg.register("key1", "value1")
    reg.register("key2", "value2")

    assert reg.get("key1") == "value1"
    assert reg.supports("key2") is True
    assert reg.supports("key3") is False

    with pytest.raises(KeyError, match="already registered"):
        reg.register("key1", "value1_dup")

    reg.register("key1", "value1_overwritten", overwrite=True)
    assert reg.get("key1") == "value1_overwritten"


def test_contract_validator_specification():
    # Valid spec
    valid_spec = AssetSpecification(
        identity=AssetIdentity(asset_id="asset_valid", asset_type=AssetType.WEAPON),
        seed=42,
    )
    rep1 = ContractValidator.validate_specification(valid_spec)
    assert rep1.is_valid is True

    # Invalid spec with negative seed
    invalid_spec = AssetSpecification(
        identity=AssetIdentity(asset_id="asset_bad", asset_type=AssetType.WEAPON),
        seed=-1,
    )
    rep2 = ContractValidator.validate_specification(invalid_spec)
    assert rep2.is_valid is False
    assert any("SPEC_INVALID_SEED" == d.code for d in rep2.diagnostics)


def test_capability_registry_discovery():
    reg = CapabilityRegistry()

    cap_char = CapabilityDescription(
        capability_id="blender_character_generator",
        asset_types=[AssetType.CHARACTER, AssetType.CREATURE],
        operations=[OperationType.GENERATE, OperationType.OPTIMIZE],
        targets=["unreal", "generic"],
    )
    cap_audio = CapabilityDescription(
        capability_id="procedural_audio_synthesizer",
        asset_types=[AssetType.AUDIO],
        operations=[OperationType.GENERATE],
        targets=["generic"],
    )

    reg.register_capability(cap_char)
    reg.register_capability(cap_audio)

    # Queries
    assert reg.can_produce(AssetType.CHARACTER) is True
    assert reg.can_produce(AssetType.AUDIO) is True
    assert reg.can_produce(AssetType.WEAPON) is False

    # Filter by target
    unreal_caps = reg.find_for_asset(AssetType.CHARACTER, target="unreal")
    assert len(unreal_caps) == 1
    assert unreal_caps[0].capability_id == "blender_character_generator"

    unity_caps = reg.find_for_asset(AssetType.CHARACTER, target="unity")
    assert len(unity_caps) == 0
