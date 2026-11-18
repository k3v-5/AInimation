# Editorial Diff & Version Impact Governance Engine

**Documento:** `docs/EDITORIAL_DIFF.md`  
**Módulos:** `src/editorial/qa/editorial-diff-engine.ts`, `src/editorial/qa/impact-analyzer.ts`  
**Requisitos cubiertos:** REQ-082  
**Estado:** PRODUCTION READY  
**Versión de Motor:** `v4.0.0-editorial-master`  

---

## 1. Propósito

El **Editorial Diff Engine** calcula comparaciones matemáticas y semánticas precisas entre dos versiones sucesivas de la Representación Intermedia Editorial (`before` y `after`).

No se limita a un simple diff textual JSON; analiza el impacto editorial de cada intervención humana o de IA sobre la narrativa, el ritmo (*pacing*), la carga cognitiva, el balance dramático y las restricciones de continuidad.

---

## 2. Tipos Canónicos de Cambio (`EditorialDiffType`)

- `ADDED`: Nuevo clip o elemento insertado en el timeline.
- `REMOVED`: Elemento eliminado de una pista.
- `MODIFIED`: Alteración de parámetros o contenido textual.
- `MOVED`: Desplazamiento temporal de un elemento (`startSeconds`).
- `RESIZED`: Modificación de la duración de un clip (`durationSeconds`).
- `REORDERED`: Cambio en el orden secuencial de clips dentro de una pista.

---

## 3. Desglose Estructurado de Impacto (`EditorialImpactReport`)

Cada reporte de diff (`EditorialDiffReport`) incluye un bloque de impacto multidimensional:

1. **Duración (`duration`):** `beforeSeconds`, `afterSeconds`, `deltaSeconds`.
2. **Ritmo (`pacing`):** Puntuación de alineación previa, posterior y delta.
3. **Atención (`attention`):** Variación en la curva de retención media del espectador.
4. **Carga Cognitiva (`cognitiveLoad`):** Delta en el índice $C = 0.30V + 0.25D + 0.20S + 0.15M + 0.10K$ y número de intervalos de sobrecarga generados o resueltos.
5. **Narrativa (`narrative`):** Conteo de relaciones causales modificadas, beats afectados y si se introdujo riesgo de spoiler.
6. **Continuidad (`continuity`):** Violaciones nuevas vs. resueltas (eje 180°, jump cuts).

---

## 4. Identidad Reflexiva y Determinismo

- $\text{diff}(IR, IR)$ produce estrictamente 0 cambios y nivel de impacto `"NONE"`.
- Los hashes canónicos de entrada (`beforeChecksumSha256` / `fromChecksum`) y salida (`afterChecksumSha256` / `toChecksum`) son sellados con SHA-256 inmutable.

---

## 5. Herramientas MCP Disponibles

- `editorial_compare_revisions`: Realiza el diff estructural y semántico completo.
- `editorial_get_change_impact`: Extrae únicamente la matriz de impacto editorial y nivel de riesgo.
