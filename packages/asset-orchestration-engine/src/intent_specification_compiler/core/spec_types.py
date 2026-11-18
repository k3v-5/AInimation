from enum import Enum

class ConstraintType(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"

class ValueType(str, Enum):
    EXACT = "EXACT"
    RANGE = "RANGE"
    APPROXIMATE = "APPROXIMATE"
    ENUM = "ENUM"
    BOOLEAN = "BOOLEAN"

class UnitType(str, Enum):
    METERS = "METERS"
    CENTIMETERS = "CENTIMETERS"
    DEGREES = "DEGREES"
    KILOGRAMS = "KILOGRAMS"
    SECONDS = "SECONDS"

class AISpecStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    FROZEN = "FROZEN"
    SUPERSEDED = "SUPERSEDED"

SpecStatus = AISpecStatus

class ApprovalState(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AIRequirementStatus(str, Enum):
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    PARTIAL = "PARTIAL"
    IMPLEMENTED = "IMPLEMENTED"
    VALIDATED = "VALIDATED"

RequirementStatus = AIRequirementStatus
