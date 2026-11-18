# Editorial Diff & Proposal-First Engine (Fase 4I — REQ-083)

## 1. Propósito
El **Editorial Diff Engine** calcula con precisión matemática el impacto multidimensional que cualquier cambio produce sobre la línea de tiempo:
$$\Delta IR = IR_{\text{candidate}} - IR_{\text{baseline}}$$
Compara representaciones intermedias (IR), nunca archivos de vídeo renderizados, garantizando velocidad milimétrica y total reproducibilidad.

## 2. Métricas de Impacto y Niveles de Riesgo
- **Deltas Computados:**
  - $\Delta\text{duración}$ en segundos.
  - $\Delta\text{cortes}$ (clips agregados/removidos).
  - $\Delta\text{alineación de ritmo}$ (puntos sobre 100).
  - $\Delta\text{contraste dramático}$.
  - $\Delta\text{pico de carga cognitiva}$.
  - $\Delta\text{integridad de evidencias}$.
- **Clasificación de Riesgo:**
  - `CRITICAL`: Si se elimina evidencia obligatoria o se introducen nuevos defectos `BLOCKING`.
  - `HIGH`: Si la duración varía $>10\%$, el pacing cae $>15$ puntos o la carga cognitiva sube $>0.15$.
  - `MEDIUM`: Variaciones moderadas de montaje y desplazamientos temporales.
  - `LOW`: Cambios cosméticos o $diff(A, A) = \emptyset$.

## 3. Arquitectura Proposal-First
Toda corrección automática se genera como una `EditorialProposal`. Para ser aplicada, el motor valida que el `beforeChecksum` coincida exactamente con la IR de destino; en caso de discrepancia por edición concurrente, arroja `ChecksumMismatchError`, garantizando la no destructividad del proyecto.
