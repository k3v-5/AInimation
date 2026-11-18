"""
UAF-81.92: Advanced Multi-Agent NPC Ecosystem, Cognitive GOAP, Squad Tactics & Faction Reputation.
Decoupled, deterministic cognitive AI planning, squad coordination, and Unreal Engine 5 StateTree export.
"""

from uaf.ai.core import (
    FactionId,
    DispositionType,
    TacticalRole,
    StimulusType,
    PerceptionStimulus,
    WorldState,
    GOAPAction,
    GOAPGoal,
)
from uaf.ai.goap import (
    GOAPPlan,
    GOAPPlanner,
)
from uaf.ai.squad import (
    SquadMember,
    SquadBlackboard,
    Squad,
)
from uaf.ai.perception import (
    TrackedThreat,
    PerceptionSensor,
)
from uaf.ai.faction import (
    FactionReputationMatrix,
)
from uaf.ai.export import (
    StateTreeTaskSchema,
    StateTreeNodeSchema,
    UE5StateTreeManifest,
    UE5AIExporter,
)

__all__ = [
    # Core
    "FactionId",
    "DispositionType",
    "TacticalRole",
    "StimulusType",
    "PerceptionStimulus",
    "WorldState",
    "GOAPAction",
    "GOAPGoal",
    # GOAP
    "GOAPPlan",
    "GOAPPlanner",
    # Squad
    "SquadMember",
    "SquadBlackboard",
    "Squad",
    # Perception
    "TrackedThreat",
    "PerceptionSensor",
    # Faction
    "FactionReputationMatrix",
    # Export
    "StateTreeTaskSchema",
    "StateTreeNodeSchema",
    "UE5StateTreeManifest",
    "UE5AIExporter",
]
