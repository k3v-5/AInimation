"""
Tests for AssetIdentity, AssetType, and AssetSpecification.
Verifies immutability, schema versioning, and canonical specification hash stability.
UAF-81.0 Sections 11, 12, 13, 14, 15.
"""

import pytest
from uaf.core.identity.asset_types import AssetType
from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.specification.asset_specification import AssetSpecification


def test_asset_identity_creation_and_urn():
    identity = AssetIdentity(
        asset_id="sword_01",
        asset_type=AssetType.WEAPON,
        namespace="combat",
        version="2.1.0",
    )
    assert identity.urn == "urn:uaf:combat:weapon:sword_01@2.1.0"
    assert identity.asset_type == AssetType.WEAPON


def test_asset_identity_empty_id_raises():
    with pytest.raises(ValueError, match="non-empty"):
        AssetIdentity(asset_id="", asset_type=AssetType.CHARACTER)


def test_asset_identity_serialization():
    identity = AssetIdentity(asset_id="hero", asset_type=AssetType.CHARACTER)
    data = identity.to_dict()
    reconstructed = AssetIdentity.from_dict(data)

    assert reconstructed.asset_id == identity.asset_id
    assert reconstructed.asset_type == AssetType.CHARACTER
    assert reconstructed.urn == identity.urn


def test_asset_specification_immutability():
    identity = AssetIdentity(asset_id="prop_crate", asset_type=AssetType.PROP)
    spec = AssetSpecification(
        identity=identity,
        parameters={"size": [1.0, 1.0, 1.0], "material": "wood"},
        seed=1001,
    )

    with pytest.raises(AttributeError):
        spec.seed = 2002  # Frozen


def test_asset_specification_hash_stability():
    identity = AssetIdentity(asset_id="shield_01", asset_type=AssetType.WEAPON)
    spec1 = AssetSpecification(
        identity=identity,
        parameters={"defense": 50, "durability": 100},
        seed=42,
    )
    # Spec with same logical parameters defined in different order
    spec2 = AssetSpecification(
        identity=identity,
        parameters={"durability": 100, "defense": 50},
        seed=42,
    )

    assert spec1.specification_hash == spec2.specification_hash
    assert len(spec1.specification_hash) == 64  # SHA-256 hex string


def test_asset_specification_different_params_different_hash():
    identity = AssetIdentity(asset_id="shield_01", asset_type=AssetType.WEAPON)
    spec1 = AssetSpecification(identity=identity, parameters={"defense": 50}, seed=42)
    spec2 = AssetSpecification(identity=identity, parameters={"defense": 51}, seed=42)

    assert spec1.specification_hash != spec2.specification_hash
