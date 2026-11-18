"""
ConfigResolver implements the 5-level configuration precedence rule:
DEFAULT -> PROJECT -> ENVIRONMENT -> RUNTIME -> OPERATION
UAF-81.0 Section 35.
"""

from typing import Dict, Any, Optional
from .uaf_config import UAFConfig


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges override into base, returning a new dictionary.
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigResolver:
    """
    Resolves configuration values across all 5 precedence layers deterministically.
    """
    @classmethod
    def resolve(
        cls,
        default_cfg: Optional[Dict[str, Any]] = None,
        project_cfg: Optional[Dict[str, Any]] = None,
        environment_cfg: Optional[Dict[str, Any]] = None,
        runtime_cfg: Optional[Dict[str, Any]] = None,
        operation_cfg: Optional[Dict[str, Any]] = None,
    ) -> UAFConfig:
        """
        Applies layers in strict ascending precedence:
        1. DEFAULT
        2. PROJECT
        3. ENVIRONMENT
        4. RUNTIME
        5. OPERATION
        """
        base = default_cfg or UAFConfig.create_default().to_dict()

        if project_cfg:
            base = deep_merge(base, project_cfg)
        if environment_cfg:
            base = deep_merge(base, environment_cfg)
        if runtime_cfg:
            base = deep_merge(base, runtime_cfg)
        if operation_cfg:
            base = deep_merge(base, operation_cfg)

        return UAFConfig.from_dict(base)
