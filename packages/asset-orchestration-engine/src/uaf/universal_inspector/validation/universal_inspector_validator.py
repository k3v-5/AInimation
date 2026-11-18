"""
UAF-81.68: Universal Inspector Validator.
Validates property schemas, property paths, security boundaries,
type safety, snapshot determinism, and diagnostic bundle integrity.
"""

from __future__ import annotations

import math
import re
from typing import List, Set, Tuple

from uaf.universal_inspector.models.definition import (
    InspectorDiagnosticBundle,
    InspectorSnapshot,
    PropertyClipboard,
    PropertyFlags,
    PropertyPath,
    PropertySchema,
    PropertyType,
)


class UniversalInspectorValidator:
    """
    Authoritative validator enforcing normative invariants for the Universal Property Inspector.
    """

    @staticmethod
    def validate_schema(schema: PropertySchema) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not schema.schema_id or not isinstance(schema.schema_id, str):
            errors.append("INVALID_SCHEMA_ID: Schema ID must be a non-empty string.")

        seen_prop_ids: Set[str] = set()
        seen_paths: Set[str] = set()

        for pid, prop in schema.properties.items():
            if pid != prop.property_id:
                errors.append(f"MISMATCHED_ID: Dictionary key '{pid}' does not match property_id '{prop.property_id}'.")

            if prop.property_id in seen_prop_ids:
                errors.append(f"NO_DUPLICATE_PROPERTY_IDS: Duplicate property_id '{prop.property_id}'.")
            seen_prop_ids.add(prop.property_id)

            if prop.path in seen_paths:
                errors.append(f"DUPLICATE_PATH: Duplicate property path '{prop.path}'.")
            seen_paths.add(prop.path)

            # Validate path format
            valid_path, path_errs = UniversalInspectorValidator.validate_property_path(prop.path)
            if not valid_path:
                errors.extend(path_errs)

            # Validate numeric bounds
            if prop.prop_type in (PropertyType.INT, PropertyType.UINT, PropertyType.FLOAT, PropertyType.DOUBLE):
                meta = prop.metadata
                if meta.min_value is not None and meta.max_value is not None:
                    if meta.min_value > meta.max_value:
                        errors.append(f"INVALID_RANGE: Property '{prop.property_id}' min_value ({meta.min_value}) > max_value ({meta.max_value}).")
                if meta.min_value is not None and (math.isnan(meta.min_value) or math.isinf(meta.min_value)):
                    errors.append(f"NON_FINITE_BOUND: Property '{prop.property_id}' min_value is non-finite.")
                if meta.max_value is not None and (math.isnan(meta.max_value) or math.isinf(meta.max_value)):
                    errors.append(f"NON_FINITE_BOUND: Property '{prop.property_id}' max_value is non-finite.")

            # Validate enum types
            if prop.prop_type == PropertyType.ENUM:
                if not prop.metadata.enum_values:
                    errors.append(f"EMPTY_ENUM: Enum property '{prop.property_id}' has no declared enum values.")

        return len(errors) == 0, errors

    @staticmethod
    def validate_property_path(path_str: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not path_str or not isinstance(path_str, str):
            errors.append("EMPTY_PATH: Property path must be a non-empty string.")
            return False, errors

        if ".." in path_str or "__" in path_str or path_str.startswith("/") or path_str.startswith("\\"):
            errors.append(f"NO_PROPERTY_PATH_ESCAPE: Path traversal attempt detected in '{path_str}'.")

        try:
            PropertyPath.parse(path_str)
        except Exception as e:
            errors.append(f"PARSE_ERROR: Failed to parse path '{path_str}': {str(e)}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_clipboard(clipboard: PropertyClipboard) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        if not clipboard.source_schema_id:
            errors.append("MISSING_SCHEMA: Clipboard must declare source_schema_id.")

        for p_path in clipboard.property_paths:
            valid_path, path_errs = UniversalInspectorValidator.validate_property_path(p_path)
            if not valid_path:
                errors.extend(path_errs)

        return len(errors) == 0, errors

    @staticmethod
    def validate_snapshot(snapshot: InspectorSnapshot) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = snapshot.compute_hash()
        if snapshot.state_hash != expected:
            errors.append(f"SNAPSHOT_CORRUPTION: Expected state hash '{expected}', got '{snapshot.state_hash}'.")
        return len(errors) == 0, errors

    @staticmethod
    def validate_diagnostic_bundle(bundle: InspectorDiagnosticBundle) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        expected = bundle.sign()
        if bundle.signature != expected:
            errors.append(f"BUNDLE_CORRUPTION: Expected signature '{expected}', got '{bundle.signature}'.")
        return len(errors) == 0, errors
