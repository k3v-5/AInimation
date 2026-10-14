# Task Assignment: explorer_m7_it2_2

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2
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
Investigate and design exact drop-in implementation fixes for Frontend Intermediate Asset Cards (`F-UI-07`) and Comprehensive Documentation (`GEMINI.md §3` & `F-DOC-01`):
1. **Frontend Intermediate Asset Cards (`F-UI-07`)**:
   - Inspect `src/components/copilot/CopilotChat.tsx` and `src/types/index.ts`.
   - `PlanStepSchema` declares `output_preview: z.string().nullable().optional()`.
   - Design the visual rendering of intermediate asset cards inside `CopilotChat.tsx` (and/or an asset card tray) when steps are approved/completed:
     - For audio analysis: Stems card (`stems: vocals, drums, bass, other`).
     - For image-to-3d: 3D Mesh card (`.glb` preview badge, vertex/polygon metrics, "Ver en Viewport" action).
     - For auto-rigging: Rigged mesh card (skeleton type: `ue5_mannequin`, bone count: 21).
     - For mocap: Mocap clip card (`.mp4`/`.glb`, frame count, duration).
     - For render: Rendered video card (`final_music_video.mp4`, resolution, FPS).
   - Ensure visual verification standards (GEMINI.md §5) are satisfied: clean Tailwind CSS styling, badges, Lucide icons, responsive layout, and strict Zero-Any TypeScript compliance.
2. **Comprehensive Documentation in `README.md` (`GEMINI.md §3` & `F-DOC-01`)**:
   - Inspect `README.md` and `backend/mcp/tools.py`.
   - Design full documentation additions:
     - Full JSON Schema definitions for all 6 FastMCP tools.
     - Concrete JSON-RPC invocation request/response examples for MCP client calls.
     - Environment variables table (`FAL_KEY`, `TRIPO_API_KEY`, `REPLICATE_API_TOKEN`, `CAS_CACHE_DIR`, `UE5_REMOTE_REST_PORT`, `UE5_REMOTE_WS_PORT`, `LOG_LEVEL`).
     - Default network ports table (UE5 REST: 30010, UE5 WS: 30020, WebRTC Signaling: 8888, Vite Dev: 5173).

Provide ready-to-apply code changes and verification instructions in `handoff.md`.


## 2026-10-14T03:41:57Z
You are explorer_m7_it2_2.
Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2
Project root: e:\Disco F\Dev\IANIMATION
Task assignment: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_m7_it2_2\DISPATCH.md
Original user request: e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md
Guidelines: e:\Disco F\Dev\IANIMATION\GEMINI.md
Project plan: e:\Disco F\Dev\IANIMATION\.agents\teamwork\PROJECT.md
E2E readiness: e:\Disco F\Dev\IANIMATION\TEST_READY.md
Gate status: e:\Disco F\Dev\IANIMATION\.agents\teamwork\orchestrator_3\GATE_STATUS.md
Reviewer 2 report: e:\Disco F\Dev\IANIMATION\.agents\teamwork\reviewer_m7_2\handoff.md

Your mission is to explore and design exact drop-in implementation fixes for:
1. Rendering intermediate asset cards in src/components/copilot/CopilotChat.tsx / App.tsx for approved/completed steps (audio stems card, 3D mesh GLB card, auto-rig card, mocap card, rendered video card) satisfying GEMINI.md §5 visual standards.
2. Expanding README.md with complete MCP tool JSON Schemas, JSON-RPC invocation examples, environment variables table, and network ports table per GEMINI.md §3.
Document exact code changes and verification instructions in handoff.md, then send a message to parent.
