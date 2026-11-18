from typing import Dict, Any, List, Optional, Tuple

class SemanticDetector:
    @classmethod
    def detect_forbidden_components(
        cls,
        detected_components: List[str],
        forbidden_list: List[str]
    ) -> List[str]:
        found_forbidden = []
        for comp in detected_components:
            for forbidden in forbidden_list:
                if forbidden.lower() in comp.lower():
                    found_forbidden.append(comp)
        return found_forbidden
