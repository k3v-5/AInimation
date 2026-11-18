# Especificación Técnica: Fase 5A — Media & Asset System

**Documento:** `spec/phase-5a-media-asset-system.md`  
**Estado:** VIGENTE / NORMATIVO  
**Módulos:** `src/assets/`, `src/resources/`

---

## 0. Propósito y Principios Arquitectónicos

La **Fase 5A** establece la infraestructura de medios reales y gestión de recursos binarios (`video.mp4`, `image.png`, `audio.wav`, `font.ttf`, `logo.svg`).

### Invariantes Fundamentales

1. **Separación Estricta: Asset $\neq$ Element**
   - **`Asset`:** Representa la fuente física/archivo y sus metadatos intrínsecos (resolución nativa, duración, codec, framerate, hash SHA-256).
   - **`Element`:** Representa una instancia de uso de ese asset en la escena (posición, recorte `sourceStart` $\to$ `sourceEnd`, velocidad `speed`, transformaciones y efectos).
   - Un único Asset puede ser referenciado por múltiples elementos sin duplicar almacenamiento ni decodificación.

2. **Desacoplamiento de Importación y Decodificación:**
   - **Importar:** Registrar el archivo y extraer sus metadatos ($O(1)$ sin cargar píxeles en memoria).
   - **Decodificar:** Carga perezosa (*on-demand*) de fotogramas solicitados por el timeline/renderer.

3. **Separación de Estado de Proyecto vs. Estado de Runtime:**
   - `project.json` solo almacena referencias a `AssetSource` (rutas relativas/absolutas y metadatos).
   - El estado de decodificación, texturas GPU y caché LRU (`FrameCache`) pertenece exclusivamente al runtime.

4. **Resiliencia ante Archivos Faltantes (*Missing Assets*):**
   - Si un archivo cambia de ubicación, el estado pasa a `missing` sin corromper el proyecto ni las referencias de los elementos. Se admite revinculación (*relink*).

---

## 1. Tipos, Metadatos y Ciclo de Vida

### 1.1. Tipos de Asset (`AssetType`)
`"video" | "image" | "audio" | "font" | "svg" | "unknown"`

### 1.2. Estados del Ciclo de Vida (`AssetLifecycleState`)
`"unloaded" | "loading" | "ready" | "missing" | "error"`

### 1.3. Esquemas de Metadatos
- **`VideoMetadata`:** `{ width: number; height: number; duration: number; fps: number; codec?: string; bitrate?: number; hasAudio: boolean; hasAlpha?: boolean }`
- **`ImageMetadata`:** `{ width: number; height: number; format: string; hasAlpha?: boolean; colorSpace?: string }`
- **`AudioMetadata`:** `{ duration: number; sampleRate: number; channels: number; codec?: string; bitrate?: number }`
- **`FontMetadata`:** `{ family: string; style: string; weight: number; format: string }`
- **`SVGMetadata`:** `{ width: number; height: number; viewBox?: string }`

---

## 2. Mapeo Temporal (Composition Time vs. Source Time)

Para un elemento que utiliza un segmento de un video:
$$\text{sourceTime}(t_{\text{comp}}) = \text{sourceStart} + (t_{\text{comp}} \cdot \text{speed})$$
$$\text{compositionTime}(t_{\text{source}}) = \frac{t_{\text{source}} - \text{sourceStart}}{\text{speed}}$$
con $\text{speed} > 0$.

---

## 3. Caché y Proveedores de Fotogramas (`FrameProvider` & `FrameCache`)

- **`Frame`:** Estructura neutral de fotograma `{ width, height, format, timestamp, data }`.
- **`FrameCache`:** Caché LRU (Least Recently Used) parametrizable por número máximo de fotogramas y memoria máxima.
- **`ResourceManager`:** Orquestador central para la resolución de assets, carga bajo demanda y consulta de caché.

---

## 4. Inspección Binaria de Encabezados (`MediaMetadataProbe`)

Para evitar asunciones incorrectas sobre la duración de clips de video o audio al importarlos, el motor incorpora un parser binario sin dependencias:
- **MP4/MOV:** Decodificación de átomos ISO `moov -> mvhd` y `tkhd` para calcular duración exacta:
  $$\text{durationSec} = \frac{\text{rawDuration}}{\text{timescale}}$$
- **WAV (RIFF):** Decodificación del encabezado fmt y cálculo de duración por `byteRate`:
  $$\text{durationSec} = \frac{\text{dataSize}}{\text{byteRate}}$$
- **FLAC:** Decodificación del bloque `STREAMINFO` (frecuencia de muestreo y número total de muestras).
- **PNG/JPG:** Extracción de dimensiones físicas de imagen sin decodificar píxeles.
- Integrado automáticamente en `AssetImporter.importFromPath()` para poblar los metadatos reales del archivo.
