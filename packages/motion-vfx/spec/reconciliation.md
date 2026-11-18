# 🔍 Especificación de Reconciliación de Estado (Expected vs Actual)

**Estándar:** `Autonomous After Effects MCP — State Reconciliation Specification`  
**Referencia:** `REQ-021`  

---

## 1. Algoritmo de Reconciliación de Capas

Tras compilar y ejecutar instrucciones en After Effects, el motor consulta el estado real del runtime y lo compara contra el estado esperado de la `ProjectIR`:

$$\text{Reconcile}(\text{State}_{\text{expected}}, \text{State}_{\text{actual}}) \longrightarrow \{\text{status}, \text{discrepancies}, \text{warnings}\}$$

### Tolerancias de Equivalencia:
- **Posición ($X, Y$):** $\Delta \le 0.05\text{ px}$ (se considera `EQUIVALENT`).
- **Escala ($S_X, S_Y$):** $\Delta \le 0.01\%$ (se considera `EQUIVALENT`).
- **Rotación:** $\Delta \le 0.01^\circ$ (se considera `EQUIVALENT`).
- **Tiempos ($inPoint, outPoint$):** $\Delta \le 1.0 \text{ frame duration}$ (se considera `EQUIVALENT`).

Si una discrepancia supera el umbral permitido (ej. $\Delta \text{pos} > 2.0\text{ px}$ por modificación no autorizada o error de anclaje), el reconciliador emite un error `RECONCILIATION_MISMATCH` con diagnóstico estructurado para auto-reparación.
