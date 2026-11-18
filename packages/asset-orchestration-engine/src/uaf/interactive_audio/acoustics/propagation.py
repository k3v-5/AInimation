"""
UAF-81.94: Sabine & Eyring Acoustic Reverberation Calculator & Topological Sound Diffraction.
Analytical calculation of RT60 reverberation times, axial room resonance modes,
and topological acoustic occlusion across WFC level graphs.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from uaf.interactive_audio.core.contracts import (
    AcousticMaterial,
    AcousticRaycastResult,
    MATERIAL_ABSORPTION_TABLE,
    MaterialAbsorption,
    OcclusionState,
    RoomAcousticProfile,
)


class SabineEyringAcousticCalculator:
    """
    Computes analytical physical acoustic parameters of 3D architectural spaces
    using the classical Sabine and Eyring reverberation equations.
    """

    SPEED_OF_SOUND_MPS: float = 343.0  # Speed of sound in dry air at 20°C (m/s)

    @classmethod
    def calculate_room_profile(
        cls,
        room_id: str,
        dimensions_m: Tuple[float, float, float],
        materials: Dict[AcousticMaterial, float],
    ) -> RoomAcousticProfile:
        """
        Evaluates room volume, surface area, frequency-dependent absorption,
        Sabine/Eyring RT60 decay, and fundamental axial standing wave resonances.
        """
        length, width, height = dimensions_m
        length = max(0.5, float(length))
        width = max(0.5, float(width))
        height = max(0.5, float(height))

        volume = length * width * height
        surface_area = 2.0 * (length * width + length * height + width * height)

        # Normalize material fractions
        total_frac = sum(materials.values())
        if total_frac <= 0.0:
            materials = {AcousticMaterial.CONCRETE: 1.0}
            total_frac = 1.0
        normalized_materials = {k: v / total_frac for k, v in materials.items()}

        # Compute average absorption for mid-frequencies (500-1000 Hz)
        alpha_bar_mid = 0.0
        for mat, frac in normalized_materials.items():
            alpha_mid = MATERIAL_ABSORPTION_TABLE[mat]["alpha_mid"]
            alpha_bar_mid += frac * alpha_mid

        alpha_bar_mid = max(0.005, min(0.99, alpha_bar_mid))

        # 1. Sabine Reverberation Time: RT60 = 0.161 * V / (S * alpha_bar)
        total_absorption_sabins = surface_area * alpha_bar_mid
        rt60_sabine = (0.161 * volume) / max(0.01, total_absorption_sabins)

        # 2. Eyring Reverberation Time: RT60 = 0.161 * V / (-S * ln(1 - alpha_bar))
        ln_term = -math.log(max(0.001, 1.0 - alpha_bar_mid))
        rt60_eyring = (0.161 * volume) / max(0.001, surface_area * ln_term)

        # 3. Axial Standing Wave Resonances (Modes along X, Y, Z axes up to n=2)
        c = cls.SPEED_OF_SOUND_MPS
        axial_modes: List[float] = []

        # (1,0,0), (0,1,0), (0,0,1)
        f_x1 = (c / 2.0) * (1.0 / length)
        f_y1 = (c / 2.0) * (1.0 / width)
        f_z1 = (c / 2.0) * (1.0 / height)
        axial_modes.extend([round(f_x1, 1), round(f_y1, 1), round(f_z1, 1)])

        # (2,0,0), (0,2,0), (0,0,2)
        axial_modes.extend([round(f_x1 * 2.0, 1), round(f_y1 * 2.0, 1), round(f_z1 * 2.0, 1)])
        axial_modes = sorted(list(set(axial_modes)))

        return RoomAcousticProfile(
            room_id=room_id,
            dimensions_m=(length, width, height),
            volume_m3=round(volume, 2),
            surface_area_m2=round(surface_area, 2),
            material_distribution=normalized_materials,
            rt60_sabine_seconds=round(rt60_sabine, 3),
            rt60_eyring_seconds=round(rt60_eyring, 3),
            axial_resonance_modes_hz=axial_modes,
        )


class TopologicalAcousticDiffraction:
    """
    Simulates sound propagation and barrier occlusion through topological level graphs.
    """

    CLOSED_DOOR_TRANSMISSION_LOSS_DB: float = 24.0  # Heavy acoustic barrier isolation
    CLOSED_DOOR_LOW_PASS_HZ: float = 800.0          # Muffled frequency cutoff
    PORTAL_TRANSMISSION_LOSS_DB: float = 6.0        # Corner diffraction loss
    PORTAL_LOW_PASS_HZ: float = 5000.0

    @classmethod
    def evaluate_path_occlusion(
        cls,
        source_pos: Tuple[float, float, float],
        listener_pos: Tuple[float, float, float],
        source_room_id: str,
        listener_room_id: str,
        path_distance_rooms: int = 0,
        doors_closed_along_path: int = 0,
    ) -> AcousticRaycastResult:
        """
        Calculates direct vs occluded acoustic transmission properties between
        a sound source and the audio listener.
        """
        # Euclidean distance
        dx = source_pos[0] - listener_pos[0]
        dy = source_pos[1] - listener_pos[1]
        dz = source_pos[2] - listener_pos[2]
        euclidean_dist = math.sqrt(dx * dx + dy * dy + dz * dz)

        # Same room: Direct Line-Of-Sight
        if source_room_id == listener_room_id:
            return AcousticRaycastResult(
                distance_m=round(euclidean_dist, 2),
                direct_path_clear=True,
                occlusion_state=OcclusionState.CLEAR_LOS,
                occlusion_alpha=0.0,
                transmission_loss_db=0.0,
                low_pass_cutoff_hz=20000.0,
            )

        # If doors are closed between rooms
        if doors_closed_along_path > 0:
            loss = cls.CLOSED_DOOR_TRANSMISSION_LOSS_DB * float(doors_closed_along_path)
            cutoff = max(100.0, cls.CLOSED_DOOR_LOW_PASS_HZ / (1.5 ** (doors_closed_along_path - 1)))
            return AcousticRaycastResult(
                distance_m=round(euclidean_dist, 2),
                direct_path_clear=False,
                occlusion_state=OcclusionState.FULL_OCCLUDED,
                occlusion_alpha=min(1.0, 0.85 + 0.05 * doors_closed_along_path),
                transmission_loss_db=round(loss, 1),
                low_pass_cutoff_hz=round(cutoff, 1),
            )

        # Open portal / corridor diffraction (1 room away)
        if path_distance_rooms == 1:
            return AcousticRaycastResult(
                distance_m=round(euclidean_dist, 2),
                direct_path_clear=False,
                occlusion_state=OcclusionState.PORTAL_DIFFRACTION,
                occlusion_alpha=0.35,
                transmission_loss_db=cls.PORTAL_TRANSMISSION_LOSS_DB,
                low_pass_cutoff_hz=cls.PORTAL_LOW_PASS_HZ,
            )

        # Multiple rooms away without line of sight
        mult_loss = cls.PORTAL_TRANSMISSION_LOSS_DB * float(path_distance_rooms) + 12.0
        return AcousticRaycastResult(
            distance_m=round(euclidean_dist, 2),
            direct_path_clear=False,
            occlusion_state=OcclusionState.PARTIALLY_OCCLUDED,
            occlusion_alpha=min(1.0, 0.40 + 0.10 * path_distance_rooms),
            transmission_loss_db=round(mult_loss, 1),
            low_pass_cutoff_hz=round(max(250.0, 3000.0 / float(path_distance_rooms)), 1),
        )
