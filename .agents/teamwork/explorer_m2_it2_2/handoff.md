# Handoff Report: Milestone 2 — Remediation Design for `backend/ue5/client.py`

**Agent**: `explorer_m2_it2_2`  
**Working Directory**: `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m2_it2_2`  
**Date**: 2026-10-14  
**Target File**: `backend/ue5/client.py`  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Handoff Type**: Hard (Complete Drop-In Remediation Design)  

---

## 1. Observation

### 1.1 Direct Repository Evidence in `backend/ue5/client.py`

#### Finding A: Inadequate GLB Header Validation in `_validate_glb_container()`
In `backend/ue5/client.py`, lines 117–133:
```python
def _validate_glb_container(path: Path) -> Optional[str]:
    """Validate binary glTF container header, magic bytes, and length."""
    if path.suffix.lower() != ".glb":
        return None
    try:
        data = path.read_bytes()
        if len(data) < 12:
            return f"Corrupt GLB: file size ({len(data)} bytes) is smaller than 12-byte header"
        magic, version, total_length = struct.unpack("<4sII", data[:12])
        if magic != b"glTF":
            return f"Corrupt GLB: invalid magic {magic!r}"
        if len(data) < total_length:
            return f"Corrupt GLB: truncated buffer ({len(data)} < {total_length} bytes)"
        return None
    except Exception as err:
        return f"Cannot read GLB container: {err}"
```
**Defects Observed**:
1. **Unchecked Version**: `version` is unpacked on line 125 but never validated. glTF 2.0 requires `version == 2`. Files with invalid versions (e.g. version 1 or garbage) pass validation.
2. **Non-Conforming Length Check**: Line 128 evaluates `if len(data) < total_length:`. The Khronos glTF 2.0 specification requires exact length equality: `total_length == file_size`. Padded files with trailing garbage bypass validation.
3. **Memory Inefficiency**: `path.read_bytes()` reads the entire file into RAM, which causes severe memory overhead and stalls on production 3D assets (e.g. 50–500 MB GLB meshes). Only the 12-byte header needs to be read from disk alongside `path.stat().st_size`.

#### Finding B: Incomplete Path Validation in `import_asset()` (Sync and Async)
In `backend/ue5/client.py`, lines 272–291 (`UE5RestClient.import_asset`) and lines 496–515 (`AsyncUE5RestClient.import_asset`):
```python
if not source_path or not source_path.strip():
    return {
        "Success": False,
        "Error": f"Asset file does not exist: {source_path}",
        "AssetPath": "",
    }
path_obj = Path(source_path)
if not path_obj.exists() or not path_obj.is_file():
...
```
**Defects Observed**:
1. If `source_path` is not a string (e.g. `None` passed in unvalidated runtime contexts), calling `.strip()` can raise `AttributeError`. A type check `not isinstance(source_path, str) or not source_path.strip()` ensures bulletproof input validation.
2. The error message on empty or whitespace paths should explicitly indicate that the path cannot be empty while containing `"does not exist"` to satisfy all boundary assertions across test suites (`assert "does not exist" in str(res.get("Error", ""))`).
3. Must guarantee that both `path_obj.exists()` and `path_obj.is_file()` are strictly verified to prevent directory paths (e.g. `"."` or `tmp_path`) from being treated as meshes (Challenger M2_2 Finding 1.5, Finding 4).

#### Finding C: Offline Development Fallback Masks Server-Side Error Responses
In `backend/ue5/client.py`, lines 222–231 (`UE5RestClient.call`) and lines 447–455 (`AsyncUE5RestClient.call`):
```python
res = self._request("PUT", "/remote/object/call", payload)
if not res.get("Success", True) and "Error" in res:
    # Fallback simulated response for offline development
    return {
        "Success": True,
        "Object": object_path,
        "Function": function_name,
        "Output": parameters if parameters is not None else {},
    }
return res
```
And similarly in `set_property()` (lines 248–256 and 472–480):
```python
res = self._request("PUT", "/remote/object/property", payload)
if not res.get("Success", True) and "Error" in res:
    return {
        "Success": True,
        "Object": object_path,
        "Property": property_name,
        "Value": value,
    }
return res
```
**Defects Observed (Reviewer M2_1 Finding 3.1)**:
When `_request` executes against a live Unreal Engine editor or `UE5MockServer`:
- If the server returns a legitimate error (e.g. `{"Success": False, "Error": "Source asset not found: missing.glb"}` or HTTP 400/500 with `{"Success": False, "Error": "...", "StatusCode": 400}`), `not res.get("Success", True) and "Error" in res` evaluates to `True`.
- `client.call()` **overwrites the real server error** and returns `{"Success": True, ...}`, falsely reporting success when the remote engine operation failed!
- The offline fallback was meant solely for when UE5 is completely offline/unreachable (`urllib.error.URLError`, `ConnectionError`, `ClientConnectorError`, `TimeoutError`, `OSError`).

---

## 2. Logic Chain

1. **Asset Boundary Defense**:
   - Upstream AI generative adapters (Fal.ai, Tripo, ComfyUI, procedural stubs) deliver `.glb` files. If an upstream generator fails mid-stream, produces an empty file, or truncates the buffer, passing that file to Unreal Engine causes engine crashes or corrupted asset registries.
   - Client-side validation in `import_asset()` ensures invalid containers are rejected immediately with structured error responses (`{"Success": False, "Error": "...", "AssetPath": ""}`) without placing load on the game engine.

2. **Khronos glTF 2.0 Binary Specification Contract**:
   - A conforming `.glb` file starts with a fixed 12-byte header:
     - Byte 0–3: `magic` (uint32 little-endian `0x46546C67`, ASCII `b"glTF"`)
     - Byte 4–7: `version` (uint32 little-endian `2`)
     - Byte 8–11: `total_length` (uint32 little-endian total file size in bytes)
   - Validation requires:
     a. `file_size = path.stat().st_size >= 12`
     b. `magic == b"glTF"`
     c. `version == 2`
     d. `total_length == file_size`
   - Reading only the first 12 bytes via `open(path, "rb").read(12)` checks container integrity in $O(1)$ memory without loading large binaries into RAM.

3. **Narrowing the Offline Fallback**:
   - `_request()` in `UE5RestClient` catches `urllib.error.HTTPError` on HTTP responses, and `(urllib.error.URLError, ConnectionError, TimeoutError, OSError)` on network transport failures.
   - `_request()` in `AsyncUE5RestClient` handles `resp.status >= 400` on HTTP responses, and `(aiohttp.ClientError, asyncio.TimeoutError, OSError)` on network transport failures.
   - By tagging `"ConnectionFailure": True` on genuine network failures (where no HTTP response could be obtained from the remote host) and providing a dedicated helper `_is_connection_failure(res: UE5ParamDict) -> bool`:
     - Offline development fallback triggers **only** when `_is_connection_failure(res)` is `True` (preserving the offline development workflow and passing `test_client_timeout_handling` and `test_client_offline_graceful_fallback`).
     - Real error responses from the engine or mock server (`{"Success": False, "Error": "..."}`) have `_is_connection_failure(res) == False` and are **passed through intact** to the caller.

---

## 3. Concrete Drop-In Remediation Design

### Component 1: Upgraded `_validate_glb_container()` Function

```python
def _validate_glb_container(path: Path) -> Optional[str]:
    """
    Validate binary glTF 2.0 container header, magic bytes, version, and length.

    Checks:
    1. File size >= 12 bytes.
    2. Header magic == b"glTF".
    3. Header version == 2.
    4. Header total_length == file_size.

    Returns None if valid, or a descriptive error string if corrupt or malformed.
    """
    if path.suffix.lower() != ".glb":
        return None
    try:
        file_size = path.stat().st_size
        if file_size < 12:
            return (
                f"Corrupt GLB file: file size ({file_size} bytes) "
                f"is smaller than 12-byte header ({path})"
            )
        with open(path, "rb") as f:
            header = f.read(12)
        if len(header) < 12:
            return f"Corrupt GLB file: unable to read 12-byte header from {path}"

        magic, version, total_length = struct.unpack("<4sII", header)
        if magic != b"glTF":
            return f"Corrupt GLB file: invalid magic {magic!r} in {path} (expected b'glTF')"
        if version != 2:
            return f"Corrupt GLB file: unsupported version {version} in {path} (expected 2)"
        if total_length != file_size:
            return (
                f"Corrupt GLB file: container length mismatch in {path} "
                f"(header declares {total_length} bytes, actual file size is {file_size} bytes)"
            )
        return None
    except OSError as err:
        return f"Cannot read GLB container {path}: {err}"
```

### Component 2: Dedicated `_is_connection_failure()` Helper

```python
def _is_connection_failure(res: UE5ParamDict) -> bool:
    """
    Determine if a REST response represents an unreachable host or connection transport failure.

    Returns True ONLY when the client could not establish a connection to the server
    (e.g., host unreachable, URLError, ClientConnectorError, connection refused, or timeout),
    and False if the server was reached (even if it returned HTTP 4xx/5xx or application Success: False).
    """
    if res.get("Success") is True:
        return False
    if res.get("ConnectionFailure") is True or res.get("ConnectionError") is True:
        return True
    # If the server returned an HTTP status code, the server was reached; not a transport failure
    if "StatusCode" in res:
        return False
    # If ConnectionFailure flag was not set but error originated from transport failure without StatusCode
    if "Endpoint" in res and "Error" in res:
        err_lower = str(res.get("Error", "")).lower()
        transport_markers = (
            "connection refused",
            "winerror 10061",
            "winerror 10054",
            "winerror 10060",
            "urlerror",
            "clientconnectorerror",
            "cannot connect",
            "timed out",
            "timeout",
            "unreachable",
            "no route to host",
        )
        return any(marker in err_lower for marker in transport_markers)
    return False
```

### Component 3: Narrowed Fallback and Dynamic Validation in `UE5RestClient`

```python
    def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[UE5ParamDict] = None,
    ) -> UE5ParamDict:
        """Execute HTTP request with retry logic and fallback."""
        url = f"{self.base_url}{endpoint}"
        data_bytes = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Content-Type": "application/json"} if payload is not None else {}

        last_error: Optional[Exception] = None
        max_attempts = self.retry_config.max_retries + 1

        for attempt in range(max_attempts):
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    if raw:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict):
                            result: UE5ParamDict = parsed
                            return result
                    return {"Success": True}
            except (urllib.error.HTTPError) as http_err:
                last_error = http_err
                # Retry on server errors (502, 503, 504)
                if http_err.code in (502, 503, 504) and attempt < max_attempts - 1:
                    time.sleep(self.retry_config.calculate_delay(attempt))
                    continue
                try:
                    error_body = http_err.read().decode("utf-8")
                    error_json = json.loads(error_body) if error_body else {}
                    err_msg = str(error_json.get("errorMessage", str(http_err)))
                except Exception:
                    err_msg = str(http_err)
                logger.debug("UE5 REST HTTP error (%s %s): %s", method, endpoint, err_msg)
                return {"Success": False, "Error": err_msg, "StatusCode": http_err.code}
            except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as net_err:
                last_error = net_err
                if attempt < max_attempts - 1:
                    time.sleep(self.retry_config.calculate_delay(attempt))
                    continue
                break

        logger.debug("UE5 REST request failed after retries (%s %s): %s", method, endpoint, last_error)
        return {
            "Success": False,
            "Error": str(last_error),
            "Endpoint": endpoint,
            "ConnectionFailure": True,
        }

    def call(
        self,
        object_path: str,
        function_name: str,
        parameters: Optional[UE5ParamDict] = None,
        generate_transaction: bool = False,
    ) -> UE5ParamDict:
        """Invoke an Unreal Engine function on an actor or UObject via PUT /remote/object/call."""
        payload: UE5ParamDict = {
            "objectPath": object_path,
            "functionName": function_name,
            "parameters": parameters if parameters is not None else {},
            "generateTransaction": generate_transaction,
        }
        res = self._request("PUT", "/remote/object/call", payload)
        if _is_connection_failure(res):
            # Fallback simulated response strictly for offline development when host is unreachable
            return {
                "Success": True,
                "Object": object_path,
                "Function": function_name,
                "Output": parameters if parameters is not None else {},
            }
        return res

    def set_property(
        self,
        object_path: str,
        property_name: str,
        value: UE5ParamValue,
        generate_transaction: bool = False,
    ) -> UE5ParamDict:
        """Set a property value on an actor or component via PUT /remote/object/property."""
        payload: UE5ParamDict = {
            "objectPath": object_path,
            "propertyName": property_name,
            "access": "WRITE",
            "propertyValue": value,
            "generateTransaction": generate_transaction,
        }
        res = self._request("PUT", "/remote/object/property", payload)
        if _is_connection_failure(res):
            return {
                "Success": True,
                "Object": object_path,
                "Property": property_name,
                "Value": value,
            }
        return res

    def import_asset(
        self,
        source_path: str,
        destination_path: str = "/Game/Imported",
    ) -> UE5ParamDict:
        """Dynamically import a 3D asset (.glb, .gltf, .fbx) into Unreal Engine Content Browser."""
        # 1. Validate that source_path is non-empty string and not whitespace
        if not isinstance(source_path, str) or not source_path.strip():
            return {
                "Success": False,
                "Error": f"Asset file does not exist: source path cannot be empty or whitespace ({source_path!r})",
                "AssetPath": "",
            }

        # 2. Validate path_obj.exists() and path_obj.is_file()
        path_obj = Path(source_path)
        if not path_obj.exists() or not path_obj.is_file():
            return {
                "Success": False,
                "Error": f"Asset file does not exist or is not a regular file: {source_path}",
                "AssetPath": "",
            }

        # 3. If .glb, validate 12-byte header
        glb_err = _validate_glb_container(path_obj)
        if glb_err:
            return {
                "Success": False,
                "Error": glb_err,
                "AssetPath": "",
            }

        params: UE5ParamDict = {
            "SourcePath": str(path_obj.resolve()),
            "DestinationPath": destination_path,
        }
        return self.call(
            object_path="/Script/UnrealEd.Default__EditorAssetLibrary",
            function_name="ImportAsset",
            parameters=params,
        )
```

### Component 4: Narrowed Fallback and Dynamic Validation in `AsyncUE5RestClient`

```python
    async def _request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[UE5ParamDict] = None,
    ) -> UE5ParamDict:
        """Asynchronously execute HTTP request with retry logic."""
        await self.open()
        assert self._session is not None

        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        last_error: Optional[Exception] = None
        max_attempts = self.retry_config.max_retries + 1

        for attempt in range(max_attempts):
            try:
                async with self._session.request(method, url, json=payload, headers=headers) as resp:
                    raw = await resp.text()
                    if resp.status in (502, 503, 504) and attempt < max_attempts - 1:
                        await asyncio.sleep(self.retry_config.calculate_delay(attempt))
                        continue
                    if resp.status >= 400:
                        try:
                            error_json = json.loads(raw)
                            err_msg = str(error_json.get("errorMessage", f"HTTP {resp.status}"))
                        except Exception:
                            err_msg = f"HTTP {resp.status}: {raw}"
                        return {"Success": False, "Error": err_msg, "StatusCode": resp.status}

                    if raw:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict):
                            result: UE5ParamDict = parsed
                            return result
                    return {"Success": True}
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as err:
                last_error = err
                if attempt < max_attempts - 1:
                    await asyncio.sleep(self.retry_config.calculate_delay(attempt))
                    continue
                break

        logger.debug("Async UE5 REST request failed (%s %s): %s", method, endpoint, last_error)
        return {
            "Success": False,
            "Error": str(last_error),
            "Endpoint": endpoint,
            "ConnectionFailure": True,
        }

    async def call(
        self,
        object_path: str,
        function_name: str,
        parameters: Optional[UE5ParamDict] = None,
        generate_transaction: bool = False,
    ) -> UE5ParamDict:
        """Asynchronously invoke an Unreal Engine function on an actor or UObject."""
        payload: UE5ParamDict = {
            "objectPath": object_path,
            "functionName": function_name,
            "parameters": parameters if parameters is not None else {},
            "generateTransaction": generate_transaction,
        }
        res = await self._request("PUT", "/remote/object/call", payload)
        if _is_connection_failure(res):
            # Fallback simulated response strictly for offline development when host is unreachable
            return {
                "Success": True,
                "Object": object_path,
                "Function": function_name,
                "Output": parameters if parameters is not None else {},
            }
        return res

    async def set_property(
        self,
        object_path: str,
        property_name: str,
        value: UE5ParamValue,
        generate_transaction: bool = False,
    ) -> UE5ParamDict:
        """Asynchronously set a property value on an actor or component."""
        payload: UE5ParamDict = {
            "objectPath": object_path,
            "propertyName": property_name,
            "access": "WRITE",
            "propertyValue": value,
            "generateTransaction": generate_transaction,
        }
        res = await self._request("PUT", "/remote/object/property", payload)
        if _is_connection_failure(res):
            return {
                "Success": True,
                "Object": object_path,
                "Property": property_name,
                "Value": value,
            }
        return res

    async def import_asset(
        self,
        source_path: str,
        destination_path: str = "/Game/Imported",
    ) -> UE5ParamDict:
        """Asynchronously import a 3D asset (.glb, .gltf, .fbx) into Content Browser."""
        # 1. Validate that source_path is non-empty string and not whitespace
        if not isinstance(source_path, str) or not source_path.strip():
            return {
                "Success": False,
                "Error": f"Asset file does not exist: source path cannot be empty or whitespace ({source_path!r})",
                "AssetPath": "",
            }

        # 2. Validate path_obj.exists() and path_obj.is_file()
        path_obj = Path(source_path)
        if not path_obj.exists() or not path_obj.is_file():
            return {
                "Success": False,
                "Error": f"Asset file does not exist or is not a regular file: {source_path}",
                "AssetPath": "",
            }

        # 3. If .glb, validate 12-byte header
        glb_err = _validate_glb_container(path_obj)
        if glb_err:
            return {
                "Success": False,
                "Error": glb_err,
                "AssetPath": "",
            }

        params: UE5ParamDict = {
            "SourcePath": str(path_obj.resolve()),
            "DestinationPath": destination_path,
        }
        return await self.call(
            object_path="/Script/UnrealEd.Default__EditorAssetLibrary",
            function_name="ImportAsset",
            parameters=params,
        )
```

---

## 4. Complete Drop-In Patch for `backend/ue5/client.py`

Below is the unified patch applying these remediations cleanly:

```diff
--- a/backend/ue5/client.py
+++ b/backend/ue5/client.py
@@ -117,17 +117,62 @@
 def _validate_glb_container(path: Path) -> Optional[str]:
-    """Validate binary glTF container header, magic bytes, and length."""
+    """
+    Validate binary glTF 2.0 container header, magic bytes, version, and length.
+
+    Checks:
+    1. File size >= 12 bytes.
+    2. Header magic == b"glTF".
+    3. Header version == 2.
+    4. Header total_length == file_size.
+
+    Returns None if valid, or a descriptive error string if corrupt or malformed.
+    """
     if path.suffix.lower() != ".glb":
         return None
     try:
-        data = path.read_bytes()
-        if len(data) < 12:
-            return f"Corrupt GLB: file size ({len(data)} bytes) is smaller than 12-byte header"
-        magic, version, total_length = struct.unpack("<4sII", data[:12])
+        file_size = path.stat().st_size
+        if file_size < 12:
+            return (
+                f"Corrupt GLB file: file size ({file_size} bytes) "
+                f"is smaller than 12-byte header ({path})"
+            )
+        with open(path, "rb") as f:
+            header = f.read(12)
+        if len(header) < 12:
+            return f"Corrupt GLB file: unable to read 12-byte header from {path}"
+
+        magic, version, total_length = struct.unpack("<4sII", header)
         if magic != b"glTF":
-            return f"Corrupt GLB: invalid magic {magic!r}"
-        if len(data) < total_length:
-            return f"Corrupt GLB: truncated buffer ({len(data)} < {total_length} bytes)"
+            return f"Corrupt GLB file: invalid magic {magic!r} in {path} (expected b'glTF')"
+        if version != 2:
+            return f"Corrupt GLB file: unsupported version {version} in {path} (expected 2)"
+        if total_length != file_size:
+            return (
+                f"Corrupt GLB file: container length mismatch in {path} "
+                f"(header declares {total_length} bytes, actual file size is {file_size} bytes)"
+            )
         return None
-    except Exception as err:
-        return f"Cannot read GLB container: {err}"
+    except OSError as err:
+        return f"Cannot read GLB container {path}: {err}"
+
+
+def _is_connection_failure(res: UE5ParamDict) -> bool:
+    """
+    Determine if a REST response represents an unreachable host or connection transport failure.
+
+    Returns True ONLY when the client could not establish a connection to the server
+    (e.g., host unreachable, URLError, ClientConnectorError, connection refused, or timeout),
+    and False if the server was reached (even if it returned HTTP 4xx/5xx or application Success: False).
+    """
+    if res.get("Success") is True:
+        return False
+    if res.get("ConnectionFailure") is True or res.get("ConnectionError") is True:
+        return True
+    if "StatusCode" in res:
+        return False
+    if "Endpoint" in res and "Error" in res:
+        err_lower = str(res.get("Error", "")).lower()
+        transport_markers = (
+            "connection refused",
+            "winerror 10061",
+            "winerror 10054",
+            "winerror 10060",
+            "urlerror",
+            "clientconnectorerror",
+            "cannot connect",
+            "timed out",
+            "timeout",
+            "unreachable",
+            "no route to host",
+        )
+        return any(marker in err_lower for marker in transport_markers)
+    return False
@@ -204,3 +249,7 @@
         logger.debug("UE5 REST request failed after retries (%s %s): %s", method, endpoint, last_error)
-        return {"Success": False, "Error": str(last_error), "Endpoint": endpoint}
+        return {
+            "Success": False,
+            "Error": str(last_error),
+            "Endpoint": endpoint,
+            "ConnectionFailure": True,
+        }
 
     def call(
@@ -222,4 +271,4 @@
         res = self._request("PUT", "/remote/object/call", payload)
-        if not res.get("Success", True) and "Error" in res:
-            # Fallback simulated response for offline development
+        if _is_connection_failure(res):
+            # Fallback simulated response strictly for offline development when host is unreachable
             return {
@@ -248,3 +297,3 @@
         res = self._request("PUT", "/remote/object/property", payload)
-        if not res.get("Success", True) and "Error" in res:
+        if _is_connection_failure(res):
             return {
@@ -277,8 +326,9 @@
         """Dynamically import a 3D asset (.glb, .gltf, .fbx) into Unreal Engine Content Browser."""
-        if not source_path or not source_path.strip():
+        if not isinstance(source_path, str) or not source_path.strip():
             return {
                 "Success": False,
-                "Error": f"Asset file does not exist: {source_path}",
+                "Error": f"Asset file does not exist: source path cannot be empty or whitespace ({source_path!r})",
                 "AssetPath": "",
             }
         path_obj = Path(source_path)
@@ -430,3 +480,7 @@
         logger.debug("Async UE5 REST request failed (%s %s): %s", method, endpoint, last_error)
-        return {"Success": False, "Error": str(last_error), "Endpoint": endpoint}
+        return {
+            "Success": False,
+            "Error": str(last_error),
+            "Endpoint": endpoint,
+            "ConnectionFailure": True,
+        }
 
     async def call(
@@ -447,3 +501,4 @@
         res = await self._request("PUT", "/remote/object/call", payload)
-        if not res.get("Success", True) and "Error" in res:
+        if _is_connection_failure(res):
+            # Fallback simulated response strictly for offline development when host is unreachable
             return {
@@ -472,3 +527,3 @@
         res = await self._request("PUT", "/remote/object/property", payload)
-        if not res.get("Success", True) and "Error" in res:
+        if _is_connection_failure(res):
             return {
@@ -501,8 +556,9 @@
         """Asynchronously import a 3D asset (.glb, .gltf, .fbx) into Content Browser."""
-        if not source_path or not source_path.strip():
+        if not isinstance(source_path, str) or not source_path.strip():
             return {
                 "Success": False,
-                "Error": f"Asset file does not exist: {source_path}",
+                "Error": f"Asset file does not exist: source path cannot be empty or whitespace ({source_path!r})",
                 "AssetPath": "",
             }
         path_obj = Path(source_path)
```

---

## 5. Caveats

1. **Non-GLB Formats**:
   - For other 3D formats (such as `.fbx` and `.gltf`), the client verifies that the file exists on disk and is a regular file (`path_obj.exists() and path_obj.is_file()`). Binary container parsing is specific to `.glb` (glTF 2.0 binary). FBX binary containers remain validated by Unreal Engine's native FBX importer.
2. **Offline Mode Contract**:
   - The offline simulated response is retained strictly for offline developer workflows when no engine instance or mock server is listening on the configured HTTP port. With `_is_connection_failure()`, genuine server responses returning `Success: False` are never masked.
3. **Zero-Any Typing Policy**:
   - All proposed additions and signatures strictly utilize concrete types and `UE5ParamDict` (`Dict[str, UE5ParamValue]`). No `Any` annotations or imports are introduced.

---

## 6. Conclusion

The proposed drop-in design addresses all reported defects:
1. **Dynamic Asset Integrity**: Malformed GLB files (0-byte, invalid magic, wrong version, truncated buffers), directory paths, empty strings, and whitespace strings are rejected deterministically before dispatching to UE5.
2. **Reliable Error Propagation**: The offline development fallback is strictly confined to genuine network connection failures, ensuring server-returned errors (`Success: False`) are surfaced accurately.
3. **Zero-Any Strict Compliance**: Fully complies with GEMINI.md engineering standards and Clean Architecture modularity.

---

## 7. Verification Method

Once applied by the worker, the following independent tests verify the fix:

### 7.1 Verify Corrupt GLB and Directory Import Handling
```powershell
python -m pytest tests/backend/test_challenger_m2_2.py -k "test_challenge_corrupt_glb_container_handling or test_challenge_directory_path_rejected or test_import_asset_empty_string_path" -v
```
*Expected*: All tests pass without xfail or assertion failures.

### 7.2 Verify Offline Fallback and Timeout Handling
```powershell
python -m pytest tests/backend/test_ue5_bridge.py -k "test_client_timeout_handling or test_client_offline_graceful_fallback" -v
```
*Expected*: 2 passed (offline fallback functions when target port is unreachable).

### 7.3 Verify Server-Side Error Preservation (Reviewer Finding 3.1)
```powershell
python -c "
from backend.ue5.client import UE5RestClient
from backend.ue5.mock_server import UE5MockServer

server = UE5MockServer(host='127.0.0.1', port=30089, ws_port=30099)
server.start()
try:
    client = UE5RestClient(host='127.0.0.1', port=30089)
    res = client.call('/Script/EditorAssetLibrary', 'ImportAsset', {'SourcePath': 'missing_file.glb'})
    assert res.get('Success') is False, f'Error masked! Got: {res}'
    assert 'not found' in str(res.get('Error', ''))
    print('PASS: Real server error preserved correctly!')
finally:
    server.stop()
"
```
*Expected*: `PASS: Real server error preserved correctly!`.

### 7.4 Verify 100% Zero-Any Compliance via AST
```powershell
python -c "
import ast
tree = ast.parse(open('backend/ue5/client.py', encoding='utf-8').read(), filename='backend/ue5/client.py')
found = []
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and any(a.name == 'Any' for a in node.names):
        found.append(('Import Any', node.lineno))
    elif isinstance(node, ast.Name) and node.id == 'Any':
        found.append(('Name Any', node.lineno))
assert len(found) == 0, f'Found Any: {found}'
print('PASS: 100% Zero-Any AST check passed!')
"
```
*Expected*: `PASS: 100% Zero-Any AST check passed!`.
