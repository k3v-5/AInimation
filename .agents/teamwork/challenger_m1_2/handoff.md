# Handoff Report: Challenger 2 - Milestone 1 Empirical Verification

**Agent**: `challenger_m1_2` (EMPIRICAL CHALLENGER / critic & specialist)  
**Target Milestone**: Milestone 1 (`backend/core/`)  
**Verdict**: **`REQUEST_CHANGES`**  

---

## 1. Observation

We created an empirical stress-test suite in `tests/backend/test_challenger_m1_2.py` and executed it via `python -m pytest tests/backend/test_challenger_m1_2.py -v -s`.

### Observation 1: Event & Callback Duplication in `TelemetryBus.emit_threadsafe()`
- **File**: `backend/core/telemetry.py`, lines 246–266 and lines 208–230:
  ```python
  # telemetry.py: emit_threadsafe()
  def emit_threadsafe(self, event: TelemetryEvent) -> None:
      self._history.append(event)          # <-- 1st append
      ...
      self._invoke_callbacks(event)       # <-- 1st callback invocation
      ...
      asyncio.run_coroutine_threadsafe(self.emit(event), loop)

  # telemetry.py: emit()
  async def emit(self, event: TelemetryEvent) -> None:
      self._history.append(event)          # <-- 2nd append
      ...
      self._invoke_callbacks(event)       # <-- 2nd callback invocation
  ```
- **Execution Output**:
  ```text
  FAILED tests/backend/test_challenger_m1_2.py::test_emit_threadsafe_duplicate_emission_with_running_loop
  [DIAGNOSTIC] callback_count: 2, history_count: 2
  AssertionError: BUG CONFIRMED: callback called 2 times for a single emit_threadsafe call!
  assert 2 == 1
  ```
- In concurrent stress testing with 20 threads producing 200 events (`test_emit_threadsafe_heavy_concurrency_with_running_loop`):
  ```text
  [DIAGNOSTIC] Concurrency loop test: emitted=200, queue=200, cb=400, history=400
  AssertionError: Callbacks duplicated: got 400, expected 200
  ```
- Every callback subscriber received exactly 400 calls for 200 emissions, and `_history` stored 400 entries.

### Observation 2: Unhandled Coroutine in Async Callbacks Invoked from Threads
- **File**: `backend/core/telemetry.py`, lines 201–206:
  ```python
  if inspect.isawaitable(result):
      loop = self.get_event_loop()
      if loop is not None and loop.is_running():
          asyncio.create_task(result)  # type: ignore[arg-type]
  except Exception as exc:
      logger.warning("Error executing telemetry callback subscriber: %s", exc)
  ```
- When `_invoke_callbacks()` is called from a background worker thread, `asyncio.create_task()` attempts to fetch the running loop of the *current thread* (`RuntimeError: no running event loop in thread`), causing the exception to be swallowed and the coroutine abandoned.
- **Execution Warning**:
  ```text
  tests/backend/test_challenger_m1_2.py::test_emit_threadsafe_async_callback_from_thread
  RuntimeWarning: coroutine 'test_emit_threadsafe_async_callback_from_thread.<locals>._test.<locals>.async_cb' was never awaited
  ```

### Observation 3: Path Traversal Boundary Escape in `ContentAddressableStorage`
- **File**: `backend/core/cache.py`, lines 144–148:
  ```python
  def _get_entry_dir(self, namespace: str, cache_key: str) -> Path:
      prefix = cache_key[:2]
      suffix = cache_key[2:]
      return self.base_dir / namespace / prefix / suffix
  ```
- When `namespace = "../../escaped_dir"` is passed, `_get_entry_dir` escapes `base_dir`.
- **Execution Output**:
  ```text
  FAILED tests/backend/test_challenger_m1_2.py::test_cas_cache_path_traversal_boundaries
  [DIAGNOSTIC] File resolved to: C:\Users\sasuk\AppData\Local\Temp\pytest-of-sasuk\pytest-417\escaped_dir\60\d86ab71b48f21052540cc5b2cd54caf575de107042ebf3429c6fbd47fd2e1a\asset.txt
  [DIAGNOSTIC] Is outside base_dir: True
  AssertionError: Security boundary breached: path traversal escaped base_dir to ...
  ```
- Furthermore, `cache.invalidate_namespace(namespace)` executes `shutil.rmtree(self.base_dir / namespace)`, which can delete arbitrary directories outside `base_dir`.

### Observation 4: Extensionless Asset Files Ignored by `get_total_size_bytes()`
- **File**: `backend/core/cache.py`, lines 484–490:
  ```python
  def get_total_size_bytes(self) -> int:
      total = 0
      for p in self.base_dir.rglob("asset.*"):
          if p.is_file():
              total += p.stat().st_size
      return total
  ```
- If an ingested file has no extension, the stored file is named `asset`. `rglob("asset.*")` matches only files containing a dot.
- **Execution Output**:
  ```text
  FAILED tests/backend/test_challenger_m1_2.py::test_cas_cache_get_total_size_bytes_without_extension
  [DIAGNOSTIC] get_total_size_bytes for file without extension: 0
  AssertionError: get_total_size_bytes() returned 0, expected 50! rglob('asset.*') skips extensionless files.
  assert 0 == 50
  ```

### Observation 5: Case Sensitivity Crash on `IANIMATION_LOG_LEVEL`
- **File**: `backend/core/config.py`, lines 18 and 58:
  ```python
  LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
  ...
  log_level: LogLevel = Field(default="INFO", ...)
  ```
- When `IANIMATION_LOG_LEVEL="debug"` or `"info"` is set, Pydantic throws a `ValidationError`:
  ```text
  1 validation error for Settings
  log_level
    Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL' [type=literal_error, input_value='debug', input_type=str]
  ```
- Even though `case_sensitive=False` is configured in `SettingsConfigDict`, Pydantic only normalizes environment variable names, not `Literal` values.

---

## 2. Logic Chain

1. **Telemetry Duplication**:
   - `emit_threadsafe` was designed to allow worker threads to publish events. However, it both synchronously updates history/callbacks AND schedules `self.emit()` onto the asyncio event loop.
   - When the event loop executes `self.emit()`, it unconditionally re-appends to `_history` and re-invokes all callbacks.
   - Under heavy concurrency (20 threads, 200 events), every event was recorded and delivered twice (400 total), polluting subscriber streams and corrupting telemetry logs.
   
2. **Async Callback Execution from Background Threads**:
   - `asyncio.create_task` cannot be invoked from a thread without an active event loop for that thread.
   - Calling `emit_threadsafe` with an async callback subscriber causes the coroutine to be dropped without being scheduled on the registered event loop.

3. **Cache Path Traversal**:
   - `ContentAddressableStorage._get_entry_dir` concatenates `namespace` directly into a `Path`.
   - Without validation against relative path components (`..`), arbitrary files can be written and subsequently wiped via `invalidate_namespace` outside the sandbox directory.

4. **Cache Size Discrepancy**:
   - In `put_file()`, extensionless files are stored as `entry_dir / "asset"`.
   - `get_total_size_bytes()` searches for `asset.*`, ignoring `asset`, causing total cache size accounting to report 0 bytes for extensionless artifacts while `prune_lru` reads their `metadata.json` sizes.

5. **Config Usability**:
   - Standard shell and deployment environments often provide `LOG_LEVEL=info` or `LOG_LEVEL=debug` in lowercase. Strict `Literal` matching without a pre-validator causes fatal application initialization crashes.

---

## 3. Caveats

- In single-threaded execution where no asyncio event loop is initialized, `emit_threadsafe()` does not schedule coroutines onto the loop and only dispatches once. However, in any real deployment (FastMCP server, FastAPI/Starlette, or async UI listeners), the event loop is active, making the duplicate dispatch 100% reproducible.
- Live external cloud providers (Fal.ai, Tripo, Replicate) and live Unreal Engine instances were simulated with mock fixtures in compliance with M1 requirements.

---

## 4. Conclusion & Required Changes

Verdict: **`REQUEST_CHANGES`**

The implementation in `backend/core/` is solid in architectural structure and passes basic tests, but has critical concurrency and security boundary bugs that will compromise Milestone 2 (UE5 bridge thread pools) and Milestone 3 (AI worker threads).

### Actionable Remediation Items for Worker:

1. **Fix `TelemetryBus.emit_threadsafe()`**:
   - Avoid double mutation. In `emit_threadsafe`, either:
     - Update history and callbacks ONLY in `emit()` on the loop thread, OR
     - If history must be updated synchronously in `emit_threadsafe`, pass a flag or internal method (e.g. `_broadcast_queues_only(event)`) to the scheduled coroutine so `emit()` does not duplicate history or callbacks.
2. **Fix `_invoke_callbacks()` cross-thread coroutine scheduling**:
   - Replace `asyncio.create_task(result)` with cross-thread safe scheduling:
     ```python
     if inspect.isawaitable(result):
         loop = self.get_event_loop()
         if loop is not None and loop.is_running():
             try:
                 running_loop = asyncio.get_running_loop()
                 if running_loop is loop:
                     loop.create_task(result)
                 else:
                     asyncio.run_coroutine_threadsafe(result, loop)
             except RuntimeError:
                 asyncio.run_coroutine_threadsafe(result, loop)
     ```
3. **Harden `ContentAddressableStorage` against Path Traversal**:
   - Sanitize `namespace` and `cache_key`: disallow path separators or enforce `assert entry_dir.resolve().is_relative_to(self.base_dir.resolve())`.
4. **Fix `ContentAddressableStorage.get_total_size_bytes()`**:
   - Count all asset files regardless of dot extension: iterate through `self.base_dir.rglob("asset*")` or iterate `*/*/*/metadata.json` and sum `metadata.file_size_bytes`.
5. **Add Pre-Validator for `Settings.log_level`**:
   - Add `@field_validator("log_level", mode="before")` that normalizes `v.upper()` so `"info"` or `"debug"` are accepted without runtime errors.
   - Add `ge=1, le=65535` constraints to port fields (`ue5_http_port`, `ue5_ws_port`, `mcp_server_port`).

---

## 5. Verification Method

To verify these findings independently:

```powershell
# 1. Run the empirical stress test suite authored by Challenger 2:
python -m pytest tests/backend/test_challenger_m1_2.py -v -s

# 2. Inspect failing tests demonstrating the exact bugs:
# - test_emit_threadsafe_heavy_concurrency_with_running_loop (duplicate history/callbacks)
# - test_cas_cache_get_total_size_bytes_without_extension (extensionless asset omission)
# - test_cas_cache_path_traversal_boundaries (directory traversal security boundary breach)
```

Invalidation conditions for verdict:
- Worker resolves the 5 remediation items above such that `python -m pytest tests/backend/ -v` and `python -m pytest tests/backend/test_challenger_m1_2.py -v` both pass 100% with 0 failures and 0 warnings.
