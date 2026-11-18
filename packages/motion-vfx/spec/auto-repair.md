# 🔧 Especificación del Bucle de Auto-Reparación Determinista (Auto-Repair Engine)

**Estándar:** `Autonomous After Effects MCP — Bounded Auto-Repair Specification`  
**Referencia:** `REQ-027`  

---

## 1. Algoritmo de Auto-Reparación y Convergencia Acotada

Cuando el evaluador de QA detecta un fallo reparable (ej. colisión de texto o texto fuera de safe area), el motor ejecuta un bucle de diagnóstico y corrección con límite estricto de iteraciones:

$$\text{Loop}_{\text{repair}} = \text{Diagnosis} \longrightarrow \text{Candidate Strategy} \longrightarrow \text{Score} \longrightarrow \text{Apply Best Fix} \longrightarrow \text{Re-QA}$$

### Límite de Convergencia:
- $\text{max\_repair\_iterations} = 3$.
- Si tras 3 iteraciones el score no supera el umbral ($\ge 85.0\%$), el motor aborta la transacción y emite un reporte de fallo bloqueante `REPAIR_CONVERGENCE_FAILED` sin entrar en bucles infinitos.
