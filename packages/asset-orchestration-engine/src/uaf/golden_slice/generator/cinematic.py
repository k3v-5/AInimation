"""Cinematic sequence, camera roles, and gameplay transition generator."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass
class CinematicKeyframe:
    frame: int
    camera_location: Tuple[float, float, float]
    camera_rotation: Tuple[float, float, float]
    fov: float
    trigger_event: str = ""


@dataclass
class CinematicSlice:
    sequence_id: str
    duration_frames: int
    fps: float
    camera_modes: List[str] = field(default_factory=lambda: [
        "third_person",
        "combat_camera",
        "cinematic_camera",
        "aim_camera",
        "death_camera",
    ])
    keyframes: List[CinematicKeyframe] = field(default_factory=list)
    has_transition_to_gameplay: bool = True

    def validate(self) -> List[str]:
        errors: List[str] = []
        if len(self.keyframes) < 2:
            errors.append("Cinematic sequence has fewer than 2 keyframes")
        if not self.has_transition_to_gameplay:
            errors.append("Cinematic sequence missing gameplay transition trigger")
        return errors


class CinematicGenerator:
    """Generates cinematic intro sequence with camera movement and gameplay handover."""

    def generate(self) -> CinematicSlice:
        keyframes = [
            CinematicKeyframe(0, (0.0, -500.0, 300.0), (0.0, -15.0, 90.0), 65.0, "VFX_IntroFog"),
            CinematicKeyframe(75, (0.0, -300.0, 220.0), (0.0, -10.0, 90.0), 55.0, "AUDIO_HeroDialogue"),
            CinematicKeyframe(150, (0.0, -180.0, 160.0), (0.0, -5.0, 90.0), 50.0, "ANIM_HeroDrawWeapon"),
            CinematicKeyframe(200, (0.0, -150.0, 150.0), (0.0, 0.0, 90.0), 60.0, "EVENT_TransitionToGameplay"),
        ]

        return CinematicSlice(
            sequence_id="seq_intro_cinematic",
            duration_frames=200,
            fps=30.0,
            keyframes=keyframes,
            has_transition_to_gameplay=True,
        )
