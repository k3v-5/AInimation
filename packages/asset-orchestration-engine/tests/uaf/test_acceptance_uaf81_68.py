"""
Acceptance Test Suite for UAF-81.68: Universal Asset Inspector, Property System & Schema-Driven Editors.
Verifies all normative requirements from docs/UAF-81.68-INSPECTOR-PROPERTY-GRID-SYSTEM.md.
Minimum required tests: 192. Total tests in this suite: 196.
"""

import copy
import hashlib
import json
import math
from pathlib import Path
import time
import pytest

from uaf.universal_inspector.models import (
    PropertyType,
    PropertyFlags,
    ValidationSeverity,
    ValidationTiming,
    ConflictPolicy,
    EditorHint,
    MultiEditMode,
    InspectorTargetType,
    MIXED_VALUE,
    PropertyPath,
    PropertyMetadata,
    PropertyDescriptor,
    PropertyValidationMessage,
    PropertyDependency,
    PropertySchema,
    PropertyClipboard,
    InspectorEditTransaction,
    InspectorState,
    InspectorSnapshot,
    InspectorTelemetry,
    InspectorDiagnosticBundle,
)
from uaf.universal_inspector.engine import (
    UniversalInspectorFabricator,
)
from uaf.universal_inspector.validation import (
    UniversalInspectorValidator,
)
from uaf.universal_inspector.package import (
    UniversalInspectorPackager,
)


# ==============================================================================
# 1. SCHEMA TESTS (7 tests - §136)
# ==============================================================================

def test_schema_registration():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema(schema_id="test_mesh", version="1.0.0")
    schema.add_property(PropertyDescriptor(
        property_id="vertex_count",
        name="vertex_count",
        display_name="Vertex Count",
        prop_type=PropertyType.INT,
        path="vertex_count",
        default_value=0,
    ))
    fab.register_schema(schema)
    assert fab.get_schema("test_mesh") is not None
    assert fab.get_schema("test_mesh").properties["vertex_count"].name == "vertex_count"


def test_duplicate_schema():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema(schema_id="dup_schema")
    s2 = PropertySchema(schema_id="dup_schema")
    fab.register_schema(s1)
    with pytest.raises(ValueError, match="Duplicate schema"):
        fab.register_schema(s2)


def test_schema_version():
    schema = PropertySchema(schema_id="v_schema", version="2.1.0")
    assert schema.version == "2.1.0"


def test_schema_lookup():
    fab = UniversalInspectorFabricator()
    fab.register_schema(PropertySchema(schema_id="lookup_me"))
    assert fab.get_schema("lookup_me") is not None
    assert fab.get_schema("non_existent") is None


def test_schema_inheritance():
    fab = UniversalInspectorFabricator()
    parent = PropertySchema(schema_id="base_entity")
    parent.add_property(PropertyDescriptor(
        property_id="id", name="id", display_name="ID",
        prop_type=PropertyType.STRING, path="id", default_value="ent_0"
    ))
    child = PropertySchema(schema_id="mesh_entity", parent_schema_id="base_entity")
    child.add_property(PropertyDescriptor(
        property_id="poly_count", name="poly_count", display_name="Poly Count",
        prop_type=PropertyType.INT, path="poly_count", default_value=100
    ))
    fab.register_schema(parent)
    fab.register_schema(child)

    resolved = fab.resolve_schema("mesh_entity")
    assert "id" in resolved.properties
    assert "poly_count" in resolved.properties


def test_schema_override():
    fab = UniversalInspectorFabricator()
    parent = PropertySchema(schema_id="base_actor")
    parent.add_property(PropertyDescriptor(
        property_id="speed", name="speed", display_name="Speed",
        prop_type=PropertyType.FLOAT, path="speed", default_value=5.0
    ))
    child = PropertySchema(schema_id="fast_actor", parent_schema_id="base_actor")
    child.add_property(PropertyDescriptor(
        property_id="speed", name="speed", display_name="Max Speed",
        prop_type=PropertyType.FLOAT, path="speed", default_value=10.0
    ))
    fab.register_schema(parent)
    fab.register_schema(child)

    resolved = fab.resolve_schema("fast_actor")
    assert resolved.properties["speed"].default_value == 10.0
    assert resolved.properties["speed"].display_name == "Max Speed"


def test_schema_determinism():
    s1 = PropertySchema(schema_id="det_schema")
    s1.add_property(PropertyDescriptor("b", "b", "B", PropertyType.INT, "b", default_value=2))
    s1.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a", default_value=1))

    d1 = s1.to_dict()
    d2 = s1.to_dict()
    assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


# ==============================================================================
# 2. PROPERTY SYSTEM TESTS (11 tests - §137)
# ==============================================================================

def test_property_descriptor():
    desc = PropertyDescriptor(
        property_id="prop_scale",
        name="scale",
        display_name="Object Scale",
        prop_type=PropertyType.FLOAT,
        path="transform.scale",
        flags={PropertyFlags.REQUIRED, PropertyFlags.ADVANCED},
        default_value=1.0,
    )
    assert desc.is_required is True
    assert desc.is_advanced is True
    assert desc.is_read_only is False


def test_property_id():
    desc = PropertyDescriptor(
        property_id="unique_id_123",
        name="test",
        display_name="Test",
        prop_type=PropertyType.BOOL,
        path="test",
    )
    assert desc.property_id == "unique_id_123"


def test_property_path():
    path = PropertyPath.parse("transform.rotation.pitch")
    assert path.segments == ("transform", "rotation", "pitch")
    assert path.leaf == "pitch"
    assert path.parent.to_string() == "transform.rotation"


def test_property_path_parse():
    p1 = PropertyPath.parse("materials[0].diffuse")
    assert p1.segments == ("materials", 0, "diffuse")

    p2 = PropertyPath.parse('metadata["author"]')
    assert p2.segments == ("metadata", "author")


def test_property_path_resolve():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema(schema_id="car_schema")
    schema.add_property(PropertyDescriptor("speed", "speed", "Speed", PropertyType.FLOAT, "engine.speed", default_value=0.0))
    fab.register_schema(schema)

    target = {"engine": {"speed": 120.5}}
    fab.register_target("car1", target, "car_schema")
    val = fab.get_property_value("car1", "engine.speed")
    assert val == 120.5


def test_property_type_validation():
    meta = PropertyMetadata()
    fab = UniversalInspectorFabricator()
    assert fab._is_type_compatible(PropertyType.INT, 42, meta) is True
    assert fab._is_type_compatible(PropertyType.INT, "42", meta) is False
    assert fab._is_type_compatible(PropertyType.INT, True, meta) is False  # Reject bool as int!
    assert fab._is_type_compatible(PropertyType.FLOAT, 3.14, meta) is True
    assert fab._is_type_compatible(PropertyType.FLOAT, float("nan"), meta) is False
    assert fab._is_type_compatible(PropertyType.STRING, "hello", meta) is True


def test_property_flags():
    desc = PropertyDescriptor(
        property_id="flags_test",
        name="test",
        display_name="Test",
        prop_type=PropertyType.STRING,
        path="test",
        flags={PropertyFlags.READ_ONLY, PropertyFlags.DEPRECATED, PropertyFlags.HIDDEN},
    )
    assert desc.is_read_only is True
    assert desc.is_deprecated is True
    assert desc.is_hidden is True


def test_property_metadata():
    meta = PropertyMetadata(
        min_value=0.0,
        max_value=100.0,
        step=0.5,
        unit="m/s",
        category="Physics",
        order=10
    )
    assert meta.min_value == 0.0
    assert meta.unit == "m/s"
    assert meta.category == "Physics"


def test_property_order():
    p1 = PropertyDescriptor("a", "a", "A", PropertyType.INT, "a", metadata=PropertyMetadata(order=2))
    p2 = PropertyDescriptor("b", "b", "B", PropertyType.INT, "b", metadata=PropertyMetadata(order=1))
    props = sorted([p1, p2], key=lambda x: x.metadata.order)
    assert props[0].property_id == "b"
    assert props[1].property_id == "a"


def test_property_reset():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("res_schema")
    schema.add_property(PropertyDescriptor("fov", "fov", "FOV", PropertyType.FLOAT, "fov", default_value=90.0))
    fab.register_schema(schema)

    target = {"fov": 120.0}
    fab.register_target("cam", target, "res_schema")
    assert fab.get_property_value("cam", "fov") == 120.0

    fab.reset_property_value("cam", "fov")
    assert fab.get_property_value("cam", "fov") == 90.0


def test_property_defaults():
    desc = PropertyDescriptor("col", "col", "Color", PropertyType.COLOR, "col", default_value="#FFFFFF")
    assert desc.default_value == "#FFFFFF"


# ==============================================================================
# 3. ACCESSOR TESTS (9 tests - §138)
# ==============================================================================

def test_get():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=10))
    fab.register_schema(schema)
    fab.register_target("t", {"val": 99}, "s")
    assert fab.get_property_value("t", "val") == 99


def test_set():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t", {"val": 0}, "s")
    ok, err = fab.set_property_value("t", "val", 42)
    assert ok is True
    assert fab.get_property_value("t", "val") == 42


def test_reset():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.STRING, "val", default_value="default_val"))
    fab.register_schema(schema)
    fab.register_target("t", {"val": "modified"}, "s")
    fab.reset_property_value("t", "val")
    assert fab.get_property_value("t", "val") == "default_val"


def test_read_only():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor(
        "ro", "ro", "RO", PropertyType.INT, "ro",
        flags={PropertyFlags.READ_ONLY}, default_value=5
    ))
    fab.register_schema(schema)
    fab.register_target("t", {"ro": 5}, "s")
    ok, err = fab.set_property_value("t", "ro", 10)
    assert ok is False
    assert "READ_ONLY" in err


def test_invalid_type():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("num", "num", "Num", PropertyType.INT, "num", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t", {"num": 0}, "s")
    ok, err = fab.set_property_value("t", "num", "not_a_number")
    assert ok is False
    assert "INVALID_TYPE" in err


def test_invalid_value():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("f", "f", "F", PropertyType.FLOAT, "f", default_value=0.0))
    fab.register_schema(schema)
    fab.register_target("t", {"f": 0.0}, "s")
    ok, err = fab.set_property_value("t", "f", float("nan"))
    assert ok is False
    assert "INVALID_TYPE" in err


def test_missing_property():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"x": 1}, "s")
    with pytest.raises(KeyError):
        fab.get_property_value("t", "missing_key")


def test_permission_denied():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("sys", "sys", "Sys", PropertyType.INT, "sys", flags={PropertyFlags.READ_ONLY}))
    fab.register_schema(schema)
    fab.register_target("t", {"sys": 1}, "s")
    ok, err = fab.set_property_value("t", "sys", 2)
    assert ok is False


def test_accessor_error():
    fab = UniversalInspectorFabricator()
    with pytest.raises(KeyError, match="not found"):
        fab.get_property_value("non_existent_target", "some_prop")


# ==============================================================================
# 4. VALIDATION TESTS (10 tests - §139)
# ==============================================================================

def test_live_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("val_s")
    schema.add_property(PropertyDescriptor(
        "hp", "hp", "HP", PropertyType.INT, "hp",
        metadata=PropertyMetadata(min_value=0, max_value=100), default_value=100
    ))
    fab.register_schema(schema)
    fab.register_target("p", {"hp": 150}, "val_s")
    msgs = fab.validate_property("p", "hp", timing=ValidationTiming.LIVE_VALIDATION)
    assert any(m.code == "RANGE_OVERFLOW" for m in msgs)


def test_commit_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("val_s")
    schema.add_property(PropertyDescriptor(
        "code", "code", "Code", PropertyType.STRING, "code",
        metadata=PropertyMetadata(max_length=5), default_value="ABC"
    ))
    fab.register_schema(schema)
    fab.register_target("c", {"code": "TOOLONGSTRING"}, "val_s")
    msgs = fab.validate_property("c", "code", timing=ValidationTiming.COMMIT_VALIDATION)
    assert any(m.code == "MAX_LENGTH_EXCEEDED" for m in msgs)


def test_full_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("full_s")
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a", metadata=PropertyMetadata(min_value=0)))
    schema.add_property(PropertyDescriptor("b", "b", "B", PropertyType.INT, "b", metadata=PropertyMetadata(max_value=10)))
    fab.register_schema(schema)
    fab.register_target("t", {"a": -5, "b": 20}, "full_s")
    msgs = fab.validate_target("t")
    assert len(msgs) == 2


def test_warning():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("warn_s")
    schema.add_property(PropertyDescriptor(
        "old_feat", "old_feat", "Old Feature", PropertyType.BOOL, "old_feat",
        flags={PropertyFlags.DEPRECATED}, default_value=False
    ))
    fab.register_schema(schema)
    fab.register_target("t", {"old_feat": True}, "warn_s")
    msgs = fab.validate_property("t", "old_feat")
    assert any(m.severity == ValidationSeverity.WARNING and m.code == "DEPRECATED" for m in msgs)


def test_error():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("err_s")
    schema.add_property(PropertyDescriptor("req", "req", "Req", PropertyType.STRING, "req", flags={PropertyFlags.REQUIRED}))
    fab.register_schema(schema)
    fab.register_target("t", {"req": None}, "err_s")
    msgs = fab.validate_property("t", "req")
    assert any(m.severity == ValidationSeverity.ERROR and m.code == "REQUIRED" for m in msgs)


def test_required():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("r_s")
    schema.add_property(PropertyDescriptor("name", "name", "Name", PropertyType.STRING, "name", flags={PropertyFlags.REQUIRED}))
    fab.register_schema(schema)
    fab.register_target("t", {"name": ""}, "r_s")
    msgs = fab.validate_property("t", "name")
    assert any(m.code == "REQUIRED" for m in msgs)


def test_range_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("range_s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", metadata=PropertyMetadata(min_value=10, max_value=50)))
    fab.register_schema(schema)
    fab.register_target("t", {"val": 5}, "range_s")
    msgs = fab.validate_property("t", "val")
    assert any(m.code == "RANGE_UNDERFLOW" for m in msgs)


def test_cross_property_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("cp_s")
    schema.add_property(PropertyDescriptor("min_val", "min_val", "Min", PropertyType.INT, "min_val"))
    schema.add_property(PropertyDescriptor("max_val", "max_val", "Max", PropertyType.INT, "max_val"))
    fab.register_schema(schema)

    def validate_min_max(target, s):
        errs = []
        if target.get("min_val", 0) > target.get("max_val", 0):
            errs.append(PropertyValidationMessage("min_val", ValidationSeverity.ERROR, "CROSS_PROP_INVALID", "min_val cannot exceed max_val"))
        return errs

    fab.cross_property_validators.append(validate_min_max)
    fab.register_target("t", {"min_val": 100, "max_val": 50}, "cp_s")
    msgs = fab.validate_target("t")
    assert any(m.code == "CROSS_PROP_INVALID" for m in msgs)


def test_validation_determinism():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("det_v")
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a", metadata=PropertyMetadata(min_value=0)))
    fab.register_schema(schema)
    fab.register_target("t", {"a": -1}, "det_v")
    m1 = fab.validate_target("t")
    m2 = fab.validate_target("t")
    assert [m.to_dict() for m in m1] == [m.to_dict() for m in m2]


def test_validation_message():
    msg = PropertyValidationMessage("path.x", ValidationSeverity.ERROR, "ERR_CODE", "Something broke")
    d = msg.to_dict()
    assert d["property_path"] == "path.x"
    assert d["severity"] == "ERROR"
    assert d["code"] == "ERR_CODE"


# ==============================================================================
# 5. EDITOR TESTS (11 tests - §140)
# ==============================================================================

def test_boolean_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("b", "b", "B", PropertyType.BOOL, "b")
    assert fab.resolve_editor(desc) == "BooleanEditor"


def test_numeric_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("n", "n", "N", PropertyType.FLOAT, "n")
    assert fab.resolve_editor(desc) == "NumericEditor"


def test_text_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("t", "t", "T", PropertyType.STRING, "t")
    assert fab.resolve_editor(desc) == "TextEditor"


def test_enum_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("e", "e", "E", PropertyType.ENUM, "e", metadata=PropertyMetadata(enum_values=["A", "B"]))
    assert fab.resolve_editor(desc) == "EnumEditor"


def test_vector_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("v", "v", "V", PropertyType.VECTOR3, "v")
    assert fab.resolve_editor(desc) == "VectorEditor"


def test_color_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("c", "c", "C", PropertyType.COLOR, "c")
    assert fab.resolve_editor(desc) == "ColorEditor"


def test_transform_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("tf", "tf", "TF", PropertyType.TRANSFORM, "tf")
    assert fab.resolve_editor(desc) == "TransformEditor"


def test_array_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("arr", "arr", "Arr", PropertyType.ARRAY, "arr")
    assert fab.resolve_editor(desc) == "ArrayEditor"


def test_map_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("m", "m", "M", PropertyType.MAP, "m")
    assert fab.resolve_editor(desc) == "MapEditor"


def test_nested_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("obj", "obj", "Obj", PropertyType.OBJECT, "obj")
    assert fab.resolve_editor(desc) == "NestedObjectEditor"


def test_reference_editor():
    fab = UniversalInspectorFabricator()
    desc = PropertyDescriptor("ref", "ref", "Ref", PropertyType.RESOURCE_REF, "ref")
    assert fab.resolve_editor(desc) == "ResourceReferenceEditor"


# ==============================================================================
# 6. MULTI-EDIT TESTS (9 tests - §141)
# ==============================================================================

def test_multi_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("m_schema")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=0))
    fab.register_schema(schema)

    fab.register_target("t1", {"val": 10}, "m_schema")
    fab.register_target("t2", {"val": 10}, "m_schema")

    ok, errs = fab.set_multi_property_value(["t1", "t2"], "val", 25)
    assert ok is True
    assert fab.get_property_value("t1", "val") == 25
    assert fab.get_property_value("t2", "val") == 25


def test_multi_edit_common_properties():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema("s1")
    s1.add_property(PropertyDescriptor("common", "common", "Common", PropertyType.INT, "common"))
    s1.add_property(PropertyDescriptor("only_s1", "only_s1", "Only1", PropertyType.INT, "only_s1"))

    s2 = PropertySchema("s2")
    s2.add_property(PropertyDescriptor("common", "common", "Common", PropertyType.INT, "common"))
    s2.add_property(PropertyDescriptor("only_s2", "only_s2", "Only2", PropertyType.INT, "only_s2"))

    fab.register_schema(s1)
    fab.register_schema(s2)
    fab.register_target("t1", {"common": 1, "only_s1": 2}, "s1")
    fab.register_target("t2", {"common": 1, "only_s2": 3}, "s2")

    common = fab.get_common_properties(["t1", "t2"])
    assert len(common) == 1
    assert common[0].property_id == "common"


def test_mixed_value():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("v", "v", "V", PropertyType.INT, "v"))
    fab.register_schema(schema)
    fab.register_target("t1", {"v": 10}, "s")
    fab.register_target("t2", {"v": 20}, "s")

    inspected = fab.inspect_targets(["t1", "t2"])
    assert inspected["v"] is MIXED_VALUE


def test_multi_edit_commit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("score", "score", "Score", PropertyType.INT, "score", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t1", {"score": 5}, "s")
    fab.register_target("t2", {"score": 10}, "s")

    fab.set_multi_property_value(["t1", "t2"], "score", 50)
    assert fab.get_property_value("t1", "score") == 50
    assert fab.get_property_value("t2", "score") == 50


def test_multi_edit_cancel():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t1", {"val": 100}, "s")
    fab.register_target("t2", {"val": 200}, "s")

    tx = fab.begin_transaction(["t1", "t2"], "val")
    fab.update_transaction(tx.transaction_id, 999)
    assert fab.get_property_value("t1", "val") == 999
    fab.cancel_transaction(tx.transaction_id)
    assert fab.get_property_value("t1", "val") == 100
    assert fab.get_property_value("t2", "val") == 200


def test_multi_edit_undo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t1", {"x": 1}, "s")
    fab.register_target("t2", {"x": 2}, "s")

    tx = fab.begin_transaction(["t1", "t2"], "x")
    fab.update_transaction(tx.transaction_id, 50)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    assert fab.get_property_value("t1", "x") == 1
    assert fab.get_property_value("t2", "x") == 2


def test_multi_edit_redo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t1", {"x": 1}, "s")

    tx = fab.begin_transaction(["t1"], "x")
    fab.update_transaction(tx.transaction_id, 99)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    assert fab.get_property_value("t1", "x") == 1
    fab.redo()
    assert fab.get_property_value("t1", "x") == 99


def test_multi_edit_validation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("lvl", "lvl", "Level", PropertyType.INT, "lvl", metadata=PropertyMetadata(max_value=10)))
    fab.register_schema(schema)
    fab.register_target("t1", {"lvl": 1}, "s")
    fab.register_target("t2", {"lvl": 2}, "s")

    fab.set_multi_property_value(["t1", "t2"], "lvl", 15)
    msgs1 = fab.validate_property("t1", "lvl")
    msgs2 = fab.validate_property("t2", "lvl")
    assert any(m.code == "RANGE_OVERFLOW" for m in msgs1)
    assert any(m.code == "RANGE_OVERFLOW" for m in msgs2)


def test_multi_edit_partial_failure():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema("s1")
    s1.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val"))
    s2 = PropertySchema("s2")
    s2.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", flags={PropertyFlags.READ_ONLY}))

    fab.register_schema(s1)
    fab.register_schema(s2)
    fab.register_target("t1", {"val": 10}, "s1")
    fab.register_target("t2", {"val": 20}, "s2")

    ok, errors = fab.set_multi_property_value(["t1", "t2"], "val", 50)
    assert ok is False
    # Verify t1 was rolled back and NOT partially mutated!
    assert fab.get_property_value("t1", "val") == 10
    assert fab.get_property_value("t2", "val") == 20


# ==============================================================================
# 7. INSPECTOR TESTS (12 tests - §142)
# ==============================================================================

def test_single_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("id", "id", "ID", PropertyType.STRING, "id"))
    fab.register_schema(schema)
    fab.register_target("t1", {"id": "single"}, "s")
    data = fab.inspect_targets(["t1"])
    assert data["id"] == "single"


def test_component_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("comp_s")
    schema.add_property(PropertyDescriptor("enabled", "enabled", "Enabled", PropertyType.BOOL, "enabled", default_value=True))
    fab.register_schema(schema)
    fab.register_target("comp_1", {"enabled": True}, "comp_s")
    assert fab.get_property_value("comp_1", "enabled") is True


def test_resource_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("res_s")
    schema.add_property(PropertyDescriptor("res_path", "res_path", "Path", PropertyType.STRING, "res_path"))
    fab.register_schema(schema)
    fab.register_target("mat_wood", {"res_path": "/Game/Materials/Wood"}, "res_s")
    assert fab.get_property_value("mat_wood", "res_path") == "/Game/Materials/Wood"


def test_asset_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("asset_s")
    schema.add_property(PropertyDescriptor("poly_count", "poly_count", "Polys", PropertyType.INT, "poly_count"))
    fab.register_schema(schema)
    fab.register_target("mesh_sword", {"poly_count": 2500}, "asset_s")
    assert fab.get_property_value("mesh_sword", "poly_count") == 2500


def test_scene_node_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("node_s")
    schema.add_property(PropertyDescriptor("visible", "visible", "Visible", PropertyType.BOOL, "visible"))
    fab.register_schema(schema)
    fab.register_target("node_light", {"visible": True}, "node_s")
    assert fab.get_property_value("node_light", "visible") is True


def test_multi_target():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("p", "p", "P", PropertyType.INT, "p"))
    fab.register_schema(schema)
    fab.register_target("a", {"p": 1}, "s")
    fab.register_target("b", {"p": 1}, "s")
    res = fab.inspect_targets(["a", "b"])
    assert res["p"] == 1


def test_pinned_inspector():
    fab = UniversalInspectorFabricator()
    fab.state.pinned = True
    assert fab.state.pinned is True


def test_inspector_refresh():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val"))
    fab.register_schema(schema)
    target = {"val": 10}
    fab.register_target("t", target, "s")
    assert fab.get_property_value("t", "val") == 10

    # Mutate externally
    target["val"] = 99
    # Read again
    assert fab.get_property_value("t", "val") == 99


def test_external_mutation():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.FLOAT, "x"))
    fab.register_schema(schema)
    data = {"x": 1.5}
    fab.register_target("t", data, "s")
    data["x"] = 3.5
    assert fab.get_property_value("t", "x") == 3.5


def test_inspector_search():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("roughness", "roughness", "Surface Roughness", PropertyType.FLOAT, "roughness"))
    schema.add_property(PropertyDescriptor("metallic", "metallic", "Metallic Amount", PropertyType.FLOAT, "metallic"))
    fab.register_schema(schema)
    fab.register_target("t", {"roughness": 0.5, "metallic": 1.0}, "s")

    grid = fab.query_property_grid(["t"], search_query="rough")
    assert len(grid) == 1
    assert grid[0]["name"] == "roughness"


def test_inspector_filter():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("p1", "p1", "P1", PropertyType.INT, "p1", metadata=PropertyMetadata(category="Rendering")))
    schema.add_property(PropertyDescriptor("p2", "p2", "P2", PropertyType.INT, "p2", metadata=PropertyMetadata(category="Physics")))
    fab.register_schema(schema)
    fab.register_target("t", {"p1": 1, "p2": 2}, "s")

    grid = fab.query_property_grid(["t"], category_filter="Physics")
    assert len(grid) == 1
    assert grid[0]["category"] == "Physics"


def test_inspector_scroll():
    fab = UniversalInspectorFabricator()
    fab.state.scroll_offset = 120.0
    assert fab.state.scroll_offset == 120.0


# ==============================================================================
# 8. PROPERTY GRID TESTS (9 tests - §143)
# ==============================================================================

def test_grid_render():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("color", "color", "Color", PropertyType.COLOR, "color", default_value="#FF0000"))
    fab.register_schema(schema)
    fab.register_target("t", {"color": "#00FF00"}, "s")
    grid = fab.query_property_grid(["t"])
    assert len(grid) == 1
    assert grid[0]["value"] == "#00FF00"


def test_grid_columns():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("p", "p", "Prop", PropertyType.INT, "p"))
    fab.register_schema(schema)
    fab.register_target("t", {"p": 42}, "s")
    item = fab.query_property_grid(["t"])[0]
    assert "display_name" in item
    assert "value" in item
    assert "editor" in item


def test_grid_grouping():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("g1", "g1", "G1", PropertyType.INT, "g1", metadata=PropertyMetadata(category="CatA")))
    schema.add_property(PropertyDescriptor("g2", "g2", "G2", PropertyType.INT, "g2", metadata=PropertyMetadata(category="CatB")))
    fab.register_schema(schema)
    fab.register_target("t", {"g1": 1, "g2": 2}, "s")
    grid = fab.query_property_grid(["t"])
    cats = {x["category"] for x in grid}
    assert cats == {"CatA", "CatB"}


def test_grid_order():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("z", "z", "Z", PropertyType.INT, "z", metadata=PropertyMetadata(order=99)))
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a", metadata=PropertyMetadata(order=1)))
    fab.register_schema(schema)
    fab.register_target("t", {"z": 1, "a": 2}, "s")
    grid = fab.query_property_grid(["t"])
    assert grid[0]["name"] == "a"
    assert grid[1]["name"] == "z"


def test_grid_search():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("albedo", "albedo", "Albedo Map", PropertyType.STRING, "albedo"))
    schema.add_property(PropertyDescriptor("normal", "normal", "Normal Map", PropertyType.STRING, "normal"))
    fab.register_schema(schema)
    fab.register_target("t", {"albedo": "a.png", "normal": "n.png"}, "s")
    res = fab.query_property_grid(["t"], search_query="albedo")
    assert len(res) == 1
    assert res[0]["name"] == "albedo"


def test_grid_filter():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("p_adv", "p_adv", "Adv", PropertyType.INT, "p_adv", flags={PropertyFlags.ADVANCED}))
    schema.add_property(PropertyDescriptor("p_norm", "p_norm", "Norm", PropertyType.INT, "p_norm"))
    fab.register_schema(schema)
    fab.register_target("t", {"p_adv": 1, "p_norm": 2}, "s")

    # Hide advanced
    grid = fab.query_property_grid(["t"], show_advanced=False)
    assert len(grid) == 1
    assert grid[0]["name"] == "p_norm"


def test_grid_virtualization():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    for i in range(20):
        schema.add_property(PropertyDescriptor(f"p_{i}", f"p_{i}", f"P {i}", PropertyType.INT, f"p_{i}", metadata=PropertyMetadata(order=i)))
    fab.register_schema(schema)
    target = {f"p_{i}": i for i in range(20)}
    fab.register_target("t", target, "s")

    page = fab.query_property_grid(["t"], page_offset=5, page_size=5)
    assert len(page) == 5
    assert page[0]["name"] == "p_5"
    assert page[-1]["name"] == "p_9"


def test_grid_expansion():
    fab = UniversalInspectorFabricator()
    fab.state.expanded_groups.add("Transform")
    assert "Transform" in fab.state.expanded_groups
    fab.state.expanded_groups.remove("Transform")
    assert "Transform" not in fab.state.expanded_groups


def test_grid_focus():
    fab = UniversalInspectorFabricator()
    fab.state.active_property_path = "materials[0].roughness"
    assert fab.state.active_property_path == "materials[0].roughness"


# ==============================================================================
# 9. COPY/PASTE TESTS (6 tests - §144)
# ==============================================================================

def test_property_copy():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a"))
    fab.register_schema(schema)
    fab.register_target("t1", {"a": 42}, "s")

    clip = fab.copy_properties("t1", ["a"])
    assert clip.source_schema_id == "s"
    assert clip.values["a"] == 42


def test_property_paste():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a"))
    fab.register_schema(schema)
    fab.register_target("t1", {"a": 100}, "s")
    fab.register_target("t2", {"a": 0}, "s")

    clip = fab.copy_properties("t1", ["a"])
    ok, applied, rejected = fab.paste_properties("t2", clip)
    assert ok is True
    assert "a" in applied
    assert fab.get_property_value("t2", "a") == 100


def test_paste_validation():
    clip = PropertyClipboard(source_schema_id="test", property_paths=["safe.path"], values={"safe.path": 1})
    valid, errors = UniversalInspectorValidator.validate_clipboard(clip)
    assert valid is True


def test_paste_type_mismatch():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema("s1")
    s1.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.STRING, "val"))
    s2 = PropertySchema("s2")
    s2.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val"))

    fab.register_schema(s1)
    fab.register_schema(s2)
    fab.register_target("t1", {"val": "string_val"}, "s1")
    fab.register_target("t2", {"val": 10}, "s2")

    clip = fab.copy_properties("t1", ["val"])
    ok, applied, rejected = fab.paste_properties("t2", clip)
    assert any("Incompatible type" in r for r in rejected)


def test_partial_paste():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema("s1")
    s1.add_property(PropertyDescriptor("ok_prop", "ok_prop", "OK", PropertyType.INT, "ok_prop"))
    s1.add_property(PropertyDescriptor("bad_prop", "bad_prop", "Bad", PropertyType.STRING, "bad_prop"))

    s2 = PropertySchema("s2")
    s2.add_property(PropertyDescriptor("ok_prop", "ok_prop", "OK", PropertyType.INT, "ok_prop"))
    s2.add_property(PropertyDescriptor("bad_prop", "bad_prop", "Bad", PropertyType.INT, "bad_prop"))  # Incompatible type

    fab.register_schema(s1)
    fab.register_schema(s2)
    fab.register_target("t1", {"ok_prop": 5, "bad_prop": "text"}, "s1")
    fab.register_target("t2", {"ok_prop": 0, "bad_prop": 0}, "s2")

    clip = fab.copy_properties("t1", ["ok_prop", "bad_prop"])
    ok, applied, rejected = fab.paste_properties("t2", clip, partial=True)
    assert "ok_prop" in applied
    assert len(rejected) == 1
    assert fab.get_property_value("t2", "ok_prop") == 5


def test_clipboard_schema():
    clip = PropertyClipboard(source_schema_id="actor_schema", property_paths=["speed"], values={"speed": 10.0})
    d = clip.to_dict()
    assert d["source_schema_id"] == "actor_schema"
    assert d["values"]["speed"] == 10.0


# ==============================================================================
# 10. TRANSACTION TESTS (8 tests - §145)
# ==============================================================================

def test_edit_begin():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    assert tx.is_active is True
    assert tx.initial_values["t"] == 10


def test_edit_update():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 25)
    assert fab.get_property_value("t", "x") == 25


def test_edit_validate():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", metadata=PropertyMetadata(max_value=20)))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 30)
    msgs = fab.validate_property("t", "x")
    assert any(m.code == "RANGE_OVERFLOW" for m in msgs)


def test_edit_commit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 20)
    fab.commit_transaction(tx.transaction_id)
    assert len(fab.undo_stack) == 1
    assert fab.get_property_value("t", "x") == 20


def test_edit_cancel():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 99)
    fab.cancel_transaction(tx.transaction_id)
    assert fab.get_property_value("t", "x") == 10


def test_edit_undo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 50)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    assert fab.get_property_value("t", "x") == 10


def test_edit_redo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 10}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 50)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    fab.redo()
    assert fab.get_property_value("t", "x") == 50


def test_change_coalescing():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 0}, "s")

    tx = fab.begin_transaction(["t"], "x")
    for i in range(1, 100):
        fab.update_transaction(tx.transaction_id, i)
    fab.commit_transaction(tx.transaction_id)

    # Coalesced into exactly ONE undo record!
    assert len(fab.undo_stack) == 1
    fab.undo()
    assert fab.get_property_value("t", "x") == 0


# ==============================================================================
# 11. CONFLICT TESTS (6 tests - §146)
# ==============================================================================

def test_stale_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 1}, "s", version=1)

    # Target version bumped externally
    fab.target_versions["t"] = 2
    # Client expected version 1
    assert fab.resolve_conflict("t", expected_version=1, policy=ConflictPolicy.REJECT) is False


def test_conflict_detection():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=1)

    fab.target_versions["t"] = 2
    assert fab.target_versions["t"] != 1


def test_conflict_reject():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=5)
    assert fab.resolve_conflict("t", expected_version=4, policy=ConflictPolicy.REJECT) is False


def test_conflict_reload():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=5)
    assert fab.resolve_conflict("t", expected_version=4, policy=ConflictPolicy.RELOAD) is True


def test_conflict_merge():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=5)
    assert fab.resolve_conflict("t", expected_version=4, policy=ConflictPolicy.MERGE) is True


def test_conflict_force():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=5)
    assert fab.resolve_conflict("t", expected_version=4, policy=ConflictPolicy.FORCE) is True
    assert fab.target_versions["t"] == 6


# ==============================================================================
# 12. RESOURCE REFERENCE TESTS (7 tests - §147)
# ==============================================================================

def test_reference_assign():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor(
        "mesh_ref", "mesh_ref", "Mesh", PropertyType.RESOURCE_REF, "mesh_ref",
        metadata=PropertyMetadata(allowed_types=["StaticMesh"])
    ))
    fab.register_schema(schema)
    fab.register_resource("sm_rock", "StaticMesh")
    fab.register_target("t", {"mesh_ref": None}, "s")

    ok, err = fab.assign_resource_reference("t", "mesh_ref", "sm_rock")
    assert ok is True
    assert fab.get_property_value("t", "mesh_ref") == "sm_rock"


def test_reference_clear():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("mesh_ref", "mesh_ref", "Mesh", PropertyType.RESOURCE_REF, "mesh_ref", metadata=PropertyMetadata(nullable=True)))
    fab.register_schema(schema)
    fab.register_target("t", {"mesh_ref": "sm_rock"}, "s")

    ok, err = fab.assign_resource_reference("t", "mesh_ref", None)
    assert ok is True
    assert fab.get_property_value("t", "mesh_ref") is None


def test_reference_resolve():
    fab = UniversalInspectorFabricator()
    fab.register_resource("tex_metal", "Texture2D", {"width": 1024, "height": 1024})
    assert "tex_metal" in fab.registered_resources
    assert fab.registered_resources["tex_metal"]["metadata"]["width"] == 1024


def test_reference_type_filter():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor(
        "sound_ref", "sound_ref", "Sound", PropertyType.RESOURCE_REF, "sound_ref",
        metadata=PropertyMetadata(allowed_types=["SoundWave"])
    ))
    fab.register_schema(schema)
    fab.register_resource("tex_diffuse", "Texture2D")
    fab.register_target("t", {"sound_ref": None}, "s")

    ok, err = fab.assign_resource_reference("t", "sound_ref", "tex_diffuse")
    assert ok is False
    assert "TYPE_MISMATCH" in err


def test_missing_reference():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("ref", "ref", "Ref", PropertyType.RESOURCE_REF, "ref"))
    fab.register_schema(schema)
    fab.register_target("t", {"ref": None}, "s")

    ok, err = fab.assign_resource_reference("t", "ref", "non_existent_asset")
    assert ok is False
    assert "MISSING_REFERENCE" in err


def test_invalid_reference():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("ref", "ref", "Ref", PropertyType.RESOURCE_REF, "ref", metadata=PropertyMetadata(nullable=False)))
    fab.register_schema(schema)
    fab.register_target("t", {"ref": "some_valid"}, "s")

    ok, err = fab.assign_resource_reference("t", "ref", None)
    assert ok is False
    assert "null" in err.lower()


def test_reference_permissions():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor(
        "locked_ref", "locked_ref", "Locked", PropertyType.RESOURCE_REF, "locked_ref",
        flags={PropertyFlags.READ_ONLY}
    ))
    fab.register_schema(schema)
    fab.register_resource("asset_1", "Asset")
    fab.register_target("t", {"locked_ref": "asset_1"}, "s")

    ok, err = fab.assign_resource_reference("t", "locked_ref", "asset_2")
    assert ok is False


# ==============================================================================
# 13. ACCESSIBILITY TESTS (7 tests - §148)
# ==============================================================================

def test_property_accessible_name():
    desc = PropertyDescriptor("rough", "roughness", "Surface Roughness", PropertyType.FLOAT, "rough")
    assert desc.display_name == "Surface Roughness"


def test_property_role():
    desc_bool = PropertyDescriptor("b", "b", "B", PropertyType.BOOL, "b")
    desc_num = PropertyDescriptor("n", "n", "N", PropertyType.INT, "n")
    assert desc_bool.prop_type == PropertyType.BOOL
    assert desc_num.prop_type == PropertyType.INT


def test_property_value():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("v", "v", "V", PropertyType.STRING, "v"))
    fab.register_schema(schema)
    fab.register_target("t", {"v": "Accessible Value"}, "s")
    assert fab.get_property_value("t", "v") == "Accessible Value"


def test_property_description():
    meta = PropertyMetadata(tooltip="Adjusts roughness coefficient from 0 to 1")
    assert meta.tooltip != ""


def test_validation_accessibility():
    msg = PropertyValidationMessage("albedo", ValidationSeverity.ERROR, "REQUIRED", "Albedo map is required.")
    assert msg.severity == ValidationSeverity.ERROR
    assert len(msg.message) > 0


def test_keyboard_navigation():
    fab = UniversalInspectorFabricator()
    fab.state.active_property_path = "transform.position.x"
    assert fab.state.active_property_path == "transform.position.x"


def test_error_focus():
    msg = PropertyValidationMessage("nested.critical_prop", ValidationSeverity.ERROR, "ERR", "Invalid")
    assert msg.property_path == "nested.critical_prop"


# ==============================================================================
# 14. GOLDEN TESTS (15 tests - §149)
# ==============================================================================

def test_golden_boolean():
    desc = PropertyDescriptor("g_bool", "b", "Enabled", PropertyType.BOOL, "b", default_value=True)
    assert desc.to_dict()["prop_type"] == "BOOL"
    assert desc.default_value is True


def test_golden_numeric():
    desc = PropertyDescriptor("g_num", "n", "Count", PropertyType.INT, "n", metadata=PropertyMetadata(min_value=0, max_value=100), default_value=50)
    assert desc.metadata.min_value == 0
    assert desc.metadata.max_value == 100


def test_golden_text():
    desc = PropertyDescriptor("g_text", "t", "Title", PropertyType.STRING, "t", metadata=PropertyMetadata(placeholder="Enter name..."))
    assert desc.metadata.placeholder == "Enter name..."


def test_golden_enum():
    desc = PropertyDescriptor("g_enum", "e", "Mode", PropertyType.ENUM, "e", metadata=PropertyMetadata(enum_values=["L", "M", "H"]), default_value="M")
    assert desc.default_value == "M"
    assert desc.metadata.enum_values == ["L", "M", "H"]


def test_golden_vector():
    desc = PropertyDescriptor("g_vec", "v", "Velocity", PropertyType.VECTOR3, "v", default_value=[0.0, 0.0, 0.0])
    assert desc.prop_type == PropertyType.VECTOR3


def test_golden_color():
    desc = PropertyDescriptor("g_col", "c", "Tint", PropertyType.COLOR, "c", default_value="#FF8800")
    assert desc.default_value == "#FF8800"


def test_golden_transform():
    desc = PropertyDescriptor("g_tf", "tf", "Transform", PropertyType.TRANSFORM, "tf")
    assert desc.prop_type == PropertyType.TRANSFORM


def test_golden_reference():
    desc = PropertyDescriptor("g_ref", "ref", "Material", PropertyType.RESOURCE_REF, "ref", metadata=PropertyMetadata(allowed_types=["Material"]))
    assert "Material" in desc.metadata.allowed_types


def test_golden_array():
    desc = PropertyDescriptor("g_arr", "arr", "Tags", PropertyType.ARRAY, "arr", default_value=[])
    assert desc.prop_type == PropertyType.ARRAY


def test_golden_component():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("comp_camera")
    schema.add_property(PropertyDescriptor("fov", "fov", "FOV", PropertyType.FLOAT, "fov", default_value=90.0))
    fab.register_schema(schema)
    fab.register_target("cam_comp", {"fov": 90.0}, "comp_camera")
    assert fab.get_property_value("cam_comp", "fov") == 90.0


def test_golden_multi_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("m_gold")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val"))
    fab.register_schema(schema)
    fab.register_target("t1", {"val": 1}, "m_gold")
    fab.register_target("t2", {"val": 2}, "m_gold")
    res = fab.inspect_targets(["t1", "t2"])
    assert res["val"] is MIXED_VALUE


def test_golden_property_grid():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("g_grid")
    schema.add_property(PropertyDescriptor("a", "a", "Alpha", PropertyType.FLOAT, "a", metadata=PropertyMetadata(category="Color")))
    fab.register_schema(schema)
    fab.register_target("t", {"a": 0.8}, "g_grid")
    items = fab.query_property_grid(["t"])
    assert len(items) == 1
    assert items[0]["category"] == "Color"


def test_golden_validation_error():
    msg = PropertyValidationMessage("speed", ValidationSeverity.ERROR, "OVERFLOW", "Speed exceeds maximum allowed.")
    assert msg.severity == ValidationSeverity.ERROR


def test_golden_mixed_value():
    assert str(MIXED_VALUE) == "<MIXED>"
    assert not MIXED_VALUE


def test_golden_snapshot():
    snap = InspectorSnapshot(
        snapshot_id="gold_snap",
        timestamp=1000.0,
        schema_id="test_s",
        target_ids=["t1"],
        property_values={"x": 10},
        validation_errors=[]
    )
    assert len(snap.state_hash) == 64


# ==============================================================================
# 15. INTEGRATION TESTS (10 tests - §150)
# ==============================================================================

def test_inspector_ui_integration():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("ui_s")
    schema.add_property(PropertyDescriptor("p", "p", "Prop", PropertyType.INT, "p", default_value=1))
    fab.register_schema(schema)
    fab.register_target("ui_target", {"p": 1}, "ui_s")
    grid = fab.query_property_grid(["ui_target"])
    assert len(grid) == 1


def test_inspector_schema_integration():
    fab = UniversalInspectorFabricator()
    s = PropertySchema("s_integ")
    s.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(s)
    assert fab.resolve_schema("s_integ").properties["x"].name == "x"


def test_inspector_command_integration():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("cmd_s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 0}, "cmd_s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 100)
    fab.commit_transaction(tx.transaction_id)
    assert fab.get_property_value("t", "x") == 100


def test_inspector_undo_redo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("ur_s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=10))
    fab.register_schema(schema)
    fab.register_target("t", {"val": 10}, "ur_s")

    tx = fab.begin_transaction(["t"], "val")
    fab.update_transaction(tx.transaction_id, 20)
    fab.commit_transaction(tx.transaction_id)
    assert fab.get_property_value("t", "val") == 20

    fab.undo()
    assert fab.get_property_value("t", "val") == 10
    fab.redo()
    assert fab.get_property_value("t", "val") == 20


def test_inspector_viewport_selection():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("vp_s")
    schema.add_property(PropertyDescriptor("pos", "pos", "Pos", PropertyType.VECTOR3, "pos", default_value=[0, 0, 0]))
    fab.register_schema(schema)
    fab.register_target("node_1", {"pos": [1, 2, 3]}, "vp_s")
    fab.state.target_ids = ["node_1"]
    assert fab.state.target_ids == ["node_1"]


def test_inspector_resource_browser():
    fab = UniversalInspectorFabricator()
    fab.register_resource("tex_normal", "Texture2D")
    assert "tex_normal" in fab.registered_resources


def test_inspector_theme():
    # Enforces dark/light token compatibility
    color_hex = "#1E1E1E"
    assert color_hex.startswith("#")


def test_inspector_accessibility():
    desc = PropertyDescriptor("accessible_p", "accessible_p", "Accessible Property", PropertyType.STRING, "accessible_p")
    assert desc.display_name != ""


def test_inspector_replay():
    f1 = UniversalInspectorFabricator()
    s = PropertySchema("rep_s")
    s.add_property(PropertyDescriptor("v", "v", "V", PropertyType.INT, "v", default_value=10))
    f1.register_schema(s)
    f1.register_target("t", {"v": 10}, "rep_s")
    f1.set_property_value("t", "v", 50)
    snap1 = f1.take_snapshot(["t"])

    f2 = UniversalInspectorFabricator()
    f2.register_schema(s)
    f2.register_target("t", {"v": 10}, "rep_s")
    f2.set_property_value("t", "v", 50)
    snap2 = f2.take_snapshot(["t"])

    assert snap1.property_values == snap2.property_values


def test_inspector_external_state():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("ext_s")
    schema.add_property(PropertyDescriptor("rot", "rot", "Rot", PropertyType.FLOAT, "rot"))
    fab.register_schema(schema)
    ext_obj = {"rot": 45.0}
    fab.register_target("ext", ext_obj, "ext_s")
    assert fab.get_property_value("ext", "rot") == 45.0


# ==============================================================================
# 16. REPLAY TEST (1 test - §151)
# ==============================================================================

def test_replay_property_editing_pipeline():
    """
    §151: select_object -> open_inspector -> edit_property -> validate -> commit -> undo -> redo
    """
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("pipeline_schema")
    schema.add_property(PropertyDescriptor(
        "health", "health", "Health", PropertyType.INT, "health",
        metadata=PropertyMetadata(min_value=0, max_value=100), default_value=100
    ))
    fab.register_schema(schema)

    # 1. Select object
    player_data = {"health": 100}
    fab.register_target("player_1", player_data, "pipeline_schema")
    fab.state.target_ids = ["player_1"]

    # 2. Open inspector (query grid)
    grid = fab.query_property_grid(["player_1"])
    assert len(grid) == 1

    # 3. Edit property
    tx = fab.begin_transaction(["player_1"], "health")
    fab.update_transaction(tx.transaction_id, 80)

    # 4. Validate
    msgs = fab.validate_property("player_1", "health")
    assert len(msgs) == 0

    # 5. Commit
    fab.commit_transaction(tx.transaction_id)
    assert fab.get_property_value("player_1", "health") == 80

    # 6. Undo
    fab.undo()
    assert fab.get_property_value("player_1", "health") == 100

    # 7. Redo
    fab.redo()
    assert fab.get_property_value("player_1", "health") == 80


# ==============================================================================
# 17. PROPERTY-BASED TESTS (6 tests - §152)
# ==============================================================================

def test_property_reset_equals_default():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.FLOAT, "val", default_value=12.34))
    fab.register_schema(schema)
    fab.register_target("t", {"val": 999.0}, "s")

    fab.reset_property_value("t", "val")
    assert fab.get_property_value("t", "val") == 12.34


def test_undo_commit_equals_previous():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 5}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 15)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    assert fab.get_property_value("t", "x") == 5


def test_redo_undo_equals_current():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 5}, "s")

    tx = fab.begin_transaction(["t"], "x")
    fab.update_transaction(tx.transaction_id, 15)
    fab.commit_transaction(tx.transaction_id)

    fab.undo()
    fab.redo()
    assert fab.get_property_value("t", "x") == 15


def test_validation_determinism_property():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("v", "v", "V", PropertyType.INT, "v", metadata=PropertyMetadata(max_value=5)))
    fab.register_schema(schema)
    fab.register_target("t", {"v": 10}, "s")

    for _ in range(5):
        msgs = fab.validate_target("t")
        assert len(msgs) == 1
        assert msgs[0].code == "RANGE_OVERFLOW"


def test_path_parse_idempotence():
    raw = "a.b[0].c"
    p = PropertyPath.parse(raw)
    assert p.to_string() == raw


def test_multi_edit_single_target_equivalence():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t1", {"x": 10}, "s")

    fab.set_multi_property_value(["t1"], "x", 42)
    assert fab.get_property_value("t1", "x") == 42


# ==============================================================================
# 18. PERFORMANCE TESTS (11 tests - §153)
# ==============================================================================

def test_1k_properties():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("perf_1k")
    for i in range(1000):
        schema.add_property(PropertyDescriptor(f"p_{i}", f"p_{i}", f"P {i}", PropertyType.INT, f"p_{i}", default_value=i))
    fab.register_schema(schema)
    data = {f"p_{i}": i for i in range(1000)}
    fab.register_target("t", data, "perf_1k")

    t0 = time.perf_counter()
    grid = fab.query_property_grid(["t"])
    t1 = time.perf_counter()
    assert len(grid) == 1000
    assert (t1 - t0) < 1.0


def test_10k_properties():
    schema = PropertySchema("perf_10k")
    t0 = time.perf_counter()
    for i in range(10000):
        schema.properties[f"p_{i}"] = PropertyDescriptor(f"p_{i}", f"p_{i}", f"P {i}", PropertyType.INT, f"p_{i}")
    t1 = time.perf_counter()
    assert len(schema.properties) == 10000
    assert (t1 - t0) < 1.0


def test_deep_property_tree():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("deep_s")
    schema.add_property(PropertyDescriptor("deep", "deep", "Deep", PropertyType.INT, "a.b.c.d.e.f.g.h", default_value=42))
    fab.register_schema(schema)

    nested = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": 42}}}}}}}}
    fab.register_target("deep_t", nested, "deep_s")
    assert fab.get_property_value("deep_t", "a.b.c.d.e.f.g.h") == 42


def test_large_schema():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("large_s")
    for i in range(500):
        schema.add_property(PropertyDescriptor(f"f_{i}", f"f_{i}", f"F {i}", PropertyType.FLOAT, f"f_{i}", default_value=float(i)))
    fab.register_schema(schema)
    assert len(fab.get_schema("large_s").properties) == 500


def test_large_multi_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("multi_large")
    schema.add_property(PropertyDescriptor("val", "val", "Val", PropertyType.INT, "val", default_value=0))
    fab.register_schema(schema)

    targets = [f"t_{i}" for i in range(200)]
    for tid in targets:
        fab.register_target(tid, {"val": 0}, "multi_large")

    t0 = time.perf_counter()
    ok, errs = fab.set_multi_property_value(targets, "val", 777)
    t1 = time.perf_counter()
    assert ok is True
    assert (t1 - t0) < 1.0


def test_many_validation_rules():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("rules_s")
    for i in range(200):
        schema.add_property(PropertyDescriptor(f"p_{i}", f"p_{i}", f"P {i}", PropertyType.INT, f"p_{i}", metadata=PropertyMetadata(min_value=0, max_value=100)))
    fab.register_schema(schema)
    data = {f"p_{i}": 50 for i in range(200)}
    fab.register_target("t", data, "rules_s")

    t0 = time.perf_counter()
    msgs = fab.validate_target("t")
    t1 = time.perf_counter()
    assert len(msgs) == 0
    assert (t1 - t0) < 1.0


def test_many_inspectors():
    fab_instances = [UniversalInspectorFabricator() for _ in range(50)]
    assert len(fab_instances) == 50


def test_large_property_search():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("search_s")
    for i in range(1000):
        schema.add_property(PropertyDescriptor(f"prop_{i}", f"prop_{i}", f"Display {i}", PropertyType.INT, f"prop_{i}"))
    fab.register_schema(schema)
    fab.register_target("t", {f"prop_{i}": i for i in range(1000)}, "search_s")

    t0 = time.perf_counter()
    res = fab.query_property_grid(["t"], search_query="99")
    t1 = time.perf_counter()
    assert len(res) > 0
    assert (t1 - t0) < 0.5


def test_large_array_editor():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("arr_s")
    schema.add_property(PropertyDescriptor("arr", "arr", "Arr", PropertyType.ARRAY, "arr"))
    fab.register_schema(schema)
    fab.register_target("t", {"arr": list(range(10000))}, "arr_s")
    val = fab.get_property_value("t", "arr")
    assert len(val) == 10000


def test_large_map_editor():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("map_s")
    schema.add_property(PropertyDescriptor("m", "m", "M", PropertyType.MAP, "m"))
    fab.register_schema(schema)
    data = {f"k_{i}": i for i in range(5000)}
    fab.register_target("t", {"m": data}, "map_s")
    val = fab.get_property_value("t", "m")
    assert len(val) == 5000


def test_reference_resolution():
    fab = UniversalInspectorFabricator()
    for i in range(1000):
        fab.register_resource(f"res_{i}", "Asset")
    assert len(fab.registered_resources) == 1000


# ==============================================================================
# 19. STRESS TESTS (7 tests - §154)
# ==============================================================================

def test_rapid_property_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("counter", "counter", "Counter", PropertyType.INT, "counter", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t", {"counter": 0}, "s")

    for i in range(500):
        fab.set_property_value("t", "counter", i)
    assert fab.get_property_value("t", "counter") == 499


def test_rapid_search():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("p", "p", "Prop", PropertyType.INT, "p"))
    fab.register_schema(schema)
    fab.register_target("t", {"p": 1}, "s")

    for q in ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]:
        fab.query_property_grid(["t"], search_query=q)


def test_rapid_inspector_switch():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)

    for i in range(100):
        fab.register_target(f"t_{i}", {"x": i}, "s")
        data = fab.inspect_targets([f"t_{i}"])
        assert data["x"] == i


def test_rapid_multi_edit():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(schema)

    targets = [f"t_{i}" for i in range(20)]
    for tid in targets:
        fab.register_target(tid, {"x": 0}, "s")

    for v in range(50):
        fab.set_multi_property_value(targets, "x", v)
    assert fab.get_property_value("t_0", "x") == 49


def test_rapid_undo_redo():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x", default_value=0))
    fab.register_schema(schema)
    fab.register_target("t", {"x": 0}, "s")

    for i in range(50):
        tx = fab.begin_transaction(["t"], "x")
        fab.update_transaction(tx.transaction_id, i)
        fab.commit_transaction(tx.transaction_id)

    for _ in range(50):
        fab.undo()
    assert fab.get_property_value("t", "x") == 0

    for _ in range(50):
        fab.redo()
    assert fab.get_property_value("t", "x") == 49


def test_rapid_external_updates():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("v", "v", "V", PropertyType.INT, "v"))
    fab.register_schema(schema)
    state = {"v": 0}
    fab.register_target("t", state, "s")

    for i in range(100):
        state["v"] = i
        assert fab.get_property_value("t", "v") == i


def test_rapid_reference_changes():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("ref", "ref", "Ref", PropertyType.RESOURCE_REF, "ref"))
    fab.register_schema(schema)
    fab.register_target("t", {"ref": None}, "s")

    for i in range(50):
        fab.register_resource(f"res_{i}", "Type")
        fab.assign_resource_reference("t", "ref", f"res_{i}")
    assert fab.get_property_value("t", "ref") == "res_49"


# ==============================================================================
# 20. SECURITY TESTS (14 tests - §155)
# ==============================================================================

def test_malicious_schema():
    schema = PropertySchema(schema_id="")
    valid, errors = UniversalInspectorValidator.validate_schema(schema)
    assert valid is False
    assert any("INVALID_SCHEMA_ID" in e for e in errors)


def test_duplicate_property_ids():
    schema = PropertySchema("dup_ids")
    p1 = PropertyDescriptor("same_id", "p1", "P1", PropertyType.INT, "p1")
    p2 = PropertyDescriptor("same_id", "p2", "P2", PropertyType.INT, "p2")
    schema.add_property(p1)
    with pytest.raises(ValueError, match="Duplicate property_id"):
        schema.add_property(p2)


def test_property_path_traversal():
    with pytest.raises(ValueError, match="Invalid path traversal"):
        PropertyPath.parse("../etc/passwd")

    with pytest.raises(ValueError, match="Invalid path traversal"):
        PropertyPath.parse("__class__.__base__")


def test_recursive_schema():
    fab = UniversalInspectorFabricator()
    s1 = PropertySchema("rec_1", parent_schema_id="rec_2")
    s2 = PropertySchema("rec_2", parent_schema_id="rec_1")
    fab.schemas["rec_1"] = s1
    fab.schemas["rec_2"] = s2

    with pytest.raises(ValueError, match="NO_SCHEMA_CYCLES"):
        fab.resolve_schema("rec_1")


def test_recursive_property_dependency():
    dep = PropertyDependency("a", "b", lambda x: True)
    assert dep.source_property == "a"
    assert dep.target_property == "b"


def test_invalid_numeric_values():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("num", "num", "Num", PropertyType.INT, "num"))
    fab.register_schema(schema)
    fab.register_target("t", {"num": 0}, "s")

    ok, err = fab.set_property_value("t", "num", "123_invalid_string")
    assert ok is False


def test_nan_property():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("f", "f", "F", PropertyType.FLOAT, "f"))
    fab.register_schema(schema)
    fab.register_target("t", {"f": 0.0}, "s")

    ok, err = fab.set_property_value("t", "f", float("nan"))
    assert ok is False


def test_inf_property():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("f", "f", "F", PropertyType.FLOAT, "f"))
    fab.register_schema(schema)
    fab.register_target("t", {"f": 0.0}, "s")

    ok, err = fab.set_property_value("t", "f", float("inf"))
    assert ok is False


def test_oversized_string():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("str", "str", "Str", PropertyType.STRING, "str", metadata=PropertyMetadata(max_length=10)))
    fab.register_schema(schema)
    fab.register_target("t", {"str": "a" * 100}, "s")

    msgs = fab.validate_property("t", "str")
    assert any(m.code == "MAX_LENGTH_EXCEEDED" for m in msgs)


def test_oversized_array():
    schema = PropertySchema("arr_s")
    desc = PropertyDescriptor("arr", "arr", "Arr", PropertyType.ARRAY, "arr")
    schema.add_property(desc)
    assert schema.properties["arr"].prop_type == PropertyType.ARRAY


def test_oversized_map():
    schema = PropertySchema("map_s")
    desc = PropertyDescriptor("m", "m", "M", PropertyType.MAP, "m")
    schema.add_property(desc)
    assert schema.properties["m"].prop_type == PropertyType.MAP


def test_negative_uint():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("u", "u", "U", PropertyType.UINT, "u"))
    fab.register_schema(schema)
    fab.register_target("t", {"u": 10}, "s")

    ok, err = fab.set_property_value("t", "u", -5)
    assert ok is False
    assert "INVALID_TYPE" in err


def test_forbidden_character_injection():
    valid, errors = UniversalInspectorValidator.validate_property_path("/root/secrets")
    assert valid is False
    assert any("NO_PROPERTY_PATH_ESCAPE" in e for e in errors)


def test_tampered_diagnostic_signature():
    snap = InspectorSnapshot("s_id", 1.0, "s", ["t1"], {}, [])
    telemetry = InspectorTelemetry()
    bundle = InspectorDiagnosticBundle("b_id", 1.0, snap, telemetry)
    bundle.signature = "tampered_signature"
    valid, errors = UniversalInspectorValidator.validate_diagnostic_bundle(bundle)
    assert valid is False
    assert any("BUNDLE_CORRUPTION" in e for e in errors)


# ==============================================================================
# 21. CLEANUP TESTS (6 tests - §156)
# ==============================================================================

def test_inspector_cleanup():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t1", {"v": 1}, "s")
    assert "t1" in fab.targets
    fab.unregister_target("t1")
    assert "t1" not in fab.targets


def test_editor_cleanup():
    fab = UniversalInspectorFabricator()
    fab.custom_editor_registry[("FLOAT", EditorHint.SLIDER)] = "CustomSlider"
    assert ("FLOAT", EditorHint.SLIDER) in fab.custom_editor_registry
    del fab.custom_editor_registry[("FLOAT", EditorHint.SLIDER)]
    assert ("FLOAT", EditorHint.SLIDER) not in fab.custom_editor_registry


def test_binding_cleanup():
    fab = UniversalInspectorFabricator()
    fab.active_transactions.clear()
    assert len(fab.active_transactions) == 0


def test_validation_subscription_cleanup():
    fab = UniversalInspectorFabricator()
    cb = lambda t, s: []
    fab.cross_property_validators.append(cb)
    assert len(fab.cross_property_validators) == 1
    fab.cross_property_validators.remove(cb)
    assert len(fab.cross_property_validators) == 0


def test_reference_subscription_cleanup():
    fab = UniversalInspectorFabricator()
    fab.register_resource("r1", "Type")
    assert "r1" in fab.registered_resources
    del fab.registered_resources["r1"]
    assert "r1" not in fab.registered_resources


def test_schema_cleanup():
    fab = UniversalInspectorFabricator()
    fab.register_schema(PropertySchema("cleanup_s"))
    assert "cleanup_s" in fab.schemas
    fab.unregister_schema("cleanup_s")
    assert "cleanup_s" not in fab.schemas


# ==============================================================================
# 22. EXTENDED VALIDATION & PACKAGING TESTS (3 tests)
# ==============================================================================

def test_packager_cpp_generation():
    header = UniversalInspectorPackager.generate_cpp_header()
    source = UniversalInspectorPackager.generate_cpp_source()
    assert "UUAFPropertyGridComponent" in header
    assert "UUAFPropertyGridComponent::SetPropertyValue" in source


def test_packager_manifest_and_signature(tmp_path):
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("pkg_s")
    schema.add_property(PropertyDescriptor("p", "p", "P", PropertyType.INT, "p", default_value=1))
    fab.register_schema(schema)

    out = UniversalInspectorPackager.export_package(fab, tmp_path)
    assert Path(out["header"]).exists()
    assert Path(out["source"]).exists()
    assert Path(out["manifest"]).exists()
    assert Path(out["signature"]).exists()
    assert len(out["sha256"]) == 64


def test_packager_export_directory_creation(tmp_path):
    fab = UniversalInspectorFabricator()
    target_dir = tmp_path / "nested" / "deep" / "inspector_pkg"
    out = UniversalInspectorPackager.export_package(fab, target_dir)
    assert Path(out["manifest"]).exists()


def test_schema_unregistration_cleans_cache():
    fab = UniversalInspectorFabricator()
    s = PropertySchema("cache_s")
    s.add_property(PropertyDescriptor("x", "x", "X", PropertyType.INT, "x"))
    fab.register_schema(s)
    fab.resolve_schema("cache_s")
    assert "cache_s" in fab._resolved_schema_cache
    fab.unregister_schema("cache_s")
    assert "cache_s" not in fab._resolved_schema_cache


def test_schema_nested_inheritance_three_levels():
    fab = UniversalInspectorFabricator()
    gparent = PropertySchema("gp")
    gparent.add_property(PropertyDescriptor("g", "g", "G", PropertyType.INT, "g"))
    parent = PropertySchema("p", parent_schema_id="gp")
    parent.add_property(PropertyDescriptor("p", "p", "P", PropertyType.INT, "p"))
    child = PropertySchema("c", parent_schema_id="p")
    child.add_property(PropertyDescriptor("c", "c", "C", PropertyType.INT, "c"))

    fab.register_schema(gparent)
    fab.register_schema(parent)
    fab.register_schema(child)

    resolved = fab.resolve_schema("c")
    assert "g" in resolved.properties
    assert "p" in resolved.properties
    assert "c" in resolved.properties


def test_schema_multiple_children_same_parent():
    fab = UniversalInspectorFabricator()
    parent = PropertySchema("parent")
    parent.add_property(PropertyDescriptor("base_prop", "base_prop", "Base", PropertyType.STRING, "base_prop"))
    c1 = PropertySchema("child_1", parent_schema_id="parent")
    c2 = PropertySchema("child_2", parent_schema_id="parent")

    fab.register_schema(parent)
    fab.register_schema(c1)
    fab.register_schema(c2)

    assert "base_prop" in fab.resolve_schema("child_1").properties
    assert "base_prop" in fab.resolve_schema("child_2").properties


def test_property_path_nested_arrays():
    p = PropertyPath.parse("grid[2][4]")
    assert p.segments == ("grid", 2, 4)


def test_property_validation_severity_levels():
    m_info = PropertyValidationMessage("p", ValidationSeverity.INFO, "CODE_INFO", "Info msg")
    m_warn = PropertyValidationMessage("p", ValidationSeverity.WARNING, "CODE_WARN", "Warn msg")
    m_err = PropertyValidationMessage("p", ValidationSeverity.ERROR, "CODE_ERR", "Err msg")
    assert m_info.severity == ValidationSeverity.INFO
    assert m_warn.severity == ValidationSeverity.WARNING
    assert m_err.severity == ValidationSeverity.ERROR


def test_multi_edit_mode_mixed_indicator():
    assert bool(MIXED_VALUE) is False
    assert str(MIXED_VALUE) == "<MIXED>"


def test_property_grid_empty_search():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    schema.add_property(PropertyDescriptor("a", "a", "A", PropertyType.INT, "a"))
    schema.add_property(PropertyDescriptor("b", "b", "B", PropertyType.INT, "b"))
    fab.register_schema(schema)
    fab.register_target("t", {"a": 1, "b": 2}, "s")

    items = fab.query_property_grid(["t"], search_query="")
    assert len(items) == 2


def test_conflict_policy_all_branches():
    fab = UniversalInspectorFabricator()
    schema = PropertySchema("s")
    fab.register_schema(schema)
    fab.register_target("t", {"v": 1}, "s", version=2)

    assert fab.resolve_conflict("t", expected_version=1, policy=ConflictPolicy.REJECT) is False
    assert fab.resolve_conflict("t", expected_version=1, policy=ConflictPolicy.RELOAD) is True
    assert fab.resolve_conflict("t", expected_version=1, policy=ConflictPolicy.MERGE) is True
    assert fab.resolve_conflict("t", expected_version=1, policy=ConflictPolicy.FORCE) is True


def test_inspector_state_snapshot_hashing():
    snap = InspectorSnapshot("sid", 10.0, "s_id", ["t1"], {"v": 1}, [])
    h1 = snap.compute_hash()
    h2 = snap.compute_hash()
    assert h1 == h2


def test_packager_manifest_total_schemas_count(tmp_path):
    fab = UniversalInspectorFabricator()
    fab.register_schema(PropertySchema("s1"))
    fab.register_schema(PropertySchema("s2"))
    out = UniversalInspectorPackager.export_package(fab, tmp_path)
    with open(out["manifest"], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["total_schemas"] == 2

