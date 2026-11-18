from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class SlotAssignment:
    component_id: str
    material_id: str
    slot_index: int = 0
    slot_name: str = "default_slot"

class MaterialAssignmentManager:
    def __init__(self):
        self.assignments: Dict[str, SlotAssignment] = {} # comp_id -> SlotAssignment

    def assign_material(self, component_id: str, material_id: str, slot_index: int = 0, slot_name: str = "default_slot"):
        self.assignments[component_id] = SlotAssignment(
            component_id=component_id,
            material_id=material_id,
            slot_index=slot_index,
            slot_name=slot_name
        )

    def get_assignment(self, component_id: str) -> Optional[SlotAssignment]:
        return self.assignments.get(component_id)

    def list_assignments(self) -> List[SlotAssignment]:
        return list(self.assignments.values())
