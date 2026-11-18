from typing import Dict, Set, List

class DirtyTracker:
    def __init__(self):
        self.states: Dict[str, str] = {} # component_id -> CLEAN, DIRTY, BUILDING, BUILT, INVALID, FAILED

    def mark_dirty(self, component_id: str):
        self.states[component_id] = "DIRTY"

    def mark_clean(self, component_id: str):
        self.states[component_id] = "CLEAN"

    def mark_built(self, component_id: str):
        self.states[component_id] = "BUILT"

    def get_status(self, component_id: str) -> str:
        return self.states.get(component_id, "CLEAN")

    def get_dirty_components(self) -> List[str]:
        return [cid for cid, st in self.states.items() if st == "DIRTY"]
