"""
UAF-81.99: Debris Field & Niagara VFX Emitter Solver.
Computes kinetic impulse velocities on fractured pieces and provides material-calibrated
Niagara particle emitter presets for concrete dust, sparks, and shards.
"""

import math
from typing import Dict, List, Optional

from ..core.contracts import (
    Vector3D,
    DebrisParticlePreset,
    DestructionMaterialType,
)


class DebrisFieldEmitter:
    """
    Computes kinetic blast dispersal velocities and generates Niagara visual effect configs.
    """

    @staticmethod
    def calculate_kinetic_impulse(
        piece_centroid: Vector3D,
        piece_mass_kg: float,
        impact_point: Vector3D,
        blast_energy_joules: float = 5000.0,
        max_speed_mps: float = 40.0,
    ) -> Vector3D:
        """
        Calculates blast impulse velocity vector based on distance and kinetic energy conservation.
        """
        dist = max(0.1, piece_centroid.distance_to(impact_point))
        direction = (piece_centroid - impact_point).normalized()

        # Inverse square energy attenuation
        effective_energy = blast_energy_joules / (dist ** 2)

        # v = sqrt(2 * E / m)
        mass = max(0.05, piece_mass_kg)
        speed = math.sqrt((2.0 * effective_energy) / mass)
        speed = min(max_speed_mps, speed)

        return Vector3D(
            x=round(direction.x * speed, 3),
            y=round(direction.y * speed, 3),
            z=round(max(0.5, direction.z * speed + 1.5), 3),  # Add slight upward lift
        )

    @staticmethod
    def get_preset_for_material(material_type: DestructionMaterialType) -> DebrisParticlePreset:
        """
        Returns tailored Niagara particle emitter presets according to physical material properties.
        """
        if material_type == DestructionMaterialType.CONCRETE:
            return DebrisParticlePreset(
                preset_name="NE_Concrete_Dust_Shards",
                dust_color_rgba=[0.75, 0.74, 0.72, 0.65],
                particle_spawn_rate=180.0,
                lifetime_s=3.5,
                initial_speed_min=2.0,
                initial_speed_max=14.0,
                spark_chance=0.05,
            )
        elif material_type == DestructionMaterialType.MASONRY_BRICK:
            return DebrisParticlePreset(
                preset_name="NE_Brick_Terracotta_Dust",
                dust_color_rgba=[0.68, 0.35, 0.22, 0.70],
                particle_spawn_rate=150.0,
                lifetime_s=4.0,
                initial_speed_min=1.5,
                initial_speed_max=11.0,
                spark_chance=0.02,
            )
        elif material_type == DestructionMaterialType.REINFORCED_METAL:
            return DebrisParticlePreset(
                preset_name="NE_Metal_Sparks_Smoke",
                dust_color_rgba=[0.25, 0.25, 0.28, 0.40],
                particle_spawn_rate=80.0,
                lifetime_s=1.5,
                initial_speed_min=5.0,
                initial_speed_max=22.0,
                spark_chance=0.45,
            )
        elif material_type == DestructionMaterialType.TEMPERED_GLASS:
            return DebrisParticlePreset(
                preset_name="NE_Glass_Micro_Shards",
                dust_color_rgba=[0.88, 0.95, 0.98, 0.30],
                particle_spawn_rate=250.0,
                lifetime_s=2.0,
                initial_speed_min=3.0,
                initial_speed_max=18.0,
                spark_chance=0.0,
            )
        elif material_type == DestructionMaterialType.STRUCTURAL_WOOD:
            return DebrisParticlePreset(
                preset_name="NE_Wood_Splinters_Sawdust",
                dust_color_rgba=[0.78, 0.65, 0.45, 0.50],
                particle_spawn_rate=120.0,
                lifetime_s=3.0,
                initial_speed_min=1.5,
                initial_speed_max=10.0,
                spark_chance=0.0,
            )
        else:  # COMPOSITE_PLASTIC
            return DebrisParticlePreset(
                preset_name="NE_Composite_Plastic_Chunks",
                dust_color_rgba=[0.5, 0.5, 0.5, 0.35],
                particle_spawn_rate=90.0,
                lifetime_s=2.5,
                initial_speed_min=2.0,
                initial_speed_max=12.0,
                spark_chance=0.02,
            )
