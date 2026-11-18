"""
Tests for AssetArchetype, ArchetypeRegistry, and UnitNormalizer.
UAF-81.1 Sections 14, 15, 16, 17, 18, 19, 20.
"""

import pytest
from uaf.intelligence.archetypes.archetype_registry import ArchetypeRegistry
from uaf.intelligence.parameters.unit_normalizer import UnitNormalizer
from uaf.intelligence.parameters.parameter_metadata import ParameterMetadata
from uaf.intelligence.parameters.parameter_type import ParameterType, ParameterProvenance
from uaf.core.identity.asset_types import AssetType


def test_standard_archetypes_preloaded():
    reg = ArchetypeRegistry()
    assert reg.supports("HumanoidCharacter")
    assert reg.supports("Creature")
    assert reg.supports("MilitaryWeapon")
    assert reg.supports("ModularWall")
    assert reg.supports("Material")
    assert reg.supports("TextureSet")
    assert reg.supports("Terrain")
    assert reg.supports("OpenWorldRegion")

    char_archetype = reg.get("HumanoidCharacter")
    assert "height" in char_archetype.required_parameters
    assert "organic_surface_generation" in char_archetype.required_capabilities


def test_archetype_parameter_validation():
    reg = ArchetypeRegistry()
    char_archetype = reg.get("HumanoidCharacter")

    # Missing nothing since default has height and build
    missing = char_archetype.validate_parameters({})
    assert len(missing) == 0

    # Custom archetype without defaults
    from uaf.intelligence.archetypes.archetype import AssetArchetype
    custom = AssetArchetype(
        archetype_id="CustomStrict",
        asset_type=AssetType.PROP,
        required_parameters=["length", "width", "height"],
        default_parameters={},
    )
    missing_custom = custom.validate_parameters({"length": 1.0})
    assert set(missing_custom) == {"width", "height"}


def test_unit_normalizer_conversions():
    # Centimeters to meters
    assert UnitNormalizer.normalize_length("185cm") == 1.85
    assert UnitNormalizer.normalize_length("100cm") == 1.0

    # Millimeters to meters
    assert UnitNormalizer.normalize_length("1850mm") == 1.85

    # Kilometers to meters
    assert UnitNormalizer.normalize_length("2km") == 2000.0

    # Imperial to meters
    assert UnitNormalizer.normalize_length("1m") == 1.0
    assert pytest.approx(UnitNormalizer.normalize_length("6ft"), 0.001) == 1.8288
    assert pytest.approx(UnitNormalizer.normalize_length("72in"), 0.001) == 1.8288

    # Pure numeric
    assert UnitNormalizer.normalize_length(1.75) == 1.75
    assert UnitNormalizer.normalize_length("1.75") == 1.75


def test_unit_normalizer_invalid_units_raise():
    with pytest.raises(ValueError, match="Cannot parse dimension"):
        UnitNormalizer.normalize_length("invalid_string")

    with pytest.raises(ValueError, match="Unknown or unsupported unit"):
        UnitNormalizer.normalize_length("100parsecs")


def test_parameter_metadata_provenance():
    meta = ParameterMetadata(
        name="shoulder_width",
        param_type=ParameterType.FLOAT,
        default=0.52,
        minimum=0.45,
        maximum=0.60,
        unit="meters",
        provenance=ParameterProvenance.DERIVED,
        confidence=0.95,
    )
    assert meta.provenance == ParameterProvenance.DERIVED
    assert meta.confidence == 0.95
    data = meta.to_dict()
    assert data["provenance"] == "DERIVED"
