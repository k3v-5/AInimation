from enum import Enum

class SceneStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    BUILDING = "BUILDING"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"

class BuildStage(int, Enum):
    ANALYSIS = 0
    PROXY_LAYOUT = 1
    LANDMARKS = 2
    PRIMARY_STRUCTURES = 3
    SECONDARY_STRUCTURES = 4
    ROADS_CONNECTORS = 5
    DECORATION = 6
    MATERIALS = 7
    VALIDATION = 8

class NodeDirtyState(str, Enum):
    CLEAN = "CLEAN"
    DIRTY = "DIRTY"
    BUILDING = "BUILDING"
    FAILED = "FAILED"
    VALIDATED = "VALIDATED"

class ReconciliationStatus(str, Enum):
    MATCH = "MATCH"
    MISSING = "MISSING"
    ORPHAN = "ORPHAN"
    MODIFIED = "MODIFIED"
    CORRUPTED = "CORRUPTED"
