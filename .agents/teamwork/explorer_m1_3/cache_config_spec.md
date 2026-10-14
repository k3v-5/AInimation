# CAS Asset Cache & App Config Specification (`cache_config_spec.md`)

## 1. Overview and Architecture

This document specifies the technical design, architectural contracts, and complete reference implementations for:
1. `backend/core/config.py`: Centralized environment and application configuration powered by Pydantic v2 `BaseSettings` (`pydantic-settings`).
2. `backend/core/cache.py`: Content-Addressable Storage (CAS) asset cache utilizing SHA-256 content and parameter hashing for computationally heavy and expensive generation steps (3D meshes `.glb`/`.fbx`, audio stems `.wav`, mocap data `.glb`/`.bvh`/`.json`, and neural passes).

Both components adhere strictly to the project engineering directives in `GEMINI.md`:
- **100% Strict Typing (Zero-Any Policy)**: No use of `typing.Any`. All parameters, returns, mappings, and collections use strict unions, generics, and Pydantic models.
- **SOLID Architecture**: Clean separation between storage interfaces, hashing utilities, and configuration domains.
- **Atomic Operations & Fault Tolerance**: Thread-safe execution, atomic writes via unique temporary files and filesystem renames, and predictable TTL/LRU invalidation.
- **Cross-Platform Compatibility**: Robust handling of Windows and POSIX path semantics with `pathlib.Path`.

---

## 2. Configuration Architecture (`backend/core/config.py`)

### 2.1 Design Requirements & Scope

The application configuration must consolidate all runtime parameters across:
- **Environment & Flags**: Execution environment (`development`, `test`, `production`), `fast_test_mode` (for mock fallbacks and instant synthesis without real external API calls or GPU passes), and log level.
- **Directory Paths**: Project root, asset cache directory, final outputs directory, temporary working directory. All paths automatically resolved and verified.
- **UE5 Bridge & Mock Settings**: Remote Control REST port (`30010`), WebSocket port (`30020`), host (`127.0.0.1`), mock server mode toggle, and request timeout.
- **FastMCP Server Settings**: MCP server name, host, port, transport protocol (`sse`, `stdio`).
- **Telemetry & Bus Settings**: Telemetry broadcast WebSocket port (`8001`), historical event buffer limit.
- **Cloud API Keys & Services**: Optional cloud API credentials for Fal.ai (`FAL_KEY`), Tripo AI (`TRIPO_API_KEY`), Replicate (`REPLICATE_API_TOKEN`), and local ComfyUI host/port.
- **Cache Policy**: Cache enablement flag, default TTL, max storage quota in bytes.

### 2.2 Environment Hierarchy and Precedence
1. Explicit function arguments / override dictionary (e.g. in test suites via `get_test_settings`).
2. Operating system environment variables prefixed with `IANIMATION_` (e.g. `IANIMATION_FAST_TEST_MODE=true`).
3. Standard cloud API environment variables without prefix as fallback (e.g. `FAL_KEY`, `TRIPO_API_KEY`).
4. Local `.env` file at project root (UTF-8 encoded).
5. Safe default values in Pydantic fields.

### 2.3 Strict Type Models for Configuration

```python
# Literal types for strict settings validation (Zero-Any Policy)
AppEnvironment = Literal["development", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
McpTransport = Literal["sse", "stdio", "stream"]
```

### 2.4 Reference Implementation (`backend/core/config.py`)

```python
"""backend/core/config.py

Central application configuration and environment variable resolver for IANIMATION.
Adheres strictly to Pydantic v2 BaseSettings and the Zero-Any policy.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["development", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
McpTransport = Literal["sse", "stdio", "stream"]


class Settings(BaseSettings):
    """Central configuration class for IANIMATION application.
    
    Loads configuration from environment variables (prefixed with IANIMATION_),
    standard service environment variables (e.g. FAL_KEY), or local .env files.
    """

    model_config = SettingsConfigDict(
        env_prefix="IANIMATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Application & Execution Flags
    # -------------------------------------------------------------------------
    app_name: str = Field(
        default="IANIMATION 3D AI Orchestrator",
        description="Name of the desktop application orchestrator.",
    )
    env: AppEnvironment = Field(
        default="development",
        description="Runtime environment mode (development, production, test).",
    )
    fast_test_mode: bool = Field(
        default=False,
        description=(
            "When True, enables synthetic mock fallbacks for AI inference and UE5 calls, "
            "allowing ultra-fast offline test execution without GPU/Cloud dependencies."
        ),
    )
    log_level: LogLevel = Field(
        default="INFO",
        description="Root logging verbosity level.",
    )
    debug: bool = Field(
        default=False,
        description="Enable verbose debug assertions and telemetry details.",
    )

    # -------------------------------------------------------------------------
    # File System Paths
    # -------------------------------------------------------------------------
    project_root: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Root directory of the project.",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.cwd() / ".cache",
        description="Directory for Content-Addressable Storage (CAS) asset cache.",
    )
    output_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "outputs",
        description="Directory for final exported renders, audio stems, and 3D files.",
    )
    temp_dir: Path = Field(
        default_factory=lambda: Path.cwd() / ".tmp",
        description="Directory for temporary scratch files during processing.",
    )

    # -------------------------------------------------------------------------
    # Unreal Engine 5 Bridge & Mock Settings
    # -------------------------------------------------------------------------
    ue5_host: str = Field(
        default="127.0.0.1",
        description="Host address for Unreal Engine 5 Remote Control API.",
    )
    ue5_http_port: int = Field(
        default=30010,
        description="Unreal Engine 5 Remote Control REST HTTP port.",
    )
    ue5_ws_port: int = Field(
        default=30020,
        description="Unreal Engine 5 Remote Control WebSocket port.",
    )
    ue5_mock_mode: bool = Field(
        default=True,
        description="If True, connect to internal UE5 Mock Server instead of requiring live UE5.",
    )
    ue5_timeout_seconds: float = Field(
        default=30.0,
        description="Timeout in seconds for UE5 Remote Control RPC calls.",
    )

    # -------------------------------------------------------------------------
    # FastMCP Server Settings
    # -------------------------------------------------------------------------
    mcp_server_name: str = Field(
        default="ianimation-mcp",
        description="Identifiable name of the FastMCP server instance.",
    )
    mcp_server_host: str = Field(
        default="127.0.0.1",
        description="Host on which FastMCP server binds.",
    )
    mcp_server_port: int = Field(
        default=8000,
        description="Port for FastMCP SSE server or HTTP endpoint.",
    )
    mcp_transport: McpTransport = Field(
        default="sse",
        description="Communication transport protocol for MCP client-server communication.",
    )

    # -------------------------------------------------------------------------
    # Telemetry & Event Streaming Settings
    # -------------------------------------------------------------------------
    telemetry_ws_port: int = Field(
        default=8001,
        description="WebSocket broadcast port for real-time progress and telemetry events.",
    )
    telemetry_history_size: int = Field(
        default=1000,
        description="Maximum number of historical telemetry events preserved in memory.",
    )

    # -------------------------------------------------------------------------
    # Cloud API Keys & External Services (Optional / Fallback)
    # -------------------------------------------------------------------------
    fal_key: Optional[str] = Field(
        default=None,
        description="API key for Fal.ai Cloud Generative 3D & Image services.",
    )
    tripo_api_key: Optional[str] = Field(
        default=None,
        description="API key for Tripo AI 3D Mesh generation platform.",
    )
    replicate_api_token: Optional[str] = Field(
        default=None,
        description="API token for Replicate models (Demucs, 3D, Mocap).",
    )
    comfyui_host: str = Field(
        default="127.0.0.1",
        description="Host address for local or headless ComfyUI server.",
    )
    comfyui_port: int = Field(
        default=8188,
        description="Port for local ComfyUI REST/WebSocket endpoint.",
    )

    # -------------------------------------------------------------------------
    # CAS Asset Cache Policies
    # -------------------------------------------------------------------------
    cache_enabled: bool = Field(
        default=True,
        description="Global toggle for Content-Addressable Storage (CAS) caching.",
    )
    cache_ttl_seconds: int = Field(
        default=86400 * 7,  # 7 days
        description="Default Time-To-Live in seconds for cached assets (0 = indefinite).",
    )
    cache_max_size_bytes: int = Field(
        default=10 * 1024 * 1024 * 1024,  # 10 GiB
        description="Maximum cache storage quota in bytes before LRU eviction triggers.",
    )

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("cache_dir", "output_dir", "temp_dir", "project_root", mode="after")
    @classmethod
    def resolve_and_normalize_path(cls, v: Path) -> Path:
        """Resolve paths to absolute normalized paths."""
        return v.resolve()

    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    @property
    def ue5_http_url(self) -> str:
        """Construct the full base HTTP URL for UE5 Remote Control."""
        return f"http://{self.ue5_host}:{self.ue5_http_port}"

    @property
    def ue5_ws_url(self) -> str:
        """Construct the full base WebSocket URL for UE5 Remote Control."""
        return f"ws://{self.ue5_host}:{self.ue5_ws_port}/remote/protocol"

    @property
    def comfyui_url(self) -> str:
        """Construct the full base HTTP URL for ComfyUI."""
        return f"http://{self.comfyui_host}:{self.comfyui_port}"

    # -------------------------------------------------------------------------
    # Directory Bootstrap Helper
    # -------------------------------------------------------------------------
    def ensure_directories(self) -> None:
        """Create configured directory paths on disk if they do not exist."""
        for path in (self.cache_dir, self.output_dir, self.temp_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve cached application settings instance.
    
    Reads external cloud keys from standard un-prefixed env vars if IANIMATION_ prefix was not set.
    """
    settings = Settings()
    
    # Fallback to standard cloud environment variable names if not provided via prefix
    if not settings.fal_key:
        settings.fal_key = os.getenv("FAL_KEY")
    if not settings.tripo_api_key:
        settings.tripo_api_key = os.getenv("TRIPO_API_KEY")
    if not settings.replicate_api_token:
        settings.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

    settings.ensure_directories()
    return settings


def get_test_settings(**overrides: Union[str, int, float, bool, Path, None]) -> Settings:
    """Construct an isolated Settings instance for test execution.
    
    Does not use the global lru_cache, allowing fine-grained test overrides.
    """
    settings = Settings(**overrides)
    settings.ensure_directories()
    return settings
```

---

## 3. CAS Asset Cache Architecture (`backend/core/cache.py`)

### 3.1 Design Principles and CAS Protocol

In the IANIMATION production pipeline, generative operations (Audio stem isolation with Demucs, Image-to-3D mesh synthesis, Auto-Rigging, MediaPipe 3D mocap extraction, and Neural video enhancement) require seconds to minutes of computation or cloud credit expenditure.

To ensure instant responsiveness, idempotent re-executions, and deterministic testing:
1. **Content-Addressable Keying (SHA-256)**:
   - A unique cache key is generated from the SHA-256 hash of the input file(s) AND a canonical normalized representation of all execution parameters (e.g. `texture_resolution=1024`, `model="tripo-v2.5"`, `fps=30`).
2. **Two-Tier Namespace Hierarchy**:
   - Assets are partitioned by subsystem namespace (e.g. `audio_stems`, `image_to_3d`, `auto_rig`, `mocap`, `neural`).
   - Within each namespace, files are organized by a 2-character hex prefix directory to maintain filesystem performance across tens of thousands of items:
     `<cache_dir>/<namespace>/<sha256[:2]>/<sha256[2:]>/`
3. **Atomic File Ingestion**:
   - Assets are written first to a temporary file (`.tmp.<uuid>`) within the same directory tree.
   - Flushed and forced to disk via `os.fsync`.
   - Atomically renamed to the final asset filename using `os.replace` (atomic on both Windows and POSIX within the same filesystem).
   - Prevents race conditions, corrupted incomplete reads, or orphaned partial writes during process aborts.
4. **Sidecar Metadata Envelope**:
   - Every asset is stored alongside a JSON metadata file (`metadata.json`) containing creation timestamp, last accessed timestamp, TTL expiration, byte size, origin tags, and parameter hashes.
5. **Thread-Safety & Concurrency**:
   - In-memory index and mutations protected by a reentrant lock (`threading.RLock`).
6. **Zero-Any Compliance**:
   - Parameter representations and metadata tags are strictly typed:
     `Mapping[str, Union[str, int, float, bool, None]]` and `Dict[str, str]`.

### 3.2 Metadata Schema (`AssetMetadata`)

```python
class AssetMetadata(BaseModel):
    """Structured sidecar metadata for a cached asset."""
    cache_key: str = Field(..., description="Full SHA-256 hex string cache key.")
    namespace: str = Field(..., description="Subsystem namespace (e.g. image_to_3d, audio_stems).")
    original_filename: str = Field(..., description="Original base filename of the stored artifact.")
    asset_extension: str = Field(..., description="File extension including leading dot (e.g. .glb, .wav).")
    file_size_bytes: int = Field(..., ge=0, description="Exact size of the asset file in bytes.")
    sha256_hash: str = Field(..., description="Direct SHA-256 hash of the stored file contents.")
    created_at: datetime = Field(..., description="UTC timestamp when the asset was first ingested.")
    accessed_at: datetime = Field(..., description="UTC timestamp of the most recent retrieval.")
    ttl_seconds: Optional[int] = Field(default=None, description="Time-to-live in seconds, or None for no expiration.")
    tags: Dict[str, str] = Field(default_factory=dict, description="Arbitrary metadata key-value tags.")
    params: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="Canonical parameters used during generation of this asset.",
    )

    @property
    def is_expired(self) -> bool:
        """Check whether the asset has exceeded its configured TTL."""
        if self.ttl_seconds is None or self.ttl_seconds <= 0:
            return False
        now = datetime.now(timezone.utc)
        return (now - self.created_at).total_seconds() > self.ttl_seconds
```

### 3.3 Canonical Hashing Mechanism

Hashing must be deterministic regardless of dictionary insertion order:
```python
def canonical_params_hash(params: Mapping[str, Union[str, int, float, bool, None]]) -> str:
    """Compute a deterministic SHA-256 hash from a dictionary of parameters."""
    normalized_json = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized_json.encode("utf-8")).hexdigest()

def compute_cache_key(
    namespace: str,
    input_hashes: Sequence[str],
    params: Mapping[str, Union[str, int, float, bool, None]],
) -> str:
    """Compute an unforgeable composite cache key for an operation."""
    hasher = hashlib.sha256()
    hasher.update(namespace.encode("utf-8"))
    for h in sorted(input_hashes):
        hasher.update(h.encode("utf-8"))
    hasher.update(canonical_params_hash(params).encode("utf-8"))
    return hasher.hexdigest()
```

### 3.4 Reference Implementation (`backend/core/cache.py`)

```python
"""backend/core/cache.py

Content-Addressable Storage (CAS) asset cache for IANIMATION.
Provides SHA-256 content/parameter keying, atomic disk writes, TTL invalidation,
LRU eviction, and metadata tagging with strict typing (Zero-Any policy).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

from pydantic import BaseModel, Field

# Strictly typed parameter value union to prevent Any
ParamValue = Union[str, int, float, bool, None]
ParamDict = Mapping[str, ParamValue]


# -----------------------------------------------------------------------------
# Asset Metadata Model
# -----------------------------------------------------------------------------
class AssetMetadata(BaseModel):
    """Pydantic model representing sidecar metadata for a cached asset."""

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
    """Compute SHA-256 hex digest of a file using buffered chunk streaming.
    
    Safe for very large files (.glb meshes, raw .wav stems, 4K .mp4 renders).
    """
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def canonical_params_hash(params: ParamDict) -> str:
    """Compute deterministic SHA-256 hash of a dictionary with sorted keys."""
    serialized = json.dumps(params, sort_keys=True, separators=(",", ":"))
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
    """Thread-safe Content-Addressable Storage (CAS) engine.
    
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
        """Resolve partitioned directory: <base_dir>/<namespace>/<key[:2]>/<key[2:]>/"""
        prefix = cache_key[:2]
        suffix = cache_key[2:]
        return self.base_dir / namespace / prefix / suffix

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
        """Ingest an existing file on disk into the CAS cache atomically.
        
        If cache_key is not supplied, it is derived from the source file content hash.
        """
        source_path = source_path.resolve()
        if not source_path.is_file():
            raise FileNotFoundError(f"Source file does not exist: {source_path}")

        file_hash = hash_file(source_path)
        effective_params = dict(params or {})
        effective_tags = dict(tags or {})

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
        effective_params = dict(params or {})
        effective_tags = dict(tags or {})

        if cache_key is None:
            cache_key = compute_composite_cache_key(namespace, [data_hash], effective_params)

        ext = extension if extension.startswith(".") else f".{extension}"
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
        """Retrieve a cached asset by namespace and exact cache_key.
        
        Returns None if not present or expired (and purges expired entries).
        """
        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
            meta_path = self._get_metadata_path(entry_dir)

            if not meta_path.is_file():
                return None

            try:
                with meta_path.open("r", encoding="utf-8") as f:
                    meta_dict = json.load(f)
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
        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
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
        with self._lock:
            ns_dir = self.base_dir / namespace
            if not ns_dir.is_dir():
                return 0
            count = 0
            for meta_file in ns_dir.glob("*/*/metadata.json"):
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
                        meta_dict = json.load(f)
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
        """Prune least-recently-accessed assets until total cache size <= target_max_bytes.
        
        Returns (pruned_count, freed_bytes).
        """
        quota = target_max_bytes if target_max_bytes is not None else self.max_size_bytes

        with self._lock:
            entries: List[Tuple[datetime, int, str, str]] = []  # (accessed_at, size, ns, key)
            total_size = 0

            for meta_path in self.base_dir.glob("*/*/*/metadata.json"):
                try:
                    with meta_path.open("r", encoding="utf-8") as f:
                        meta_dict = json.load(f)
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
        for p in self.base_dir.rglob("asset.*"):
            if p.is_file():
                total += p.stat().st_size
        return total
```

---

## 4. Test Specifications

### 4.1 Config Test Plan (`tests/backend/test_config.py`)

The test suite must verify:
1. `test_default_settings`: Checks defaults for ports (30010, 30020, 8000), directory paths, and fallback flags.
2. `test_computed_properties`: Validates `ue5_http_url` and `ue5_ws_url` string formatting.
3. `test_environment_overrides`: Verifies that `IANIMATION_FAST_TEST_MODE=true` or custom ports override defaults.
4. `test_ensure_directories`: Asserts that `cache_dir`, `output_dir`, and `temp_dir` are automatically created on disk.
5. `test_get_test_settings_isolation`: Verifies that test settings instances are decoupled from global singleton.

```python
"""tests/backend/test_config.py"""

import os
from pathlib import Path
from backend.core.config import Settings, get_settings, get_test_settings


def test_default_settings(tmp_path: Path) -> None:
    settings = get_test_settings(project_root=tmp_path, cache_dir=tmp_path / "cache")
    assert settings.ue5_http_port == 30010
    assert settings.ue5_ws_port == 30020
    assert settings.mcp_server_port == 8000
    assert settings.fast_test_mode is False
    assert settings.ue5_mock_mode is True
    assert settings.cache_dir.is_dir()


def test_computed_properties() -> None:
    settings = Settings(ue5_host="192.168.1.100", ue5_http_port=30010, ue5_ws_port=30020)
    assert settings.ue5_http_url == "http://192.168.1.100:30010"
    assert settings.ue5_ws_url == "ws://192.168.1.100:30020/remote/protocol"


def test_environment_variable_overrides(monkeypatch) -> None:
    monkeypatch.setenv("IANIMATION_FAST_TEST_MODE", "true")
    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "30999")
    monkeypatch.setenv("FAL_KEY", "test-fal-key-1234")

    settings = get_settings()
    assert settings.fast_test_mode is True
    assert settings.ue5_http_port == 30999
    assert settings.fal_key == "test-fal-key-1234"
```

### 4.2 Cache Test Plan (`tests/backend/test_cache.py`)

The test suite must verify:
1. `test_hashing_determinism`: Asserts that `hash_bytes`, `hash_file`, and `canonical_params_hash` are completely stable and order-independent.
2. `test_put_and_get_bytes`: Tests in-memory byte ingestion, metadata preservation, and retrieval.
3. `test_put_and_get_file`: Tests file ingestion, extension preservation, and atomic creation.
4. `test_cache_miss`: Verifies that non-existent keys return `None`.
5. `test_ttl_expiration`: Verifies that assets with `ttl_seconds=1` are invalidated after expiry.
6. `test_composite_key_hit`: Validates `get_by_inputs` with identical parameters and input files.
7. `test_atomic_write_safety`: Verifies temporary files are cleaned up and replaced without corruption.
8. `test_lru_pruning`: Verifies least-recently-accessed eviction when quota is exceeded.

```python
"""tests/backend/test_cache.py"""

import time
from pathlib import Path
from backend.core.cache import (
    ContentAddressableStorage,
    canonical_params_hash,
    hash_bytes,
    hash_file,
)


def test_canonical_params_hash_order_independence() -> None:
    params_a = {"resolution": 1024, "provider": "fal", "turbo": True}
    params_b = {"turbo": True, "provider": "fal", "resolution": 1024}
    assert canonical_params_hash(params_a) == canonical_params_hash(params_b)


def test_put_and_get_file(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    sample_file = tmp_path / "model.glb"
    sample_file.write_bytes(b"GLB_BINARY_CONTENT_STUB")

    cached = cache.put_file(
        source_path=sample_file,
        namespace="image_to_3d",
        params={"resolution": 1024},
        tags={"provider": "tripo"},
    )

    assert cached.file_path.is_file()
    assert cached.metadata.namespace == "image_to_3d"
    assert cached.metadata.tags["provider"] == "tripo"

    # Retrieve by key
    retrieved = cache.get("image_to_3d", cached.cache_key)
    assert retrieved is not None
    assert retrieved.file_path.read_bytes() == b"GLB_BINARY_CONTENT_STUB"


def test_get_by_inputs(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    img = tmp_path / "character.png"
    img.write_bytes(b"FAKE_PNG_BYTES")

    cached = cache.put_file(
        source_path=img,
        namespace="image_to_3d",
        params={"res": 512},
    )

    hit = cache.get_by_inputs(
        namespace="image_to_3d",
        input_file_paths=[img],
        params={"res": 512},
    )
    assert hit is not None
    assert hit.cache_key == cached.cache_key


def test_ttl_expiration(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas")
    cached = cache.put_bytes(
        data=b"EXPIRE_ME",
        extension=".bin",
        namespace="temp",
        ttl_seconds=1,
    )
    
    assert cache.get("temp", cached.cache_key) is not None
    time.sleep(1.2)
    assert cache.get("temp", cached.cache_key) is None


def test_lru_pruning(tmp_path: Path) -> None:
    cache = ContentAddressableStorage(base_dir=tmp_path / "cas", max_size_bytes=50)
    
    # Store 3 items of 25 bytes each (total 75 bytes > 50)
    c1 = cache.put_bytes(b"A" * 25, ".bin", "ns")
    time.sleep(0.05)
    c2 = cache.put_bytes(b"B" * 25, ".bin", "ns")
    time.sleep(0.05)
    c3 = cache.put_bytes(b"C" * 25, ".bin", "ns")

    pruned, freed = cache.prune_lru(target_max_bytes=50)
    assert pruned >= 1
    assert freed >= 25
    # Oldest c1 should have been pruned
    assert cache.get("ns", c1.cache_key) is None
    # Most recent c3 should still exist
    assert cache.get("ns", c3.cache_key) is not None
```

---

## 5. Pipeline Integration Contracts

### 5.1 Image-to-3D Integration (`backend/ai/image_to_3d.py`)
```python
# Usage pattern in Image-to-3D provider:
cached = cache.get_by_inputs(
    namespace="image_to_3d",
    input_file_paths=[Path(request.image_path)],
    params={"provider": request.provider, "texture_res": request.texture_resolution},
)
if cached is not None:
    return ImageTo3DResult(
        mesh_path=str(cached.file_path),
        cached=True,
        vertex_count=int(cached.metadata.tags.get("vertex_count", "0")),
        ...
    )
```

### 5.2 Audio Stems Integration (`backend/ai/audio.py`)
```python
# Demucs stem separation caching:
stems_cache_key = compute_composite_cache_key(
    namespace="audio_stems",
    input_hashes=[hash_file(Path(audio_path))],
    params={"model": "htdemucs_4stems"},
)
```

### 5.3 FastMCP Tool Reporting
All 6 atomic FastMCP tools can inspect the cache and return immediate cached responses (`cached=True`), fulfilling acceptance criteria:
`image_to_3d(image_path: str, provider: str = "auto", texture_resolution: int = 1024) -> ImageTo3DResult`

---

## 6. GEMINI.md Compliance Matrix

| Rule | Requirement | Implementation in Spec |
|------|-------------|-------------------------|
| **SOLID: SRP** | Single responsibility per class | `Settings` handles configuration only; `ContentAddressableStorage` handles filesystem CAS only; `AssetMetadata` represents sidecar contract. |
| **SOLID: OCP** | Extensible without modification | Custom CAS storage backends (e.g. S3/MinIO) can implement the same API without altering caller pipelines. |
| **SOLID: LSP** | Subtypes substitutable | `CachedAsset` and `AssetMetadata` maintain uniform interface contracts. |
| **SOLID: DIP** | Depend on abstractions | Pipeline providers receive `ContentAddressableStorage` or `Settings` via dependency injection (`get_settings()`). |
| **Zero-Any Policy** | 0% `Any` types across code | Strict `ParamValue = Union[str, int, float, bool, None]`, typed mappings, strict literals. |
| **Pydantic v2** | Native v2 models and settings | `BaseSettings` with `SettingsConfigDict`, `field_validator`, and `BaseModel` sidecar schemas. |
| **Atomic Writes** | Fault tolerance on write | Temp file creation -> `os.fsync` -> `os.replace` eliminates corrupt partial reads. |
| **Platform Portability** | Windows & POSIX path safety | Pure `pathlib.Path` with `.resolve()`, normalized forward/backslash handling. |
