# Vlog Travel Overlays Engine

**Documento:** `09-VLOG-TRAVEL-OVERLAYS-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** Core 2D/3D, Timeline Engine, Typography Engine, Audio Engine, Reframing Engine, Localization Engine, After Effects JSX Exporter  

---

## 1. Objetivo

Definir de manera determinista el sistema encargado de generar overlays gráficos especializados para Vlogs, viajes y documentales.

El sistema deberá poder producir automáticamente:
- Geo-Badges.
- Nombre de ciudad/localización.
- Estado/provincia/país.
- Hora local.
- Fecha.
- Coordenadas GPS.
- Mini-mapas.
- Rutas animadas.
- Marcadores de origen/destino.
- Polaroid Freeze-Frames.
- Etiquetas de lugares.
- Indicadores de distancia.
- Indicadores de desplazamiento.
- Overlays informativos.
- Animaciones de entrada/salida.
- SFX asociados.
- Variantes por idioma.
- Variantes por aspect ratio.

---

## 2. Principio arquitectónico

Los overlays no deberán ser creados directamente desde texto libre. Todo overlay deberá derivarse de un objeto tipado `OverlayDefinition`.

El flujo será:

$$\text{Metadata} \longrightarrow \text{OverlayDefinition} \longrightarrow \text{Validation} \longrightarrow \text{Layout} \longrightarrow \text{Animation} \longrightarrow \text{Localization} \longrightarrow \text{Aspect-Ratio Adaptation} \longrightarrow \text{Timeline} \longrightarrow \text{After Effects JSX}$$

---

## 3. Fuera del alcance

Este módulo no será responsable de:
- obtener mapas desde APIs externas;
- geocodificación online;
- traducción;
- generación de voz;
- edición del vídeo;
- clasificación A-Roll/B-Roll;
- render final de After Effects.

El módulo podrá consumir metadata geográfica proporcionada por otros componentes.

---

## 4. Filosofía Offline

El sistema deberá funcionar sin depender obligatoriamente de:
- Google Maps API
- Mapbox API
- OpenStreetMap API
- Google Geocoding API

La generación deberá ser posible utilizando:
- coordenadas;
- mapas locales;
- geometrías vectoriales;
- assets preexistentes;
- datos suministrados por el proyecto.

---

## 5. Overlay Types

```typescript
type TravelOverlayType =
  | "GEO_BADGE"
  | "TIME_BADGE"
  | "DATE_BADGE"
  | "GPS_BADGE"
  | "LOCATION_LABEL"
  | "MAP_ROUTE"
  | "MAP_MARKER"
  | "DISTANCE_BADGE"
  | "DIRECTION_BADGE"
  | "POLAROID"
  | "FREEZE_FRAME"
  | "TRAVEL_INFO_CARD";
```

---

## 6. Identidad del Overlay

Todo overlay deberá tener:

```typescript
interface OverlayIdentity {
  id: string;
  type: TravelOverlayType;
  version: string;
}
```
El ID deberá ser único dentro del proyecto.

---

## 7. Overlay Instance

```typescript
interface TravelOverlay {
  identity: OverlayIdentity;
  timeline: OverlayTimeline;
  content: OverlayContent;
  style: OverlayStyle;
  layout: OverlayLayout;
  animation: OverlayAnimation;
  localization?: OverlayLocalization;
  audio?: OverlayAudio;
}
```

---

## 8. Timeline

```typescript
interface OverlayTimeline {
  start: number;
  end: number;
  duration: number;
}
```
Debe cumplirse:
$$\text{end} > \text{start}, \quad \text{duration} = \text{end} - \text{start}$$

---

## 9. Relative Narrative Binding

Los overlays deberán poder vincularse a una narrativa:

```typescript
interface NarrativeBinding {
  narrativeId: string;
  relativeStart?: number;
  relativeEnd?: number;
}
```
Esto permite que un overlay se desplace automáticamente cuando cambia la duración de una locución.

---

## 10. Absolute Binding

También podrá existir:
```typescript
interface AbsoluteBinding {
  absoluteStart: number;
}
```
pero deberá declararse explícitamente.

---

## 11. Binding Priority

$$\text{Narrative Word Anchor} > \text{Narrative Segment Anchor} > \text{Relative Timeline} > \text{Absolute Timeline}$$

---

## 12. Geo Metadata

```typescript
interface GeoLocation {
  latitude: number;
  longitude: number;
  city?: string;
  state?: string;
  country?: string;
  countryCode?: string;
  timezone?: string;
}
```

---

## 13. Coordenadas

Las coordenadas deberán validarse:
$$\text{latitude} \in [-90, 90], \quad \text{longitude} \in [-180, 180]$$
Valores fuera de rango deberán producir:
$$\text{InvalidGeoCoordinateError}$$

---

## 14. Geo Badge

El Geo Badge deberá poder representar:
- 📍 Guadalajara / Jalisco • México
- 📍 Guadalajara, Jalisco
según configuración.

---

## 15. Geo Badge Data

```typescript
interface GeoBadgeContent {
  location: GeoLocation;
  showCity: boolean;
  showState: boolean;
  showCountry: boolean;
  showCoordinates: boolean;
}
```

---

## 16. Localización del Texto

El contenido visible deberá pasar por el sistema de localización. Los nombres propios no deberán traducirse automáticamente salvo que exista un alias explícito.

---

## 17. Time Badge

```typescript
interface TimeBadgeContent {
  timestamp: string;
  timezone: string;
  format: TimeFormat;
}
```

---

## 18. Time Formats

```typescript
type TimeFormat =
  | "12_HOUR"
  | "24_HOUR";
```
Configuración recomendada:
- `ES-MX` $\longrightarrow$ `24_HOUR`
- `EN-US` $\longrightarrow$ `12_HOUR`

---

## 19. Date Badge

```typescript
interface DateBadgeContent {
  date: string;
  locale: string;
  format: DateFormat;
}
```

---

## 20. Date Formats

```typescript
type DateFormat =
  | "DD_MM_YYYY"
  | "MM_DD_YYYY"
  | "YYYY_MM_DD"
  | "LONG"
  | "SHORT";
```

---

## 21. Timezone

La hora deberá calcularse usando la zona horaria del lugar, no la del ordenador que ejecuta el render.

---

## 22. Missing Timezone

Si no existe timezone:
1. usar timezone explícita del proyecto;
2. usar timezone del proyecto fuente;
3. emitir warning.
Nunca inventar una zona horaria.

---

## 23. GPS Badge

Ejemplo:
$$20.6597^\circ\text{ N}, \quad 103.3496^\circ\text{ W}$$

```typescript
interface GPSFormatConfig {
  decimals: number;
  useCardinalDirections: boolean;
  includeDegreeSymbol: boolean;
}
```

---

## 24. GPS Precision

La precisión por defecto será de $4\text{ decimales}$ (configurable).

---

## 25. Privacy Mode

Deberá existir `privacyMode: boolean`. Cuando esté activo, el sistema podrá ocultar o reducir la precisión GPS (ej. a 2 decimales).

---

## 26. Location Label

Una etiqueta podrá vincularse directamente a una coordenada visual:

```typescript
interface LocationLabel {
  text: string;
  geo?: GeoLocation;
  screenPosition?: Vector2;
}
```

---

## 27. Screen Position

Si se especifica posición manual:
$$x \in [0, 1], \quad y \in [0, 1]$$
utilizando coordenadas normalizadas.

---

## 28. Safe Zone

Todos los overlays deberán comprobar `safeZone` antes de producirse.

---

## 29. Aspect Ratio

El layout deberá soportar 16:9, 9:16, 1:1, 4:5, 21:9.

---

## 30. Aspect-Ratio Strategy

```typescript
type OverlayAspectStrategy =
  | "SCALE"
  | "REPOSITION"
  | "COMPACT"
  | "STACK"
  | "HIDE_SECONDARY";
```

---

## 31. Mobile Strategy

Para 9:16 y 4:5 la prioridad será:
$$\text{REPOSITION} > \text{COMPACT} > \text{STACK} > \text{HIDE\_SECONDARY}$$

---

## 32. Geo Badge Layout

El Geo Badge se compone de:
```
[ICON]
[PRIMARY LOCATION]
[SECONDARY LOCATION]
```

---

## 33. Geo Badge Dimensions

Las dimensiones deberán ser relativas al canvas, no codificadas únicamente en píxeles.

---

## 34. Typography

El sistema deberá reutilizar el Typography Engine existente. No deberá existir un segundo motor tipográfico.

---

## 35. Text Overflow

Si el texto excede el ancho permitido:
1. reducir tracking;
2. reducir tamaño;
3. aumentar altura;
4. compactar;
5. truncar únicamente si está permitido.
Nunca truncar silenciosamente.

---

## 36. Text Truncation

Si se requiere truncación (`...`), deberá generarse un warning explícito.

---

## 37. Icon System

Los iconos deberán utilizar assets vectoriales internos o generados proceduralmente, no fuentes emoji del sistema operativo.

---

## 38. Emoji

Si se utiliza emoji (📍), deberá existir fallback vectorial para evitar diferencias de render entre máquinas.

---

## 39. Animation

```typescript
interface OverlayAnimation {
  entrance: AnimationPreset;
  idle?: AnimationPreset;
  exit: AnimationPreset;
}
```

---

## 40. Animation Presets

```typescript
type AnimationPreset =
  | "NONE"
  | "FADE"
  | "SLIDE_LEFT"
  | "SLIDE_RIGHT"
  | "SLIDE_UP"
  | "SLIDE_DOWN"
  | "SCALE_POP"
  | "SPRING"
  | "TYPE_ON"
  | "DRAW_PATH"
  | "CAMERA_FLASH";
```

---

## 41. Entrance Duration

Valor recomendado: $0.25\text{ s}$.

---

## 42. Exit Duration

Valor recomendado: $0.20\text{ s}$.

---

## 43. Animation Safety

La animación no deberá extenderse fuera del intervalo del overlay.

---

## 44. Map Route

```typescript
interface MapRouteContent {
  origin: GeoLocation;
  destination: GeoLocation;
  waypoints?: GeoLocation[];
}
```

---

## 45. Route Geometry

```typescript
interface RouteGeometry {
  points: GeoPoint[];
}
```

---

## 46. Offline Route Mode

El sistema deberá aceptar rutas previamente calculadas en JSON sin exigir conexión externa.

---

## 47. Map Canvas

```typescript
interface MapCanvas {
  width: number;
  height: number;
  projection: MapProjection;
}
```

---

## 48. Projection

```typescript
type MapProjection =
  | "EQUIRECTANGULAR"
  | "MERCATOR"
  | "LOCAL_CARTESIAN";
```

---

## 49. Route Drawing

La ruta deberá poder animarse mediante `progress: number` ($0\% \to 100\%$).

---

## 50. Progress Constraint

$$\text{progress} \in [0, 1]$$

---

## 51. Route Animation

```typescript
interface RouteAnimation {
  startProgress: number;
  endProgress: number;
  duration: number;
  easing: EasingType;
}
```

---

## 52. Map Marker

```typescript
interface MapMarker {
  position: GeoLocation;
  label?: string;
  icon?: string;
  emphasis: number;
}
```

---

## 53. Marker Priority

$$\text{primary destination} > \text{current position} > \text{waypoints} > \text{secondary locations}$$

---

## 54. Map Scale

El sistema deberá calcular automáticamente un bounding box (`origin` + `destination` + `waypoints`) y añadir padding.

---

## 55. Map Padding

`mapPadding: number` con valor recomendado del $10\%$ del mapa.

---

## 56. Map Overflow

Nunca deberá producirse un marker fuera del canvas.

---

## 57. Current Position

Podrá mostrarse `●` como posición actual.

---

## 58. Travel Direction

Podrá mostrarse mediante flecha orientada según bearing.

---

## 59. Bearing

```typescript
interface Bearing {
  degrees: number; // [0, 360)
}
```

---

## 60. Distance Badge

```typescript
interface DistanceBadge {
  distance: number;
  unit: "KM" | "MI" | "M";
}
```

---

## 61. Distance Conversion

El engine deberá utilizar conversiones deterministas sin depender del locale para alterar el valor matemático.

---

## 62. Unit Localization

- `ES-MX` $\longrightarrow$ `km`
- `EN-US` $\longrightarrow$ `mi`
configurable.

---

## 63. Polaroid

El Polaroid será una composición de:
- foto
- marco blanco
- sombra
- pie de foto (caption)
- fecha opcional
- ubicación opcional

---

## 64. Polaroid Data

```typescript
interface PolaroidContent {
  sourceAssetId: string;
  caption?: string;
  date?: string;
  location?: string;
}
```

---

## 65. Freeze Frame

```typescript
interface FreezeFrameContent {
  sourceClipId: string;
  sourceTime: number;
  duration: number;
}
```

---

## 66. Freeze Frame Validation

$$\text{sourceTime} \ge \text{clip.start}, \quad \text{sourceTime} < \text{clip.end}$$

---

## 67. Camera Shutter

Un Polaroid podrá activar `camera_shutter.wav` del `SoundBankManager`.

---

## 68. SFX Binding

```typescript
interface OverlayAudio {
  soundId: string;
  relativeTime: number;
  volume: number;
}
```

---

## 69. Audio Ducking

El overlay podrá solicitar ducking musical (`duckMusic: boolean`), pero la ejecución pertenece al Audio Engine.

---

## 70. Freeze Frame Animation

Secuencia recomendada:
$$\text{video} \longrightarrow \text{freeze} \longrightarrow \text{flash} \longrightarrow \text{scale} \longrightarrow \text{polaroid frame} \longrightarrow \text{caption}$$

---

## 71. Flash Duration

Valor inicial: $0.08\text{ s}$.

---

## 72. Polaroid Rotation

Rotación determinista entre $-3^\circ$ y $+3^\circ$ utilizando la semilla del proyecto.

---

## 73. Deterministic Random

Nunca utilizar `Math.random()` para elementos reproducibles; usar el PRNG determinista existente.

---

## 74. Shadow

```typescript
interface ShadowStyle {
  opacity: number;
  blur: number;
  offsetX: number;
  offsetY: number;
}
```

---

## 75. Color System

Los colores deberán definirse mediante el sistema de estilos existente de v3.4.0.

---

## 76. Theme

```typescript
type TravelOverlayTheme =
  | "CINEMATIC"
  | "MINIMAL"
  | "EDITORIAL"
  | "DOCUMENTARY"
  | "VIBRANT";
```

---

## 77. Style Override

```typescript
styleOverride?: Partial<OverlayStyle>;
```

---

## 78. Localization

```typescript
interface OverlayLocalization {
  language: SupportedLanguage;
  localizedStrings: Record<string, string>;
}
```
Idiomas: `es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`.

---

## 79. Numeric Localization

Los números respetarán el locale (`1,234.5` vs `1.234,5`).

---

## 80. Proper Names

Los nombres de ciudades y lugares deberán conservarse según metadata; no traducir *"Guadalajara"* a variantes inventadas.

---

## 81. Date Localization

La fecha deberá ser generada por locale, no mediante sustitución textual manual.

---

## 82. Time Localization

La hora deberá utilizar timezone + locale.

---

## 83. Content Missing

Si falta `city`, el sistema podrá mostrar `state` si existe.

---

## 84. Missing Metadata Policy

$$\text{city missing} \longrightarrow \text{state} \longrightarrow \text{country} \longrightarrow \text{coordinates} \longrightarrow \text{OverlayMetadataMissingError}$$

---

## 85. Overlay Visibility

```typescript
interface VisibilityRule {
  enabled: boolean;
  minDuration?: number;
  maxDuration?: number;
}
```

---

## 86. Minimum Display Duration

Valor mínimo recomendado: $0.80\text{ s}$ (nunca $0.05\text{ s}$).

---

## 87. Maximum Display Duration

Configurable; $8.0\text{ s}$ por defecto.

---

## 88. Repetition Prevention

`repetitionCooldown = 5.0s` por defecto para evitar repeticiones absurdas del mismo badge.

---

## 89. Overlay Collision Detection

El engine deberá detectar colisiones entre:
- Geo Badge
- Subtitles
- CTA
- Face
- Other overlays

---

## 90. Collision Priority

1. Face / Subject
2. Subtitles
3. Safety-critical information
4. Primary overlay
5. Secondary overlay
6. Decorative elements

---

## 91. Collision Resolution

Estrategias: `move`, `scale`, `stack`, `hide secondary`.

---

## 92. Subtitle Avoidance

Los overlays no deberán cubrir subtítulos activos.

---

## 93. Face Avoidance

Si existe bounding box facial (`FaceRegion`), el overlay deberá evitarla.

---

## 94. Face Region

```typescript
interface FaceRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}
```

---

## 95. Confidence

Si $\text{confidence} < \text{threshold}$, el rostro no deberá considerarse restricción obligatoria.

---

## 96. Overlay Anchor

```typescript
type OverlayAnchor =
  | "TOP_LEFT"
  | "TOP_CENTER"
  | "TOP_RIGHT"
  | "CENTER_LEFT"
  | "CENTER"
  | "CENTER_RIGHT"
  | "BOTTOM_LEFT"
  | "BOTTOM_CENTER"
  | "BOTTOM_RIGHT"
  | "CUSTOM";
```

---

## 97. Responsive Layout

El layout deberá poder recalcularse cuando cambie canvas, aspect ratio, tamaño de subtítulos o safe zones.

---

## 98. Overlay Scaling

El sistema distinguirá entre `uniform scale`, `font scale`, `padding scale` y `stroke scale`.

---

## 99. 9:16 Layout

En vertical: regiones superior, media e inferior organizadas inteligentemente para evitar la UI de TikTok / Reels / Shorts.

---

## 100. Safe Area Configuration

```typescript
interface SafeArea {
  top: number;
  right: number;
  bottom: number;
  left: number;
}
```
Valores normalizados en $[0, 1]$.

---

## 101. Platform Presets

```typescript
type PlatformPreset =
  | "YOUTUBE"
  | "SHORTS"
  | "INSTAGRAM_REELS"
  | "TIKTOK"
  | "GENERIC";
```

---

## 102. Platform Safety

El engine no asumirá que todos los vídeos se publicarán en una plataforma concreta.

---

## 103. Timeline Integration

Cada overlay se convierte finalmente en `TimelineLayer`.

---

## 104. Layer Naming

Formato:
$$\text{VLOG\_OVR\_<TYPE>\_<ID>}$$
Ejemplo: `VLOG_OVR_GEO_BADGE_GDL01`.

---

## 105. Layer Metadata

Contiene: `overlayId`, `overlayType`, `narrativeId`, `language`, `version`.

---

## 106. After Effects Mapping

Capas compatibles con `Shape Layers`, `Text Layers`, `Null Layers`, `Footage Layers` y `Precompositions`.

---

## 107. Geo Badge AE Structure

```
GEO_BADGE
├── Background
├── Icon
├── PrimaryText
├── SecondaryText
└── Accent
```

---

## 108. Map AE Structure

```
MAP_ROUTE
├── MapBackground
├── Route
├── OriginMarker
├── DestinationMarker
├── Labels
└── CurrentPosition
```

---

## 109. Polaroid AE Structure

```
POLAROID
├── Photo
├── Frame
├── Shadow
├── Caption
└── Date
```

---

## 110. Match Names

El JSX deberá utilizar Match Names universales (`ADBE Root Vectors Group`, `ADBE Text Document`).

---

## 111. Spanish/English AE

Compatible sin depender de nombres localizados de efectos en la interfaz de After Effects.

---

## 112. No External Fonts Assumption

No asumir que una fuente específica está instalada; proveer `fontFallbackChain`.

---

## 113. Font Fallback

$$\text{Primary} \longrightarrow \text{Secondary} \longrightarrow \text{System Sans}$$

---

## 114. Missing Asset

Si falta un icono, generar fallback procedural.

---

## 115. Missing Map

Si falta mapa de fondo, usar `route-only mode`.

---

## 116. Route-only Mode

`background` + `route` + `markers` sin mapa cartográfico externo.

---

## 117. Rendering Independence

Los cálculos de coordenadas, bounding box, geometría de ruta, layout y animación se prueban sin After Effects.

---

## 118. Validation

```typescript
validateOverlay(overlay: TravelOverlay): ValidationResult
```

---

## 119. Validation Rules

- ID válido
- tipo válido
- duración > 0
- coordenadas válidas
- layout válido
- aspect ratio soportado
- texto válido
- animation duration válida
- asset references válidas

---

## 120. Error Types

```typescript
type TravelOverlayError =
  | "InvalidGeoCoordinateError"
  | "OverlayMetadataMissingError"
  | "OverlayDurationError"
  | "OverlayCollisionError"
  | "InvalidRouteError"
  | "InvalidOverlayLayoutError"
  | "OverlayAssetMissingError"
  | "UnsupportedAspectRatioError";
```

---

## 121. Warnings

- `LOW_GEO_PRECISION`
- `TEXT_COMPACTED`
- `SECONDARY_ELEMENT_HIDDEN`
- `ROUTE_SIMPLIFIED`
- `FONT_FALLBACK_USED`

---

## 122. Determinism

Mismo proyecto + definición + config + assets + seed produce resultado idéntico.

---

## 123. Serialization

Todos los overlays son serializables a JSON estándar.

---

## 124. Schema Version

$$\text{schemaVersion} = \text{"1.0.0"}$$

---

## 125. Migration

Si cambia el schema ($v_1 \to v_2$), deberá existir un migrador formal.

---

## 126. Testing — Geo Badge

- Input: Guadalajara, Jalisco, México.
- Expected: primary = Guadalajara, secondary = Jalisco • México.

---

## 127. Testing — Invalid Coordinates

- Input: $\text{latitude} = 120$.
- Expected: `InvalidGeoCoordinateError`.

---

## 128. Testing — Timezone

Ubicación con timezone conocida produce la hora correspondiente a dicha zona.

---

## 129. Testing — Multi-Language

El mismo overlay produce ES, EN, PT, FR, DE sin alterar su geometría base.

---

## 130. Testing — Aspect Ratio

Pasa pruebas en 16:9, 9:16, 1:1, 4:5, 21:9.

---

## 131. Testing — Collision

Al interceptar una región de subtítulos: `move/reposition` automático.

---

## 132. Testing — Face

Al ocupar una región facial: `reposition` si existe posición alternativa válida.

---

## 133. Testing — Route

Ruta con origen, destino y waypoint produce geometría de ruta, marcadores, bounding box y animación.

---

## 134. Testing — Route Progress

Verificar progreso en $0$ (inicio), $0.5$ (mitad) y $1.0$ (final).

---

## 135. Testing — Freeze Frame

El fotograma seleccionado corresponde exactamente al timestamp solicitado.

---

## 136. Testing — Polaroid

Produce foto, marco, sombra, caption y fecha opcional.

---

## 137. Testing — SFX

`camera_shutter.wav` se asocia al evento correcto cuando está habilitado.

---

## 138. Testing — Determinism

Dos ejecuciones con la misma seed producen idéntico ángulo y layout del Polaroid.

---

## 139. Testing — Missing Asset

Asset inexistente produce error controlado o fallback definido.

---

## 140. Testing — Serialization

$$\text{object} \longrightarrow \text{JSON} \longrightarrow \text{deserialize} \longrightarrow \text{object} \quad (\text{semántica idéntica})$$

---

## 141. Property-Based Testing

Generar coordenadas válidas, duraciones, aspect ratios, textos, rutas y comprobar invariantes.

---

## 142. Geo Property

$$\text{latitude} \in [-90, 90], \quad \text{longitude} \in [-180, 180]$$

---

## 143. Route Property

Toda ruta conserva origen y destino aunque se simplifique su geometría.

---

## 144. Layout Property

Ningún elemento obligatorio queda fuera del canvas + safe area.

---

## 145. Duration Property

$$\text{overlay.end} > \text{overlay.start}$$

---

## 146. Animation Property

$$\text{animation.start} \ge \text{overlay.start}, \quad \text{animation.end} \le \text{overlay.end}$$

---

## 147. Collision Property

Dos elementos `exclusive = true` no pueden ocupar regiones incompatibles simultáneamente.

---

## 148. Integration Test

$$\text{VlogFootage} \longrightarrow \text{Narrative} \longrightarrow \text{Localized Voice} \longrightarrow \text{Adaptive Pacing} \longrightarrow \text{Travel Overlay} \longrightarrow \text{Subtitle} \longrightarrow \text{Final Timeline} \longrightarrow \text{JSX}$$

---

## 149. Golden Project

Crear `golden_travel_vlog_project.json` con ciudad, ruta, timestamps, B-roll, A-roll, subtítulos, Polaroid, Geo Badge y mapa.

---

## 150. Golden Output

Comparar conteo de capas, nombres, timings, IDs, idioma, posiciones y duraciones.

---

## 151. Performance

Overlays generados como metadata/geometría vectorial antes del render sin renderizar vídeo.

---

## 152. Batch Generation

Capaz de generar $100+$ overlays en una ejecución sin intervención manual.

---

## 153. CLI

```bash
npm run vlog:overlays
```

---

## 154. Dry Run

```bash
npm run vlog:overlays -- --dry-run
```
produce `overlay-plan.json` sin modificar el proyecto final.

---

## 155. Debug Output

`overlay-debug.json` con posición, dimensiones, colisiones, safe zones y metadata fuente.

---

## 156. Logging

Registra: `overlayId`, `type`, `narrativeId`, `language`, `start`, `end`, `position`, `strategy`, `warnings`.

---

## 157. Idempotency

Ejecutar dos veces el pipeline sobre el mismo estado no duplica overlays.

---

## 158. Duplicate Detection

Identifica `overlayId + version` como identidad lógica.

---

## 159. Versioning

Una modificación visual incrementa `version` para invalidar caché.

---

## 160. Cache

$$\text{hash}(\text{definition} + \text{content} + \text{style} + \text{layout} + \text{language} + \text{aspectRatio})$$

---

## 161. Cache Invalidation

Se invalida al cambiar contenido, estilo, layout, idioma, asset o schema.

---

## 162. Definition of Done

- [ ] Geo Badge definido
- [ ] Time Badge definido
- [ ] Date Badge definido
- [ ] GPS Badge definido
- [ ] Location Label definido
- [ ] Map Route definido
- [ ] Map Marker definido
- [ ] Distance Badge definido
- [ ] Direction Badge definido
- [ ] Polaroid definido
- [ ] Freeze Frame definido
- [ ] Travel Info Card definido
- [ ] Geo metadata definido
- [ ] Coordinate validation definida
- [ ] Privacy mode definido
- [ ] Timezone definido
- [ ] Localization definida
- [ ] Aspect ratios definidos
- [ ] Safe zones definidas
- [ ] Collision detection definida
- [ ] Face avoidance definido
- [ ] Subtitle avoidance definido
- [ ] Animation system definido
- [ ] SFX binding definido
- [ ] Map projection definida
- [ ] Route geometry definida
- [ ] Route animation definida
- [ ] Deterministic random definido
- [ ] AE layer structures definidas
- [ ] Match Names definidos
- [ ] Font fallback definido
- [ ] Asset fallback definido
- [ ] Offline mode definido
- [ ] JSON serialization definida
- [ ] Schema version definida
- [ ] Migration strategy definida
- [ ] Validation definida
- [ ] Error handling definido
- [ ] Unit tests definidos
- [ ] Property tests definidos
- [ ] Integration tests definidos
- [ ] Golden project definido
- [ ] CLI definido
- [ ] Dry-run definido
- [ ] Logging definido
- [ ] Idempotency definida
- [ ] Cache definida
- [ ] Cache invalidation definida

---

## 163. Estado del documento

**Documento:** `09-VLOG-TRAVEL-OVERLAYS-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento establece que los overlays de viaje son componentes declarativos, deterministas, localizables y adaptables a cualquier formato soportado. Ninguna decisión esencial de layout, timing, contenido o compatibilidad deberá quedar delegada implícitamente a After Effects.
