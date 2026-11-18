from typing import Dict, Any, List
from ..core.spec_schema import AssetSpec

class SpecTaskCompiler:
    @staticmethod
    def compile_spec_to_tasks(spec: AssetSpec) -> List[Dict[str, Any]]:
        tasks = [
            {
                "task_id": "T_WALLS",
                "task_type": "CREATE_WALLS",
                "implements": ["REQ-001", "REQ-002", "REQ-004"],
                "parameters": {"lean_angle_deg": spec.visual.lean_angle_deg}
            },
            {
                "task_id": "T_ROOF",
                "task_type": "CREATE_ROOF",
                "parent_id": "T_WALLS",
                "implements": ["REQ-001", "REQ-003"]
            },
            {
                "task_id": "T_DOOR",
                "task_type": "CREATE_DOOR",
                "parent_id": "T_WALLS",
                "implements": ["REQ-005", "REQ-008"],
                "parameters": {"width": spec.door.width_m, "material": spec.door.material}
            },
            {
                "task_id": "T_WINDOWS",
                "task_type": "CREATE_WINDOWS",
                "parent_id": "T_WALLS",
                "implements": ["REQ-006"],
                "parameters": {"count": spec.windows.count, "style": spec.windows.style}
            },
            {
                "task_id": "T_STAIRS",
                "task_type": "CREATE_STAIRS",
                "parent_id": "T_WALLS",
                "implements": ["REQ-007"],
                "parameters": {"location": spec.stairs.location, "destination": spec.stairs.destination}
            },
            {
                "task_id": "T_QA",
                "task_type": "VALIDATE_SPEC",
                "parent_id": "T_STAIRS",
                "validates": [req.req_id for req in spec.requirements]
            }
        ]
        return tasks
