import time
from typing import Dict, Any, List, Optional
from ..core.memory_schema import (
    AssetMemoryRecord, BuildMemoryRecord, CorrectionMemoryRecord,
    PatternRecord, FailureMemoryRecord, ReferenceMemoryRecord, ProjectMemoryRecord
)
from ..core.memory_types import PatternState

class MemoryStore:
    def __init__(self):
        self.asset_memory: Dict[str, AssetMemoryRecord] = {}
        self.build_memory: Dict[str, BuildMemoryRecord] = {}
        self.correction_memory: Dict[str, CorrectionMemoryRecord] = {}
        self.pattern_memory: Dict[str, PatternRecord] = {}
        self.failure_memory: Dict[str, FailureMemoryRecord] = {}
        self.reference_memory: Dict[str, ReferenceMemoryRecord] = {}
        self.project_memory: ProjectMemoryRecord = ProjectMemoryRecord("darx_project_default")
        self.audit_log: List[Dict[str, Any]] = []

    def save_pattern(self, pattern: PatternRecord):
        self.pattern_memory[pattern.pattern_id] = pattern
        self.audit_log.append({
            "action": "SAVE_PATTERN",
            "pattern_id": pattern.pattern_id,
            "state": pattern.state.value,
            "timestamp": time.time()
        })

    def get_pattern(self, pattern_id: str) -> Optional[PatternRecord]:
        return self.pattern_memory.get(pattern_id)

    def list_patterns(self) -> List[PatternRecord]:
        return list(self.pattern_memory.values())

    def delete_pattern(self, pattern_id: str):
        if pattern_id in self.pattern_memory:
            del self.pattern_memory[pattern_id]
            self.audit_log.append({
                "action": "DELETE_PATTERN",
                "pattern_id": pattern_id,
                "timestamp": time.time()
            })

    def save_asset(self, record: AssetMemoryRecord):
        self.asset_memory[record.asset_id] = record

    def save_build(self, record: BuildMemoryRecord):
        self.build_memory[record.build_id] = record

    def save_correction(self, record: CorrectionMemoryRecord):
        self.correction_memory[record.correction_id] = record

    def save_failure(self, record: FailureMemoryRecord):
        self.failure_memory[record.failure_id] = record

    def export_snapshot(self) -> Dict[str, Any]:
        return {
            "patterns": {k: vars(v) for k, v in self.pattern_memory.items()},
            "assets_count": len(self.asset_memory),
            "builds_count": len(self.build_memory),
            "audit_count": len(self.audit_log)
        }

    def reset_memory(self, scope: str = "ALL"):
        if scope in ["ALL", "PATTERN"]:
            self.pattern_memory.clear()
        if scope in ["ALL", "ASSET"]:
            self.asset_memory.clear()
        if scope in ["ALL", "BUILD"]:
            self.build_memory.clear()
        if scope in ["ALL", "FAILURE"]:
            self.failure_memory.clear()
