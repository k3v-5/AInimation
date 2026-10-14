# Dispatch: Survey Agent 2 (Explorer - AI Pipeline Architecture)

## Mission
Survey, analyze requirements, and enumerate features for R2 (Hybrid AI Pipelines: Audio Librosa/Demucs, Image-to-3D with PBR, Auto-Rigging, Mocap/Rotoscopy, ComfyUI Neural Enhancer, abstract provider interfaces, cloud API adapters vs local fallback stubs, async progress reporting).

## Working Directory
`e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2`

## Mandatory Reading
- `e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md` (read first before starting)
- `e:\Disco F\Dev\IANIMATION\PROJECT_STATUS.md`
- `e:\Disco F\Dev\IANIMATION\GEMINI.md`
- Explore workspace root `e:\Disco F\Dev\IANIMATION` for any existing code or configuration.

## Outputs
- `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2\survey_report.md`
- `e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2\handoff.md`

## 2026-10-14T00:30:09Z
Received from: e8d2c723-385e-49cb-842f-6806cc37fde9
Content:
You are Survey Agent 2 (Explorer - AI Pipeline Architecture) for the IANIMATION project.

Working directory: e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2
Mandatory reading:
- e:\Disco F\Dev\IANIMATION\.agents\teamwork\ORIGINAL_REQUEST.md (READ THIS FIRST VERBATIM)
- e:\Disco F\Dev\IANIMATION\PROJECT_STATUS.md
- e:\Disco F\Dev\IANIMATION\GEMINI.md
- Inspect the repository at e:\Disco F\Dev\IANIMATION for any existing files, scripts, or configurations.

Your Objective:
Perform an exhaustive survey and architectural analysis for R2: Hybrid AI Pipelines (Cloud API + Local Fallback):
1. Abstract Provider Interfaces (SOLID LSP/OCP) for AI engines allowing plug-and-play switching between Cloud providers and Local backends.
2. Audio Analysis: Librosa & Demucs integration. Extracting BPM, beat frames/timestamps, onset envelopes, and stem separation (vocals, drums, bass, other) formatted into clean Pydantic v2 schemas.
3. Image-to-3D: Generating structured 3D meshes (.glb) with PBR textures from reference 2D images. Providers: Cloud (Fal.ai / Tripo AI / Replicate) with local fallback stubs/TRELLIS. Error handling, retries, asset caching.
4. Auto-Rigging: Bipedal skeletal detection and standard deformable armature (.fbx / .glb) rigging.
5. Mocap & Rotoscopy: 3D motion extraction from reference dance/character video (.mp4) and background removal (GVHMR / 4DHumans / stub motion data).
6. Neural Enhancer: ComfyUI integration (ControlNet / AnimateDiff / Wan 2.1) for aesthetic final video pass.
7. Asynchronous, non-blocking execution architecture with event-driven progress reporting, cancelation, and retry queues.

Write your findings to:
- e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2\survey_report.md
- e:\Disco F\Dev\IANIMATION\.agents\teamwork\explorer_survey_2\handoff.md
Update progress.md with timestamped heartbeats as you work.
When done, notify your parent with a concise summary and report path.
