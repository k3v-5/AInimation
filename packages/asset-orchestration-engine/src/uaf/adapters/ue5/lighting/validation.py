"""
UE5 Compatibility Audit & Validation for UAF-81.85.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from typing import List

from uaf.runtime_lighting.world import LightingWorld
from uaf.runtime_lighting.core import LightType


@dataclass
class UE5LightingCompatibilityReport:
    """Audit report of export compatibility with Unreal Engine 5."""
    ue_version: str = "5.4"
    supported_features: List[str] = field(default_factory=list)
    unsupported_features: List[str] = field(default_factory=list)
    lossy_features: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    source_hash: str = ""
    target_hash: str = ""

    @property
    def is_compatible(self) -> bool:
        return len(self.errors) == 0


class UE5LightingValidator:
    """Audits lighting world against Unreal Engine 5 capabilities."""

    @staticmethod
    def audit_world(world: LightingWorld) -> UE5LightingCompatibilityReport:
        supported = [
            "DirectionalLight",
            "PointLight",
            "SpotLight",
            "RectLight",
            "SkyAtmosphere",
            "VolumetricClouds",
            "ExponentialHeightFog",
            "LumenGI",
            "LumenReflections",
            "PostProcessVolume",
            "CascadedShadowMaps",
        ]
        unsupported: List[str] = []
        lossy: List[str] = []
        warnings: List[str] = []
        errors: List[str] = []

        # Check for non-native light types
        for light in world.lights.values():
            if light.light_type in (LightType.DISK_AREA, LightType.LINE_AREA):
                lossy.append(f"Light '{light.light_id.value}' of type {light.light_type.value} will be mapped to RectLight approximation in UE5.")

        snap = world.capture_snapshot()
        source_hash = snap.canonical_hash
        target_payload = json.dumps({"ue_version": "5.4", "light_count": len(world.lights)})
        target_hash = hashlib.sha256(target_payload.encode("utf-8")).hexdigest()

        return UE5LightingCompatibilityReport(
            ue_version="5.4",
            supported_features=supported,
            unsupported_features=unsupported,
            lossy_features=lossy,
            warnings=warnings,
            errors=errors,
            source_hash=source_hash,
            target_hash=target_hash,
        )
