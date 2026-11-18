# Vlog Travel Overlay Engine

**Documento:** `12-VLOG-TRAVEL-OVERLAY-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  

---

## 1. Objetivo

Definir el motor responsable de generar automáticamente gráficos audiovisuales específicos para:
- Vlogs de viaje.
- Documentales de viaje.
- Lifestyle.
- City guides.
- Food travel.
- Road trips.
- Walking tours.
- Travel shorts.
- Documentales multilingües.

El motor deberá generar elementos nativos compatibles con After Effects sin depender de composición manual.

---

## 2. Elementos Soportados

El módulo deberá soportar:
- Geo-Badge
- Location Card
- City Title
- Country Flag
- Local Time
- Date
- Weather Data
- Altitude
- Coordinates
- Mini Map
- Route Map
- Animated Route
- Start/End Markers
- Distance
- Travel Duration
- Polaroid Freeze Frame
- Photo Card
- Lower Third
- POI Card
- Chapter Card
- Airport/Station Card
- Currency Card
- Price Card
- Restaurant Card
- Hotel Card
- Street Label
- Neighborhood Label

Los elementos que dependan de datos externos deberán funcionar también con datos previamente suministrados en el proyecto.

---

## 3. Principio Fundamental

Los overlays deberán ser datos + plantilla, no gráficos hardcodeados:

$$\text{Structured Data} \longrightarrow \text{Overlay Resolver} \longrightarrow \text{Geometry} \longrightarrow \text{Animation} \longrightarrow \text{Style Preset} \longrightarrow \text{AE JSX}$$

---

## 4. Overlay Base

```typescript
interface TravelOverlay {
  id: string;
  type: TravelOverlayType;
  start: number;
  end: number;
  zIndex: number;
  stylePreset?: string;
  data: unknown;
}
```

---

## 5. Tipos

```typescript
type TravelOverlayType =
  | "GEO_BADGE"
  | "LOCATION_CARD"
  | "CITY_TITLE"
  | "MAP"
  | "ROUTE"
  | "POLAROID"
  | "LOWER_THIRD"
  | "POI_CARD"
  | "CHAPTER_CARD"
  | "PRICE_CARD"
  | "TIME_CARD"
  | "WEATHER_CARD"
  | "COORDINATE_CARD";
```

---

## 6. Coordinate System

Todo overlay deberá utilizar coordenadas normalizadas:
$$x \in [0, 1], \quad y \in [0, 1]$$
Posteriormente se convertirán al tamaño real de composición.

---

## 7. Resolution Independence

El mismo overlay deberá poder renderizarse en:
- `1920x1080` (16:9)
- `1080x1920` (9:16)
- `1080x1080` (1:1)
- `1080x1350` (4:5)
- `2560x1080` (21:9)
sin modificar manualmente sus coordenadas.

---

## 8. Safe Zones

Cada composición deberá definir:

```typescript
interface SafeZone {
  top: number;
  right: number;
  bottom: number;
  left: number;
}
```
en coordenadas normalizadas.

---

## 9. Social Safe Zones

Deberán existir perfiles para:
- `YOUTUBE`
- `SHORTS`
- `TIKTOK`
- `INSTAGRAM_REELS`
- `INSTAGRAM_FEED`

---

## 10. Overlay Collision

Los overlays no podrán solaparse con: subtítulos, speaker tracking, otros overlays o elementos protegidos.

---

## 11. Collision Resolver

Cuando exista colisión:
$$\text{Preferred position} \longrightarrow \text{Alternative position} \longrightarrow \text{Scale reduction} \longrightarrow \text{Vertical displacement} \longrightarrow \text{Warning}$$
El sistema deberá evitar ocultar contenido crítico.

---

## 12. Geo-Badge

Ejemplo conceptual:
```
📍 Guadalajara, Jalisco
8:42 PM
```

---

## 13. GeoBadge Data

```typescript
interface GeoBadgeData {
  city: string;
  region?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  localTime?: string;
  date?: string;
}
```

---

## 14. Geo-Badge Layout

El badge se compone de: Icon, City, Region/Country, Optional Time, Optional Date.

---

## 15. Icon

El pin de localización deberá ser vectorial (SVG/paths), no dependiendo de un archivo raster obligatorio.

---

## 16. Pin Animation

Entrada default:
$$\text{scale } 0\% \longrightarrow 115\% \longrightarrow 100\%$$
con curvas de aceleración (easing) configurables.

---

## 17. Badge Animation

El contenedor podrá utilizar `opacity`, `translate`, `scale` o `mask reveal`.

---

## 18. Location Title

Permitirá `uppercase`, `title case` o `lowercase` según el preset seleccionado.

---

## 19. Country Flag

Las banderas utilizarán representación vectorial o asset local pre-empaquetado, sin descargas online durante el render.

---

## 20. Local Time

$$\text{timezone} \longrightarrow \text{timestamp} \longrightarrow \text{local time}$$
La hora calculada será determinista respecto al timestamp de entrada.

---

## 21. No System Clock Dependency

Prohibido utilizar `new Date()` del sistema como fuente de datos en tiempo de renderizado; debe utilizarse un timestamp explícito.

---

## 22. Date Formatting

El formato dependerá del idioma (`es-MX`, `en-US`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 23. Localization

Todos los textos del overlay pasarán por el sistema de localización; nunca cablear palabras fijas en el renderizador.

---

## 24. Mini Map

El mapa podrá representar: ciudad, región, país, ruta, POIs, origen y destino.

---

## 25. Map Data Model

```typescript
interface MapData {
  center: {
    latitude: number;
    longitude: number;
  };
  zoom: number;
  markers: MapMarker[];
  route?: MapRoute;
}
```

---

## 26. Map Marker

```typescript
interface MapMarker {
  id: string;
  latitude: number;
  longitude: number;
  label?: string;
  type?: string;
}
```

---

## 27. Route

```typescript
interface MapRoute {
  points: GeoPoint[];
  startMarker?: GeoMarker;
  endMarker?: GeoMarker;
}
```

---

## 28. GeoPoint

```typescript
interface GeoPoint {
  latitude: number;
  longitude: number;
}
```

---

## 29. Projection

El motor separará las coordenadas geográficas $(\text{lat}, \text{lon})$ de las coordenadas de pantalla $(x, y)$.

---

## 30. Projection Interface

```typescript
interface MapProjection {
  project(point: GeoPoint): Point2D;
}
```

---

## 31. Projection Requirements

Implementación modular e intercambiable con soporte básico para proyecciones 2D locales (Mercator / Local Cartesian).

---

## 32. Offline Requirement

El renderer no dependerá de llamadas vivas a Google Maps, Mapbox u OpenStreetMap.

---

## 33. Map Assets

Los datos cartográficos entrarán como SVG local, JSON local, mapa prerenderizado o trazado vectorial provisto por el usuario.

---

## 34. Route Animation

La ruta podrá dibujarse progresivamente ($0\% \to 100\%$) mediante Trim Paths.

---

## 35. Route Draw Property

```typescript
interface RouteAnimation {
  start: number;
  end: number;
  easing: Easing;
}
```

---

## 36. Start Marker

Salida rotulada como `A`, `START` u `ORIGIN` según idioma/preset.

---

## 37. End Marker

Llegada rotulada como `B`, `DESTINATION` o `ARRIVAL`.

---

## 38. Marker Animation

$$\text{opacity } 0, \quad \text{scale } 70\% \longrightarrow 110\% \longrightarrow 100\%$$

---

## 39. Route Pulse

Los marcadores podrán emitir pulsos de escala, opacidad o anillos expansivos.

---

## 40. Distance

$$\text{distance} = \text{geographicDistance}(A, B) \quad (\text{cálculo determinista por fórmula de Haversine})$$

---

## 41. Distance Formatting

Ejemplos: `1.2 km`, `850 m`, `3.4 mi` según configuración de unidades.

---

## 42. Travel Duration

Formato legible localizado: `2h 15m`, `35 min`, `8 min`.

---

## 43. Unit System

Soporte de sistemas `METRIC` e `IMPERIAL`.

---

## 44. Default Unit

- `es-MX`, `es-ES`, `pt-BR`, `fr-FR`, `de-DE`, `en-GB` $\longrightarrow$ `METRIC`
- `en-US` $\longrightarrow$ `IMPERIAL`

---

## 45. Polaroid Freeze Frame

Composición de fotograma congelado, marco blanco, sombra proyectada, caption y fecha/ubicación opcional.

---

## 46. Freeze Frame Timing

```typescript
interface FreezeFrame {
  sourceLayerId: string;
  start: number;
  duration: number;
}
```

---

## 47. Default Duration

Valor recomendado inicial: $1.50\text{ s}$ (configurable).

---

## 48. Freeze Frame Capture

El fotograma debe capturarse exactamente en el instante `captureTime` especificado.

---

## 49. Photo Rotation

Rotación visual sutil:
$$\text{rotation} \in [-4^\circ, +4^\circ]$$

---

## 50. Deterministic Rotation

Derivada deterministamente de $\text{PRNG}(\text{seed} + \text{overlayId})$.

---

## 51. Shadow

Configurable con `offsetX`, `offsetY`, `blur`, `opacity` y `color`.

---

## 52. Shutter Sound

Disparo sincronizado de `camera_shutter.wav` a través del subsistema de audio.

---

## 53. Caption

Soporte multilínea para pies de foto y descripciones de lugares.

---

## 54. Photo Border

Escalado proporcional vectorial relativo a la resolución del canvas.

---

## 55. Lower Third

```typescript
interface LowerThirdData {
  title: string;
  subtitle?: string;
  icon?: string;
}
```

---

## 56. Lower Third Animation

Entrada por traslación horizontal (`translate X`) y opacidad con curvas de desaceleración.

---

## 57. POI Card

Diseñado para restaurantes, hoteles, museos, monumentos, cafeterías y parques.

---

## 58. POI Data

```typescript
interface POICardData {
  name: string;
  category?: string;
  city?: string;
  rating?: number;
  price?: string;
}
```

---

## 59. No Invented Data

Si no se suministran rating o precio, el componente no deberá inventar cifras falsas.

---

## 60. Price Card

```typescript
interface PriceCardData {
  item: string;
  amount: number;
  currency: string;
}
```

---

## 61. Currency Formatting

Formateo respetuoso de monedas y locales (`MXN`, `USD`, `EUR`, `BRL`, `GBP`).

---

## 62. Weather Card

```typescript
interface WeatherCardData {
  temperature: number;
  unit: "C" | "F";
  condition: string;
  timestamp: number;
}
```

---

## 63. Weather Data Source

Sin consultas de red vivas en el motor; los datos climáticos deben entrar como payload estructurado.

---

## 64. Coordinate Card

Presentación técnica de latitud/longitud con formato cardinal ($20.6597^\circ\text{ N}, \; 103.3496^\circ\text{ W}$).

---

## 65. Coordinate Precision

Precisión por defecto: $4\text{ decimales}$.

---

## 66. Chapter Card

Cartelas de separación narrativa (`CHAPTER 03 - CENTRO HISTÓRICO`).

---

## 67. Chapter Timing

Vinculado lógicamente al `chapterId` de la estructura del proyecto.

---

## 68. Semantic Anchoring

Los overlays pueden anclarse a: `SEGMENT`, `SHOT`, `WORD`, `LOCATION`, `CHAPTER`, `TRANSITION`.

---

## 69. Overlay Anchor

```typescript
interface OverlayAnchor {
  kind:
    | "TIME"
    | "SEGMENT"
    | "SHOT"
    | "WORD"
    | "LOCATION"
    | "CHAPTER";
  id?: string;
  offset?: number;
}
```

---

## 70. Localization Reflow

Al cambiar de idioma, los overlays recalculan ancho, saltos de línea, posición y duración de lectura.

---

## 71. Text Overflow

Prohibido que el texto sobresalga de su caja contenedora sin emitir advertencia o auto-corrección.

---

## 72. Overflow Resolution

$$\text{Reducir tracking} \longrightarrow \text{Reducir tamaño fuente} \longrightarrow \text{Ampliar caja} \longrightarrow \text{Multilínea} \longrightarrow \text{Layout alternativo} \longrightarrow \text{Warning}$$

---

## 73. Font Selection

Uso de tipografías registradas en el catálogo del motor tipográfico.

---

## 74. Font Fallback

Cadena formal de fuentes alternativas ante fuentes ausentes.

---

## 75. Emoji

Preferencia por iconos vectoriales procedimentales sobre fuentes de emojis del SO.

---

## 76. Style Profiles

```typescript
interface OverlayStyleProfile {
  fontFamily: string;
  fontSize: number;
  color: string;
  background?: string;
  borderRadius?: number;
  shadow?: ShadowConfig;
  animation?: AnimationConfig;
}
```

---

## 77. Preset Integration

Herencia estilística de presets consagrados: Cinematic Travel, Johnny Harris, Vox, Magnates Media, Minimalist Kinetic.

---

## 78. Override Hierarchy

$$\text{Configuración explícita} > \text{Configuración proyecto} > \text{Style preset} > \text{Defaults globales}$$

---

## 79. Z-Index

Composición en capas determinista controlada por valor numérico de `zIndex`.

---

## 80. Occlusion

Ocultamiento o reposicionamiento temporal ante interferencias con rostros, sujetos u objetos principales.

---

## 81. Face-Aware Placement

Integración con los bounding boxes del `ActiveSpeakerReframing` para evitar tapar al interlocutor.

---

## 82. Placement Zones

Nueve zonas canónicas: `TOP_LEFT`, `TOP_CENTER`, `TOP_RIGHT`, `CENTER_LEFT`, `CENTER`, `CENTER_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_CENTER`, `BOTTOM_RIGHT`.

---

## 83. Auto Placement

Algoritmo de optimización multiobjetivo para seleccionar la zona con mayor espacio libre y menor interferencia.

---

## 84. Overlay Score

$$\text{score} = \text{safeZone} \times 0.35 + \text{freeSpace} \times 0.30 + \text{faceAvoidance} \times 0.20 + \text{subtitleAvoidance} \times 0.15$$

---

## 85. Animation Presets

Catálogo: `POP`, `SLIDE`, `FADE`, `REVEAL`, `TYPE_ON`, `SCALE`, `MAP_DRAW`, `STAMP`, `POLAROID`.

---

## 86. Animation Determinism

Misma entrada genera idénticos keyframes, duraciones y curvas Bezier.

---

## 87. Easing

Reutilización de curvas Bezier cubic ease-in-out existentes en el Core v3.4.0.

---

## 88. Motion Blur

Habilitación de desenfoque de movimiento en capas con desplazamientos rápidos (`comp.motionBlur = true`).

---

## 89. Reduced Motion

Modo de accesibilidad `reducedMotion: boolean` para transiciones discretas sin desplazamientos agresivos.

---

## 90. Accessibility

Prohibido transmitir información crítica únicamente mediante color o animaciones efímeras.

---

## 91. Contrast

Comprobación automatizada de contraste WCAG según perfil de legibilidad.

---

## 92. Background Adaptation

Generación automática de cajas, pastillas (*pills*), sombras o fondos degradados (*scrims*) ante bajo contraste.

---

## 93. Overlay Manifest

```typescript
interface TravelOverlayManifest {
  projectId: string;
  compositionId: string;
  overlays: TravelOverlay[];
  safeZones: SafeZone;
  stylePreset: string;
  locale: string;
  unitSystem: "METRIC" | "IMPERIAL";
}
```

---

## 94. AE Layer Naming

$$\text{VLOG\_OVERLAY\_<TYPE>\_<ID>}$$
Ejemplo: `VLOG_OVERLAY_GEO_BADGE_001`, `VLOG_OVERLAY_MAP_002`, `VLOG_OVERLAY_POLAROID_003`.

---

## 95. AE Layer Structure

```
Parent Null
├── Background (Shape)
├── Icon (Vector)
├── Primary Text (Text Layer)
├── Secondary Text (Text Layer)
├── Accent (Shape)
└── Animation Controller (Expression / Slider Controls)
```

---

## 96. Expression Policy

Minimizar expresiones de alto costo computacional; preferir valores estáticos y keyframes horneados.

---

## 97. Match Names

Uso estricto de Match Names universales (`ADBE Root Vectors Group`, `ADBE Text Document`).

---

## 98. Locale Independence

Independencia de nombres de propiedades traducidos al español u otros idiomas en After Effects.

---

## 99. JSX Export

Generación limpia del script JSX que crea capas, importa vectores y aplica keyframes.

---

## 100. Render Validation

Validación previa de IDs únicos, coordenadas no nulas, duraciones positivas y assets resueltos.

---

## 101. Invalid Coordinates

Valores `NaN`, `Infinity`, `null` o `undefined` provocan fallo bloqueante.

---

## 102. Geographic Validation

$$\text{latitud} \in [-90, +90], \quad \text{longitud} \in [-180, +180]$$

---

## 103. Missing Location

Si faltan coordenadas, los overlays cartográficos se cancelan con advertencia sin inventar ubicaciones.

---

## 104. Timestamp Validation

Los tiempos deben ser positivos ($\ge 0$) y compatibles con la duración de la composición.

---

## 105. Overlay Duration

$$\text{end} > \text{start}$$

---

## 106. Freeze Frame Validation

`captureTime` debe pertenecer al intervalo válido del clip fuente.

---

## 107. Test Categories

Pruebas de geometría, localización, safe zones, colisión, proyección de mapas, rutas animadas, polaroids y exportación JSX.

---

## 108. Property-Based Tests

Verificación generativa de coordenadas aleatorias, resoluciones múltiples y tiempos de visualización.

---

## 109. Geometry Invariant

Todo elemento visible permanece dentro de los límites del canvas más el margen de seguridad.

---

## 110. Localization Invariant

El cambio de idioma no altera el significado semántico ni los datos geográficos de origen.

---

## 111. Determinism Test

Dos ejecuciones sobre la misma entrada producen manifests, geometrías y keyframes idénticos.

---

## 112. Snapshot Tests

Snapshots JSON para `GeoBadge`, `Map`, `Route`, `Polaroid`, `LowerThird` y `ChapterCard`.

---

## 113. AE Export Tests

Validación de sintaxis JSX y comprobación de nombres de capas e importaciones.

---

## 114. No Network Test

Ejecución de la suite completa con conexión a red deshabilitada.

---

## 115. CLI

```bash
npm run vlog:overlays
```

---

## 116. Dry Run

```bash
npm run vlog:overlays -- --dry-run
```
produce `travel-overlay-manifest.json` y `travel-overlay-validation.json`.

---

## 117. Debug

```bash
npm run vlog:overlays -- --debug
```
emite mapas de calor de colisión, safe zones y cálculo de puntuaciones.

---

## 118. Error Codes

- `OVERLAY_INVALID_TIME`
- `OVERLAY_INVALID_COORDINATE`
- `OVERLAY_TEXT_OVERFLOW`
- `OVERLAY_COLLISION`
- `OVERLAY_MISSING_ASSET`
- `OVERLAY_INVALID_LOCALE`
- `OVERLAY_INVALID_PROJECTION`
- `OVERLAY_OUT_OF_BOUNDS`
- `OVERLAY_INVALID_DATA`

---

## 119. Warning Codes

- `OVERLAY_AUTO_REPOSITIONED`
- `OVERLAY_TEXT_RESIZED`
- `OVERLAY_LOW_CONTRAST`
- `OVERLAY_FACE_NEARBY`
- `OVERLAY_SUBTITLE_NEARBY`
- `OVERLAY_OPTIONAL_DATA_MISSING`

---

## 120. Performance

Generación de geometrías vectoriales sin renderizar vídeo en tiempo de análisis.

---

## 121. Asset Deduplication

Reutilización compartida de vectores e iconos entre múltiples overlays.

---

## 122. Font Deduplication

Declaración única de familias tipográficas por proyecto.

---

## 123. Data Provenance

```typescript
interface OverlayProvenance {
  source: string;
  sourceId?: string;
  generatedAt?: string;
}
```

---

## 124. No Hidden Dependencies

Sin dependencias del DOM del navegador, zona horaria del sistema operativo o servicios en la nube.

---

## 125. Input Contract

```
Project
├── composition
├── locale
├── safeZones
├── stylePreset
├── locations
├── chapters
├── shots
├── overlays
└── assets
```

---

## 126. Output Contract

Produce: `TravelOverlayManifest`, script After Effects JSX, informe de validación, advertencias y manifiesto de assets.

---

## 127. Definition of Done

- [ ] GeoBadge
- [ ] LocationCard
- [ ] CityTitle
- [ ] CountryFlag
- [ ] LocalTime
- [ ] Date
- [ ] WeatherCard
- [ ] CoordinateCard
- [ ] MiniMap
- [ ] Route
- [ ] StartMarker
- [ ] EndMarker
- [ ] RouteAnimation
- [ ] Distance
- [ ] TravelDuration
- [ ] Metric/Imperial
- [ ] Polaroid
- [ ] FreezeFrame
- [ ] ShutterEvent
- [ ] LowerThird
- [ ] POICard
- [ ] PriceCard
- [ ] ChapterCard
- [ ] SemanticAnchoring
- [ ] Localization
- [ ] TextReflow
- [ ] OverflowProtection
- [ ] SafeZones
- [ ] CollisionDetection
- [ ] FaceAvoidance
- [ ] SubtitleAvoidance
- [ ] PlacementResolver
- [ ] StyleProfiles
- [ ] PresetIntegration
- [ ] AnimationPresets
- [ ] ReducedMotion
- [ ] ContrastValidation
- [ ] DeterministicAnimation
- [ ] Manifest
- [ ] AE Export
- [ ] MatchNames
- [ ] AssetDeduplication
- [ ] DataValidation
- [ ] CLI
- [ ] DryRun
- [ ] Debug
- [ ] ErrorCodes
- [ ] WarningCodes
- [ ] UnitTests
- [ ] PropertyTests
- [ ] SnapshotTests
- [ ] AE ExportTests
- [ ] OfflineTests

---

## 128. Estado Final

**Documento:** `12-VLOG-TRAVEL-OVERLAY-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este módulo deberá considerarse terminado únicamente cuando los overlays puedan regenerarse automáticamente después de cambiar idioma, resolución, aspect ratio, duración, posición del hablante o timeline, sin necesidad de modificar manualmente el JSX.
