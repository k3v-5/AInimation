# Especificación Técnica: Fase 5E — Subtitle / Caption Engine

**Documento:** `spec/phase-5e-caption-engine.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/captions/`

---

## 0. Propósito y Principios Arquitectónicos

La **Fase 5E** construye el motor de subtítulos y *kinetic captions* de alto impacto para formatos cortos (TikTok, Reels, YouTube Shorts).

### Invariante Fundamental: Un Caption es una Composición de TextElements
Un subtítulo **no tiene un renderer aislado**. El flujo es:
```
Transcript (Audio / Whisper / SRT / VTT)
  └── Segmentation (agrupación por palabras o duración)
        └── Caption Track (instancias temporales en Timeline)
              └── Caption Layout (cálculo de líneas, word bounding boxes y safe areas)
                    └── TextElements & ShapeElements (Motion Graphics Engine)
```

---

## 1. Modelo de Datos y Estructuras

### 1.1. Transcripción y Word Timing (`Transcript`)
```typescript
interface TranscriptWord {
  id: string;
  text: string;
  start: number; // segundos
  end: number;   // segundos [start, end)
  confidence?: number;
}

interface TranscriptSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  words?: TranscriptWord[];
}

interface Transcript {
  id: string;
  language?: string;
  segments: TranscriptSegment[];
}
```

### 1.2. Estilos, Resaltado y Safe Area
- **`CaptionStyle`:** Tipografía (`fontFamily`, `fontSize`, `fontWeight`), color, stroke, sombra (`shadow`), caja de fondo (`background`) y alineación (`left`, `center`, `right`).
- **`WordEmphasis` / `WordStyleOverride`:** Modificaciones por palabra (ej. color amarillo, escala $1.2\text{x}$, caja de fondo).
- **`SafeArea` & `PlatformProfile`:** Márgenes de seguridad para UI de TikTok (`top: 150`, `bottom: 350`, `left: 60`, `right: 120`).
- **`CaptionLayoutMode`:** `"static" | "word-by-word" | "karaoke" | "highlight"`.

---

## 2. Segmentación, Layout y Evaluación

1. **Segmentación:** Divide las palabras en frases manejables con límites `maxWords` (ej. 3-4 palabras) o `maxDuration` (ej. 1.5s-2.0s).
2. **Layout & Safe Positioning:** Calcula saltos de línea automáticos cuando el ancho acumulado supera `maxWidth`, y posiciona el bloque respetando la zona segura.
3. **Evaluación Activa & Karaoke:** En el instante $t$, determina qué palabra está activa (`activeWordId`), el progreso continuo de la palabra ($\tau \in [0, 1]$) y aplica el estilo de resaltado (*highlight*).
