"""
Tests for ResolutionPipeline, CapabilityGapReport, and SpecificationMigrator.
UAF-81.1 Sections 46, 47, 48, 55, 65.
"""

import pytest
from uaf.core.identity.asset_identity import AssetIdentity
from uaf.core.identity.asset_types import AssetType
from uaf.core.specification.asset_specification import AssetSpecification
from uaf.capabilities.capability_registry import CapabilityRegistry
from uaf.capabilities.capability_description import CapabilityDescription
from uaf.intelligence.compiler.resolution_pipeline import ResolutionPipeline
from uaf.intelligence.compiler.capability_gap import CapabilityGapReport
from uaf.intelligence.compiler.migrator import SpecificationMigrator


def test_resolution_pipeline_normalizes_and_inherits_archetype():
    pipeline = ResolutionPipeline()

    spec = AssetSpecification(
        identity=AssetIdentity(asset_id="tactical_soldier", asset_type=AssetType.CHARACTER),
        parameters={
            "archetype": "HumanoidCharacter",
            "height": "185cm",  # Will be normalized to 1.85m
            "facial_fidelity": "high",
            "clothing_complexity": "high",
            "complexity": "C4",
        },
        seed=1234,
    )

    resolved = pipeline.resolve(spec)

    # Check unit normalization
    assert resolved.resolved_parameters["height"] == 1.85
    # Check default inheritance from archetype
    assert resolved.resolved_parameters["species"] == "humanoid"
    # Check required capabilities extracted
    assert "organic_surface_generation" in resolved.required_capabilities
    assert "advanced_facial_generation" in resolved.required_capabilities
    assert "cloth_geometry" in resolved.required_capabilities
    # Check hashes
    assert len(resolved.intent_hash) == 64
    assert len(resolved.resolved_specification_hash) == 64
    # Check trace
    assert len(resolved.resolution_trace) > 0


def test_capability_gap_report():
    reg = CapabilityRegistry()
    # Register only basic procedural generator
    reg.register_capability(
        CapabilityDescription(
            capability_id="primitive_procedural_generator",
            asset_types=[AssetType.PROP],
        )
    )

    required = ["primitive_procedural_generator", "cloth_geometry", "advanced_facial_generation"]
    report = CapabilityGapReport.evaluate(required, reg, asset_id="hero_char")

    assert report.is_supported is False
    assert set(report.missing_capabilities) == {"cloth_geometry", "advanced_facial_generation"}
    assert "cloth_geometry" in report.rationale


def test_specification_migrator():
    legacy_payload = {
        "spec_id": "legacy_weapon_01",
        "type": "WEAPON",
        "schema_version": "0.9.0",
        "params": {"fire_rate": 600},
    }

    migrated, was_migrated = SpecificationMigrator.migrate(legacy_payload)
    assert was_migrated is True
    assert migrated["schema_version"] == "1.0.0"
    assert migrated["identity"]["asset_id"] == "legacy_weapon_01"
    assert migrated["parameters"]["fire_rate"] == 600
