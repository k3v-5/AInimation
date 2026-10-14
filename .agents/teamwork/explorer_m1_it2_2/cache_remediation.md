# CAS Asset Cache Remediation Specification

**Module**: `backend/core/cache.py`  
**Milestone**: Milestone 1 Iteration 2 (CAS Cache Remediation)  
**Author**: Explorer 2 (`explorer_m1_it2_2`)  
**Target Class**: `ContentAddressableStorage`, `canonical_params_hash`, and helper definitions  

---

## Executive Summary

Empirical adversarial testing in Milestone 1 Iteration 1 revealed four defects in `backend/core/cache.py`:
1. **Path Traversal in `_get_entry_dir()`**: `self.base_dir / namespace / prefix / suffix` permitted directory traversal characters (e.g. `../../escaped_dir`), allowing read, write, and deletion outside `base_dir`.
2. **Directory Wiping Bug in `invalidate()` and `invalidate_namespace()`**: When `cache_key` was empty or shorter than 3 characters, `suffix` was empty and `self.base_dir / namespace / "" / ""` resolved to `self.base_dir / namespace` (or `self.base_dir`), causing `shutil.rmtree(entry_dir)` to delete the entire namespace or the entire cache root.
3. **`get_total_size_bytes()` Omission of Extensionless Assets**: `self.base_dir.rglob("asset.*")` omitted extensionless files named `asset`, reporting `0` bytes for valid artifacts.
4. **`canonical_params_hash` Failure on `Path` Objects**: `json.dumps(params)` crashed with `TypeError: Object of type WindowsPath is not JSON serializable` when `pathlib.Path` objects were passed in parameters.

This document provides exact, drop-in remediation specifications conforming to the Zero-Any policy, SOLID principles, and defensive programming standards.

---

## Exact Proposed Changes for `backend/core/cache.py`

### Change 1: Add `import re` and Update Type Union & Identifier Regex

**Location**: Lines 8-26 of `backend/core/cache.py`

#### Before:
```python
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import threading
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union
import uuid

from pydantic import BaseModel, ConfigDict, Field

# Strictly typed parameter value union to prevent Any
ParamValue = Union[str, int, float, bool, None]
ParamDict = Mapping[str, ParamValue]
```

#### After:
```python
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
```

**Rationale**:
- `import re` is required for regex compilation.
- Adding `Path` to `ParamValue` allows callers to pass `Path` instances without `type: ignore` or `Any`, adhering strictly to the Zero-Any policy.
- `_IDENTIFIER_PATTERN` restricts namespace and cache_key characters to `[a-zA-Z0-9_\-]`, disallowing `/`, `\`, `.`, and null bytes.

---

### Change 2: Coerce `Path` Objects in `canonical_params_hash()`

**Location**: Lines 97-101 of `backend/core/cache.py`

#### Before:
```python
def canonical_params_hash(params: ParamDict) -> str:
    """Compute deterministic SHA-256 hash of a dictionary with sorted keys."""
    serialized = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```

#### After:
```python
def _canonical_json_default(obj: object) -> str:
    """Coerce non-primitive objects (such as Path) to deterministic strings."""
    if isinstance(obj, Path):
        return obj.as_posix()
    return str(obj)


def canonical_params_hash(params: ParamDict) -> str:
    """Compute deterministic SHA-256 hash of a dictionary with sorted keys."""
    serialized = json.dumps(
        params,
        sort_keys=True,
        separators=(",", ":"),
        default=_canonical_json_default,
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```

**Rationale**:
- `_canonical_json_default` converts `Path` objects via `obj.as_posix()`, ensuring uniform forward-slash representations across Windows and POSIX systems.
- Passing `default=_canonical_json_default` prevents `TypeError: Object of type WindowsPath is not JSON serializable`.
- Property: `canonical_params_hash({"source": Path("test/model.glb")}) == canonical_params_hash({"source": "test/model.glb"})`.

---

### Change 3: Harden `_get_entry_dir()` Against Path Traversal and Escape

**Location**: Lines 144-149 of `backend/core/cache.py`

#### Before:
```python
    def _get_entry_dir(self, namespace: str, cache_key: str) -> Path:
        """Resolve partitioned directory: <base_dir>/<namespace>/<key[:2]>/<key[2:]>/"""
        prefix = cache_key[:2]
        suffix = cache_key[2:]
        return self.base_dir / namespace / prefix / suffix
```

#### After:
```python
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
```

**Rationale**:
- Regex validation rejects any namespace or key with `..`, `/`, `\`, spaces, or control characters with `ValueError`.
- Minimum key length of 3 guarantees `prefix` (2 chars) and non-empty `suffix` (>= 1 char), preventing collapse into parent directories.
- `resolved_entry.is_relative_to(resolved_base)` and `resolved_entry == resolved_base` verify that the path strictly resides inside `base_dir`.

---

### Change 4: Normalize `Path` Parameters and Extension Handling in Ingestion

**Location**: Lines 176-184 & 240-248 of `backend/core/cache.py`

#### In `put_file()`:
```python
        file_hash = hash_file(source_path)
        effective_params: Dict[str, ParamValue] = {
            k: (v.as_posix() if isinstance(v, Path) else v)
            for k, v in (params or {}).items()
        }
        effective_tags: Dict[str, str] = dict(tags or {})
```

#### In `put_bytes()`:
```python
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
```

**Rationale**:
- Coercing `Path` values into `as_posix()` strings in `effective_params` ensures sidecar `metadata.json` contains valid, portable JSON primitives.
- `put_bytes` cleanly handles `extension=""` for extensionless assets without producing an awkward `"asset."` filename.

---

### Change 5: Graceful Cache Miss on Invalid Key in `get()`

**Location**: Lines 344-348 of `backend/core/cache.py`

#### Before:
```python
        with self._lock:
            entry_dir = self._get_entry_dir(namespace, cache_key)
            meta_path = self._get_metadata_path(entry_dir)
```

#### After:
```python
        with self._lock:
            try:
                entry_dir = self._get_entry_dir(namespace, cache_key)
            except ValueError:
                # Malformed namespace or key cannot match any valid cache entry
                return None

            meta_path = self._get_metadata_path(entry_dir)
```

**Rationale**:
- Read lookups (`get`) with malformed or invalid keys should gracefully return `None` (cache miss) rather than crashing caller lookup flows, while write and delete operations strictly reject invalid inputs.

---

### Change 6: Prevent Namespace & Base Directory Wiping in `invalidate()` and `invalidate_namespace()`

**Location**: Lines 398-422 of `backend/core/cache.py`

#### Before:
```python
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
            for _ in ns_dir.glob("*/*/metadata.json"):
                count += 1
            shutil.rmtree(ns_dir, ignore_errors=True)
            return count
```

#### After:
```python
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
```

**Rationale**:
- Explicit validation at the entry of both `invalidate` and `invalidate_namespace` guarantees empty strings (`""`) or keys under 3 characters raise `ValueError`.
- Extra defense-in-depth checks (`if resolved_entry in (resolved_base, resolved_ns)`) guarantee `shutil.rmtree` is never called on `self.base_dir` or the namespace root.
- In `invalidate_namespace()`, `ns_dir == resolved_base` check prevents base directory destruction.

---

### Change 7: Fix Size Calculation in `get_total_size_bytes()` for Extensionless Assets

**Location**: Lines 483-490 of `backend/core/cache.py`

#### Before:
```python
    def get_total_size_bytes(self) -> int:
        """Calculate total byte size of all assets currently residing in cache."""
        total = 0
        for p in self.base_dir.rglob("asset.*"):
            if p.is_file():
                total += p.stat().st_size
        return total
```

#### After:
```python
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
```

**Rationale**:
- `rglob("asset*")` accompanied by `p.name == "asset" or p.name.startswith("asset.")` matches:
  - Extensionless files: `entry_dir / "asset"` (resolving the bug found by Challenger 2).
  - Extensioned files: `entry_dir / "asset.glb"`, `"asset.wav"`, `"asset.mp4"`, `"asset.txt"`, `"asset.bin"`.
  - Excludes sidecars: `metadata.json` (starts with `m`).
  - Excludes temp files: `.tmp_*` (starts with `.`).
- `try ... except OSError` guards against race conditions where files are pruned during scanning.
- Evaluated under `self._lock` for thread safety.

---

## Test Suite Adjustments Required for Iteration 2

The initial adversarial test suites (`tests/backend/test_adversarial_m1.py` and `tests/backend/test_challenger_m1_2.py`) were authored in Iteration 1 to demonstrate the existence of the vulnerabilities. Upon applying the remediation above, the following test assertions must be updated to test the resolved behavior:

### 1. `tests/backend/test_challenger_m1_2.py`
In `test_cas_cache_path_traversal_boundaries`:
```python
def test_cas_cache_path_traversal_boundaries(tmp_path: Path) -> None:
    """Test that namespaces with directory traversal are rejected with ValueError."""
    base_dir = tmp_path / "cas_sandbox"
    cache = ContentAddressableStorage(base_dir=base_dir)

    evil_ns = "../../escaped_dir"
    with pytest.raises(ValueError, match="Invalid namespace"):
        cache.put_bytes(b"MALICIOUS_PAYLOAD", ".txt", namespace=evil_ns)
```

### 2. `tests/backend/test_adversarial_m1.py`
In `TestCASCacheAdversarial`:
- `test_vulnerability_invalidate_empty_key_wipes_entire_namespace`:
  Wrap `temp_cas.invalidate(namespace, "")` in `with pytest.raises(ValueError, match="Invalid cache_key"):`, and assert `ns_dir.is_dir()`.
- `test_vulnerability_invalidate_empty_namespace_wipes_base_dir`:
  Wrap `temp_cas.invalidate("", "")` in `with pytest.raises(ValueError, match="Invalid namespace"):`, and assert `temp_cas.base_dir.is_dir()`.
- `test_vulnerability_path_traversal_escapes_base_dir`:
  Wrap `temp_cas._get_entry_dir("../../escaped_sandbox", ...)` in `with pytest.raises(ValueError, match="Invalid namespace"):`.
- `test_params_hash_type_error_on_path_object`:
  Replace `with pytest.raises(TypeError)` with:
  ```python
  digest = canonical_params_hash({"source_file": Path("test/model.glb")})
  assert isinstance(digest, str) and len(digest) == 64
  assert digest == canonical_params_hash({"source_file": "test/model.glb"})
  ```
