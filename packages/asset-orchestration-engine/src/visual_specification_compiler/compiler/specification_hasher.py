import hashlib
import json
from typing import Dict, Any

class SpecificationHasher:
    @classmethod
    def compute_hash(cls, vas_dict: Dict[str, Any]) -> str:
        # Excluir campos volátiles que no alteran el contenido semántico
        excluded_keys = {"specification_id", "specification_hash", "compilation_metadata", "timestamp"}
        logical_content = {k: v for k, v in vas_dict.items() if k not in excluded_keys}
        
        # Serializar con claves ordenadas determinísticamente
        serialized = json.dumps(logical_content, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
