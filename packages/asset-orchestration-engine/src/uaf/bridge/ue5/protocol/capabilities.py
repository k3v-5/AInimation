"""UE5 capability negotiation and feature detection."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class UE5Feature(str, Enum):
    NIAGARA = "Niagara"
    CONTROL_RIG = "ControlRig"
    SEQUENCER = "Sequencer"
    WORLD_PARTITION = "WorldPartition"
    LUMEN = "Lumen"
    NANITE = "Nanite"
    SUBSTRATE = "Substrate"
    ANIMATION = "Animation"
    PHYSICS = "Physics"
    AUDIO = "Audio"
    LIVELINK = "LiveLink"
    EDITOR = "Editor"
    RUNTIME = "Runtime"


@dataclass
class UE5Capabilities:
    """Advertised features and operational constraints of the connected UE5 instance."""
    engine_version: str = "5.4.0"
    bridge_plugin_version: str = "1.0.0"
    platform: str = "Windows"
    supported_features: Set[UE5Feature] = field(default_factory=lambda: set(UE5Feature))
    max_batch_size: int = 1000
    supports_hot_reload: bool = True
    supports_nanite: bool = True
    supports_lumen: bool = True
    enabled_features: Optional[Set[UE5Feature]] = None

    def __post_init__(self) -> None:
        if self.enabled_features is not None:
            self.supported_features = set(self.enabled_features)
        else:
            self.enabled_features = set(self.supported_features)

    def supports(self, feature: UE5Feature) -> bool:
        return feature in self.supported_features

    def has_feature(self, feature: UE5Feature) -> bool:
        return self.supports(feature)

    def add_feature(self, feature: UE5Feature) -> None:
        self.supported_features.add(feature)
        if self.enabled_features is not None:
            self.enabled_features.add(feature)

    def remove_feature(self, feature: UE5Feature) -> None:
        self.supported_features.discard(feature)
        if self.enabled_features is not None:
            self.enabled_features.discard(feature)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_version": self.engine_version,
            "bridge_plugin_version": self.bridge_plugin_version,
            "platform": self.platform,
            "supported_features": sorted([f.value for f in self.supported_features]),
            "max_batch_size": self.max_batch_size,
            "supports_hot_reload": self.supports_hot_reload,
            "supports_nanite": self.supports_nanite,
            "supports_lumen": self.supports_lumen,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UE5Capabilities:
        feats = set()
        for f in data.get("supported_features", []):
            try:
                feats.add(UE5Feature(f))
            except ValueError:
                pass
        return cls(
            engine_version=data.get("engine_version", "5.4.0"),
            bridge_plugin_version=data.get("bridge_plugin_version", "1.0.0"),
            platform=data.get("platform", "Windows"),
            supported_features=feats,
            max_batch_size=data.get("max_batch_size", 1000),
            supports_hot_reload=data.get("supports_hot_reload", True),
            supports_nanite=data.get("supports_nanite", True),
            supports_lumen=data.get("supports_lumen", True),
        )
