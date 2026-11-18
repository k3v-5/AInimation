from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class PropertyChange:
    actor_id: str
    property_name: str
    before: Any
    after: Any

@dataclass
class SceneDiff:
    added_actors: List[str] = field(default_factory=list)
    modified_actors: List[str] = field(default_factory=list)
    removed_actors: List[str] = field(default_factory=list)
    unchanged_actors: List[str] = field(default_factory=list)
    property_changes: List[PropertyChange] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "added_actors": self.added_actors,
            "modified_actors": self.modified_actors,
            "removed_actors": self.removed_actors,
            "unchanged_actors": self.unchanged_actors,
            "property_changes": [p.__dict__ for p in self.property_changes],
            "total_actors_affected": len(self.added_actors) + len(self.modified_actors) + len(self.removed_actors)
        }
