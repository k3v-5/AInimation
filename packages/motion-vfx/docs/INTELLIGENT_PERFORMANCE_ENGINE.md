# Intelligent Performance & Semantic Trimming Engine (RF-056)
## Motor Objetivo: v4.0.0-editorial-master | Nivel 5 de Producción Certificado

El **Intelligent Performance & Semantic Trimming Engine (RF-056)** es el subsistema de poda editorial semántica y selección de tomas del motor editorial v4.0.0. Opera de forma 100% determinista, declarativa y **proposal-first**, garantizando que ningún material fuente sea modificado destructivamente y preservando la naturalidad interpretativa, la causalidad narrativa y la evidencia factual.

---

## 1. Principios Arquitectónicos
1. **No Destructividad (`REQ-056.001`):**
   Los archivos de vídeo y audio originales nunca se sobrescriben, cortan ni recodifican. Toda decisión se plasma como propuestas estructuradas en la IR Editorial.
2. **Proposal First (`REQ-056.002`):**
   $$\text{Detection} \longrightarrow \text{Scoring} \longrightarrow \text{Proposal} \longrightarrow \text{Validation} \longrightarrow \text{Commit to IR}$$
3. **Determinismo Criptográfico (`REQ-056.003`):**
   $$\text{same input} + \text{same profile} + \text{same version} \implies \text{byte-identical report and SHA-256}$$
   Cero números no finitos (`NaN`, `Infinity`), cero aleatoriedad, serialización canónica con claves ordenadas lexicográficamente y redondeo a 4 decimales.
4. **Preservación de Expresividad Humana:**
   Protección prioritaria de risas espontáneas, respiraciones expresivas y pausas reflexivas (`preservationWeight >= 0.75`), frente a errores técnicos eliminables (`FALSE_START`, `STUTTER`, `TECHNICAL_ERROR`).

---

## 2. Componentes del Subsistema

### 2.1 `SemanticRedundancyEngine`
- **Fórmula de Redundancia Semántica:**
  $$\text{redundancyScore} = \text{clamp}(0.40 \cdot s_{\text{sem}} + 0.30 \cdot o_{\text{info}} + 0.15 \cdot p_{\text{temp}} + 0.15 \cdot r_{\text{narr}}, 0, 1)$$
- **Protección de Evidencia (`REQ-056.020`):**
  Si el segmento B aporta hechos, fechas, citas o cifras no presentes en A, se conserva B y no se considera redundantemente descartable.
- Recomendaciones: `KEEP_BOTH`, `KEEP_A`, `KEEP_B`, `REVIEW`.

### 2.2 `BestTakeSelector`
- **Score Ponderado de Toma:**
  $$\begin{aligned}
  \text{takeScore} &= 0.20 \cdot \text{sem} + 0.15 \cdot \text{phon} + 0.15 \cdot \text{voc} + 0.10 \cdot \text{vis} + 0.10 \cdot \text{eye} \\
  &+ 0.10 \cdot \text{nat} + 0.10 \cdot \text{cont} + 0.05 \cdot \text{aud} + 0.05 \cdot \text{dur}
  \end{aligned}$$
- **Desempate Determinista:**
  Ante una diferencia $< 0.02$, se desempatará en orden:
  1. Mayor integridad semántica.
  2. Mayor naturalidad.
  3. Mayor claridad fonética.
  4. Mejor continuidad.
  5. Menor duración.
  6. ID lexicográficamente menor.
- Auto-selección: `winnerScore >= 0.80` y diferencia $\ge 0.05$. En caso contrario, se deriva a `REVIEW`.

### 2.3 `NaturalPerformancePreservation`
- Clasificación de 12 marcadores (`BREATH`, `LAUGH`, `REFLECTIVE_PAUSE`, `EMPHATIC_PAUSE`, `EMOTIONAL_REACTION`, `FALSE_START`, `STUTTER`, `WORD_REPETITION`, `TECHNICAL_ERROR`, `HESITATION`, `FILLER`, `UNCERTAINTY`).
- Regla: `if (authenticityScore > technicalDefectScore) PRESERVE` (salvo `TECHNICAL_ERROR`).

### 2.4 `IntelligentTrimmingEngine` (Orquestador)
- **Límites Físicos:** $0 \le \text{start} < \text{end} \le \text{sourceDuration}$.
- **Padding Editorial:** `preRoll = 0.08s`, `postRoll = 0.12s`, protección de respiración a $\pm 0.15s$.
- **Micro-Crossfade:** Transiciones automáticas de $0.025s$ para evitar chasquidos acústicos.
- **Protección contra Sobrepoda:** Si $\text{reductionRatio} > 0.30$ ($30\%$), el estado pasa a `REVIEW_REQUIRED`.

---

## 3. CLI y Herramientas MCP
- **CLI:**
  ```bash
  npm run editorial:trim -- --input fixtures/performance/intelligent-trimming-production.json --dry-run
  ```
- **Herramientas MCP:**
  - `editorial_detect_redundancy`
  - `editorial_select_best_take`
  - `editorial_analyze_performance`
  - `editorial_generate_trim_plan`
  - `editorial_get_trim_report`

---

## 4. Batería de Pruebas
1. `SemanticRedundancyEngine.test.ts`: 4/4 PASS
2. `BestTakeSelector.test.ts`: 4/4 PASS
3. `NaturalPerformancePreservation.test.ts`: 3/3 PASS
4. `IntelligentTrimmingEngine.test.ts`: 5/5 PASS
5. `PerformancePropertyTests.test.ts` (PBT 1 a 7 con `fast-check`): 4/4 PASS
6. `GoldenEditorialSnapshot.test.ts` (Fixture de producción): 5/5 PASS
- **Total Suite:** 1,190 / 1,190 pruebas en verde (421 suites). Gate 20 aprobado.
