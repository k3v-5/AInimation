# Empirical Challenger Report: Milestone 2 — UE5 Bridge & Mock Server Stress Testing

**Agent**: `challenger_m2_1`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\challenger_m2_1`  
**Date**: 2026-10-14  
**Target Milestone**: Milestone 2: Unreal Engine 5 Bridge (`backend/ue5/`)  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

### 1.1 Summary of Tests Executed
1. **Baseline Suite**: `python -m pytest tests/backend/test_ue5_bridge.py -v` (43 items).
   - Execution result: 43 passed in 8.38s.
2. **Dedicated Challenger Stress Harness**: `tests/backend/test_challenger_m2.py` (16 adversarial stress tests).
   - High-concurrency multi-threaded RPCs (20 threads x 5 requests = 100 requests).
   - Concurrent pipelined WebSocket client sessions (5 clients x 10 in-flight requests = 50 requests).
   - Heavy read/write property contention across 10 threads.
   - Rapid sequential start/stop cycles on default ports 30010 (HTTP) and 30020 (WS).
   - Server start/stop idempotency.
   - Boundary & singularity trajectory math for CineCamera Look-At (zero distance, vertical pitch $\pm 90^\circ$, collinear axes, extreme floats $10^{12}$ and $10^{-9}$).
   - Boundary beat grids (empty, negative, duplicate, out-of-range, extreme FOV/distance).
   - MRQ cooperative cancellation via `asyncio.Event` (pre-cancelled, warmup phase, frame execution loop, concurrent mixed cancellation/completion).
3. **Full Backend Suite**: `python -m pytest tests/backend/ -v` (655 tests total).
   - Execution result: **3 failed, 652 passed in 35.35s**.

---

### 1.2 Verbatim Errors and Empirical Findings

#### Finding 1 (Critical): Silent Port Binding Failure & Socket Reset on Rapid Server Cycles
- **File**: `backend/ue5/mock_server.py`, lines 365–373:
  ```python
  # 1. Start HTTP REST Server
  try:
      self.http_server = MockHTTPServer((self.host, self.port), UE5RESTHandler)
      self._http_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
      self._http_thread.start()
      logger.info("UE5 Mock HTTP REST server listening on http://%s:%d", self.host, self.port)
  except OSError as err:
      logger.debug("HTTP port %d already bound or busy: %s", self.port, err)
  ...
  self._is_running = True
  ```
- **Observed Behavior**:
  When a server is rapidly restarted on port 30010 (e.g. cycle 1 -> cycle 2), the OS socket may be in `TIME_WAIT`/`FIN_WAIT`. `MockHTTPServer((self.host, self.port), UE5RESTHandler)` raises `OSError` (`[WinError 10048] Only one usage of each socket address is normally permitted`).
  Line 371 **silently catches `OSError`**, leaving `self.http_server = None`, but proceeds to set `self._is_running = True`.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2.py::TestServerLifecycleAndSocketReuse::test_rapid_start_stop_cycles_default_ports
  E   ConnectionResetError: [WinError 10054] Se ha forzado la interrupción de una conexión existente por el host remoto
  ```
- **Impact**: Any consumer or client connecting to the supposedly "running" server encounters dropped connections or `ConnectionResetError` because no HTTP server is actually listening.

---

#### Finding 2 (Critical): Global State Shared Across `UE5MockServer` Instances Clobbers WebSocket Event Loop
- **File**: `backend/ue5/mock_server.py`, lines 257 and 354:
  ```python
  class UE5RESTHandler(BaseHTTPRequestHandler):
      state = UE5MockState()  # <-- Class attribute shared across all handler & server instances
  ...
  class UE5MockServer:
      def __init__(...):
          ...
          self.state: UE5MockState = UE5RESTHandler.state
  ```
- **Observed Behavior**:
  Because `UE5RESTHandler.state` is a class attribute, all `UE5MockServer` instances share a single singleton `UE5MockState`.
  When ANY server instance stops via `server.stop()`, line 519 runs `self.state.reset()` and line 493 runs `self.state.ws_loop = None`.
  If another server instance was running or created, its `self.state.ws_loop` is set to `None`.
  When `set_property` calls `_broadcast_event`:
  ```python
  def _broadcast_event(self, event_data: UE5ParamDict) -> None:
      if self.ws_loop and self.ws_loop.is_running() and self.ws_connections:
          asyncio.run_coroutine_threadsafe(self._async_broadcast(event_data), self.ws_loop)
  ```
  Because `self.ws_loop` was clobbered to `None`, **no events are ever dispatched** to connected WebSocket clients.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_concurrent_websocket_rpc_and_subscriptions
  >       assert len(received_events) >= 5
  E       assert 0 >= 5
  E        +  where 0 = len([])
  ```

---

#### Finding 3 (High): Single-Threaded `MockHTTPServer` Causes Dropped Connections Under Concurrency
- **File**: `backend/ue5/mock_server.py`, lines 329–331:
  ```python
  class MockHTTPServer(HTTPServer):
      """HTTPServer with socket address reuse enabled for clean testing lifecycles."""
      allow_reuse_address = True
  ```
- **Observed Behavior**:
  `HTTPServer` inherits from `socketserver.TCPServer`, which is strictly single-threaded and has a default request queue backlog of 5 (`request_queue_size = 5`).
  Under concurrent multi-threaded load (e.g. 10 threads making concurrent `set_property` and `get_property` calls), incoming connection requests exceed the backlog and are dropped or reset by Windows TCP stack.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_mock_server_concurrent_mixed_read_write_heavy
  E   AssertionError: Errors during heavy read/write contention: ['Read returned None at tid=4, op=0']
  ```
- **Impact**: Server is unable to reliably serve concurrent requests from multiple threads or services without connection drops.

---

#### Finding 4 (High): Empty String Asset Path Resolves to Working Directory and Imports as Valid Asset
- **File**: `backend/ue5/client.py`, lines 468–475 and `backend/ue5/mock_server.py`, lines 120–128:
  ```python
  # client.py
  path_obj = Path(source_path)
  if not path_obj.exists():
      return {"Success": False, "Error": f"Asset file does not exist: {source_path}", ...}
  ```
- **Observed Behavior**:
  In Python, `Path("").exists()` evaluates to `Path(".").exists()`, which is `True` and resolves to the current working directory (`E:\Disco F\Dev\IANIMATION`).
  When `client.import_asset("")` is invoked, `Path("")` bypasses validation, `Path("").stem` resolves to `"IANIMATION"`, and the mock server reports:
  `{'Success': True, 'AssetPath': '/Game/Imported/IANIMATION'}`.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2_2.py::TestDynamicAssetImportErrorHandling::test_import_asset_empty_string_path
  E   AssertionError: assert True is False
  E    +  where True = {'Success': True, 'AssetPath': '/Game/Imported/IANIMATION'}.get('Success')
  ```

---

#### Finding 5 (Medium): CineCamera `front_close` Preset Has Hardcoded Pitch/Yaw Facing Away from Target
- **File**: `backend/ue5/camera.py`, lines 143–149:
  ```python
  elif preset == "front_close":
      x = 0.0 + 20.0 * math.sin(progress * math.pi * 4.0)
      y = -self.distance * 0.5
      z = center_z + 10.0 * math.cos(progress * math.pi * 2.0)
      pitch = 0.0
      yaw = 0.0
  ```
- **Observed Behavior**:
  Camera is positioned at `y = -self.distance * 0.5` (offset along negative Y axis), looking towards the focal target at `(0, 0, center_z)`. In Unreal coordinates (+X forward, +Y right), the vector from camera to target points along +Y (`yaw = +90.0`).
  By hardcoding `yaw = 0.0`, the camera faces along +X instead of facing the target actor.
  Other presets call `self.calculate_look_at(cam_pos, target)`, but `front_close` hardcodes `pitch = 0.0, yaw = 0.0`.

---

#### Finding 6 (Medium): Synchronous `MRQManager.render()` Lacks `cancellation_token` Parameter
- **File**: `backend/ue5/mrq.py`, lines 193–201:
  ```python
  def render(
      self,
      scene_path: str,
      output_path: str,
      fps: int = 30,
      resolution: str = "1280x720",
      warmup_frames: int = 15,
      anti_aliasing_samples: int = 8,
  ) -> RenderResult:
  ```
- **Observed Behavior**:
  While `render_async()` accepts `cancellation_token: Optional[asyncio.Event] = None`, the synchronous facade `render()` and functional facade `render_sequence()` do not expose or accept a `cancellation_token` parameter, making cooperative cancellation inaccessible via synchronous calls.

---

## 2. Logic Chain

1. **Premise 1**: Port lifecycle resilience requires that a server either binds its port and serves incoming traffic or explicitly raises an error if binding fails.
2. **Observation 1**: `mock_server.py:371` swallows `OSError` during port binding, leaves `self.http_server = None`, yet flags `self._is_running = True`. During rapid start/stop cycles, `urlopen` fails with `ConnectionResetError` (Observation 1.2, Finding 1).
3. **Premise 2**: Multi-instance testing and isolated components require independent server states.
4. **Observation 2**: `UE5RESTHandler.state = UE5MockState()` is a static class variable. Server teardown sets `ws_loop = None` globally, breaking WebSocket event dispatching for any concurrent or subsequent server (Observation 1.2, Finding 2).
5. **Premise 3**: FastMCP and orchestrators make concurrent multi-threaded RPC calls to UE5 Remote Control.
6. **Observation 3**: `MockHTTPServer(HTTPServer)` is single-threaded with backlog 5, causing dropped connections and `None` property responses under concurrency (Observation 1.2, Finding 3).
7. **Premise 4**: Input validation must reject empty strings for filesystem and asset paths.
8. **Observation 4**: `import_asset("")` passes `Path("").exists()` because it resolves to `.` (the project directory), creating fictitious asset `/Game/Imported/IANIMATION` (Observation 1.2, Finding 4).
9. **Conclusion**: Milestone 2 contains critical and high-severity robustness bugs in server lifecycle, state isolation, concurrency handling, and asset input validation. Therefore, Milestone 2 cannot be approved in its current state.

---

## 3. Caveats

- **Live Unreal Editor Remote Control Web Plugin**: Testing was conducted against `UE5MockServer`, client adapters, and mathematical/cancellation models. Live Unreal Editor 5.4 was not attached in this CI environment.
- **Boundary Math Robustness**: Trajectory boundary math (`calculate_look_at` zero distance, vertical pitch $\pm 90^\circ$, collinear axes, extreme floats) was proven mathematically robust and passed all adversarial tests.
- **Cancellation Robustness**: Cooperative cancellation in `render_async()` was verified to function correctly when passed an `asyncio.Event`.

---

## 4. Conclusion & Actionable Recommendations

**Verdict: REQUEST_CHANGES**

To resolve these findings, the worker agent must implement the following targeted fixes:

1. **Fix Port Binding Failure Handling in `mock_server.py`**:
   - In `UE5MockServer.start()`, do NOT silently catch `OSError`. If port binding fails, raise the exception or retry binding with a short backoff (e.g. 3 attempts with 0.1s sleep), and do NOT set `_is_running = True` if `http_server` or WebSocket server failed to bind.
2. **Fix State Isolation in `mock_server.py`**:
   - Replace class attribute `UE5RESTHandler.state = UE5MockState()` with an instance-based or server-bound state. In `MockHTTPServer`, store `server.state = self.state`. In `UE5RESTHandler`, reference `self.server.state` instead of `self.state` class variable.
3. **Enable Threading on `MockHTTPServer` in `mock_server.py`**:
   - Change `MockHTTPServer` to inherit from `http.server.ThreadingHTTPServer`:
     ```python
     from http.server import ThreadingHTTPServer

     class MockHTTPServer(ThreadingHTTPServer):
         allow_reuse_address = True
         daemon_threads = True
     ```
4. **Validate Non-Empty String in `import_asset()`**:
   - In `backend/ue5/client.py` (`import_asset`) and `backend/ue5/mock_server.py` (`call_function("ImportAsset")`):
     ```python
     if not source_path or not str(source_path).strip():
         return {"Success": False, "Error": "Source asset path cannot be empty", "AssetPath": ""}
     ```
5. **Fix CineCamera `front_close` Preset in `backend/ue5/camera.py`**:
   - Replace hardcoded `pitch = 0.0, yaw = 0.0` with `pitch, yaw = self.calculate_look_at(cam_pos, target)`.
6. **Expose `cancellation_token` in `MRQManager.render()`**:
   - Add `cancellation_token: Optional[asyncio.Event] = None` to `MRQManager.render()` and `render_sequence()` and forward it to `render_async()`.

---

## 5. Verification Method

To independently reproduce the failures identified in this report:

1. **Reproduce Rapid Start/Stop Socket Reset (`Finding 1`)**:
   ```powershell
   python -m pytest tests/backend/test_challenger_m2.py -k "test_rapid_start_stop_cycles_default_ports" -v
   ```
   *Observed*: `ConnectionResetError: [WinError 10054]`.

2. **Reproduce Empty Path Import (`Finding 4`)**:
   ```powershell
   python -m pytest tests/backend/test_challenger_m2_2.py -k "test_import_asset_empty_string_path" -v
   ```
   *Observed*: `AssertionError: assert True is False` (returns `/Game/Imported/IANIMATION`).

3. **Reproduce WebSocket Event Clobbering (`Finding 2`) & Read/Write Dropped Connections (`Finding 3`)**:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py tests/backend/test_challenger_m2.py -v
   ```
   *Observed*: Failures in `test_concurrent_websocket_rpc_and_subscriptions` and `test_mock_server_concurrent_mixed_read_write_heavy`.
