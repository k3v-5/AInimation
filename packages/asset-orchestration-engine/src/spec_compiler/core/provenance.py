from enum import Enum

class AttributeProvenance(str, Enum):
    EXPLICIT = "EXPLICIT"
    LEARNED = "LEARNED"
    INFERRED = "INFERRED"
    DEFAULT = "DEFAULT"
    UNKNOWN = "UNKNOWN"
