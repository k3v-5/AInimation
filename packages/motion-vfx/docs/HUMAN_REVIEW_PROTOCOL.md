# Protocolo de Revisión Humana en el Bucle (*Human-in-the-Loop*)

**Documento:** `docs/HUMAN_REVIEW_PROTOCOL.md`  
**Módulos:** `src/editorial/qa/human-review-queue.ts`  
**Requisitos cubiertos:** REQ-081, REQ-083  
**Estado:** PRODUCTION READY  
**Versión de Motor:** `v4.0.0-editorial-master`  

---

## 1. Principio Rector

Ninguna decisión con nivel de incertidumbre crítico debe ser adoptada de forma autónoma por la IA sin la confirmación o mediación de un editor humano.

- **Umbral de Confianza:** Cualquier propuesta o hallazgo donde $\text{confidence} < 0.70$ o con severidad `BLOCKING` ingresa obligatoriamente a la `HumanReviewQueue`.
- **Inmutabilidad y No Sobrescritura:** La aprobación, rechazo o modificación humana genera una nueva versión formal de la IR (`IR-vN`) y un evento de auditoría `ReviewAuditEvent`.

---

## 2. Algoritmo de Priorización Determinista

La prioridad de cada elemento en la cola se evalúa en el rango $[0, 100]$:

$$\text{priority} = \text{baseSeverity} + (W_{\text{severity}} \times W_{\text{duration}} \times (1 - \text{confidence}) \times 100)$$

Donde:
- `baseSeverity`: 50.0 para `BLOCKING`, 0.0 para otros.
- $W_{\text{severity}}$: Pesos normalizados (`BLOCKING: 1.0`, `WARNING: 0.6`, `SUGGESTION: 0.2`).
- Desempate estricto: Prioridad $\to$ Confianza $\to$ Timestamp $\to$ ID lexicográfico.

---

## 3. Estados del Ciclo de Vida

```
             ┌───────────┐
             │  PENDING  │
             └─────┬─────┘
       ┌───────────┼───────────┐
       ▼           ▼           ▼
┌───────────┐┌───────────┐┌───────────┐
│ APPROVED  ││ REJECTED  ││ DEFERRED  │
└───────────┘└───────────┘└───────────┘
```

1. **PENDING:** Hallazgo a la espera de intervención humana.
2. **APPROVED:** Aprobado por el editor humano. Si incluye una remediación, ésta se aplica en la nueva revisión de la IR.
3. **REJECTED:** Descartado por el editor humano con justificación obligatoria.
4. **DEFERRED:** Aplazado para revisión editorial posterior.

---

## 4. MCP Tools de Revisión

- `editorial_get_review_queue`: Inspecciona los elementos pendientes ordenados por prioridad.
- `editorial_approve_review`: Aprueba un elemento y registra la firma del revisor.
- `editorial_reject_review`: Rechaza un elemento exigiendo motivo obligatorio.
- `editorial_review_decide`: Decisión genérica con registro en bitácora inmutable.
