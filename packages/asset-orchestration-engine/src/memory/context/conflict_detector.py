from typing import List, Dict, Any, Optional, Tuple
from ..core.memory_types import MemoryRecord, MemorySource, MemoryType

class ContextConflictDetector:
    """
    Detects and resolves memory contradictions based on authoritative source hierarchy:
    USER > PROJECT_CONSTRAINT > ASSET_CONSTRAINT > BLENDER > VALIDATION > DECISION > AGENT.
    """
    SOURCE_PRIORITY = {
        MemorySource.USER: 100,
        MemorySource.PROMPT_COMPILER: 90,
        MemorySource.BLENDER: 85,
        MemorySource.VALIDATION: 80,
        MemorySource.CRITIC: 75,
        MemorySource.STRATEGY_ENGINE: 70,
        MemorySource.REFERENCE_ANALYSIS: 65,
        MemorySource.SYSTEM: 60,
        MemorySource.RECOVERY: 55,
        MemorySource.AGENT: 40
    }

    def detect_conflicts(self, records: List[MemoryRecord]) -> List[Tuple[MemoryRecord, MemoryRecord, str]]:
        conflicts = []
        key_map: Dict[str, List[MemoryRecord]] = {}
        for r in records:
            # Check content keys like length, material, dimension
            for k in r.content.keys():
                key_id = f"{r.semantic_id}_{k}" if r.semantic_id else f"{r.project_id}_{k}"
                if key_id not in key_map:
                    key_map[key_id] = []
                key_map[key_id].append(r)

        for key_id, recs in key_map.items():
            if len(recs) > 1:
                # Check if values differ
                for i in range(len(recs)):
                    for j in range(i + 1, len(recs)):
                        val_i = recs[i].content
                        val_j = recs[j].content
                        if val_i != val_j:
                            conflicts.append((recs[i], recs[j], f"Contradictory values for {key_id}"))
        return conflicts

    def resolve_conflict(self, rec_a: MemoryRecord, rec_b: MemoryRecord) -> MemoryRecord:
        # Priority 1: Source Hierarchy
        pri_a = self.SOURCE_PRIORITY.get(rec_a.source, 50)
        pri_b = self.SOURCE_PRIORITY.get(rec_b.source, 50)
        if pri_a > pri_b:
            return rec_a
        elif pri_b > pri_a:
            return rec_b

        # Priority 2: Confidence
        if rec_a.confidence > rec_b.confidence:
            return rec_a
        elif rec_b.confidence > rec_a:
            return rec_b

        # Priority 3: Recency (newer wins)
        if rec_a.updated_at >= rec_b.updated_at:
            return rec_a
        return rec_b
