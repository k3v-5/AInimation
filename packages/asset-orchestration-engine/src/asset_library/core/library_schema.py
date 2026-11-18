from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

Tuple_3 = Tuple[float, float, float]

class ParameterVisibility(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    SYSTEM = "SYSTEM"

@dataclass
class SocketDefinition:
    socket_id: str
    socket_type: str # BLADE_SOCKET, GRIP_SOCKET, POMMEL_SOCKET
    transform: Tuple_3 = (0.0, 0.0, 0.0)
    allowed_components: List[str] = field(default_factory=list)

@dataclass
class ComponentDefinition:
    component_id: str
    category: str # blade, guard, handle, pommel
    version: str = "1.0.0"
    parameters: Dict[str, Any] = field(default_factory=dict)
    sockets: Dict[str, SocketDefinition] = field(default_factory=dict)
    materials: Dict[str, Any] = field(default_factory=dict)
    status: str = "PRODUCTION" # EXPERIMENTAL, VALIDATED, PRODUCTION

@dataclass
class VariantDefinition:
    variant_id: str # e.g. Medieval, Fantasy, SciFi
    template_id: str
    component_selection: Dict[str, str] = field(default_factory=dict) # category -> component_id
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)
    style_rules: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PresetDefinition:
    preset_id: str # e.g. ShortSword, LongSword, HeavySword
    template_id: str
    parameter_overrides: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildIntent:
    template_id: str
    variant_id: Optional[str] = None
    preset_id: Optional[str] = None
    component_overrides: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    user_overrides: Dict[str, Any] = field(default_factory=dict)
    seed: int = 42

@dataclass
class ResolvedBuildSpec:
    spec_id: str
    template_id: str
    template_version: str
    variant_id: str
    preset_id: Optional[str]
    components: Dict[str, ComponentDefinition]
    resolved_parameters: Dict[str, Any]
    dependency_lock: Dict[str, str]
    manifest_hash: str = ""

@dataclass
class BuildManifest:
    manifest_id: str
    manifest_hash: str
    template_id: str
    template_version: str
    component_versions: Dict[str, str]
    parameters: Dict[str, Any]
    seed: int
