from typing import List, Optional, Dict, Any

class ClarificationManager:
    @staticmethod
    def generate_ambiguity_question(target_name: str, candidates: List[str]) -> str:
        options_str = " o ".join([f"'{c}'" for c in candidates])
        return f"¿Cuál elemento '{target_name}' deseas modificar: {options_str}?"

    @staticmethod
    def generate_missing_target_question(asset_id: str, available_components: List[str]) -> str:
        comps_str = ", ".join([f"'{c}'" for c in available_components])
        return f"No se especificó qué componente de '{asset_id}' modificar. Componentes disponibles: {comps_str}."
