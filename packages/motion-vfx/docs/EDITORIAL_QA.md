# Editorial Quality Assurance (QA) Engine & Auditoría Pre-Render

**Documento:** `docs/EDITORIAL_QA.md`  
**Módulos:** `src/editorial/qa/`  
**Requisitos cubiertos:** REQ-030, REQ-081  
**Estado:** PRODUCTION CERTIFIED — LEVEL 5  
**Versión de Motor:** `v4.0.0-editorial-master`  

---

## 1. Propósito y Filosofía

El **Editorial QA Engine** inspecciona y valida formalmente la Representación Intermedia Editorial (`EditorialIR` / `EditorialDocument`) antes de cualquier invocación a ExtendScript JSX, compilación visual, procesamiento de audio o renderizado final.

### Principios Fundamentales
1. **No-Destructividad (REQ-030-P01):** El QA jamás muta vídeo, audio, imágenes, archivos de proyecto o la IR de entrada. Todas las remediaciones propuestas son puramente declarativas y estructuradas.
2. **Determinismo Criptográfico (REQ-030-P02):** Misma IR + misma configuración $\implies$ salida binariamente idéntica (`QAHash.canonicalStringify()` y `QAHash.computeCanonicalSha256()`). No depende de horas de reloj volátiles, números aleatorios o iteración no ordenada de propiedades.
3. **Calidad Cuantificable y Clamping:** Puntuación global `qualityScore` acotada estrictamente en $[0, 100]$:
   $$\text{qualityScore} = \text{clamp}(100 - (25 \times N_{\text{BLOCKING}} + 5 \times N_{\text{WARNING}} + 1 \times N_{\text{SUGGESTION}}), 0, 100)$$
4. **Política de Bloqueo Inviolable:** Si existe al menos un hallazgo de severidad `BLOCKING`, `status = "BLOCKED"` y `canExport = false`, con independencia del score numérico.

---

## 2. Severidades y Acciones

| Severidad | Código | Impacto en Exportación | Destino Automático |
|---|---|---|---|
| **BLOCKING** | Invalida certificación | `canExport = false`, `status = "BLOCKED"` | Cola de Revisión Humana y Bloqueo de Pipeline |
| **WARNING** | Alerta editorial | `canExport = true` (salvo `--strict` / `--fail-on-warnings`) | Reporte de Auditoría; cola si confianza $< 0.70$ |
| **SUGGESTION**| Optimización opcional | No bloquea exportación | Recomendaciones contextuales |

---

## 3. Catálogo Canónico de Reglas Implementadas

### 3.1 Estructura (`STRUCTURAL`)
- `QA-STRUCT-001`: Detección de pistas vacías o lista de pistas corrupta.
- `QA-STRUCT-002`: Detección de clips sin `assetId` o referenciando assets ausentes en el registro.
- `QA-STRUCT-003`: Identificadores duplicados en tracks o clips (colisiones).
- `QA-STRUCT-004`: Validación de esquema IR (`schemaVersion`, `projectId`, `metadata`).

### 3.2 Temporalidad (`TEMPORAL`)
- `QA-TIME-001`: Duraciones no negativas ($duration \ge 0$).
- `QA-TIME-002`: Timecodes finitos y válidos (rechaza estrictamente `NaN`, `Infinity`, números negativos).
- `QA-TIME-003`: Inversión temporal ($start \le end$).
- `QA-TIME-004`: Solapamientos temporales ilegales en pistas primarias mono-composición.
- `QA-TIME-005`: Huecos no intencionados (Head Gaps y Black Gaps inter-clip).
- `QA-TIME-006`: Consistencia entre duración declarada en metadata y extensión de clips acumulada ($\epsilon \le 10^{-3}$).

### 3.3 Narrativa (`NARRATIVE`)
- `QA-NARR-001`: Ausencia de beats obligatorios (`HOOK`, `CLIMAX`).
- `QA-NARR-002`: Inversión causal (revelación antes de investigación/pregunta).
- `QA-NARR-003`: Spoilers prematuros antes del tiempo de maduración dramática.

### 3.4 Evidencia (`EVIDENCE`)
- `QA-EVIDENCE-001`: Afirmaciones fácticas obligatorias sin respaldo probatorio o con fuente ausente.
- `QA-EVIDENCE-003`: Afirmaciones que requieren tarjeta de citación en pantalla.

### 3.5 Rendimiento y Exportación (`EXPORT`, `COGNITIVE`, `PACING`)
- `QA-LOAD-001`: Sobrecarga cognitiva sostenida ($C \ge 0.85$ durante $\ge 3.0\text{s}$).
- `QA-PACE-001`: Desalineación de ritmo editorial frente a la curva objetivo.
- `QA-EXPORT-001`: Validación de compatibilidad con After Effects (dimensiones no nulas y pistas activas).

---

## 4. Uso Mediante CLI

```bash
# Auditoría rápida con salida estándar
npm run editorial:qa -- --input=fixtures/editorial/qa/golden-valid-documentary.json

# Salida en JSON estructurado
npm run editorial:qa -- --input=fixtures/editorial/qa/golden-valid-documentary.json --json

# Modo estricto para CI/CD (falla en WARNINGS)
npm run editorial:qa -- --input=fixtures/editorial/qa/golden-warning-pacing.json --strict
```
