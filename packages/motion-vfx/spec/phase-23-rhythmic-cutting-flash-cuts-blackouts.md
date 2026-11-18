# Especificación Técnica: Fase 23 — Machine-Gun Flash Cuts, Syncopated Rhythmic Cutting, Blackout Drops & Audio Vacuums

**Versión:** 1.0.0  
**Fecha:** 2026-09-05  
**Módulo:** `src/rhythm/`  
**Objetivo:** Implementar la cuarta fase del Programa de Videoclips de Alto Calibre para After Effects, permitiendo montaje rítmico ultra-rápido (*Machine-Gun Rapid Cuts*), cortes sincopados a compás musical, y vacíos visuales dramáticos (*Blackout Drops*) inspirados en Kendrick Lamar (*HUMBLE.*), Ralphie Choo (*Máquina Culona*) y Tyler, The Creator.

---

## 1. Fundamentos Matemáticos y Arquitectura Temporal

### 1.1 Rejilla Rítmica y Subdivisión Temporal Cuantizada
Dado un tempo en pulsos por minuto ($\text{BPM} > 0$):
- Duración de un pulso de negra (quarter note):
  $$T_{\text{beat}} = \frac{60.0}{\text{BPM}}$$
- Duración de una barra / compás ($4/4$):
  $$T_{\text{bar}} = 4 \times T_{\text{beat}}$$
- Duraciones de subdivisión:
  $$T_{1/8} = \frac{T_{\text{beat}}}{2}, \quad T_{1/16} = \frac{T_{\text{beat}}}{4}, \quad T_{1/32} = \frac{T_{\text{beat}}}{8}, \quad T_{\text{triplet}} = \frac{T_{\text{beat}}}{3}$$

Todos los tiempos calculados se cuantizan estrictamente a la rejilla de fotogramas del proyecto ($\text{FPS}$):
$$t_{\text{snapped}} = \frac{\text{round}(t \cdot \text{FPS})}{\text{FPS}}$$

### 1.2 Ráfagas "Machine-Gun" (High-Frequency Strobe Cuts)
Una ráfaga *Machine-Gun* intercala fotogramas de metraje o sólidos de color (blanco puro, rojo carmesí `#FF1424` o inversión cromática) durante una ventana temporal $[t_{\text{start}}, t_{\text{end}}]$:
- Período por corte: $\tau \in \{1, 2, 3\} \text{ frames}$.
- Número de cortes en la ráfaga:
  $$N_{\text{cuts}} = \left\lfloor \frac{(t_{\text{end}} - t_{\text{start}}) \cdot \text{FPS}}{\tau} \right\rfloor$$
- Cada corte activa una capa con visibilidad mutuamente excluyente durante $\tau$ frames:
  $$\text{inPoint}_k = t_{\text{start}} + \frac{k \cdot \tau}{\text{FPS}}, \quad \text{outPoint}_k = \text{inPoint}_k + \frac{\tau}{\text{FPS}}$$

### 1.3 Vacío Visual y Caída a Negro (Blackout Drop & Audio Vacuum)
En producciones de alto impacto, justo antes de un *drop* sonoro explosivo o cambio drástico de beat (*beat switch*), el audio entra en succión/vacío (*vacuum*) y la imagen se apaga a negro absoluto durante $\Delta t_{\text{vacuum}} \in [0.06\text{s}, 0.35\text{s}]$:
- Intervalo de vacío: $[t_{\text{drop}} - \Delta t_{\text{vacuum}}, t_{\text{drop}}]$
- En After Effects: todas las capas de video se silencian u ocultan, o se superpone una capa de negro puro al 100% que desaparece súbitamente en $t = t_{\text{drop}}$, acompañada opcionalmente de un flash blanco de 1 frame en el impacto exacto ($t_{\text{drop}}$).

### 1.4 Montaje Sincopado y Polirritmias
El motor admite secuencias de corte guiadas por:
1. Lista de transientes percusivos reales (extraídos de análisis de audio).
2. Claves rítmicas sincopadas predefinidas:
   - Clave de Trap / Drill (acentos en contratiempos de corchea y tresillos de hi-hat).
   - Compás de 12 tiempos (flamenco / Ralphie Choo: acentos en 3, 6, 8, 10, 12).

---

## 2. Definición de Tipos e Interfaces (`src/rhythm/rhythm-types.ts`)

```typescript
export type FlashCutMode = "MEDIA_INTERLEAVE" | "WHITE_STROBE" | "CRIMSON_STROBE" | "CHROMATIC_INVERT";

export interface MachineGunBurstSpec {
  id: string;
  startTimeSeconds: number;
  durationSeconds: number;
  frameHold: number; // 1, 2, o 3 fotogramas por corte
  mode: FlashCutMode;
  mediaLayerIndices?: number[];
  colorHex?: string;
}

export interface BlackoutVacuumSpec {
  id: string;
  dropTimeSeconds: number;
  vacuumDurationSeconds: number; // Duración del apagón previo (ej. 0.15s)
  impactFlashFrame: boolean;     // 1 frame de destello blanco en t = dropTime
  flashColorHex?: string;        // Default "#FFFFFF" o "#FF1424"
}

export interface SyncopatedCutPoint {
  timeSeconds: number;
  mediaAssetId: string;
  inPointSeconds?: number;
  durationSeconds?: number;
}

export interface SyncopatedSequenceSpec {
  id: string;
  bpm: number;
  fps: number;
  cutPoints: SyncopatedCutPoint[];
}

export interface RhythmPlan {
  id: string;
  bpm: number;
  fps: number;
  bursts: MachineGunBurstSpec[];
  blackouts: BlackoutVacuumSpec[];
  syncopatedCuts: SyncopatedCutPoint[];
  extendScriptLines: string[];
  checksumSha256: string;
}
```

---

## 3. Principios Arquitectónicos e Invariantes

1. **Cuantización Estricta a Fotogramas:** Ningún `inPoint` o `outPoint` puede caer en sub-frames fraccionarios.
2. **Exclusión Mutua en Ráfagas:** En un instante $t$ durante una ráfaga estroboscópica, sólo una capa o sólido de corte está activo para evitar parpadeos no deterministas.
3. **Invariante de Motion Blur:** `comp.motionBlur = true` en toda composición generada.
4. **Determinismo SHA-256:** Toda ejecución con idénticos parámetros produce el mismo código y el mismo hash.
