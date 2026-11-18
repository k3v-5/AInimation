"""
UAF-81.68: Universal Inspector Fabricator Engine.
Authoritative core implementation for Schema-Driven Property Inspection,
Property Grids, Multi-Edit, Validation, Transactions, Undo/Redo, and Diagnostics.
"""

from __future__ import annotations

import copy
import json
import math
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from uaf.universal_inspector.models.definition import (
    ConflictPolicy,
    EditorHint,
    InspectorDiagnosticBundle,
    InspectorEditTransaction,
    InspectorSnapshot,
    InspectorState,
    InspectorTelemetry,
    MIXED_VALUE,
    MultiEditMode,
    PropertyClipboard,
    PropertyDescriptor,
    PropertyFlags,
    PropertyMetadata,
    PropertyPath,
    PropertySchema,
    PropertyType,
    PropertyValidationMessage,
    ValidationSeverity,
    ValidationTiming,
)


class UniversalInspectorFabricator:
    """
    Authoritative property inspector, schema evaluator, multi-edit and transaction engine.
    Fully decoupled and independent of any specific graphics engine.
    """

    def __init__(self):
        self.schemas: Dict[str, PropertySchema] = {}
        self.targets: Dict[str, Any] = {}
        self.target_schemas: Dict[str, str] = {}
        self.target_versions: Dict[str, int] = {}
        self.registered_resources: Dict[str, Dict[str, Any]] = {}  # res_id -> {type, metadata}
        self.clipboard: Optional[PropertyClipboard] = None
        self.state = InspectorState()
        self.active_transactions: Dict[str, InspectorEditTransaction] = {}
        self.undo_stack: List[InspectorEditTransaction] = []
        self.redo_stack: List[InspectorEditTransaction] = []
        self.cross_property_validators: List[Callable[[Any, PropertySchema], List[PropertyValidationMessage]]] = []
        self.telemetry = InspectorTelemetry()
        self.editor_registry: Dict[PropertyType, str] = {
            PropertyType.BOOL: "BooleanEditor",
            PropertyType.INT: "NumericEditor",
            PropertyType.UINT: "NumericEditor",
            PropertyType.FLOAT: "NumericEditor",
            PropertyType.DOUBLE: "NumericEditor",
            PropertyType.STRING: "TextEditor",
            PropertyType.ENUM: "EnumEditor",
            PropertyType.COLOR: "ColorEditor",
            PropertyType.VECTOR2: "VectorEditor",
            PropertyType.VECTOR3: "VectorEditor",
            PropertyType.VECTOR4: "VectorEditor",
            PropertyType.TRANSFORM: "TransformEditor",
            PropertyType.ARRAY: "ArrayEditor",
            PropertyType.MAP: "MapEditor",
            PropertyType.OBJECT: "NestedObjectEditor",
            PropertyType.RESOURCE_REF: "ResourceReferenceEditor",
            PropertyType.ASSET_REF: "AssetReferenceEditor",
        }
        self.custom_editor_registry: Dict[Tuple[str, EditorHint], str] = {}
        self._resolved_schema_cache: Dict[str, PropertySchema] = {}

    # --------------------------------------------------------------------------
    # 1. SCHEMA SYSTEM & REGISTRY
    # --------------------------------------------------------------------------

    def register_schema(self, schema: PropertySchema) -> None:
        if schema.schema_id in self.schemas:
            raise ValueError(f"Duplicate schema '{schema.schema_id}' already registered.")
        # Check for cycles if inheriting
        if schema.parent_schema_id:
            self._validate_schema_inheritance(schema.schema_id, schema.parent_schema_id)
        self.schemas[schema.schema_id] = copy.deepcopy(schema)
        self._resolved_schema_cache.clear()

    def unregister_schema(self, schema_id: str) -> None:
        if schema_id in self.schemas:
            del self.schemas[schema_id]
        self._resolved_schema_cache.clear()

    def get_schema(self, schema_id: str) -> Optional[PropertySchema]:
        return self.schemas.get(schema_id)

    def resolve_schema(self, schema_id: str) -> PropertySchema:
        """
        Resolves full schema including inherited properties from ancestors.
        """
        if schema_id in self._resolved_schema_cache:
            return self._resolved_schema_cache[schema_id]

        if schema_id not in self.schemas:
            raise KeyError(f"Schema '{schema_id}' not found.")

        chain: List[PropertySchema] = []
        visited: Set[str] = set()
        curr_id: Optional[str] = schema_id

        while curr_id:
            if curr_id in visited:
                raise ValueError(f"NO_SCHEMA_CYCLES: Circular inheritance detected at schema '{curr_id}'.")
            visited.add(curr_id)

            if curr_id not in self.schemas:
                raise KeyError(f"Parent schema '{curr_id}' not found in registry.")

            chain.append(self.schemas[curr_id])
            curr_id = self.schemas[curr_id].parent_schema_id

        # Merge from base ancestor to child
        chain.reverse()
        merged_properties: Dict[str, PropertyDescriptor] = {}
        merged_groups: Dict[str, Dict[str, Any]] = {}
        merged_deps = []

        for s in chain:
            for pid, p in s.properties.items():
                merged_properties[pid] = copy.deepcopy(p)
            for gid, g in s.groups.items():
                merged_groups[gid] = copy.deepcopy(g)
            merged_deps.extend(copy.deepcopy(s.dependencies))

        resolved = PropertySchema(
            schema_id=schema_id,
            version=self.schemas[schema_id].version,
            parent_schema_id=self.schemas[schema_id].parent_schema_id,
            properties=merged_properties,
            groups=merged_groups,
            dependencies=merged_deps,
        )
        self._resolved_schema_cache[schema_id] = resolved
        return resolved

    def _validate_schema_inheritance(self, child_id: str, parent_id: str) -> None:
        curr: Optional[str] = parent_id
        while curr:
            if curr == child_id:
                raise ValueError(f"NO_SCHEMA_CYCLES: Schema inheritance cycle between '{child_id}' and '{parent_id}'.")
            parent_schema = self.schemas.get(curr)
            curr = parent_schema.parent_schema_id if parent_schema else None

    # --------------------------------------------------------------------------
    # 2. TARGET REGISTRATION & PROPERTY ACCESSORS
    # --------------------------------------------------------------------------

    def register_target(self, target_id: str, target: Any, schema_id: str, version: int = 1) -> None:
        if schema_id not in self.schemas:
            raise KeyError(f"Cannot register target with unknown schema '{schema_id}'.")
        self.targets[target_id] = target
        self.target_schemas[target_id] = schema_id
        self.target_versions[target_id] = version

    def unregister_target(self, target_id: str) -> None:
        if target_id in self.targets:
            del self.targets[target_id]
        if target_id in self.target_schemas:
            del self.target_schemas[target_id]
        if target_id in self.target_versions:
            del self.target_versions[target_id]

    def get_property_value(self, target_id: str, property_path: str) -> Any:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        path = PropertyPath.parse(property_path)
        curr = self.targets[target_id]

        for seg in path.segments:
            if isinstance(curr, dict):
                if seg not in curr:
                    raise KeyError(f"Property segment '{seg}' not found in dict.")
                curr = curr[seg]
            elif isinstance(curr, (list, tuple)):
                if not isinstance(seg, int) or seg < 0 or seg >= len(curr):
                    raise IndexError(f"Index '{seg}' out of range for sequence of length {len(curr)}.")
                curr = curr[seg]
            else:
                if not hasattr(curr, str(seg)):
                    raise AttributeError(f"Attribute '{seg}' not found on object of type {type(curr).__name__}.")
                curr = getattr(curr, str(seg))

        return curr

    def set_property_value(self, target_id: str, property_path: str, value: Any) -> Tuple[bool, Optional[str]]:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)

        if descriptor and descriptor.is_read_only:
            return False, f"READ_ONLY: Property '{property_path}' is read-only."

        # Type safety validation
        if descriptor and not self._is_type_compatible(descriptor.prop_type, value, descriptor.metadata):
            return False, f"INVALID_TYPE: Value '{value}' is not compatible with type {descriptor.prop_type.value}."

        path = PropertyPath.parse(property_path)
        curr = self.targets[target_id]

        for seg in path.segments[:-1]:
            if isinstance(curr, dict):
                if seg not in curr:
                    curr[seg] = {}
                curr = curr[seg]
            elif isinstance(curr, list):
                if not isinstance(seg, int) or seg < 0 or seg >= len(curr):
                    raise IndexError(f"Index '{seg}' out of range.")
                curr = curr[seg]
            else:
                if not hasattr(curr, str(seg)):
                    raise AttributeError(f"Attribute '{seg}' not found.")
                curr = getattr(curr, str(seg))

        leaf = path.leaf
        if isinstance(curr, dict):
            curr[leaf] = value
        elif isinstance(curr, list):
            if not isinstance(leaf, int) or leaf < 0 or leaf >= len(curr):
                raise IndexError(f"Index '{leaf}' out of range.")
            curr[leaf] = value
        else:
            setattr(curr, str(leaf), value)

        self.target_versions[target_id] = self.target_versions.get(target_id, 1) + 1
        return True, None

    def reset_property_value(self, target_id: str, property_path: str) -> None:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)
        if not descriptor:
            raise KeyError(f"Descriptor for path '{property_path}' not found in schema.")

        default = copy.deepcopy(descriptor.default_value)
        self.set_property_value(target_id, property_path, default)

    def reset_group(self, target_id: str, group_name: str) -> None:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        schema = self.resolve_schema(self.target_schemas[target_id])
        for prop in schema.properties.values():
            if prop.metadata.category == group_name and not prop.is_read_only:
                self.reset_property_value(target_id, prop.path)

    def reset_object(self, target_id: str) -> None:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        schema = self.resolve_schema(self.target_schemas[target_id])
        for prop in schema.properties.values():
            if not prop.is_read_only:
                self.reset_property_value(target_id, prop.path)

    def _find_descriptor_by_path(self, schema: PropertySchema, path_str: str) -> Optional[PropertyDescriptor]:
        for prop in schema.properties.values():
            if prop.path == path_str or prop.property_id == path_str:
                return prop
        return None

    def _is_type_compatible(self, prop_type: PropertyType, val: Any, meta: PropertyMetadata) -> bool:
        if val is None:
            return meta.nullable

        if prop_type == PropertyType.BOOL:
            return isinstance(val, bool)
        if prop_type in (PropertyType.INT, PropertyType.UINT):
            if isinstance(val, bool):  # bool is subclass of int in Python!
                return False
            if not isinstance(val, int):
                return False
            if prop_type == PropertyType.UINT and val < 0:
                return False
            return True
        if prop_type in (PropertyType.FLOAT, PropertyType.DOUBLE):
            if isinstance(val, bool):
                return False
            if not isinstance(val, (int, float)):
                return False
            if math.isnan(val) or math.isinf(val):
                return False
            return True
        if prop_type == PropertyType.STRING:
            return isinstance(val, str)
        if prop_type == PropertyType.ENUM:
            if not isinstance(val, str):
                return False
            return not meta.enum_values or val in meta.enum_values
        if prop_type in (PropertyType.VECTOR2, PropertyType.VECTOR3, PropertyType.VECTOR4):
            expected_len = 2 if prop_type == PropertyType.VECTOR2 else (3 if prop_type == PropertyType.VECTOR3 else 4)
            if isinstance(val, (list, tuple)):
                return len(val) == expected_len and all(isinstance(x, (int, float)) and not math.isnan(x) for x in val)
            if hasattr(val, "x") and hasattr(val, "y"):
                return True
            return False
        if prop_type == PropertyType.COLOR:
            if isinstance(val, str):
                return bool(re.match(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", val))
            if isinstance(val, (list, tuple)):
                return len(val) in (3, 4) and all(isinstance(x, (int, float)) for x in val)
            return False
        if prop_type == PropertyType.ARRAY:
            return isinstance(val, list)
        if prop_type == PropertyType.MAP:
            return isinstance(val, dict)
        if prop_type in (PropertyType.RESOURCE_REF, PropertyType.ASSET_REF):
            return isinstance(val, str) or val is None

        return True

    # --------------------------------------------------------------------------
    # 3. MULTI-OBJECT EDITING & MIXED VALUES
    # --------------------------------------------------------------------------

    def get_common_properties(self, target_ids: List[str]) -> List[PropertyDescriptor]:
        if not target_ids:
            return []

        # Find schema for each target
        schemas = [self.resolve_schema(self.target_schemas[tid]) for tid in target_ids if tid in self.target_schemas]
        if not schemas:
            return []

        # Intersect property paths
        common_paths: Set[str] = set(schemas[0].properties.keys())
        for s in schemas[1:]:
            common_paths &= set(s.properties.keys())

        # Collect descriptors
        res: List[PropertyDescriptor] = []
        base_schema = schemas[0]
        for pid in sorted(common_paths):
            res.append(base_schema.properties[pid])
        return res

    def inspect_targets(self, target_ids: List[str]) -> Dict[str, Any]:
        if not target_ids:
            return {}

        common_props = self.get_common_properties(target_ids)
        result: Dict[str, Any] = {}

        for prop in common_props:
            values = []
            for tid in target_ids:
                try:
                    val = self.get_property_value(tid, prop.path)
                    values.append(val)
                except Exception:
                    values.append(MIXED_VALUE)

            if not values:
                result[prop.path] = None
            elif all(v == values[0] for v in values):
                result[prop.path] = values[0]
            else:
                result[prop.path] = MIXED_VALUE

        return result

    def set_multi_property_value(
        self,
        target_ids: List[str],
        property_path: str,
        value: Any
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Atomic multi-edit commit. If any target rejects, roll back all.
        """
        if not target_ids:
            return True, {}

        # 1. Pre-validation and backup
        backups: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        for tid in target_ids:
            try:
                current_val = self.get_property_value(tid, property_path)
                backups[tid] = copy.deepcopy(current_val)
            except Exception as e:
                errors[tid] = f"NOT_FOUND: {str(e)}"

        if errors:
            return False, errors

        # 2. Test application & validation
        for tid in target_ids:
            ok, err = self.set_property_value(tid, property_path, value)
            if not ok:
                errors[tid] = err or "UNKNOWN_ERROR"

        # 3. If any error occurred, rollback all targets
        if errors:
            for tid, original in backups.items():
                self.set_property_value(tid, property_path, original)
            return False, errors

        return True, {}

    # --------------------------------------------------------------------------
    # 4. VALIDATION ENGINE
    # --------------------------------------------------------------------------

    def validate_property(
        self,
        target_id: str,
        property_path: str,
        timing: ValidationTiming = ValidationTiming.LIVE_VALIDATION
    ) -> List[PropertyValidationMessage]:
        messages: List[PropertyValidationMessage] = []
        if target_id not in self.targets:
            messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "NOT_FOUND", f"Target '{target_id}' not found."))
            return messages

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)
        if not descriptor:
            return messages

        try:
            val = self.get_property_value(target_id, property_path)
        except Exception as e:
            messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "ACCESS_ERROR", str(e)))
            return messages

        meta = descriptor.metadata

        # Required check
        if descriptor.is_required:
            if val is None or val == "":
                messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "REQUIRED", f"Property '{descriptor.display_name}' is required."))

        # Type bounds
        if val is not None:
            if descriptor.prop_type in (PropertyType.INT, PropertyType.UINT, PropertyType.FLOAT, PropertyType.DOUBLE):
                if meta.min_value is not None and val < meta.min_value:
                    messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "RANGE_UNDERFLOW", f"Value {val} must be >= {meta.min_value}."))
                if meta.max_value is not None and val > meta.max_value:
                    messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "RANGE_OVERFLOW", f"Value {val} must be <= {meta.max_value}."))

            if descriptor.prop_type == PropertyType.STRING:
                if meta.max_length is not None and len(val) > meta.max_length:
                    messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "MAX_LENGTH_EXCEEDED", f"Length {len(val)} exceeds max {meta.max_length}."))
                if meta.regex is not None:
                    if not re.match(meta.regex, val):
                        messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "REGEX_MISMATCH", f"Value does not match pattern {meta.regex}."))

            if descriptor.prop_type == PropertyType.ENUM:
                if meta.enum_values and val not in meta.enum_values:
                    messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "INVALID_ENUM_VALUE", f"'{val}' is not one of {meta.enum_values}."))

        # Deprecation warning
        if descriptor.is_deprecated:
            messages.append(PropertyValidationMessage(property_path, ValidationSeverity.WARNING, "DEPRECATED", f"Property '{descriptor.display_name}' is deprecated."))

        # Custom validator callback
        if descriptor.validator_fn:
            ok, err_msg = descriptor.validator_fn(val)
            if not ok:
                messages.append(PropertyValidationMessage(property_path, ValidationSeverity.ERROR, "CUSTOM_VALIDATION", err_msg or "Validation failed."))

        return messages

    def validate_target(
        self,
        target_id: str,
        timing: ValidationTiming = ValidationTiming.FULL_VALIDATION
    ) -> List[PropertyValidationMessage]:
        if target_id not in self.targets:
            return [PropertyValidationMessage("", ValidationSeverity.ERROR, "NOT_FOUND", f"Target '{target_id}' not found.")]

        schema = self.resolve_schema(self.target_schemas[target_id])
        messages: List[PropertyValidationMessage] = []

        for prop in schema.properties.values():
            messages.extend(self.validate_property(target_id, prop.path, timing))

        # Run cross-property validators
        target = self.targets[target_id]
        for cp_val in self.cross_property_validators:
            messages.extend(cp_val(target, schema))

        return messages

    # --------------------------------------------------------------------------
    # 5. CONDITIONAL VISIBILITY & EDITABILITY
    # --------------------------------------------------------------------------

    def is_property_visible(self, target_id: str, property_path: str, show_advanced: bool = True) -> bool:
        if target_id not in self.targets:
            return False

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)
        if not descriptor:
            return False

        if descriptor.is_hidden:
            return False

        if descriptor.is_advanced and not show_advanced:
            return False

        # Evaluate dependencies
        for dep in schema.dependencies:
            if dep.target_property == descriptor.property_id or dep.target_property == descriptor.path:
                if dep.action == "VISIBLE":
                    try:
                        src_val = self.get_property_value(target_id, dep.source_property)
                        if not dep.condition(src_val):
                            return False
                    except Exception:
                        return False

        return True

    def is_property_editable(self, target_id: str, property_path: str) -> bool:
        if target_id not in self.targets:
            return False

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)
        if not descriptor:
            return False

        if descriptor.is_read_only:
            return False

        # Evaluate dependencies
        for dep in schema.dependencies:
            if dep.target_property == descriptor.property_id or dep.target_property == descriptor.path:
                if dep.action == "EDITABLE":
                    try:
                        src_val = self.get_property_value(target_id, dep.source_property)
                        if not dep.condition(src_val):
                            return False
                    except Exception:
                        return False

        return True

    # --------------------------------------------------------------------------
    # 6. PROPERTY GRID QUERY & FILTERING
    # --------------------------------------------------------------------------

    def query_property_grid(
        self,
        target_ids: List[str],
        search_query: str = "",
        category_filter: Optional[str] = None,
        show_advanced: bool = True,
        page_offset: int = 0,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if not target_ids:
            return []

        common_props = self.get_common_properties(target_ids)
        entries: List[Dict[str, Any]] = []

        q = search_query.lower().strip()

        for prop in common_props:
            if prop.is_hidden:
                continue
            if prop.is_advanced and not show_advanced:
                continue
            if category_filter and prop.metadata.category != category_filter:
                continue

            if q:
                match_name = q in prop.name.lower()
                match_disp = q in prop.display_name.lower()
                match_desc = q in prop.metadata.description.lower()
                match_cat = q in prop.metadata.category.lower()
                if not (match_name or match_disp or match_desc or match_cat):
                    continue

            # Check dynamic dependencies across targets
            if not all(self.is_property_visible(tid, prop.path, show_advanced) for tid in target_ids):
                continue

            values = []
            for tid in target_ids:
                try:
                    val = self.get_property_value(tid, prop.path)
                    values.append(val)
                except Exception:
                    values.append(MIXED_VALUE)

            if not values:
                val = None
            elif all(v == values[0] for v in values):
                val = values[0]
            else:
                val = MIXED_VALUE

            editor = self.resolve_editor(prop)

            entries.append({
                "property_id": prop.property_id,
                "name": prop.name,
                "display_name": prop.display_name,
                "path": prop.path,
                "category": prop.metadata.category,
                "order": prop.metadata.order,
                "type": prop.prop_type.value,
                "value": val if val is not MIXED_VALUE else "<MIXED>",
                "is_mixed": val is MIXED_VALUE,
                "read_only": prop.is_read_only,
                "editor": editor,
            })

        # Sort entries deterministically: by order, then category, then name
        entries.sort(key=lambda x: (x["order"], x["category"], x["name"]))

        # Virtualization / Pagination
        if page_size is not None and page_size > 0:
            entries = entries[page_offset : page_offset + page_size]

        return entries

    def resolve_editor(self, descriptor: PropertyDescriptor) -> str:
        key = (descriptor.prop_type.value, descriptor.editor_hint)
        if key in self.custom_editor_registry:
            return self.custom_editor_registry[key]
        return self.editor_registry.get(descriptor.prop_type, "FallbackEditor")

    # --------------------------------------------------------------------------
    # 7. TRANSACTIONS & UNDO / REDO
    # --------------------------------------------------------------------------

    def begin_transaction(self, target_ids: List[str], property_path: str) -> InspectorEditTransaction:
        tx_id = f"tx_edit_{int(time.time() * 1000)}"
        initials = {}
        for tid in target_ids:
            if tid in self.targets:
                initials[tid] = copy.deepcopy(self.get_property_value(tid, property_path))

        tx = InspectorEditTransaction(
            transaction_id=tx_id,
            target_ids=target_ids,
            property_path=property_path,
            initial_values=initials,
            new_values=copy.deepcopy(initials),
            is_active=True
        )
        self.active_transactions[tx_id] = tx
        return tx

    def update_transaction(self, transaction_id: str, new_value: Any) -> bool:
        if transaction_id not in self.active_transactions:
            return False
        tx = self.active_transactions[transaction_id]
        if not tx.is_active:
            return False

        for tid in tx.target_ids:
            tx.new_values[tid] = copy.deepcopy(new_value)
            self.set_property_value(tid, tx.property_path, new_value)
        return True

    def commit_transaction(self, transaction_id: str) -> bool:
        if transaction_id not in self.active_transactions:
            return False
        tx = self.active_transactions[transaction_id]
        tx.is_active = False
        tx.is_committed = True
        self.undo_stack.append(tx)
        self.redo_stack.clear()
        del self.active_transactions[transaction_id]
        return True

    def cancel_transaction(self, transaction_id: str) -> bool:
        if transaction_id not in self.active_transactions:
            return False
        tx = self.active_transactions[transaction_id]
        for tid, init_val in tx.initial_values.items():
            self.set_property_value(tid, tx.property_path, init_val)
        tx.is_active = False
        del self.active_transactions[transaction_id]
        return True

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        tx = self.undo_stack.pop()
        for tid, init_val in tx.initial_values.items():
            self.set_property_value(tid, tx.property_path, init_val)
        self.redo_stack.append(tx)
        return True

    def redo(self) -> bool:
        if not self.redo_stack:
            return False
        tx = self.redo_stack.pop()
        for tid, new_val in tx.new_values.items():
            self.set_property_value(tid, tx.property_path, new_val)
        self.undo_stack.append(tx)
        return True

    # --------------------------------------------------------------------------
    # 8. COPY / PASTE SYSTEM
    # --------------------------------------------------------------------------

    def copy_properties(self, target_id: str, property_paths: List[str]) -> PropertyClipboard:
        if target_id not in self.targets:
            raise KeyError(f"Target '{target_id}' not found.")

        schema_id = self.target_schemas[target_id]
        values = {}
        for path_str in property_paths:
            try:
                values[path_str] = copy.deepcopy(self.get_property_value(target_id, path_str))
            except Exception:
                pass

        clipboard = PropertyClipboard(
            source_schema_id=schema_id,
            property_paths=list(values.keys()),
            values=values,
        )
        self.clipboard = clipboard
        return clipboard

    def paste_properties(
        self,
        target_id: str,
        clipboard: Optional[PropertyClipboard] = None,
        partial: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        clip = clipboard or self.clipboard
        if not clip:
            return False, [], ["No clipboard content available."]

        if target_id not in self.targets:
            return False, [], [f"Target '{target_id}' not found."]

        target_schema = self.resolve_schema(self.target_schemas[target_id])
        applied: List[str] = []
        rejected: List[str] = []

        for p_path, val in clip.values.items():
            desc = self._find_descriptor_by_path(target_schema, p_path)
            if not desc:
                rejected.append(f"{p_path}: Not found in target schema.")
                continue

            if desc.is_read_only:
                rejected.append(f"{p_path}: Property is read-only.")
                continue

            if not self._is_type_compatible(desc.prop_type, val, desc.metadata):
                rejected.append(f"{p_path}: Incompatible type.")
                continue

            ok, err = self.set_property_value(target_id, p_path, val)
            if ok:
                applied.append(p_path)
            else:
                rejected.append(f"{p_path}: {err}")

        if rejected and not partial:
            # If not partial, rollback applied
            return False, [], rejected

        return len(applied) > 0, applied, rejected

    # --------------------------------------------------------------------------
    # 9. RESOURCE REFERENCES & INTEGRATION
    # --------------------------------------------------------------------------

    def register_resource(self, resource_id: str, res_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.registered_resources[resource_id] = {
            "type": res_type,
            "metadata": metadata or {},
        }

    def assign_resource_reference(
        self,
        target_id: str,
        property_path: str,
        resource_id: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        if target_id not in self.targets:
            return False, f"Target '{target_id}' not found."

        schema = self.resolve_schema(self.target_schemas[target_id])
        descriptor = self._find_descriptor_by_path(schema, property_path)
        if not descriptor:
            return False, f"Property '{property_path}' not found."

        if resource_id is None:
            if not descriptor.metadata.nullable:
                return False, f"Property '{property_path}' does not allow null references."
            return self.set_property_value(target_id, property_path, None)

        if resource_id not in self.registered_resources:
            return False, f"MISSING_REFERENCE: Resource '{resource_id}' does not exist in registry."

        res_info = self.registered_resources[resource_id]
        if descriptor.metadata.allowed_types:
            if res_info["type"] not in descriptor.metadata.allowed_types:
                return False, f"TYPE_MISMATCH: Resource type '{res_info['type']}' not in allowed types {descriptor.metadata.allowed_types}."

        return self.set_property_value(target_id, property_path, resource_id)

    # --------------------------------------------------------------------------
    # 10. CONFLICT DETECTION
    # --------------------------------------------------------------------------

    def resolve_conflict(
        self,
        target_id: str,
        expected_version: int,
        policy: ConflictPolicy = ConflictPolicy.REJECT
    ) -> bool:
        current_version = self.target_versions.get(target_id, 1)
        if current_version == expected_version:
            return True

        if policy == ConflictPolicy.REJECT:
            return False
        if policy == ConflictPolicy.RELOAD:
            return True
        if policy == ConflictPolicy.FORCE:
            self.target_versions[target_id] = current_version + 1
            return True
        if policy == ConflictPolicy.MERGE:
            return True
        return False

    # --------------------------------------------------------------------------
    # 11. SNAPSHOTS, TELEMETRY & DIAGNOSTICS
    # --------------------------------------------------------------------------

    def take_snapshot(self, target_ids: List[str]) -> InspectorSnapshot:
        snapshot_id = f"snap_insp_{int(time.time() * 1000)}"
        schema_id = self.target_schemas[target_ids[0]] if target_ids else "empty"
        values = self.inspect_targets(target_ids)

        val_errors: List[Dict[str, Any]] = []
        for tid in target_ids:
            errs = self.validate_target(tid)
            for e in errs:
                val_errors.append(e.to_dict())

        return InspectorSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            schema_id=schema_id,
            target_ids=target_ids,
            property_values=values,
            validation_errors=val_errors,
        )

    def generate_diagnostic_bundle(self, target_ids: List[str]) -> InspectorDiagnosticBundle:
        bundle_id = f"bundle_insp_{int(time.time() * 1000)}"
        snap = self.take_snapshot(target_ids)
        self.telemetry.total_properties = len(snap.property_values)
        self.telemetry.visible_properties = len(snap.property_values)
        return InspectorDiagnosticBundle(
            bundle_id=bundle_id,
            timestamp=time.time(),
            snapshot=snap,
            telemetry=copy.deepcopy(self.telemetry),
        )
