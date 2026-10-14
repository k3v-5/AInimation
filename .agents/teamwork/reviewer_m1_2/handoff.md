# Handoff Report: Milestone 1 Adversarial Review

**Reviewer**: Reviewer 2 / Adversarial Critic  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\reviewer_m1_2`  
**Target Codebase**: `backend/core/` and `tests/backend/`  
**Verdict**: **`REQUEST_CHANGES`**

---

## 1. Observation

### 1.1 Baseline Test Verification

- **Command 1**: `python -m pytest tests/backend/test_models.py tests/backend/test_telemetry.py tests/backend/test_config.py tests/backend/test_cache.py -v`
  - Output: `40 passed in 2.47s` (100% pass rate).
  - All 16 model tests, 8 telemetry tests, 5 config tests, and 11 cache tests pass under nominal conditions.

- **Command 2**: `python -m tests.e2e.runner --tier 1`
  - Output: `8 passed, 33 skipped in 1.60s`.
  - Result: `STATUS: SUCCESS - All active tests passed, pending tests marked. Features In Scope: 41, Covered Features: 41 (100.0%)`.

- **Command 3**: `python -m pytest tests/e2e/ -v`
  - Output: `10 passed, 48 skipped in 2.22s`.

- **Integrity & Zero-Any Check**:
  - `grep_search` across `backend/core/` for `\bAny\b`: 0 type annotations found using `Any` (only docstring references to "Zero-Any policy").
  - AST inspection: Zero facade returns (`pass`, `return True`, static stubs). All implementations contain genuine business logic.

---

### 1.2 Adversarial Stress Test Findings & Reproductions

When subjecting `backend/core/` to adversarial concurrency, multi-threaded emission, and boundary stress tests, 4 tests failed in `tests/backend/`:

#### Observation O-1: Double Emission & Duplicate History in `emit_threadsafe`
- **File & Line**: `backend/core/telemetry.py:252-267`
- **Verbatim Code**:
  ```python
  def emit_threadsafe(self, event: TelemetryEvent) -> None:
      # Update history and latest caches synchronously
      self._history.append(event)
      if isinstance(event, ProgressEvent):
          self._latest_progress = event
      elif isinstance(event, PlanProposalEvent):
          self._latest_plan = event

      # Always invoke sync callbacks immediately
      self._invoke_callbacks(event)

      loop = self.get_event_loop()
      if loop is None or not loop.is_running():
          logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")
          return

      asyncio.run_coroutine_threadsafe(self.emit(event), loop)
  ```
- **Observed Behavior**:
  When `emit_threadsafe` is called while an event loop is running, it appends to `_history` and calls `_invoke_callbacks(event)` synchronously. Then `asyncio.run_coroutine_threadsafe(self.emit(event), loop)` runs `emit(event)` on the loop thread, which executes lines 221 and 228 of `telemetry.py`:
  ```python
  self._history.append(event)  # DUPLICATE!
  ...
  self._invoke_callbacks(event)  # DUPLICATE!
  ```
- **Reproduction**:
  ```powershell
  python -c "import asyncio; from backend.core.telemetry import TelemetryBus, ProgressEvent;
  async def main():
      bus = TelemetryBus()
      bus.set_event_loop(asyncio.get_running_loop())
      events = []
      bus.subscribe(lambda e: events.append(e))
      bus.emit_threadsafe(ProgressEvent(stage='test', percentage=50, message='hi'))
      await asyncio.sleep(0.05)
      print('Callback count:', len(events))
      print('History count:', len(bus.get_history()))
  asyncio.run(main())"
  ```
  - Result:
    ```
    Callback count: 2
    History count: 2
    ```
    (Expected 1 callback, 1 history item; received 2 callbacks and 2 history items).
  - In `test_challenger_m1_2.py::test_emit_threadsafe_heavy_concurrency_with_running_loop`:
    ```
    [DIAGNOSTIC] Concurrency loop test: emitted=200, queue=200, cb=400, history=400
    AssertionError: Callbacks duplicated: got 400, expected 200
    ```

---

#### Observation O-2: Worker Thread Async Callback Crash & Coroutine Leak
- **File & Line**: `backend/core/telemetry.py:201-204`
- **Verbatim Code**:
  ```python
  if inspect.isawaitable(result):
      loop = self.get_event_loop()
      if loop is not None and loop.is_running():
          asyncio.create_task(result)
  ```
- **Observed Behavior**:
  `asyncio.create_task` operates strictly on the running loop of the *current calling thread*. If `emit_threadsafe` invokes `_invoke_callbacks` from a background worker thread, `asyncio.create_task` raises `RuntimeError: no running event loop`. The error is swallowed in `except Exception`, and the coroutine object is leaked unawaited.
- **Reproduction**:
  ```powershell
  python -c "import asyncio, threading; from backend.core.telemetry import TelemetryBus, ProgressEvent;
  async def main():
      bus = TelemetryBus()
      bus.set_event_loop(asyncio.get_running_loop())
      async def async_cb(e): pass
      bus.subscribe(async_cb)
      def worker(): bus.emit_threadsafe(ProgressEvent(stage='test', percentage=50, message='hi'))
      t = threading.Thread(target=worker); t.start(); t.join()
  asyncio.run(main())"
  ```
  - Verbatim Output:
    ```
    WARNING:ianimation.telemetry:Error executing telemetry callback subscriber: no running event loop
    RuntimeWarning: coroutine 'async_cb' was never awaited
    ```

---

#### Observation O-3: `TelemetryBus.emit` Lacks Cooperative Yielding (Event Loop Starvation)
- **File & Line**: `backend/core/telemetry.py:208-245`
- **Observed Behavior**:
  `bus.emit` is defined as `async def emit(self, event: TelemetryEvent) -> None:`, but contains zero `await` statements. When a producer emits multiple events in a loop, it runs synchronously without yielding control to the asyncio event loop.
- **Test Failure**:
  In `tests/backend/test_adversarial_m1.py::TestTelemetryBusAdversarial::test_rapid_emission_high_concurrency`:
  - 10 async producers emitted 500 events each (total 5,000 events) into 5 queues with `maxsize=3000`.
  - Because `emit` never yielded control, producers starved consumer tasks until queues filled up.
  - The drop policy kicked in and dropped 2,000 events.
  - Result:
    ```
    AssertionError: Consumer 0 received 3000/5000
    assert 3000 == 5000
    ```

---

#### Observation O-4: CAS Cache Path Traversal via Unsanitized `namespace`
- **File & Line**: `backend/core/cache.py:144-149`
- **Verbatim Code**:
  ```python
  def _get_entry_dir(self, namespace: str, cache_key: str) -> Path:
      prefix = cache_key[:2]
      suffix = cache_key[2:]
      return self.base_dir / namespace / prefix / suffix
  ```
- **Observed Behavior**:
  When `namespace` contains directory traversal sequences (e.g. `../../escaped_dir`), the target file resolves outside `base_dir`.
- **Test Failure**:
  In `tests/backend/test_challenger_m1_2.py::test_cas_cache_path_traversal_boundaries`:
  ```
  [DIAGNOSTIC] File resolved to: C:\Users\sasuk\AppData\Local\Temp\pytest-of-sasuk\pytest-418\escaped_dir\60\d86ab...\asset.txt
  [DIAGNOSTIC] Is outside base_dir: True
  AssertionError: Security boundary breached: path traversal escaped base_dir
  ```

---

#### Observation O-5: CAS Cache `get_total_size_bytes` Misses Extensionless Assets
- **File & Line**: `backend/core/cache.py:486-489`
- **Verbatim Code**:
  ```python
  def get_total_size_bytes(self) -> int:
      total = 0
      for p in self.base_dir.rglob("asset.*"):
          if p.is_file():
              total += p.stat().st_size
      return total
  ```
- **Observed Behavior**:
  `rglob("asset.*")` matches `asset.<ext>`, but fails to match files with no extension named `asset` (e.g. raw binary blobs).
- **Test Failure**:
  In `tests/backend/test_challenger_m1_2.py::test_cas_cache_get_total_size_bytes_without_extension`:
  ```
  AssertionError: get_total_size_bytes() returned 0, expected 50! rglob('asset.*') skips extensionless files.
  assert 0 == 50
  ```

---

#### Observation O-6: `put_file` Default Key Derivation Conflates Output with Input Hashes
- **File & Line**: `backend/core/cache.py:180-181`
- **Observed Behavior**:
  In `put_file`, if `cache_key` is omitted, it hashes `source_path` (the generated output asset). However, `get_by_inputs` queries using `hash_file(input_file_paths)`. Consequently, queries using `get_by_inputs` for cached output assets will always miss unless the caller manually calculates `cache_key` beforehand and supplies it to `put_file`.

---

## 2. Logic Chain

1. **Integrity Mode Derivation**:
   - `ORIGINAL_REQUEST.md` specifies `Integrity mode: demo`.
   - AST inspection of `backend/core/` verified zero facade methods, zero hardcoded test returns, and 100% Zero-Any strict typing compliance. The code is genuine and uncheated.

2. **Concurrency Analysis & Blast Radius**:
   - Observations O-1 and O-2 demonstrate that `TelemetryBus.emit_threadsafe` is flawed when bridging between synchronous worker threads and the main asyncio event loop.
   - In Milestone 2 (`backend/ue5/`) and Milestone 3 (`backend/ai/`), long-running operations (such as Demucs audio stem separation, ComfyUI generation, and UE5 Movie Render Queue monitoring) will run in background threads and invoke `emit_progress_sync` / `emit_threadsafe`.
   - Under current logic, every threadsafe progress update will duplicate callbacks and double-record history when the event loop is active, and will crash/leak if any UI WebSocket or FastMCP subscriber registers an asynchronous callback handler.
   - This poses a direct stability risk to Milestones 2, 3, and 4.

3. **Storage Boundary Analysis**:
   - Observations O-4 and O-5 demonstrate that `ContentAddressableStorage` in `cache.py` lacks path sanitization and extensionless file handling.
   - If user-provided namespace strings or extensionless files are stored, path traversal can occur or disk quotas will be miscalculated.

4. **Verdict Deduction**:
   - Because these defects are concrete, reproducible, and directly affect downstream milestone consumers, approving without fixes would allow concurrency bugs into the foundation.
   - Therefore, the verdict is **`REQUEST_CHANGES`**.

---

## 3. Caveats

- **No Integrity Violation**: This is NOT an integrity violation rejection. The implementation is authentic, well-structured, follows SOLID principles, and satisfies the Zero-Any policy.
- **Baseline Test Pass**: All 40 standard unit tests pass because current baseline tests only test `emit_threadsafe` when no event loop is running, or with synchronous callbacks on the main thread. The bugs manifest under concurrent multi-threaded execution with an active event loop.
- **Implementation Scope**: Per the reviewer constraint ("Review-only — do NOT modify implementation code"), we have documented exact lines, failure proofs, and recommended fixes for Worker M1 to apply.

---

## 4. Conclusion & Required Changes

**Verdict**: **`REQUEST_CHANGES`**

### Actionable Fixes Required for Worker M1:

1. **Fix `backend/core/telemetry.py:246-267` (`emit_threadsafe`)**:
   - If an active event loop is detected and running, `emit_threadsafe` should delegate dispatch to `asyncio.run_coroutine_threadsafe(self.emit(event), loop)`.
   - It should NOT call `self._history.append` and `self._invoke_callbacks` synchronously *before* scheduling `self.emit(event)`, because `self.emit(event)` repeats both operations when it executes on the loop.
   - Alternatively, pass an internal parameter `_from_threadsafe=True` to `emit` to prevent duplicate history and callback execution.

2. **Fix `backend/core/telemetry.py:201-204` (`_invoke_callbacks`)**:
   - If an awaitable result is returned by an async callback, check if the current thread is the loop thread.
   - If on the loop thread: `loop.create_task(result)`.
   - If on a foreign worker thread: `asyncio.run_coroutine_threadsafe(result, loop)`.

3. **Fix `backend/core/cache.py:144-149` (`_get_entry_dir`)**:
   - Sanitize `namespace` and `cache_key` to prevent path traversal (e.g. `assert ".." not in namespace` and ensure `resolved_path.is_relative_to(self.base_dir)`).

4. **Fix `backend/core/cache.py:486-489` (`get_total_size_bytes`)**:
   - Change pattern matching from `self.base_dir.rglob("asset.*")` to inspect all asset files (e.g. `p.name.startswith("asset")` or `rglob("asset*")`).

5. **Fix `backend/core/telemetry.py:141` (`subscribe` return type)**:
   - Change return type annotation from `AsyncIterator[...]` to `AsyncContextManager[asyncio.Queue[TelemetryEvent]]` to accurately reflect `@asynccontextmanager`.

---

## 5. Verification Method

Once Worker M1 applies the changes, verify resolution using:

```powershell
# 1. Run baseline unit tests
python -m pytest tests/backend/test_models.py tests/backend/test_telemetry.py tests/backend/test_config.py tests/backend/test_cache.py -v

# 2. Run adversarial stress tests to confirm all 4 concurrency & boundary failures are resolved
python -m pytest tests/backend/test_adversarial_m1.py tests/backend/test_challenger_m1_2.py -v

# 3. Run E2E feature verification
python -m tests.e2e.runner --tier 1
```

**Invalidation Conditions**:
- Any test failure in `tests/backend/`
- Any failure in `tests.e2e.runner --tier 1`
- Any duplication of callbacks or history in `emit_threadsafe`
- Any path traversal escape in `CASCache`
