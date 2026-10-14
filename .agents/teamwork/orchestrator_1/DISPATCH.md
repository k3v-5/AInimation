## 2026-10-14T00:28:39Z

You are the Project Orchestrator for the IANIMATION project.

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\orchestrator_1
Project root: e:\Disco F\Dev\IANIMATION
Original user request: e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md
Project status: e:\Disco F\Dev\IANIMATION\PROJECT_STATUS.md
Project guidelines & rules: e:\Disco F\Dev\IANIMATION\GEMINI.md

Your mission:
Orchestrate the complete implementation and verification of the "Orquestador de Animación 3D e IA" desktop application and backend ecosystem, satisfying all requirements (R1-R4) and acceptance criteria detailed in ORIGINAL_REQUEST.md:
1. R1: Unreal Engine 5 Headless / Remote Control Orchestration (WebSocket / REST client, asset loading, PBR materials, Lumen lights, camera sequencing, MRQ trigger, plus a high-fidelity mock server for testing without running UE5).
2. R2: Hybrid AI Pipeline (Audio BPM/beats/stems via Librosa/Demucs, Image-to-3D with PBR textures, Auto-Rigging, Mocap/Rotoscopy, ComfyUI Neural Enhancer integration; async non-blocking execution with progress reporting).
3. R3: Tauri Desktop Native App (Rust + React/TypeScript, drag & drop media dropzone, multi-track audiovisual timeline, 3D preview viewport / WebRTC Pixel Streaming support, Copilot dialog console with step-by-step intermediate previews).
4. R4: Python FastMCP Server & Human-in-the-Loop Copilot (Atomic tools analyze_audio, image_to_3d, auto_rig, extract_mocap, build_ue5_scene, render_video with strict JSON Schema, production plan proposals with human confirmation points, real-time telemetry/progress via WebSocket/SSE).
5. Comprehensive Test Suites & Verification: Automated unit/integration tests (pytest for backend/MCP, frontend component tests) and an end-to-end simulation CLI script verify_pipeline.py.
6. Engineering standards: SOLID, 100% strict typing (TypeScript strict: true without any, Python typing + Pydantic v2), continuous documentation, updating PROJECT_STATUS.md, and rigorous visual verification.

Manage your subagents, maintain your plan.md, progress.md, and BRIEFING.md in your working directory, update PROJECT_STATUS.md as progress occurs, and notify me with your completion report when the project is fully implemented and verified.
