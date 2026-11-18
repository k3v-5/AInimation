"""Spatialized audio and music cues generator for the vertical slice."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

from uaf.golden_slice.manifest.seeds import SeedManager


@dataclass
class SoundCueDescriptor:
    cue_id: str
    semantic_name: str
    bus: str  # "SFX", "Music", "Voice", "Ambience"
    is_spatialized: bool = True
    attenuation_radius_m: float = 30.0
    volume_multiplier: float = 1.0
    pitch_multiplier: float = 1.0
    is_looping: bool = False


@dataclass
class AudioSlice:
    cues: Dict[str, SoundCueDescriptor] = field(default_factory=dict)
    active_buses: List[str] = field(default_factory=lambda: ["Master", "SFX", "Music", "Voice", "Ambience"])

    def validate(self) -> List[str]:
        errors: List[str] = []
        required_cues = ["footsteps", "weapons", "impacts", "ambient", "environment", "ui", "music", "voice"]
        for req in required_cues:
            if req not in self.cues:
                errors.append(f"Missing required audio cue '{req}'")
        return errors


class AudioGenerator:
    """Generates 3D spatialized sound cues and bus routing."""

    def __init__(self, seeds: SeedManager) -> None:
        self.rng = seeds.get_rng("audio")

    def generate(self) -> AudioSlice:
        cue_data = [
            ("footsteps", "SC_Player_Footsteps", "SFX", True, 20.0, 0.8, 1.0, False),
            ("weapons", "SC_Weapon_Swing", "SFX", True, 25.0, 1.0, 1.0, False),
            ("impacts", "SC_Flesh_Impact", "SFX", True, 30.0, 1.0, 1.0, False),
            ("ambient", "SC_Forest_Wind", "Ambience", False, 100.0, 0.6, 1.0, True),
            ("environment", "SC_River_Waterflow", "Ambience", True, 45.0, 0.7, 1.0, True),
            ("ui", "SC_Menu_Click", "SFX", False, 0.0, 0.9, 1.0, False),
            ("music", "SC_Combat_OST_Theme", "Music", False, 0.0, 0.8, 1.0, True),
            ("voice", "SC_Hero_Efforts", "Voice", True, 25.0, 1.0, 1.0, False),
        ]

        cues: Dict[str, SoundCueDescriptor] = {}
        for key, name, bus, spat, radius, vol, pitch, loop in cue_data:
            cues[key] = SoundCueDescriptor(
                cue_id=key,
                semantic_name=name,
                bus=bus,
                is_spatialized=spat,
                attenuation_radius_m=radius,
                volume_multiplier=vol,
                pitch_multiplier=pitch,
                is_looping=loop,
            )

        return AudioSlice(cues=cues)
