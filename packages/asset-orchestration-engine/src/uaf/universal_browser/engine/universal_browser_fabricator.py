"""
UAF-81.69: Universal Asset Browser & Resource Catalog Fabricator Engine.
Authoritative core implementation for Catalog Management, Search Indexing,
Filtering, Collections, Thumbnails, Previews, Watchers, and Browser Virtualization.
"""

from __future__ import annotations

from collections import OrderedDict
import copy
import hashlib
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from uaf.universal_browser.models.definition import (
    AssetCollection,
    AssetHealth,
    AssetIdentity,
    AssetMetadata,
    AssetTag,
    AssetType,
    BrowserDiagnosticBundle,
    BrowserSelection,
    BrowserStateSnapshot,
    BrowserTelemetry,
    BrowserViewMode,
    CatalogEntry,
    CatalogEntryState,
    CollectionType,
    ImportStatus,
    PreviewItem,
    PreviewMode,
    SearchQuery,
    SearchResult,
    SortDirection,
    SortField,
    ThumbnailItem,
    normalize_catalog_path,
)


class UniversalBrowserFabricator:
    """
    Authoritative asset browser, catalog, inverted search index, and preview system.
    Fully decoupled from external graphical systems.
    """

    def __init__(self):
        self.catalog: Dict[str, CatalogEntry] = {}  # asset_id -> CatalogEntry
        self.path_to_id: Dict[str, str] = {}  # canonical_path -> asset_id
        self.inverted_index: Dict[str, Set[str]] = {}  # token -> set of asset_ids
        self.tags: Dict[str, AssetTag] = {}  # tag_name -> AssetTag
        self.collections: Dict[str, AssetCollection] = {}  # collection_id -> AssetCollection
        self.favorites: Set[str] = set()
        self.recent_items: List[str] = []
        self.max_recent_items: int = 50
        self.current_view_mode: BrowserViewMode = BrowserViewMode.GRID
        self.selection = BrowserSelection()
        self.thumbnail_cache: OrderedDict[str, ThumbnailItem] = OrderedDict()
        self.max_thumbnail_cache_size: int = 500
        self.preview_cache: Dict[str, PreviewItem] = {}
        self.active_watchers: Set[str] = set()
        self.telemetry = BrowserTelemetry()

    # --------------------------------------------------------------------------
    # 1. CATALOG MANAGEMENT & PATH NORMALIZATION
    # --------------------------------------------------------------------------

    def add_entry(self, entry: CatalogEntry) -> None:
        if entry.identity.asset_id in self.catalog:
            raise ValueError(f"NO_DUPLICATE_ASSET_IDENTITY: Asset with ID '{entry.identity.asset_id}' already exists.")

        norm_path = normalize_catalog_path(entry.identity.canonical_path)
        if norm_path in self.path_to_id:
            raise ValueError(f"NO_DUPLICATE_ASSET_IDENTITY: Canonical path '{norm_path}' already in catalog.")

        entry.identity.canonical_path = norm_path
        self.catalog[entry.identity.asset_id] = entry
        self.path_to_id[norm_path] = entry.identity.asset_id

        # Index entry
        self._index_entry(entry)
        self.telemetry.catalog_size = len(self.catalog)

    def remove_entry(self, asset_id: str) -> None:
        if asset_id not in self.catalog:
            return

        entry = self.catalog[asset_id]
        norm_path = entry.identity.canonical_path

        # Unindex
        self._unindex_entry(entry)

        del self.catalog[asset_id]
        if norm_path in self.path_to_id:
            del self.path_to_id[norm_path]

        # Remove from collections, favorites, recent
        if asset_id in self.favorites:
            self.favorites.remove(asset_id)
        if asset_id in self.recent_items:
            self.recent_items.remove(asset_id)
        for col in self.collections.values():
            if asset_id in col.item_ids:
                col.item_ids.remove(asset_id)

        # Invalidate caches
        self.invalidate_thumbnail(asset_id)
        if asset_id in self.preview_cache:
            del self.preview_cache[asset_id]

        # Remove from selection
        if asset_id in self.selection.selected_asset_ids:
            self.selection.selected_asset_ids.remove(asset_id)
            if self.selection.active_asset_id == asset_id:
                self.selection.active_asset_id = None

        self.telemetry.catalog_size = len(self.catalog)

    def get_entry(self, asset_id: str) -> Optional[CatalogEntry]:
        return self.catalog.get(asset_id)

    def get_entry_by_path(self, canonical_path: str) -> Optional[CatalogEntry]:
        norm_path = normalize_catalog_path(canonical_path)
        asset_id = self.path_to_id.get(norm_path)
        return self.catalog.get(asset_id) if asset_id else None

    def rename_entry(self, asset_id: str, new_path: str) -> None:
        if asset_id not in self.catalog:
            raise KeyError(f"Asset '{asset_id}' not found in catalog.")

        norm_new_path = normalize_catalog_path(new_path)
        if norm_new_path in self.path_to_id and self.path_to_id[norm_new_path] != asset_id:
            raise ValueError(f"Path '{norm_new_path}' already occupied by asset '{self.path_to_id[norm_new_path]}'.")

        entry = self.catalog[asset_id]
        old_path = entry.identity.canonical_path

        self._unindex_entry(entry)
        del self.path_to_id[old_path]

        entry.identity.canonical_path = norm_new_path
        entry.identity.display_name = norm_new_path.split("/")[-1]
        entry.version += 1

        self.path_to_id[norm_new_path] = asset_id
        self._index_entry(entry)

    def duplicate_entry(self, asset_id: str, target_path: str) -> CatalogEntry:
        if asset_id not in self.catalog:
            raise KeyError(f"Asset '{asset_id}' not found.")

        source = self.catalog[asset_id]
        new_id = f"asset_{int(time.time() * 1000)}_{len(self.catalog)}"
        norm_path = normalize_catalog_path(target_path)

        new_identity = AssetIdentity(
            asset_id=new_id,
            canonical_path=norm_path,
            display_name=norm_path.split("/")[-1],
            asset_type=source.identity.asset_type,
        )
        new_entry = CatalogEntry(
            identity=new_identity,
            metadata=copy.deepcopy(source.metadata),
            state=CatalogEntryState.REGISTERED,
            import_status=ImportStatus.READY,
        )
        self.add_entry(new_entry)
        return new_entry

    # --------------------------------------------------------------------------
    # 2. INVERTED SEARCH INDEX & TOKENIZATION
    # --------------------------------------------------------------------------

    def _extract_tokens(self, text: str) -> Set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def _index_entry(self, entry: CatalogEntry) -> None:
        aid = entry.identity.asset_id
        tokens = set()
        tokens |= self._extract_tokens(entry.identity.display_name)
        tokens |= self._extract_tokens(entry.identity.canonical_path)
        tokens |= self._extract_tokens(entry.identity.asset_type.value)
        for tag in entry.metadata.tags:
            tokens |= self._extract_tokens(tag)

        for token in tokens:
            if token not in self.inverted_index:
                self.inverted_index[token] = set()
            self.inverted_index[token].add(aid)

        self.telemetry.index_size = len(self.inverted_index)

    def _unindex_entry(self, entry: CatalogEntry) -> None:
        aid = entry.identity.asset_id
        for token_set in self.inverted_index.values():
            token_set.discard(aid)

    def rebuild_search_index(self) -> None:
        self.inverted_index.clear()
        for entry in self.catalog.values():
            self._index_entry(entry)
        self.telemetry.index_size = len(self.inverted_index)

    def search(self, query: Union[str, SearchQuery], limit: int = 100) -> List[SearchResult]:
        t0 = time.perf_counter()

        if isinstance(query, str):
            sq = SearchQuery.parse(query)
        else:
            sq = query

        if not sq.tokens and not sq.raw_query:
            # Return all entries up to limit
            results = [SearchResult(entry=e, score=1.0) for e in self.catalog.values()]
            results.sort(key=lambda r: (r.entry.identity.canonical_path, r.entry.identity.asset_id))
            return results[:limit]

        query_tokens = [t.lower() for t in (sq.tokens or self._extract_tokens(sq.raw_query))]
        raw_lower = sq.raw_query.lower()

        scores: Dict[str, float] = {}
        matched_fields: Dict[str, List[str]] = {}

        for q_tok in query_tokens:
            for idx_tok, aids in self.inverted_index.items():
                match_weight = 0.0
                if idx_tok == q_tok:
                    match_weight = 10.0
                elif idx_tok.startswith(q_tok):
                    match_weight = 5.0
                elif q_tok in idx_tok:
                    match_weight = 2.0

                if match_weight > 0:
                    for aid in aids:
                        scores[aid] = scores.get(aid, 0.0) + match_weight

        # Filter and assemble SearchResults
        search_results: List[SearchResult] = []
        for aid, score in scores.items():
            if aid not in self.catalog:
                continue
            entry = self.catalog[aid]

            # Path search check: if raw query in canonical path, boost score
            if raw_lower and raw_lower in entry.identity.canonical_path.lower():
                score += 15.0

            # Exact display name match boost
            if raw_lower and entry.identity.display_name.lower() == raw_lower:
                score += 20.0

            # Filter conditions
            if sq.type_filters and entry.identity.asset_type not in sq.type_filters:
                continue
            if sq.tag_filters and not (sq.tag_filters & entry.metadata.tags):
                continue
            if sq.path_prefix and not entry.identity.canonical_path.startswith(sq.path_prefix):
                continue
            if sq.status_filters and entry.import_status not in sq.status_filters:
                continue

            search_results.append(SearchResult(
                entry=entry,
                score=score,
                matched_fields=["display_name", "canonical_path"]
            ))

        # Sort deterministically: score DESC, canonical_path ASC, asset_id ASC
        search_results.sort(key=lambda r: (-r.score, r.entry.identity.canonical_path, r.entry.identity.asset_id))

        t1 = time.perf_counter()
        self.telemetry.search_latency_ms = (t1 - t0) * 1000.0
        return search_results[:limit]

    # --------------------------------------------------------------------------
    # 3. FILTERING & DETERMINISTIC SORTING
    # --------------------------------------------------------------------------

    def filter_and_sort(
        self,
        type_filters: Optional[Set[AssetType]] = None,
        tag_filters: Optional[Set[str]] = None,
        path_prefix: str = "",
        status_filters: Optional[Set[ImportStatus]] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        sort_field: SortField = SortField.NAME,
        sort_direction: SortDirection = SortDirection.ASCENDING
    ) -> List[CatalogEntry]:
        t0 = time.perf_counter()

        filtered: List[CatalogEntry] = []
        for entry in self.catalog.values():
            if type_filters and entry.identity.asset_type not in type_filters:
                continue
            if tag_filters and not (tag_filters & entry.metadata.tags):
                continue
            if path_prefix and not entry.identity.canonical_path.startswith(path_prefix):
                continue
            if status_filters and entry.import_status not in status_filters:
                continue
            if min_size is not None and entry.metadata.file_size_bytes < min_size:
                continue
            if max_size is not None and entry.metadata.file_size_bytes > max_size:
                continue
            filtered.append(entry)

        # Deterministic sorting
        def sort_key(e: CatalogEntry):
            if sort_field == SortField.NAME:
                prim = e.identity.display_name.lower()
            elif sort_field == SortField.PATH:
                prim = e.identity.canonical_path.lower()
            elif sort_field == SortField.TYPE:
                prim = e.identity.asset_type.value
            elif sort_field == SortField.SIZE:
                prim = e.metadata.file_size_bytes
            elif sort_field == SortField.DATE_MODIFIED:
                prim = e.metadata.modified_time
            elif sort_field == SortField.IMPORT_STATUS:
                prim = e.import_status.value
            else:
                prim = e.identity.display_name.lower()

            return (prim, e.identity.canonical_path, e.identity.asset_id)

        reverse = (sort_direction == SortDirection.DESCENDING)
        filtered.sort(key=sort_key, reverse=reverse)

        t1 = time.perf_counter()
        self.telemetry.sort_latency_ms = (t1 - t0) * 1000.0
        return filtered

    # --------------------------------------------------------------------------
    # 4. TAG SYSTEM
    # --------------------------------------------------------------------------

    def create_tag(self, tag_id: str, name: str, color_hex: str = "#888888", group: str = "General") -> AssetTag:
        if not name or not name.strip():
            raise ValueError("Tag name must not be empty.")
        if tag_id in self.tags:
            raise ValueError(f"Duplicate tag ID '{tag_id}'.")

        tag = AssetTag(tag_id=tag_id, name=name.strip(), color_hex=color_hex, group=group)
        self.tags[tag_id] = tag
        return tag

    def assign_tag(self, asset_id: str, tag_name: str) -> None:
        if asset_id not in self.catalog:
            raise KeyError(f"Asset '{asset_id}' not found.")
        if not tag_name or not tag_name.strip():
            raise ValueError("Tag name must not be empty.")

        entry = self.catalog[asset_id]
        entry.metadata.tags.add(tag_name.strip())
        self._index_entry(entry)

    def remove_tag(self, asset_id: str, tag_name: str) -> None:
        if asset_id not in self.catalog:
            return
        entry = self.catalog[asset_id]
        if tag_name in entry.metadata.tags:
            entry.metadata.tags.remove(tag_name)
            self._index_entry(entry)

    # --------------------------------------------------------------------------
    # 5. COLLECTION SYSTEM
    # --------------------------------------------------------------------------

    def create_collection(
        self,
        collection_id: str,
        name: str,
        col_type: CollectionType = CollectionType.STATIC,
        parent_id: Optional[str] = None,
        query_predicate: Optional[Callable[[CatalogEntry], bool]] = None
    ) -> AssetCollection:
        if collection_id in self.collections:
            raise ValueError(f"Duplicate collection ID '{collection_id}'.")

        if parent_id:
            self._validate_collection_cycle(collection_id, parent_id)

        col = AssetCollection(
            collection_id=collection_id,
            name=name,
            collection_type=col_type,
            parent_id=parent_id,
            query_predicate=query_predicate,
        )
        self.collections[collection_id] = col
        return col

    def _validate_collection_cycle(self, child_id: str, parent_id: str) -> None:
        curr = parent_id
        while curr:
            if curr == child_id:
                raise ValueError(f"NO_COLLECTION_CYCLES: Collection nesting cycle between '{child_id}' and '{parent_id}'.")
            parent_col = self.collections.get(curr)
            curr = parent_col.parent_id if parent_col else None

    def add_to_collection(self, collection_id: str, asset_id: str) -> None:
        if collection_id not in self.collections:
            raise KeyError(f"Collection '{collection_id}' not found.")
        if asset_id not in self.catalog:
            raise KeyError(f"Asset '{asset_id}' not found.")

        col = self.collections[collection_id]
        if col.collection_type != CollectionType.STATIC:
            raise ValueError("Cannot manually add items to a SMART collection.")
        col.item_ids.add(asset_id)

    def remove_from_collection(self, collection_id: str, asset_id: str) -> None:
        if collection_id in self.collections:
            col = self.collections[collection_id]
            col.item_ids.discard(asset_id)

    def get_collection_members(self, collection_id: str) -> List[CatalogEntry]:
        if collection_id not in self.collections:
            raise KeyError(f"Collection '{collection_id}' not found.")

        col = self.collections[collection_id]
        if col.collection_type == CollectionType.STATIC:
            return [self.catalog[aid] for aid in sorted(col.item_ids) if aid in self.catalog]

        if col.query_predicate:
            return [e for e in self.catalog.values() if col.query_predicate(e)]
        return []

    # --------------------------------------------------------------------------
    # 6. FAVORITES & RECENT ITEMS
    # --------------------------------------------------------------------------

    def toggle_favorite(self, asset_id: str) -> bool:
        if asset_id not in self.catalog:
            raise KeyError(f"Asset '{asset_id}' not found.")
        if asset_id in self.favorites:
            self.favorites.remove(asset_id)
            return False
        self.favorites.add(asset_id)
        return True

    def is_favorite(self, asset_id: str) -> bool:
        return asset_id in self.favorites

    def get_favorites(self) -> List[CatalogEntry]:
        return [self.catalog[aid] for aid in sorted(self.favorites) if aid in self.catalog]

    def add_recent(self, asset_id: str) -> None:
        if asset_id not in self.catalog:
            return
        if asset_id in self.recent_items:
            self.recent_items.remove(asset_id)
        self.recent_items.insert(0, asset_id)
        if len(self.recent_items) > self.max_recent_items:
            self.recent_items = self.recent_items[: self.max_recent_items]

    def get_recent(self) -> List[CatalogEntry]:
        return [self.catalog[aid] for aid in self.recent_items if aid in self.catalog]

    # --------------------------------------------------------------------------
    # 7. BROWSER VIEWS & VIRTUALIZATION
    # --------------------------------------------------------------------------

    def set_view_mode(self, mode: BrowserViewMode) -> None:
        self.current_view_mode = mode

    def get_virtualized_entries(self, offset: int = 0, limit: int = 50) -> List[CatalogEntry]:
        all_sorted = self.filter_and_sort(sort_field=SortField.NAME)
        return all_sorted[offset : offset + limit]

    def build_folder_tree(self) -> Dict[str, Any]:
        """
        Builds a hierarchical folder tree structure from canonical paths.
        """
        tree: Dict[str, Any] = {"name": "Root", "path": "/", "children": {}, "asset_ids": []}

        for aid, entry in self.catalog.items():
            parts = [p for p in entry.identity.canonical_path.split("/") if p]
            curr = tree
            accum_path = ""
            for folder in parts[:-1]:
                accum_path += "/" + folder
                if folder not in curr["children"]:
                    curr["children"][folder] = {"name": folder, "path": accum_path, "children": {}, "asset_ids": []}
                curr = curr["children"][folder]
            curr["asset_ids"].append(aid)

        return tree

    # --------------------------------------------------------------------------
    # 8. SELECTION MANAGEMENT
    # --------------------------------------------------------------------------

    def select_asset(self, asset_id: str, mode: str = "SET") -> None:
        if asset_id not in self.catalog:
            return

        if mode == "SET":
            self.selection.selected_asset_ids = [asset_id]
            self.selection.active_asset_id = asset_id
            self.selection.anchor_id = asset_id
        elif mode == "ADD":
            if asset_id not in self.selection.selected_asset_ids:
                self.selection.selected_asset_ids.append(asset_id)
            self.selection.active_asset_id = asset_id
        elif mode == "TOGGLE":
            if asset_id in self.selection.selected_asset_ids:
                self.selection.selected_asset_ids.remove(asset_id)
                if self.selection.active_asset_id == asset_id:
                    self.selection.active_asset_id = self.selection.selected_asset_ids[-1] if self.selection.selected_asset_ids else None
            else:
                self.selection.selected_asset_ids.append(asset_id)
                self.selection.active_asset_id = asset_id
        elif mode == "RANGE":
            all_entries = self.filter_and_sort(sort_field=SortField.NAME)
            ids = [e.identity.asset_id for e in all_entries]
            anchor = self.selection.anchor_id or asset_id
            if anchor in ids and asset_id in ids:
                i1 = ids.index(anchor)
                i2 = ids.index(asset_id)
                start, end = min(i1, i2), max(i1, i2)
                self.selection.selected_asset_ids = ids[start : end + 1]
                self.selection.active_asset_id = asset_id

    # --------------------------------------------------------------------------
    # 9. THUMBNAILS & PREVIEWS
    # --------------------------------------------------------------------------

    def request_thumbnail(self, asset_id: str, width: int = 128, height: int = 128) -> ThumbnailItem:
        cache_key = f"{asset_id}_{width}x{height}"
        if cache_key in self.thumbnail_cache:
            self.telemetry.thumbnail_cache_hits += 1
            # Move to end for LRU
            item = self.thumbnail_cache.pop(cache_key)
            self.thumbnail_cache[cache_key] = item
            return item

        self.telemetry.thumbnail_cache_misses += 1
        entry = self.catalog.get(asset_id)
        is_placeholder = entry is None or entry.state == CatalogEntryState.ERROR

        item = ThumbnailItem(
            asset_id=asset_id,
            cache_key=cache_key,
            width=width,
            height=height,
            is_placeholder=is_placeholder,
            data_bytes=b"THUMBNAIL_BYTES_STUB",
        )

        # LRU eviction
        if len(self.thumbnail_cache) >= self.max_thumbnail_cache_size:
            self.thumbnail_cache.popitem(last=False)

        self.thumbnail_cache[cache_key] = item
        return item

    def invalidate_thumbnail(self, asset_id: str) -> None:
        keys_to_remove = [k for k in self.thumbnail_cache if k.startswith(f"{asset_id}_")]
        for k in keys_to_remove:
            del self.thumbnail_cache[k]

    def request_preview(self, asset_id: str, mode: PreviewMode = PreviewMode.THUMBNAIL) -> PreviewItem:
        if asset_id not in self.catalog:
            return PreviewItem(asset_id=asset_id, preview_mode=mode, ready=False, error="Asset not found")

        entry = self.catalog[asset_id]
        item = PreviewItem(
            asset_id=asset_id,
            preview_mode=mode,
            ready=(entry.import_status == ImportStatus.READY),
            metadata={"type": entry.identity.asset_type.value, "path": entry.identity.canonical_path},
        )
        self.preview_cache[asset_id] = item
        return item

    # --------------------------------------------------------------------------
    # 10. ASSET DISCOVERY & WATCHERS
    # --------------------------------------------------------------------------

    def discover_asset(self, canonical_path: str, asset_type: AssetType, size: int = 1024) -> CatalogEntry:
        norm_path = normalize_catalog_path(canonical_path)
        aid = f"disc_{hashlib.md5(norm_path.encode('utf-8')).hexdigest()[:12]}"
        identity = AssetIdentity(
            asset_id=aid,
            canonical_path=norm_path,
            display_name=norm_path.split("/")[-1],
            asset_type=asset_type,
        )
        meta = AssetMetadata(file_size_bytes=size)
        entry = CatalogEntry(identity=identity, metadata=meta, state=CatalogEntryState.DISCOVERED)
        self.add_entry(entry)
        return entry

    def notify_file_modified(self, canonical_path: str, new_size: int) -> None:
        entry = self.get_entry_by_path(canonical_path)
        if entry:
            entry.metadata.file_size_bytes = new_size
            entry.metadata.modified_time = time.time()
            entry.state = CatalogEntryState.MODIFIED
            entry.version += 1
            self.invalidate_thumbnail(entry.identity.asset_id)

    def notify_file_deleted(self, canonical_path: str) -> None:
        entry = self.get_entry_by_path(canonical_path)
        if entry:
            self.remove_entry(entry.identity.asset_id)

    # --------------------------------------------------------------------------
    # 11. BROWSER COMMANDS & DRAG / DROP
    # --------------------------------------------------------------------------

    def execute_command(self, command_name: str, payload: Dict[str, Any]) -> Any:
        cmd = command_name.upper()
        if cmd == "OPEN":
            aid = payload.get("asset_id")
            if aid:
                self.add_recent(aid)
            return True
        if cmd == "INSPECT":
            aid = payload.get("asset_id")
            if aid:
                self.add_recent(aid)
            return True
        if cmd == "RENAME":
            self.rename_entry(payload["asset_id"], payload["new_path"])
            return True
        if cmd == "DELETE":
            self.remove_entry(payload["asset_id"])
            return True
        if cmd == "DUPLICATE":
            return self.duplicate_entry(payload["asset_id"], payload["target_path"])
        if cmd == "FAVORITE":
            return self.toggle_favorite(payload["asset_id"])
        if cmd == "TAG":
            aid = payload["asset_id"]
            tag_name = payload["tag_name"]
            action = payload.get("action", "assign").lower()
            if action == "remove":
                self.remove_tag(aid, tag_name)
            else:
                self.assign_tag(aid, tag_name)
            return True
        if cmd == "COLLECTION":
            cid = payload["collection_id"]
            aid = payload["asset_id"]
            action = payload.get("action", "add").lower()
            if action == "remove":
                self.remove_from_collection(cid, aid)
            else:
                self.add_to_collection(cid, aid)
            return True
        if cmd == "REFRESH":
            aid = payload.get("asset_id")
            if aid and aid in self.catalog:
                entry = self.catalog[aid]
                entry.metadata.modified_time = time.time()
                self._index_entry(entry)
            else:
                self.rebuild_search_index()
            return True
        if cmd == "RETRY":
            aid = payload["asset_id"]
            if aid in self.catalog:
                entry = self.catalog[aid]
                entry.import_status = ImportStatus.READY
                entry.state = CatalogEntryState.PROCESSED
                entry.error_message = None
            return True

        raise ValueError(f"Unknown browser command '{command_name}'.")

    def validate_drag_drop(self, source_asset_ids: List[str], target_destination: str) -> Tuple[bool, Optional[str]]:
        if not source_asset_ids:
            return False, "EMPTY_SELECTION: No assets to drag."
        for aid in source_asset_ids:
            if aid not in self.catalog:
                return False, f"MISSING_ASSET: Asset '{aid}' does not exist."

        norm_dest = normalize_catalog_path(target_destination)
        return True, None

    # --------------------------------------------------------------------------
    # 12. SNAPSHOTS, TELEMETRY & DIAGNOSTICS
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> BrowserStateSnapshot:
        snap_id = f"snap_browser_{int(time.time() * 1000)}"
        cat_data = {aid: e.to_dict() for aid, e in self.catalog.items()}
        tag_data = {tid: t.to_dict() for tid, t in self.tags.items()}
        col_data = {cid: c.to_dict() for cid, c in self.collections.items()}

        return BrowserStateSnapshot(
            snapshot_id=snap_id,
            timestamp=time.time(),
            catalog_entries=cat_data,
            selection=list(self.selection.selected_asset_ids),
            tags=tag_data,
            collections=col_data,
        )

    def generate_diagnostic_bundle(self) -> BrowserDiagnosticBundle:
        bundle_id = f"bundle_browser_{int(time.time() * 1000)}"
        snap = self.take_snapshot()
        self.telemetry.catalog_size = len(self.catalog)
        self.telemetry.index_size = len(self.inverted_index)
        return BrowserDiagnosticBundle(
            bundle_id=bundle_id,
            timestamp=time.time(),
            snapshot=snap,
            telemetry=copy.deepcopy(self.telemetry),
        )
