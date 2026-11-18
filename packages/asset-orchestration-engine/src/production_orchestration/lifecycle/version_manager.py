from typing import Dict, Any, Optional

class VersionManager:
    """Manages immutable production asset versions without silent overwrites."""

    @staticmethod
    def format_version(semantic_id: str, version_number: int) -> str:
        return f"{semantic_id}.v{version_number:03d}"

    @staticmethod
    def get_next_version(current_version_str: Optional[str]) -> str:
        if not current_version_str or ".v" not in current_version_str:
            return "v001"
        try:
            num = int(current_version_str.split(".v")[-1])
            return f"v{num + 1:03d}"
        except Exception:
            return "v001"
