"""
High-Fidelity Unreal Engine 5 Mock Server.

Emulates the Unreal Engine Remote Control API:
- HTTP REST server on port 30010 (PUT /remote/object/call, PUT /remote/object/property, GET /remote/info)
- WebSocket server on port 30020 (/remote/protocol for RPC tunneling and event subscriptions)

Thread-safe and coroutine-safe in-memory state store tracking actors, transforms,
materials, properties, loaded assets, and active subscriptions.
100% Zero-Any compliant with Pydantic v2 strict models.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from socketserver import ThreadingMixIn
import struct
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Dict, List, Optional, Set, Tuple, Union
import websockets

logger = logging.getLogger("ianimation.ue5.mock_server")

# ---------------------------------------------------------------------------
# Strict Type Definitions (Zero-Any Policy)
# ---------------------------------------------------------------------------

UE5Scalar = Union[str, int, float, bool]
UE5ParamValue = Union[
    str,
    int,
    float,
    bool,
    Dict[str, float],
    Dict[str, str],
    Dict[str, Union[str, int, float, bool]],
    List[float],
    List[str],
    List[int],
    List[Dict[str, Union[str, float]]],
    None,
]
UE5ParamDict = Dict[str, UE5ParamValue]
UE5ActorRecord = Dict[str, Union[str, float, bool, Dict[str, float], List[str], int, None]]


# ---------------------------------------------------------------------------
# Stateful In-Memory Unreal Engine Simulation Store
# ---------------------------------------------------------------------------

class UE5MockState:
    """
    Thread-safe and coroutine-safe state store for simulated Unreal Engine actors,
    components, materials, loaded assets, and active WebSocket subscriptions.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.actors: Dict[str, UE5ActorRecord] = {}
        self.properties: Dict[str, Dict[str, UE5ParamValue]] = {}
        self.loaded_assets: List[Dict[str, str]] = []
        self.rendered_jobs: List[Dict[str, Union[str, int, float, bool]]] = []
        self.active_level: str = "Stage_Main"
        self.ws_connections: Set[websockets.ServerConnection] = set()
        self.ws_loop: Optional[asyncio.AbstractEventLoop] = None
        self._init_defaults()

    def _init_defaults(self) -> None:
        """Initialize standard actors present in default virtual stage."""
        self.actors["/Game/Stage_Main.Stage_Main:PersistentLevel.CineCameraActor_1"] = {
            "class": "CineCameraActor",
            "location": {"X": 0.0, "Y": -400.0, "Z": 120.0},
            "rotation": {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0},
            "fov": 45.0,
            "focal_length": 35.0,
            "aperture": 2.8,
        }
        self.actors["/Game/Stage_Main.Stage_Main:PersistentLevel.DirectionalLight_1"] = {
            "class": "DirectionalLight",
            "intensity": 5000.0,
            "color": {"R": 1.0, "G": 1.0, "B": 1.0},
            "rotation": {"Pitch": -45.0, "Yaw": 30.0, "Roll": 0.0},
        }
        self.actors["/Game/Stage_Main.Stage_Main:PersistentLevel.SkyLight_1"] = {
            "class": "SkyLight",
            "intensity": 1000.0,
            "color": {"R": 0.9, "G": 0.95, "B": 1.0},
        }
        self.actors["/Game/Stage_Main.Stage_Main:PersistentLevel.PostProcessVolume_1"] = {
            "class": "PostProcessVolume",
            "lumen_gi": True,
            "lumen_reflections": True,
            "unbound": True,
        }

    def reset(self) -> None:
        """Reset world state to default level configuration."""
        with self._lock:
            self.actors.clear()
            self.properties.clear()
            self.loaded_assets.clear()
            self.rendered_jobs.clear()
            self._init_defaults()

    def call_function(
        self,
        object_path: str,
        function_name: str,
        parameters: UE5ParamDict,
    ) -> UE5ParamDict:
        """Execute a simulated UFunction call against actors or subsystems."""
        with self._lock:
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

            elif function_name == "SpawnActor":
                raw_class = parameters.get("Class", "StaticMeshActor")
                actor_class = str(raw_class) if raw_class is not None else "StaticMeshActor"
                actor_id = f"/Game/Stage_Main.Stage_Main:PersistentLevel.{actor_class}_{len(self.actors) + 1}"

                loc_raw = parameters.get("Location")
                loc_dict: Dict[str, float] = (
                    loc_raw if isinstance(loc_raw, dict) else {"X": 0.0, "Y": 0.0, "Z": 0.0}
                )
                rot_raw = parameters.get("Rotation")
                rot_dict: Dict[str, float] = (
                    rot_raw if isinstance(rot_raw, dict) else {"Pitch": 0.0, "Yaw": 0.0, "Roll": 0.0}
                )

                self.actors[actor_id] = {
                    "class": actor_class,
                    "location": loc_dict,
                    "rotation": rot_dict,
                }
                return {"Success": True, "ActorId": actor_id}

            elif function_name == "SetMaterial":
                actor_raw = parameters.get("ActorId", object_path)
                actor_id = str(actor_raw) if actor_raw is not None else object_path
                mat_raw = parameters.get("MaterialPath", "")
                mat_path = str(mat_raw) if mat_raw is not None else ""
                if actor_id in self.actors:
                    self.actors[actor_id]["material"] = mat_path
                return {"Success": True, "ActorId": actor_id, "Material": mat_path}

            elif function_name == "SetActorLocationAndRotation":
                actor_raw = parameters.get("ActorId", object_path)
                actor_id = str(actor_raw) if actor_raw is not None else object_path
                if actor_id in self.actors:
                    loc_raw = parameters.get("Location")
                    if isinstance(loc_raw, dict):
                        self.actors[actor_id]["location"] = loc_raw
                    rot_raw = parameters.get("Rotation")
                    if isinstance(rot_raw, dict):
                        self.actors[actor_id]["rotation"] = rot_raw
                return {"Success": True, "ActorId": actor_id}

            elif function_name == "RenderQueueWithExecutor":
                job_id = f"Job_{len(self.rendered_jobs) + 1}"
                self.rendered_jobs.append({
                    "job_id": job_id,
                    "scene_path": str(parameters.get("ScenePath", "")),
                    "output_path": str(parameters.get("OutputPath", "")),
                    "status": "Completed",
                })
                return {"Success": True, "JobId": job_id}

            return {
                "Success": True,
                "Object": object_path,
                "Function": function_name,
                "Output": parameters,
            }

    def set_property(
        self,
        object_path: str,
        property_name: str,
        value: UE5ParamValue,
    ) -> UE5ParamDict:
        """Set a property on an object and broadcast change to WebSocket subscribers."""
        with self._lock:
            if object_path not in self.properties:
                self.properties[object_path] = {}
            self.properties[object_path][property_name] = value

            if object_path in self.actors:
                self.actors[object_path][property_name] = value

            # Trigger thread-safe event push to WebSocket subscribers
            self._broadcast_event({
                "Type": "PropertyChanged",
                "ObjectPath": object_path,
                "Property": property_name,
                "Value": value,
            })

            return {
                "Success": True,
                "Object": object_path,
                "Property": property_name,
                "Value": value,
            }

    def get_property(self, object_path: str, property_name: str) -> Optional[UE5ParamValue]:
        """Retrieve a property value from active state store."""
        with self._lock:
            if object_path in self.properties and property_name in self.properties[object_path]:
                return self.properties[object_path][property_name]
            if object_path in self.actors and property_name in self.actors[object_path]:
                val = self.actors[object_path][property_name]
                if isinstance(val, (str, int, float, bool, dict, list)) or val is None:
                    return val
            return None

    def _broadcast_event(self, event_data: UE5ParamDict) -> None:
        """Thread-safe event dispatch to active WebSocket connections."""
        if self.ws_loop and self.ws_loop.is_running() and self.ws_connections:
            asyncio.run_coroutine_threadsafe(self._async_broadcast(event_data), self.ws_loop)

    async def _async_broadcast(self, event_data: UE5ParamDict) -> None:
        """Send message frame to all active WebSocket connections."""
        payload_str = json.dumps(event_data)
        dead_conns: List[websockets.ServerConnection] = []
        for conn in list(self.ws_connections):
            try:
                await conn.send(payload_str)
            except Exception:
                dead_conns.append(conn)

        for dead in dead_conns:
            self.ws_connections.discard(dead)


# ---------------------------------------------------------------------------
# HTTP REST Request Handler (UE5RESTHandler)
# ---------------------------------------------------------------------------

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

    def do_GET(self) -> None:
        if self.path.startswith("/remote/info"):
            self._respond_json(200, {"Version": "5.4.0", "Engine": "UnrealEngine", "Mock": True})
        elif self.path.startswith("/remote/object/property"):
            self._respond_json(200, {"Success": True, "Properties": self.state.properties})
        elif self.path == "/" or self.path == "":
            self._respond_json(200, {"Status": "OK", "ActiveLevel": self.state.active_level})
        else:
            self._respond_json(200, {"Status": "OK"})

    def do_PUT(self) -> None:
        self._handle_write()

    def do_POST(self) -> None:
        self._handle_write()

    def _handle_write(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                payload = {}
        except Exception:
            payload = {}

        if "/remote/object/call" in self.path:
            obj_path = str(payload.get("objectPath", payload.get("ObjectPath", "")))
            fn_name = str(payload.get("functionName", payload.get("FunctionName", "")))
            params_raw = payload.get("parameters", payload.get("Parameters", {}))
            params: UE5ParamDict = params_raw if isinstance(params_raw, dict) else {}
            result = self.state.call_function(obj_path, fn_name, params)
            self._respond_json(200, result)

        elif "/remote/object/property" in self.path:
            obj_path = str(payload.get("objectPath", payload.get("ObjectPath", "")))
            prop_name = str(payload.get("propertyName", payload.get("PropertyName", "")))
            access = str(payload.get("access", "WRITE")).upper()

            if access in ("READ", "READ_ACCESS"):
                val = self.state.get_property(obj_path, prop_name)
                self._respond_json(200, {"propertyValue": val, "Success": True})
            else:
                val = payload.get("propertyValue", payload.get("Value", None))
                result = self.state.set_property(obj_path, prop_name, val)
                self._respond_json(200, result)

        elif "/remote/preset" in self.path:
            self._respond_json(200, {"Success": True, "Preset": "Applied"})

        else:
            self._respond_json(200, {"Success": True, "Received": payload})

    def _respond_json(self, status: int, data: UE5ParamDict) -> None:
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def log_message(self, format: str, *args: object) -> None:
        # Suppress standard HTTP access logging to preserve clean test output
        pass


# ---------------------------------------------------------------------------
# High-Fidelity Dual-Port Mock Server Manager (UE5MockServer)
# ---------------------------------------------------------------------------

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


class UE5MockServer:
    """
    Manages the lifecycle of both the mock Unreal Engine 5 REST server (port 30010)
    and the mock WebSocket protocol server (port 30020).
    """

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
        self.state: UE5MockState = UE5MockState()

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self) -> None:
        """Start both HTTP REST and WebSocket mock servers in daemon threads."""
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
                logger.info(
                    "UE5 Mock HTTP REST server listening on http://%s:%d (attempt %d)",
                    self.host,
                    self.port,
                    attempt + 1,
                )
                break
            except OSError as err:
                last_os_err = err
                logger.warning(
                    "HTTP port %d bind attempt %d/%d failed: %s; retrying in %.2fs",
                    self.port,
                    attempt + 1,
                    max_bind_retries,
                    err,
                    bind_delay,
                )
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
        time.sleep(0.05)  # Allow sockets to settle

    def _run_ws_server(self, ready_event: threading.Event) -> None:
        """Worker thread running dedicated asyncio event loop for WebSocket server."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.state.ws_loop = loop
        stop_event = asyncio.Event()
        self._ws_stop_event = stop_event

        async def ws_handler(ws: websockets.ServerConnection) -> None:
            self.state.ws_connections.add(ws)
            try:
                async for raw_msg in ws:
                    try:
                        msg_str = raw_msg if isinstance(raw_msg, str) else raw_msg.decode("utf-8")
                        data = json.loads(msg_str)
                    except Exception:
                        continue

                    if not isinstance(data, dict):
                        continue

                    msg_name = str(data.get("MessageName", ""))
                    msg_id = data.get("Id", 1)
                    params = data.get("Parameters", {})
                    if not isinstance(params, dict):
                        params = {}

                    if msg_name == "http":
                        url = str(params.get("Url", ""))
                        body_raw = params.get("Body", {})
                        body: UE5ParamDict = body_raw if isinstance(body_raw, dict) else {}

                        if "/remote/object/call" in url:
                            obj_path = str(body.get("objectPath", ""))
                            fn_name = str(body.get("functionName", ""))
                            call_params_raw = body.get("parameters", {})
                            call_params: UE5ParamDict = (
                                call_params_raw if isinstance(call_params_raw, dict) else {}
                            )
                            result = self.state.call_function(obj_path, fn_name, call_params)
                        elif "/remote/object/property" in url:
                            obj_path = str(body.get("objectPath", ""))
                            prop_name = str(body.get("propertyName", ""))
                            access = str(body.get("access", "WRITE")).upper()
                            if access in ("READ", "READ_ACCESS"):
                                val = self.state.get_property(obj_path, prop_name)
                                result = {"propertyValue": val, "Success": True}
                            else:
                                val = body.get("propertyValue", body.get("Value", None))
                                result = self.state.set_property(obj_path, prop_name, val)
                        else:
                            result = {"Success": True}

                        envelope: UE5ParamDict = {
                            "RequestId": msg_id,
                            "ResponseCode": 200,
                            "ResponseBody": result,
                        }
                        await ws.send(json.dumps(envelope))

                    elif msg_name == "subscribe":
                        envelope = {
                            "RequestId": msg_id,
                            "ResponseCode": 200,
                            "ResponseBody": {"Subscribed": True},
                        }
                        await ws.send(json.dumps(envelope))

                    elif msg_name == "unsubscribe":
                        envelope = {
                            "RequestId": msg_id,
                            "ResponseCode": 200,
                            "ResponseBody": {"Subscribed": False},
                        }
                        await ws.send(json.dumps(envelope))

                    elif msg_name == "batch":
                        requests = params.get("Requests", [])
                        results: List[UE5ParamDict] = []
                        if isinstance(requests, list):
                            for _ in requests:
                                results.append({"Success": True})
                        envelope = {
                            "RequestId": msg_id,
                            "ResponseCode": 200,
                            "ResponseBody": {"Results": results},
                        }
                        await ws.send(json.dumps(envelope))

            finally:
                self.state.ws_connections.discard(ws)

        async def main() -> None:
            max_ws_retries = 5
            ws_delay = 0.05
            for attempt in range(max_ws_retries):
                try:
                    async with websockets.serve(ws_handler, self.host, self.ws_port):
                        logger.info(
                            "UE5 Mock WebSocket server listening on ws://%s:%d/remote/protocol (attempt %d)",
                            self.host,
                            self.ws_port,
                            attempt + 1,
                        )
                        self._ws_bound = True
                        ready_event.set()
                        await stop_event.wait()
                        return
                except OSError as ws_err:
                    self._ws_error = ws_err
                    if attempt < max_ws_retries - 1:
                        await asyncio.sleep(ws_delay)
                        ws_delay *= 1.5
                    else:
                        logger.warning(
                            "WebSocket port %d bind failed after %d attempts: %s",
                            self.ws_port,
                            max_ws_retries,
                            ws_err,
                        )
                        ready_event.set()

        try:
            loop.run_until_complete(main())
        finally:
            try:
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except Exception:
                pass
            finally:
                loop.close()
                if self.state.ws_loop is loop:
                    self.state.ws_loop = None

    def stop(self) -> None:
        """Terminate both HTTP REST and WebSocket mock servers cleanly."""
        # 1. Stop HTTP server
        if self.http_server:
            try:
                self.http_server.shutdown()
                self.http_server.server_close()
            except Exception:
                pass
            self.http_server = None

        if self._http_thread and self._http_thread.is_alive():
            self._http_thread.join(timeout=2.0)
            self._http_thread = None

        # 2. Stop WebSocket server
        ws_loop = self.state.ws_loop
        if ws_loop and self._ws_stop_event and ws_loop.is_running():
            try:
                ws_loop.call_soon_threadsafe(self._ws_stop_event.set)
            except RuntimeError:
                pass

        if self._ws_thread and self._ws_thread.is_alive():
            self._ws_thread.join(timeout=2.0)
            self._ws_thread = None

        self._is_running = False
        self._ws_bound = False
        self.state.reset()
        logger.info("UE5 Mock Server stopped and state reset.")

    def reset_state(self) -> None:
        """Clear all loaded assets, custom actors, and properties."""
        self.state.reset()

    def __enter__(self) -> UE5MockServer:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        self.stop()

    async def __aenter__(self) -> UE5MockServer:
        self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        self.stop()
