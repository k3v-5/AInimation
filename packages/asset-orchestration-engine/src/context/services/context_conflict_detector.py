import time
from typing import List, Dict, Any, Optional, Tuple
from ..core.context_models import ContextConflict, ConflictStatus
from ...memory.core.memory_types import MemoryRecord, MemorySource

class ContextConflictDetector:
    """
    Detects and manages contradictions across memory records and context parameters.
    """
    SOURCE_PRIORITY = {
        MemorySource.USER: 100,
        MemorySource.PROMPT_COMPILER: 90,
        MemorySource.BLENDER: 85,
        MemorySource.VALIDATION: 80,
        MemorySource.AOE: 70,
        MemorySource.REFERENCE_ANALYSIS: 65,
        MemorySource.RECOVERY: 55,
        MemorySource.AGENT: 40
    }

    def __init__(self):
        self._conflicts: List[ContextConflict] = []

    def detect_conflicts(self, records: List[MemoryRecord]) -> List[ContextConflict]:
        conflicts = []
        key_map: Dict[str, List[MemoryRecord]] = {}
        for r in records:
            for k in r.content.keys():
                key_id = f"{r.semantic_id}_{k}" if r.semantic_id else f"{r.project_id}_{k}"
                if key_id not in key_map:
                    key_map[key_id] = []
                key_map[key_id].append(r)

        for key_id, recs in key_map.items():
            if len(recs) > 1:
                for i in range(len(recs)):
                    for j in range(i + 1, len(recs)):
                        val_i = recs[i].content
                        val_j = recs[j].content
                        if val_i != val_j:
                            conflict = ContextConflict(
                                conflict_id=f"CONF_{int(time.time()*1000)%100000}",
                                memory_a_id=recs[i].memory_id,
                                memory_b_id=recs[j].memory_id,
                                conflict_type=f"CONTRADICTION_{key_id}",
                                severity="HIGH"
                            )
                            conflicts.append(conflict)
                            self._conflicts.append(conflict)
        return conflicts

    def resolve_conflict(self, conflict: ContextConflict, record_a: MemoryRecord, record_b: MemoryRecord) -> MemoryRecord:
        pri_a = self.SOURCE_PRIORITY.get(record_a.source, 50)
        pri_b = self.SOURCE_PRIORITY.get(record_b.source, 50)
        winner = record_a if pri_a >= pri_b else record_b
        
        conflict.resolution_status = ConflictStatus.RESOLVED
        conflict.resolution_details = {
            "winner_memory_id": winner.memory_id,
            "winner_source": winner.source.value,
            "resolved_at": time.time()
        }
        return winner

    def list_conflicts(self) -> List[ContextConflict]:
        return list(self._conflicts)
