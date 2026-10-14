# Remediation Design and Handoff Report: UE5 Mock Server Hardening

**Agent**: `explorer_m2_it2_1`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_it2_1`  
**Target File**: `backend/ue5/mock_server.py`  
**Reference Artifact**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_it2_1\proposed_mock_server.py`  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Status**: COMPLETE (Ready for Implementation)

---

## 1. Observation

Direct code inspections of `backend/ue5/mock_server.py` and empirical findings from `challenger_m2_1/handoff.md`, `reviewer_m2_2/handoff.md`, and test suites `tests/backend/test_challenger_m2.py` and `tests/backend/test_challenger_m2_2.py`:

### 1.1 Single-Threaded HTTP Server Head-of-Line Blocking
- **File & Line**: `backend/ue5/mock_server.py`, lines 329–331:
  ```python
  class MockHTTPServer(HTTPServer):
      """HTTPServer with socket address reuse enabled for clean testing lifecycles."""
      allow_reuse_address = True
  ```
- **Observed Behavior**: `HTTPServer` inherits directly from `socketserver.TCPServer`, which is strictly single-threaded with a request backlog of 5. Under concurrent multi-threaded RPC load (e.g. 20 worker threads issuing 100 requests in `test_high_concurrency_threaded_rest_calls`), incoming connection requests get queued or dropped.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_high_concurrency_threaded_rest_calls
  AssertionError: Expected 100 unique actor IDs, got 99
  assert 99 == 100
  ```

### 1.2 Global State Shared Across `UE5MockServer` Instances
- **File & Line**: `backend/ue5/mock_server.py`, lines 257 and 354:
  ```python
  class UE5RESTHandler(BaseHTTPRequestHandler):
      state = UE5MockState()  # Class-level attribute shared across all handler & server instances
  ...
  class UE5MockServer:
      def __init__(...):
          ...
          self.state: UE5MockState = UE5RESTHandler.state
  ```
- **Observed Behavior**: All `UE5MockServer` instances bind to the single class attribute `UE5RESTHandler.state`. When an ephemeral test server stops via `server.stop()`, line 519 runs `self.state.reset()` and line 493 runs `self.state.ws_loop = None`. If another server instance is active or created in the same process, its state is erased and its `ws_loop` is nullified, causing subsequent WebSocket property events to never be dispatched.
- **Verbatim Error**:
  ```
  FAILED tests/backend/test_challenger_m2.py::TestHighConcurrencyRPC::test_concurrent_websocket_rpc_and_subscriptions
  >       assert len(received_events) >= 5
  E       assert 0 >= 5
  E        +  where 0 = len([])
  ```

### 1.3 Port Binding Resilience & Silent Port Binding Failure
- **File & Line**: `backend/ue5/mock_server.py`, lines 365–373:
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
- **Observed Behavior**: During rapid start/stop cycles (e.g. `test_rapid_start_stop_cycles_default_ports`), the OS TCP socket may momentarily remain in `TIME_WAIT`. `MockHTTPServer` raises `OSError` (`[WinError 10048] Only one usage of each socket address is normally permitted`). The `except OSError` catches it, leaves `self.http_server = None`, yet sets `self._is_running = True`. Clients attempting to connect encounter `ConnectionResetError` [WinError 10054] because no HTTP listener actually exists.

### 1.4 Dynamic Asset Import Container Validation Deficiencies
- **File & Line**: `backend/ue5/mock_server.py`, lines 116–130:
  ```python
  if function_name == "ImportAsset":
      asset_path = str(parameters.get("SourcePath", parameters.get("source_path", "")))
      dest_path = str(parameters.get("DestinationPath", parameters.get("destination_path", "/Game/Imported")))
      if asset_path and not Path(asset_path).exists():
          return {"Success": False, "Error": f"Source asset not found: {asset_path}"}
      asset_stem = Path(asset_path).stem if asset_path else "ImportedAsset"
      ...
      return {"Success": True, "AssetPath": f"{dest_path}/{asset_stem}"}
  ```
- **Observed Behavior**:
  1. Empty string or whitespace (`""`): `Path("").exists()` resolves to `Path(".").exists()` (True), importing `"ImportedAsset"` with `Success: True`.
  2. Directory path (e.g. `some_folder`): `Path("some_folder").exists()` is True, importing a directory as a mesh with `Success: True`.
  3. Corrupt GLB files (0-byte, invalid magic byte header, truncated length buffer): Bypasses all validation and falsely reports `Success: True`.

---

## 2. Logic Chain

1. **Premise 1 (HTTP Concurrency)**: FastMCP tool calls, multi-threaded pipelines, and adversarial tests dispatch concurrent REST requests. A single-threaded `HTTPServer` queues sockets in the OS listen backlog, causing timeouts and dropped requests (Observation 1.1).
   - *Inference*: Inheriting from `socketserver.ThreadingMixIn` with `daemon_threads = True` and `allow_reuse_address = True` delegates each incoming HTTP connection to a daemon thread, eliminating head-of-line blocking.

2. **Premise 2 (State & Event Loop Isolation)**: Parallel testing and clean architecture require independent server instances. `UE5RESTHandler.state` as a class variable creates cross-server mutable state leakage (Observation 1.2).
   - *Inference*: Decoupling state by:
     - Instantiating `self.state = UE5MockState()` independently inside `UE5MockServer.__init__`.
     - Assigning `self.http_server.state = self.state`.
     - Making `UE5RESTHandler.state` a dynamic `@property` resolving `self.server.state` with a static fallback `_default_state`.
     - In `stop()` and `_run_ws_server` finally block, guarding loop cleanup with `if self.state.ws_loop is loop: self.state.ws_loop = None`.
     Guarantees that stopping or resetting one server instance never alters another server instance's actors, properties, or WebSocket event loop.

3. **Premise 3 (Deterministic Port Binding)**: Rapid stop/start cycles on identical ports experience transient socket binding collisions on Windows (`TIME_WAIT`). Swallowing `OSError` without retry causes the server to report running when it is un-bound (Observation 1.3).
   - *Inference*: An exponential backoff retry loop (5 attempts, initial 0.05s delay scaling by 1.5x) allows the OS socket stack to release the port. If binding fails after all attempts, raising `OSError` and leaving `_is_running = False` preserves deterministic failure signaling.

4. **Premise 4 (GLB Container Integrity)**: UE5 runtime asset loading cannot accept invalid paths, directories, or corrupt binary payloads (Observation 1.4).
   - *Inference*: Enforcing strict validation in `ImportAsset`:
     - Reject empty or whitespace-only paths (`"Source asset path cannot be empty"`).
     - Require `path_obj.exists() and path_obj.is_file()` (`"Source asset not found or is not a regular file"`).
     - For `.glb` extensions, unpack the 12-byte binary glTF header:
       - Validate file size $\ge 12$ bytes.
       - Validate container magic `magic == b"glTF"`.
       - Validate version `version == 2`.
       - Validate total container length `total_length == file_size`.
     Guarantees that corrupt, truncated, or directory paths immediately return structured failure responses (`Success: False`).

---

## 3. Caveats

- **No Caveats on Specifications**: All 4 areas specified in the dispatch have been addressed with exact mathematical, structural, and behavioral conformity.
- **Zero-Any Strictness**: The proposed file has been verified with the project's strict AST visitor to ensure zero imports or usage of `Any`.
- **Backward Compatibility**: `UE5RESTHandler._default_state` is retained as a fallback so that any external or direct invocation of `UE5RESTHandler` without a parent server object functions without raising `AttributeError`.

---

## 4. Conclusion & Concrete Drop-In Remediation Design

The complete replacement file is formulated, tested, and stored at:  
`e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_it2_1\proposed_mock_server.py`.

### 4.1 Key Code Diffs

#### Change 1: Imports and `MockHTTPServer`
```python
# Added imports
from socketserver import ThreadingMixIn
import struct

# Inherit from ThreadingMixIn and HTTPServer
class MockHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTPServer with socket address reuse enabled for concurrent testing."""

    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        server_address: Tuple[str, int],
        RequestHandlerClass: type[BaseHTTPRequestHandler],
        state: Optional[UE5MockState] = None,
    ) -> None:
        super().__init__(server_address, RequestHandlerClass)
        self.state: UE5MockState = state if state is not None else UE5MockState()
```

#### Change 2: Decoupled `UE5RESTHandler.state`
```python
class UE5RESTHandler(BaseHTTPRequestHandler):
    """HTTP Request handler implementing the official UE5 Remote Control REST API."""

    _default_state: UE5MockState = UE5MockState()

    @property
    def state(self) -> UE5MockState:
        """Access the isolated UE5MockState bound to this HTTP server instance."""
        server = self.server
        if server is not None and hasattr(server, "state"):
            server_state = getattr(server, "state")
            if isinstance(server_state, UE5MockState):
                return server_state
        return self._default_state
```

#### Change 3: Server Instance Initialization and Lifecycle Resilience
```python
class UE5MockServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 30010,
        ws_port: int = 30020,
    ) -> None:
        self.host: str = host
        self.port: int = port
        self.ws_port: int = ws_port
        self.http_server: Optional[MockHTTPServer] = None
        self._http_thread: Optional[threading.Thread] = None
        self._ws_thread: Optional[threading.Thread] = None
        self._ws_stop_event: Optional[asyncio.Event] = None
        self._ws_bound: bool = False
        self._ws_error: Optional[Exception] = None
        self._is_running: bool = False
        self.state: UE5MockState = UE5MockState()  # Isolated per instance

    def start(self) -> None:
        if self._is_running:
            return

        # 1. Start HTTP REST Server with retry backoff for socket reuse
        max_bind_retries = 5
        bind_delay = 0.05
        http_bound = False
        last_os_err: Optional[OSError] = None

        for attempt in range(max_bind_retries):
            try:
                self.http_server = MockHTTPServer(
                    (self.host, self.port),
                    UE5RESTHandler,
                    state=self.state,
                )
                self.http_server.state = self.state
                self._http_thread = threading.Thread(
                    target=self.http_server.serve_forever,
                    daemon=True,
                )
                self._http_thread.start()
                http_bound = True
                break
            except OSError as err:
                last_os_err = err
                time.sleep(bind_delay)
                bind_delay *= 1.5

        if not http_bound or self.http_server is None:
            self.stop()
            raise OSError(
                f"Failed to bind UE5 Mock HTTP REST server to {self.host}:{self.port} "
                f"after {max_bind_retries} attempts: {last_os_err}"
            )

        # 2. Start WebSocket Server with retry backoff
        ws_bound_event = threading.Event()
        self._ws_bound = False
        self._ws_error = None
        self._ws_thread = threading.Thread(
            target=self._run_ws_server,
            args=(ws_bound_event,),
            daemon=True,
        )
        self._ws_thread.start()
        ws_bound_event.wait(timeout=2.0)

        if not self._ws_bound:
            self.stop()
            raise OSError(
                f"Failed to bind UE5 Mock WebSocket server to {self.host}:{self.ws_port}: {self._ws_error}"
            )

        self._is_running = True
        time.sleep(0.05)
```

#### Change 4: GLB Container Validation in `ImportAsset`
```python
            if function_name == "ImportAsset":
                asset_path = str(parameters.get("SourcePath", parameters.get("source_path", "")))
                dest_path = str(parameters.get("DestinationPath", parameters.get("destination_path", "/Game/Imported")))

                if not asset_path or not asset_path.strip():
                    return {
                        "Success": False,
                        "Error": "Source asset path cannot be empty",
                        "AssetPath": "",
                    }

                path_obj = Path(asset_path)
                if not path_obj.exists() or not path_obj.is_file():
                    return {
                        "Success": False,
                        "Error": f"Source asset not found or is not a regular file: {asset_path}",
                        "AssetPath": "",
                    }

                # Validate binary glTF container header if .glb
                if path_obj.suffix.lower() == ".glb":
                    file_size = path_obj.stat().st_size
                    if file_size < 12:
                        return {
                            "Success": False,
                            "Error": f"Corrupt GLB: file size ({file_size} bytes) is smaller than 12-byte header: {asset_path}",
                            "AssetPath": "",
                        }
                    try:
                        with open(path_obj, "rb") as f:
                            header = f.read(12)
                        if len(header) < 12:
                            return {
                                "Success": False,
                                "Error": f"Corrupt GLB: unable to read 12-byte header: {asset_path}",
                                "AssetPath": "",
                            }
                        magic, version, total_length = struct.unpack("<4sII", header)
                        if magic != b"glTF":
                            return {
                                "Success": False,
                                "Error": f"Corrupt GLB: invalid container magic {magic!r}, expected b'glTF': {asset_path}",
                                "AssetPath": "",
                            }
                        if version != 2:
                            return {
                                "Success": False,
                                "Error": f"Corrupt GLB: unsupported glTF version {version}, expected 2: {asset_path}",
                                "AssetPath": "",
                            }
                        if total_length != file_size:
                            return {
                                "Success": False,
                                "Error": (
                                    f"Corrupt GLB: total length in header ({total_length}) "
                                    f"does not match file size ({file_size}): {asset_path}"
                                ),
                                "AssetPath": "",
                            }
                    except Exception as err:
                        return {
                            "Success": False,
                            "Error": f"Cannot read GLB container {asset_path}: {err}",
                            "AssetPath": "",
                        }

                asset_stem = path_obj.stem
                normalized_dest = dest_path.rstrip("/") if dest_path else "/Game/Imported"
                asset_record = {
                    "source": asset_path,
                    "destination": normalized_dest,
                    "asset_name": asset_stem,
                }
                self.loaded_assets.append(asset_record)
                return {"Success": True, "AssetPath": f"{normalized_dest}/{asset_stem}"}
```

---

## 5. Verification Method

To verify the implementation independently:

1. **AST Zero-Any Verification**:
   ```powershell
   python -c "
   import ast
   from pathlib import Path

   py_file = Path('backend/ue5/mock_server.py')
   violations = []

   class AnyDetector(ast.NodeVisitor):
       def visit_Import(self, node):
           for alias in node.names:
               if alias.name == 'Any' or alias.name.endswith('.Any'):
                   violations.append(f'{node.lineno}: Import {alias.name}')
           self.generic_visit(node)

       def visit_ImportFrom(self, node):
           if node.module in ('typing', 'typing_extensions'):
               for alias in node.names:
                   if alias.name == 'Any':
                       violations.append(f'{node.lineno}: ImportFrom Any')
           self.generic_visit(node)

       def visit_Name(self, node):
           if node.id == 'Any':
               violations.append(f'{node.lineno}: Name Any')
           self.generic_visit(node)

       def visit_Constant(self, node):
           if isinstance(node.value, str) and node.value.strip() == 'Any':
               violations.append(f'{node.lineno}: Constant Any')
           self.generic_visit(node)

   tree = ast.parse(py_file.read_text(encoding='utf-8'))
   AnyDetector().visit(tree)
   assert len(violations) == 0, f'Violations: {violations}'
   print('Zero-Any check PASSED')
   "
   ```

2. **Combined Concurrency & Stress Verification**:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py tests/backend/test_challenger_m2.py tests/backend/test_challenger_m2_2.py -v
   ```
   *Expected*: All 113 items pass without dropped connections, socket errors, or state contamination.

3. **Full Backend Suite & E2E Suites**:
   ```powershell
   python -m pytest tests/backend/ -q
   python -m tests.e2e.runner --tier all
   ```
   *Expected*: 100% pass across all unit and integration test suites.
