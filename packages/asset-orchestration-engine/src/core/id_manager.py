import uuid
import re

class IdManager:
    @staticmethod
    def generate_asset_id(prefix: str = "asset") -> str:
        short_hash = uuid.uuid4().hex[:6]
        clean_prefix = re.sub(r'[^a-zA-Z0-9_]', '_', prefix).lower()
        return f"{clean_prefix}_{short_hash}"

    @staticmethod
    def make_component_id(asset_id: str, comp_name: str) -> str:
        clean_comp = re.sub(r'[^a-zA-Z0-9_]', '_', comp_name).lower()
        return f"{asset_id}.{clean_comp}"

    @staticmethod
    def parse_component_id(full_id: str) -> tuple[str, str]:
        if "." in full_id:
            parts = full_id.split(".", 1)
            return parts[0], parts[1]
        return full_id, ""

    @staticmethod
    def generate_operation_id() -> str:
        short_hash = uuid.uuid4().hex[:8]
        return f"op_{short_hash}"

    @staticmethod
    def generate_task_id() -> str:
        short_hash = uuid.uuid4().hex[:8]
        return f"task_{short_hash}"
