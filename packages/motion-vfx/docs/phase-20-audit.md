# Auditoría de Arquitectura e Integración: Fase 20 — Autonomous Production Orchestrator, Revision Engine & Deterministic QA (v2.0.0)

## 1. Mapa de Arquitectura Encontrada (Fases 1–19)

El repositorio `after-effects-mcp` implementa un motor determinista audiovisual completo y modular estructurado a lo largo de 19 fases:

1. **Núcleo Temporal y Composición (`src/core/`):**
   - `Composition`: contenedor con dimensiones (`width`, `height`), `fps`, `duration` y assets.
   - `Composition.evaluate(t)`: método de evaluación determinista puro que genera snapshots inmutables (`CompositionSnapshot`).
   - `BaseElement`, `Transform2D`, `Matrix2D`.

2. **Línea de Tiempo y Audio (`src/timeline/` y `src/audio/`):**
   - `VideoTimeline`, `Track`, `Clip`, `TimeRange`.
   - `AudioMixer`, `AudioBuffer`, `MasterBus`, `AudioAnalyzer`, `AudioMath`.

3. **Subtítulos y Tipografía (`src/captions/` y `src/typography/`):**
   - `CaptionDocument`, `CaptionSegment`, `CaptionWord`, `CaptionEvaluator`, `SafeZoneResolver`.
   - Layout tipográfico cinético y cálculo determinista de bounds visuales.

4. **Persistencia, Grafo de Revisiones y Workflows (`src/persistence/`, `src/revisions/`, `src/workflows/`):**
   - `ProjectStore` (`MemoryProjectStore`, `FileProjectStore` con escrituras atómicas `.tmp` $\to$ `fsync` $\to$ `rename`).
   - `ProjectSerializer`: serialización canónica determinista y hashes SHA-256.
   - `RevisionGraph` (DAG con branching, merge 3-way, diff semántico y reversibilidad estricta $\text{reversePatch}(\text{applyPatch}(P, \Delta), \Delta) \equiv P$).
   - `WorkflowEngine` con checkpoints y recuperación determinista ante caídas.

5. **Cadena de Renderizado y Exportadores (`src/rendering/`, `src/exporters/`):**
   - `RenderPipeline`, `Compositor`, `RenderGraph`, `FrameScheduler`.
   - Exportadores a After Effects JSX, FCPXML y EDL con `PathSanitizer`.

---

## 2. Mapa de Dependencias e Integraciones Reutilizables

| Componente | Ubicación | Uso en Fase 20 |
|---|---|---|
| `Composition.evaluate(t)` | `src/core/composition.ts` | **Evaluación pura:** inspección visual y muestreo en QA sin mutar la IR. |
| `SafeZoneResolver` | `src/captions/safezones/SafeZoneResolver.ts` | Validación geométrica exacta de `CaptionChecks` contra perfiles de plataformas sociales (TikTok, Reels, Shorts). |
| `MotionBudgetManager` | `src/motion-graphics/core/MotionBudgetManager.ts` | Validación cinemática en `VisualChecks` contra el presupuesto de movimiento. |
| `AudioAnalyzer` / `AudioMath` | `src/audio/` | Análisis de clipping, picos, silencios y balance en `AudioChecks`. |
| `ProjectSerializer` | `src/persistence/ProjectSerializer.ts` | Hashing canónico determinista SHA-256 de `ProductionBrief`, `ProductionJob`, `QAReport` y `ArtifactManifest`. |
| `RevisionManager` | `src/revisions/RevisionManager.ts` | Creación inmutable de nuevas revisiones ($rev_n \to rev_{n+1}$) tras aplicar `ChangeSet`. |
| `PathSanitizer` | `src/exporters/common/PathSanitizer.ts` | Sandboxing de rutas en `ArtifactRegistry` y herramientas MCP. |

---

## 3. Mapa de Nuevos Módulos para Fase 20

1. **Orquestador de Producción (`src/orchestration/`):**
   - `ProductionOrchestrator.ts`, `ProductionJob.ts`, `ProductionState.ts`, `ProductionPlan.ts`, `ProductionStep.ts`, `ProductionContext.ts`, `ProductionResult.ts`.
2. **Scheduler y Resolución de Dependencias (`src/orchestration/scheduler/`):**
   - `StepScheduler.ts`, `DependencyResolver.ts` (DAG con detección de ciclos `ProductionPlanCycleError`), `ExecutionPolicy.ts`.
3. **Motor de Revisiones y ChangeSets (`src/orchestration/revisions/`):**
   - `RevisionEngine.ts`, `ChangeSet.ts`, `ChangeApplier.ts`, `RevisionHistory.ts`, `RollbackEngine.ts`.
4. **Motor de QA Estructurado (`src/orchestration/qa/`):**
   - `QAEngine.ts`, `QACheck.ts`, `QAIssue.ts`, `QAScore.ts`, `QAReport.ts`, `QAThresholds.ts`.
   - `checks/`: `StructuralChecks.ts`, `TimelineChecks.ts`, `CaptionChecks.ts`, `AudioChecks.ts`, `VisualChecks.ts`, `AssetChecks.ts`, `ExportChecks.ts`.
5. **Estrategias de Reparación Deterministas (`src/orchestration/repair/`):**
   - `RepairEngine.ts`, `RepairStrategy.ts`, `RepairPolicy.ts` con protección anti-bucles (`maxRevisions`, `RevisionLoopDetectedError`).
6. **Checkpoints, Aprobación y Artefactos (`src/orchestration/checkpoints/`, `approval/`, `artifacts/`, `events/`):**
   - `CheckpointManager.ts`, `Checkpoint.ts`.
   - `ApprovalEngine.ts`, `ApprovalPolicy.ts`.
   - `ArtifactManifest.ts`, `ArtifactRegistry.ts`.
   - `ProductionEvent.ts`, `EventLog.ts`.
7. **Errores Tipados (`src/orchestration/errors/`):**
   - `OrchestrationErrors.ts` (15 errores con contexto tipado).
8. **Herramientas y Recursos MCP (`src/mcp/`):**
   - 7 Herramientas MCP: `create_production_job`, `run_production_job`, `get_production_status`, `inspect_production_qa`, `revise_production`, `approve_production`, `rollback_production`.
   - 7 Recursos MCP: `production://{jobId}`, `production://{jobId}/revisions`, `production://{jobId}/qa`, `production://{jobId}/artifacts`, `production://{jobId}/events`, `capabilities://production`, `policies://production`.

---

## 4. Riesgos Identificados y Estrategia de Mitigación

| Riesgo | Impacto | Estrategia de Mitigación |
|---|---|---|
| **No-determinismo por timestamps u orden de ejecución** | Hashes divergentes en `jobId` o `QAReport` | Hashing SHA-256 canónico estricto sobre `canonicalize()`, excluyendo timestamps de la representación canónica y ordenando `QAIssue` canónicamente. |
| **Bucles infinitos de reparación (QA $\to$ ChangeSet $\to$ QA $\to$ ...)** | Consumo descontrolado de CPU o bloqueo | `RevisionPolicy` con límites estrictos (`maxRevisions = 5`, `maxSameIssueRepairs = 3`) que lanzan `RevisionLoopDetectedError` ante no-convergencia. |
| **Mutación destructiva de la IR durante el QA** | Inconsistencia de estado | `QAEngine` recibe un contexto inmutable y no modifica la IR; las modificaciones sólo se producen mediante `ChangeSet` validados que crean una **nueva revisión** ($rev_n \to rev_{n+1}$). |
| **Inyección o corrupción a través de MCP** | Vulnerabilidad de seguridad | Validación Zod estricta, rechazo de `eval`/`Function`, sandboxing de rutas con `PathSanitizer` y límites máximos de payload. |

---

## 5. Mapa de Pruebas de 7 Capas y Línea Base

- **Estado de Pruebas Previas:** 557 tests pasando al 100% en verde en 5.38s.
- **Suites a Implementar en Fase 20:**
  1. `src/tests/orchestration/ProductionBriefAndJob.test.ts` (validación Zod, determinismo de `jobId`, máquina de estados y transiciones).
  2. `src/tests/orchestration/DAGSchedulerAndCheckpoints.test.ts` (detección de ciclos `ProductionPlanCycleError`, orden topológico, checkpoints y recuperación).
  3. `src/tests/orchestration/ChangeSetAndRevisionEngine.test.ts` (aplicación de `ChangeSet`, validación de targets, rollback no destructivo y detección de conflictos).
  4. `src/tests/orchestration/QAEngineAndChecks.test.ts` (pruebas exhaustivas de las 7 familias de checks con fixtures positivos y negativos).
  5. `src/tests/orchestration/DeterministicRepairAndLoopProtection.test.ts` (estrategias de reparación, convergencia y detección de bucles `RevisionLoopDetectedError`).
  6. `src/tests/orchestration/ProductionOrchestratorE2E.test.ts` (pipeline completo Brief $\to$ Plan $\to$ IR $\to$ QA $\to$ Repair $\to$ Re-QA $\to$ Export $\to$ Manifest).
  7. `src/tests/orchestration/MCPProductionTools.test.ts` (7 herramientas MCP y 7 recursos declarativos).
  8. `src/tests/orchestration/ProductionOrchestrationPBT.test.ts` (Property-Based Testing con `fast-check` para invariantes, determinismo e idempotencia).
  9. `src/tests/benchmarks/ProductionOrchestratorBenchmark.test.ts` (benchmarks de 10 a 10,000 capas/captions/issues).
