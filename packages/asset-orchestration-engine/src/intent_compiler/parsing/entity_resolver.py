from typing import Dict, List, Optional, Tuple
from ..core.intent_schema import RequestContext

class EntityResolver:
    @staticmethod
    def resolve_entity(target_keyword: str, context: RequestContext) -> Tuple[bool, Optional[str], str]:
        tk = target_keyword.lower()
        matching_ids = [eid for eid, etype in context.available_entities.items() if tk in eid or tk in etype.lower()]

        if len(matching_ids) == 1:
            return True, matching_ids[0], f"Resolved '{target_keyword}' to '{matching_ids[0]}'."
        elif len(matching_ids) > 1:
            return False, None, f"TARGET_AMBIGUITY: Multiple entities match '{target_keyword}' ({matching_ids}). Please specify target ID."
        else:
            return True, None, "No specific scene entity resolved (creating new asset)."
