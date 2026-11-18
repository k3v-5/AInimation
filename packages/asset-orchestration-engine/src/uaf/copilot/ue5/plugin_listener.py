"""
UAF-81.95: Unreal Engine 5 Co-Pilot In-Editor Listener Companion.
Receives live sync deltas, dispatches actor updates into the UE5 Slate/Editor loop,
and captures designer viewport transformations for feedback reporting.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from uaf.copilot.core.contracts import (
    CoPilotCommandType,
    CoPilotMessage,
    LiveActorSync,
    Transform3D,
    Vector3D,
    Rotator3D,
)
from uaf.copilot.protocol.messages import MessageBuilder, serialize_message, deserialize_message


class UE5CoPilotListener:
    """
    Editor-side companion module running within the Unreal Engine Python runtime.
    Bridges between the external aoe-copilot-daemon and Unreal's EditorActorSubsystem.
    """

    def __init__(self, daemon_host: str = "127.0.0.1", daemon_port: int = 27182):
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.is_active: bool = False
        self.applied_actors: Dict[str, LiveActorSync] = {}

    def handle_incoming_sync_command(self, raw_json: str) -> str:
        """
        Processes an incoming JSON string from the daemon and produces an ACK string.
        """
        msg = deserialize_message(raw_json)

        if msg.command_type == CoPilotCommandType.SYNC_SPAWNER_AI:
            actors_data = msg.payload.get("actors", [])
            for a_dict in actors_data:
                actor = LiveActorSync(**a_dict)
                self.applied_actors[actor.actor_id] = actor
            ack = MessageBuilder.build_ack(
                reply_to_id=msg.message_id,
                sender="UE5_EDITOR_LISTENER",
                details={"applied_count": len(actors_data)},
            )
            return serialize_message(ack)

        elif msg.command_type == CoPilotCommandType.SYNC_TERRAIN_REGION:
            ack = MessageBuilder.build_ack(
                reply_to_id=msg.message_id,
                sender="UE5_EDITOR_LISTENER",
                details={"status": "VIEWPORT_TERRAIN_UPDATED"},
            )
            return serialize_message(ack)

        # Default fallback
        ack = MessageBuilder.build_ack(
            reply_to_id=msg.message_id,
            sender="UE5_EDITOR_LISTENER",
        )
        return serialize_message(ack)

    def report_designer_actor_moved(
        self,
        actor_id: str,
        location_cm: Tuple[float, float, float],
        rotation_deg: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        lock_designer: bool = True,
    ) -> CoPilotMessage:
        """
        Generates a feedback message when a human designer moves an actor
        in the Unreal Editor viewport. Coordinates in cm are automatically
        converted to meters.
        """
        pos_m = Vector3D.from_ue5_cm(location_cm[0], location_cm[1], location_cm[2])
        rot = Rotator3D(pitch=rotation_deg[0], yaw=rotation_deg[1], roll=rotation_deg[2])
        transform = Transform3D(position=pos_m, rotation=rot)

        return MessageBuilder.build_feedback_transform(
            actor_id=actor_id,
            new_transform=transform,
            lock_designer=lock_designer,
            sender="UE5_EDITOR_VIEWPORT",
        )

    @classmethod
    def generate_editor_runner_script(cls) -> str:
        """
        Produces standalone Python script for running the listener
        inside Unreal Engine Editor's Python console.
        """
        return '''"""
Autonomous UE5 In-Editor Co-Pilot Hook for UAF-81.95.
Attaches to editor viewport and communicates with aoe-copilot-daemon.
"""

import unreal

class EditorCoPilotRunner:
    def __init__(self):
        self.actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        print("[AOE Co-Pilot] Attached to Unreal Editor Actor Subsystem.")

    def apply_actor_transform(self, actor_label, pos_cm, rot_deg):
        actors = self.actor_subsystem.get_all_level_actors()
        for a in actors:
            if a.get_actor_label() == actor_label:
                new_loc = unreal.Vector(pos_cm[0], pos_cm[1], pos_cm[2])
                new_rot = unreal.Rotator(rot_deg[0], rot_deg[1], rot_deg[2])
                a.set_actor_location_and_rotation(new_loc, new_rot, False, True)
                print(f"[AOE Co-Pilot] Live updated {actor_label} transform.")
                return True
        return False

if __name__ == "__main__":
    runner = EditorCoPilotRunner()
'''
