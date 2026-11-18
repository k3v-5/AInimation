"""
UAF-81.69: Universal Asset Browser & Resource Catalog System - Models and Definitions.
Authoritative domain models, catalog entries, identities, metadata,
search representations, collections, thumbnails, previews, and diagnostics.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


# ==============================================================================
# ENUMS
# ==============================================================================

class AssetType(str, Enum):
    STATIC_MESH = "STATIC_MESH"
    SKELETAL_MESH = "SKELETAL_MESH"
    MATERIAL = "MATERIAL"
    TEXTURE = "TEXTURE"
    AUDIO = "AUDIO"
    ANIMATION = "ANIMATION"
    LEVEL = "LEVEL"
    BLUEPRINT = "BLUEPRINT"
    CONFIG = "CONFIG"
    RAW = "RAW"


class CatalogEntryState(str, Enum):
    DISCOVERED = "DISCOVERED"
    REGISTERED = "REGISTERED"
    IMPORTING = "IMPORTING"
    PROCESSED = "PROCESSED"
    MODIFIED = "MODIFIED"
    MISSING = "MISSING"
    ERROR = "ERROR"


class ImportStatus(str, Enum):
    QUEUED = "QUEUED"
    IMPORTING = "IMPORTING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class BrowserViewMode(str, Enum):
    TREE = "TREE"
    LIST = "LIST"
    GRID = "GRID"


class SortField(str, Enum):
    NAME = "NAME"
    PATH = "PATH"
    TYPE = "TYPE"
    SIZE = "SIZE"
    DATE_MODIFIED = "DATE_MODIFIED"
    IMPORT_STATUS = "IMPORT_STATUS"


class SortDirection(str, Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class CollectionType(str, Enum):
    STATIC = "STATIC"
    SMART = "SMART"


class PreviewMode(str, Enum):
    THUMBNAIL = "THUMBNAIL"
    INSPECTOR_2D = "2D_INSPECTOR"
    VIEWPORT_3D = "3D_VIEWPORT"
    METADATA_ONLY = "METADATA_ONLY"


class AssetHealth(str, Enum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CORRUPTED = "CORRUPTED"
    DEPRECATED = "DEPRECATED"


# ==============================================================================
# PATH NORMALIZATION HELPER
# ==============================================================================

def normalize_catalog_path(raw_path: str) -> str:
    if not raw_path or not isinstance(raw_path, str):
        raise ValueError("Catalog path must be a non-empty string.")

    # Convert backslashes first
    normalized = raw_path.replace("\\", "/")

    # Disallow traversal escapes
    if ".." in normalized:
        raise ValueError(f"NO_NON_CANONICAL_CATALOG_PATH: Path traversal attempt in '{raw_path}'.")

    # Squeeze consecutive slashes
    normalized = re.sub(r"/+", "/", normalized)

    # Ensure leading slash if not empty
    if not normalized.startswith("/"):
        normalized = "/" + normalized

    # Strip trailing slash unless root
    if len(normalized) > 1 and normalized.endswith("/"):
        normalized = normalized[:-1]

    # Check for invalid characters
    if re.search(r'[<>:"|?*]', normalized):
        raise ValueError(f"Invalid characters detected in catalog path: '{raw_path}'.")

    return normalized


# ==============================================================================
# IDENTITY & METADATA
# ==============================================================================

@dataclass
class AssetIdentity:
    asset_id: str
    canonical_path: str
    display_name: str
    asset_type: AssetType
    content_hash: str = ""

    def __post_init__(self):
        self.canonical_path = normalize_catalog_path(self.canonical_path)
        if not self.display_name:
            self.display_name = self.canonical_path.split("/")[-1]
        if not self.content_hash:
            payload = f"{self.asset_id}:{self.canonical_path}:{self.asset_type.value}"
            self.content_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "canonical_path": self.canonical_path,
            "display_name": self.display_name,
            "asset_type": self.asset_type.value,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetIdentity:
        try:
            atype = AssetType(data.get("asset_type", "STATIC_MESH"))
        except ValueError:
            atype = AssetType.STATIC_MESH
        return cls(
            asset_id=data["asset_id"],
            canonical_path=data["canonical_path"],
            display_name=data.get("display_name", ""),
            asset_type=atype,
            content_hash=data.get("content_hash", ""),
        )


@dataclass
class AssetMetadata:
    file_size_bytes: int = 0
    created_time: float = field(default_factory=time.time)
    modified_time: float = field(default_factory=time.time)
    tags: Set[str] = field(default_factory=set)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    health: AssetHealth = AssetHealth.HEALTHY
    asset_health: Optional[AssetHealth] = None

    def __post_init__(self):
        if self.asset_health is not None:
            self.health = self.asset_health
        else:
            self.asset_health = self.health

    @property
    def custom_attributes(self) -> Dict[str, Any]:
        return self.custom_fields

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_size_bytes": self.file_size_bytes,
            "created_time": self.created_time,
            "modified_time": self.modified_time,
            "tags": sorted(list(self.tags)),
            "custom_fields": self.custom_fields,
            "dependencies": self.dependencies,
            "health": self.health.value,
            "asset_health": self.health.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetMetadata:
        h_str = data.get("health") or data.get("asset_health", "HEALTHY")
        try:
            h = AssetHealth(h_str)
        except ValueError:
            h = AssetHealth.HEALTHY
        return cls(
            file_size_bytes=data.get("file_size_bytes", 0),
            created_time=data.get("created_time", time.time()),
            modified_time=data.get("modified_time", time.time()),
            tags=set(data.get("tags", [])),
            custom_fields=data.get("custom_fields", data.get("custom_attributes", {})),
            dependencies=data.get("dependencies", []),
            health=h,
            asset_health=h,
        )


@dataclass
class CatalogEntry:
    identity: AssetIdentity
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    state: CatalogEntryState = CatalogEntryState.REGISTERED
    import_status: ImportStatus = ImportStatus.READY
    import_progress: float = 1.0
    error_message: Optional[str] = None
    version: int = 1

    def compute_hash(self) -> str:
        d = self.to_dict()
        encoded = json.dumps(d, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @property
    def entry_hash(self) -> str:
        return self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "metadata": self.metadata.to_dict(),
            "state": self.state.value,
            "import_status": self.import_status.value,
            "import_progress": self.import_progress,
            "error_message": self.error_message,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CatalogEntry:
        identity = AssetIdentity.from_dict(data["identity"])
        metadata = AssetMetadata.from_dict(data.get("metadata", {}))
        state = CatalogEntryState(data.get("state", "REGISTERED"))
        import_status = ImportStatus(data.get("import_status", "READY"))
        return cls(
            identity=identity,
            metadata=metadata,
            state=state,
            import_status=import_status,
            import_progress=data.get("import_progress", 1.0),
            error_message=data.get("error_message"),
            version=data.get("version", 1),
        )


# ==============================================================================
# SEARCH, TAGS & COLLECTIONS
# ==============================================================================

@dataclass
class SearchQuery:
    raw_query: str = ""
    tokens: List[str] = field(default_factory=list)
    type_filters: Set[AssetType] = field(default_factory=set)
    tag_filters: Set[str] = field(default_factory=set)
    path_prefix: str = ""
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    status_filters: Set[ImportStatus] = field(default_factory=set)

    @classmethod
    def parse(cls, raw: str) -> SearchQuery:
        parts = raw.split()
        type_filters = set()
        tag_filters = set()
        path_prefix = ""
        remaining_words = []

        for p in parts:
            if p.startswith("type:"):
                val = p[5:]
                try:
                    type_filters.add(AssetType(val))
                except ValueError:
                    pass
            elif p.startswith("tag:"):
                tag_filters.add(p[4:].lower())
            elif p.startswith("path:"):
                path_prefix = p[5:]
            elif p.startswith("query:"):
                remaining_words.append(p[6:])
            else:
                remaining_words.append(p)

        clean_query = " ".join(remaining_words)
        tokens = [t.lower() for t in re.findall(r"\w+", clean_query)]
        return cls(
            raw_query=clean_query,
            tokens=tokens,
            type_filters=type_filters,
            tag_filters=tag_filters,
            path_prefix=path_prefix,
        )


@dataclass
class SearchResult:
    entry: CatalogEntry
    score: float
    matched_fields: List[str] = field(default_factory=list)
    highlights: Dict[str, str] = field(default_factory=dict)


@dataclass
class AssetTag:
    tag_id: str
    name: str
    color_hex: str = "#888888"
    group: str = "General"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag_id": self.tag_id,
            "name": self.name,
            "color_hex": self.color_hex,
            "group": self.group,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetTag:
        return cls(
            tag_id=data["tag_id"],
            name=data["name"],
            color_hex=data.get("color_hex", "#888888"),
            group=data.get("group", "General"),
        )


@dataclass
class AssetCollection:
    collection_id: str
    name: str
    collection_type: CollectionType = CollectionType.STATIC
    item_ids: Set[str] = field(default_factory=set)
    query_predicate: Optional[Callable[[CatalogEntry], bool]] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collection_id": self.collection_id,
            "name": self.name,
            "collection_type": self.collection_type.value,
            "item_ids": sorted(list(self.item_ids)),
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssetCollection:
        return cls(
            collection_id=data["collection_id"],
            name=data["name"],
            collection_type=CollectionType(data.get("collection_type", "STATIC")),
            parent_id=data.get("parent_id"),
            item_ids=set(data.get("item_ids", [])),
        )


# ==============================================================================
# THUMBNAIL & PREVIEWS
# ==============================================================================

@dataclass
class ThumbnailItem:
    asset_id: str
    cache_key: str
    width: int = 128
    height: int = 128
    format: str = "PNG"
    data_bytes: bytes = field(default_factory=bytes)
    timestamp: float = field(default_factory=time.time)
    is_placeholder: bool = False


@dataclass
class PreviewItem:
    asset_id: str
    preview_mode: PreviewMode = PreviewMode.THUMBNAIL
    ready: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ==============================================================================
# SELECTION, SNAPSHOT & TELEMETRY
# ==============================================================================

@dataclass
class BrowserSelection:
    selected_asset_ids: List[str] = field(default_factory=list)
    active_asset_id: Optional[str] = None
    anchor_id: Optional[str] = None

    def clear(self) -> None:
        self.selected_asset_ids.clear()
        self.active_asset_id = None
        self.anchor_id = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_asset_ids": list(self.selected_asset_ids),
            "active_asset_id": self.active_asset_id,
            "anchor_id": self.anchor_id,
        }



@dataclass
class BrowserStateSnapshot:
    snapshot_id: str
    timestamp: float
    catalog_entries: Dict[str, Dict[str, Any]]
    selection: List[str]
    tags: Dict[str, Dict[str, Any]]
    collections: Dict[str, Dict[str, Any]]
    state_hash: str = ""

    def compute_hash(self) -> str:
        canonical = {
            "catalog_entries": {k: v for k, v in sorted(self.catalog_entries.items())},
            "selection": sorted(self.selection),
            "tags": {k: v for k, v in sorted(self.tags.items())},
            "collections": {k: v for k, v in sorted(self.collections.items())},
        }
        encoded = json.dumps(canonical, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def __post_init__(self):
        if not self.state_hash:
            self.state_hash = self.compute_hash()


@dataclass
class BrowserTelemetry:
    catalog_size: int = 0
    index_size: int = 0
    search_latency_ms: float = 0.0
    filter_latency_ms: float = 0.0
    sort_latency_ms: float = 0.0
    thumbnail_cache_hits: int = 0
    thumbnail_cache_misses: int = 0
    active_watchers: int = 0


@dataclass
class BrowserDiagnosticBundle:
    bundle_id: str
    timestamp: float
    snapshot: BrowserStateSnapshot
    telemetry: BrowserTelemetry
    signature: str = ""

    def sign(self) -> str:
        payload = f"{self.bundle_id}:{self.timestamp}:{self.snapshot.state_hash}:{self.telemetry.catalog_size}:{self.telemetry.index_size}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def __post_init__(self):
        if not self.signature:
            self.signature = self.sign()


# Collision-safe aliases for root uaf export
BrowserAssetIdentity = AssetIdentity
BrowserCatalogEntry = CatalogEntry
BrowserAssetMetadata = AssetMetadata
