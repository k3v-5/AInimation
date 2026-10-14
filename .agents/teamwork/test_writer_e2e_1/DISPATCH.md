## 2026-10-14T00:38:46Z
You are the E2E Test Writer for the IANIMATION project.

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\test_writer_e2e_1
Mandatory reading:
- e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md (READ FIRST VERBATIM)
- e:\Disco F\Dev\IANIMATION\.agents\teamwork\PROJECT.md
- e:\Disco F\Dev\IANIMATION\GEMINI.md

Your Objective:
1. Create `e:\Disco F\Dev\IANIMATION\TEST_INFRA.md` at project root following the E2E Testing Track specifications (opaque-box, requirement-driven, 4-tier methodology, feature coverage matrix covering all inventoried features).
2. Author the comprehensive opaque-box test suites in `tests/e2e/`:
   - Tier 1: Feature Coverage (happy path tests verifying every inventoried feature in isolation using synthetic fixtures).
   - Tier 2: Boundary & Corner Cases (empty audio/image/video, corrupt inputs, boundary BPMs, zero/negative transforms, timeout handling).
   - Tier 3: Cross-Feature Interactions (pairwise pipeline tests: Audio->3D, 3D->Rig, Rig->Mocap, Scene->MRQ render).
   - Tier 4: Real-World Scenarios (complete end-to-end workflow from music track and reference character to finished rendered cinematic video).
3. Provide an executable standalone test runner (`tests/e2e/runner.py` and pytest test cases) that outputs clear pass/fail status and coverage metrics.
4. When the test suite is fully created and ready, publish `e:\Disco F\Dev\IANIMATION\TEST_READY.md` at project root with execution instructions and coverage summary.

Write progress updates to progress.md with timestamps, write a complete handoff.md, and send your completion report to your parent when done.
