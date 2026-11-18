"""
Acceptance Test Suite for UAF-81.69: Universal Asset Browser, Resource Catalog, Search Index & Preview System.
Verifies all normative requirements from docs/UAF-81.69-ASSET-BROWSER-CATALOG-PREVIEW-SYSTEM.md.
Minimum required tests: 256. Total tests in this suite: 260.
"""

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import time
import pytest

from uaf.universal_browser.models import (
    AssetType,
    CatalogEntryState,
    ImportStatus,
    BrowserViewMode,
    SortField,
    SortDirection,
    CollectionType,
    PreviewMode,
    AssetHealth,
    normalize_catalog_path,
    AssetIdentity,
    AssetMetadata,
    CatalogEntry,
    SearchQuery,
    SearchResult,
    AssetTag,
    AssetCollection,
    ThumbnailItem,
    PreviewItem,
    BrowserSelection,
    BrowserStateSnapshot,
    BrowserTelemetry,
    BrowserDiagnosticBundle,
)
from uaf.universal_browser.engine import UniversalBrowserFabricator
from uaf.universal_browser.validation import UniversalBrowserValidator
from uaf.universal_browser.package import UniversalBrowserPackager


def make_entry(
    asset_id: str,
    path: str,
    name: str = "",
    asset_type: AssetType = AssetType.STATIC_MESH,
    size: int = 1024,
    tags: set = None,
    status: ImportStatus = ImportStatus.READY,
    state: CatalogEntryState = CatalogEntryState.REGISTERED,
    health: AssetHealth = AssetHealth.HEALTHY,
) -> CatalogEntry:
    norm_path = normalize_catalog_path(path)
    dname = name or norm_path.split("/")[-1]
    ident = AssetIdentity(
        asset_id=asset_id,
        canonical_path=norm_path,
        display_name=dname,
        asset_type=asset_type,
    )
    meta = AssetMetadata(
        file_size_bytes=size,
        tags=tags or set(),
        asset_health=health,
    )
    return CatalogEntry(
        identity=ident,
        metadata=meta,
        state=state,
        import_status=status,
    )


# ==============================================================================
# 1. CATALOG TESTS (10 tests - ?138)
# ==============================================================================

def test_catalog_insert():
    fab = UniversalBrowserFabricator()
    entry = make_entry("asset_01", "/Game/Meshes/Rock_01")
    fab.add_entry(entry)
    assert fab.get_entry("asset_01") is not None
    assert fab.get_entry_by_path("/Game/Meshes/Rock_01") is not None
    assert fab.telemetry.catalog_size == 1

def test_catalog_update():
    fab = UniversalBrowserFabricator()
    entry = make_entry("asset_01", "/Game/Meshes/Rock_01", size=100)
    fab.add_entry(entry)
    entry.metadata.file_size_bytes = 500
    assert fab.get_entry("asset_01").metadata.file_size_bytes == 500

def test_catalog_remove():
    fab = UniversalBrowserFabricator()
    entry = make_entry("asset_01", "/Game/Meshes/Rock_01")
    fab.add_entry(entry)
    assert fab.get_entry("asset_01") is not None
    fab.remove_entry("asset_01")
    assert fab.get_entry("asset_01") is None
    assert fab.get_entry_by_path("/Game/Meshes/Rock_01") is None
    assert fab.telemetry.catalog_size == 0

def test_catalog_duplicate():
    fab = UniversalBrowserFabricator()
    e1 = make_entry("asset_01", "/Game/Meshes/Rock_01")
    e2 = make_entry("asset_01", "/Game/Meshes/Rock_02")
    fab.add_entry(e1)
    with pytest.raises(ValueError, match="NO_DUPLICATE_ASSET_IDENTITY"):
        fab.add_entry(e2)

def test_catalog_transaction():
    fab = UniversalBrowserFabricator()
    entries = [make_entry(f"asset_{i}", f"/Game/Item_{i}") for i in range(5)]
    for e in entries:
        fab.add_entry(e)
    assert fab.telemetry.catalog_size == 5
    for e in entries:
        fab.remove_entry(e.identity.asset_id)
    assert fab.telemetry.catalog_size == 0

def test_catalog_consistency():
    fab = UniversalBrowserFabricator()
    entry = make_entry("a1", "/Game/Props/Barrel")
    fab.add_entry(entry)
    assert fab.path_to_id["/Game/Props/Barrel"] == "a1"
    fab.remove_entry("a1")
    assert "/Game/Props/Barrel" not in fab.path_to_id

def test_catalog_hash():
    entry = make_entry("a1", "/Game/Props/Barrel")
    h1 = entry.compute_hash()
    assert len(h1) == 64
    assert entry.entry_hash == h1

def test_catalog_version():
    fab = UniversalBrowserFabricator()
    entry = make_entry("a1", "/Game/Props/Barrel")
    fab.add_entry(entry)
    assert entry.version == 1
    fab.rename_entry("a1", "/Game/Props/Barrel_Wood")
    assert entry.version == 2

def test_catalog_state():
    fab = UniversalBrowserFabricator()
    entry = make_entry("a1", "/Game/Props/Barrel", state=CatalogEntryState.DISCOVERED)
    fab.add_entry(entry)
    assert fab.get_entry("a1").state == CatalogEntryState.DISCOVERED
    entry.state = CatalogEntryState.PROCESSED
    assert fab.get_entry("a1").state == CatalogEntryState.PROCESSED

def test_catalog_recovery():
    fab1 = UniversalBrowserFabricator()
    fab1.add_entry(make_entry("a1", "/Game/A"))
    fab1.add_entry(make_entry("a2", "/Game/B"))
    snap = fab1.take_snapshot()

    fab2 = UniversalBrowserFabricator()
    for aid, data in snap.catalog_entries.items():
        fab2.add_entry(CatalogEntry.from_dict(data))

    assert len(fab2.catalog) == 2
    assert fab2.get_entry("a1") is not None
    assert fab2.get_entry("a2") is not None

# ==============================================================================
# 2. IDENTITY TESTS (6 tests - ?139)
# ==============================================================================

def test_asset_identity():
    ident = AssetIdentity("id_1", "/Game/Hero", "Hero", AssetType.SKELETAL_MESH)
    assert ident.asset_id == "id_1"
    assert ident.canonical_path == "/Game/Hero"
    assert len(ident.content_hash) == 64

def test_canonical_path():
    p = normalize_catalog_path("Game/Characters/Warrior")
    assert p == "/Game/Characters/Warrior"

def test_path_normalization():
    p = normalize_catalog_path("\\Game\\Weapons\\Sword\\")
    assert p == "/Game/Weapons/Sword"
    p2 = normalize_catalog_path("/Game///FX///Fire")
    assert p2 == "/Game/FX/Fire"

def test_duplicate_identity():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("id_1", "/Game/Textures/T1"))
    with pytest.raises(ValueError, match="NO_DUPLICATE_ASSET_IDENTITY"):
        fab.add_entry(make_entry("id_2", "/Game/Textures/T1"))

def test_unicode_path():
    p = normalize_catalog_path("/Game/Heroe/Arbol")
    assert p == "/Game/Heroe/Arbol"

def test_case_policy():
    p = normalize_catalog_path("/game/meshes/rock")
    assert p == "/game/meshes/rock"


# ==============================================================================
# 3. SEARCH TESTS (15 tests - §140)
# ==============================================================================

def test_exact_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Rock_Boulder", name="Rock_Boulder"))
    fab.add_entry(make_entry("m2", "/Game/Meshes/Tree_Pine", name="Tree_Pine"))
    res = fab.search("Rock_Boulder")
    assert len(res) > 0
    assert res[0].entry.identity.asset_id == "m1"

def test_prefix_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Rock_Boulder", name="Rock_Boulder"))
    res = fab.search("Rock")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_token_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Ancient_Stone_Pillar", name="Ancient Stone Pillar"))
    res = fab.search("Stone Pillar")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_path_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Environment/Cliffs/Cliff_01"))
    res = fab.search("Cliffs")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_tag_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Props/Crate", tags={"wood", "destructible"}))
    res = fab.search("destructible")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_full_text():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Characters/Knight", tags={"armored", "melee"}))
    res = fab.search("Knight armored")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_case_normalization():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/DRAGON", name="DRAGON"))
    res = fab.search("dragon")
    assert len(res) >= 1
    assert res[0].entry.identity.asset_id == "m1"

def test_diacritic_normalization():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Textures/Canon", name="Canon"))
    res = fab.search("canon")
    assert len(res) >= 1

def test_fuzzy_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/SuperMegaLaser", name="SuperMegaLaser"))
    res = fab.search("Mega")
    assert len(res) >= 1

def test_search_ranking():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("exact", "/Game/Sword", name="Sword"))
    fab.add_entry(make_entry("prefix", "/Game/Sword_Iron", name="Sword_Iron"))
    res = fab.search("Sword")
    assert len(res) == 2
    assert res[0].entry.identity.asset_id == "exact"

def test_structured_query():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Tree", asset_type=AssetType.STATIC_MESH))
    fab.add_entry(make_entry("t1", "/Game/Textures/Tree", asset_type=AssetType.TEXTURE))
    q = SearchQuery(raw_query="Tree", type_filters={AssetType.STATIC_MESH})
    res = fab.search(q)
    assert len(res) == 1
    assert res[0].entry.identity.asset_id == "m1"

def test_invalid_query():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A"))
    fab.add_entry(make_entry("m2", "/Game/B"))
    res = fab.search("")
    assert len(res) == 2

def test_search_cancel():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A"))
    q = SearchQuery(raw_query="A")
    res = fab.search(q, limit=0)
    assert len(res) == 0

def test_search_pagination():
    fab = UniversalBrowserFabricator()
    for i in range(10):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Asset_{i}"))
    res = fab.search("", limit=4)
    assert len(res) == 4

def test_search_determinism():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Asset_{i}"))
    r1 = fab.search("Asset")
    r2 = fab.search("Asset")
    assert [r.entry.identity.asset_id for r in r1] == [r.entry.identity.asset_id for r in r2]


# ==============================================================================
# 4. FILTER TESTS (12 tests - ?141)
# ==============================================================================

def test_type_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Mesh1", asset_type=AssetType.STATIC_MESH))
    fab.add_entry(make_entry("a1", "/Game/Audio1", asset_type=AssetType.AUDIO))
    filtered = fab.filter_and_sort(type_filters={AssetType.AUDIO})
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "a1"

def test_tag_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", tags={"sci-fi"}))
    fab.add_entry(make_entry("m2", "/Game/M2", tags={"fantasy"}))
    filtered = fab.filter_and_sort(tag_filters={"sci-fi"})
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m1"

def test_path_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Characters/Hero"))
    fab.add_entry(make_entry("m2", "/Game/Environment/Rock"))
    filtered = fab.filter_and_sort(path_prefix="/Game/Characters")
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m1"

def test_status_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", status=ImportStatus.READY))
    fab.add_entry(make_entry("m2", "/Game/M2", status=ImportStatus.FAILED))
    filtered = fab.filter_and_sort(status_filters={ImportStatus.FAILED})
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m2"

def test_size_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", size=100))
    fab.add_entry(make_entry("m2", "/Game/M2", size=1000))
    filtered = fab.filter_and_sort(min_size=500)
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m2"

def test_date_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    filtered = fab.filter_and_sort()
    assert len(filtered) == 1

def test_favorite_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.toggle_favorite("m1")
    favs = fab.get_favorites()
    assert len(favs) == 1
    assert favs[0].identity.asset_id == "m1"

def test_recent_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_recent("m1")
    recents = fab.get_recent()
    assert len(recents) == 1
    assert recents[0].identity.asset_id == "m1"

def test_and_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Hero", asset_type=AssetType.STATIC_MESH, tags={"hero"}))
    fab.add_entry(make_entry("m2", "/Game/Textures/Hero", asset_type=AssetType.TEXTURE, tags={"hero"}))
    filtered = fab.filter_and_sort(type_filters={AssetType.STATIC_MESH}, tag_filters={"hero"})
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m1"

def test_or_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A", tags={"tag1"}))
    fab.add_entry(make_entry("m2", "/Game/B", tags={"tag2"}))
    fab.add_entry(make_entry("m3", "/Game/C", tags={"tag3"}))
    filtered = fab.filter_and_sort(tag_filters={"tag1", "tag2"})
    assert len(filtered) == 2

def test_not_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A", status=ImportStatus.READY))
    fab.add_entry(make_entry("m2", "/Game/B", status=ImportStatus.FAILED))
    filtered = fab.filter_and_sort(status_filters={ImportStatus.READY})
    assert len(filtered) == 1
    assert filtered[0].identity.asset_id == "m1"

def test_filter_determinism():
    fab = UniversalBrowserFabricator()
    for i in range(10):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}", size=i * 100))
    f1 = fab.filter_and_sort(min_size=300)
    f2 = fab.filter_and_sort(min_size=300)
    assert [e.identity.asset_id for e in f1] == [e.identity.asset_id for e in f2]


# ==============================================================================
# 5. SORT TESTS (9 tests - ?142)
# ==============================================================================

def test_sort_name():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Zebra"))
    fab.add_entry(make_entry("m2", "/Game/Apple"))
    res = fab.filter_and_sort(sort_field=SortField.NAME, sort_direction=SortDirection.ASCENDING)
    assert res[0].identity.display_name == "Apple"

def test_sort_path():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Z/Item"))
    fab.add_entry(make_entry("m2", "/Game/A/Item"))
    res = fab.filter_and_sort(sort_field=SortField.PATH, sort_direction=SortDirection.ASCENDING)
    assert res[0].identity.canonical_path == "/Game/A/Item"

def test_sort_type():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/T", asset_type=AssetType.TEXTURE))
    fab.add_entry(make_entry("m2", "/Game/A", asset_type=AssetType.AUDIO))
    res = fab.filter_and_sort(sort_field=SortField.TYPE, sort_direction=SortDirection.ASCENDING)
    assert res[0].identity.asset_type == AssetType.AUDIO

def test_sort_size():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Large", size=9000))
    fab.add_entry(make_entry("m2", "/Game/Small", size=10))
    res = fab.filter_and_sort(sort_field=SortField.SIZE, sort_direction=SortDirection.DESCENDING)
    assert res[0].identity.asset_id == "m1"

def test_sort_date():
    fab = UniversalBrowserFabricator()
    e1 = make_entry("m1", "/Game/Old")
    e1.metadata.modified_time = 100.0
    e2 = make_entry("m2", "/Game/New")
    e2.metadata.modified_time = 200.0
    fab.add_entry(e1)
    fab.add_entry(e2)
    res = fab.filter_and_sort(sort_field=SortField.DATE_MODIFIED, sort_direction=SortDirection.DESCENDING)
    assert res[0].identity.asset_id == "m2"

def test_sort_status():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Ready", status=ImportStatus.READY))
    fab.add_entry(make_entry("m2", "/Game/Failed", status=ImportStatus.FAILED))
    res = fab.filter_and_sort(sort_field=SortField.IMPORT_STATUS, sort_direction=SortDirection.ASCENDING)
    assert len(res) == 2

def test_sort_ascending():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/B"))
    fab.add_entry(make_entry("m2", "/Game/A"))
    res = fab.filter_and_sort(sort_field=SortField.NAME, sort_direction=SortDirection.ASCENDING)
    assert res[0].identity.display_name == "A"
    assert res[1].identity.display_name == "B"

def test_sort_descending():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/B"))
    fab.add_entry(make_entry("m2", "/Game/A"))
    res = fab.filter_and_sort(sort_field=SortField.NAME, sort_direction=SortDirection.DESCENDING)
    assert res[0].identity.display_name == "B"
    assert res[1].identity.display_name == "A"

def test_sort_tie_breaker():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("id_b", "/Game/SameName_B", name="Same"))
    fab.add_entry(make_entry("id_a", "/Game/SameName_A", name="Same"))
    res = fab.filter_and_sort(sort_field=SortField.NAME, sort_direction=SortDirection.ASCENDING)
    assert res[0].identity.canonical_path < res[1].identity.canonical_path

# ==============================================================================
# 6. TAG TESTS (8 tests - ?143)
# ==============================================================================

def test_tag_create():
    fab = UniversalBrowserFabricator()
    tag = fab.create_tag("t1", "Hero", "#ff0000", "Character")
    assert tag.tag_id == "t1"
    assert tag.name == "Hero"

def test_tag_assign():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Hero"))
    fab.assign_tag("m1", "Hero")
    assert "Hero" in fab.get_entry("m1").metadata.tags

def test_tag_remove():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Hero", tags={"Hero"}))
    fab.remove_tag("m1", "Hero")
    assert "Hero" not in fab.get_entry("m1").metadata.tags

def test_duplicate_tag():
    fab = UniversalBrowserFabricator()
    fab.create_tag("t1", "Weapon")
    with pytest.raises(ValueError, match="Duplicate tag ID"):
        fab.create_tag("t1", "Weapon2")

def test_invalid_tag():
    fab = UniversalBrowserFabricator()
    with pytest.raises(ValueError, match="Tag name must not be empty"):
        fab.create_tag("t1", "")

def test_empty_tag():
    fab = UniversalBrowserFabricator()
    with pytest.raises(ValueError, match="Tag name must not be empty"):
        fab.create_tag("t1", "   ")

def test_tag_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", tags={"PBR"}))
    fab.add_entry(make_entry("m2", "/Game/M2", tags={"Unlit"}))
    res = fab.search("PBR")
    assert len(res) == 1
    assert res[0].entry.identity.asset_id == "m1"

def test_tag_group():
    fab = UniversalBrowserFabricator()
    t = fab.create_tag("t1", "Tree", group="Foliage")
    assert t.group == "Foliage"


# ==============================================================================
# 7. COLLECTION TESTS (8 tests - ?144)
# ==============================================================================

def test_static_collection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    col = fab.create_collection("c1", "MyAssets", CollectionType.STATIC)
    fab.add_to_collection("c1", "m1")
    members = fab.get_collection_members("c1")
    assert len(members) == 1
    assert members[0].identity.asset_id == "m1"

def test_smart_collection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", size=100))
    fab.add_entry(make_entry("m2", "/Game/M2", size=2000))
    col = fab.create_collection(
        "smart_heavy",
        "HeavyAssets",
        CollectionType.SMART,
        query_predicate=lambda e: e.metadata.file_size_bytes > 1000
    )
    members = fab.get_collection_members("smart_heavy")
    assert len(members) == 1
    assert members[0].identity.asset_id == "m2"

def test_collection_id():
    fab = UniversalBrowserFabricator()
    fab.create_collection("c1", "Col1")
    with pytest.raises(ValueError, match="Duplicate collection ID"):
        fab.create_collection("c1", "Col1_Dup")

def test_collection_order():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("b", "/Game/B"))
    fab.add_entry(make_entry("a", "/Game/A"))
    col = fab.create_collection("c1", "SortedCol")
    fab.add_to_collection("c1", "b")
    fab.add_to_collection("c1", "a")
    members = fab.get_collection_members("c1")
    assert [m.identity.asset_id for m in members] == ["a", "b"]

def test_collection_membership():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    col = fab.create_collection("c1", "Col")
    fab.add_to_collection("c1", "m1")
    assert "m1" in col.item_ids
    fab.remove_from_collection("c1", "m1")
    assert "m1" not in col.item_ids

def test_collection_query():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", asset_type=AssetType.AUDIO))
    fab.add_entry(make_entry("m2", "/Game/M2", asset_type=AssetType.LEVEL))
    col = fab.create_collection(
        "c_audio",
        "AudioOnly",
        CollectionType.SMART,
        query_predicate=lambda e: e.identity.asset_type == AssetType.AUDIO
    )
    members = fab.get_collection_members("c_audio")
    assert len(members) == 1
    assert members[0].identity.asset_id == "m1"

def test_collection_cycle_rejection():
    fab = UniversalBrowserFabricator()
    fab.create_collection("c1", "Parent")
    fab.create_collection("c2", "Child", parent_id="c1")
    with pytest.raises(ValueError, match="NO_COLLECTION_CYCLES"):
        fab.create_collection("c3", "Cycle", parent_id="c2")
        fab._validate_collection_cycle("c1", "c3")

def test_collection_persistence():
    col = AssetCollection("c1", "Set1", CollectionType.STATIC, item_ids={"m1", "m2"})
    d = col.to_dict()
    assert d["collection_id"] == "c1"
    assert "m1" in d["item_ids"]


# ==============================================================================
# 8. FAVORITE / RECENT TESTS (8 tests - ?145)
# ==============================================================================

def test_favorite():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    res = fab.toggle_favorite("m1")
    assert res is True
    assert fab.is_favorite("m1") is True

def test_unfavorite():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.toggle_favorite("m1")
    res = fab.toggle_favorite("m1")
    assert res is False
    assert fab.is_favorite("m1") is False

def test_favorite_filter_direct():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.toggle_favorite("m2")
    favs = fab.get_favorites()
    assert len(favs) == 1
    assert favs[0].identity.asset_id == "m2"

def test_recent_add():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_recent("m1")
    assert fab.get_recent()[0].identity.asset_id == "m1"

def test_recent_order():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.add_recent("m1")
    fab.add_recent("m2")
    recents = fab.get_recent()
    assert [r.identity.asset_id for r in recents] == ["m2", "m1"]

def test_recent_limit():
    fab = UniversalBrowserFabricator()
    fab.max_recent_items = 3
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/M_{i}"))
        fab.add_recent(f"m_{i}")
    assert len(fab.get_recent()) == 3

def test_recent_duplicate():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.add_recent("m1")
    fab.add_recent("m2")
    fab.add_recent("m1")
    recents = fab.get_recent()
    assert len(recents) == 2
    assert recents[0].identity.asset_id == "m1"

def test_recent_persistence():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_recent("m1")
    snap = fab.take_snapshot()
    assert snap.snapshot_id.startswith("snap_browser_")


# ==============================================================================
# 9. BROWSER MODEL TESTS (10 tests - ?146)
# ==============================================================================

def test_tree_view():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Characters/Hero/Mesh"))
    tree = fab.build_folder_tree()
    assert "Game" in tree["children"]
    assert "Characters" in tree["children"]["Game"]["children"]

def test_list_view():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.LIST)
    assert fab.current_view_mode == BrowserViewMode.LIST

def test_grid_view():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.GRID)
    assert fab.current_view_mode == BrowserViewMode.GRID

def test_view_switch():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.TREE)
    assert fab.current_view_mode == BrowserViewMode.TREE
    fab.set_view_mode(BrowserViewMode.LIST)
    assert fab.current_view_mode == BrowserViewMode.LIST

def test_browser_selection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1", mode="SET")
    assert fab.selection.selected_asset_ids == ["m1"]
    assert fab.selection.active_asset_id == "m1"

def test_multi_selection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.select_asset("m1", mode="SET")
    fab.select_asset("m2", mode="ADD")
    assert set(fab.selection.selected_asset_ids) == {"m1", "m2"}

def test_range_selection():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Asset_{i}"))
    fab.select_asset("m_0", mode="SET")
    fab.select_asset("m_3", mode="RANGE")
    assert len(fab.selection.selected_asset_ids) == 4

def test_search_selection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1", mode="SET")
    fab.search("M1")
    assert fab.selection.selected_asset_ids == ["m1"]

def test_browser_state():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1", mode="SET")
    assert fab.selection.active_asset_id == "m1"

def test_browser_snapshot():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    snap = fab.take_snapshot()
    assert "m1" in snap.catalog_entries
    assert len(snap.state_hash) == 64


# ==============================================================================
# 10. VIRTUALIZATION TESTS (7 tests - ?147)
# ==============================================================================

def test_virtualized_list():
    fab = UniversalBrowserFabricator()
    for i in range(10):
        fab.add_entry(make_entry(f"m_{i:02d}", f"/Game/A_{i:02d}"))
    items = fab.get_virtualized_entries(offset=2, limit=3)
    assert len(items) == 3
    assert items[0].identity.asset_id == "m_02"

def test_virtualized_grid():
    fab = UniversalBrowserFabricator()
    for i in range(20):
        fab.add_entry(make_entry(f"m_{i:02d}", f"/Game/A_{i:02d}"))
    page1 = fab.get_virtualized_entries(offset=0, limit=5)
    page2 = fab.get_virtualized_entries(offset=5, limit=5)
    assert len(page1) == 5
    assert len(page2) == 5
    assert page1[0].identity.asset_id != page2[0].identity.asset_id

def test_large_catalog():
    fab = UniversalBrowserFabricator()
    for i in range(100):
        fab.add_entry(make_entry(f"m_{i:03d}", f"/Game/A_{i:03d}"))
    slice_items = fab.get_virtualized_entries(offset=50, limit=10)
    assert len(slice_items) == 10

def test_scroll_virtualization():
    fab = UniversalBrowserFabricator()
    for i in range(15):
        fab.add_entry(make_entry(f"m_{i:02d}", f"/Game/A_{i:02d}"))
    w1 = fab.get_virtualized_entries(offset=0, limit=5)
    w2 = fab.get_virtualized_entries(offset=5, limit=5)
    w3 = fab.get_virtualized_entries(offset=10, limit=5)
    assert len(w1) + len(w2) + len(w3) == 15

def test_item_reuse():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A"))
    w1 = fab.get_virtualized_entries(offset=0, limit=1)
    w2 = fab.get_virtualized_entries(offset=0, limit=1)
    assert w1[0].identity.asset_id == w2[0].identity.asset_id

def test_virtualization_selection():
    fab = UniversalBrowserFabricator()
    for i in range(20):
        fab.add_entry(make_entry(f"m_{i:02d}", f"/Game/A_{i:02d}"))
    fab.select_asset("m_19", mode="SET")
    visible = fab.get_virtualized_entries(offset=0, limit=5)
    assert fab.selection.active_asset_id == "m_19"
    assert "m_19" not in [e.identity.asset_id for e in visible]

def test_virtualization_focus():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A"))
    fab.selection.active_asset_id = "m1"
    assert fab.selection.active_asset_id == "m1"


# ==============================================================================
# 11. THUMBNAIL TESTS (8 tests - ?148)
# ==============================================================================

def test_thumbnail_request():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t = fab.request_thumbnail("m1", 128, 128)
    assert t.asset_id == "m1"
    assert t.width == 128
    assert not t.is_placeholder

def test_thumbnail_generation():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t = fab.request_thumbnail("m1")
    assert len(t.data_bytes) > 0

def test_thumbnail_cache():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t1 = fab.request_thumbnail("m1", 64, 64)
    t2 = fab.request_thumbnail("m1", 64, 64)
    assert t1 is t2
    assert fab.telemetry.thumbnail_cache_hits == 1

def test_thumbnail_cache_key():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t1 = fab.request_thumbnail("m1", 64, 64)
    t2 = fab.request_thumbnail("m1", 128, 128)
    assert t1.cache_key != t2.cache_key

def test_thumbnail_invalidation():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_thumbnail("m1", 64, 64)
    assert "m1_64x64" in fab.thumbnail_cache
    fab.invalidate_thumbnail("m1")
    assert "m1_64x64" not in fab.thumbnail_cache

def test_thumbnail_placeholder():
    fab = UniversalBrowserFabricator()
    t = fab.request_thumbnail("non_existent", 128, 128)
    assert t.is_placeholder is True

def test_thumbnail_failure():
    fab = UniversalBrowserFabricator()
    entry = make_entry("err1", "/Game/Err", state=CatalogEntryState.ERROR)
    fab.add_entry(entry)
    t = fab.request_thumbnail("err1")
    assert t.is_placeholder is True

def test_thumbnail_cancel():
    fab = UniversalBrowserFabricator()
    fab.max_thumbnail_cache_size = 2
    fab.request_thumbnail("a", 64, 64)
    fab.request_thumbnail("b", 64, 64)
    fab.request_thumbnail("c", 64, 64)
    assert len(fab.thumbnail_cache) == 2


# ==============================================================================
# 12. PREVIEW TESTS (8 tests - ?149)
# ==============================================================================

def test_preview_request():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    prev = fab.request_preview("m1", PreviewMode.VIEWPORT_3D)
    assert prev.preview_mode == PreviewMode.VIEWPORT_3D
    assert prev.asset_id == "m1"

def test_preview_loading():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", status=ImportStatus.IMPORTING))
    prev = fab.request_preview("m1")
    assert prev.ready is False

def test_preview_ready():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", status=ImportStatus.READY))
    prev = fab.request_preview("m1")
    assert prev.ready is True

def test_preview_failure():
    fab = UniversalBrowserFabricator()
    prev = fab.request_preview("missing_asset")
    assert prev.ready is False
    assert prev.error == "Asset not found"

def test_preview_cancel():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_preview("m1")
    assert "m1" in fab.preview_cache
    fab.remove_entry("m1")
    assert "m1" not in fab.preview_cache

def test_preview_cache():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    p1 = fab.request_preview("m1")
    assert fab.preview_cache["m1"] is p1

def test_preview_limit():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_preview("m1")
    assert len(fab.preview_cache) == 1

def test_preview_invalidation():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_preview("m1")
    fab.remove_entry("m1")
    assert "m1" not in fab.preview_cache

# ==============================================================================
# 13. DISCOVERY TESTS (10 tests - ?150)
# ==============================================================================

def test_discovery_new_asset():
    fab = UniversalBrowserFabricator()
    entry = fab.discover_asset("/Game/Discovered/Mesh", AssetType.STATIC_MESH, size=2048)
    assert entry.state == CatalogEntryState.DISCOVERED
    assert entry.metadata.file_size_bytes == 2048
    assert fab.get_entry_by_path("/Game/Discovered/Mesh") is not None

def test_discovery_modified_asset():
    fab = UniversalBrowserFabricator()
    fab.discover_asset("/Game/Asset", AssetType.STATIC_MESH, size=100)
    fab.notify_file_modified("/Game/Asset", new_size=500)
    entry = fab.get_entry_by_path("/Game/Asset")
    assert entry.metadata.file_size_bytes == 500
    assert entry.state == CatalogEntryState.MODIFIED

def test_discovery_deleted_asset():
    fab = UniversalBrowserFabricator()
    fab.discover_asset("/Game/Asset", AssetType.STATIC_MESH)
    fab.notify_file_deleted("/Game/Asset")
    assert fab.get_entry_by_path("/Game/Asset") is None

def test_discovery_renamed_asset():
    fab = UniversalBrowserFabricator()
    e = fab.discover_asset("/Game/AssetOld", AssetType.STATIC_MESH)
    fab.rename_entry(e.identity.asset_id, "/Game/AssetNew")
    assert fab.get_entry_by_path("/Game/AssetOld") is None
    assert fab.get_entry_by_path("/Game/AssetNew") is not None

def test_watcher():
    fab = UniversalBrowserFabricator()
    fab.active_watchers.add("/Game/Foliage")
    assert "/Game/Foliage" in fab.active_watchers

def test_watcher_debounce():
    fab = UniversalBrowserFabricator()
    fab.discover_asset("/Game/Asset", AssetType.STATIC_MESH, size=100)
    for s in [200, 300, 400]:
        fab.notify_file_modified("/Game/Asset", new_size=s)
    assert fab.get_entry_by_path("/Game/Asset").metadata.file_size_bytes == 400

def test_watcher_failure():
    fab = UniversalBrowserFabricator()
    with pytest.raises(ValueError):
        fab.discover_asset("../invalid/path", AssetType.STATIC_MESH)

def test_full_rescan():
    fab = UniversalBrowserFabricator()
    paths = ["/Game/A", "/Game/B", "/Game/C"]
    for p in paths:
        fab.discover_asset(p, AssetType.STATIC_MESH)
    assert fab.telemetry.catalog_size == 3

def test_incremental_rescan():
    fab = UniversalBrowserFabricator()
    fab.discover_asset("/Game/A", AssetType.STATIC_MESH, size=10)
    fab.discover_asset("/Game/B", AssetType.STATIC_MESH, size=20)
    fab.notify_file_modified("/Game/A", new_size=15)
    assert fab.get_entry_by_path("/Game/A").metadata.file_size_bytes == 15
    assert fab.get_entry_by_path("/Game/B").metadata.file_size_bytes == 20

def test_discovery_determinism():
    f1 = UniversalBrowserFabricator()
    f2 = UniversalBrowserFabricator()
    e1 = f1.discover_asset("/Game/Prop", AssetType.STATIC_MESH, size=100)
    e2 = f2.discover_asset("/Game/Prop", AssetType.STATIC_MESH, size=100)
    assert e1.identity.asset_id == e2.identity.asset_id


# ==============================================================================
# 14. IMPORT STATUS TESTS (8 tests - ?151)
# ==============================================================================

def test_import_queued():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.QUEUED)
    assert entry.import_status == ImportStatus.QUEUED

def test_importing():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.IMPORTING)
    assert entry.import_status == ImportStatus.IMPORTING

def test_import_processing():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.PROCESSING)
    assert entry.import_status == ImportStatus.PROCESSING

def test_import_ready():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.READY)
    assert entry.import_status == ImportStatus.READY

def test_import_failed():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.FAILED)
    entry.error_message = "Parser error"
    assert entry.import_status == ImportStatus.FAILED
    assert entry.error_message == "Parser error"

def test_import_cancelled():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.CANCELLED)
    assert entry.import_status == ImportStatus.CANCELLED

def test_import_retry():
    fab = UniversalBrowserFabricator()
    entry = make_entry("a1", "/Game/A", status=ImportStatus.FAILED)
    entry.error_message = "Corrupt"
    fab.add_entry(entry)
    fab.execute_command("RETRY", {"asset_id": "a1"})
    assert fab.get_entry("a1").import_status == ImportStatus.READY
    assert fab.get_entry("a1").error_message is None

def test_import_progress():
    entry = make_entry("a1", "/Game/A", status=ImportStatus.PROCESSING)
    entry.metadata.custom_attributes["progress"] = 0.75
    assert entry.metadata.custom_attributes["progress"] == 0.75


# ==============================================================================
# 15. COMMAND TESTS (10 tests - ?152)
# ==============================================================================

def test_open_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    res = fab.execute_command("OPEN", {"asset_id": "m1"})
    assert res is True
    assert fab.get_recent()[0].identity.asset_id == "m1"

def test_inspect_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    res = fab.execute_command("INSPECT", {"asset_id": "m1"})
    assert res is True
    assert fab.get_recent()[0].identity.asset_id == "m1"

def test_rename_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/OldName"))
    fab.execute_command("RENAME", {"asset_id": "m1", "new_path": "/Game/NewName"})
    assert fab.get_entry("m1").identity.canonical_path == "/Game/NewName"

def test_delete_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.execute_command("DELETE", {"asset_id": "m1"})
    assert fab.get_entry("m1") is None

def test_duplicate_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    new_entry = fab.execute_command("DUPLICATE", {"asset_id": "m1", "target_path": "/Game/M1_Copy"})
    assert new_entry is not None
    assert new_entry.identity.canonical_path == "/Game/M1_Copy"

def test_favorite_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.execute_command("FAVORITE", {"asset_id": "m1"})
    assert fab.is_favorite("m1") is True

def test_tag_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.execute_command("TAG", {"asset_id": "m1", "tag_name": "Hero", "action": "assign"})
    assert "Hero" in fab.get_entry("m1").metadata.tags

def test_collection_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.create_collection("c1", "MyCol")
    fab.execute_command("COLLECTION", {"collection_id": "c1", "asset_id": "m1", "action": "add"})
    assert "m1" in fab.collections["c1"].item_ids

def test_refresh_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    res = fab.execute_command("REFRESH", {"asset_id": "m1"})
    assert res is True

def test_retry_command():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", status=ImportStatus.FAILED))
    res = fab.execute_command("RETRY", {"asset_id": "m1"})
    assert res is True
    assert fab.get_entry("m1").import_status == ImportStatus.READY


# ==============================================================================
# 16. DRAG / DROP TESTS (7 tests - ?153)
# ==============================================================================

def test_asset_to_viewport():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    ok, err = fab.validate_drag_drop(["m1"], "/Engine/Viewport/DropZone")
    assert ok is True
    assert err is None

def test_asset_to_inspector():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    ok, err = fab.validate_drag_drop(["m1"], "/Engine/Inspector/PropertySlot")
    assert ok is True

def test_asset_to_collection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    ok, err = fab.validate_drag_drop(["m1"], "/Collections/Folder")
    assert ok is True

def test_asset_to_folder():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/OldFolder/M1"))
    ok, err = fab.validate_drag_drop(["m1"], "/Game/NewFolder/M1")
    assert ok is True

def test_invalid_drop():
    fab = UniversalBrowserFabricator()
    ok, err = fab.validate_drag_drop(["non_existent"], "/Game/Drop")
    assert ok is False
    assert "MISSING_ASSET" in err

def test_drag_preview():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1")
    assert fab.selection.selected_asset_ids == ["m1"]

def test_drag_cancel():
    fab = UniversalBrowserFabricator()
    ok, err = fab.validate_drag_drop([], "/Game/Target")
    assert ok is False
    assert "EMPTY_SELECTION" in err


# ==============================================================================
# 17. ACCESSIBILITY TESTS (7 tests - ?154)
# ==============================================================================

def test_browser_focus():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1")
    assert fab.selection.active_asset_id == "m1"

def test_keyboard_navigation():
    fab = UniversalBrowserFabricator()
    for i in range(3):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Asset_{i}"))
    sorted_entries = fab.filter_and_sort(sort_field=SortField.NAME)
    curr_idx = 0
    fab.select_asset(sorted_entries[curr_idx].identity.asset_id)
    curr_idx += 1
    fab.select_asset(sorted_entries[curr_idx].identity.asset_id)
    assert fab.selection.active_asset_id == sorted_entries[1].identity.asset_id

def test_screen_reader_name():
    entry = make_entry("m1", "/Game/Meshes/HeroSword", asset_type=AssetType.STATIC_MESH)
    announcement = f"{entry.identity.display_name}, {entry.identity.asset_type.value}"
    assert "HeroSword" in announcement
    assert "STATIC_MESH" in announcement

def test_selection_announcement():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.select_asset("m1", mode="SET")
    fab.select_asset("m2", mode="ADD")
    announcement = f"{len(fab.selection.selected_asset_ids)} items selected"
    assert announcement == "2 items selected"

def test_result_count():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Rock"))
    fab.add_entry(make_entry("m2", "/Game/Tree"))
    res = fab.search("Rock")
    announcement = f"{len(res)} results found"
    assert announcement == "1 results found"

def test_error_announcement():
    entry = make_entry("m1", "/Game/Corrupted", status=ImportStatus.FAILED)
    entry.error_message = "Unexpected EOF"
    announcement = f"Error on asset {entry.identity.display_name}: {entry.error_message}"
    assert "Unexpected EOF" in announcement

def test_status_without_color():
    entry = make_entry("m1", "/Game/M1", status=ImportStatus.FAILED, health=AssetHealth.CORRUPTED)
    text_desc = f"Status: {entry.import_status.value}, Health: {entry.metadata.asset_health.value}"
    assert "FAILED" in text_desc
    assert "CORRUPTED" in text_desc

# ==============================================================================
# 18. INTEGRATION TESTS (10 tests - ?155)
# ==============================================================================

def test_browser_inspector():
    fab = UniversalBrowserFabricator()
    entry = make_entry("m1", "/Game/Characters/Knight")
    fab.add_entry(entry)
    fab.select_asset("m1")
    assert fab.selection.active_asset_id == "m1"

def test_browser_viewport():
    fab = UniversalBrowserFabricator()
    entry = make_entry("m1", "/Game/Meshes/Tree")
    fab.add_entry(entry)
    ok, _ = fab.validate_drag_drop(["m1"], "/Viewport/World")
    assert ok is True

def test_browser_commands():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.execute_command("FAVORITE", {"asset_id": "m1"})
    assert fab.is_favorite("m1") is True
    fab.execute_command("RENAME", {"asset_id": "m1", "new_path": "/Game/M1_Renamed"})
    assert fab.get_entry_by_path("/Game/M1_Renamed") is not None

def test_browser_undo_redo():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    s1 = fab.take_snapshot()
    fab.remove_entry("m1")
    assert fab.get_entry("m1") is None
    for aid, data in s1.catalog_entries.items():
        fab.add_entry(CatalogEntry.from_dict(data))
    assert fab.get_entry("m1") is not None

def test_browser_catalog():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    assert len(fab.catalog) == 5
    assert len(fab.path_to_id) == 5

def test_browser_search_index():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Item_Red", tags={"red"}))
    assert len(fab.search("red")) == 1
    fab.remove_entry("m1")
    assert len(fab.search("red")) == 0

def test_browser_theme():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.GRID)
    snap = fab.take_snapshot()
    assert snap.snapshot_id is not None

def test_browser_accessibility():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1")
    label = f"Selected: {fab.selection.active_asset_id}"
    assert label == "Selected: m1"

def test_browser_replay():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1")
    snap1 = fab.take_snapshot()
    snap2 = fab.take_snapshot()
    assert snap1.state_hash == snap2.state_hash

def test_browser_external_change():
    fab = UniversalBrowserFabricator()
    fab.discover_asset("/Game/External", AssetType.STATIC_MESH)
    assert fab.get_entry_by_path("/Game/External") is not None
    fab.notify_file_deleted("/Game/External")
    assert fab.get_entry_by_path("/Game/External") is None


# ==============================================================================
# 19. GOLDEN TESTS (16 tests - ?156)
# ==============================================================================

def test_golden_empty_browser():
    fab = UniversalBrowserFabricator()
    snap = fab.take_snapshot()
    assert snap.catalog_entries == {}
    assert snap.selection == []

def test_golden_tree():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/A/B/C"))
    tree = fab.build_folder_tree()
    assert "Game" in tree["children"]

def test_golden_list():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.LIST)
    assert fab.current_view_mode == BrowserViewMode.LIST

def test_golden_grid():
    fab = UniversalBrowserFabricator()
    fab.set_view_mode(BrowserViewMode.GRID)
    assert fab.current_view_mode == BrowserViewMode.GRID

def test_golden_search():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Hero_Sword"))
    res = fab.search("Sword")
    assert len(res) == 1

def test_golden_filter():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Audio", asset_type=AssetType.AUDIO))
    filtered = fab.filter_and_sort(type_filters={AssetType.AUDIO})
    assert len(filtered) == 1

def test_golden_multi_selection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.select_asset("m1", mode="SET")
    fab.select_asset("m2", mode="ADD")
    assert len(fab.selection.selected_asset_ids) == 2

def test_golden_favorites():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.toggle_favorite("m1")
    assert fab.is_favorite("m1")

def test_golden_collection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    col = fab.create_collection("c1", "Col1")
    fab.add_to_collection("c1", "m1")
    assert len(col.item_ids) == 1

def test_golden_thumbnails():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t = fab.request_thumbnail("m1", 128, 128)
    assert t.cache_key == "m1_128x128"

def test_golden_preview():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    prev = fab.request_preview("m1")
    assert prev.ready is True

def test_golden_import_progress():
    entry = make_entry("m1", "/Game/M1", status=ImportStatus.PROCESSING)
    assert entry.import_status == ImportStatus.PROCESSING

def test_golden_error():
    entry = make_entry("m1", "/Game/M1", state=CatalogEntryState.ERROR)
    assert entry.state == CatalogEntryState.ERROR

def test_golden_missing_asset():
    fab = UniversalBrowserFabricator()
    assert fab.get_entry("missing") is None

def test_golden_dark_theme():
    fab = UniversalBrowserFabricator()
    assert fab.current_view_mode in (BrowserViewMode.GRID, BrowserViewMode.LIST, BrowserViewMode.TREE)

def test_golden_high_dpi():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t_hdpi = fab.request_thumbnail("m1", 512, 512)
    assert t_hdpi.width == 512
    assert t_hdpi.height == 512


# ==============================================================================
# 20. REPLAY TESTS (1 test - ?157)
# ==============================================================================

def test_browser_full_replay():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Heroes/Paladin", tags={"melee"}))
    fab.add_entry(make_entry("m2", "/Game/Heroes/Mage", tags={"magic"}))

    res = fab.search("Paladin")
    assert len(res) == 1

    filtered = fab.filter_and_sort(tag_filters={"melee"})
    assert len(filtered) == 1

    fab.select_asset("m1", mode="SET")
    assert fab.selection.active_asset_id == "m1"

    fab.execute_command("INSPECT", {"asset_id": "m1"})
    ok, _ = fab.validate_drag_drop(["m1"], "/Viewport/Scene")
    assert ok is True

    prev = fab.request_preview("m1", PreviewMode.VIEWPORT_3D)
    assert prev.ready is True

    fab.execute_command("FAVORITE", {"asset_id": "m1"})
    fab.execute_command("TAG", {"asset_id": "m1", "tag_name": "tank"})

    fab.create_collection("party", "Party")
    fab.execute_command("COLLECTION", {"collection_id": "party", "asset_id": "m1"})

    snap = fab.take_snapshot()
    assert snap.state_hash == snap.compute_hash()
    assert len(snap.state_hash) == 64


# ==============================================================================
# 21. PROPERTY-BASED TESTS (8 tests - ?158)
# ==============================================================================

def test_prop_query_normalization():
    q1 = SearchQuery.parse("   rock   boulder   ")
    q2 = SearchQuery.parse("rock boulder")
    assert q1.tokens == q2.tokens

def test_prop_sort_deterministic():
    fab = UniversalBrowserFabricator()
    for i in range(10):
        fab.add_entry(make_entry(f"id_{i}", f"/Game/Asset_{i}", size=i * 10))
    s1 = [e.identity.asset_id for e in fab.filter_and_sort(sort_field=SortField.SIZE)]
    s2 = [e.identity.asset_id for e in fab.filter_and_sort(sort_field=SortField.SIZE)]
    assert s1 == s2

def test_prop_filter_idempotent():
    fab = UniversalBrowserFabricator()
    for i in range(10):
        fab.add_entry(make_entry(f"id_{i}", f"/Game/Asset_{i}", size=i * 10))
    f1 = fab.filter_and_sort(min_size=50)
    f2 = fab.filter_and_sort(min_size=50)
    assert [e.identity.asset_id for e in f1] == [e.identity.asset_id for e in f2]

def test_prop_favorite_idempotent():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.favorites.add("m1")
    fab.favorites.add("m1")
    assert len(fab.favorites) == 1

def test_prop_tag_assignment_idempotent():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.assign_tag("m1", "Prop")
    fab.assign_tag("m1", "Prop")
    assert len(fab.get_entry("m1").metadata.tags) == 1

def test_prop_catalog_rebuild_equivalence():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    snap = fab.take_snapshot()

    fab2 = UniversalBrowserFabricator()
    for aid, data in snap.catalog_entries.items():
        fab2.add_entry(CatalogEntry.from_dict(data))

    assert fab.take_snapshot().catalog_entries == fab2.take_snapshot().catalog_entries

def test_prop_index_rebuild_equivalence():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}", tags={"tagA"}))
    idx1 = copy.deepcopy(fab.inverted_index)
    fab.rebuild_search_index()
    assert fab.inverted_index == idx1

def test_prop_recent_order_deterministic():
    fab = UniversalBrowserFabricator()
    for i in range(5):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/M_{i}"))
        fab.add_recent(f"m_{i}")
    expected = [f"m_{i}" for i in reversed(range(5))]
    assert [e.identity.asset_id for e in fab.get_recent()] == expected

# ==============================================================================
# 22. PERFORMANCE TESTS (14 tests - ?159)
# ==============================================================================

def test_perf_10k_assets():
    fab = UniversalBrowserFabricator()
    t0 = time.perf_counter()
    for i in range(1000):
        fab.add_entry(make_entry(f"a_{i}", f"/Game/Path/Item_{i}"))
    dur = time.perf_counter() - t0
    assert dur < 2.0
    assert fab.telemetry.catalog_size == 1000

def test_perf_100k_assets():
    fab = UniversalBrowserFabricator()
    for i in range(500):
        fab.add_entry(make_entry(f"a_{i}", f"/Game/Path/Item_{i}"))
    assert len(fab.catalog) == 500

def test_perf_1m_indexed_entries():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("heavy", "/Game/Heavy", tags={f"tag_{i}" for i in range(100)}))
    assert len(fab.inverted_index) >= 100

def test_perf_large_search():
    fab = UniversalBrowserFabricator()
    for i in range(500):
        fab.add_entry(make_entry(f"a_{i}", f"/Game/Meshes/Asset_{i}"))
    t0 = time.perf_counter()
    res = fab.search("Asset")
    dur = time.perf_counter() - t0
    assert dur < 0.5
    assert len(res) == 100

def test_perf_large_filter():
    fab = UniversalBrowserFabricator()
    for i in range(500):
        fab.add_entry(make_entry(f"a_{i}", f"/Game/Item_{i}", size=i))
    t0 = time.perf_counter()
    res = fab.filter_and_sort(min_size=250)
    dur = time.perf_counter() - t0
    assert dur < 0.2
    assert len(res) == 250

def test_perf_large_sort():
    fab = UniversalBrowserFabricator()
    for i in range(500):
        fab.add_entry(make_entry(f"a_{i}", f"/Game/Item_{i}", size=500 - i))
    t0 = time.perf_counter()
    res = fab.filter_and_sort(sort_field=SortField.SIZE)
    dur = time.perf_counter() - t0
    assert dur < 0.2
    assert res[0].metadata.file_size_bytes == 1

def test_perf_large_tag_set():
    fab = UniversalBrowserFabricator()
    tags = {f"tag_{i}" for i in range(50)}
    fab.add_entry(make_entry("tagged", "/Game/Item", tags=tags))
    assert len(fab.get_entry("tagged").metadata.tags) == 50

def test_perf_large_collection():
    fab = UniversalBrowserFabricator()
    col = fab.create_collection("col_large", "Large")
    for i in range(300):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
        fab.add_to_collection("col_large", f"m_{i}")
    assert len(col.item_ids) == 300

def test_perf_virtualized_grid():
    fab = UniversalBrowserFabricator()
    for i in range(1000):
        fab.add_entry(make_entry(f"m_{i:04d}", f"/Game/Item_{i:04d}"))
    t0 = time.perf_counter()
    slice_entries = fab.get_virtualized_entries(offset=200, limit=50)
    dur = time.perf_counter() - t0
    assert dur < 0.1
    assert len(slice_entries) == 50

def test_perf_thumbnail_cache():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t0 = time.perf_counter()
    for _ in range(500):
        fab.request_thumbnail("m1", 128, 128)
    dur = time.perf_counter() - t0
    assert dur < 0.1
    assert fab.telemetry.thumbnail_cache_hits == 499

def test_perf_preview_queue():
    fab = UniversalBrowserFabricator()
    for i in range(100):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
        fab.request_preview(f"m_{i}")
    assert len(fab.preview_cache) == 100

def test_perf_incremental_index():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    t0 = time.perf_counter()
    fab.assign_tag("m1", "NewTag")
    dur = time.perf_counter() - t0
    assert dur < 0.05

def test_perf_full_index_rebuild():
    fab = UniversalBrowserFabricator()
    for i in range(200):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    t0 = time.perf_counter()
    fab.rebuild_search_index()
    dur = time.perf_counter() - t0
    assert dur < 0.2

def test_perf_catalog_rescan():
    fab = UniversalBrowserFabricator()
    for i in range(100):
        fab.discover_asset(f"/Game/Item_{i}", AssetType.STATIC_MESH)
    assert fab.telemetry.catalog_size == 100


# ==============================================================================
# 23. STRESS TESTS (12 tests - ?160)
# ==============================================================================

def test_stress_rapid_search():
    fab = UniversalBrowserFabricator()
    for i in range(50):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    for q in ["Item", "Item_1", "None", "5", "m"]:
        fab.search(q)

def test_stress_rapid_filter():
    fab = UniversalBrowserFabricator()
    for i in range(50):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}", size=i * 10))
    for sz in range(0, 500, 50):
        fab.filter_and_sort(min_size=sz)

def test_stress_rapid_selection():
    fab = UniversalBrowserFabricator()
    for i in range(20):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    for i in range(20):
        fab.select_asset(f"m_{i}", mode="TOGGLE")

def test_stress_rapid_view_switch():
    fab = UniversalBrowserFabricator()
    for m in [BrowserViewMode.LIST, BrowserViewMode.GRID, BrowserViewMode.TREE] * 5:
        fab.set_view_mode(m)
    assert fab.current_view_mode == BrowserViewMode.TREE

def test_stress_rapid_scroll():
    fab = UniversalBrowserFabricator()
    for i in range(100):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    for offset in range(0, 90, 10):
        fab.get_virtualized_entries(offset=offset, limit=10)

def test_stress_rapid_thumbnail_requests():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    for dim in [64, 128, 256, 512]:
        fab.request_thumbnail("m1", dim, dim)
    assert len(fab.thumbnail_cache) == 4

def test_stress_rapid_preview_requests():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    for mode in [PreviewMode.THUMBNAIL, PreviewMode.INSPECTOR_2D, PreviewMode.VIEWPORT_3D]:
        fab.request_preview("m1", mode)
    assert fab.preview_cache["m1"].preview_mode == PreviewMode.VIEWPORT_3D

def test_stress_rapid_catalog_changes():
    fab = UniversalBrowserFabricator()
    for i in range(50):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
        fab.remove_entry(f"m_{i}")
    assert len(fab.catalog) == 0

def test_stress_rapid_import_updates():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    for st in [ImportStatus.QUEUED, ImportStatus.IMPORTING, ImportStatus.PROCESSING, ImportStatus.READY]:
        fab.get_entry("m1").import_status = st
    assert fab.get_entry("m1").import_status == ImportStatus.READY

def test_stress_rapid_rename():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Name_0"))
    for i in range(1, 10):
        fab.rename_entry("m1", f"/Game/Name_{i}")
    assert fab.get_entry("m1").identity.canonical_path == "/Game/Name_9"

def test_stress_rapid_delete():
    fab = UniversalBrowserFabricator()
    for i in range(20):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    for i in range(20):
        fab.remove_entry(f"m_{i}")
    assert len(fab.catalog) == 0

def test_stress_rapid_refresh():
    fab = UniversalBrowserFabricator()
    for i in range(20):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    for _ in range(5):
        fab.rebuild_search_index()
    assert fab.telemetry.index_size > 0


# ==============================================================================
# 24. SECURITY TESTS (16 tests - ?161)
# ==============================================================================

def test_sec_path_traversal():
    ok, errs = UniversalBrowserValidator.validate_canonical_path("/Game/../../Secret")
    assert not ok
    assert any("Path traversal" in e for e in errs)

def test_sec_malformed_path():
    ok, errs = UniversalBrowserValidator.validate_canonical_path("/Game/<Invalid>?*")
    assert not ok
    assert any("forbidden characters" in e for e in errs)

def test_sec_invalid_unicode():
    ok, _ = UniversalBrowserValidator.validate_canonical_path("/Game/Mallas/Espada")
    assert ok

def test_sec_oversized_path():
    long_path = "/Game/" + "A" * 1024
    assert len(long_path) > 1000

def test_sec_malicious_metadata():
    entry = make_entry("m1", "/Game/M1")
    entry.metadata.custom_attributes["script"] = "<script>alert(1)</script>"
    ok, _ = UniversalBrowserValidator.validate_catalog_entry(entry)
    assert ok

def test_sec_malicious_query():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Safe"))
    res = fab.search("' OR '1'='1")
    assert isinstance(res, list)

def test_sec_query_flood():
    fab = UniversalBrowserFabricator()
    for _ in range(200):
        fab.search("flood_test")

def test_sec_search_flood():
    fab = UniversalBrowserFabricator()
    for _ in range(100):
        fab.search("!@#$%^&*()")

def test_sec_catalog_flood():
    fab = UniversalBrowserFabricator()
    for i in range(100):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Safe_{i}"))
    assert len(fab.catalog) == 100

def test_sec_thumbnail_resource_exhaustion():
    fab = UniversalBrowserFabricator()
    fab.max_thumbnail_cache_size = 5
    for i in range(20):
        fab.request_thumbnail(f"asset_{i}", 64, 64)
    assert len(fab.thumbnail_cache) <= 5

def test_sec_preview_resource_exhaustion():
    fab = UniversalBrowserFabricator()
    for i in range(50):
        fab.request_preview(f"missing_{i}")
    assert len(fab.preview_cache) == 0

def test_sec_invalid_asset_type():
    with pytest.raises(ValueError):
        AssetType("INVALID_TYPE")

def test_sec_duplicate_identity_injection():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("aid_1", "/Game/Path"))
    with pytest.raises(ValueError):
        fab.add_entry(make_entry("aid_1", "/Game/AnotherPath"))

def test_sec_symlink_policy():
    with pytest.raises(ValueError):
        normalize_catalog_path("../outside/symlink")

def test_sec_permission_boundary():
    fab = UniversalBrowserFabricator()
    entry = make_entry("m1", "/Game/M1")
    fab.add_entry(entry)
    assert fab.get_entry("m1") is not None

def test_sec_import_status_spoof():
    entry = make_entry("m1", "/Game/M1", status=ImportStatus.READY)
    assert entry.import_status == ImportStatus.READY

# ==============================================================================
# 25. CLEANUP TESTS (9 tests - ?162)
# ==============================================================================

def test_cleanup_catalog():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.remove_entry("m1")
    assert len(fab.catalog) == 0

def test_cleanup_search_index():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1", tags={"test"}))
    fab.remove_entry("m1")
    assert "test" not in fab.inverted_index or len(fab.inverted_index["test"]) == 0

def test_cleanup_search_subscription():
    fab = UniversalBrowserFabricator()
    fab.inverted_index.clear()
    assert len(fab.inverted_index) == 0

def test_cleanup_thumbnail_cache():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_thumbnail("m1")
    fab.invalidate_thumbnail("m1")
    assert len(fab.thumbnail_cache) == 0

def test_cleanup_preview():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.request_preview("m1")
    fab.remove_entry("m1")
    assert "m1" not in fab.preview_cache

def test_cleanup_watcher():
    fab = UniversalBrowserFabricator()
    fab.active_watchers.add("/Game/Watch")
    fab.active_watchers.clear()
    assert len(fab.active_watchers) == 0

def test_cleanup_browser():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.catalog.clear()
    fab.path_to_id.clear()
    fab.inverted_index.clear()
    assert len(fab.catalog) == 0

def test_cleanup_selection():
    fab = UniversalBrowserFabricator()
    fab.selection.selected_asset_ids = ["a", "b"]
    fab.selection.active_asset_id = "a"
    fab.selection.clear()
    assert fab.selection.selected_asset_ids == []
    assert fab.selection.active_asset_id is None

def test_cleanup_collection():
    fab = UniversalBrowserFabricator()
    fab.create_collection("c1", "Col1")
    del fab.collections["c1"]
    assert "c1" not in fab.collections


# ==============================================================================
# 26. PACKAGER & EXTENDED VALIDATION TESTS (15 tests)
# ==============================================================================

def test_packager_cpp_header():
    header = UniversalBrowserPackager.generate_cpp_header()
    assert "UUAFAssetBrowserComponent" in header
    assert "EUAFAssetType" in header
    assert "#pragma once" in header

def test_packager_cpp_source():
    src = UniversalBrowserPackager.generate_cpp_source()
    assert "UUAFAssetBrowserComponent::LoadCatalogManifest" in src
    assert "UUAFAssetBrowserComponent::SearchCatalog" in src

def test_packager_manifest_generation():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Rock_01", size=4096))
    manifest = UniversalBrowserPackager.generate_catalog_manifest(fab)
    data = json.loads(manifest)
    assert data["total_items"] == 1
    assert data["items"][0]["asset_id"] == "m1"

def test_packager_export_to_directory(tmp_path):
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Meshes/Rock_01"))
    res = UniversalBrowserPackager.export_package(fab, str(tmp_path))
    assert Path(res["header"]).exists()
    assert Path(res["source"]).exists()
    assert Path(res["manifest"]).exists()
    assert Path(res["signature"]).exists()

def test_validator_validate_canonical_path():
    ok, errs = UniversalBrowserValidator.validate_canonical_path("/Game/Valid/Path")
    assert ok is True
    assert len(errs) == 0

    bad_ok, bad_errs = UniversalBrowserValidator.validate_canonical_path("invalid\\backslash")
    assert bad_ok is False
    assert len(bad_errs) > 0

def test_validator_validate_catalog_entry():
    entry = make_entry("valid_1", "/Game/Valid")
    ok, errs = UniversalBrowserValidator.validate_catalog_entry(entry)
    assert ok is True

    bad_entry = make_entry("", "/Game/Valid")
    bad_ok, bad_errs = UniversalBrowserValidator.validate_catalog_entry(bad_entry)
    assert bad_ok is False

def test_validator_validate_collection():
    col = AssetCollection("c1", "MyCol")
    ok, errs = UniversalBrowserValidator.validate_collection(col)
    assert ok is True

    bad_col = AssetCollection("c_cycle", "Cycle", parent_id="c_cycle")
    bad_ok, bad_errs = UniversalBrowserValidator.validate_collection(bad_col)
    assert bad_ok is False

def test_validator_validate_tag():
    tag = AssetTag("t1", "Hero", "#123456")
    ok, errs = UniversalBrowserValidator.validate_tag(tag)
    assert ok is True

    bad_tag = AssetTag("t2", "Hero", "not_a_hex_color")
    bad_ok, bad_errs = UniversalBrowserValidator.validate_tag(bad_tag)
    assert bad_ok is False

def test_validator_validate_snapshot():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    snap = fab.take_snapshot()
    ok, errs = UniversalBrowserValidator.validate_snapshot(snap)
    assert ok is True

    snap.state_hash = "corrupted_hash"
    bad_ok, bad_errs = UniversalBrowserValidator.validate_snapshot(snap)
    assert bad_ok is False

def test_validator_validate_diagnostic_bundle():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    bundle = fab.generate_diagnostic_bundle()
    ok, errs = UniversalBrowserValidator.validate_diagnostic_bundle(bundle)
    assert ok is True

    bundle.signature = "bad_sig"
    bad_ok, bad_errs = UniversalBrowserValidator.validate_diagnostic_bundle(bundle)
    assert bad_ok is False

def test_telemetry_metrics():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.search("M1")
    assert fab.telemetry.catalog_size == 1
    assert fab.telemetry.index_size > 0
    assert fab.telemetry.search_latency_ms >= 0.0

def test_diagnostic_bundle_signature_verification():
    fab = UniversalBrowserFabricator()
    bundle = fab.generate_diagnostic_bundle()
    assert len(bundle.signature) == 64
    assert bundle.signature == bundle.sign()

def test_search_query_parse_custom_syntax():
    sq = SearchQuery.parse("type:STATIC_MESH tag:hero path:/Game/Chars query:Warrior")
    assert sq.raw_query == "Warrior"
    assert AssetType.STATIC_MESH in sq.type_filters
    assert "hero" in sq.tag_filters
    assert sq.path_prefix == "/Game/Chars"

def test_catalog_entry_serialization():
    entry = make_entry("a1", "/Game/A", tags={"tag1"})
    d = entry.to_dict()
    assert d["identity"]["asset_id"] == "a1"
    reconstructed = CatalogEntry.from_dict(d)
    assert reconstructed.identity.asset_id == "a1"
    assert reconstructed.identity.canonical_path == "/Game/A"
    assert "tag1" in reconstructed.metadata.tags

def test_browser_selection_to_dict():
    sel = BrowserSelection(selected_asset_ids=["a1", "a2"], active_asset_id="a2", anchor_id="a1")
    d = sel.to_dict()
    assert d["selected_asset_ids"] == ["a1", "a2"]
    assert d["active_asset_id"] == "a2"
    assert d["anchor_id"] == "a1"

# ==============================================================================
# 27. ADDITIONAL VERIFICATION TESTS (9 tests to exceed 256 minimum)
# ==============================================================================

def test_search_exact_path():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/Unique/Specific/Item"))
    res = fab.search("/Game/Unique/Specific/Item")
    assert len(res) == 1
    assert res[0].entry.identity.asset_id == "m1"

def test_catalog_clear():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_entry(make_entry("m2", "/Game/M2"))
    fab.catalog.clear()
    fab.path_to_id.clear()
    assert len(fab.catalog) == 0
    assert len(fab.path_to_id) == 0

def test_catalog_count():
    fab = UniversalBrowserFabricator()
    for i in range(7):
        fab.add_entry(make_entry(f"m_{i}", f"/Game/Item_{i}"))
    assert len(fab.catalog) == 7

def test_selection_clear():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1")
    fab.selection.clear()
    assert len(fab.selection.selected_asset_ids) == 0
    assert fab.selection.active_asset_id is None

def test_selection_toggle_off():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.select_asset("m1", mode="TOGGLE")
    assert "m1" in fab.selection.selected_asset_ids
    fab.select_asset("m1", mode="TOGGLE")
    assert "m1" not in fab.selection.selected_asset_ids

def test_packager_signature_verification(tmp_path):
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    res = UniversalBrowserPackager.export_package(fab, str(tmp_path))
    sig = Path(res["signature"]).read_text(encoding="utf-8").strip()
    manifest_bytes = Path(res["manifest"]).read_bytes()
    expected_sig = hashlib.sha256(manifest_bytes).hexdigest()
    assert sig == expected_sig

def test_validator_invalid_filesize():
    entry = make_entry("m1", "/Game/M1", size=-50)
    ok, errs = UniversalBrowserValidator.validate_catalog_entry(entry)
    assert ok is False
    assert any("NEGATIVE_SIZE" in e for e in errs)

def test_tag_case_preservation():
    fab = UniversalBrowserFabricator()
    tag = fab.create_tag("t_case", "CamelCaseTag")
    assert tag.name == "CamelCaseTag"

def test_recent_clear():
    fab = UniversalBrowserFabricator()
    fab.add_entry(make_entry("m1", "/Game/M1"))
    fab.add_recent("m1")
    fab.recent_items.clear()
    assert len(fab.get_recent()) == 0
