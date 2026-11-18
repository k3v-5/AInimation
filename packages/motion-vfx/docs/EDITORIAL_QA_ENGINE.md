# Editorial QA & Audit Engine (Fase 4I — REQ-030 & REQ-081)

## 1. Propósito y Filosofía
El **Editorial QA Engine** actúa como el árbitro transversal del compilador editorial.
**Principio de No-Recalculación:** No vuelve a calcular algoritmos de atención, ritmo o evidencias desde cero; agrega los diagnósticos computados por las capas especializadas y aplica políticas de calidad sobre la `EditorialIR`.

## 2. Severidades y Reglas
- **`BLOCKING`:** Impide la exportación (`canExport = false`). Errores críticos como brechas negras en vídeo primario (`QA-TIME-002`), assets no encontrados (`QA-ASSET-001`), afirmaciones sin fuente verificada (`QA-EVIDENCE-001`) o datos sin respaldo factual (`QA-DATA-001`).
- **`WARNING`:** Alertas de riesgo editorial que permiten exportación (`QA-TIME-001` flash frames, `QA-COGNITIVE-001` sobrecarga cognitiva, `QA-PACING-001` desviación de ritmo, `QA-CONTRAST-001` monotonía).
- **`SUGGESTION`:** Optimizaciones opcionales de montaje y balance compositivo.

## 3. Puntuación Global (`overallScore`)
$$\text{overallScore} = \text{clamp}(100.0 - 25.0 \cdot N_{\text{blocking}} - 5.0 \cdot N_{\text{warning}} - 1.0 \cdot N_{\text{suggestion}}, 0.0, 100.0)$$
Todo reporte emite un sello inmutable SHA-256 sobre JSON Canónico.
