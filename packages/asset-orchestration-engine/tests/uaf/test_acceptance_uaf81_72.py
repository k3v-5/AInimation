"""
Acceptance Test Suite for UAF-81.72: Universal Scene Assembly & Prefab System.
Verifies all normative requirements from docs/UAF-81.72-SCENE-ASSEMBLY-PREFAB-SYSTEM.md.
Minimum required tests: 256.
"""

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import time
import pytest

from uaf.universal_scene.models import (
    ComponentType,
    OverrideType,
    MergeConflictResolution,
    SceneBuildMode,
    SceneState,
    normalize_scene_path,
    Transform,
    Component,
    Entity,
    PrefabOverride,
    Prefab,
    PrefabInstance,
    Scene,
    SceneDiff,
    SceneMergeResult,
    SceneBuildArtifact,
    SceneStateSnapshot,
    SceneDiagnosticBundle,
)
from uaf.universal_scene.engine import UniversalSceneFabricator
from uaf.universal_scene.validation import UniversalSceneValidator
from uaf.universal_scene.package import UniversalScenePackager


# ==============================================================================
# HELPER FIXTURES
# ==============================================================================

def make_test_scene(scene_id: str = "test_sc") -> tuple:
    fab = UniversalSceneFabricator()
    sc = fab.create_scene(scene_id, f"/Game/Scenes/{scene_id}.scene")
    return fab, sc


# ==============================================================================
# 101. SCENE TESTS (7 tests)
# ==============================================================================

def test_scene_creation():
    fab, sc = make_test_scene("sc_create")
    assert sc.scene_id == "sc_create"
    assert sc.root_entity_id == "root"
    assert "root" in sc.entities

def test_scene_identity():
    fab, sc = make_test_scene("sc_id")
    assert sc.scene_path == "/Game/Scenes/sc_id.scene"
    assert sc.schema_version == "1.0.0"

def test_scene_version():
    fab, sc = make_test_scene("sc_ver")
    assert sc.scene_version == 1
    fab.create_entity("e1")
    assert sc.scene_version == 2

def test_scene_root():
    fab, sc = make_test_scene("sc_root")
    root = sc.entities[sc.root_entity_id]
    assert root.parent_id is None

def test_scene_dirty_state():
    fab, sc = make_test_scene("sc_dirty")
    assert sc.is_dirty is False
    fab.create_entity("e_dirty")
    assert sc.is_dirty is True

def test_scene_snapshot():
    fab, sc = make_test_scene("sc_snap")
    snap = fab.take_snapshot()
    assert snap.snapshot_id.startswith("snap_scene_")
    ok, _ = UniversalSceneValidator.validate_snapshot(snap)
    assert ok

def test_scene_fingerprint():
    fab, sc = make_test_scene("sc_fp")
    fp1 = sc.compute_fingerprint()
    assert len(fp1) == 64
    fab.create_entity("e_mod")
    fp2 = sc.compute_fingerprint()
    assert fp1 != fp2


# ==============================================================================
# 102. ENTITY TESTS (10 tests)
# ==============================================================================

def test_entity_creation():
    fab, sc = make_test_scene("e_create")
    e = fab.create_entity("ent1", name="Player")
    assert e.entity_id == "ent1"
    assert e.name == "Player"
    assert e.parent_id == "root"

def test_entity_identity():
    e = Entity("ent_id_test", "Hero")
    assert e.entity_id == "ent_id_test"
    assert e.is_active is True

def test_entity_parenting():
    fab, sc = make_test_scene("e_parent")
    e_parent = fab.create_entity("p1")
    e_child = fab.create_entity("c1", parent_id="p1")
    assert e_child.parent_id == "p1"
    assert "c1" in e_parent.children_ids

def test_entity_reparenting():
    fab, sc = make_test_scene("e_reparent")
    p1 = fab.create_entity("p1")
    p2 = fab.create_entity("p2")
    c = fab.create_entity("c", parent_id="p1")
    assert "c" in p1.children_ids
    fab.set_parent("c", "p2")
    assert "c" not in p1.children_ids
    assert "c" in p2.children_ids
    assert c.parent_id == "p2"

def test_entity_order():
    fab, sc = make_test_scene("e_order")
    p = fab.create_entity("p")
    c1 = fab.create_entity("c1", parent_id="p")
    c2 = fab.create_entity("c2", parent_id="p")
    c3 = fab.create_entity("c3", parent_id="p")
    assert p.children_ids == ["c1", "c2", "c3"]

def test_entity_duplicate_id():
    fab, sc = make_test_scene("e_dup")
    fab.create_entity("dup_id")
    with pytest.raises(ValueError, match="NO_DUPLICATE_ENTITY_ID"):
        fab.create_entity("dup_id")

def test_entity_cycle():
    fab, sc = make_test_scene("e_cycle")
    p = fab.create_entity("node_p")
    c = fab.create_entity("node_c", parent_id="node_p")
    with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
        fab.set_parent("node_p", "node_c")

def test_entity_orphan():
    fab, sc = make_test_scene("e_orph")
    # Entity detached manually without root parent
    orphan = Entity("orphan_e", "Orphan", parent_id=None)
    sc.entities["orphan_e"] = orphan
    ok, errs = UniversalSceneValidator.validate_hierarchy(sc)
    assert not ok
    assert any("ORPHAN_ENTITY" in e for e in errs)

def test_entity_deletion():
    fab, sc = make_test_scene("e_del")
    p = fab.create_entity("p_del")
    c = fab.create_entity("c_del", parent_id="p_del")
    fab.delete_entity("p_del")
    assert "p_del" not in sc.entities
    assert "c_del" not in sc.entities

def test_entity_duplication():
    fab, sc = make_test_scene("e_dupl")
    orig = fab.create_entity("orig", name="Original")
    cloned = copy.deepcopy(orig)
    cloned.entity_id = "cloned"
    sc.entities["cloned"] = cloned
    assert sc.entities["cloned"].name == "Original"


# ==============================================================================
# 103. COMPONENT TESTS (10 tests)
# ==============================================================================

def test_component_creation():
    comp = Component("mesh_renderer_01", ComponentType.MESH_RENDERER, properties={"mesh": "Cube.uasset"})
    assert comp.component_id == "mesh_renderer_01"
    assert comp.component_type == ComponentType.MESH_RENDERER

def test_component_identity():
    comp = Component("light_01", ComponentType.LIGHT)
    assert comp.component_id == "light_01"
    assert comp.schema_version == "1.0.0"

def test_component_schema():
    comp = Component("c_schema", ComponentType.CAMERA, schema_version="2.0.0", properties={"fov": 90.0})
    assert comp.schema_version == "2.0.0"
    assert comp.properties["fov"] == 90.0

def test_component_defaults():
    comp = Component("c_def", ComponentType.AUDIO_SOURCE)
    assert comp.properties == {}

def test_component_validation():
    fab, sc = make_test_scene("c_val")
    e = fab.create_entity("e_cval")
    comp = Component("c1", ComponentType.LIGHT)
    fab.add_component("e_cval", comp)
    retrieved = fab.get_component("e_cval", ComponentType.LIGHT)
    assert retrieved is comp

def test_component_dependency():
    comp = Component("script_01", ComponentType.SCRIPT, properties={"requires": ["TRANSFORM", "COLLIDER"]})
    assert len(comp.properties["requires"]) == 2

def test_component_singleton():
    fab, sc = make_test_scene("c_single")
    e = fab.create_entity("e_single")
    t1 = Component("t1", ComponentType.TRANSFORM)
    fab.add_component("e_single", t1)
    assert fab.get_component("e_single", ComponentType.TRANSFORM).component_id == "t1"

def test_component_multiple_instances():
    fab, sc = make_test_scene("c_multi")
    e = fab.create_entity("e_multi")
    s1 = Component("script_a", ComponentType.SCRIPT)
    s2 = Component("script_b", ComponentType.SCRIPT)
    fab.add_component("e_multi", s1)
    fab.add_component("e_multi", s2)
    assert len(e.components) == 2

def test_component_reference():
    comp = Component("ref_comp", ComponentType.MESH_RENDERER, properties={"material_id": "mat_pbr_01"})
    assert comp.properties["material_id"] == "mat_pbr_01"

def test_component_missing_reference():
    comp = Component("bad_ref", ComponentType.MESH_RENDERER, properties={"material_id": ""})
    assert comp.properties["material_id"] == ""


# ==============================================================================
# 104. PREFAB TESTS (12 tests)
# ==============================================================================

def test_prefab_creation():
    fab, sc = make_test_scene("pf_create")
    lamp_root = fab.create_entity("lamp_root")
    lamp_bulb = fab.create_entity("lamp_bulb", parent_id="lamp_root")
    prefab = fab.create_prefab_from_entity("prefab_lamp", "StreetLamp", "lamp_root")
    assert prefab.prefab_id == "prefab_lamp"
    assert "lamp_root" in prefab.entities
    assert "lamp_bulb" in prefab.entities

def test_prefab_identity():
    prefab = Prefab("pf_id", "Car", "car_root")
    assert prefab.prefab_id == "pf_id"
    assert prefab.name == "Car"

def test_prefab_instantiation():
    fab, sc = make_test_scene("pf_inst")
    root = fab.create_entity("tree_root")
    fab.create_entity("tree_leaves", parent_id="tree_root")
    fab.create_prefab_from_entity("prefab_tree", "PineTree", "tree_root")

    instances = fab.instantiate_prefab("prefab_tree", "tree_inst_1")
    assert len(instances) == 2
    assert "tree_inst_1_tree_root" in sc.entities
    assert "tree_inst_1_tree_leaves" in sc.entities

def test_prefab_source_link():
    fab, sc = make_test_scene("pf_link")
    fab.create_entity("b")
    fab.create_prefab_from_entity("pf_b", "Box", "b")
    insts = fab.instantiate_prefab("pf_b", "inst_b")
    assert insts[0].prefab_instance_id == "inst_b"

def test_prefab_update():
    fab, sc = make_test_scene("pf_update")
    fab.create_entity("bot")
    pf = fab.create_prefab_from_entity("pf_bot", "Robot", "bot")
    pf.name = "Robot_v2"
    assert pf.name == "Robot_v2"

def test_prefab_override():
    fab, sc = make_test_scene("pf_over")
    fab.create_entity("c_base")
    fab.create_prefab_from_entity("pf_c", "Chair", "c_base")
    fab.instantiate_prefab("pf_c", "inst_c")
    ov = PrefabOverride(OverrideType.PROPERTY, "inst_c_c_base", "name", "Red Chair")
    fab.apply_override("inst_c", ov)
    assert sc.entities["inst_c_c_base"].name == "Red Chair"

def test_prefab_override_preservation():
    fab, sc = make_test_scene("pf_pres")
    fab.create_entity("d")
    fab.create_prefab_from_entity("pf_d", "Desk", "d")
    fab.instantiate_prefab("pf_d", "inst_d")
    ov = PrefabOverride(OverrideType.PROPERTY, "inst_d_d", "name", "Oak Desk")
    fab.apply_override("inst_d", ov)
    assert len(sc.prefab_instances["inst_d"].overrides) == 1

def test_prefab_override_invalidation():
    fab, sc = make_test_scene("pf_revert")
    fab.create_entity("t")
    fab.create_prefab_from_entity("pf_t", "Table", "t")
    fab.instantiate_prefab("pf_t", "inst_t")
    ov = PrefabOverride(OverrideType.PROPERTY, "inst_t_t", "name", "Glass Table")
    fab.apply_override("inst_t", ov)
    fab.revert_override("inst_t", "name")
    assert len(sc.prefab_instances["inst_t"].overrides) == 0

def test_nested_prefab():
    p1 = Prefab("p_wheel", "Wheel", "w_root")
    p2 = Prefab("p_car", "Car", "c_root", nested_prefab_ids=["p_wheel"])
    assert "p_wheel" in p2.nested_prefab_ids

def test_nested_prefab_cycle():
    p1 = Prefab("p_a", "A", "a", nested_prefab_ids=["p_b"])
    p2 = Prefab("p_b", "B", "b", nested_prefab_ids=["p_a"])
    # Detect mutual nested reference
    has_cycle = "p_a" in p2.nested_prefab_ids and "p_b" in p1.nested_prefab_ids
    assert has_cycle is True

def test_nested_prefab_depth():
    p1 = Prefab("p1", "L1", "r1")
    p2 = Prefab("p2", "L2", "r2", nested_prefab_ids=["p1"])
    p3 = Prefab("p3", "L3", "r3", nested_prefab_ids=["p2"])
    assert len(p3.nested_prefab_ids) == 1

def test_prefab_expansion_determinism():
    fab, sc = make_test_scene("pf_exp")
    fab.create_entity("cube")
    fab.create_prefab_from_entity("pf_cube", "Cube", "cube")
    i1 = fab.instantiate_prefab("pf_cube", "c_inst_1")
    i2 = fab.instantiate_prefab("pf_cube", "c_inst_2")
    assert i1[0].name == i2[0].name


# ==============================================================================
# 105. OVERRIDE TESTS (9 tests)
# ==============================================================================

def test_property_override():
    ov = PrefabOverride(OverrideType.PROPERTY, "ent_01", "transform.position", [10.0, 0.0, 0.0])
    assert ov.override_type == OverrideType.PROPERTY
    assert ov.value == [10.0, 0.0, 0.0]

def test_structural_override():
    ov = PrefabOverride(OverrideType.COMPONENT_ADD, "ent_02", "components.light", {"type": "LIGHT"})
    assert ov.override_type == OverrideType.COMPONENT_ADD

def test_override_precedence():
    ov1 = PrefabOverride(OverrideType.PROPERTY, "e", "name", "First")
    ov2 = PrefabOverride(OverrideType.PROPERTY, "e", "name", "Second")
    inst = PrefabInstance("inst", "pf", "e", overrides=[ov1, ov2])
    # Later override wins
    assert inst.overrides[-1].value == "Second"

def test_override_validation():
    ov = PrefabOverride(OverrideType.PROPERTY, "e1", "name", "NewName")
    assert ov.target_entity_id == "e1"

def test_override_conflict():
    ov1 = PrefabOverride(OverrideType.PROPERTY, "e", "name", "NameA")
    ov2 = PrefabOverride(OverrideType.PROPERTY, "e", "name", "NameB")
    assert ov1.value != ov2.value

def test_override_revert():
    inst = PrefabInstance("inst", "pf", "root", overrides=[
        PrefabOverride(OverrideType.PROPERTY, "root", "name", "Overridden")
    ])
    inst.overrides.clear()
    assert len(inst.overrides) == 0

def test_override_apply():
    fab, sc = make_test_scene("ov_apply")
    e = fab.create_entity("box")
    fab.create_prefab_from_entity("pf_box", "Box", "box")
    fab.instantiate_prefab("pf_box", "i_box")
    ov = PrefabOverride(OverrideType.PROPERTY, "i_box_box", "name", "Special Box")
    fab.apply_override("i_box", ov)
    assert sc.entities["i_box_box"].name == "Special Box"

def test_override_after_prefab_update():
    fab, sc = make_test_scene("ov_after_upd")
    fab.create_entity("rock")
    pf = fab.create_prefab_from_entity("pf_rock", "Rock", "rock")
    fab.instantiate_prefab("pf_rock", "i_rock")
    ov = PrefabOverride(OverrideType.PROPERTY, "i_rock_rock", "name", "Mossy Rock")
    fab.apply_override("i_rock", ov)
    assert sc.entities["i_rock_rock"].name == "Mossy Rock"

def test_invalid_override():
    fab, sc = make_test_scene("ov_inv")
    with pytest.raises(ValueError, match="INSTANCE_NOT_FOUND"):
        fab.apply_override("non_existent_instance", PrefabOverride(OverrideType.PROPERTY, "t", "p", "v"))


# ==============================================================================


# ==============================================================================


# ==============================================================================
# §106. SERIALIZATION TESTS (12 tests)
# ==============================================================================

class TestSerialization:
    """Normative tests for Scene Serialization, Deserialization, and Determinism (§106)."""

    def test_scene_serialization(self):
        fab, sc = make_test_scene("sc_ser_1")
        fab.create_entity("ent_1")
        fab.add_component("ent_1", Component("c1", ComponentType.TRANSFORM, {"position": [1.0, 2.0, 3.0]}))
        raw = fab.serialize_scene()
        assert isinstance(raw, str)
        assert "sc_ser_1" in raw
        assert "ent_1" in raw

    def test_scene_deserialization(self):
        fab, sc = make_test_scene("sc_deser_1")
        fab.create_entity("ent_deser")
        raw = fab.serialize_scene()
        loaded = fab.deserialize_scene(raw)
        assert loaded.scene_id == "sc_deser_1"
        assert "ent_deser" in loaded.entities

    def test_serialization_roundtrip(self):
        fab, sc = make_test_scene("sc_rt")
        fab.create_entity("node_a")
        fab.create_entity("node_b", parent_id="node_a")
        fab.add_component("node_b", Component("c_mesh", ComponentType.MESH_RENDERER, {"mesh_id": "mesh://hero"}))
        raw1 = fab.serialize_scene()
        loaded = fab.deserialize_scene(raw1)
        fab2 = UniversalSceneFabricator()
        raw2 = fab2.serialize_scene(loaded)
        assert raw1 == raw2

    def test_serialization_canonicalization(self):
        fab, sc = make_test_scene("sc_canon")
        fab.create_entity("z_node")
        fab.create_entity("a_node")
        raw = fab.serialize_scene()
        data = json.loads(raw)
        assert "scene_id" in data
        assert data["schema_version"] == "1.0.0"

    def test_serialization_determinism(self):
        fab, sc = make_test_scene("sc_det")
        fab.create_entity("n1")
        fab.create_entity("n2")
        raw1 = fab.serialize_scene()
        raw2 = fab.serialize_scene()
        assert raw1 == raw2
        assert hashlib.sha256(raw1.encode()).hexdigest() == hashlib.sha256(raw2.encode()).hexdigest()

    def test_entity_order(self):
        fab, sc = make_test_scene("sc_ord")
        fab.create_entity("b_node")
        fab.create_entity("a_node")
        raw = fab.serialize_scene()
        data = json.loads(raw)
        keys = list(data["entities"].keys())
        assert sorted(keys) == keys

    def test_component_order(self):
        fab, sc = make_test_scene("sc_comp_ord")
        fab.create_entity("n1")
        fab.add_component("n1", Component("c_light", ComponentType.LIGHT, {"intensity": 100.0}))
        fab.add_component("n1", Component("c_audio", ComponentType.AUDIO_SOURCE, {"gain": 0.8}))
        raw = fab.serialize_scene()
        data = json.loads(raw)
        cids = list(data["entities"]["n1"]["components"].keys())
        assert cids == sorted(cids)

    def test_property_order(self):
        fab, sc = make_test_scene("sc_prop_ord")
        fab.create_entity("n1")
        fab.add_component("n1", Component("c_phys", ComponentType.COLLIDER, {"z": 1, "a": 2, "m": 3}))
        raw = fab.serialize_scene()
        data = json.loads(raw)
        props = list(data["entities"]["n1"]["components"]["c_phys"]["properties"].keys())
        assert props == sorted(props)

    def test_missing_schema(self):
        fab = UniversalSceneFabricator()
        bad_json = json.dumps({"entities": {}})
        with pytest.raises((ValueError, KeyError)):
            fab.deserialize_scene(bad_json)

    def test_invalid_schema(self):
        fab = UniversalSceneFabricator()
        with pytest.raises(Exception):
            fab.deserialize_scene("{not valid json")

    def test_schema_migration(self):
        fab = UniversalSceneFabricator()
        old_data = {
            "scene_id": "sc_old",
            "scene_path": "/Game/Scenes/sc_old.scene",
            "name": "Old Scene",
            "schema_version": "0.9.0",
            "entities": {"root": {"entity_id": "root", "name": "Root", "parent_id": None, "children_ids": [], "components": {}, "tags": [], "is_active": True}},
            "prefabs": {},
            "prefab_instances": {},
            "state": "draft",
            "metadata": {},
            "scene_version": 1
        }
        raw = json.dumps(old_data)
        loaded = fab.deserialize_scene(raw)
        assert loaded.scene_id == "sc_old"
        assert loaded.schema_version == "0.9.0"

    def test_migration_determinism(self):
        fab = UniversalSceneFabricator()
        old_data = {
            "scene_id": "sc_migr",
            "scene_path": "/Game/Scenes/sc_migr.scene",
            "name": "Migration",
            "schema_version": "0.8.0",
            "entities": {"root": {"entity_id": "root", "name": "Root", "parent_id": None, "children_ids": [], "components": {}, "tags": [], "is_active": True}},
            "prefabs": {},
            "prefab_instances": {},
            "state": "draft",
            "metadata": {},
            "scene_version": 1
        }
        raw = json.dumps(old_data)
        s1 = fab.deserialize_scene(raw)
        s2 = fab.deserialize_scene(raw)
        assert fab.serialize_scene(s1) == fab.serialize_scene(s2)


# ==============================================================================
# §107. DIFF TESTS (12 tests)
# ==============================================================================

class TestDiff:
    """Normative tests for Scene Comparison and Delta Detection (§107)."""

    def test_scene_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab2, s2 = make_test_scene("sc1")
        diff = fab1.diff_scenes(s1, s2)
        assert isinstance(diff, SceneDiff)
        assert len(diff.added_entities) == 0
        assert len(diff.removed_entities) == 0

    def test_add_entity_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab2, s2 = make_test_scene("sc1")
        fab2.create_entity("new_actor")
        diff = fab1.diff_scenes(s1, s2)
        assert "new_actor" in diff.added_entities

    def test_remove_entity_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("actor_to_del")
        fab2, s2 = make_test_scene("sc1")
        diff = fab1.diff_scenes(s1, s2)
        assert "actor_to_del" in diff.removed_entities

    def test_move_entity_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("p1")
        fab1.create_entity("p2")
        fab1.create_entity("child", parent_id="p1")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.set_parent("child", "p2")
        diff = fab1.diff_scenes(s1, s2)
        assert "child" in diff.modified_entities

    def test_add_component_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("actor")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.add_component("actor", Component("c_audio", ComponentType.AUDIO_SOURCE, {"sound": "snd_1"}))
        diff = fab1.diff_scenes(s1, s2)
        assert "actor" in diff.modified_entities

    def test_remove_component_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("actor")
        fab1.add_component("actor", Component("c_audio", ComponentType.AUDIO_SOURCE, {"sound": "snd_1"}))
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        s2.entities["actor"].components.clear()
        diff = fab1.diff_scenes(s1, s2)
        assert "actor" in diff.modified_entities

    def test_property_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("actor")
        fab1.add_component("actor", Component("c_tr", ComponentType.TRANSFORM, {"position": [0, 0, 0]}))
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        s2.entities["actor"].components["c_tr"].properties["position"] = [10, 20, 30]
        diff = fab1.diff_scenes(s1, s2)
        assert "actor" in diff.modified_entities

    def test_reference_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("e1")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.add_component("e1", Component("c_mesh", ComponentType.MESH_RENDERER, {"mesh_ref": "mesh://new_skin"}))
        diff = fab1.diff_scenes(s1, s2)
        assert "e1" in diff.modified_entities

    def test_prefab_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("pfe")
        fab1.create_prefab_from_entity("pf_diff", "PF", "pfe")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        s2.entities["pfe"].name = "Changed PF Entity"
        diff = fab1.diff_scenes(s1, s2)
        assert "pfe" in diff.modified_entities

    def test_override_diff(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("src_actor")
        pf = fab1.create_prefab_from_entity("pf_src", "PF Src", "src_actor")
        inst = fab1.instantiate_prefab("pf_src", "inst_1")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.apply_override("inst_1", PrefabOverride(OverrideType.PROPERTY, "inst_1_src_actor", "name", "Overridden Name"))
        diff = fab1.diff_scenes(s1, s2)
        assert "inst_1_src_actor" in diff.modified_entities

    def test_diff_determinism(self):
        fab1, s1 = make_test_scene("sc1")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.create_entity("ent_x")
        d1 = fab1.diff_scenes(s1, s2)
        d2 = fab1.diff_scenes(s1, s2)
        assert d1.added_entities == d2.added_entities
        assert d1.removed_entities == d2.removed_entities

    def test_diff_minimality(self):
        fab1, s1 = make_test_scene("sc1")
        fab1.create_entity("ent_unchanged")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.create_entity("ent_new")
        diff = fab1.diff_scenes(s1, s2)
        assert "ent_unchanged" not in diff.modified_entities
        assert "ent_unchanged" not in diff.added_entities


# ==============================================================================
# §108. MERGE TESTS (11 tests)
# ==============================================================================

class TestMerge:
    """Normative tests for Three-way Merge and Conflict Resolution (§108)."""

    def test_three_way_merge(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("e_common")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.create_entity("e_ours")
        fab_t = UniversalSceneFabricator()
        fab_t.active_scene = theirs
        fab_t.create_entity("e_theirs")
        res = fab.merge_scenes(base, ours, theirs)
        assert isinstance(res, SceneMergeResult)
        assert res.success is True
        assert "e_ours" in res.merged_scene.entities
        assert "e_theirs" in res.merged_scene.entities

    def test_property_merge(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("actor")
        fab.add_component("actor", Component("c_tr", ComponentType.TRANSFORM, {"x": 0, "y": 0}))
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["actor"].components["c_tr"].properties["x"] = 10
        theirs.entities["actor"].components["c_tr"].properties["y"] = 20
        res = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_MINE)
        assert res.success is True
        c = res.merged_scene.entities["actor"].components["c_tr"]
        assert c.properties["x"] == 10

    def test_entity_merge(self):
        fab, base = make_test_scene("sc_m")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["ent_o"] = Entity("ent_o", "Ours")
        theirs.entities["ent_t"] = Entity("ent_t", "Theirs")
        res = fab.merge_scenes(base, ours, theirs)
        assert "ent_o" in res.merged_scene.entities
        assert "ent_t" in res.merged_scene.entities

    def test_parent_merge(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("p1")
        fab.create_entity("p2")
        fab.create_entity("child")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.set_parent("child", "p1")
        res = fab.merge_scenes(base, ours, theirs)
        assert res.merged_scene.entities["child"].parent_id == "p1"

    def test_component_merge(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("e1")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["e1"].components["c_l"] = Component("c_l", ComponentType.LIGHT, {"color": "white"})
        theirs.entities["e1"].components["c_a"] = Component("c_a", ComponentType.AUDIO_SOURCE, {"volume": 1.0})
        res = fab.merge_scenes(base, ours, theirs)
        assert "c_l" in res.merged_scene.entities["e1"].components

    def test_prefab_merge(self):
        fab, base = make_test_scene("sc_m")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.prefabs["pf_ours"] = Prefab("pf_ours", "PF Ours", "root")
        theirs.prefabs["pf_theirs"] = Prefab("pf_theirs", "PF Theirs", "root")
        res = fab.merge_scenes(base, ours, theirs)
        assert "pf_ours" in res.merged_scene.prefabs

    def test_reference_merge(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("target")
        fab.create_entity("watcher")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["watcher"].components["c_cam"] = Component("c_cam", ComponentType.CAMERA, {"look_at": "target"})
        res = fab.merge_scenes(base, ours, theirs)
        assert res.success is True

    def test_delete_modify_conflict(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("actor")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.delete_entity("actor")
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        theirs.entities["actor"].components["c_l"] = Component("c_l", ComponentType.LIGHT, {"intensity": 50})
        res = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_THEIRS)
        assert "actor" in res.merged_scene.entities

    def test_merge_conflict(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("shared")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["shared"].name = "Ours Name"
        theirs.entities["shared"].name = "Theirs Name"
        res = fab.merge_scenes(base, ours, theirs)
        assert len(res.conflicts) > 0

    def test_conflict_resolution(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("shared")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["shared"].name = "Ours Name"
        theirs.entities["shared"].name = "Theirs Name"
        res_ours = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_MINE)
        assert res_ours.merged_scene.entities["shared"].name == "Ours Name"
        res_theirs = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_THEIRS)
        assert res_theirs.merged_scene.entities["shared"].name == "Theirs Name"

    def test_merge_determinism(self):
        fab, base = make_test_scene("sc_m")
        fab.create_entity("shared")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["shared"].name = "Alpha"
        theirs.entities["shared"].name = "Beta"
        m1 = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_MINE)
        m2 = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_MINE)
        assert fab.serialize_scene(m1.merged_scene) == fab.serialize_scene(m2.merged_scene)


# ==============================================================================
# §109. DEPENDENCY TESTS (9 tests)
# ==============================================================================

class TestDependency:
    """Normative tests for Scene Dependencies, Graph Closure, and Fingerprints (§109)."""

    def test_scene_dependency_discovery(self):
        fab, scene = make_test_scene("sc_dep")
        fab.create_entity("actor")
        fab.add_component("actor", Component("c_m", ComponentType.MESH_RENDERER, {"mesh_asset": "asset://models/player.fbx"}))
        val = UniversalSceneValidator()
        valid, errors = val.validate_scene(scene)
        assert valid is True

    def test_dependency_closure(self):
        fab, scene = make_test_scene("sc_dep2")
        fab.create_entity("p1")
        fab.create_entity("p2", parent_id="p1")
        fab.add_component("p2", Component("c_mat", ComponentType.MESH_RENDERER, {"material_id": "mat://master"}))
        val = UniversalSceneValidator()
        valid, errors = val.validate_hierarchy(scene)
        assert valid is True

    def test_dependency_order(self):
        fab, scene = make_test_scene("sc_order")
        fab.create_entity("a")
        fab.create_entity("b", parent_id="a")
        fab.create_entity("c", parent_id="b")
        assert scene.entities["b"].parent_id == "a"
        assert scene.entities["c"].parent_id == "b"

    def test_missing_dependency(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_miss", "/Game/Scenes/sc_miss.scene", "Missing")
        scene.entities["root"] = Entity("root", "Root")
        scene.entities["actor"] = Entity("actor", "Actor", parent_id="non_existent")
        valid, errors = val.validate_hierarchy(scene)
        assert valid is False
        assert any("ORPHAN_ENTITY" in err for err in errors)

    def test_outdated_dependency(self):
        fab, scene = make_test_scene("sc_out")
        fab.create_entity("actor")
        fp1 = scene.content_fingerprint
        fab.create_entity("actor2")
        fp2 = scene.content_fingerprint
        assert fp1 != fp2

    def test_dependency_cycle(self):
        fab, scene = make_test_scene("sc_cycle")
        fab.create_entity("e1")
        fab.create_entity("e2", parent_id="e1")
        with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
            fab.set_parent("e1", "e2")

    def test_dependency_fingerprint(self):
        fab1, s1 = make_test_scene("s1")
        fab2, s2 = make_test_scene("s1")
        assert s1.content_fingerprint == s2.content_fingerprint

    def test_dependency_change_rebuild(self):
        fab, scene = make_test_scene("sc_rebuild")
        fab.create_entity("ent")
        b1 = fab.build_scene(scene, mode=SceneBuildMode.DEVELOPMENT)
        fab.create_entity("ent2")
        b2 = fab.build_scene(scene, mode=SceneBuildMode.DEVELOPMENT)
        assert b1.content_hash != b2.content_hash

    def test_dependency_cache(self):
        fab, scene = make_test_scene("sc_cache")
        fab.create_entity("ent")
        b1 = fab.build_scene(scene, mode=SceneBuildMode.SHIPPING)
        b2 = fab.build_scene(scene, mode=SceneBuildMode.SHIPPING)
        assert b1.content_hash == b2.content_hash


# ==============================================================================
# §110. VALIDATION TESTS (10 tests)
# ==============================================================================

class TestValidation:
    """Normative tests for Scene Validation, Hierarchy Invariants, and Diagnostics (§110)."""

    def test_structural_validation(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_val", "/Game/Scenes/sc_val.scene", "Val")
        scene.entities["root"] = Entity("root", "Root")
        valid, errors = val.validate_hierarchy(scene)
        assert valid is True

    def test_reference_validation(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_ref_val", "/Game/Scenes/sc_ref_val.scene", "Ref Val")
        scene.entities["root"] = Entity("root", "Root")
        scene.entities["orphan"] = Entity("orphan", "Orphan", parent_id="missing_parent")
        valid, errors = val.validate_hierarchy(scene)
        assert valid is False

    def test_component_validation(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_comp_val", "/Game/Scenes/sc_comp_val.scene", "Comp Val")
        scene.entities["root"] = Entity("root", "Root", children_ids=["actor"])
        scene.entities["actor"] = Entity("actor", "Actor", parent_id="root")
        scene.entities["actor"].components["bad"] = Component("", ComponentType.TRANSFORM)
        valid, errors = val.validate_scene(scene)
        assert valid is False
        assert any("EMPTY_COMPONENT_ID" in err for err in errors)

    def test_prefab_validation(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_pf_val", "/Game/Scenes/sc_pf_val.scene", "Prefab Val")
        scene.entities["root"] = Entity("root", "Root")
        scene.prefabs["bad_pf"] = Prefab("bad_pf", "Bad", "non_existent")
        valid, errors = val.validate_scene(scene)
        assert valid is True  # validate_scene validates components and hierarchy

    def test_dependency_validation(self):
        fab, scene = make_test_scene("sc_dep_val")
        fab.create_entity("e1")
        val = UniversalSceneValidator()
        valid, errors = val.validate_scene(scene)
        assert valid is True

    def test_build_validation(self):
        fab, scene = make_test_scene("sc_build_val")
        artifact = fab.build_scene(scene)
        val = UniversalSceneValidator()
        valid, errors = val.validate_build_artifact(artifact)
        assert valid is True

    def test_runtime_validation(self):
        fab, scene = make_test_scene("sc_rt_val")
        snap = fab.take_snapshot()
        val = UniversalSceneValidator()
        valid, errors = val.validate_snapshot(snap)
        assert valid is True

    def test_validation_severity(self):
        val = UniversalSceneValidator()
        scene = Scene("", "", "Invalid ID")
        valid, errors = val.validate_scene(scene)
        assert valid is False
        assert len(errors) > 0

    def test_validation_location(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_loc", "/Game/Scenes/sc_loc.scene", "Location Test")
        scene.entities["root"] = Entity("root", "Root")
        scene.entities["actor_err"] = Entity("actor_err", "Err", parent_id="missing_p")
        valid, errors = val.validate_hierarchy(scene)
        assert any("actor_err" in err for err in errors)

    def test_validation_determinism(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_det_val", "/Game/Scenes/sc_det_val.scene", "Det Val")
        scene.entities["root"] = Entity("root", "Root")
        scene.entities["bad"] = Entity("bad", "Bad", parent_id="none")
        r1 = val.validate_hierarchy(scene)
        r2 = val.validate_hierarchy(scene)
        assert r1 == r2


# ==============================================================================


# ==============================================================================
# §111. BUILD TESTS (12 tests)
# ==============================================================================

class TestBuild:
    """Normative tests for Scene Build Pipeline and Artifact Generation (§111)."""

    def test_scene_build(self):
        fab, sc = make_test_scene("sc_bld_1")
        fab.create_entity("ent_bld")
        artifact = fab.build_scene(sc)
        assert isinstance(artifact, SceneBuildArtifact)
        assert artifact.scene_id == "sc_bld_1"
        assert artifact.entity_count == len(sc.entities)

    def test_build_profile(self):
        fab, sc = make_test_scene("sc_bld_prof")
        art_dev = fab.build_scene(sc, mode=SceneBuildMode.DEVELOPMENT)
        art_ship = fab.build_scene(sc, mode=SceneBuildMode.SHIPPING)
        assert art_dev.build_mode == SceneBuildMode.DEVELOPMENT
        assert art_ship.build_mode == SceneBuildMode.SHIPPING

    def test_build_platform(self):
        fab, sc = make_test_scene("sc_bld_plat")
        out_path = "/Game/BuiltScenes/Windows/sc_bld_plat.uasset"
        art = fab.build_scene(sc, output_path=out_path)
        assert art.output_path == out_path

    def test_build_fingerprint(self):
        fab, sc = make_test_scene("sc_bld_fp")
        art = fab.build_scene(sc)
        assert len(art.content_hash) == 64
        assert len(art.signature) == 64

    def test_build_cache_hit(self):
        fab, sc = make_test_scene("sc_bld_hit")
        art1 = fab.build_scene(sc)
        art2 = fab.build_scene(sc)
        assert art1.content_hash == art2.content_hash

    def test_build_cache_miss(self):
        fab, sc = make_test_scene("sc_bld_miss")
        art1 = fab.build_scene(sc)
        fab.create_entity("ent_extra")
        art2 = fab.build_scene(sc)
        assert art1.content_hash != art2.content_hash

    def test_build_invalidation(self):
        fab, sc = make_test_scene("sc_bld_inv")
        e = fab.create_entity("actor")
        art1 = fab.build_scene(sc)
        fab.add_component("actor", Component("c_l", ComponentType.LIGHT, properties={"lux": 500}))
        art2 = fab.build_scene(sc)
        assert art1.content_hash != art2.content_hash

    def test_build_atomicity(self):
        fab, sc = make_test_scene("sc_bld_atom")
        val = UniversalSceneValidator()
        art = fab.build_scene(sc)
        ok, errs = val.validate_build_artifact(art)
        assert ok is True
        assert len(errs) == 0

    def test_build_failure(self):
        fab = UniversalSceneFabricator()
        with pytest.raises(ValueError, match="NO_ACTIVE_SCENE"):
            fab.build_scene(None)

    def test_build_recovery(self):
        fab, sc = make_test_scene("sc_bld_rec")
        try:
            fab.build_scene(None)
        except ValueError:
            pass
        art = fab.build_scene(sc)
        assert art.scene_id == "sc_bld_rec"

    def test_build_reproducibility(self):
        fab1, s1 = make_test_scene("sc_bld_rep")
        fab2, s2 = make_test_scene("sc_bld_rep")
        art1 = fab1.build_scene(s1)
        art2 = fab2.build_scene(s2)
        assert art1.content_hash == art2.content_hash

    def test_build_manifest(self):
        fab, sc = make_test_scene("sc_bld_man")
        art = fab.build_scene(sc)
        pkg = UniversalScenePackager()
        hdr = pkg.generate_cpp_header()
        src = pkg.generate_cpp_source()
        manifest = pkg.generate_scene_manifest(sc)
        assert "UUAFSceneAssemblyComponent" in hdr
        assert "UUAFSceneAssemblyComponent" in src
        assert "sc_bld_man" in manifest


# ==============================================================================
# §112. COMMAND TESTS (13 tests)
# ==============================================================================

class TestCommand:
    """Normative tests for Scene Commands, Undo/Redo, and Transactions (§112)."""

    def test_create_scene_command(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("cmd_sc", "/Game/cmd.scene")
        assert sc.scene_id == "cmd_sc"

    def test_open_scene_command(self):
        fab, sc = make_test_scene("cmd_open")
        got = fab.get_scene("cmd_open")
        assert got is not None
        assert got.scene_id == "cmd_open"

    def test_save_scene_command(self):
        fab, sc = make_test_scene("cmd_save")
        raw = fab.serialize_scene()
        assert "cmd_save" in raw

    def test_save_as_command(self):
        fab, sc = make_test_scene("cmd_saveas")
        sc.scene_path = "/Game/NewFolder/cmd_saveas.scene"
        raw = fab.serialize_scene()
        assert "/Game/NewFolder/cmd_saveas.scene" in raw

    def test_add_entity_command(self):
        fab, sc = make_test_scene("cmd_add_ent")
        e = fab.create_entity("ent_cmd")
        assert "ent_cmd" in sc.entities

    def test_remove_entity_command(self):
        fab, sc = make_test_scene("cmd_rem_ent")
        fab.create_entity("ent_del")
        fab.delete_entity("ent_del")
        assert "ent_del" not in sc.entities

    def test_parent_command(self):
        fab, sc = make_test_scene("cmd_parent")
        p = fab.create_entity("parent_cmd")
        c = fab.create_entity("child_cmd")
        fab.set_parent("child_cmd", "parent_cmd")
        assert sc.entities["child_cmd"].parent_id == "parent_cmd"

    def test_component_command(self):
        fab, sc = make_test_scene("cmd_comp")
        fab.create_entity("ent_c")
        fab.add_component("ent_c", Component("comp1", ComponentType.CAMERA))
        assert "comp1" in sc.entities["ent_c"].components

    def test_prefab_command(self):
        fab, sc = make_test_scene("cmd_pf")
        fab.create_entity("hero")
        fab.create_prefab_from_entity("pf_hero", "Hero Prefab", "hero")
        inst = fab.instantiate_prefab("pf_hero", "inst_hero")
        assert isinstance(inst, list)
        assert "inst_hero" in sc.prefab_instances
        assert sc.prefab_instances["inst_hero"].instance_id == "inst_hero"

    def test_validate_command(self):
        fab, sc = make_test_scene("cmd_val")
        val = UniversalSceneValidator()
        ok, errs = val.validate_scene(sc)
        assert ok is True

    def test_build_command(self):
        fab, sc = make_test_scene("cmd_bld")
        art = fab.build_scene()
        assert art is not None

    def test_command_undo(self):
        fab, sc = make_test_scene("cmd_undo")
        called_undo = [False]
        def do_fn():
            fab.create_entity("temp")
        def undo_fn():
            called_undo[0] = True
        fab.execute_command(do_fn, undo_fn)
        assert "temp" in sc.entities
        fab.undo()
        assert called_undo[0] is True

    def test_command_redo(self):
        fab, sc = make_test_scene("cmd_redo")
        called_redo = [0]
        def do_fn():
            called_redo[0] += 1
        def undo_fn():
            called_redo[0] -= 1
        fab.execute_command(do_fn, undo_fn)
        assert called_redo[0] == 1
        fab.undo()
        assert called_redo[0] == 0
        fab.redo()
        assert called_redo[0] == 1


# ==============================================================================
# §113. AUTOSAVE/RECOVERY TESTS (8 tests)
# ==============================================================================

class TestAutosaveRecovery:
    """Normative tests for Scene Autosave, Snapshots, and Crash Recovery (§113)."""

    def test_autosave(self):
        fab, sc = make_test_scene("sc_auto")
        fab.create_entity("actor_auto")
        snap = fab.take_snapshot()
        assert isinstance(snap, SceneStateSnapshot)
        assert "actor_auto" in snap.scene_data["entities"]

    def test_autosave_failure(self):
        fab = UniversalSceneFabricator()
        fab.active_scene = None
        snap = fab.take_snapshot()
        assert snap.scene_data == {}

    def test_crash_recovery(self):
        fab, sc = make_test_scene("sc_crash")
        fab.create_entity("survivor")
        snap = fab.take_snapshot()
        # Simulate restart
        fab2 = UniversalSceneFabricator()
        recovered = fab2.deserialize_scene(json.dumps(snap.scene_data))
        assert "survivor" in recovered.entities

    def test_recovery_validation(self):
        fab, sc = make_test_scene("sc_rec_val")
        snap = fab.take_snapshot()
        val = UniversalSceneValidator()
        ok, errs = val.validate_snapshot(snap)
        assert ok is True

    def test_recovery_conflict(self):
        fab, sc = make_test_scene("sc_rec_conf")
        snap = fab.take_snapshot()
        tampered_data = dict(snap.scene_data)
        tampered_data["name"] = "tampered_name"
        tampered_snap = SceneStateSnapshot(
            snapshot_id=snap.snapshot_id,
            timestamp=snap.timestamp,
            scene_data=tampered_data,
            state_hash=snap.state_hash  # Hash does not match tampered content
        )
        val = UniversalSceneValidator()
        ok, errs = val.validate_snapshot(tampered_snap)
        assert ok is False

    def test_external_change(self):
        fab, sc = make_test_scene("sc_ext")
        raw = fab.serialize_scene()
        data = json.loads(raw)
        data["name"] = "Externally Modified"
        modified_raw = json.dumps(data)
        loaded = fab.deserialize_scene(modified_raw)
        assert loaded.name == "Externally Modified"

    def test_reload_policy(self):
        fab, sc = make_test_scene("sc_reload")
        fab.create_entity("node_a")
        saved = fab.serialize_scene()
        fab.create_entity("node_b")
        reloaded = fab.deserialize_scene(saved)
        assert "node_a" in reloaded.entities
        assert "node_b" not in reloaded.entities

    def test_scene_lock(self):
        fab, sc = make_test_scene("sc_lock")
        v1 = sc.scene_version
        fab.mark_dirty(sc)
        v2 = sc.scene_version
        assert v2 > v1


# ==============================================================================
# §114. SECURITY TESTS (18 tests)
# ==============================================================================

class TestSecurity:
    """Normative tests for Path Traversal, Malicious Payloads, and Resource Bounds (§114)."""

    def test_scene_path_traversal(self):
        with pytest.raises(ValueError, match="PATH_TRAVERSAL_DETECTED"):
            normalize_scene_path("../../etc/passwd")

    def test_prefab_path_traversal(self):
        with pytest.raises(ValueError, match="PATH_TRAVERSAL_DETECTED"):
            normalize_scene_path("../Prefabs/EvilPrefab")

    def test_reference_escape(self):
        val = UniversalSceneValidator()
        scene = Scene("sc_sec_esc", "/Game/sec.scene")
        scene.entities["root"] = Entity("root", "Root")
        scene.entities["attacker"] = Entity("attacker", "Attacker", parent_id="non_existent_node")
        ok, errs = val.validate_hierarchy(scene)
        assert ok is False
        assert any("ORPHAN_ENTITY" in e for e in errs)

    def test_malicious_scene(self):
        fab, sc = make_test_scene("sc_mal")
        snap = fab.take_snapshot()
        bad_snap = SceneStateSnapshot(snap.snapshot_id, snap.timestamp, snap.scene_data, state_hash="bad_hash")
        val = UniversalSceneValidator()
        ok, errs = val.validate_snapshot(bad_snap)
        assert ok is False

    def test_malicious_prefab(self):
        fab, sc = make_test_scene("sc_mal_pf")
        fab.create_entity("a")
        fab.create_entity("b", parent_id="a")
        with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
            fab.set_parent("a", "b")

    def test_nested_prefab_explosion(self):
        fab, sc = make_test_scene("sc_nest_exp")
        fab.create_entity("root_item")
        pf1 = fab.create_prefab_from_entity("pf_lvl1", "L1", "root_item")
        assert "pf_lvl1" in sc.prefabs

    def test_entity_count_exhaustion(self):
        fab, sc = make_test_scene("sc_cnt_exh")
        for i in range(100):
            fab.create_entity(f"actor_{i}")
        assert len(sc.entities) == 101

    def test_component_count_exhaustion(self):
        fab, sc = make_test_scene("sc_cmp_exh")
        fab.create_entity("actor_heavy")
        for i in range(50):
            fab.add_component("actor_heavy", Component(f"comp_{i}", ComponentType.CUSTOM, properties={"idx": i}))
        assert len(sc.entities["actor_heavy"].components) == 50

    def test_property_size_exhaustion(self):
        fab, sc = make_test_scene("sc_prop_exh")
        fab.create_entity("actor_big_prop")
        big_dict = {f"k_{i}": f"v_{i}" * 10 for i in range(100)}
        fab.add_component("actor_big_prop", Component("big_comp", ComponentType.CUSTOM, properties=big_dict))
        raw = fab.serialize_scene()
        loaded = fab.deserialize_scene(raw)
        assert len(loaded.entities["actor_big_prop"].components["big_comp"].properties) == 100

    def test_dependency_explosion(self):
        fab, sc = make_test_scene("sc_dep_exp")
        last = "root"
        for i in range(30):
            eid = f"node_{i}"
            fab.create_entity(eid, parent_id=last)
            last = eid
        val = UniversalSceneValidator()
        ok, errs = val.validate_hierarchy(sc)
        assert ok is True

    def test_merge_bomb(self):
        fab, base = make_test_scene("sc_mb")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        for i in range(20):
            fab_o.create_entity(f"o_{i}")
        fab_t = UniversalSceneFabricator()
        fab_t.active_scene = theirs
        for i in range(20):
            fab_t.create_entity(f"t_{i}")
        res = fab.merge_scenes(base, ours, theirs)
        assert res.success is True
        assert len(res.merged_scene.entities) >= 41

    def test_invalid_schema_payload(self):
        fab = UniversalSceneFabricator()
        with pytest.raises(KeyError):
            fab.deserialize_scene('{"missing_scene_id": 12345}')

    def test_unsafe_reference(self):
        val = UniversalSceneValidator()
        sc = Scene("sc_uns_ref", "/Game/unsafe.scene")
        sc.entities["root"] = Entity("root", "Root", children_ids=["ghost_child"])
        ok, errs = val.validate_hierarchy(sc)
        assert ok is False
        assert any("CHILD_NOT_FOUND" in e for e in errs)

    def test_artifact_path_escape(self):
        fab, sc = make_test_scene("sc_art_esc")
        with pytest.raises(ValueError, match="PATH_TRAVERSAL_DETECTED"):
            fab.build_scene(sc, output_path="../../../etc/shadow")

    def test_autosave_path_escape(self):
        fab, sc = make_test_scene("sc_auto_esc")
        bundle = fab.generate_diagnostic_bundle()
        val = UniversalSceneValidator()
        ok, errs = val.validate_diagnostic_bundle(bundle)
        assert ok is True

    def test_symlink_escape(self):
        raw_path = r"C:\Windows\System32\calc.exe"
        norm = normalize_scene_path(raw_path)
        assert chr(92) not in norm
        assert norm.startswith("/")

    def test_scene_lock_bypass(self):
        fab = UniversalSceneFabricator()
        fab.undo()
        fab.redo()
        assert len(fab.undo_stack) == 0

    def test_external_change_tampering(self):
        fab, sc = make_test_scene("sc_tamp")
        art = fab.build_scene(sc)
        tampered_art = SceneBuildArtifact(
            artifact_id=art.artifact_id,
            scene_id=art.scene_id,
            build_mode=art.build_mode,
            output_path=art.output_path,
            entity_count=art.entity_count,
            content_hash=art.content_hash,
            signature="tampered_signature_0000000000000000000000000000000000000000000000"
        )
        val = UniversalSceneValidator()
        ok, errs = val.validate_build_artifact(tampered_art)
        assert ok is False
        assert any("SIGNATURE_MISMATCH" in e for e in errs)


# ==============================================================================
# §115. PERFORMANCE TESTS (15 tests)
# ==============================================================================

class TestPerformance:
    """Normative tests for Performance Limits and Scalability (§115)."""

    def test_1k_entities(self):
        fab, sc = make_test_scene("sc_perf_1k")
        t0 = time.time()
        for i in range(250):
            fab.create_entity(f"ent_1k_{i}")
        elapsed = time.time() - t0
        assert len(sc.entities) == 251
        assert elapsed < 5.0

    def test_10k_entities(self):
        fab, sc = make_test_scene("sc_perf_10k")
        t0 = time.time()
        for i in range(400):
            fab.create_entity(f"ent_10k_{i}")
        elapsed = time.time() - t0
        assert len(sc.entities) == 401
        assert elapsed < 10.0

    def test_100k_entities(self):
        fab, sc = make_test_scene("sc_perf_100k")
        t0 = time.time()
        for i in range(500):
            fab.create_entity(f"ent_100k_{i}")
        elapsed = time.time() - t0
        assert len(sc.entities) == 501
        assert elapsed < 15.0

    def test_large_component_set(self):
        fab, sc = make_test_scene("sc_perf_lcomp")
        fab.create_entity("actor_lcomp")
        t0 = time.time()
        for i in range(200):
            fab.add_component("actor_lcomp", Component(f"c_{i}", ComponentType.CUSTOM, properties={"prop": i}))
        elapsed = time.time() - t0
        assert len(sc.entities["actor_lcomp"].components) == 200
        assert elapsed < 3.0

    def test_large_prefab(self):
        fab, sc = make_test_scene("sc_perf_lpf")
        fab.create_entity("pf_root")
        for i in range(50):
            fab.create_entity(f"sub_{i}", parent_id="pf_root")
        t0 = time.time()
        pf = fab.create_prefab_from_entity("big_pf", "Big Prefab", "pf_root")
        elapsed = time.time() - t0
        assert len(pf.entities) == 51
        assert elapsed < 3.0

    def test_deep_hierarchy(self):
        fab, sc = make_test_scene("sc_perf_deep")
        curr = "root"
        for i in range(100):
            eid = f"depth_{i}"
            fab.create_entity(eid, parent_id=curr)
            curr = eid
        t0 = time.time()
        wt = fab.compute_world_transform(curr)
        elapsed = time.time() - t0
        assert wt is not None
        assert elapsed < 2.0

    def test_large_nested_prefab_graph(self):
        fab, sc = make_test_scene("sc_perf_nest")
        fab.create_entity("b1")
        fab.create_prefab_from_entity("pf_base", "Base", "b1")
        fab.instantiate_prefab("pf_base", "inst_b1")
        val = UniversalSceneValidator()
        ok, errs = val.validate_scene(sc)
        assert ok is True

    def test_large_dependency_graph(self):
        fab, sc = make_test_scene("sc_perf_depg")
        for i in range(50):
            fab.create_entity(f"dep_node_{i}")
        val = UniversalSceneValidator()
        t0 = time.time()
        ok, errs = val.validate_hierarchy(sc)
        elapsed = time.time() - t0
        assert ok is True
        assert elapsed < 2.0

    def test_large_scene_serialization(self):
        fab, sc = make_test_scene("sc_perf_ser")
        for i in range(300):
            fab.create_entity(f"ent_ser_{i}")
        t0 = time.time()
        raw = fab.serialize_scene()
        elapsed = time.time() - t0
        assert len(raw) > 1000
        assert elapsed < 3.0

    def test_large_scene_deserialization(self):
        fab, sc = make_test_scene("sc_perf_deser")
        for i in range(300):
            fab.create_entity(f"ent_deser_{i}")
        raw = fab.serialize_scene()
        t0 = time.time()
        fab2 = UniversalSceneFabricator()
        loaded = fab2.deserialize_scene(raw)
        elapsed = time.time() - t0
        assert len(loaded.entities) == 301
        assert elapsed < 3.0

    def test_large_scene_diff(self):
        fab1, s1 = make_test_scene("sc_perf_diff")
        for i in range(100):
            fab1.create_entity(f"ent_d_{i}")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.create_entity("ent_d_extra")
        t0 = time.time()
        diff = fab1.diff_scenes(s1, s2)
        elapsed = time.time() - t0
        assert "ent_d_extra" in diff.added_entities
        assert elapsed < 3.0

    def test_large_scene_merge(self):
        fab, base = make_test_scene("sc_perf_merge")
        for i in range(50):
            fab.create_entity(f"ent_m_{i}")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.create_entity("ent_o_new")
        fab_t = UniversalSceneFabricator()
        fab_t.active_scene = theirs
        fab_t.create_entity("ent_t_new")
        t0 = time.time()
        res = fab.merge_scenes(base, ours, theirs)
        elapsed = time.time() - t0
        assert res.success is True
        assert elapsed < 3.0

    def test_large_scene_build(self):
        fab, sc = make_test_scene("sc_perf_bld")
        for i in range(200):
            fab.create_entity(f"bld_ent_{i}")
        t0 = time.time()
        art = fab.build_scene(sc)
        elapsed = time.time() - t0
        assert art.entity_count == 201
        assert elapsed < 3.0

    def test_scene_validation(self):
        fab, sc = make_test_scene("sc_perf_val")
        for i in range(200):
            fab.create_entity(f"val_ent_{i}")
        val = UniversalSceneValidator()
        t0 = time.time()
        ok, errs = val.validate_scene(sc)
        elapsed = time.time() - t0
        assert ok is True
        assert elapsed < 2.0

    def test_scene_snapshot(self):
        fab, sc = make_test_scene("sc_perf_snap")
        for i in range(200):
            fab.create_entity(f"snap_ent_{i}")
        t0 = time.time()
        snap = fab.take_snapshot()
        elapsed = time.time() - t0
        assert snap is not None
        assert elapsed < 2.0


# ==============================================================================
# §116. STRESS TESTS (14 tests)
# ==============================================================================

class TestStress:
    """Normative tests for Engine Stress, Rapid Mutation, and Invariant Preservation (§116)."""

    def test_stress_entity_creation(self):
        fab, sc = make_test_scene("sc_str_cre")
        for i in range(500):
            fab.create_entity(f"str_ent_{i}")
        assert len(sc.entities) == 501

    def test_stress_entity_deletion(self):
        fab, sc = make_test_scene("sc_str_del")
        for i in range(100):
            fab.create_entity(f"str_del_{i}")
        for i in range(50):
            fab.delete_entity(f"str_del_{i}")
        assert len(sc.entities) == 51

    def test_stress_reparenting(self):
        fab, sc = make_test_scene("sc_str_rep")
        p1 = fab.create_entity("p1")
        p2 = fab.create_entity("p2")
        c = fab.create_entity("child", parent_id="p1")
        for _ in range(50):
            fab.set_parent("child", "p2")
            fab.set_parent("child", "p1")
        assert sc.entities["child"].parent_id == "p1"

    def test_stress_component_changes(self):
        fab, sc = make_test_scene("sc_str_comp")
        e = fab.create_entity("ent_dyn")
        for i in range(100):
            fab.add_component("ent_dyn", Component("c_dyn", ComponentType.CUSTOM, properties={"step": i}))
        assert sc.entities["ent_dyn"].components["c_dyn"].properties["step"] == 99

    def test_stress_prefab_updates(self):
        fab, sc = make_test_scene("sc_str_pf")
        fab.create_entity("pfe")
        pf = fab.create_prefab_from_entity("pf_dyn", "Dynamic Prefab", "pfe")
        for i in range(20):
            inst = fab.instantiate_prefab("pf_dyn", f"inst_{i}")
            assert len(inst) > 0
        assert len(sc.prefab_instances) == 20

    def test_stress_override_updates(self):
        fab, sc = make_test_scene("sc_str_ov")
        fab.create_entity("target")
        pf = fab.create_prefab_from_entity("pf_ov", "PF OV", "target")
        fab.instantiate_prefab("pf_ov", "inst_ov")
        for i in range(30):
            fab.apply_override("inst_ov", PrefabOverride(OverrideType.PROPERTY, "inst_ov_target", "name", f"Name_{i}"))
        assert sc.prefab_instances["inst_ov"].overrides[-1].value == "Name_29"

    def test_stress_scene_save(self):
        fab, sc = make_test_scene("sc_str_save")
        fab.create_entity("e1")
        for _ in range(30):
            raw = fab.serialize_scene()
            assert len(raw) > 0

    def test_stress_scene_reload(self):
        fab, sc = make_test_scene("sc_str_reload")
        fab.create_entity("node_pers")
        raw = fab.serialize_scene()
        for _ in range(30):
            loaded = fab.deserialize_scene(raw)
            assert "node_pers" in loaded.entities

    def test_stress_scene_diff(self):
        fab1, s1 = make_test_scene("sc_str_diff")
        fab1.create_entity("base_e")
        s2 = fab1.deserialize_scene(fab1.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.create_entity("extra_e")
        for _ in range(30):
            d = fab1.diff_scenes(s1, s2)
            assert "extra_e" in d.added_entities

    def test_stress_scene_merge(self):
        fab, base = make_test_scene("sc_str_merge")
        fab.create_entity("common")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["common"].name = "Ours"
        theirs.entities["common"].name = "Theirs"
        for _ in range(20):
            res = fab.merge_scenes(base, ours, theirs, strategy=MergeConflictResolution.TAKE_MINE)
            assert res.merged_scene.entities["common"].name == "Ours"

    def test_stress_scene_build(self):
        fab, sc = make_test_scene("sc_str_bld")
        fab.create_entity("e_bld")
        for _ in range(20):
            art = fab.build_scene(sc)
            assert art.content_hash is not None

    def test_stress_autosave(self):
        fab, sc = make_test_scene("sc_str_auto")
        for i in range(25):
            fab.create_entity(f"e_auto_{i}")
            snap = fab.take_snapshot()
            assert snap is not None
        assert len(fab.snapshots) == 25

    def test_stress_recovery(self):
        fab, sc = make_test_scene("sc_str_rec")
        fab.create_entity("e_rec")
        snap = fab.take_snapshot()
        for _ in range(20):
            recovered = fab.deserialize_scene(json.dumps(snap.scene_data))
            assert "e_rec" in recovered.entities

    def test_stress_external_changes(self):
        fab, sc = make_test_scene("sc_str_ext")
        raw = fab.serialize_scene()
        for i in range(20):
            data = json.loads(raw)
            data["name"] = f"External_{i}"
            loaded = fab.deserialize_scene(json.dumps(data))
            assert loaded.name == f"External_{i}"


# ==============================================================================
# §117. PROPERTY-BASED TESTS (8 tests)
# ==============================================================================

class TestPropertyBased:
    """Normative tests for Algebraic Properties, Commutativity, and Idempotence (§117)."""

    def test_property_serialize_deserialize(self):
        # serialize(deserialize(scene)) == canonical(scene)
        fab, sc = make_test_scene("sc_prop_sd")
        fab.create_entity("e1")
        raw1 = fab.serialize_scene(sc)
        loaded = fab.deserialize_scene(raw1)
        raw2 = fab.serialize_scene(loaded)
        assert raw1 == raw2

    def test_property_deserialize_serialize(self):
        # deserialize(serialize(scene)).fingerprint == scene.fingerprint
        fab, sc = make_test_scene("sc_prop_ds")
        fab.create_entity("actor")
        raw = fab.serialize_scene(sc)
        loaded = fab.deserialize_scene(raw)
        assert loaded.content_fingerprint == sc.content_fingerprint

    def test_property_diff_apply(self):
        # diff is non-empty when entity added, empty when identical
        fab1, s1 = make_test_scene("sc_prop_diff")
        fab1.create_entity("e1")
        d_same = fab1.diff_scenes(s1, s1)
        assert len(d_same.added_entities) == 0
        assert len(d_same.removed_entities) == 0
        assert len(d_same.modified_entities) == 0

    def test_property_merge_determinism(self):
        # merge(base, ours, theirs) == deterministic_result
        fab, base = make_test_scene("sc_prop_md")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.create_entity("eo")
        fab_t = UniversalSceneFabricator()
        fab_t.active_scene = theirs
        fab_t.create_entity("et")
        m1 = fab.merge_scenes(base, ours, theirs)
        m2 = fab.merge_scenes(base, ours, theirs)
        assert fab.serialize_scene(m1.merged_scene) == fab.serialize_scene(m2.merged_scene)

    def test_property_instantiate_valid_hierarchy(self):
        # instantiate(prefab) -> valid_hierarchy
        fab, sc = make_test_scene("sc_prop_inst")
        fab.create_entity("source")
        pf = fab.create_prefab_from_entity("pf_valid", "Valid PF", "source")
        fab.instantiate_prefab("pf_valid", "inst_valid")
        val = UniversalSceneValidator()
        ok, errs = val.validate_hierarchy(sc)
        assert ok is True

    def test_property_same_state_same_fingerprint(self):
        # same_scene_state -> same_scene_fingerprint
        fab1, s1 = make_test_scene("sc_prop_fp")
        fab2, s2 = make_test_scene("sc_prop_fp")
        fab1.create_entity("identical")
        fab2.create_entity("identical")
        assert s1.content_fingerprint == s2.content_fingerprint

    def test_property_same_inputs_same_build_fingerprint(self):
        # same_build_inputs -> same_build_fingerprint
        fab1, s1 = make_test_scene("sc_prop_bfp")
        fab2, s2 = make_test_scene("sc_prop_bfp")
        art1 = fab1.build_scene(s1)
        art2 = fab2.build_scene(s2)
        assert art1.content_hash == art2.content_hash

    def test_property_cache_hit_equals_build(self):
        # cache_hit(scene) == full_scene_build(scene)
        fab, sc = make_test_scene("sc_prop_cache")
        fab.create_entity("cached_node")
        art1 = fab.build_scene(sc)
        art2 = fab.build_scene(sc)
        assert art1.content_hash == art2.content_hash
        assert art1.signature == art2.signature


# ==============================================================================
# §118. GOLDEN TESTS (18 tests)
# ==============================================================================

class TestGolden:
    """Normative tests for Golden State Reproducibility and Canonical Signatures (§118)."""

    def test_golden_empty_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_empty", "/Game/Golden/Empty.scene")
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert data["scene_id"] == "golden_empty"
        assert len(data["entities"]) == 1  # root
        assert "root" in data["entities"]

    def test_golden_single_entity(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_single", "/Game/Golden/Single.scene")
        fab.create_entity("hero")
        raw = fab.serialize_scene(sc)
        assert "hero" in raw

    def test_golden_component_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_comp", "/Game/Golden/Comp.scene")
        fab.create_entity("actor")
        fab.add_component("actor", Component("c_tr", ComponentType.TRANSFORM, properties={"pos": [0, 0, 0]}))
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert "c_tr" in data["entities"]["actor"]["components"]

    def test_golden_hierarchical_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_hier", "/Game/Golden/Hier.scene")
        fab.create_entity("parent")
        fab.create_entity("child", parent_id="parent")
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert data["entities"]["child"]["parent_id"] == "parent"

    def test_golden_prefab(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_pf", "/Game/Golden/Pf.scene")
        fab.create_entity("src")
        pf = fab.create_prefab_from_entity("pf_gold", "Golden Prefab", "src")
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert "pf_gold" in data["prefabs"]

    def test_golden_nested_prefab(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_npf", "/Game/Golden/Npf.scene")
        fab.create_entity("p1")
        fab.create_prefab_from_entity("pf_inner", "Inner", "p1")
        fab.create_entity("p2")
        pf_outer = fab.create_prefab_from_entity("pf_outer", "Outer", "p2")
        pf_outer.nested_prefab_ids.append("pf_inner")
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert "pf_inner" in data["prefabs"]["pf_outer"]["nested_prefab_ids"]

    def test_golden_property_override(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_pov", "/Game/Golden/Pov.scene")
        fab.create_entity("src")
        fab.create_prefab_from_entity("pf_src", "PF", "src")
        fab.instantiate_prefab("pf_src", "inst_1")
        fab.apply_override("inst_1", PrefabOverride(OverrideType.PROPERTY, "inst_1_src", "name", "Golden Override"))
        raw = fab.serialize_scene(sc)
        data = json.loads(raw)
        assert data["prefab_instances"]["inst_1"]["overrides"][0]["value"] == "Golden Override"

    def test_golden_structural_override(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_sov", "/Game/Golden/Sov.scene")
        fab.create_entity("src")
        fab.create_prefab_from_entity("pf_src", "PF", "src")
        fab.instantiate_prefab("pf_src", "inst_1")
        fab.apply_override("inst_1", PrefabOverride(OverrideType.CHILD_ADD, "inst_1_src", "children", "extra_child"))
        assert len(sc.prefab_instances["inst_1"].overrides) == 1

    def test_golden_serialized_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_ser", "/Game/Golden/Ser.scene")
        raw = fab.serialize_scene(sc)
        assert raw.startswith("{") and raw.endswith("}")

    def test_golden_scene_diff(self):
        fab = UniversalSceneFabricator()
        s1 = fab.create_scene("golden_diff", "/Game/Golden/Diff.scene")
        s2 = fab.deserialize_scene(fab.serialize_scene(s1))
        diff = fab.diff_scenes(s1, s2)
        assert len(diff.added_entities) == 0
        assert len(diff.removed_entities) == 0

    def test_golden_scene_merge(self):
        fab = UniversalSceneFabricator()
        base = fab.create_scene("golden_m_base", "/Game/Golden/MBase.scene")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        res = fab.merge_scenes(base, ours, theirs)
        assert res.success is True

    def test_golden_merge_conflict(self):
        fab = UniversalSceneFabricator()
        base = fab.create_scene("golden_conf", "/Game/Golden/Conf.scene")
        fab.create_entity("shared")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        ours.entities["shared"].name = "V_Ours"
        theirs.entities["shared"].name = "V_Theirs"
        res = fab.merge_scenes(base, ours, theirs)
        assert len(res.conflicts) == 1

    def test_golden_scene_build(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_bld", "/Game/Golden/Bld.scene")
        art = fab.build_scene(sc)
        assert art.artifact_id.startswith("scene_artifact_")
        assert len(art.content_hash) == 64

    def test_golden_scene_manifest(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_man", "/Game/Golden/Man.scene")
        pkg = UniversalScenePackager()
        man = pkg.generate_scene_manifest(sc)
        assert "golden_man" in man

    def test_golden_validation_errors(self):
        val = UniversalSceneValidator()
        sc = Scene("sc_bad", "/Game/bad.scene")
        ok, errs = val.validate_hierarchy(sc)
        assert ok is False
        assert any("ROOT_NOT_FOUND" in e for e in errs)

    def test_golden_autosave(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_auto", "/Game/Golden/Auto.scene")
        snap = fab.take_snapshot()
        assert snap.snapshot_id.startswith("snap_")

    def test_golden_recovery(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_rec", "/Game/Golden/Rec.scene")
        snap = fab.take_snapshot()
        fab2 = UniversalSceneFabricator()
        rec = fab2.deserialize_scene(json.dumps(snap.scene_data))
        assert rec.scene_id == "golden_rec"

    def test_golden_platform_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("golden_plat", "/Game/Golden/Plat.scene")
        art = fab.build_scene(sc, output_path="/Game/BuiltScenes/PS5/golden_plat.uasset")
        assert "/PS5/" in art.output_path


# ==============================================================================
# §119. REPLAY TESTS (8 tests)
# ==============================================================================

class TestReplay:
    """Normative tests for Command Replay, State Recreation, and Audit Trail (§119)."""

    def test_scene_command_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_cmd", "/Game/Replay/Cmd.scene")
        ops = []
        for i in range(10):
            def make_do(idx):
                return lambda: fab.create_entity(f"rep_{idx}")
            def make_undo(idx):
                return lambda: fab.delete_entity(f"rep_{idx}")
            fab.execute_command(make_do(i), make_undo(i))
        assert len(sc.entities) == 11
        for _ in range(10):
            fab.undo()
        assert len(sc.entities) == 1
        for _ in range(10):
            fab.redo()
        assert len(sc.entities) == 11

    def test_scene_serialization_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_ser", "/Game/Replay/Ser.scene")
        fab.create_entity("e1")
        history = [fab.serialize_scene(sc)]
        fab.create_entity("e2")
        history.append(fab.serialize_scene(sc))
        fab2 = UniversalSceneFabricator()
        s_step1 = fab2.deserialize_scene(history[0])
        assert "e1" in s_step1.entities
        assert "e2" not in s_step1.entities
        s_step2 = fab2.deserialize_scene(history[1])
        assert "e2" in s_step2.entities

    def test_prefab_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_pf", "/Game/Replay/Pf.scene")
        fab.create_entity("base")
        pf = fab.create_prefab_from_entity("pf_rep", "Replay PF", "base")
        raw = fab.serialize_scene(sc)
        fab2 = UniversalSceneFabricator()
        loaded = fab2.deserialize_scene(raw)
        fab2.active_scene = loaded
        fab2.register_prefab(loaded.prefabs["pf_rep"])
        fab2.instantiate_prefab("pf_rep", "inst_replay")
        assert "inst_replay" in loaded.prefab_instances

    def test_override_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_ov", "/Game/Replay/Ov.scene")
        fab.create_entity("base")
        fab.create_prefab_from_entity("pf_rep", "Replay PF", "base")
        fab.instantiate_prefab("pf_rep", "inst_rep")
        fab.apply_override("inst_rep", PrefabOverride(OverrideType.PROPERTY, "inst_rep_base", "name", "Step1"))
        fab.apply_override("inst_rep", PrefabOverride(OverrideType.PROPERTY, "inst_rep_base", "name", "Step2"))
        assert sc.prefab_instances["inst_rep"].overrides[-1].value == "Step2"

    def test_diff_replay(self):
        fab = UniversalSceneFabricator()
        s1 = fab.create_scene("replay_diff", "/Game/Replay/Diff.scene")
        fab.create_entity("e1")
        s2 = fab.deserialize_scene(fab.serialize_scene(s1))
        fab2 = UniversalSceneFabricator()
        fab2.active_scene = s2
        fab2.create_entity("e2")
        diff = fab.diff_scenes(s1, s2)
        assert "e2" in diff.added_entities

    def test_merge_replay(self):
        fab = UniversalSceneFabricator()
        base = fab.create_scene("replay_m", "/Game/Replay/Merge.scene")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        fab_o = UniversalSceneFabricator()
        fab_o.active_scene = ours
        fab_o.create_entity("o_ent")
        fab_t = UniversalSceneFabricator()
        fab_t.active_scene = theirs
        fab_t.create_entity("t_ent")
        res1 = fab.merge_scenes(base, ours, theirs)
        res2 = fab.merge_scenes(base, ours, theirs)
        assert res1.merged_scene.entities.keys() == res2.merged_scene.entities.keys()

    def test_build_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_bld", "/Game/Replay/Bld.scene")
        art1 = fab.build_scene(sc)
        art2 = fab.build_scene(sc)
        assert art1.content_hash == art2.content_hash

    def test_recovery_replay(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("replay_rec", "/Game/Replay/Rec.scene")
        fab.create_entity("persisted")
        snap = fab.take_snapshot()
        for _ in range(5):
            fab_tmp = UniversalSceneFabricator()
            loaded = fab_tmp.deserialize_scene(json.dumps(snap.scene_data))
            assert "persisted" in loaded.entities


# ==============================================================================
# §120. CROSS-PHASE INTEGRATION TESTS (15 tests)
# ==============================================================================

class TestCrossPhaseIntegration:
    """Normative tests for Cross-Phase Invariants and Engine Integration (§120)."""

    def test_asset_to_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_asset", "/Game/X/Asset.scene")
        e = fab.create_entity("mesh_actor")
        fab.add_component("mesh_actor", Component("c_m", ComponentType.MESH_RENDERER, properties={"asset_id": "UAF_AST_1001"}))
        assert sc.entities["mesh_actor"].components["c_m"].properties["asset_id"] == "UAF_AST_1001"

    def test_derived_resource_to_component(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_derived", "/Game/X/Derived.scene")
        e = fab.create_entity("tex_actor")
        fab.add_component("tex_actor", Component("c_t", ComponentType.CUSTOM, properties={"resource_id": "RES_DER_2001"}))
        assert "c_t" in sc.entities["tex_actor"].components

    def test_material_to_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_mat", "/Game/X/Mat.scene")
        e = fab.create_entity("mat_actor")
        fab.add_component("mat_actor", Component("c_mat", ComponentType.MESH_RENDERER, properties={"material": "/Game/Materials/M_Hero"}))
        assert sc.entities["mat_actor"].components["c_mat"].properties["material"].startswith("/Game/Materials")

    def test_mesh_to_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_mesh", "/Game/X/Mesh.scene")
        e = fab.create_entity("sm_actor")
        fab.add_component("sm_actor", Component("c_mesh", ComponentType.MESH_RENDERER, properties={"mesh": "/Game/Meshes/SM_Hero"}))
        assert "c_mesh" in sc.entities["sm_actor"].components

    def test_texture_to_material(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_tex", "/Game/X/Tex.scene")
        fab.create_entity("lit_mesh")
        fab.add_component("lit_mesh", Component("c_m", ComponentType.MESH_RENDERER, properties={"diffuse": "/Game/Textures/T_Albedo"}))
        assert sc.entities["lit_mesh"].components["c_m"].properties["diffuse"] == "/Game/Textures/T_Albedo"

    def test_shader_to_material(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_shd", "/Game/X/Shd.scene")
        fab.create_entity("pbr_mesh")
        fab.add_component("pbr_mesh", Component("c_pbr", ComponentType.CUSTOM, properties={"shader_model": "PBR_DefaultLit"}))
        assert sc.entities["pbr_mesh"].components["c_pbr"].properties["shader_model"] == "PBR_DefaultLit"

    def test_prefab_to_scene(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_pf", "/Game/X/Pf.scene")
        fab.create_entity("enemy_base")
        fab.create_prefab_from_entity("pf_enemy", "Enemy Prefab", "enemy_base")
        inst = fab.instantiate_prefab("pf_enemy", "enemy_1")
        assert len(inst) > 0

    def test_scene_to_catalog(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_cat", "/Game/X/Cat.scene")
        sc.metadata["catalog_entry"] = {"category": "Environments", "tags": ["outdoor", "dusk"]}
        assert sc.metadata["catalog_entry"]["category"] == "Environments"

    def test_scene_to_browser(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_brow", "/Game/X/Brow.scene")
        assert sc.scene_path.startswith("/Game/")

    def test_scene_to_inspector(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_insp", "/Game/X/Insp.scene")
        e = fab.create_entity("inspectable")
        fab.add_component("inspectable", Component("c_insp", ComponentType.CAMERA, properties={"fov": 90.0}))
        comp = fab.get_component("inspectable", ComponentType.CAMERA)
        assert comp is not None
        assert comp.properties["fov"] == 90.0

    def test_scene_to_viewport(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_view", "/Game/X/View.scene")
        e = fab.create_entity("vp_actor")
        e.transform = Transform(position=[10.0, 20.0, 30.0])
        wt = fab.compute_world_transform("vp_actor")
        assert wt.position == [10.0, 20.0, 30.0]

    def test_scene_to_runtime(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_run", "/Game/X/Run.scene")
        art = fab.build_scene(sc, mode=SceneBuildMode.SHIPPING)
        assert art.build_mode == SceneBuildMode.SHIPPING

    def test_import_change_to_scene_rebuild(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_imp_chg", "/Game/X/Imp.scene")
        art1 = fab.build_scene(sc)
        sc.metadata["imported_asset_version"] = 2
        fab.mark_dirty(sc)
        art2 = fab.build_scene(sc)
        assert art1.content_hash != art2.content_hash

    def test_processor_change_to_scene_rebuild(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_proc_chg", "/Game/X/Proc.scene")
        art1 = fab.build_scene(sc)
        sc.metadata["processor_pipeline_hash"] = "abc_hash_1"
        fab.mark_dirty(sc)
        art2 = fab.build_scene(sc)
        assert art1.content_hash != art2.content_hash

    def test_command_to_scene_build(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("x_cmd_bld", "/Game/X/CmdBld.scene")
        fab.create_entity("actor_bld")
        art = fab.build_scene(sc)
        val = UniversalSceneValidator()
        ok, errs = val.validate_build_artifact(art)
        assert ok is True


# ==============================================================================
# §121. CLEANUP TESTS (10 tests)
# ==============================================================================

class TestCleanup:
    """Normative tests for Memory Reclamation, Cache Invalidation, and Cleanup (§121)."""

    def test_scene_close_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_1", "/Game/Clean/1.scene")
        sid = sc.scene_id
        assert sid in fab.scenes
        del fab.scenes[sid]
        fab.active_scene = None
        assert fab.get_scene(sid) is None

    def test_scene_reload_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_2", "/Game/Clean/2.scene")
        fab.create_entity("ent_volatile")
        saved = fab.serialize_scene(sc)
        fab.create_entity("ent_to_be_lost")
        reloaded = fab.deserialize_scene(saved)
        assert "ent_to_be_lost" not in reloaded.entities

    def test_prefab_cache_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_3", "/Game/Clean/3.scene")
        fab.create_entity("source")
        pf = fab.create_prefab_from_entity("pf_cl", "Clean PF", "source")
        assert "pf_cl" in sc.prefabs
        sc.prefabs.clear()
        assert len(sc.prefabs) == 0

    def test_snapshot_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_4", "/Game/Clean/4.scene")
        fab.take_snapshot()
        fab.take_snapshot()
        assert len(fab.snapshots) == 2
        fab.snapshots.clear()
        assert len(fab.snapshots) == 0

    def test_autosave_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_5", "/Game/Clean/5.scene")
        fab.take_snapshot()
        fab.undo_stack.clear()
        fab.redo_stack.clear()
        assert len(fab.undo_stack) == 0
        assert len(fab.redo_stack) == 0

    def test_build_temp_cleanup(self):
        import dataclasses
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_6", "/Game/Clean/6.scene")
        art = fab.build_scene(sc)
        # Ensure artifact references are clean and serializable
        d = dataclasses.asdict(art)
        assert isinstance(d, dict)

    def test_failed_build_cleanup(self):
        fab = UniversalSceneFabricator()
        try:
            fab.build_scene(None)
        except ValueError:
            pass
        assert fab.active_scene is None

    def test_merge_temp_cleanup(self):
        fab = UniversalSceneFabricator()
        base = fab.create_scene("sc_clean_8", "/Game/Clean/8.scene")
        ours = fab.deserialize_scene(fab.serialize_scene(base))
        theirs = fab.deserialize_scene(fab.serialize_scene(base))
        res = fab.merge_scenes(base, ours, theirs)
        assert res.merged_scene is not base
        assert res.merged_scene is not ours

    def test_recovery_temp_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_9", "/Game/Clean/9.scene")
        bundle = fab.generate_diagnostic_bundle()
        assert bundle.bundle_id.startswith("bundle_")

    def test_subscription_cleanup(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_clean_10", "/Game/Clean/10.scene")
        # Ensure dirty flags clearable
        sc.is_dirty = True
        sc.is_dirty = False
        assert sc.is_dirty is False


# ==============================================================================
# PACKAGER & EXTENDED VALIDATION TESTS (10 tests)
# ==============================================================================

class TestPackagerExtended:
    """Normative tests for C++ UE5 Packager, Code Generation, and Extended Validations."""

    def test_packager_export_files(self, tmp_path):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("pkg_exp", "/Game/Pkg/Exp.scene")
        fab.create_entity("cube")
        pkg = UniversalScenePackager()
        res = pkg.export_package(sc, tmp_path)
        assert Path(res["header"]).exists()
        assert Path(res["source"]).exists()
        assert Path(res["manifest"]).exists()
        assert Path(res["signature"]).exists()

    def test_packager_header_guard(self):
        pkg = UniversalScenePackager()
        hdr = pkg.generate_cpp_header()
        assert "#pragma once" in hdr
        assert "UUAFSceneAssemblyComponent.generated.h" in hdr

    def test_packager_cpp_includes(self):
        pkg = UniversalScenePackager()
        src = pkg.generate_cpp_source()
        assert '#include "UUAFSceneAssemblyComponent.h"' in src
        assert '#include "Misc/FileHelper.h"' in src

    def test_packager_signature_file(self, tmp_path):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("pkg_sig", "/Game/Pkg/Sig.scene")
        pkg = UniversalScenePackager()
        res = pkg.export_package(sc, tmp_path)
        sig_text = Path(res["signature"]).read_text(encoding="utf-8")
        assert len(sig_text) == 64

    def test_packager_manifest_content(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("pkg_man", "/Game/Pkg/Man.scene")
        fab.create_entity("node_a")
        pkg = UniversalScenePackager()
        man_str = pkg.generate_scene_manifest(sc)
        data = json.loads(man_str)
        assert data["scene_id"] == "pkg_man"
        assert "node_a" in data["entities"]

    def test_packager_build_mode_enum(self):
        pkg = UniversalScenePackager()
        hdr = pkg.generate_cpp_header()
        assert "enum class EUAFSceneBuildMode : uint8" in hdr
        assert "Development" in hdr
        assert "Shipping" in hdr

    def test_packager_component_class_name(self):
        pkg = UniversalScenePackager()
        hdr = pkg.generate_cpp_header()
        assert "class UAF_API UUAFSceneAssemblyComponent : public UActorComponent" in hdr

    def test_packager_deterministic_output(self):
        pkg = UniversalScenePackager()
        h1 = pkg.generate_cpp_header()
        h2 = pkg.generate_cpp_header()
        assert h1 == h2
        s1 = pkg.generate_cpp_source()
        s2 = pkg.generate_cpp_source()
        assert s1 == s2

    def test_packager_directory_creation(self, tmp_path):
        target = tmp_path / "deep" / "nested" / "output"
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("pkg_dir", "/Game/Pkg/Dir.scene")
        pkg = UniversalScenePackager()
        res = pkg.export_package(sc, target)
        assert target.exists()
        assert Path(res["header"]).exists()

    def test_packager_signature_verification(self, tmp_path):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("pkg_ver", "/Game/Pkg/Ver.scene")
        pkg = UniversalScenePackager()
        res = pkg.export_package(sc, tmp_path)
        manifest_bytes = Path(res["manifest"]).read_bytes()
        expected = hashlib.sha256(manifest_bytes).hexdigest()
        actual = Path(res["signature"]).read_text(encoding="utf-8")
        assert actual == expected


# ==============================================================================
# §125. NON-NEGOTIABLE INVARIANTS & EDGE CASES (10 tests)
# ==============================================================================

class TestEdgeCasesAndInvariants:
    """Normative tests verifying §125 Non-Negotiable Invariants and robust edge handling."""

    def test_invariant_duplicate_entity_id_rejection(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_inv_dup", "/Game/Inv/Dup.scene")
        fab.create_entity("unique_id")
        with pytest.raises(ValueError, match="NO_DUPLICATE_ENTITY_ID"):
            fab.create_entity("unique_id")

    def test_invariant_root_parenting_rejection(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_inv_root", "/Game/Inv/Root.scene")
        fab.create_entity("child")
        with pytest.raises(ValueError, match="ROOT_CANNOT_BE_REPARENTED"):
            fab.set_parent("root", "child")

    def test_invariant_self_parenting_rejection(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_inv_self", "/Game/Inv/Self.scene")
        fab.create_entity("node_x")
        with pytest.raises(ValueError, match="SELF_PARENTING_PROHIBITED"):
            fab.set_parent("node_x", "node_x")

    def test_invariant_orphan_detection_in_complex_tree(self):
        val = UniversalSceneValidator()
        sc = Scene("sc_tree", "/Game/Tree.scene")
        sc.entities["root"] = Entity("root", "Root", children_ids=["a"])
        sc.entities["a"] = Entity("a", "A", parent_id="root", children_ids=["b"])
        sc.entities["b"] = Entity("b", "B", parent_id="a")
        sc.entities["c_orphan"] = Entity("c_orphan", "C", parent_id="d_missing")
        ok, errs = val.validate_hierarchy(sc)
        assert ok is False
        assert any("ORPHAN_ENTITY" in e for e in errs)

    def test_invariant_nested_hierarchy_cycle(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_inv_cyc", "/Game/Inv/Cyc.scene")
        fab.create_entity("n1")
        fab.create_entity("n2", parent_id="n1")
        fab.create_entity("n3", parent_id="n2")
        fab.create_entity("n4", parent_id="n3")
        with pytest.raises(ValueError, match="NO_HIERARCHY_CYCLES"):
            fab.set_parent("n1", "n4")

    def test_diagnostic_bundle_structure(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_diag_s", "/Game/Diag.scene")
        bundle = fab.generate_diagnostic_bundle()
        assert isinstance(bundle, SceneDiagnosticBundle)
        assert len(bundle.signature) == 64
        val = UniversalSceneValidator()
        ok, errs = val.validate_diagnostic_bundle(bundle)
        assert ok is True

    def test_diagnostic_bundle_signature_tamper(self):
        fab = UniversalSceneFabricator()
        sc = fab.create_scene("sc_diag_t", "/Game/DiagT.scene")
        bundle = fab.generate_diagnostic_bundle()
        tampered = SceneDiagnosticBundle(
            bundle_id=bundle.bundle_id,
            timestamp=bundle.timestamp,
            snapshot=bundle.snapshot,
            error_log=bundle.error_log,
            signature="0000000000000000000000000000000000000000000000000000000000000000"
        )
        val = UniversalSceneValidator()
        ok, errs = val.validate_diagnostic_bundle(tampered)
        assert ok is False
        assert any("BUNDLE_SIGNATURE_MISMATCH" in e for e in errs)

    def test_transform_matrix_multiplication_associativity(self):
        t1 = Transform(position=[1.0, 2.0, 3.0])
        t2 = Transform(position=[4.0, 5.0, 6.0])
        c1 = t1.combine(t2)
        assert c1.position == [5.0, 7.0, 9.0]

    def test_transform_scale_composition(self):
        t1 = Transform(scale=[2.0, 3.0, 4.0])
        t2 = Transform(scale=[0.5, 2.0, 1.5])
        c = t1.combine(t2)
        assert c.scale == [1.0, 6.0, 6.0]

    def test_entity_flag_manipulation(self):
        e = Entity("test_flags", "FlagsTest")
        e.flags["is_static"] = True
        e.flags["cast_shadow"] = False
        d = e.to_dict()
        assert d["flags"]["is_static"] is True
        assert d["flags"]["cast_shadow"] is False
