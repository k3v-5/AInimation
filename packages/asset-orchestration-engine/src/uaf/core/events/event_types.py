"""
Concrete domain event types for UAF.
UAF-81.0 Section 36.
"""

from typing import Dict, Any, Optional
from .event_model import UAFEvent


class ProductionStarted(UAFEvent):
    def __init__(self, production_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            event_type="ProductionStarted",
            production_id=production_id,
            payload=payload or {},
            **kwargs,
        )


class ProductionCompleted(UAFEvent):
    def __init__(self, production_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            event_type="ProductionCompleted",
            production_id=production_id,
            payload=payload or {},
            **kwargs,
        )


class OperationStarted(UAFEvent):
    def __init__(self, production_id: str, operation_id: str, asset_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            event_type="OperationStarted",
            production_id=production_id,
            operation_id=operation_id,
            asset_id=asset_id,
            payload=payload or {},
            **kwargs,
        )


class OperationCompleted(UAFEvent):
    def __init__(self, production_id: str, operation_id: str, asset_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            event_type="OperationCompleted",
            production_id=production_id,
            operation_id=operation_id,
            asset_id=asset_id,
            payload=payload or {},
            **kwargs,
        )


class OperationFailed(UAFEvent):
    def __init__(self, production_id: str, operation_id: str, asset_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(
            event_type="OperationFailed",
            production_id=production_id,
            operation_id=operation_id,
            asset_id=asset_id,
            payload=payload or {},
            **kwargs,
        )


class ArtifactCreated(UAFEvent):
    def __init__(self, production_id: str, operation_id: str, asset_id: str, artifact_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        p = payload or {}
        p["artifact_id"] = artifact_id
        super().__init__(
            event_type="ArtifactCreated",
            production_id=production_id,
            operation_id=operation_id,
            asset_id=asset_id,
            payload=p,
            **kwargs,
        )


class ArtifactValidated(UAFEvent):
    def __init__(self, production_id: str, operation_id: str, asset_id: str, artifact_id: str, is_valid: bool, payload: Optional[Dict[str, Any]] = None, **kwargs):
        p = payload or {}
        p["artifact_id"] = artifact_id
        p["is_valid"] = is_valid
        super().__init__(
            event_type="ArtifactValidated",
            production_id=production_id,
            operation_id=operation_id,
            asset_id=asset_id,
            payload=p,
            **kwargs,
        )


class ArtifactPublished(UAFEvent):
    def __init__(self, production_id: str, asset_id: str, manifest_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        p = payload or {}
        p["manifest_id"] = manifest_id
        super().__init__(
            event_type="ArtifactPublished",
            production_id=production_id,
            asset_id=asset_id,
            payload=p,
            **kwargs,
        )


class CheckpointCreated(UAFEvent):
    def __init__(self, production_id: str, checkpoint_id: str, operation_id: Optional[str] = None, payload: Optional[Dict[str, Any]] = None, **kwargs):
        p = payload or {}
        p["checkpoint_id"] = checkpoint_id
        super().__init__(
            event_type="CheckpointCreated",
            production_id=production_id,
            operation_id=operation_id,
            payload=p,
            **kwargs,
        )


class CheckpointRestored(UAFEvent):
    def __init__(self, production_id: str, checkpoint_id: str, payload: Optional[Dict[str, Any]] = None, **kwargs):
        p = payload or {}
        p["checkpoint_id"] = checkpoint_id
        super().__init__(
            event_type="CheckpointRestored",
            production_id=production_id,
            payload=p,
            **kwargs,
        )
