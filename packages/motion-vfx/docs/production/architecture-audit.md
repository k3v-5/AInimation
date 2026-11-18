# Auditoría de Arquitectura: Fase 18 — Production Control Plane

**Fecha:** 2026-08-26  
**Objetivo:** Auditar la base de código existente para integrar la capa de orquestación de producción, control de revisiones inmutables, Render QA y validaciones sin duplicar lógica ni romper la IR canónica.

---

## 1. Estado de la Base de Código (Fases 1–17)

1. **IR Canónica y Core Temporal:**
   - `src/core/`: `Composition`, `Layer`, `Property<T>`, `Keyframe<T>`, `Transform`.
   - `src/timeline/`: `VideoTimeline`, `TimelineTrack`, `Clip`, `TimeRange`.
   - `src/elements/`: `BaseElement`, `ShapeElement`, `TextElement`, `VideoElement`, `AudioElement`, `ImageElement`.
   - `src/captions/`: `CaptionEngine`, `CaptionTimeline`, `WordHighlighting`, `WhisperParser`, `SRTParser`.
   - `src/rendering/`: `RenderPipeline`, `FrameScheduler`, `Compositor`, `RenderGraph`, `RenderValidator`.
   - `src/exporters/`: `AfterEffectsJSXCompiler`, `FCPXMLExporter`, `EDLExporter`, `CapabilityMatrix`, `ExportManifest`, `PathSanitizer`, `TimecodeUtils`.
   - `src/runtime/`: `ProjectRuntime`, `ProjectRepository`, `ProjectSession`, `ProjectTransaction`, `StorageAdapter`, `FileSystemStorageAdapter`, `MemoryStorageAdapter`, `ProjectSerializer`.

2. **Suite de Tests Actual:**
   - Total de suites: **257 suites**.
   - Total de tests: **534 tests pasando al 100% en verde**.

3. **Invariantes Arquitectónicos:**
   - La IR canónica es la única fuente de verdad.
   - Cero funciones no deterministas (`Math.random()`, `Date.now()`, `new Date()`) en la IR y en los hashes canónicos.
   - Hashing determinista basado en serialización canónica con claves ordenadas lexicográficamente, números normalizados y UTF-8 estricto.

---

## 2. Reutilización vs Nuevos Módulos

| Componente Requerido | Decisión Arquitectónica |
|---|---|
| **Hashing Canónico** | Reutilizar y extender `ProjectSerializer` / `RevisionHasher` en `src/production/revision/RevisionHasher.ts` para garantizar hashes idénticos cross-process. |
| **Persistencia y Storage** | Reutilizar `StorageAdapter` (`FileSystemStorageAdapter` / `MemoryStorageAdapter`) desacoplando la persistencia de revisiones y checkpoints. |
| **Modelos de Producción** | Crear en `src/production/model/`: `ProductionProject`, `ProductionRevision`, `ProductionCheckpoint`, `ProductionOperation`. |
| **Operaciones Declarativas** | Crear en `src/production/model/ProductionOperation.ts` y `RevisionBuilder.ts` aplicando mutaciones puras sobre la IR. |
| **Diff Estructurado** | Crear en `src/production/revision/RevisionDiff.ts` detectando composiciones, capas, propiedades, keyframes, captions, timing, resolución y efectos. |
| **Validación Pre-Render** | Crear en `src/production/validation/`: `ProductionValidator`, `StructuralValidator`, `TemporalValidator`, `VisualValidator`, `AudioValidator`, `CaptionValidator`, `AssetValidator`. |
| **Render QA** | Crear en `src/production/qa/`: `RenderQAEngine`, `QARules` (15 reglas obligatorias), `QAReport`, `QAIssue`, `QASamplingStrategy`. |
| **Pipeline de Producción** | Crear en `src/production/orchestration/`: `ProductionPipeline`, `PipelineStage`, `PipelineContext`, `PipelineExecutor` con soporte `dryRun`. |
| **MCP Tools** | Integrar en `src/mcp/tools/` las 7 herramientas de producción y exponer recursos `production://`. |

---

## 3. Conclusión de Auditoría

La arquitectura existente proporciona una base modular y determinista sólida. La nueva capa en `src/production/` operará como el plano de control y aseguramiento de calidad (QA) sobre la IR canónica, garantizando reproducibilidad total, inmutabilidad de revisiones y capacidad de rollback sin pérdida de historial.
