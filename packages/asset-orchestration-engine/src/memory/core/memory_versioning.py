from typing import Dict, List, Optional
from .memory_types import MemoryRecord, MemoryStatus

class MemoryVersionManager:
    """Manages immutable version chains and supersession of memory records."""
    def __init__(self):
        self._version_chains: Dict[str, List[str]] = {}

    def register_version(self, root_key: str, memory_id: str):
        if root_key not in self._version_chains:
            self._version_chains[root_key] = []
        self._version_chains[root_key].append(memory_id)

    def get_history(self, root_key: str) -> List[str]:
        return list(self._version_chains.get(root_key, []))

    def create_superseded_version(self, old_record: MemoryRecord, new_record: MemoryRecord) -> MemoryRecord:
        new_record.version = old_record.version + 1
        new_record.parent_memory_id = old_record.memory_id
        new_record.supersedes_memory_id = old_record.memory_id
        old_record.status = MemoryStatus.SUPERSEDED
        old_record.superseded_by = new_record.memory_id
        return new_record
