# Telemetry Remediation Report: Milestone 1 Iteration 2

**Author**: Explorer 1 (`explorer_m1_it2_1`)  
**Target File**: `backend/core/telemetry.py`  
**Date**: 2026-10-14  
**Status**: Remediation Formulated & Empirically Verified (Ready for Implementation)

---

## 1. Executive Summary

During Milestone 1 Iteration 2 adversarial review (`reviewer_m1_2` and `challenger_m1_2`), two critical concurrency bugs were identified in `backend/core/telemetry.py`:
1. **Event & History Duplication in `emit_threadsafe()`**: Calling `emit_threadsafe()` when an event loop was running caused every telemetry event to be recorded twice in `_history` and delivered twice to all callback subscribers (e.g. 400 callbacks received for 200 emitted events under 20-thread concurrency).
2. **Background Thread Async Callback Failure & Coroutine Leak**: Invoking `emit_threadsafe()` from a background thread with an asynchronous callback subscriber called `asyncio.create_task()` without an active event loop on that thread, raising `RuntimeError: no running event loop` (silently swallowed in `except Exception`) and leaking the coroutine unawaited with `RuntimeWarning: coroutine was never awaited`.
3. **Type Annotation Inaccuracy in `subscribe()`**: `subscribe()` was typed as returning `AsyncIterator[asyncio.Queue[TelemetryEvent]]` when operating in context manager mode, despite returning an `AsyncContextManager[asyncio.Queue[TelemetryEvent]]`.

This document formulates the exact, production-ready remediation code changes resolving all three issues while maintaining 100% compliance with the Zero-Any Policy (Pydantic v2 / strict typing) and Clean Architecture / SOLID design principles.

---

## 2. Problem Analysis & Remediation Details

### Issue 1: Event Duplication in `emit_threadsafe()`

#### Root Cause
In `backend/core/telemetry.py` lines 246–267:
```python
def emit_threadsafe(self, event: TelemetryEvent) -> None:
    # 1. First append to _history and invoke callbacks synchronously on worker thread:
    self._history.append(event)
    if isinstance(event, ProgressEvent):
        self._latest_progress = event
    elif isinstance(event, PlanProposalEvent):
        self._latest_plan = event

    self._invoke_callbacks(event)

    loop = self.get_event_loop()
    if loop is None or not loop.is_running():
        return

    # 2. Schedules self.emit(event) onto the event loop:
    asyncio.run_coroutine_threadsafe(self.emit(event), loop)
```
When `self.emit(event)` executes on the event loop (lines 220–229):
```python
    self._history.append(event)  # DUPLICATE APPEND
    if isinstance(event, ProgressEvent):
        self._latest_progress = event
    elif isinstance(event, PlanProposalEvent):
        self._latest_plan = event

    self._invoke_callbacks(event)  # DUPLICATE CALLBACK EXECUTION
```
Consequently:
- Every callback subscriber received the event twice (once on the worker thread, once on the loop thread).
- `_history` stored duplicate entries for each emission.
- In multi-threaded workloads (such as Demucs audio separation or UE5 render loops), subscriber streams received duplicate frames.

#### Remediation Strategy
When an event loop is running (`loop is not None and loop.is_running()`), `emit_threadsafe()` must **delegate solely** to `asyncio.run_coroutine_threadsafe(self.emit(event), loop)` and return immediately.
It must **NOT** append to `_history`, update latest caches, or invoke callbacks beforehand on the worker thread.
All state mutation (`_history.append`, `_latest_progress`, `_latest_plan`), callback invocations, and queue broadcasting will occur exactly once within `self.emit(event)` on the loop thread.

When NO event loop is running (e.g. standalone CLI, unit test before loop initialization), `emit_threadsafe()` executes the fallback synchronous path: appends to `_history`, updates latest caches, invokes sync callbacks, and logs a debug notice.

---

### Issue 2: Background Thread Async Callback Execution & Coroutine Leak

#### Root Cause
In `backend/core/telemetry.py` lines 201–206:
```python
if inspect.isawaitable(result):
    loop = self.get_event_loop()
    if loop is not None and loop.is_running():
        asyncio.create_task(result)  # type: ignore[arg-type]
```
`asyncio.create_task()` operates exclusively on the running event loop of the *calling thread*. If `_invoke_callbacks` is executed on a background worker thread where no loop is running, `asyncio.create_task` raises `RuntimeError: no running event loop in thread`. The exception was caught by `except Exception`, but the coroutine object was dropped without ever being scheduled or awaited, leaking memory and producing `RuntimeWarning: coroutine was never awaited`.

#### Remediation Strategy
1. Introduce a typed static helper method `_wrap_awaitable(awaitable: Awaitable[object]) -> None` that awaits the coroutine and catches/logs any runtime exceptions so unhandled task errors never occur.
2. When an awaitable is returned by a callback subscriber:
   - Check if an event loop is registered and running (`loop is not None and loop.is_running()`).
   - If running, inspect `asyncio.get_running_loop()`:
     - If the calling thread is running `loop` (`current_loop is loop`), schedule directly via `loop.create_task(coro)`.
     - If the calling thread is a background worker thread (`current_loop is not loop`), route the coroutine through `asyncio.run_coroutine_threadsafe(coro, loop)`.
   - If NO event loop is running, log a warning and explicitly close the coroutine (`result.close()`) if `inspect.iscoroutine(result)` to prevent coroutine leaks and `RuntimeWarning` diagnostics.

---

### Issue 3: Precise Return Type Annotation in `subscribe()`

#### Root Cause
In `backend/core/telemetry.py` line 141:
```python
def subscribe(...) -> Union[AsyncIterator[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
```
`subscribe()` delegates context manager invocations to `_subscribe_context_manager()`, which is decorated with `@asynccontextmanager`. Calling an `@asynccontextmanager`-decorated function returns an `AsyncContextManager` (from `typing`), not a raw `AsyncIterator`.

#### Remediation Strategy
Update typing import to include `AsyncContextManager` and change return type annotation to:
```python
Union[AsyncContextManager[asyncio.Queue[TelemetryEvent]], Callable[[], None]]
```

---

## 3. Exact Unified Diff Patch

The exact unified diff patch is saved at:
`e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m1_it2_1\telemetry.patch`

```diff
--- a/backend/core/telemetry.py
+++ b/backend/core/telemetry.py
@@ -20,8 +20,11 @@
 import inspect
 import logging
 from typing import (
+    AsyncContextManager,
     AsyncIterator,
+    Awaitable,
     Callable,
+    Coroutine,
     Deque,
     Dict,
     List,
@@ -138,7 +141,7 @@
         callback_or_replay: Union[TelemetryEventCallback, bool] = True,
         replay_history: bool = True,
         max_queue_size: Optional[int] = None,
-    ) -> Union[AsyncIterator[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
+    ) -> Union[AsyncContextManager[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
         """
         Flexible subscriber method supporting both callback functions and async context managers.
 
@@ -193,6 +196,14 @@
                 finally:
                     queue.task_done()
 
+    @staticmethod
+    async def _wrap_awaitable(awaitable: Awaitable[object]) -> None:
+        """Wrap an awaitable in a coroutine with exception logging."""
+        try:
+            await awaitable
+        except Exception as exc:
+            logger.warning("Error executing async telemetry callback subscriber: %s", exc)
+
     def _invoke_callbacks(self, event: TelemetryEvent) -> None:
         """Execute all registered callback subscribers."""
         for callback in list(self._callbacks):
@@ -201,7 +212,22 @@
                 if inspect.isawaitable(result):
                     loop = self.get_event_loop()
                     if loop is not None and loop.is_running():
-                        asyncio.create_task(result)  # type: ignore[arg-type]
+                        coro: Coroutine[object, object, None] = self._wrap_awaitable(result)
+                        try:
+                            current_loop = asyncio.get_running_loop()
+                        except RuntimeError:
+                            current_loop = None
+
+                        if current_loop is loop:
+                            loop.create_task(coro)
+                        else:
+                            asyncio.run_coroutine_threadsafe(coro, loop)
+                    else:
+                        logger.warning(
+                            "TelemetryBus._invoke_callbacks: async callback dropped; no running event loop available."
+                        )
+                        if inspect.iscoroutine(result):
+                            result.close()
             except Exception as exc:
                 logger.warning("Error executing telemetry callback subscriber: %s", exc)
 
@@ -246,24 +272,23 @@
     def emit_threadsafe(self, event: TelemetryEvent) -> None:
         """
         Thread-safe emission helper for synchronous background worker threads.
-        Schedules `emit` on the registered asyncio event loop or invokes callbacks immediately.
-        """
-        # Update history and latest caches synchronously
+        Schedules `emit` on the registered asyncio event loop or invokes callbacks immediately
+        if no event loop is active.
+        """
+        loop = self.get_event_loop()
+        if loop is not None and loop.is_running():
+            asyncio.run_coroutine_threadsafe(self.emit(event), loop)
+            return
+
+        # Fallback when running without an active event loop (e.g. standalone CLI or unit test)
         self._history.append(event)
         if isinstance(event, ProgressEvent):
             self._latest_progress = event
         elif isinstance(event, PlanProposalEvent):
             self._latest_plan = event
 
-        # Always invoke sync callbacks immediately
         self._invoke_callbacks(event)
-
-        loop = self.get_event_loop()
-        if loop is None or not loop.is_running():
-            logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")
-            return
-
-        asyncio.run_coroutine_threadsafe(self.emit(event), loop)
+        logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")
 
     def get_history(self) -> List[TelemetryEvent]:
         """Return a snapshot of recent telemetry events."""
```

---

## 4. Before and After Code Comparisons

### 4.1 Imports & Type Annotations
**Before**:
```python
from typing import (
    AsyncIterator,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Union,
)
```

**After**:
```python
from typing import (
    AsyncContextManager,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Union,
)
```

### 4.2 `subscribe()` Return Type Annotation
**Before**:
```python
    def subscribe(
        self,
        callback_or_replay: Union[TelemetryEventCallback, bool] = True,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> Union[AsyncIterator[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
```

**After**:
```python
    def subscribe(
        self,
        callback_or_replay: Union[TelemetryEventCallback, bool] = True,
        replay_history: bool = True,
        max_queue_size: Optional[int] = None,
    ) -> Union[AsyncContextManager[asyncio.Queue[TelemetryEvent]], Callable[[], None]]:
```

### 4.3 Async Callback Execution in `_invoke_callbacks()`
**Before**:
```python
    def _invoke_callbacks(self, event: TelemetryEvent) -> None:
        """Execute all registered callback subscribers."""
        for callback in list(self._callbacks):
            try:
                result = callback(event)
                if inspect.isawaitable(result):
                    loop = self.get_event_loop()
                    if loop is not None and loop.is_running():
                        asyncio.create_task(result)  # type: ignore[arg-type]
            except Exception as exc:
                logger.warning("Error executing telemetry callback subscriber: %s", exc)
```

**After**:
```python
    @staticmethod
    async def _wrap_awaitable(awaitable: Awaitable[object]) -> None:
        """Wrap an awaitable in a coroutine with exception logging."""
        try:
            await awaitable
        except Exception as exc:
            logger.warning("Error executing async telemetry callback subscriber: %s", exc)

    def _invoke_callbacks(self, event: TelemetryEvent) -> None:
        """Execute all registered callback subscribers."""
        for callback in list(self._callbacks):
            try:
                result = callback(event)
                if inspect.isawaitable(result):
                    loop = self.get_event_loop()
                    if loop is not None and loop.is_running():
                        coro: Coroutine[object, object, None] = self._wrap_awaitable(result)
                        try:
                            current_loop = asyncio.get_running_loop()
                        except RuntimeError:
                            current_loop = None

                        if current_loop is loop:
                            loop.create_task(coro)
                        else:
                            asyncio.run_coroutine_threadsafe(coro, loop)
                    else:
                        logger.warning(
                            "TelemetryBus._invoke_callbacks: async callback dropped; no running event loop available."
                        )
                        if inspect.iscoroutine(result):
                            result.close()
            except Exception as exc:
                logger.warning("Error executing telemetry callback subscriber: %s", exc)
```

### 4.4 `emit_threadsafe()`
**Before**:
```python
    def emit_threadsafe(self, event: TelemetryEvent) -> None:
        """
        Thread-safe emission helper for synchronous background worker threads.
        Schedules `emit` on the registered asyncio event loop or invokes callbacks immediately.
        """
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

**After**:
```python
    def emit_threadsafe(self, event: TelemetryEvent) -> None:
        """
        Thread-safe emission helper for synchronous background worker threads.
        Schedules `emit` on the registered asyncio event loop or invokes callbacks immediately
        if no event loop is active.
        """
        loop = self.get_event_loop()
        if loop is not None and loop.is_running():
            asyncio.run_coroutine_threadsafe(self.emit(event), loop)
            return

        # Fallback when running without an active event loop (e.g. standalone CLI or unit test)
        self._history.append(event)
        if isinstance(event, ProgressEvent):
            self._latest_progress = event
        elif isinstance(event, PlanProposalEvent):
            self._latest_plan = event

        self._invoke_callbacks(event)
        logger.debug("TelemetryBus.emit_threadsafe running without active event loop; queue broadcast deferred.")
```

---

## 5. Blast Radius & Downstream Call Site Impact

All synchronous emission helper functions in `backend/core/telemetry.py` delegate directly to `target_bus.emit_threadsafe(event)`:
- `emit_progress_sync()` (line 372)
- `emit_log_sync()` (line 398)
- `emit_asset_ready_sync()` (line 436)

By fixing `emit_threadsafe()`, all synchronous helpers across the system benefit immediately:
1. **UE5 Bridge (Milestone 2)**: Long-running Movie Render Queue status tickers and WebSocket pollers emitting via `emit_progress_sync` from background thread pools will dispatch cleanly without duplicate entries in telemetry logs.
2. **AI Pipelines (Milestone 3)**: Audio Demucs separation and ComfyUI job pollers running in `ThreadPoolExecutor` workers will emit single events to frontend listeners without flooding WebSocket/SSE connections.
3. **FastMCP Server (Milestone 4)**: MCP tool executions emitting logs and asset readiness from thread pools will not double-count events or corrupt client plan state.

---

## 6. Test Suite Adjustment Guidance

### 6.1 `tests/backend/test_challenger_m1_2.py`
In `tests/backend/test_challenger_m1_2.py`:
- `test_emit_threadsafe_heavy_concurrency_with_running_loop` previously failed with `Callbacks duplicated: got 400, expected 200`. With the remediation applied, this test passes 100% (200 expected, 200 received).
- `test_emit_threadsafe_async_callback_from_thread` previously produced `RuntimeWarning: coroutine was never awaited`. With the remediation applied, this test passes with 0 warnings.
- Note for Worker: In `test_emit_threadsafe_duplicate_emission_with_running_loop` (lines 105–153), Challenger omitted `asyncio.run(_test())` at line 154. Adding `asyncio.run(_test())` verifies that `cb_count == 1` and `hist_count == 1` passes cleanly.

### 6.2 `tests/backend/test_adversarial_m1.py`
In `tests/backend/test_adversarial_m1.py` lines 507–550, Challenger in Milestone 1 Iteration 1 created `test_emit_threadsafe_double_invocation_and_history_duplication` as an empirical bug demonstration asserting that the bug was present:
```python
# Lines 538 and 544 in test_adversarial_m1.py:
assert call_count == 2
assert len(history) == 2
```
When Worker M1 applies the remediation fix, this test will fail because `call_count` will now correctly be `1` (single invocation) and `len(history)` will be `1`.
**Action for Worker M1**: Update lines 538 and 544 in `tests/backend/test_adversarial_m1.py` to assert single invocation (`call_count == 1` and `len(history) == 1`) and rename the test to `test_emit_threadsafe_single_invocation_and_history`.

---

## 7. Artifact Index

- **Replacement File**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m1_it2_1\proposed_telemetry.py`
- **Diff Patch**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m1_it2_1\telemetry.patch`
- **Handoff Report**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m1_it2_1\handoff.md`
