"""
ParameterType and Provenance enumerations.
UAF-81.1 Sections 16, 22, 23.
"""

from enum import Enum


class ParameterType(str, Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    ENUM = "ENUM"
    VECTOR2 = "VECTOR2"
    VECTOR3 = "VECTOR3"
    COLOR = "COLOR"
    RANGE = "RANGE"
    CURVE = "CURVE"
    REFERENCE = "REFERENCE"
    LIST = "LIST"
    MAP = "MAP"
    OBJECT = "OBJECT"


class ParameterProvenance(str, Enum):
    USER_DEFINED = "USER_DEFINED"
    DERIVED = "DERIVED"
    DEFAULTED = "DEFAULTED"
    INFERRED = "INFERRED"
