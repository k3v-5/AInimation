# Especificación Técnica: Vlog Intelligence Engine (v3.5.x)
**Arquitectura de Comprensión Audiovisual, Montaje Editorial y Localización Multi-Idioma**

---

## 1. Visión y Principios de Diseño

El **Vlog Intelligence Engine (v3.5.x)** constituye una capa superior de inteligencia editorial montada estrictamente sobre el núcleo determinista existente (**Core Editing Engine v3.4.0**). No reemplaza ni muta el core, sino que orquesta la toma de decisiones creativas y de localización antes de compilar al grafo de ejecución (`ProjectIR` / After Effects ExtendScript JSX).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      v3.4.0 CORE EDITING ENGINE                         │
│  (Matrix2D, Timeline [t1, t2), Property<T>, AE Universal Compiler, DSL) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▲
                                     │ Consume
┌────────────────────────────────────┴────────────────────────────────────┐
│                  v3.5.x VLOG INTELLIGENCE ENGINE                        │
├─────────────────────────────────────────────────────────────────────────┤
│ 1. Speech Intelligence   │ VAD, Silence Stripper (>250ms), Micro-Fade   │
│ 2. Shot Intelligence     │ Classifier (A-Roll / B-Roll / Action), Faces │
│ 3. Semantic Matching     │ ShotManifest cacheable ↔ Transcript tags     │
│ 4. Editorial Planning    │ VlogEditPlanner (Analizadores ➔ EditPlan)    │
│ 5. Localization (TTS)    │ TTSProvider ($0 recurring cost), Multi-Lang  │
│ 6. Adaptive Pacing       │ Contratos Temporales, Bounds [0.95x - 1.05x] │
│ 7. Travel Overlays       │ Primitivas Declarativas (GeoBadge, RouteMap) │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       v3.6.x CONTENT FACTORY                            │
│  (Long-form Vlog, Shorts, Multi-language Stacks, Publishing Packages)  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Invariante Sagrado: Separación de Análisis y Decisión

> **Regla de Oro:** *Los analizadores nunca deben editar ni mutar el timeline.*

1. **Analizadores (Entrada $\to$ Metadatos Puros):**
   - $\text{Audio} \xrightarrow{\text{VAD}} \text{SilenceMap}$
   - $\text{Audio} \xrightarrow{\text{Whisper}} \text{Transcript}$
   - $\text{Footage} \xrightarrow{\text{Vision/Metadata}} \text{ShotManifest}$
   - $\text{GPS/Exif} \xrightarrow{\text{Extractor}} \text{LocationMetadata}$

2. **Planificador Editorial (`VlogEditPlanner`):**
   $$\text{VlogEditPlanner}(\text{Transcript}, \text{SilenceMap}, \text{ShotManifest}, \text{LocationMetadata}) \xrightarrow{\text{Decisión Editorial}} \text{EditPlan}$$

3. **Compilador / Generador:**
   $$\text{EditPlan} \xrightarrow{\text{Compiler}} \text{ProjectIR} \xrightarrow{\text{JSX Engine}} \text{After Effects ExtendScript (.jsx)}$$

---

## 3. Definición Formal de Contratos Temporales

En lugar de heurísticas rígidas de porcentaje, la sincronización entre voz, idioma y metraje visual se rige por contratos temporales tipados:

```typescript
export interface SpeechSegment {
  id: string;
  sourceStart: number;
  sourceEnd: number;
  language: string;
  words: {
    text: string;
    start: number;
    end: number;
    confidence?: number;
  }[];
  duration: number;
  semanticTags: string[];
  energy: number; // RMS normalizado 0.0 -> 1.0
}

export type ShotType = "A_ROLL" | "B_ROLL" | "TIMELAPSE" | "ACTION";

export interface GeoLocation {
  city: string;
  country?: string;
  coordinates?: [number, number]; // [Lat, Long]
  timestamp?: string;
}

export interface VlogShot {
  id: string;
  sourceFilePath: string;
  start: number;
  end: number;
  type: ShotType;
  semanticTags: string[];
  visualScore: number;
  faceScore?: number;
  location?: GeoLocation;
}

export interface ShotManifest {
  schemaVersion: "1.0.0";
  sourceDirectory: string;
  analyzedAt: string;
  shots: VlogShot[];
}
```

---

## 4. Hoja de Ruta de Implementación de 5 Fases

### Fase 1: `VlogJumpCutEngine` & Speech Intelligence (v3.5.0)
- Detección de silencios $> 250\text{ms}$ con Voice Activity Detection (VAD).
- Preservación íntegra de palabras habladas con margen de ataque/decaimiento de $50\text{ms}$.
- Micro-crossfade de audio de $10\text{ms}$ para evitar artefactos o clics audibles.
- Alternancia de cámara con **Dynamic Punch-In** ($100\% \to 115\% \to 100\%$) alineada a frases y picos de energía.

### Fase 2: `VlogFootageClassifier` & `ShotManifest` (v3.5.1)
- Clasificación de metraje en A-Roll, B-Roll, Timelapse y Acción.
- Detección de rostros y cálculo de `motionScore`.
- Manifiesto desacoplado y cacheable (`ShotManifest.json`) reutilizable entre idiomas.
- Emparejamiento semántico palabra clave $\leftrightarrow$ B-Roll disponible.

### Fase 3: Localización & Proveedor TTS Intercambiable (v3.5.2)
- Abstracción `TTSProvider`:
  ```typescript
  export interface TTSProvider {
    name: string;
    synthesize(text: string, language: string): Promise<{ audioBuffer: Buffer; durationSec: number }>;
    getWordTimings(audioBuffer: Buffer): Promise<Array<{ word: string; start: number; end: number }>>;
  }
  ```
- Soporte local sin costes recurrentes de APIs (Zero recurring API cost) para Español, Inglés, Portugués, Francés y Alemán.

### Fase 4: `VlogAdaptivePacingEngine` (v3.5.3)
- Resolución del contrato temporal entre idioma traducido y tomas de apoyo.
- Restricciones acotadas:
  - Dilatación de voz (*TTS stretch*): $[0.95\text{x}, 1.05\text{x}]$.
  - Extensión de B-Roll: Primera prioridad.
  - Reemplazo de B-Roll por toma complementaria: Segunda prioridad.
  - Modificación de A-Roll: Evitar.

### Fase 5: Primitivas Declarativas de Viaje & Suite de Determinismo (v3.5.4)
- Primitivas visuales declarativas: `GeoBadge`, `RouteMap`, `PolaroidFreeze`, `ChapterCard`.
- `VlogDeterminismSuite`:
  $$\text{RAW} + \text{TRANSCRIPT} + \text{MANIFEST} + \text{LANG} + \text{SEED} \equiv \text{EditPlan idéntico}$$
