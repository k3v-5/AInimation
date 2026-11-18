# 🔍 DYNAMIC PUNCH-IN ENGINE
## ESPECIFICACIÓN TÉCNICA DEL MÓDULO (v3.5.0)
**Documento:** `docs/vlog-expansion/06-DYNAMIC-PUNCH-IN.md`  
**Capa:** `v3.5.x Vlog Intelligence Layer`  
**Estado:** `FUENTE ÚNICA DE VERDAD (SSOT) — ESPECIFICACIÓN TÉCNICA`  
**Versión:** `1.0.0`  
**Fecha:** `2026-09-01`  

---

## 1. Propósito
Calcular eventos de modulación dinámica de escala ($100\% \to 115\% \to 100\%$) sobre tomas A-Roll habladas, gatillados por eventos editoriales (picos de energía, preguntas o énfasis) para mantener la atención del espectador sin requerir cortes de cámara físicos.

## 2. Alcance
- Detección de picos de energía acústica RMS $\ge 0.70$.
- Detección de palabras de énfasis, signos de exclamación o interrogación en el transcript.
- Control estricto de cooldown ($2.5\text{s}$) para evitar saltos de zoom consecutivos o desagradables.
- Acotación de duración de cada punch-in entre $[1.20\text{s}, 6.00\text{s}]$.
- Abstracción de `FocusPoint` normalizado $[0.0, 1.0]$ con centrado geométrico por defecto.

## 3. No Alcance
- No realiza tracking facial en tiempo real por píxeles en esta fase (provee la abstracción `FocusPoint` lista para recibir coordenadas de visión en Fase 2).
- No aplica zoom continuo progresivo (*slow push-in*); calcula cambios de encuadre en cortes o fronteras de palabra.

## 4. Entradas
- `segments: Array<{ start: number; end: number; duration: number }>`: Segmentos de habla activos.
- `energyProfile?: AudioSamplePoint[]`: Muestras RMS del audio.
- `transcript?: TranscriptAnalysis`: Palabras con marcas de tiempo y texto.
- `config: VlogJumpCutConfig`: Parámetros de escala, cooldown y umbrales.

## 5. Salidas
- `PunchInEvent[]`: Lista ordenada de eventos de punch-in calculados:
  - `start: number`: Timestamp de inicio del punch-in.
  - `end: number`: Timestamp de fin del punch-in.
  - `scale: number`: Escala aplicada ($1.15$).
  - `focusPoint: FocusPoint`: Punto central de encuadre.
  - `reason: PunchInTriggerReason`: Causa del disparo (`emphasis`, `energy_climax`, etc.).

## 6. Interfaces
```typescript
export interface FocusPoint {
  readonly x: number; // 0.0 a 1.0
  readonly y: number; // 0.0 a 1.0
}

export type PunchInTriggerReason =
  | "emphasis"
  | "sentence_boundary"
  | "energy_climax"
  | "manual";

export interface PunchInEvent {
  readonly start: number;
  readonly end: number;
  readonly scale: number;
  readonly focusPoint: FocusPoint;
  readonly reason: PunchInTriggerReason;
}
```

## 7. Configuración
```typescript
export interface DynamicPunchInConfig {
  readonly normalScale: number;            // 1.00
  readonly punchInScale: number;           // 1.15
  readonly minPunchInDurationSec: number;    // 1.20 s
  readonly maxPunchInDurationSec: number;    // 6.00 s
  readonly punchInCooldownSec: number;       // 2.50 s
  readonly punchInEnergyThreshold: number; // 0.70 (RMS)
  readonly defaultFocusPoint: FocusPoint;  // { x: 0.5, y: 0.5 }
}
```

## 8. Algoritmo
1. Inicializar `lastPunchInEnd = -config.punchInCooldownSec`.
2. Para cada segmento de habla $S_i$:
   - Comprobar si $(S_i.\text{start} - \text{lastPunchInEnd}) \ge \text{punchInCooldownSec}$. Si es menor, omitir.
   - Extraer muestras de energía en $[S_i.\text{start}, S_i.\text{end}]$ y calcular $\text{maxRMS}$.
   - Evaluar si $\text{maxRMS} \ge \text{punchInEnergyThreshold}$.
   - Evaluar si alguna palabra en el segmento contiene `?`, `!` o mayúsculas sostenidas.
   - Si se cumple condición de disparo:
     - $\text{targetDuration} = \min(\text{maxDuration}, \max(\text{minDuration}, S_i.\text{duration}))$.
     - $\text{pEnd} = \min(S_i.\text{start} + \text{targetDuration}, S_i.\text{end})$.
     - Registrar `PunchInEvent` con `scale = punchInScale` ($1.15$) y `focusPoint = defaultFocusPoint`.
     - Actualizar `lastPunchInEnd = pEnd`.
3. Retornar lista de `PunchInEvent[]`.

## 9. Reglas de Negocio
- **RN-P01 (No Saturación):** No pueden existir dos punch-ins separados por menos de $2.5\text{s}$ de video.
- **RN-P02 (Duración Mínima):** Un punch-in no puede durar menos de $1.20\text{s}$ para evitar parpadeos visuales molestos.
- **RN-P03 (Respeto de Frontera):** Un punch-in nunca puede extenderse más allá del final del segmento de habla en el que se originó.

## 10. Invariantes
- **INV-P01:** $\forall P \in \text{PunchIns}: P.\text{scale} == 1.15$.
- **INV-P02:** $\forall P \in \text{PunchIns}: 0.0 \le P.\text{focusPoint}.x \le 1.0 \land 0.0 \le P.\text{focusPoint}.y \le 1.0$.
- **INV-P03:** $\forall i: P_{i+1}.\text{start} - P_i.\text{end} \ge 2.50\text{s}$.

## 11. Casos Normales
- Discurso con 1 frase tranquila (1.00) seguida de una exclamación (1.15 durante 3s) y retorno a la normalidad (1.00).

## 12. Casos Límite
- **Audio Monótono sin Picos:** 0 punch-ins generados; todo el video permanece al $100\%$.
- **Segmento de 0.5s con Energía Alta:** El punch-in se acota exactamente a $0.5\text{s}$ (no desborda el segmento).
- **Ráfaga de 5 Preguntas Seguidas en 3 Segundos:** Se dispara el punch-in en la primera pregunta y el cooldown bloquea las siguientes 4 para evitar saltos epilépticos.

## 13. Errores
- `InvalidTimeRangeError`: Segmentos con timestamps inválidos o invertidos.

## 14. Recuperación
- Si faltan datos de energía o transcript, el módulo opera con los datos disponibles sin fallar (degrada a detección por energía si no hay transcript, o por texto si no hay audio RMS).

## 15. Determinismo
- 100% determinista: el mismo set de segmentos y energía produce exactamente los mismos punch-ins.

## 16. Rendimiento
- Evaluación instantánea en memoria ($< 5\text{ms}$ para un video de 1 hora).

## 17. Dependencias
- `src/automation/vlog/jump-cut/types.ts` y `config.ts`.

## 18. Compatibilidad
- Las escalas resultantes se mapean a keyframes de escala y posición en Adobe After Effects (`layer.transform.scale.setValue([115, 115])`).

## 19. Seguridad
- Focus points estrictamente acotados a $[0.0, 1.0]$ para impedir que la cámara se desplace fuera del encuadre.

## 20. Tests
- Tests unitarios en `src/tests/automation/vlog/jump-cut/DynamicPunchIn.test.ts`.

## 21. Fixtures
- Segmentos sintéticos con perfiles de energía controlados.

## 22. Golden Tests
- Snapshot de punch-ins de `golden-vlog-input.json`.

## 23. Integración
- Invocado directamente por `VlogJumpCutEngine.ts` durante el paso 6 del pipeline editorial.

## 24. Definition of Done
- Tests de Dynamic Punch-In pasando al 100% con verificación de cooldown y escalas.
