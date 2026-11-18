"""
UAF-81.82: Authoritative AI Agent Component Model.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from ..avoidance.steering import SteeringController
from ..behavior.tree import BehaviorTree
from ..models.definition import (
    AIAgentSnapshot,
    AIEntity,
    AILOD,
    AIPriority,
    AgentKinematics,
    Vec3,
    ensure_finite_vec3,
    vec3_distance,
)
from ..perception.damage import DamageSensor
from ..perception.hearing import HearingSensor
from ..perception.memory import SensoryMemory
from ..perception.vision import VisionSensor
from .blackboard import Blackboard


class AIAgent:
    """
    Authoritative runtime AI agent coordinating perception, decision-making,
    blackboard state, memory, and steering.
    """

    def __init__(
        self,
        agent_id: str,
        entity_id: str,
        position: Vec3 = (0.0, 0.0, 0.0),
        velocity: Vec3 = (0.0, 0.0, 0.0),
        radius: float = 0.5,
        height: float = 1.8,
        navigation_profile: str = "Default",
        team_id: str = "Neutral",
        lod: AILOD = AILOD.LOD0_FULL,
        priority: AIPriority = AIPriority.NORMAL,
    ):
        self.agent_id = agent_id
        self.entity_id = entity_id
        self.position = ensure_finite_vec3(position, f"AIAgent({agent_id}).position")
        self.velocity = ensure_finite_vec3(velocity, f"AIAgent({agent_id}).velocity")
        self.preferred_velocity: Vec3 = (0.0, 0.0, 0.0)
        self.radius = radius
        self.height = height
        self.navigation_profile = navigation_profile
        self.team_id = team_id
        self.lod = lod
        self.priority = priority
        self.enabled: bool = True

        # Components
        self.blackboard = Blackboard()
        self.behavior_tree: Optional[BehaviorTree] = None
        self.sensory_memory = SensoryMemory()
        self.vision_sensor = VisionSensor()
        self.hearing_sensor = HearingSensor()
        self.damage_sensor = DamageSensor()

        # Path following state
        self.current_path_points: Tuple[Vec3, ...] = ()
        self.current_waypoint_index: int = 0
        self.current_target_id: Optional[str] = None
        self.max_speed: float = 4.0
        self.max_acceleration: float = 10.0

    def seek_target(self, target_pos: Vec3, speed: Optional[float] = None) -> None:
        """Set preferred velocity toward target_pos using kinematic steering."""
        spd = speed if speed is not None else self.max_speed
        self.preferred_velocity = SteeringController.seek(self.position, target_pos, spd)

    def follow_active_path(self) -> None:
        """Advance steering along active path waypoints."""
        if not self.current_path_points:
            self.preferred_velocity = (0.0, 0.0, 0.0)
            return

        pref_vel, new_idx = SteeringController.follow_path(
            self.position,
            self.current_path_points,
            self.current_waypoint_index,
            self.max_speed,
            waypoint_radius=0.6,
        )
        self.preferred_velocity = pref_vel
        self.current_waypoint_index = new_idx

    def set_path(self, points: Tuple[Vec3, ...]) -> None:
        self.current_path_points = points
        self.current_waypoint_index = 0

    def clear_path(self) -> None:
        self.current_path_points = ()
        self.current_waypoint_index = 0
        self.preferred_velocity = (0.0, 0.0, 0.0)

    def to_kinematics(self) -> AgentKinematics:
        return AgentKinematics(
            position=self.position,
            velocity=self.velocity,
            preferred_velocity=self.preferred_velocity,
            max_speed=self.max_speed,
            max_acceleration=self.max_acceleration,
            radius=self.radius,
        )

    def to_entity(self) -> AIEntity:
        return AIEntity(
            entity_id=self.entity_id,
            agent_id=self.agent_id,
            position=self.position,
            velocity=self.velocity,
            radius=self.radius,
            height=self.height,
            navigation_profile=self.navigation_profile,
            team_id=self.team_id,
            enabled=self.enabled,
        )
