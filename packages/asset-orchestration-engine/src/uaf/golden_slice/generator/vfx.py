"""Niagara visual effects generator for representative golden vertical slice systems."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from uaf.golden_slice.manifest.seeds import SeedManager


@dataclass
class NiagaraSystemDescriptor:
    system_id: str
    semantic_name: str
    sim_target: str  # "CPUSim" or "GPUSim"
    emitters_count: int
    max_particles: int
    warmup_s: float
    is_looping: bool
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_cpu_us: float = 120.0
    estimated_gpu_us: float = 250.0


@dataclass
class VFXSlice:
    systems: Dict[str, NiagaraSystemDescriptor] = field(default_factory=dict)

    def validate(self) -> List[str]:
        errors: List[str] = []
        required_effects = [
            "muzzle_flash",
            "impact",
            "blood_damage",
            "dust",
            "fire",
            "smoke",
            "environmental_particles",
            "ability_effect",
            "death_effect",
            "weather",
        ]
        for req in required_effects:
            if req not in self.systems:
                errors.append(f"Missing required golden VFX system '{req}'")
        return errors

    @property
    def total_max_particles(self) -> int:
        return sum(s.max_particles for s in self.systems.values())


class VFXGenerator:
    """Generates the 10 required representative Niagara visual effects systems."""

    def __init__(self, seeds: SeedManager) -> None:
        self.rng = seeds.get_rng("vfx")

    def generate(self) -> VFXSlice:
        configs = [
            ("muzzle_flash", "NS_MuzzleFlash", "CPUSim", 2, 200, 0.0, False, {"FlashColor": [1.0, 0.8, 0.2]}),
            ("impact", "NS_WeaponImpact", "CPUSim", 3, 500, 0.0, False, {"DecalSize": 25.0}),
            ("blood_damage", "NS_DamageSpurt", "CPUSim", 2, 350, 0.0, False, {"VelocityScale": 1.2}),
            ("dust", "NS_FootstepDust", "CPUSim", 1, 150, 0.0, False, {"DustRadius": 50.0}),
            ("fire", "NS_CampfireFire", "GPUSim", 3, 2500, 0.5, True, {"HeatIntensity": 2.0}),
            ("smoke", "NS_HeavySmoke", "GPUSim", 2, 1800, 1.0, True, {"Density": 0.9}),
            ("environmental_particles", "NS_ForestFloatingSpores", "GPUSim", 1, 3000, 2.0, True, {"SwarmRadius": 2000.0}),
            ("ability_effect", "NS_WhirlwindAura", "GPUSim", 4, 3500, 0.0, False, {"AuraRadius": 350.0}),
            ("death_effect", "NS_EnemyDisintegration", "GPUSim", 3, 2000, 0.0, False, {"DissolveTime": 1.5}),
            ("weather", "NS_DynamicRainSystem", "GPUSim", 2, 5000, 1.0, True, {"RainIntensity": 0.75}),
        ]

        systems: Dict[str, NiagaraSystemDescriptor] = {}
        for key, asset_name, target, emitters, max_part, warmup, looping, params in configs:
            systems[key] = NiagaraSystemDescriptor(
                system_id=key,
                semantic_name=asset_name,
                sim_target=target,
                emitters_count=emitters,
                max_particles=max_part,
                warmup_s=warmup,
                is_looping=looping,
                parameters=params,
            )

        return VFXSlice(systems=systems)
