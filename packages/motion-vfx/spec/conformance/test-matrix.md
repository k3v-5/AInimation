# 🧪 Matriz de Conformidad y Trazabilidad de Pruebas

Esta matriz vincula cada requisito normativo con su suite de pruebas automatizadas y su puerta de certificación correspondiente.

---

## 📊 Matriz de Trazabilidad de Requisitos

| ID Requisito | Título del Requisito | Severidad | Puerta de Certificación | Suites de Prueba de Verificación | Estado |
|---|---|---|---|---|---|
| **REQ-001** | Canonical IR as Single Source of Truth | CRITICAL | Gate 01: IR | `src/tests/core/Composition.test.ts`, `src/tests/schema/Serialization.test.ts` | **PASS** |
| **REQ-002** | Deterministic Reconstructibility | CRITICAL | Gate 01: IR | `src/tests/schema/ProjectValidator.test.ts`, `src/tests/serialization/RoundTrip.test.ts` | **PASS** |
| **REQ-003** | Cryptographic Project Hashing | CRITICAL | Gate 01: IR | `src/tests/core/ProjectHash.test.ts` | **PASS** |
| **REQ-004** | Immutable Stable Object Identifiers | CRITICAL | Gate 01: IR | `src/tests/core/StableIds.test.ts` | **PASS** |
| **REQ-005** | Level A: Logical Determinism | CRITICAL | Gate 02: Determinism | `src/tests/ai-planner/DeterministicPlan.test.ts` | **PASS** |
| **REQ-006** | Level B: Structural Determinism | CRITICAL | Gate 02: Determinism | `src/tests/transform/TransformMath.test.ts`, `src/tests/animation/Interpolation.test.ts` | **PASS** |
| **REQ-007** | Level C: Perceptual Determinism | MAJOR | Gate 02: Determinism | `src/tests/qa/PerceptualQA.test.ts` | **PASS** |
| **REQ-008** | Level D: Binary Determinism | MINOR | Gate 02: Determinism | `src/tests/exporters/JSXSerializer.test.ts` | **PASS** |
| **REQ-009** | Operation Idempotency (operation_id) | CRITICAL | Gate 03: Idempotency | `src/tests/agent/AgentValidator.test.ts` | **PASS** |
| **REQ-010** | Optimistic Concurrency Versioning | CRITICAL | Gate 03: Idempotency | `src/tests/ai-director/RevisionEngine.test.ts` | **PASS** |
| **REQ-011** | Network Retry Deduplication | MAJOR | Gate 03: Idempotency | `src/tests/agent/AgentSession.test.ts` | **PASS** |
| **REQ-012** | ACID Transaction Envelope | CRITICAL | Gate 04: Transactions | `src/tests/workflow/WorkflowEngine.test.ts` | **PASS** |
| **REQ-013** | Strict Cryptographic Rollback | CRITICAL | Gate 04: Transactions | `src/tests/ai-director/RevisionEngine.test.ts` | **PASS** |
| **REQ-014** | Transaction Abort on Faults | CRITICAL | Gate 04: Transactions | `src/tests/workflow/WorkflowRecovery.test.ts` | **PASS** |
| **REQ-015** | Strict 6-Category MCP Interface | CRITICAL | Gate 05: MCP Contract | `src/tests/cli/CLIRunner.test.ts` | **PASS** |
| **REQ-016** | Structured Error Catalog | CRITICAL | Gate 05: MCP Contract | `src/tests/errors/ErrorHierarchy.test.ts` | **PASS** |
| **REQ-017** | Context Budget Optimization | MAJOR | Gate 05: MCP Contract | `src/tests/ai-director/ChangeSetDiff.test.ts` | **PASS** |
| **REQ-018** | Dry-Run Simulation Mode | CRITICAL | Gate 05: MCP Contract | `src/tests/ai-planner/PlanValidator.test.ts` | **PASS** |
| **REQ-019** | JSON-RPC 2.0 IPC Bridge Protocol | CRITICAL | Gate 06: AE Bridge | `src/tests/exporters/AELiveBridgeProtocol.test.ts` | **PASS** |
| **REQ-020** | Heartbeat and Disconnect Detection | MAJOR | Gate 06: AE Bridge | `src/tests/exporters/AELiveBridgeProtocol.test.ts` | **PASS** |
| **REQ-021** | State Reconciliation (Expected vs Actual) | CRITICAL | Gate 06: AE Bridge | `src/tests/exporters/AELiveBridgeProtocol.test.ts` | **PASS** |
| **REQ-022** | Prohibition of Arbitrary JSX Emission | CRITICAL | Gate 06: AE Bridge | `src/tests/exporters/AfterEffectsJSXCompiler.test.ts` | **PASS** |
| **REQ-023** | Spatial & Title Safe Zones Enforcement | CRITICAL | Gate 07: Constraints | `src/tests/captions/SafeZoneResolver.test.ts` | **PASS** |
| **REQ-024** | Visual OCR Collision Avoidance | MAJOR | Gate 07: Constraints | `src/tests/media-intelligence/VideoOCREngine.test.ts` | **PASS** |
| **REQ-025** | Subject Saliency & Face Protection | MAJOR | Gate 07: Constraints | `src/tests/camera/AutoReframeEngine.test.ts` | **PASS** |
| **REQ-026** | 7-Family Automated QA Suite | CRITICAL | Gate 08: QA | `src/tests/qa/QAEvaluator.test.ts` | **PASS** |
| **REQ-027** | Bounded Auto-Repair Loop (max_iterations) | CRITICAL | Gate 08: QA | `src/tests/ai-planner/PlanRepairEngine.test.ts` | **PASS** |
| **REQ-028** | Render Manifest Certification | MAJOR | Gate 08: QA | `src/tests/exporters/ExportManifest.test.ts` | **PASS** |
| **REQ-029** | 100% Offline Capability | CRITICAL | Gate 09: Security | `src/tests/captions/SpeechRecognitionEngine.test.ts`, `src/tests/audio/AudioTransientSync.test.ts` | **PASS** |
| **REQ-030** | Path Traversal & Filesystem Sandbox | CRITICAL | Gate 09: Security | `src/tests/common/PathSanitizer.test.ts` | **PASS** |
| **REQ-031** | Resource Limits Enforcement | MAJOR | Gate 09: Security | `src/tests/schema/ResourceLimits.test.ts` | **PASS** |
| **REQ-032** | E2E Macro Pipeline (Golden E2E) | CRITICAL | Gate 10: Golden E2E | `src/tests/e2e/GoldenProject.test.ts` | **PASS** |
