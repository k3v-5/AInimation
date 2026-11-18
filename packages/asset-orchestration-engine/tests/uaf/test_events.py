"""
Tests for UAFEvent and concrete domain events.
Verifies event immutability, correlation IDs, and event serialization.
UAF-81.0 Sections 36, 37, 38.
"""

import pytest
from uaf.core.events.event_model import UAFEvent
from uaf.core.events.event_types import (
    ProductionStarted,
    ProductionCompleted,
    OperationStarted,
    OperationCompleted,
    OperationFailed,
    ArtifactCreated,
    ArtifactValidated,
    ArtifactPublished,
    CheckpointCreated,
    CheckpointRestored,
)


def test_event_immutability():
    ev = ProductionStarted(production_id="prod_001", payload={"initiator": "ci_pipeline"})
    assert ev.event_type == "ProductionStarted"
    assert ev.production_id == "prod_001"

    with pytest.raises(AttributeError):
        ev.production_id = "prod_tampered"  # Frozen dataclass


def test_event_correlation():
    ev = OperationStarted(
        production_id="prod_100",
        operation_id="op_200",
        asset_id="asset_300",
        payload={"stage": "mesh_cleanup"},
    )
    assert ev.production_id == "prod_100"
    assert ev.operation_id == "op_200"
    assert ev.asset_id == "asset_300"
    assert ev.payload["stage"] == "mesh_cleanup"

    data = ev.to_dict()
    reconstructed = UAFEvent.from_dict(data)
    assert reconstructed.event_id == ev.event_id
    assert reconstructed.operation_id == "op_200"


def test_concrete_event_payloads():
    art_ev = ArtifactCreated(
        production_id="p1",
        operation_id="op1",
        asset_id="a1",
        artifact_id="art_texture_diffuse",
    )
    assert art_ev.payload["artifact_id"] == "art_texture_diffuse"

    val_ev = ArtifactValidated(
        production_id="p1",
        operation_id="op1",
        asset_id="a1",
        artifact_id="art_texture_diffuse",
        is_valid=True,
    )
    assert val_ev.payload["is_valid"] is True
