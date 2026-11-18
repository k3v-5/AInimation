"""
Implementation models representing executable components binding capabilities to tools.
UAF-81.2 Sections 4, 23, 51, 52, 53.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


class ExecutionBackend(str, Enum):
    IN_PROCESS = "IN_PROCESS"
    BLENDER = "BLENDER"
    UNREAL = "UNREAL"
    EXTERNAL_TOOL = "EXTERNAL_TOOL"


@dataclass(frozen=True)
class ImplementationDescription:
    """
    Concrete component capable of executing an operation fulfilling a capability.
    """
    implementation_id: str
    capability_id: str
    backend_type: ExecutionBackend
    version: str = "1.0.0"
    name: str = ""
    executable: Optional[str] = None
    min_tool_version: Optional[str] = None
    arguments: List[str] = field(default_factory=list)
    timeout_seconds: float = 300.0
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    is_available: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "implementation_id": self.implementation_id,
            "capability_id": self.capability_id,
            "backend_type": self.backend_type.value,
            "version": self.version,
            "name": self.name,
            "executable": self.executable,
            "min_tool_version": self.min_tool_version,
            "arguments": self.arguments,
            "timeout_seconds": self.timeout_seconds,
            "resource_requirements": self.resource_requirements,
            "is_available": self.is_available,
        }
