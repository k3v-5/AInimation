# Empirical Challenger Report: Milestone 1 (backend/core)

**Verdict**: `REQUEST_CHANGES`

---

## 1. Observation

Adversarial stress-testing of `backend/core/` was performed via empirical execution using the newly authored adversarial suite `tests/backend/test_adversarial_m1.py` and peer challenge suite `tests/backend/test_challenger_m1_2.py`.

### A. TelemetryBus Double Invocation & History Duplication
- **File**: `backend/core/telemetry.py`, lines 221-228 & 252-266
```python
252:        self._history.append(event)
...
259:        self._invoke_callbacks(event)
...
266:        asyncio.run_coroutine_threadsafe(self.emit(event), loop)
```
Inside `self.emit(event)` (lines 221, 228):
```python
221:        self._history.append(event)
...
228:        self._invoke_callbacks(event)
```
- **Execution & Output**:
Running `tests/backend/test_adversarial_m1.py::TestTelemetryBusAdversarial::test_emit_threadsafe_double_invocation_and_history_duplication` and `tests/backend/test_challenger_m1_2.py::test_emit_threadsafe_heavy_concurrency_with_running_loop`:
```
AssertionError: Callbacks duplicated: got 400, expected 200
assert 400 == 200
[DIAGNOSTIC] Concurrency loop test: emitted=200, queue=200, cb=400, history=400
```
When `emit_threadsafe()` is called with an active event loop, the single event is appended to `self._history` TWICE (once in `emit_threadsafe`, once in `emit`), and registered synchronous callbacks are invoked TWICE (once on the caller thread, once on the main asyncio loop thread).

### B. TelemetryBus Async Callbacks Failure on Background Threads
- **File**: `backend/core/telemetry.py`, lines 198-206:
```python
201:                result = callback(event)
202:                if inspect.isawaitable(result):
203:                    loop = self.get_event_loop()
204:                    if loop is not None and loop.is_running():
205:                        asyncio.create_task(result)
```
- **Execution & Output**:
```
WARNING  ianimation.telemetry:telemetry.py:206 Error executing telemetry callback subscriber: no running event loop
RuntimeWarning: coroutine 'test_emit_threadsafe_async_callback_from_thread.<locals>._test.<locals>.async_cb' was never awaited
```
When `emit_threadsafe` runs on a background worker thread, `asyncio.create_task(result)` fails with `RuntimeError: no running event loop` because `create_task()` expects a running loop on the current OS thread. The coroutine is dropped and never awaited.

### C. CAS Cache Empty Key & Short Key Invalidation Deletes Entire Namespaces or Base Directory
- **File**: `backend/core/cache.py`, lines 146-148 & 401-408:
```python
146:        prefix = cache_key[:2]
147:        suffix = cache_key[2:]
148:        return self.base_dir / namespace / prefix / suffix
...
401:        entry_dir = self._get_entry_dir(namespace, cache_key)
402:        if entry_dir.is_dir():
403:            shutil.rmtree(entry_dir, ignore_errors=True)
```
- **Execution & Output**:
Executing `tests/backend/test_adversarial_m1.py::TestCASCacheAdversarial::test_vulnerability_invalidate_empty_key_wipes_entire_namespace`:
```python
cas.put_bytes(b"asset_1", ".txt", "critical_ns", cache_key="1111111111111111111111111111111111111111111111111111111111111111")
cas.put_bytes(b"asset_2", ".txt", "critical_ns", cache_key="2222222222222222222222222222222222222222222222222222222222222222")
cas.invalidate("critical_ns", "")
# Result: ns_dir.is_dir() is False! (All assets in namespace deleted!)
```
And executing `test_vulnerability_invalidate_empty_namespace_wipes_base_dir`:
```python
cas.invalidate("", "") # or cas.invalidate_namespace("")
# Result: cas.base_dir.is_dir() is False! (Entire cache storage directory wiped from disk!)
```
When `cache_key` is <= 2 characters, `suffix` is empty. `Path("base") / "ns" / "" / ""` resolves to `base/ns`. `shutil.rmtree` recursively destroys the entire namespace or prefix bucket. If `namespace` is empty, it deletes `self.base_dir`.

### D. CAS Cache Path Traversal Escapes `base_dir` Sandbox
- **File**: `backend/core/cache.py`, line 148:
- **Execution & Output**:
```
tests/backend/test_challenger_m1_2.py::test_cas_cache_path_traversal_boundaries
AssertionError: Security boundary breached: path traversal escaped base_dir to C:\Users\sasuk\AppData\Local\Temp\pytest-of-sasuk\pytest-419\escaped_dir\60\d86ab71b48f21052540cc5b2cd54caf575de107042ebf3429c6fbd47fd2e1a\asset.txt
assert not True
```
Passing `namespace="../../escaped_dir"` allows assets to be written and deleted outside the configured `base_dir` sandbox.

### E. CAS Cache `get_total_size_bytes()` Omits Extensionless Files
- **File**: `backend/core/cache.py`, line 486:
```python
486:        for p in self.base_dir.rglob("asset.*"):
```
- **Execution & Output**:
```
tests/backend/test_challenger_m1_2.py::test_cas_cache_get_total_size_bytes_without_extension
AssertionError: get_total_size_bytes() returned 0, expected 50! rglob('asset.*') skips extensionless files.
assert 0 == 50
```
Files stored without an extension are named `asset`. `rglob("asset.*")` matches only filenames with a dot, ignoring extensionless files and skewing cache size/quota calculations.

### F. CAS Cache `canonical_params_hash` Crashes on `Path` Objects
- **File**: `backend/core/cache.py`, line 99:
```python
99:        serialized = json.dumps(params, sort_keys=True, separators=(",", ":"))
```
- **Execution & Output**:
```python
canonical_params_hash({"source": Path("audio.wav")})
# TypeError: Object of type WindowsPath is not JSON serializable
```

---

## 2. Logic Chain

1. **TelemetryBus Concurrency & Thread-Safety**:
   - As observed in Section 1.A, `emit_threadsafe()` is designed to bridge synchronous worker threads to the asyncio event loop.
   - However, `emit_threadsafe()` modifies `self._history` and invokes callbacks synchronously, and then schedules `self.emit()` onto the loop via `run_coroutine_threadsafe()`.
   - `self.emit()` unconditionally appends to `self._history` and invokes callbacks again.
   - Therefore, every synchronous emission causes 2x history growth and 2x callback invocations across two different threads. This will cause downstream bugs in UI event listeners, progress counters, and telemetry monitors in M4/M5.
   - Furthermore, as observed in Section 1.B, `_invoke_callbacks` attempts `asyncio.create_task(result)` on whichever thread triggered the callback. On non-event-loop worker threads, this raises `RuntimeError` and drops the coroutine unawaited.

2. **CAS Cache Security and Integrity**:
   - As observed in Section 1.C, `_get_entry_dir()` lacks input validation on `namespace` and `cache_key`.
   - When a caller issues `invalidate(ns, "")` or `invalidate(ns, "ab")`, the resolved directory is the parent namespace or prefix folder. Calling `shutil.rmtree` on this resolved path deletes all sibling assets in that bucket or namespace.
   - If `invalidate("", "")` or `invalidate_namespace("")` is invoked, `entry_dir` is `self.base_dir`, resulting in the deletion of the entire cache base folder.
   - As observed in Section 1.D, absence of path normalization and prefix checks (`resolved.is_relative_to(self.base_dir)`) allows path traversal attacks.

3. **Domain Models & Model Validation**:
   - Pydantic models in `backend/core/models.py` were rigorously tested in `tests/backend/test_adversarial_m1.py` (Tests 1-8).
   - Extra field injection on `StrictBaseModel` is properly rejected.
   - Numerical bounds (`ColorRGB`, `AudioAnalysisRequest`, `CameraKeyframe`, `MovieRenderQueueJobConfig`) are strictly enforced.
   - Polymorphic dispatch in `TelemetryEvent.model_validate` correctly delegates to `ProgressEvent`, `PlanProposalEvent`, `AssetReadyEvent`, and `LogEvent`.
   - The domain models are sound; the defects are concentrated in `telemetry.py` and `cache.py`.

---

## 3. Caveats

- FastMCP live server endpoints (`sse` and `stdio`) were tested via simulated contexts, as the full FastMCP server is scheduled for implementation in Milestone 4.
- Unreal Engine 5 live socket connections were tested via synthetic structures, as the UE5 client/mock server is scheduled for Milestone 2.

---

## 4. Conclusion

Milestone 1 domain models (`backend/core/models.py`) and central configuration (`backend/core/config.py`) are robust, well-typed, and satisfy Zero-Any requirements.

However, **CRITICAL** data-loss and security defects exist in `backend/core/cache.py`, and **HIGH** concurrency defects exist in `backend/core/telemetry.py`.

### Required Fixes for Approval:

1. **`backend/core/cache.py`**:
   - Validate `namespace` and `cache_key` in `_get_entry_dir()`, `put()`, `get()`, `invalidate()`, and `invalidate_namespace()`:
     - Require non-empty strings.
     - Reject path traversal characters (`..`, `/`, `\`).
     - Require `cache_key` to have minimum length (e.g., valid hex SHA-256 string, len == 64).
     - Guard `invalidate()`: ensure `entry_dir != self.base_dir` and `entry_dir != self.base_dir / namespace`.
     - Guard `invalidate_namespace()`: ensure `ns_dir != self.base_dir`.
   - Fix `get_total_size_bytes()`: match both `asset` and `asset.*` (e.g. check `p.name.startswith("asset")`).
   - Fix `canonical_params_hash()`: serialize `Path` objects (e.g., `default=str` in `json.dumps`).

2. **`backend/core/telemetry.py`**:
   - Prevent double invocation in `emit_threadsafe()`:
     - When `loop` is active and running, delegate history appending and callback invocation to `self.emit()` on the loop, OR pass an internal flag `_from_threadsafe=True` to `emit()` so it does not append to history or invoke sync callbacks a second time.
   - Fix async callback execution from worker threads:
     - In `_invoke_callbacks()`, check if the current thread is the loop thread. If not, schedule awaitable results via `asyncio.run_coroutine_threadsafe(result, loop)`.

---

## 5. Verification Method

To independently reproduce all findings and verify the subsequent fixes:

```powershell
# 1. Run Challenger 1 adversarial suite:
python -m pytest tests/backend/test_adversarial_m1.py -v

# 2. Run Challenger 2 concurrency & security suite:
python -m pytest tests/backend/test_challenger_m1_2.py -v

# 3. Run all backend tests:
python -m pytest tests/backend/ -v
```

Invalidation conditions for verdict:
- `test_emit_threadsafe_heavy_concurrency_with_running_loop` passes with exactly 1 callback per emitted event.
- `test_cas_cache_path_traversal_boundaries` passes (path traversal rejected with `ValueError`).
- `test_cas_cache_get_total_size_bytes_without_extension` passes.
- Invalidation with empty key/namespace raises `ValueError` rather than deleting directories.
