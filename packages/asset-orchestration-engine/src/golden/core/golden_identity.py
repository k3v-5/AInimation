import re
from typing import Tuple

class GoldenIdentityHelper:
    """Utilities for generating and parsing standardized golden asset identities."""

    @staticmethod
    def generate_golden_id(semantic_id: str, version: int = 1) -> str:
        clean_sem = semantic_id.strip().lower()
        return f"golden.{clean_sem}.v{version}"

    @staticmethod
    def parse_golden_id(golden_id: str) -> Tuple[str, int]:
        m = re.match(r"^golden\.(.+)\.v(\d+)$", golden_id.strip())
        if not m:
            raise ValueError(f"Invalid golden_id format: '{golden_id}'. Expected 'golden.<semantic_id>.v<version>'")
        semantic_id = m.group(1)
        version = int(m.group(2))
        return semantic_id, version

    @staticmethod
    def next_golden_id(current_golden_id: str) -> str:
        sem_id, ver = GoldenIdentityHelper.parse_golden_id(current_golden_id)
        return GoldenIdentityHelper.generate_golden_id(sem_id, ver + 1)
