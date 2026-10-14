# Task Assignment: explorer_m7_it2_1

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_1
Project root: e:\Disco F\Dev\IANIMATION
Original request: e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md
Guidelines: e:\Disco F\Dev\IANIMATION\GEMINI.md
Project plan: e:\Disco F\Dev\IANIMATION\.agents\teamwork\PROJECT.md
E2E readiness: e:\Disco F\Dev\IANIMATION\TEST_READY.md
Gate status: e:\Disco F\Dev\IANIMATION\.agents\teamwork\orchestrator_3\GATE_STATUS.md

## Full Audit Evidence & Review Reports (MANDATORY TO READ):
- Auditor Evidence Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\auditor_m7_1\handoff.md
- Reviewer 1 Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\reviewer_m7_1\handoff.md
- Reviewer 2 Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\reviewer_m7_2\handoff.md
- Challenger 1 Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\challenger_m7_1\handoff.md
- Challenger 2 Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\challenger_m7_2\handoff.md

## Scope & Objective
Investigate and design exact drop-in implementation fixes for Backend AI & MCP Decoupling, Zero-Any AST violations, and Engine defects:
1. **Decouple Backend from Test Fixtures**:
   - `backend/ai/image_to_3d.py`, `auto_rig.py`, `mocap.py`, `neural.py` currently import from `tests.e2e.fixtures.*`.
   - Design a self-contained production procedural module (e.g., `backend/ai/procedural.py` or `backend/core/procedural_assets.py`) providing genuine standalone glTF binary generation and video container generation without any `tests/` imports.
2. **Eliminate All 14 AST `Any` Violations in `backend/`**:
   - `backend/mcp/server.py` lines 32, 43, 47: Replace `Any` with `JSONValue` / `JSONDict` or strictly bounded `TypeVar`.
   - `backend/mcp/tools.py` line 139: Replace `Dict[str, Any]` with `SceneConfigDict` or `JSONDict`.
   - `backend/ai/neural.py` line 41: Replace `Dict[str, Any]` with `Dict[str, JSONValue]` or dedicated Pydantic model.
   - Remove unused `from typing import Any` from `backend/main.py:15`, `backend/ai/async_engine.py:12`, `backend/ai/base.py:11`, `backend/ai/mocap.py:11`, `backend/mcp/plan_engine.py:12`.
3. **Eliminate Hardcoded Mock Constants**:
   - In `backend/ai/neural.py:43`: Generate dynamic prompt IDs using SHA-256 or UUID (`f"prompt_{uuid.uuid4().hex[:12]}"`).
   - In `backend/ai/mocap.py:48-54`: Dynamically compute frame count and duration from input video file size or target fps.
   - In `backend/ai/image_to_3d.py:98-99`: Dynamically read vertex count and polygon count from the generated glTF buffer.
4. **Fix Engine Defects**:
   - `backend/ue5/client.py`: Fix `AsyncUE5RestClient.health_check` to use `await self.open()` and `self._session`.
   - `backend/mcp/plan_engine.py`: Promote `plan.status = PlanStatus.APPROVED` when all steps are approved in `confirm_step`.
   - `backend/mcp/tools.py`: Align signatures with `PROJECT.md` (add `texture_resolution: int = 1024` to `image_to_3d`, default `separate_stems: bool = True` in `analyze_audio`).

Provide ready-to-apply code changes and verification commands in `handoff.md`.
