"""
Content-Addressable Storage (CAS) asset cache for IANIMATION.

Provides SHA-256 content/parameter keying, atomic disk writes, TTL invalidation,
LRU eviction, and metadata tagging with strict typing (Zero-Any policy).
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import threading
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union
import uuid

from pydantic import BaseModel, ConfigDict, Field

# Strictly typed parameter value union to prevent Any (including Path support)
ParamValue = Union[str, int, float, bool, Path, None]
ParamDict = Mapping[str, ParamValue]

# Safe identifier pattern for cache namespaces and keys (defense against path traversal)
_IDENTIFIER_PATTERN: re.Pattern[str] = re.compile(r"^[a-zA-Z0-9_\-]+$")


# -----------------------------------------------------------------------------
# Asset Metadata Model
# -----------------------------------------------------------------------------

class AssetMetadata(BaseModel):
    """Pydantic model representing sidecar metadata for a cached asset."""
    model_config = ConfigDict(
        strict=False,
        validate_assignment=True,
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=False,
    )

    cache_key: str = Field(..., description="Unique SHA-256 hex cache key.")
    namespace: str = Field(..., description="Pipeline namespace (e.g. image_to_3d, audio_stems).")
    original_filename: str = Field(..., description="Original filename of the stored artifact.")
    asset_extension: str = Field(..., description="Asset extension including dot (e.g. .glb).")
    file_size_bytes: int = Field(..., ge=0, description="Size of the asset in bytes.")
    sha256_hash: str = Field(..., description="SHA-256 checksum of the asset file.")
    created_at: datetime = Field(..., description="UTC creation timestamp.")
    accessed_at: datetime = Field(..., description="UTC last accessed timestamp.")
    ttl_seconds: Optional[int] = Field(default=None, description="Time-To-Live in seconds.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Descriptive key-value tags.")
    params: Dict[str, ParamValue] = Field(default_factory=dict, description="Input generation parameters.")

    @property
    def is_expired(self) -> bool:
        """Determine whether the asset has exceeded its configured TTL."""
        if self.ttl_seconds is None or self.ttl_seconds <= 0:
            return False
        now = datetime.now(timezone.utc)
        return (now - self.created_at).total_seconds() > self.ttl_seconds


class CachedAsset(BaseModel):
    """Reference wrapper containing an asset file path and its verified metadata."""
    model_config = ConfigDict(
        strict=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    cache_key: str
    file_path: Path
    metadata: AssetMetadata


# -----------------------------------------------------------------------------
# Hashing Utilities
# -----------------------------------------------------------------------------

def hash_bytes(data: bytes) -> str:
    """Compute SHA-256 hex digest of in-memory bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_file(file_path: Path, chunk_size: int = 65536) -> str:
    """
    Compute SHA-256 hex digest of a file using buffered chunk streaming.

    Safe for very large files (.glb meshes, raw .wav stems, 4K .mp4 renders).
    """
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def _canonical_json_default(obj: object) -> str:
    """Coerce non-primitive objects (such as Path) to deterministic strings."""
    if isinstance(obj, Path):
        return obj.as_posix().replace("\\", "/")
    return str(obj).replace("\\", "/")


def canonical_params_hash(params: ParamDict) -> str:
    """Compute deterministic SHA-256 hash of a dictionary with sorted keys."""
    serialized = json.dumps(
        params,
        sort_keys=True,
        separators=(",", ":"),
        default=_canonical_json_default,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_composite_cache_key(
    namespace: str,
    input_hashes: Sequence[str],
    params: ParamDict,
) -> str:
    """Generate a composite cache key combining namespace, input content hashes, and parameters."""
    hasher = hashlib.sha256()
    hasher.update(namespace.encode("utf-8"))
    for h in sorted(input_hashes):
        hasher.update(h.encode("utf-8"))
    hasher.update(canonical_params_hash(params).encode("utf-8"))
    return hasher.hexdigest()


# -----------------------------------------------------------------------------
# Content-Addressable Storage (CAS) Manager
# -----------------------------------------------------------------------------

class ContentAddressableStorage:
    """
    Thread-safe Content-Addressable Storage (CAS) engine.

    Stores files indexed by SHA-256 keys with atomic writes, metadata sidecars,
    TTL invalidation, and LRU pruning.
    """

    def __init__(
        self,
        base_dir: Path,
        default_ttl_seconds: Optional[int] = 86400 * 7,
        max_size_bytes: int = 10 * 1024 * 1024 * 1024,
    ) -> None:
        self.base_dir: Path = base_dir.resolve()
        self.default_ttl_seconds: Optional[int] = default_ttl_seconds
        self.max_size_bytes: int = max_size_bytes
        self._lock: threading.RLock = threading.RLock()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Internal Path Resolvers
    # -------------------------------------------------------------------------
    def _get_entry_dir(self, namespace: str, cache_key: str) -> Path:
        """
        Resolve partitioned directory: <base_dir>/<namespace>/<key[:2]>/<key[2:]>/

        Sanitizes and validates namespace and cache_key against path traversal,
        verifying that the resolved directory strictly resides within base_dir.
        """
        if not isinstance(namespace, str) or not _IDENTIFIER_PATTERN.match(namespace):
            raise ValueError(
                f"Invalid namespace '{namespace}': must be non-empty and match regex ^[a-zA-Z0-9_\\-]+$"
            )
        if not isinstance(cache_key, str) or len(cache_key) < 3 or not _IDENTIFIER_PATTERN.match(cache_key):
            raise ValueError(
                f"Invalid cache_key '{cache_key}': must be at least 3 characters and match regex ^[a-zA-Z0-9_\\-]+$"
            )

        prefix = cache_key[:2]
        suffix = cache_key[2:]
        entry_dir = self.base_dir / namespace / prefix / suffix

        resolved_entry = entry_dir.resolve()
        resolved_base = self.base_dir.resolve()
        if not resolved_entry.is_relative_to(resolved_base) or resolved_entry == resolved_base:
            raise ValueError(
                f"Path traversal detected: {entry_dir} escapes base directory {self.base_dir}"
            )

        return entry_dir

    def _get_metadata_path(self, entry_dir: Path) -> Path:
        """Resolve path to sidecar metadata JSON file."""
        return entry_dir / "metadata.json"

    # -------------------------------------------------------------------------
    # Ingestion & Atomic Writing
    # -------------------------------------------------------------------------
    def put_file(
        self,
        source_path: Path,
        namespace: str,
        cache_key: Optional[str] = None,
        params: Optional[ParamDict] = None,
        tags: Optional[Dict[str, str]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> CachedAsset:
        """
        Ingest an existing file on disk into the CAS cache atomically.

        If cache_key is not supplied, it is derived from the source file content hash.
        """
        source_path = source_path.resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        file_hash = hash_file(source_path)
        effective_params: Dict[str, ParamValue] = {
            k: (v.as_posix() if isinstance(v, Path) else v)
            for k, v in (params or {}).items()
        }
        effective_tags: Dict[str, str] = dict(tags or {})

        if cache_key is None:
            cache_key = compute_composite_cache_key(namespace, [file_hash], effective_params)

        ext = source_path.suffix.lower()
        now = datetime.now(timezone.utc)
        effective_ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
            entry_dir.mkdir(parents=True, exist_ok=True)

            target_asset_path = entry_dir / f"asset{ext}"
            meta_path = self._get_metadata_path(entry_dir)

            # Atomic copy using temporary file
            temp_asset_path = entry_dir / f".tmp_{uuid.uuid4().hex}{ext}"
            shutil.copy2(source_path, temp_asset_path)

            # Flush to disk
            with temp_asset_path.open("a+b") as f:
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            temp_asset_path.replace(target_asset_path)

            metadata = AssetMetadata(
                cache_key=cache_key,
                namespace=namespace,
                original_filename=source_path.name,
                asset_extension=ext,
                file_size_bytes=target_asset_path.stat().st_size,
                sha256_hash=file_hash,
                created_at=now,
                accessed_at=now,
                ttl_seconds=effective_ttl,
                tags=effective_tags,
                params=effective_params,
            )

            # Write metadata sidecar atomically
            self._write_metadata_atomically(meta_path, metadata)

            return CachedAsset(
                cache_key=cache_key,
                file_path=target_asset_path,
                metadata=metadata,
            )

    def put_bytes(
        self,
        data: bytes,
        extension: str,
        namespace: str,
        cache_key: Optional[str] = None,
        original_filename: str = "artifact",
        params: Optional[ParamDict] = None,
        tags: Optional[Dict[str, str]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> CachedAsset:
        """Store in-memory bytes into the CAS cache atomically."""
        data_hash = hash_bytes(data)
        effective_params: Dict[str, ParamValue] = {
            k: (v.as_posix() if isinstance(v, Path) else v)
            for k, v in (params or {}).items()
        }
        effective_tags: Dict[str, str] = dict(tags or {})

        if cache_key is None:
            cache_key = compute_composite_cache_key(namespace, [data_hash], effective_params)

        if not extension:
            ext = ""
        elif extension.startswith("."):
            ext = extension
        else:
            ext = f".{extension}"
        now = datetime.now(timezone.utc)
        effective_ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds

        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
            entry_dir.mkdir(parents=True, exist_ok=True)

            target_asset_path = entry_dir / f"asset{ext}"
            meta_path = self._get_metadata_path(entry_dir)

            temp_asset_path = entry_dir / f".tmp_{uuid.uuid4().hex}{ext}"
            with temp_asset_path.open("wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            temp_asset_path.replace(target_asset_path)

            metadata = AssetMetadata(
                cache_key=cache_key,
                namespace=namespace,
                original_filename=original_filename,
                asset_extension=ext,
                file_size_bytes=len(data),
                sha256_hash=data_hash,
                created_at=now,
                accessed_at=now,
                ttl_seconds=effective_ttl,
                tags=effective_tags,
                params=effective_params,
            )

            self._write_metadata_atomically(meta_path, metadata)

            return CachedAsset(
                cache_key=cache_key,
                file_path=target_asset_path,
                metadata=metadata,
            )

    def put(
        self,
        source: Union[Path, str, bytes],
        namespace: str,
        cache_key: Optional[str] = None,
        extension: Optional[str] = None,
        original_filename: str = "artifact",
        params: Optional[ParamDict] = None,
        tags: Optional[Dict[str, str]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> CachedAsset:
        """Unified put method supporting files on disk or in-memory byte payloads."""
        if isinstance(source, (str, Path)):
            p = Path(source)
            if p.is_file():
                return self.put_file(
                    source_path=p,
                    namespace=namespace,
                    cache_key=cache_key,
                    params=params,
                    tags=tags,
                    ttl_seconds=ttl_seconds,
                )
        if isinstance(source, bytes):
            ext = extension if extension is not None else ".bin"
            return self.put_bytes(
                data=source,
                extension=ext,
                namespace=namespace,
                cache_key=cache_key,
                original_filename=original_filename,
                params=params,
                tags=tags,
                ttl_seconds=ttl_seconds,
            )
        raise ValueError(f"Unsupported source type for put: {type(source)}")

    def _write_metadata_atomically(self, meta_path: Path, metadata: AssetMetadata) -> None:
        """Write metadata JSON to a temp file and atomically replace target."""
        temp_meta_path = meta_path.parent / f".tmp_meta_{uuid.uuid4().hex}.json"
        with temp_meta_path.open("w", encoding="utf-8") as f:
            f.write(metadata.model_dump_json(indent=2))
            f.flush()
            os.fsync(f.fileno())
        temp_meta_path.replace(meta_path)

    # -------------------------------------------------------------------------
    # Retrieval & Lookup
    # -------------------------------------------------------------------------
    def get(self, namespace: str, cache_key: str) -> Optional[CachedAsset]:
        """
        Retrieve a cached asset by namespace and exact cache_key.

        Returns None if not present or expired (and purges expired entries).
        """
        with self._lock:
            try:
                entry_dir = self._get_entry_dir(namespace, cache_key)
            except ValueError:
                # Malformed namespace or key cannot match any valid cache entry
                return None

            meta_path = self._get_metadata_path(entry_dir)

            if not meta_path.is_file():
                return None

            try:
                with meta_path.open("r", encoding="utf-8") as f:
                    meta_dict: Dict[str, object] = json.load(f)
                metadata = AssetMetadata.model_validate(meta_dict)
            except Exception:
                # Corrupted metadata; invalidate
                self.invalidate(namespace, cache_key)
                return None

            # Verify TTL
            if metadata.is_expired:
                self.invalidate(namespace, cache_key)
                return None

            asset_path = entry_dir / f"asset{metadata.asset_extension}"
            if not asset_path.is_file():
                self.invalidate(namespace, cache_key)
                return None

            # Update accessed_at timestamp
            metadata.accessed_at = datetime.now(timezone.utc)
            self._write_metadata_atomically(meta_path, metadata)

            return CachedAsset(
                cache_key=cache_key,
                file_path=asset_path,
                metadata=metadata,
            )

    def get_by_inputs(
        self,
        namespace: str,
        input_file_paths: Sequence[Path],
        params: ParamDict,
    ) -> Optional[CachedAsset]:
        """Compute composite cache key from input file hashes and retrieve cached asset if present."""
        input_hashes: List[str] = []
        for p in input_file_paths:
            if not p.is_file():
                return None
            input_hashes.append(hash_file(p))

        cache_key = compute_composite_cache_key(namespace, input_hashes, params)
        return self.get(namespace, cache_key)

    # -------------------------------------------------------------------------
    # Invalidation & Cleanup
    # -------------------------------------------------------------------------
    def invalidate(self, namespace: str, cache_key: str) -> bool:
        """Remove a specific cached entry from disk."""
        if not isinstance(namespace, str) or not _IDENTIFIER_PATTERN.match(namespace):
            raise ValueError(
                f"Invalid namespace '{namespace}': must be non-empty and match regex ^[a-zA-Z0-9_\\-]+$"
            )
        if not isinstance(cache_key, str) or len(cache_key) < 3 or not _IDENTIFIER_PATTERN.match(cache_key):
            raise ValueError(
                f"Invalid cache_key '{cache_key}': must be at least 3 characters and match regex ^[a-zA-Z0-9_\\-]+$"
            )

        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
            resolved_entry = entry_dir.resolve()
            resolved_base = self.base_dir.resolve()
            resolved_ns = (self.base_dir / namespace).resolve()

            if resolved_entry in (resolved_base, resolved_ns):
                raise ValueError(
                    f"Refusing to invalidate directory {resolved_entry}: target cannot be base_dir or namespace root"
                )

            if entry_dir.is_dir():
                shutil.rmtree(entry_dir, ignore_errors=True)
                # Cleanup parent prefix directory if empty
                parent_prefix = entry_dir.parent
                if parent_prefix.is_dir() and not any(parent_prefix.iterdir()):
                    parent_prefix.rmdir()
                return True
            return False

    def invalidate_namespace(self, namespace: str) -> int:
        """Remove all entries belonging to a specific namespace."""
        if not isinstance(namespace, str) or not _IDENTIFIER_PATTERN.match(namespace):
            raise ValueError(
                f"Invalid namespace '{namespace}': must be non-empty and match regex ^[a-zA-Z0-9_\\-]+$"
            )

        with self._lock:
            ns_dir = (self.base_dir / namespace).resolve()
            resolved_base = self.base_dir.resolve()
            if ns_dir == resolved_base or not ns_dir.is_relative_to(resolved_base):
                raise ValueError(
                    f"Invalid namespace '{namespace}': cannot resolve to or escape base directory"
                )
            if not ns_dir.is_dir():
                return 0
            count = 0
            for _ in ns_dir.glob("*/*/metadata.json"):
                count += 1
            shutil.rmtree(ns_dir, ignore_errors=True)
            return count

    def prune_expired(self) -> int:
        """Scan all cached entries and prune expired assets."""
        with self._lock:
            pruned_count = 0
            for meta_path in list(self.base_dir.glob("*/*/*/metadata.json")):
                try:
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_dict: Dict[str, object] = json.load(f)
                    metadata = AssetMetadata.model_validate(meta_dict)
                    if metadata.is_expired:
                        self.invalidate(metadata.namespace, metadata.cache_key)
                        pruned_count += 1
                except Exception:
                    # Invalidate corrupted entry
                    entry_dir = meta_path.parent
                    shutil.rmtree(entry_dir, ignore_errors=True)
                    pruned_count += 1
            return pruned_count

    def prune_lru(self, target_max_bytes: Optional[int] = None) -> Tuple[int, int]:
        """
        Prune least-recently-accessed assets until total cache size <= target_max_bytes.

        Returns (pruned_count, freed_bytes).
        """
        quota = target_max_bytes if target_max_bytes is not None else self.max_size_bytes

        with self._lock:
            entries: List[Tuple[datetime, int, str, str]] = []  # (accessed_at, size, ns, key)
            total_size = 0

            for meta_path in self.base_dir.glob("*/*/*/metadata.json"):
                try:
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_dict: Dict[str, object] = json.load(f)
                    metadata = AssetMetadata.model_validate(meta_dict)
                    entries.append((metadata.accessed_at, metadata.file_size_bytes, metadata.namespace, metadata.cache_key))
                    total_size += metadata.file_size_bytes
                except Exception:
                    continue

            if total_size <= quota:
                return (0, 0)

            # Sort ascending by accessed_at (oldest first)
            entries.sort(key=lambda x: x[0])

            pruned_count = 0
            freed_bytes = 0

            for _, size, ns, key in entries:
                if total_size <= quota:
                    break
                if self.invalidate(ns, key):
                    pruned_count += 1
                    freed_bytes += size
                    total_size -= size

            return (pruned_count, freed_bytes)

    def get_total_size_bytes(self) -> int:
        """Calculate total byte size of all assets currently residing in cache."""
        total = 0
        with self._lock:
            for p in self.base_dir.rglob("asset*"):
                if p.is_file() and (p.name == "asset" or p.name.startswith("asset.")):
                    try:
                        total += p.stat().st_size
                    except OSError:
                        continue
        return total


# Contract aliases for test suites and cross-milestone imports
CASCache = ContentAddressableStorage
ContentAddressableCache = ContentAddressableStorage


_GLOBAL_CAS_CACHE: Optional[ContentAddressableStorage] = None


def get_cache(base_dir: Optional[Path] = None) -> ContentAddressableStorage:
    """Retrieve or initialize the global ContentAddressableStorage instance."""
    global _GLOBAL_CAS_CACHE
    if _GLOBAL_CAS_CACHE is None:
        target_dir = base_dir if base_dir is not None else (Path.cwd() / ".cache")
        _GLOBAL_CAS_CACHE = ContentAddressableStorage(base_dir=target_dir)
    return _GLOBAL_CAS_CACHE
