# Handoff Report: Milestone 2 — UE5 Bridge & Mock Server Adversarial Review

**Agent**: `reviewer_m2_2`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\reviewer_m2_2`  
**Date**: 2026-10-14  
**Target Milestone**: Milestone 2: UE5 Bridge & Mock Server (`backend/ue5/`)  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

### 1.1 Direct Repository Evidence & Verbatim Test Results

1. **Test Suite Executions**:
   - `python -m pytest tests/backend/test_ue5_bridge.py -v`:
     **43 passed in 8.48s** (100% green in isolation).
   - `python -m tests.e2e.runner --tier 1`:
     **41 passed in 1.63s** (100.0% feature coverage).
   - `python -m tests.e2e.runner --tier all`:
     **58 passed in 110.37s** (100.0% coverage across Tiers 1–4).
   - `python -m pytest tests/backend/ -q`:
     **FAILED**: 1 failed, 598 passed in 34.56s.
     Verbatim Failure:
     ```
     FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_concurrent_websocket_rpc_and_subscriptions
     AssertionError: assert 2 >= 5
      where 2 = len([
          {'Type': 'PropertyChanged', 'ObjectPath': '/Game/Stage_Main.PersistentLevel.Actor_1', 'Property': 'CustomScalar', 'Value': 42.5},
          {'Type': 'PropertyChanged', 'ObjectPath': '/Game/TestActor', 'Property': 'Intensity', 'Value': 1000.0}
      ])
     ```
   - Combined Sequential Execution (`python -m pytest tests/backend/test_ue5_bridge.py tests/backend/test_challenger_m2.py -v`):
     **2 failed, 57 passed in 17.37s**:
     ```
     FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_high_concurrency_threaded_rest_calls
     AssertionError: Expected 100 unique actor IDs, got 99
     assert 99 == 100

     FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_concurrent_websocket_rpc_and_subscriptions
     AssertionError: assert 0 >= 5
      where 0 = len([])
     ```

2. **Code Flaw 1: Shared Mutable Global State in `backend/ue5/mock_server.py`**:
   - Lines 257–258:
     ```python
     class UE5RESTHandler(BaseHTTPRequestHandler):
         """HTTP Request handler implementing the official UE5 Remote Control REST API."""

         state = UE5MockState()
     ```
   - Line 354:
     ```python
     class UE5MockServer:
         ...
         self.state: UE5MockState = UE5RESTHandler.state
     ```
   - Empirical Reproduction:
     ```python
     s1 = UE5MockServer(host='127.0.0.1', port=30010, ws_port=30020)
     s2 = UE5MockServer(host='127.0.0.1', port=30011, ws_port=30021)
     assert s1.state is s2.state  # Evaluates to True!
     s2.state.actors['/Game/Custom'] = {'class': 'Actor'}
     s1.stop()  # Executes self.state.reset()
     assert '/Game/Custom' not in s2.state.actors  # s1.stop() erased s2 state!
     ```
   - Stopping one server instance invokes `self.state.reset()` and sets `self.state.ws_loop = None`, destroying state and hijacking/clearing the WebSocket event loop of any other concurrently active or subsequent server.

3. **Code Flaw 2: Single-Threaded Head-of-Line Blocking in `MockHTTPServer`**:
   - Lines 329–331 in `backend/ue5/mock_server.py`:
     ```python
     class MockHTTPServer(HTTPServer):
         """HTTPServer with socket address reuse enabled for clean testing lifecycles."""
         allow_reuse_address = True
     ```
   - Python standard library `HTTPServer` is single-threaded and processes requests sequentially. Under high concurrency (e.g. 20 worker threads sending 100 simultaneous REST calls in `test_high_concurrency_threaded_rest_calls`), incoming sockets fill the OS listen queue, causing connection drops or request timeouts.
   - Missing inheritance from `socketserver.ThreadingMixIn`.

4. **Zero-Any Compliance & Clean Architecture Verification**:
   - Grep search for `\bAny\b` across `backend/ue5/`: **0 matches** (100% compliant).
   - Grep search for `tests` across imports in `backend/ue5/`: **0 matches** (Clean Architecture satisfied).
   - Inspecting `sys.modules` upon importing `backend.ue5`: Zero `tests` modules loaded.

5. **Camera Look-At Math & MRQ Telemetry**:
   - `CineCameraChoreographer.calculate_look_at`: Pitch calculation protected with `dist_xy = max(1e-5, dist_xy)`; no division-by-zero or NaN when camera position equals target position.
   - Presets generated valid bounded keyframes across all 5 configurations (`smooth_orbit`, `dramatic_orbit`, `aerial_pan`, `front_close`, `spiral_ascent`).
   - MRQ cancellation token isolation: Verified that cancelling Job A via its cooperative `asyncio.Event` raises `CancelledError` for Job A while Job B completes cleanly with its output file generated.

---

## 2. Logic Chain

1. **Premise 1 (Server Isolation Contract)**: Modular testability and production stability require that instances of `UE5MockServer` maintain encapsulated state. Two servers listening on different ports must not share world actors, loaded assets, or WebSocket event loop references.
2. **Premise 2 (Shared State Invalidation)**: `UE5RESTHandler.state = UE5MockState()` binds a class-level singleton. Because `UE5MockServer.state` points to `UE5RESTHandler.state`, calling `stop()` on any ephemeral server instance (such as in lifecycle unit tests) invokes `self.state.reset()` and nullifies `self.state.ws_loop`.
3. **Premise 3 (Observed Cross-Test Contamination)**: When `pytest tests/backend/` executes, `test_ue5_bridge.py` starts and stops ephemeral servers. The lingering singleton state retains stale property events (`CustomScalar`, `Intensity`) and disrupts the subsequent `test_challenger_m2.py` suite, causing `test_concurrent_websocket_rpc_and_subscriptions` to fail with `AssertionError: assert 2 >= 5` or `assert 0 >= 5`.
4. **Premise 4 (HTTP Concurrency Bottleneck)**: `MockHTTPServer` does not inherit from `ThreadingMixIn`. When 20 threads concurrently invoke `SpawnActor`, requests encounter head-of-line blocking in the single-threaded server, dropping connections and returning simulated offline fallback responses without `ActorId`, resulting in 99 unique IDs instead of 100.
5. **Conclusion**: While individual bridge unit tests in `test_ue5_bridge.py` pass in isolation, the mock server fails under multi-instance lifecycles and concurrent multi-threaded load across the backend test suite. Therefore, changes must be requested before Milestone 2 can be approved.

---

## 3. Caveats

- **No Integrity Violations Detected**: No hardcoded test results, facade shortcuts, or dummy bypasses were found in the implementation. The Look-At math, PBR parameters, and MRQ video container generation are genuine, fully implemented algorithms.
- **Isolated Tests vs Combined Suite**: All 43 tests in `test_ue5_bridge.py` and all 58 tests in `tests.e2e.runner` pass when executed in their respective dedicated processes. The failure manifests when multiple test modules or servers run in the same Python process.

---

## 4. Conclusion

**Verdict: REQUEST_CHANGES**

### Required Action Items for Worker (`worker_m2_1`):

1. **Refactor `UE5MockState` from Class Attribute to Instance Attribute**:
   - In `backend/ue5/mock_server.py`:
     - Modify `UE5MockServer.__init__` to instantiate an independent `self.state = UE5MockState()`.
     - Pass `self.state` to `self.http_server.state`.
     - Update `UE5RESTHandler` to access `self.server.state` dynamically:
       ```python
       @property
       def state(self) -> UE5MockState:
           if hasattr(self.server, "state"):
               return self.server.state  # type: ignore[no-any-return]
           return UE5RESTHandler._default_state
       ```
     - Ensure `self.state.ws_connections` and `self.state.ws_loop` are strictly bound to each server instance.
2. **Add Multi-Threading Support to `MockHTTPServer`**:
   - In `backend/ue5/mock_server.py`:
     - Import `from socketserver import ThreadingMixIn`.
     - Define:
       ```python
       class MockHTTPServer(ThreadingMixIn, HTTPServer):
           """Multi-threaded HTTPServer with socket address reuse enabled."""
           allow_reuse_address = True
           daemon_threads = True
       ```
3. **Verify Full Backend Suite**:
   - Run `python -m pytest tests/backend/ -v` and ensure all 599+ tests pass without a single failure.

---

## 5. Verification Method

To verify the issues and validate future fixes:

1. **Verify State Contamination Bug (Current Baseline Fails)**:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py tests/backend/test_challenger_m2.py -v
   ```
   *Current Failure*: `test_high_concurrency_threaded_rest_calls` and `test_concurrent_websocket_rpc_and_subscriptions` fail.
   *Target Fixed State*: 59 passed with 0 failures.

2. **Verify Full Backend Test Suite**:
   ```powershell
   python -m pytest tests/backend/ -v
   ```
   *Current Failure*: 1 failed, 598 passed.
   *Target Fixed State*: 599 passed, 0 failures.

3. **Verify E2E Suite Invariance**:
   ```powershell
   python -m tests.e2e.runner --tier all
   ```
   *Expected*: 58 passed, 0 failed (100.0% coverage).
