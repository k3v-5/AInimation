# Milestone 7 Architectural, Gate & Adversarial Review Report

- **Date**: 2026-10-14T03:35:30Z
- **Reviewer**: `reviewer_m7_1` (Archetype: reviewer, Roles: reviewer, critic)
- **Target**: Milestone 7 (Full Verification, E2E Gate, Architecture & Quality)
- **Verdict**: **REQUEST_CHANGES**

---

## 1. Review Summary

| Evaluation Dimension | Status | Notes |
|---|---|---|
| **E2E Test Execution** | PASS (58/58) | Standalone runner & pytest pass all 4 tiers (116.90s / 91.61s) |
| **Backend Test Execution** | PASS (664/664) | Core & UE5 suites pass in 35.60s |
| **Frontend Test & Build** | PASS (10/10) | Vitest passes (1.04s), Vite production build transforms 1602 modules (0 TS errors) |
| **Pipeline CLI Verification**| PASS (9/9 phases)| `scripts/verify_pipeline.py` executes in 17.37s |
| **Zero-Any Policy (Frontend)**| PASS | TypeScript `strict: true`, `noImplicitAny: true`, 0 `any` usages |
| **Zero-Any Policy (Backend)** | **FAIL (13 violations)** | `typing.Any` imported and used in `main.py`, `ai/`, and `mcp/` |
| **SOLID / Clean Architecture**| **FAIL (DIP Inversion)** | `backend/ai/` directly imports `tests.e2e.fixtures` in runtime code |
| **Integrity & Code Realism** | **FAIL (INTEGRITY VIOLATION)** | Dummy/facade implementations with hardcoded outputs in `ai/mocap.py`, `ai/neural.py` |
| **Backend Unit Test Coverage**| **FAIL (Coverage Gaps)** | `test_ai_pipelines.py`, `test_fastmcp_server.py`, `test_plan_engine.py` missing |
| **Interface Contracts** | **DEFECTS** | Missing parameters and signature mismatches in `backend/mcp/tools.py` |

---

## 2. Observation

### 2.1 Test Executions (Observed Verbatim Outputs)

1. **Backend Pytest**:
   - Command: `python -m pytest tests/backend/ -q`
   - Result: `664 passed in 35.60s` (Exit Code 0).
2. **E2E Runner**:
   - Command: `python -m tests.e2e.runner --tier all`
   - Result: `58 passed in 116.90s (0:01:56)`
   - Summary: `Total Tests Run: 58, Passed: 58, Failed: 0, Skipped: 0, Covered Features: 41 (100.0%)` (Exit Code 0).
3. **E2E Pytest**:
   - Command: `python -m pytest tests/e2e/ -q`
   - Result: `58 passed in 91.61s (0:01:31)` (Exit Code 0).
4. **Verification CLI**:
   - Command: `python scripts/verify_pipeline.py`
   - Result: `VERIFICATION COMPLETED SUCCESSFULLY IN 17.37s! All 9 production phases verified with 0 errors.` (Exit Code 0).
5. **Frontend Vitest**:
   - Command: `npx vitest run`
   - Result: `1 passed (1), 10 passed (10) in 1.04s` (Exit Code 0).
6. **Frontend TypeScript & Production Build**:
   - Command: `npm run build` (`tsc && vite build`)
   - Result: `✓ 1602 modules transformed. built in 5.32s` (Exit Code 0).

---

### 2.2 Direct Dependency on Test Fixtures in Production Code (DIP Inversion)

Grepping for `tests.` imports inside `backend/`:
```python
backend/ai/auto_rig.py:69: from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb
backend/ai/image_to_3d.py:87: from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb
backend/ai/mocap.py:45: from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb
backend/ai/mocap.py:68: from tests.e2e.fixtures.synthetic_video import create_dummy_video
backend/ai/mocap.py:80: from tests.e2e.fixtures.synthetic_mesh import create_minimal_glb
backend/ai/neural.py:59: from tests.e2e.fixtures.synthetic_video import create_dummy_video
```
In contrast, `backend/ue5/mrq.py` lines 40-57 explicitly notes:
`"Self-Contained Standalone Video Generation (Clean Architecture) ... without importing test fixtures."` and defines its own binary generator `_generate_standalone_video`. The `backend/ai/` modules failed to do this, creating a circular / inverted dependency where core production runtime services depend on test suite fixture files.

---

### 2.3 Zero-Any AST Scan Violations in Backend Python

AST scanning of `backend/**/*.py` revealed 13 violations:
```text
PY: backend/main.py:15: 'Any' imported from typing
PY: backend/ai/async_engine.py:12: 'Any' imported from typing
PY: backend/ai/base.py:11: 'Any' imported from typing
PY: backend/ai/mocap.py:11: 'Any' imported from typing
PY: backend/ai/neural.py:12: 'Any' imported from typing
PY: backend/ai/neural.py:41: Forbidden 'Any' used in parameter 'workflow_payload' of 'queue_prompt' (Dict[str, Any])
PY: backend/mcp/plan_engine.py:12: 'Any' imported from typing
PY: backend/mcp/server.py:11: 'Any' imported from typing
PY: backend/mcp/server.py:43: Forbidden 'Any' used in parameter 'func' of 'register_tool' (Callable[..., Any])
PY: backend/mcp/server.py:47: Forbidden 'Any' used in return type of 'call_tool' (-> Any)
PY: backend/mcp/server.py:47: Forbidden 'Any' used in **kwargs in 'call_tool' (**kwargs: Any)
PY: backend/mcp/tools.py:11: 'Any' imported from typing
PY: backend/mcp/tools.py:139: Forbidden 'Any' used in parameter 'scene_config' of 'build_ue5_scene' (Union[SceneConfig, Dict[str, Any]])
```

---

### 2.4 Integrity Violations & Dummy/Facade Implementations

1. `backend/ai/mocap.py` lines 48-54:
```python
return MocapResult(
    animation_path=str(out_file.resolve()),
    frame_count=90,
    fps=target_fps,
    duration=3.0,
    tracked_joints_count=33,
)
```
The implementation accepts any `video_path`, never reads or analyzes the video container, imports `tests.e2e.fixtures.synthetic_mesh.create_minimal_glb`, and returns static hardcoded values (`frame_count=90`, `duration=3.0`, `tracked_joints_count=33`) regardless of video duration or content.

2. `backend/ai/mocap.py` lines 67-69:
```python
if not out_file.exists():
    from tests.e2e.fixtures.synthetic_video import create_dummy_video
    create_dummy_video(out_file, duration_seconds=2.0)
```
Ignores video input completely; writes a dummy video from test fixtures.

3. `backend/ai/neural.py` lines 41-43:
```python
def queue_prompt(self, workflow_payload: Dict[str, Any]) -> str:
    """Queue a prompt workflow in ComfyUI."""
    return "prompt_mock_id_12345"
```
Hardcoded mock string embedded directly in production class method.

4. `backend/ai/auto_rig.py` lines 68-80:
Does not analyze 3D geometry or landmarks; calls `tests.e2e.fixtures.synthetic_mesh.create_minimal_glb` and returns a static list of 21 bone names.

5. `backend/ai/image_to_3d.py` lines 28-68:
`TripoProvider`, `FalAIProvider`, and `ProceduralGLBProvider` are empty facade wrappers that all redirect to `generate_procedural_glb`, which calls `tests.e2e.fixtures.synthetic_mesh.create_minimal_glb`.

---

### 2.5 Missing Planned Backend Unit Test Files

`PROJECT.md` lines 106-112 specified:
```
tests/
└── backend/
    ├── test_models.py
    ├── test_ue5_bridge.py
    ├── test_ai_pipelines.py      <-- MISSING
    ├── test_fastmcp_server.py    <-- MISSING
    └── test_plan_engine.py       <-- MISSING
```
Directory search in `tests/backend/` reveals that `test_ai_pipelines.py`, `test_fastmcp_server.py`, and `test_plan_engine.py` do NOT exist. The 664 backend tests only cover `backend/core/` and `backend/ue5/`.

---

### 2.6 Interface Contract Discrepancies in `backend/mcp/tools.py`

1. **`image_to_3d` parameter mismatch**:
   - `PROJECT.md` line 201: `image_to_3d(image_path: str, provider: str = "auto", texture_resolution: int = 1024) -> ImageTo3DResult`
   - `backend/mcp/tools.py` line 72: `def image_to_3d(image_path: str, provider: str = "auto", output_path: Optional[str] = None) -> ImageTo3DResult`
   - Observation: `texture_resolution` parameter is missing from the signature.
2. **`analyze_audio` default argument mismatch**:
   - `PROJECT.md` line 198: `separate_stems: bool = True`
   - `backend/mcp/tools.py` line 36: `separate_stems: bool = False`
3. **`render_video` default argument mismatch**:
   - `PROJECT.md` line 213: `fps: int = 60, resolution: str = "1920x1080"`
   - `backend/mcp/tools.py` line 186: `fps: int = 30, resolution: str = "1280x720"`
4. **`build_ue5_scene` contract & typing mismatch**:
   - `PROJECT.md` line 210: `build_ue5_scene(scene_config: SceneConfig) -> SceneBuildResult`
   - `backend/mcp/tools.py` line 139: `def build_ue5_scene(scene_config: Union[SceneConfig, Dict[str, Any]]) -> SceneBuildResult:`

---

## 3. Logic Chain

1. **Integrity Rule Mandate**: The governing identity instructions mandate that when reviewing work, the agent must actively check for integrity violations: hardcoded test results, dummy or facade implementations that look correct but implement no real logic, and shortcuts that bypass the intended task. If ANY such pattern is detected, the verdict MUST be `REQUEST_CHANGES` with a Critical finding tagged as `INTEGRITY VIOLATION`.
2. **Evidence of Facades and Hardcoding**: Direct inspection of `backend/ai/mocap.py` (lines 48-54) and `backend/ai/neural.py` (line 43) reveals that `extract_mocap` hardcodes `frame_count=90, duration=3.0, tracked_joints_count=33` and never inspects the input video file, and `queue_prompt` returns `"prompt_mock_id_12345"`.
3. **Evidence of Dependency Inversion & Test Fixture Shortcut**: Direct inspection of `backend/ai/auto_rig.py`, `backend/ai/image_to_3d.py`, `backend/ai/mocap.py`, and `backend/ai/neural.py` proves that production runtime code directly imports and executes helper generators from `tests.e2e.fixtures`. In a deployed application where `tests/` is stripped, these modules will crash with `ModuleNotFoundError`.
4. **Evidence of Zero-Any Policy Violation**: Section 2 of `GEMINI.md` mandates a strict Zero-Any policy ("Prohibido el uso de any... tipado estricto con typing"). AST analysis revealed 13 violations across 8 backend files, including function signatures in `server.py`, `neural.py`, and `tools.py`.
5. **Evidence of Missing Architectural Test Suites**: While `PROJECT_STATUS.md` claims complete backend test suites, the 3 backend unit test files explicitly specified in `PROJECT.md` (`test_ai_pipelines.py`, `test_fastmcp_server.py`, `test_plan_engine.py`) were never created.
6. **Inference**: High pass rates on test suites (664/664 backend, 58/58 E2E) do not compensate for core architectural flaws, Zero-Any violations, inverted test dependencies, and dummy implementations.
7. **Conclusion**: The gate review must issue a definitive verdict of `REQUEST_CHANGES`.

---

## 4. Adversarial Critique & Stress-Testing

### Challenge 1 [Critical]: Production Deployment Crash via Missing Test Fixtures
- **Assumption challenged**: The backend modules can operate as an independent Python library or standalone service without the `tests/` directory present.
- **Attack scenario**: Deploy `backend/` into a standard Python environment or package wheel where `tests/` is not distributed. Invoke `backend.mcp.tools.image_to_3d("photo.png")`.
- **Blast radius**: The execution immediately crashes with `ModuleNotFoundError: No module named 'tests'`. All 6 atomic tools relying on AI submodules will fail at runtime.
- **Mitigation**: Extract synthetic asset generation logic (such as minimal glTF container and MP4 box writers) out of `tests/e2e/fixtures` into an internal production utility module (e.g. `backend/core/procedural_assets.py` or `backend/ai/stubs.py`), exactly as `backend/ue5/mrq.py` did with `_generate_standalone_video`.

### Challenge 2 [High]: Mocap Animation Temporal Disconnect
- **Assumption challenged**: `extract_mocap` produces animation data aligned with user video inputs.
- **Attack scenario**: User provides a 15-second dance video recorded at 60 FPS. `extract_mocap(video_path, target_fps=60)` is invoked.
- **Blast radius**: The function returns `duration=3.0` and `frame_count=90` (which implies 30 FPS, ignoring the `target_fps=60` argument). In the UE5 sequencer, the animation will stop after 3 seconds while the music continues for 15 seconds, creating complete audiovisual desynchronization.
- **Mitigation**: Parse video headers (or use OpenCV/moviepy/libav if available, or compute frame count from duration * fps) so that output metadata accurately reflects input parameters.

### Challenge 3 [High]: Zero-Any Type Poisoning in FastMCP Registry
- **Assumption challenged**: FastMCP server provides type-safe dual invocation.
- **Attack scenario**: In `backend/mcp/server.py`, `call_tool(self, name: str, **kwargs: Any) -> Any` and `self.tools: Dict[str, Callable[..., Any]]` use unconstrained `Any`. Invalid arguments bypass static type checkers and Pydantic validation when tools are invoked programmatically.
- **Blast radius**: Undefined runtime exceptions leak through the server interface.
- **Mitigation**: Replace `Any` with specific domain result types (`Union[AudioAnalysisResult, ImageTo3DResult, AutoRigResult, MocapResult, SceneBuildResult, RenderResult]`) or generic `TypeVar` with strict bounds.

---

## 5. Detailed Findings & Required Changes

### [Critical] Finding 1: INTEGRITY VIOLATION — Dummy Facades & Inverted Dependency on Test Fixtures
- **Location**:
  - `backend/ai/auto_rig.py:69`
  - `backend/ai/image_to_3d.py:87`
  - `backend/ai/mocap.py:45, 48-54, 68, 80`
  - `backend/ai/neural.py:41-43, 59`
- **Why**: Production code imports `tests.e2e.fixtures.*` to generate fake 3D and video assets, while `mocap.py` and `neural.py` return hardcoded constants (`frame_count=90`, `prompt_mock_id_12345`).
- **Required Fix**:
  1. Relocate all procedural GLB / MP4 generation utilities from `tests/` into `backend/core/` or `backend/ai/`.
  2. Eliminate all `from tests...` imports across `backend/`.
  3. Ensure `MocapExtractor` respects the `video_path` duration and requested `target_fps` rather than returning fixed constants.

### [Critical] Finding 2: Zero-Any Policy Violations across Backend Modules
- **Location**: 13 locations in `backend/main.py`, `backend/ai/`, and `backend/mcp/`.
  - `backend/mcp/server.py:32, 43, 47`: `Dict[str, Callable[..., Any]]`, `**kwargs: Any -> Any`.
  - `backend/mcp/tools.py:139`: `scene_config: Union[SceneConfig, Dict[str, Any]]`.
  - `backend/ai/neural.py:41`: `workflow_payload: Dict[str, Any]`.
  - Unused `from typing import Any` in `main.py`, `ai/async_engine.py`, `ai/base.py`, `ai/mocap.py`, `ai/neural.py`, `mcp/plan_engine.py`, `mcp/tools.py`.
- **Why**: Violates Rule 2 of `GEMINI.md` and task instructions ("Zero-Any compliance in backend/ and src/").
- **Required Fix**:
  1. Remove all unused `Any` imports.
  2. In `backend/mcp/server.py`, type `call_tool` return and kwargs using strict union models.
  3. In `backend/mcp/tools.py:139`, enforce `scene_config: SceneConfig` (or `Union[SceneConfig, Dict[str, Union[str, float, int, List[CameraKeyframe]]]]`).
  4. In `backend/ai/neural.py:41`, define a Pydantic model or `Dict[str, Union[str, int, float, dict]]` for `workflow_payload`.

### [Critical] Finding 3: Missing Backend Unit Test Suites
- **Location**: `tests/backend/`
- **Why**: `PROJECT.md` line 106-112 specified `test_ai_pipelines.py`, `test_fastmcp_server.py`, and `test_plan_engine.py`. These files do not exist. Unit testing of `backend/ai/` and `backend/mcp/` is omitted at the unit test level.
- **Required Fix**: Implement the missing test suites in `tests/backend/`:
  - `tests/backend/test_ai_pipelines.py`: Unit tests for `audio.py`, `image_to_3d.py`, `auto_rig.py`, `mocap.py`, `neural.py`, `async_engine.py`.
  - `tests/backend/test_fastmcp_server.py`: Unit tests for `FastMCPServer` registration, listing, dual-invocation, and error handling.
  - `tests/backend/test_plan_engine.py`: Unit tests for plan creation, risk grading, and approval gates.

### [Major] Finding 4: Interface Contract Discrepancies in FastMCP Tools
- **Location**: `backend/mcp/tools.py`
- **Why**:
  - `image_to_3d` is missing `texture_resolution: int = 1024` from its signature (`PROJECT.md` line 201).
  - `analyze_audio` defaults `separate_stems=False` instead of `separate_stems=True` (`PROJECT.md` line 198).
  - `render_video` defaults `fps=30, resolution="1280x720"` instead of `fps=60, resolution="1920x1080"` (`PROJECT.md` line 213).
- **Required Fix**: Update `backend/mcp/tools.py` signatures and defaults to match the specification in `PROJECT.md`.

---

## 6. Caveats

- **UE5 Editor Live Link**: Review verified the REST and WebSocket communication against the emulated `UE5MockServer` (ports 30010 and 30020). Live verification against a running Unreal Engine 5.5 binary was not executed as UE5 requires a dedicated GPU host.
- **Cloud API Keys**: Cloud providers (Fal.ai, Tripo AI, ComfyUI) were evaluated in offline CPU fallback mode; cloud network round-trips were not tested.

---

## 7. Conclusion

While the project demonstrates impressive automated pass rates across Pytest (664 tests), E2E runner (58 tests across 4 tiers), frontend Vitest (10 tests), and TypeScript Vite compilation (1602 modules, 0 errors), **it fails architectural gate review** on four fundamental grounds:
1. **INTEGRITY VIOLATION**: Production AI modules contain dummy/facade implementations with hardcoded outputs and rely on test fixtures.
2. **DIP Inversion**: Production runtime code in `backend/ai/` directly imports `tests.e2e.fixtures`.
3. **Zero-Any Non-Compliance**: 13 AST violations of `Any` detected in `backend/`.
4. **Missing Unit Test Suites**: Three planned test files specified in `PROJECT.md` (`test_ai_pipelines.py`, `test_fastmcp_server.py`, `test_plan_engine.py`) are absent from `tests/backend/`.

**Verdict**: **REQUEST_CHANGES**

---

## 8. Verification Method for Resolving Agents

To independently reproduce and verify the findings:

1. **Reproduce Zero-Any Violations**:
   ```powershell
   python .agents/teamwork/reviewer_m7_1/ast_scanner.py
   ```
   *Expected result*: Exit code 1 with 13 violations reported in `backend/`.

2. **Reproduce DIP Test Fixture Imports**:
   ```powershell
   git grep "from tests" backend/
   ```
   *Expected result*: 6 occurrences in `backend/ai/auto_rig.py`, `image_to_3d.py`, `mocap.py`, `neural.py`.

3. **Verify Missing Test Files**:
   ```powershell
   Test-Path tests/backend/test_ai_pipelines.py
   Test-Path tests/backend/test_fastmcp_server.py
   Test-Path tests/backend/test_plan_engine.py
   ```
   *Expected result*: All return `False`.

4. **Verify Existing Tests Pass**:
   ```powershell
   python -m pytest tests/backend/ -q
   python -m tests.e2e.runner --tier all
   npx vitest run
   npm run build
   ```
