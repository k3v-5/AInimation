"""
UAF-81.92: Multi-Agent Squad Tactics, Tactical Roles & Coordinated Maneuvers.
Implements squad blackboard communication, bounding overwatch (leapfrogging),
flanking route geometry (>= 60 deg separation), and door breach synchronization.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from uaf.ai.core.contracts import TacticalRole, WorldState


class SquadMember(BaseModel):
    """Discrete agent participating in squad tactical maneuvers."""
    agent_id: str
    role: TacticalRole
    world_pos: Tuple[float, float, float]  # [X, Y, Z] in Unreal cm
    health_pct: float = 1.0
    is_suppressing: bool = False
    is_moving: bool = False
    current_order: str = "IDLE"


class SquadBlackboard(BaseModel):
    """Shared tactical memory and threat awareness across squad members."""
    threat_target_id: Optional[str] = None
    threat_world_pos: Optional[Tuple[float, float, float]] = None
    threat_forward_vector: Tuple[float, float, float] = (1.0, 0.0, 0.0)
    is_threat_suppressed: bool = False
    assigned_flank_pos: Optional[Tuple[float, float, float]] = None
    active_maneuver: str = "PATROL"


class Squad(BaseModel):
    """
    Tactical unit coordinating multi-agent maneuvers across level geometry.
    """
    squad_id: str
    leader_id: str
    members: Dict[str, SquadMember] = Field(default_factory=dict)
    blackboard: SquadBlackboard = Field(default_factory=SquadBlackboard)

    def add_member(self, member: SquadMember) -> None:
        self.members[member.agent_id] = member

    def get_member_by_role(self, role: TacticalRole) -> Optional[SquadMember]:
        for m in self.members.values():
            if m.role == role:
                return m
        return None

    def execute_bounding_overwatch(self, advance_target_pos: Tuple[float, float, float]) -> Dict[str, str]:
        """
        Coordinates leapfrogging / bounding overwatch between Pointman and Suppressor.
        Returns dictionary of orders issued to members: {agent_id: order_string}.
        """
        orders: Dict[str, str] = {}
        pointman = self.get_member_by_role(TacticalRole.POINTMAN)
        suppressor = self.get_member_by_role(TacticalRole.SUPPRESSOR)

        if not pointman or not suppressor:
            # Fallback for solo/incomplete squad
            for m in self.members.values():
                orders[m.agent_id] = "ADVANCE_CAUTIOUSLY"
            return orders

        # Suppressor provides continuous covering fire
        suppressor.is_suppressing = True
        suppressor.is_moving = False
        suppressor.current_order = "PROVIDE_COVERING_FIRE"
        orders[suppressor.agent_id] = "PROVIDE_COVERING_FIRE"
        self.blackboard.is_threat_suppressed = True

        # Pointman bounds forward under cover of suppressor
        pointman.is_suppressing = False
        pointman.is_moving = True
        pointman.current_order = f"BOUND_FORWARD_TO_{advance_target_pos}"
        orders[pointman.agent_id] = f"BOUND_FORWARD_TO_{advance_target_pos}"

        self.blackboard.active_maneuver = "BOUNDING_OVERWATCH"
        return orders

    def select_flanking_position(
        self,
        candidate_positions: List[Tuple[float, float, float]],
        min_angle_deg: float = 60.0,
    ) -> Optional[Tuple[float, float, float]]:
        """
        Evaluates candidate positions and selects a flanking location that attacks
        from outside the threat's front view arc (angular separation >= min_angle_deg).
        """
        if not self.blackboard.threat_world_pos:
            return candidate_positions[0] if candidate_positions else None

        tx, ty, _ = self.blackboard.threat_world_pos
        fx, fy, _ = self.blackboard.threat_forward_vector
        f_len = math.hypot(fx, fy)
        if f_len > 1e-5:
            fx /= f_len
            fy /= f_len
        else:
            fx, fy = 1.0, 0.0

        cos_threshold = math.cos(math.radians(min_angle_deg))
        valid_flanks: List[Tuple[float, float, float]] = []

        for cand in candidate_positions:
            cx, cy, _ = cand
            dx, dy = cx - tx, cy - ty
            dist = math.hypot(dx, dy)

            if dist < 1e-4:
                continue

            dx /= dist
            dy /= dist

            # Dot product with threat forward vector
            dot = (dx * fx) + (dy * fy)

            # If dot <= cos_threshold, angle is >= min_angle_deg (outside front arc)
            if dot <= cos_threshold:
                valid_flanks.append(cand)

        if valid_flanks:
            chosen = valid_flanks[0]
            self.blackboard.assigned_flank_pos = chosen
            flanker = self.get_member_by_role(TacticalRole.FLANKER)
            if flanker:
                flanker.current_order = f"FLANK_TO_{chosen}"
            return chosen

        return None

    def coordinate_breach(self, door_location: Tuple[float, float, float]) -> Dict[str, str]:
        """
        Coordinates a tactical room breach sequence on a WFC interior door:
        Pointman breaches, Suppressor covers long hallway, Flanker enters to clear blind corner.
        """
        orders: Dict[str, str] = {}
        for m in self.members.values():
            if m.role == TacticalRole.POINTMAN:
                m.current_order = "BREACH_DOOR"
                orders[m.agent_id] = "BREACH_DOOR"
            elif m.role == TacticalRole.FLANKER:
                m.current_order = "CLEAR_CORNER_LEFT"
                orders[m.agent_id] = "CLEAR_CORNER_LEFT"
            elif m.role == TacticalRole.SUPPRESSOR:
                m.current_order = "COVER_HALLWAY_CENTER"
                orders[m.agent_id] = "COVER_HALLWAY_CENTER"
            else:
                m.current_order = "STACK_REAR_GUARD"
                orders[m.agent_id] = "STACK_REAR_GUARD"

        self.blackboard.active_maneuver = "ROOM_BREACH"
        return orders
