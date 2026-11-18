"""
UAF-81.68: Universal Asset Inspector & Property Grid System - Models and Definitions.
Authoritative domain models, property descriptors, schemas, property paths,
editor descriptors, transactions, and diagnostic structures.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import math
import re
from typing import Any, Callable, ClassVar, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class PropertyType(str, Enum):
    BOOL = "BOOL"
    INT = "INT"
    UINT = "UINT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    STRING = "STRING"
    ENUM = "ENUM"
    COLOR = "COLOR"
    VECTOR2 = "VECTOR2"
    VECTOR3 = "VECTOR3"
    VECTOR4 = "VECTOR4"
    TRANSFORM = "TRANSFORM"
    OBJECT = "OBJECT"
    ARRAY = "ARRAY"
    MAP = "MAP"
    RESOURCE_REF = "RESOURCE_REF"
    ASSET_REF = "ASSET_REF"


class PropertyFlags(str, Enum):
    READ_ONLY = "READ_ONLY"
    HIDDEN = "HIDDEN"
    ADVANCED = "ADVANCED"
    OPTIONAL = "OPTIONAL"
    DEPRECATED = "DEPRECATED"
    REQUIRED = "REQUIRED"


class ValidationSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ValidationTiming(str, Enum):
    LIVE_VALIDATION = "LIVE_VALIDATION"
    COMMIT_VALIDATION = "COMMIT_VALIDATION"
    FULL_VALIDATION = "FULL_VALIDATION"


class ConflictPolicy(str, Enum):
    REJECT = "REJECT"
    RELOAD = "RELOAD"
    MERGE = "MERGE"
    FORCE = "FORCE"


class EditorHint(str, Enum):
    DEFAULT = "DEFAULT"
    SLIDER = "SLIDER"
    COLOR_PICKER = "COLOR_PICKER"
    DROPDOWN = "DROPDOWN"
    FILE_PICKER = "FILE_PICKER"
    MULTILINE_TEXT = "MULTILINE_TEXT"
    CHECKBOX = "CHECKBOX"
    SPINBOX = "SPINBOX"
    KEY_VALUE_TABLE = "KEY_VALUE_TABLE"


class MultiEditMode(str, Enum):
    UNIFORM = "UNIFORM"
    MIXED = "MIXED"


class InspectorTargetType(str, Enum):
    SINGLE_OBJECT = "SINGLE_OBJECT"
    COMPONENT = "COMPONENT"
    RESOURCE = "RESOURCE"
    ASSET = "ASSET"
    SCENE_NODE = "SCENE_NODE"
    MULTI_OBJECT = "MULTI_OBJECT"


# ==============================================================================
# MIXED VALUE SENTINEL
# ==============================================================================

class _MixedValueSentinel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_MixedValueSentinel, cls).__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<MIXED>"

    def __str__(self) -> str:
        return "<MIXED>"

    def __bool__(self) -> bool:
        return False


MIXED_VALUE = _MixedValueSentinel()


# ==============================================================================
# PROPERTY PATH
# ==============================================================================

@dataclass(frozen=True)
class PropertyPath:
    raw_path: str
    segments: Tuple[Union[str, int], ...] = field(default_factory=tuple)
    _cache: ClassVar[Dict[str, PropertyPath]] = {}

    @classmethod
    def parse(cls, path_str: str) -> PropertyPath:
        if not path_str or not isinstance(path_str, str):
            raise ValueError("PropertyPath must be a non-empty string.")

        if path_str in cls._cache:
            return cls._cache[path_str]

        # Security check: disallow traversal escapes like '..' or '__'
        if ".." in path_str or "__" in path_str:
            raise ValueError(f"Invalid path traversal attempt in PropertyPath: '{path_str}'.")

        # Parse dot notation and brackets: e.g. transform.position.x or items[0] or map["key"]
        tokens: List[Union[str, int]] = []
        pattern = re.compile(r'([a-zA-Z0-9_-]+)|\[([0-9]+)\]|\["([^"]+)"\]|\[\'([^\']+)\'\]')
        for match in pattern.finditer(path_str):
            if match.group(1):
                tokens.append(match.group(1))
            elif match.group(2) is not None:
                tokens.append(int(match.group(2)))
            elif match.group(3) is not None:
                tokens.append(match.group(3))
            elif match.group(4) is not None:
                tokens.append(match.group(4))

        if not tokens:
            raise ValueError(f"Failed to parse any valid segments from path: '{path_str}'.")

        instance = cls(raw_path=path_str, segments=tuple(tokens))
        cls._cache[path_str] = instance
        return instance

    @property
    def parent(self) -> Optional[PropertyPath]:
        if len(self.segments) <= 1:
            return None
        parent_segments = self.segments[:-1]
        parent_raw = ".".join(str(s) for s in parent_segments)
        return PropertyPath(raw_path=parent_raw, segments=parent_segments)

    @property
    def leaf(self) -> Union[str, int]:
        return self.segments[-1]

    def to_string(self) -> str:
        return self.raw_path


# ==============================================================================
# METADATA & DESCRIPTOR
# ==============================================================================

@dataclass
class PropertyMetadata:
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    precision: Optional[int] = None
    unit: str = ""
    max_length: Optional[int] = None
    multiline: bool = False
    regex: Optional[str] = None
    placeholder: str = ""
    enum_values: List[str] = field(default_factory=list)
    enum_labels: Dict[str, str] = field(default_factory=dict)
    allowed_types: List[str] = field(default_factory=list)
    nullable: bool = True
    tooltip: str = ""
    description: str = ""
    category: str = "General"
    order: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "min_value": self.min_value,
            "max_value": self.max_value,
            "step": self.step,
            "precision": self.precision,
            "unit": self.unit,
            "max_length": self.max_length,
            "multiline": self.multiline,
            "regex": self.regex,
            "placeholder": self.placeholder,
            "enum_values": list(self.enum_values),
            "enum_labels": dict(self.enum_labels),
            "allowed_types": list(self.allowed_types),
            "nullable": self.nullable,
            "tooltip": self.tooltip,
            "description": self.description,
            "category": self.category,
            "order": self.order,
        }


@dataclass
class PropertyDescriptor:
    property_id: str
    name: str
    display_name: str
    prop_type: PropertyType
    path: str
    flags: Set[PropertyFlags] = field(default_factory=set)
    default_value: Any = None
    metadata: PropertyMetadata = field(default_factory=PropertyMetadata)
    validator_fn: Optional[Callable[[Any], Tuple[bool, Optional[str]]]] = None
    editor_hint: EditorHint = EditorHint.DEFAULT

    @property
    def is_read_only(self) -> bool:
        return PropertyFlags.READ_ONLY in self.flags

    @property
    def is_hidden(self) -> bool:
        return PropertyFlags.HIDDEN in self.flags

    @property
    def is_advanced(self) -> bool:
        return PropertyFlags.ADVANCED in self.flags

    @property
    def is_deprecated(self) -> bool:
        return PropertyFlags.DEPRECATED in self.flags

    @property
    def is_required(self) -> bool:
        return PropertyFlags.REQUIRED in self.flags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "property_id": self.property_id,
            "name": self.name,
            "display_name": self.display_name,
            "prop_type": self.prop_type.value,
            "path": self.path,
            "flags": [f.value for f in sorted(self.flags, key=lambda x: x.value)],
            "default_value": self.default_value if self.default_value is not MIXED_VALUE else "<MIXED>",
            "metadata": self.metadata.to_dict(),
            "editor_hint": self.editor_hint.value,
        }


# ==============================================================================
# VALIDATION MESSAGE & DEPENDENCIES
# ==============================================================================

@dataclass
class PropertyValidationMessage:
    property_path: str
    severity: ValidationSeverity
    code: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "property_path": self.property_path,
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
        }


@dataclass
class PropertyDependency:
    source_property: str
    target_property: str
    condition: Callable[[Any], bool]
    action: str = "VISIBLE"  # VISIBLE, EDITABLE


# ==============================================================================
# SCHEMA SYSTEM
# ==============================================================================

@dataclass
class PropertySchema:
    schema_id: str
    version: str = "1.0.0"
    parent_schema_id: Optional[str] = None
    properties: Dict[str, PropertyDescriptor] = field(default_factory=dict)
    groups: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dependencies: List[PropertyDependency] = field(default_factory=list)

    def add_property(self, descriptor: PropertyDescriptor) -> None:
        if descriptor.property_id in self.properties:
            raise ValueError(f"Duplicate property_id '{descriptor.property_id}' in schema '{self.schema_id}'.")
        self.properties[descriptor.property_id] = descriptor

    def get_property(self, property_id: str) -> Optional[PropertyDescriptor]:
        return self.properties.get(property_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "version": self.version,
            "parent_schema_id": self.parent_schema_id,
            "properties": {pid: prop.to_dict() for pid, prop in self.properties.items()},
            "groups": self.groups,
        }


# ==============================================================================
# CLIPBOARD & TRANSACTIONS
# ==============================================================================

@dataclass
class PropertyClipboard:
    source_schema_id: str
    property_paths: List[str] = field(default_factory=list)
    values: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_schema_id": self.source_schema_id,
            "property_paths": self.property_paths,
            "values": {k: v if v is not MIXED_VALUE else "<MIXED>" for k, v in self.values.items()},
            "version": self.version,
        }


@dataclass
class InspectorEditTransaction:
    transaction_id: str
    target_ids: List[str]
    property_path: str
    initial_values: Dict[str, Any]
    new_values: Dict[str, Any]
    is_active: bool = True
    is_committed: bool = False


# ==============================================================================
# INSPECTOR STATE, SNAPSHOT & TELEMETRY
# ==============================================================================

@dataclass
class InspectorState:
    target_ids: List[str] = field(default_factory=list)
    active_schema_id: Optional[str] = None
    selection: List[str] = field(default_factory=list)
    filter_query: str = ""
    search_query: str = ""
    expanded_groups: Set[str] = field(default_factory=set)
    scroll_offset: float = 0.0
    pinned: bool = False
    active_property_path: Optional[str] = None


@dataclass
class InspectorSnapshot:
    snapshot_id: str
    timestamp: float
    schema_id: str
    target_ids: List[str]
    property_values: Dict[str, Any]
    validation_errors: List[Dict[str, Any]]
    state_hash: str = ""

    def compute_hash(self) -> str:
        canonical = {
            "snapshot_id": self.snapshot_id,
            "schema_id": self.schema_id,
            "target_ids": sorted(self.target_ids),
            "property_values": {k: str(v) for k, v in sorted(self.property_values.items())},
            "validation_errors": self.validation_errors,
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()


@dataclass
class InspectorTelemetry:
    total_properties: int = 0
    visible_properties: int = 0
    edited_count: int = 0
    validation_time_ms: float = 0.0
    commit_time_ms: float = 0.0


@dataclass
class InspectorDiagnosticBundle:
    bundle_id: str
    timestamp: float
    snapshot: InspectorSnapshot
    telemetry: InspectorTelemetry
    signature: str = ""

    def sign(self) -> str:
        payload = f"{self.bundle_id}:{self.timestamp}:{self.snapshot.state_hash}:{self.telemetry.total_properties}:{self.telemetry.edited_count}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.sign()
