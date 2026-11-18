"""Niagara particle system and user parameter synchronization bridge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class NiagaraEmitterDescriptor:
    emitter_name: str
    is_enabled: bool = True
    sim_target: str = "CPUSim"  # CPUSim or GPUSim
    spawn_rate: float = 100.0
    lifetime: float = 1.0
    is_active: Optional[bool] = None

    def __post_init__(self) -> None:
        if self.is_active is not None:
            self.is_enabled = self.is_active
        else:
            self.is_active = self.is_enabled


@dataclass
class NiagaraBridgePayload:
    asset_id: str = ""
    semantic_name: str = ""
    emitters: List[NiagaraEmitterDescriptor] = field(default_factory=list)
    user_parameters: Dict[str, Any] = field(default_factory=dict)
    warmup_time_s: float = 0.0
    is_looping: bool = True
    system_id: Optional[str] = None
    system_asset_path: Optional[str] = None
    system_parameters: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.system_id is not None:
            self.asset_id = self.system_id
        else:
            self.system_id = self.asset_id

        if self.system_asset_path is not None:
            self.semantic_name = self.system_asset_path
        else:
            self.system_asset_path = self.semantic_name

        if self.system_parameters is not None:
            self.user_parameters = self.system_parameters
        else:
            self.system_parameters = self.user_parameters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "system_id": self.system_id,
            "semantic_name": self.semantic_name,
            "system_asset_path": self.system_asset_path,
            "emitters": [
                {
                    "name": e.emitter_name,
                    "enabled": e.is_enabled,
                    "sim_target": e.sim_target,
                    "spawn_rate": e.spawn_rate,
                    "lifetime": e.lifetime,
                }
                for e in self.emitters
            ],
            "user_parameters": dict(self.user_parameters),
            "system_parameters": dict(self.system_parameters or {}),
            "warmup_time_s": self.warmup_time_s,
            "is_looping": self.is_looping,
        }
