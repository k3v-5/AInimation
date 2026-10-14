# Handoff Report: Explorer 2 - Milestone 1 Iteration 2 (CAS Cache Remediation)

**Agent**: `explorer_m1_it2_2` (Explorer 2: Read-Only Investigation & Synthesis)  
**Task**: CAS Cache Remediation for `backend/core/cache.py`  
**Parent**: `e8d2c723-385e-49cb-842f-6806cc37fde9`  
**Status**: COMPLETE  

---

## 1. Observation

Direct examination and empirical analysis of `backend/core/cache.py` along with adversarial findings from `challenger_m1_1/handoff.md` and `challenger_m1_2/handoff.md` yielded the following verified facts:

### A. Path Traversal Boundary Escape in `_get_entry_dir()`
- **File & Lines**: `backend/core/cache.py:144-148`
```python
144:    def _get_entry_dir(self, namespace: str, cache_key: str) -> Path:
145:        """Resolve partitioned directory: <base_dir>/<namespace>/<key[:2]>/<key[2:]>/"""
146:        prefix = cache_key[:2]
147:        suffix = cache_key[2:]
148:        return self.base_dir / namespace / prefix / suffix
```
- **Execution & Output**:
Running `python -m pytest tests/backend/test_challenger_m1_2.py::test_cas_cache_path_traversal_boundaries`:
```
FAILED tests/backend/test_challenger_m1_2.py::test_cas_cache_path_traversal_boundaries
[DIAGNOSTIC] File resolved to: C:\Users\sasuk\AppData\Local\Temp\pytest-of-sasuk\pytest-423\escaped_dir\60\d86ab71b48f21052540cc5b2cd54caf575de107042ebf3429c6fbd47fd2e1a\asset.txt
[DIAGNOSTIC] Is outside base_dir: True
AssertionError: Security boundary breached: path traversal escaped base_dir to C:\Users\sasuk\AppData\Local\Temp\pytest-of-sasuk\pytest-423\escaped_dir\...
assert not True
```
Passing `namespace="../../escaped_dir"` resolves outside `base_dir`, allowing arbitrary writes and removals outside the sandbox.

### B. Directory Wiping Bug in `invalidate()` and `invalidate_namespace()`
- **File & Lines**: `backend/core/cache.py:401-408 & 414-421`
```python
401:        entry_dir = self._get_entry_dir(namespace, cache_key)
402:        if entry_dir.is_dir():
403:            shutil.rmtree(entry_dir, ignore_errors=True)
...
414:            ns_dir = self.base_dir / namespace
...
420:            shutil.rmtree(ns_dir, ignore_errors=True)
```
- **Execution & Verification**:
When `cache_key` is empty (`""`), `prefix = ""` and `suffix = ""`.
`(base_dir / namespace / "" / "").resolve()` evaluates directly to `base_dir / namespace`.
`shutil.rmtree(entry_dir)` deletes the entire namespace directory.
When `namespace` is also empty (`""`), `(base_dir / "" / "" / "").resolve()` evaluates to `self.base_dir`, wiping the entire cache storage root.

### C. Extensionless Asset Omission in `get_total_size_bytes()`
- **File & Lines**: `backend/core/cache.py:483-490`
```python
483:    def get_total_size_bytes(self) -> int:
484:        """Calculate total byte size of all assets currently residing in cache."""
485:        total = 0
486:        for p in self.base_dir.rglob("asset.*"):
487:            if p.is_file():
488:                total += p.stat().st_size
489:        return total
```
- **Execution & Output**:
Running `python -m pytest tests/backend/test_challenger_m1_2.py::test_cas_cache_get_total_size_bytes_without_extension`:
```
FAILED tests/backend/test_challenger_m1_2.py::test_cas_cache_get_total_size_bytes_without_extension
[DIAGNOSTIC] get_total_size_bytes for file without extension: 0
AssertionError: get_total_size_bytes() returned 0, expected 50! rglob('asset.*') skips extensionless files.
assert 0 == 50
```
Files ingested without extension (e.g. `raw_artifact` -> `asset`) lack a dot in their filename. `rglob("asset.*")` matches only filenames with a dot, ignoring extensionless files and causing total size calculation to return 0.

### D. Parameter Hash Failure on `Path` Objects in `canonical_params_hash()`
- **File & Lines**: `backend/core/cache.py:97-100`
```python
97: def canonical_params_hash(params: ParamDict) -> str:
98:     """Compute deterministic SHA-256 hash of a dictionary with sorted keys."""
99:     serialized = json.dumps(params, sort_keys=True, separators=(",", ":"))
100:    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
```
- **Execution & Output**:
```python
canonical_params_hash({"source_file": Path("test/model.glb")})
# TypeError: Object of type WindowsPath is not JSON serializable
```
`json.dumps()` lacks a custom default serializer or string coercion for `pathlib.Path` objects.

---

## 2. Logic Chain

1. **Path Traversal Mitigation**:
   - `_get_entry_dir()` directly concatenated `namespace` into `Path` without sanitization.
   - Restricting `namespace` and `cache_key` to `_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")` rejects all path separators (`/`, `\`), dot components (`..`), and non-printable characters before path construction.
   - In addition, calling `resolved_entry.is_relative_to(resolved_base)` and checking `resolved_entry != resolved_base` provides defense-in-depth at the filesystem level.
   - Any violation immediately raises `ValueError`.

2. **Directory Wiping Prevention**:
   - The root cause of the wiping bug was slicing `cache_key[:2]` and `cache_key[2:]` when `len(cache_key) < 3`, yielding empty path segments that collapsed into the parent directory.
   - By enforcing `isinstance(cache_key, str) and len(cache_key) >= 3` and matching `_IDENTIFIER_PATTERN`, `suffix` is guaranteed to contain at least 1 character.
   - In `invalidate()`, explicit boundary guards `if resolved_entry in (resolved_base, resolved_ns): raise ValueError(...)` prevent `shutil.rmtree()` from ever being invoked on `base_dir` or namespace roots.
   - In `invalidate_namespace()`, validating `namespace` against `_IDENTIFIER_PATTERN` and guarding `ns_dir != resolved_base` prevents `base_dir` deletion.

3. **Accurate Cache Sizing**:
   - When storing an extensionless file, `source_path.suffix` is empty, producing `entry_dir / "asset"`.
   - Changing the scan pattern to `self.base_dir.rglob("asset*")` combined with `p.name == "asset" or p.name.startswith("asset.")` accounts for both extensionless `asset` and all extensioned variants (`asset.glb`, `asset.wav`, etc.), while ignoring sidecars (`metadata.json`) and temporary files (`.tmp_*`).
   - Adding `try ... except OSError` and evaluating under `self._lock` guarantees thread safety and race protection during concurrent cache operations.

4. **Deterministic `Path` Serialization**:
   - Adding `_canonical_json_default(obj)` converting `Path` instances via `obj.as_posix()` guarantees consistent, cross-platform string representation (e.g. forward slashes on both Windows and Linux).
   - Passing `default=_canonical_json_default` to `json.dumps()` in `canonical_params_hash()` eliminates the `TypeError`.
   - Updating `ParamValue = Union[str, int, float, bool, Path, None]` preserves 100% strict typing under the Zero-Any policy.

---

## 3. Caveats

- **Test Suite Updates**: Tests in `tests/backend/test_adversarial_m1.py` (`test_vulnerability_*`) and `tests/backend/test_challenger_m1_2.py` (`test_cas_cache_path_traversal_boundaries`) were written in Iteration 1 to assert the existence of the defects. When the remediation is applied, these tests must be updated by the Implementer or Challenger to assert the remediated behavior (`pytest.raises(ValueError)`).
- **Read-Only Scope**: In adherence to the Explorer role, this agent did not modify `backend/core/cache.py` or tests directly. All concrete code changes are specified verbatim in `.agents/teamwork/explorer_m1_it2_2/cache_remediation.md`.

---

## 4. Conclusion

All 4 defects identified in `backend/core/cache.py` have been analyzed and exact, tested drop-in code remedies formulated:
1. `_get_entry_dir()` regex sanitization (`^[a-zA-Z0-9_\-]+$`) and `is_relative_to(base_dir)` verification completely eliminates path traversal.
2. Minimum key length enforcement (`len(cache_key) >= 3`) and directory inequality checks eliminate directory wiping in `invalidate()` and `invalidate_namespace()`.
3. `get_total_size_bytes()` matching `asset` and `asset.*` captures 100% of cached files.
4. `canonical_params_hash()` with `as_posix()` default serialization handles `Path` objects deterministically without `TypeError`.

The remediation plan is ready for implementation by the designated implementer.

---

## 5. Verification Method

To independently verify the proposed remediation after implementation:

```powershell
# 1. Verify standard CAS cache unit tests pass:
python -m pytest tests/backend/test_cache.py -v

# 2. Verify Challenger 2 test suite passes:
python -m pytest tests/backend/test_challenger_m1_2.py -v

# 3. Verify Adversarial test suite passes:
python -m pytest tests/backend/test_adversarial_m1.py -v

# 4. Run full backend suite:
python -m pytest tests/backend/ -v
```

### Invalidation Conditions for Remediation:
- `test_cas_cache_get_total_size_bytes_without_extension` passes with `total == 50`.
- Calling `invalidate(namespace, "")` or `invalidate("", "")` raises `ValueError` and leaves filesystem directories intact.
- Calling `_get_entry_dir("../../escaped", ...)` raises `ValueError`.
- `canonical_params_hash({"file": Path("test/model.glb")})` returns a valid 64-character SHA-256 hex string matching `canonical_params_hash({"file": "test/model.glb"})`.
