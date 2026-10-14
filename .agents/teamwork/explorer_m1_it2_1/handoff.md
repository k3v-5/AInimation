# Handoff Report: Explorer 1 - Milestone 1 Iteration 2 (Telemetry Remediation)

**Agent**: `explorer_m1_it2_1` (Explorer / Investigator & Synthesizer)  
**Parent Agent**: `e8d2c723-385e-49cb-842f-6806cc37fde9`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m1_it2_1`  
**Target Codebase**: `backend/core/telemetry.py`  
**Type**: Hard Handoff (Investigation & Remediation Formulation Complete)

---

## 1. Observation

### 1.1 Direct Observation of Issue 1: Event Duplication in `emit_threadsafe()`
- **File & Lines**: `backend/core/telemetry.py:246-267` and `220-229`
- **Verbatim Code**:
  ```python
  # telemetry.py: emit_threadsafe()
  def emit_threadsafe(self, event: TelemetryEvent) -> None:
      self._history.append(event)          # <-- 1st append
      if isinstance(event, ProgressEvent):
          self._latest_progress = event
      elif isinstance(event, PlanProposalEvent):
          self._latest_plan = event

      self._invoke_callbacks(event)       # <-- 1st callback invocation

      loop = self.get_event_loop()
      if loop is None or not loop.is_running():
          logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")
          return

      asyncio.run_coroutine_threadsafe(self.emit(event), loop)

  # telemetry.py: emit()
  async def emit(self, event: TelemetryEvent) -> None:
      self._history.append(event)          # <-- 2nd append
      if isinstance(event, ProgressEvent):
          self._latest_progress = event
      elif isinstance(event, PlanProposalEvent):
          self._latest_plan = event

      self._invoke_callbacks(event)       # <-- 2nd callback invocation
  ```
- **Reproduction Command**:
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
- **Verbatim Output**:
  ```
  Callback count: 2
  History count: 2
  ```
- **Observed Test Failure**:
  In `tests/backend/test_challenger_m1_2.py::test_emit_threadsafe_heavy_concurrency_with_running_loop`:
  ```
  [DIAGNOSTIC] Concurrency loop test: emitted=200, queue=200, cb=400, history=400
  AssertionError: Callbacks duplicated: got 400, expected 200
  ```

### 1.2 Direct Observation of Issue 2: Background Thread Async Callback Crash & Coroutine Leak
- **File & Lines**: `backend/core/telemetry.py:201-206`
- **Verbatim Code**:
  ```python
  if inspect.isawaitable(result):
      loop = self.get_event_loop()
      if loop is not None and loop.is_running():
          asyncio.create_task(result)  # type: ignore[arg-type]
  except Exception as exc:
      logger.warning("Error executing telemetry callback subscriber: %s", exc)
  ```
- **Reproduction Command**:
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
- **Verbatim Output**:
  ```
  Error executing telemetry callback subscriber: no running event loop
  E:\Disco F\Dev\IANIMATION\backend\core\telemetry.py:259: RuntimeWarning: coroutine 'main.<locals>.async_cb' was never awaited
    self._invoke_callbacks(event)
  RuntimeWarning: Enable tracemalloc to get the object allocation traceback
  ```

### 1.3 Direct Observation of Issue 3: Inaccurate Return Type on `subscribe()`
- **File & Line**: `backend/core/telemetry.py:141`
- **Verbatim Code**:
  ```python
  def subscribe(
      self,
      callback_or_replay: Union[TelemetryEventCallback, bool] = True,
      replay_history: bool = True,
      max_queue_size: Optional[int] = None,
  ) -> Union[AsyncIterator[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
  ```
- **Observation**: Calling `bus.subscribe()` in context-manager mode returns `self._subscribe_context_manager()`, which is an `@asynccontextmanager` function producing an `AsyncContextManager[asyncio.Queue[TelemetryEvent]]`, not an `AsyncIterator`.

---

## 2. Logic Chain

1. **Step 1 (Duplication Cause)**:
   - In `emit_threadsafe()`, lines 252–259 append to `self._history` and invoke `self._invoke_callbacks(event)` synchronously on the worker thread.
   - Line 266 then schedules `self.emit(event)` onto the event loop via `asyncio.run_coroutine_threadsafe()`.
   - When the event loop executes `self.emit(event)`, lines 221 and 228 repeat both operations (`self._history.append` and `self._invoke_callbacks`).
   - Consequently, every event emitted via `emit_threadsafe()` is recorded and called twice.

2. **Step 2 (Duplication Remediation Deduction)**:
   - When an active event loop is running (`loop is not None and loop.is_running()`), `emit_threadsafe()` must solely delegate to `asyncio.run_coroutine_threadsafe(self.emit(event), loop)` and return immediately.
   - It must NOT modify `_history` or invoke callbacks beforehand on the worker thread.
   - All state mutations (`_history`, `_latest_progress`, `_latest_plan`), callback invocations, and queue broadcasting will occur exactly once inside `emit(event)` on the loop thread.
   - When no event loop is running, the synchronous fallback executes once.

3. **Step 3 (Cross-Thread Async Callback Cause)**:
   - `asyncio.create_task()` requires a running event loop on the current OS thread.
   - Worker threads spawned by `threading.Thread` or `ThreadPoolExecutor` do not have a default running asyncio event loop.
   - Therefore, calling `asyncio.create_task()` on a worker thread raises `RuntimeError: no running event loop in thread`.
   - The exception is swallowed in `except Exception`, leaving the coroutine unawaited and causing a memory leak and runtime warning.

4. **Step 4 (Cross-Thread Async Callback Remediation Deduction)**:
   - When a callback returns an awaitable, check if `loop` is active and running.
   - If `current_loop is loop` (calling thread is the event loop thread), schedule with `loop.create_task(coro)`.
   - If calling thread is a background worker thread, schedule with `asyncio.run_coroutine_threadsafe(coro, loop)`.
   - Wrap the awaitable in `_wrap_awaitable(awaitable)` so any exception inside the async callback is caught and logged.
   - If no event loop is running, log a warning and call `result.close()` if `inspect.iscoroutine(result)` to prevent unawaited coroutine warnings.

5. **Step 5 (Empirical Verification of Formulated Fix)**:
   - We implemented the formulated logic in `proposed_telemetry.py` and validated it against all 8 baseline unit tests and all 4 challenger concurrency tests.
   - Output: 8/8 baseline tests PASSED; 4/4 challenger tests PASSED with 0 duplicate callbacks and 0 unawaited coroutine warnings.

---

## 3. Caveats

1. **Read-Only Explorer Constraint**: As Explorer, this agent did not modify `backend/core/telemetry.py` directly. Instead, full artifacts were produced:
   - Unified diff patch: `telemetry.patch`
   - Production drop-in replacement: `proposed_telemetry.py`
   - Detailed remediation guide: `telemetry_remediation.md`
2. **`test_adversarial_m1.py` Assertion Inversion**:
   In `tests/backend/test_adversarial_m1.py:538`, Challenger in Iteration 1 wrote `assert call_count == 2` to demonstrate the bug. Once Worker applies the fix, that test will fail until Worker updates lines 538 and 544 to assert single invocation (`assert call_count == 1` and `assert len(history) == 1`).
3. **`test_challenger_m1_2.py` Missing `asyncio.run`**:
   In `tests/backend/test_challenger_m1_2.py:154`, the test `test_emit_threadsafe_duplicate_emission_with_running_loop` defined `async def _test()` but omitted `asyncio.run(_test())`. When `asyncio.run(_test())` is executed, it passes 100% with the proposed remediation.
4. **Scope Isolation**:
   This remediation is scoped to `backend/core/telemetry.py`. Other items identified by Reviewer 2 (such as CAS cache path traversal and `Settings.log_level` case normalization) are handled by parallel tracks or subsequent workers.

---

## 4. Conclusion

The remediation for `backend/core/telemetry.py` is fully formulated, rigorously verified, and ready for drop-in application by Worker M1.
- **Issue 1 (Event Duplication)**: Resolved by delegating solely to `asyncio.run_coroutine_threadsafe(self.emit(event), loop)` when an event loop is running.
- **Issue 2 (Async Callback Execution from Worker Threads)**: Resolved by routing awaitables through `asyncio.run_coroutine_threadsafe(coro, loop)` on foreign threads and wrapping in `_wrap_awaitable` with `result.close()` fallback.
- **Issue 3 (Typing Accuracy)**: Resolved by updating `subscribe()` return type to `AsyncContextManager[asyncio.Queue[TelemetryEvent]]`.
- **Policy Compliance**: 100% Zero-Any compliance, strict Pydantic v2 / typing adherence, zero facades.

---

## 5. Verification Method

To independently verify the proposed remediation:

```powershell
# 1. Verify syntax and byte-compilation of proposed_telemetry.py
python -m py_compile .agents/teamwork/explorer_m1_it2_1/proposed_telemetry.py

# 2. Run verification script testing proposed module against all baseline and challenger test suites
python -c "import importlib.util, pytest, sys
import backend.core.telemetry
spec = importlib.util.spec_from_file_location('proposed_telemetry', '.agents/teamwork/explorer_m1_it2_1/proposed_telemetry.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
backend.core.telemetry.TelemetryBus = mod.TelemetryBus

assert pytest.main(['tests/backend/test_telemetry.py', '-v']) == 0
assert pytest.main(['tests/backend/test_challenger_m1_2.py', '-k', 'emit_threadsafe', '-v']) == 0
print('ALL VERIFICATIONS PASSED!')
"
```

**Invalidation Conditions**:
- Any callback duplication in `emit_threadsafe()`
- Any `RuntimeWarning: coroutine was never awaited`
- Any failure in `tests/backend/test_telemetry.py`
