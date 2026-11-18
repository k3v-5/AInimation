# Auditoría de Arquitectura e Integración: Fase 19 — Deterministic Render Orchestration, Preview Engine & Production Render Pipeline (v1.9.0)

## 1. Arquitectura Encontrada

El repositorio `after-effects-mcp` cuenta con un motor audiovisual modular y determinista estructurado en 18 fases previas:

1. **Núcleo Temporal y Composición (`src/core/`):**
   - `Composition`: contenedor principal con dimensiones (`width`, `height`), `fps`, `duration`, y registro de assets.
   - `Composition.evaluate(time: Time)`: método central de evaluación que genera snapshots inmutables (`CompositionSnapshot`, `LayerSnapshot`, `BaseElementState`) sin mutación de estado.
   - Tipos temporales racionales y validaciones estrictas (`src/core/types.ts`, `src/validation/validators.ts`).

2. **Modelo de Elementos y Capas (`src/elements/` y `src/core/layer.ts`):**
   - `BaseElement`: clase base abstracta (`TextElement`, `VideoElement`, `AudioElement`, `ShapeElement`, etc.) que implementa `evaluate(time)`.
   - Sistema de transformación 2D afín (`src/transform/`, `Matrix2D`).

3. **Línea de Tiempo y Audio (`src/timeline/` y `src/audio/`):**
   - `VideoTimeline`, `Track`, `Clip`, `TimeRange`.
   - `AudioEngine` completo con `AudioBuffer`, `AudioMixer`, `MasterBus`, `AudioMath` y `AudioAnalyzer`.

4. **Motor de Subtítulos y Tipografía (`src/captions/` y `src/typography/`):**
   - `CaptionDocument`, `CaptionSegment`, `CaptionWord`, `CaptionEvaluator`, `SafeZoneResolver`.
   - Layout tipográfico cinético con cálculo determinista de bounds visuales y staggers.

5. **Persistencia y Control de Revisiones (`src/persistence/` y `src/revisions/` - Fase 18):**
   - `ProjectStore` (`MemoryProjectStore`, `FileProjectStore` con escrituras atómicas `.tmp` $\to$ `fsync` $\to$ `rename`).
   - `ProjectSerializer`: serialización canónica determinista y hashes SHA-256.
   - `RevisionGraph` (DAG no lineal), `RevisionDiff`, `RevisionPatch` y `RevisionMerge`.

6. **Renderizado Inicial Preexistente (`src/rendering/`):**
   - Existe una base inicial de Fase 9 con `RenderGraph`, `Compositor`, `FrameScheduler`, `RenderPipeline`, `RenderValidator` y `OutputProfiles`.

---

## 2. Módulos Reutilizables

| Módulo Existente | Ubicación | Cómo se Reutiliza en Fase 19 |
|---|---|---|
| `Composition.evaluate(t)` | `src/core/composition.ts` | **Fuente de verdad:** evalúa el estado del fotograma en el instante $t$ sin duplicar animación. |
| `BlendMath` | `src/compositing/core/BlendMath.ts` | Mezcla de píxeles y modos de fusión (Alpha, Screen, Multiply, Add, etc.). |
| `AudioMixer` / `AudioBuffer` | `src/audio/` | Renderizado y mezcla de audio multicanal con sample rate exacto (44.1/48kHz). |
| `CaptionEvaluator` | `src/captions/core/CaptionEvaluator.ts` | Extracción de subtítulos activos y palabras destacadas en el instante $t$. |
| `ProjectSerializer` | `src/persistence/ProjectSerializer.ts` | Serialización canónica y generación de hashes SHA-256 de jobs, configs y manifests. |
| `PathSanitizer` | `src/exporters/common/PathSanitizer.ts` | Validación y sandboxing de rutas de salida para prevenir Path Traversal. |
| `fast-check` | `devDependencies` | Property-Based Testing para invariantes de determinismo, renderizado y chunking. |

---

## 3. Módulos que Faltan para Fase 19 (v1.9.0)

1. **Orquestación y Configuración Declarativa (`src/rendering/core/`):**
   - `RenderConfig.ts` (esquema Zod estricto y tipos).
   - `RenderJob.ts` (identidad determinista $jobId = \text{hash}(\text{canonicalIR} + \text{config} + \text{version} + \text{seed})$).
   - `RenderContext.ts`, `RenderResult.ts`, `RenderProgress.ts`, `RenderCancellation.ts`.

2. **Render Graph & Scheduler Topológico (`src/rendering/graph/`):**
   - `TopologicalScheduler.ts` con detección estricta de ciclos (`RenderGraphCycleError`) y ordenamiento determinista.
   - `RenderGraphBuilder.ts` y `RenderGraphExecutor.ts`.

3. **Frame Rendering & Buffers (`src/rendering/frame/`):**
   - `FrameRenderer.ts`, `FrameStateRenderer.ts`, `FrameBuffer.ts`, `PixelFormat.ts` (`rgba8`, `rgb24`, `bgra8`), `ColorSpace.ts`.

4. **Scheduler Concurrente & Chunks (`src/rendering/scheduler/`):**
   - `ChunkPlanner.ts`, `RenderWorker.ts`, `RenderScheduler.ts`, `DeterministicOrdering.ts`.

5. **Caché Determinista & Invalidación (`src/rendering/cache/`):**
   - `RenderCache.ts`, `RenderCacheKey.ts`, `FrameCache.ts`, `NodeCache.ts`, `CacheManifest.ts`.

6. **Preview Engine (`src/rendering/preview/`):**
   - `PreviewRenderer.ts`, `PreviewConfig.ts`, `PreviewResult.ts` (salidas `json-state`, `svg`, `png`).

7. **Salida de Producción & Encoders (`src/rendering/output/`):**
   - `ImageSequenceWriter.ts` (escritura atómica con padding determinista `frame_000000.png`).
   - `VideoEncoder.ts` y `AudioEncoder.ts` (detección de FFmpeg con fallback explícito `EncoderUnavailableError`).
   - `Muxer.ts`, `OutputValidator.ts`.

8. **Checkpoints y Recuperación (`src/rendering/resume/`):**
   - `RenderCheckpoint.ts`, `RenderCheckpointStore.ts`, `RenderRecovery.ts`.

9. **Hashes y Verificación de Determinismo (`src/rendering/hashing/`):**
   - `FrameHasher.ts`, `OutputHasher.ts`, utilidad `verifyDeterministicRender()`.

10. **Jerarquía de Errores Tipados (`src/rendering/errors/`):**
    - 14 errores tipados con contexto completo.

---

## 4. APIs Públicas Existentes y Contratos que NO Deben Romperse

- `Composition.evaluate(time: Time): CompositionSnapshot`
- `BaseElement.evaluate(time: Time): BaseElementState`
- `ProjectStore` e interfaces de persistencia de Fase 18.
- 16 herramientas MCP existentes de Fase 17 y Fase 18.
- Todas las 557 pruebas unitarias y de integración de Fases 1–18 deben permanecer 100% en verde.

---

## 5. Riesgos Identificados y Estrategia de Mitigación

| Riesgo | Impacto | Estrategia de Mitigación |
|---|---|---|
| **No-determinismo por concurrencia** | Salidas divergentes entre 1 y 4 workers | Los workers renderizan chunks desacoplados a buffers temporales indexados; el ensamblado y secuenciación se realiza mediante ordenamiento topológico determinista. |
| **Drift en cálculo de tiempos de frame** | Desincronización acumulativa de audio/video | Cálculo exacto de frame boundaries: $t_n = \frac{n}{\text{fps}}$, evitando sumas sucesivas de números de coma flotante. |
| **Corrupción de archivos por interrupción** | Archivos incompletos marcados como válidos | Escritura atómica `.tmp` $\to$ `flush` $\to$ `validate` $\to$ `atomic rename`. |
| **Ausencia de binarios FFmpeg en CI/CD** | Fallo espurio de tests | Detección limpia de entorno: si FFmpeg no está disponible, se emite `EncoderUnavailableError` con fallback a `ImageSequenceWriter` y se aíslan los tests dependientes de códec. |
| **Uso excesivo de memoria en renders largos** | OOM al acumular fotogramas en RAM | Procesamiento en streaming por chunks con liberación explícita de `FrameBuffer` tras escritura a disco o encoder. |

---

## 6. Comandos Reales del Repositorio

- **Compilación TypeScript:** `npm run build` (`tsc && copyfiles -u 1 "src/scripts/**/*" build && copyfiles -u 1 "src/tests/**/*.json" build`)
- **Ejecución de Tests:** `npm test` (`node --test build/tests/**/*.test.js`)
- **Entorno:** Node.js v20+, ESM estricto (`"type": "module"`).

---

## 7. Estrategia de Verificación de 7 Capas para Fase 19

1. **Unit Tests:** Configuración, validación Zod, buffers, cálculo de hashes, nodos del grafo.
2. **Integration Tests:** Pipeline completo de render de composición a secuencia de imágenes y preview.
3. **Graph Invariant Tests:** Detección de ciclos ($A \to B \to C \to A$), ordenamiento topológico determinista.
4. **Equivalence Tests:**
   - Concurrency Equivalence (1 worker vs 4 workers $\implies$ idénticos hashes).
   - Cache Equivalence (cache activada vs desactivada $\implies$ idéntico resultado).
   - Chunk Equivalence (chunkSize 1 vs 10 vs 100 $\implies$ idéntico resultado).
   - Resume Equivalence (render completo vs cancel + resume $\implies$ idéntico resultado).
5. **Cross-Process Determinism:** Verificación interproceso de hashes SHA-256 de frames.
6. **Security & Sandbox Tests:** Path traversal, paths nulos, extensiones no permitidas, overwrite false.
7. **Performance Benchmarks:** Escalabilidad probada en 10, 100, 1,000 frames y 10, 100, 1,000 capas.
