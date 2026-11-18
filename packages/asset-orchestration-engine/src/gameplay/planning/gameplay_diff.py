from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class GameplayDiff:
    added_capabilities: List[str] = field(default_factory=list)
    modified_data: List[Dict[str, Any]] = field(default_factory=list)
    added_interactions: List[str] = field(default_factory=list)
    unchanged_aspects: List[str] = field(default_factory=lambda: ["Mesh", "Material", "Transform", "Unrelated_Blueprints"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "added_capabilities": self.added_capabilities,
            "modified_data": self.modified_data,
            "added_interactions": self.added_interactions,
            "unchanged_aspects": self.unchanged_aspects
        }
