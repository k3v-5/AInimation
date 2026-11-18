# Especificación Técnica: Fase 6 — Asset & Media Intelligence

**Documento:** `spec/phase-6-media-intelligence.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulo:** `src/media-intelligence/`

---

## 0. Propósito y Separación Arquitectónica

La **Fase 6** transforma los archivos multimedia crudos en **entidades semánticas indexadas (`Asset`)** con metadatos completos, transcripción, detección de tomas (*shots*), objetos, caras, embeddings visuales/textuales y puntuación de calidad para el planificador de IA:

$$\text{Media File} \neq \text{Asset}$$

```
                 MEDIA FILE (URI / Path)
                            │
                            ↓
                    MEDIA INSPECTOR
             (Resolution, FPS, Codec, Audio)
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
      Checksum         Shot Detector     Transcript
     (SHA-256)      (Keyframes & Cuts)  (Spoken Words)
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ↓
                     ASSET ENTITY
             (Embeddings, Objects, Faces)
                            │
                            ↓
                     ASSET REPOSITORY
                 & B-ROLL RANKING ENGINE
                            │
                            ↓
                     AI ASSET CONTEXT
```

---

## 1. Modelo de Datos (`Asset`, `AssetMetadata`, `MediaShot`)

### 1.1. Tipos de Asset y Metadatos
- **`AssetType`:** `"video" | "audio" | "image" | "font" | "subtitle" | "graphic" | "sequence"`.
- **`AssetSource`:** `uri`, `size`, `checksum`.
- **`AssetMetadata`:** `filename`, `mimeType`, `duration`, `width`, `height`, `frameRate`, `sampleRate`, `channels`, `codec`, `bitrate`.

### 1.2. Detección de Tomas (*Shots*) y Detecciones
- **`MediaShot`:** `id`, `start`, `end`, `keyframes: Time[]`, `description`, `tags`, `objects`, `faces`, `quality`, `embedding`.
- **`ObjectDetection` & `FaceDetection`:** `label`, `bbox: Rect`, `confidence`.

---

## 2. Búsqueda Semántica y Puntuación B-roll (`BrollRanker`)

1. **Similitud Coseno de Embeddings:**
   $$\text{cosineSimilarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \cdot \|\vec{v}\|_2}$$
2. **Puntuación Multicriterio de Selección B-roll:**
   $$S_{final} = 0.4 \cdot S_{\text{semantic}} + 0.2 \cdot S_{\text{visual}} + 0.2 \cdot S_{\text{quality}} + 0.2 \cdot S_{\text{relevance}}$$

---

## 3. Repositorio y Reconexión de Assets (`AssetRepository`)

1. **Colecciones Inteligentes (*Smart Collections*):** Consultas dinámicas (`type`, `tags`, `semanticQuery`, `resolution`).
2. **Reconexión (*Relinking*):** Detección de archivos faltantes y restauración automática por Checksum SHA-256.
