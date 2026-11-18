from typing import Dict, Any, List, Set
from ..core.adaptive_types import ScopeLevel

class PartialRegenerator:
    # Grafo de Dependencias de Componentes
    DEPENDENCY_GRAPH: Dict[str, List[str]] = {
        "foundation": ["walls"],
        "walls": ["roof", "door", "windows"],
        "roof": ["chimney"],
        "door": [],
        "windows": [],
        "chimney": []
    }

    @classmethod
    def determine_dirty_components(
        cls,
        changed_parameter: str,
        scope: ScopeLevel = ScopeLevel.PARAMETER
    ) -> List[str]:
        if "roof" in changed_parameter:
            # Component Isolation: Solo el tejado es dirty
            return ["roof"]
        elif "window" in changed_parameter:
            # Solo las ventanas son dirty
            return ["windows"]
        elif "door" in changed_parameter:
            return ["door"]
        elif "width" in changed_parameter or "depth" in changed_parameter:
            # Propagación Topológica: fundación, muros, tejado
            return ["foundation", "walls", "roof"]
        elif "wall_height" in changed_parameter:
            return ["walls", "roof", "windows"]
        else:
            return ["roof"]
