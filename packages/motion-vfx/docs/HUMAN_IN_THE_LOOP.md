# Human-in-the-Loop Governance (Fase 4I — REQ-082)

## 1. Propósito
Garantiza la supervisión y control humano sobre decisiones editoriales complejas mediante una cola de revisión priorizada (`HumanReviewQueue`), evitando la toma de decisiones ciegas por parte de la IA en situaciones de ambigüedad.

## 2. Calibración de Umbrales de Confianza
En lugar de un umbral universal rígido, cada familia de reglas cuenta con su propio umbral de certeza requerido:
- `QA-EVIDENCE-001` (Afirmaciones y Datos): $\ge 0.85$
- `QA-ASSET-001` (Licencias y Fuentes): $\ge 0.90$
- `QA-COGNITIVE-001` (Mitigación Sensorial): $\ge 0.75$
- `QA-PACING-001` (Alineación de Ritmo): $\ge 0.60$
- `QA-TIME-001` (Cortes y Flash Frames): $\ge 0.70$

## 3. Invariante de Bloqueo
**`BLOCKING` nunca se desestima por confianza:** Los hallazgos clasificados como `BLOCKING` siempre entran a la cola de revisión humana para su resolución explícita o rechazo justificado.

## 4. Prioridad y Trazabilidad Inmutable
$$\text{priority} = \text{clamp}(\text{severityWeight} \cdot (1 - \text{confidence}) \cdot \text{impactWeight} + \text{blockingBonus}, 0.0, 1.0)$$
Toda decisión humana queda registrada en `ReviewDecision` con firmas criptográficas `checksumBefore` y `checksumAfter`, preservando el historial completo de auditoría.
