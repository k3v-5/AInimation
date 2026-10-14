# Task Assignment: worker_m7_it2

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\worker_m7_it2
Project root: e:\Disco F\Dev\IANIMATION
Original request: e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md
Guidelines: e:\Disco F\Dev\IANIMATION\GEMINI.md
Project plan: e:\Disco F\Dev\IANIMATION\.agents\teamwork\PROJECT.md
E2E readiness: e:\Disco F\Dev\IANIMATION\TEST_READY.md
Gate status: e:\Disco F\Dev\IANIMATION\.agents\teamwork\orchestrator_3\GATE_STATUS.md

## Reference Reports & Drop-in Implementations:
- Explorer 1 (Backend Integrity, Decoupling & AST Zero-Any):
  - Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_1\handoff.md
  - Proposed Procedural Module: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_1\proposed_procedural.py
- Explorer 2 (Frontend Intermediate Asset Cards & README Documentation):
  - Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\handoff.md
  - Proposed Component: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\proposed_IntermediateAssetCard.tsx
  - Proposed CopilotChat: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\proposed_CopilotChat.tsx
  - Proposed Copilot index: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\proposed_copilot_index.ts
  - Proposed App: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\proposed_App.tsx
  - Proposed README: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\proposed_README.md
- Explorer 3 (E2E Test Integrity & Backend Unit Test Suites):
  - Report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_3\handoff.md
  - E2E Test Patch: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_3\proposed_test_tier1_features.patch
  - Proposed AI Tests: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_3\proposed_test_ai_pipelines.py
  - Proposed MCP Server Tests: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_3\proposed_test_fastmcp_server.py
  - Proposed Plan Engine Tests: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_3\proposed_test_plan_engine.py

## Scope & Implementation Tasks:
1. **Apply Backend Decoupling & Procedural Asset Module**:
   - Create `backend/ai/procedural.py` from `explorer_m7_it2_1/proposed_procedural.py`.
   - Update `backend/ai/image_to_3d.py`, `backend/ai/auto_rig.py`, `backend/ai/mocap.py`, and `backend/ai/neural.py` to import from `backend.ai.procedural` instead of `tests.e2e.fixtures`. Verify ZERO `from tests...` imports remain in `backend/`.
2. **Eliminate All 14 AST `Any` Violations in `backend/`**:
   - Apply strict types in `backend/mcp/server.py` (`JSONValue`, `JSONDict`), `backend/mcp/tools.py` (`SceneConfigDict`), and `backend/ai/neural.py`.
   - Remove unused `from typing import Any` in `main.py`, `async_engine.py`, `base.py`, `mocap.py`, `plan_engine.py`.
   - Verify with the AST scanner from `auditor_m7_1/handoff.md`: 0 violations must be reported.
3. **Eliminate Hardcoded Mock Constants & Fix Engine Defects**:
   - Update `neural.py` with dynamic UUID prompt IDs.
   - Update `mocap.py` with dynamic frame/duration calculation.
   - Update `image_to_3d.py` with genuine vertex/polygon counts parsed from GLB buffer.
   - Fix `AsyncUE5RestClient.health_check` in `backend/ue5/client.py`.
   - Fix `PlanEngine.confirm_step` in `backend/mcp/plan_engine.py` to promote `plan.status = PlanStatus.APPROVED` when all steps approved.
   - Align `backend/mcp/tools.py` signatures (add `texture_resolution` to `image_to_3d`, default `separate_stems=True` in `analyze_audio`).
4. **Implement Frontend Intermediate Asset Cards (F-UI-07)**:
   - Create `src/components/copilot/IntermediateAssetCard.tsx` from `explorer_m7_it2_2/proposed_IntermediateAssetCard.tsx`.
   - Update `src/components/copilot/CopilotChat.tsx`, `src/components/copilot/index.ts`, and `src/App.tsx`.
   - Verify `npm run build` (`tsc && vite build`) passes with 0 errors under `strict: true`.
   - Verify `npx vitest run` passes.
5. **Expand Documentation in `README.md` (GEMINI.md §3 & F-DOC-01)**:
   - Update `README.md` using `explorer_m7_it2_2/proposed_README.md` with complete FastMCP tool JSON Schemas, invocation examples, environment variables table, and network ports table.
6. **Remediate E2E Tests & Add Missing Backend Unit Test Suites**:
   - Apply `proposed_test_tier1_features.patch` to `tests/e2e/test_tier1_features.py` (replacing self-certifying `assert True` in F-E2E-01/02 and facade checks in F-UI-07/F-DOC-01).
   - Create `tests/backend/test_ai_pipelines.py` from `explorer_m7_it2_3/proposed_test_ai_pipelines.py`.
   - Create `tests/backend/test_fastmcp_server.py` from `explorer_m7_it2_3/proposed_test_fastmcp_server.py`.
   - Create `tests/backend/test_plan_engine.py` from `explorer_m7_it2_3/proposed_test_plan_engine.py`.
7. **Run Full Verification**:
   - `python -m pytest tests/backend/` (all tests passing)
   - `python -m tests.e2e.runner --tier all --verbose` (58/58 passing, 100% feature coverage)
   - `python scripts/verify_pipeline.py` (9/9 phases passing)
   - `npx vitest run` (frontend tests passing)
   - `npm run build` (production build 0 errors)
   - Zero-Any AST script (0 violations)
   - Zero `tests.` import check (0 leaks)
8. Document all commands, file diffs, outputs, and metrics in `handoff.md`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
