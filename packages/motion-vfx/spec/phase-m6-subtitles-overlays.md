# Especificación Técnica Integral: Milestone 6 (Subtítulos Multilingües & Travel Overlays)

**Versión:** 1.0.0  
**Estado:** FORMAL SPECIFICATION  
**Sistema:** Motor Audiovisual v3.5.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documentos 01–20, M1 (Contratos), M4 (Voiceover), M5 (Adaptive Pacing)  

---

## 1. Alcance y Objetivos

### 1.1 Objetivos de Subtítulos Multilingües
1. **Generación determinista palabra-por-palabra:** Derivación de `SubtitleWord` y `SubtitleCue` a partir de `VoiceoverTrack` o `TranscriptSegment`.
2. **Sincronización Karaoke TIME Style:** Resaltado progresivo palabra por palabra (`highlightColor: "#FF1424"`, fuente condensada ultra-bold, estiramiento vertical 120%–150%, interletraje negativo).
3. **Soporte canónico de los 7 locales:** `es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`.
4. **Verificación de Deriva Temporal:**
   - Objetivo de sincronía: $|\Delta t| \le 40\text{ ms}$ (OK).
   - Deriva moderada: $40\text{ ms} < |\Delta t| \le 100\text{ ms}$ (WARNING).
   - Deriva grave / fallo: $|\Delta t| > 100\text{ ms}$ (ERROR) y $> 250\text{ ms}$ (FATAL).
5. **Segmentación y legibilidad:**
   - Longitud máxima de línea: 38 caracteres en 16:9, 26 caracteres en 9:16.
   - Duración mínima por cue: 0.8s; duración máxima por cue: 3.5s.
   - Límite de palabras por cue: 3 a 7 palabras para lectura dinámica tipo social/vlog.
6. **Normalización Unicode y Grafemas:** Normalización NFKC, conteo basado en Intl.Segmenter o regex de grafemas compuestos, descarte de caracteres invisibles corruptos.

### 1.2 Objetivos de Travel Overlays
1. **Geo-Badges:** Tarjetas de ubicación con ciudad, país, coordenadas GPS, altitud, hora local y estilo editorial carmesí.
2. **Location Cards & Time-Badges:** Título de locación, región geográfica, etiqueta de categoría y sello temporal.
3. **Route Maps & Haversine Geodesics:**
   - Cálculo de distancias geodésicas utilizando como radio canónico de la fórmula Haversine:
     $$EARTH\_MEAN\_RADIUS\_KM = 6371.0088\text{ km}$$
     $$\Delta\sigma = 2 \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
     $$d = EARTH\_MEAN\_RADIUS\_KM \cdot \Delta\sigma$$
   - Interpolación y trim paths para animación vectorial en After Effects [0% -> 100%].
4. **Polaroid Freeze-Frame:**
   - Captura y congelamiento de fotograma con inclinación determinista $\theta \in [-15^\circ, 15^\circ]$ basada en seed SHA-256 (sin aleatoriedad).
   - Sincronización exacta del efecto de sonido de obturador (*camera shutter SFX*) en el fotograma exacto: $|\Delta t_{\text{sfx}}| \le 1\text{ frame}$ ($\le 33.3\text{ ms}$ a 30 fps).
5. **Multi-Aspect Ratio Safe Zones:**
   - Ratios soportados: `16:9` (1920x1080), `9:16` (1080x1920), `1:1` (1080x1080), `4:5` (1080x1350), `21:9` (2560x1080).
   - En `9:16` (Shorts/Reels/TikTok): Reserva obligatoria de safe zone inferior (20% inferior reservado para título/audio de la app) y margen lateral derecho (15% reservado para botones de like/share).
6. **Resolución de Colisiones Espacio-Temporales:**
   - Prioridad numérica canónica:
     `POLAROID_FREEZE (5) > SUBTITLE_CUE (4) > LOCATION_CARD (3) > GEO_BADGE (2) > ROUTE_MAP (1)`.
   - Si dos elementos se solapan en tiempo y espacio en la misma área de pantalla, el de menor prioridad se desplaza a un slot alternativo no colisionante (ej. top-left a top-right o bottom a center) o retrasa su aparición.

---

## 2. Fórmulas Matemáticas y Definiciones Contractuales

### 2.1 Sincronización Karaoke
Dado un segmento con $N$ palabras, donde cada palabra $i$ tiene $[t_{i,\text{start}}, t_{i,\text{end}}]$:
$$\text{isHighlighted}(t) = \begin{cases} \text{true} & \text{si } t_{i,\text{start}} \le t < t_{i,\text{end}} \\ \text{false} & \text{en otro caso} \end{cases}$$

### 2.2 Geodesia Haversine
```typescript
function haversineDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371.0088; // WGS-84 mean radius
  const toRad = Math.PI / 180;
  const dLat = (lat2 - lat1) * toRad;
  const dLon = (lon2 - lon1) * toRad;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * toRad) * Math.cos(lat2 * toRad) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Number((R * c).toFixed(4));
}
```

### 2.3 Rotación Determinista de Polaroid
Para garantizar reproducibilidad exacta sin `Math.random()`:
$$\text{seedHash} = \text{SHA256}(\text{id} + \text{freezeTimestampSeconds})$$
$$\text{val} = \text{seedHash}[0] \cdot 256 + \text{seedHash}[1]$$
$$\text{rotationDegrees} = -15 + \left(\frac{\text{val}}{65535}\right) \cdot 30$$

### 2.4 Safe Zones por Aspect Ratio
| Aspect Ratio | Safe Margin X (%) | Safe Margin Top (%) | Safe Margin Bottom (%) | Social UI Reserve |
| :--- | :---: | :---: | :---: | :--- |
| **16:9** | 5% | 5% | 10% | None |
| **9:16** | 8% | 10% | 20% | Bottom 20%, Right 15% |
| **1:1** | 6% | 6% | 10% | None |
| **4:5** | 6% | 8% | 12% | None |
| **21:9** | 10% | 5% | 10% | None |

---

## 3. Arquitectura de Módulos (M6)

```
src/vlog/
  ├── subtitles/
  │     ├── subtitle-formatter.ts           # Formateo y wrapping de cues por aspecto y locale
  │     ├── karaoke-generator.ts            # Generador de cues con palabras y timestamps
  │     ├── vlog-subtitle-engine.ts         # Orquestador de subtítulos multilingüe
  │     └── index.ts
  ├── overlays/
  │     ├── haversine-geodesic.ts           # Motor de cálculo geodésico y Route Paths
  │     ├── polaroid-generator.ts           # Freeze frame, rotación determinista y SFX sync
  │     ├── safe-zone-layout-engine.ts      # Bounding boxes, Safe Zones y prevención de colisiones
  │     ├── vlog-travel-overlay-engine.ts   # Motor central de Travel Overlays
  │     └── index.ts
```

---

## 4. Plan de Pruebas y Criterios de Aceptación
1. **Tests unitarios específicos por subsistema:**
   - `SubtitleFormatter.test.ts`
   - `KaraokeGenerator.test.ts`
   - `VlogSubtitleEngine.test.ts`
   - `HaversineGeodesic.test.ts`
   - `PolaroidGenerator.test.ts`
   - `SafeZoneLayoutEngine.test.ts`
   - `VlogTravelOverlayEngine.test.ts`
2. **Property-Based Testing (PBT con `fast-check`):**
   - Distancia Haversine simétrica $d(A, B) = d(B, A) \ge 0$.
   - Rotación Polaroid acotada estrictamente en $[-15^\circ, 15^\circ]$.
   - Cues de subtítulos nunca solapan fuera de orden temporal.
   - Safe zone layout nunca sitúa elementos en la zona prohibida de UI en 9:16.
3. **Cero regresiones:** los 827 tests anteriores deben permanecer 100% en verde.
