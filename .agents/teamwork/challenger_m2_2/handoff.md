# Adversarial Challenge Report: Milestone 2 — Unreal Engine 5 Bridge Verification

**Agent**: `challenger_m2_2`  
**Role**: `critic`, `specialist` (Empirical Challenger)  
**Target Milestone**: Milestone 2: Unreal Engine 5 Bridge & Mock Server (`backend/ue5/`)  
**Parent Task ID**: `7287cd58-777e-4099-99af-79aab795ba88`  
**Date**: 2026-10-14  
**Verdict**: **REQUEST_CHANGES**

---

## 1. Observation

### 1.1 Baseline Test Suite Execution
- Command: `python -m pytest tests/backend/test_ue5_bridge.py -v`
- Result: **43 passed in 8.02s**.
- Observation: All nominal and basic boundary tests implemented by `worker_m2_1` pass without regressions.

### 1.2 AST-Level Zero-Any Verification
- Target directory: `backend/ue5/*.py` (7 files: `__init__.py`, `camera.py`, `client.py`, `lighting.py`, `materials.py`, `mock_server.py`, `mrq.py`).
- Analysis tool: `ast.NodeVisitor` parsing AST trees, checking `ast.Import`, `ast.ImportFrom`, `ast.Name(id="Any")`, and `ast.Constant(value="Any")`.
- Verbatim result: **0 occurrences of `Any`** across all AST nodes in `backend/ue5/`.
- Assessment: 100% compliant with the GEMINI.md Zero-Any policy.

### 1.3 PBR Material Boundary Conditions & Clamping
- Evaluated: `PBRMaterialInstance`, `MaterialManager.create_material()`, `create_pbr_material()`, and `PBRTextureSet`.
- Tested in `tests/backend/test_challenger_m2_2.py::TestPBRMaterialBoundaries`:
  - Out-of-bounds scalar inputs on `PBRMaterialInstance`:
    - `roughness` $\in \{-1.0, -0.0001, 1.0001, 2.0, \text{NaN}, \text{Inf}, -\text{Inf}\}$ correctly raise `pydantic.ValidationError`.
    - `metallic` and `specular` outside $[0.0, 1.0]$ correctly raise `ValidationError`.
    - `emissive_intensity < 0.0` correctly raises `ValidationError`.
    - `ColorRGB` with components outside $[0.0, 1.0]$ correctly raises `ValidationError`.
  - Robust value clamping in `MaterialManager.create_material()`:
    - Input values $-999.0$ and $+999.0$ are clamped to $0.0$ and $1.0$ respectively.
  - Strict dict coercion in `create_pbr_material()`:
    - Extra fields (e.g. `"alpha": 1.0` or `"unknown_slot"`) are rejected due to `extra="forbid"` on `StrictBaseModel`.
  - Texture path serialization in `to_ue5_parameters()`:
    - Empty string paths (`""`) and `None` paths are correctly omitted from UE5 parameter payloads (`AlbedoMap`, `NormalMap`, etc.), while valid non-empty paths are preserved.

### 1.4 Lumen Lighting Rig Presets & Fallbacks
- Evaluated: `LightingRig.get_preset()`, `setup_lumen_lighting()`, `LightActorConfig`, `LumenLightingSetup`.
- Tested in `tests/backend/test_challenger_m2_2.py::TestLumenLightingRigStress`:
  - All 5 standard presets (`studio_3point`, `cyberpunk_neon`, `dramatic`, `outdoor_sunlight`, `night_moonlight`) are properly calibrated with Lumen GI and reflections enabled.
  - Unknown preset fallbacks: Empty strings `""`, whitespace `"   "`, and unrecognized names (e.g. `"CUSTOM_LIGHTING"`, `"!@#$%^&*"`) safely fall back to `studio_3point` with 4 standard light actors.
  - Substring/case-insensitive matching works as intended (e.g. `"neon_lights"` -> `cyberpunk_neon`, `"night_sky"` -> `night_moonlight`).
- **Defects Identified**:
  1. `LightActorConfig.intensity` in `backend/ue5/lighting.py:29` has no lower bound constraint (`ge=0.0`). It permits negative intensities (e.g. `intensity = -5000.0`), which is non-physical in Lumen lighting and invalid in real PBR rendering.
  2. `LightingRig.get_preset()` lacks an `intensity_scale: float = 1.0` parameter to allow uniform photometric scaling across presets.
  3. `setup_lumen_lighting(None)` crashes with `AttributeError: 'NoneType' object has no attribute 'lower'` at `backend/ue5/lighting.py:57` instead of falling back to `"studio_3point"`.

### 1.5 Dynamic Asset Import Error Handling (Empirical Bug Confirmation)
- Investigated files: `backend/ue5/client.py` (lines 254–276, 464–486) and `backend/ue5/mock_server.py` (lines 116–130).
- **Observed Behavior via Empirical Testing**:
  1. **Corrupt GLB Containers**:
     - Test: `test_challenge_corrupt_glb_container_handling` in `tests/backend/test_challenger_m2_2.py`:
       - Zero-byte empty file: `empty_corrupt.glb` (0 bytes).
       - Bad magic file: `bad_magic.glb` (`b"NOT_A_GLTF_BINARY_FILE_GARBAGE"`).
       - Truncated GLB: `truncated.glb` (header specifies length 255, but file is 36 bytes, generated via `create_corrupt_glb`).
       - Plain text file renamed to `.glb`: `readme.glb`.
     - Actual response from `UE5RestClient.import_asset()` and `UE5MockServer.call_function("ImportAsset")`:
       ```json
       {"Success": true, "AssetPath": "/Game/Imported/empty_corrupt"}
       {"Success": true, "AssetPath": "/Game/Imported/bad_magic"}
       {"Success": true, "AssetPath": "/Game/Imported/truncated"}
       {"Success": true, "AssetPath": "/Game/Imported/readme"}
       ```
     - Verbatim error in `mock_server.py`:
       ```python
       # Lines 120-128 in backend/ue5/mock_server.py:
       if asset_path and not Path(asset_path).exists():
           return {"Success": False, "Error": f"Source asset not found: {asset_path}"}
       asset_stem = Path(asset_path).stem if asset_path else "ImportedAsset"
       asset_record = {
           "source": asset_path,
           "destination": dest_path,
           "asset_name": asset_stem,
       }
       self.loaded_assets.append(asset_record)
       return {"Success": True, "AssetPath": f"{dest_path}/{asset_stem}"}
       ```
     - Neither `client.py` nor `mock_server.py` performs any GLB binary container validation (12-byte Khronos header: magic `b"glTF"`, version 2, and total byte length). Corrupt assets are registered into `self.loaded_assets` and returned as successful.
  2. **Directory Paths Imported as Meshes**:
     - Test: `test_challenge_directory_path_rejected` in `tests/backend/test_challenger_m2_2.py`:
       - Invoking `client.import_asset(str(tmp_path))` or `client.import_asset(".")` succeeds with `{"Success": true, "AssetPath": "/Game/Imported/IANIMATION"}`!
       - Root cause: `path_obj.exists()` evaluates to `True` for directories on disk. Code lacks `path_obj.is_file()` validation.

---

## 2. Logic Chain

1. **Premise 1 (Acceptance & Specification Contract)**:
   - Milestone 2 acceptance criteria and `PROJECT.md` require: *"Dynamic runtime asset loading for .glb and .fbx meshes"* producing verifiable structured success/error codes.
   - Dispatch focus areas specifically mandated: *"Dynamic asset import error handling on malformed/corrupt GLB files and non-existent paths."*
   - Tier 2 E2E test `test_f_ue5_04_corrupt_glb_import_failure` requires: *"UE5 asset importer returns structured error on malformed glTF binary."*
2. **Premise 2 (Empirical Reproduction)**:
   - When a 0-byte file, an invalid magic file, or a truncated GLB is passed to `UE5RestClient.import_asset()`, the client sends `SourcePath` to `mock_server.py`.
   - `mock_server.py` evaluates only `Path(asset_path).exists()`. Because the file exists on the filesystem, it returns `{"Success": True, "AssetPath": "..."}` and stores the corrupt asset into `loaded_assets`.
   - When a directory path (e.g. `"."`) is passed, `Path.exists()` evaluates to `True`, causing a directory to be imported as a 3D asset mesh.
3. **Premise 3 (Blast Radius Assessment)**:
   - In production and downstream milestones (M3 AI Pipelines, M4 FastMCP, M6 Integration), if an upstream provider (Tripo, Fal, or procedural generator) produces a corrupt GLB or fails mid-generation, `build_ue5_scene` and `render_video` will receive a fictitious `Success: True` response.
   - Downstream actors and movie render queues will fail unexpectedly later in the pipeline with cryptic engine crashes rather than catching the asset error early at the boundary.
4. **Conclusion**:
   - `backend/ue5/` is 90% complete and highly functional, but fails the dynamic asset import error handling requirement on corrupt GLBs and directory paths.
   - A verdict of **REQUEST_CHANGES** is necessary to harden `client.py` and `mock_server.py` before downstream milestones depend on it.

---

## 3. Caveats

- All 43 tests in `tests/backend/test_ue5_bridge.py` pass cleanly.
- The 52 passed tests in `tests/backend/test_challenger_m2_2.py` verify that camera choreography, PBR materials, Lumen presets, AST Zero-Any compliance, and nominal asset importing are solid.
- The findings are localized to container validation in `backend/ue5/client.py`, `backend/ue5/mock_server.py`, and minor validation in `backend/ue5/lighting.py`.

---

## 4. Conclusion & Required Changes

**Verdict**: **REQUEST_CHANGES**

### Required Action Items for Worker (`worker_m2_1`):

1. **GLB & Asset Container Validation in `backend/ue5/client.py`**:
   - In both `UE5RestClient.import_asset()` (line 254) and `AsyncUE5RestClient.import_asset()` (line 464):
     ```python
     path_obj = Path(source_path)
     if not path_obj.exists() or not path_obj.is_file():
         return {
             "Success": False,
             "Error": f"Asset file does not exist or is not a regular file: {source_path}",
             "AssetPath": "",
         }

     # Validate binary container if .glb
     if path_obj.suffix.lower() == ".glb":
         file_size = path_obj.stat().st_size
         if file_size < 12:
             return {
                 "Success": False,
                 "Error": f"Corrupt GLB file: file size {file_size} bytes is smaller than 12-byte header ({source_path})",
                 "AssetPath": "",
             }
         with open(path_obj, "rb") as f:
             header = f.read(12)
         magic, version, total_length = struct.unpack("<4sII", header)
         if magic != b"glTF" or version != 2 or total_length != file_size:
             return {
                 "Success": False,
                 "Error": f"Invalid or corrupt GLB header in {source_path} (magic={magic!r}, version={version}, total_length={total_length}, actual={file_size})",
                 "AssetPath": "",
             }
     ```

2. **GLB Container Validation in `backend/ue5/mock_server.py`**:
   - In `UE5MockState.call_function("ImportAsset")` (line 116):
     - Perform identical validation: verify `path_obj.is_file()`, and if `.glb`, verify 12-byte header (`magic == b"glTF"`, `version == 2`, `total_length == file_size`).
     - Return `{"Success": False, "Error": f"Corrupt or malformed GLB asset: {asset_path}"}` upon container validation failure.

3. **Photometric Validation in `backend/ue5/lighting.py`**:
   - In `LightActorConfig` (line 29):
     `intensity: float = Field(default=5000.0, ge=0.0, description="Luminous flux in Lumens or illuminance in Lux")`
   - In `setup_lumen_lighting(preset: Optional[str] = "studio_3point", intensity_scale: float = 1.0)`:
     Handle `preset is None` by safely defaulting: `name = str(preset or "studio_3point").lower().strip()`.
     If `intensity_scale != 1.0`, multiply each light's intensity by `max(0.0, intensity_scale)`.

---

## 5. Verification Method

To verify the challenges and confirm the fixes:

1. **Run Full Baseline Bridge Tests**:
   ```powershell
   python -m pytest tests/backend/test_ue5_bridge.py -v
   ```
   *Expected*: 43 passed.

2. **Run Challenger Stress Suite**:
   ```powershell
   python -m pytest tests/backend/test_challenger_m2_2.py -v
   ```
   *Current Result*: 52 passed, 2 xfailed.  
   *Post-Fix Result*: 54 passed (0 xfailed).

3. **Direct Reproduction of the Defect**:
   ```powershell
   python -c "
   from pathlib import Path
   from backend.ue5.client import UE5RestClient
   from backend.ue5.mock_server import UE5MockServer
   from tests.e2e.fixtures.synthetic_mesh import create_corrupt_glb

   server = UE5MockServer(port=30090, ws_port=30091)
   server.start()
   client = UE5RestClient(port=30090)

   corrupt_file = Path('temp_corrupt.glb')
   create_corrupt_glb(corrupt_file)

   res = client.import_asset(str(corrupt_file))
   print('Result with corrupt GLB:', res)

   server.stop()
   corrupt_file.unlink(missing_ok=True)
   "
   ```
   *Current Output*: `{'Success': True, 'AssetPath': '/Game/Imported/temp_corrupt'}` (BUG: accepted).  
   *Target Fixed Output*: `{'Success': False, 'Error': 'Invalid or corrupt GLB header...', 'AssetPath': ''}`.
