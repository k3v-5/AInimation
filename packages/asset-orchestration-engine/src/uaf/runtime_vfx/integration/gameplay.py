"""
UAF-81.84.8: Gameplay, Physics and Audio Event Integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..emitter.emitter import VFXEmitter
from ..graph.events import VFXEvent, VFXEventBus
from ..math.operators import vec3_add
from ..models.definition import Vec3, ensure_finite_vec3


@dataclass
class VFXAttachment:
    """Attaches a VFX emitter to an entity, bone or world transform."""
    parent_entity_id: Optional[str]
    local_offset: Vec3 = (0.0, 0.0, 0.0)
    world_position: Vec3 = (0.0, 0.0, 0.0)

    def update_transform(self, parent_world_pos: Vec3) -> Vec3:
        self.world_position = vec3_add(parent_world_pos, self.local_offset)
        return self.world_position


class GameplayVFXBridge:
    """
    Connects high-level gameplay events (weapon fire, damage, footstep, explosion)
    and physical impacts to VFX systems, and emits audio references.
    """

    def __init__(self, event_bus: VFXEventBus):
        self.event_bus = event_bus
        self.audio_triggers: List[Dict[str, Any]] = []

    def on_impact(self, position: Vec3, normal: Vec3, surface_type: str, hit_entity_id: Optional[str] = None) -> VFXEvent:
        """Trigger physical impact VFX event."""
        pos = ensure_finite_vec3(position, "GameplayVFXBridge.on_impact")
        norm = ensure_finite_vec3(normal, "GameplayVFXBridge.on_impact normal")

        event = VFXEvent(
            event_id=f"evt_impact_{len(self.audio_triggers) + 1}",
            tick=0,
            event_type="OnImpact",
            position=pos,
            normal=norm,
            payload={
                "surface_type": surface_type,
                "hit_entity_id": hit_entity_id,
            },
        )
        self.event_bus.post_event(event)

        # Emit associated audio trigger reference (without duplicating audio runtime)
        self.audio_triggers.append({
            "audio_event_name": f"Play_Impact_{surface_type}",
            "position": pos,
        })
        return event

    def on_weapon_fire(self, muzzle_pos: Vec3, direction: Vec3, weapon_type: str) -> VFXEvent:
        """Trigger weapon muzzle flash / projectile trail event."""
        event = VFXEvent(
            event_id=f"evt_fire_{len(self.audio_triggers) + 1}",
            tick=0,
            event_type="OnWeaponFire",
            position=ensure_finite_vec3(muzzle_pos, "on_weapon_fire"),
            normal=ensure_finite_vec3(direction, "on_weapon_fire dir"),
            payload={"weapon_type": weapon_type},
        )
        self.event_bus.post_event(event)
        return event

    def on_explosion(self, position: Vec3, blast_radius: float, damage: float) -> VFXEvent:
        """Trigger explosion cascade."""
        pos = ensure_finite_vec3(position, "on_explosion")
        event = VFXEvent(
            event_id=f"evt_expl_{len(self.audio_triggers) + 1}",
            tick=0,
            event_type="OnExplosion",
            position=pos,
            payload={"blast_radius": blast_radius, "damage": damage},
        )
        self.event_bus.post_event(event)

        self.audio_triggers.append({
            "audio_event_name": "Play_Explosion_Default",
            "position": pos,
        })
        return event
